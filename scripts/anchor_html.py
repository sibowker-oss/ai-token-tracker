#!/usr/bin/env python3
"""wq-102 Stage 2 — Install `data-num` anchors in the priority HTML pages.

Reads `data/numbers-manifest.json` and edits each priority HTML file in place
to attach a `data-num="<id>"` attribute to every catalogued number's enclosing
element. The literal value is preserved as the editorial fallback.

Strategies (in priority order):
  1. JS-array entries (anchor_selector starts with `js:`)        → SKIP, render
                                                                    script handles
  2. og:description meta entries (page=index.html, line=11)      → SKIP, render
                                                                    script rewrites
                                                                    the content attr
                                                                    via per-token map
  3. Entry with `anchor_dom_id` set (id="card-capex" etc.)       → ADD data-num=
                                                                    to that element
  4. Token sits inside `<span data-narrative="...">…</span>`     → ADD data-num=
                                                                    to that span
  5. Otherwise                                                   → WRAP literal in
                                                                    `<span data-num=
                                                                    "<id>">…</span>`

Idempotent: running twice produces no diff (skips elements already carrying
the same `data-num` value).

CLI:
  python3 scripts/anchor_html.py
  python3 scripts/anchor_html.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
BETA = ROOT / "beta"
MANIFEST = ROOT / "data" / "numbers-manifest.json"


# ── Element locators ──────────────────────────────────────────────────────

# Open-tag pattern that captures attributes; we only operate on tags that
# already exist. We never re-balance arbitrary HTML.
TAG_OPEN_BY_ID = lambda dom_id: re.compile(
    r"(<[a-zA-Z][\w-]*\b[^>]*\bid\s*=\s*['\"]"
    + re.escape(dom_id)
    + r"['\"][^>]*)>"
)


def _has_data_num(tag_open: str, expected_id: str) -> bool:
    m = re.search(r"\bdata-num\s*=\s*['\"]([\w\-\.]+)['\"]", tag_open)
    return m is not None and m.group(1) == expected_id


def _add_data_num_to_tag(tag_open: str, num_id: str) -> str:
    # If already carries the SAME data-num, no-op. Different data-num →
    # leave as-is too (don't clobber an existing claim).
    if re.search(r"\bdata-num\s*=", tag_open):
        return tag_open
    # Insert before the closing > (preserving any self-closing slash).
    return tag_open + f' data-num="{num_id}"'


def install_anchor_on_id(html: str, dom_id: str, num_id: str) -> tuple[str, bool]:
    """Add `data-num="<num_id>"` to the open tag of the element whose id matches.
    Returns (new_html, changed)."""
    pat = re.compile(
        r"(<[a-zA-Z][\w-]*\b)([^>]*\bid\s*=\s*['\"]"
        + re.escape(dom_id)
        + r"['\"][^>]*)>",
    )
    matches = list(pat.finditer(html))
    if not matches:
        return html, False
    m = matches[0]
    open_tag = m.group(0)  # full "<tagname ...>"
    if _has_data_num(open_tag, num_id):
        return html, False
    new_open = _add_data_num_to_tag(open_tag.rstrip(">"), num_id) + ">"
    return html[: m.start()] + new_open + html[m.end():], True


# Match the OPENING <span data-narrative="..."> tag at a given line+col window.
# We pick the narrative span whose open tag sits on the same line and whose
# closing </span> appears after the token's column.
NARRATIVE_OPEN_RE = re.compile(
    r"<span([^>]*\bdata-narrative\s*=\s*['\"][\w_\.]+['\"][^>]*)>"
)


def install_anchor_on_narrative_span(
    line: str, token_col: int, num_id: str
) -> tuple[str, bool]:
    """Within a single line, find the <span data-narrative="..."> that wraps
    the token at `token_col` and add data-num to it.
    Returns (new_line, changed)."""
    candidates = []
    for m in NARRATIVE_OPEN_RE.finditer(line):
        if m.end() <= token_col:
            candidates.append(m)
    if not candidates:
        return line, False
    open_match = candidates[-1]
    close_idx = line.find("</span>", open_match.end())
    if close_idx == -1 or close_idx < token_col:
        return line, False
    open_tag = open_match.group(0)
    if _has_data_num(open_tag, num_id):
        return line, False
    new_open = _add_data_num_to_tag(open_tag.rstrip(">"), num_id) + ">"
    return line[: open_match.start()] + new_open + line[open_match.end():], True


def wrap_literal_with_anchor(
    line: str, col_start: int, col_end: int, num_id: str, expected_literal: str
) -> tuple[str, bool]:
    """Wrap `line[col_start:col_end]` in <span data-num="<id>">…</span>.

    Idempotence: if the line already contains `data-num="<num_id>"` anywhere,
    skip. This protects against re-runs after anchors have shifted line
    offsets — the anchor is already installed for this id, just at a
    different column than the manifest recorded.
    """
    if col_end <= col_start or col_end > len(line):
        return line, False
    # Already anchored on this line? — skip.
    if f'data-num="{num_id}"' in line:
        return line, False
    literal = line[col_start:col_end]
    # Stale offsets: if the literal at the recorded span doesn't match the
    # expected text, the line was modified by a prior run. Bail out.
    if literal != expected_literal:
        return line, False
    wrapper = f'<span data-num="{num_id}">{literal}</span>'
    return line[:col_start] + wrapper + line[col_end:], True


# ── Driver ────────────────────────────────────────────────────────────────


def is_skippable(entry: dict) -> str | None:
    """Return reason to skip this entry, or None to anchor it."""
    sel = entry.get("anchor_selector") or ""
    if sel.startswith("js:"):
        return "js_array"
    # og:description meta tag — handled separately by render script
    if (
        entry.get("page") == "index.html"
        and entry.get("_capture", {}).get("line") == 11
    ):
        return "og_description"
    return None


def anchor_page(page_path: Path, entries: list[dict], dry_run: bool = False) -> dict:
    """Install anchors on a single page file. Returns a stats dict."""
    text = page_path.read_text()
    lines = text.split("\n")
    stats = {
        "page": page_path.name,
        "anchored_via_id": 0,
        "anchored_via_narrative": 0,
        "anchored_via_wrap": 0,
        "skipped_js": 0,
        "skipped_og": 0,
        "no_change": 0,
        "errors": [],
    }

    # Bucket: which DOM ids appear on more than one manifest entry? Those
    # entries can't all be anchored by id (you can only set one data-num
    # attribute per element); fall through to per-token wrapping for all
    # but the first entry sharing the same id.
    domid_counts: dict[str, int] = defaultdict(int)
    for e in entries:
        if is_skippable(e) is None and e.get("anchor_dom_id"):
            domid_counts[e["anchor_dom_id"]] += 1

    # Group entries by line, then process each line's entries in REVERSE
    # column order so that wrapping later tokens doesn't shift earlier
    # tokens' columns.
    by_line: dict[int, list[dict]] = defaultdict(list)
    by_dom_id: list[dict] = []
    seen_domids: set[str] = set()
    for e in entries:
        why = is_skippable(e)
        if why == "js_array":
            stats["skipped_js"] += 1
            continue
        if why == "og_description":
            stats["skipped_og"] += 1
            continue
        anchor_id = e.get("anchor_dom_id")
        # Single-occupant DOM id → anchor via id attribute on the parent
        # element. Shared DOM ids → none get a parent anchor; ALL fall
        # through to per-token wrapping so the parent element's other text
        # ("$34:$1" stays $34 + `:$1`) is preserved when render rewrites.
        if anchor_id and domid_counts[anchor_id] == 1:
            by_dom_id.append(e)
            continue
        cap = e.get("_capture", {})
        ln = cap.get("line")
        if ln is None:
            stats["errors"].append(f"missing line for {e['id']}")
            continue
        by_line[ln].append(e)

    # 1) DOM-id-based anchors (no positional sensitivity)
    for e in by_dom_id:
        new_text, changed = install_anchor_on_id(text, e["anchor_dom_id"], e["id"])
        if changed:
            text = new_text
            lines = text.split("\n")
            stats["anchored_via_id"] += 1
        else:
            stats["no_change"] += 1

    # 2) Per-line anchors: narrative-wrap or literal-wrap, in reverse col order
    for ln_no, line_entries in by_line.items():
        if ln_no - 1 >= len(lines):
            stats["errors"].append(f"line {ln_no} out of range")
            continue
        line = lines[ln_no - 1]
        # Sort entries on the line by column DESCENDING so we edit from the
        # right; col offsets of earlier tokens don't shift.
        line_entries.sort(
            key=lambda e: (e["_capture"].get("col") or 0),
            reverse=True,
        )
        for e in line_entries:
            cap = e["_capture"]
            col = cap.get("col") or 0
            col_end = cap.get("col_end") or (col + len(e["current_rendered_value"]))
            # Try narrative-span anchor first
            new_line, changed = install_anchor_on_narrative_span(line, col, e["id"])
            if changed:
                line = new_line
                stats["anchored_via_narrative"] += 1
                continue
            # Fall back to wrap
            new_line, changed = wrap_literal_with_anchor(
                line, col, col_end, e["id"], e["current_rendered_value"]
            )
            if changed:
                line = new_line
                stats["anchored_via_wrap"] += 1
            else:
                stats["no_change"] += 1
        lines[ln_no - 1] = line

    new_text = "\n".join(lines)
    if not dry_run and new_text != page_path.read_text():
        page_path.write_text(new_text)
    return stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=str(MANIFEST))
    ap.add_argument("--beta-dir", default=str(BETA))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    manifest = json.loads(Path(args.manifest).read_text())
    by_page: dict[str, list[dict]] = defaultdict(list)
    for e in manifest["entries"]:
        by_page[e["page"]].append(e)

    overall = []
    for page in (
        "index.html",
        "capital.html",
        "revenue.html",
        "compute.html",
        "usage.html",
        "power.html",
    ):
        path = Path(args.beta_dir) / page
        if not path.exists():
            print(f"  ! missing {path}")
            continue
        stats = anchor_page(path, by_page.get(page, []), dry_run=args.dry_run)
        overall.append(stats)
        print(
            f"  {page:>14}: id={stats['anchored_via_id']:>3} "
            f"narr={stats['anchored_via_narrative']:>3} "
            f"wrap={stats['anchored_via_wrap']:>3} "
            f"skip_js={stats['skipped_js']:>3} "
            f"skip_og={stats['skipped_og']:>2} "
            f"nc={stats['no_change']:>3}"
            + (f"  {len(stats['errors'])} ERR" if stats["errors"] else "")
        )
        for err in stats["errors"]:
            print(f"      ! {err}")

    if args.dry_run:
        print("\n(dry-run — no files written)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
