#!/usr/bin/env python3
"""
Dedupe the candidates queue. Future runs of monitor_sources.py replace per
source automatically, but this script cleans up queues that predate that
behavior (e.g. the one-time State of AI double-extraction on 2026-04-23).

Fingerprint keeps the most recent extraction (by extracted_at) when two
claims collide.

Run: python3 scripts/dedupe_candidates.py [--date YYYY-MM-DD]
"""

import argparse
import json
import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, 'data-updates')


def fingerprint(c):
    t = c.get('type')
    src = c.get('source_url') or (c.get('source') or {}).get('url', '')
    if t == 'power_project':
        return (t, c.get('queue_market'), c.get('queue_id'))
    if t in ('hiring_snapshot', 'patent_snapshot'):
        return (t, c.get('company_slug'), c.get('window'))
    if t == 'company_surfaced':
        return (t, c.get('candidate_name'))
    return (src, (c.get('claim') or '')[:200])


def dedupe(claims):
    by_fp = {}
    for c in claims:
        fp = fingerprint(c)
        existing = by_fp.get(fp)
        if existing is None:
            by_fp[fp] = c
            continue
        # Keep whichever has the later extracted_at
        new_ts = c.get('extracted_at', '')
        old_ts = existing.get('extracted_at', '')
        if new_ts > old_ts:
            by_fp[fp] = c
    return list(by_fp.values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--date', default=datetime.now().strftime('%Y-%m-%d'))
    args = ap.parse_args()
    path = os.path.join(OUTPUT_DIR, f'{args.date}-candidates.json')
    if not os.path.exists(path):
        print(f"No queue at {path}")
        return 1
    claims = json.load(open(path))
    before = len(claims)
    deduped = dedupe(claims)
    after = len(deduped)
    json.dump(deduped, open(path, 'w'), indent=2)
    print(f"{path}: {before} → {after} claims ({before - after} duplicates removed)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
