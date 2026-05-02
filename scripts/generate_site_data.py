#!/usr/bin/env python3
"""
generate_site_data.py — Generates site-data.json from entities.json

Reads the entity-first data model (entities.json) and produces the
presentation-layer site-data.json that all public pages consume.

Sections generated from entities:
  - meta (timestamp + counts)
  - dashboard.providers (current snapshot per model provider)

Sections passed through from existing site-data.json (editorial content):
  - sankey (hand-crafted flows — too complex to auto-derive yet)
  - dashboard.regions, industries, useCases, crossWeights, demandMatrix,
    demandTypes, demandWeights, topConsumers, models, enterpriseReality
  - timeline (quarterly data + editorial events)
  - gateway (live pricing snapshots)
  - calculator (product cost-benefit)

The idea: entities.json is the source of truth for provider metrics.
This script updates the provider cards and timeline latest quarter
from entities, while preserving all editorial/hand-crafted content.
"""

import json
import sys
import os
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
SITE_DIR = ROOT_DIR

def load_json(path):
    with open(path) as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  Written: {path}")

def get_providers(entities):
    """Extract model_provider entities."""
    return [c for c in entities["companies"] if "model_provider" in c.get("roles", [])]

def generate(entities_path, existing_site_data_path, output_path):
    entities = load_json(entities_path)
    site = load_json(existing_site_data_path)

    providers = get_providers(entities)

    # ── Update meta ──
    site["meta"]["generatedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    site["meta"]["source"] = "Generated from entities.json"

    # ── Update dashboard.providers from entity current snapshots ──
    # Map entity slugs to dashboard keys
    SLUG_TO_DASHBOARD_KEY = {
        "openai": "OpenAI",
        "anthropic": "Anthropic",
        "google": "Google/Gemini",
        "meta": "Meta",
        "deepseek": "DeepSeek",
        "mistral": "Mistral",
        "xai": "xAI",
        "minimax": "Minimax",
        "moonshot": "Moonshot",
    }

    for provider in providers:
        slug = provider["slug"]
        dashboard_key = SLUG_TO_DASHBOARD_KEY.get(slug)
        if not dashboard_key:
            continue
        if dashboard_key not in site["dashboard"]["providers"]:
            continue

        current = provider.get("current", {})
        card = site["dashboard"]["providers"][dashboard_key]

        # Update from current snapshot
        if "arr" in current and current["arr"] is not None:
            card["rev"] = current["arr"]
        if "tokens_per_day" in current and current["tokens_per_day"] is not None:
            card["tokens"] = current["tokens_per_day"]
        if "growth_rate" in current and current["growth_rate"] is not None:
            card["growth"] = current["growth_rate"]
        if "consumer_pct" in current:
            card["consumerPct"] = current["consumer_pct"]
        if "biz_pct" in current:
            card["bizPct"] = current["biz_pct"]

    # ── Update timeline latest quarter from entity current snapshots ──
    SLUG_TO_TIMELINE_IDX = {
        "openai": 0, "anthropic": 1, "google": 2, "deepseek": 3,
        "mistral": 4, "xai": 5, "meta": 6, "minimax": 8, "moonshot": 9,
    }

    if "timeline" in site and "revData" in site["timeline"]:
        latest_rev = site["timeline"]["revData"][-1]
        latest_tok = site["timeline"]["tokenData"][-1]

        for provider in providers:
            slug = provider["slug"]
            idx = SLUG_TO_TIMELINE_IDX.get(slug)
            if idx is None:
                continue
            current = provider.get("current", {})
            if "arr" in current and current["arr"] is not None:
                latest_rev[idx] = current["arr"]
            if "tokens_per_day" in current and current["tokens_per_day"] is not None:
                latest_tok[idx] = current["tokens_per_day"]

    # ── Update topConsumers ARR/tokens from ai_app entities ──
    ai_apps = [c for c in entities["companies"] if "ai_app" in c.get("roles", [])]
    app_lookup = {}
    for app in ai_apps:
        app_lookup[app["name"].lower()] = app
        # Also index by slug
        app_lookup[app["slug"].lower()] = app

    for consumer in site["dashboard"].get("topConsumers", []):
        co_name = consumer.get("co", "").lower()
        co_slug = co_name.replace(" ", "-").replace(".", "")
        entity = app_lookup.get(co_name) or app_lookup.get(co_slug)
        if not entity:
            continue

        current = entity.get("current", {})
        financials = entity.get("financials", {})

        # Get latest year financials
        latest_year = None
        for year in sorted(financials.keys(), reverse=True):
            if not year.endswith("_projected"):
                latest_year = year
                break

        year_data = financials.get(latest_year, {}) if latest_year else {}

        # Update ARR
        arr = year_data.get("arr") or current.get("arr")
        if arr is not None:
            if isinstance(arr, (int, float)):
                if arr >= 1:
                    consumer["arrNumeric"] = int(arr * 1e9) if arr < 100 else int(arr)
                else:
                    consumer["arrNumeric"] = int(arr * 1e9)

        # Update tokens
        tokens = current.get("tokens_per_day")
        if tokens is not None:
            if isinstance(tokens, (int, float)):
                consumer["tokensNumeric"] = int(tokens * 1e9) if tokens < 1e6 else int(tokens)

    # ── Update market aggregate totals ──
    market = entities.get("market_aggregates", {}).get("2025", {})
    if market:
        if "total_customer_revenue" in market:
            site["sankey"]["totalCustomerRevenue"] = market["total_customer_revenue"]
        if "total_vc_subsidy" in market:
            site["sankey"]["totalVCSubsidy"] = market["total_vc_subsidy"]
        if "total_system_cost" in market:
            site["sankey"]["totalSystem"] = market["total_system_cost"]
        # Update outcome totals
        if "total_inference_cost" in market and len(site["sankey"].get("outcomes", [])) > 0:
            site["sankey"]["outcomes"][0]["value"] = market["total_inference_cost"]
        if "total_people_cost" in market and len(site["sankey"].get("outcomes", [])) > 1:
            site["sankey"]["outcomes"][1]["value"] = market["total_people_cost"]
        if "total_margin" in market and len(site["sankey"].get("outcomes", [])) > 2:
            site["sankey"]["outcomes"][2]["value"] = market["total_margin"]

    # ── wq-044 wire-completion (Phase 1.2): propagate per-provider engine ──
    # output into site-data.json:sankey.providers AND
    # data/sankey-projections.json:<year>.providers. Without this propagation
    # the rendered Sankey reads stale hand-curated values regardless of what
    # the engine wrote into entities.json:market_aggregates.providers.
    #
    # Single-regenerator approach (option a from the wq-044 wire-completion
    # brief §1.2): generate_site_data.py owns BOTH writes. No separate
    # build_sankey.py — keeps the entry point single and the data flow
    # linear: derive_market_aggregates.py → entities.json → generate_site_data.py
    # → site-data.json + sankey-projections.json → renderer.
    #
    # Slug → display label mapping for sankey-projections.json which uses
    # "Google (Gemini)" / "IaaS/Open" labels (vs site-data.json which uses
    # "Google (Gemini)" / "IaaS"). Keep both shapes in sync with their
    # respective existing schemas.
    if market and isinstance(market.get("providers"), dict):
        provider_block = market["providers"]
        # Preserve order per existing site-data.json:sankey.providers (OpenAI,
        # Anthropic, IaaS, Google) by reading the existing labels and matching
        # by slug-to-label mapping. Unknown slugs append at end.
        existing_sankey_providers = site["sankey"].get("providers") or []
        sankey_label_to_slug = {
            "OpenAI": "openai",
            "Anthropic": "anthropic",
            "Google (Gemini)": "google",
            "Google/Gemini": "google",
            "Meta (Llama)": "meta",
            "Meta": "meta",
            "DeepSeek": "deepseek",
            "Mistral": "mistral",
            "xAI": "xai",
            "Minimax": "minimax",
            "Moonshot": "moonshot",
        }
        new_sankey_providers = []
        seen_slugs = set()
        for existing in existing_sankey_providers:
            slug = sankey_label_to_slug.get(existing.get("label", ""))
            if slug and slug in provider_block:
                p = provider_block[slug]
                new_sankey_providers.append({
                    "label": existing.get("label", p["label"]),
                    "value": round(p["value"], 4),
                    "color": existing.get("color", p["color"]),
                })
                seen_slugs.add(slug)
            else:
                # Preserve aggregation entries (e.g. "IaaS") that don't map to
                # a single entity. Their value stays hand-curated.
                new_sankey_providers.append(existing)
        # Append any model_provider entities not already in the existing
        # sankey.providers list (e.g. small providers DeepSeek/Mistral/xAI).
        # Skip if value=0 to avoid cluttering the chart with zero-value bars.
        for slug, p in provider_block.items():
            if slug in seen_slugs:
                continue
            if p["value"] <= 0:
                continue
            new_sankey_providers.append({
                "label": p["label"],
                "value": round(p["value"], 4),
                "color": p["color"],
            })
        site["sankey"]["providers"] = new_sankey_providers

    # ── Write output ──
    save_json(output_path, site)

    # ── wq-044 wire-completion (Phase 1.2): also regenerate sankey-projections.json ──
    sankey_proj_path = os.path.join(SITE_DIR, "data", "sankey-projections.json")
    if os.path.exists(sankey_proj_path) and market and isinstance(market.get("providers"), dict):
        sankey_proj = load_json(sankey_proj_path)
        year_block = sankey_proj.get("2025") or {}
        existing_proj_providers = year_block.get("providers") or []
        sankey_label_to_slug_proj = {
            "OpenAI": "openai",
            "Anthropic": "anthropic",
            "Google (Gemini)": "google",
            "IaaS/Open": None,
            "Meta (Llama)": "meta",
            "DeepSeek": "deepseek",
            "Mistral": "mistral",
            "xAI": "xai",
            "Minimax": "minimax",
            "Moonshot": "moonshot",
        }
        new_proj_providers = []
        for existing in existing_proj_providers:
            slug = sankey_label_to_slug_proj.get(existing.get("label", ""))
            if slug and slug in market["providers"]:
                p = market["providers"][slug]
                tier = p.get("tier", "3C")
                src = (
                    f"wq-044 engine-derived from entities.json:market_aggregates.2025.providers.{slug} "
                    f"(${p['customer_revenue']}B customer + ${p['vc_subsidy']}B {p['subsidy_source'].split(' ')[0]})"
                )
                new_proj_providers.append({
                    "label": existing.get("label", p["label"]),
                    "value": round(p["value"], 4),
                    "color": existing.get("color", p["color"]),
                    "tier": tier,
                    "src": src,
                })
            else:
                # Preserve aggregation entries (IaaS/Open).
                new_proj_providers.append(existing)
        year_block["providers"] = new_proj_providers
        if "total_customer_revenue" in market:
            year_block["totalCustomerRevenue"] = market["total_customer_revenue"]
        if "total_vc_subsidy" in market:
            year_block["totalVCSubsidy"] = market["total_vc_subsidy"]
        sankey_proj["2025"] = year_block
        save_json(sankey_proj_path, sankey_proj)

    # ── Summary ──
    provider_count = len([p for p in providers if SLUG_TO_DASHBOARD_KEY.get(p["slug"])])
    consumer_count = len(ai_apps)
    print(f"  Updated {provider_count} provider cards, {consumer_count} AI apps tracked")
    print(f"  Market totals: customer rev ${market.get('total_customer_revenue', '?')}B, VC subsidy ${market.get('total_vc_subsidy', '?')}B")


if __name__ == "__main__":
    # Default paths: beta/entities.json → beta/site-data.json
    entities_path = os.path.join(SITE_DIR, "entities.json")
    existing_path = os.path.join(SITE_DIR, "site-data.json")
    output_path = os.path.join(SITE_DIR, "site-data.json")

    # Allow overriding via CLI args
    if len(sys.argv) > 1:
        entities_path = sys.argv[1]
    if len(sys.argv) > 2:
        existing_path = sys.argv[2]
    if len(sys.argv) > 3:
        output_path = sys.argv[3]

    print("generate_site_data.py")
    print(f"  Entities: {entities_path}")
    print(f"  Existing: {existing_path}")
    print(f"  Output:   {output_path}")
    generate(entities_path, existing_path, output_path)
    print("  Done.")
