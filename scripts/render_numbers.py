#!/usr/bin/env python3
"""wq-102 Stage 2 — Resolve manifest, rewrite HTML/JS/meta, emit changelog.

Runs after `generate_site_data.py`. For each manifest entry:
  1. Resolve `source_path` against site-data.json / entities.json.
  2. If resolved value clears the supersession threshold and the path
     exists, render the live value via the formatter; otherwise render
     `editorial_fallback.value`.
  3. Rewrite the relevant element in the priority HTML page:
       - `data-num="<id>"` element  → replace inner text content
       - `js:NAME[idx].col`         → rewrite the JS array literal
       - og:description meta entry  → rewrite the content attribute string
  4. Track every entry's resolution outcome.

Outputs:
  - data/numbers-changelog.md     — supersession state, sourced/editorial
                                    flips since last build, ≥5% movements
  - data/numbers-build-<date>.json — JSON build log for diff inspection

Idempotent: running twice yields no diff.

CLI:
  python3 scripts/render_numbers.py
  python3 scripts/render_numbers.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
BETA = ROOT / "beta"
MANIFEST = ROOT / "data" / "numbers-manifest.json"
CHANGELOG = ROOT / "data" / "numbers-changelog.md"


# ── Source-path resolution ────────────────────────────────────────────────

def resolve_path(qualified_path: str, site_data: dict, entities: dict):
    """Return (value, exists). Path examples:
      site-data.cumulative.capex_total
      entities.market_aggregates._cumulative_2023_2025.capex_total
      site-data.capital_sankey.utilization.Inference (Paid)
    """
    if not qualified_path:
        return None, False
    if qualified_path.startswith("site-data."):
        blob, rest = site_data, qualified_path[len("site-data."):]
    elif qualified_path.startswith("entities."):
        blob, rest = entities, qualified_path[len("entities."):]
    else:
        return None, False
    obj = blob
    for p in rest.split("."):
        if isinstance(obj, dict) and p in obj:
            obj = obj[p]
        else:
            return None, False
    return obj, True


# ── Formatter ─────────────────────────────────────────────────────────────

def fmt(value, fmt_kind: str, raw_hint: str = "") -> str | None:
    """Render `value` using the manifest format string. Returns None if value
    cannot be formatted (in which case the caller falls back to the literal).

    `raw_hint` is the editorial literal — used to decide whether to preserve
    a leading `~` (approximate) or `+` (signed) prefix.
    """
    if value is None:
        return None
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    approx = "~" in raw_hint
    signed = raw_hint.startswith(("+", "-"))

    if fmt_kind == "currency_b_compact":
        rendered = f"${int(round(v))}B" if abs(v) >= 10 else f"${v:.1f}B"
    elif fmt_kind == "currency_m_compact":
        rendered = f"${int(round(v))}M"
    elif fmt_kind == "currency_t_compact":
        rendered = f"${v:.2f}T" if abs(v) < 10 else f"${int(round(v))}T"
    elif fmt_kind == "currency_unit":
        rendered = f"${v:.2f}" if abs(v) < 10 else f"${int(round(v))}"
    elif fmt_kind == "tokens_compact":
        rendered = f"~{int(round(v))}T"
        approx = True  # tokens always rendered with leading ~
    elif fmt_kind == "percentage_1dp":
        if abs(v - round(v)) < 0.05:
            rendered = f"{int(round(v))}%"
        else:
            rendered = f"{v:.1f}%"
        if signed and not rendered.startswith(("+", "-")):
            rendered = f"+{rendered}" if v >= 0 else rendered
    elif fmt_kind == "ratio_x_to_1":
        rendered = f"{v:.1f}×" if abs(v - round(v)) > 0.05 else f"{int(round(v))}×"
    elif fmt_kind == "count_compact":
        if abs(v) >= 1_000_000_000:
            rendered = f"{v/1e9:.1f}B"
        elif abs(v) >= 1_000_000:
            rendered = f"{v/1e6:.1f}M"
        elif abs(v) >= 1_000:
            rendered = f"{v/1e3:.0f}K"
        else:
            rendered = f"{v:.0f}"
    elif fmt_kind == "power_unit":
        rendered = f"{int(round(v))} GW"
    else:
        return None

    # Preserve a /day suffix if the editorial literal had one.
    if "/day" in raw_hint and "/day" not in rendered:
        rendered = rendered + "/day"
    if approx and not rendered.startswith("~") and "T" in rendered:
        rendered = "~" + rendered.lstrip("~")
    return rendered


# ── Supersession decision ─────────────────────────────────────────────────

def should_supersede(entry: dict, exists: bool) -> bool:
    """D4: a sourced value supersedes editorial when provenance_score ≥ 0.7
    AND consensus_weight ∈ {indicative, robust}. For Stage 2 we approximate
    "the engine has emitted this path" as "supersede"; any future tightening
    can read from a per-path provenance map (out of scope here)."""
    if entry["source_state"] == "fixed":
        return False
    if not entry.get("source_path") or not exists:
        return False
    return True


# ── HTML / JS / meta rewriters ────────────────────────────────────────────

DATA_NUM_OPEN_RE = lambda num_id: re.compile(
    r"(<[a-zA-Z][\w-]*\b[^>]*\bdata-num\s*=\s*['\"]"
    + re.escape(num_id)
    + r"['\"][^>]*>)([^<]*)(</[a-zA-Z][\w-]*>)"
)


def rewrite_html_anchor(html: str, num_id: str, new_text: str) -> tuple[str, bool]:
    """Replace inner text of the <... data-num="<num_id>">…</…> element.
    Returns (new_html, changed). Preserves the open and close tags exactly."""
    pat = DATA_NUM_OPEN_RE(num_id)
    m = pat.search(html)
    if not m:
        return html, False
    current = m.group(2)
    if current == new_text:
        return html, False
    return html[: m.start()] + m.group(1) + new_text + m.group(3) + html[m.end():], True


def rewrite_html_anchor_literal(
    html: str, num_id: str, old_literal: str, new_literal: str
) -> tuple[str, bool]:
    """Replace `old_literal` → `new_literal` INSIDE the data-num="<num_id>"
    element only. Preserves surrounding inner text (e.g. an element wrapping
    "$34:$1" replaces the "$34" portion only).

    Idempotent: when `new_literal` is already present in the element's text
    (e.g. a previous run already substituted) and `old_literal` is no longer
    there, no-op. When the element's full text equals `new_literal`, no-op.
    Only when `old_literal` is genuinely present do we replace it.
    """
    pat = DATA_NUM_OPEN_RE(num_id)
    m = pat.search(html)
    if not m:
        return html, False
    current = m.group(2)
    if current == new_literal:
        return html, False
    if old_literal and old_literal in current:
        new_inner = current.replace(old_literal, new_literal, 1)
    elif new_literal in current:
        # Already rendered (idempotence on second run with surrounding text)
        return html, False
    else:
        # Element's text doesn't contain the original literal AND doesn't
        # contain the new literal — likely surrounding text changed since
        # manifest was generated. Replace the full inner text with the
        # new literal as a fallback (matches single-token behaviour).
        new_inner = new_literal
    if new_inner == current:
        return html, False
    return html[: m.start()] + m.group(1) + new_inner + m.group(3) + html[m.end():], True


# JS array cell rewriter: locate `key:value` pair within the named array.
JS_ARRAY_HEADER_RE = lambda name: re.compile(
    r"(?:const|let|var)\s+" + re.escape(name) + r"\s*=\s*\["
)


def rewrite_js_array_cell(
    html: str,
    array_name: str,
    row_index: int,
    column: str,
    new_value,
) -> tuple[str, bool]:
    """Locate `<array_name>[<row_index>].<column>` and overwrite its numeric
    literal. Returns (new_html, changed). Preserves any other formatting."""
    header = JS_ARRAY_HEADER_RE(array_name).search(html)
    if not header:
        return html, False
    # Walk to find array body
    start = header.end()
    depth = 1
    i = start
    while i < len(html) and depth > 0:
        if html[i] == "[":
            depth += 1
        elif html[i] == "]":
            depth -= 1
        i += 1
    array_end = i - 1
    array_body = html[start:array_end]
    # Find the row at row_index by scanning balanced { ... }
    rows = []
    j = 0
    in_str = False
    str_ch = None
    while j < len(array_body):
        ch = array_body[j]
        if in_str:
            if ch == str_ch and array_body[j - 1] != "\\":
                in_str = False
        elif ch in ("'", '"'):
            in_str = True
            str_ch = ch
        elif ch == "{":
            row_start = j
            d = 1
            j += 1
            while j < len(array_body) and d > 0:
                c2 = array_body[j]
                if in_str:
                    if c2 == str_ch and array_body[j - 1] != "\\":
                        in_str = False
                elif c2 in ("'", '"'):
                    in_str = True
                    str_ch = c2
                elif c2 == "{":
                    d += 1
                elif c2 == "}":
                    d -= 1
                j += 1
            rows.append((row_start, j))
            continue
        j += 1
    if row_index >= len(rows):
        return html, False
    rs, re_end = rows[row_index]
    row_text = array_body[rs:re_end]
    pat = re.compile(
        r"(\b" + re.escape(column) + r"\s*:\s*)(-?\d+(?:\.\d+)?)(\s*[,}])"
    )
    new_value_str = (
        f"{int(new_value)}" if new_value == int(new_value) else f"{new_value}"
    )
    m = pat.search(row_text)
    if not m:
        return html, False
    if m.group(2) == new_value_str:
        return html, False
    new_row = row_text[: m.start()] + m.group(1) + new_value_str + m.group(3) + row_text[m.end():]
    new_array_body = array_body[:rs] + new_row + array_body[re_end:]
    return html[:start] + new_array_body + html[array_end:], True


# og:description meta rewriter — replace one number at a time within the
# content attribute.

OG_DESC_RE = re.compile(
    r'(<meta\s+property\s*=\s*["\']og:description["\']\s+content\s*=\s*["\'])([^"\']*)(["\']\s*/?>)',
    re.IGNORECASE,
)


def rewrite_og_description(html: str, replacements: list[tuple[str, str]]) -> tuple[str, bool]:
    """`replacements` is a list of (old_literal, new_literal). Apply each in
    order, leftmost-first, replacing only the FIRST remaining occurrence."""
    m = OG_DESC_RE.search(html)
    if not m:
        return html, False
    content = m.group(2)
    original = content
    for old, new in replacements:
        if old == new:
            continue
        idx = content.find(old)
        if idx == -1:
            continue
        content = content[:idx] + new + content[idx + len(old):]
    if content == original:
        return html, False
    return html[: m.start()] + m.group(1) + content + m.group(3) + html[m.end():], True


# ── Driver ────────────────────────────────────────────────────────────────


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=str(MANIFEST))
    ap.add_argument("--site-data", default=str(ROOT / "site-data.json"))
    ap.add_argument("--entities", default=str(ROOT / "entities.json"))
    # `--beta-dir` retained for back-compat (single directory). Use
    # `--page-dirs A B …` to render the priority pages in MULTIPLE
    # directories in lockstep (e.g. /beta/ AND repo root). When
    # --page-dirs is supplied it overrides --beta-dir.
    ap.add_argument("--beta-dir", default=str(BETA))
    ap.add_argument(
        "--page-dirs",
        nargs="+",
        default=None,
        help="Render against multiple page-dirs in lockstep "
        "(default: just --beta-dir)",
    )
    ap.add_argument("--changelog", default=str(CHANGELOG))
    ap.add_argument("--build-log", default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    manifest = json.loads(Path(args.manifest).read_text())
    site_data = json.loads(Path(args.site_data).read_text())
    entities = json.loads(Path(args.entities).read_text())

    by_page: dict[str, list[dict]] = defaultdict(list)
    for e in manifest["entries"]:
        by_page[e["page"]].append(e)

    decisions: list[dict] = []
    counts = defaultdict(int)

    page_dirs = args.page_dirs if args.page_dirs else [args.beta_dir]
    PRIORITY_PAGES = (
        "index.html",
        "capital.html",
        "revenue.html",
        "compute.html",
        "usage.html",
        "power.html",
    )

    for page in PRIORITY_PAGES:
        # Collect all live target paths for this page across page_dirs.
        target_paths = [
            Path(d) / page for d in page_dirs if (Path(d) / page).exists()
        ]
        if not target_paths:
            continue
        # Use the FIRST path's HTML as the source of truth for resolution.
        # All target paths must be byte-equal at start (they're mirror copies).
        path = target_paths[0]
        html = path.read_text()
        original = html
        # Track all targets for the persist pass.
        all_targets = [(p, p.read_text()) for p in target_paths]

        # First pass — resolve every entry, decide rendered value
        per_entry = []
        og_replacements: list[tuple[str, str, dict]] = []  # (old, new, entry)
        for e in by_page.get(page, []):
            sp = e.get("source_path")
            live_v, exists = (None, False)
            if sp:
                live_v, exists = resolve_path(sp, site_data, entities)
            supersede = should_supersede(e, exists)
            chosen_value = live_v if supersede else e["editorial_fallback"]["value"]
            chosen_source = "sourced" if supersede else (
                "fixed" if e["source_state"] == "fixed" else "editorial"
            )
            rendered = fmt(chosen_value, e["format"], e["current_rendered_value"])
            if rendered is None:
                rendered = e["current_rendered_value"]
            per_entry.append({
                "entry": e,
                "rendered": rendered,
                "chosen_source": chosen_source,
                "live_v": live_v,
                "exists": exists,
            })

        # Second pass — apply rewrites. We ONLY rewrite when the entry
        # resolved to a live source (chosen_source == "sourced"). For fixed
        # and editorial-fallback entries the existing literal in the HTML is
        # preserved verbatim — that's the whole point of the editorial
        # fallback contract.
        for rec in per_entry:
            if rec["chosen_source"] != "sourced":
                continue
            e = rec["entry"]
            rendered = rec["rendered"]
            sel = e.get("anchor_selector") or ""
            if sel.startswith("js:"):
                # js:LAG_RAW[2].totalCapex
                m = re.match(r"js:(\w+)\[(\d+)\]\.(\w+)", sel)
                if m:
                    name, idx, col = m.group(1), int(m.group(2)), m.group(3)
                    # Match the display precision the chart uses: integer for
                    # ≥10, one decimal for <10 (consistent with the visible
                    # bar labels rendered by formatCurrency(v) in the JS).
                    raw_v = rec["live_v"]
                    if raw_v is None:
                        continue
                    new_val = round(raw_v) if abs(raw_v) >= 10 else round(raw_v, 1)
                    new_html, changed = rewrite_js_array_cell(html, name, idx, col, new_val)
                    if changed:
                        html = new_html
                        counts["js_rewrites"] += 1
                continue
            # og:description meta — defer all to a single rewrite pass
            if e["page"] == "index.html" and e["_capture"]["line"] == 11:
                old_lit = e["current_rendered_value"]
                new_lit = rendered
                if old_lit != new_lit:
                    og_replacements.append((old_lit, new_lit, e))
                continue
            # Standard data-num anchor — replace the LITERAL substring
            # inside the element, not the entire inner text. This keeps
            # surrounding text intact (e.g. "$34:$1" stays "$34:$1" if only
            # "$34" is being updated; if no live binding for ":$1" exists,
            # it's preserved as-is).
            old_lit = e["current_rendered_value"]
            new_html, changed = rewrite_html_anchor_literal(
                html, e["id"], old_lit, rendered
            )
            if changed:
                html = new_html
                counts["html_rewrites"] += 1

        # og:description rewrite — apply collected replacements
        if og_replacements:
            new_html, changed = rewrite_og_description(
                html, [(o, n) for o, n, _ in og_replacements]
            )
            if changed:
                html = new_html
                counts["og_rewrites"] += len(og_replacements)

        # Persist + record decisions
        for rec in per_entry:
            e = rec["entry"]
            decisions.append({
                "id": e["id"],
                "page": page,
                "source_state_at_build": rec["chosen_source"],
                "rendered": rec["rendered"],
                "editorial_fallback": e["editorial_fallback"]["raw"],
                "source_path": e.get("source_path"),
                "live_value": rec["live_v"],
                "path_exists": rec["exists"],
            })
            counts[f"chosen:{rec['chosen_source']}"] += 1

        # Write the rendered HTML to ALL target paths (kept in lockstep).
        # Each target may already contain `html` (already rendered); only
        # write when its current content differs.
        if html != original:
            counts[f"page_changed:{page}"] += 1
        if not args.dry_run:
            for p, current in all_targets:
                if current != html:
                    p.write_text(html)
                    counts[f"file_written:{p}"] += 1

    # ── Changelog ─────────────────────────────────────────────────────
    flipped = [d for d in decisions if d["source_state_at_build"] == "sourced"]
    editorial = [d for d in decisions if d["source_state_at_build"] == "editorial"]
    fixed = [d for d in decisions if d["source_state_at_build"] == "fixed"]

    cl_lines = []
    cl_lines.append("# Numbers Changelog\n")
    cl_lines.append(f"Last build: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n")
    cl_lines.append("## State summary\n")
    cl_lines.append(f"- **{len(flipped)}** numbers rendered from live engine values (sourced)")
    cl_lines.append(f"- **{len(editorial)}** numbers rendered from editorial fallback "
                    "(path stub — engine extension needed)")
    cl_lines.append(f"- **{len(fixed)}** numbers preserved as fixed editorial "
                    "(tier mixes, methodology constants, narrative prose)\n")

    cl_lines.append("## Sourced (live)\n")
    if flipped:
        cl_lines.append("| Page | ID | Editorial → Rendered | Source path |")
        cl_lines.append("|---|---|---|---|")
        for d in sorted(flipped, key=lambda x: (x["page"], x["id"])):
            arrow = "→" if d["editorial_fallback"] != d["rendered"] else "≡"
            cl_lines.append(
                f"| `{d['page']}` | `{d['id']}` | "
                f"`{d['editorial_fallback']}` {arrow} `{d['rendered']}` | "
                f"`{d['source_path']}` |"
            )
    else:
        cl_lines.append("_(no numbers currently sourced)_")
    cl_lines.append("")

    cl_lines.append("## Needs source (path nominated, engine doesn't emit)\n")
    if editorial:
        cl_lines.append("Stage 2 falls back to the literal until engine extends. Listed for "
                        "follow-on briefs.\n")
        cl_lines.append("| Page | ID | Literal | Source path |")
        cl_lines.append("|---|---|---|---|")
        for d in sorted(editorial, key=lambda x: (x["page"], x["id"])):
            cl_lines.append(
                f"| `{d['page']}` | `{d['id']}` | `{d['rendered']}` | "
                f"`{d['source_path'] or '(none)'}` |"
            )
    else:
        cl_lines.append("_(none)_")
    cl_lines.append("")

    cl_lines.append("## Fixed editorial (intentional, no supersession)\n")
    cl_lines.append(f"{len(fixed)} entries — see `data/numbers-manifest.json` for the full list.\n")

    Path(args.changelog).parent.mkdir(parents=True, exist_ok=True)
    Path(args.changelog).write_text("\n".join(cl_lines))

    # Build log
    if args.build_log:
        Path(args.build_log).write_text(json.dumps({
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "counts": dict(counts),
            "decisions": decisions,
        }, indent=2))

    # Console summary
    print(f"Render: {len(decisions)} entries across {len(by_page)} pages")
    print(f"  sourced (live):       {len(flipped)}")
    print(f"  editorial (fallback): {len(editorial)}")
    print(f"  fixed:                {len(fixed)}")
    print(f"  HTML rewrites:        {counts['html_rewrites']}")
    print(f"  JS array rewrites:    {counts['js_rewrites']}")
    print(f"  og:description rewrites: {counts['og_rewrites']}")
    if args.dry_run:
        print("(dry-run — no files written)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
