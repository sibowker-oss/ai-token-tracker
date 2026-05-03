#!/usr/bin/env python3
"""wq-063 — Cumulative aggregator.

Walks entities.json:market_aggregates across 2023–2025 (extending to 2026
once populated). For each year, captures:
  - customer_revenue_gross  (sum of non-VC buyers = sum of grossed channels)
  - customer_revenue_net    (provider-received chPass = sum of providers)
  - capex                   (mag7_capex + neocloud_capex if present)
  - tokens                  (annual token volume if present; placeholder)

Writes the result into entities.json:market_aggregates._cumulative_2023_2025.
Site-data.json mirror is written by generate_site_data.py.

Falls back to per-entity collected_revenue when market_aggregates.<year> is
absent, so the cumulative always shows the best available number per year.

CLI:
  python3 scripts/derive_cumulative_aggregates.py --dry-run
  python3 scripts/derive_cumulative_aggregates.py --apply  # MUTATES entities.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTITIES_PATH = ROOT / "entities.json"
OVERRIDES_PATH = ROOT / "data" / "consensus_overrides.json"

YEARS = ["2023", "2024", "2025"]


_SCHEMA_DOC_KEYS = {"_doc", "_schema_examples", "_schema", "_notes"}


def _load_overrides() -> dict:
    """Editorial overrides. Drops schema/doc keys (`_doc`, `_schema_examples`)
    but RETAINS real override keys that happen to start with `_` like
    `_cumulative_2023_2025.<field>`. Checks expiry — expired overrides are ignored."""
    if not OVERRIDES_PATH.exists():
        return {}
    raw = json.loads(OVERRIDES_PATH.read_text())
    today = "2026-05-03"  # used as the comparison date for expiry semantics
    out = {}
    for k, v in raw.items():
        if k in _SCHEMA_DOC_KEYS:
            continue
        if not isinstance(v, dict):
            continue
        # A real override always has a 'value' field; schema examples nest other dicts
        if "value" not in v:
            continue
        expires = v.get("expires_at")
        if expires and expires < today:
            continue
        out[k] = v
    return out


def _apply_override(field_name: str, engine_value, overrides: dict) -> tuple:
    """Returns (final_value, override_metadata_or_None). field_name is
    the dotted key as it appears in consensus_overrides.json."""
    ov = overrides.get(field_name)
    if not ov:
        return (engine_value, None)
    return (ov.get("value"), {
        "engine_value": engine_value,
        "override_value": ov.get("value"),
        "reason": ov.get("reason"),
        "set_by": ov.get("set_by"),
        "set_at": ov.get("set_at"),
        "expires_at": ov.get("expires_at"),
    })


def _gross_from_channels_grossed(channels_grossed: list) -> float | None:
    """Sum channels_grossed[*].value — this IS the buyer-gross customer total
    (engine grosses up channels so chPass = sum(provider routing) and the
    grossed value includes channel margins that flow direct to cashflow)."""
    if not channels_grossed:
        return None
    return round(sum(c.get("value", 0) for c in channels_grossed), 4)


def _gross_from_per_entity(companies: list, year: str) -> float | None:
    """Fallback: sum collected_revenue across all companies for a year.
    Less precise than the engine output (no channel grossing applied) but
    gives a real number for years without a full engine run."""
    total = 0.0
    n = 0
    for c in companies:
        cr = ((c.get("financials") or {}).get(year) or {}).get("collected_revenue")
        if isinstance(cr, (int, float)):
            total += cr
            n += 1
    return round(total, 4) if n > 0 else None


def _capex_for_year(ma_year: dict) -> float:
    """Capex = mag7_capex + neocloud_capex + sovereign_capex (when present).
    Currently only mag7_capex is populated; others default to 0."""
    return sum(
        (ma_year.get(k) or 0) for k in ("mag7_capex", "neocloud_capex", "sovereign_capex")
    )


def _tokens_for_year(ma_year: dict) -> float:
    """Annual token volume. Currently no aggregated annual field exists in
    market_aggregates — return None and let the renderer fall back to the
    hardcoded display value with a documented warning."""
    val = ma_year.get("tokens_annual") or ma_year.get("annual_tokens")
    return val if isinstance(val, (int, float)) else None


def derive_cumulative(entities: dict) -> dict:
    ma = entities.get("market_aggregates") or {}
    companies = entities.get("companies") or []

    by_year: dict = {}
    cumulative = {
        "customer_revenue_gross": 0.0,
        "customer_revenue_net": 0.0,
        "capex": 0.0,
        "tokens": 0.0,
    }
    sources_log: list[str] = []

    for year in YEARS:
        ma_year = ma.get(year) or {}

        # Net (provider-received) — engine output
        net = ma_year.get("total_customer_revenue")

        # Gross (buyer-paid, includes channel margins)
        # Preference: engine-written total_customer_revenue_gross if present;
        # fallback: sum of channels_grossed; then per-entity collected_revenue.
        gross = ma_year.get("total_customer_revenue_gross")
        if gross is None:
            gross = _gross_from_channels_grossed(ma_year.get("channels_grossed") or [])
        gross_source = "engine_gross_field"
        if gross is None:
            gross = _gross_from_channels_grossed(ma_year.get("channels_grossed") or [])
            if gross is not None:
                gross_source = "channels_grossed_sum"
        if gross is None:
            gross = _gross_from_per_entity(companies, year)
            gross_source = "per_entity_collected_revenue" if gross is not None else "missing"

        capex = _capex_for_year(ma_year) if ma_year else 0
        tokens = _tokens_for_year(ma_year) if ma_year else None

        by_year[year] = {
            "customer_revenue_gross": gross,
            "customer_revenue_net": net,
            "capex": capex if capex else None,
            "tokens": tokens,
            "_gross_source": gross_source,
            "_engine_run": "_engine_run_at" in ma_year,
        }
        if gross is not None:
            cumulative["customer_revenue_gross"] += gross
        if net is not None:
            cumulative["customer_revenue_net"] += net
        cumulative["capex"] += capex or 0
        if tokens:
            cumulative["tokens"] += tokens

        sources_log.append(f"{year}: gross={gross} ({gross_source}), net={net}, capex={capex or 0}")

    cumulative["customer_revenue_gross"] = round(cumulative["customer_revenue_gross"], 4)
    cumulative["customer_revenue_net"] = round(cumulative["customer_revenue_net"], 4)
    cumulative["capex"] = round(cumulative["capex"], 4)
    cumulative["by_year"] = by_year
    cumulative["capex_total"] = round(cumulative["capex"], 4)

    # Tokens display value: prefer 2025 annualized if present, else null with
    # caveat — front-end falls back to hardcoded ~360T in that case (per brief §5).
    cumulative["tokens_2025_annualized"] = by_year.get("2025", {}).get("tokens")

    yr_2025_gross = by_year.get("2025", {}).get("customer_revenue_gross")
    if cumulative["capex_total"] and yr_2025_gross:
        cumulative["infra_to_revenue_ratio_2025"] = round(
            cumulative["capex_total"] / yr_2025_gross
        )
    else:
        cumulative["infra_to_revenue_ratio_2025"] = None

    # ── Editorial overrides (consensus_overrides.json) ────────────────────
    # Each override key is "_cumulative_2023_2025.<field>". When present and
    # not expired, override.value wins over engine output. Engine value is
    # preserved on the cumulative._overrides metadata for audit traceability.
    overrides = _load_overrides()
    overrides_log = {}
    for field in ("capex_total", "customer_revenue_gross", "customer_revenue_net", "tokens_2025_annualized"):
        key = f"_cumulative_2023_2025.{field}"
        engine_val = cumulative.get(field)
        final_val, meta = _apply_override(key, engine_val, overrides)
        if meta is not None:
            cumulative[field] = final_val
            overrides_log[field] = meta
    # If overrides changed gross/capex, recompute ratio. Match the semantics
    # that index.html SCENARIOS uses (capex_total / cumulative gross), so the
    # field served from site-data.json:cumulative agrees with the rendered
    # hook-ratio number.
    if overrides_log and cumulative.get("capex_total") and cumulative.get("customer_revenue_gross"):
        cumulative["infra_to_revenue_ratio_2025"] = round(
            cumulative["capex_total"] / cumulative["customer_revenue_gross"]
        )
    cumulative["_overrides"] = overrides_log

    cumulative["_engine"] = "scripts/derive_cumulative_aggregates.py (wq-063)"
    cumulative["_sources"] = sources_log
    cumulative["_doc"] = (
        "Cumulative 2023–2025 totals. Buyer-gross is the public headline "
        "number (what customers actually paid; includes channel margins). "
        "Net is provider-received chPass. Years without a market_aggregates "
        "entry fall back to per-entity collected_revenue summing where "
        "available. Tokens require an annual aggregation field on "
        "market_aggregates that doesn't yet exist for prior years; falls "
        "back to null and the front-end keeps its hardcoded ~360T display."
    )

    return cumulative


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write back into entities.json")
    ap.add_argument("--dry-run", action="store_true", help="print to stdout only")
    args = ap.parse_args()

    if not args.apply and not args.dry_run:
        args.dry_run = True

    entities = json.loads(ENTITIES_PATH.read_text())
    cumulative = derive_cumulative(entities)

    print("=== wq-063 cumulative aggregates ===")
    for year in YEARS:
        y = cumulative["by_year"][year]
        print(
            f"  {year}: gross={y['customer_revenue_gross']} "
            f"net={y['customer_revenue_net']} "
            f"capex={y['capex']} tokens={y['tokens']} "
            f"({y['_gross_source']})"
        )
    print(
        f"  CUMULATIVE: gross={cumulative['customer_revenue_gross']} "
        f"net={cumulative['customer_revenue_net']} "
        f"capex_total={cumulative['capex_total']} "
        f"ratio_2025={cumulative['infra_to_revenue_ratio_2025']}"
    )

    # Sanity gate: 2024 gross should not exceed 2025 gross (would imply
    # negative growth, which contradicts every public source).
    yr_2024 = cumulative["by_year"]["2024"]["customer_revenue_gross"]
    yr_2025 = cumulative["by_year"]["2025"]["customer_revenue_gross"]
    if yr_2024 is not None and yr_2025 is not None and yr_2024 > yr_2025:
        print(
            f"\nERROR: 2024 cr_gross ({yr_2024}) > 2025 cr_gross ({yr_2025}). "
            "Refusing to write — investigate data."
        )
        return 2

    if args.apply:
        entities.setdefault("market_aggregates", {})
        entities["market_aggregates"]["_cumulative_2023_2025"] = cumulative
        ENTITIES_PATH.write_text(json.dumps(entities, indent=2) + "\n")
        print(f"\nWritten: entities.json:market_aggregates._cumulative_2023_2025")
    else:
        print("\n(dry-run; pass --apply to write)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
