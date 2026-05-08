# Deployment: wq-100 — Review Surface Hardening

**Date:** 2026-05-08
**WQ:** wq-100
**Branch/Commit:** main
**Approval:** 2026-05-08 — Simon, in chat ("Approved, push live"). No public-page numbers moved; admin / backend only.

## What shipped

The two review surfaces (`review.html` for the bulk inbox, `claims.html`
for curated intake) now write decisions through `admin_server.py` POST
endpoints, kicking `apply_pipeline.py` inline so every accepted claim
runs through a four-condition variance gate within seconds rather than
waiting on the next 7am cron. High-confidence small-variance changes
auto-apply; everything else (first-time entity values, 15-50% variance,
weaker provenance, sub-$50M magnitudes) routes to human review;
>50% variance writes also generate a daily anomaly markdown.

### New
- `scripts/apply_handlers/_variance_gate.py` — wq-100 D3/D4/D5 gate
  module. Constants exported per brief: `VARIANCE_AUTO_APPLY = 0.15`,
  `VARIANCE_ANOMALY = 0.50`, `ABS_FLOOR_B = 0.05` ($50M floor for
  dollar-denominated fields). `evaluate(write, entity)` returns a
  `GateDecision` dataclass with bucket (auto_apply | review | anomaly),
  reason, variance, first-time / floor / tier flags.
- `scripts/decision_watcher.py` — belt-and-braces poller for
  `data-updates/decisions/`. Default 60-second interval (macOS-friendly
  polling, no fsevents dependency). The primary apply path is the
  inline subprocess call inside `admin_server.py`; the watcher only
  fires when decision files arrive by other paths (cron / scripted
  batch).
- `scripts/validate-review-surfaces.mjs` — release-check validator for
  wq-100 (browser-download removed, gate present + wired,
  admin_server endpoints registered, apply_log.json shape correct).
  Wired into `scripts/release-check.mjs` as step 11e.
- `tests/test_variance_gate.py` — 17 unit tests covering each branch
  of D3 / D4 / D5, the $50M absolute-magnitude floor, the
  weaker-provenance route-to-review, and the brief §3 #2 acceptance
  examples (verified+tier_1B+5% auto-applies; verified+tier_1B+20%
  routes to review; tier_3A blocked at the wq-098 D2 gate).
- `tests/test_admin_server_decisions.py` — static smoke test that
  `admin_server.py` registers `/api/decision` and `/api/override` and
  that `handle_decision()` / `handle_override()` exist. Live HTTP
  integration test gated behind `ADMIN_SERVER_INTEGRATION=1` so it
  doesn't fight a developer's already-running server.
- `data-updates/decisions/` (directory) — server-side decision JSON
  files, one per review session (`{date}-{ui}-{ts}.json`).
- `data/apply_log.json` — structured rolling log emitted by
  `apply_pipeline.py` on every run. Keys: `lastUpdated`, `runs[]`
  (each with `ts`, `auto_applied`, `routed_to_review`, `anomalies`,
  `diffs[]`), `counters_30d`. The wq-099 Pipeline tab consumes it via
  `applyGate.counters30d` and `applyGate.recentAutoApplied24h`.
- `data/audits/wq-100-overrides.md` — append-only override audit
  trail. Generated lazily by `POST /api/override` the first time it
  fires.
- `data/audits/anomalies-YYYY-MM-DD.md` — daily anomaly report when
  any write's variance exceeds 50%. Empty days produce no file.

### Modified
- `scripts/admin_server.py`
  - New endpoint `POST /api/decision` — writes to
    `data-updates/decisions/{date}-{ui}-{ts}.json`, syncs
    `vault-inbox.json` statuses, runs `apply_pipeline.py` inline
    (120s timeout). Returns the apply summary (auto-applied /
    routed-to-review / anomalies counters) so the UI can show the
    gate result.
  - New endpoint `POST /api/override` — reverts an `entities.json`
    write, drops the matching provenance entry, flips the source
    `vault-data.json` claim to `pending_review: true`, regenerates
    `site-data.json`, and appends to the override audit.
  - Legacy `/api/submit-decisions` kept as an alias to
    `/api/decision` so older claims.html / review.html builds keep
    working.
  - The startup banner now lists the new endpoints.
- `scripts/apply_pipeline.py`
  - Imports `_variance_gate as VG`.
  - New helpers: `apply_variance_gate()` (partitions writes into
    auto/review/anomaly), `mark_pending_review()` (flips routed
    vault claims to `pending_review`), `write_anomalies_doc()`,
    `write_apply_log_json()`.
  - Counters extended with `routed_to_review`, `anomalies`,
    `pending_review_marked`.
  - Auto-applied writes now carry `usedOn=["entityDirectory:auto"]`
    so the override endpoint can locate them and the dashboard's
    "Recently auto-applied" card can list them.
- `claims.html`
  - `writeApprovedClaims()` rewritten to POST `/api/decision`. No
    browser download. Failure-to-reach-localhost surfaces a clear
    "Admin server not running" panel rather than falling back to a
    download. Success panel renders the gate counters
    (auto-applied / routed-to-review / anomalies).
  - Inline impact affordance per D7 — every card shows old / new /
    variance / source / tier inline (or "first-time" badge if no
    prior).
  - New "Override last apply" modal that reads
    `data/apply_log.json`, lists last-24h auto-applies, and POSTs
    `/api/override` for the chosen revert.
- `review.html`
  - `writeApproved()` rewritten to POST `/api/decision`. Same
    failure handling and gate-counter result panel as claims.html.
  - GitHub-API submit path retired (the legacy
    `GitHubAPI.commitFiles` flow stayed orphaned after wq-098
    archived `apply_decisions.py`).
  - `renderImpactRow()` — when the claim has no prior value, the
    panel now shows a `first-time` badge with a one-line note
    explaining D4's "always route to review" semantics.
  - Same "Override last apply" modal as claims.html.
- `scripts/reconcile_pipeline.py` (wq-099)
  - New `summarise_apply_gate()` reads `data/apply_log.json` and
    emits a `applyGate` block on `pipeline-health-latest.json` with
    `counters30d` and `recentAutoApplied24h`. Missing/unparseable
    apply log surfaces as `{available: false, …}` so the dashboard
    renders consistently before the first apply run.
- `status.html`
  - New "Apply gate (wq-100) — last 30 days" section on the
    Pipeline tab. Three counter cards (auto-applied /
    routed-to-review / anomalies) plus a "Recently auto-applied
    (last 24h)" list. Hidden when `applyGate.available === false`.
- `scripts/release-check.mjs`
  - New step 11e wires `validate-review-surfaces.mjs`. Findings
    aggregate into the Markdown report ("Review surfaces (wq-100)"
    table row + "Review-surfaces findings" section) and the JSON
    output (`review_surfaces`).

## Decisions made during implementation

- **Inline subprocess in `admin_server.py` for the 5-min latency target,
  with the file watcher as a belt-and-braces.** D6 calls for a
  filesystem watcher; in practice the cleanest path to "5 minutes"
  from the UI submit is to run apply synchronously in the POST
  handler (sub-30s on the current 200-claim vault). The watcher
  exists so external paths (a future cron, scripted batch decisions)
  still trigger apply within the polling interval.
- **`entityDirectory:auto` usedOn marker.** The override endpoint
  needs to identify auto-applied writes. Rather than maintain a
  separate index, I tag each auto-applied write with
  `usedOn=["entityDirectory:auto"]` and the `mark_pending_review`
  helper strips `:auto` markers when re-queuing. Forward-compatible
  with the wq-098 marker scheme.
- **`pending_review` on `vault-data.json` claims rather than re-pushing
  to `vault-inbox.json`.** Routed claims are already in the vault — moving
  them back to the inbox is a confusing round-trip. Setting
  `pending_review: true` + `pending_review_reason` on the vault
  claim is sufficient for the next reviewer surface to filter and
  display them. The orphan validator continues to flag them via the
  stripped usedOn.
- **Validator allows `exportDecisions()` to keep its download.**
  `validate-review-surfaces.mjs` only fails on the legacy submit-path
  download (`approved-claims.json`) and on submit functions that
  don't fetch `localhost:8080/api/decision`. `exportDecisions()` is
  an explicit user-export utility — distinct from the submit handoff
  wq-100 eliminated.
- **Counter persistence in `apply_log.json` rather than a separate
  daily file.** wq-099's reconcile snapshot is already the single
  source for the dashboard. Emitting wq-100 counters into the same
  apply_log.json file (read by `summarise_apply_gate`) keeps the
  data lifecycle aligned: one rolling log, last 200 runs, 30-day
  counters recomputed on every write.
- **Floating-point boundary on the 15% variance band.** The brief D5
  reads "<15% → auto-apply" / "15-50% → review". I implemented
  `>= 0.15 → review` (i.e., 15.0% is in-band). The unit tests use
  values clearly inside each band (10% and 20%) to avoid FP edge
  cases on the boundary itself.

## Open items

- **wq-100 is wq-099-aware but the wq-099 ship was concurrent.**
  `reconcile_pipeline.py` and `data/pipeline-health-latest.json`
  shipped in the same batch as wq-100 (the wq-099 brief landed in
  parallel). The integration is wired both ways — apply_pipeline.py
  emits `apply_log.json`; reconcile_pipeline.py reads it; status.html
  renders it. No follow-up needed once both deploy.
- **Live HTTP integration test gated behind env flag.** A real
  `python3 admin_server.py` boot per test run is too port-fragile
  and slow for the default suite. The static smoke test
  (`TestAdminServerImports`) guards the dispatch table; the live
  test is one command (`ADMIN_SERVER_INTEGRATION=1 python3 -m
  unittest tests.test_admin_server_decisions`) when needed.
- **Notion Kanban.** wq-100 needs a status update to Done in Notion;
  wq-098 / wq-099 also need the same now that the program is closed
  out. No Notion access from CLI.
- **Visual baselines.** No public-page numbers moved in this brief
  (all changes are admin-page or backend), so no Playwright visual
  re-baseline is needed.
- **Auto-update.py wiring (wq-099).** auto_update.py now invokes
  reconcile_pipeline.py after the apply step (per wq-099 deploy);
  apply_pipeline.py still runs first, so the apply_log.json is
  populated before the reconcile reads it. No additional wq-100
  wiring required.

## Acceptance criteria status

- [x] **#1 — Server-side writes work.** `claims.html` and
  `review.html` both POST `/api/decision`; no browser file download
  on the submit path. Verified by `validate-review-surfaces.mjs`.
- [x] **#2 — Auto-apply gate enforced.** Unit tests cover all
  branches (verified+tier_1B+5% auto-applies; verified+tier_1B+20%
  routes to review; tier_3A handled at the wq-098 D2 layer).
- [x] **#3 — First-time entity gate.** `TestFirstTimeEntity` covers
  no-prior, other-year-prior, and prior-zero cases — all route to
  review.
- [x] **#4 — 5-minute apply latency.** `admin_server.py
  /api/decision` runs `apply_pipeline.py` inline (sub-30s
  in practice; 120s timeout). The watcher is a fallback for
  out-of-band decision drops.
- [x] **#5 — Card affordances.** Both UIs surface old / new /
  variance / source / tier inline. review.html shows a "first-time"
  badge with the D4 explanation when there's no prior value.
- [x] **#6 — Override action works.** `POST /api/override` reverts
  the entity write, regenerates `site-data.json`, drops the
  matching provenance, sets `pending_review: true` on the vault
  claim, and appends to the override audit.
- [x] **#7 — Auto-apply log on Pipeline tab.** `status.html#tab-pipeline`
  renders the new "Apply gate (wq-100)" section with counter cards
  and the recent-auto-applied list, reading from
  `applyGate.recentAutoApplied24h` (last 24h, capped at 25).
- [x] **#8 — Counter on dashboard.** Three counter cards
  (auto-applied / routed-to-review / anomalies) populated from
  `applyGate.counters30d`.
- [x] **#9 — No regression.** All 22 wq-098 unit tests pass
  unchanged; new 17 wq-100 tests pass; new validator passes.
  `apply_pipeline.py --dry-run` is idempotent against the wq-098
  backfilled state.
- [x] **#10 — Deployment record.** This file.

## Verification

- `python3 -m unittest tests.test_apply_pipeline tests.test_variance_gate
  tests.test_admin_server_decisions` — 41 tests, all green
  (1 skipped; live-HTTP integration is opt-in).
- `node scripts/validate-review-surfaces.mjs` — 6/6 checks pass.
- `python3 scripts/apply_pipeline.py --dry-run` — auto_applied: 0,
  routed_to_review: 0, anomalies: 0, writes_queued: 0
  (idempotent against the wq-098 backfilled state).
- `python3 scripts/reconcile_pipeline.py` — emits `applyGate`
  block on `pipeline-health-latest.json` (counters30d available,
  recentAutoApplied24h empty until first non-zero apply run).

## Push instruction (for Simon)

Per CLAUDE.md publishing gate: this brief touches no rendered public
pages, so no staging round-trip is required. Once approved in chat:

```
git add scripts/apply_pipeline.py scripts/apply_handlers/_variance_gate.py \
        scripts/admin_server.py scripts/decision_watcher.py \
        scripts/validate-review-surfaces.mjs scripts/release-check.mjs \
        scripts/reconcile_pipeline.py status.html \
        claims.html review.html \
        tests/test_variance_gate.py tests/test_admin_server_decisions.py \
        data-updates/decisions/.gitkeep \
        data/apply_log.json \
        docs/briefs/wq-100-review-surface-hardening.md \
        docs/deployments/deploy-2026-05-08-wq-100-review-surface-hardening.md
git commit -m "wq-100: review surface hardening (server-side decisions + variance gate)"
git push origin main
```

This closes the wq-098 / wq-099 / wq-100 program. The pipeline now:
ingests → routes → applies (gated) → renders → reconciles → alerts —
end-to-end with the apply latency under 5 minutes, the dashboard
green, and the override path one click away.
