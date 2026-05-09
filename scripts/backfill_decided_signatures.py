#!/usr/bin/env python3
"""backfill_decided_signatures.py — one-time seed of decided-signatures.json.

Walks every file in data-updates/decisions/ and records each item's signature
into data-updates/decided-signatures.json so claims.html stops resurfacing
items decided before the suppress-list mechanism existed.

Idempotent: re-running adds nothing if every signature is already indexed.
Safe to run any time the historical record needs to be re-derived.
"""

from __future__ import annotations

import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from _decided_signatures import record_decisions  # noqa: E402

ROOT_DIR = os.path.dirname(SCRIPT_DIR)
DECISIONS_DIR = os.path.join(ROOT_DIR, "data-updates", "decisions")


def main() -> int:
    if not os.path.isdir(DECISIONS_DIR):
        print(f"No decisions dir at {DECISIONS_DIR} — nothing to backfill.")
        return 0

    files = sorted(
        f for f in os.listdir(DECISIONS_DIR)
        if f.endswith(".json")
    )
    if not files:
        print(f"No decision files in {DECISIONS_DIR} — nothing to backfill.")
        return 0

    total_added = 0
    for fname in files:
        path = os.path.join(DECISIONS_DIR, fname)
        try:
            with open(path) as f:
                payload = json.load(f)
        except Exception as e:
            print(f"  SKIP {fname}: {e}")
            continue

        # Tolerate both wrapped {ui, decisions: {...}} and flat shapes.
        if isinstance(payload, dict) and "decisions" in payload:
            decisions = payload.get("decisions") or {}
            decided_at = payload.get("submitted_at")
        else:
            decisions = payload or {}
            decided_at = decisions.get("submitted_at")

        added = record_decisions(decisions, decided_at=decided_at)
        total_added += added
        if added:
            print(f"  {fname}: +{added} signatures")
        else:
            print(f"  {fname}: (already indexed)")

    print(f"\nBackfill complete — {total_added} new signatures across {len(files)} decision file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
