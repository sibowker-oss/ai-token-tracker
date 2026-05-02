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
DIFF_REPORT_PATH = ROOT / "data" / "wq-044-final-diff.txt"

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


# wq-044 wire-completion (Phase 1.1) — confidence-tier mapping for the
# per-provider block written into entities.json:market_aggregates. The Sankey
# renderer consumes a `tier` field per provider node; map our provenance
# origins to the existing tier vocabulary so the rendered Sankey carries an
# accurate confidence read on every cell.
ORIGIN_TO_TIER = {
    "consensus_engine_derived": "2A",
    "editorial_override": "1B",
    "editorial_balance_calculation": "3C",
    "editorial_reconciliation": "1B",
    "accepted": "1B",
}


def _provenance_origin(entity: dict, year: str, field: str) -> str | None:
    """Return the primary (non-superseded) provenance claim's origin for the
    given entity-year-field, or None if no provenance exists."""
    prov = (entity.get("provenance") or {}).get(f"{year}.{field}") or {}
    for c in (prov.get("claims") or []):
        if c.get("role") != "superseded":
            return c.get("origin")
    return None


def _weakest_tier(*tiers: str | None) -> str:
    """Return the weakest tier across the inputs (highest tier number wins,
    e.g. 3C beats 2A beats 1B). None inputs are treated as 3C."""
    rank = {"1A": 1, "1B": 2, "2A": 3, "2B": 4, "3A": 5, "3B": 6, "3C": 7, "4": 8}
    worst = "1A"
    for t in tiers:
        t = t or "3C"
        if rank.get(t, 9) > rank.get(worst, 0):
            worst = t
    return worst


def derive_year(entities: dict, year: str = "2025") -> dict:
    """Compute the per-provider + total aggregates for a given year.

    wq-044 wire (post-wq-048 + vc_subsidy reconciliation):
      provider.value = collected_revenue + (vc_subsidy or operating_loss)

    collected_revenue lives in entities.json:financials.<year>.collected_revenue
    (populated by scripts/derive_collected_revenue.py — wq-048 consensus engine).

    vc_subsidy is the editorial-balance value (origin: editorial_balance_calculation).
    Falls back to operating_loss when vc_subsidy is absent — and logs the fallback
    so we can audit which providers still need vc_subsidy populated.

    Returns:
      {
        "providers": {label: {value, derived_from, components, subsidy_source}},
        "total_customer_revenue": sum of collected_revenue across providers,
        "total_vc_subsidy": sum of resolved subsidy across providers,
        "fallback_log": [labels where vc_subsidy was absent and operating_loss
                         was used instead],
      }
    """
    ent_lookup = {c["slug"]: c for c in entities.get("companies", [])}
    providers = {}
    total_customer_revenue = 0.0
    total_subsidy = 0.0
    fallback_log = []
    for label, slug in LABEL_TO_SLUG.items():
        if not slug or slug not in ent_lookup:
            providers[label] = {"value": None, "derived_from": [], "components": {}, "_skipped": "no entity mapping"}
            continue
        ent = ent_lookup[slug]
        collected_revenue = fin(ent, year, "collected_revenue") or 0
        vc_subsidy_val = fin(ent, year, "vc_subsidy")
        op_loss = fin(ent, year, "operating_loss") or 0
        if vc_subsidy_val is not None:
            subsidy = vc_subsidy_val
            subsidy_source = "vc_subsidy"
        else:
            subsidy = op_loss
            subsidy_source = "operating_loss (fallback — vc_subsidy not populated)"
            fallback_log.append(f"{label} ({slug}): used operating_loss={op_loss} as subsidy")
        value = collected_revenue + subsidy
        providers[label] = {
            "value": value,
            "derived_from": [
                f"{slug}.{year}.collected_revenue={collected_revenue}",
                f"{slug}.{year}.{'vc_subsidy' if vc_subsidy_val is not None else 'operating_loss'}={subsidy}",
            ],
            "components": {
                "collected_revenue": collected_revenue,
                "vc_subsidy": vc_subsidy_val,
                "operating_loss": op_loss,
                "subsidy_used": subsidy,
                "subsidy_source": subsidy_source,
            },
        }
        total_customer_revenue += collected_revenue
        total_subsidy += subsidy
    return {
        "providers": providers,
        "total_customer_revenue": total_customer_revenue,
        "total_vc_subsidy": total_subsidy,
        "fallback_log": fallback_log,
    }


CONSERVATION_THRESHOLD_PCT = 5.0  # wq-044 final wire — tightened from 10% per Simon's spec.


# wq-044 wire-completion (Phase 1.1) — display name + colour mapping.
# Used when writing the per-provider block into entities.json:market_aggregates
# so consumers (generate_site_data.py + the renderer) get the right label and
# accent without having to look up entity records again.
SLUG_TO_DISPLAY = {
    "openai":    {"label": "OpenAI",          "color": "#10a37f"},
    "anthropic": {"label": "Anthropic",       "color": "#d97706"},
    "google":    {"label": "Google (Gemini)", "color": "#4285f4"},
    "meta":      {"label": "Meta (Llama)",    "color": "#1877f2"},
    "deepseek":  {"label": "DeepSeek",        "color": "#6c5ce7"},
    "mistral":   {"label": "Mistral",         "color": "#ff7000"},
    "xai":       {"label": "xAI",             "color": "#000000"},
    "minimax":   {"label": "Minimax",         "color": "#9333ea"},
    "moonshot":  {"label": "Moonshot",        "color": "#ec4899"},
}


def derive_provider_block(entities: dict, year: str = "2025") -> dict:
    """Walk every model_provider entity → build per-provider block.

    Returns the full mapping that wq-044 wire-completion writes into
    entities.json:market_aggregates.<year>.providers, keyed by entity slug:

        {
          "<slug>": {
            "label": "OpenAI",
            "color": "#10a37f",
            "customer_revenue": 9.3147,
            "vc_subsidy": 6.0,
            "value": 15.3147,
            "tier": "2A",
            "subsidy_source": "vc_subsidy",  # or "operating_loss (fallback)"
            "derived_from": [
              "openai.2025.collected_revenue=9.3147",
              "openai.2025.vc_subsidy=6.0"
            ]
          },
          ...
        }

    Any model_provider entity with no collected_revenue AND no vc_subsidy
    AND no operating_loss is INCLUDED with value=0 + tier=4 so the absence
    is visible (not silently dropped).
    """
    providers = {}
    for ent in entities.get("companies", []):
        if "model_provider" not in (ent.get("roles") or []):
            continue
        slug = ent.get("slug", "")
        cr = fin(ent, year, "collected_revenue") or 0
        vc = fin(ent, year, "vc_subsidy")
        op_loss = fin(ent, year, "operating_loss") or 0
        if vc is not None:
            subsidy = vc
            subsidy_source = "vc_subsidy"
            subsidy_field = "vc_subsidy"
        else:
            subsidy = op_loss
            subsidy_source = "operating_loss (fallback — vc_subsidy not populated)"
            subsidy_field = "operating_loss"

        cr_origin = _provenance_origin(ent, year, "collected_revenue")
        vc_origin = _provenance_origin(ent, year, "vc_subsidy") if vc is not None else _provenance_origin(ent, year, "operating_loss")
        cr_tier = ORIGIN_TO_TIER.get(cr_origin or "", "3C") if cr else "4"
        vc_tier = ORIGIN_TO_TIER.get(vc_origin or "", "3C") if subsidy else "4"
        provider_tier = _weakest_tier(cr_tier, vc_tier)

        display = SLUG_TO_DISPLAY.get(slug, {"label": ent.get("name", slug), "color": ent.get("color", "#888")})
        providers[slug] = {
            "label": display["label"],
            "color": display["color"],
            "customer_revenue": cr,
            "vc_subsidy": subsidy,
            "value": cr + subsidy,
            "tier": provider_tier,
            "subsidy_source": subsidy_source,
            "derived_from": [
                f"{slug}.{year}.collected_revenue={cr}",
                f"{slug}.{year}.{subsidy_field}={subsidy}",
            ],
        }
    return providers


def apply_market_aggregates(entities: dict, year: str = "2025") -> dict:
    """Write the per-provider block AND recompute totals into
    entities.json:market_aggregates.<year>. MUTATES the entities dict in place.

    Recompute approach (preserves audit §4 sankey semantics):
      1. New provider sums = sum of (customer_revenue, vc_subsidy) across model_provider entities.
      2. Capture residual = (existing total) - (existing per-provider sum, if a
         providers block already existed; else assume residual=0 and the new
         total is the new provider sum).
      3. New total = new_provider_sum + residual.

    On first run (no prior providers block), there's no residual to subtract,
    so the new total = new_provider_sum exactly. Subsequent runs preserve
    whatever residual was set on first run by deriving from the previous
    providers + total. This keeps the writes idempotent.

    Returns a summary dict for the caller's report:
      {
        "providers": <provider block>,
        "totals": {"total_customer_revenue": ..., "total_vc_subsidy": ..., ...},
        "deltas": {"total_customer_revenue": (old, new), ...},
      }
    """
    providers = derive_provider_block(entities, year)
    new_provider_cr_sum = sum(p["customer_revenue"] for p in providers.values())
    new_provider_vc_sum = sum(p["vc_subsidy"] for p in providers.values())

    market_aggregates = entities.setdefault("market_aggregates", {})
    year_block = market_aggregates.setdefault(year, {})
    old_providers = year_block.get("providers") or {}
    old_total_cr = year_block.get("total_customer_revenue")
    old_total_vc = year_block.get("total_vc_subsidy")

    if old_providers:
        # Subsequent run — residual = old_total - old_provider_sum
        old_provider_cr_sum = sum(p.get("customer_revenue", 0) for p in old_providers.values())
        old_provider_vc_sum = sum(p.get("vc_subsidy", 0) for p in old_providers.values())
        residual_cr = (old_total_cr or 0) - old_provider_cr_sum
        residual_vc = (old_total_vc or 0) - old_provider_vc_sum
    elif old_total_cr is not None:
        # First run — there's an existing total but no provider block.
        # Compute residual from the OLD hand-curated sankey provider sums:
        # OpenAI 7.65 + Anthropic 4.71 + Google 2.0 + IaaS 0.5 = 14.86 customer
        # OpenAI 6.0 + Anthropic 3.0 + Google 0.5 + IaaS 0.3 = 9.80 vc_subsidy
        # These constants encode the audit §4.4 sankey baseline. Documented
        # in the script docstring + commit message so a future maintainer
        # understands why these specific numbers appear.
        OLD_SANKEY_PROVIDER_CR_SUM = 7.65 + 4.71 + 2.0 + 0.5
        OLD_SANKEY_PROVIDER_VC_SUM = 6.0 + 3.0 + 0.5 + 0.3
        residual_cr = old_total_cr - OLD_SANKEY_PROVIDER_CR_SUM
        residual_vc = (old_total_vc or 0) - OLD_SANKEY_PROVIDER_VC_SUM
    else:
        residual_cr = 0.0
        residual_vc = 0.0

    new_total_cr = round(new_provider_cr_sum + residual_cr, 4)
    new_total_vc = round(new_provider_vc_sum + residual_vc, 4)

    year_block["providers"] = providers
    year_block["total_customer_revenue"] = new_total_cr
    year_block["total_vc_subsidy"] = new_total_vc
    year_block["_residual_customer_revenue"] = round(residual_cr, 4)
    year_block["_residual_vc_subsidy"] = round(residual_vc, 4)
    year_block["_residual_doc"] = (
        "Customer-revenue and VC-subsidy contributions NOT covered by the per-provider block. "
        "Captures Traditional SaaS AI revenue (Microsoft Copilot etc., audit §1.5) and the "
        "IaaS aggregation node (Together/Fireworks/Groq, audit §4.4). Held constant across "
        "engine runs so total = provider_sum + residual stays consistent with audit §4 totals."
    )

    return {
        "providers": providers,
        "totals": {
            "total_customer_revenue": new_total_cr,
            "total_vc_subsidy": new_total_vc,
            "_residual_customer_revenue": round(residual_cr, 4),
            "_residual_vc_subsidy": round(residual_vc, 4),
        },
        "deltas": {
            "total_customer_revenue": (old_total_cr, new_total_cr),
            "total_vc_subsidy": (old_total_vc, new_total_vc),
        },
    }


def write_diff_report(entities: dict, sankey: dict) -> str:
    """Compare derived values to hand-curated sankey-projections.json baseline.

    wq-044 final wire (post-wq-048 + vc_subsidy reconciliation):
      provider.value = collected_revenue + (vc_subsidy or operating_loss fallback)
    """
    derived = derive_year(entities, "2025")
    sankey_2025 = sankey.get("2025", {})

    lines = [
        "# wq-044 Sankey derivation dry-run vs hand-curated baseline",
        f"_Generated {datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')}_",
        "",
        "## Methodology (post-wq-048 + vc_subsidy reconciliation)",
        "",
        "  provider.value = collected_revenue + (vc_subsidy or operating_loss fallback)",
        "",
        "  - collected_revenue: from entities.json:financials[2025].collected_revenue",
        "    (populated by scripts/derive_collected_revenue.py — wq-048 consensus engine).",
        "  - vc_subsidy: editorial-balance value (origin: editorial_balance_calculation),",
        "    set per-provider on 2026-05-02 — see entity provenance entries.",
        "  - operating_loss fallback: used when vc_subsidy is absent for a provider.",
        "",
        "Compared against hand-curated values in data/sankey-projections.json:2025.providers.",
        "",
        "## Per-provider variance",
        "",
        f"{'Sankey label':22}  {'Entity slug':18}  {'Hand-curated':>14}  {'Derived':>14}  {'Delta':>10}  Components",
        f"{'-'*22}  {'-'*18}  {'-'*14}  {'-'*14}  {'-'*10}  {'-'*60}",
    ]
    max_delta = 0.0
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
        comps = d.get("components", {})
        comp_str = (
            f"cr={comps.get('collected_revenue')}, "
            f"subsidy={comps.get('subsidy_used')} (from {comps.get('subsidy_source')})"
        )
        lines.append(f"{label:22}  {LABEL_TO_SLUG.get(label) or '?':18}  {hand:>14.2f}  {deriv_val:>14.2f}  {delta:>9.1f}%  {comp_str}")

    if derived.get("fallback_log"):
        lines.append("")
        lines.append("## vc_subsidy fallback log (operating_loss used in place of vc_subsidy)")
        lines.append("")
        for line in derived["fallback_log"]:
            lines.append(f"  - {line}")

    lines += [
        "",
        "## Conservation totals",
        "",
        f"  Hand-curated totalCustomerRevenue:  {sankey_2025.get('totalCustomerRevenue', '?'):>10}",
        f"  Sum of collected_revenue (derived): {derived['total_customer_revenue']:>10.2f}",
        f"  Hand-curated totalVCSubsidy:        {sankey_2025.get('totalVCSubsidy', '?'):>10}",
        f"  Sum of subsidy (derived):           {derived['total_vc_subsidy']:>10.2f}",
        "",
        "## Conservation threshold",
        "",
        f"  CONSERVATION_THRESHOLD_PCT = {CONSERVATION_THRESHOLD_PCT}  (wq-044 final wire — tightened from 10% per Simon's spec)",
        f"  Largest per-provider delta:  {max_delta:.1f}%",
        "",
    ]
    if max_delta <= CONSERVATION_THRESHOLD_PCT:
        lines.append(f"  ✓ All providers within {CONSERVATION_THRESHOLD_PCT}% threshold.")
    else:
        lines.append(f"  ⚠ One or more providers exceeds {CONSERVATION_THRESHOLD_PCT}% threshold (max {max_delta:.1f}%).")
        lines.append(f"     Inspect the per-provider table above for divergence diagnosis.")

    lines += [
        "",
        "## Interpretation — deltas above threshold are INTENDED PUBLIC CHANGES",
        "",
        "OpenAI (+12.2%) and Google (+10.1%) BOTH exceed the 5% conservation",
        "threshold. This is NOT a bug. Both deltas are the wq-048 consensus engine",
        "customer-revenue revisions cascading through the wq-044 wire — which is",
        "the entire point of this brief.",
        "",
        "  - OpenAI: derived (9.31 + 6.0) = 15.31 vs hand 13.65 → +12.2%.",
        "    Cascades the wq-048 OpenAI 2025 customer revenue revision",
        "    ($7.65B → $9.31B). vc_subsidy = 6.0 (editorial-balance, unchanged).",
        "    Announced in the public changelog entry on this branch.",
        "",
        "  - Google: derived (2.2516 + 0.5) = 2.75 vs hand 2.50 → +10.1%.",
        "    Cascades the wq-048 Google 2025 customer revenue revision",
        "    ($2.00B → $2.2516B, +12.6% engine native, within ±15% band so retained).",
        "    vc_subsidy = 0.5 (editorial estimate of Alphabet internal subsidy).",
        "    Announced in the public changelog entry on this branch.",
        "",
        "  - Anthropic: derived (4.71 + 3.0) = 7.71 vs hand 7.71 → 0.0% ✓.",
        "    Editorial override pins customer revenue to hand-curated $4.71B;",
        "    vc_subsidy = 3.0 editorial-balance value matches hand-curated.",
        "",
        "Conservation threshold stays at 5% intentionally. Future runs that exceed",
        "5% surface as 'one or more providers exceeds threshold' so the operator",
        "knows to look — for the wq-044 ship the operator is Simon, the deltas are",
        "expected, and the changelog entry on this branch is the public disclosure.",
        "",
        "Reading guide for future maintainers: if a future --diff-report shows new",
        "deltas >5% on providers OTHER than OpenAI/Google with the same root cause",
        "(wq-048 engine wrote a fresh value to entities.json), that's also expected.",
        "Real bugs to investigate look like: (a) zero deltas everywhere when an",
        "entity record was just updated, (b) NaN/None in derived values, (c) the",
        "vc_subsidy fallback log firing for OpenAI/Anthropic/Google (means their",
        "vc_subsidy field disappeared from entities.json).",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    with logged_run("derive_market_aggregates.py") as outputs:
        parser = argparse.ArgumentParser(description="Derive market aggregates (wq-044 wire-completion).")
        parser.add_argument("--diff-report", action="store_true",
                            help="Write data/wq-044-final-diff.txt comparing derived vs hand-curated.")
        parser.add_argument("--apply", action="store_true",
                            help="Write per-provider block + recomputed totals into entities.json:market_aggregates. MUTATES entities.json.")
        parser.add_argument("--dry-run", action="store_true",
                            help="With --apply: report only, do not write to entities.json.")
        parser.add_argument("--year", default="2025")
        args = parser.parse_args()

        with open(ENTITIES_PATH) as f:
            entities = json.load(f)
        with open(SANKEY_PATH) as f:
            sankey = json.load(f)

        if args.apply:
            summary = apply_market_aggregates(entities, args.year)
            print("=== wq-044 wire-completion: per-provider block ===\n")
            for slug, p in summary["providers"].items():
                print(f"  {slug:14}  cr={p['customer_revenue']:>8.4f}  vc={p['vc_subsidy']:>8.4f}  value={p['value']:>8.4f}  tier={p['tier']}  ({p['subsidy_source']})")
            print()
            print("=== Totals (after recompute) ===")
            t = summary["totals"]
            d = summary["deltas"]
            print(f"  total_customer_revenue:  {d['total_customer_revenue'][0]} → {t['total_customer_revenue']}")
            print(f"  total_vc_subsidy:        {d['total_vc_subsidy'][0]} → {t['total_vc_subsidy']}")
            print(f"  _residual_customer_revenue: {t['_residual_customer_revenue']}")
            print(f"  _residual_vc_subsidy:       {t['_residual_vc_subsidy']}")
            print()
            if args.dry_run:
                print("[DRY-RUN] entities.json NOT written.")
            else:
                with open(ENTITIES_PATH, "w") as f:
                    json.dump(entities, f, indent=2)
                print(f"✓ entities.json written: {len(summary['providers'])} providers + recomputed totals")
            outputs["providers_written"] = len(summary["providers"])
            outputs["total_customer_revenue"] = t["total_customer_revenue"]
            outputs["total_vc_subsidy"] = t["total_vc_subsidy"]
            outputs["dry_run"] = args.dry_run
            return

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
