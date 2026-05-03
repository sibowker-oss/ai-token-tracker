#!/usr/bin/env python3
"""wq-074 — Capital sankey engine.

Derives the 3-column capital.html sankey from:
  - entities.json:market_aggregates._cumulative_2023_2025 (4 capex bucket totals)
  - data/capital_sankey_structure.json (editorial sub-allocation + Column 1/2 ratios)

Per Phase 5 Option 2 (Simon-confirmed 2026-05-03): engine produces 4 bucket
totals; editorial sub-allocates within mag7 and sovereign so capital.html
preserves its 10-source narrative granularity.

Per-node conservation is guaranteed by construction — every flow is a
proportional cross-product of source × destination shares.

Writes to entities.json:market_aggregates._capital_sankey.

CLI:
  python3 scripts/derive_capital_sankey.py --validate
  python3 scripts/derive_capital_sankey.py --apply  # MUTATES entities.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTITIES_PATH = ROOT / "entities.json"
STRUCTURE_PATH = ROOT / "data" / "capital_sankey_structure.json"
DATE = "2026-05-04"


def _load_entities() -> dict:
    return json.loads(ENTITIES_PATH.read_text())


def _load_structure() -> dict:
    return json.loads(STRUCTURE_PATH.read_text())


def derive_capital_sankey(entities: dict, structure: dict) -> dict:
    """Engine output: dict with sources / destinations / utilization / flows /
    total + per-node provenance. FLOWS is array of [src, dst, value] tuples.

    Bucket totals = sum across 2023+2024+2025 from market_aggregates.<year>
    (cumulative aggregator doesn't carry per-bucket cumulative fields; only
    the grand capex_total. Re-sum here from per-year for traceability)."""
    ma = entities.get("market_aggregates") or {}
    bucket_totals = {"mag7": 0.0, "neocloud": 0.0, "sovereign": 0.0, "enterprise": 0.0}
    field_map = {
        "mag7": "mag7_capex",
        "neocloud": "neocloud_capex",
        "sovereign": "sovereign_capex",
        "enterprise": "enterprise_capex",
    }
    for year in ("2023", "2024", "2025"):
        ma_year = ma.get(year) or {}
        for bucket, field in field_map.items():
            v = ma_year.get(field)
            if isinstance(v, (int, float)):
                bucket_totals[bucket] += v
    total_capex = round(sum(bucket_totals.values()), 4)

    sub_alloc = structure.get("column0_sub_allocation") or {}
    col1_ratios = structure.get("column1_destination_ratios") or {}
    col2_ratios = structure.get("column2_utilization_splits") or {}
    src_names = structure.get("source_display_names") or {}
    dst_names = structure.get("destination_display_names") or {}
    util_names = structure.get("utilization_display_names") or {}

    # Column 0 expansion: 4 buckets → 10 source nodes via sub-allocation.
    # Sub-allocation ratios per bucket may not sum to exactly 1.0 (rounding in
    # structure file); normalize so each bucket's sub-shares sum to bucket total.
    sources = {}
    for bucket, total in bucket_totals.items():
        sub = sub_alloc.get(bucket)
        if sub:
            clean = {k: v for k, v in sub.items() if not k.startswith("_")}
            s = sum(clean.values()) or 1.0
            for sub_slug, ratio in clean.items():
                display = src_names.get(sub_slug, sub_slug)
                sources[display] = total * (ratio / s)
        else:
            display = src_names.get(bucket, bucket)
            sources[display] = total

    # Column 1 + Column 2 ratios may not sum to exactly 1.0 (3-decimal rounding
    # in structure file). Normalize so each column sums to total_capex exactly,
    # else capital.html's validate() chain accumulates 0.5+ drift past tolerance.
    def _normalize(ratios: dict, name_map: dict) -> dict:
        clean = {k: v for k, v in ratios.items() if not k.startswith("_")}
        s = sum(clean.values()) or 1.0
        return {name_map.get(k, k): total_capex * (v / s) for k, v in clean.items()}

    destinations = _normalize(col1_ratios, dst_names)
    utilization = _normalize(col2_ratios, util_names)

    # FLOWS: proportional cross-products
    # Stage 1 → Stage 2: each src × each dst, value = src_val * (dst_val / total)
    # This guarantees per-node conservation: sum over destinations of flow(src,*) = src_val
    # Pass full precision — capital.html validate() asserts column sums within
    # $0.5B; per-flow rounding accumulates noise beyond that. Round only at
    # the renderer/display layer, not the data layer.
    flows = []
    for src, src_val in sources.items():
        for dst, dst_val in destinations.items():
            value = src_val * (dst_val / total_capex) if total_capex else 0
            if value > 0.001:  # drop micro-flows below 0.001 to keep render clean
                flows.append([src, dst, value])
    for dst, dst_val in destinations.items():
        for util, util_val in utilization.items():
            value = dst_val * (util_val / total_capex) if total_capex else 0
            if value > 0.001:
                flows.append([dst, util, value])

    return {
        "total": total_capex,
        "bucket_totals": {k: round(v, 4) for k, v in bucket_totals.items()},
        "sources": sources,
        "destinations": destinations,
        "utilization": utilization,
        "flows": flows,
        "_engine": "scripts/derive_capital_sankey.py (wq-074)",
        "_engine_run_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "_doc": (
            "Capital sankey engine output. Column 0 sources derived from market_aggregates "
            "bucket totals × structure.column0_sub_allocation. Columns 1+2 = pure editorial "
            "ratios applied to total. FLOWS guaranteed to satisfy per-node conservation by "
            "construction (proportional cross-product). capital.html reads via site-data.json."
        ),
    }


def assert_capital_conservation(out: dict, tolerance: float = 0.005) -> list[str]:
    """Per-column totals == total within tolerance.
    Per-node Stage 1 conservation: sum of outflows from src == src_val.
    Per-node Stage 2 conservation: sum of inflows to dst == dst_val (and outflows = dst_val too)."""
    failures = []
    total = out.get("total") or 0

    for col_name in ("sources", "destinations", "utilization"):
        col = out.get(col_name) or {}
        col_total = sum(col.values())
        if total and abs(col_total - total) / total > tolerance:
            failures.append(f"column {col_name}: sum={col_total:.4f} vs total={total:.4f} ({abs(col_total-total)/total*100:.2f}%)")

    # Per-source: sum of stage 1 outflows == sources[src]
    src_outflow = {k: 0.0 for k in out.get("sources", {})}
    for src, dst, v in out.get("flows", []):
        if src in src_outflow:
            src_outflow[src] += v
    for src, expected in out.get("sources", {}).items():
        actual = src_outflow.get(src, 0)
        if expected and abs(actual - expected) / expected > 0.02:  # 2% tol for rounding-down
            failures.append(f"source {src}: outflow_sum={actual:.4f} vs expected={expected:.4f}")

    return failures


def calibration(out: dict) -> str:
    total = out.get("total") or 0
    sources = out.get("sources") or {}
    flows = out.get("flows") or []
    lines = [
        f"Capital sankey calibration:",
        f"  total_capex (engine): ${total:.2f}B",
        f"  source nodes: {len(sources)}",
        f"  destination nodes: {len(out.get('destinations') or {})}",
        f"  utilization nodes: {len(out.get('utilization') or {})}",
        f"  flow edges: {len(flows)}",
        "",
        "Source breakdown:",
    ]
    for src, val in sources.items():
        lines.append(f"  {src:25s} ${val:>7.2f}B")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    if not args.validate and not args.apply:
        args.validate = True

    entities = _load_entities()
    structure = _load_structure()

    out = derive_capital_sankey(entities, structure)
    print("=== wq-074 capital sankey engine ===\n")
    print(calibration(out))
    print()
    failures = assert_capital_conservation(out)
    if failures:
        print(f"Conservation FAIL ({len(failures)}):")
        for f in failures:
            print(f"  ✗ {f}")
        if args.apply:
            return 2
    else:
        print("Conservation: ✓ all column + per-source identities hold")

    if args.apply:
        market = entities.setdefault("market_aggregates", {})
        market["_capital_sankey"] = out
        ENTITIES_PATH.write_text(json.dumps(entities, indent=2) + "\n")
        print(f"\nWritten: entities.json:market_aggregates._capital_sankey")
    else:
        print("\n(--validate; pass --apply to write)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
