#!/usr/bin/env python3
"""One-shot: coerce loose dateOfClaim values to ISO YYYY-MM-DD on
non-frozen vault-inbox items. Preserves the original string in
`dateOfClaim_original` for any row we touched. See
briefs/active/2026-04-25-vault-inbox-cleanup.md §3.
"""
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VAULT = REPO / "vault-inbox.json"

sys.path.insert(0, str(REPO / "scripts"))
from coerce_date import coerce  # noqa: E402

FROZEN = {"accepted", "declined"}


def main():
    data = json.loads(VAULT.read_text(encoding="utf-8"))
    items = data.get("items", [])

    coerced = 0
    unparseable = Counter()
    for item in items:
        if item.get("status") in FROZEN:
            continue
        raw = item.get("dateOfClaim")
        iso, was = coerce(raw)
        if was:
            item["dateOfClaim_original"] = raw
            item["dateOfClaim"] = iso
            coerced += 1
        elif iso is None and isinstance(raw, str) and raw.strip():
            unparseable[raw] += 1

    VAULT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    print(f"coerced: {coerced}")
    print(f"unparseable: {sum(unparseable.values())} ({len(unparseable)} distinct)")
    if unparseable:
        print("top unparseable shapes (review manually in admin.html):")
        for shape, n in unparseable.most_common(20):
            print(f"  {n:3d}  {shape!r}")


if __name__ == "__main__":
    sys.exit(main())
