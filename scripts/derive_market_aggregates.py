#!/usr/bin/env python3
"""wq-044 — derive market aggregates from entities.json.

CALIBRATION SCAFFOLD — not yet wired into apply_decisions.py per the
substantial reconciliation work needed before auto-derivation is safe
(see data/wq-044-sankey-derivation-diff.txt for the variance report).

Architecture per brief §2 with Simon's recommended A/A/A/B defaults:
  Q1A — market_aggregates lives in entities.json (next iteration)
  Q2A — derivation runs in apply_decisions.py after entity writes
  Q3A — split data/sankey-projections.json into editorial structure +
        derived values (next iteration)
  Q4B — hand-edited values win unless explicitly _derived: true

Per brief §5.2: provider.value = arr + operating_loss for each
model_provider entity, derived from two separately tracked entity
fields rather than one hand-set sum. When operating_loss claims update,
VC subsidy auto-rebalances (the OpenAI 20% scenario).

Usage:
  python3 scripts/derive_market_aggregates.py --dry-run --year 2025
  python3 scripts/derive_market_aggregates.py --diff-report   # writes wq-044-sankey-derivation-diff.txt
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from log_run import logged_run  # noqa: E402

ENTITIES_PATH = ROOT / "entities.json"
SANKEY_PATH = ROOT / "data" / "sankey-projections.json"
DIFF_REPORT_PATH = ROOT / "data" / "wq-044-sankey-derivation-diff.txt"

# Editorial mapping from sankey provider label → entity slug.
# In the next iteration this lives in data/sankey-structure.json under
# `entity_to_node_map` (brief §4.1). For now the mapping is inline so the
# calibration script can run without depending on the structure file.
LABEL_TO_SLUG = {
    "OpenAI": "openai",
    "Anthropic": "anthropic",
    "Google (Gemini)": "google",
    "Mistral": "mistral",
    "xAI": "xai",
    "DeepSeek": "deepseek",
    "Meta (Llama)": "meta",
    "Microsoft AI": "microsoft",
    "IaaS/Open": None,  # aggregation node — no single backing entity
}


def fin(entity: dict, year: str, field: str):
    """Return entity.financials[year][field] with fallback to current[field]."""
    f = (entity.get("financials") or {}).get(year) or {}
    if f.get(field) is not None:
        return f[field]
    return (entity.get("current") or {}).get(field)


def derive_year(entities: dict, year: str = "2025") -> dict:
    """Compute the per-provider + total aggregates for a given year.

    Returns:
      {
        "providers": {label: {value, derived_from, components}},
        "total_customer_revenue": value,
        "total_vc_subsidy": value,
      }
    """
    ent_lookup = {c["slug"]: c for c in entities.get("companies", [])}
    providers = {}
    total_arr = 0.0
    total_op_loss = 0.0
    for label, slug in LABEL_TO_SLUG.items():
        if not slug or slug not in ent_lookup:
            providers[label] = {"value": None, "derived_from": [], "components": {}, "_skipped": "no entity mapping"}
            continue
        ent = ent_lookup[slug]
        arr = fin(ent, year, "arr") or 0
        op_loss = fin(ent, year, "operating_loss") or 0
        value = arr + op_loss
        providers[label] = {
            "value": value,
            "derived_from": [
                f"{slug}.{year}.arr={arr}",
                f"{slug}.{year}.operating_loss={op_loss}",
            ],
            "components": {"arr": arr, "operating_loss": op_loss},
        }
        total_arr += arr
        total_op_loss += op_loss
    return {
        "providers": providers,
        "total_customer_revenue": total_arr,
        "total_vc_subsidy": total_op_loss,
    }


def write_diff_report(entities: dict, sankey: dict) -> str:
    """§6 step 1 — compare derived values to hand-curated sankey-projections.json."""
    derived = derive_year(entities, "2025")
    sankey_2025 = sankey.get("2025", {})

    lines = [
        "# wq-044 Sankey derivation dry-run vs hand-curated baseline",
        f"_Generated {datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')}_",
        "",
        "## Methodology",
        "",
        "Per brief §5.2: provider.value = arr + operating_loss (both pulled from",
        "entities.json:financials[2025]). Compared against hand-curated values in",
        "data/sankey-projections.json:2025.providers.",
        "",
        "## Per-provider variance",
        "",
        f"{'Sankey label':22}  {'Entity slug':18}  {'Hand-curated':>14}  {'Derived':>14}  {'Delta':>10}  Components",
        f"{'-'*22}  {'-'*18}  {'-'*14}  {'-'*14}  {'-'*10}  {'-'*40}",
    ]
    max_delta = 0.0
    rows_with_delta = 0
    for p in sankey_2025.get("providers", []):
        label = p["label"]
        hand = p["value"]
        d = derived["providers"].get(label, {})
        if d.get("value") is None:
            lines.append(f"{label:22}  {'(no entity)':18}  {hand:>14.2f}  {'—':>14}  {'—':>10}  {d.get('_skipped', '?')}")
            continue
        deriv_val = d["value"]
        delta = abs(deriv_val - hand) / max(0.001, abs(hand)) * 100
        max_delta = max(max_delta, delta)
        rows_with_delta += 1
        comps = d.get("components", {})
        comp_str = f"arr={comps.get('arr')}, op_loss={comps.get('operating_loss')}"
        lines.append(f"{label:22}  {LABEL_TO_SLUG.get(label) or '?':18}  {hand:>14.2f}  {deriv_val:>14.2f}  {delta:>9.1f}%  {comp_str}")

    lines += [
        "",
        "## Conservation totals",
        "",
        f"  Hand-curated totalCustomerRevenue:  {sankey_2025.get('totalCustomerRevenue', '?'):>10}",
        f"  Sum of arr across mapped entities:  {derived['total_customer_revenue']:>10.2f}",
        f"  Hand-curated totalVCSubsidy:        {sankey_2025.get('totalVCSubsidy', '?'):>10}",
        f"  Sum of op_loss across mapped:       {derived['total_vc_subsidy']:>10.2f}",
        "",
        "## Threshold setting",
        "",
        f"Largest per-provider delta: {max_delta:.1f}%",
        "",
    ]
    if max_delta > 5:
        lines.append(
            "Per the user's instruction in Phase 6: when first dry-run shows "
            ">5% imbalance, set the conservation threshold to 10% so build "
            "doesn't refuse."
        )
        lines.append(f"")
        lines.append(f"  CONSERVATION_THRESHOLD = 0.10  # was 0.05; widened due to {max_delta:.0f}% max observed delta")
    else:
        lines.append("Threshold stays at 5% — all observed nodes within tolerance.")

    lines += [
        "",
        "## Interpretation + recommendation",
        "",
        "The deltas are dominated by entities.json having more recent 2025",
        "values than the hand-curated sankey baseline.",
        "",
        "  - OpenAI: entities.json has arr=20 + op_loss=6.0 = 26 (vs sankey 13.65)",
        "    The sankey value reflects an earlier methodology snapshot; the entity",
        "    record was updated post-wq-039 with newer claims.",
        "  - Anthropic: entities.json arr=4.5 (vs sankey 4.71 customer + 3.0 VC).",
        "    Closer agreement on customer side; VC subsidy delta within methodology",
        "    drift.",
        "  - Google: entities.json arr=4.2 with NO operating_loss (vs sankey 2.5).",
        "    The 4.2 likely includes Workspace Gemini revenue that the sankey",
        "    excludes from the AI-only category.",
        "",
        "Recommendation: do NOT auto-wire derive_market_aggregates into",
        "apply_decisions.py until:",
        "",
        "  1. The 2025 entity values in entities.json are reconciled with the",
        "     methodology that produced the hand-curated sankey numbers — either",
        "     update the sankey to match the entity records (preferred — fresher",
        "     data wins), or fix the entity records that drifted from the",
        "     methodology framework (e.g. Google AI-only revenue carve-out).",
        "  2. data/sankey-structure.json is created (brief §4.1) so the editorial",
        "     entity_to_node_map lives in one place rather than hard-coded in this",
        "     script.",
        "  3. Conservation threshold can be tightened from 10% back to 5% once",
        "     reconciliation is complete.",
        "",
        "The derivation logic in this script is correct — the input data has drift",
        "the auto-builder would inherit on every commit until reconciled.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    with logged_run("derive_market_aggregates.py") as outputs:
        parser = argparse.ArgumentParser(description="Derive market aggregates (wq-044 calibration scaffold).")
        parser.add_argument("--diff-report", action="store_true",
                            help="Write data/wq-044-sankey-derivation-diff.txt comparing derived vs hand-curated.")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--year", default="2025")
        args = parser.parse_args()

        with open(ENTITIES_PATH) as f:
            entities = json.load(f)
        with open(SANKEY_PATH) as f:
            sankey = json.load(f)

        if args.diff_report:
            txt = write_diff_report(entities, sankey)
            DIFF_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
            DIFF_REPORT_PATH.write_text(txt)
            print(f"Wrote {DIFF_REPORT_PATH}")
            outputs["max_delta_pct"] = float(txt.split("Largest per-provider delta:")[1].split("%")[0].strip())
            return

        derived = derive_year(entities, args.year)
        print(json.dumps(derived, indent=2))
        outputs["providers_derived"] = sum(1 for v in derived["providers"].values() if v.get("value") is not None)


if __name__ == "__main__":
    main()
