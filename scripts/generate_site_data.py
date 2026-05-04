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


# ── wq-055 Phase C — write full Sankey from market_aggregates engine output ──

def _apply_sankey_engine_output(target, market, year, is_projections=False):
    """Apply engine output to target dict.

    For site-data.json the target is `site` and we mutate `site["sankey"]`.
    For sankey-projections.json the target is the year block (e.g. sp["2025"])
    and we mutate it directly.

    Per wq-055 §3.2 conservation:
      sum(non-VC buyers) == sum(channels) == total_customer_revenue (engine)
      sum(provider value) == total_provider_value (engine)
      Channels rescale proportionally from existing structure.
      Buyers (non-VC) rescale proportionally; VC = sum(provider vc_subsidy).
      Outcomes: Inference = sum(provider inference_cost),
                People/SG&A = sum(provider opex),
                Op Cash Flow = sum(channel margins).
    """
    sankey = target if is_projections else target["sankey"]

    # Engine totals
    total_cr = market["total_customer_revenue"]
    total_vc = market["total_vc_subsidy"]
    total_provider = market["total_provider_value"]

    # ── Providers list (visible, post-aggregation) ──
    providers_visible_slugs = market.get("providers_visible") or list(market["providers"].keys())
    providers_by_slug = market["providers"]
    other_block = market.get("other_aggregation")

    new_providers = []
    for slug in providers_visible_slugs:
        if slug == (other_block or {}).get("_slug") or (other_block and slug not in providers_by_slug):
            continue
        p = providers_by_slug.get(slug)
        if not p:
            continue
        entry = {
            "label": p["label"],
            "value": p["value"],
            "color": p["color"],
        }
        if is_projections:
            entry["tier"] = _tier_from_origins(p)
            entry["src"] = _src_from_origins(p)
        new_providers.append(entry)
    if other_block:
        entry = {
            "label": other_block["label"],
            "value": other_block["value"],
            "color": other_block["color"],
        }
        if is_projections:
            entry["tier"] = "3C"
            entry["src"] = (
                "wq-055 small-provider aggregation: "
                + ", ".join(other_block["members"])
                + f" ({other_block['aggregation_rule']})"
            )
        new_providers.append(entry)
    sankey["providers"] = new_providers

    # ── costParams.vcSubsidy per provider ──
    # Built from engine output. wq-062: also surfaced on site-data.json:sankey
    # (was sankey-projections.json only) so the per-provider Column C balance
    # validator + renderer can read it from either file.
    new_vc_subsidy = {}
    for slug in providers_visible_slugs:
        p = providers_by_slug.get(slug)
        if p:
            new_vc_subsidy[p["label"]] = round(p["vc_subsidy"], 4)
    if other_block:
        new_vc_subsidy[other_block["label"]] = round(other_block["vc_subsidy"], 4)
    if is_projections and "costParams" in sankey:
        sankey["costParams"]["vcSubsidy"] = new_vc_subsidy

    # ── Channels (wq-062: use engine-grossed values when available) ──
    # market.channels_grossed is the per-channel block from derive_sankey_routing:
    #   [{label, value (gross), chPass (net), margin, gross_up_factor}, ...]
    # Fall back to proportional rescale of the existing channel structure if
    # the routing block isn't present (backward compat with pre-wq-062 data).
    channels_grossed = market.get("channels_grossed") or []
    old_channels = sankey.get("channels") or []
    if channels_grossed:
        # Build label → existing channel dict so we can preserve color/etc.
        old_by_label = {c.get("label"): c for c in old_channels}
        new_channels = []
        for grossed in channels_grossed:
            base = dict(old_by_label.get(grossed["label"]) or {"label": grossed["label"]})
            base["label"] = grossed["label"]
            base["value"] = round(grossed["value"], 4)
            new_channels.append(base)
        sankey["channels"] = new_channels
    elif old_channels:
        # Backward compat — proportional rescale (wq-055 behaviour)
        old_channel_total = sum(c.get("value", 0) for c in old_channels)
        if old_channel_total > 0:
            scale = total_cr / old_channel_total
            new_channels = []
            for c in old_channels:
                nc = dict(c)
                nc["value"] = round(c["value"] * scale, 4)
                new_channels.append(nc)
            sankey["channels"] = new_channels

    # ── Buyers (non-VC = sum(channel.value); VC = engine sum) ──
    # wq-062: with grossed channels, non-VC buyer total = sum(channels gross)
    # to preserve buyer↔channel conservation. Without channels_grossed, fall
    # back to proportional rescale to total_cr (wq-055 behaviour).
    new_channel_total = sum(c.get("value", 0) for c in (sankey.get("channels") or []))
    old_buyers = sankey.get("buyers") or []
    old_non_vc_total = sum(b.get("value", 0) for b in old_buyers if b.get("label") != "VC/Investors")
    target_non_vc = new_channel_total if channels_grossed else total_cr
    if old_buyers and old_non_vc_total > 0:
        scale = target_non_vc / old_non_vc_total
        new_buyers = []
        for b in old_buyers:
            nb = dict(b)
            if b.get("label") == "VC/Investors":
                nb["value"] = round(total_vc, 4)
            else:
                nb["value"] = round(b["value"] * scale, 4)
            new_buyers.append(nb)
        sankey["buyers"] = new_buyers

    # ── Outcomes ──
    # Inference = sum(provider inference_cost)
    # People/SG&A = sum(provider opex)
    # Op Cash Flow = sum(channel margins)
    total_inf = sum(p.get("inference_cost", 0) for p in providers_by_slug.values())
    total_opex = sum(p.get("opex", 0) for p in providers_by_slug.values())
    if other_block:
        # Aggregation node: split by inferencePct 0.50 (its constituents are estimated)
        # Per derive_sankey aggregation, the Other node already sums per-provider
        # inference_cost and opex implicitly through its `value`. Add explicitly
        # using the same per-component pattern.
        for slug in other_block["members"]:
            p = providers_by_slug.get(slug)
            if p:
                # Already counted above (loop is across providers_by_slug)
                pass
    total_inf = round(total_inf, 4)
    total_opex = round(total_opex, 4)

    new_channels = sankey.get("channels") or []
    margin_pcts = {"Hyperscalers": 0.20, "Trad. SaaS": 0.60}
    cashflow = sum(c.get("value", 0) * margin_pcts.get(c.get("label"), 0) for c in new_channels)
    cashflow = round(cashflow, 4)

    old_outcomes = sankey.get("outcomes") or []
    if old_outcomes:
        for o in old_outcomes:
            label = o.get("label", "")
            if label == "Inference":
                o["value"] = total_inf
            elif "People" in label or "SG&A" in label or "Operating Cost" in label or "Other Op" in label:
                o["value"] = total_opex
            elif "Cash" in label or "Margin" in label:
                o["value"] = cashflow

    # ── Top-level totals ──
    sankey["totalCustomerRevenue"] = round(total_cr, 4)
    sankey["totalVCSubsidy"] = round(total_vc, 4)
    sankey["totalSystem"] = round(total_provider + cashflow, 4)
    # wq-063 — buyer-gross customer revenue (= sum(channels grossed) =
    # what customers actually paid, including channel margins kept by
    # Hyperscaler/SaaS resellers). Renderer reads this for the headline
    # Customer Revenue card; net (totalCustomerRevenue) remains for the
    # Sankey provider column / Column-C math.
    gross = market.get("total_customer_revenue_gross")
    if gross is None and channels_grossed:
        gross = round(sum((c.get("value") or 0) for c in channels_grossed), 4)
    if gross is not None:
        sankey["totalCustomerRevenue_gross"] = round(gross, 4)

    # ── wq-062: per-provider routing block ──
    # Renderer reads this to assemble channel→provider flows directly
    # (bypasses proportional routing). Falls back to proportional in
    # buildSankey() if absent (backward compat).
    routing = market.get("routing") or {}
    if routing:
        # Map slug → provider label so the renderer can look up by either.
        sankey["routing"] = routing
        # Also surface the slug on each provider entry so renderer can match.
        provider_label_to_slug = {}
        for slug, p in providers_by_slug.items():
            provider_label_to_slug[p.get("label")] = slug
        if other_block:
            # Other Model Providers slug is a fixed sentinel from cost_structure;
            # also matches the routing dict key written by derive_sankey.
            other_slug = next((k for k in routing.keys() if k.startswith("_other")), "_other_model_providers")
            provider_label_to_slug[other_block.get("label")] = other_slug
        for prov_entry in sankey.get("providers", []):
            slug = provider_label_to_slug.get(prov_entry.get("label"))
            if slug:
                prov_entry["slug"] = slug

    # ── wq-062: surface marginPcts + vcSubsidy on site-data.json:sankey ──
    # site-data.json:sankey didn't carry costParams pre-wq-062. The per-provider
    # Column C balance check (validate-sankey-conservation rule 5) needs both
    # vcSubsidy (per-provider) and marginPcts (to subtract channel margins from
    # the buyers↔providers identity).
    if not is_projections:
        sankey.setdefault("costParams", {})
        sankey["costParams"]["vcSubsidy"] = new_vc_subsidy
        sankey["costParams"]["marginPcts"] = {"Hyperscalers": 0.20, "Trad. SaaS": 0.60}


def _tier_from_origins(p):
    """Per-provider tier derives from weakest cost-component origin.
    Sourced → 1B/2A. Derived → 2A/2B. Estimated → 3C. Override → 1B/3C."""
    origins = (p.get("inference_cost_origin"), p.get("opex_origin"), p.get("vc_origin"))
    if any(o == "estimated" for o in origins):
        return "3C"
    if any(o == "derived" for o in origins):
        return "2A"
    if any(o == "editorial_override" for o in origins):
        return "1B"
    if all(o == "preserved_hand_curated" for o in origins if o):
        return "1B"
    return "2A"


def _src_from_origins(p):
    """Per-provider src string for sankey-projections.json reader."""
    bits = [
        f"customer_revenue=${p.get('customer_revenue', '?')}B (wq-048 engine)",
        f"inference_cost=${p.get('inference_cost', '?')}B ({p.get('inference_cost_origin', '?')})",
        f"opex=${p.get('opex', '?')}B ({p.get('opex_origin', '?')})",
        f"vc_subsidy=${p.get('vc_subsidy', '?')}B ({p.get('vc_origin', '?')})",
    ]
    return "wq-055 engine — " + "; ".join(bits)

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

    # ── wq-063: cumulative aggregates (read from entities.json) ──
    # Mirrors entities.json:market_aggregates._cumulative_2023_2025 into
    # site-data.json:cumulative for index.html SCENARIOS to consume.
    cumulative = (entities.get("market_aggregates") or {}).get("_cumulative_2023_2025")
    if cumulative:
        site["cumulative"] = cumulative

    # ── wq-067: market aggregates per year (read from entities.json) ──
    # Surfaces per-source capex / tokens / segment composition / per-channel
    # totals / derived ratios / YoY deltas for the public site to consume
    # without re-deriving in JS.
    market_section = {}
    for year in ("2023", "2024", "2025"):
        ma_year = (entities.get("market_aggregates") or {}).get(year) or {}
        if not ma_year:
            continue
        # Surface only the public-facing wq-067 fields (skip provenance/internal).
        public_fields = (
            "mag7_capex", "neocloud_capex", "sovereign_capex", "enterprise_capex", "total_capex",
            "tokens_per_day_total", "tokens_annual_inference", "tokens_annual_training",
            "total_segment_consumer", "total_segment_sme", "total_segment_enterprise",
            "total_per_channel",
            "infra_to_revenue_ratio", "capex_per_token_usd", "revenue_per_token_usd",
            "yoy_total_customer_revenue_growth_pct", "yoy_total_capex_growth_pct",
            "yoy_tokens_annual_inference_growth_pct",
            "total_customer_revenue", "total_customer_revenue_gross", "total_vc_subsidy",
        )
        out_year = {k: ma_year.get(k) for k in public_fields if ma_year.get(k) is not None}
        if out_year:
            market_section[year] = out_year
    if market_section:
        site["market"] = market_section

    # ── wq-074: capital sankey (read from entities.json) ──
    # Mirrors entities.json:market_aggregates._capital_sankey into
    # site-data.json:capital_sankey for capital.html to consume via fetch.
    capital_sankey = (entities.get("market_aggregates") or {}).get("_capital_sankey")
    if capital_sankey:
        # Surface public-facing fields only (skip _engine / _engine_run_at / _doc).
        public = {k: v for k, v in capital_sankey.items() if not k.startswith("_")}
        if public:
            site["capital_sankey"] = public

    # ── wq-055: write FULL Sankey from market_aggregates engine output ──
    # Per brief §2 #3: providers, costParams.vcSubsidy, buyers, channels,
    # outcomes, totals — all derived consistently from one engine block.
    market = entities.get("market_aggregates", {}).get("2025", {})
    if market and market.get("providers"):
        _apply_sankey_engine_output(site, market, year="2025")
        # Also write the full Sankey to data/sankey-projections.json so the
        # Sankey renderer (revenue.html, follow-the-trillion.html) reads
        # consistent values from both files.
        sankey_proj_path = os.path.join(SITE_DIR, "data", "sankey-projections.json")
        if os.path.exists(sankey_proj_path):
            with open(sankey_proj_path) as f:
                sp = json.load(f)
            if "2025" in sp:
                _apply_sankey_engine_output(sp["2025"], market, year="2025", is_projections=True)
            with open(sankey_proj_path, "w") as f:
                json.dump(sp, f, indent=2)
            print(f"  Written: {sankey_proj_path} (sankey block, year=2025)")

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
