#!/usr/bin/env python3
"""One-shot: migrate orphan-Accepts to raw_pool (wq-023 §5).

Items with status=accepted AND no mapped metric (metricKey missing,
empty, or 'unknown') are not surfacing anywhere on the site — they
were filed, not used. Move them to status=raw_pool so the Accept
contract holds: an Accept means the claim moves a number on the site.

Predicate matches the audit list at audits/2026-04-25-orphan-accepts.md
1:1 (verified at write time: 90 ids).

Usage: python3 scripts/migrate_orphan_accepts.py
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VAULT = REPO / "vault-inbox.json"

MIGRATION_NOTE = (
    "wq-023 Phase 3 — moved from accepted to raw_pool because metric "
    "was unmapped at accept time"
)


def is_orphan_accept(item):
    if item.get("status") != "accepted":
        return False
    mk = item.get("metricKey")
    return not mk or mk == "unknown"


def main():
    data = json.loads(VAULT.read_text(encoding="utf-8"))
    items = data.get("items", [])

    migrated = 0
    for item in items:
        if not is_orphan_accept(item):
            continue
        item["status"] = "raw_pool"
        item["migration_note"] = MIGRATION_NOTE
        migrated += 1

    VAULT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"migrated: {migrated}")


if __name__ == "__main__":
    sys.exit(main())
