#!/usr/bin/env python3
"""
Validate the four structured claim types defined in metric-schema.json against
fixture payloads in tests/fixtures/claims/. Plain Python, no pytest.

Run: python3 tests/test_claim_schema.py

Authored under wq-014 (briefs/active/2026-04-23-structured-claim-schema.md).
"""

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(BASE_DIR, 'metric-schema.json')
FIXTURE_DIR = os.path.join(BASE_DIR, 'tests', 'fixtures', 'claims')

CLAIM_TYPES = ['power_project', 'hiring_snapshot', 'patent_snapshot', 'company_surfaced']


def validate_claim(claim, type_def, type_name):
    errors = []

    required = set(type_def.get('required', []))
    optional = set(type_def.get('optional', []))
    known = required | optional
    present = set(claim.keys())

    missing = required - present
    if missing:
        errors.append(f"missing required fields: {sorted(missing)}")

    unknown = present - known
    if unknown:
        errors.append(f"unknown fields (not in required or optional): {sorted(unknown)}")

    if claim.get('type') != type_name:
        errors.append(f"type field is {claim.get('type')!r}, expected {type_name!r}")

    source = claim.get('source')
    if not isinstance(source, dict):
        errors.append("`source` must be an object")
    else:
        source_spec = type_def.get('source_block', {})
        for field, spec in source_spec.items():
            if spec.get('required') and field not in source:
                errors.append(f"source.{field} is required but missing")
        conf = source.get('confidence')
        if conf is not None and conf not in ('high', 'medium', 'low'):
            errors.append(f"source.confidence must be high/medium/low, got {conf!r}")

    return errors


def main():
    with open(SCHEMA_PATH) as f:
        schema = json.load(f)

    claim_types = schema.get('claim_types', {})
    if not claim_types:
        print("FAIL: metric-schema.json has no claim_types block")
        return 1

    for t in CLAIM_TYPES:
        if t not in claim_types:
            print(f"FAIL: claim_types.{t} is not defined in metric-schema.json")
            return 1

    failed = 0
    for t in CLAIM_TYPES:
        fixture_path = os.path.join(FIXTURE_DIR, f"{t}.expected.json")
        if not os.path.exists(fixture_path):
            print(f"FAIL: fixture missing at {fixture_path}")
            failed += 1
            continue

        with open(fixture_path) as f:
            claim = json.load(f)

        errors = validate_claim(claim, claim_types[t], t)
        if errors:
            print(f"FAIL {t}:")
            for e in errors:
                print(f"  - {e}")
            failed += 1
        else:
            print(f"PASS {t}")

    if failed:
        print(f"\n{failed} of {len(CLAIM_TYPES)} claim types failed validation.")
        return 1

    print(f"\nAll {len(CLAIM_TYPES)} claim types valid.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
