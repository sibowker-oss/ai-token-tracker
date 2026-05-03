#!/usr/bin/env python3
"""wq-070 extension — add _other_closed synthetic aggregator entity.

Aggregates closed-weight model providers not individually tracked:
Cohere, AI21, Samsung Gauss, Apple Intelligence. ~10 T/day combined per
model-assumptions.md §2.4 v3 'Other closed' aggregate estimate.

Adding this brings tokens_per_day_total from 300 → 310 T/day, retiring
the _cumulative_2023_2025.tokens_2025_annualized=360 override (engine
within ±15%).

CLI:
  python3 scripts/add_other_closed_entity.py --apply  # MUTATES entities.json + metric-schema.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTITIES_PATH = ROOT / "entities.json"
SCHEMA_PATH = ROOT / "metric-schema.json"
DATE = "2026-05-03"

ENTITY = {
    "slug": "_other_closed",
    "name": "Other Closed Providers",
    "displayName": "Other Closed Model Providers",
    "roles": ["aggregator"],
    "_synthetic": True,
    "_aggregates": "Closed-weight providers not individually tracked: Cohere + AI21 + Samsung Gauss + Apple Intelligence",
    "region": "Global",
    "color": "#94a3b8",
    "current": {
        "tokens_per_day": 10,
        "tokens_per_day_date": DATE,
    },
    "provenance": {
        "current.tokens_per_day": {
            "confidence": "low",
            "claim_count": 1,
            "claims": [
                {
                    "id": "audit-20260503-other-closed-tokens",
                    "claim": "Aggregated estimate of closed-weight providers not individually tracked: ~10T/day across Cohere + AI21 + Samsung Gauss + Apple Intelligence",
                    "value": 10,
                    "unit": "T/day",
                    "weight": "indicative",
                    "confidence": "speculative",
                    "source": "model-assumptions.md §2.4 v3 'Other closed' aggregate estimate",
                    "origin": "editorial_audit_doc_addition",
                    "date": DATE,
                    "role": "supports",
                }
            ],
        },
    },
}

MATCH_RULE = {
    "pattern": "cohere|ai21|samsung.*gauss|apple.*intelligence",
    "slug": "_other_closed",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not args.apply and not args.dry_run:
        args.dry_run = True

    entities = json.loads(ENTITIES_PATH.read_text())
    schema = json.loads(SCHEMA_PATH.read_text())

    print("=== wq-070 ext — add _other_closed synthetic entity ===\n")

    by_slug = {c.get("slug"): c for c in entities.get("companies") or []}
    if "_other_closed" in by_slug:
        print("SKIP: _other_closed already in entities.json")
    else:
        entities["companies"].append(ENTITY)
        print(f"ADD _other_closed: 10T/day, role=aggregator (synthetic)")

    rules = schema.setdefault("entity_match_rules", [])
    if any(r.get("slug") == "_other_closed" for r in rules):
        print("SKIP: _other_closed match rule already present")
    else:
        rules.append(MATCH_RULE)
        print(f"ADD rule _other_closed: pattern={MATCH_RULE['pattern']}")

    if args.apply:
        ENTITIES_PATH.write_text(json.dumps(entities, indent=2) + "\n")
        SCHEMA_PATH.write_text(json.dumps(schema, indent=2) + "\n")
        print(f"\nWritten: {ENTITIES_PATH}")
        print(f"Written: {SCHEMA_PATH}")
    else:
        print("\n(dry-run)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
