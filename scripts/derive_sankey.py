#!/usr/bin/env python3
"""wq-055 — Sankey balancing engine.

Per-component reliability hierarchy (sourced > derived > estimated):

  customer_revenue   — wq-048 engine output (collected_revenue field)
  inference_cost     — TIER 1 sourced (entity field) → TIER 2 derived → TIER 3 estimated
  opex               — TIER 1 sourced (entity field) → TIER 2 derived → TIER 3 estimated
  vc_subsidy         — DERIVED balancing plug = max(0, provider_total - customer_revenue)

Phase A confirmation (Simon 2026-05-03):
  1. Opex TIER 2 condition uses LITERAL pseudocode (interpretation A):
     requires entity-field `inference_cost` present; otherwise falls to
     TIER 3 size_band estimate. Anthropic stays at TIER 3 estimated for
     both inf and opex, producing $7.30B (within ±15% band).

  2. reference_revenue convention (b) §7.2 published-at-time: use the
     customer revenue figure that was published in the Sankey
     methodology AT THE TIME the operating_loss claim was made. For
     OpenAI 2025: ref_revenue = $7.65B (the prior hand-curated value).
     Backfill via scripts/backfill_reference_revenue.py.

  3. Override consistency (Simon 2026-05-03): when vc_subsidy override
     fires, provider_total is forced to (cr + override) to maintain
     Sankey conservation. This intentionally breaks engine consistency
     (inf + opex no longer equals provider_total). Engine logs both
     the engine-derived value AND the override-forced value so the
     audit trail shows what the engine wanted vs what editorial chose.

CLI:
  python3 scripts/derive_sankey.py --validate
  python3 scripts/derive_sankey.py --backfill --dry-run
  python3 scripts/derive_sankey.py --backfill --apply       # MUTATES entities.json
  python3 scripts/derive_sankey.py --entity openai --year 2025
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from log_run import logged_run  # noqa: E402

ENTITIES_PATH = ROOT / "entities.json"
COST_STRUCTURE_PATH = ROOT / "data" / "sankey_cost_structure.json"
OVERRIDES_PATH = ROOT / "data" / "consensus_overrides.json"
VALIDATION_REPORT_PATH = ROOT / "data" / "wq-055-validation-report.txt"
BACKFILL_REPORT_PATH = ROOT / "data" / "wq-055-backfill-report.txt"
CONSENSUS_LOG_PATH = ROOT / "data" / "consensus_log.md"


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_cost_structure() -> dict:
    with open(COST_STRUCTURE_PATH) as f:
        return json.load(f)


def load_overrides() -> dict:
    if not OVERRIDES_PATH.exists():
        return {}
    with open(OVERRIDES_PATH) as f:
        d = json.load(f)
    # Strip _doc / _schema_example keys so override key lookups are clean
    return {k: v for k, v in d.items() if not k.startswith("_")}


def load_entities() -> dict:
    with open(ENTITIES_PATH) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Reference revenue lookup (per Phase A confirmation 2 — convention b)
# ---------------------------------------------------------------------------

def reference_revenue_for(entity: dict, year: str, field: str,
                          default: Optional[float] = None) -> tuple[Optional[float], str]:
    """Return (ref_revenue, origin_str) for a given operating_loss claim.

    Convention (b) §7.2 published-at-time: walks the provenance entry for the
    given field; reads `reference_revenue` if backfill has populated it.
    Falls back to `default` (typically current cr) if absent and logs a
    warning origin string so the caller can flag the resulting derivation
    as low-confidence.
    """
    prov = (entity.get("provenance") or {}).get(f"{year}.{field}") or {}
    for c in (prov.get("claims") or []):
        if c.get("role") == "superseded":
            continue
        if "reference_revenue" in c:
            return (c["reference_revenue"], f"{entity['slug']}.{year}.{field}.reference_revenue")
    if default is not None:
        return (default, f"fallback to current cr (ref_revenue not backfilled)")
    return (None, "absent")


# ---------------------------------------------------------------------------
# Component resolvers — per brief §3.1
# ---------------------------------------------------------------------------

def _fin(entity: dict, year: str, field: str):
    f = (entity.get("financials") or {}).get(year) or {}
    return f.get(field)


def resolve_inference_cost(entity: dict, year: str, cost_structure: dict) -> tuple[float, str, list[str]]:
    """Returns (value, origin, derived_from). Sourced > Derived > Estimated."""
    cr = _fin(entity, year, "collected_revenue")
    inf = _fin(entity, year, "inference_cost")
    op_loss = _fin(entity, year, "operating_loss")
    opex_estimate = _fin(entity, year, "opex")  # rare

    # TIER 1 — sourced (e.g. Zitron leak for OpenAI 2025 = $5B)
    if inf is not None:
        return (inf, "sourced", [f"{entity['slug']}.{year}.inference_cost"])

    # TIER 2 — derived from operating_loss math
    if op_loss is not None and cr is not None and opex_estimate is not None:
        ref_revenue, ref_origin = reference_revenue_for(entity, year, "operating_loss", default=cr)
        derived = max(0, op_loss + ref_revenue - opex_estimate)
        return (derived, "derived",
                [f"{entity['slug']}.{year}.operating_loss",
                 f"{entity['slug']}.{year}.opex",
                 f"reference_revenue={ref_revenue} ({ref_origin})"])

    # TIER 3 — estimated
    cs = cost_structure["inference_estimation"]
    rate = cs.get("providerRates", {}).get(entity["slug"], cs["providerRates"].get("_default", cs["default_rate"]))
    return ((cr or 0) * rate, "estimated",
            [f"customer_revenue × {rate} (provider rate from cost_structure)"])


def resolve_opex(entity: dict, year: str, cost_structure: dict) -> tuple[float, str, list[str]]:
    """Returns (value, origin, derived_from). Sourced rare; mostly estimated.

    INTERPRETATION A confirmed by Simon 2026-05-03: TIER 2 condition checks
    entity-field `inference_cost` (literal pseudocode). When entity-field
    inf is absent, falls to TIER 3 size_band even if a TIER 3 inference
    estimate could be computed.
    """
    cr = _fin(entity, year, "collected_revenue")
    opex = _fin(entity, year, "opex")
    op_loss = _fin(entity, year, "operating_loss")
    inf = _fin(entity, year, "inference_cost")

    # TIER 1 — sourced (rare; companies don't usually break out opex)
    if opex is not None:
        return (opex, "sourced", [f"{entity['slug']}.{year}.opex"])

    # TIER 2 — derived from operating_loss math
    # INTERPRETATION A: requires entity-field `inf` (not resolved value).
    if op_loss is not None and cr is not None and inf is not None:
        ref_revenue, ref_origin = reference_revenue_for(entity, year, "operating_loss", default=cr)
        derived = max(0, op_loss + ref_revenue - inf)
        return (derived, "derived",
                [f"{entity['slug']}.{year}.operating_loss",
                 f"{entity['slug']}.{year}.inference_cost",
                 f"reference_revenue={ref_revenue} ({ref_origin})"])

    # TIER 3 — estimated by size band
    cs = cost_structure["opex_estimation"]
    rate = _opex_rate_for_size_band(cr or 0, cs["size_bands"])
    return ((cr or 0) * rate, "estimated",
            [f"customer_revenue × {rate} (opex rate from size band)"])


def _opex_rate_for_size_band(cr: float, size_bands: list[dict]) -> float:
    """Find the first band whose max_revenue >= cr (or null = unbounded)."""
    for band in size_bands:
        max_rev = band.get("max_revenue")
        if max_rev is None or cr <= max_rev:
            return band["rate"]
    return size_bands[-1]["rate"]


# ---------------------------------------------------------------------------
# Override resolution
# ---------------------------------------------------------------------------

def _override_active(ov: dict, today: Optional[str] = None) -> bool:
    expires = ov.get("expires_at")
    if not expires:
        return True
    today = today or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return today < expires


def _vc_subsidy_override(slug: str, year: str, overrides: dict) -> Optional[dict]:
    key = f"{slug}.{year}.vc_subsidy"
    ov = overrides.get(key)
    if ov and _override_active(ov):
        return ov
    return None


def _cost_param_override(year: str, path: str, overrides: dict):
    """Look up cost-structure parameter override like `2025.cost_structure.providerRates.openai`."""
    key = f"{year}.cost_structure.{path}"
    ov = overrides.get(key)
    if ov and _override_active(ov):
        return ov
    return None


# ---------------------------------------------------------------------------
# Per-provider derivation
# ---------------------------------------------------------------------------

def derive_provider(entity: dict, year: str, cost_structure: dict, overrides: dict) -> Optional[dict]:
    """Run the §3.1 algorithm for one model_provider entity.

    Returns the provider block (or None if entity has no collected_revenue).
    """
    cr = _fin(entity, year, "collected_revenue")
    if cr is None or cr == 0:
        return None

    inf, inf_origin, inf_from = resolve_inference_cost(entity, year, cost_structure)
    opex, opex_origin, opex_from = resolve_opex(entity, year, cost_structure)

    # Provider total from documented/derived/estimated outflows
    engine_provider_total = inf + opex
    engine_vc_subsidy = max(0, engine_provider_total - cr)

    # Apply vc_subsidy override per Phase A confirmation 3:
    # override forces provider_total = cr + override.value (Sankey conservation)
    # but engine logs BOTH the engine-derived total AND the override-forced
    # value with a discrepancy flag — auditable trail.
    slug = entity["slug"]
    ov = _vc_subsidy_override(slug, year, overrides)
    override_discrepancy = None
    if ov is not None:
        vc_subsidy = ov["value"]
        provider_total = cr + vc_subsidy
        vc_origin = "editorial_override"
        if abs(provider_total - engine_provider_total) > 0.001:
            override_discrepancy = {
                "engine_provider_total": round(engine_provider_total, 4),
                "engine_vc_subsidy": round(engine_vc_subsidy, 4),
                "override_provider_total": round(provider_total, 4),
                "override_vc_subsidy": vc_subsidy,
                "delta_total": round(provider_total - engine_provider_total, 4),
                "reason": ov.get("reason", ""),
                "expires_at": ov.get("expires_at"),
                "set_by": ov.get("set_by"),
                "set_at": ov.get("set_at"),
            }
    else:
        vc_subsidy = engine_vc_subsidy
        provider_total = engine_provider_total
        vc_origin = "balancing_plug_derived"

    # Display name + colour from entity (or inferred)
    display = {
        "label": entity.get("name", slug),
        "color": entity.get("color", "#888"),
    }

    # wq-062 — capture revenue_by_channel (may be None) so derive_sankey_routing
    # can split per-provider customer_revenue across Sankey channels.
    revenue_by_channel = _fin(entity, year, "revenue_by_channel")
    # wq-090 — capture entity_archetype so per-archetype channel + buyer-segment
    # routing can read it. Falls back to "_default" downstream when missing.
    entity_archetype = entity.get("entity_archetype")

    return {
        "slug": slug,
        "label": display["label"],
        "color": display["color"],
        "customer_revenue": round(cr, 4),
        "inference_cost": round(inf, 4),
        "inference_cost_origin": inf_origin,
        "inference_cost_derived_from": inf_from,
        "opex": round(opex, 4),
        "opex_origin": opex_origin,
        "opex_derived_from": opex_from,
        "vc_subsidy": round(vc_subsidy, 4),
        "vc_origin": vc_origin,
        "value": round(provider_total, 4),
        "override_discrepancy": override_discrepancy,
        "revenue_by_channel": revenue_by_channel,
        "entity_archetype": entity_archetype,
    }


# ---------------------------------------------------------------------------
# Small-provider aggregation — per brief §5
# ---------------------------------------------------------------------------

def aggregate_small_providers(providers: list[dict], cost_structure: dict) -> list[dict]:
    """Collapse providers below threshold_pct of total (and outside top
    min_visible_rank) into 'Other Model Providers' node. Single-member
    Other → keep visible (Other-with-one-member is silly)."""
    cfg = cost_structure["small_provider_aggregation"]
    threshold_pct = cfg["threshold_pct"]
    min_visible = cfg["min_visible_rank"]

    if not providers:
        return providers

    sorted_provs = sorted(providers, key=lambda p: p["value"], reverse=True)
    total = sum(p["value"] for p in providers)
    threshold = total * threshold_pct

    visible = []
    aggregated = []
    for rank, p in enumerate(sorted_provs):
        if rank < min_visible or p["value"] >= threshold:
            visible.append(p)
        else:
            aggregated.append(p)

    if len(aggregated) <= 1:
        # Single-member Other is silly; keep the member visible
        visible.extend(aggregated)
        return visible

    other = {
        "slug": cfg["other_node_slug"],
        "label": cfg["other_node_label"],
        "color": cfg["other_node_color"],
        "customer_revenue": round(sum(p["customer_revenue"] for p in aggregated), 4),
        "vc_subsidy": round(sum(p["vc_subsidy"] for p in aggregated), 4),
        "value": round(sum(p["value"] for p in aggregated), 4),
        "members": [p["slug"] for p in aggregated],
        "vc_origin": "small_provider_aggregation",
        "aggregation_rule": f"value < {threshold_pct*100:.1f}% of total AND outside top {min_visible}",
    }
    visible.append(other)
    return visible


# ---------------------------------------------------------------------------
# wq-062 — per-provider-per-channel routing
# ---------------------------------------------------------------------------

def _archetype_splits(channel_mapping: dict, archetype: str | None,
                       table_key: str) -> list[dict]:
    """Resolve api_pct_by_archetype / enterprise_pct_by_archetype splits for a
    given archetype, falling back to `_default` when the archetype key is
    absent. Returns the list of {channel, weight} dicts (empty list if no
    table is configured)."""
    table = channel_mapping.get(table_key) or {}
    if not isinstance(table, dict):
        return []
    return list(table.get(archetype) or table.get("_default") or [])


def _routing_for_provider(provider: dict, channel_mapping: dict) -> dict:
    """Compute one provider's per-channel net routing values.

    Returns {channel_label: value_net_to_provider}. Sums to provider's
    customer_revenue exactly (modulo float rounding).

    wq-090 — channel routing is now per-archetype:
      - subscription_pct uses the flat `subscription_pct` splits (always 100% Model Subs)
      - api_pct uses `api_pct_by_archetype[entity_archetype]` (frontier_lab → ~95/5
        Model API/Hyperscalers; ai_native → 90/10; enterprise_saas → 50/50; etc.)
      - enterprise_pct uses `enterprise_pct_by_archetype[entity_archetype]`
      - Falls back to `_default` table entries when the archetype is missing.

    Backward compat: if the cost-structure file still has the wq-062 flat
    `api_pct` / `enterprise_pct` lists (no `_by_archetype`), the engine reuses
    them as if they were the `_default` row of the archetype table.
    """
    cr = provider.get("customer_revenue") or 0
    rbc = provider.get("revenue_by_channel")
    archetype = provider.get("entity_archetype")
    routing = {}

    if rbc:
        # Subscription — flat (consumer-app channel mix for all archetypes)
        sub_splits = channel_mapping.get("subscription_pct") or []
        sub_pct = (rbc.get("subscription_pct", 0) or 0) / 100.0
        for split in sub_splits:
            routing[split["channel"]] = routing.get(split["channel"], 0) + cr * sub_pct * split["weight"]

        # API — per-archetype (with backward-compat fallback to flat api_pct)
        api_splits = _archetype_splits(channel_mapping, archetype, "api_pct_by_archetype")
        if not api_splits:
            api_splits = channel_mapping.get("api_pct") or []
        api_pct = (rbc.get("api_pct", 0) or 0) / 100.0
        for split in api_splits:
            routing[split["channel"]] = routing.get(split["channel"], 0) + cr * api_pct * split["weight"]

        # Enterprise — per-archetype (with backward-compat fallback to flat enterprise_pct)
        ent_splits = _archetype_splits(channel_mapping, archetype, "enterprise_pct_by_archetype")
        if not ent_splits:
            ent_splits = channel_mapping.get("enterprise_pct") or []
        ent_pct = (rbc.get("enterprise_pct", 0) or 0) / 100.0
        for split in ent_splits:
            routing[split["channel"]] = routing.get(split["channel"], 0) + cr * ent_pct * split["weight"]
    else:
        # Default split — apply percentages to cr directly
        defaults = channel_mapping.get("_default_for_unmapped") or {}
        for ch, pct in defaults.items():
            if ch.startswith("_"):
                continue
            routing[ch] = routing.get(ch, 0) + cr * pct

    return {ch: round(v, 4) for ch, v in routing.items() if v > 0}


def derive_buyer_channel_matrix(providers_pre_aggregation: list[dict],
                                 channel_mapping: dict,
                                 segment_comp_by_archetype: dict,
                                 channel_margins: dict) -> dict:
    """wq-090 — per-(buyer, channel) gross-value matrix.

    The Revenue Ledger Sankey renderer used to compute buyer→channel ribbon
    values via flat proportional rescale (each buyer flows to each channel
    pro-rata to channel size). That mis-attributed AI-Native cohort spend to
    Model Subs, since AI Natives are companies with thin headcount that hit
    APIs — not consumers paying for Subs.

    The per-archetype engine math already determines which channels each
    buyer's dollars flow through:

      - Consumer dollars = sum of provider × subscription_pct           → Model Subs (always)
      - AI Natives dollars = sum of provider × api_pct × seg.api_to_ai_natives
        → routed via api_pct_by_archetype (Model API + Hyperscalers)
      - Ents & Govs dollars = api_pct × seg.api_to_ents_govs (same channels)
        + enterprise_pct                              → Trad. SaaS + Hyperscalers per archetype

    For rbc-less entities, _default_for_unmapped channels × _default_split
    buyer breakdown are applied as an outer product. This matrix is then
    surfaced on `market_aggregates.<year>.buyer_channel_matrix` so the
    renderer can emit ribbons keyed to the actual underlying flow rather
    than rescale them proportionally.

    Returns: {buyer_label: {channel_label: gross_value}}.
    """
    matrix: dict[str, dict[str, float]] = {
        "Consumer": {},
        "AI Natives": {},
        "Enterprises & Govs": {},
    }

    def _add(buyer, channel, value):
        if value <= 0:
            return
        matrix.setdefault(buyer, {})
        matrix[buyer][channel] = matrix[buyer].get(channel, 0.0) + value

    def _gross(channel, value):
        margin = channel_margins.get(channel, 0)
        factor = (1.0 / (1.0 - margin)) if margin < 1 else 1.0
        return value * factor

    for p in providers_pre_aggregation:
        cr = p.get("customer_revenue") or 0
        if not cr:
            continue
        rbc = p.get("revenue_by_channel")
        archetype = p.get("entity_archetype")
        seg = (segment_comp_by_archetype.get(archetype)
               or segment_comp_by_archetype.get("_default")
               or {})

        if rbc:
            sub_pct = (rbc.get("subscription_pct", 0) or 0) / 100.0
            api_pct = (rbc.get("api_pct", 0) or 0) / 100.0
            ent_pct = (rbc.get("enterprise_pct", 0) or 0) / 100.0

            # Subscription → Consumer (route via subscription_pct splits, gross)
            for split in (channel_mapping.get("subscription_pct") or []):
                v = _gross(split["channel"], cr * sub_pct * split["weight"])
                _add("Consumer", split["channel"], v * seg.get("subscription_to_consumer", 1.0))

            # API → AI Natives + Ents & Govs (route via api_pct_by_archetype splits)
            api_splits = _archetype_splits(channel_mapping, archetype, "api_pct_by_archetype") \
                or (channel_mapping.get("api_pct") or [])
            for split in api_splits:
                v = _gross(split["channel"], cr * api_pct * split["weight"])
                _add("AI Natives", split["channel"], v * seg.get("api_to_ai_natives", 0.4))
                _add("Enterprises & Govs", split["channel"], v * seg.get("api_to_ents_govs", 0.6))

            # Enterprise → Ents & Govs (route via enterprise_pct_by_archetype splits)
            ent_splits = _archetype_splits(channel_mapping, archetype, "enterprise_pct_by_archetype") \
                or (channel_mapping.get("enterprise_pct") or [])
            for split in ent_splits:
                v = _gross(split["channel"], cr * ent_pct * split["weight"])
                _add("Enterprises & Govs", split["channel"], v * seg.get("enterprise_to_ents_govs", 1.0))
        else:
            # No rbc — channel-aware buyer attribution. Each channel slice
            # routes only to the buyers that realistically use that channel:
            # Subs is consumer-only; Trad. SaaS is ents-govs-only; APIs and
            # Hyperscalers are split between AI Natives and Ents & Govs;
            # AI Native Apps mixes all three. Avoids the rbc-less leakage of
            # AI Natives → Model Subs that the prior flat _default_split
            # produced.
            defaults = channel_mapping.get("_default_for_unmapped") or {}
            for ch, pct in defaults.items():
                if ch.startswith("_"):
                    continue
                grossed = _gross(ch, cr * pct)
                if ch == "Model Subs":
                    _add("Consumer", ch, grossed)
                elif ch == "Trad. SaaS":
                    _add("Enterprises & Govs", ch, grossed)
                elif ch == "Model API":
                    _add("AI Natives", ch, grossed * 0.50)
                    _add("Enterprises & Govs", ch, grossed * 0.50)
                elif ch == "Hyperscalers":
                    _add("AI Natives", ch, grossed * 0.30)
                    _add("Enterprises & Govs", ch, grossed * 0.70)
                elif ch == "AI Native Apps":
                    _add("Consumer", ch, grossed * 0.40)
                    _add("AI Natives", ch, grossed * 0.30)
                    _add("Enterprises & Govs", ch, grossed * 0.30)
                else:
                    # Unknown channel — fall back to even split so we don't drop value
                    _add("Consumer", ch, grossed * 0.34)
                    _add("AI Natives", ch, grossed * 0.33)
                    _add("Enterprises & Govs", ch, grossed * 0.33)

    # Round to 4dp and drop near-zero entries so the renderer doesn't draw 0-value ribbons
    out: dict[str, dict[str, float]] = {}
    for buyer, ch_map in matrix.items():
        ch_round = {ch: round(v, 4) for ch, v in ch_map.items() if v > 0.005}
        if ch_round:
            out[buyer] = ch_round
    return out


def derive_buyer_provider_routing(raw_providers: list[dict],
                                   buyer_segments_gross: dict,
                                   buyer_channel_matrix: dict,
                                   channel_margins: dict,
                                   buyer_provider_split: dict) -> dict:
    """wq-090 — per-buyer-per-provider net-revenue allocation.

    Inputs:
      raw_providers           — engine providers (slug + customer_revenue)
      buyer_segments_gross    — {buyer: gross_total} from derive_buyer_segments
      buyer_channel_matrix    — {buyer: {channel: gross}} from derive_buyer_channel_matrix
      channel_margins         — {channel: margin_pct}
      buyer_provider_split    — editorial table from cost_structure (e.g. AI Natives 45/45/10)

    Output:
      {buyer_label: {provider_slug: net_value}}

    Conservation:
      sum_buyers  buyer_provider_routing[B][P] == provider.customer_revenue (within rounding)
      sum_provs   buyer_provider_routing[B][P] == buyer_net (sum_C matrix[B][C] × (1-margin[C]))

    Logic:
      1. Compute each buyer's NET total (gross minus channel margins per the matrix).
      2. Compute Consumer split engine-side from per-provider subscription_pct rollup
         (Consumer money flows entirely from subscription_pct; allocate per provider).
      3. Apply editorial split to AI Natives (or other named buyers).
      4. Back-solve Ents & Govs as the residual: Ents = provider.cr − Consumer × c_split − AI Natives × an_split.
         Floor at 0 to avoid negatives if editorial split overshoots.
    """
    # Per-buyer NET totals (post channel margin)
    buyer_net = {}
    for buyer, ch_map in (buyer_channel_matrix or {}).items():
        net = 0.0
        for ch, gross in (ch_map or {}).items():
            margin = channel_margins.get(ch, 0)
            net += gross * (1 - margin)
        buyer_net[buyer] = round(net, 4)

    # Provider customer_revenue totals (net)
    prov_cr = {p["slug"]: (p.get("customer_revenue") or 0) for p in raw_providers}
    if not prov_cr:
        return {}

    # Step 2 — Consumer split derives from per-provider subscription_pct rollup
    # (Consumer money is the Model Subs channel by construction)
    consumer_total_net = buyer_net.get("Consumer", 0)
    consumer_to_provider = {}
    for p in raw_providers:
        slug = p["slug"]
        cr = p.get("customer_revenue") or 0
        rbc = p.get("revenue_by_channel")
        if rbc:
            sub_pct = (rbc.get("subscription_pct", 0) or 0) / 100.0
            consumer_to_provider[slug] = cr * sub_pct
        else:
            # rbc-less: use _default_for_unmapped Model Subs share — engine routing already
            # captures this via routing[provider][Model Subs]
            consumer_to_provider[slug] = 0.0
    # Top up rbc-less providers with Model Subs share of total cr (mirrors _default_for_unmapped)
    for p in raw_providers:
        slug = p["slug"]
        if consumer_to_provider.get(slug, 0) == 0:
            cr = p.get("customer_revenue") or 0
            # Default Subs share is 0.4 per _default_for_unmapped. Documented in cost_structure.
            consumer_to_provider[slug] = cr * 0.4
    # Normalise so Consumer total matches buyer_net["Consumer"]
    c_sum = sum(consumer_to_provider.values())
    if c_sum > 0 and consumer_total_net > 0:
        scale = consumer_total_net / c_sum
        for slug in consumer_to_provider:
            consumer_to_provider[slug] *= scale

    # Step 3 — AI Natives split per editorial table
    ai_natives_total_net = buyer_net.get("AI Natives", 0)
    an_split = (buyer_provider_split or {}).get("AI Natives") or {}
    an_to_provider = {}
    for slug, cr in prov_cr.items():
        weight = an_split.get(slug, 0)
        an_to_provider[slug] = ai_natives_total_net * weight

    # Step 4 — Ents & Govs back-solves to satisfy each provider's CR
    ents_to_provider = {}
    for slug, cr in prov_cr.items():
        residual = cr - consumer_to_provider.get(slug, 0) - an_to_provider.get(slug, 0)
        ents_to_provider[slug] = max(0.0, residual)

    return {
        "Consumer": {slug: round(v, 4) for slug, v in consumer_to_provider.items() if v > 0.005},
        "AI Natives": {slug: round(v, 4) for slug, v in an_to_provider.items() if v > 0.005},
        "Enterprises & Govs": {slug: round(v, 4) for slug, v in ents_to_provider.items() if v > 0.005},
    }


def derive_buyer_segments(providers_pre_aggregation: list[dict],
                           channel_mapping: dict,
                           segment_comp_by_archetype: dict,
                           channel_margins: dict) -> dict:
    """wq-090 — per-archetype buyer-segment routing in GROSS terms.

    For each provider, the customer-paid amount through each channel is the
    chPass × 1/(1-margin) for that channel. We then split that gross amount
    into Consumer / AI Natives / Enterprises & Govs per the archetype's
    segment_composition row:
      - subscription_pct  → 100% Consumer
      - api_pct           → split api_to_ai_natives / api_to_ents_govs
      - enterprise_pct    → 100% Enterprises & Govs

    Conservation: sum of returned values ≈ sum(channels gross) (the buyer↔
    channel identity the renderer relies on).
    """
    consumer = ai_natives = ents_govs = 0.0
    for p in providers_pre_aggregation:
        cr = p.get("customer_revenue") or 0
        if not cr:
            continue
        rbc = p.get("revenue_by_channel")
        archetype = p.get("entity_archetype")
        seg = (segment_comp_by_archetype.get(archetype)
               or segment_comp_by_archetype.get("_default")
               or {})

        if rbc:
            sub_pct = (rbc.get("subscription_pct", 0) or 0) / 100.0
            api_pct = (rbc.get("api_pct", 0) or 0) / 100.0
            ent_pct = (rbc.get("enterprise_pct", 0) or 0) / 100.0

            sub_splits = channel_mapping.get("subscription_pct") or []
            api_splits = _archetype_splits(channel_mapping, archetype, "api_pct_by_archetype") \
                or (channel_mapping.get("api_pct") or [])
            ent_splits = _archetype_splits(channel_mapping, archetype, "enterprise_pct_by_archetype") \
                or (channel_mapping.get("enterprise_pct") or [])

            def gross(splits, pct):
                total = 0.0
                for s in splits:
                    margin = channel_margins.get(s["channel"], 0)
                    factor = (1.0 / (1.0 - margin)) if margin < 1 else 1.0
                    total += cr * pct * s["weight"] * factor
                return total

            consumer += gross(sub_splits, sub_pct) * (seg.get("subscription_to_consumer", 1.0))
            api_grossed = gross(api_splits, api_pct)
            ai_natives += api_grossed * (seg.get("api_to_ai_natives", 0.4))
            ents_govs += api_grossed * (seg.get("api_to_ents_govs", 0.6))
            ents_govs += gross(ent_splits, ent_pct) * (seg.get("enterprise_to_ents_govs", 1.0))
        else:
            # No rbc — use _default_for_unmapped channel split, then default segment split
            defaults = channel_mapping.get("_default_for_unmapped") or {}
            grossed = 0.0
            for ch, pct in defaults.items():
                if ch.startswith("_"):
                    continue
                margin = channel_margins.get(ch, 0)
                factor = (1.0 / (1.0 - margin)) if margin < 1 else 1.0
                grossed += cr * pct * factor
            ds = segment_comp_by_archetype.get("_default_split") \
                or {"consumer": 0.4, "ai_natives": 0.2, "ents_govs": 0.4}
            consumer += grossed * ds.get("consumer", 0.4)
            ai_natives += grossed * ds.get("ai_natives", 0.2)
            ents_govs += grossed * ds.get("ents_govs", 0.4)

    return {
        "Consumer": round(consumer, 4),
        "AI Natives": round(ai_natives, 4),
        "Enterprises & Govs": round(ents_govs, 4),
    }


def derive_sankey_routing(providers_visible: list[dict],
                           providers_pre_aggregation: list[dict],
                           channel_mapping: dict,
                           channel_margins: dict,
                           preserve_channels: list[str]) -> tuple[dict, list[dict]]:
    """Compute per-provider-per-channel routing + grossed-up channel list.

    For Other Model Providers, sums routing across the aggregated members
    (since each member has its own revenue_by_channel or _default fallback).

    Returns (routing, channels):
      routing  = {provider_slug: {channel_label: net_value}}
      channels = [{label, value (gross), chPass (net), margin}, ...]
                 in the order of preserve_channels (channels with chPass>0)
    """
    routing: dict[str, dict[str, float]] = {}

    # Build a slug → pre-aggregation provider lookup so we can route Other
    # by walking its members rather than trying to route the aggregate.
    pre_by_slug = {p["slug"]: p for p in providers_pre_aggregation}

    for p in providers_visible:
        slug = p["slug"]
        if p.get("vc_origin") == "small_provider_aggregation":
            # Aggregate routing across members
            agg_routing: dict[str, float] = {}
            for member_slug in p.get("members") or []:
                member = pre_by_slug.get(member_slug)
                if not member:
                    continue
                member_routing = _routing_for_provider(member, channel_mapping)
                for ch, v in member_routing.items():
                    agg_routing[ch] = agg_routing.get(ch, 0) + v
            routing[slug] = {ch: round(v, 4) for ch, v in agg_routing.items() if v > 0}
            continue
        # Regular provider (incl. preserved IaaS — which has no rbc; uses defaults)
        routing[slug] = _routing_for_provider(p, channel_mapping)

    # Sum chPass per channel
    chPass_by_channel: dict[str, float] = {ch: 0.0 for ch in preserve_channels}
    for slug, channel_values in routing.items():
        for ch, v in channel_values.items():
            chPass_by_channel[ch] = chPass_by_channel.get(ch, 0) + v

    # Gross up: channel.value × (1 - margin) = chPass → channel.value = chPass / (1 - margin)
    channels = []
    for ch_label in preserve_channels:
        chPass = chPass_by_channel.get(ch_label, 0)
        if chPass <= 0:
            continue
        margin = channel_margins.get(ch_label, 0)
        gross = chPass / (1 - margin) if margin < 1 else chPass
        channels.append({
            "label": ch_label,
            "value": round(gross, 4),
            "chPass": round(chPass, 4),
            "margin": margin,
            "gross_up_factor": round(1 / (1 - margin), 4) if margin < 1 else 1.0,
        })

    return routing, channels


# ---------------------------------------------------------------------------
# Full Sankey derivation
# ---------------------------------------------------------------------------

def derive_sankey(entities: dict, cost_structure_full: dict, year: str,
                  overrides: dict) -> dict:
    """Run engine across all model_provider entities for one year.

    Returns:
      {
        "providers": [...] (already aggregated per §5),
        "providers_pre_aggregation": [...] (full raw list, for provenance),
        "totals": {total_customer_revenue, total_vc_subsidy, total_provider_value},
        "fallback_log": [strings noting providers that hit fallback paths],
        "iaas_aggregation": {...},  # preserved hand-curated IaaS block
      }
    """
    cs_year = cost_structure_full[year]
    raw_providers = []
    fallback_log = []

    for entity in entities.get("companies", []):
        if "model_provider" not in (entity.get("roles") or []):
            continue
        block = derive_provider(entity, year, cs_year, overrides)
        if block is None:
            continue
        raw_providers.append(block)
        # Capture fallback signals for the report
        if block["inference_cost_origin"] == "estimated":
            fallback_log.append(f"{block['slug']}: inference_cost ESTIMATED (no source/op_loss path)")
        if block["opex_origin"] == "estimated":
            fallback_log.append(f"{block['slug']}: opex ESTIMATED (no source/op_loss path)")

    # wq-053 — Derive the IaaS aggregation node from role=iaas_provider entities
    # when populated; fall back to hand-curated cost_structure block otherwise.
    # Roll up customer_revenue (sourced) and let vc_subsidy emerge as balancing
    # plug like other providers. Same color/label as the legacy hand-curated block.
    iaas_block = cs_year.get("iaas_aggregation")
    if iaas_block:
        iaas_entities = [
            c for c in (entities.get("companies") or [])
            if "iaas_provider" in (c.get("roles") or [])
        ]
        iaas_cr_rollup = sum(
            ((c.get("financials") or {}).get(year, {}).get("collected_revenue") or 0)
            for c in iaas_entities
        )

        if iaas_cr_rollup > 0:
            # Engine-derived path: sum customer_revenue across iaas_provider entities.
            # vc_subsidy preserved at hand-curated level (IaaS providers rarely
            # disclose operating losses; engine's balancing plug logic doesn't apply
            # to a rollup node without per-entity cost components).
            iaas_value = iaas_cr_rollup + iaas_block["vc_subsidy"]
            iaas_provider = {
                "slug": "iaas",
                "label": iaas_block["label"],
                "color": iaas_block["color"],
                "customer_revenue": round(iaas_cr_rollup, 4),
                "vc_subsidy": iaas_block["vc_subsidy"],
                "vc_origin": "preserved_hand_curated",
                "value": round(iaas_value, 4),
                "tier": "2A",  # upgraded from hand-curated 1B → derived 2A
                "src": (
                    f"wq-053 engine — rolled up from {len(iaas_entities)} iaas_provider entities "
                    f"({', '.join(c['slug'] for c in iaas_entities)}); "
                    f"customer_revenue=${iaas_cr_rollup:.2f}B + vc_subsidy=${iaas_block['vc_subsidy']:.2f}B (hand-curated)"
                ),
                "inference_cost": round(iaas_value * 0.50, 4),
                "inference_cost_origin": "estimated",
                "inference_cost_derived_from": [f"iaas rollup × 0.50 (inference rate)"],
                "opex": round(iaas_value * 0.50, 4),
                "opex_origin": "estimated",
                "opex_derived_from": [f"iaas rollup × 0.50"],
                "override_discrepancy": None,
                "_iaas_members": [c["slug"] for c in iaas_entities],
            }
        else:
            # Fallback: hand-curated block (no entity data populated yet)
            iaas_provider = {
                "slug": "iaas",
                "label": iaas_block["label"],
                "color": iaas_block["color"],
                "customer_revenue": iaas_block["customer_revenue"],
                "vc_subsidy": iaas_block["vc_subsidy"],
                "vc_origin": "preserved_hand_curated",
                "value": iaas_block["value"],
                "tier": iaas_block.get("tier"),
                "src": iaas_block.get("src"),
                "inference_cost": round(iaas_block["value"] * 0.50, 4),
                "inference_cost_origin": "preserved_hand_curated",
                "inference_cost_derived_from": ["iaas_aggregation.value × 0.50 (inference rate)"],
                "opex": round(iaas_block["value"] * 0.50, 4),
                "opex_origin": "preserved_hand_curated",
                "opex_derived_from": ["iaas_aggregation.value × 0.50"],
                "override_discrepancy": None,
            }
        raw_providers.append(iaas_provider)

    aggregated_providers = aggregate_small_providers(raw_providers, cs_year)

    total_customer = round(sum(p["customer_revenue"] for p in aggregated_providers), 4)
    total_vc = round(sum(p["vc_subsidy"] for p in aggregated_providers), 4)
    total_provider = round(sum(p["value"] for p in aggregated_providers), 4)

    # wq-062 — per-provider-per-channel routing + grossed-up channels
    channel_mapping = cs_year.get("channel_mapping") or {}
    channel_margins = cs_year.get("marginPcts") or {}
    preserve_channels = (cs_year.get("channelRouting") or {}).get("preserve_channels") or []
    routing, channels_grossed = derive_sankey_routing(
        aggregated_providers, raw_providers,
        channel_mapping, channel_margins, preserve_channels,
    )

    # wq-090 — per-archetype buyer-segment routing (Consumer / AI Natives /
    # Enterprises & Govs). Emits gross totals so the renderer's buyer column
    # ties to channels-gross by construction.
    seg_comp_by_archetype = (
        (cs_year.get("market_aggregates_estimation") or {})
        .get("segment_composition_by_archetype") or {}
    )
    buyer_segments_gross = derive_buyer_segments(
        raw_providers, channel_mapping, seg_comp_by_archetype, channel_margins,
    )
    buyer_channel_matrix = derive_buyer_channel_matrix(
        raw_providers, channel_mapping, seg_comp_by_archetype, channel_margins,
    )

    # wq-090 — per-(buyer, provider) net allocation per the editorial split
    buyer_provider_split = (channel_mapping.get("buyer_provider_split") or {})
    buyer_provider_routing = derive_buyer_provider_routing(
        raw_providers, buyer_segments_gross, buyer_channel_matrix,
        channel_margins, buyer_provider_split,
    )

    return {
        "providers": aggregated_providers,
        "providers_pre_aggregation": raw_providers,
        "totals": {
            "total_customer_revenue": total_customer,
            "total_vc_subsidy": total_vc,
            "total_provider_value": total_provider,
        },
        "fallback_log": fallback_log,
        "routing": routing,
        "channels_grossed": channels_grossed,
        "buyer_segments_gross": buyer_segments_gross,
        "buyer_channel_matrix": buyer_channel_matrix,
        "buyer_provider_routing": buyer_provider_routing,
    }


# ---------------------------------------------------------------------------
# Conservation pre-check (§3.2)
# ---------------------------------------------------------------------------

def conservation_precheck(sankey: dict, tolerance: float = 0.005) -> list[str]:
    """Check provider self-consistency: provider.value == cr + vc_subsidy
    (within tolerance) for every provider EXCEPT those with override
    discrepancy noted. Returns list of failure strings (empty = pass).

    Buyer/channel/outcome conservation checks happen in Phase C when those
    sections get derived. This pre-check covers what's known after Phase B.
    """
    findings = []
    for p in sankey["providers"]:
        if p.get("vc_origin") == "small_provider_aggregation":
            # Aggregation node: same self-consistency, just use stored sums
            derived = p["customer_revenue"] + p["vc_subsidy"]
            if p["value"] > 0 and abs(derived - p["value"]) / p["value"] > tolerance:
                findings.append(f"{p['slug']} aggregation self-consistency: cr+vc={derived} vs value={p['value']}")
            continue
        if p.get("vc_origin") == "preserved_hand_curated":
            continue  # IaaS hand-curated; no engine self-consistency claim
        derived = p["customer_revenue"] + p["vc_subsidy"]
        if p["value"] > 0 and abs(derived - p["value"]) / p["value"] > tolerance:
            findings.append(f"{p['slug']} self-consistency: cr+vc={derived} vs value={p['value']}")
    return findings


# ---------------------------------------------------------------------------
# Validation report (§4)
# ---------------------------------------------------------------------------

def format_validation_report(sankey: dict, cost_structure_year: dict) -> str:
    targets = cost_structure_year.get("validation_targets", {})

    lines = [
        "# wq-055 Sankey balancing engine — validation report",
        f"_Generated {datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')}_",
        "",
        "## Phase B calibration gate (§4) — engine output vs hand-curated",
        "",
        f"{'Provider':12}  {'CR':>8}  {'Inf cost (tier)':>22}  {'Opex (tier)':>22}  {'Total':>10}  {'Hand':>10}  {'Δ%':>8}  {'In band?':>9}  {'vc_subsidy':>11}",
        f"{'-'*12}  {'-'*8}  {'-'*22}  {'-'*22}  {'-'*10}  {'-'*10}  {'-'*8}  {'-'*9}  {'-'*11}",
    ]
    by_slug = {p["slug"]: p for p in sankey["providers_pre_aggregation"]}
    for slug, target in targets.items():
        if slug.startswith("_") or not isinstance(target, dict):
            continue
        p = by_slug.get(slug)
        if not p:
            lines.append(f"{slug:12}  {'—':>8}  {'(not derived)':>22}  {'':>22}  {'—':>10}  ${target['value']:>8.2f}B  {'—':>8}  {'—':>9}  {'—':>11}")
            continue
        inf_str = f"${p['inference_cost']:.2f}B ({p['inference_cost_origin'][:6]})"
        opex_str = f"${p['opex']:.2f}B ({p['opex_origin'][:6]})"
        delta = (p["value"] - target["value"]) / target["value"] * 100
        in_band = "✓ yes" if abs(delta) <= 15 else "✗ NO"
        lines.append(
            f"{slug:12}  ${p['customer_revenue']:>6.2f}B  {inf_str:>22}  {opex_str:>22}  ${p['value']:>8.2f}B  ${target['value']:>8.2f}B  {delta:>+7.1f}%  {in_band:>9}  ${p['vc_subsidy']:>9.2f}B"
        )

    # New providers (no validation_targets)
    lines += ["", "## New providers (no hand-curated baseline; engine output only)", ""]
    lines.append(f"{'Provider':12}  {'CR':>8}  {'Inf cost (tier)':>22}  {'Opex (tier)':>22}  {'Total':>10}  {'vc_subsidy':>11}")
    lines.append(f"{'-'*12}  {'-'*8}  {'-'*22}  {'-'*22}  {'-'*10}  {'-'*11}")
    target_slugs = {k for k in targets.keys() if not k.startswith("_")}
    for p in by_slug.values():
        if p["slug"] in target_slugs or p["slug"] == "iaas":
            continue
        inf_str = f"${p['inference_cost']:.2f}B ({p['inference_cost_origin'][:6]})"
        opex_str = f"${p['opex']:.2f}B ({p['opex_origin'][:6]})"
        lines.append(f"{p['slug']:12}  ${p['customer_revenue']:>6.2f}B  {inf_str:>22}  {opex_str:>22}  ${p['value']:>8.2f}B  ${p['vc_subsidy']:>9.2f}B")

    # Small-provider aggregation result
    lines += ["", "## Small-provider aggregation outcome", ""]
    other = next((p for p in sankey["providers"] if p.get("vc_origin") == "small_provider_aggregation"), None)
    if other:
        lines.append(f"  Other Model Providers: ${other['value']:.2f}B (members: {', '.join(other['members'])})")
        lines.append(f"  cr=${other['customer_revenue']:.2f}B  vc_subsidy=${other['vc_subsidy']:.2f}B")
        lines.append(f"  Aggregation rule: {other['aggregation_rule']}")
    else:
        lines.append("  No providers aggregated — all visible at their derived values.")

    # Visible providers in final Sankey
    lines += ["", "## Visible providers in rendered Sankey (post-aggregation)", ""]
    for p in sankey["providers"]:
        flag = ""
        if p.get("vc_origin") == "small_provider_aggregation":
            flag = " (aggregated)"
        elif p.get("vc_origin") == "editorial_override":
            flag = " (vc_subsidy override)"
        elif p.get("vc_origin") == "preserved_hand_curated":
            flag = " (preserved hand-curated)"
        lines.append(f"  {p['label']:25}  ${p['value']:>7.2f}B  cr=${p['customer_revenue']:>6.2f}B  vc=${p['vc_subsidy']:>6.2f}B{flag}")

    # Override discrepancies
    discrepancies = [p for p in sankey["providers_pre_aggregation"] if p.get("override_discrepancy")]
    if discrepancies:
        lines += ["", "## vc_subsidy override discrepancies (engine vs editorial)", ""]
        for p in discrepancies:
            d = p["override_discrepancy"]
            lines.append(f"  {p['slug']}.{2025}.vc_subsidy:")
            lines.append(f"    Engine derived:    provider_total=${d['engine_provider_total']:.2f}B  vc_subsidy=${d['engine_vc_subsidy']:.2f}B")
            lines.append(f"    Override forced:   provider_total=${d['override_provider_total']:.2f}B  vc_subsidy=${d['override_vc_subsidy']}")
            lines.append(f"    Delta on total: ${d['delta_total']:+.2f}B (override broke engine consistency intentionally)")
            lines.append(f"    Reason: {d['reason']}")
            lines.append(f"    Expires: {d.get('expires_at', 'never')}; set_by: {d.get('set_by')}; set_at: {d.get('set_at')}")

    # Fallback log
    if sankey["fallback_log"]:
        lines += ["", "## Fallback signals (entity data missing → TIER 3 estimates fired)", ""]
        for line in sankey["fallback_log"]:
            lines.append(f"  - {line}")

    # Totals + conservation pre-check
    lines += ["", "## Totals (pre-channel/buyer/outcome derivation)", ""]
    t = sankey["totals"]
    lines.append(f"  total_customer_revenue (sum of providers): ${t['total_customer_revenue']:.2f}B")
    lines.append(f"  total_vc_subsidy       (sum of providers): ${t['total_vc_subsidy']:.2f}B")
    lines.append(f"  total_provider_value   (sum of providers): ${t['total_provider_value']:.2f}B")
    lines.append(f"  hand-curated total customer revenue:       $17.47B (audit §4.4)")
    lines.append(f"  hand-curated total VC subsidy:              $9.39B")
    lines.append(f"  hand-curated total system:                 $26.86B")
    lines.append("")
    lines.append(f"  NOTE: residual customer revenue from non-provider channels (Trad SaaS,")
    lines.append(f"        IaaS aggregation already in providers, etc.) handled in Phase C")
    lines.append(f"        when generate_site_data.py rebuilds buyer/channel/outcome columns.")

    findings = conservation_precheck(sankey)
    lines += ["", "## Provider self-consistency (conservation pre-check)", ""]
    if not findings:
        lines.append("  ✓ All providers: customer_revenue + vc_subsidy == value within 0.5%")
    else:
        for f in findings:
            lines.append(f"  ✗ {f}")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    with logged_run("derive_sankey.py") as outputs:
        parser = argparse.ArgumentParser(description="Sankey balancing engine (wq-055).")
        parser.add_argument("--validate", action="store_true",
                            help="Run validation gate, write report, exit. NO entity writes.")
        parser.add_argument("--backfill", action="store_true",
                            help="Walk every model_provider × year and derive sankey block.")
        parser.add_argument("--dry-run", action="store_true",
                            help="With --backfill: report only, do not write to entities.json.")
        parser.add_argument("--apply", action="store_true",
                            help="With --backfill: WRITE derived values. Otherwise dry-run.")
        parser.add_argument("--entity", help="Inspect a single entity slug.")
        parser.add_argument("--year", default="2025")
        args = parser.parse_args()

        cost_structure = load_cost_structure()
        overrides = load_overrides()
        entities = load_entities()

        outputs["overrides_loaded"] = len(overrides)

        if args.entity:
            ent = next((c for c in entities.get("companies", []) if c.get("slug") == args.entity), None)
            if not ent:
                print(f"No entity with slug={args.entity!r}")
                outputs["error"] = "entity_not_found"
                return
            block = derive_provider(ent, args.year, cost_structure[args.year], overrides)
            print(json.dumps(block, indent=2))
            outputs["derived_value"] = block["value"] if block else None
            return

        if args.validate or args.backfill:
            sankey = derive_sankey(entities, cost_structure, args.year, overrides)
            report = format_validation_report(sankey, cost_structure[args.year])
            print(report)

            out_path = VALIDATION_REPORT_PATH if args.validate else BACKFILL_REPORT_PATH
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(report)
            print(f"Wrote {out_path}")

            outputs["providers_derived"] = len(sankey["providers_pre_aggregation"])
            outputs["providers_visible"] = len(sankey["providers"])
            outputs["total_provider_value"] = sankey["totals"]["total_provider_value"]
            outputs["fallback_count"] = len(sankey["fallback_log"])

            if args.backfill and args.apply:
                written_block = apply_market_aggregates(entities, sankey, args.year)
                with open(ENTITIES_PATH, "w") as f:
                    json.dump(entities, f, indent=2)
                today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                with open(CONSENSUS_LOG_PATH, "a") as f:
                    f.write(
                        f"\n## {today} — wq-055 derive_sankey.py --apply\n"
                        f"- Year: {args.year}\n"
                        f"- Providers written: {len(written_block['providers'])}\n"
                        f"- Visible (post-aggregation): {len(sankey['providers'])}\n"
                        f"- total_customer_revenue: {written_block['totals']['total_customer_revenue']}\n"
                        f"- total_vc_subsidy: {written_block['totals']['total_vc_subsidy']}\n"
                        f"- total_provider_value: {written_block['totals']['total_provider_value']}\n"
                    )
                print(f"\n✓ entities.json:market_aggregates.{args.year} written.")
                print(f"  Run scripts/generate_site_data.py to regenerate site-data.json:sankey + sankey-projections.json:{args.year}.")
                outputs["entities_written"] = True


def apply_market_aggregates(entities: dict, sankey: dict, year: str) -> dict:
    """Write engine output to entities.json:market_aggregates.<year>.

    Idempotent: re-runs overwrite the prior block. Mutates entities in place;
    caller saves the file.

    Block shape (preserved from prior wq-044 wire-completion + extended for
    wq-055 per-component visibility):

        market_aggregates.<year>:
          total_customer_revenue: float
          total_vc_subsidy:       float
          total_provider_value:   float
          providers:              {<slug>: {full per-provider block including
                                            per-component tier + override
                                            discrepancy details}}
          providers_visible:      [<slug>, ...] (post-aggregation order)
          other_aggregation:      {members, value, customer_revenue, vc_subsidy}
                                  if Other node was created; else null
          fallback_log:           [strings noting TIER 3 estimates]
          _residual_doc:          context for non-provider revenue (Trad SaaS)
          _engine_run_at:         ISO timestamp
    """
    market_aggregates = entities.setdefault("market_aggregates", {})
    year_block = market_aggregates.setdefault(year, {})

    # Per-provider block keyed by slug (for stable lookup)
    providers_by_slug = {p["slug"]: p for p in sankey["providers_pre_aggregation"]}

    # Order in which they appear post-aggregation (Other Model Providers may
    # be the last entry if it was created)
    providers_visible_order = [p["slug"] for p in sankey["providers"]]

    # Other-aggregation summary if it fired
    other = next((p for p in sankey["providers"] if p.get("vc_origin") == "small_provider_aggregation"), None)
    other_block = None
    if other is not None:
        other_block = {
            "label": other["label"],
            "color": other["color"],
            "value": other["value"],
            "customer_revenue": other["customer_revenue"],
            "vc_subsidy": other["vc_subsidy"],
            "members": other["members"],
            "aggregation_rule": other["aggregation_rule"],
        }

    year_block["providers"] = providers_by_slug
    year_block["providers_visible"] = providers_visible_order
    year_block["other_aggregation"] = other_block
    year_block["total_customer_revenue"] = sankey["totals"]["total_customer_revenue"]
    year_block["total_vc_subsidy"] = sankey["totals"]["total_vc_subsidy"]
    year_block["total_provider_value"] = sankey["totals"]["total_provider_value"]
    year_block["fallback_log"] = sankey["fallback_log"]
    # wq-062 — per-provider-per-channel routing + grossed-up channels
    year_block["routing"] = sankey.get("routing") or {}
    year_block["channels_grossed"] = sankey.get("channels_grossed") or []
    # wq-090 — per-archetype buyer-segment routing (gross terms)
    year_block["buyer_segments_gross"] = sankey.get("buyer_segments_gross") or {}
    # wq-090 — per-(buyer, channel) gross-value matrix for the renderer
    year_block["buyer_channel_matrix"] = sankey.get("buyer_channel_matrix") or {}
    # wq-090 — per-(buyer, provider) net-revenue allocation
    year_block["buyer_provider_routing"] = sankey.get("buyer_provider_routing") or {}
    # wq-063 — buyer-gross customer total = sum(channels_grossed.value).
    # Channels are grossed up so chPass = sum(provider routing per channel),
    # and channel margins flow direct to cashflow (kept by Hyperscaler/SaaS
    # resellers, not received by providers). The gross figure is what
    # customers actually paid; total_customer_revenue (= net) is what
    # providers received. Renderer reads gross for the headline.
    year_block["total_customer_revenue_gross"] = round(
        sum((c.get("value") or 0) for c in (sankey.get("channels_grossed") or [])), 4
    )
    year_block["_residual_doc"] = (
        "Engine writes per-provider customer_revenue derived from "
        "entities.json:financials.<year>.collected_revenue (wq-048). "
        "Channel/buyer totals computed by generate_site_data.py from this "
        "block + the existing editorial channel structure (proportional "
        "rescale to total_customer_revenue). Non-provider revenue (e.g. "
        "Microsoft Copilot via Trad SaaS channel) handled in the channel "
        "structure, not in providers."
    )
    year_block["_engine_run_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    year_block["_engine"] = "scripts/derive_sankey.py (wq-055)"

    return {
        "providers": providers_by_slug,
        "totals": {
            "total_customer_revenue": sankey["totals"]["total_customer_revenue"],
            "total_vc_subsidy": sankey["totals"]["total_vc_subsidy"],
            "total_provider_value": sankey["totals"]["total_provider_value"],
        },
    }


if __name__ == "__main__":
    main()
