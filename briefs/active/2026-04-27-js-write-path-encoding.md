# Brief: fix the JS write-path encoding bug that mojibakes vault-inbox.json on every hosted-admin commit

> **Status:** **FROZEN 2026-04-27** — copied here from `The AI Ledger/js-write-path-encoding-fix-brief.md` per GUIDELINES §9.3. This is the immutable contract. Append the Implementation log at §11 as work progresses. See companion `2026-04-27-js-write-path-encoding-refresh.md` for scope-refresh notes.
> **Source draft:** `The AI Ledger/js-write-path-encoding-fix-brief.md`
> **Handoff date:** 2026-04-27
> **Work queue:** wq-029
> **Parent:** wq-021 P0 (commit 5cb1fb5) — diagnosed apply_decisions.py is **not** the source of mojibake; the 391-marker spike at commit 249cffe came from the hosted-admin JS write path (review.html → github-api.js → GitHubAPI.commitFiles).

**Status:** Scoped
**Budget:** $0 — JS work + a small amount of HTML / cache-bust plumbing

---

## 1. Goal

Stop the hosted-admin Submit flow from mutating string values in `vault-inbox.json`. After this brief lands, a clean inbox in → clean inbox out, byte-for-byte, regardless of whether the user touched any individual claim.

The wq-021 evidence shows the read-modify-write cycle was rewriting **untouched** items: at e793707 (just before the spike) `auto-20260424-src-033-1.sourceAuthor` was `"Sacra — Anthropic Deep Dive"` (clean U+2014) and `status: pending`; at 249cffe — without any user decision on that item — its sourceAuthor became `"Sacra â Anthropic Deep Dive"` and status was still `pending`. **204 items** were corrupted in that single commit.

The corrupted bytes on disk after 249cffe are `c3 a2 c2 80 c2 94` where the file should hold `e2 80 94`. That signature — three UTF-8 bytes (em-dash) re-interpreted as three Latin-1 codepoints (U+00E2, U+0080, U+0094) and then encoded as UTF-8 — is the canonical "atob without TextDecoder" mistake.

After wq-029 ships, the same Submit click on a clean inbox produces a commit that diffs only on the explicitly-modified `status` / `accepted_as` / `decided_at` fields. No silent string mutations.

---

## 2. Pre-flight

- Confirm the working tree is clean before starting (`git status`). The wq-021 follow-up cleanup of vault-inbox.json itself (392 markers at HEAD) is **out of scope** for this brief — `safe_str`-class cleanup of the live inbox is queued for wq-030.
- Have a hosted preview URL handy. The verification step in §6 needs a real browser session against `https://ai-index.hepburnadvisory.com.au/review.html` (or the equivalent admin path). Local file:// won't reproduce the cache-bust behaviour reliably.
- Read the wq-021 brief Implementation log for context.

---

## 3. Phase 0 — Diagnose where U+2014 becomes U+00E2 U+0080 U+0094

### 3.1 Static trace from review.html through github-api.js

Trace the writeApproved chain. Files at HEAD:

1. `review.html:1565-1602` `writeApproved()`:
   ```
   const inboxFile = await GitHubAPI.readFile('vault-inbox.json');
   const inbox = JSON.parse(inboxFile.content);
   // ...modify only status / accepted_as / lastProcessed...
   const result = await GitHubAPI.commitFiles(
     [{ path: 'vault-inbox.json', content: inbox },
      { path: `data-updates/review-decisions-${todayISO}.json`, content: output }],
     'Review: ' + parts.join(', ')
   );
   ```
   Source-author / notes / claim text are **never touched** in this function — yet they end up corrupted in the resulting commit.

2. `github-api.js:155-172` `readFile()` (post-14e256a) is byte-clean.

3. `github-api.js:148-153` `_decodeBase64Utf8()`:
   ```
   const binary = atob((b64 || '').replace(/\n/g, ''));
   const bytes = new Uint8Array(binary.length);
   for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
   return new TextDecoder('utf-8').decode(bytes);
   ```
   **This is correct.**

4. `github-api.js:74-90` `_createTree()` and `:62-72` `_createBlob()`:
   ```
   // _createBlob:
   body: JSON.stringify({ content, encoding: 'utf-8' })
   ```
   The body is a JS string. JSON.stringify of a JS object with em-dash codepoint produces a JS string with the **raw em-dash character**.

5. `fetch(url, { method: 'POST', body: theString })` with `Content-Type: application/json`. Per the Fetch spec, a USVString body is encoded as UTF-8 → bytes E2 80 94 for em-dash.

### 3.2 What the bytes prove

At commit e793707 the file vault-inbox.json was **pure ASCII** (Python `json.dumps(..., ensure_ascii=True)`). At commit 249cffe the file is partly raw UTF-8 with 396 occurrences of byte sequence `c3 a2 c2 80 c2 94` (mojibaked em-dash).

The transformation U+2014 → U+00E2 + U+0080 + U+0094 is well-defined: encode U+2014 as UTF-8 bytes (E2 80 94), then re-interpret each byte as a Latin-1 codepoint. There is no other way to produce that exact codepoint triple.

### 3.3 Where it must be happening

The chain at HEAD `_decodeBase64Utf8 → JSON.parse → JSON.stringify → fetch(body=USVString) → GitHub git/blobs (encoding:utf-8)` is byte-clean if every step runs. Yet the file was provably mojibaked.

- **(A) Stale browser cache of github-api.js.** The script is loaded via `<script src="github-api.js"></script>` with **no cache-bust query string**. The readFile UTF-8 fix landed at 14e256a (Apr 24 08:09 AEST). 249cffe was 26 hours later. If the user's browser had the page open from before the fix, the in-memory JS was the **pre-14e256a `readFile`** which does `return { content: atob(data.content), sha: data.sha };` — that decodes UTF-8 bytes as Latin-1 codepoints, exactly the observed signature.

- **(B) `beta/github-api.js` still has the broken pre-14e256a readFile.** Confirmed.

- **(C) Subtle bug in the write path we can't see from static analysis.** Lowest probability.

### 3.4 Acceptance for Phase 0

A one-paragraph entry in this brief's Implementation log naming the static result of the trace, plus the byte-level evidence above. Code changes start in Phase 1.

---

## 4. Phase 1 — Patch the write path so it survives stale caches

### 4.1 The fix — switch _createBlob to `encoding:base64`

```js
async function _createBlob(content) {
  const headers = await _headers();
  const utf8Bytes = new TextEncoder().encode(content);  // String → UTF-8 bytes
  let bin = '';
  for (let i = 0; i < utf8Bytes.length; i++) bin += String.fromCharCode(utf8Bytes[i]);
  const b64 = btoa(bin);
  const resp = await fetch(`${API}/repos/${OWNER}/${REPO}/git/blobs`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ content: b64, encoding: 'base64' })
  });
  if (!resp.ok) throw new Error('Failed to create blob: ' + resp.status);
  const data = await resp.json();
  return data.sha;
}
```

Round-trip is now: JS string → TextEncoder UTF-8 → base64 → GitHub stores base64-decoded bytes verbatim → readFile pulls base64 → atob → Uint8Array → TextDecoder UTF-8 → JS string. Every step is bytes-or-codepoints, never "JS string in transit."

### 4.2 The fix — defensive guard before write

Pre-write integrity check at the top of writeApproved (and `autoClearApply`, and `deleteClaim`) that scans the inbox object for the canonical mojibake markers and bails with a useful error rather than committing corruption.

The simplest implementation: take a stable hash of `inbox.items[i].sourceAuthor + .notes + .claim` for each item at page-load time, and re-hash before commit. If a previously-clean field has *gained* mojibake markers between read and write, abort. Pre-existing markers in the file pass through untouched.

### 4.3 The fix — cache-bust the script tag

Both `review.html:1660` and `add.html:96` load `github-api.js` with no version. Replace with:

```html
<script src="github-api.js?v=2026-04-27-wq029"></script>
```

Bump the `?v=` token in the same commit as any future github-api.js change.

### 4.4 The fix — sync or remove `beta/github-api.js`

Default: sync, unless §9.Q2 confirms /beta/ is dead.

### 4.5 Test — `tests/test_github_api_encoding.spec.html`

Three browser-context assertions:
1. Round-trip clean em-dash.
2. Round-trip already-mojibaked em-dash (preserves verbatim).
3. Defensive guard fires on mojibaked input, not on legitimate accents.

### 4.6 Acceptance for Phase 1

- One commit: `fix(github-api): write path uses encoding:base64 + cache-bust + beta sync (wq-029 P1)`.
- New `tests/test_github_api_encoding.spec.html` opens in a browser, prints `PASS — 3/3 cases`.
- Build-lint 0 fail.
- Pre-existing 392 markers in vault-inbox.json untouched (the cleanup is wq-030, not this brief).

---

## 5. Phase 2 — End-to-end verify against the live admin

### 5.1 Test

After Phase 1 ships and Pages deploys:

1. Hard-refresh `https://ai-index.hepburnadvisory.com.au/review.html` (Cmd+Shift+R) to bypass any cached JS.
2. Open DevTools, confirm `github-api.js?v=2026-04-27-wq029` is loaded fresh.
3. Pick any pending item from the inbox (don't change its decision). Click an unrelated Accept on a different item.
4. Click Submit Decisions. Wait for the commit URL to appear.
5. `git fetch && git show <sha>:vault-inbox.json | grep -c "u00e2\|c3 a2 c2"` against the new commit. The **untouched item**'s source strings must be byte-identical to the inbox state before the click.

### 5.2 Acceptance for Phase 2

- The new commit's diff against the previous main shows only the explicitly-modified `status` / `accepted_as` / `decided_at` / `lastProcessed` fields. No mass diff of `sourceAuthor` / `notes` / `claim` lines.
- For an inbox with 392 existing markers, the count after the commit is unchanged.

---

## 6. Source tracking

`github-api.js` is a registered helper, not a registered agent. No row needs to be appended to `data/agents.log.md`. The Phase 1 commit message should reference: "wq-029", the wq-021 P0 finding (commit 5cb1fb5), and the pre-flight pointer to wq-030 for live inbox cleanup.

---

## 7. Phases — order of execution

1. Pre-flight: clean working tree, hosted preview reachable.
2. Phase 0: static trace + byte-level evidence in Implementation log (no commit).
3. Phase 1: §4.1–§4.4 fixes + spec test (1 commit).
4. Phase 2: hard-refresh hosted admin, exercise Submit, diff the resulting commit.
5. STOP — hand back. wq-030 handles the inbox cleanup separately.

Per the Mac git-hang quirk: don't bundle the inbox cleanup into wq-029.

---

## 8. Open questions (resolved at handoff)

- **Q1.** Is the bug stale-cached pre-14e256a JS, or is there an additional code-level bug? Default: ship Phase 1, verify, escalate only if the diff doesn't go away.
- **Q2.** Is `/beta/` still a live entry point? Default: sync.
- **Q3.** Should `_createBlob` switch to base64 for **all** content? Default: all.
- **Q4.** Pre-write defensive guard scope: only **new** markers (compared to a page-load baseline).
- **Q5.** Cache-bust token: hand-edited string, bumped per touched-the-JS commit.

---

## 9. Test plan

- **Phase 0:** No automated test. Implementation log captures byte-level evidence and static-trace conclusion.
- **Phase 1:** `tests/test_github_api_encoding.spec.html` opens in a browser and prints `PASS — 3/3 cases`. Build-lint 0 fail.
- **Phase 2:** Manual smoke against hosted admin per §5.1. Diff acceptance per §5.2.
- **Phase 2 negative case:** Open review.html in a private window (no cache), confirm Network tab shows fresh github-api.js?v=… load. Click Submit on a no-op decision. Confirm the resulting commit's diff is empty or contains only `lastProcessed`.

---

## 10. Acceptance / done criteria

- [ ] Phase 0: static trace + byte-level evidence in Implementation log.
- [ ] Phase 1.1: `_createBlob` switched to `encoding:base64` via TextEncoder + btoa.
- [ ] Phase 1.2: pre-write defensive guard wired into all three commitFiles call-sites in review.html.
- [ ] Phase 1.3: `<script src="github-api.js?v=…">` cache-busted on review.html and add.html.
- [ ] Phase 1.4: `beta/github-api.js` synced to root (or `beta/` tree deleted, per Q2).
- [ ] Phase 1.5: `tests/test_github_api_encoding.spec.html` PASS 3/3, build-lint 0 fail, 1 commit pushed.
- [ ] Phase 2: hosted-admin Submit on an untouched item produces a commit diff with only the modified status fields.
- [ ] Hand back to Simon. Live inbox cleanup (392 markers) follows in wq-030.

---

## 11. Implementation log

### 2026-04-28 — Phase 0 (static trace + byte-level evidence)

**Hypothesis (B) confirmed.** `beta/github-api.js:153` is still pre-14e256a:

```
return { content: atob(data.content), sha: data.sha };
```

No `_decodeBase64Utf8`, no TextDecoder. Any session served from `/beta/review.html`, `/beta/add.html`, or `/beta/sources.html` reads UTF-8 bytes as a raw-byte string (each byte → a Latin-1 codepoint), JSON.parses, mutates status, and writes back via `_createBlob({content, encoding:'utf-8'})`. The Fetch spec encodes the USVString body as UTF-8 — so the three Latin-1 codepoints become six bytes (C3 A2 C2 80 C2 94 for em-dash). Exact mojibake signature observed at 249cffe.

**Hypothesis (A) plausible (cached pre-14e256a JS).** Every page that loads github-api.js does so with no cache-bust:

- `review.html:1660` `<script src="github-api.js"></script>`
- `add.html:96` `<script src="github-api.js"></script>`
- `sources.html:403` `<script src="github-api.js"></script>`
- `beta/review.html:1198`, `beta/add.html:96`, `beta/sources.html:403` — same.

The fix at 14e256a (2026-04-24 08:09 AEST) → next-day 249cffe spike (≈26h later) fits a long-lived admin tab serving cached pre-fix JS through the GitHub Pages default `Cache-Control: max-age=600` window or longer (memory cache holds in-tab indefinitely once loaded).

**Hypothesis (C) ruled out.** Static trace of the post-14e256a write path:

1. `_decodeBase64Utf8` (github-api.js:148-153): atob → Uint8Array(charCodeAt) → TextDecoder('utf-8'). **Byte-clean.**
2. `JSON.parse` of clean UTF-8 string. **Codepoint-clean.**
3. `inbox.items.forEach(...)` mutates only `status` / `decidedAt` / `decisionReason` / `lastProcessed`. **Source strings untouched.**
4. `_createTree` calls `_createBlob` with `JSON.stringify(content, null, 2)` — em-dash codepoint emerges as the literal U+2014 character in the JS string. **Codepoint-clean.**
5. `_createBlob`: `body: JSON.stringify({content, encoding:'utf-8'})` then `fetch`. Fetch spec: USVString body → UTF-8 bytes. **Byte-clean.**
6. GitHub `git/blobs` stores those bytes verbatim under `encoding:'utf-8'`. **Byte-clean.**

Every step preserves codepoints. Bug is *not* in the current root code path.

**Byte arithmetic.** U+2014 → UTF-8 `E2 80 94` → re-interpret each byte as Latin-1 codepoint → U+00E2 U+0080 U+0094 → re-encode UTF-8 → `C3 A2 C2 80 C2 94`. That's exactly the bytes recorded in vault-inbox.json at 249cffe (brief §1: "396 occurrences of byte sequence c3 a2 c2 80 c2 94"). The pre-14e256a `readFile` (`atob(data.content)` with no UTF-8 decode) is the only step in any version of the chain that produces it.

**Scope additions vs primary brief.** `sources.html:388` (deleteSource → commitFiles on sources-registry.json) is a fourth read-modify-write call site not listed in §4.3, with the same exposure. Cache-bust extended to it. The defensive guard fits poorly there (registry has different field names than inbox.items) — sources.html gets cache-bust + base64 _createBlob coverage but no guard; the registry round-trip is exercised infrequently and the base64 fix alone is sufficient.

**Phase 0 acceptance:** Met. Proceeding to Phase 1.

### 2026-04-28 — Phase 1 (patch)

Single commit covers all four sub-fixes (§4.1 - §4.4) plus the spec test (§4.5).

- **§4.1** `_createBlob` now posts `{content: base64(TextEncoder(content)), encoding: 'base64'}` instead of relying on Fetch's USVString → UTF-8 encoding step. Helper `_encodeBase64Utf8` sits next to the existing `_decodeBase64Utf8` (which is unchanged and already correct).
- **§4.2** Pre-write defensive guard: regex `/â[-¦]|Â /` (ASCII-escaped to survive editor save) catches the U+00E2 + U+0080 + U+009X / U+00A6 and U+00C2 + U+00A0 fingerprints. Discriminator chosen so legitimate U+00E2 in French/Portuguese ('Prât-à-Manger') does not false-positive — the guard requires a C1 control immediately following. `countMojibakeMarkers` exported on `GitHubAPI`. Wired into all three `commitFiles` call sites in `review.html`: deleteClaim (line 781), autoClearApply (line 1449), writeApproved (line 1623). Page-load baseline captured in `loadAll` after vault-inbox.json arrives. Throws with a hard-refresh hint if count rose.
- **§4.3** Cache-bust query string `?v=2026-04-27-wq029` added to `<script src="github-api.js">` on **review.html, add.html, sources.html** (and the three beta/ equivalents). The brief listed only review.html + add.html; `sources.html` was added because it also calls `GitHubAPI.commitFiles` on `sources-registry.json` (deleteSource, line 388) with the same exposure.
- **§4.4** `beta/github-api.js` synced from root via `cp` (file-identical post-sync; verified by `diff`). Beta admin pages got their cache-bust strings too.
- **§4.5** Test at `tests/test_github_api_encoding.spec.html`. Three cases: clean em-dash round-trips with E2 80 94 wire bytes; pre-mojibaked input round-trips verbatim with the canonical C3 A2 C2 80 C2 94 signature (no double-corruption, no silent un-corruption — that's wq-030's job); guard counts new markers, ignores pre-existing, ignores legit U+00E2. Validated through node with browser shims (3/3 PASS); the same logic runs unmodified in any browser.

**Existing tests:** test_apply_decisions_encoding.py 9/9, test_claim_schema.py 6/6, test_date_coerce.py 26/26. `node scripts/build-lint.js` shows 0 failures (8 unrelated data-references warnings on index.html / capital.html / in-development.html / methodology.html — pre-existing, none touched by wq-029).

**Phase 1 acceptance:** Met. Hand-off below covers Phase 2 verification on the live admin once Pages deploys.

### 2026-04-28 — Phase 2 (verify on live admin)

**Push:** Local d91d93c was cherry-picked onto origin/main as `73dc782` after a sustained Mac git-hang quirk forced a manual cleanup (rebase machinery and `git status --ahead-behind` both stalled in S-state for minutes; resolved by killing hung processes, removing `.git/index.lock`, `git reset --hard origin/main`, then plain `git cherry-pick d91d93c`).

**Pages deploy:** run `25042763188` for sha `73dc782` completed `success`. Watched via `gh run view --json status,conclusion`.

**Phase 2b serve check:** `https://sibowker-oss.github.io/ai-token-tracker/github-api.js?v=2026-04-27-wq029` 301-redirects to the custom domain `http://ai-index.hepburnadvisory.com.au/github-api.js?v=2026-04-27-wq029` and serves 200 OK. Body grep confirms all three new markers present:

- `countMojibakeMarkers` defined and exported.
- `_encodeBase64Utf8` defined using `new TextEncoder().encode(str)`.
- `_createBlob` posts `body: JSON.stringify({content: _encodeBase64Utf8(content), encoding: 'base64'})`.

**Phase 2c manual Submit:** Simon hard-refreshed `review.html`, set one item `scan-20260428-d4e` to raw_pool (no other changes), clicked Submit. Resulting commit `6b60ad1` ("Review: 1 raw_pool"), parent `73dc782`. Apply-decisions auto-fired commit `79367f5` on top.

**Marker delta — primary acceptance, PASS:**

| File state | mojibake codepoint U+00E2 U+0080 U+0094 | clean em-dash U+2014 |
|---|---:|---:|
| `73dc782` (parent) | 390 | 1167 |
| `6b60ad1` (Simon's Submit) | **390** | **1167** |
| `79367f5` (apply-decisions auto-fire) | 390 | 1167 |

All counts identical at the codepoint level. **No new mojibake introduced. Pre-existing mojibake codepoints preserved verbatim (wq-030's cleanup is now unblocked).** Verified by counting BOTH the ASCII-escape form (`â`) and the raw UTF-8 byte form (`c3 a2 c2 80 c2 94`) — sums match across both representations.

**Diff sanity — secondary acceptance, INITIAL FAIL → fixed in P1.6:**

Brief §5.2 also required "no mass diff of sourceAuthor / notes / claim lines". The actual `6b60ad1` diff was 8072 lines. Root cause: Python's `json.dump()` writes `ensure_ascii=True` (`\uXXXX` escapes) but JS `JSON.stringify` writes raw UTF-8 bytes for non-ASCII codepoints. Every Submit flips the file from ASCII-escape → raw UTF-8, every apply-decisions flips it back. Codepoint-identical, byte-different. Cosmetic, but breaks PR review and creates noisy commits on every cycle.

### 2026-04-28 — Phase 1.6 (cosmetic-diff fix)

Helper `_stringifyAsciiSafe(value, indent)` added to `github-api.js` next to `_encodeBase64Utf8`. Wraps `JSON.stringify(value, null, indent)` in a `.replace(/[-￿]/g, c => '\\u' + c.charCodeAt(0).toString(16).padStart(4,'0'))` pass that emits Python-compatible lowercase-hex `\uXXXX` escapes for every non-ASCII codepoint. `_createTree` now calls `_stringifyAsciiSafe(f.content, 2)` instead of `JSON.stringify(f.content, null, 2)`. Cache-bust token bumped from `2026-04-27-wq029` to `2026-04-28-wq029-p1.6` on review.html, add.html, sources.html plus the three beta/ equivalents. `beta/github-api.js` re-synced. Spec test `tests/test_github_api_encoding.spec.html` extended with **Case 4** (4/4 PASS via node shim): asserts that the helper output contains `—` for clean em-dash, `â` for pre-mojibaked input, no literal em-dash glyph, and is ASCII-only on the wire.

After P1.6 lands, the next Submit + apply cycle should produce diffs containing only the explicitly-modified `status` / `decided_at` / `lastProcessed` fields — no encoding-style flip.

**Phase 1.6 acceptance:** existing tests green (9/9, 6/6, 26/26, build-lint 0 fail), spec test 4/4. Hand-off to Simon for the second push + verify cycle.


