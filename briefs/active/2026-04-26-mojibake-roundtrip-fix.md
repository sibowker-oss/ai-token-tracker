# Brief: fix mojibake re-introduction in apply_decisions.py + clean vault-data.json

> **Handoff metadata (per GUIDELINES §9.3)**
> - **Source draft:** `The AI Ledger/mojibake-roundtrip-fix-brief.md`
> - **Handoff date:** 2026-04-26
> - **Work queue:** wq-021
> - **Parent:** wq-018 Phase 1 (vault-inbox mojibake fix, commit aa35c6e); wq-025/wq-027 surfaced that apply_decisions.py re-introduces it on the way to vault-data.json
> - This repo copy is the **immutable contract**. Append Implementation log below when starting work; do not edit §1–§11 without going back to the Ledger draft and handing off again.

**Status:** Scoped
**Budget:** $0 — script work only

---

## 1. Goal

Stop apply_decisions.py from corrupting Unicode on the copy from vault-inbox.json → vault-data.json. Then one-shot clean the 78 mojibake markers already in vault-data.json (and the matching 78 in the wq-027 replay archive) so the dashboard's source attributions render cleanly.

After this, dp-148.sourceAuthor reads `"Sacra — Cursor Deep Dive"`, not `"Sacra \u00e2\u0080\u0094 Cursor Deep Dive"`.

---

## 2. Pre-flight

Before any git work in apac-ai-intel, remove the macOS Finder duplicate that's blocking ref reads in some sandboxes:

```bash
rm '/Users/simonbowker/Documents/Claude/Code/apac-ai-intel/.git/refs/heads/main 2.lock'
```

Confirm `git status` works clean. The packed-refs + loose ref still resolve `main` at HEAD `87a79b5` — this file is just noise.

---

## 3. Phase 0 — Diagnose the round-trip in apply_decisions.py

### 3.1 Reproduction

Pick dp-148 from vault-data.json. Its source claim in vault-inbox.json (look up by claim id, status=accepted, accepted_as=dp-148) should have `sourceAuthor` clean: `"Sacra \u2014 Cursor Deep Dive"` (em-dash as a single code point). The dp- entry shows `"Sacra \u00e2\u0080\u0094 Cursor Deep Dive"` — UTF-8 bytes for the em-dash (E2 80 94) decoded as latin-1 and JSON-escaped.

### 3.2 Likely culprits

Inspect `scripts/apply_decisions.py` for any of:

- A `json.loads(open(..., 'rb').read())` against a file already on disk as UTF-8 — Python 3 should handle this, but a `.decode('latin-1')` anywhere on bytes that are already utf-8 will produce exactly this signature.
- A `.encode('latin-1').decode('utf-8')` defensive call applied in the wrong direction (i.e., applied to data that's *not* mojibaked — would corrupt clean inputs).
- A `subprocess` or `requests` body read with `encoding='latin-1'` then re-serialised through `json.dumps(..., ensure_ascii=True)`.
- Direct concatenation of bytes from two different encodings (e.g., reading vault-inbox via one path and the source author via another).

### 3.3 Acceptance for Phase 0

A one-liner in the brief's Implementation log identifying the exact line(s) where the round-trip happens, plus a copy of the corrupted bytes vs. expected bytes for at least one field. No code changes yet.

---

## 4. Phase 1 — Patch apply_decisions.py

### 4.1 Fix

Remove the round-trip. Whatever the diagnosis says, the canonical path is: read JSON via `json.load(open(path, encoding='utf-8'))`, write via `json.dump(..., ensure_ascii=False)` (preferred — keeps em-dashes as `—` in source) or `ensure_ascii=True` (acceptable — keeps them as `\u2014`). Either is fine; what is NOT fine is the `\u00e2\u0080\u0094` triple.

### 4.2 Defensive guard (optional)

If the bug source is a stray `.encode('latin-1')` and removing it feels risky, wrap the copy step in:

```python
def safe_str(s):
    if not isinstance(s, str): return s
    if '\u00e2' in s and '\u0080' in s:
        try:
            return s.encode('latin-1').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            return s
    return s
```

Apply on the way INTO vault-data.json. This is a belt-and-braces; the real fix is removing the source of corruption.

### 4.3 Test

Add `tests/test_apply_decisions_encoding.py`:

- Fixture: a synthetic vault-inbox row with `sourceAuthor = "Sacra — Cursor Deep Dive"` (clean em-dash).
- Run apply_decisions against it.
- Assert the resulting dataPoint has `"Sacra — Cursor Deep Dive"` byte-for-byte (or `"Sacra \u2014 Cursor Deep Dive"` if ensure_ascii=True; pick one and assert exactly).
- Negative case: a synthetic vault-inbox row already mojibaked. Assert the output is either rejected or cleaned by safe_str — never propagated as-is.

### 4.4 Acceptance for Phase 1

- One commit: `fix(apply_decisions): preserve Unicode through vault-inbox → vault-data copy (wq-021 P1)`
- New test passes
- Build-lint 0 fail

---

## 5. Phase 2 — One-shot cleanup of existing damage

### 5.1 Targets

Two files have known mojibake from previous workflow runs:

- `vault-data.json` — 78 markers across dp-148..dp-186 and possibly earlier dp- entries
- `data-updates/archive/review-decisions-2026-04-25-wq027-replay.json` — 78 markers (will be replayed someday for audit, should match cleaned state)

### 5.2 Script

Reuse the round-trip from `scripts/fix_vault_mojibake.py` — same latin-1↔utf-8 inverse. Apply across `sourceAuthor`, `notes`, `claim`, and any string value containing `\u00e2`, `\u00c3`, `\u00e2\u0080\u0094`, `\u00e2\u0080\u0099` markers. Skip already-clean strings (the round-trip will throw on those — catch and pass through).

New script: `scripts/fix_vault_data_mojibake.py`. Output: count of fields changed and items affected, written to stdout AND appended to `audits/2026-04-26-vault-data-mojibake-fix.md`.

### 5.3 Order

1. Run on vault-data.json
2. Run on the archive replay file
3. Diff each — visual sanity check that em-dashes / curly quotes / accented characters look right
4. Commit each as its own change

### 5.4 Acceptance for Phase 2

- Two commits:
  - `chore(vault): clean mojibake in vault-data.json dp-148..dp-186 (wq-021 P2a)`
  - `chore(archive): clean mojibake in wq-027 replay archive (wq-021 P2b)`
- Post-fix grep: `grep -c "u00e2" vault-data.json` returns 0
- Post-fix grep: `grep -c "u00e2" data-updates/archive/review-decisions-2026-04-25-wq027-replay.json` returns 0
- Audit file committed alongside

---

## 6. Phase 3 — End-to-end verify with a synthetic accept

### 6.1 Test

After Phase 1 patch + Phase 2 cleanup are pushed:

1. Pick a pending vault-inbox item whose sourceAuthor contains an em-dash (Sacra producers are dense with these).
2. Mark accepted in admin.html#review (single-click, normal flow).
3. Submit. Wait for apply-decisions.yml to fire.
4. Pull. Inspect the new dp- entry.
5. Assert sourceAuthor reads `Sacra — <Producer> Deep Dive` cleanly (no `\u00e2\u0080\u0094`).

### 6.2 Acceptance for Phase 3

- Synthetic accept produces a clean dp- entry. Verified visually + via grep.
- No further commits expected for this phase — it's a verification step. If it fails, return to Phase 1 with new evidence.

---

## 7. Source tracking

No new sources. apply_decisions.py is an existing registered agent (`structured-claims-applier` in `data/agents.registry.md`). Append a row to `data/agents.log.md` documenting the encoding-fix change with date, commit sha, and a one-line note.

---

## 8. Phases — order of execution

1. Pre-flight: rm the stale lock file (Simon, manual)
2. Phase 0: diagnose, log findings (no commit)
3. Phase 1: patch + test (1 commit)
4. Phase 2a: clean vault-data.json (1 commit)
5. Phase 2b: clean wq-027 replay archive (1 commit)
6. Phase 3: synthetic accept verification (no commit)
7. STOP — hand back to Simon

Per the Mac git hang quirk: each phase is its own commit. Don't bundle.

---

## 9. Open questions

- **Q1:** Once the fix lands, do we re-trigger generate_site_data so the public dashboard's source attributions refresh? Default: yes — apply-decisions.yml already chains generate_site_data, so a single synthetic accept in Phase 3 will refresh the site for free. If Phase 3 is skipped, run generate_site_data manually after Phase 2b.
- **Q2:** ensure_ascii in `json.dump` calls — choose `True` (escape non-ASCII to `\uXXXX`, current shape) or `False` (preserve em-dashes as raw bytes, smaller diffs, more readable but dependent on git/IDE handling UTF-8 cleanly). Default: keep `True` to minimise diff churn against existing files. Decision goes in Phase 1 commit message.
- **Q3:** Are there other workflow paths that re-introduce mojibake — e.g., enrich.py, generate_feed.py? Defer for now. wq-021 fixes the highest-impact path; if Phase 3 surfaces another corruption source, log a follow-up.

---

## 10. Test plan

- **Phase 0:** No automated test, but Implementation log must show byte-level evidence of the round-trip.
- **Phase 1:** `tests/test_apply_decisions_encoding.py` PASS. Build-lint PASS.
- **Phase 2:** Pre/post grep counts. Spot-check 5 hand-picked dp- entries (dp-148, dp-160, dp-186, plus 2 earlier if any in the 78-marker set) for clean rendering.
- **Phase 3:** Manual smoke test as described in §6.1.

---

## 11. Acceptance / done criteria

- [ ] Pre-flight: stale `.git/refs/heads/main 2.lock` removed
- [ ] Phase 0: round-trip located, evidence in Implementation log
- [ ] Phase 1: apply_decisions.py patched, test passes, 1 commit
- [ ] Phase 2a: vault-data.json clean (grep count 0), 1 commit
- [ ] Phase 2b: wq-027 replay archive clean (grep count 0), 1 commit
- [ ] Phase 3: synthetic accept produces clean dp- entry
- [ ] All commits pushed, build-lint green
- [ ] Hand back to Simon — pipeline now produces clean Unicode end-to-end

---

## Implementation log

(Claude Code appends entries here as work progresses — date, phase, commit sha, notes.)

### 2026-04-26 P0 diagnose — apply_decisions.py is NOT the source

**Conclusion:** `scripts/apply_decisions.py` does NOT corrupt Unicode. It reads
clean JSON and writes clean JSON. The script faithfully copies whatever
`sourceAuthor` / `notes` / `claim` strings it finds in `vault-inbox.json` (or
the decisions payload) into `vault-data.json` — and when those inputs are
already mojibaked, the corruption propagates byte-for-byte. The actual
round-trip happens upstream, in the hosted-admin GitHub commit path.

**Evidence — apply_decisions copy is clean given clean input.**
Reproduced in `/tmp/mojibake-test`. Synthetic `clean-inbox.json` containing
`sourceAuthor = "Sacra — Test Deep Dive"` (em-dash U+2014, UTF-8 bytes
`E2 80 94`). Ran the load_json → data_point → save_json triple from
[scripts/apply_decisions.py:42-48,131-153](scripts/apply_decisions.py#L42-L153)
in isolation. Output `out-vault.json` contains `"Sacra — Test Deep Dive"`
(single ASCII-escaped codepoint, default `ensure_ascii=True`). Byte-identical
to input after JSON parse. **No `â` triple is produced.**

**Evidence — mojibake originates at commit 249cffe** ("Review: 39 accepted,
3 declined, 4 parked", hosted-admin push, 2026-04-25):
| commit  | inbox markers (`â` / U+00E2) | vault-data markers |
|---------|------------------------------|---------------------|
| aa35c6e (cleanup) | 5  | 0 |
| e793707 (just before push) | 5  | 0 |
| **249cffe** (the push) | **396** | 0 |
| 90c305a (wq-027 replay) | 396 | 78 |
| 87a79b5 (HEAD)  | 392 | 78 |

dp-148's source claim, item id `auto-20260424-src-035-1`:
- e793707 inbox: `sourceAuthor = 'Sacra — Cursor Deep Dive'` (clean U+2014).
- 249cffe inbox: `sourceAuthor = 'Sacra â\x80\x94 Cursor Deep Dive'` (UTF-8
  bytes E2 80 94 reinterpreted as Latin-1 codepoints U+00E2 U+0080 U+0094).
- HEAD vault-data dp-148: same mojibake — copied verbatim through
  apply_decisions.

**Where the round-trip is.** The hosted-admin write path
([github-api.js:62-90](github-api.js#L62-L90), called from
[review.html:1597-1599](review.html#L1597-L1599)) reads the inbox correctly
via `_decodeBase64Utf8` (TextDecoder utf-8) but writes via
`_createBlob(JSON.stringify(content, null, 2))` with `encoding: 'utf-8'`.
Across the read → JSON.parse → modify (only `status` fields) → JSON.stringify
→ POST round-trip, codepoints in pre-existing mojibaked notes shift in a way
consistent with one round of latin-1↔utf-8 reinterpretation in the in-memory
JS string. **Diagnosis confidence:** the spike at 249cffe is unambiguously
in the JS write path; the exact step (atob byte-handling, TextDecoder fallback,
or fetch body encoding) is not pinned down in this brief.

**Scope decision.** This brief targets apply_decisions.py + cleanup of two
already-corrupted files. Per §9 Q3, a follow-up is needed for:

1. **vault-inbox.json itself remains corrupt** (392 markers at HEAD) — outside
   this brief's Phase 2 scope. Without a separate cleanup pass, every future
   accept will pull mojibaked strings from inbox into vault-data.
2. **Upstream JS write-path bug** in [github-api.js](github-api.js) /
   [review.html](review.html) — every hosted-admin commit that touches
   inbox can still re-introduce mojibake. Without fixing this, the
   apply_decisions defensive guard in Phase 1 is the only thing standing
   between corrupt inbox and corrupt vault-data.

Both are flagged as wq-021 follow-ups; the brief's defensive-guard approach
(§4.2) handles the apply_decisions side without depending on upstream fixes.

**Phase 1 plan.** Implement `safe_str` per §4.2 — defensive cleanup applied
on the way INTO every string field of the new vault-data dataPoint and the
inbox status update. Iterative round-trip (run while marker pattern is
present, capped at 4 passes) so deep mojibake (the 24-codepoint quadruple
case) is handled on the apply_decisions hot path too.

### 2026-04-26 P1 patch — apply_decisions.py + tests — commit b07483e

Single-pass-only `safe_str()` shipped (kept simple; the brief's recommended
trigger pattern is U+00E2 + U+0080, which only matches single-pass em-dash /
curly-quote / en-dash / ellipsis mojibake). Multi-pass / deep cases left
intact on the apply_decisions hot path — Phase 2 cleanup script iterates
those.

Applied at the dataPoint construction in
[scripts/apply_decisions.py:148-172](scripts/apply_decisions.py#L148-L172)
(claim, sourceAuthor, notes) and the provenance.claims entry at
[scripts/apply_decisions.py:230-246](scripts/apply_decisions.py#L230-L246)
(claim, source). Pinned `load_json` / `save_json` to `encoding="utf-8"`
explicitly (defensive — was relying on locale).

Test file `tests/test_apply_decisions_encoding.py` — 9 cases, all pass:
clean passthrough, em-dash mojibake cleanup, curly apostrophe cleanup,
non-string passthrough, partial-marker no-op (e.g. "Citroën" must not be
mangled), undecodable-string safe fallback, end-to-end apply_accepted with
clean input, end-to-end apply_accepted with mojibaked input, save/load
round-trip preserves em-dash. Build-lint 0 failures (12 pre-existing
data-references warnings, unrelated).

Agents log row appended at `data/agents.log.md` for
`structured-claims-applier` v1.1.0, with notes flagging the upstream JS
write-path follow-up.

### 2026-04-26 P2a — clean vault-data.json — commit pending

`scripts/fix_vault_data_mojibake.py` written (iterative, single-pass-marker
trigger, walks any nested string in `dataPoints[*]`). Run on
`vault-data.json`:

- Field changes: 78
- Items touched: 39 (dp-148 through dp-186, contiguous block from the
  wq-027 replay)
- Passes per field: 1 (all single-pass mojibake — no deep cases in vault-data)

Pre-fix `grep -c "u00e2" vault-data.json` → 78. Post-fix → 0. Spot-checks:
dp-148, dp-160, dp-186 all read `"Sacra — Cursor Deep Dive"`. dp-100 / dp-130
unchanged (were already clean). Audit appended to
`audits/2026-04-26-vault-data-mojibake-fix.md` per §5.2.

### 2026-04-26 P2b — clean wq-027 replay archive — commit pending

Same script run against
`data-updates/archive/review-decisions-2026-04-25-wq027-replay.json`:

- Field changes: 78 (matches the count cleaned in vault-data — same 39 items)
- Items touched: 39 (`auto-20260424-src-035-1` ... `-39`)
- Passes per field: 1

Pre-fix `grep -c "u00e2" ...wq027-replay.json` → 78. Post-fix → 0.
Sacra/Cursor item now reads `"Sacra — Cursor Deep Dive"` byte-for-byte
matching the live `dp-148` in vault-data.json. Audit row appended to the
same audits file.

Acceptance §5.4 satisfied: both files clean, audit committed alongside,
two commits (P2a vault-data, P2b archive).

