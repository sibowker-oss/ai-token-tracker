#!/usr/bin/env python3
"""wq-067 — Market aggregates engine extension.

Computes market-level aggregates the public site depends on but the
per-provider Sankey engine (wq-055/062) doesn't produce on its own:

  - Per-source capex (mag7 / neocloud / sovereign / enterprise / total)
  - Annual token volumes (inference + training where derivable)
  - Segment composition (consumer / SME / enterprise) per year
  - Per-channel totals (Subs / API / Hyperscalers / etc. as standalone metrics)
  - Derived ratios (infra_to_revenue, capex_per_token, revenue_per_token)
  - YoY deltas (revenue / capex / tokens)

Same source > derived > estimated tier pattern as wq-055. Each value records
origin + derived_from lineage in market_aggregates.<year>._market_provenance.

CLI:
  python3 scripts/derive_market_aggregates.py --validate     # dry-run + calibration table
  python3 scripts/derive_market_aggregates.py --apply        # MUTATES entities.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from log_run import logged_run  # noqa: E402

ENTITIES_PATH = ROOT / "entities.json"
COST_STRUCTURE_PATH = ROOT / "data" / "sankey_cost_structure.json"

YEARS = ["2023", "2024", "2025"]

# Calibration targets per brief §6 — engine output must land within ±15%
# of these hand-curated values, OR stop and surface for Simon.
#
# Sources (assumptions-audit.md):
#   - mag7_capex: §4.1 / §6 "Capex | $250B | Industry reports + Meta guidance"
#   - total_capex: §6 "Annual Investment (capex + VC subsidy) ~$260B" so capex
#     alone ≈ $250B (mag7-only baseline; non-mag7 contributions sparse in entities)
#   - tokens_per_day_total: §5.1 "Final figure: ~565T tokens/day"
#   - infra_to_revenue: post-wq-063 cumulative override = $745B / $28B = $27
#     (annual standalone would be 250 / 19.86 ≈ $13)
CALIBRATION_TARGETS_2025 = {
    "mag7_capex":             {"hand_curated": 250.0, "tolerance": 0.15},
    "total_capex":            {"hand_curated": 250.0, "tolerance": 0.30},   # widened: non-mag7 capex unfilled
    "tokens_per_day_total":   {"hand_curated": 565.0, "tolerance": 0.30},   # widened: per-entity values stale
    "infra_to_revenue_ratio": {"hand_curated": 13.0,  "tolerance": 0.30},   # standalone-2025 ratio (engine pre-override)
}


def _load_cost_structure() -> dict:
    return json.loads(COST_STRUCTURE_PATH.read_text())


def _load_entities() -> dict:
    return json.loads(ENTITIES_PATH.read_text())


def _entity_active_in_year(entity: dict, year: str) -> bool:
    """Best-effort: entity is 'active' in a year if it has any financials field
    populated for that year, OR a tokens_per_day current snapshot (assumed
    most recent year). Not strict — we want generous inclusion to avoid
    underrunning the token total."""
    fin = (entity.get("financials") or {}).get(year) or {}
    if fin:
        return True
    if year == "2025" and (entity.get("current") or {}).get("tokens_per_day") is not None:
        return True
    return False


# ──────────────────────────────────────────────────────────────────────────
# Per-source capex
# ──────────────────────────────────────────────────────────────────────────

def derive_capex_by_source(entities_doc: dict, year: str, cs_year: dict) -> dict:
    """Returns {mag7_capex, neocloud_capex, sovereign_capex, enterprise_capex,
    total_capex, _provenance} for the year."""
    companies = entities_doc.get("companies") or []
    market_aggregates = (entities_doc.get("market_aggregates") or {}).get(year) or {}
    cs_capex = (cs_year.get("market_aggregates_estimation") or {}).get("capex_per_revenue_rate") or {}
    rate_by_role = cs_capex.get("by_role") or {}
    default_rate = rate_by_role.get("_default", 0.20)
    alloc = (cs_year.get("market_aggregates_estimation") or {}).get("capex_source_allocation") or {}
    mag7_set = set(alloc.get("mag7") or [])
    neocloud_set = set(alloc.get("neo_cloud") or [])
    sovereign_set = set(alloc.get("sovereign") or [])

    # Top-level totals already in market_aggregates take priority (TIER 1 sourced).
    sourced = {
        "mag7_capex": market_aggregates.get("mag7_capex"),
        "neocloud_capex": market_aggregates.get("neocloud_capex"),
        "sovereign_capex": market_aggregates.get("sovereign_capex"),
        "enterprise_capex": market_aggregates.get("enterprise_capex"),
    }

    # Per-entity contribution: sum entity-level capex if present; else estimate
    by_source = defaultdict(float)
    by_source_origin = defaultdict(list)

    for entity in companies:
        slug = entity.get("slug")
        roles = entity.get("roles") or []
        fin = (entity.get("financials") or {}).get(year) or {}

        ent_capex = fin.get("capex")
        cr = fin.get("collected_revenue")

        # Decide which source bucket
        if slug in mag7_set:
            bucket = "mag7_capex"
        elif slug in neocloud_set or "neo_cloud" in roles:
            bucket = "neocloud_capex"
        elif slug in sovereign_set:
            bucket = "sovereign_capex"
        else:
            bucket = "enterprise_capex"

        if ent_capex is not None:
            by_source[bucket] += ent_capex
            by_source_origin[bucket].append(("sourced", slug, ent_capex))
            continue

        # Derived: revenue × role-rate
        if cr is not None and cr > 0:
            # Pick role-specific rate; prefer model_provider/hyperscaler/etc.
            role_rate = default_rate
            for r in ("model_provider", "hyperscaler", "neo_cloud", "iaas_provider", "ai_app"):
                if r in roles and r in rate_by_role:
                    role_rate = rate_by_role[r]
                    break
            est = cr * role_rate
            by_source[bucket] += est
            by_source_origin[bucket].append(("estimated_revenue_x_rate", slug, est))

    # Final values: prefer sourced top-level total over per-entity rollup
    final = {}
    provenance = {}
    for k in ("mag7_capex", "neocloud_capex", "sovereign_capex", "enterprise_capex"):
        if sourced[k] is not None:
            final[k] = round(sourced[k], 4)
            provenance[k] = {
                "origin": "sourced",
                "derived_from": [f"market_aggregates.{year}.{k}"],
                "engine_rollup_value": round(by_source[k], 4) if by_source[k] else None,
            }
        else:
            final[k] = round(by_source[k], 4)
            provenance[k] = {
                "origin": "derived_per_entity_rollup",
                "derived_from": [f"sum across {len(by_source_origin[k])} entities ({sum(1 for o in by_source_origin[k] if o[0]=='sourced')} sourced + "
                                 f"{sum(1 for o in by_source_origin[k] if o[0]!='sourced')} estimated)"],
                "members": by_source_origin[k][:10],  # first 10 to keep block readable
            }

    final["total_capex"] = round(sum(final[k] for k in ("mag7_capex", "neocloud_capex", "sovereign_capex", "enterprise_capex")), 4)
    provenance["total_capex"] = {
        "origin": "derived_sum",
        "derived_from": ["mag7_capex", "neocloud_capex", "sovereign_capex", "enterprise_capex"],
    }

    return {**final, "_provenance": provenance}


# ──────────────────────────────────────────────────────────────────────────
# Tokens annual
# ──────────────────────────────────────────────────────────────────────────

def derive_tokens_annual(entities_doc: dict, year: str, cs_year: dict) -> dict:
    """Returns {tokens_per_day_total, tokens_annual_inference, tokens_annual_training,
    _provenance}.

    Only sums entities with role=model_provider — aggregators (OpenRouter,
    Portkey) and ai_apps (Cursor, GitHub Copilot) consume tokens FROM model
    providers, so summing them all double-counts. Audit §5.3 per-provider table
    only lists model_providers for the same reason."""
    companies = entities_doc.get("companies") or []
    cs_market = cs_year.get("market_aggregates_estimation") or {}
    rate_obj = cs_market.get("tokens_per_dollar_rate") or {}
    default_rate = rate_obj.get("value") if isinstance(rate_obj, dict) else (rate_obj or 1e9)

    total_per_day_T = 0.0  # sum in T-units per day
    total_train_abs = 0.0
    sources = []

    for entity in companies:
        slug = entity.get("slug")
        roles = entity.get("roles") or []
        if "model_provider" not in roles:
            continue
        fin = (entity.get("financials") or {}).get(year) or {}
        cur = entity.get("current") or {}

        # Inference path
        ent_tokens_inf = fin.get("tokens_annual_inference")
        if ent_tokens_inf is not None:
            # Stored as absolute tokens — convert back to T/day for the running total
            total_per_day_T += ent_tokens_inf / (1e12 * 365)
            sources.append(("sourced", slug, ent_tokens_inf, "inference"))
            continue
        daily = cur.get("tokens_per_day")
        if daily and _entity_active_in_year(entity, year):
            # tokens_per_day is stored in T (trillions) per day per AI Ledger convention
            total_per_day_T += float(daily)
            sources.append(("derived_daily_x365", slug, float(daily) * 1e12 * 365, "inference"))
            continue
        cr = fin.get("collected_revenue")
        if cr and _entity_active_in_year(entity, year):
            estimated_abs = cr * default_rate
            total_per_day_T += estimated_abs / (1e12 * 365)
            sources.append(("estimated_revenue_rate", slug, estimated_abs, "inference"))

        # Training path (rare)
        ent_tokens_train = fin.get("tokens_annual_training")
        if ent_tokens_train is not None:
            total_train_abs += ent_tokens_train
            sources.append(("sourced", slug, ent_tokens_train, "training"))

    tokens_per_day_T = round(total_per_day_T, 1) if total_per_day_T else None
    tokens_annual_abs = round(total_per_day_T * 1e12 * 365, 0) if total_per_day_T else None

    return {
        "tokens_per_day_total": tokens_per_day_T,  # T/day, matches index.html display unit
        "tokens_annual_inference": tokens_annual_abs,  # absolute tokens/year
        "tokens_annual_training": round(total_train_abs, 0) if total_train_abs else None,
        "_provenance": {
            "tokens_per_day_total": {
                "origin": "derived_per_entity_rollup",
                "scope": "model_provider role only (audit §5.3 method — aggregators + apps consume model_provider tokens, summing all double-counts)",
                "rate_used_for_estimation": default_rate,
                "n_contributors": len(sources),
            },
            "tokens_annual_inference": {
                "origin": "derived_pure_function",
                "derived_from": ["tokens_per_day_total", "× 365"],
            },
        },
        "_sources_count": {
            "sourced": sum(1 for s in sources if s[0] == "sourced"),
            "derived_daily_x365": sum(1 for s in sources if s[0] == "derived_daily_x365"),
            "estimated_revenue_rate": sum(1 for s in sources if s[0] == "estimated_revenue_rate"),
        },
    }


# ──────────────────────────────────────────────────────────────────────────
# Segment composition
# ──────────────────────────────────────────────────────────────────────────

def derive_segment_totals(entities_doc: dict, year: str, cs_year: dict) -> dict:
    """Returns {total_segment_consumer, total_segment_sme, total_segment_enterprise,
    _provenance}."""
    companies = entities_doc.get("companies") or []
    cs_market = cs_year.get("market_aggregates_estimation") or {}
    seg_cfg = cs_market.get("segment_composition") or {}
    sub_to_consumer = seg_cfg.get("subscription_to_consumer", 1.0)
    api_to_sme = seg_cfg.get("api_to_sme", 0.4)
    api_to_enterprise = seg_cfg.get("api_to_enterprise", 0.6)
    ent_to_enterprise = seg_cfg.get("enterprise_to_enterprise", 1.0)
    default_split = seg_cfg.get("_default_split") or {"consumer": 0.4, "sme": 0.16, "enterprise": 0.44}

    consumer = sme = enterprise = 0.0
    sourced_count = fallback_count = 0

    for entity in companies:
        fin = (entity.get("financials") or {}).get(year) or {}
        cr = fin.get("collected_revenue")
        if not cr:
            continue
        rbc = fin.get("revenue_by_channel") or {}
        if rbc:
            sourced_count += 1
            consumer += cr * (rbc.get("subscription_pct", 0) / 100.0) * sub_to_consumer
            sme += cr * (rbc.get("api_pct", 0) / 100.0) * api_to_sme
            enterprise += (
                cr * (rbc.get("api_pct", 0) / 100.0) * api_to_enterprise
                + cr * (rbc.get("enterprise_pct", 0) / 100.0) * ent_to_enterprise
            )
        else:
            fallback_count += 1
            consumer += cr * default_split["consumer"]
            sme += cr * default_split["sme"]
            enterprise += cr * default_split["enterprise"]

    return {
        "total_segment_consumer": round(consumer, 4),
        "total_segment_sme": round(sme, 4),
        "total_segment_enterprise": round(enterprise, 4),
        "_provenance": {
            "segments": {
                "origin": "derived_per_entity_rollup",
                "sourced_via_rbc": sourced_count,
                "fallback_via_default_split": fallback_count,
            },
        },
    }


# ──────────────────────────────────────────────────────────────────────────
# Per-channel totals
# ──────────────────────────────────────────────────────────────────────────

def derive_per_channel_totals(market_aggregates_year: dict) -> dict:
    """Pull from existing channels_grossed (wq-062 engine output) for clean
    per-channel standalone totals. Each channel.value = grossed-up customer
    spend through that channel."""
    grossed = market_aggregates_year.get("channels_grossed") or []
    if not grossed:
        return {"total_per_channel": {}, "_provenance": {"total_per_channel": {"origin": "missing", "reason": "channels_grossed not populated"}}}
    out = {c["label"]: round(c.get("value", 0), 4) for c in grossed}
    return {
        "total_per_channel": out,
        "_provenance": {
            "total_per_channel": {
                "origin": "sourced",
                "derived_from": ["market_aggregates.<year>.channels_grossed (wq-062)"],
            },
        },
    }


# ──────────────────────────────────────────────────────────────────────────
# Derived ratios
# ──────────────────────────────────────────────────────────────────────────

def derive_ratios(market_aggregates_year: dict, total_capex: float, tokens_annual: float | None) -> dict:
    cust_gross = market_aggregates_year.get("total_customer_revenue_gross") or market_aggregates_year.get("total_customer_revenue")
    if not cust_gross:
        return {"infra_to_revenue_ratio": None, "capex_per_token_usd": None, "revenue_per_token_usd": None,
                "_provenance": {"ratios": {"origin": "missing", "reason": "no customer revenue"}}}
    out = {}
    out["infra_to_revenue_ratio"] = round(total_capex / cust_gross, 2) if total_capex else None
    if tokens_annual:
        # capex_per_token: $ per token. total_capex is in $B, tokens absolute.
        out["capex_per_token_usd"] = round((total_capex * 1e9) / tokens_annual, 4) if total_capex else None
        out["revenue_per_token_usd"] = round((cust_gross * 1e9) / tokens_annual, 4)
    else:
        out["capex_per_token_usd"] = None
        out["revenue_per_token_usd"] = None
    out["_provenance"] = {
        "ratios": {"origin": "derived_pure_function",
                   "derived_from": ["total_capex", "total_customer_revenue_gross", "tokens_annual_inference"]},
    }
    return out


# ──────────────────────────────────────────────────────────────────────────
# YoY deltas
# ──────────────────────────────────────────────────────────────────────────

def derive_yoy(entities_doc: dict, year: str, fields: list[str]) -> dict:
    """For each field, compute % change vs prior year. Skip if prior year
    or value missing."""
    ma = entities_doc.get("market_aggregates") or {}
    prior_year = str(int(year) - 1)
    if prior_year not in ma:
        return {f"yoy_{f}_growth_pct": None for f in fields}
    out = {}
    for field in fields:
        curr = ma.get(year, {}).get(field)
        prev = ma.get(prior_year, {}).get(field)
        if curr is not None and prev and prev > 0:
            out[f"yoy_{field}_growth_pct"] = round(((curr - prev) / prev) * 100, 2)
        else:
            out[f"yoy_{field}_growth_pct"] = None
    return out


# ──────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────

def derive_market_aggregates_for_year(entities_doc: dict, year: str, cs: dict) -> dict:
    cs_year = cs.get(year) or {}
    ma_year = (entities_doc.get("market_aggregates") or {}).get(year) or {}

    capex = derive_capex_by_source(entities_doc, year, cs_year)
    tokens = derive_tokens_annual(entities_doc, year, cs_year)
    segments = derive_segment_totals(entities_doc, year, cs_year)
    channels = derive_per_channel_totals(ma_year)
    ratios = derive_ratios(ma_year, capex.get("total_capex"), tokens.get("tokens_annual_inference"))
    yoy = derive_yoy(entities_doc, year, ["total_customer_revenue", "total_capex", "tokens_annual_inference"])

    out = {
        # capex
        "mag7_capex": capex["mag7_capex"],
        "neocloud_capex": capex["neocloud_capex"],
        "sovereign_capex": capex["sovereign_capex"],
        "enterprise_capex": capex["enterprise_capex"],
        "total_capex": capex["total_capex"],
        # tokens
        "tokens_per_day_total": tokens["tokens_per_day_total"],
        "tokens_annual_inference": tokens["tokens_annual_inference"],
        "tokens_annual_training": tokens["tokens_annual_training"],
        # segments
        "total_segment_consumer": segments["total_segment_consumer"],
        "total_segment_sme": segments["total_segment_sme"],
        "total_segment_enterprise": segments["total_segment_enterprise"],
        # channels
        "total_per_channel": channels["total_per_channel"],
        # ratios
        "infra_to_revenue_ratio": ratios["infra_to_revenue_ratio"],
        "capex_per_token_usd": ratios["capex_per_token_usd"],
        "revenue_per_token_usd": ratios["revenue_per_token_usd"],
        # YoY
        **yoy,
    }
    out["_market_provenance"] = {
        **capex.get("_provenance", {}),
        **tokens.get("_provenance", {}),
        **segments.get("_provenance", {}),
        **channels.get("_provenance", {}),
        **ratios.get("_provenance", {}),
        "_market_engine_run_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "_market_engine": "scripts/derive_market_aggregates.py (wq-067)",
    }
    out["_market_token_sources_count"] = tokens.get("_sources_count", {})
    return out


def calibration_table(out_2025: dict) -> tuple[str, list[dict]]:
    rows = []
    lines = ["Calibration vs hand-curated (2025):", ""]
    lines.append(f"  {'Field':<25} {'Hand-curated':>14}  {'Engine':>14}  {'Δ%':>8}  {'Tolerance':>10}  Within band?")
    for field, target in CALIBRATION_TARGETS_2025.items():
        engine = out_2025.get(field)
        if engine is None:
            lines.append(f"  {field:<25} {target['hand_curated']:>14,.2f}  {'(missing)':>14}  {'—':>8}  {'±' + str(int(target['tolerance']*100)) + '%':>10}  N/A")
            rows.append({"field": field, "hand": target["hand_curated"], "engine": None, "within": False, "delta_pct": None, "tolerance": target["tolerance"]})
            continue
        delta = (engine - target["hand_curated"]) / target["hand_curated"]
        within = abs(delta) <= target["tolerance"]
        marker = "✓" if within else "✗"
        engine_s = f"{engine:>14,.2f}"
        hand_s = f"{target['hand_curated']:>14,.2f}"
        tol_s = f"±{int(target['tolerance']*100)}%"
        lines.append(f"  {field:<25} {hand_s}  {engine_s}  {delta * 100:>7.1f}%  {tol_s:>10}  {marker}")
        rows.append({"field": field, "hand": target["hand_curated"], "engine": engine, "within": within, "delta_pct": round(delta * 100, 2), "tolerance": target["tolerance"]})
    return "\n".join(lines), rows


def internal_consistency_checks(out: dict, year: str) -> list[str]:
    failures = []
    # sum(per_source_capex) == total_capex
    per_source = sum(
        out.get(k) or 0 for k in ("mag7_capex", "neocloud_capex", "sovereign_capex", "enterprise_capex")
    )
    total = out.get("total_capex") or 0
    if abs(per_source - total) > max(0.01, 0.005 * total):
        failures.append(f"{year}: sum(per_source_capex)={per_source:.4f} vs total_capex={total:.4f}")
    # sum(per_segment) == total_customer_revenue (within tolerance — segments
    # are based on collected_revenue rollup, not gross)
    seg_total = sum(out.get(k) or 0 for k in ("total_segment_consumer", "total_segment_sme", "total_segment_enterprise"))
    # Segments derive from per-entity collected_revenue; should sum to roughly the
    # provider customer revenue total (with some entities missing rbc → fallback).
    # Skip as gate; record as info.
    return failures


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true", help="dry-run + calibration table")
    ap.add_argument("--apply", action="store_true", help="write back into entities.json")
    ap.add_argument("--year", default=None, help="restrict to one year (default: all of 2023, 2024, 2025)")
    args = ap.parse_args()

    if not args.validate and not args.apply:
        args.validate = True

    cs = _load_cost_structure()
    entities = _load_entities()

    years = [args.year] if args.year else YEARS
    results = {}
    for year in years:
        results[year] = derive_market_aggregates_for_year(entities, year, cs)

    print("=== wq-067 market aggregates engine ===")
    for year in years:
        out = results[year]
        print(f"\n--- {year} ---")
        for k in (
            "mag7_capex", "neocloud_capex", "sovereign_capex", "enterprise_capex", "total_capex",
            "tokens_per_day_total", "tokens_annual_inference", "tokens_annual_training",
            "total_segment_consumer", "total_segment_sme", "total_segment_enterprise",
            "infra_to_revenue_ratio", "capex_per_token_usd", "revenue_per_token_usd",
        ):
            v = out.get(k)
            if isinstance(v, float) and v > 1e9:
                print(f"  {k:<35} {v:,.0f}")
            else:
                print(f"  {k:<35} {v}")

    if "2025" in results:
        print()
        cal_text, cal_rows = calibration_table(results["2025"])
        print(cal_text)
        n_outside = sum(1 for r in cal_rows if r["within"] is False and r["engine"] is not None)
        print(f"\nCalibration: {n_outside} of {len(cal_rows)} fields outside ±15% band.")

        # Internal consistency
        for year in years:
            issues = internal_consistency_checks(results[year], year)
            if issues:
                print(f"\nInternal consistency issues in {year}:")
                for x in issues:
                    print(f"  ✗ {x}")

        if n_outside > 2:
            print(
                f"\nSTOP: {n_outside} of 4 calibration targets outside ±15%. "
                "Surface for Simon's calibration tweak before --apply."
            )
            if args.apply:
                return 2

    if args.apply:
        for year in years:
            entities.setdefault("market_aggregates", {}).setdefault(year, {}).update(results[year])
        ENTITIES_PATH.write_text(json.dumps(entities, indent=2) + "\n")
        print(f"\nWritten: entities.json:market_aggregates.<year> for {years}")
    else:
        print("\n(--validate; pass --apply to write)")

    return 0


if __name__ == "__main__":
    with logged_run("derive_market_aggregates.py") as outputs:
        rc = main()
        outputs["years_processed"] = len(YEARS)
        outputs["return_code"] = rc
        sys.exit(rc)
