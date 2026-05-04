#!/usr/bin/env python3
"""wq-053 — IaaS provider backfill + match rules.

Per Phase A verification (this branch): all 5 IaaS-relevant entities already
exist in entities.json. Required actions reduce to:
  1. Backfill collected_revenue for fireworks ($0.10B), groq ($0.10B),
     replicate ($0.05B) per brief §3 #3
  2. Reclassify groq: role ai_app → iaas_provider (per brief §3 #2)
  3. Add provenance entries for backfilled values
  4. Add match rules for together / lambda / coreweave (per brief §4.3)

Engine extension (derive_sankey.py) handled separately.

CLI:
  python3 scripts/wq053_iaas_backfill.py --apply
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

# Per brief §3 #3 (audit §4.4 puts combined IaaS at ~$0.50B)
REVENUE_2025 = [
    {"slug": "fireworks", "value": 0.10,
     "source": "Editorial estimate per brief §3 #3 (~$0.10B 2025; combined IaaS ~$0.50B per audit §4.4)"},
    {"slug": "groq", "value": 0.10,
     "source": "Editorial estimate per brief §3 #2 (LPU-based inference; ~$0.10B 2025)"},
    {"slug": "replicate", "value": 0.05,
     "source": "Editorial estimate per brief §3 #3 (inference + open model hosting; ~$0.05B 2025)"},
]

ROLE_FIXES = [
    {"slug": "groq", "from_role": "ai_app", "to_roles": ["iaas_provider"],
     "reason": "wq-053 §3 #2 — Groq is LPU-based inference platform; classified as iaas_provider"},
]

# Per brief §4.3
NEW_MATCH_RULES = [
    {"pattern": "together(?:\\.ai)?|togethercomputer", "slug": "together"},
    {"pattern": "lambda\\.labs|lambda\\.cloud|lambdalabs", "slug": "lambda"},
    {"pattern": "coreweave", "slug": "coreweave"},
    {"pattern": "groq", "slug": "groq"},
    {"pattern": "openrouter", "slug": "openrouter"},
    {"pattern": "replicate\\.com|\\breplicate\\b", "slug": "replicate"},
]


def apply_revenue(entities: dict) -> list[str]:
    log = []
    by_slug = {c.get("slug"): c for c in entities.get("companies") or []}
    for entry in REVENUE_2025:
        slug = entry["slug"]
        ent = by_slug.get(slug)
        if not ent:
            log.append(f"SKIP {slug}: not in entities.json")
            continue
        fin = ent.setdefault("financials", {})
        yr = fin.setdefault("2025", {})
        prev = yr.get("collected_revenue")
        if prev is not None:
            log.append(f"  {slug}.2025.collected_revenue: ${prev}B preserved (existing value not overwritten)")
            continue
        yr["collected_revenue"] = entry["value"]
        prov = ent.setdefault("provenance", {})
        prov["financials.2025.collected_revenue"] = {
            "confidence": "low",
            "claim_count": 1,
            "claims": [{
                "id": f"audit-{DATE.replace('-','')}-{slug}-2025-rev",
                "claim": f"{slug} 2025 customer revenue per editorial estimate (wq-053 §3)",
                "value": entry["value"],
                "unit": "$B",
                "weight": "indicative",
                "source": entry["source"],
                "origin": "editorial_audit_doc_addition",
                "date": DATE,
            }],
        }
        log.append(f"  {slug}.2025.collected_revenue: null → ${entry['value']}B")
    return log


def apply_role_fixes(entities: dict) -> list[str]:
    log = []
    by_slug = {c.get("slug"): c for c in entities.get("companies") or []}
    for fix in ROLE_FIXES:
        slug = fix["slug"]
        ent = by_slug.get(slug)
        if not ent:
            log.append(f"SKIP {slug}: not in entities.json")
            continue
        prev_roles = ent.get("roles", [])
        ent["roles"] = fix["to_roles"]
        prov = ent.setdefault("provenance", {})
        prov["_role_fix_wq053"] = {
            "claim": f"Role corrected {prev_roles} → {fix['to_roles']} per {fix['reason']}",
            "origin": "editorial_classification_fix",
            "date": DATE,
            "previous_roles": prev_roles,
        }
        log.append(f"  {slug}: roles {prev_roles} → {fix['to_roles']}")
    return log


def add_match_rules(schema: dict) -> list[str]:
    rules = schema.setdefault("entity_match_rules", [])
    existing_slugs = {r.get("slug") for r in rules}
    log = []
    for new in NEW_MATCH_RULES:
        if new["slug"] in existing_slugs:
            log.append(f"SKIP rule {new['slug']}: already present")
            continue
        rules.append(new)
        log.append(f"ADD rule {new['slug']}: pattern={new['pattern']}")
    return log


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not args.apply and not args.dry_run:
        args.dry_run = True

    entities = json.loads(ENTITIES_PATH.read_text())
    schema = json.loads(SCHEMA_PATH.read_text())

    print("=== wq-053 IaaS backfill ===\n")
    print("→ 1/3  customer_revenue 2025 backfill (fireworks/groq/replicate)")
    for line in apply_revenue(entities):
        print(line)

    print("\n→ 2/3  role corrections")
    for line in apply_role_fixes(entities):
        print(line)

    print("\n→ 3/3  match rules")
    for line in add_match_rules(schema):
        print(f"  {line}")

    if args.apply:
        ENTITIES_PATH.write_text(json.dumps(entities, indent=2) + "\n")
        SCHEMA_PATH.write_text(json.dumps(schema, indent=2) + "\n")
        print(f"\nWritten: {ENTITIES_PATH}\nWritten: {SCHEMA_PATH}")
    else:
        print("\n(dry-run)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
