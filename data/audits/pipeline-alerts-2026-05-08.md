# Pipeline alerts — 2026-05-08

_Generated_: 2026-05-08T06:58:48.803239Z
_Source_: `scripts/reconcile_pipeline.py` (wq-099)

**1 assertion(s) failed.** Each entry below names the failing assertion, the affected count, and the recommended next action.

## apply_propagation — failing

**Count:** 19

**Detail:** 19 verified tier-2A-or-better claim(s) have usedOn=[]. Sample IDs: dp-042, dp-048, dp-051, dp-104, dp-107, dp-110, dp-151, dp-159, dp-174, dp-199.

**Recommended action:** A verified tier-2A-or-better claim has `usedOn: []` — likely an apply_pipeline regression or a manual vault edit that bypassed the pipeline. Run `python3 scripts/apply_pipeline.py --dry-run --verbose` and check the audit doc at `data/audits/wq-098-skipped-claims.md`.
