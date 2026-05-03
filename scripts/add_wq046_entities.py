#!/usr/bin/env python3
"""wq-046 — add 7 missing entities to entities.json.

Per Phase-1 verification (Claude Code, 2026-05-03): glean / fireworks /
anyscale already in entities.json with correct roles. Reduced scope from
brief's original 10 → 7 entities.

CLI:
  python3 scripts/add_wq046_entities.py --dry-run
  python3 scripts/add_wq046_entities.py --apply
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

NEW_ENTITIES = [
    {
        "slug": "databricks",
        "name": "Databricks",
        "displayName": "Databricks",
        "roles": ["traditional_saas", "ai_app"],
        "region": "US",
        "color": "#ff3621",  # brand red-orange
        "model_type": "proprietary",
        "website": "https://www.databricks.com",
        "products": ["Mosaic AI", "Unity Catalog", "Lakehouse"],
        "_doc": "Data + AI platform; growing AI-specific revenue stream",
    },
    {
        "slug": "scale",
        "name": "Scale AI",
        "displayName": "Scale AI",
        "roles": ["ai_app"],
        "region": "US",
        "color": "#1a1a1a",
        "model_type": "proprietary",
        "website": "https://scale.com",
        "products": ["Data Engine", "RLHF", "Government"],
        "_doc": "Data labelling for AI training",
    },
    {
        "slug": "modal",
        "name": "Modal Labs",
        "displayName": "Modal Labs",
        "roles": ["iaas_provider"],
        "region": "US",
        "color": "#7fee64",
        "model_type": "proprietary",
        "website": "https://modal.com",
        "products": ["Modal Cloud", "Serverless GPU"],
        "_doc": "Serverless GPU infrastructure for AI",
    },
    {
        "slug": "harvey",
        "name": "Harvey AI",
        "displayName": "Harvey AI",
        "roles": ["ai_app"],
        "region": "US",
        "color": "#0f1d3a",
        "model_type": "proprietary",
        "website": "https://www.harvey.ai",
        "products": ["Harvey Assistant", "Harvey Workflow"],
        "_doc": "Legal AI platform",
    },
    {
        "slug": "cohere",
        "name": "Cohere",
        "displayName": "Cohere",
        "roles": ["model_provider"],
        "region": "Canada",
        "color": "#39594d",
        "model_type": "both",
        "website": "https://cohere.com",
        "products": ["Command", "Embed", "Rerank"],
        "_doc": "Frontier model provider; open + commercial",
    },
    {
        "slug": "cursor",
        "name": "Cursor",
        "displayName": "Cursor",
        "roles": ["ai_app"],
        "region": "US",
        "color": "#000000",
        "model_type": "proprietary",
        "website": "https://cursor.com",
        "products": ["Cursor IDE"],
        "_doc": "AI coding assistant (built by Anysphere)",
    },
    {
        "slug": "super_com",
        "name": "Super.com",
        "displayName": "Super.com",
        "roles": ["ai_app"],
        "region": "US",
        "color": "#ff5e8a",
        "model_type": "proprietary",
        "website": "https://www.super.com",
        "products": ["Super App", "Travel + Finance"],
        "_doc": "Consumer AI travel/finance",
    },
]

# Per brief §5
NEW_MATCH_RULES = [
    {"pattern": "databricks", "slug": "databricks"},
    {"pattern": "\\bscale\\.?ai\\b|scale\\sai\\b", "slug": "scale"},
    {"pattern": "modal\\.com|modal\\s+labs|modal\\s+inc", "slug": "modal"},
    {"pattern": "harvey\\.ai|harvey\\s+legal", "slug": "harvey"},
    {"pattern": "cohere", "slug": "cohere"},
    {"pattern": "cursor\\.com|cursor\\s+ide|anysphere", "slug": "cursor"},
    {"pattern": "super\\.com|super\\s+app", "slug": "super_com"},
]


def _build_entity(spec: dict) -> dict:
    rec = {
        "slug": spec["slug"],
        "name": spec["name"],
        "displayName": spec["displayName"],
        "roles": spec["roles"],
        "region": spec["region"],
        "model_type": spec["model_type"],
        "color": spec["color"],
        "website": spec.get("website"),
        "products": spec.get("products", []),
        "current": {},
        "financials": {},
        "provenance": {
            "_entity_creation": {
                "claim": "Entity created 2026-05-03 to close wq-046 matcher coverage gap; role/region/model_type defaults per editorial classification",
                "source": "wq-046 brief",
                "origin": "editorial_audit_doc_addition",
                "date": DATE,
                "_doc": spec.get("_doc", ""),
            },
        },
    }
    if not rec["website"]:
        del rec["website"]
    return rec


def add_entities(entities: dict) -> tuple[int, list[str]]:
    by_slug = {c.get("slug"): c for c in entities.get("companies") or []}
    added = 0
    log = []
    for spec in NEW_ENTITIES:
        slug = spec["slug"]
        if slug in by_slug:
            log.append(f"SKIP {slug}: already in entities.json")
            continue
        entities["companies"].append(_build_entity(spec))
        added += 1
        log.append(f"ADD {slug}: {spec['name']} (roles={','.join(spec['roles'])}, region={spec['region']})")
    return added, log


def add_match_rules(schema: dict) -> tuple[int, list[str]]:
    rules = schema.setdefault("entity_match_rules", [])
    existing_slugs = {r.get("slug") for r in rules}
    added = 0
    log = []
    for new in NEW_MATCH_RULES:
        if new["slug"] in existing_slugs:
            log.append(f"SKIP rule {new['slug']}: already present")
            continue
        rules.append(new)
        added += 1
        log.append(f"ADD rule {new['slug']}: pattern={new['pattern']}")
    return added, log


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not args.apply and not args.dry_run:
        args.dry_run = True

    entities = json.loads(ENTITIES_PATH.read_text())
    schema = json.loads(SCHEMA_PATH.read_text())

    print("=== wq-046 add 7 missing entities ===\n")
    print("→ 1/2  entities.json:companies")
    n_ent, ent_log = add_entities(entities)
    for line in ent_log:
        print(f"  {line}")
    print(f"  {n_ent} added\n")

    print("→ 2/2  metric-schema.json:entity_match_rules")
    n_rules, rule_log = add_match_rules(schema)
    for line in rule_log:
        print(f"  {line}")
    print(f"  {n_rules} added\n")

    if args.apply:
        ENTITIES_PATH.write_text(json.dumps(entities, indent=2) + "\n")
        SCHEMA_PATH.write_text(json.dumps(schema, indent=2) + "\n")
        print(f"Written: {ENTITIES_PATH}\nWritten: {SCHEMA_PATH}")
    else:
        print("(dry-run)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
