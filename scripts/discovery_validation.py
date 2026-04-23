#!/usr/bin/env python3
"""
Discovery validation harness — wq-013 §12.6.

Re-runs the discovery signal paths against the 31 validation companies from
§6 and checks that each would be surfaced by at least one signal:

  1. patent assignee_ids populated (PatentsView path)
  2. ATS token known (Greenhouse / Lever / Ashby / Workable path)
  3. LCA employer name string known (DoL LCA path)

A company that is invisible to all three paths is a recall gap. The report
tells Simon which signals to fill in before trusting the discovery engine
to surface unknown candidates.

Run:
  python3 scripts/discovery_validation.py
  python3 scripts/discovery_validation.py --json        (machine-readable)
  python3 scripts/discovery_validation.py --report      (writes markdown to reports/)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALIAS_MAP = os.path.join(BASE_DIR, 'data', 'company-alias-map.json')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')


def check_signals(slug: str, entry: dict) -> dict:
    """Return a per-signal visibility flag for this company."""
    return {
        'patents': bool(entry.get('patent_assignee_ids')),
        'ats': bool((entry.get('ats') or {}).get('token')),
        'lca': bool(entry.get('lca_names')),
    }


def run():
    with open(ALIAS_MAP) as f:
        alias = json.load(f)
    companies = alias.get('companies', {})

    by_category = {}
    overall = {'patents': 0, 'ats': 0, 'lca': 0, 'any': 0, 'none': 0, 'all': 0}
    per_company = {}

    for slug, entry in companies.items():
        cat = entry.get('category', 'uncategorised')
        signals = check_signals(slug, entry)
        any_hit = any(signals.values())
        all_hit = all(signals.values())
        per_company[slug] = {
            'canonical': entry.get('canonical', slug),
            'category': cat,
            'signals': signals,
            'any': any_hit,
            'all': all_hit,
        }
        by_category.setdefault(cat, {'total': 0, 'any': 0, 'all': 0, 'none': 0, 'slugs': []})
        by_category[cat]['total'] += 1
        by_category[cat]['slugs'].append(slug)
        if any_hit:
            by_category[cat]['any'] += 1
        if all_hit:
            by_category[cat]['all'] += 1
        if not any_hit:
            by_category[cat]['none'] += 1

        for k, v in signals.items():
            if v:
                overall[k] += 1
        if any_hit:
            overall['any'] += 1
        if all_hit:
            overall['all'] += 1
        if not any_hit:
            overall['none'] += 1

    return {
        'generated_at': datetime.now().isoformat(),
        'n_companies': len(companies),
        'overall': overall,
        'by_category': by_category,
        'per_company': per_company,
    }


def format_text(result: dict) -> str:
    lines = [f"Discovery validation — {result['generated_at'][:10]}",
             f"Validation set: {result['n_companies']} companies (wq-013 §6)",
             ""]
    o = result['overall']
    n = result['n_companies']
    lines.append(f"Signal coverage:")
    lines.append(f"  patent_assignee_ids: {o['patents']:2d}/{n}  ({100*o['patents']//n}%)")
    lines.append(f"  ats.token:           {o['ats']:2d}/{n}  ({100*o['ats']//n}%)")
    lines.append(f"  lca_names:           {o['lca']:2d}/{n}  ({100*o['lca']//n}%)")
    lines.append(f"Surfaced by ≥1 signal: {o['any']:2d}/{n}")
    lines.append(f"Surfaced by all 3:     {o['all']:2d}/{n}")
    lines.append(f"Zero signals (recall gap): {o['none']}")
    lines.append("")

    lines.append("By category:")
    for cat, c in result['by_category'].items():
        lines.append(f"  {cat}: {c['any']}/{c['total']} surfaced (gap: {c['none']})")
    lines.append("")

    recall_gap = [s for s, d in result['per_company'].items() if not d['any']]
    if recall_gap:
        lines.append(f"Recall gap — fix these before trusting discovery:")
        for s in recall_gap:
            lines.append(f"  - {s}  ({result['per_company'][s]['canonical']})")
    else:
        lines.append("No recall gaps — every validation company is visible to at least one signal path.")

    partial = [s for s, d in result['per_company'].items() if d['any'] and not d['all']]
    if partial:
        lines.append("")
        lines.append(f"Partial coverage (surfaceable but incomplete):")
        for s in partial:
            missing = [k for k, v in result['per_company'][s]['signals'].items() if not v]
            lines.append(f"  - {s}: missing {', '.join(missing)}")

    return '\n'.join(lines)


def write_report(result: dict) -> str:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    path = os.path.join(REPORTS_DIR, f"discovery-coverage-{datetime.now().strftime('%Y-%m-%d')}.md")
    body = '# Discovery validation report\n\n```\n' + format_text(result) + '\n```\n'
    with open(path, 'w') as f:
        f.write(body)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', action='store_true', help='Emit machine-readable JSON.')
    ap.add_argument('--report', action='store_true', help='Write markdown to reports/ directory.')
    args = ap.parse_args()

    result = run()

    if args.json:
        print(json.dumps(result, indent=2))
        return 0
    if args.report:
        path = write_report(result)
        print(f"Report written: {path}")
        return 0

    print(format_text(result))
    return 0


if __name__ == '__main__':
    sys.exit(main())
