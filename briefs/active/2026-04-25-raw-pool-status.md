# Brief: Raw pool status — three-state Accept

> **Handoff metadata (per GUIDELINES §9.3)**
> - **Source draft:** `The AI Ledger/raw-pool-status-brief.md`
> - **Handoff date:** 2026-04-25
> - **Work queue:** wq-022 (audit) + wq-023 (implementation)
> - **Parent:** wq-018 (first batch review surfaced the orphan-accept problem)
> - This repo copy is the **immutable contract**. Append Implementation log below when starting work; do not edit §1–§10 without going back to the Ledger draft and handing off again.

**Status:** Scoped
**Budget:** $0

---

## 1. Goal

Stop the inbox from accepting claims that go nowhere. Today, status=accepted has two meanings depending on whether the claim's `metric` field maps to a live data point: known-metric Accepts overwrite the data point with full provenance; unknown-metric Accepts sit in vault-inbox.json with status=accepted but render nowhere on the site. They are filed, not used.

Per Ledger goal — *"the numbers should form the opinions with the reader"* — orphan-Accepts are dead weight. Add a fourth status (`raw_pool`) that explicitly captures *trustworthy but unmapped* claims, separate from *trustworthy and surfaced*.

After this ships, an Accept means the claim actually moves a number on the site. Raw pool means the claim is good but doesn't have a slot yet.

---

## 2. Phase 0 — Audit current accepts (wq-022)

Before writing code, count the damage. Report the following for vault-inbox.json:

1. Of the 46 items most recently accepted (wq-018 first batch — accept dates 2026-04-25), how many had `metric` ≠ "unknown" / null / missing?
2. For those metric-known items, confirm they actually updated a corresponding entry in `data/site-data.json`. Spot-check 3 — read the data point's current value and provenance; should show the recently-accepted claim.
3. For metric-unknown items, list the claim ids — these are the migration candidates for Phase 3.
4. Total accepts in vault-inbox.json (currently 161). Repeat the metric-known vs metric-unknown split across all 161, not just the 46. This tells us the broader scope of orphan-Accepts beyond the recent batch.

Output: `audits/2026-04-25-orphan-accepts.md` with the counts and the migration-candidate list.

---

## 3. Phase 1 — Schema + writer

### 3.1 Add `raw_pool` as valid status

Update wherever vault-inbox.json statuses are validated:

- `metric-schema.json` — add to status enum
- `apply_claims.py` STATUS_VALUES (or equivalent constant)
- `validate-provenance.mjs` if it checks status values

### 3.2 apply_claims.py behaviour

When apply_claims.py processes claims for site-data.json updates, it should:

- Read items with status=accepted as it does today (these now MUST have known metrics; if any have metric=unknown, log a warning — they shouldn't exist after Phase 3 migration).
- Skip items with status=raw_pool entirely. They're not for the site.
- Preserve existing decline/park behaviour unchanged.

### 3.3 Acceptance criteria

- Schema enum includes raw_pool.
- apply_claims.py runs against current vault and produces the same site-data.json as before (no regressions).
- Tests in tests/test_claim_schema.py extended to cover raw_pool — at minimum, a sample item with status=raw_pool round-trips through validation.

---

## 4. Phase 2 — Review UI (review.html)

### 4.1 Fourth button

Add a "Raw pool" button to each claim card alongside Accept / Decline / Park. Suggested colour: blue/teal (different from Accept's green). Keyboard shortcut: `r`.

### 4.2 Auto-route prompt on Accept-with-unknown-metric

When user clicks Accept on an item where `metric` is unknown / null / missing:

- Show a one-time-per-session modal: *"This claim has no mapped metric. Accepts are reserved for claims that update a live data point. Move to Raw pool instead?"*
- Two actions: **Move to Raw pool** (default) and **Override and Accept anyway** (with a "are you sure?" confirm).
- Per-session sticky: once user picks an action, don't ask again for the rest of the session — apply the same default.

### 4.3 Filter chip

Add a "Raw pool (N)" filter chip in the bottom status row, next to Pending / Parked / Accepted / Declined / All.

### 4.4 Stats pill

Add a stat-pill at the top: `Raw pool: <count>`. Same styling as Accepted/Declined/Parked but neutral colour (e.g., grey or blue).

### 4.5 Acceptance criteria

- Fourth button visible on every claim card; click sets status=raw_pool, persists via existing saveDecisions → localStorage → Submit → GitHubAPI.commitFiles flow.
- Auto-route prompt fires exactly once per session per direction.
- Filter chip and stat-pill counts match the underlying data.
- Submit pushes Raw pool decisions back to vault-inbox.json the same way Accept does.

---

## 5. Phase 3 — Migrate orphan-Accepts to Raw pool

### 5.1 Migration script

`scripts/migrate_orphan_accepts.py`:

- Read vault-inbox.json.
- For every item with status=accepted AND metric in {unknown, null, missing}, set status=raw_pool.
- Preserve all other fields. Add a top-level `migration_note: "wq-023 Phase 3 — moved from accepted to raw_pool because metric was unmapped at accept time"` per item.
- Output: count of items migrated.

### 5.2 Acceptance criteria

- After migration: zero items with status=accepted AND metric=unknown.
- The Phase 0 audit candidate list maps 1:1 to the migrated set.
- Commit message: `chore(vault): migrate N orphan-accepts to raw_pool (wq-023)`.

---

## 6. Out of scope (deferred)

- **Promotion flow** raw_pool → accepted (when a slot is later created). Defer to its own work-queue item if/when needed.
- **Surfacing raw pool elsewhere** — e.g., podcast prep, analyst notes, future charts. Raw pool exists, that's enough for v1.
- **Bulk re-categorisation UI** for raw pool items. v1 ships individual click-to-promote; bulk later if friction warrants.

---

## 7. Phases — order of execution

1. **Phase 0** audit (commit: `audit(vault): orphan-accept count for wq-022/wq-023`)
2. **Phase 1** schema + writer (commit: `feat(vault): raw_pool status (wq-023 P1)`)
3. **Phase 2** review.html UI (commit: `feat(review): raw pool button + filter + auto-route prompt (wq-023 P2)`)
4. **Phase 3** migrate orphan-accepts (commit per §5.2)
5. **STOP** — hand back to Simon to verify in admin.html#review and resume the next batch of pending claims.

Per Simon's Mac git hang quirk: each phase is its own commit. Don't bundle.

---

## 8. Open questions

- **Q1:** "Override and Accept anyway" path in §4.2 — keep it (escape hatch for genuine edge cases) or remove (force discipline)? Default: keep for v1, remove later if abused.
- **Q2:** Does any existing tooling (build-lint, validate-provenance) treat status=accepted as an invariant for "must have a metric"? If so, add raw_pool to the same check or carve raw_pool out explicitly.
- **Q3:** What about items currently parked because of unknown metric? Worth a one-time pass to reclassify those as raw_pool too, or leave parked for v1? Default: leave parked. Park is an intentional user action.

---

## 9. Test plan

- **Phase 0:** Manual review of audits/ output.
- **Phase 1:** Unit test extension in tests/test_claim_schema.py — raw_pool round-trips through validation. apply_claims.py regression: snapshot diff of site-data.json before/after a no-op run = empty.
- **Phase 2:** Manual smoke test on localhost — click Raw pool, confirm count increments, Submit, pull, confirm vault-inbox.json updated. Click Accept on a metric=unknown item, confirm prompt fires; choose default; confirm subsequent Accepts of unknown-metric items in same session auto-route silently.
- **Phase 3:** Pre/post counts. Pre: N accepts with metric=unknown. Post: 0 accepts with metric=unknown, N raw_pool entries new.
- **Build-lint** must pass with zero failures after each phase commit.

---

## 10. Acceptance / done criteria

- [ ] Phase 0: audit report committed to `audits/2026-04-25-orphan-accepts.md`
- [ ] Phase 1: schema + writer recognise raw_pool, 1 commit
- [ ] Phase 2: fourth button + filter chip + stat-pill + auto-route prompt live in review.html, 1 commit
- [ ] Phase 3: orphan-accept migration committed, vault-inbox.json shows zero accepted+unknown-metric, 1 commit
- [ ] All commits pushed, build-lint green
- [ ] Hand back to Simon

---

## Implementation log

(Claude Code appends entries here as work progresses — date, phase, commit sha, notes.)
