# wq-100 — Review Surface Hardening: Server-Side Decisions + Auto-Apply with Variance Gate

**Stage:** Scoped
**Priority:** M (quality of life — wq-098 fixes apply, wq-099 fixes visibility, this fixes the human review experience)
**Owner:** Claude Code
**Briefing status:** ready_for_review
**Decisions resolved:** 2026-05-08 (Simon, in Cowork session)
**Companion scoping doc:** `/Users/simonbowker/Documents/Claude/Projects/The AI Ledger/PIPELINE-SCOPING-2026-05-08.md`
**Repo copy (canonical):** `/Users/simonbowker/Developer/apac-ai-intel/docs/briefs/wq-100-review-surface-hardening.md`
**Parent briefs:** wq-098 (Pipeline Apply Layer Rebuild) — must ship first; wq-099 (Pipeline Health) — companion, can ship in parallel

---

## §0 — Context

TAIL has **two review surfaces** by design (validated against git history 2026-05-08):

- **`review.html`** — bulk inbox triage. Built for high-volume noisy extraction (extract_claims, scan_sources, monitor_sources, podcasts). Has materiality scoring, raw-pool, bulk actions, provenance guard. Operates on `vault-inbox.json`. Lineage: wq-023, wq-025, wq-040, wq-041.
- **`claims.html`** — curated source intake review. Built for editorial / structured claims (curated_intake.py, wq-083 parallel path). Smaller volume, well-formed types. Operates on `data-updates/*-candidates.json` and `data-updates/curated-*.json`. Lineage: wq-014, wq-083, wq-086.

The architectural separation is correct — the two ingestion paths produce data with different shapes that need different review patterns. **Don't collapse them.** What's broken is the *handoff* and the *workflow*, not the structural split.

**Problems this brief fixes:**

1. **Browser-download handoff** — claims.html (and partially review.html) outputs decisions as a browser file download, requiring Simon to manually move files to `data-updates/`. The `data-updates/approved-claims.json` file required by the legacy apply step doesn't exist on disk because that handoff never happens reliably.
2. **Cron lag** — even when decisions are written, they sit until the next 7am `auto_update.py` run before applying. Reviewing at 8am means an ~23-hour wait to see your decision propagate.
3. **Every claim requires human review** — even high-confidence Tier 1B disclosed numbers that have no business slowing down for human eyes (e.g., a freshly-extracted Anthropic earnings call quote with audited backing).

---

## §Decisions (resolved 2026-05-08)

| # | Decision | Resolved choice |
|---|---|---|
| D1 | Architectural separation | **Keep both review.html and claims.html.** They handle different ingestion shapes. Don't collapse. |
| D2 | Server-side decision writes | Eliminate the browser-download path for both UIs. Both write decisions through `admin_server.py` POST endpoints to `data-updates/decisions/{date}-{ui}.json`. The local admin server must be running during review sessions (already required for current admin tools). |
| D3 | Auto-apply gate | Auto-apply only if **all** four conditions met: (a) `confidence: verified`, (b) provenance ≥ tier_2A, (c) variance from existing entityDirectory value <15%, (d) provenance ≥ existing entityDirectory provenance. Anything failing any condition routes to human review. |
| D4 | First-time entity values | If entityDirectory has no existing value for the entity+field, **always** route to human review for the first claim — even if it would otherwise pass D3. Establishes a deliberate human-set baseline. |
| D5 | Variance bands | <15% → auto-apply (if other D3 conditions met). 15–50% → human review with the change highlighted. >50% → human review + flagged as anomaly in the dashboard. |
| D6 | Apply latency | After human accepts, `apply_pipeline.py` runs within 5 minutes. Implementation: file watcher on `data-updates/decisions/` triggers immediate apply. No more 23-hour cron lag for reviewed claims. |
| D7 | UI affordances on review surfaces | Each review card (in both UIs) shows: (a) old value if any, (b) new value, (c) variance % (or "first-time"), (d) source URL + provenance tier, (e) one-click accept/reject/park. Decisions write server-side immediately. |
| D8 | Auto-apply log surface | Auto-applied claims appear in a "Recently auto-applied" section on the Pipeline tab from wq-099 — Simon can spot-check anything that auto-applied without slowing the apply. |
| D9 | Override path | If Simon spots an auto-apply that was wrong, claims.html / review.html each have an "override last apply" action that reverts the entityDirectory change and queues the claim for re-review. Reverts are logged. |
| D10 | Variance threshold tuning | Start at 15% / 50%. Surface a counter on the wq-099 dashboard: "Last 30 days: X auto-applied, Y went to review, Z anomalies." If the auto-apply rate is too low (everything goes to review) or too high (Simon overrides often), tune the thresholds in a follow-on. Don't optimise pre-launch. |

No open decisions. Implement directly.

---

## §1 — Goal

Reviewing a claim takes one click; the result publishes within 5 minutes; routine high-confidence claims auto-apply without bothering Simon at all; everything that needs his eyes is queued cleanly with the relevant context surfaced. After this brief: zero browser-download handoffs, zero 23-hour cron-wait windows, and Simon's review queue contains only the claims that actually need a human.

---

## §2 — Files touched

### Modified
- `claims.html` — replace browser-download submit path with `admin_server.py` POST. Add the new card affordances per D7. Add the override action per D9.
- `review.html` — same as above (server-side writes if not already, plus consistent card affordances).
- `scripts/admin_server.py` — add POST endpoints: `/api/decision`, `/api/override`. Add file-watcher trigger for `apply_pipeline.py`.
- `scripts/apply_pipeline.py` (built in wq-098) — extend with variance-gate logic per D3/D4/D5. Auto-apply path runs without human intervention; human-review path leaves claim in `pending_review` state.
- `scripts/auto_update.py` — keep nightly cron as a safety net, but real-time apply is the new primary path.

### New
- `data-updates/decisions/` (directory) — server-side decision JSON files, one per review session.
- `scripts/decision_watcher.py` (or hooks into admin_server.py) — file-watcher that triggers `apply_pipeline.py` when a new decision lands.

### Validators
- `scripts/release-check.mjs` — assert: (a) no browser-download code path remains in claims.html/review.html submit logic, (b) auto-apply variance gate has unit test coverage, (c) override action writes a reversal record visible in the apply log.

---

## §3 — Acceptance criteria

1. **Server-side writes work.** Submitting from claims.html or review.html writes to `data-updates/decisions/` via `admin_server.py` POST. No browser file downloads. Verify via network inspector.
2. **Auto-apply gate enforced** per D3. Unit tests confirm: verified+tier_1B+5%-variance auto-applies; verified+tier_1B+20%-variance routes to review; tier_3A always routes to review.
3. **First-time entity gate** — synthetic test: claim for a brand-new entity routes to review even if it would otherwise pass D3.
4. **5-minute apply latency** — submit a decision, observe `apply_pipeline.py` runs and entityDirectory updates within 5 minutes (file watcher) or on next short cron (max 5 min).
5. **Card affordances** — both UIs show old/new/variance/source/provenance for each claim. Verify visually at desktop and 375px.
6. **Override action works.** Click "override last apply", verify entityDirectory reverts and claim returns to review queue. Reversal logged.
7. **Auto-apply log on Pipeline tab** — wq-099 dashboard shows recently-auto-applied claims (last 24h) with diff visible.
8. **Counter on dashboard** per D10. Last 30 days: auto-applied / review-routed / anomaly counts.
9. **No regression** — `npm run release-check` passes; no broken existing review functionality.
10. **Deployment record** at `docs/deployments/deploy-YYYY-MM-DD-wq-100-review-surface-hardening.md`.

---

## §4 — Implementation outline

### Phase A — admin_server.py extension (0.5 session)

1. Add `POST /api/decision` endpoint — receives decision JSON, writes to `data-updates/decisions/{date}-{ui}-{ts}.json`. Returns success.
2. Add `POST /api/override` endpoint — receives entity + field + revert-to value. Logs reversal. Triggers re-review.
3. Add file-watcher (or short-cron alternative) on `data-updates/decisions/` that invokes `apply_pipeline.py` on new files.
4. Document the new endpoints in admin_server.py header comment.

### Phase B — Variance gate in apply_pipeline.py (0.5 session)

1. Extend `apply_pipeline.py` (built in wq-098) with the gate logic per D3/D4/D5.
2. Auto-apply path: claim meets all conditions → apply directly, mark `usedOn: ["entityDirectory:auto"]`, log to apply log.
3. Human-review path: claim fails any condition → leave in vault with `pending_review: true` flag, queue for human surface.
4. Anomaly path: variance >50% → also write to `data/audits/anomalies-YYYY-MM-DD.md` for Simon's morning glance.

### Phase C — Review UI updates (0.75 session)

1. Replace browser-download submit logic in claims.html with `admin_server.py` POST.
2. Same in review.html.
3. Add card affordances per D7: old/new/variance/source/provenance visible inline.
4. Add "override last apply" action — POSTs to `/api/override`.
5. Mobile sanity at 375px.

### Phase D — Dashboard integration with wq-099 (0.25 session)

1. Extend `reconcile_pipeline.py` (from wq-099) to surface auto-apply / review-routed / anomaly counts in `pipeline-health-latest.json`.
2. Pipeline tab on status.html renders the counter.
3. Add "Recently auto-applied (last 24h)" card listing diffs.

### Phase E — Verify & ship (0.25 session)

1. `npm run build-lint` passes.
2. `npm run release-check` passes including new gate assertions.
3. Manual smoke: submit a low-tier claim, verify routes to review. Submit a high-tier claim with <15% variance, verify auto-applies within 5 min. Override one, verify revert.
4. Write deployment record.
5. Push to main after Simon's chat approval.

**Total estimate: ~2 sessions.**

---

## §5 — Edge cases

1. **admin_server.py not running.** UI shows a clear error: "Admin server not running. Start it with `python3 scripts/admin_server.py` and try again." Does NOT silently fall back to browser download (defeats the purpose).

2. **Concurrent edits.** Two reviewers (or two browser tabs) submit conflicting decisions. Last-write-wins by timestamp. Override action available if a wrong call propagates.

3. **Variance gate mis-fires on near-zero baselines.** If entityDirectory has $0.01B and a new claim says $0.05B, that's a 400% variance but $40M absolute. Add absolute-magnitude floor: variance gate only applies when both old and new are ≥$50M. Below $50M, default to human review.

4. **First-time entity for a known multi-tier company.** Microsoft adds Microsoft Fabric AI as a new product. entityDirectory has microsoft_m365_copilot, microsoft_github_copilot, microsoft_azure but no microsoft_fabric_ai. First-time gate fires correctly — routes to review.

5. **Auto-applied claim is later corrected.** Override action available. Reversion logged. The corrected claim then re-runs through the gate (typically routes to review because variance from the now-updated value is small).

6. **File-watcher doesn't fire on macOS / Linux differences.** Provide a short-cron fallback (every 5 min) as belt-and-braces. apply_pipeline.py is idempotent so running both is safe.

---

## §6 — Test plan

1. Unit tests for variance gate: each branch of D3 / D4 / D5 with synthetic input.
2. Integration test: submit decision via admin_server.py POST, verify file written, verify apply runs.
3. Integration test: override action reverts entityDirectory correctly and re-queues the claim.
4. Manual: open both UIs at desktop and 375px. Verify card affordances.
5. Manual: synthetic anomaly (variance >50%) — verify dashboard shows anomaly card.

---

## §7 — Out of scope

- External notifications (email/Slack when human review accumulates) — wq-099 morning-glance covers this for now.
- Bulk actions on review queue — review.html already has these from wq-023; not extending.
- Cross-UI unification — keeping the two review surfaces by design (D1).
- Mobile-first review experience — admin pages are desktop-primary; basic mobile sanity only.
- Multi-user review (different users with different permissions) — single-reviewer assumption (Simon).

---

## §8 — Definition of done

1. All §3 acceptance criteria met.
2. Variance gate unit-tested across all branches.
3. Manual smoke confirms 5-minute apply latency end-to-end.
4. `npm run release-check` passes with new assertions.
5. Deployment record written.
6. Branch merged after Simon's chat approval.
7. Notion Kanban card moved to Done. Pipeline program (wq-098/099/100) complete.

---

## §9 — Handoff prompt for VS Code / Claude Code

> Paste the block below into a fresh VS Code Claude Code session.

```
Implement wq-100 — Review Surface Hardening: Server-Side Decisions + Auto-Apply with Variance Gate.

Read in order:
1. /Users/simonbowker/Developer/apac-ai-intel/CLAUDE.md
2. /Users/simonbowker/Developer/apac-ai-intel/TAIL-WORKFLOW-PROTOCOL.md
3. /Users/simonbowker/Documents/Claude/Projects/The AI Ledger/PIPELINE-SCOPING-2026-05-08.md (parent context)
4. /Users/simonbowker/Developer/apac-ai-intel/docs/briefs/wq-100-review-surface-hardening.md (canonical brief)

Context: TAIL has two review surfaces (review.html for bulk inbox, claims.html for curated intake) — keep both, they handle different ingestion shapes. This brief fixes the workflow: kill the browser-download handoff (server-side decision writes via admin_server.py), add a variance gate that auto-applies high-confidence small-variance changes (verified + tier_2A+ + variance <15% + same-or-higher provenance), keep human review for everything else.

Depends on: wq-098 (apply_pipeline.py must exist).

The brief is fully scoped — 10 decisions resolved 2026-05-08. Implement Phases A through E sequentially. Estimated ~2 sessions.

Critical reminders:
- Keep both review surfaces. Don't collapse claims.html and review.html.
- Variance gate has 4 conditions (D3) — all must pass for auto-apply. First-time entity values ALWAYS go to human review (D4) regardless.
- Variance bands: <15% auto-apply, 15-50% review, >50% review + anomaly flag.
- Absolute-magnitude floor: variance gate only applies when both old and new ≥$50M. Below that, always review.
- Apply latency target: 5 minutes via file watcher on data-updates/decisions/.
- admin_server.py must be running during review sessions; fail loudly if not (don't fall back to browser download).
- Override action available so Simon can revert wrong auto-applies.

When done, push to main after my chat approval, update Notion card, and close out the wq-098/099/100 program.
```

---

*End of brief.*
