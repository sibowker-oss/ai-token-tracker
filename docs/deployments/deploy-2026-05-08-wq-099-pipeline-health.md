# Deployment: wq-099 — Pipeline Health: Dashboard + Reconciliation + Alerts

**Date:** 2026-05-08
**WQ:** wq-099
**Branch/Commit:** main (staged on top of 5273236 — pre-push, awaiting Simon's chat approval per CLAUDE.md publishing gate)

## What shipped

Visibility surface for the claims pipeline. A new **Pipeline** tab on
`status.html` answers the four-question morning glance:

1. What came in overnight?
2. What's waiting for me?
3. What might be stale?
4. What broke?

Backed by a nightly reconciliation script (`scripts/reconcile_pipeline.py`)
that runs as part of `auto_update.py`'s daily chain and writes a single
JSON snapshot the dashboard reads. Six structural assertions evaluate
on every run; failures flip the dashboard cards red and write an alert
markdown file under `data/audits/pipeline-alerts-YYYY-MM-DD.md`. A
manual "Run reconciliation now" button on the Pipeline tab triggers a
fresh run via `admin_server.py`.

### New
- `scripts/reconcile_pipeline.py` — reconciliation engine. Loads vault,
  vault-inbox, entities, site-data, runs.jsonl. Computes
  `ingestSummary`, `reviewQueueSummary`, `staleEntities`, `vaultSummary`,
  and runs the six assertions. Writes
  - `data/pipeline-health-YYYY-MM-DD.json`
  - `data/pipeline-health-latest.json`
  - `data/audits/pipeline-alerts-YYYY-MM-DD.md` (only on assertion fail)
- `scripts/validate-pipeline-health-freshness.mjs` — release-check
  validator. Asserts `pipeline-health-latest.json` exists, is <30h old,
  and has zero active alerts. Catches the case where reconcile silently
  stops running.
- `data/pipeline-health-2026-05-08-initial.json` — seeded baseline. The
  brief specifies `2026-05-09-initial.json`; today is 2026-05-08 so the
  date in the filename reflects actual run date. Functionally equivalent.
- `data/pipeline-health-2026-05-08.json`,
  `data/pipeline-health-latest.json` — first regular snapshot.
- `data/audits/pipeline-alerts-2026-05-08.md` — first alert file (one
  failing assertion: `apply_propagation`, 19 verified tier-2A+ orphans
  carried over from wq-098 — see Open items below).
- `docs/decisions/open/dec-2026-05-09-d7-dashboard-block-removal.md` —
  parked decision file for the D7 portion of the brief (see below).

### Modified
- `status.html` — added a top-level tab bar (Run log / Pipeline) plus
  the Pipeline panel, four summary cards, the six-assertion list, the
  stale-entity table, and the manual-refresh button. Mobile-checked at
  375px (cards collapse to single column; nothing overflows). Existing
  Run log behaviour unchanged.
- `scripts/auto_update.py` — wired `reconcile_pipeline.py` into the
  daily chain immediately after `apply_pipeline`. Pipes `alertCount`
  into the `logged_run` outputs so the run log records it.
- `scripts/admin_server.py` — added `POST /api/run-reconcile` endpoint
  that subprocesses `python3 scripts/reconcile_pipeline.py` (60s
  timeout) and returns success / `asOf` / `alertCount`.
- `scripts/release-check.mjs` — added step 11d
  (validate-pipeline-health-freshness), surfaced findings in the
  summary table + verdict count + report.json output.

### Deferred
- **D7 (delete `dashboard.providers` / `dashboard.topConsumers` from
  site-data.json).** Parked in
  `docs/decisions/open/dec-2026-05-09-d7-dashboard-block-removal.md`.
  The brief's premise that these blocks are empty post-wq-096 is wrong;
  both are populated and load-bearing for `apply_pipeline.py`,
  `wq096_emit.py`, `generate_site_data.py`, `auto_update.py`, and
  `vault.html`. The wq-098 deployment record explicitly cites
  `dashboard.topConsumers[Cursor].arrNumeric=2_000_000_000` as
  acceptance criterion #5. Removing them now would silently break
  wq-098. See the decision file for the full producer/consumer map and
  the three options.
- **methodology.html deprecation note.** Tied to D7; deferred with it.

## Decisions made during implementation

- **Tab structure on `status.html` rather than separate page.** Brief
  D1 specified "new tab", which I read as a sub-tab on `status.html`
  (tab toggle between "Run log" and "Pipeline"). Alternative would have
  been a new admin-nav entry; the existing Status nav slot already has
  one entry and the brief's intent is "leverages the admin nav, auth,
  design system" — sub-tab on the existing page satisfies all three.
- **Tier derivation reuses `apply_handlers/_shared.derive_tier`.**
  Vault claims don't carry a `tier` field; both wq-098's
  `validate-pipeline-orphans.mjs` and `apply_pipeline.py` derive tier
  from `(sourceType, confidence)`. Reused the canonical helper rather
  than duplicating the ladder. First draft used `claim.get("tier")`
  directly which under-counted high-tier orphans; fix re-aligned with
  the wq-098 validator (both now report 19 dp- entries).
- **`looks_like_arr` filter on entity-vault sync.** The "$B" unit in
  vault is generic — many claims with `unit: "$B"` describe valuation
  / funding / burn rather than ARR. Imported the same text-signal
  filter `apply_handlers/arr.py:_looks_like_arr` uses so the
  reconciliation matches what `apply_pipeline` would actually apply.
  Without it, Google/Gemini and OpenAI surfaced spurious
  multi-hundred-billion "vault truth" values pulled from total-revenue
  or funding-round claims.
- **Stale entity gate requires `usedOn=[]`.** Brief §5.4 says "the
  cited claim is the highest-tier most-recent claim available". I
  interpreted this conservatively — only surface as stale if the
  highest-tier verified vault claim has *not* been applied yet
  (`usedOn=[]`). If it's already been applied and the entity still
  diverges, `apply_pipeline.py` already chose the existing value
  (divergence guard >15%) and surfaced that decision in its own
  audit doc — re-flagging here would be noise.
- **Latest non-projected year filter excludes future years.** Some
  entities have `2030` (without `_projected` suffix) carrying forecast
  values. Restricted "latest applied year" to current-or-prior so
  reconciliation doesn't compare against forecasts.
- **Manual `/api/run-reconcile` deliberately uses subprocess, not
  in-process import.** Keeps the admin server's lifetime decoupled
  from anything `reconcile_pipeline.py` imports, and makes the audit
  trail visible in the response body.
- **Snapshot baseline filename uses today's actual date.** Brief D6
  specifies `pipeline-health-2026-05-09-initial.json`; current date is
  2026-05-08 so the file is `pipeline-health-2026-05-08-initial.json`.
  The `--suffix initial` argument is the durable contract; date
  encoding follows the run.
- **Linter/Cowork-side additions accepted.** During Phase B + C the
  file was extended with an `applyGate` block in
  `reconcile_pipeline.py` and a corresponding `pipe-apply-gate-section`
  in `status.html` — likely the wq-100 apply-gate integration landing
  in parallel. Left intact; my Pipeline tab structure passes through
  the new section unchanged.

## Acceptance criteria status

- [x] **#1 — Pipeline tab on status.html.** 4 summary cards (ingest /
  review / stale / alerts) + 6-assertion list + stale-entity table +
  freshness chip + manual refresh button. Visual smoke test via
  Playwright: tab switch works, all 4 summary cards render, 6
  assertions render, no console errors. Mobile (375px) validated.
- [x] **#2 — Reconciliation runs nightly.** Wired into
  `auto_update.py:main()` immediately after `apply_pipeline`. Snapshot
  freshness ceiling (30h) enforced by step 11d in release-check.
- [x] **#3 — Six assertions implemented.** `ingest_health`,
  `review_queue_freshness`, `apply_propagation`, `entity_vault_sync`,
  `arrmodel_consistency`, `handler_coverage`. Each returns
  `{name, passed, count, details}`. Synthetic-input unit-tested for the
  three most likely to fire (`apply_propagation`,
  `review_queue_freshness`, `handler_coverage`).
- [x] **#4 — Alert file generated on failure.** Confirmed:
  `data/audits/pipeline-alerts-2026-05-08.md` produced by initial run
  (`apply_propagation` failing — 19 carried-over high-tier orphans).
  Each failing assertion gets a section with count, detail, and a
  recommended-action line. Affected IDs / entities listed where
  available.
- [x] **#5 — Card colour-coding.** Per-card tone derived from per-card
  fail/orange/green per the renderPipeline logic. Verified
  `apply_propagation` failure shows the alerts card red.
- [x] **#6 — Manual refresh button.** End-to-end test:
  `curl -X POST /api/run-reconcile` returns
  `{"success":true,"alertCount":1,"asOf":"2026-05-08T..."}`. Status
  page button wired to the same endpoint with disabled state during
  the run and a re-fetch on completion.
- [ ] **#7 — Legacy structure removal.** **Deferred per D7 decision
  file.** See decision file for the conflict.
- [x] **#8 — Initial baseline snapshot.** Committed at
  `data/pipeline-health-2026-05-08-initial.json` (filename uses today's
  date; brief specified 2026-05-09).
- [x] **#9 — Deployment record.** This file.

## Open items

- **D7 decision waiting on Cowork** — see
  `docs/decisions/open/dec-2026-05-09-d7-dashboard-block-removal.md`.
  Pick option A/B/C; A (defer) is recommended.
- **First-run alert: `apply_propagation` failing with 19 orphans.**
  This is the wq-098-known carry-over (multi-tier ambiguous entities,
  string-shaped values, unmatched entities — see
  `data/audits/wq-098-skipped-claims.md`). The reconciliation correctly
  flags it as a real problem, but it's *expected* state, not
  regression. Once wq-100 (review surface hardening) lands, the orphan
  count should drop to zero.
- **`ingest_health` reads `claims_added` etc. from `runs.jsonl`
  outputs.** Different scripts use different output keys
  (`claims_added` vs `items_enriched` vs `alerts_total`). Current
  reconcile takes the first non-zero of those. Worth normalising to a
  single canonical `inboxed_count` in a follow-up if more scrapers
  land — for now this matches the existing scrapers' output shape.
- **Entity matching is intentionally conservative.** Tight match
  (sourceAuthor exact, or tag = slug) avoids the false-positive trap
  but will under-count when an entity's name doesn't appear cleanly in
  the source author. Acceptable trade-off; surfacing fewer real stale
  cases is better than surfacing many false ones.
- **`pipeline-orphans.json` / `pipeline-health-freshness.json` both
  fail in current state.** Both findings reflect the same underlying
  19-orphan reality. Once wq-100 dispositions those, both clear
  together.
- **Notion Kanban.** wq-099 needs a status update to Done in Notion;
  no Notion access from CLI.

## Verification

- `python3 scripts/reconcile_pipeline.py --suffix initial` — succeeds,
  writes baseline, latest, and alert markdown.
- `python3 -m py_compile scripts/reconcile_pipeline.py
  scripts/auto_update.py scripts/admin_server.py` — clean.
- `node --check scripts/validate-pipeline-health-freshness.mjs
  scripts/release-check.mjs` — clean.
- `node scripts/validate-pipeline-health-freshness.mjs` — produces
  expected `[fail] 1 reconciliation alert(s) active` finding (matches
  the 19-orphan baseline).
- `node scripts/validate-pipeline-orphans.mjs` — same 19 orphans.
  Cross-validates the two are in sync.
- Admin-server roundtrip: started server, fetched `status.html`
  (HTTP 200, 30k bytes), `pipeline-health-latest.json` (200, 2.2k),
  POSTed `/api/run-reconcile` (200,
  `success=true alertCount=1`).
- Headless Playwright smoke: tab switch fires, Pipeline panel becomes
  visible, 4 summary cards + 6 assertion rows render, no console
  errors. Mobile viewport at 375px shows the cards collapsing as
  expected.

## Push instruction (for Simon)

Per CLAUDE.md publishing gate: this brief is **admin-only** (D8 of the
brief; see also acceptance #1 — "no public-page impact"). The Pipeline
tab lives behind the existing `status.html` admin password. No public
URL changes; no rendered numbers change; no staging gate needed.

Once approved in chat:

```
git add scripts/reconcile_pipeline.py \
        scripts/validate-pipeline-health-freshness.mjs \
        scripts/auto_update.py scripts/admin_server.py \
        scripts/release-check.mjs \
        status.html \
        data/pipeline-health-2026-05-08-initial.json \
        data/pipeline-health-2026-05-08.json \
        data/pipeline-health-latest.json \
        data/audits/pipeline-alerts-2026-05-08.md \
        docs/briefs/wq-099-pipeline-health.md \
        docs/decisions/open/dec-2026-05-09-d7-dashboard-block-removal.md \
        docs/deployments/deploy-2026-05-08-wq-099-pipeline-health.md
git commit -m "wq-099: pipeline health — dashboard, reconciliation, alerts"
git push origin main
```
