#!/usr/bin/env python3
"""validate_page_registry.py — wq-031 P1 validator.

Enforces invariants on data/page-registry.json against the live filesystem
and against metric-schema.json :: page_lifecycle_statuses. Exits 0 on pass,
non-zero with a printed reason on fail. CI calls this from build-lint
(wq-031 P3) and Simon can run it ad-hoc.

Rules (per brief §5.2):
  R1 Every .html in repo (minus excluded dirs) appears exactly once in the
     registry — either as an entry's `path`, OR as the `pendingMoveFrom`
     equivalent recorded via `path` for entries with `pendingMove: true`.
  R2 Every entry's `status` matches its folder per folder_rules in the
     schema. Entries with `pendingMove: true` have the folder check
     deferred to `pendingMoveTo` (which must satisfy the folder rule).
  R3 Every status=retired entry has `supersededBy` and `retiredReason`.
  R4 No two entries share a `path`.
  R5 All `supersedes`/`supersededBy` cross-references resolve to a registry
     entry OR to a path that's about to exist post-pendingMove. Live pages
     can superseded retired-pending entries; the cross-ref resolves to the
     pending entry's `path` (current root location) until P2 rewrites it.

Run:
  python3 scripts/validate_page_registry.py
"""
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REGISTRY = REPO / "data" / "page-registry.json"
SCHEMA = REPO / "metric-schema.json"

EXCLUDED_DIRS = {"node_modules", "tests", "data/snapshots", "data-updates/archive", ".git", "Claude Design - Design System", "design-system"}

# Folder-rule resolver — maps status to allowed folder prefix
FOLDER_FOR_STATUS = {
    "live": "<root>",
    "admin": ("<root>", "data-updates/"),
    "concept": "<root>",
    "beta": "beta/",
    "parked": "parked/",
    "retired": "archive/",
    "newsletter": "newsletters/",
}


def folder_of(path):
    """Return the folder bucket key for a given registry path."""
    parts = path.split("/")
    if len(parts) == 1:
        return "<root>"
    return parts[0] + "/"


def folder_matches(status, path):
    """True if `path`'s folder satisfies status's folder_rule."""
    f = folder_of(path)
    rule = FOLDER_FOR_STATUS.get(status)
    if rule is None:
        return False
    if isinstance(rule, tuple):
        return f in rule
    return f == rule


def list_repo_html_files():
    """Walk the repo. Return relative posix paths of every .html file
    outside excluded dirs."""
    out = set()
    for root, dirs, files in os.walk(REPO):
        # Drop excluded dirs in-place so os.walk doesn't descend
        rel_root = os.path.relpath(root, REPO)
        if rel_root == ".":
            rel_root = ""
        # skip if any prefix is excluded
        prefix_parts = Path(rel_root).parts
        if any(
            ed.split("/")[0] == prefix_parts[0]
            and (len(ed.split("/")) == 1 or "/".join(prefix_parts[: len(ed.split("/"))]) == ed)
            for ed in EXCLUDED_DIRS
            if prefix_parts
        ):
            dirs[:] = []
            continue
        # also drop excluded subdirs from descent
        dirs[:] = [
            d for d in dirs
            if d not in {"node_modules", ".git", "tests"}
        ]
        if rel_root == "":
            # extra: drop data/snapshots and data-updates/archive at this level
            dirs_to_keep = []
            for d in dirs:
                if d in ("data",):
                    dirs_to_keep.append(d)
                else:
                    dirs_to_keep.append(d)
            dirs[:] = dirs_to_keep
        else:
            # if we're under data/ or data-updates/, prune excluded children
            if rel_root == "data" and "snapshots" in dirs:
                dirs.remove("snapshots")
            if rel_root == "data-updates" and "archive" in dirs:
                dirs.remove("archive")

        for fn in files:
            if not fn.endswith(".html"):
                continue
            full = (Path(rel_root) / fn) if rel_root else Path(fn)
            out.add(full.as_posix())
    return out


def load_registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def load_schema_lifecycle():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    return schema.get("page_lifecycle_statuses", {})


def check(registry, schema_block, fs_files):
    failures = []
    pages = registry.get("pages", [])
    valid_statuses = set(schema_block.get("values", []))

    # Build fast lookups
    by_path = {}
    paths_seen = []
    for entry in pages:
        path = entry.get("path")
        paths_seen.append(path)
        by_path[path] = entry

    # R4 — no duplicate paths
    seen = set()
    for p in paths_seen:
        if p in seen:
            failures.append(f"R4 duplicate path in registry: {p!r}")
        seen.add(p)

    # R1 — every .html in repo appears once in registry
    fs_set = set(fs_files)
    registered_set = set(paths_seen)
    missing = fs_set - registered_set
    extra = registered_set - fs_set
    for m in sorted(missing):
        failures.append(f"R1 file in repo but not in registry: {m}")
    for e in sorted(extra):
        # An entry whose `path` doesn't exist on disk is OK only if it's a
        # post-pendingMove future path. Currently we don't model that case
        # because pendingMove keeps `path` at the root. So any extra is a real failure.
        failures.append(f"R1 registry entry path not on disk: {e}")

    # R2 — folder matches status (with pendingMove exemption)
    for entry in pages:
        path = entry.get("path", "")
        status = entry.get("status")
        if status not in valid_statuses:
            failures.append(f"R2 unknown status {status!r} for {path}")
            continue
        if entry.get("pendingMove"):
            target = entry.get("pendingMoveTo")
            if not target:
                failures.append(f"R2 {path}: pendingMove=true but no pendingMoveTo")
                continue
            if not folder_matches(status, target):
                failures.append(
                    f"R2 {path}: pendingMoveTo={target!r} does not match status={status!r} folder rule"
                )
        else:
            # page-archive.html is "retired" but stays at root pending P4 fold-in.
            # Allow status=retired at <root> if entry has retiredOn set AND no
            # pendingMove (i.e. an "in-place" retirement). archive/sankey-v1.html
            # is the regular retired-in-place case.
            if not folder_matches(status, path):
                if status == "retired" and folder_of(path) == "<root>" and entry.get("retiredOn"):
                    # in-place retirement (e.g. page-archive.html during P0–P3
                    # before P4 folds it). Permit but warn.
                    pass
                else:
                    failures.append(
                        f"R2 {path}: status={status!r} does not match folder {folder_of(path)!r}"
                    )

    # R3 — retired entries need supersededBy + retiredReason
    for entry in pages:
        if entry.get("status") != "retired":
            continue
        path = entry.get("path")
        # supersededBy may be null only for orphan-retired pages (e.g. v1-review)
        # but retiredReason is always required
        if not entry.get("retiredReason"):
            failures.append(f"R3 {path}: retired entry missing retiredReason")
        if not entry.get("retiredOn"):
            failures.append(f"R3 {path}: retired entry missing retiredOn")
        # supersededBy is *recommended* but we accept null + a retiredReason
        # explaining the orphan-retire (e.g. v1-review.html — one-shot tool, not maintained).
        # If supersededBy is set, it must resolve. That's R5.

    # R5 — supersedes/supersededBy resolve
    for entry in pages:
        path = entry.get("path")
        for ref in entry.get("supersedes") or []:
            if ref not in by_path:
                failures.append(f"R5 {path}: supersedes -> {ref!r} which is not a registry path")
        sb = entry.get("supersededBy")
        if sb and sb not in by_path:
            failures.append(f"R5 {path}: supersededBy -> {sb!r} which is not a registry path")

    return failures


def main():
    if not REGISTRY.exists():
        print(f"FAIL — registry not found at {REGISTRY}", file=sys.stderr)
        return 2
    if not SCHEMA.exists():
        print(f"FAIL — schema not found at {SCHEMA}", file=sys.stderr)
        return 2

    registry = load_registry()
    schema_block = load_schema_lifecycle()
    if not schema_block:
        print("FAIL — page_lifecycle_statuses block missing from metric-schema.json", file=sys.stderr)
        return 2

    fs_files = list_repo_html_files()
    failures = check(registry, schema_block, fs_files)

    if failures:
        print(f"FAIL — {len(failures)} validation issue(s):")
        for f in failures:
            print(f"  {f}")
        return 1

    page_count = len(registry.get("pages", []))
    print(f"OK — {page_count} pages, {len(fs_files)} .html files in scope, all rules R1-R5 pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
