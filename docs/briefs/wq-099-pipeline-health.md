# wq-099 — Pipeline Health: Dashboard + Reconciliation + Alerts

**Stage:** Scoped
**Priority:** H (no future broken-pipeline-discovered-by-accident; wq-098 fixes today's mess but this prevents the next one)
**Owner:** Claude Code
**Briefing status:** ready_for_review
**Decisions resolved:** 2026-05-08 (Simon, in Cowork session)
**Companion scoping doc:** `/Users/simonbowker/Documents/Claude/Projects/The AI Ledger/PIPELINE-SCOPING-2026-05-08.md`
**Repo copy (canonical):** `/Users/simonbowker/Developer/apac-ai-intel/docs/briefs/wq-099-pipeline-health.md`
**Parent briefs:** wq-098 (Pipeline Apply Layer Rebuild) — must ship first; wq-100 (Review Surface Hardening) — companion, can ship in parallel after wq-098

---

## §0 — Context

The defect surfaced 2026-05-08: 79% of vault entries had `usedOn: []` for months without anyone noticing. wq-098 rebuilds the apply layer to fix the propagation. This brief delivers the **visibility surface** that ensures the next failure is caught in days, not months.

The existing `status.html` shows whether **cron jobs ran**. It doesn't show whether **claims actually flowed through to publication.** That's the gap.

**Non-tech user story (Simon's morning glance):**

> When I open TAIL each morning I want to see four things in 10 seconds:
> 1. **What came in overnight** — did the scrapers find anything, or quiet night?
> 2. **What's waiting for me** — how many claims need my eyes today, which entities they affect, oldest waiting?
> 3. **What might be stale** — are any published numbers out of sync with newer vault claims? (e.g. site shows Cursor $1B, vault has $2B Sacra-verified)
> 4. **What broke** — did a scraper fail, did apply hit an unhandled type, did anything need review and get ignored for >7 days?
>
> Without this, I discover broken things weeks later by accident.

---

## §Decisions (resolved 2026-05-08)

| # | Decision | Resolved choice |
|---|---|---|
| D1 | Surface location | New tab on `status.html` (existing admin page) — leverages the admin nav, auth, design system. NOT a separate Notion artifact, NOT a Cowork artifact. Tab labelled "Pipeline" or "Claims Flow". |
| D2 | Data source | A new nightly script `scripts/reconcile_pipeline.py` writes a single JSON output `data/pipeline-health-YYYY-MM-DD.json` (date-stamped, plus a `pipeline-health-latest.json` symlink). Dashboard reads `pipeline-health-latest.json`. Decouples the dashboard from live computation. |
| D3 | Refresh cadence | Reconciliation runs nightly via existing `auto_update.py` cron (7am). Dashboard shows the latest snapshot's timestamp. Manual "refresh now" button on the page calls `admin_server.py` to trigger a fresh run on demand (admin-only). |
| D4 | Alerts | Alerts surface in two places: (a) the dashboard card colour-coding (red/orange/green), and (b) a new `data/audits/pipeline-alerts-YYYY-MM-DD.md` markdown file when assertions fail. **No external email/Slack/PagerDuty in this brief** — those can come later if morning-glance proves insufficient. |
| D5 | Reconciliation assertions | The nightly script asserts six conditions. Any failure flags the dashboard card red and writes the alert file. See §5 for the full list. |
| D6 | Backfill | Run `reconcile_pipeline.py` once against current state to seed historical baseline. Snapshot stored at `data/pipeline-health-2026-05-09-initial.json` for diff reference. |
| D7 | Removal of legacy structures | Now is the moment to delete `dashboard.providers` and `dashboard.topConsumers` from `site-data.json` (emptied by wq-096, no longer written by wq-098 apply pipeline). Add deprecation note in `methodology.html`. |
| D8 | Public-page impact | Zero. This brief only touches admin pages. `status.html` admin view extends; nothing public moves. No staging gate needed. |

No open decisions. Implement directly.

---

## §1 — Goal

Simon opens `/status.html` and within 10 seconds knows: the pipeline is healthy or it isn't, what needs his attention today, what shipped overnight, what's stale on the public site. A nightly reconciliation script asserts six structural invariants and surfaces any failure in the dashboard + an alert markdown file. After this brief, "the pipeline silently rotted for months" is impossible.

---

## §2 — Files touched

### Modified
- `status.html` — add a new "Pipeline" tab (or section) that reads `data/pipeline-health-latest.json` and renders the four-question summary.
- `scripts/auto_update.py` — wire `reconcile_pipeline.py` into the daily 7am chain after apply.
- `site-data.json` — remove `dashboard.providers` and `dashboard.topConsumers` blocks (D7).
- `methodology.html` — note the deprecation (one line in the data-sources section).

### New
- `scripts/reconcile_pipeline.py` — nightly assertion script. Reads vault, entityDirectory, site-data, log files. Writes `data/pipeline-health-YYYY-MM-DD.json` and `pipeline-health-latest.json`. Writes `data/audits/pipeline-alerts-YYYY-MM-DD.md` if any assertion fails.
- `data/pipeline-health-latest.json` (generated) — the single source the dashboard reads.

### Validators
- `scripts/release-check.mjs` — assert `data/pipeline-health-latest.json` exists and is <30 hours old (catches the case where reconcile stops running).

---

## §3 — Acceptance criteria

1. **Pipeline tab on status.html** renders the four-question summary clearly. At a glance Simon can see: ingest count last 24h, review queue depth + age of oldest, stale entities count, alert count (with 0 or N).
2. **Reconciliation script runs nightly** as part of `auto_update.py`. `data/pipeline-health-latest.json` is no more than 30 hours old at any time.
3. **Six assertions implemented** per §5. Each assertion produces a structured result in the JSON output (passed/failed/count).
4. **Alert file generated** when any assertion fails: `data/audits/pipeline-alerts-YYYY-MM-DD.md` with the failing assertion(s), affected claim/entity IDs, and recommended action.
5. **Dashboard colour-coding works.** Card border red if any assertion failed in latest snapshot; orange if review queue >7 days old or stale entity exists; green otherwise.
6. **Manual refresh button** on the Pipeline tab triggers a fresh `reconcile_pipeline.py` run via `admin_server.py` API. Loading state shows during run; new snapshot rendered when complete.
7. **Legacy structure removal** — `dashboard.providers` and `dashboard.topConsumers` deleted from site-data.json. No reference remains in any consumer code (CI assertion).
8. **Initial baseline snapshot** committed at `data/pipeline-health-2026-05-09-initial.json`.
9. **Deployment record written** at `docs/deployments/deploy-YYYY-MM-DD-wq-099-pipeline-health.md`.

---

## §4 — Implementation outline

### Phase A — Reconciliation script + assertions (1 session)

1. Build `scripts/reconcile_pipeline.py` core: load vault, entityDirectory, sources-registry, site-data, recent log files.
2. Implement the six assertions per §5. Each returns `{ name, passed, count, details }`.
3. Aggregate into a single `pipeline-health` JSON object with: `asOf`, `ingestSummary`, `reviewQueueSummary`, `staleEntities`, `assertions`, `alertCount`.
4. Write to `data/pipeline-health-YYYY-MM-DD.json` and update `pipeline-health-latest.json` symlink.
5. If any assertion fails, write `data/audits/pipeline-alerts-YYYY-MM-DD.md` with structured failure details.
6. Run once against current state to seed baseline.

### Phase B — Dashboard tab on status.html (0.5 session)

1. Add Pipeline tab structure to status.html using existing admin-nav patterns.
2. Render the four-question summary cards reading from `pipeline-health-latest.json`.
3. Add manual refresh button wired to `admin_server.py` POST endpoint.
4. Add age indicator showing snapshot freshness.
5. Mobile sanity at 375px.

### Phase C — Cron wiring + cleanup (0.25 session)

1. Add `reconcile_pipeline.py` invocation to `auto_update.py` after apply step.
2. Verify next-morning log shows clean run.
3. Delete `dashboard.providers` and `dashboard.topConsumers` from site-data.json.
4. Update methodology.html.
5. Add CI assertion: no consumer references the deleted blocks.

### Phase D — Verify & ship (0.25 session)

1. `npm run build-lint` passes.
2. `npm run release-check` passes including new assertions.
3. Manual eyeball — open status.html#pipeline, verify all four cards render, verify a synthetic assertion failure surfaces correctly.
4. Write deploy record.
5. Push to main after Simon's chat approval.

**Total estimate: ~2 sessions.**

---

## §5 — The six reconciliation assertions

Each assertion runs nightly. Failure → red card on dashboard + alert markdown file.

1. **Ingest health.** Count of new claims added to vault-inbox.json in the last 24h. Pass if >0 OR no scrapers were scheduled to run. Fail if scrapers ran but produced zero new claims (likely indicates broken adapter).

2. **Review queue freshness.** No `vault-inbox.json` item with `status: pending` older than 7 days. Fail with list of stale claim IDs.

3. **Apply propagation.** Zero verified + tier_2A-or-better vault-data.json claims with `usedOn: []`. (After wq-098 backfill, this should be zero. Future violations indicate apply pipeline regression.)

4. **Entity-vault sync.** For every `entityDirectory.<entity>.<field>` populated from a vault claim, the cited claim is the highest-tier most-recent claim available for that entity+field. Fail with list of out-of-sync entities.

5. **arrModel internal consistency.** `arrModel.combined.apps_total + arrModel.combined.compute_net = arrModel.combined.industry_total` within $0.1B tolerance. (Already in wq-096 invariants; this duplicates the check at runtime.)

6. **Handler coverage.** Every distinct `unit` value in vault-data.json has a registered handler in `apply_pipeline.py`. Fail with list of unhandled units. (Catches new ingestion types added without corresponding handler.)

---

## §6 — Edge cases

1. **First-run with empty health file.** Dashboard tab shows "No data yet — running first reconciliation" with manual-refresh button as primary CTA.

2. **Reconciliation script fails entirely** (e.g. malformed vault). Falls back to a "Reconciliation script failed at HH:MM" red card with the error message. Does not silently leave stale data on the dashboard.

3. **Dashboard reads stale snapshot.** If `pipeline-health-latest.json` is >30 hours old, render with an orange "Stale snapshot — last refresh X hours ago" warning regardless of underlying assertions.

4. **Backward-compat for deleted dashboard blocks.** Search the codebase for any reads of `dashboard.providers` or `dashboard.topConsumers` before deletion; redirect any remaining consumers to the new structures (`providers` block, `topConsumers` block at the site-data.json root) per wq-096.

---

## §7 — Test plan

1. Unit test for each of the six assertions — synthetic input, assert correct pass/fail outcome.
2. Integration test — run `reconcile_pipeline.py` on a fixture vault, assert output JSON shape.
3. Manual: introduce a synthetic stale entity in test fixture, run reconcile, verify dashboard shows orange warning + alert file generated.
4. Manual: open status.html#pipeline at desktop and 375px, verify rendering.

---

## §8 — Out of scope

- External alerting (email, Slack, PagerDuty) — defer until morning-glance proves insufficient.
- Historical trending charts — current scope is "snapshot of now". Trends can come in a follow-on.
- Per-source-adapter health detail beyond the existing `monitor_sources.py` output. The Pipeline tab summarises; deep-dive lives elsewhere.
- Dashboard for non-claim pipeline (e.g. capex extraction, hiring snapshots not affecting headline ARR) — same script can extend in a follow-on.

---

## §9 — Definition of done

1. All §3 acceptance criteria met.
2. Six assertions implemented and tested.
3. Dashboard tab live on status.html with manual refresh working.
4. `npm run release-check` passes.
5. Initial baseline snapshot committed.
6. Deployment record written.
7. Branch merged after Simon's chat approval.
8. Notion Kanban card moved to Done.

---

## §10 — Handoff prompt for VS Code / Claude Code

> Paste the block below into a fresh VS Code Claude Code session.

```
Implement wq-099 — Pipeline Health: Dashboard + Reconciliation + Alerts.

Read in order:
1. /Users/simonbowker/Developer/apac-ai-intel/CLAUDE.md
2. /Users/simonbowker/Developer/apac-ai-intel/TAIL-WORKFLOW-PROTOCOL.md
3. /Users/simonbowker/Documents/Claude/Projects/The AI Ledger/PIPELINE-SCOPING-2026-05-08.md (parent context)
4. /Users/simonbowker/Developer/apac-ai-intel/docs/briefs/wq-099-pipeline-health.md (canonical brief)

Context: wq-098 (apply layer rebuild) ships the structural fix. This brief ships the visibility surface so the next failure is caught in days, not months. Existing status.html shows cron-job status; this brief adds a "Pipeline" tab showing whether claims actually flowed to publication.

The brief is fully scoped — 8 decisions resolved 2026-05-08. Implement Phases A through D sequentially. Estimated ~2 sessions.

Critical reminders:
- Surface lives on status.html as a new tab — NOT a separate page, NOT Notion, NOT a Cowork artifact.
- Reconciliation runs nightly via auto_update.py and writes data/pipeline-health-latest.json.
- Dashboard reads the JSON; decouples render from compute.
- Six assertions per brief §5 must all be implemented.
- Manual refresh button calls admin_server.py to trigger fresh run.
- Delete dashboard.providers and dashboard.topConsumers from site-data.json (wq-096 emptied them, wq-098 doesn't write them).
- Admin-only — no public-page impact, no staging gate needed.

When done, push to main after my chat approval, update Notion card, close out the wq-098/099 program (wq-100 ships in parallel).
```

---

*End of brief.*
