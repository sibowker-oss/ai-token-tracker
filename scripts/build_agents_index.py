#!/usr/bin/env python3
"""build_agents_index.py — wq-088 §"Files touched"/Implementation §5.

Generates data/agents-index.json from:
  1. data/agents.registry.md — the canonical pipe-table of agents that write
     to site-data.json (per GUIDELINES §6.3).
  2. scripts/*.py — every Python script in the pipeline, with a one-line
     purpose pulled from its module docstring.

The Agents admin page (/agents.html) renders this file client-side. Repo
state is the contract — this script just normalises it for the UI.

Run:
  python3 scripts/build_agents_index.py
  python3 scripts/build_agents_index.py --check
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REGISTRY_MD = REPO / "data" / "agents.registry.md"
SCRIPTS_DIR = REPO / "scripts"
OUT = REPO / "data" / "agents-index.json"

# Group scripts by filename prefix (kept short — readers can extend).
GROUP_RULES: list[tuple[str, str]] = [
    ("apply_",       "apply"),
    ("audit_",       "audit"),
    ("backfill_",    "backfill"),
    ("build_",       "build"),
    ("classify_",    "classify"),
    ("derive_",      "derive"),
    ("enrich",       "enrich"),
    ("extract_",     "extract"),
    ("monitor_",     "monitor"),
    ("scan_",        "scan"),
    ("scrape_",      "scrape"),
    ("validate_",    "validate"),
    ("validate-",    "validate"),
    ("news_",        "news"),
    ("newsletter",   "newsletter"),
    ("triangulate",  "triangulate"),
    ("anthropic_",   "anthropic"),
]


def parse_registry(md: str) -> list[dict]:
    """Pull the registry pipe-table out of the markdown.
    Returns a list of dicts keyed by header column. The registry file has a
    Columns-description table earlier; we want the one whose first header
    is exactly `name` (case-insensitive), per agents.registry.md §Registry."""
    lines = md.splitlines()
    for i, line in enumerate(lines):
        if not line.lstrip().startswith("|"):
            continue
        if i + 1 >= len(lines) or not re.match(r"^\s*\|[\s\-\|:]+\|\s*$", lines[i + 1]):
            continue
        headers = [h.strip() for h in line.strip().strip("|").split("|")]
        if not headers or headers[0].lower() != "name":
            continue
        rows: list[dict] = []
        for body in lines[i + 2:]:
            if not body.strip().startswith("|"):
                break
            if re.match(r"^\s*\|[\s\-\|:]+\|\s*$", body):
                continue
            cells = [c.strip() for c in body.strip().strip("|").split("|")]
            if len(cells) < len(headers):
                cells.extend([""] * (len(headers) - len(cells)))
            rows.append(dict(zip(headers, cells[:len(headers)])))
        return rows
    return []


def script_purpose(path: Path) -> str:
    """Return the first non-empty line of the module docstring, or empty string."""
    try:
        src = path.read_text(encoding="utf-8")
    except Exception:
        return ""
    try:
        mod = ast.parse(src)
    except SyntaxError:
        return ""
    doc = ast.get_docstring(mod) or ""
    for line in doc.splitlines():
        line = line.strip()
        if line:
            # If it starts with "<filename> — …", strip the redundant prefix.
            m = re.match(r"^[\w\.\-]+\.py\s*[—\-:]\s*(.+)$", line)
            return m.group(1) if m else line
    return ""


def group_for(name: str) -> str:
    for prefix, group in GROUP_RULES:
        if name.startswith(prefix):
            return group
    return "other"


def collect_scripts() -> list[dict]:
    out: list[dict] = []
    for p in sorted(SCRIPTS_DIR.glob("*.py")):
        if p.name == "__init__.py" or p.name.startswith("_"):
            continue
        out.append({
            "name": p.name,
            "path": str(p.relative_to(REPO)).replace("\\", "/"),
            "purpose": script_purpose(p),
            "group": group_for(p.name),
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="Exit 1 if the file would change.")
    args = ap.parse_args()

    registry_rows: list[dict] = []
    if REGISTRY_MD.exists():
        registry_rows = parse_registry(REGISTRY_MD.read_text(encoding="utf-8"))

    scripts = collect_scripts()

    payload = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "registry_path": str(REGISTRY_MD.relative_to(REPO)).replace("\\", "/"),
        "registry": registry_rows,
        "scripts": scripts,
        "script_count": len(scripts),
        "registry_count": len(registry_rows),
    }

    serialized = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        if OUT.exists():
            try:
                prev = json.loads(OUT.read_text(encoding="utf-8"))
                cur = dict(payload); cur.pop("generated_at", None)
                prev.pop("generated_at", None)
                if prev == cur:
                    print(f"OK — {OUT.relative_to(REPO)} is up-to-date "
                          f"({len(scripts)} scripts, {len(registry_rows)} registry rows).")
                    return 0
            except Exception:
                pass
        print(f"DIFF — {OUT.relative_to(REPO)} would change. Run scripts/build_agents_index.py.", file=sys.stderr)
        return 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists() and OUT.read_text(encoding="utf-8") == serialized:
        print(f"unchanged {OUT.relative_to(REPO)} ({len(scripts)} scripts, {len(registry_rows)} registry rows).")
        return 0
    OUT.write_text(serialized, encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO)} ({len(scripts)} scripts, {len(registry_rows)} registry rows).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
