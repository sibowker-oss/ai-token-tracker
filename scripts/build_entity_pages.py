#!/usr/bin/env python3
"""wq-042 — auto-build per-entity detail pages for entities crossing the
data threshold defined in data/render_config.json.

Reads entities.json + data/render_config.json, applies qualifies_for_detail_page(),
and writes companies/<slug>.html per qualifying entity from a small inline template.
Run as part of the build pipeline (see .github/workflows/build-lint.yml).

Usage:
  python3 scripts/build_entity_pages.py                 # write pages
  python3 scripts/build_entity_pages.py --dry-run       # report qualifiers only
  python3 scripts/build_entity_pages.py --report        # write the qualification report
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from log_run import logged_run  # noqa: E402

ENTITIES_PATH = ROOT / "entities.json"
RENDER_CONFIG_PATH = ROOT / "data" / "render_config.json"
COMPANIES_DIR = ROOT / "companies"
QUALIFICATION_REPORT_PATH = ROOT / "data" / "wq-042-entity-qualification.txt"
RENDER_COVERAGE_PATH = ROOT / "data" / "render_coverage.md"

CONF_RANK = {"low": 0, "estimated": 1, "medium": 1, "high": 2, "verified": 2}


def _load_render_config() -> dict:
    if not RENDER_CONFIG_PATH.exists():
        return {
            "detail_page_threshold": {
                "min_populated_fields": 3,
                "min_best_confidence": "medium",
                "min_provenance_entries": 1,
            },
            "roles": {},
        }
    with open(RENDER_CONFIG_PATH) as f:
        return json.load(f)


def _populated_field_count(entity: dict) -> int:
    """Distinct field names with non-null values across current + financials.

    Counts the union, not duplicates (so 2024.arr + 2025.arr counts as 1).
    """
    fields = set()
    current = entity.get("current") or {}
    for k, v in current.items():
        if v is not None:
            fields.add(k)
    fin = entity.get("financials") or {}
    for year, year_data in fin.items():
        if not isinstance(year_data, dict):
            continue
        for k, v in year_data.items():
            if v is not None:
                fields.add(k)
    return len(fields)


def _best_confidence(entity: dict) -> str:
    prov = entity.get("provenance") or {}
    best = "low"
    best_rank = CONF_RANK["low"]
    for p in prov.values():
        if not isinstance(p, dict):
            continue
        c = p.get("confidence", "low")
        r = CONF_RANK.get(c, 0)
        if r > best_rank:
            best = c
            best_rank = r
    return best


def _provenance_entry_count(entity: dict) -> int:
    """Count of distinct provenance entries (one per metric.year)."""
    prov = entity.get("provenance") or {}
    return sum(1 for v in prov.values() if isinstance(v, dict) and v.get("claims"))


def qualifies_for_detail_page(entity: dict, threshold: dict) -> tuple[bool, str]:
    """Per brief §4.1. Returns (ok, reason_string)."""
    n_fields = _populated_field_count(entity)
    if n_fields < threshold["min_populated_fields"]:
        return False, f"fields={n_fields} < {threshold['min_populated_fields']}"

    best_conf = _best_confidence(entity)
    min_conf = threshold["min_best_confidence"]
    if CONF_RANK.get(best_conf, 0) < CONF_RANK.get(min_conf, 0):
        return False, f"best_confidence={best_conf} < {min_conf}"

    n_prov = _provenance_entry_count(entity)
    if n_prov < threshold["min_provenance_entries"]:
        return False, f"provenance_entries={n_prov} < {threshold['min_provenance_entries']}"

    return True, f"fields={n_fields}, best_conf={best_conf}, prov={n_prov}"


def report(entities: dict, config: dict) -> str:
    """Build the §6 step 2 qualification dry-run report."""
    threshold = config["detail_page_threshold"]
    qualifiers = []
    non_qualifiers = []
    for entity in entities.get("companies", []):
        ok, reason = qualifies_for_detail_page(entity, threshold)
        if ok:
            qualifiers.append((entity, reason))
        else:
            non_qualifiers.append((entity, reason))

    lines = [
        "# wq-042 entity-qualification dry-run",
        f"_Generated {datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')}_",
        "",
        f"Threshold: min_populated_fields={threshold['min_populated_fields']} | "
        f"min_best_confidence={threshold['min_best_confidence']} | "
        f"min_provenance_entries={threshold['min_provenance_entries']}",
        "",
        f"## Qualifies for detail page: {len(qualifiers)} of {len(entities['companies'])}",
        "",
    ]
    for ent, reason in sorted(qualifiers, key=lambda x: x[0].get("name", "")):
        lines.append(f"  ✓  {ent['slug']:30}  {ent['name']:30}  ({reason})")

    lines += [
        "",
        f"## Does NOT qualify: {len(non_qualifiers)} of {len(entities['companies'])}",
        "",
    ]
    for ent, reason in sorted(non_qualifiers, key=lambda x: x[0].get("name", "")):
        lines.append(f"  ✗  {ent['slug']:30}  {ent['name']:30}  ({reason})")
    return "\n".join(lines) + "\n"


def _slug_to_filename(slug: str) -> str:
    return re.sub(r"[^a-z0-9._-]", "-", slug.lower()) + ".html"


def _build_detail_page_html(entity: dict) -> str:
    """Minimal admin-style template: header, current snapshot, financials, source list."""
    slug = entity.get("slug", "")
    name = entity.get("name", slug)
    roles = ", ".join(entity.get("roles", []) or [])
    region = entity.get("region", "")
    website = entity.get("website", "")
    current = entity.get("current") or {}
    fin = entity.get("financials") or {}
    prov = entity.get("provenance") or {}

    # Current snapshot rows
    snap_rows = "".join(
        f"<tr><td>{k}</td><td>{_fmt(v)}</td></tr>"
        for k, v in sorted(current.items()) if v is not None
    ) or "<tr><td colspan='2'>No current snapshot data.</td></tr>"

    # Financials timeline
    fin_rows = []
    years = sorted([y for y in fin.keys() if isinstance(fin.get(y), dict)])
    if years:
        all_fields = sorted({f for y in years for f in fin[y].keys()})
        header = "<th>Year</th>" + "".join(f"<th>{f}</th>" for f in all_fields)
        for y in years:
            row = f"<th>{y}</th>" + "".join(f"<td>{_fmt(fin[y].get(f))}</td>" for f in all_fields)
            fin_rows.append(f"<tr>{row}</tr>")
        fin_table = f"<table><thead><tr>{header}</tr></thead><tbody>{''.join(fin_rows)}</tbody></table>"
    else:
        fin_table = "<p>No financials timeline.</p>"

    # Provenance summary
    prov_rows = "".join(
        f"<tr><td>{k}</td><td>{(v or {}).get('confidence', '?')}</td>"
        f"<td>{len((v or {}).get('claims', []) or [])}</td></tr>"
        for k, v in sorted(prov.items())
    ) or "<tr><td colspan='3'>No provenance entries.</td></tr>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{_esc(name)} — Entity profile</title>
<style>
  body {{ font-family:-apple-system,'SF Pro Display',sans-serif; background:#0a0e1a; color:#e2e8f0; max-width:920px; margin:0 auto; padding:32px; }}
  h1 {{ font-size:26px; margin:0 0 4px 0; }}
  .meta {{ color:#94a3b8; font-size:13px; margin-bottom:24px; }}
  h2 {{ font-size:14px; text-transform:uppercase; letter-spacing:0.5px; color:#94a3b8; margin:24px 0 8px; }}
  table {{ width:100%; border-collapse:collapse; font-size:13px; }}
  th, td {{ padding:8px 10px; text-align:left; border-bottom:1px solid #1e293b; }}
  th {{ font-weight:600; color:#cbd5e1; background:#111827; }}
  a {{ color:#3b82f6; }}
  .nav-back {{ display:inline-block; font-size:12px; margin-bottom:18px; }}
  .auto-tag {{ display:inline-block; font-size:10px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px; color:#8b5cf6; background:rgba(139,92,246,0.10); padding:2px 8px; border-radius:6px; }}
</style>
</head>
<body>
  <a class="nav-back" href="../directory.html">← Directory</a>
  <h1>{_esc(name)} <span class="auto-tag">auto-promoted</span></h1>
  <div class="meta">
    <strong>Slug:</strong> {_esc(slug)}
    {('· <strong>Roles:</strong> ' + _esc(roles)) if roles else ''}
    {('· <strong>Region:</strong> ' + _esc(region)) if region else ''}
    {('· <a href="' + _esc(website) + '" target="_blank">Website ↗</a>') if website else ''}
  </div>

  <h2>Current snapshot</h2>
  <table><tbody>{snap_rows}</tbody></table>

  <h2>Financials timeline</h2>
  {fin_table}

  <h2>Provenance summary</h2>
  <table><thead><tr><th>Field.year</th><th>Best confidence</th><th>Claims</th></tr></thead><tbody>{prov_rows}</tbody></table>

  <p style="margin-top:32px;color:#94a3b8;font-size:11px;">
    Auto-generated by <code>scripts/build_entity_pages.py</code> · wq-042 · entity passed the data-threshold gate.
  </p>
</body>
</html>
"""


def _fmt(v) -> str:
    if v is None:
        return ""
    if isinstance(v, (int, float)):
        return f"{v:,}"
    return _esc(str(v))


def _esc(s: str) -> str:
    return (str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def build_pages(entities: dict, config: dict, dry_run: bool = False) -> tuple[int, int, str]:
    threshold = config["detail_page_threshold"]
    written = 0
    skipped = 0
    log_lines = []
    for entity in entities.get("companies", []):
        ok, reason = qualifies_for_detail_page(entity, threshold)
        if not ok:
            skipped += 1
            continue
        path = COMPANIES_DIR / _slug_to_filename(entity["slug"])
        log_lines.append(f"  WRITE  {path.relative_to(ROOT)}  ({reason})")
        if dry_run:
            written += 1
            continue
        COMPANIES_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(_build_detail_page_html(entity))
        written += 1

    coverage_md = (
        f"# Render coverage report (wq-042)\n\n"
        f"_Generated {datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')}_\n\n"
        f"- Entities total: {len(entities.get('companies', []))}\n"
        f"- Detail pages written: {written}\n"
        f"- Below threshold (directory only): {skipped}\n"
    )
    return written, skipped, coverage_md


def main() -> None:
    with logged_run("build_entity_pages.py") as outputs:
        parser = argparse.ArgumentParser(description="Build entity detail pages (wq-042).")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--report", action="store_true",
                            help="Write data/wq-042-entity-qualification.txt and exit.")
        args = parser.parse_args()

        with open(ENTITIES_PATH) as f:
            entities = json.load(f)
        config = _load_render_config()

        if args.report:
            txt = report(entities, config)
            QUALIFICATION_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
            QUALIFICATION_REPORT_PATH.write_text(txt)
            print(f"Wrote {QUALIFICATION_REPORT_PATH}")
            outputs["qualifying_entities"] = txt.count("\n  ✓  ")
            outputs["non_qualifying_entities"] = txt.count("\n  ✗  ")
            return

        written, skipped, coverage_md = build_pages(entities, config, dry_run=args.dry_run)
        if not args.dry_run:
            RENDER_COVERAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
            RENDER_COVERAGE_PATH.write_text(coverage_md)
        print(f"Pages written: {written}, skipped (below threshold): {skipped}, dry_run={args.dry_run}")
        outputs["pages_written"] = written
        outputs["pages_skipped"] = skipped
        outputs["dry_run"] = args.dry_run


if __name__ == "__main__":
    main()
