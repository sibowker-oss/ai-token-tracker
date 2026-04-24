#!/usr/bin/env python3
"""One-shot: unmojibake pending vault-inbox items.

Latin-1-decoded UTF-8 round-trip on `sourceAuthor`, `notes`, `claim` for any
item whose status is not 'accepted' or 'declined'. Accepted/declined items are
frozen and not touched. See briefs/active/2026-04-25-vault-inbox-cleanup.md §2.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VAULT = REPO / "vault-inbox.json"

FIELDS = ("sourceAuthor", "notes", "claim")
FROZEN = {"accepted", "declined"}


def fix_mojibake(s):
    if not isinstance(s, str):
        return s
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def main():
    data = json.loads(VAULT.read_text(encoding="utf-8"))
    items = data.get("items", [])

    field_changes = 0
    item_changes = 0
    for item in items:
        if item.get("status") in FROZEN:
            continue
        touched = False
        for field in FIELDS:
            v = item.get(field)
            new = fix_mojibake(v)
            if new != v:
                item[field] = new
                field_changes += 1
                touched = True
        if touched:
            item_changes += 1

    # Preserve existing JSON encoding convention (ensure_ascii=True).
    VAULT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"items touched: {item_changes}")
    print(f"field changes: {field_changes}")


if __name__ == "__main__":
    sys.exit(main())
