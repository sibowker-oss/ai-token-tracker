#!/usr/bin/env python3
"""wq-070 — Prune redundant cumulative overrides.

Walks data/consensus_overrides.json. For each `_cumulative_2023_2025.<field>`
override, reads the engine_value preserved on
entities.json:market_aggregates._cumulative_2023_2025._overrides[<field>]
and removes the override when the engine output is within tolerance.

Default tolerance is 0.15 (±15%) per brief intent — overrides exist to hold
a published number while engine catches up; once engine lands inside the
band, the override stops adding signal and starts hiding the engine answer.

CLI:
  python3 scripts/prune_cumulative_overrides.py --dry-run
  python3 scripts/prune_cumulative_overrides.py --apply
  python3 scripts/prune_cumulative_overrides.py --tolerance 0.05  # tighter
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTITIES_PATH = ROOT / "entities.json"
OVERRIDES_PATH = ROOT / "data" / "consensus_overrides.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--tolerance", type=float, default=0.15,
                    help="auto-remove when |engine - override| / override <= tolerance (default 0.15)")
    args = ap.parse_args()
    if not args.apply and not args.dry_run:
        args.dry_run = True

    entities = json.loads(ENTITIES_PATH.read_text())
    overrides = json.loads(OVERRIDES_PATH.read_text())
    cumulative = (entities.get("market_aggregates") or {}).get("_cumulative_2023_2025") or {}
    ov_meta = cumulative.get("_overrides") or {}

    print(f"=== wq-070 cumulative override prune (tolerance ±{int(args.tolerance*100)}%) ===\n")
    if not ov_meta:
        print("No active overrides on _cumulative_2023_2025. Nothing to prune.")
        return 0

    removed = []
    kept = []
    for field, meta in ov_meta.items():
        key = f"_cumulative_2023_2025.{field}"
        engine_val = meta.get("engine_value")
        override_val = meta.get("override_value")
        if engine_val is None or override_val is None or override_val == 0:
            kept.append((key, "engine value missing — can't compare"))
            continue
        delta = abs(engine_val - override_val) / abs(override_val)
        if delta <= args.tolerance:
            removed.append((key, f"engine={engine_val} override={override_val} Δ={delta*100:.1f}% ≤ ±{int(args.tolerance*100)}%"))
        else:
            kept.append((key, f"engine={engine_val} override={override_val} Δ={delta*100:.1f}% > ±{int(args.tolerance*100)}%"))

    print("Removable:")
    for k, msg in removed:
        print(f"  ✓ {k}: {msg}")
    if not removed:
        print("  (none)")
    print("\nStays held:")
    for k, msg in kept:
        print(f"  · {k}: {msg}")
    if not kept:
        print("  (none)")

    if args.apply and removed:
        for key, _ in removed:
            if key in overrides:
                del overrides[key]
        OVERRIDES_PATH.write_text(json.dumps(overrides, indent=2) + "\n")
        print(f"\nWrote {OVERRIDES_PATH} ({len(removed)} override(s) removed)")
    elif removed:
        print("\n(dry-run; pass --apply to write)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
