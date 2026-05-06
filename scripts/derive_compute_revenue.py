#!/usr/bin/env python3
"""wq-091 — Compute Revenue aggregator (v3: plain-English segment schema).

Reads data/compute_disclosures.json (filings extracts + per-segment decomposition),
applies the three-segment aggregation rule, and writes to site-data.json:compute.* .

Segments (plain-English; replaces wq-089 'Bucket 1/2/3' shorthand):
  - frontier_lab_compute  — Model Providers paying external hyperscalers/neoclouds
                            for compute to train and serve their own foundation
                            models. Circular-financing line.
  - ai_workload_compute   — AI Natives + enterprises + model-serving infra cos +
                            sovereign workloads buying raw cloud capacity.
  - hosted_model_apis     — Packaged token APIs (Bedrock, Azure OpenAI Service,
                            Vertex partner-served). Pass-through to model labs
                            applies HERE only.

D6 verification gate (data/methodology_constants.json:compute_revenue) confirms
all four reviewed entities (MSFT/AMZN/GOOGL/ORCL) use principal (gross) revenue
recognition for AI reseller arrangements. The aggregator additionally enforces:
  - Copilot scope-out (copilot_excluded_*_usd_b is published separately, not
    summed into compute totals)
  - Pass-through scoped to Hosted model APIs only (was applied to total AI
    revenue prior to wq-089 — overstated by ~10x)

Aggregation rule:
  Compute Revenue (gross, post-Copilot) = Σ (frontier_lab + ai_workload + hosted_model_apis_gross)
  Compute Revenue (net of Hosted model APIs pass-through) = gross − Σ hosted_model_apis_pass_through
  Frontier lab compute (the circular-financing line) = Σ frontier_lab_compute
  Copilot excluded (tracked-but-not-published-on-Compute) = Σ copilot_excluded

Layer-Stack uses sum-of-quarterlies for compute (same time-basis as the other
three layers) and the live measured-cohort apps revenue from
site-data.json:sankey.totalCustomerRevenue.

CLI:
  python3 scripts/derive_compute_revenue.py --validate
  python3 scripts/derive_compute_revenue.py --apply        # MUTATES site-data.json
  python3 scripts/derive_compute_revenue.py --print-summary
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DISCLOSURES_PATH = ROOT / "data" / "compute_disclosures.json"
METHODOLOGY_PATH = ROOT / "data" / "methodology_constants.json"
SITE_DATA_PATH = ROOT / "site-data.json"

CATEGORY_LABELS = {
    "mag3": "Mag3 hyperscalers",
    "oracle": "Oracle",
    "public_neocloud": "Public neoclouds",
    "private_neocloud": "Private neoclouds",
}


def load_disclosures() -> dict:
    with open(DISCLOSURES_PATH) as f:
        return json.load(f)


def load_methodology() -> dict:
    with open(METHODOLOGY_PATH) as f:
        return json.load(f)


def load_site_data() -> dict:
    with open(SITE_DATA_PATH) as f:
        return json.load(f)


def component_compute_gross_2025(c: dict) -> float:
    """Per-component gross compute revenue (post-Copilot)."""
    return (
        c["frontier_lab_compute_2025_usd_b"]
        + c["ai_workload_compute_2025_usd_b"]
        + c["hosted_model_apis_gross_2025_usd_b"]
    )


def component_compute_gross_q1_2026(c: dict) -> float:
    return (
        c["frontier_lab_compute_q1_2026_usd_b"]
        + c["ai_workload_compute_q1_2026_usd_b"]
        + c["hosted_model_apis_gross_q1_2026_usd_b"]
    )


def component_compute_net_2025(c: dict) -> float:
    return component_compute_gross_2025(c) - c["hosted_model_apis_pass_through_2025_usd_b"]


def component_compute_net_q1_2026(c: dict) -> float:
    return (
        component_compute_gross_q1_2026(c)
        - c["hosted_model_apis_pass_through_q1_2026_usd_b"]
    )


def aggregate(disclosures: dict, methodology: dict, site_data: dict) -> dict:
    """Compute segment aggregates + concentration shares for site-data.json:compute."""
    components = disclosures["components"]

    # D6 gate — refuse to aggregate if any component is not principal-confirmed.
    treatment_ok = all(
        c.get("principal_agent_confirmed") is True and c.get("treatment") == "principal"
        for c in components.values()
    )
    if not treatment_ok:
        raise SystemExit(
            "D6 gate FAIL: not all components are principal-treatment-confirmed. "
            "Aggregation rule changes if any component shifts to agent treatment. "
            "Stop and update aggregator."
        )

    # Segment sums (ecosystem-wide, 2025).
    frontier_lab_compute_2025 = sum(c["frontier_lab_compute_2025_usd_b"] for c in components.values())
    ai_workload_compute_2025 = sum(c["ai_workload_compute_2025_usd_b"] for c in components.values())
    hosted_model_apis_gross_2025 = sum(c["hosted_model_apis_gross_2025_usd_b"] for c in components.values())
    hosted_model_apis_pass_through_2025 = sum(
        c["hosted_model_apis_pass_through_2025_usd_b"] for c in components.values()
    )
    hosted_model_apis_net_2025 = hosted_model_apis_gross_2025 - hosted_model_apis_pass_through_2025
    copilot_excluded_2025 = sum(c["copilot_excluded_2025_usd_b"] for c in components.values())

    # Segment sums (Q1 2026).
    frontier_lab_compute_q1_2026 = sum(c["frontier_lab_compute_q1_2026_usd_b"] for c in components.values())
    ai_workload_compute_q1_2026 = sum(c["ai_workload_compute_q1_2026_usd_b"] for c in components.values())
    hosted_model_apis_gross_q1_2026 = sum(c["hosted_model_apis_gross_q1_2026_usd_b"] for c in components.values())
    hosted_model_apis_pass_through_q1_2026 = sum(
        c["hosted_model_apis_pass_through_q1_2026_usd_b"] for c in components.values()
    )
    hosted_model_apis_net_q1_2026 = hosted_model_apis_gross_q1_2026 - hosted_model_apis_pass_through_q1_2026
    copilot_excluded_q1_2026 = sum(c["copilot_excluded_q1_2026_usd_b"] for c in components.values())

    # Compute Revenue gross (post-Copilot) = frontier_lab + ai_workload + hosted_model_apis_gross.
    # Copilot is scoped OUT — tracked separately, not summed in.
    compute_gross_2025 = frontier_lab_compute_2025 + ai_workload_compute_2025 + hosted_model_apis_gross_2025
    compute_net_2025 = compute_gross_2025 - hosted_model_apis_pass_through_2025

    compute_gross_q1_2026 = (
        frontier_lab_compute_q1_2026 + ai_workload_compute_q1_2026 + hosted_model_apis_gross_q1_2026
    )
    compute_net_q1_2026 = compute_gross_q1_2026 - hosted_model_apis_pass_through_q1_2026

    # Concentration uses gross-disclosed compute (post-Copilot).
    by_category = {k: 0.0 for k in CATEGORY_LABELS}
    for c in components.values():
        by_category[c["category"]] += component_compute_gross_q1_2026(c)

    concentration = {
        "mag3_share_pct": round(by_category["mag3"] / compute_gross_q1_2026 * 100, 1),
        "oracle_share_pct": round(by_category["oracle"] / compute_gross_q1_2026 * 100, 1),
        "public_neocloud_share_pct": round(by_category["public_neocloud"] / compute_gross_q1_2026 * 100, 1),
        "private_neocloud_share_pct": round(by_category["private_neocloud"] / compute_gross_q1_2026 * 100, 1),
        "other_share_pct": 0.0,
    }

    # YoY growth headline — sum-of-quarterlies 2025 vs reference 2024.
    quarterly = disclosures["quarterly"]
    sum_q_2025_gross = 0.0
    for q in quarterly:
        if q["quarter"].startswith("2025"):
            for k, v in q.items():
                if k != "quarter":
                    sum_q_2025_gross += v
    annualised_gross_pre_copilot = compute_gross_2025 + copilot_excluded_2025
    copilot_ratio = (
        copilot_excluded_2025 / annualised_gross_pre_copilot
        if annualised_gross_pre_copilot > 0
        else 0.0
    )
    sum_q_2025_post_copilot = sum_q_2025_gross * (1 - copilot_ratio)

    yoy = disclosures.get("yoy_reference", {})
    compute_2024_gross = yoy.get("compute_revenue_2024_gross_usd_b")
    yoy_growth_pct = None
    if compute_2024_gross:
        yoy_growth_pct = round(
            (sum_q_2025_post_copilot - compute_2024_gross) / compute_2024_gross * 100,
            1,
        )

    # Layer-Stack ratios — all four layers on lookback 2025 actuals.
    ls = disclosures["layer_stack_inputs"]
    apps_revenue_live = round(
        site_data.get("sankey", {}).get("totalCustomerRevenue", 0.0),
        3,
    )
    silicon = ls["silicon_revenue_2025_usd_b"]
    power = ls["power_revenue_2025_usd_b"]
    layer_stack = {
        "apps_revenue_2025_usd_b": apps_revenue_live,
        "apps_revenue_2025_basis": ls["apps_revenue_2025_basis"],
        "apps_revenue_2025_source": ls["apps_revenue_2025_source"],
        "apps_revenue_2025_tier": ls["apps_revenue_2025_tier"],
        "compute_revenue_2025_gross_usd_b": round(sum_q_2025_post_copilot, 2),
        "compute_revenue_2025_net_usd_b": round(
            sum_q_2025_post_copilot - hosted_model_apis_pass_through_2025, 2
        ),
        "compute_revenue_2025_basis": ls["compute_revenue_2025_basis"],
        "compute_revenue_2025_tier": ls["compute_revenue_2025_tier"],
        "silicon_revenue_2025_usd_b": silicon,
        "silicon_revenue_2025_source": ls["silicon_revenue_2025_source"],
        "silicon_revenue_2025_tier": ls["silicon_revenue_2025_tier"],
        "power_revenue_2025_usd_b": power,
        "power_revenue_2025_source": ls["power_revenue_2025_source"],
        "power_revenue_2025_tier": ls["power_revenue_2025_tier"],
        "apps_to_compute_2025": (
            round(
                (sum_q_2025_post_copilot - hosted_model_apis_pass_through_2025)
                / max(apps_revenue_live, 1e-6),
                2,
            )
            if apps_revenue_live > 0
            else None
        ),
        "compute_to_silicon_2025": round(
            silicon / max(sum_q_2025_post_copilot - hosted_model_apis_pass_through_2025, 1e-6), 2
        ),
        "silicon_to_power_2025": round(power / max(silicon, 1e-6), 2),
    }

    # Build per-component output (preserved fields for tooltip + side-panel).
    components_out = {}
    for slug, c in components.items():
        components_out[slug] = {
            "label": c["label"],
            "entity_slug": c["entity_slug"],
            "category": c["category"],
            "category_label": CATEGORY_LABELS[c["category"]],
            # Plain-English segment fields (canonical schema)
            "frontier_lab_compute_2025_usd_b": c["frontier_lab_compute_2025_usd_b"],
            "ai_workload_compute_2025_usd_b": c["ai_workload_compute_2025_usd_b"],
            "hosted_model_apis_gross_2025_usd_b": c["hosted_model_apis_gross_2025_usd_b"],
            "hosted_model_apis_pass_through_2025_usd_b": c["hosted_model_apis_pass_through_2025_usd_b"],
            "hosted_model_apis_net_2025_usd_b": c["hosted_model_apis_net_2025_usd_b"],
            "copilot_excluded_2025_usd_b": c["copilot_excluded_2025_usd_b"],
            "frontier_lab_compute_q1_2026_usd_b": c["frontier_lab_compute_q1_2026_usd_b"],
            "ai_workload_compute_q1_2026_usd_b": c["ai_workload_compute_q1_2026_usd_b"],
            "hosted_model_apis_gross_q1_2026_usd_b": c["hosted_model_apis_gross_q1_2026_usd_b"],
            "hosted_model_apis_pass_through_q1_2026_usd_b": c["hosted_model_apis_pass_through_q1_2026_usd_b"],
            "hosted_model_apis_net_q1_2026_usd_b": c["hosted_model_apis_net_q1_2026_usd_b"],
            "copilot_excluded_q1_2026_usd_b": c["copilot_excluded_q1_2026_usd_b"],
            # Derived per-component compute totals (post-Copilot, what shows on /compute.html)
            "compute_gross_2025_usd_b": round(component_compute_gross_2025(c), 3),
            "compute_net_2025_usd_b": round(component_compute_net_2025(c), 3),
            "compute_gross_q1_2026_usd_b": round(component_compute_gross_q1_2026(c), 3),
            "compute_net_q1_2026_usd_b": round(component_compute_net_q1_2026(c), 3),
            "tier_frontier_lab_compute": c.get("tier_frontier_lab_compute"),
            "tier_ai_workload_compute": c.get("tier_ai_workload_compute"),
            "tier_hosted_model_apis": c.get("tier_hosted_model_apis"),
            "segment_basis": c["segment_basis"],
            "principal_agent_confirmed": c["principal_agent_confirmed"],
            "treatment": c["treatment"],
            "ai_run_rate_disclosure": c.get("ai_run_rate_disclosure"),
            "underlying_segment": c.get("underlying_segment"),
            "retrievedAt": c["retrievedAt"],
            "nextReview": c["nextReview"],
            "confidence": c["confidence"],
            "notes": c.get("notes"),
        }

    return {
        "lastReportedQuarter": disclosures["lastReportedQuarter"],
        # Headline aggregates (annualised, post-Copilot)
        "compute_revenue_2025_gross_usd_b": round(compute_gross_2025, 2),
        "compute_revenue_2025_net_usd_b": round(compute_net_2025, 2),
        "model_pass_through_2025_usd_b": round(hosted_model_apis_pass_through_2025, 3),
        "compute_revenue_q1_2026_gross_usd_b": round(compute_gross_q1_2026, 2),
        "compute_revenue_q1_2026_net_usd_b": round(compute_net_q1_2026, 2),
        # Segment aggregates — first-class outputs (plain-English schema)
        "frontier_lab_compute_2025_usd_b": round(frontier_lab_compute_2025, 2),
        "ai_workload_compute_2025_usd_b": round(ai_workload_compute_2025, 2),
        "hosted_model_apis_gross_2025_usd_b": round(hosted_model_apis_gross_2025, 2),
        "hosted_model_apis_pass_through_2025_usd_b": round(hosted_model_apis_pass_through_2025, 3),
        "hosted_model_apis_net_2025_usd_b": round(hosted_model_apis_net_2025, 2),
        "frontier_lab_compute_q1_2026_usd_b": round(frontier_lab_compute_q1_2026, 2),
        "ai_workload_compute_q1_2026_usd_b": round(ai_workload_compute_q1_2026, 2),
        "hosted_model_apis_gross_q1_2026_usd_b": round(hosted_model_apis_gross_q1_2026, 2),
        "hosted_model_apis_pass_through_q1_2026_usd_b": round(hosted_model_apis_pass_through_q1_2026, 3),
        "hosted_model_apis_net_q1_2026_usd_b": round(hosted_model_apis_net_q1_2026, 2),
        # Copilot scope-out (tracked but not part of compute totals)
        "copilot_excluded_2025_usd_b": round(copilot_excluded_2025, 2),
        "copilot_excluded_q1_2026_usd_b": round(copilot_excluded_q1_2026, 2),
        # YoY growth headline (Box 4)
        "yoy_growth_pct": yoy_growth_pct,
        "compute_revenue_2024_gross_usd_b": compute_2024_gross,
        "compute_revenue_2025_gross_sum_of_quarterlies_usd_b": round(sum_q_2025_post_copilot, 2),
        # Concentration + Layer Stack
        "concentration": concentration,
        "layer_stack_ratios": layer_stack,
        "quarterly": disclosures["quarterly"],
        "components": components_out,
        # Provenance + gate
        "_d6_gate": "PASS — principal-everywhere confirmed per data/methodology_constants.json:compute_revenue.principal_agent_treatment; Copilot scope-out applied; pass-through scoped to Hosted model APIs only.",
        "_engine": "scripts/derive_compute_revenue.py (wq-091 v3 — plain-English segment schema)",
        "_generatedAt": datetime.now(timezone.utc).isoformat(),
        "_notes": (
            "Three-segment model: Frontier lab compute (the circular-financing "
            "line — Model Providers paying external hyperscalers/neoclouds), AI "
            "workload compute (AI Natives + enterprises + sovereign workloads), "
            "Hosted model APIs (packaged token APIs). Pass-through applies to "
            "Hosted model APIs only. Copilot scoped OUT — tracked separately "
            "under copilot_excluded_*. See /methodology.html §Compute Revenue — "
            "three-segment model."
        ),
    }


def print_summary(block: dict) -> None:
    print(f"\nCompute Ledger v3 — derived {block['_generatedAt']}")
    print(f"  Last reported quarter: {block['lastReportedQuarter']}")
    print(f"  D6 gate: {block['_d6_gate']}")
    print()
    print("  ─── 2025 (annualised, post-Copilot) ───")
    print(f"  Frontier lab compute:                  ${block['frontier_lab_compute_2025_usd_b']}B")
    print(f"  AI workload compute:                   ${block['ai_workload_compute_2025_usd_b']}B")
    print(f"  Hosted model APIs gross:               ${block['hosted_model_apis_gross_2025_usd_b']}B")
    print(f"  Hosted model APIs pass-through:        ${block['model_pass_through_2025_usd_b']}B")
    print(f"  Hosted model APIs net:                 ${block['hosted_model_apis_net_2025_usd_b']}B")
    print(f"  Compute Revenue gross (post-Copilot):  ${block['compute_revenue_2025_gross_usd_b']}B")
    print(f"  Compute Revenue net:                   ${block['compute_revenue_2025_net_usd_b']}B")
    print(f"  Copilot excluded (future Apps Ledger): ${block['copilot_excluded_2025_usd_b']}B")
    print()
    print("  ─── Q1 2026 (post-Copilot) ───")
    print(f"  Frontier lab compute:           ${block['frontier_lab_compute_q1_2026_usd_b']}B")
    print(f"  AI workload compute:            ${block['ai_workload_compute_q1_2026_usd_b']}B")
    print(f"  Hosted model APIs gross:        ${block['hosted_model_apis_gross_q1_2026_usd_b']}B")
    print(f"  Compute Revenue gross:          ${block['compute_revenue_q1_2026_gross_usd_b']}B")
    print(f"  Compute Revenue net:            ${block['compute_revenue_q1_2026_net_usd_b']}B")
    print(f"  Copilot excluded:               ${block['copilot_excluded_q1_2026_usd_b']}B")
    print()
    print(
        f"  YoY growth (sum-of-quarterlies post-Copilot 2025 vs 2024 reference): "
        f"{block['yoy_growth_pct']}%"
    )
    print()
    c = block["concentration"]
    print("  Concentration (Q1 2026 gross-basis, post-Copilot):")
    print(f"    Mag3:               {c['mag3_share_pct']}%")
    print(f"    Oracle:             {c['oracle_share_pct']}%")
    print(f"    Public neocloud:    {c['public_neocloud_share_pct']}%")
    print(f"    Private neocloud:   {c['private_neocloud_share_pct']}%")
    print()
    ls = block["layer_stack_ratios"]
    print("  Layer-Stack (lookback 2025, sum-of-quarterlies basis):")
    print(f"    Apps Revenue (cohort, live from sankey): ${ls['apps_revenue_2025_usd_b']}B")
    print(
        f"    Compute Revenue (gross, sum-of-quarterlies post-Copilot): "
        f"${ls['compute_revenue_2025_gross_usd_b']}B"
    )
    print(f"    Compute Revenue (net): ${ls['compute_revenue_2025_net_usd_b']}B")
    print(f"    Silicon Revenue: ${ls['silicon_revenue_2025_usd_b']}B")
    print(f"    Power: ${ls['power_revenue_2025_usd_b']}B")
    print()
    print(f"  Components ({len(block['components'])}):")
    for slug, c in block["components"].items():
        print(
            f"    {c['label']:30s} compute gross 2025 ${c['compute_gross_2025_usd_b']:.2f}B "
            f"(Frontier ${c['frontier_lab_compute_2025_usd_b']:.2f}B / "
            f"Workload ${c['ai_workload_compute_2025_usd_b']:.2f}B / "
            f"Hosted APIs ${c['hosted_model_apis_gross_2025_usd_b']:.2f}B); "
            f"copilot excluded ${c['copilot_excluded_2025_usd_b']:.2f}B"
        )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true",
                    help="Validate the disclosures file and print derived block. No write.")
    ap.add_argument("--apply", action="store_true",
                    help="Write derived block to site-data.json:compute.")
    ap.add_argument("--print-summary", action="store_true",
                    help="Print derived summary without writing.")
    args = ap.parse_args()

    disclosures = load_disclosures()
    methodology = load_methodology()
    site_data = load_site_data()
    block = aggregate(disclosures, methodology, site_data)

    if args.validate or args.print_summary or not args.apply:
        print_summary(block)

    if args.apply:
        site_data["compute"] = block
        with open(SITE_DATA_PATH, "w") as f:
            json.dump(site_data, f, indent=2)
        print(
            f"\n✓ Wrote site-data.json:compute "
            f"(gross ${block['compute_revenue_2025_gross_usd_b']}B, "
            f"net ${block['compute_revenue_2025_net_usd_b']}B, "
            f"frontier lab compute ${block['frontier_lab_compute_2025_usd_b']}B, "
            f"copilot excluded ${block['copilot_excluded_2025_usd_b']}B)"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
