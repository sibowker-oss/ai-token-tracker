# wq-098 — Direct vault-data.json writers audit

**Date:** 2026-05-08
**Brief:** wq-098 §Phase A.2

Inventory of every script that opens `vault-data.json` for write, with the
post-rebuild disposition. Per Decision D5: only `apply_pipeline.py` writes
to `vault-data.json` after this brief; everything else routes via
`vault-inbox.json` or is allowlisted as maintenance.

| Script | Pre-098 behaviour | Post-098 disposition | Reason |
|---|---|---|---|
| `scripts/apply_claims.py` | Writes accepted claims (legacy `data-updates/approved-claims.json` flow) | **Archived** as `apply_claims.legacy.py`. CI fails on import. | Replaced by `apply_pipeline.py`. The browser-download approval handoff is dead per scoping doc Failure #1. |
| `scripts/apply_decisions.py` | Writes accepted claims + entities + provenance from review-decisions files | **Archived** as `apply_decisions.legacy.py`. CI fails on import. | Replaced by `apply_pipeline.py`. Claim-level apply logic merged into the new dispatcher; triangulation soft-park branch preserved in the new script. |
| `scripts/enrich_vault.py` | Re-classifies vault items with status='pending_enrichment' (sets unit/category/value cleanups; does not add new dataPoints) | **Allowlisted (maintenance)** | Only mutates existing rows; does not add new claims. Documented as a vault hygiene script. Future work (wq-100+) may move it to a separate vault-hygiene channel. |
| `scripts/fix_vault_data_mojibake.py` | Repairs UTF-8/Latin-1 round-trip errors in existing string fields | **Allowlisted (maintenance)** | Repair-only; touches text fields, not values or `usedOn`. Already noted in CLAUDE.md as a maintenance script. |
| `scripts/anthropic_monthly_review.py` | **Read-only** — generates `data/anthropic-monthly-*.md` reports; never writes vault-data.json | No change | Verified: only reads `VAULT_DATA_PATH`; writes go to `REPORT_DIR`. |
| `scripts/reconcile.py` | **Read-only** | No change | |

## Allowlist (allowed to write `vault-data.json` post-098)

```
scripts/apply_pipeline.py                — canonical apply
scripts/apply_handlers/*.py              — typed handlers invoked by apply_pipeline
scripts/enrich_vault.py                  — maintenance: mutates existing rows only
scripts/fix_vault_data_mojibake.py       — maintenance: repairs encoding
scripts/apply_claims.legacy.py           — archived (must NOT be imported)
scripts/apply_decisions.legacy.py        — archived (must NOT be imported)
```

## What changes for ingestion scripts

No ingestion script in scope was found writing directly to `vault-data.json`. All
inbox-side writers (`extract_claims.py`, `scan_sources.py`, `monitor_sources.py`,
`curated_intake.py`, `_telemetry_router.py`, podcast scrapers) already write to
`vault-inbox.json` only. That branch of D5 is already conformant; this audit
documents the existing state rather than redirecting any code path.

The bypass closure work for this brief is therefore limited to: archiving the
legacy apply scripts, asserting the allowlist in `release-check.mjs`, and
making `apply_pipeline.py` the single entry point.
