# Deployment: Homepage refresh — Compute Ledger integration & "five ledgers" reframe (wq-093)

**Date:** 2026-05-07
**WQ:** wq-093
**Branch:** `wq-093-homepage-compute-ledger-refresh-v2` (this work, awaiting Simon's approval before merge)
**Replaces (by intent):** the reverted attempt on `1c81e59` (commit subject `feat(wq-093): homepage refresh — Compute Ledger integration & "five ledgers" reframe`, reverted by `3e9ef65` on 2026-05-06). The reverted commit shipped the Layer Stack as a D1 Option B inline-SVG **pyramid**; the resolved brief calls for the type-led editorial **Option F** layout (no SVG, no pyramid).
**Parent context:**
- `docs/deployments/deploy-2026-05-06-wq-087-compute-ledger.md`
- `docs/deployments/deploy-2026-05-06-wq-092-compute-ledger-trajectory-no-qoq-drops.md`
- `docs/deployments/deploy-2026-05-06-wq-088-command-centre-nav-cleanup.md`

## Status

- **Built on feature branch.** Not yet merged to `main`; not yet on the live site.
- **Staging URL (local preview):** `http://localhost:4173/index.html` (Node `http-server` on port 4173, serving the working tree).
- **Approval status:** awaiting Simon's explicit chat approval per the TAIL Publishing Gate (CLAUDE.md). Required affirmative: "approved" / "ship it" / "promote" / "go live".

## What shipped (on the branch)

### Modified files

- **`index.html`** — primary file. Five-ledger reframe per brief D1–D8.
  - `<meta description>` and `og:description` rewritten to enumerate all five ledgers and lead on the new $43B Compute number.
  - **Masthead** H2 → `The AI economy, layer by layer.` Tagline → `Capital in. Compute spent. Power drawn. Tokens out. Revenue back. Five ledgers, one system.` Attribution unchanged.
  - **NEW Layer Stack hero (D1 Option F — type-led editorial).** Replaces the reverted pyramid. A vertical sequence of four rows (`.layerstack-row`), each with three stacked elements: small uppercase eyebrow (`01 — APPS REVENUE` …), large editorial dollar figure (~36px desktop, ~26px mobile), and a 3px-tall sparkbar div scaled to % width against Silicon $165B = 100% (Apps 10.5%, Compute 26%, Silicon 100%, Power 15%). No SVG, no pyramid, no card wrappers. Each row is a single clickable `<a>` linking to the layer's ledger (Apps→/revenue, Compute→/compute, Silicon→/capital, Power→/power). Caption beneath uses the brief §6.2 lock copy.
  - **Hero reconciliation strip** expanded from 3 → 5 tiles per §6.3: Capital ($745B, live read) · Revenue ($17B cohort) · **Compute ($43B — new)** · Usage (~360T) · **Power link-only** ("Power Ledger →" / "Power infrastructure — v3 in progress", no big-number, no tier pill). Sub-line: `Five ledgers, triangulated from primary sources.`
  - **Narrative flow** replaced. Old `Capital in → Assets Built → Tokens Out → Revenue Back` swapped for `Apps Revenue → Compute → Silicon → Power` per §6.5. Step labels and locked copy from brief; icon colours pulled from new `--apps` / `--compute` / `--silicon` / `--power` accents.
  - **Hero hook** swapped to Compute-anchored (D7): `$2.50 of compute spend stands behind every $1 of customer-paid AI Apps Revenue today.` Sub-line: `The gap is funded by hyperscaler equity in the same labs.` Ratio is computed live as `compute / apps` rounded to nearest tenth and formatted `$X.XX`.
  - **Live tile** (D5) swapped from MSFT Copilot + Salesforce Agentforce ARR ($3.2B) → Compute Revenue 2025 signal ($43B / +153% YoY / 79% frontier-lab). Source link → `methodology.html#compute-revenue-three-segment-model`.
  - **Ledger entry cards** expanded from 3 → 5 with full §6.7 copy. Power card uses `.is-link-only` modifier — value renders as `v3 in progress` (muted), no tier pills. Card grid: 3-up by default, **5-up at ≥1100px** (CSS media query addition). Card colours mapped to the layer accents (`--capital` / `--revenue` / `--compute` / `--usage` / `--power`).
  - **`SCENARIOS` block** rewired (`_buildScenarios`, `_initScenariosFromData`, `applyScenario`):
    - Apps Revenue base now reads `sankey.totalCustomerRevenue` (cohort, ~$17.36B per wq-092) instead of `cumulative.customer_revenue_gross`.
    - Compute base added (`compute.compute_revenue_2025_gross_usd_b`).
    - Bear/Bull apply ±15% sensitivity to Apps and Tokens; **Compute is held constant in v1** per brief §7.1 — coupling Compute to Apps under the band implies a methodology call (does Compute drop with Apps, or absorb the gap as more pass-through?) deferred to a follow-up. The hook ratio still moves under Bear/Bull because it's `Compute / band-shifted Apps` (Bear ≈ $2.92, Base $2.50, Bull ≈ $2.16).
    - `applyScenario` updated for new DOM IDs (`hero-revenue` → Apps cohort, new `hero-compute`, `ls-apps`, `ls-compute`, `nar-apps`, `nar-compute`, `card-compute`).
  - CSS additions: `--apps`, `--compute`, `--silicon` design tokens; `.layerstack-hero` + `.layerstack-row` block (eyebrow / figure / sparkbar styles + hover); `.ledger-cards` 5-up media query at ≥1100px; `.ledger-card.is-link-only` modifier; mobile rules add a Layer Stack shrink (figure 26px, container padding 40/16/32).

- **`methodology.html`** — Section 5 "Data Sources" lede string-fix: `the three ledgers` → `the ledgers`. One line, no other changes.

- **`beta/index.html`** — `<meta description>` + `og:description` + masthead H2 + masthead tagline string-swept to the five-ledger framing. Beta is hand-edited / frozen v1 staging; no public links into `/beta/` from any production page (verified). Did the brief's required minimum string sweep; did NOT mirror the new Layer Stack hero / 5-tile strip / 5 cards into beta (per §7.2).

- **`beta/methodology.html`** — same one-line `the three ledgers` → `the ledgers` parity fix.

### New files

- **`tests/release-check/homepage.spec.ts`** — 17 desktop-chrome assertions across two `test.describe` groups:
  - Group 1 — `index.html — wq-093 five-ledger reframe`: AC1 masthead H2 + tagline + "three ledgers" absent; AC3 Layer Stack hero is 4 type-led rows with sparkbars (no SVG, no pyramid term, click-throughs land on the right pages); AC4 hero strip = 5 tiles + Power tile is link-only (no `.tier`); AC4-data Compute hero tile reads `$4XB` and Revenue hero tile reads `$1XB` (matched against `site-data.json`); AC5 narrative flow `Apps → Compute → Silicon → Power` (case-insensitive, since CSS uppercases the labels); AC6 hook is Compute-anchored `$X.XX` and contains "compute spend" + "apps revenue"; AC7 live tile = $43B Compute signal + +153% + 79%, no Copilot/Agentforce; AC8 ledger cards = 5 with the right titles and Power card link-only; AC9 footer Ledger group includes all five.
  - Group 2 — `Public-page sweep — wq-093 §3.2 "three ledgers" absent`: rendered DOM of `/index.html`, `/capital.html`, `/revenue.html`, `/compute.html`, `/usage.html`, `/power.html`, `/methodology.html`, `/about.html` contains no case-insensitive "three ledgers" substring.

### Test results (local, on the running preview at :4173)

- `npm run build-lint` → **0 fail, 1 advisory** (pre-existing `dataReferences map absent`, unchanged).
- `npx playwright test tests/release-check/homepage.spec.ts --project desktop-chrome` → **17/17 passed**.
- Regression: `compute.spec.ts + admin-nav.spec.ts + structure.spec.ts + smoke.spec.ts --project desktop-chrome` → **46 passed, 11 skipped, 0 failed** (the 11 skips are the existing `chips`/`about`-without-collapsible pattern).

## Decisions made during implementation

### Strategic
None — all eight Cowork decisions (D1–D8) resolved 2026-05-06. No `docs/decisions/open/` files written.

### Tactical

1. **Branch named `…-v2`.** The first wq-093 attempt landed on `1c81e59` and was reverted on `3e9ef65` for shipping Option B (pyramid) instead of the Cowork-resolved Option F. Naming the new branch `…-v2` keeps the reverted-and-replayed history readable.
2. **Layer Stack built inline in `index.html`.** Brief §5 explicitly calls for inline HTML+CSS, not a shared component or SVG. Total cost: ~16 lines of CSS + ~30 lines of HTML for the four rows + caption.
3. **Sparkbar widths as inline `style="width:X%"`.** Keeps the % values literally next to the figure they scale, so a future Apps revision (e.g. $30B) only needs the figure changed in two places (`#ls-apps` text + the inline `width`). No JS-driven width recompute — over-engineering for a quarterly editorial number.
4. **Power sparkbar at 15% / Apps at 10.5%.** Brief gives Apps "~10%" and Power "~15%". Apps actual ratio = 17.36/165 = 10.52%; Power actual ratio = 25/165 = 15.15%. Rounded to 10.5% and 15% for clean inline values.
5. **`--apps` / `--compute` / `--silicon` added as new CSS variables.** The existing `--purple` (8b5cf6) collides with `--usage`, which would muddle the Layer Stack vs Usage tile colour story. Added explicit accent tokens (purple #a855f7 / teal #06b6d4 / coral #fb7185 / amber existing `--power`). Power re-uses `--power`.
6. **5-up ledger card grid kicks in at ≥1100px.** At 1320px container width, 5 × ~220px + gaps fits comfortably; below 1100px, falls back to 3-up which also accommodates 5 cards as 3-then-2 visually. This is the cleanest break in the existing CSS without a wider refactor.
7. **Power hero tile uses inline `font-size:22px` and a "Power Ledger →" arrow.** No big-number; the value box becomes a CTA. Brief allows either omitting the tile or making it link-only — link-only preserves the 5-tile parity with the ledger cards and footer.
8. **Hero hook ratio rounding policy.** `formatRatio(v) = '$' + (Math.round((compute / v) * 10) / 10).toFixed(2)`. Live computation 43.07 / 17.36 = 2.481 → 2.5 → "$2.50" (matches the brief §6.4 lock copy). Nearest-tenth-then-format-as-2-decimals keeps the displayed ratio stable when the underlying numbers shift by a few percent quarter-on-quarter.
9. **`SCENARIOS` keep the existing ±15% pattern; Compute held constant.** Per §7.1. The Bear/Bull bands move Apps + Tokens; the hook ratio recomputes against the band-shifted Apps (Compute steady), which is methodologically defensible because the band IS Apps uncertainty under the same Compute observation.
10. **Beta left as a frozen v1 archive.** Did the brief-required string sweep only; no new Layer Stack hero / 5-tile / 5 cards mirrored over. Treating `/beta/` as a deprecated v1 snapshot per brief §7.2.
11. **Visual baselines NOT regenerated yet.** The previous wq-093 attempt regenerated 6 `index-*-darwin.png` baselines and was then reverted, taking the baselines with it. Decision: defer rebaselining until Simon approves the staging build, so we don't ship more dead snapshots if Option F needs visual revision. Rebaseline immediately after approval, before the merge.

## Open items

1. **Visual snapshot rebaseline for `index.html`** (6 viewports) — pending approval. Will run `playwright test tests/release-check/visual.spec.ts --update-snapshots --project <each>` after Simon green-lights the layout.
2. **Bear/Bull Compute coupling** (§7.1 deferral) — v1 holds Compute constant. If editorial review later wants the band to move Compute too, build a `data/scenarios.json` block defining per-metric sensitivities. Filed as a follow-up; no decision file written; the brief explicitly authorised this deferral.
3. **`beta/` archival** — long-term plan should be either to delete or to fully mirror — not both. No regression today.
4. **Notion wq-093 card** to be moved In Progress → Done with the post-merge SHA (repo cannot mutate Notion directly).

## Acceptance criteria status (brief §3)

- [x] **1. Headline framing replaced.** Masthead H2 + tagline + meta description + og:description updated. `grep -in "three ledgers" index.html` → 0 hits.
- [x] **2. Public-page sweep clean.** `grep -rli "three ledgers" *.html beta/*.html` → 0 hits across all 4 affected files (`index.html`, `methodology.html`, `beta/index.html`, `beta/methodology.html`). Asserted via Playwright Group 2 across 8 public pages.
- [x] **3. Layer Stack hero renders as a type-led editorial layout (D1 Option F).** Inline HTML+CSS; 4 rows of (eyebrow + figure + 3px sparkbar). Sparkbar widths Apps 10.5%, Compute 26%, Silicon 100%, Power 15%. No SVG, no pyramid. Click-through asserted in `homepage.spec.ts` AC3.
- [x] **4. Hero tiles updated.** 5 tiles per §6.3. Power tile link-only with "v3 in progress" caveat. Click-throughs asserted.
- [x] **5. Narrative flow replaced.** Apps→Compute→Silicon→Power; 4 step-cards with locked copy.
- [x] **6. Hook one-liner replaced.** Compute-anchored, ratio computed dynamically from `compute.compute_revenue_2025_gross_usd_b / sankey.totalCustomerRevenue`. Falls back to `$2.50` literal if fetch fails.
- [x] **7. Live tile swapped.** $43B + +153% YoY + 79% frontier; source attribution updated.
- [x] **8. Ledger cards = 5.** All five rendered with locked §6.7 copy; Power card link-only.
- [x] **9. Footer "The Ledger" group lists all five.** Unchanged from wq-088 — already in place.
- [/] **10. Mobile sanity.** CSS media query in place (Layer Stack figure shrinks to 26px at ≤768px; sparkbar % preserved; hero tiles already stack via existing rule). **Visual screenshot pass deferred** until rebaselining (see Open items #1).
- [x] **11. No regressions.** `npm run build-lint` → 0 fail (1 pre-existing advisory). `compute.spec.ts + admin-nav.spec.ts + structure.spec.ts + smoke.spec.ts` → 46 passed, 11 skipped, 0 failed on desktop-chrome.
- [x] **12. Validator extension passes.** New `homepage.spec.ts` 17/17 on desktop-chrome.
- [/] **13. Visual baseline rebaselined.** Deferred to post-approval per Tactical #11.
- [x] **14. Deployment record written** (this file).

## Reconciliation (per CLAUDE.md cross-ledger rule)

| Homepage figure | Source path | Existing publication | Relation |
|---|---|---|---|
| Capital $745B (CY23–25 cumulative) | `cumulative.capex_total` (live read; current value $766B) | `capital.html` headline | Equal (live read) |
| Revenue $17B (2025 cohort) | `sankey.totalCustomerRevenue` (~$17.36B) | `revenue.html` cohort total + `compute.html` Layer Stack Apps node | Equal |
| Compute $43B (2025 sum-of-Q post-Copilot) | `compute.compute_revenue_2025_gross_usd_b` ($43.07B) | `compute.html` hero | Equal |
| Tokens ~360T/day | `cumulative.tokens_2025_annualized` (live read; current 310) | `usage.html` hero | Equal (live read) |
| Layer Stack Silicon $165B + Power $25B | hard-coded constants in the homepage Layer Stack figures | `compute.html` Layer Stack constants | Equal — same numerical values; not yet wired through `site-data.json`, so the homepage and compute page would silently diverge if the Layer Stack constants change. Filed as a follow-up, not a blocker today (matches the prior wq-093 attempt's reconciliation note). |

No silent divergences from already-published numbers.

## Publishing Gate

**Status: awaiting approval.** Per CLAUDE.md (TAIL Publishing Gate, hard stop):

1. ✅ Built on feature branch.
2. ✅ Staging URL: `http://localhost:4173/index.html` (Node `http-server` running locally).
3. ⏳ **Awaiting Simon's explicit affirmative in chat** ("approved" / "ship it" / "promote" / "go live").
4. ❌ Not yet merged to `main`; not yet on the live site.
5. n/a — staging-first is feasible; no exception decision file required.

**Approval timestamp:** _TBD — to be filled in immediately on receipt of approval, alongside the merge SHA._
