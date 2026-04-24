#!/usr/bin/env python3
"""Unit tests for scripts/coerce_date.coerce — the 7 input shapes from the
wq-018 brief plus a handful of variations the vault-inbox actually contains.

Run: python3 tests/test_date_coerce.py
"""
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "scripts"))

from coerce_date import coerce  # noqa: E402

CASES_COERCED = [
    # Quarter end
    ("2026-Q1", "2026-03-31"),
    ("2026-Q2", "2026-06-30"),
    ("2026-Q3", "2026-09-30"),
    ("2026-Q4", "2026-12-31"),
    ("Q1 2026", "2026-03-31"),
    ("Q4 2024", "2024-12-31"),
    # Year end
    ("2026", "2026-12-31"),
    ("2025", "2025-12-31"),
    # Month end (calendar-aware)
    ("2026-04", "2026-04-30"),
    ("2026-02", "2026-02-28"),
    ("2024-02", "2024-02-29"),
    # Month-name + year
    ("April 2026", "2026-04-30"),
    ("February 2024", "2024-02-29"),
    ("October 2025", "2025-10-31"),
    # Year + parenthetical annotation
    ("2026 (annualized)", "2026-12-31"),
    # Fiscal year
    ("FY 2025", "2025-12-31"),
    ("End of FY 2025", "2025-12-31"),
]

CASES_ISO = [
    ("2026-04-25", "2026-04-25"),
    ("2024-12-31", "2024-12-31"),
]

CASES_UNPARSEABLE = [
    "recent",
    "Early 2026",
    "2025-2026",
    "unspecified (from investor relations page snapshot)",
    "",
    "   ",
    None,
]


def main():
    failures = []

    for raw, expected in CASES_COERCED:
        iso, was = coerce(raw)
        if iso != expected or was is not True:
            failures.append(f"  coerce {raw!r}: got ({iso!r}, {was}), expected ({expected!r}, True)")

    for raw, expected in CASES_ISO:
        iso, was = coerce(raw)
        if iso != expected or was is not False:
            failures.append(f"  passthrough {raw!r}: got ({iso!r}, {was}), expected ({expected!r}, False)")

    for raw in CASES_UNPARSEABLE:
        iso, was = coerce(raw)
        if iso is not None or was is not False:
            failures.append(f"  unparseable {raw!r}: got ({iso!r}, {was}), expected (None, False)")

    if failures:
        print(f"FAIL — {len(failures)} cases:")
        for line in failures:
            print(line)
        return 1
    total = len(CASES_COERCED) + len(CASES_ISO) + len(CASES_UNPARSEABLE)
    print(f"OK — {total} cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
