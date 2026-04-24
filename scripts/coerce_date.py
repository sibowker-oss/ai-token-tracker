"""Coerce loose date strings to ISO YYYY-MM-DD.

Used by extractors that ingest LLM-emitted dates (`2026-Q1`, `April 2026`, `2025`)
and by the one-shot vault-inbox cleanup. Rules:

  YYYY-MM-DD          → unchanged
  YYYY-Q[1-4]         → quarter end (03-31 / 06-30 / 09-30 / 12-31)
  Q[1-4] YYYY         → quarter end
  Month YYYY          → month end (calendar-aware)
  YYYY-MM             → month end
  YYYY                → year end (12-31)
  YYYY (annotation)   → strip annotation, recurse
  FY YYYY / End of FY → year end

Anything else: returns (None, False). Callers decide whether to leave the
original string in place or fall back to a default.
"""
from __future__ import annotations

import calendar
import re

ISO_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
QUARTER_END_DAY = {1: (3, 31), 2: (6, 30), 3: (9, 30), 4: (12, 31)}

_MONTH_NAMES = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _month_end(year: int, month: int) -> str:
    last = calendar.monthrange(year, month)[1]
    return f"{year:04d}-{month:02d}-{last:02d}"


def _year_end(year: int) -> str:
    return f"{year:04d}-12-31"


def coerce(raw):
    """Return (iso_string_or_None, was_coerced).

    - If `raw` is already ISO, returns (raw, False).
    - If we coerced something looser, returns (iso, True).
    - If unparseable, returns (None, False).
    """
    if not isinstance(raw, str):
        return None, False
    s = raw.strip()
    if not s:
        return None, False

    if ISO_RE.match(s):
        return s, False

    # Strip a trailing parenthetical annotation: "2026 (annualized)" -> "2026"
    paren = re.match(r"^(.+?)\s*\([^)]*\)\s*$", s)
    if paren:
        inner_iso, _ = coerce(paren.group(1))
        if inner_iso:
            return inner_iso, True

    # FY YYYY / End of FY YYYY / Fiscal YYYY
    fy = re.match(r"^(?:end\s+of\s+)?(?:fy|fiscal)\s*(\d{4})$", s, re.IGNORECASE)
    if fy:
        return _year_end(int(fy.group(1))), True

    # YYYY-Q[1-4]
    m = re.match(r"^(\d{4})[-\s]?Q([1-4])$", s, re.IGNORECASE)
    if m:
        year = int(m.group(1))
        month, day = QUARTER_END_DAY[int(m.group(2))]
        return f"{year:04d}-{month:02d}-{day:02d}", True

    # Q[1-4] YYYY
    m = re.match(r"^Q([1-4])[\s-]?(\d{4})$", s, re.IGNORECASE)
    if m:
        year = int(m.group(2))
        month, day = QUARTER_END_DAY[int(m.group(1))]
        return f"{year:04d}-{month:02d}-{day:02d}", True

    # YYYY-MM
    m = re.match(r"^(\d{4})-(\d{1,2})$", s)
    if m:
        year, month = int(m.group(1)), int(m.group(2))
        if 1 <= month <= 12:
            return _month_end(year, month), True

    # Month YYYY  (month name)
    m = re.match(r"^([A-Za-z]+)\s+(\d{4})$", s)
    if m:
        name = m.group(1).lower()
        if name in _MONTH_NAMES:
            return _month_end(int(m.group(2)), _MONTH_NAMES[name]), True

    # YYYY (year alone)
    m = re.match(r"^(\d{4})$", s)
    if m:
        return _year_end(int(m.group(1))), True

    return None, False


def coerce_or_keep(raw, fallback=None):
    """Convenience for extractors: return ISO if coercible, else fallback (or original)."""
    iso, _ = coerce(raw)
    if iso:
        return iso
    return fallback if fallback is not None else raw
