# Brief: page lifecycle registry — gate audits & lint on page status

> **Handoff metadata (per GUIDELINES §9.3)**
> - **Source draft:** `The AI Ledger/page-lifecycle-registry-brief.md`
> - **Handoff date:** 2026-04-26
> - **Work queue:** wq-031
> - **Parent:** wq-016 audit (2026-04-26) surfaced that chips.html and capital.html disagree on the same canonical number ($170B vs $201B for the Inference (Ad Platform) node; page totals diverge $604B vs $745B). Two retired pages — chips.html (superseded by capital.html) and sankey.html (superseded by revenue.html) — are still in repo root and getting picked up by build-lint, audits, and any other site-wide checks. Same problem will recur whenever a page is iterated.
> - This repo copy is the **immutable contract**. Append Implementation log below when starting work; do not edit §1–§13 without going back to the Ledger draft and handing off again.

**Status:** Scoped
**Budget:** $0 — scripts + manifest only

---

## 1. Goal

Make page lifecycle status a first-class, registered piece of metadata. Codify the convention that's already half-built (`/archive/`, `/parked/`, `/beta/`, `page-archive.html`) into a single manifest, gate every site-wide check on it, and physically relocate stranded retired pages so root only contains live + admin + concept pages.

After this:
- chips.html and sankey.html no longer surface in build-lint dataReferences (they're at `/archive/chips-v1.html` and `/archive/sankey-v2.html`)
- `data/page-registry.json` is the source of truth: every .html file in the repo has a registered lifecycle status
- build-lint, future audits, and the public nav can all be derived from the registry
- The chips.html-vs-capital.html drift becomes impossible: a retired page can't drift, it's frozen at a snapshot under /archive/

---

## 2. Pre-flight

- Confirm wq-021 commits are pushed to origin (currently 4 commits ahead; rebase aborted earlier today). This brief assumes `5cb1fb5` is on `origin/main` before any phase work begins.
- Stash named "pre-rebase" still exists. Drop it before any new git work in this brief — it's just bot-runtime data + linter noise.

---

## 3. Concept

### 3.1 Lifecycle states

Seven states, derived from Simon's confirmed classifications 2026-04-26:

| State | Folder | In public nav? | Linted? | Notes |
|---|---|---|---|---|
| `live` | root | yes | yes (full) | Public ledger + infrastructure pages. Includes about, methodology, changelog, index, capital, revenue, usage, power, openrouter, in-development, timeline. dataReferences applies; per-page lint exclusions handled in registry entry if needed (e.g. changelog's historical-by-design literals) |
| `admin` | root | no | partial | Tooling: admin, add, ask, claims, vault, source-ledger, sources, settings. Schema-checked but skipped on dataReferences |
| `concept` | root | no | no | Experiments/in-flight ideas: ipo-watch, subsidy-clock, predictions, benchmarks, confidence. Stay in root for active iteration but excluded from audits. Surfaced in archive.html under a "Concepts" section |
| `beta` | `/beta/` | no | no | Parallel staging tree, 49 files. Already excluded by directory boundary |
| `parked` | `/parked/` | no | no | Paused work; might come back |
| `retired` | `/archive/` | no | no | Superseded by a live page. URL preserved, frozen content. Surfaced in archive.html |
| `newsletter` | `/newsletters/` | no | no | Immutable timestamped artefacts |

### 3.2 Manifest

`data/page-registry.json`. One entry per .html file in the repo (excluding node_modules, tests/reports, data/snapshots, data-updates/archive). Schema:

```json
{
  "schema_version": "1.0",
  "last_updated": "YYYY-MM-DD",
  "pages": [
    {
      "path": "capital.html",
      "status": "live",
      "title": "Capital Ledger",
      "purpose": "Capex flows by hyperscaler and infrastructure node",
      "supersedes": ["archive/chips-v1.html"],
      "supersededBy": null,
      "addedOn": "2026-04-15",
      "retiredOn": null,
      "lastReviewed": "2026-04-26"
    },
    {
      "path": "archive/chips-v1.html",
      "status": "retired",
      "title": "Compute & Chips — v1",
      "purpose": "Original capex Sankey before the v2 rebalance",
      "supersedes": [],
      "supersededBy": "capital.html",
      "addedOn": "2026-02-XX",
      "retiredOn": "2026-04-26",
      "retiredReason": "RHS totals diverged from capital.html by $141B — different node count + stale numbers. Capital.html is the canonical capex view."
    }
  ]
}
```

Fields match the spirit of `data/sources.registry.md` and `data/agents.registry.md` — every entry carries enough provenance that future-Claude (or future-Simon) understands why.

### 3.3 archive.html becomes the registry-driven non-public index

archive.html is the password-gated nav for everything not on the public site (Simon's clarification 2026-04-26). After this brief, archive.html reads `data/page-registry.json` at load and renders three sections:

- **Concepts** — status=concept (active experiments)
- **Retired** — status=retired (superseded versions, frozen)
- **Parked** — status=parked (paused; might come back)

Adding a page to any section is a registry edit, not an HTML edit. page-archive.html — the older one-card gallery — is folded into archive.html during this brief or marked redundant for retire (decide in §10 Q2).

### 3.4 build-lint integration

dataReferences check (and any future page-scoped checks) gated on registry status:

```js
const registry = JSON.parse(fs.readFileSync('data/page-registry.json'));
const checkable = new Set(
  registry.pages
    .filter(p => p.status === 'live')
    .map(p => p.path)
);
// ...inside checkDataReferences, skip files not in `checkable`
```

Fail (not warn) on any .html in repo root that isn't in the registry — forces every new page to be classified.

Per-page lint exclusions (e.g. changelog.html's $770B historical-by-design literal flagged by wq-016 audit) handled via an optional `lintExclusions: ["dataReferences"]` field on the registry entry. Keeps the lifecycle simple — concept and admin pages get blanket exclusion via status, live pages can carve out specific exemptions per registry entry.

---

## 4. Phase 0 — Build the registry from confirmed classifications

### 4.1 Classifications (confirmed by Simon 2026-04-26)

| Path | Status | Notes |
|---|---|---|
| `index.html` | live | |
| `capital.html` | live | |
| `revenue.html` | live | supersedes sankey.html |
| `usage.html` | live | |
| `power.html` | live | |
| `openrouter.html` | live | |
| `in-development.html` | live | |
| `timeline.html` | live | |
| `about.html` | live | |
| `methodology.html` | live | |
| `changelog.html` | live | `lintExclusions: ["dataReferences"]` — $770B historical literal is by-design (wq-016 audit class C) |
| `admin.html` | admin | |
| `add.html` | admin | |
| `ask.html` | admin | |
| `claims.html` | admin | |
| `vault.html` | admin | |
| `source-ledger.html` | admin | |
| `sources.html` | admin | |
| `settings.html` | admin | |
| `archive.html` | admin | The password-gated registry-driven index for non-public pages |
| `ipo-watch.html` | concept | |
| `subsidy-clock.html` | concept | |
| `predictions.html` | concept | |
| `benchmarks.html` | concept | |
| `confidence.html` | concept | |
| `dashboard.html` | retired | v1; supersededBy index.html. Move to `/archive/dashboard-v1.html` |
| `chips.html` | retired | v1; supersededBy capital.html. Move to `/archive/chips-v1.html`. RHS totals diverged $141B from capital — never reconciled |
| `sankey.html` | retired | v2; supersededBy revenue.html. Move to `/archive/sankey-v2.html` (existing `/archive/sankey-v1.html` is the older predecessor) |
| `v1-review.html` | retired | Legacy review tooling. Move to `/archive/v1-review.html` |
| `page-archive.html` | retired-or-merge | Pre-existing one-card archive gallery, supersededBy archive.html (registry-driven). See §10 Q2 |
| `/beta/*.html` (49) | beta | All bulk-classified |
| `/parked/*.html` (9) | parked | All bulk-classified |
| `/archive/sankey-v1.html` | retired | Already in correct location, registry only |
| `/newsletters/brief-*.html` (5) | newsletter | All bulk-classified |
| `/data-updates/review-consumers.html` | admin | Nested admin tooling |
| `/beta/data-updates/review-consumers.html` | beta | Beta duplicate, leave alone |

### 4.2 Output

- `data/page-registry.json` covering every .html under apac-ai-intel/ except `node_modules/`, `tests/reports/`, `data/snapshots/`, `data-updates/archive/`
- `audits/2026-04-26-page-inventory.md` with the table above + any newly-discovered ambiguities

### 4.3 Acceptance for Phase 0

- Registry validates with the validator from Phase 1 (chicken-and-egg: scaffold validator alongside, but full validation happens in Phase 1 commit)
- 1 commit: `feat(registry): page-registry.json from confirmed classifications (wq-031 P0)`

---

## 5. Phase 1 — Schema + validator

### 5.1 Extend metric-schema.json

Add a `page_lifecycle_statuses` block with the seven values from §3.1 and per-status rules (folder requirement, navigability, lint applicability).

### 5.2 Add validator

`scripts/validate_page_registry.py`:
- Every .html in repo (minus excluded dirs) appears exactly once in `data/page-registry.json`
- Every entry's `status` matches its folder per §3.1
- Every status=retired entry has a `supersededBy` and `retiredReason`
- No two entries share a path
- All `supersedes`/`supersededBy` cross-references resolve to a registry entry

### 5.3 Acceptance for Phase 1

- Schema block landed
- Validator runs clean against the Phase 0 draft registry
- 1 commit: `feat(schema): page_lifecycle_statuses + validator (wq-031 P1)`

---

## 6. Phase 2 — Physical relocation

### 6.1 Moves

```
git mv dashboard.html archive/dashboard-v1.html
git mv chips.html archive/chips-v1.html
git mv sankey.html archive/sankey-v2.html
git mv v1-review.html archive/v1-review.html
```

Each move is its own commit per the Mac git hang quirk.

Concept pages (ipo-watch, subsidy-clock, predictions, benchmarks, confidence) stay in repo root — registry status alone gates them out of audits. They're under active iteration and a folder move would create churn for no audit-correctness gain.

### 6.2 Stub redirects (optional v1)

For URLs that may have external inbound links, leave a 5-line meta-refresh stub at the old path:

```html
<!doctype html><meta http-equiv="refresh" content="0; url=archive/chips-v1.html">
<title>Moved — Capital Ledger</title>
<a href="archive/chips-v1.html">Redirecting to archive/chips-v1.html…</a>
<a href="capital.html">Or jump to the current Capital Ledger.</a>
```

Decision in §10 Q1 — default no stubs except dashboard.html → index.html (highest external-link risk per project knowledge).

### 6.3 Registry update

Each move commit also updates `data/page-registry.json` so the entry's path changes from `<name>.html` to `archive/<name>-vN.html` and `retiredOn` is set. archive.html doesn't need hand-edit — Phase 4 will make it registry-driven; in the interim, page-archive.html keeps its existing single sankey-v1 card.

### 6.4 Acceptance for Phase 2

- 4 commits (one per moved page, per Mac git hang quirk)
  - `chore(retire): move dashboard.html → archive/dashboard-v1.html (wq-031 P2a)`
  - `chore(retire): move chips.html → archive/chips-v1.html (wq-031 P2b)`
  - `chore(retire): move sankey.html → archive/sankey-v2.html (wq-031 P2c)`
  - `chore(retire): move v1-review.html → archive/v1-review.html (wq-031 P2d)`
- Registry updated with each entry as it moves
- Build-lint warning count drops by the chips + sankey + dashboard + v1-review literal count

---

## 7. Phase 3 — build-lint integration

### 7.1 dataReferences gating

Modify `scripts/build-lint.js` `checkDataReferences()` to:
1. Read `data/page-registry.json`
2. Build a set of paths where status === `live` (admin, concept, retired etc. all skipped)
3. Apply per-entry `lintExclusions` array — if it includes `"dataReferences"`, skip even though status=live
4. Loop only over the resulting set

### 7.2 Unregistered-page check

New build-lint failure rule: any .html in repo root not present in registry fails the build. Forces every new page to be classified.

### 7.3 Acceptance for Phase 3

- build-lint passes against current state with the new gating
- Adding a new unregistered .html to repo root reliably fails build-lint
- 1 commit: `feat(build-lint): gate page checks on registry, fail unregistered (wq-031 P3)`

---

## 8. Phase 4 — archive.html becomes registry-driven

### 8.1 Rewrite

archive.html fetches `data/page-registry.json` at load and renders three sections:

- **Concepts** — status=concept, sorted alphabetically. Card shows title, purpose, lastReviewed.
- **Retired** — status=retired, sorted by retiredOn desc. Card shows title, purpose, retiredOn, retiredReason, supersededBy link, and the iframe thumbnail.
- **Parked** — status=parked. Card shows title, purpose, addedOn.

Password gate (existing in archive.html and page-archive.html) preserved.

### 8.2 Folding page-archive.html

Per §10 Q2 default, the merge happens in this phase. Either delete page-archive.html or convert it to a meta-refresh stub pointing to archive.html.

### 8.3 Acceptance for Phase 4

- Adding a status=retired/concept/parked entry to the registry surfaces a new card on archive.html with no HTML edit
- Existing sankey-v1 card still renders correctly
- page-archive.html either folded into archive.html or stubbed to redirect
- 1 commit: `feat(archive): archive.html driven by page-registry.json (wq-031 P4)`

---

## 9. Out of scope (deferred)

- **Auto-derived main nav** from registry. Today nav is hand-edited; consistent enough for v1. Worth a follow-up brief once registry is stable.
- **Beta tree audit.** 49 files in `/beta/`, half of them duplicates of root pages. Worth a separate cleanup sweep — but already excluded from build-lint by directory boundary, so no urgency.
- **Versioned archive naming convention.** `chips-v1.html` works for now; if a page goes through v2, v3, v4, may want a more deliberate scheme (date-stamp? semver?). Decide on demand.
- **Cross-page reconciliation enforcement.** A future build-lint check could detect chips.html-vs-capital.html-style drift between live pages by reading shared anchor keys. Tracked separately as wq-016 Phase 2 follow-up.

---

## 10. Open questions

- **Q1:** Stub redirects for retired pages (§6.2)? Default: no stubs in general — Hepburn ledger pages aren't deeply linked externally yet; meta-refresh stubs add complexity for marginal value. **Exception: dashboard.html** — was the public-facing index of the v1 Ledger that the project knowledge still references (`sibowker-oss.github.io/ai-token-tracker/dashboard.html`). Leave a meta-refresh stub at `dashboard.html` pointing to `index.html` to avoid breaking the linkable URL.
- **Q2:** archive.html vs page-archive.html. archive.html is confirmed as the password-gated nav (Simon 2026-04-26). page-archive.html is the older one-card gallery. Default: fold page-archive.html into archive.html during Phase 4 — either delete page-archive.html or convert it to a meta-refresh stub. archive.html becomes the single index.
- **Q3:** Auto-derived main nav from registry. Today the public nav is hand-edited per page. Auto-derivation would make the registry the true single source of truth. Default: keep manual for v1, separate brief for nav auto-derivation. Reasoning: nav has design considerations (ordering, grouping, mobile collapse) the registry can't capture cleanly.
- **Q4:** Should the brief touch `/beta/`? 49 files, half duplicating root pages. Already excluded by directory boundary so no audit-correctness gain. Default: leave alone for v1; separate cleanup brief if Simon ever wants to clean it up or promote a beta page to live.

---

## 11. Phases — order of execution

1. **Phase 0** build registry from §4.1 confirmed classifications + audit doc (1 commit)
2. **Phase 1** schema + validator (1 commit)
3. **Phase 2** physical moves (4 commits — dashboard, chips, sankey, v1-review)
4. **Phase 3** build-lint integration (1 commit)
5. **Phase 4** archive.html registry-driven, fold page-archive.html (1 commit)
6. STOP — hand back to Simon

Per Mac git hang quirk: each phase is its own commit. Don't bundle.

Total: 8 commits. Larger than wq-021 but every phase is independently verifiable.

---

## 12. Test plan

- **Phase 0:** Manual review of audit doc; Simon's sign-off on the §4.1 table. Validator runs clean once Phase 1 lands.
- **Phase 1:** validate_page_registry.py exits 0 against Phase 0 registry. Synthetic broken cases (duplicate path, missing folder match, dangling supersededBy) must each fail loudly.
- **Phase 2:** dashboard, chips, sankey, v1-review no longer in `git ls-files | grep -E '^[^/]+\.html$'`. All visible at `/archive/`. Stub at dashboard.html (per §10 Q1) redirects to index.html.
- **Phase 3:** build-lint passes. Add a synthetic `test-unregistered.html` to root → build-lint fails. Remove it → build-lint passes again. Toggle changelog.html's `lintExclusions` and verify the $770B literal flips between flagged and exempt.
- **Phase 4:** Add a status=retired entry to the registry pointing to a real `/archive/` file. Open archive.html in browser → new card appears. No HTML edit needed. All three sections (Concepts, Retired, Parked) render with correct counts.
- **Build-lint must be 0 fail after each phase commit.**

---

## 13. Acceptance / done criteria

- [ ] Phase 0: data/page-registry.json built from §4.1 table, audits/2026-04-26-page-inventory.md committed
- [ ] Phase 1: page_lifecycle_statuses in metric-schema.json, validate_page_registry.py PASS, 1 commit
- [ ] Phase 2: dashboard, chips, sankey, v1-review all relocated under /archive/, registry updated, dashboard.html stub at root, 4 commits
- [ ] Phase 3: build-lint reads registry, dataReferences scoped to status=live (with per-page exclusions honoured), unregistered-root-pages fail, 1 commit
- [ ] Phase 4: archive.html driven by registry with Concepts/Retired/Parked sections, page-archive.html folded in, 1 commit
- [ ] All commits pushed, build-lint green
- [ ] wq-016 dataReferences warnings drop substantially (chips, sankey, dashboard, v1-review all gone from lint scope; changelog literal exempt via lintExclusions)
- [ ] Hand back to Simon

---

## 14. Implementation log

(Claude Code appends entries here as work progresses — date, phase, commit sha, notes.)

### 2026-04-26 Pre-flight — wq-021 sync to origin

Dropped pre-rebase stash (junk per handoff). `git pull --rebase` against
`a718b68 News alerts: 2026-04-25` and `857eb99 Vault scan: 284 pending claims`
on origin. Rebase paused once mid-flight (the standard Mac git
hang-quirk pattern); aborted and retried. wq-021 commits rewritten by
the rebase (b07483e/9b17954/b46a9aa/5cb1fb5 → 47d1b76/9547837/9855e07/ab97a10),
content preserved. Pushed `ab97a10` to `origin/main`. Working tree clean
modulo the wq-031 brief (untracked).

### 2026-04-26 P0 — registry from §4.1 — commit 9b643d3

`data/page-registry.json` covers 87 .html files outside excluded dirs
(node_modules / tests/reports / data/snapshots / data-updates/archive).
By status: 12 live, 11 admin, 5 concept, 6 retired (4 pending move + 1
archive/sankey-v1.html in place + 1 page-archive.html in place), 10
parked, 38 beta, 5 newsletter. Each entry has full provenance: title
extracted from the file's `<title>` tag, addedOn from `git log
--diff-filter=A --reverse | head -1`, retired entries carry retiredReason,
the four pending-move entries carry `pendingMove: true` + `pendingMoveTo`.
changelog.html carries `lintExclusions: ["dataReferences"]` for the
$770B historical-by-design literal.

`audits/2026-04-26-page-inventory.md` documents two ambiguities outside
brief §4.1: `follow-the-trillion.html` defaulted to `live` (public FTBT
page, in nav), `review.html` defaulted to `admin` (hosted-admin queue
UI). Brief's parked count (9) and beta count (49) corrected to filesystem
truth (10 and 38). Validator runs in P1 — chicken-and-egg per §4.3.

### 2026-04-26 P1 — schema + validator — commit 38e0f53

`metric-schema.json` gains `page_lifecycle_statuses` block: 7 valid
states with definitions + folder rules + required fields per status.
Mirrors the shape of the existing `inbox_statuses` block.

`scripts/validate_page_registry.py` enforces five rules (R1 every .html
in repo appears once; R2 status matches folder, with pendingMove deferring
to pendingMoveTo's folder; R3 retired entries carry retiredOn +
retiredReason; R4 no duplicate paths; R5 supersedes/supersededBy
resolve). Validator reports `OK — 87 pages, 87 .html files in scope, all
rules R1-R5 pass`.

`tests/test_validate_page_registry.py` covers six synthetic broken
cases per §12 — duplicate path, folder/status mismatch, dangling
supersededBy, file-on-disk-not-in-registry, retired-missing-reason, plus
the baseline. 6/6 PASS.

Build-lint 0 failures.

### 2026-04-26 P2 — physical relocations — commits 8962fb3, dac79db, d24e23c, 42d9b1d

Four `git mv` commits, one per moved page per the Mac git hang quirk:

- **P2a** (8962fb3) `dashboard.html → archive/dashboard-v1.html` plus a
  meta-refresh stub at root per brief §10 Q1 (legacy URL preservation).
  index.html `supersedes: [archive/dashboard-v1.html]`. Two registry
  entries: the moved page at archive/, plus the redirect stub at root
  (retired-in-place).
- **P2b** (dac79db) `chips.html → archive/chips-v1.html`. capital.html
  `supersedes: [archive/chips-v1.html]`. retiredReason captures the
  wq-016 audit's $141B divergence finding. No stub.
- **P2c** (d24e23c) `sankey.html → archive/sankey-v2.html`. revenue.html
  `supersedes: [archive/sankey-v2.html, archive/sankey-v1.html]`.
  archive/sankey-v2.html `supersedes: [archive/sankey-v1.html]`. No stub.
- **P2d** (42d9b1d) `v1-review.html → archive/v1-review.html`. Orphan-retired
  with `supersededBy: null` — one-shot tool, retiredReason explains. No stub.

Validator clean after each commit (88 entries; the dashboard stub adds
one). Build-lint 0 failures throughout. Lint warnings drop: chips.html's
$170B + $1.07T no longer in scope (file is under archive/, build-lint's
root scan misses it).

### 2026-04-26 P3 — build-lint registry-gating — commit 8e4739b

`scripts/build-lint.js`:
- New helpers `loadPageRegistry` / `buildLintScope` / `checkUnregisteredRootPages`.
- `checkDataReferences` now scopes to `liveCheckable` — paths where status === 'live'
  AND lintExclusions doesn't include 'dataReferences'. Concept/admin/retired/etc skipped.
- New build failure: `unregistered-page` fires on any .html in repo root
  not in registry — forces classification on every new page.

§12 P3 synthetic tests: all PASS.
- `test-unregistered.html` at root → fail with `[unregistered-page]`.
- Remove it → 0 failures.
- Strip changelog.html's `lintExclusions` → +1 changelog warning. Restore → 0.

dataReferences warning count: 12 → 9. Three eliminated:
chips.html × 2 (moved), changelog.html × 1 (excluded). The remaining 9
(capital × 3, index × 1, in-development × 3, follow-the-trillion × 1,
methodology × 1) are real wq-016 Phase 2 follow-ups, out of wq-031 scope.

### 2026-04-26 P4 — archive.html registry-driven — commit f8cb4ac

`archive.html` rewritten to fetch `data/page-registry.json` and render
three sections: Concepts (5 cards, alphabetical), Retired (5 cards,
sorted by retiredOn desc, redirect stubs filtered), Parked (10 cards,
alphabetical). Each card has an iframe thumbnail (250%×0.4 scale = 16:10
preview), title, purpose, and meta. Retired cards add the retiredReason
callout and a "Superseded by" anchor; redirect-stub entries (titles
starting with "Moved —") are filtered from the visible list.

Password gate preserved (same SHA-256 + localStorage key). The previous
"Decision Archive" claim-list UI is dropped per Simon's 2026-04-26
clarification that archive.html is the registry-driven page-list now.
The vault-data + vault-inbox claim data is still on disk; a claim
audit UI is a separate brief if wanted.

`page-archive.html` replaced with a 5-line meta-refresh stub to
archive.html. admin.html's "Page Archive" iframe tab still resolves
during the transition; cleaning up that tab is a follow-up since brief
defers admin nav changes.

Registry update: archive.html title and purpose changed to reflect new
role; page-archive.html's title becomes "Moved — Page Archive (redirect
stub)" with expanded retiredReason.

Validator clean (88 pages). Build-lint 0 failures. test_validate_page_registry
6/6 PASS.

### 2026-04-26 — STOP

Phases 0/1/2a/2b/2c/2d/3/4 complete. 8 commits on `main`:

- 9b643d3 P0 registry + audit
- 38e0f53 P1 schema + validator + tests
- 8962fb3 P2a dashboard + stub
- dac79db P2b chips
- d24e23c P2c sankey
- 42d9b1d P2d v1-review
- 8e4739b P3 build-lint registry-gating
- f8cb4ac P4 archive.html registry-driven

Build-lint green at HEAD. Registry validator green. wq-016 dataReferences
warnings dropped from 12 to 9 (chips × 2, changelog × 1 eliminated).
Handed back to Simon. Two ambiguities flagged for confirm in the audit
doc (follow-the-trillion = live, review.html = admin).
