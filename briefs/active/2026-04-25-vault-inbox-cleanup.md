# Brief: vault-inbox cleanup + first-batch review prep

> **Handoff metadata (per GUIDELINES §9.3)**
> - **Source draft:** `The AI Ledger/vault-inbox-cleanup-brief.md`
> - **Handoff date:** 2026-04-25
> - **Work queue:** wq-018
> - **Parent:** wq-015 (Stream 1 activation; produced the 336-claim haul)
> - This repo copy is the **immutable contract**. Append Implementation log below when starting work; do not edit §1–§10 without going back to the Ledger draft and handing off again.

**Status:** Scoped
**Budget:** $0 — all script work, no external calls

---

## 1. Goal

Make `vault-inbox.json` reviewable. Today there are **336 pending claims** from the wq-015 sweep. Two pre-existing data quality bugs make hand-review polluting:

1. **Mojibake in 205/336 `sourceAuthor` fields** — UTF-8 was double-encoded somewhere in the extractor pipeline. `Sacra — OpenAI` reads as `Sacra Ã¢â‚¬â€ OpenAI`.
2. **Unparseable `dateOfClaim` in 324/336** — extractor emitted `2026-Q1`, `2024-Q4`, `2023` etc. instead of ISO dates. Vault normalizer will choke when these are accepted.

Fix both before Simon clicks Accept on anything. Then surface a small, high-confidence first batch in admin.html#review so momentum gets going.

---

## 2. Phase 1 — Mojibake fix (script)

### 2.1 Diagnosis

`sourceAuthor` (and likely `notes` and `claim` text in some rows) is UTF-8 bytes that have been decoded as latin-1 then re-encoded as UTF-8. The fix is the inverse: encode as latin-1, decode as utf-8.

```python
def fix_mojibake(s: str) -> str:
    if s is None: return s
    try:
        return s.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s  # already clean
```

### 2.2 Where to apply

Run across every pending item (status != "accepted" and status != "declined") on these fields:
- `sourceAuthor`
- `notes`
- `claim`
- any string field where `Ã` or `â` appears

Do NOT touch already-accepted items — they're frozen, and the live site renders from `data/site-data.json` not vault-inbox anyway.

### 2.3 Acceptance criteria

- After run: zero occurrences of `Ã`, `â€`, `Â` in pending-status items.
- Spot check: `Sacra Ã¢â‚¬â€ OpenAI Deep Dive` becomes `Sacra — OpenAI Deep Dive`.
- Diff is review-able as a single commit titled `fix(vault): unmojibake 205 pending sourceAuthor fields`.

---

## 3. Phase 2 — Date coercion (script + extractor patch)

### 3.1 Diagnosis

Extractor emits `dateOfClaim` values like `2026-Q1`, `Q4 2024`, `2023`. Vault schema expects ISO `YYYY-MM-DD`.

### 3.2 Coercion rules

| Input | Coerced output | Note |
|---|---|---|
| `2026-Q1` / `Q1 2026` | `2026-03-31` | Quarter end |
| `2026-Q2` | `2026-06-30` | |
| `2026-Q3` | `2026-09-30` | |
| `2026-Q4` | `2026-12-31` | |
| `2026` | `2026-12-31` | Year end (most pessimistic for "current as of") |
| `2026-04` | `2026-04-30` | Month end |
| Already ISO | unchanged | |
| Unparseable | leave + log | Surface count for manual fix |

Add a `dateOfClaim_original` field on coerced rows so the original string is preserved in case the rule was wrong.

### 3.3 Where to apply

1. **One-shot fix** on existing 336 pending items in `vault-inbox.json`.
2. **Extractor patch** in `scripts/extract_claims.py` (or wherever the producer is) so future runs emit ISO dates directly. If multiple extractors emit non-ISO dates, fix the common normalization helper.

### 3.4 Acceptance criteria

- Zero pending items with non-ISO `dateOfClaim`.
- `dateOfClaim_original` populated on every row that was coerced — so we have a full audit trail.
- A new run of `monitor_sources.py` against any test source emits ISO dates without any post-processing.

---

## 4. Phase 3 — First-batch surface in admin.html#review

### 4.1 Add a "First batch" filter chip

In `admin.html#review`, add a quick-filter chip labelled **"First batch (30)"** that surfaces only:

- All `PyPI Stats` items (12, all verified) — `sourceAuthor` contains "PyPI"
- All `Jiemian` items (6, all verified) — `sourceAuthor` contains "Jiemian"
- Sacra Cursor items where `confidence == "verified"` (12 of 28) — `sourceAuthor` contains "Cursor" and confidence is verified

Order: PyPI first → Jiemian → Sacra Cursor. Goal: warm-up that should accept at ~90%+ rate.

### 4.2 Persist Simon's review choices

Currently uncertain whether admin.html writes back to vault-inbox.json on accept/decline or just stages locally. Confirm. If not persisting, fix that — Simon needs his decisions saved between sessions or this whole exercise is wasted.

### 4.3 Show count badges

Per-producer count badge next to the filter chip so Simon can see progress: `Sacra OpenAI 63 → 47 (16 reviewed)`.

---

## 5. Phase 4 — Bulk review queues (after first batch)

Once Phase 3 is shipped and Simon has cleared the first 30, add filter chips for the next batches in suggested order:

1. OpenAI Press 31 Mar 25 (30 — 90% verified, but historical 60% accept rate so click-through, not bulk-accept)
2. Sacra OpenAI Deep Dive (63)
3. Sacra Anthropic Deep Dive (53)
4. economics of AI report (42 — unseen producer; verify credibility before bulk-accepting)
5. Sacra Perplexity (26)
6. Coreweave (30) — weak historical signal, save for late
7. AMD IR (16) — weak historical signal
8. 36Kr CN (12) — translation sanity check needed
9. NVIDIA IR (4) + Platformonomics (4) — likely park, all speculative

---

## 6. Source tracking

No new sources added. This brief is operations on existing claims.

If extractor patches in §3.3 change agent behaviour materially, append a row to `data/agents.log.md` for the affected agent (likely `monitor-sources` or whichever extractor variant emitted the bad dates).

---

## 7. Phases — order of execution

1. **Phase 1** mojibake fix (script + commit) — atomic, no UI change.
2. **Phase 2** date coercion (script + commit) — atomic, no UI change.
3. **Phase 3** admin.html First-batch chip + persistence verify — UI change.
4. **STOP and hand back to Simon** — Simon clears first 30 in admin.html#review.
5. **Phase 4** subsequent batch chips, added on demand as Simon finishes each batch.

Per Simon's Mac git hang quirk: each phase is its own commit. Don't bundle.

---

## 8. Open questions

- **Q1:** Should `dateOfClaim_original` be a top-level field or nested under `provenance`? Default: top-level for simplicity; revisit if it pollutes the schema.
- **Q2:** Does admin.html#review currently persist accept/decline back to vault-inbox.json? If no — that's a blocker for the whole review, fix in Phase 3.
- **Q3:** For the 12 unparseable dates that survive coercion, surface them as a "needs manual date" filter in admin.html, or fix by hand once and call it done? Default: count them first, decide.

---

## 9. Test plan

- **Mojibake fix:** before/after diff on 5 hand-picked rows. Asserts: `Ã¢â‚¬â€` → `—`, `Ã©` → `é`, etc.
- **Date coercion:** unit test in `tests/test_date_coerce.py` with the 7 input shapes from §3.2.
- **First-batch chip:** manual smoke test in admin.html — clicking the chip surfaces exactly 30 items, no more no less.
- **Build-lint:** must pass with zero failures after each phase commit.

---

## 10. Acceptance / done criteria

- [ ] Phase 1: 0 mojibake in pending items, 1 commit
- [ ] Phase 2: 0 non-ISO `dateOfClaim` in pending items, 1 commit, 1 extractor patch commit
- [ ] Phase 3: First-batch chip live in admin.html, persistence verified, 1 commit
- [ ] All commits pushed, build-lint green
- [ ] Hand back to Simon with "30 high-confidence claims ready in admin.html#review"

---

## Implementation log

(Claude Code appends entries here as work progresses — date, phase, commit sha, notes.)
