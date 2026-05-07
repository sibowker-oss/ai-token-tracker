#!/usr/bin/env python3
"""wq-090 — one-time script to populate entity_archetype on every entity.

Archetype taxonomy (per wq-090 brief Phase 2):
  - frontier_lab     — labs that train and serve foundation models
  - ai_native        — AI-native scale-ups (apps built on frontier APIs)
  - enterprise_saas  — traditional SaaS layering AI features
  - hyperscaler      — cloud providers (AWS / Azure / GCP, plus neoclouds for routing)
  - iaas             — token-API aggregators / inference infra (Together, Fireworks, Groq…)
  - consumer_app     — pure consumer chat surfaces (rare; usually rolled under frontier_lab)

Sankey-relevant entities (those routed by derive_sankey.py): model_provider + iaas_provider
roles. Other roles get an archetype too so derive_market_aggregates can apply the
new segment_composition_by_archetype table consistently.

Idempotent — safe to re-run; preserves any pre-existing entity_archetype value.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTITIES_PATH = ROOT / "entities.json"

# Slug → archetype overrides where role-based default is wrong
SLUG_OVERRIDES = {
    # Frontier labs — model_provider role covers all 14 + cohere
    # (no per-slug override needed; default by role)

    # Hyperscalers / neoclouds — all map to "hyperscaler" archetype for routing
    # (neo_cloud role mapped via ROLE_DEFAULTS below)

    # IaaS aggregators / inference providers
    "openrouter": "iaas",
    "portkey": "iaas",
    "_self_hosted": "iaas",
    "_other_closed": "iaas",

    # Databricks: dual role traditional_saas + ai_app — treat as enterprise_saas
    "databricks": "enterprise_saas",
}

# Role → default archetype
ROLE_DEFAULTS = {
    "model_provider": "frontier_lab",
    "iaas_provider": "iaas",
    "hyperscaler": "hyperscaler",
    "neo_cloud": "hyperscaler",  # neoclouds route like hyperscalers
    "traditional_saas": "enterprise_saas",
    "ai_app": "ai_native",
    "aggregator": "iaas",
    "gpu_provider": "hyperscaler",  # GPU providers in Sankey context = infra
}


def archetype_for(entity: dict) -> str:
    slug = entity.get("slug")
    if slug in SLUG_OVERRIDES:
        return SLUG_OVERRIDES[slug]
    for role in entity.get("roles") or []:
        if role in ROLE_DEFAULTS:
            return ROLE_DEFAULTS[role]
    return "ai_native"  # generic fallback


def main() -> None:
    with open(ENTITIES_PATH) as f:
        ent = json.load(f)

    added = 0
    preserved = 0
    archetype_counts: dict[str, int] = {}
    for c in ent.get("companies", []):
        if c.get("entity_archetype"):
            preserved += 1
            archetype_counts[c["entity_archetype"]] = archetype_counts.get(c["entity_archetype"], 0) + 1
            continue
        a = archetype_for(c)
        c["entity_archetype"] = a
        archetype_counts[a] = archetype_counts.get(a, 0) + 1
        added += 1

    with open(ENTITIES_PATH, "w") as f:
        json.dump(ent, f, indent=2)
    print(f"wq-090 archetype assignment: added={added} preserved={preserved}")
    print("Archetype breakdown:")
    for a, n in sorted(archetype_counts.items(), key=lambda kv: -kv[1]):
        print(f"  {a:18} {n}")


if __name__ == "__main__":
    main()
