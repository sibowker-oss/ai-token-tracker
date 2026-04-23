#!/usr/bin/env python3
"""
Structured claim extractor — produces the four structured claim types defined
by metric-schema.json `claim_types` (wq-014) from typed input sources (ISO
queue rows, ATS API responses, USPTO / PatentsView JSON, LCA rows).

Sibling to `extract_claims.py`, which handles free-text podcast transcripts.
The two are deliberately separate:

  extract_claims.py           — narrative input, LLM-driven, one output type.
  extract_structured_claims.py — typed input, deterministic, four output types.

Writes: data-updates/{YYYY-MM-DD}-structured-candidates.json
Read by: claims.html (type-branched render in Phase 1.3).

Run:
  python3 scripts/extract_structured_claims.py --type power_project \\
      --input tests/fixtures/claims/power_project.input.json
  python3 scripts/extract_structured_claims.py --self-test

Called by: monitor_sources.py adapters (Stream 2 / Stream 3).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(BASE_DIR, 'metric-schema.json')
FIXTURE_DIR = os.path.join(BASE_DIR, 'tests', 'fixtures', 'claims')
OUTPUT_DIR = os.path.join(BASE_DIR, 'data-updates')

CLAIM_TYPES = ('power_project', 'hiring_snapshot', 'patent_snapshot', 'company_surfaced')


# ---------------------------------------------------------------------------
# LLM prompt templates — used by Stream 2 / Stream 3 adapters when the input
# is narrative rather than structured (e.g. a news article mentioning a power
# project, or a funding announcement mentioning a new AI-native). Not wired in
# this commit; wq-012 / wq-013 will invoke them when narrative sources land.
# ---------------------------------------------------------------------------

PROMPT_POWER_PROJECT = """You are reading an interconnection-queue filing or a news article about a
data-centre power project. Extract ONE claim per identifiable project as a JSON object with
the fields defined in metric-schema.json claim_types.power_project. Do not invent values;
leave unknown fields as null. Do not attribute an operator unless the document explicitly
names one; the attribution layer handles LLC-to-operator mapping downstream."""

PROMPT_HIRING_SNAPSHOT = """You are reading an ATS job-board response for ONE company. Summarise the
snapshot per metric-schema.json claim_types.hiring_snapshot. Use the AI-engineer regex from
brief wq-013 §9 to classify roles. Prompt engineers are a SEPARATE category (not counted in
open_roles_ai_titled). Window is the ISO week the fetch covers."""

PROMPT_PATENT_SNAPSHOT = """You are reading a PatentsView / USPTO / Google Patents BigQuery response
for ONE assignee. Summarise the rolling counts per metric-schema.json claim_types.patent_snapshot.
CPC classification follows brief wq-013 §10. ai_cpc_share_trailing_12m is AI-CPC applications /
all applications over trailing 12 months."""

PROMPT_COMPANY_SURFACED = """You are reading a patent application, H-1B LCA row, or trade-press
mention that references a company not in companies.json. Emit one claim per metric-schema.json
claim_types.company_surfaced. density_score_estimate is provided by the caller (ai_native_density
module); do not estimate it here."""

PROMPTS = {
    'power_project': PROMPT_POWER_PROJECT,
    'hiring_snapshot': PROMPT_HIRING_SNAPSHOT,
    'patent_snapshot': PROMPT_PATENT_SNAPSHOT,
    'company_surfaced': PROMPT_COMPANY_SURFACED,
}


# ---------------------------------------------------------------------------
# Deterministic claim builders — preferred over LLM for typed input.
# Each make_* function takes a dict of already-extracted fields and returns
# a claim payload conforming to metric-schema.json claim_types.<type>.
# ---------------------------------------------------------------------------

def _require(inp: dict, *keys: str) -> None:
    missing = [k for k in keys if inp.get(k) is None]
    if missing:
        raise ValueError(f"input missing required fields: {missing}")


def _normalise_source(src: dict, required: tuple[str, ...]) -> dict:
    missing = [k for k in required if src.get(k) is None]
    if missing:
        raise ValueError(f"source block missing required fields: {missing}")
    conf = src.get('confidence')
    if conf not in ('high', 'medium', 'low'):
        raise ValueError(f"source.confidence must be high/medium/low, got {conf!r}")
    return dict(src)


def make_power_project_claim(inp: dict) -> dict:
    _require(inp, 'queue_market', 'queue_id', 'stage', 'source')
    source = _normalise_source(inp['source'], ('url', 'retrievedAt', 'nextReview', 'confidence'))

    claim = {
        'type': 'power_project',
        'queue_market': inp['queue_market'],
        'queue_id': inp['queue_id'],
        'stage': inp['stage'],
        'source': source,
    }
    for field in ('company_slug', 'attribution_confidence', 'attribution_sources',
                  'poi', 'county', 'mw_requested', 'mw_approved', 'mw_in_service',
                  'requested_cod', 'llc_of_record'):
        if field in inp:
            claim[field] = inp[field]
    return claim


def make_hiring_snapshot_claim(inp: dict) -> dict:
    _require(inp, 'company_slug', 'window', 'metrics', 'source')
    source = _normalise_source(inp['source'],
                               ('type', 'token', 'url', 'retrievedAt', 'nextReview', 'confidence'))
    required_metrics = ('open_roles_total', 'open_roles_ai_titled',
                        'open_roles_prompt_engineer', 'ai_titled_share', 'new_ai_roles_7d')
    missing_m = [k for k in required_metrics if inp['metrics'].get(k) is None]
    if missing_m:
        raise ValueError(f"metrics missing required fields: {missing_m}")

    claim = {
        'type': 'hiring_snapshot',
        'company_slug': inp['company_slug'],
        'window': inp['window'],
        'metrics': dict(inp['metrics']),
        'source': source,
    }
    if 'by_function' in inp:
        claim['by_function'] = dict(inp['by_function'])
    return claim


def make_patent_snapshot_claim(inp: dict) -> dict:
    _require(inp, 'company_slug', 'assignee_ids', 'window', 'metrics', 'source')
    source = _normalise_source(inp['source'],
                               ('type', 'url', 'retrievedAt', 'nextReview', 'confidence'))
    required_metrics = ('applications_published_last_30d', 'applications_published_trailing_12m',
                        'grants_last_30d', 'grants_trailing_12m', 'ai_cpc_share_trailing_12m')
    missing_m = [k for k in required_metrics if inp['metrics'].get(k) is None]
    if missing_m:
        raise ValueError(f"metrics missing required fields: {missing_m}")

    claim = {
        'type': 'patent_snapshot',
        'company_slug': inp['company_slug'],
        'assignee_ids': list(inp['assignee_ids']),
        'window': inp['window'],
        'metrics': dict(inp['metrics']),
        'source': source,
    }
    if 'top_cpc_subclasses' in inp:
        claim['top_cpc_subclasses'] = [dict(x) for x in inp['top_cpc_subclasses']]
    return claim


def make_company_surfaced_claim(inp: dict) -> dict:
    _require(inp, 'candidate_name', 'first_seen_signal', 'source')
    source = _normalise_source(inp['source'], ('url', 'retrievedAt', 'confidence'))

    claim = {
        'type': 'company_surfaced',
        'candidate_name': inp['candidate_name'],
        'first_seen_signal': dict(inp['first_seen_signal']),
        'source': source,
    }
    if 'candidate_aliases' in inp:
        claim['candidate_aliases'] = list(inp['candidate_aliases'])
    if 'density_score_estimate' in inp:
        claim['density_score_estimate'] = inp['density_score_estimate']
    return claim


BUILDERS = {
    'power_project': make_power_project_claim,
    'hiring_snapshot': make_hiring_snapshot_claim,
    'patent_snapshot': make_patent_snapshot_claim,
    'company_surfaced': make_company_surfaced_claim,
}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def append_candidates(claims: list[dict]) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = datetime.utcnow().strftime('%Y-%m-%d')
    out_path = os.path.join(OUTPUT_DIR, f'{today}-structured-candidates.json')
    existing = []
    if os.path.exists(out_path):
        with open(out_path) as f:
            existing = json.load(f)
    existing.extend(claims)
    with open(out_path, 'w') as f:
        json.dump(existing, f, indent=2)
    return out_path


def self_test() -> int:
    """Run every fixture input through its builder and compare to the expected output."""
    failed = 0
    for t in CLAIM_TYPES:
        in_path = os.path.join(FIXTURE_DIR, f'{t}.input.json')
        out_path = os.path.join(FIXTURE_DIR, f'{t}.expected.json')
        if not os.path.exists(in_path):
            print(f"SKIP {t}: no input fixture at {in_path}")
            continue
        with open(in_path) as f:
            inp = json.load(f)
        with open(out_path) as f:
            expected = json.load(f)
        got = BUILDERS[t](inp)
        if got == expected:
            print(f"PASS {t}")
        else:
            print(f"FAIL {t}: builder output does not match expected fixture")
            print(f"  expected: {json.dumps(expected, sort_keys=True)}")
            print(f"  got:      {json.dumps(got, sort_keys=True)}")
            failed += 1
    return 1 if failed else 0


def main():
    ap = argparse.ArgumentParser(description='Structured claim extractor (wq-014).')
    ap.add_argument('--type', choices=CLAIM_TYPES, help='Claim type to build.')
    ap.add_argument('--input', help='Path to a JSON file containing the typed input.')
    ap.add_argument('--self-test', action='store_true', help='Run fixture round-trip checks.')
    ap.add_argument('--stdout', action='store_true',
                    help='Print the built claim(s) to stdout instead of appending to candidates.')
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    if not args.type or not args.input:
        ap.error('--type and --input are required unless --self-test is passed.')

    with open(args.input) as f:
        inp = json.load(f)

    items = inp if isinstance(inp, list) else [inp]
    claims = [BUILDERS[args.type](x) for x in items]

    if args.stdout:
        print(json.dumps(claims, indent=2))
        return 0

    path = append_candidates(claims)
    print(f"Appended {len(claims)} claim(s) to {path}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
