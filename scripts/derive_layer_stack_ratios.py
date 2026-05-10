#!/usr/bin/env python3
"""wq-102 Stage 2 — Compute layer-stack ratios anchored on gross apps revenue.

The homepage hero stack ("Capex 19× Apps Revenue · 2025 calendar", etc.) and
hook ratio ("$2.50 of compute spend stands behind every $1 of customer-paid
AI Apps Revenue") are ratios of an upstream layer to apps revenue. The
existing `derive_compute_revenue.py` already populates a few ratios (e.g.
`apps_to_compute_2025`) anchored on NET apps revenue, but the public-facing
"Apps Revenue" pill uses GROSS, so the ratios on the page need the gross
denominator to stay internally consistent.

This script post-processes `site-data.json:compute.layer_stack_ratios` to
add:

  - capex_to_apps_gross_x
  - usage_notional_to_apps_gross_x
  - compute_to_apps_gross_x          (also as $/per-$1: compute_per_dollar_apps_gross)
  - power_to_apps_gross_x
  - usage_notional_2025_usd_b        (tokens × 365 × $/M token rate)

Runs after `generate_site_data.py` + `derive_compute_revenue.py`, before
`render_numbers.py`.

CLI:
  python3 scripts/derive_layer_stack_ratios.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_DATA_PATH = ROOT / "site-data.json"
ENTITIES_PATH = ROOT / "entities.json"

# Notional output-token rate for the Usage Ledger (wq-093 hero subtitle).
# This is editorial methodology, not a sourced number — kept as a constant
# until the Usage Ledger engine ships and surfaces a sourced rate.
USAGE_NOTIONAL_RATE_USD_PER_M_OUTPUT_TOKENS = 1.25


def main() -> int:
    site = json.loads(SITE_DATA_PATH.read_text())
    ents = json.loads(ENTITIES_PATH.read_text())

    sankey = site.get("sankey", {})
    compute = site.get("compute", {})
    cumulative = site.get("cumulative", {})
    market_2025 = ents.get("market_aggregates", {}).get("2025", {})

    apps_gross = sankey.get("totalCustomerRevenue_gross")
    capex_2025 = market_2025.get("total_capex")
    compute_gross = compute.get("compute_revenue_2025_gross_usd_b")
    tokens_per_day = cumulative.get("tokens_2025_annualized")
    ls = compute.setdefault("layer_stack_ratios", {})
    power_2025 = ls.get("power_revenue_2025_usd_b")

    if not apps_gross or apps_gross <= 0:
        print("! totalCustomerRevenue_gross missing or zero; cannot compute ratios", file=sys.stderr)
        return 1

    # Usage notional in $B/yr. tokens_per_day is in T (trillion); rate is $/M.
    # T/day × 365 days × $/M = T-tokens × 365 × $/M. Convert to $B:
    #   T = 1e12, M = 1e6, so T/M = 1e6, then × 1e9 to get $: 1e6 × $/M × $...
    # Simpler: tokens_per_day(T) × 365 × $/M / 1000 gives $B.
    usage_notional_b = None
    if tokens_per_day:
        usage_notional_b = round(
            tokens_per_day * 365 * USAGE_NOTIONAL_RATE_USD_PER_M_OUTPUT_TOKENS / 1000.0,
            2,
        )

    def ratio(num):
        return round(num / apps_gross, 2) if num else None

    ls["apps_revenue_2025_gross_usd_b"] = round(apps_gross, 3)
    ls["capex_2025_usd_b"] = capex_2025
    ls["capex_to_apps_gross_x"] = ratio(capex_2025)
    ls["compute_to_apps_gross_x"] = ratio(compute_gross)
    ls["compute_per_dollar_apps_gross"] = (
        round(compute_gross / apps_gross, 2) if compute_gross else None
    )
    ls["power_to_apps_gross_x"] = ratio(power_2025)
    ls["usage_notional_2025_usd_b"] = usage_notional_b
    ls["usage_notional_to_apps_gross_x"] = ratio(usage_notional_b)
    ls["usage_notional_rate_usd_per_m_output_tokens"] = USAGE_NOTIONAL_RATE_USD_PER_M_OUTPUT_TOKENS
    ls["_layer_stack_gross_doc"] = (
        "Layer-stack ratios anchored on GROSS apps revenue "
        "(site-data.sankey.totalCustomerRevenue_gross). The homepage "
        "hero stack reads against gross because the Revenue pill "
        "shows gross. Existing apps_to_compute_2025 etc. anchor on "
        "NET — preserved for backwards compat with prior consumers."
    )

    SITE_DATA_PATH.write_text(json.dumps(site, indent=2))
    print(
        "Wrote layer-stack gross ratios:\n"
        f"  capex_to_apps_gross_x         = {ls['capex_to_apps_gross_x']}× "
        f"(${capex_2025}B / ${round(apps_gross, 2)}B)\n"
        f"  usage_notional_to_apps_gross_x = {ls['usage_notional_to_apps_gross_x']}× "
        f"(usage notional ${usage_notional_b}B / ${round(apps_gross, 2)}B)\n"
        f"  compute_to_apps_gross_x       = {ls['compute_to_apps_gross_x']}× "
        f"(${compute_gross}B / ${round(apps_gross, 2)}B)\n"
        f"  compute_per_dollar_apps_gross = ${ls['compute_per_dollar_apps_gross']} per $1\n"
        f"  power_to_apps_gross_x         = {ls['power_to_apps_gross_x']}× "
        f"(${power_2025}B / ${round(apps_gross, 2)}B)\n"
        f"  usage_notional_2025_usd_b     = ${usage_notional_b}B"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
