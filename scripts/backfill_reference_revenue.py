#!/usr/bin/env python3
"""wq-055 — backfill `reference_revenue` on existing operating_loss
provenance claims, per Simon's Phase A confirmation 2 (convention b):

  reference_revenue = the customer revenue figure that was published in
  the §7.2 Sankey methodology AT THE TIME the operating_loss claim was
  made.

For OpenAI 2025: ref_revenue = $7.65B (the §7.2 weighted-consensus
hand-curated value before wq-048 raised it to $9.31B).

For Anthropic 2025: ref_revenue = $4.5B (the cr value at claim date
2026-03-28, per dp-057 / email-20260328-b2y).

Tiny scope (2 claims at time of writing); script is idempotent —
safe to re-run as new operating_loss claims accrue across providers.

Usage:
  python3 scripts/backfill_reference_revenue.py --dry-run   # preview
  python3 scripts/backfill_reference_revenue.py --apply     # write
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from log_run import logged_run  # noqa: E402

ENTITIES_PATH = ROOT / "entities.json"


# Convention (b) lookup table. Values are the §7.2 published-at-time customer
# revenue figure that was the editorial baseline AT THE TIME the
# operating_loss claim was made.
#
# Each entry can be set automatically via the audit walk below OR by hand
# here for cases where the claim predates a clean §7.2 baseline.
HANDCURATED_REF_REVENUE = {
    # Per brief §3.3 worked example. The $6B operating loss claim (dp-005)
    # was made when the site's published customer revenue figure for
    # OpenAI 2025 was $7.65B (the §7.2 weighted-consensus, audit §4.4
    # column). wq-048 later raised it to $9.31B; this backfill captures
    # what cr WAS when the loss was reported, for the engine's opex math.
    ("openai", "2025", "operating_loss"): {
        "value": 7.65,
        "source": "AI Ledger §7.2 weighted-consensus (audit §4.4) — published cr at time of dp-005 claim 2025-09-01",
    },
    # Per Phase A inspection: dp-006 dated 2026-03-28, dp-057 had cr=$4.5B
    # at 2026-03-25. The §7.2 baseline at that time was $4.71B (Anthropic
    # consensus weighted average, also audit §4.4). Either is defensible;
    # prefer the §7.2 published value for consistency with the OpenAI
    # convention.
    ("anthropic", "2025", "operating_loss"): {
        "value": 4.71,
        "source": "AI Ledger §7.2 weighted-consensus (audit §4.4) — published cr at time of dp-006 claim 2026-03-28",
    },
}


def find_claim(prov_block: dict) -> dict | None:
    """Return the primary (non-superseded) claim from a provenance block."""
    for c in prov_block.get("claims") or []:
        if c.get("role") != "superseded":
            return c
    return None


def backfill(dry_run: bool) -> tuple[int, int, list[str]]:
    """Walks operating_loss provenance for every model_provider entity.
    Returns (written_count, skipped_count, log_lines)."""
    with open(ENTITIES_PATH) as f:
        entities = json.load(f)

    written = 0
    skipped = 0
    log_lines = []

    for ent in entities.get("companies", []):
        if "model_provider" not in (ent.get("roles") or []):
            continue
        slug = ent.get("slug")
        prov = ent.get("provenance") or {}
        for prov_key, prov_block in list(prov.items()):
            if not prov_key.endswith(".operating_loss"):
                continue
            year = prov_key.split(".")[0]
            primary = find_claim(prov_block)
            if not primary:
                continue
            if "reference_revenue" in primary:
                log_lines.append(f"  - {slug}.{year}.operating_loss: already has reference_revenue={primary['reference_revenue']} — skipping")
                skipped += 1
                continue

            key = (slug, year, "operating_loss")
            if key not in HANDCURATED_REF_REVENUE:
                log_lines.append(f"  - {slug}.{year}.operating_loss: NO ref_revenue mapping in HANDCURATED_REF_REVENUE — skip and surface for manual mapping")
                skipped += 1
                continue

            mapping = HANDCURATED_REF_REVENUE[key]
            primary["reference_revenue"] = mapping["value"]
            primary["reference_revenue_source"] = mapping["source"]
            primary["reference_revenue_set_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            log_lines.append(f"  + {slug}.{year}.operating_loss: ref_revenue={mapping['value']}  ({mapping['source']})")
            written += 1

    if not dry_run and written > 0:
        with open(ENTITIES_PATH, "w") as f:
            json.dump(entities, f, indent=2)

    return written, skipped, log_lines


def main():
    with logged_run("backfill_reference_revenue.py") as outputs:
        parser = argparse.ArgumentParser(description="Backfill reference_revenue on operating_loss provenance (wq-055).")
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--dry-run", action="store_true")
        group.add_argument("--apply", action="store_true")
        args = parser.parse_args()

        written, skipped, log_lines = backfill(dry_run=args.dry_run)
        for line in log_lines:
            print(line)
        print()
        print(f"Backfill summary ({'DRY-RUN' if args.dry_run else 'APPLY'}):")
        print(f"  written:  {written}")
        print(f"  skipped:  {skipped}")

        outputs["written"] = written
        outputs["skipped"] = skipped
        outputs["dry_run"] = args.dry_run


if __name__ == "__main__":
    main()
