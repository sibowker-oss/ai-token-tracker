#!/usr/bin/env python3
"""wq-066 — Extract documented market-aggregate values from assumptions-audit.md.

Pulls every market-level numeric value the audit explicitly documents and
emits a structured JSON map. Where audit doesn't document a value, emits
null + the question Simon needs to answer.

Audit doc has very limited structured per-year breakdown for capex/tokens:
  - §4.1 documents 2025 totalCustomerRevenue + totalVCSubsidy (post-V3 consensus)
  - §5.1 documents 565T tokens/day total (no per-year breakdown)
  - §6 documents $250B Capex (annual; no per-year)

So most of what the extractor surfaces is "audit-only-has-2025" — earlier
years remain gaps requiring Simon's editorial input or external research.

CLI:
  python3 scripts/extract_audit_values.py
  python3 scripts/extract_audit_values.py --out data/wq-066-audit-extract.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIT_PATH = ROOT / "assumptions-audit.md"
DEFAULT_OUT = ROOT / "data" / "wq-066-audit-extract.json"


def _load_audit() -> str:
    return AUDIT_PATH.read_text()


def extract() -> dict:
    """Returns the structured audit-extract map. Not a parser — a hand-curated
    extraction that mirrors what assumptions-audit.md actually says, with
    explicit nulls for documented gaps."""
    text = _load_audit()

    # ── Verify the audit doc still has the section anchors we depend on.
    expected_anchors = [
        "## 1. Revenue Assumptions",
        "## 4. Sankey Flow Assumptions",
        "### 4.1 Top-Level Totals",
        "### 4.4 Column 3: Providers",
        "## 5. Token Volume Estimates",
        "### 5.1 Total Daily Token Estimate",
        "## 6. Dashboard Data Assumptions",
    ]
    missing = [a for a in expected_anchors if a not in text]
    if missing:
        print(f"ERROR: assumptions-audit.md missing expected anchors: {missing}", file=sys.stderr)
        return {"_error": "audit_doc_anchors_missing", "missing": missing}

    # Hand-extracted from the audit doc as of 2026-05-03 (lines surveyed:
    # §1.1 OpenAI, §1.2 Anthropic, §1.3 Google, §1.4 Other, §1.5 Trad SaaS,
    # §4.1 Top-level, §4.4 Provider table, §5.1 Token total, §6 Capex stat).
    audit = {
        "_meta": {
            "audit_doc": "assumptions-audit.md",
            "extracted_at": "2026-05-03",
            "extractor": "scripts/extract_audit_values.py (wq-066)",
            "_doc": (
                "Audit doc has limited per-year structured data. Most "
                "documented values are 2025-only. Earlier years (2023, 2024) "
                "are gaps requiring Simon's input or external research per "
                "wq-066 §3 #6 gap report."
            ),
        },

        # ── Per-year market aggregates (sparse — most are gaps) ──
        "market_aggregates": {
            "2023": {
                "total_customer_revenue": None,
                "total_customer_revenue_gross": None,
                "total_vc_subsidy": None,
                "mag7_capex": None,
                "neocloud_capex": None,
                "sovereign_capex": None,
                "enterprise_capex": None,
                "tokens_per_day_total": None,
                "_audit_section": None,
                "_gap": "audit doc has no 2023-specific market aggregates; entities.json has no 2023 collected_revenue per provider",
            },
            "2024": {
                "total_customer_revenue": None,  # only entity-level mentions ($3.6B OpenAI, $0.5B Anthropic est)
                "total_customer_revenue_gross": None,
                "total_vc_subsidy": None,
                "mag7_capex": None,
                "neocloud_capex": None,
                "sovereign_capex": None,
                "enterprise_capex": None,
                "tokens_per_day_total": None,
                "_audit_section": "§1.1 (OpenAI 2024 ~$3.6B), §1.2 (Anthropic ~$5B cumulative through early 2025)",
                "_gap": "audit doc has 2024 entity-level revenue refs but no aggregated market totals or capex/tokens",
            },
            "2025": {
                # ✓ Documented in audit §4.1
                "total_customer_revenue": 17.47,                   # §4.1 Total Customer Revenue
                "total_customer_revenue_gross": None,              # not separated in audit
                "total_vc_subsidy": 9.80,                          # §4.1 Total VC Subsidy
                "total_system_cost": 27.27,                        # §4.1 Total System
                # ✓ §6 Dashboard Data
                "mag7_capex": 250.0,                               # §6 "Capex | $250B"
                # Gaps
                "neocloud_capex": None,                            # not documented
                "sovereign_capex": None,                           # not documented
                "enterprise_capex": None,                          # not documented
                # ✓ §5.1 — note this is per-day, not per-year
                "tokens_per_day_total": 565.0,                     # §5.1 Final figure
                # ✓ §4.5 outcomes
                "total_inference_cost": 14.03,                     # §4.5 Inference
                "total_people_cost": 11.08,                        # §4.5 People/SG&A
                "total_margin": 2.15,                              # §4.5 Margin
                "_audit_section": "§1, §4, §5, §6",
            },
        },

        # ── Per-provider 2025 totals (audit §4.4) ──
        "providers_2025": {
            "openai": {"value": 13.65, "customer_revenue": 7.65, "vc_subsidy": 6.00,
                       "_audit_section": "§4.4 Column 3"},
            "anthropic": {"value": 7.71, "customer_revenue": 4.71, "vc_subsidy": 3.00,
                          "_audit_section": "§4.4 Column 3"},
            "google": {"value": 2.50, "customer_revenue": 2.00, "vc_subsidy": 0.50,
                       "_audit_section": "§4.4 Column 3"},
            "iaas": {"value": 0.80, "customer_revenue": 0.50, "vc_subsidy": 0.30,
                     "_audit_section": "§4.4 Column 3"},
        },

        # ── Per-provider 2024 collected revenue (audit §1) ──
        "entity_2024_revenue": {
            "openai": {
                "collected_revenue": 3.6,
                "_audit_section": "§1.1 (Zitron / Microsoft leaked docs; $493.8M / 0.20)",
                "_confidence": "estimated",
            },
            "anthropic": {
                "collected_revenue": 0.5,  # implied from §1.2 ($5B cumulative through early 2025, with 2024 portion ~$0.5B before 2025 ramp)
                "_audit_section": "§1.2 (cumulative $5B through early 2025; 2025 alone $4.71B implies ~$0.5B prior)",
                "_confidence": "derived",
                "_gap": "audit doesn't explicitly state 2024 standalone — derived from cumulative minus 2025",
            },
            "google": {"collected_revenue": None, "_gap": "audit only has 2025 Google revenue"},
            "meta": {"collected_revenue": None, "_gap": "audit shows $0 for 2025; 2024 not stated"},
        },

        # ── Per-provider tokens (audit §5.3) ──
        "tokens_per_day_2025": {
            "openai": 200, "anthropic": 110, "google": 90, "meta": 80,
            "deepseek": 40, "minimax": 30, "mistral": 15, "xai": 10, "moonshot": 8,
            "others_self_hosted": 134,
            "_audit_section": "§5.3",
            "_total": 717,  # sum of above
            "_gap": "entities.json model_provider tokens_per_day are stale — OpenAI=30 vs audit=200, Anthropic=6 vs 110, etc. Refresh candidate.",
        },

        # ── Cumulative (2023-2025) — what wq-063 overrides cover ──
        "cumulative_2023_2025": {
            "customer_revenue_gross": None,  # not stated as a cumulative
            "capex_total": None,             # audit only has $250B annual mag7
            "tokens_2025_annualized": None,  # audit has per-day, not annualized
            "_audit_section": None,
            "_gap": "$745B cumulative capex + $28B cumulative customer revenue + 360T cumulative tokens NOT documented in audit; held as wq-063 editorial overrides pending external sourcing",
        },
    }

    return audit


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    extract_data = extract()
    if "_error" in extract_data:
        print(f"Extraction error: {extract_data['_error']}", file=sys.stderr)
        return 2

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(extract_data, indent=2))

    # Summary
    ma = extract_data["market_aggregates"]
    n_known = 0
    n_gap = 0
    for year, fields in ma.items():
        for k, v in fields.items():
            if k.startswith("_"):
                continue
            if v is None:
                n_gap += 1
            else:
                n_known += 1
    print(f"Extracted: {n_known} known values, {n_gap} gaps across {len(ma)} years")
    print(f"Written: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
