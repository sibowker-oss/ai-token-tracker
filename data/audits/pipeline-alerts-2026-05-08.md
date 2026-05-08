# Pipeline alerts — 2026-05-08

_Generated_: 2026-05-08T08:52:38.597813Z
_Source_: `scripts/reconcile_pipeline.py` (wq-099)

**3 assertion(s) failed.** Each entry below names the failing assertion, the affected count, and the recommended next action.

## apply_propagation — failing

**Count:** 19

**Detail:** 19 verified tier-2A-or-better claim(s) have usedOn=[]. Sample IDs: dp-042, dp-048, dp-051, dp-104, dp-107, dp-110, dp-151, dp-159, dp-174, dp-199.

**Recommended action:** A verified tier-2A-or-better claim has `usedOn: []` — likely an apply_pipeline regression or a manual vault edit that bypassed the pipeline. Run `python3 scripts/apply_pipeline.py --dry-run --verbose` and check the audit doc at `data/audits/wq-098-skipped-claims.md`.

## inbox_migration_freshness — failing

**Count:** 19

**Detail:** 19 accepted inbox item(s) older than 24h have no vault dp-id (sample: audit-20260404-gap-1, audit-20260404-gap-3, audit-20260404-gap-4, audit-20260404-gap-6, audit-20260404-gap-7). Run `python3 scripts/apply_pipeline.py` to mint vault entries.

**Recommended action:** Accepted inbox items are sitting unmigrated. Run `python3 scripts/apply_pipeline.py` — the hotfix migration phase mints vault dp-NNN entries for any accepted inbox item lacking an `accepted_as` reference.

## arrmodel_vault_backed — failing

**Count:** 16

**Detail:** 16 arrModel entry/entries source their arr from a non-vault path (sample: arrModel.apps.frontier/ByteDance, arrModel.apps.frontier/Alibaba/Qwen, arrModel.apps.frontier/Tencent, arrModel.apps.frontier/Baidu, arrModel.apps.frontier/Others/Self-hosted). Confirm the entity has been applied via `apply_pipeline.py`, then rebuild site-data.json.

**Recommended action:** An arrModel entity sources its arr from a non-vault path (legacy topConsumers / providers fixture). Confirm the entity has a populated `current.arr` / `financials.<year>.arr` in entities.json (with a provenance trail), then rebuild site-data.json. See `data/audits/wq-098-arrmodel-source-leak.md`.
