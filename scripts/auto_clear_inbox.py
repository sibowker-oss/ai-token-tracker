#!/usr/bin/env python3
"""
Auto-clear the vault-inbox review queue using the safe rules agreed with
Simon on 2026-04-24. Mirrors the logic of the 'Auto-clear' UI button in
review.html so a CLI invocation and a browser-triggered run produce the
same result.

Rules (applied to status='pending' items only):

  1. ACCEPT   type=hiring_snapshot            (structured, API-deterministic)
  2. DECLINE  confidence=speculative
  3. DECLINE  weight=indicative               (any confidence)
  4. DECLINE  weight missing / '?'            (transformation artifact)
  5. PARK     weight=corroborating, confidence=estimated

Everything else stays pending for human review.

Run:
  python3 scripts/auto_clear_inbox.py                # dry-run, prints plan
  python3 scripts/auto_clear_inbox.py --apply        # writes back
"""

import argparse
import json
import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INBOX_PATH = os.path.join(BASE_DIR, 'vault-inbox.json')

AGENT_VERSION = 'auto-clear@1.0'


def classify(item):
    """Return (action, rule_name) or (None, None) to leave pending."""
    if item.get('status') != 'pending':
        return (None, None)

    weight = item.get('weight')
    confidence = item.get('confidence', '')
    t = item.get('type')

    if t == 'hiring_snapshot':
        return ('accepted', 'rule1_hiring_snapshot_structured')

    if confidence == 'speculative':
        return ('declined', 'rule2_speculative')

    if weight == 'indicative':
        return ('declined', 'rule3_indicative_never_overrides')

    if not weight or weight == '?':
        return ('declined', 'rule4_orphaned_weight')

    if weight == 'corroborating' and confidence == 'estimated':
        return ('parked', 'rule5_triangulation_only')

    return (None, None)


def run(apply_changes):
    with open(INBOX_PATH) as f:
        inbox = json.load(f)

    now = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    counts = {'accepted': 0, 'declined': 0, 'parked': 0, 'kept_pending': 0}
    per_rule = {}

    for item in inbox['items']:
        action, rule = classify(item)
        if action is None:
            if item.get('status') == 'pending':
                counts['kept_pending'] += 1
            continue
        counts[action] += 1
        per_rule[rule] = per_rule.get(rule, 0) + 1

        if apply_changes:
            item['status'] = action
            item['decidedAt'] = now
            item['decidedBy'] = AGENT_VERSION
            item['decisionReason'] = rule

    if apply_changes:
        inbox['lastProcessed'] = now[:10]
        with open(INBOX_PATH, 'w') as f:
            json.dump(inbox, f, indent=2)

    return counts, per_rule


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true',
                    help='Write changes back to vault-inbox.json. Default is dry-run.')
    args = ap.parse_args()

    mode = 'APPLY' if args.apply else 'DRY-RUN'
    print(f"Auto-clear inbox — {mode}")
    print("=" * 50)

    counts, per_rule = run(args.apply)

    print(f"\nActions:")
    for action in ('accepted', 'declined', 'parked'):
        print(f"  {counts[action]:4d}  {action}")
    print(f"  {counts['kept_pending']:4d}  left pending for human review")

    print(f"\nPer rule:")
    for rule, n in sorted(per_rule.items()):
        print(f"  {n:4d}  {rule}")

    if not args.apply:
        print(f"\n(Dry-run. Re-run with --apply to write back.)")
    else:
        print(f"\nWritten back to {INBOX_PATH}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
