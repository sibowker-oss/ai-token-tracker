#!/usr/bin/env python3
"""wq-066 — Apply audit-extract values to entities.json:market_aggregates.

Reads data/wq-066-audit-extract.json (produced by extract_audit_values.py)
and writes documented values into entities.json:market_aggregates.<year>
with provenance entries (origin = editorial_audit_doc_backfill).

Backfill policy:
  - Only writes when audit value is non-null AND target field is currently
    absent OR explicitly null (engine-derived values win when present).
  - tokens_per_day_total is treated as authoritative from audit (engine
    derivation is known stale; entity-level tokens haven't been refreshed).
  - Each backfilled field gets a _market_provenance entry documenting the
    audit section, value, and confidence.

After backfill, re-runs the cumulative aggregator and walks
consensus_overrides.json — for any override where engine output now lands
within ±5% of the override value, the override is REMOVED (engine takes over).

Generates data/wq-066-backfill-gaps.md listing every audit-extract null
with the editorial question Simon needs to answer.

CLI:
  python3 scripts/backfill_editorial.py --dry-run
  python3 scripts/backfill_editorial.py --apply   # MUTATES entities.json + overrides
"""
from __future__ import annotations

import argparse
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
ENTITIES_PATH = ROOT / "entities.json"
OVERRIDES_PATH = ROOT / "data" / "consensus_overrides.json"
EXTRACT_PATH = ROOT / "data" / "wq-066-audit-extract.json"
GAP_REPORT_PATH = ROOT / "data" / "wq-066-backfill-gaps.md"

TODAY = "2026-05-03"

# Fields where audit is authoritative (overrides engine even if engine has a value).
# tokens_per_day_total: entity-level model_provider tokens are stale; audit is right.
AUTHORITATIVE_FIELDS = {"tokens_per_day_total"}


def _load_extract() -> dict:
    return json.loads(EXTRACT_PATH.read_text())


def _load_entities() -> dict:
    return json.loads(ENTITIES_PATH.read_text())


def _load_overrides() -> dict:
    if not OVERRIDES_PATH.exists():
        return {}
    return json.loads(OVERRIDES_PATH.read_text())


def apply_backfill(extract: dict, entities: dict) -> tuple[list[str], list[str]]:
    """Returns (written_log, skipped_log)."""
    written = []
    skipped = []
    audit_ma = extract.get("market_aggregates") or {}

    market = entities.setdefault("market_aggregates", {})
    for year, audit_year in audit_ma.items():
        ma_year = market.setdefault(year, {})
        provenance = ma_year.setdefault("_market_provenance", {})
        for field, audit_val in audit_year.items():
            if field.startswith("_"):
                continue
            if audit_val is None:
                continue
            existing = ma_year.get(field)
            authoritative = field in AUTHORITATIVE_FIELDS
            if existing is None or authoritative:
                ma_year[field] = audit_val
                provenance[field] = {
                    "claim": f"{field} {year} = {audit_val} per assumptions-audit.md {audit_year.get('_audit_section', '')}",
                    "value": audit_val,
                    "source": "assumptions-audit.md",
                    "section": audit_year.get("_audit_section"),
                    "weight": "indicative",
                    "confidence": "estimated",
                    "origin": "editorial_audit_doc_backfill",
                    "date": TODAY,
                    "engine_value_at_backfill": existing,
                    "authoritative_supersedes_engine": authoritative,
                }
                written.append(f"{year}.{field}: {existing} → {audit_val}")
            else:
                skipped.append(f"{year}.{field}: existing engine value={existing} preserved (audit={audit_val})")

    return written, skipped


def remove_redundant_overrides(extract: dict, entities: dict, overrides: dict) -> list[str]:
    """For each cumulative-level override, check if backfilled engine output
    is now within ±5% of the override value. If so, REMOVE the override.

    NOTE: this runs AFTER cumulative aggregator has been re-run on the
    backfilled entities.json, so cumulative engine values reflect the latest.
    """
    removed = []
    cumulative = (entities.get("market_aggregates") or {}).get("_cumulative_2023_2025") or {}
    # _overrides metadata keeps engine_value alongside override_value
    ov_meta = cumulative.get("_overrides") or {}
    for field, meta in ov_meta.items():
        engine_val = meta.get("engine_value")
        override_val = meta.get("override_value")
        if engine_val is None or override_val is None or override_val == 0:
            continue
        delta = abs(engine_val - override_val) / abs(override_val)
        if delta <= 0.05:
            override_key = f"_cumulative_2023_2025.{field}"
            if override_key in overrides:
                removed.append(f"{override_key}: engine={engine_val} now within 5% of override={override_val}")
                del overrides[override_key]
    return removed


def write_gap_report(extract: dict, written: list[str], skipped: list[str], removed: list[str]) -> None:
    """Generates data/wq-066-backfill-gaps.md with everything Simon needs to act on."""
    audit_ma = extract.get("market_aggregates") or {}
    audit_ent = extract.get("entity_2024_revenue") or {}
    audit_tokens = extract.get("tokens_per_day_2025") or {}

    lines = []
    lines.append("# wq-066 Editorial Backfill — Gap Report")
    lines.append(f"")
    lines.append(f"Generated: {TODAY}  ·  Source: assumptions-audit.md  ·  Extractor: scripts/extract_audit_values.py")
    lines.append("")
    lines.append("## Backfill summary")
    lines.append("")
    lines.append(f"- **Written:** {len(written)} fields")
    lines.append(f"- **Skipped (engine has authoritative value):** {len(skipped)} fields")
    lines.append(f"- **Overrides removed (engine now within ±5%):** {len(removed)}")
    lines.append("")
    if written:
        lines.append("### Written values")
        for w in written:
            lines.append(f"- {w}")
        lines.append("")
    if skipped:
        lines.append("### Skipped (engine value preserved)")
        for s in skipped:
            lines.append(f"- {s}")
        lines.append("")
    if removed:
        lines.append("### Overrides removed")
        for r in removed:
            lines.append(f"- {r}")
        lines.append("")

    lines.append("## Gaps requiring Simon input")
    lines.append("")

    lines.append("### Per-year market aggregates")
    for year, fields in audit_ma.items():
        gaps = [(k, fields.get(f"_gap")) for k in fields if not k.startswith("_") and fields.get(k) is None]
        gap_specifics = []
        for k in fields:
            if k.startswith("_"):
                continue
            if fields[k] is None:
                gap_specifics.append(k)
        if gap_specifics:
            lines.append(f"")
            lines.append(f"#### {year}")
            for k in gap_specifics:
                lines.append(f"- **{k}**: not documented in audit. Question for Simon: what was {k.replace('_', ' ')} in {year}?")
            note = fields.get("_gap")
            if note:
                lines.append(f"  > Audit note: {note}")
    lines.append("")

    lines.append("### Per-entity 2024 revenue")
    for slug, info in audit_ent.items():
        if slug.startswith("_"):
            continue
        if info.get("collected_revenue") is None:
            lines.append(f"- **{slug}.2024.collected_revenue**: {info.get('_gap', 'not documented')}.")
        elif info.get("_gap"):
            lines.append(f"- **{slug}.2024.collected_revenue** = {info['collected_revenue']} (derived). {info['_gap']}")
    lines.append("")

    lines.append("### Per-provider tokens (entities.json refresh candidate)")
    audit_total = audit_tokens.get("_total")
    note = audit_tokens.get("_gap", "")
    lines.append(f"- Audit §5.3 sums to {audit_total}T/day across 9 model_providers + others.")
    lines.append(f"- entities.json model_provider tokens_per_day sums to ~164T/day (stale).")
    lines.append(f"- {note}")
    lines.append("- Suggested follow-on brief: refresh entities.json:companies[*].current.tokens_per_day for model_providers from latest signals (audit §5.3 + recent provider disclosures).")
    lines.append("")

    lines.append("### Cumulative (2023–2025) overrides held")
    cum = extract.get("cumulative_2023_2025") or {}
    if cum.get("_gap"):
        lines.append(f"- {cum['_gap']}")
    lines.append("- These remain held in data/consensus_overrides.json (expires 2026-09-01).")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("Each gap above can become its own backfill ticket once Simon answers. "
                 "Engine ingests his answer via a single edit to consensus_overrides.json "
                 "(cumulative-level) or direct entity field write (per-entity).")
    GAP_REPORT_PATH.write_text("\n".join(lines))


def _save_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    if not args.apply and not args.dry_run:
        args.dry_run = True

    if not EXTRACT_PATH.exists():
        print(f"ERROR: {EXTRACT_PATH} missing — run extract_audit_values.py first", file=sys.stderr)
        return 2

    extract = _load_extract()
    entities = _load_entities()
    overrides = _load_overrides()

    print("=== wq-066 editorial backfill ===")
    written, skipped = apply_backfill(extract, entities)
    print(f"Backfill: {len(written)} written, {len(skipped)} skipped (engine preserved)")
    for w in written[:20]:
        print(f"  + {w}")
    for s in skipped[:10]:
        print(f"  - skip {s}")

    if args.apply:
        _save_json(ENTITIES_PATH, entities)
        print(f"\nWritten: {ENTITIES_PATH}")

        # Re-run cumulative aggregator on backfilled data so override-removal
        # check sees fresh engine values.
        print("\nRe-running scripts/derive_cumulative_aggregates.py --apply ...")
        cp = subprocess.run(["python3", "scripts/derive_cumulative_aggregates.py", "--apply"],
                            cwd=ROOT, capture_output=True, text=True)
        print(cp.stdout.strip().split("\n")[-3:])
        if cp.returncode != 0:
            print(f"  stderr: {cp.stderr}")

        # Re-load entities post-aggregator (cumulative now reflects backfill)
        entities = _load_entities()
        removed = remove_redundant_overrides(extract, entities, overrides)
        if removed:
            _save_json(OVERRIDES_PATH, overrides)
            print(f"\n{len(removed)} overrides removed (engine now within ±5%):")
            for r in removed:
                print(f"  - {r}")
        else:
            print("\nNo overrides became redundant (engine still > 5% off override values)")
    else:
        removed = []
        print("\n(dry-run; pass --apply to write)")

    write_gap_report(extract, written, skipped, removed)
    print(f"\nGap report: {GAP_REPORT_PATH}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
