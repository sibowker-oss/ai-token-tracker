#!/usr/bin/env python3
"""wq-030: One-shot mojibake cleanup of vault-inbox.json items.

Scope per the wq-030 spec:
  - Only items with status in {pending, raw_pool, parked} are cleaned.
  - Items with status in {accepted, declined} are skipped — those have
    already flowed downstream and their byte-level audit trail must
    stay stable.

Reuses the iterative latin-1 → utf-8 round-trip from
fix_vault_data_mojibake.py (single-pass and multi-pass mojibake both
handled, idempotent on clean input).

Run:
  python3 scripts/fix_vault_inbox_mojibake.py [--dry-run]

Exits non-zero if vault-inbox.json doesn't exist.
"""
import json
import os
import sys
from datetime import datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INBOX = os.path.join(REPO, "vault-inbox.json")
AUDIT = os.path.join(REPO, "audits", "2026-04-29-vault-inbox-mojibake-cleanup.md")

# Single-pass mojibake markers — mirror fix_vault_data_mojibake.py
_MOJI_HIGH = "â"  # U+00E2 (UTF-8 lead byte for U+201X punctuation)
_MOJI_CTRL = ""  # U+0080 (UTF-8 second byte — invisible C1 control)

CLEANABLE = {"pending", "raw_pool", "parked"}
FROZEN = {"accepted", "declined"}
MAX_PASSES = 4


def has_marker(s):
    return isinstance(s, str) and _MOJI_HIGH in s and _MOJI_CTRL in s


def fix_field(s):
    """Iteratively undo latin-1 → utf-8 while the trigger is present."""
    if not has_marker(s):
        return s, 0
    cur = s
    passes = 0
    for _ in range(MAX_PASSES):
        if not has_marker(cur):
            break
        try:
            nxt = cur.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            break
        if nxt == cur:
            break
        cur = nxt
        passes += 1
    return cur, passes


def walk_strings(node, replace_fn):
    """Apply replace_fn(value) -> new_value to every string leaf."""
    if isinstance(node, dict):
        for k, v in list(node.items()):
            if isinstance(v, str):
                node[k] = replace_fn(v)
            elif isinstance(v, (dict, list)):
                walk_strings(v, replace_fn)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            if isinstance(v, str):
                node[i] = replace_fn(v)
            elif isinstance(v, (dict, list)):
                walk_strings(v, replace_fn)


def main(argv):
    dry_run = "--dry-run" in argv

    if not os.path.exists(INBOX):
        print(f"vault-inbox.json not found at {INBOX}", file=sys.stderr)
        return 2

    with open(INBOX, encoding="utf-8") as f:
        inbox = json.load(f)

    items = inbox.get("items", [])
    cleaned_items = 0
    cleaned_fields = 0
    frozen_skipped = 0
    other_skipped = 0
    examples = []

    def replace_one(s):
        nonlocal cleaned_fields
        if not has_marker(s):
            return s
        new, passes = fix_field(s)
        if new != s:
            cleaned_fields += 1
            return new
        return s

    for item in items:
        status = (item.get("status") or "").strip()
        if status in FROZEN:
            frozen_skipped += 1
            continue
        if status not in CLEANABLE:
            # status is unknown / missing — be safe, don't touch
            other_skipped += 1
            continue
        before = json.dumps(item, ensure_ascii=False)
        walk_strings(item, replace_one)
        after = json.dumps(item, ensure_ascii=False)
        if before != after:
            cleaned_items += 1
            if len(examples) < 5:
                examples.append({
                    "id": item.get("id"),
                    "status": status,
                    "before": before[:200],
                    "after": after[:200],
                })

    summary = (
        f"# wq-030 vault-inbox mojibake cleanup — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"\n"
        f"Mode: {'DRY-RUN' if dry_run else 'WRITE'}\n"
        f"Items in inbox:        {len(items)}\n"
        f"Items cleaned:         {cleaned_items}\n"
        f"Fields rewritten:      {cleaned_fields}\n"
        f"Items skipped (frozen accepted/declined): {frozen_skipped}\n"
        f"Items skipped (other status):             {other_skipped}\n"
    )
    if examples:
        summary += f"\nFirst {len(examples)} examples:\n"
        for e in examples:
            summary += (
                f"\n- id={e['id']} status={e['status']}\n"
                f"    before: {e['before']!r}\n"
                f"    after:  {e['after']!r}\n"
            )

    print(summary)

    if not dry_run and cleaned_fields > 0:
        # Match the existing apply_decisions.py write contract:
        # ensure_ascii=True (Python json.dump default) + indent=2.
        with open(INBOX, "w", encoding="utf-8") as f:
            json.dump(inbox, f, indent=2)
        print(f"  Wrote: {INBOX}")
        os.makedirs(os.path.dirname(AUDIT), exist_ok=True)
        with open(AUDIT, "a", encoding="utf-8") as f:
            f.write(summary + "\n---\n")
        print(f"  Audit appended: {AUDIT}")
    elif dry_run:
        print("  [DRY-RUN] No file written.")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
