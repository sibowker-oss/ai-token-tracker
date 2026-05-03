#!/usr/bin/env python3
"""wq-070 — Add 5 new model_provider entities (Chinese + self-hosted aggregator).

Adds ByteDance, Alibaba, Tencent, Baidu (Chinese model_providers) + a
synthetic _self_hosted aggregator entity that represents open-model
deployments running on customer infrastructure. Token values per
model-assumptions.md §2.4 v3 consensus midpoints.

Also writes the entity_match_rules into metric-schema.json so future
claims route correctly via apply_decisions.py.

CLI:
  python3 scripts/add_chinese_providers.py --dry-run
  python3 scripts/add_chinese_providers.py --apply  # MUTATES entities.json + metric-schema.json
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

# Per brief §4 + Phase 2 paper math (Simon-confirmed values from
# model-assumptions.md §2.4 v3 consensus midpoints).
NEW_ENTITIES = [
    {
        "slug": "bytedance",
        "name": "ByteDance",
        "displayName": "ByteDance / Doubao",
        "roles": ["model_provider"],
        "region": "China",
        "color": "#000000",
        "model_type": "proprietary",
        "website": "https://www.bytedance.com",
        "products": ["Doubao", "Coze", "Cici"],
        "tokens_per_day": 110,
        "v3_range": "100-120T",
        "claim_id": "audit-20260503-bytedance-tokens",
        "claim_text": "ByteDance/Doubao token volume v3 consensus ~110T/day per model-assumptions.md §2.4 (Volcano Engine 120T disclosure, confirmed by 4/7 models)",
    },
    {
        "slug": "alibaba",
        "name": "Alibaba",
        "displayName": "Alibaba / Qwen",
        "roles": ["model_provider"],
        "region": "China",
        "color": "#ff6a00",
        "model_type": "both",  # open-weights (Qwen) + proprietary
        "website": "https://www.alibabacloud.com",
        "products": ["Qwen (open-weights)", "Tongyi"],
        "tokens_per_day": 25,
        "v3_range": "20-30T",
        "claim_id": "audit-20260503-alibaba-tokens",
        "claim_text": "Alibaba/Qwen token volume v3 consensus ~25T/day per model-assumptions.md §2.4 (5T external + 16-17T internal company statements)",
    },
    {
        "slug": "tencent",
        "name": "Tencent",
        "displayName": "Tencent / Hunyuan",
        "roles": ["model_provider"],
        "region": "China",
        "color": "#1ba1e2",
        "model_type": "proprietary",
        "website": "https://hunyuan.tencent.com",
        "products": ["Hunyuan", "Yuanbao"],
        "tokens_per_day": 10,
        "v3_range": "8-12T",
        "claim_id": "audit-20260503-tencent-tokens",
        "claim_text": "Tencent/Hunyuan token volume v3 consensus ~10T/day per model-assumptions.md §2.4 (market share inference from China 140T total)",
    },
    {
        "slug": "baidu",
        "name": "Baidu",
        "displayName": "Baidu / Ernie",
        "roles": ["model_provider"],
        "region": "China",
        "color": "#2932e1",
        "model_type": "proprietary",
        "website": "https://yiyan.baidu.com",
        "products": ["Ernie", "Wenxin"],
        "tokens_per_day": 8,
        "v3_range": "6-10T",
        "claim_id": "audit-20260503-baidu-tokens",
        "claim_text": "Baidu/Ernie token volume v3 consensus ~8T/day per model-assumptions.md §2.4 (1T/day Aug 2024 + 33x annual growth extrapolation)",
    },
    {
        "slug": "_self_hosted",
        "name": "Self-Hosted Open Models",
        "displayName": "Self-Hosted Open Models",
        "roles": ["aggregator"],
        "region": "Global",
        "color": "#94a3b8",
        "model_type": "open",
        "products": [],
        "tokens_per_day": 30,
        "v3_range": "20-40T",
        "claim_id": "audit-20260503-selfhosted-tokens",
        "claim_text": "Self-hosted open models token volume v3 consensus ~30T/day per model-assumptions.md §2.4 (Llama/Qwen/Mistral on vLLM/Ollama/enterprise GPU)",
        "_synthetic": True,
        "_aggregates": "Open-weight model deployments (Llama, DeepSeek-open, Mistral-open, Qwen, etc.) running on customer infrastructure",
    },
]

# entity_match_rules per brief §3 #7
NEW_MATCH_RULES = [
    {"pattern": "bytedance|doubao|tiktok.*ai|volcano.*engine", "slug": "bytedance"},
    {"pattern": "alibaba|qwen|aliyun|tongyi", "slug": "alibaba"},
    {"pattern": "tencent|hunyuan|wechat.*ai|yuanbao", "slug": "tencent"},
    {"pattern": "baidu|ernie|wenxin|yiyan", "slug": "baidu"},
    {"pattern": "self.host|llama.deployed|open.model.run|on.prem.inference", "slug": "_self_hosted"},
]


def _build_entity_record(spec: dict) -> dict:
    """Build the full entities.json:companies entry for one new provider."""
    rec = {
        "slug": spec["slug"],
        "name": spec["name"],
        "displayName": spec["displayName"],
        "roles": spec["roles"],
        "region": spec["region"],
        "model_type": spec["model_type"],
        "color": spec["color"],
        "products": spec["products"],
        "current": {
            "tokens_per_day": spec["tokens_per_day"],
            "tokens_per_day_date": DATE,
        },
        "financials": {
            "2025": {
                "tokens_per_day_estimate": spec["tokens_per_day"],
            },
        },
        "provenance": {
            "current.tokens_per_day": {
                "confidence": "medium",
                "claim_count": 1,
                "claims": [
                    {
                        "id": spec["claim_id"],
                        "claim": spec["claim_text"],
                        "value": spec["tokens_per_day"],
                        "unit": "T/day",
                        "weight": "indicative",
                        "confidence": "estimated",
                        "source": f"model-assumptions.md §2.4 v3 consensus (range {spec['v3_range']})",
                        "origin": "editorial_audit_doc_addition",
                        "date": DATE,
                        "role": "supports",
                    }
                ],
            },
        },
    }
    if spec.get("website"):
        rec["website"] = spec["website"]
    if spec.get("_synthetic"):
        rec["_synthetic"] = True
        rec["_aggregates"] = spec["_aggregates"]
    return rec


def add_entities(entities: dict) -> tuple[int, list[str]]:
    """Returns (added_count, skipped_log)."""
    by_slug = {c.get("slug"): c for c in entities.get("companies") or []}
    added = 0
    log = []
    for spec in NEW_ENTITIES:
        slug = spec["slug"]
        if slug in by_slug:
            log.append(f"SKIP {slug}: already in entities.json")
            continue
        rec = _build_entity_record(spec)
        entities["companies"].append(rec)
        added += 1
        log.append(f"ADD {slug}: {spec['name']} ({spec['tokens_per_day']}T/day, role={spec['roles'][0]})")
    return added, log


def add_match_rules(schema: dict) -> tuple[int, list[str]]:
    """Returns (added_count, skipped_log)."""
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

    print("=== wq-070 add Chinese + self-hosted providers ===\n")
    print("→ 1/2  entities.json:companies — new entries")
    n_ent, ent_log = add_entities(entities)
    for line in ent_log:
        print(f"  {line}")
    print(f"  {n_ent} added\n")

    print("→ 2/2  metric-schema.json:entity_match_rules — new patterns")
    n_rules, rule_log = add_match_rules(schema)
    for line in rule_log:
        print(f"  {line}")
    print(f"  {n_rules} added\n")

    if args.apply:
        ENTITIES_PATH.write_text(json.dumps(entities, indent=2) + "\n")
        SCHEMA_PATH.write_text(json.dumps(schema, indent=2) + "\n")
        print(f"Written: {ENTITIES_PATH}")
        print(f"Written: {SCHEMA_PATH}")
    else:
        print("(dry-run; pass --apply to write)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
