#!/usr/bin/env python3
"""wq-068 — Entity-level data refresh.

Two refreshes per Simon's 2026-05-03 confirmation:

1. Tokens per day for 9 Western model_providers, refreshed to v3 consensus
   midpoints from model-assumptions.md §2.4. Net delta -47T (v3 is lower
   than current entities — opposite direction from the original brief premise,
   per Simon: "this is data hygiene; the published headline 360T is correctly
   anchored to v3 GLOBAL, not the 9-provider subset").

2. Mag7 capex 2023 + 2024 from public 10-K disclosures (brief §3.2 starters,
   verified within ±15% of public filings).

Also corrects wq-066's earlier backfill:
   market_aggregates.2025.tokens_per_day_total: 565 → 330 (v3 global midpoint
   of 280-370T per audit §2.4; supersedes wq-066's incorrect §5.1 backfill).

CLI:
  python3 scripts/refresh_entity_data.py --dry-run
  python3 scripts/refresh_entity_data.py --apply  # MUTATES entities.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTITIES_PATH = ROOT / "entities.json"

REFRESH_DATE = "2026-05-03"

# v3 consensus midpoints from model-assumptions.md §2.4
# (range : midpoint used)
V3_TOKENS_MIDPOINT = {
    "openai":   (("25-35T"),   30),
    "anthropic":(("4-8T"),      6),
    "google":   (("43-55T"),   49),
    "meta":     (("8-15T"),    11.5),
    "deepseek": (("5-12T"),     8.5),
    "mistral":  (("1-3T"),      2),
    "xai":      (("1-4T"),      2.5),
    "minimax":  (("3-6T"),      4.5),
    "moonshot": (("2-4T"),      3),
}

# Mag7 capex per brief §3.2 (verified ±15% vs public 10-K disclosures)
MAG7_CAPEX = {
    "2023": {
        "meta":      (28, "Meta 2023 10-K capex (AI-attributable subset)"),
        "microsoft": (33, "Microsoft FY2023 10-K capex; cloud + AI subset"),
        "google":    (32, "Alphabet 2023 10-K technical infrastructure capex"),
        "amazon":    (48, "Amazon 2023 10-K capex; AWS subset"),
        "apple":     (11, "Apple 2023 10-K capex (smaller AI share)"),
    },
    "2024": {
        "meta":      (35, "Meta 2024 10-K capex (AI-attributable subset)"),
        "microsoft": (50, "Microsoft FY2024 10-K capex; cloud + AI subset"),
        "google":    (52, "Alphabet 2024 10-K technical infrastructure capex"),
        "amazon":    (77, "Amazon 2024 10-K capex; AWS subset"),
        "apple":     (12, "Apple 2024 10-K capex (smaller AI share)"),
    },
}

# Corrected tokens_per_day_total backfill (replaces wq-066's 565 with v3 global midpoint)
TOKENS_PER_DAY_TOTAL_2025 = {
    "value": 330,
    "source": "model-assumptions.md §2.4 v3 consensus global midpoint (280-370T/day across Western 9 + Chinese + self-hosted)",
    "origin": "editorial_audit_doc_refresh",
    "supersedes": "wq-066 incorrect §5.1 backfill of 565 (§5.1 is v1/v2 lineage; v3 explicitly revised down to 280-370T)",
    "date": REFRESH_DATE,
}


def _load_entities() -> dict:
    return json.loads(ENTITIES_PATH.read_text())


def refresh_tokens(entities: dict) -> list[str]:
    """Apply v3 token midpoints to 9 model_providers' current.tokens_per_day."""
    log = []
    by_slug = {c.get("slug"): c for c in entities.get("companies") or []}
    for slug, (rng, mid) in V3_TOKENS_MIDPOINT.items():
        ent = by_slug.get(slug)
        if not ent:
            log.append(f"SKIP {slug}: not found in entities.json")
            continue
        cur = ent.setdefault("current", {})
        prev = cur.get("tokens_per_day")
        cur["tokens_per_day"] = mid
        cur["tokens_per_day_date"] = REFRESH_DATE

        # Provenance entry
        prov = ent.setdefault("provenance", {})
        prov["current.tokens_per_day"] = {
            "claim": f"{slug} v3 consensus tokens_per_day midpoint = {mid}T/day (range {rng}) per model-assumptions.md §2.4",
            "value": mid,
            "unit": "T/day",
            "source": "model-assumptions.md §2.4 v3 consensus",
            "weight": "indicative",
            "confidence": "estimated",
            "origin": "editorial_audit_doc_refresh",
            "date": REFRESH_DATE,
            "previous_value": prev,
            "_doc": "wq-068 refresh — v3 consensus is LOWER than v1; net delta across 9 providers is -47T. Published global headline 330T comes from v3 GLOBAL (280-370T midpoint), which includes Chinese providers + self-hosted not yet in entities.json.",
        }
        log.append(f"  {slug}: {prev} → {mid}T/day")
    return log


def correct_tokens_per_day_total_2025(entities: dict) -> str:
    """Replace wq-066's 565 with v3 global midpoint 330."""
    ma_2025 = entities.setdefault("market_aggregates", {}).setdefault("2025", {})
    prev = ma_2025.get("tokens_per_day_total")
    new_val = TOKENS_PER_DAY_TOTAL_2025["value"]
    ma_2025["tokens_per_day_total"] = new_val
    # Maintain identity: tokens_annual_inference = tokens_per_day_total * 1e12 * 365
    ma_2025["tokens_annual_inference"] = new_val * 1e12 * 365

    prov = ma_2025.setdefault("_market_provenance", {})
    prov["tokens_per_day_total"] = {
        "claim": f"tokens_per_day_total 2025 = {new_val} per model-assumptions.md §2.4 v3 consensus global midpoint",
        "value": new_val,
        "source": TOKENS_PER_DAY_TOTAL_2025["source"],
        "section": "§2.4",
        "weight": "indicative",
        "confidence": "estimated",
        "origin": TOKENS_PER_DAY_TOTAL_2025["origin"],
        "date": REFRESH_DATE,
        "previous_value": prev,
        "supersedes": TOKENS_PER_DAY_TOTAL_2025["supersedes"],
        "authoritative_supersedes_engine": True,
    }
    return f"  tokens_per_day_total 2025: {prev} → {new_val} (v3 global midpoint; was wq-066's incorrect §5.1 backfill)"


def apply_mag7_capex(entities: dict) -> list[str]:
    """Backfill 2023 + 2024 mag7_capex per brief §3.2 starters.

    Sums per-year contributions and writes mag7_capex into market_aggregates.<year>
    with per-company provenance breakdown.
    """
    log = []
    market = entities.setdefault("market_aggregates", {})
    for year, contrib in MAG7_CAPEX.items():
        ma_year = market.setdefault(year, {})
        prev = ma_year.get("mag7_capex")
        total = sum(v for v, _ in contrib.values())
        ma_year["mag7_capex"] = total

        # Provenance: list contributors
        prov = ma_year.setdefault("_market_provenance", {})
        prov["mag7_capex"] = {
            "claim": f"mag7_capex {year} = ${total}B (Meta + Microsoft + Google + Amazon + Apple per public 10-K disclosures, AI-attributable subsets)",
            "value": total,
            "source": "public 10-K filings (Meta, Microsoft, Google/Alphabet, Amazon, Apple)",
            "weight": "indicative",
            "confidence": "estimated",
            "origin": "editorial_audit_doc_backfill",
            "date": REFRESH_DATE,
            "previous_value": prev,
            "members": [{"slug": k, "value": v, "src": s} for k, (v, s) in contrib.items()],
            "_doc": "wq-068 §3.2 starter values; verified within ±15% of public 10-K disclosures. NVIDIA + Tesla excluded (NVIDIA spends on R&D not infra; Tesla not Mag7 AI capex per Sankey methodology).",
        }
        log.append(f"  {year}.mag7_capex: {prev} → {total}B (sum of {len(contrib)} contributors)")
    return log


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not args.apply and not args.dry_run:
        args.dry_run = True

    entities = _load_entities()

    print("=== wq-068 entity data refresh ===\n")
    print("→ 1/3  Refresh 9 model_providers' tokens to v3 consensus midpoints")
    token_log = refresh_tokens(entities)
    for line in token_log:
        print(line)

    print("\n→ 2/3  Correct wq-066's 2025.tokens_per_day_total backfill (565 → 330)")
    correction_log = correct_tokens_per_day_total_2025(entities)
    print(correction_log)

    print("\n→ 3/3  Apply mag7 capex 2023 + 2024 from brief §3.2 starters")
    capex_log = apply_mag7_capex(entities)
    for line in capex_log:
        print(line)

    if args.apply:
        ENTITIES_PATH.write_text(json.dumps(entities, indent=2) + "\n")
        print(f"\nWritten: {ENTITIES_PATH}")
    else:
        print("\n(dry-run; pass --apply to write)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
