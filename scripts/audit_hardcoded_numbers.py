#!/usr/bin/env python3
"""wq-064 — Site-wide hardcoded number audit (report-only).

Walks every *.html file in repo root, extracts numeric literals, classifies
each by source state / semantic category / should-be-derived, and writes a
markdown report at data/wq-064-hardcoded-audit.md.

NO CODE CHANGES to existing files. This script is purely diagnostic.

Heuristic classifier per brief §3.1:
  - Source state: hardcoded literal | populated from script (data attrs /
    DOM IDs known to be wired) | unclear
  - Semantic category: market_aggregate | per_entity_metric | scenario_assumption
    | ui_default | factual_reference | other
  - Should-be-derived: YES | NO | UNCLEAR

Output: data/wq-064-hardcoded-audit.md (summary, top 20, per-page, suggested briefs).

CLI:
  python3 scripts/audit_hardcoded_numbers.py
  python3 scripts/audit_hardcoded_numbers.py --html-dir .
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "data" / "wq-064-hardcoded-audit.md"

# Numeric literals worth catching:
#   - dollar values:     $745B, $22B, $250B, $1.2T, $17.557, $1,200, $0.50
#   - magnitudes:        ~360T, ~250B, ~50M
#   - percentages:       70%, 0.5%
#   - ratios:            $34, $44 (as ratio strings these still match dollar pattern)
#   - 4-digit years:     2023, 2024, 2025 (likely factual)
NUMERIC_PATTERN = re.compile(
    r"""
    \$?~?\d{1,3}(?:,\d{3})+(?:\.\d+)?[BMTKbmtk]?\b   # 1,234[.5]B
    | \$?~?\d+(?:\.\d+)?\s*[BMTK]\b                  # $22B, ~360T, 1.2T
    | \$\s*\d+(?:\.\d+)?\b                           # $34, $0.50
    | \d+(?:\.\d+)?\s*%                              # 70%, 12.5%
    | \b(?:19|20)\d{2}\b                             # 1900–2099 (years)
    """,
    re.VERBOSE,
)

# Things to skip outright (CSS / non-data presentation).
EXCLUDED_LINE_PATTERNS = [
    re.compile(r"<style"),
    re.compile(r"</style>"),
    re.compile(r"<svg"),
    re.compile(r"</svg>"),
    re.compile(r"viewBox\s*="),  # SVG attr
    re.compile(r"^\s*//"),  # JS comment lines
    re.compile(r"^\s*\*"),  # block comment continuations
]

# Token-level skips when a numeric literal is one of these CSS / hex / id forms.
EXCLUDED_VALUE_PATTERNS = [
    re.compile(r"^\d+\.?\d*(px|em|rem|vh|vw|deg|ms|s)\b"),  # CSS units
    re.compile(r"#[0-9a-fA-F]{3,8}\b"),  # hex colors
    re.compile(r"^\d+$"),  # bare ints can be IDs/lengths/CSS — judged in context
]

# Strong wired-from-script signals (DOM IDs known to be populated by JS).
WIRED_ID_PATTERNS = [
    re.compile(r'id\s*=\s*["\'][a-zA-Z][\w-]*["\']'),
]

# Inline JS that sets textContent / innerHTML — values around them are usually script-driven.
SCRIPT_WIRED_LINE = re.compile(r"\.(textContent|innerHTML)\s*=")
DATA_ATTR_LINE = re.compile(r"data-[\w-]+\s*=")

# Semantic keyword cues
KEYWORDS_REVENUE = ("revenue", "arr", "subscription", "billing", "earnings", "top-line")
KEYWORDS_CAPEX = ("capex", "capital", "infrastructure investment", "datacenter", "compute spend")
KEYWORDS_TOKENS = ("tokens/day", "tokens per day", "tokens", "token volume")
KEYWORDS_SUBSIDY = ("subsidy", "vc", "operating loss", "cash burn", "burn")
KEYWORDS_VALUATION = ("valuation", "raised", "funding")
KEYWORDS_RATIO = ("ratio", "/revenue", "per revenue", "per dollar", "$/")
KEYWORDS_FOUND = ("founded", "since ", "established", "year:", "founded in", "incorporated")
KEYWORDS_METHODOLOGY = ("methodology", "assumption", "estimated at", "we use", "rate")
KEYWORDS_SCENARIO = ("scenario", "bear case", "base case", "bull case", "if ")
KEYWORDS_USERS = ("users", "subscribers", "weekly users")


def _is_skippable_line(line: str) -> bool:
    return any(p.search(line) for p in EXCLUDED_LINE_PATTERNS)


def _is_skippable_value(val: str) -> bool:
    return any(p.search(val) for p in EXCLUDED_VALUE_PATTERNS)


def _split_html_by_block(text: str) -> set[int]:
    """Return the set of 1-indexed line numbers that are inside <style>...</style>
    or <!-- ... --> blocks (skip these)."""
    in_style = False
    in_comment = False
    skip = set()
    for i, line in enumerate(text.split("\n"), 1):
        # Track style block openings/closings
        if "<style" in line and "</style>" not in line:
            in_style = True
            skip.add(i)
            continue
        if in_style:
            skip.add(i)
            if "</style>" in line:
                in_style = False
            continue
        # HTML comment block
        if "<!--" in line and "-->" not in line:
            in_comment = True
            skip.add(i)
            continue
        if in_comment:
            skip.add(i)
            if "-->" in line:
                in_comment = False
            continue
    return skip


def classify(val: str, line: str, line_lower: str) -> dict:
    """Return source_state / semantic_category / should_be_derived."""

    # Source state
    is_in_string = False
    # Find if val sits inside an attribute value or a quoted string in the line
    # Crude check: count quotes around val's position
    if f"'{val}'" in line or f'"{val}"' in line:
        is_in_string = True
    if SCRIPT_WIRED_LINE.search(line):
        # value being set by JS — distinguish constant literal vs derived
        # If the line is `.textContent = '$22B'` it's still hardcoded.
        if is_in_string:
            source_state = "hardcoded_literal_in_script"
        else:
            source_state = "script_derived"
    elif "id=" in line and (val in line.split("id=")[0] or val in line):
        # Visible HTML element with an id — likely wired by JS later
        source_state = "html_element_with_id_(likely_wired)"
    elif is_in_string:
        source_state = "hardcoded_literal"
    else:
        source_state = "hardcoded_literal" if not SCRIPT_WIRED_LINE.search(line) else "unclear"

    # Semantic category
    semantic = "other"
    if any(k in line_lower for k in KEYWORDS_REVENUE):
        if any(k in line_lower for k in ("cumulative", "total", "market", "industry")):
            semantic = "market_aggregate"
        else:
            semantic = "per_entity_metric"
    elif any(k in line_lower for k in KEYWORDS_CAPEX):
        semantic = "market_aggregate"
    elif any(k in line_lower for k in KEYWORDS_TOKENS):
        semantic = "market_aggregate" if any(k in line_lower for k in ("total", "industry", "all", "system")) else "per_entity_metric"
    elif any(k in line_lower for k in KEYWORDS_SUBSIDY):
        semantic = "market_aggregate"
    elif any(k in line_lower for k in KEYWORDS_VALUATION):
        semantic = "per_entity_metric"
    elif any(k in line_lower for k in KEYWORDS_USERS):
        semantic = "per_entity_metric"
    elif any(k in line_lower for k in KEYWORDS_RATIO):
        semantic = "ratio_derived"
    elif any(k in line_lower for k in KEYWORDS_SCENARIO):
        semantic = "scenario_assumption"
    elif any(k in line_lower for k in KEYWORDS_METHODOLOGY):
        semantic = "methodology_constant"
    elif any(k in line_lower for k in KEYWORDS_FOUND):
        semantic = "factual_reference"
    elif re.match(r"^(?:19|20)\d{2}$", val):
        semantic = "date_or_year"
    elif "%" in val:
        semantic = "percentage"

    # Should it be derived?
    if semantic in ("market_aggregate", "per_entity_metric", "ratio_derived"):
        should_derive = "YES"
    elif semantic in ("scenario_assumption", "methodology_constant"):
        should_derive = "YES"  # configurable, currently in HTML
    elif semantic in ("factual_reference", "date_or_year"):
        should_derive = "NO"
    elif semantic == "percentage":
        # Composition percentages that change should be derived; methodology
        # constants (e.g. 0.20 margin) are configurable.
        should_derive = "UNCLEAR"
    else:
        should_derive = "UNCLEAR"

    return {
        "source_state": source_state,
        "semantic_category": semantic,
        "should_be_derived": should_derive,
    }


def extract_values(html_path: Path) -> list[dict]:
    text = html_path.read_text()
    skip_lines = _split_html_by_block(text)
    results = []
    rel = str(html_path.relative_to(ROOT)) if html_path.is_absolute() else str(html_path)
    for lineno, line in enumerate(text.split("\n"), 1):
        if lineno in skip_lines:
            continue
        if _is_skippable_line(line):
            continue
        for match in NUMERIC_PATTERN.finditer(line):
            val = match.group().strip()
            if _is_skippable_value(val):
                continue
            # Skip 4-digit years inside attributes that look like ids/classes
            ctx_start = max(0, match.start() - 40)
            ctx_end = min(len(line), match.end() + 40)
            context = line[ctx_start:ctx_end].strip()
            line_lower = line.lower()
            cls = classify(val, line, line_lower)
            results.append({
                "file": rel,
                "line": lineno,
                "value": val,
                "context": context,
                **cls,
            })
    return results


def prominence_score(row: dict) -> int:
    """Heuristic visual prominence — used to rank top-N candidates.
    Higher = more prominent on the page."""
    line = row.get("context", "").lower()
    score = 0
    if "hero" in line or "headline" in line:
        score += 50
    if "h1" in line or "h2" in line:
        score += 30
    if 'id="hero' in line or "id='hero" in line:
        score += 40
    if 'id="card' in line or 'id="nar' in line:
        score += 20
    if "meta name=" in line or "og:" in line:
        score += 25  # SEO description shows up in social preview
    if "footer" in line:
        score -= 10
    if row.get("source_state", "").startswith("hardcoded_literal"):
        score += 10
    if row.get("should_be_derived") == "YES":
        score += 30
    return score


def render_report(rows: list[dict]) -> str:
    total = len(rows)
    by_state = Counter(r["source_state"] for r in rows)
    by_should = Counter(r["should_be_derived"] for r in rows)
    by_semantic = Counter(r["semantic_category"] for r in rows)
    by_file = defaultdict(list)
    for r in rows:
        by_file[r["file"]].append(r)

    pct = lambda n: f"{(n * 100 / total):.0f}%" if total else "0%"

    # Top 20 unwired+should-be-derived by prominence
    candidates = [r for r in rows if r["should_be_derived"] == "YES"]
    # dedupe by (value, context-stem) so $22B in 5 places counts once but lists locations
    seen = {}
    for r in candidates:
        key = (r["value"], r["context"][:60])
        if key not in seen:
            seen[key] = {**r, "_locations": []}
        seen[key]["_locations"].append(f"{r['file']}:{r['line']}")
    deduped = list(seen.values())
    for r in deduped:
        r["_score"] = prominence_score(r)
        r["_n_locations"] = len(r["_locations"])
    deduped.sort(key=lambda r: (-r["_score"], -r["_n_locations"], r["file"]))
    top20 = deduped[:20]

    # Suggested follow-on briefs grouped by file/category
    brief_groups = defaultdict(list)
    for r in candidates:
        cat = r["semantic_category"]
        brief_groups[cat].append(r["file"])

    def _section_top20(items):
        if not items:
            return "_No high-priority candidates found._"
        lines = ["| # | Page | Line | Value | Context | Why it matters |", "|---|---|---|---|---|---|"]
        for i, r in enumerate(items, 1):
            ctx = r["context"].replace("|", "\\|")[:80]
            why = f"{r['semantic_category']} → should-be-derived; appears in {r['_n_locations']} location(s)"
            lines.append(f"| {i} | `{r['file']}` | {r['line']} | `{r['value']}` | {ctx} | {why} |")
        return "\n".join(lines)

    def _section_per_page():
        out = []
        for f in sorted(by_file.keys()):
            page_rows = by_file[f]
            out.append(f"### `{f}` ({len(page_rows)} values)\n")
            cnt_should = Counter(r["should_be_derived"] for r in page_rows)
            out.append(f"- YES (should derive): {cnt_should.get('YES', 0)}")
            out.append(f"- NO (factual / fixed): {cnt_should.get('NO', 0)}")
            out.append(f"- UNCLEAR: {cnt_should.get('UNCLEAR', 0)}")
            # Sample first 10 should-derive values
            samples = [r for r in page_rows if r["should_be_derived"] == "YES"][:10]
            if samples:
                out.append("\n| Line | Value | Context | Semantic |")
                out.append("|---|---|---|---|")
                for r in samples:
                    ctx = r["context"].replace("|", "\\|")[:70]
                    out.append(f"| {r['line']} | `{r['value']}` | {ctx} | {r['semantic_category']} |")
            out.append("")
        return "\n".join(out)

    def _section_briefs():
        suggestions = []
        # Brief A: methodology page constants
        meth = brief_groups.get("methodology_constant") or []
        if meth:
            files = sorted(set(meth))
            suggestions.append(
                f"- **Brief A: Wire methodology page constants.** "
                f"`methodology_constant` candidates appear in {len(files)} file(s) "
                f"({', '.join(files[:5])}{'...' if len(files) > 5 else ''}). "
                "Move shared rates / percentages into a config file the renderer reads."
            )
        # Brief B: per-entity metric pages
        pent = brief_groups.get("per_entity_metric") or []
        if pent:
            files = sorted(set(pent))
            suggestions.append(
                f"- **Brief B: Wire per-entity metric blocks.** "
                f"`per_entity_metric` candidates in {len(files)} file(s). "
                "Replace hand-edited valuations / user counts / ARR with reads from "
                "entities.json:companies[*].current."
            )
        # Brief C: market aggregates not yet wired
        mkt = brief_groups.get("market_aggregate") or []
        if mkt:
            files = sorted(set(mkt))
            suggestions.append(
                f"- **Brief C: Wire remaining market aggregates.** "
                f"`market_aggregate` candidates in {len(files)} file(s). "
                "Wire to entities.json:market_aggregates.<year> or :_cumulative_2023_2025 "
                "(extends wq-063 cumulative aggregator pattern)."
            )
        # Brief D: scenario assumptions
        scen = brief_groups.get("scenario_assumption") or []
        if scen:
            files = sorted(set(scen))
            suggestions.append(
                f"- **Brief D: Move scenario assumptions to data file.** "
                f"`scenario_assumption` candidates in {len(files)} file(s). "
                "Lift bear/base/bull / projection assumptions out of inline HTML "
                "into data/scenarios.json so they version-control cleanly."
            )
        # Brief E: ratio fields
        ratio = brief_groups.get("ratio_derived") or []
        if ratio:
            files = sorted(set(ratio))
            suggestions.append(
                f"- **Brief E: Compute derived ratios in JS, not literals.** "
                f"`ratio_derived` candidates in {len(files)} file(s). "
                "Ratios should be computed at render time from the values they "
                "reference, never typed in directly."
            )
        if not suggestions:
            suggestions.append("- _(No clear groupings — review per-page section.)_")
        return "\n".join(suggestions)

    md = f"""# wq-064 Hardcoded Number Audit Report

Generated: {Path(__file__).name}

## Summary

- **Total HTML files scanned:** {len(by_file)}
- **Total numeric values found:** {total:,}
- **Source state:**
  - hardcoded literals: {by_state.get('hardcoded_literal', 0):,} ({pct(by_state.get('hardcoded_literal', 0))})
  - hardcoded literal inside script (textContent/innerHTML): {by_state.get('hardcoded_literal_in_script', 0):,} ({pct(by_state.get('hardcoded_literal_in_script', 0))})
  - HTML element with id (likely wired by JS): {by_state.get('html_element_with_id_(likely_wired)', 0):,} ({pct(by_state.get('html_element_with_id_(likely_wired)', 0))})
  - script-derived: {by_state.get('script_derived', 0):,} ({pct(by_state.get('script_derived', 0))})
  - unclear: {by_state.get('unclear', 0):,} ({pct(by_state.get('unclear', 0))})
- **Should be derived:**
  - YES (rewire candidates): {by_should.get('YES', 0):,} ({pct(by_should.get('YES', 0))})
  - NO (intentionally editorial / factual): {by_should.get('NO', 0):,} ({pct(by_should.get('NO', 0))})
  - UNCLEAR (needs human judgment): {by_should.get('UNCLEAR', 0):,} ({pct(by_should.get('UNCLEAR', 0))})
- **Semantic category breakdown:**
{chr(10).join(f"  - `{k}`: {v:,}" for k, v in by_semantic.most_common())}

## Top 20 highest-priority rewire candidates

Ranked by visual prominence heuristic (hero text > nav > body > footer) and
hardcoded-literal status.

{_section_top20(top20)}

## Suggested follow-on briefs

Grouped by data source / category. Each can become its own brief once Simon
prioritises which class to attack first.

{_section_briefs()}

## Per-page inventory

{_section_per_page()}

---

## Heuristic limitations

- Classifier conflates dollar values inside CSS/SVG `viewBox` attrs with data
  values when they're not stripped. Style/SVG blocks are excluded but inline
  fragments may still leak through; spot-check before treating any single
  value as authoritative.
- "HTML element with id (likely wired)" is inferred from `id=` presence on
  the same line; doesn't actually verify a JS file populates the element.
- `should_be_derived=UNCLEAR` is a hold-back when keyword cues don't fire.
  Especially common for percentages, where some are methodology constants
  and some are composition splits.
- `factual_reference` matches on a small keyword list ("founded", "since",
  "year:") — newly-phrased facts will fall to `other`.
"""
    return md


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--html-dir", default=str(ROOT), help="root directory containing *.html (default: repo root)")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="output markdown report path")
    ap.add_argument("--json-out", default=None, help="optional structured JSON output for downstream tooling")
    args = ap.parse_args()

    html_dir = Path(args.html_dir)
    html_files = sorted(html_dir.glob("*.html"))
    if not html_files:
        print(f"No *.html files found under {html_dir}")
        return 2

    all_rows: list[dict] = []
    skipped = []
    for f in html_files:
        try:
            rows = extract_values(f)
            all_rows.extend(rows)
            print(f"  {f.name}: {len(rows)} values")
        except Exception as e:
            skipped.append((f.name, str(e)))
            print(f"  SKIPPED {f.name}: {e}")

    md = render_report(all_rows)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(md)
    print(f"\nWrote {len(all_rows):,} rows from {len(html_files)} files → {args.out}")

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(all_rows, indent=2, default=str))
        print(f"Structured JSON → {args.json_out}")

    if skipped:
        print(f"\n{len(skipped)} files skipped:")
        for name, err in skipped:
            print(f"  {name}: {err}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
