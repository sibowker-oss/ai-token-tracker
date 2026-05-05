#!/usr/bin/env python3
"""build_briefs_index.py — wq-088 §"Files touched"/Implementation §4.

Generates data/briefs-index.json from briefs/active/ + briefs/completed/.
The Briefs admin page (/briefs.html) renders this file client-side, so the
index is the contract — what's on disk shows up in the admin UI on next load.

Per-brief shape:
  {
    "id":          "wq-088",                    # null if filename has no leading wq-NNN
    "filename":    "2026-05-06-wq-088-…md",     # relative path inside briefs/<status>/
    "path":        "briefs/active/2026-05-06-wq-088-…md",  # repo-relative
    "title":       "Command Centre / Admin nav cleanup",  # from H1, falls back to slug
    "status":      "active" | "completed",
    "date":        "2026-05-06",                 # filename date (or git first-commit fallback)
    "shipped":     "2026-05-06"  | null,         # parsed from "Shipped: <date>" footer
    "shipped_commit": "abc1234"  | null,
    "frontmatter": { "id": "wq-088", "stage": "Scoped", … } | {}  # any YAML at top
  }

Run:
  python3 scripts/build_briefs_index.py            # writes data/briefs-index.json
  python3 scripts/build_briefs_index.py --check    # exits non-zero if regen would change output

Filename convention (briefs/README.md): YYYY-MM-DD-short-name.md. Legacy files
without a leading date fall back to the file's earliest git-commit date so
the Briefs page still has something sortable.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ACTIVE_DIR = REPO / "briefs" / "active"
COMPLETED_DIR = REPO / "briefs" / "completed"
OUT = REPO / "data" / "briefs-index.json"

DATE_PREFIX_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)\.md$")
WQ_RE = re.compile(r"\b(wq-\d{2,4})\b", re.IGNORECASE)
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
SHIPPED_RE = re.compile(r"Shipped:\s*(\d{4}-\d{2}-\d{2})(?:[,;]\s*commit\s+([0-9a-fA-F]{7,40}))?", re.IGNORECASE)
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_simple_yaml(block: str) -> dict:
    """Tiny YAML reader for `key: value` lines — enough for brief frontmatter.
    No deps; we don't need full YAML."""
    out: dict[str, str] = {}
    for line in block.splitlines():
        line = line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        out[key.strip()] = val.strip().strip('"').strip("'")
    return out


def first_commit_date(path: Path) -> str | None:
    try:
        res = subprocess.run(
            ["git", "log", "--diff-filter=A", "--follow", "--format=%aI", "--", str(path.relative_to(REPO))],
            cwd=REPO, capture_output=True, text=True, check=False,
        )
        out = res.stdout.strip().splitlines()
        if not out:
            return None
        first = out[-1]  # earliest add commit (last line because git log default reverse)
        return first.split("T")[0]
    except Exception:
        return None


def build_entry(path: Path, status: str) -> dict:
    text = path.read_text(encoding="utf-8")
    frontmatter: dict[str, str] = {}
    fm_match = FRONTMATTER_RE.match(text)
    body = text
    if fm_match:
        frontmatter = parse_simple_yaml(fm_match.group(1))
        body = text[fm_match.end():]

    title = frontmatter.get("title")
    if not title:
        h1 = H1_RE.search(body)
        if h1:
            title = h1.group(1).strip()
    if not title:
        title = path.stem

    fname = path.name
    m = DATE_PREFIX_RE.match(fname)
    if m:
        date = m.group(1)
    else:
        date = first_commit_date(path) or "0000-00-00"

    wq_match = WQ_RE.search(fname) or WQ_RE.search(title)
    wq_id = wq_match.group(1).lower() if wq_match else (frontmatter.get("id") or None)

    shipped_date = None
    shipped_commit = None
    sm = SHIPPED_RE.search(text)
    if sm:
        shipped_date = sm.group(1)
        shipped_commit = sm.group(2) or None

    return {
        "id": wq_id,
        "filename": fname,
        "path": str(path.relative_to(REPO)).replace("\\", "/"),
        "title": title,
        "status": status,
        "date": date,
        "shipped": shipped_date,
        "shipped_commit": shipped_commit,
        "frontmatter": frontmatter,
    }


def collect() -> list[dict]:
    entries: list[dict] = []
    for d, status in ((ACTIVE_DIR, "active"), (COMPLETED_DIR, "completed")):
        if not d.exists():
            continue
        for p in sorted(d.glob("*.md")):
            entries.append(build_entry(p, status))
    # Newest first by date, then by filename
    entries.sort(key=lambda e: (e["date"], e["filename"]), reverse=True)
    return entries


def write(payload: dict, dry: bool = False) -> bool:
    """Returns True if file was written / would change."""
    serialized = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if OUT.exists() and OUT.read_text(encoding="utf-8") == serialized:
        return False
    if not dry:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(serialized, encoding="utf-8")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="Exit 1 if writing would change output (CI use).")
    args = ap.parse_args()

    entries = collect()
    payload = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "active_count": sum(1 for e in entries if e["status"] == "active"),
        "completed_count": sum(1 for e in entries if e["status"] == "completed"),
        "entries": entries,
    }

    if args.check:
        # Compare excluding the generated_at field, which always changes.
        if OUT.exists():
            try:
                prev = json.loads(OUT.read_text(encoding="utf-8"))
                prev.pop("generated_at", None)
                cur = dict(payload)
                cur.pop("generated_at", None)
                if prev == cur:
                    print(f"OK — {OUT.relative_to(REPO)} is up-to-date ({len(entries)} briefs).")
                    return 0
            except Exception:
                pass
        print(f"DIFF — {OUT.relative_to(REPO)} would change. Run scripts/build_briefs_index.py.", file=sys.stderr)
        return 1

    changed = write(payload)
    msg = "wrote" if changed else "unchanged"
    print(f"{msg} {OUT.relative_to(REPO)} ({len(entries)} briefs: {payload['active_count']} active, {payload['completed_count']} completed).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
