# Deployment: Inbox rebase-stomp recovery + extract-claims auto-commit

**Date:** 2026-05-13
**WQ:** wq-103 (admin / inbox audit follow-up)
**Branch/Commit:** main (pushed live 2026-05-13)
**Publish-gate:** explicit waiver from Simon in chat — see
`docs/decisions/open/dec-2026-05-13-publish-gate-exception-inbox-recovery.md`

## What shipped

1. Backfilled 10 productify (`src-107`) inbox items into `vault-inbox.json`
   that were lost when `git pull --rebase origin main` at 2026-05-11 17:04
   reset the file to the upstream version, discarding local writes from a
   prior `/api/extract-claims` run. Statuses set to match the user's review
   decisions in `data-updates/decisions/2026-05-12-review-091615.json`
   (3 accepted, 1 declined, 6 parked).
2. Re-ran `apply_pipeline.py`. The 3 accepted items minted dp-260 / dp-261 /
   dp-262 in `vault-data.json`; OpenAI 2026.arr ($25B) and Anthropic 2026.arr
   ($30B) were already at value, Mistral 2026.valuation moved None → $12.85B.
   No industry-total impact (`arr_delta_b: 0.0`).
3. Hardened `scripts/admin_server.py`: `/api/extract-claims` now performs an
   immediate local `git add` + `git commit` after writing `vault-inbox.json`
   so subsequent rebases can't silently drop in-flight extractions. New
   helper `_git_commit_paths()` is local-only (never pushes) and non-fatal
   on failure.

Files changed:
- `vault-inbox.json` (backfill + reapply pipeline writes)
- `vault-data.json` (3 new dps from migration)
- `entities.json` (Mistral.2026.valuation = 12.85)
- `site-data.json` (regenerated)
- `data/apply_log.json`, `data/apply_pipeline.log`, `data/audits/wq-098-*.md`
- `scripts/admin_server.py` (extract-claims auto-commit hardening)

## Decisions made during implementation

- **Backfill stub fields for declined/parked.** The decision payload only
  carries `id` + `claim` + `note` for declined/parked items. Reconstructed
  the inbox shape with sensible defaults (sourceUrl from accepted items'
  url, sourceType=reporting, value=null, source_id=src-107, dateAdded=
  2026-05-11) plus `decisionReason: "lost-to-rebase: backfilled from..."`
  for traceability. Re-extracting from the URL would have given cleaner
  metadata but cost an API call and risked the LLM returning a different
  set of claims.
- **Auto-commit scope.** Limited the new `_git_commit_paths()` call site
  to `/api/extract-claims` (the actual failure mode). `_sync_inbox_status`
  in `/api/decision` is followed immediately by `apply_pipeline.py` which
  also touches the file, and there's no symmetric data-loss risk there
  since decisions are also persisted to `data-updates/decisions/`.
- **Local commit only, no push.** Respects the publishing gate — the
  commit lands in working git but doesn't propagate to origin without
  Simon's normal commit/push flow.

## Open items

- The 6 parked + 1 declined src-107 items have stub metadata (no value,
  no unit, no precise tags). They sit at status=declined/parked so they
  won't surface for re-review, but if anyone later mines parked items,
  the records are thin.
- `_git_commit_paths` doesn't handle a detached-HEAD or pre-commit-hook
  failure case beyond logging to stderr. Acceptable for a defensive
  belt-and-braces measure; revisit if it starts producing noise.
- Brief `wq-103-confidence-overhaul-admin-audit.md` (already untracked
  in working tree before this session) covers the broader admin audit
  — this deploy only addresses the immediate inbox loss + the one
  prevention measure.

## Acceptance criteria status

- [x] 11 src-107 items reflected in `vault-inbox.json` with correct status
  *(actually 10 — decision file had 6 parked, not 7)*
- [x] 3 accepted src-107 items migrated to `vault-data.json` as
  `human_reviewed=true`
- [x] `apply_pipeline.py` reports `inbox_migrated_new: 3`, no anomalies
- [x] `/api/extract-claims` auto-commits inbox writes locally
- [x] No live-site publish initiated (publishing gate respected)
