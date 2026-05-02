#!/usr/bin/env python3
"""wq-054 — one-off audit script for the period-attribution bug pattern.

Walks every entity's provenance block, parses claim text for period
qualifiers (H1, H2, Q1-Q4, per month, monthly, quarterly, best 4-week,
exit, year-end), and flags fields where the claim period doesn't match
the field period.

The pattern: an annual field (e.g. `2025.arr`) receives a sub-period
claim (e.g. "Anthropic had a $6 billion month in February 2026") which
gets stored as if it were the annual figure. Downstream the engine treats
the sub-period figure as a year-end snapshot and inflates everything.

This script is a throwaway audit — it doesn't modify entities.json. It
produces data/wq-054-period-audit.txt for Simon to scope the fix from.

Run:
  python3 scripts/audit_period_attribution.py
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTITIES_PATH = ROOT / "entities.json"
REPORT_PATH = ROOT / "data" / "wq-054-period-audit.txt"


# Period-qualifier regex bank. Each pattern → (label, suggested_field_suffix).
# The suffix maps to where the sub-period value SHOULD live if a target field
# existed. "no schema target — needs new field type" surfaces in the report
# when there's no obvious alternative location.
PERIOD_PATTERNS = [
    (re.compile(r"\bH1\b\s*\d{4}|\bfirst half\b|\b1H\b", re.I),         "h1",                "h1"),
    (re.compile(r"\bH2\b\s*\d{4}|\bsecond half\b|\b2H\b", re.I),        "h2",                "h2"),
    (re.compile(r"\bQ1\b|\bfirst quarter\b", re.I),                       "q1",                "q1"),
    (re.compile(r"\bQ2\b|\bsecond quarter\b", re.I),                      "q2",                "q2"),
    (re.compile(r"\bQ3\b|\bthird quarter\b", re.I),                       "q3",                "q3"),
    (re.compile(r"\bQ4\b|\bfourth quarter\b", re.I),                      "q4",                "q4"),
    (re.compile(r"\bper month\b|\b/month\b|\bmonthly\b|\$\d+(\.\d+)?B?\s*month\b", re.I),
                                                                          "monthly",           "monthly"),
    (re.compile(r"\bbest 4[- ]week\b|\b4[- ]week period\b", re.I),       "best_4_week",       "best_4_week"),
    (re.compile(r"\bexit\s+ARR\b|\byear[- ]end\b|\bend of year\b", re.I), "exit/year_end",     "exit"),
    (re.compile(r"\b(?:February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b", re.I),
                                                                          "specific_month",    "monthly"),
    (re.compile(r"\bper quarter\b|\b/quarter\b|\bquarterly\b", re.I),    "per_quarter",       "quarterly"),
]

# Annual field names that wq-054 cares about (those that are nominally
# year-totals and where storing a sub-period figure causes downstream rot).
ANNUAL_FIELDS = {
    "arr", "collected_revenue", "operating_loss", "cash_burn",
    "valuation", "total_funding", "subscription_revenue",
    "api_revenue", "enterprise_revenue", "ai_arr", "data_center_revenue",
    "managed_api_revenue", "exit_arr", "monthly_revenue_peak",
}


def detect_period_qualifiers(text: str) -> list[tuple[str, str]]:
    """Return [(label, suggested_suffix), ...] for any period qualifiers found in text."""
    if not text:
        return []
    hits = []
    seen_labels = set()
    for pattern, label, suffix in PERIOD_PATTERNS:
        if pattern.search(text):
            if label in seen_labels:
                continue
            seen_labels.add(label)
            hits.append((label, suffix))
    return hits


def field_is_inherently_annual(field: str) -> bool:
    return field in ANNUAL_FIELDS


def suggest_action(field: str, year: str, suffix: str) -> str:
    """Translate period suffix → suggested rewrite location for entities.json."""
    if suffix == "exit":
        return f"move to {year}.exit_{field} (or set field=exit_arr if applicable)"
    if suffix in ("h1", "h2"):
        return f"move to {year}_{suffix}.{field} (new sub-year block)"
    if suffix in ("q1", "q2", "q3", "q4"):
        return f"move to {year}_{suffix}.{field} (new sub-year block)"
    if suffix == "monthly":
        if field == "monthly_revenue_peak":
            return "field IS the right shape — already a monthly bucket"
        return f"move to {year}_<month>.{field} (no current schema; needs new field type) OR convert to annual via × 12"
    if suffix == "quarterly":
        return f"convert to annual via × 4 OR move to {year}_<quarter>.{field}"
    if suffix == "best_4_week":
        return "annotate field with `arr_method: best_period_x12` (already handled by wq-048 consensus engine for OpenAI specifically)"
    if suffix == "specific_month":
        return f"move to {year}_<month>.{field} (no current schema) — same as monthly"
    return "no schema target — needs new field type or annotation"


def audit_entity(entity: dict) -> list[dict]:
    """Walk every provenance.<year>.<field> claim. Flag mismatches."""
    flags = []
    slug = entity.get("slug", "")
    prov = entity.get("provenance") or {}
    for prov_key, prov_block in prov.items():
        if not isinstance(prov_block, dict):
            continue
        # prov_key shape: "<year>.<field>" or "current.<field>" or sometimes just "<field>"
        if "." not in prov_key:
            continue
        year_part, field_part = prov_key.split(".", 1)
        if year_part == "current":
            continue  # current is point-in-time; period qualifiers expected
        if not field_is_inherently_annual(field_part):
            continue
        for claim in (prov_block.get("claims") or []):
            if not isinstance(claim, dict):
                continue
            if claim.get("role") == "superseded":
                continue
            text = (claim.get("claim") or "") + " " + (claim.get("source") or "")
            qualifiers = detect_period_qualifiers(text)
            if not qualifiers:
                continue
            for label, suffix in qualifiers:
                # Skip "exit" qualifier on `exit_arr` field — that's the
                # field's whole purpose; not a mismatch.
                if suffix == "exit" and field_part == "exit_arr":
                    continue
                if suffix == "monthly" and field_part == "monthly_revenue_peak":
                    continue
                flags.append({
                    "slug": slug,
                    "year": year_part,
                    "field": field_part,
                    "claim_id": claim.get("id"),
                    "claim_value": claim.get("value"),
                    "claim_text": (claim.get("claim") or "")[:160],
                    "period_qualifier": label,
                    "suggested_action": suggest_action(field_part, year_part, suffix),
                    "claim_origin": claim.get("origin"),
                })
    return flags


def main() -> None:
    with open(ENTITIES_PATH) as f:
        entities = json.load(f)

    all_flags = []
    for ent in entities.get("companies", []):
        all_flags.extend(audit_entity(ent))

    # Aggregate
    total = len(all_flags)
    by_period = Counter(f["period_qualifier"] for f in all_flags)
    by_entity = Counter(f["slug"] for f in all_flags)
    by_field = Counter(f["field"] for f in all_flags)

    lines = [
        "# wq-054 period-attribution audit",
        f"_Generated {datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')}_",
        "",
        "## Methodology",
        "",
        "Walks every entities.json provenance.<year>.<field> claim where field is",
        "in the ANNUAL_FIELDS set (arr, collected_revenue, operating_loss, etc.).",
        "Searches the claim text + source string for period qualifiers (H1/H2/",
        "Q1-Q4/monthly/specific-month/best-4-week/exit/year-end). Flags any",
        "mismatch where a sub-period claim is sitting in a year-total field.",
        "",
        "Suppresses two intentional matches: 'exit' qualifier on the `exit_arr`",
        "field (purpose-built); 'monthly' qualifier on `monthly_revenue_peak`",
        "(also purpose-built). Audit-only — no entities.json mutations.",
        "",
        f"## Headline: {total} flagged claims across {len(by_entity)} entities",
        "",
        "## Breakdown by period qualifier",
        "",
    ]
    for label, n in sorted(by_period.items(), key=lambda x: -x[1]):
        pct = 100 * n / max(1, total)
        lines.append(f"  {label:20}  {n:>4}  ({pct:>5.1f}%)")

    lines += [
        "",
        "## Top 10 affected entities",
        "",
    ]
    for slug, n in by_entity.most_common(10):
        lines.append(f"  {slug:30}  {n:>3}")

    lines += [
        "",
        "## Breakdown by field",
        "",
    ]
    for field, n in by_field.most_common():
        lines.append(f"  {field:30}  {n:>3}")

    lines += [
        "",
        "## Per-entity flagged claims (full table)",
        "",
    ]
    by_entity_groups = defaultdict(list)
    for f in all_flags:
        by_entity_groups[f["slug"]].append(f)
    for slug in sorted(by_entity_groups):
        items = by_entity_groups[slug]
        lines.append(f"### {slug}  ({len(items)} flag(s))")
        lines.append("")
        for f in items:
            lines.append(f"  - {f['year']}.{f['field']}  qualifier='{f['period_qualifier']}'  origin={f['claim_origin']}")
            lines.append(f"    claim_id: {f['claim_id']}")
            lines.append(f"    value: {f['claim_value']}")
            lines.append(f"    text: {f['claim_text']!r}")
            lines.append(f"    suggested: {f['suggested_action']}")
            lines.append("")

    lines += [
        "## Decision framing (for Simon — wq-054 brief Options A/B/C)",
        "",
        f"  Total scale: {total} flagged claims across {len(by_entity)} entities.",
        "",
        "  Option A (highest-leverage flagged claims only): walk the top affected",
        "  entities (typically the providers like openai/anthropic/google whose",
        "  numbers feed the Sankey) and re-attribute their flagged sub-period",
        "  claims to either (i) a new year_<period>.<field> sub-block or (ii)",
        "  the existing exit_arr / monthly_revenue_peak buckets where applicable.",
        "  Engine impact: directly reduces wq-048 consensus-engine inflation risk.",
        "",
        "  Option B (schema-first): add year_h1, year_h2, year_q1-q4 as standard",
        "  sub-year blocks in entities.json schema, then bulk-migrate flagged",
        "  claims via a follow-on script. Higher upfront cost; pays off when",
        "  the next sub-period claim arrives via the review queue.",
        "",
        "  Option C (provenance annotation only): add a `period_qualifier` field",
        "  to each flagged provenance claim (e.g. `\"period_qualifier\": \"monthly\"`)",
        "  so downstream consumers can filter or convert. Doesn't move data;",
        "  documents the issue in-place. Smallest change; doesn't fix the root.",
        "",
        "  Pick A if Sankey accuracy is the priority. Pick B if you expect more",
        "  sub-period claims long-term. Pick C if this is acceptable rot for now.",
    ]

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n")
    print(f"Wrote {REPORT_PATH}")
    print(f"Headline: {total} flagged claims across {len(by_entity)} entities")
    print()
    print("Top patterns:")
    for label, n in sorted(by_period.items(), key=lambda x: -x[1])[:5]:
        print(f"  {label:20}  {n}")
    print()
    print("Top entities:")
    for slug, n in by_entity.most_common(5):
        print(f"  {slug:30}  {n}")


if __name__ == "__main__":
    main()
