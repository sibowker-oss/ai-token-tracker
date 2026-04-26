#!/usr/bin/env python3
"""Synthetic broken-case tests for scripts/validate_page_registry.py per
brief §12 (wq-031 P1 acceptance — duplicate path, missing folder match,
dangling supersededBy).

Run: python3 tests/test_validate_page_registry.py
"""
import json
import os
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "scripts"))

import validate_page_registry as v  # noqa: E402


def _load():
    return json.loads(v.REGISTRY.read_text(encoding="utf-8"))


def _schema_block():
    return v.load_schema_lifecycle()


def _fs():
    # Use the real filesystem — broken cases inject inconsistencies into the
    # registry, not the fs.
    return v.list_repo_html_files()


def test_baseline_passes():
    failures = v.check(_load(), _schema_block(), _fs())
    assert failures == [], f"baseline must pass, got: {failures}"


def test_R4_duplicate_path():
    reg = _load()
    # duplicate the first entry
    reg["pages"].append(dict(reg["pages"][0]))
    failures = v.check(reg, _schema_block(), _fs())
    assert any("R4 duplicate path" in f for f in failures), f"R4 expected to fire: {failures[:5]}"


def test_R2_folder_status_mismatch():
    reg = _load()
    # Force a beta-status entry to point at a root path
    reg["pages"].append({
        "path": "synthetic-root.html",
        "status": "beta",
        "title": "x", "purpose": "x", "supersedes": [],
        "supersededBy": None, "addedOn": "2026-04-26", "retiredOn": None,
    })
    fs = set(_fs())
    fs.add("synthetic-root.html")
    failures = v.check(reg, _schema_block(), fs)
    assert any("R2" in f and "synthetic-root.html" in f for f in failures), (
        f"R2 expected to fire: {failures[:5]}"
    )


def test_R5_dangling_supersededBy():
    reg = _load()
    # Inject an entry that supersededBy a path not in the registry
    reg["pages"].append({
        "path": "synthetic-x.html",
        "status": "retired",
        "title": "x", "purpose": "x", "supersedes": [],
        "supersededBy": "no-such-page.html",
        "retiredOn": "2026-04-26",
        "retiredReason": "synthetic test",
        "addedOn": "2026-04-26",
    })
    fs = set(_fs())
    fs.add("synthetic-x.html")
    failures = v.check(reg, _schema_block(), fs)
    assert any("R5" in f and "no-such-page.html" in f for f in failures), (
        f"R5 expected to fire: {failures[:5]}"
    )


def test_R1_missing_from_registry():
    reg = _load()
    fs = set(_fs())
    fs.add("phantom.html")  # exists on disk per fs but not in registry
    failures = v.check(reg, _schema_block(), fs)
    assert any("R1" in f and "phantom.html" in f for f in failures), (
        f"R1 expected to fire: {failures[:5]}"
    )


def test_R3_retired_missing_reason():
    reg = _load()
    # Find a retired entry, drop retiredReason
    for e in reg["pages"]:
        if e["status"] == "retired" and e.get("retiredReason"):
            e.pop("retiredReason")
            tgt = e["path"]
            break
    failures = v.check(reg, _schema_block(), _fs())
    assert any("R3" in f and tgt in f for f in failures), (
        f"R3 expected to fire on {tgt}: {failures[:5]}"
    )


def main():
    tests = [
        test_baseline_passes,
        test_R4_duplicate_path,
        test_R2_folder_status_mismatch,
        test_R5_dangling_supersededBy,
        test_R1_missing_from_registry,
        test_R3_retired_missing_reason,
    ]
    failures = []
    for t in tests:
        try:
            t()
        except AssertionError as e:
            failures.append(f"  {t.__name__}: {e}")
    if failures:
        print(f"FAIL — {len(failures)} of {len(tests)} cases:")
        for line in failures:
            print(line)
        return 1
    print(f"OK — {len(tests)} cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
