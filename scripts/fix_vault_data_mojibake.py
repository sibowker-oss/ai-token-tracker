#!/usr/bin/env python3
"""One-shot iterative mojibake cleanup over a vault-data-shaped JSON file.

Scope: any string under `dataPoints[*]` with single-pass mojibake markers
(U+00E2 + U+0080 — UTF-8 punctuation bytes decoded as Latin-1) gets the
latin-1 -> utf-8 round-trip applied. Iterates up to 4 passes per field so
deep (multi-pass) mojibake is also handled. Idempotent — running twice on
clean input is a no-op.

Targets (per briefs/active/2026-04-26-mojibake-roundtrip-fix.md §5):
  - sourceAuthor
  - notes
  - claim
  - and any other string field that happens to contain the trigger pattern

Also walks `dataPoints[*]` for any other string-valued key that contains
the trigger — defensive against fields the vault grows over time.

Run:
  python3 scripts/fix_vault_data_mojibake.py vault-data.json
  python3 scripts/fix_vault_data_mojibake.py data-updates/archive/review-decisions-2026-04-25-wq027-replay.json

The wq-027 replay archive uses a different shape (`accepted` / `declined`
/ `parked` lists at the top level instead of `dataPoints`); this script
handles both shapes by walking any list of dicts it finds.

Audit log appended to: audits/2026-04-26-vault-data-mojibake-fix.md
"""
import json
import os
import sys
from datetime import datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT = os.path.join(REPO, "audits", "2026-04-26-vault-data-mojibake-fix.md")

# Single-pass mojibake markers — see scripts/apply_decisions.py:safe_str
_MOJI_HIGH = "â"  # U+00E2 — UTF-8 lead byte for U+201X punctuation
_MOJI_CTRL = ""  # U+0080 — UTF-8 second byte for U+201X (invisible control)
MAX_PASSES = 4


def has_marker(s):
    return isinstance(s, str) and _MOJI_HIGH in s and _MOJI_CTRL in s


def fix_field(s):
    """Iteratively undo latin-1 -> utf-8 while the trigger is present."""
    if not has_marker(s):
        return s, 0
    passes = 0
    cur = s
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


def walk_and_fix(node, path=""):
    """Recursively descend a JSON-shaped Python value. For every string
    leaf with the trigger marker, replace in-place. Returns
    (field_changes, items_touched_ids, examples)."""
    field_changes = 0
    items_touched = set()
    examples = []

    if isinstance(node, dict):
        item_id = node.get("id") if isinstance(node.get("id"), str) else None
        local_changes = 0
        for k, v in list(node.items()):
            if isinstance(v, str):
                if has_marker(v):
                    new, passes = fix_field(v)
                    if new != v:
                        node[k] = new
                        field_changes += 1
                        local_changes += 1
                        if len(examples) < 5:
                            examples.append({
                                "path": path + ("." if path else "") + k,
                                "id": item_id,
                                "passes": passes,
                                "before": v[:160],
                                "after": new[:160],
                            })
            elif isinstance(v, (dict, list)):
                fc, ids, exs = walk_and_fix(v, path + ("." if path else "") + k)
                field_changes += fc
                items_touched |= ids
                for e in exs:
                    if len(examples) < 5:
                        examples.append(e)
        if local_changes and item_id:
            items_touched.add(item_id)

    elif isinstance(node, list):
        for i, v in enumerate(node):
            if isinstance(v, (dict, list)):
                fc, ids, exs = walk_and_fix(v, path + f"[{i}]")
                field_changes += fc
                items_touched |= ids
                for e in exs:
                    if len(examples) < 5:
                        examples.append(e)

    return field_changes, items_touched, examples


def main(argv):
    if len(argv) < 2:
        print("usage: fix_vault_data_mojibake.py <path>", file=sys.stderr)
        return 2

    target = argv[1]
    if not os.path.isabs(target):
        target = os.path.abspath(target)
    if not os.path.exists(target):
        print(f"file not found: {target}", file=sys.stderr)
        return 2

    with open(target, encoding="utf-8") as f:
        data = json.load(f)

    field_changes, items_touched, examples = walk_and_fix(data)

    # Match the existing apply_decisions.py write contract:
    # ensure_ascii=True (Python json.dump default) and indent=2.
    with open(target, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    rel = os.path.relpath(target, REPO)
    summary = (
        f"# fix_vault_data_mojibake.py — {rel}\n\n"
        f"date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"target: {rel}\n"
        f"field changes: {field_changes}\n"
        f"items touched: {len(items_touched)}\n"
        f"\nFirst {len(examples)} examples:\n"
    )
    for e in examples:
        summary += (
            f"\n- {e['path']}"
            f" (id={e.get('id')}, passes={e['passes']})\n"
            f"    before: {e['before']!r}\n"
            f"    after:  {e['after']!r}\n"
        )

    print(summary)

    os.makedirs(os.path.dirname(AUDIT), exist_ok=True)
    with open(AUDIT, "a", encoding="utf-8") as f:
        f.write(summary + "\n---\n")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
