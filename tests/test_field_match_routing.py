#!/usr/bin/env python3
"""Unit tests for the field_match_rules + metricKey-extended search_text
contract in scripts/apply_decisions.py (wq-028 P1).

Phase 0 audit found 140 inbox items where the metricKey already named the
canonical field but the matcher (claim_text+tags only) missed. Plus a long
tail of unmapped variants ("gross margin", "contract value", "operating
income") that needed new field_match_rules. This test pins both:

  - including metricKey in search_text rescues structured-tag claims
  - 8 new field_match_rules route their canonical metricKey strings to the
    expected entity field
  - the tightened active_rate rule no longer false-positives on
    enterprise_adoption tags + the word 'rate' floating in metricKey

Run: python3 tests/test_field_match_routing.py
"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(BASE, "metric-schema.json")
sys.path.insert(0, os.path.join(BASE, "scripts"))
from apply_decisions import match_field  # noqa: E402

with open(SCHEMA_PATH, "r") as f:
    SCHEMA = json.load(f)
RULES = SCHEMA.get("field_match_rules", [])


def route(claim, tags=None, metric_key=None):
    """Mirror the apply_decisions.py two-pass match: try claim+tags first,
    fall back to metricKey alone if no field match."""
    primary = ((claim or "") + " " + " ".join(tags or [])).lower()
    field = match_field(primary, RULES)
    if field is None and metric_key:
        field = match_field(metric_key.lower(), RULES)
    return field


def _check(name, expected, actual):
    if expected == actual:
        print(f"PASS {name}")
        return 1
    print(f"FAIL {name}: expected={expected!r} actual={actual!r}")
    return 0


def test_metrickey_extension():
    """A claim whose text doesn't reference the field but whose metricKey
    does should now route correctly (was the 140-item gap pre-wq-028)."""
    cases = [
        # (description, claim_text, tags, metric_key, expected_field)
        (
            "metricKey rescues 'annual revenue' to collected_revenue",
            "Anthropic saw revenue growth from zero to $9.5B",
            ["provider_revenue"],
            "annual revenue",
            "collected_revenue",
        ),
        (
            "metricKey rescues 'headcount' to employees",
            "Cursor scaled the team rapidly through 2025",
            ["growth_stage"],
            "headcount",
            "employees",
        ),
        (
            "metricKey rescues 'ARR' (case-insensitive) to arr",
            "Cursor crossed major milestone in early 2026",
            ["growth_stage"],
            "ARR",
            "arr",
        ),
    ]
    passes = 0
    for desc, claim, tags, mk, expected in cases:
        actual = route(claim, tags, mk)
        passes += _check(desc, expected, actual)
    return passes, len(cases)


def test_new_field_rules():
    """The 8 new field_match_rules added in wq-028 P1.2 should each route
    their primary metricKey variants to the named canonical field."""
    cases = [
        ("gross margin → gross_margin_pct", "gross margin on GPU hardware", "gross_margin_pct"),
        ("gross profit → gross_profit", "gross profit", "gross_profit"),
        ("operating income → operating_income", "operating income", "operating_income"),
        ("contract value → contract_value", "contract value", "contract_value"),
        ("deal value → contract_value", "M&A deal value", "contract_value"),
        ("rack power density → rack_power_density_kw", "rack power density", "rack_power_density_kw"),
        ("data center power capacity → dc_power_capacity_gw", "data center power capacity", "dc_power_capacity_gw"),
        ("purchase commitments → purchase_commitments", "purchase commitments", "purchase_commitments"),
        ("enterprise revenue → enterprise_revenue", "enterprise_revenue", "enterprise_revenue"),
    ]
    passes = 0
    for desc, mk, expected in cases:
        actual = route("placeholder claim text", [], mk)
        passes += _check(desc, expected, actual)
    return passes, len(cases)


def test_active_rate_tightened():
    """The active_rate pattern was loosened to require word-adjacency
    after the metricKey extension exposed false positives like
    enterprise_adoption (tag) + growth_rate (metricKey) being matched
    against `adoption.*rate` across the gap."""
    cases = [
        # Should NOT match active_rate (these were false positives pre-tightening)
        ("revenue growth rate must NOT be active_rate", "revenue growth rate", ["enterprise_adoption"], None),
        ("store count growth rate must NOT be active_rate", "store count growth rate", ["enterprise_adoption"], None),
        ("task automation rate must NOT be active_rate", "task automation rate", ["enterprise_adoption"], None),
        # Should still match active_rate (legit usage)
        ("'usage rate' still routes to active_rate", "usage rate", [], "active_rate"),
        ("'adoption rate' still routes to active_rate", "adoption rate", [], "active_rate"),
        ("'active rate' still routes to active_rate", "active rate", [], "active_rate"),
    ]
    passes = 0
    for desc, mk, tags, expected in cases:
        actual = route("placeholder claim", tags, mk)
        passes += _check(desc, expected, actual)
    return passes, len(cases)


def test_existing_rules_still_pass():
    """Pin a few existing rules to make sure adding metricKey to search_text
    didn't break old behavior. Claim text alone should still route."""
    cases = [
        ("claim text 'Anthropic ARR is $19B' → arr", "Anthropic ARR crossed $19B run rate", [], None, "arr"),
        ("claim text 'OpenAI valuation' → valuation", "OpenAI is valued at $500B", [], None, "valuation"),
        ("claim text 'capex' → capex", "Microsoft capex hit $80B", [], None, "capex"),
    ]
    passes = 0
    for desc, claim, tags, mk, expected in cases:
        actual = route(claim, tags, mk)
        passes += _check(desc, expected, actual)
    return passes, len(cases)


def main():
    suites = [
        ("metricKey extension", test_metrickey_extension),
        ("new field rules", test_new_field_rules),
        ("active_rate tightened", test_active_rate_tightened),
        ("existing rules pinned", test_existing_rules_still_pass),
    ]
    total_passes = 0
    total_cases = 0
    for label, fn in suites:
        print(f"\n--- {label} ---")
        p, c = fn()
        total_passes += p
        total_cases += c

    print(f"\n{'OK' if total_passes == total_cases else 'FAIL'} — {total_passes}/{total_cases} cases passed")
    sys.exit(0 if total_passes == total_cases else 1)


if __name__ == "__main__":
    main()
