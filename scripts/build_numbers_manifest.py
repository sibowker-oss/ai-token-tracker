#!/usr/bin/env python3
"""wq-102 Stage 1 — Build numbers-manifest.json for the six priority pages.

Walks the priority HTML pages (index, capital, revenue, compute, usage, power),
extracts every visible numeric literal, classifies it, and tries to auto-resolve
the value against site-data.json / entities.json / consensus_overrides.json.

Outputs:
  - data/numbers-manifest.json        (machine-readable; canonical for build)
  - schemas/numbers-manifest.schema.json
  - data/wq-102-source-path-gaps.md   (numbers with no auto-resolution)

Reuses extraction primitives from scripts/audit_hardcoded_numbers.py (wq-064).

CLI:
  python3 scripts/build_numbers_manifest.py
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from collections import Counter, defaultdict
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
BETA = ROOT / "beta"

PRIORITY_PAGES = [
    "index.html",
    "capital.html",
    "revenue.html",
    "compute.html",
    "usage.html",
    "power.html",
]

OUT_MANIFEST = ROOT / "data" / "numbers-manifest.json"
OUT_SCHEMA = ROOT / "schemas" / "numbers-manifest.schema.json"
OUT_GAPS = ROOT / "data" / "wq-102-source-path-gaps.md"

# ── Numeric literal extraction (broader than wq-064 — we want *every* visible
#    literal that could be data-driven, including unmarked dollar+suffix forms,
#    multipliers (e.g. 19×, 2.5x), token counts (~360T, 1.9T/day), and counts).
#
#  Each pattern captures a single token; surrounding context is taken from the line.
#
NUMERIC_PATTERNS = [
    # currency with magnitude suffix:  $745B, $43.07B, $1.2T, $250M, ~$5B
    ("currency_suffix", re.compile(r"~?\$\s*\d+(?:[\.,]\d+)?\s*[BMTKbmtk]\b")),
    # bare magnitude (no $ prefix): 360T, 30T, 1.9T/day, 95 GW
    ("magnitude_bare", re.compile(r"~?\d+(?:[\.,]\d+)?\s*[BMTK](?:/day|/d|/s|\b)")),
    # plain dollar: $34, $0.50, $2.50  (must not be inside a class/id name; we test context)
    ("currency_plain", re.compile(r"\$\s*\d+(?:\.\d+)?\b(?![BMTKbmtk])")),
    # percentages: 70%, 12.5%, +153% , -2.0%
    ("percentage", re.compile(r"[+\-]?\d+(?:\.\d+)?\s*%")),
    # ratio x: 19×, 2.5x, 1.4×
    ("ratio_x", re.compile(r"\d+(?:\.\d+)?\s*[×x]\b")),
    # gigawatts / megawatts
    ("power_units", re.compile(r"\d+(?:\.\d+)?\s*(?:GW|MW|kW|TWh|GWh)\b")),
]

# Markup / style attributes — when a numeric token sits inside one of these,
# it's CSS or layout, not data. We snip these regions out of the line before
# extraction to prevent false-positive captures like `style="--bar-w:50%;"`,
# `width:100%`, `min-width:0`, `class="tier-1"`, `id="card-capex"`.
ATTR_STRIP_PATTERNS = [
    re.compile(r"""\bstyle\s*=\s*"[^"]*\"""", re.DOTALL),
    re.compile(r"""\bstyle\s*=\s*'[^']*\'""", re.DOTALL),
    re.compile(r"""\bclass\s*=\s*"[^"]*\""""),
    re.compile(r"""\bclass\s*=\s*'[^']*'"""),
    re.compile(r"""\bid\s*=\s*"[^"]*\""""),
    re.compile(r"""\bid\s*=\s*'[^']*'"""),
    re.compile(r"""\bdata-(?:bar-w|w)\s*=\s*['"][^'"]*['"]"""),
    re.compile(r"""\bhref\s*=\s*"[^"]*\""""),
    re.compile(r"""\bsrc\s*=\s*"[^"]*\""""),
    re.compile(r"""\bviewBox\s*=\s*"[^"]*\""""),
    re.compile(r"""\baria-label\s*=\s*"[^"]*\""""),
    re.compile(r"""\baria-describedby\s*=\s*"[^"]*\""""),
    re.compile(r"""\btitle\s*=\s*"[^"]*\""""),
    re.compile(r"""\bwidth\s*=\s*"[^"]*\""""),
    re.compile(r"""\bheight\s*=\s*"[^"]*\""""),
    re.compile(r"""\bd\s*=\s*"[^"]*\""""),  # SVG path d=
    re.compile(r"""\bx\s*=\s*"[^"]*\""""),  # SVG x/y/etc.
    re.compile(r"""\by\s*=\s*"[^"]*\""""),
]


def strip_attributes(line: str) -> str:
    """Remove text inside attributes that don't render as visible content.
    Numbers inside style/class/id/href etc. are layout, not data."""
    out = line
    for pat in ATTR_STRIP_PATTERNS:
        out = pat.sub(lambda m: " " * (m.end() - m.start()), out)
    return out

# Things to skip outright at the line level (CSS / SVG / scripts handled separately).
LINE_SKIP_BLOCK_OPENERS = ("<style", "<svg")
LINE_SKIP_BLOCK_CLOSERS = ("</style>", "</svg>")

# Token-level skips after extraction.
TOKEN_SKIP_PATTERNS = [
    re.compile(r"^\d+\.?\d*(px|em|rem|vh|vw|deg|ms|s|fr)\b"),
    re.compile(r"^#[0-9a-fA-F]{3,8}$"),
    re.compile(r"^\d{4}$"),  # bare 4-digit (years) — handled separately
]

YEAR_RE = re.compile(r"^(?:19|20)\d{2}$")

# Lines we should treat as "outside the rendered DOM" (build-time JS, not visible).
# We DO want to capture id-binding hints from these to help auto-resolve.
SCRIPT_OPEN = re.compile(r"<script\b", re.IGNORECASE)
SCRIPT_CLOSE = re.compile(r"</script>", re.IGNORECASE)
HTML_COMMENT_OPEN = "<!--"
HTML_COMMENT_CLOSE = "-->"

# Inside <script>, _setText('domId', expr) and document.getElementById('x').textContent = expr
# give us "domId → JS expression" hints we can use for source_path nomination.
SETTEXT_RE = re.compile(r"_setText\(\s*['\"]([\w\-]+)['\"]\s*,\s*([^)]+?)\)")
GETBYID_TEXT_RE = re.compile(
    r"document\.getElementById\(\s*['\"]([\w\-]+)['\"]\s*\)\.(?:textContent|innerHTML)\s*=\s*([^;]+);"
)
QUERY_TEXT_RE = re.compile(
    r"\.querySelector\(\s*['\"]#([\w\-]+)['\"]\s*\)\.(?:textContent|innerHTML)\s*=\s*([^;]+);"
)

# Basic JS expression → source-path nomination:
#   d.cumulative.capex_total            -> "cumulative.capex_total"
#   d.compute.compute_revenue_2025_gross_usd_b
#   d.sankey.totalCustomerRevenue_gross
#   data.market.\"2025\".total_capex
DOTPATH_RE = re.compile(r"\bd(?:ata|\b)?\.([\w.\[\]'\"]+)")

# ── Domain keywords (semantic classifier). Borrowed from wq-064.
KEYWORDS_REVENUE = (
    "revenue",
    "arr",
    "subscription",
    "billing",
    "earnings",
    "top-line",
    "apps revenue",
)
KEYWORDS_CAPEX = (
    "capex",
    "capital",
    "infrastructure investment",
    "datacenter",
    "data centre",
    "compute spend",
    "compute spent",
    "investment",
)
KEYWORDS_TOKENS = ("tokens/day", "tokens per day", "tokens", "token volume", "t/day")
KEYWORDS_SUBSIDY = ("subsidy", "vc", "operating loss", "cash burn", "burn")
KEYWORDS_VALUATION = ("valuation", "raised", "funding", "round")
KEYWORDS_RATIO = ("ratio", "/revenue", "per revenue", "per dollar", "$/", "× apps", "× revenue", "x revenue")
KEYWORDS_FOUND = ("founded", "since ", "established", "year:", "founded in", "incorporated")
KEYWORDS_METHODOLOGY = ("methodology", "assumption", "estimated at", "we use", "rate", "factor")
KEYWORDS_SCENARIO = ("scenario", "bear case", "base case", "bull case", "if ")
KEYWORDS_USERS = ("users", "subscribers", "weekly users")
KEYWORDS_POWER = ("power", "grid", "gw", "interconnection", "substation", "energy")


# ───────────────────────── Page-block stripping ─────────────────────────


def split_blocks(text: str) -> tuple[set[int], dict[int, dict]]:
    """Return (skip_lines_for_visible_dom, script_block_lines_by_open_lineno).

    skip_lines: 1-indexed line numbers that are NOT visible in the rendered DOM
                (style, svg, script, comment). We still scan script blocks
                separately for id-binding hints.
    script_blocks: keyed by the opening <script> line, value is {start, end, lines:[lineno, content]}
                   so we can mine setText/getElementById bindings.
    """
    skip = set()
    in_style = in_svg = in_script = in_comment = False
    script_blocks: dict[int, dict] = {}
    cur_script_open: int | None = None
    cur_script_lines: list[tuple[int, str]] = []

    for i, line in enumerate(text.split("\n"), 1):
        l = line  # preserve original
        ll = l.lower()
        if in_style:
            skip.add(i)
            if "</style>" in ll:
                in_style = False
            continue
        if in_svg:
            skip.add(i)
            if "</svg>" in ll:
                in_svg = False
            continue
        if in_script:
            skip.add(i)
            cur_script_lines.append((i, l))
            if SCRIPT_CLOSE.search(l):
                in_script = False
                if cur_script_open is not None:
                    script_blocks[cur_script_open] = {
                        "start": cur_script_open,
                        "end": i,
                        "lines": cur_script_lines,
                    }
                cur_script_open = None
                cur_script_lines = []
            continue
        if in_comment:
            skip.add(i)
            if HTML_COMMENT_CLOSE in l:
                in_comment = False
            continue
        # opening detections
        if "<style" in ll and "</style>" not in ll:
            in_style = True
            skip.add(i)
            continue
        if "<svg" in ll and "</svg>" not in ll:
            in_svg = True
            skip.add(i)
            continue
        if SCRIPT_OPEN.search(l) and not SCRIPT_CLOSE.search(l):
            in_script = True
            cur_script_open = i
            cur_script_lines = [(i, l)]
            skip.add(i)
            continue
        if HTML_COMMENT_OPEN in l and HTML_COMMENT_CLOSE not in l:
            in_comment = True
            skip.add(i)
            continue
        # single-line embedded:
        if "<style" in ll or "</style>" in ll:
            skip.add(i)
            continue

    return skip, script_blocks


# ───────────────────────── Numeric extraction ─────────────────────────


def normalize_number(token: str) -> tuple[float | None, str | None]:
    """Return (numeric_value, unit_hint) for a captured token.

    Unit hints: 'B', 'M', 'T', 'K', '$', '%', '×', 'GW', 'MW', None.
    Returned numeric value is the raw number with any magnitude suffix attached
    (i.e., '$745B' → (745.0, 'B'); '~360T' → (360.0, 'T'); '15.97' → (15.97, '$')).
    """
    t = token.strip().replace(",", "")
    t_lower = t.lower()
    # multiplier (×, x)
    m = re.match(r"^(\d+(?:\.\d+)?)\s*[×x]$", t)
    if m:
        return float(m.group(1)), "×"
    # percentage
    m = re.match(r"^([+\-]?\d+(?:\.\d+)?)\s*%$", t)
    if m:
        return float(m.group(1)), "%"
    # power units
    m = re.match(r"^(\d+(?:\.\d+)?)\s*(GW|MW|kW|TWh|GWh)$", t, re.IGNORECASE)
    if m:
        return float(m.group(1)), m.group(2).upper()
    # currency with suffix
    m = re.match(r"^~?\$\s*(\d+(?:\.\d+)?)\s*([BMTKbmtk])$", t)
    if m:
        return float(m.group(1)), m.group(2).upper()
    # bare magnitude
    m = re.match(r"^~?(\d+(?:\.\d+)?)\s*([BMTKbmtk])(?:/day|/d|/s)?$", t)
    if m:
        return float(m.group(1)), m.group(2).upper()
    # plain dollar (no suffix)
    m = re.match(r"^\$\s*(\d+(?:\.\d+)?)$", t)
    if m:
        return float(m.group(1)), "$"
    # bare number
    m = re.match(r"^(\d+(?:\.\d+)?)$", t)
    if m:
        return float(m.group(1)), None
    return None, None


def detect_format(unit: str | None, raw: str) -> str:
    """Map a unit hint to a format string for the manifest entry."""
    raw_l = raw.lower().strip()
    if unit == "%":
        return "percentage_1dp"
    if unit == "×":
        return "ratio_x_to_1"
    if unit in ("GW", "MW", "KW", "TWH", "GWH"):
        return "power_unit"
    if unit == "B":
        # Heuristic: "tokens" context → tokens_compact; default currency_b_compact
        return "currency_b_compact"
    if unit == "M":
        return "currency_m_compact"
    if unit == "T":
        if "$" in raw:
            return "currency_t_compact"
        return "tokens_compact"
    if unit == "K":
        return "count_compact"
    if unit == "$":
        return "currency_unit"
    return "count_compact"


def is_skippable_token(tok: str) -> bool:
    return any(p.search(tok) for p in TOKEN_SKIP_PATTERNS)


def extract_numbers_from_line(line: str) -> list[dict]:
    """Return the numeric tokens worth cataloguing on a single line."""
    out: list[dict] = []
    used_spans: list[tuple[int, int]] = []
    for kind, pat in NUMERIC_PATTERNS:
        for m in pat.finditer(line):
            span = m.span()
            # avoid double-capture across overlapping patterns
            if any(s <= span[0] < e or s < span[1] <= e for s, e in used_spans):
                continue
            used_spans.append(span)
            tok = m.group().strip()
            if is_skippable_token(tok):
                continue
            val, unit = normalize_number(tok)
            if val is None:
                continue
            # Tier-label false positives: "1B", "2B", "3B" without a "$" prefix
            # and surrounded by tier-classification markers (1A/1B, 2A/2B, 3A/3B/3C).
            # Skip these — they're confidence-tier letters, not currency / counts.
            if (
                kind == "magnitude_bare"
                and unit == "B"
                and val < 5
                and re.search(r"\b\d[ABab]\s*/\s*\d[Bb]\b", line)
            ):
                continue
            # Generic small-magnitude bare tokens with no surrounding context
            # are usually tier badges in coloured table cells. Require either
            # a "~" prefix, a "/day" suffix, or a token-related word nearby.
            if kind == "magnitude_bare" and unit == "B" and val < 5:
                ctx = line.lower()
                if "tier" in ctx or "h100" in ctx or "h200" in ctx:
                    continue
                # If the cell is just "<td>NB</td>" style (tier badge), drop it.
                if re.search(rf"<t[hd][^>]*>\s*{re.escape(tok)}\s*</t[hd]>", line, re.IGNORECASE):
                    continue
            out.append({"raw": tok, "kind": kind, "value": val, "unit": unit, "span": span})
    return out


# ───────────────────────── Source-path index ─────────────────────────


def flatten(obj, prefix=""):
    """Yield (path, value) for every leaf in a JSON-like structure."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            np = f"{prefix}.{k}" if prefix else k
            yield from flatten(v, np)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            np = f"{prefix}[{i}]"
            yield from flatten(v, np)
    else:
        yield prefix, obj


def build_value_index(
    site_data: dict, entities: dict, overrides: dict
) -> dict[float, list[dict]]:
    """Build a map from numeric value → [ {root, path, value} ... ].

    Tolerates small unit conversions: a value stored in millions might appear in
    HTML as Bn (divide by 1000) or vice-versa. We index multiple normalisations.
    """
    idx: dict[float, list[dict]] = defaultdict(list)
    for root, blob in (("site-data", site_data), ("entities", entities)):
        for path, v in flatten(blob):
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                f = float(v)
                # primary
                idx[round(f, 4)].append({"root": root, "path": path, "value": f, "scale": 1})
                # B↔M scale (×1000 / ÷1000)
                if 0 < abs(f) < 100000:
                    idx[round(f / 1000.0, 4)].append(
                        {"root": root, "path": path, "value": f, "scale": 0.001}
                    )
                if 0 < abs(f) < 100000:
                    idx[round(f * 1000.0, 4)].append(
                        {"root": root, "path": path, "value": f, "scale": 1000}
                    )
                # round-to-int (e.g. 745.0 ↔ 745)
                idx[round(f)].append({"root": root, "path": path, "value": f, "scale": 1})
                # one-decimal (e.g., 19.279 ↔ 19.3)
                idx[round(f, 1)].append({"root": root, "path": path, "value": f, "scale": 1})
    return idx


# ───────────────────────── Classification ─────────────────────────


def classify_semantic(line: str, value: float, unit: str | None) -> str:
    ll = line.lower()
    if any(k in ll for k in KEYWORDS_RATIO) or unit == "×":
        return "ratio_derived"
    if any(k in ll for k in KEYWORDS_TOKENS) or (unit == "T" and "token" in ll):
        return "market_aggregate.tokens"
    if any(k in ll for k in KEYWORDS_CAPEX):
        # cumulative vs annual
        if any(k in ll for k in ("cumulative", "2023", "2023-25", "2023–25", "to date", "total")):
            return "market_aggregate.capex_cumulative"
        return "market_aggregate.capex_annual"
    if any(k in ll for k in KEYWORDS_REVENUE):
        if any(k in ll for k in ("cumulative", "industry", "market", "total")):
            return "market_aggregate.revenue"
        if any(k in ll for k in ("compute", "hyperscaler", "frontier", "neocloud")):
            return "market_aggregate.compute_revenue"
        return "per_entity_metric.revenue"
    if any(k in ll for k in KEYWORDS_VALUATION):
        return "per_entity_metric.valuation"
    if any(k in ll for k in KEYWORDS_USERS):
        return "per_entity_metric.users"
    if any(k in ll for k in KEYWORDS_POWER) or unit in ("GW", "MW"):
        return "market_aggregate.power"
    if any(k in ll for k in KEYWORDS_SUBSIDY):
        return "market_aggregate.vc_subsidy"
    if any(k in ll for k in KEYWORDS_SCENARIO):
        return "scenario_assumption"
    if any(k in ll for k in KEYWORDS_METHODOLOGY):
        return "methodology_constant"
    if any(k in ll for k in KEYWORDS_FOUND):
        return "factual_reference"
    if unit == "%":
        return "percentage_uncategorised"
    return "uncategorised"


def detect_anchor_id(line: str) -> str | None:
    """If the line contains id="..." (or data-num="..."), return it for binding hints."""
    m = re.search(r"\bid\s*=\s*['\"]([\w\-]+)['\"]", line)
    if m:
        return m.group(1)
    m = re.search(r"\bdata-num\s*=\s*['\"]([\w\-]+)['\"]", line)
    if m:
        return m.group(1)
    return None


# data-narrative="market_2025_total_customer_revenue_gross" → source_path hint
DATA_NARRATIVE_RE = re.compile(r'data-narrative\s*=\s*["\']([\w_\.]+)["\']')

# Hand-curated map from data-narrative keys to canonical source paths. Add
# entries here as new narrative keys appear; the build script falls back to
# leaving the entry unresolved if the key isn't mapped.
DATA_NARRATIVE_MAP = {
    "market_2025_total_customer_revenue_gross": "site-data.sankey.totalCustomerRevenue_gross",
    "market_2025_total_customer_revenue_net": "site-data.sankey.totalCustomerRevenue",
    "cumulative_2023_2025_capex_total": "site-data.cumulative.capex_total",
    "cumulative_2023_2025_tokens": "site-data.cumulative.tokens_2025_annualized",
    "compute_revenue_2025_gross": "site-data.compute.compute_revenue_2025_gross_usd_b",
    "infra_to_revenue_2025": "site-data.cumulative.infra_to_revenue_ratio_2025",
}


def detect_data_narrative_hint(line: str) -> str | None:
    """Extract data-narrative="..." attribute and map it to a known source_path."""
    m = DATA_NARRATIVE_RE.search(line)
    if not m:
        return None
    key = m.group(1)
    return DATA_NARRATIVE_MAP.get(key)


# ───────────────────────── Script-block binding mining ─────────────────────────


def mine_script_bindings(script_blocks: dict[int, dict]) -> dict[str, str]:
    """For each priority page's <script> block, parse _setText / getElementById
    hydration calls and return {dom_id: candidate_source_path}.

    We trace via simple regex against `d.<path>` references inside the call.
    """
    bindings: dict[str, str] = {}
    for blk in script_blocks.values():
        full = "\n".join(line for _, line in blk["lines"])
        for m in SETTEXT_RE.finditer(full) :
            dom_id, expr = m.group(1), m.group(2)
            path = _extract_dotpath(expr)
            if path:
                bindings.setdefault(dom_id, path)
        for m in GETBYID_TEXT_RE.finditer(full):
            dom_id, expr = m.group(1), m.group(2)
            path = _extract_dotpath(expr)
            if path:
                bindings.setdefault(dom_id, path)
        for m in QUERY_TEXT_RE.finditer(full):
            dom_id, expr = m.group(1), m.group(2)
            path = _extract_dotpath(expr)
            if path:
                bindings.setdefault(dom_id, path)
        # Also resolve via the local `b.X` shorthand pattern on index.html:
        #   _setText('card-capex', fmt$(b.capex))
        # combined with `capex: (d.cumulative && d.cumulative.capex_total) || ...`
        # → record capex → cumulative.capex_total, then when we see _setText('card-capex', ...b.capex...)
        # we resolve the dom_id.
        local_map: dict[str, str] = {}
        for lm in re.finditer(
            r"\b(\w+)\s*:\s*\(\s*d(?:ata)?\.([\w.\[\]'\"]+?)\s*&&\s*d(?:ata)?\.([\w.\[\]'\"]+?)\s*\)",
            full,
        ):
            key, _path1, path2 = lm.group(1), lm.group(2), lm.group(3)
            local_map[key] = path2
        # second pass — _setText('xxx', fmt$(b.<key>)) → bindings[xxx] = local_map[key]
        for m in re.finditer(
            r"_setText\(\s*['\"]([\w\-]+)['\"]\s*,\s*[\w$]+\(\s*b\.(\w+)", full
        ):
            dom_id, key = m.group(1), m.group(2)
            if key in local_map and dom_id not in bindings:
                bindings[dom_id] = local_map[key]
    return bindings


def _extract_dotpath(expr: str) -> str | None:
    m = DOTPATH_RE.search(expr)
    if not m:
        return None
    raw = m.group(1)
    # Trim trailing operators / parens / spaces
    raw = re.split(r"[\s\)\}\,\|\&\+\-\*/]", raw, maxsplit=1)[0]
    raw = raw.strip(".'\"")
    if not raw:
        return None
    return raw


# ───────────────────────── Auto-resolution ─────────────────────────

PATH_KEYWORD_HINTS: list[tuple[str, list[str]]] = [
    # (path keyword, [HTML context keywords])
    ("capex", ["capex", "capital", "infrastructure"]),
    ("cumulative", ["cumulative", "2023", "2023–25", "2023-25"]),
    ("compute_revenue", ["compute", "ai compute revenue", "frontier"]),
    ("totalCustomerRevenue", ["apps revenue", "customer", "revenue"]),
    ("totalCustomerRevenue_gross", ["apps revenue", "gross", "customer-paid"]),
    ("yoy", ["yoy", "year-on-year", "growth", "+1"]),
    ("token", ["tokens", "t/day", "/day"]),
    ("valuation", ["valuation"]),
    ("user_count", ["users"]),
    ("vc_subsidy", ["vc", "subsidy", "burn"]),
    ("ratio", ["ratio", "× revenue", "per revenue"]),
    ("frontier_lab_compute", ["frontier", "lab compute"]),
    ("hosted_model_apis", ["api", "hosted"]),
    ("ai_workload_compute", ["ai workload"]),
    ("mag7_capex", ["mag7", "hyperscaler"]),
    ("neocloud_capex", ["neocloud"]),
    ("sovereign_capex", ["sovereign"]),
    ("enterprise_capex", ["enterprise"]),
    ("apps_total", ["apps revenue", "apps total", "apps"]),
    ("compute_net", ["compute net", "net external"]),
    ("industry_total", ["industry total", "industry-wide"]),
    ("ai_native", ["ai-native", "ai native"]),
    ("trad_total", ["traditional", "trad saas"]),
    ("infra_to_revenue", ["infrastructure", "infra to revenue"]),
]


# Semantic → preferred source_path mapping. When the surrounding HTML context
# clearly identifies what the number IS (regardless of value), we can nominate
# the path even if the literal value differs from the live source — that
# discrepancy IS the supersession story we're installing.
#
# Each rule: (page_glob, [required context phrases (any-of)], unit_set, source_path)
# `unit_set` of None means any. page_glob "*" means any page.
SEMANTIC_PATH_RULES: list[tuple[str, list[str], set | None, str]] = [
    # ── Cumulative 2023–2025 aggregates (homepage + capital) ─────────────
    ("*", ["cumulative", "2023", "infrastructure investment"], {"B"}, "site-data.cumulative.capex_total"),
    ("*", ["of infrastructure investment"], {"B"}, "site-data.cumulative.capex_total"),
    ("*", ["cumulative 2023", "ai capital expenditure"], {"B"}, "site-data.cumulative.capex_total"),
    ("*", ["cumulative", "tokens"], {"T"}, "site-data.cumulative.tokens_2025_annualized"),
    ("*", ["tokens/day", "360t", "360 t"], {"T"}, "site-data.cumulative.tokens_2025_annualized"),
    ("*", ["~360t"], {"T"}, "site-data.cumulative.tokens_2025_annualized"),
    # ── Compute revenue (homepage hero, compute page) ────────────────────
    ("*", ["ai compute revenue earned", "compute revenue", "compute earned"], {"B"}, "site-data.compute.compute_revenue_2025_gross_usd_b"),
    ("*", ["ai compute revenue", "2025"], {"B"}, "site-data.compute.compute_revenue_2025_gross_usd_b"),
    ("*", ["+153%", "yoy", "compute"], {"%"}, "site-data.compute.yoy_growth_pct"),
    ("*", ["frontier-lab compute", "frontier lab compute"], {"B"}, "site-data.compute.frontier_lab_compute_2025_usd_b"),
    ("*", ["ai workload compute"], {"B"}, "site-data.compute.ai_workload_compute_2025_usd_b"),
    ("*", ["hosted model apis", "hosted model api"], {"B"}, "site-data.compute.hosted_model_apis_gross_2025_usd_b"),
    # ── Apps Revenue (revenue.html + homepage card) ──────────────────────
    ("*", ["customer-paid", "apps revenue"], {"B"}, "site-data.sankey.totalCustomerRevenue_gross"),
    ("*", ["customer-paid ai revenue"], {"B"}, "site-data.sankey.totalCustomerRevenue_gross"),
    ("revenue.html", ["actual revenue collected"], {"B"}, "site-data.sankey.totalCustomerRevenue"),
    ("*", ["industry total", "arr"], {"B"}, "site-data.arrModel.combined.industry_total"),
    ("*", ["apps_total", "apps total"], {"B"}, "site-data.arrModel.combined.apps_total"),
    ("*", ["compute_net", "compute net"], {"B"}, "site-data.arrModel.combined.compute_net"),
    ("*", ["ai-native share", "ai native share"], {"%"}, "site-data.arrModel.combined.ai_native_share_pct"),
    # ── Capital Sankey + bucket totals (capital.html) ────────────────────
    ("capital.html", ["mag7", "hyperscaler capex"], {"B"}, "entities.market_aggregates.2025.mag7_capex"),
    ("capital.html", ["neocloud capex"], {"B"}, "entities.market_aggregates.2025.neocloud_capex"),
    ("capital.html", ["sovereign capex"], {"B"}, "entities.market_aggregates.2025.sovereign_capex"),
    ("capital.html", ["enterprise capex"], {"B"}, "entities.market_aggregates.2025.enterprise_capex"),
    ("capital.html", ["total ai capex", "total 2025 capex"], {"B"}, "entities.market_aggregates.2025.total_capex"),
    ("capital.html", ["capital sankey total", "total cumulative"], {"B"}, "site-data.capital_sankey.total"),
    # ── Hook ratio (homepage) ────────────────────────────────────────────
    ("index.html", ["of compute spend stands behind", "compute spend stands"], {"$"}, "site-data.compute.layer_stack_ratios.compute_per_dollar_apps"),
    # ── Hyperscaler concentration (compute.html) ─────────────────────────
    ("*", ["frontier labs paid", "frontier-lab"], {"%"}, "site-data.compute.concentration.frontier_lab_share_pct"),
    # ── Power (placeholder editorial figure) ─────────────────────────────
    ("index.html", ["power", "1.4× apps revenue"], {"B"}, "site-data.compute.layer_stack_ratios.power_per_dollar_apps"),
    ("index.html", ["usage", "9.4× apps revenue"], {"B"}, "site-data.compute.layer_stack_ratios.usage_per_dollar_apps"),
    ("index.html", ["compute", "2.5× apps revenue"], {"$"}, "site-data.compute.layer_stack_ratios.compute_per_dollar_apps"),
    # NOTE: layer_stack_ratios.*_per_dollar_apps fields don't exist yet.
    # They're nominated as stubs — Stage 2 render falls back to editorial
    # until engine extension lands. _path_exists=false will be recorded.
    ("index.html", ["19× apps revenue"], {"×"}, "site-data.compute.layer_stack_ratios.capex_per_dollar_apps"),
    ("index.html", ["1.4× apps revenue"], {"×"}, "site-data.compute.layer_stack_ratios.power_per_dollar_apps"),
    ("index.html", ["9.4× apps revenue"], {"×"}, "site-data.compute.layer_stack_ratios.usage_per_dollar_apps"),
    ("index.html", ["2.5× apps revenue"], {"×"}, "site-data.compute.layer_stack_ratios.compute_per_dollar_apps"),
    # ── Homepage hook ratio (Compute / Apps Revenue) ─────────────────────
    ("index.html", ["compute spend stands behind"], {"$"}, "site-data.compute.layer_stack_ratios.compute_per_dollar_apps"),
    # ── Homepage Power placeholder + Usage notional ──────────────────────
    ("index.html", ["ais-power-figure"], {"B"}, "site-data.compute.layer_stack_ratios.power_revenue_2025_usd_b"),
    ("index.html", ["ais-usage-figure"], {"B"}, "site-data.compute.layer_stack_ratios.usage_revenue_2025_usd_b"),
    ("index.html", ["ais-capex-figure"], {"B"}, "entities.market_aggregates.2025.total_capex"),
    # ── capital.html sankey utilization narrative buckets ────────────────
    ("capital.html", ["inference (paid)"], {"B"}, "site-data.capital_sankey.utilization.Inference (Paid)"),
    ("capital.html", ["inference (free tier)"], {"B"}, "site-data.capital_sankey.utilization.Inference (Free Tier)"),
    ("capital.html", ["inference (ad platform)"], {"B"}, "site-data.capital_sankey.utilization.Inference (Ad Platform)"),
    ("capital.html", ["model training"], {"B"}, "site-data.capital_sankey.utilization.Model Training"),
    ("capital.html", ["in build / in transit"], {"B"}, "site-data.capital_sankey.utilization.In Build / In Transit"),
    # ── capital.html sensitivity panel sliders (editorial defaults) ──────
    ("capital.html", ["sens-idle-val"], {"B"}, "site-data.capital_sankey.sensitivity_defaults.idle_capex_b"),
    ("capital.html", ["sens-ads-val"], {"B"}, "site-data.capital_sankey.sensitivity_defaults.ads_capex_b"),
    ("capital.html", ["sens-china-val"], {"%"}, "site-data.capital_sankey.sensitivity_defaults.china_share_pct"),
    ("capital.html", ["sens-ratio-display"], {"$"}, "site-data.capital_sankey.sensitivity_defaults.ratio_display_usd"),
    ("capital.html", ["counterfactual: exclude"], {"B"}, "entities.market_aggregates._counterfactual.ad_self_funded_capex_b"),
    ("capital.html", ["of self-funded ad/cloud"], {"B"}, "entities.market_aggregates._counterfactual.ad_self_funded_capex_b"),
    ("capital.html", ["nvidia dc revenue"], {"B"}, "entities.market_aggregates._cumulative_2023_2025.nvidia_dc_revenue_b"),
    ("capital.html", ["allocate approximately"], {"B"}, "entities.market_aggregates._counterfactual.ad_self_funded_capex_b"),
    ("capital.html", ["total ai capex reached approximately"], {"B"}, "entities.market_aggregates._cumulative_2023_2025.capex_total"),
    ("capital.html", ["total ai capex"], {"B"}, "entities.market_aggregates._cumulative_2023_2025.capex_total"),
    ("capital.html", ["ai customer revenue"], {"B"}, "site-data.sankey.totalCustomerRevenue_gross"),
    # ── compute.html "for every $1 of customer apps revenue" ratio block ─
    ("compute.html", ["google's rpo jump"], {"B"}, "entities.market_aggregates._narrative.google_rpo_b"),
    # ── usage.html token signal lines (signal-current, target are fixed)
    # ── revenue.html methodology percentages (channel routing) — fixed via narrative rule
    # ── power.html — 95 GW manual figure (no engine path; mark as fixed)
]


# Line-level phrases that mark every number on the line as fixed editorial.
# Use sparingly — narrow phrases only.
FIXED_EDITORIAL_LINE_PHRASES = [
    # Tier mix breakdowns on hero cards (40% Sourced / 30% Derived / 30% Modeled)
    "% sourced",
    "% derived",
    "% modeled",
    # Methodology/scenario thresholds
    "signal-target",
    "signal-condition",
    "signal-current",
    # Tier explanatory rows
    "1a/1b",
    "2a/2b",
    "3a/3b",
    # Methodology rate footnotes
    "notional @",
    "/m output rate",
    "/m input rate",
    # Narrative reference targets and reconciliation prose
    "nvidia $1t target",
    "revenue reconciliation:",
    # Revenue page methodology explainers
    "why do the middle columns",
    "per-archetype channel routing",
    # Power v3 placeholder (entire page is editorial pending engine)
    "ercot + pjm",
    "interconnection queue",
    # JS-driven sensitivity / counterfactual panel readouts (handled in Stage 2
    # via direct anchor wiring, not via the static manifest auto-resolver).
    # NOTE: data-narrative=".." anchors are NOT marked fixed — they're a
    # binding signal we use to nominate source_path (see semantic rules).
    "cf-ratio-from",
    "cf-ratio-to",
    "cf-check",
]

# Token-context phrases (looked up in a small window around the token span)
# that mark THIS PARTICULAR token as rhetorical / fixed, without affecting
# other tokens on the same line.
FIXED_EDITORIAL_TOKEN_PHRASES = [
    # Rhetorical "every $1 of revenue", "for every $1"
    ("for every", 30),
    ("every $1", 30),
    ("behind every", 30),
    # "1× baseline" — narrative anchor
    ("baseline", 20),
    # "trailing-q" methodology footnote
    ("trailing-q", 30),
    ("trailing q", 30),
    # Approximation phrasing
    ("stabilises at", 30),
    ("stabilizes at", 30),
    ("is extended from", 30),
    # Threshold / target signal
    ("target:", 30),
    ("threshold:", 30),
    ("&ge;", 12),
    ("&le;", 12),
    # Regulatory / corporate numerics
    ("abn ", 20),
    ("acn ", 20),
    ("© 2026", 30),
]


def is_line_fixed(line: str) -> bool:
    ll = line.lower()
    return any(phrase in ll for phrase in FIXED_EDITORIAL_LINE_PHRASES)


def is_token_fixed(line: str, span: tuple[int, int]) -> bool:
    """Check whether the immediate vicinity of the token (±N chars) contains
    a fixed-editorial phrase. Only marks THIS token, not the whole line."""
    ll = line.lower()
    s, e = span
    for phrase, window in FIXED_EDITORIAL_TOKEN_PHRASES:
        # search within [s-window, e+window]
        ws = max(0, s - window)
        we = min(len(ll), e + window)
        if phrase in ll[ws:we]:
            return True
    return False


# Hero / headline DOM cues — when a line carries one of these, the number
# inside is prominent and SHOULD be wired to a data path (auto-resolved or
# escalated to the gap report). Conversely, a line WITHOUT any of these cues
# that sits inside narrative tags (<p>, <li>, <td>) is treated as narrative
# editorial and marked source_state=fixed when no rule fires.
HERO_CLASS_CUES = (
    'class="hero',
    'class="lc-value',
    'class="value"',
    'class="hook',
    'class="ais-figure',
    'class="lt-value',
    'class="hero-stat',
    'class="metric',
    'class="kpi',
    'class="hook-number',
    'class="big',
    'class="sens-ratio',
    'class="cp-num',
    'class="signal-current',
    'class="ais-sub',
    'class="ais-label',
    'class="lc-title',
    'class="hero-sub',
    'class="hero-strip',
    'class="cf-ratio',
    'class="kpi-period',
)


def is_hero_line(line: str) -> bool:
    ll = line.lower()
    return any(cue in ll for cue in HERO_CLASS_CUES) or "id=\"hero" in ll


NARRATIVE_TAG_RE = re.compile(
    r"<(?:p|li|td|th|blockquote|figcaption|small"
    r"|span\s+class=\"(?:notes|sub|h2-sub|cp-desc|cf-detail|lc-desc|tt-dim|sub-text)"
    r"|div\s+class=\"(?:cp-title|cp-desc|notes|bridge|narrative|sub|reconciliation|signal-current|sens-label))",
    re.IGNORECASE,
)


def is_narrative_line(line: str) -> bool:
    """Heuristic: the number on this line sits in narrative prose (e.g. inside
    a <p>, <li>, <td>, .notes, .sub, .cp-desc). Hero/headline classes override
    narrative classification.
    """
    if is_hero_line(line):
        return False
    return bool(NARRATIVE_TAG_RE.search(line))


def nominate_via_semantic_rules(
    page: str, line: str, unit: str | None
) -> str | None:
    """Try to assign source_path by context phrases (not by value match).
    A rule fires when ALL phrases are present in the line and the unit matches.
    Rules earlier in SEMANTIC_PATH_RULES win (longest-context phrases first)."""
    ll = line.lower()
    for page_glob, phrases, units, path in SEMANTIC_PATH_RULES:
        if page_glob != "*" and page_glob != page:
            continue
        if units is not None and unit not in units:
            continue
        if all(p in ll for p in phrases):
            return path
    return None


def score_path(path: str, line_lower: str) -> int:
    """Heuristic: does this candidate path match the surrounding HTML context?"""
    p = path.lower()
    score = 0
    for needle, hints in PATH_KEYWORD_HINTS:
        if needle.lower() in p:
            for h in hints:
                if h in line_lower:
                    score += 5
    # generic field-name overlap
    for word in re.findall(r"[a-z_]+", p):
        if len(word) >= 4 and word in line_lower:
            score += 2
    return score


def path_exists(qualified_path: str, site_data: dict, entities: dict) -> bool:
    """Verify a `site-data.x.y.z` or `entities.x.y.z` path resolves to a leaf."""
    if not qualified_path:
        return False
    if qualified_path.startswith("site-data."):
        blob, rest = site_data, qualified_path[len("site-data."):]
    elif qualified_path.startswith("entities."):
        blob, rest = entities, qualified_path[len("entities."):]
    else:
        return False
    obj = blob
    # split on '.' but allow keys with spaces / parens (e.g. "Inference (Paid)")
    parts = rest.split(".")
    for p in parts:
        if isinstance(obj, dict) and p in obj:
            obj = obj[p]
        else:
            return False
    return True


def attempt_resolve(
    value: float,
    unit: str | None,
    line: str,
    value_index: dict[float, list[dict]],
    binding_hint: str | None,
) -> tuple[str | None, list[str]]:
    """Return (best_source_path, candidates) for a numeric value.

    best_source_path is None when we can't disambiguate; candidates is the
    full ranked list (prefixed with root, e.g. site-data.cumulative.capex_total).
    """
    line_lower = line.lower()

    # binding_hint always wins if present (already came from JS hydration).
    if binding_hint:
        return f"site-data.{binding_hint}", [f"site-data.{binding_hint}"]

    candidates: list[dict] = []
    for key in (round(value, 4), round(value, 1), round(value)):
        candidates.extend(value_index.get(key, []))

    # dedupe
    seen = set()
    unique_candidates = []
    for c in candidates:
        k = (c["root"], c["path"])
        if k in seen:
            continue
        seen.add(k)
        unique_candidates.append(c)

    if not unique_candidates:
        return None, []

    # unit-aware filtering
    def unit_ok(c: dict) -> bool:
        path_l = c["path"].lower()
        if unit == "%":
            return "pct" in path_l or "percent" in path_l or "ratio" in path_l or "share" in path_l or "rate" in path_l or "growth" in path_l
        if unit in ("GW", "MW"):
            return "gw" in path_l or "power" in path_l or "capacity" in path_l
        if unit == "×":
            return "ratio" in path_l or "infra_to_revenue" in path_l
        if unit == "T" and "tokens" in path_l:
            return True
        return True

    filtered = [c for c in unique_candidates if unit_ok(c)] or unique_candidates

    # rank by context match
    scored = sorted(
        filtered,
        key=lambda c: -score_path(c["path"], line_lower),
    )

    ranked = [f"{c['root']}.{c['path']}" for c in scored]
    if not scored:
        return None, ranked
    top = scored[0]
    top_score = score_path(top["path"], line_lower)
    # If only 1 candidate or top has a clear margin, take it.
    if len(scored) == 1 or top_score >= 4:
        return f"{top['root']}.{top['path']}", ranked[:8]
    # Multiple ambiguous matches: only return if all top hits agree on path-tail
    # (rare). Otherwise leave unresolved with ranked candidates.
    return None, ranked[:8]


# ───────────────────────── ID generation ─────────────────────────


def page_prefix(page: str) -> str:
    return Path(page).stem  # capital, revenue, ...


def slug_from_context(line: str, value: float, unit: str | None) -> str:
    """Build a short, stable slug from the surrounding HTML context."""
    text = re.sub(r"<[^>]+>", " ", line)  # strip tags
    text = re.sub(r"[^a-zA-Z0-9 ]", " ", text).lower()
    words = [w for w in text.split() if 2 < len(w) < 20]
    # drop generic words
    drop = {
        "this",
        "that",
        "with",
        "into",
        "from",
        "have",
        "where",
        "open",
        "ledger",
        "more",
        "view",
        "page",
        "the",
        "and",
        "for",
        "are",
        "was",
        "were",
        "per",
        "year",
        "calendar",
        "data",
        "what",
        "when",
        "how",
        "all",
        "their",
        "has",
        "but",
    }
    words = [w for w in words if w not in drop and not w.isdigit()]
    return "_".join(words[:4]) or "value"


def make_id(page: str, semantic: str, line: str, value: float, unit: str | None, anchor_hint: str | None) -> str:
    if anchor_hint:
        # use existing dom id when available — most stable
        clean = re.sub(r"[^a-zA-Z0-9]+", "_", anchor_hint).strip("_").lower()
        return f"{page_prefix(page)}.dom.{clean}"
    sem_short = semantic.replace(".", "_")
    slug = slug_from_context(line, value, unit)
    return f"{page_prefix(page)}.{sem_short}.{slug}"


# ───────────────────────── Per-page extraction ─────────────────────────


def extract_page_entries(
    page_path: Path,
    value_index: dict[float, list[dict]],
    site_data: dict,
    entities: dict,
) -> tuple[list[dict], list[dict]]:
    """Return (entries, raw_rows). Entries are manifest-shaped; raw_rows are
    the underlying scan log used to write the gap report."""
    text = page_path.read_text()
    skip_lines, script_blocks = split_blocks(text)
    bindings = mine_script_bindings(script_blocks)
    page_name = page_path.name

    entries: list[dict] = []
    raw_rows: list[dict] = []

    for lineno, line in enumerate(text.split("\n"), 1):
        if lineno in skip_lines:
            continue
        # cheap pre-filter: skip lines that don't contain a digit
        if not re.search(r"\d", line):
            continue
        # strip CSS / class / id / href / style attribute payloads — those
        # numbers are layout, not data.
        scrub = strip_attributes(line)
        toks = extract_numbers_from_line(scrub)
        if not toks:
            continue
        # detect any anchor on this line (uses ORIGINAL line, since the id=
        # attribute was stripped above)
        anchor_hint = detect_anchor_id(line)
        # nominate source_path via existing dom-id binding when present
        binding_hint = bindings.get(anchor_hint) if anchor_hint else None
        narrative_hint = detect_data_narrative_hint(line)
        line_fixed = is_line_fixed(line)

        for t in toks:
            val = t["value"]
            unit = t["unit"]
            raw = t["raw"]
            # Skip pure 4-digit years that fall through (extra defence)
            if YEAR_RE.match(raw.strip("$~")):
                continue
            semantic = classify_semantic(line, val, unit)
            # Skip values we don't want to catalogue:
            #   - factual_reference (founded year, ABN, etc.)
            #   - uncategorised AND no obvious magnitude → likely UI default / count
            if semantic == "factual_reference":
                continue
            # filter out trivial counts (e.g. "5 cards", "3 segments")
            if semantic == "uncategorised" and unit is None:
                continue

            # Intentionally fixed editorial numbers (tier mixes, methodology
            # constants) carry no source_path — record state=fixed and skip
            # auto-resolution. Two checks:
            #   - line_fixed: the entire line is editorial methodology (tier mix)
            #   - token_fixed: just this token is rhetorical (e.g. "every $1")
            token_fixed = is_token_fixed(line, t["span"])
            if line_fixed or token_fixed:
                source_path = None
                candidates: list[str] = []
                source_state = "fixed"
            else:
                # 1) JS hydration binding hint (most reliable)
                # 2) data-narrative="..." attribute hint
                # 3) Semantic context-phrase rule (handles supersession story
                #    where editorial value differs from current source value)
                # 4) Value-index match (fallback when first three miss)
                rule_path = nominate_via_semantic_rules(page_name, line, unit)
                if binding_hint:
                    source_path = f"site-data.{binding_hint}"
                    candidates = [source_path]
                elif narrative_hint:
                    source_path = narrative_hint
                    candidates = [narrative_hint]
                elif rule_path:
                    source_path = rule_path
                    candidates = [rule_path]
                else:
                    source_path, candidates = attempt_resolve(
                        val, unit, line, value_index, None
                    )
                # Numbers in narrative prose without a semantic-rule match
                # are intentional editorial — preserve the literal, no
                # supersession. Hero numbers stay "editorial" (Stage 2 will
                # wire them) and surface as gaps when resolution failed.
                if not source_path and is_narrative_line(line):
                    source_state = "fixed"
                    candidates = []  # don't surface in gap report
                else:
                    source_state = "editorial"  # build flips at Stage 2

            sp_exists = bool(source_path) and path_exists(source_path, site_data, entities)
            entry = {
                "id": make_id(page_name, semantic, line, val, unit, anchor_hint),
                "page": page_name,
                "anchor_selector": (
                    f'#{anchor_hint}' if anchor_hint else f'[data-num][data-line="{lineno}"]'
                ),
                "anchor_dom_id": anchor_hint,
                "current_rendered_value": raw,
                "semantic": semantic,
                "source_state": source_state,
                "source_path": source_path,
                "source_path_exists": sp_exists,
                "source_path_candidates": candidates,
                "editorial_fallback": {
                    "value": val,
                    "unit": unit,
                    "raw": raw,
                    "origin": "html_literal_at_capture",
                    "audit_ref": f"{page_name}:{lineno}",
                },
                "supersession_threshold": {
                    "provenance_score_min": 0.7,
                    "consensus_weight_min": "indicative",
                },
                "format": detect_format(unit, raw),
                "last_changed": None,
                "notion_id": None,
                "_capture": {
                    "line": lineno,
                    "context": line.strip()[:240],
                    "binding_hint": binding_hint,
                },
            }
            entries.append(entry)
            raw_rows.append(
                {
                    "page": page_name,
                    "line": lineno,
                    "raw": raw,
                    "value": val,
                    "unit": unit,
                    "semantic": semantic,
                    "anchor_hint": anchor_hint,
                    "binding_hint": binding_hint,
                    "source_path": source_path,
                    "candidates": candidates,
                    "context": line.strip()[:240],
                }
            )
    return entries, raw_rows


# ───────────────────────── ID disambiguation + dedupe ─────────────────────────


def dedupe_and_disambiguate(entries: list[dict]) -> list[dict]:
    """1) Ensure manifest ids are unique.
    2) When two entries on different pages share (source_path, format, value),
       collapse them into a single entry with `pages: [..]`.
    """
    # Stage A: collapse cross-page duplicates by (source_path, format, value)
    by_key: dict[tuple, dict] = {}
    others: list[dict] = []
    for e in entries:
        sp = e["source_path"]
        if sp:
            key = (sp, e["format"], round(e["editorial_fallback"]["value"], 3))
            if key in by_key:
                existing = by_key[key]
                existing.setdefault("pages", [existing["page"]])
                if e["page"] not in existing["pages"]:
                    existing["pages"].append(e["page"])
                existing.setdefault("anchor_selectors", [existing["anchor_selector"]])
                existing["anchor_selectors"].append(e["anchor_selector"])
                continue
            by_key[key] = e
        else:
            others.append(e)
    merged = list(by_key.values()) + others

    # Stage B: id uniqueness pass
    seen_ids: dict[str, int] = {}
    for e in merged:
        base = e["id"]
        if base not in seen_ids:
            seen_ids[base] = 1
        else:
            seen_ids[base] += 1
            e["id"] = f"{base}_{seen_ids[base]}"
    return merged


# ───────────────────────── Outputs ─────────────────────────


SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "TAIL Numbers Manifest",
    "description": "wq-102 — binding spec for every public-rendered number on the six priority pages.",
    "type": "object",
    "required": ["version", "generated", "entries"],
    "properties": {
        "version": {"type": "string"},
        "generated": {"type": "string", "format": "date"},
        "scope": {"type": "array", "items": {"type": "string"}},
        "entries": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "id",
                    "page",
                    "anchor_selector",
                    "current_rendered_value",
                    "semantic",
                    "source_state",
                    "editorial_fallback",
                    "supersession_threshold",
                    "format",
                ],
                "properties": {
                    "id": {"type": "string", "pattern": r"^[a-z0-9_]+(\.[a-zA-Z0-9_]+)+$"},
                    "page": {"type": "string"},
                    "pages": {"type": "array", "items": {"type": "string"}},
                    "anchor_selector": {"type": "string"},
                    "anchor_selectors": {"type": "array", "items": {"type": "string"}},
                    "anchor_dom_id": {"type": ["string", "null"]},
                    "current_rendered_value": {"type": "string"},
                    "semantic": {"type": "string"},
                    "source_state": {
                        "type": "string",
                        "enum": ["editorial", "sourced", "computed", "fixed"],
                    },
                    "source_path": {"type": ["string", "null"]},
                    "source_path_exists": {"type": "boolean"},
                    "source_path_candidates": {"type": "array", "items": {"type": "string"}},
                    "editorial_fallback": {
                        "type": "object",
                        "required": ["value", "origin"],
                        "properties": {
                            "value": {"type": ["number", "string"]},
                            "unit": {"type": ["string", "null"]},
                            "raw": {"type": "string"},
                            "origin": {"type": "string"},
                            "audit_ref": {"type": "string"},
                        },
                    },
                    "supersession_threshold": {
                        "type": "object",
                        "required": ["provenance_score_min", "consensus_weight_min"],
                        "properties": {
                            "provenance_score_min": {"type": "number"},
                            "consensus_weight_min": {
                                "type": "string",
                                "enum": ["indicative", "robust"],
                            },
                        },
                    },
                    "format": {
                        "type": "string",
                        "enum": [
                            "currency_b_compact",
                            "currency_m_compact",
                            "currency_t_compact",
                            "currency_unit",
                            "tokens_compact",
                            "percentage_1dp",
                            "ratio_x_to_1",
                            "count_compact",
                            "power_unit",
                            "text_passthrough",
                        ],
                    },
                    "last_changed": {"type": ["string", "null"]},
                    "notion_id": {"type": ["string", "null"]},
                    "_capture": {
                        "type": "object",
                        "properties": {
                            "line": {"type": "integer"},
                            "context": {"type": "string"},
                            "binding_hint": {"type": ["string", "null"]},
                        },
                    },
                },
            },
        },
    },
}


def write_manifest(entries: list[dict], path: Path) -> None:
    payload = {
        "version": "1.0",
        "generated": "2026-05-10",
        "scope": PRIORITY_PAGES,
        "entries": entries,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))


def write_schema(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(SCHEMA, indent=2, ensure_ascii=False))


def write_gap_report(entries: list[dict], raw_rows: list[dict], path: Path) -> None:
    total = len(entries)
    fixed = sum(1 for e in entries if e["source_state"] == "fixed")
    auto_ok = sum(1 for e in entries if e["source_path"])
    intentional_no_path = fixed
    needs_human = sum(
        1 for e in entries if not e["source_path"] and e["source_state"] != "fixed"
    )
    no_candidates = sum(
        1
        for e in entries
        if not e["source_path"] and not e["source_path_candidates"] and e["source_state"] != "fixed"
    )
    # auto-resolution rate: anything we can ship without further human input
    # (source_path filled OR intentionally fixed editorial)
    auto_pct = ((auto_ok + intentional_no_path) / total * 100) if total else 0
    gap_pct = (no_candidates / total * 100) if total else 0

    by_page = defaultdict(list)
    for e in entries:
        by_page[e.get("page")].append(e)

    lines: list[str] = []
    lines.append("# wq-102 — Source-path gap report\n")
    lines.append("Generated 2026-05-10 by `scripts/build_numbers_manifest.py`.\n")
    lines.append("## Summary\n")
    lines.append(f"- Total manifest entries: **{total}**")
    lines.append(f"- Auto-resolved (`source_path` populated): **{auto_ok}**")
    lines.append(f"- Intentionally fixed editorial (no path needed, `source_state=fixed`): **{intentional_no_path}**")
    lines.append(f"- **Auto-resolution rate (path or fixed): {auto_pct:.1f}%** (target ≥40%)")
    lines.append(f"- Needs manual path assignment: **{needs_human}**")
    lines.append(f"- No path candidate at all: **{no_candidates}** ({gap_pct:.1f}%) (target ≤10%)\n")

    lines.append("## Entries needing manual `source_path` assignment\n")
    lines.append(
        "Entries below were extracted but the resolver couldn't pick a unique path. "
        "Where candidates exist, they're listed for human selection; where blank, the value isn't "
        "currently in `site-data.json` / `entities.json` and may need engine extension.\n"
    )
    for page, page_entries in sorted(by_page.items()):
        gap_entries = [
            e for e in page_entries if not e["source_path"] and e["source_state"] != "fixed"
        ]
        if not gap_entries:
            continue
        lines.append(f"### `{page}` — {len(gap_entries)} unresolved\n")
        lines.append("| Line | Raw | Semantic | Anchor | Candidate paths | Context |")
        lines.append("|---|---|---|---|---|---|")
        for e in gap_entries:
            cap = e.get("_capture", {})
            cands = e.get("source_path_candidates") or []
            cands_str = "<br>".join(cands[:3]) if cands else "_(none)_"
            ctx = cap.get("context", "").replace("|", "\\|").replace("\n", " ")[:120]
            lines.append(
                f"| {cap.get('line')} | `{e['current_rendered_value']}` | `{e['semantic']}` | "
                f"{e.get('anchor_dom_id') or '—'} | {cands_str} | {ctx} |"
            )
        lines.append("")

    lines.append("## Intentionally fixed editorial entries (no source_path expected)\n")
    fixed_entries = [e for e in entries if e["source_state"] == "fixed"]
    if fixed_entries:
        lines.append(f"{len(fixed_entries)} entries flagged as `source_state=fixed` "
                     "(tier-mix percentages, methodology constants, regulatory ids, etc.). "
                     "Build skips supersession but routes the literal through the formatter.\n")
        lines.append("| Page | Line | Raw | Semantic | Context |")
        lines.append("|---|---|---|---|---|")
        for e in fixed_entries[:30]:
            cap = e.get("_capture", {})
            ctx = cap.get("context", "").replace("|", "\\|").replace("\n", " ")[:100]
            lines.append(
                f"| {e['page']} | {cap.get('line')} | `{e['current_rendered_value']}` | "
                f"`{e['semantic']}` | {ctx} |"
            )
        if len(fixed_entries) > 30:
            lines.append(f"\n_({len(fixed_entries) - 30} more …)_")
        lines.append("")
    else:
        lines.append("_(none)_\n")

    lines.append("## Notes\n")
    lines.append(
        "- An entry resolved via `<script>` binding mining is marked with `binding_hint` in its "
        "`_capture` block — these were trusted directly and are NOT in the gap list above."
    )
    lines.append(
        "- Cross-page duplicates (same `source_path`, value, format) are collapsed into a single "
        "entry with `pages: [...]`."
    )
    lines.append(
        "- `editorial_fallback.value` is captured verbatim from the HTML at scan time. The "
        "supersession story lives in the gap between this fallback and the resolved live value: "
        "Stage 2 build picks the live value when its provenance clears the threshold, else the fallback."
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


# ───────────────────────── CLI ─────────────────────────


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--beta-dir", default=str(BETA))
    ap.add_argument("--site-data", default=str(ROOT / "site-data.json"))
    ap.add_argument("--entities", default=str(ROOT / "entities.json"))
    ap.add_argument("--overrides", default=str(ROOT / "data" / "consensus_overrides.json"))
    ap.add_argument("--out-manifest", default=str(OUT_MANIFEST))
    ap.add_argument("--out-schema", default=str(OUT_SCHEMA))
    ap.add_argument("--out-gaps", default=str(OUT_GAPS))
    args = ap.parse_args()

    beta = Path(args.beta_dir)
    site_data = json.loads(Path(args.site_data).read_text())
    entities = json.loads(Path(args.entities).read_text())
    overrides = json.loads(Path(args.overrides).read_text())

    print(f"Building value index from site-data.json + entities.json …")
    value_index = build_value_index(site_data, entities, overrides)
    n_paths = sum(len(v) for v in value_index.values())
    print(f"  {len(value_index):,} distinct numeric values, {n_paths:,} (path,value) pairs")

    all_entries: list[dict] = []
    all_raw: list[dict] = []
    for name in PRIORITY_PAGES:
        pp = beta / name
        if not pp.exists():
            print(f"  ! missing {pp}")
            continue
        entries, raw = extract_page_entries(pp, value_index, site_data, entities)
        all_entries.extend(entries)
        all_raw.extend(raw)
        n_resolved = sum(1 for e in entries if e["source_path"])
        print(f"  {name}: {len(entries)} entries, {n_resolved} auto-resolved")

    merged = dedupe_and_disambiguate(all_entries)
    n_total = len(merged)
    n_resolved = sum(1 for e in merged if e["source_path"])
    n_fixed = sum(1 for e in merged if e["source_state"] == "fixed")
    n_no_cand = sum(
        1
        for e in merged
        if not e["source_path"] and not e["source_path_candidates"] and e["source_state"] != "fixed"
    )
    # auto = path-resolved OR intentionally fixed (no human work needed)
    auto_pct = ((n_resolved + n_fixed) / n_total * 100) if n_total else 0
    gap_pct = (n_no_cand / n_total * 100) if n_total else 0
    print()
    print(f"After dedupe: {n_total} entries")
    print(f"  source_path populated: {n_resolved}")
    print(f"  intentionally fixed:   {n_fixed}")
    print(f"  no path & no candidate: {n_no_cand}")
    print()
    print(f"Auto-resolution rate (path OR fixed): {auto_pct:.1f}%  (target ≥ 40%)")
    print(f"No-candidate rate:                    {gap_pct:.1f}%  (target ≤ 10%)")
    print()
    print(f"Stop conditions:")
    print(f"  auto-resolution ≥ 40% → {'OK' if auto_pct >= 40 else 'FAIL'}")
    print(f"  no-candidate ≤ 10%   → {'OK' if gap_pct <= 10 else 'FAIL'}")

    write_manifest(merged, Path(args.out_manifest))
    write_schema(Path(args.out_schema))
    write_gap_report(merged, all_raw, Path(args.out_gaps))
    print()
    print(f"Wrote:")
    print(f"  {args.out_manifest}")
    print(f"  {args.out_schema}")
    print(f"  {args.out_gaps}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
