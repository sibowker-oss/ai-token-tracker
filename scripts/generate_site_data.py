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

# wq-042 — entity-directory rendering shares the qualification function with
# scripts/build_entity_pages.py so the directory marks each entity with the
# same `qualifies_for_detail_page` boolean the page builder uses.
sys.path.insert(0, SCRIPT_DIR)
try:
    from build_entity_pages import qualifies_for_detail_page  # noqa: E402
except ImportError:
    qualifies_for_detail_page = None  # graceful fallback

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

    # ── wq-042: build entityDirectory (additive — does not touch dashboard.providers) ──
    # Reads detail-page threshold from data/render_config.json so build_entity_pages.py
    # and site-data.json agree on which entities qualify. Existing pages
    # (revenue.html, capital.html, follow-the-trillion.html) are unaffected.
    render_config_path = os.path.join(ROOT_DIR, "data", "render_config.json")
    threshold = {"min_populated_fields": 3, "min_best_confidence": "medium", "min_provenance_entries": 1}
    try:
        with open(render_config_path) as f:
            threshold = json.load(f).get("detail_page_threshold", threshold)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    directory = []
    for ent in entities.get("companies", []):
        current = ent.get("current") or {}
        prov = ent.get("provenance") or {}
        best_conf = "low"
        rank = {"low": 0, "estimated": 1, "medium": 1, "high": 2, "verified": 2}
        for p in prov.values():
            if isinstance(p, dict):
                c = p.get("confidence", "low")
                if rank.get(c, 0) > rank.get(best_conf, 0):
                    best_conf = c
        qualifies = False
        if qualifies_for_detail_page:
            qualifies, _ = qualifies_for_detail_page(ent, threshold)
        directory.append({
            "slug": ent.get("slug"),
            "name": ent.get("name"),
            "roles": ent.get("roles", []) or [],
            "region": ent.get("region", ""),
            "current": {k: v for k, v in current.items() if v is not None},
            "best_confidence": best_conf,
            "provenance_entry_count": sum(1 for p in prov.values() if isinstance(p, dict) and p.get("claims")),
            "qualifies_for_detail_page": qualifies,
        })
    site["entityDirectory"] = directory

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

    # ── Write output ──
    save_json(output_path, site)

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
