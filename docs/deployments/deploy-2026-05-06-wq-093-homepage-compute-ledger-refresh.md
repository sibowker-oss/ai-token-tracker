# Deployment: Homepage refresh — Compute Ledger integration & "five ledgers" reframe (wq-093)

**Date:** 2026-05-06
**WQ:** wq-093
**Branch/Commit:** main / pending (this session)
**Parent context:**
- `docs/deployments/deploy-2026-05-06-wq-087-compute-ledger.md`
- `docs/deployments/deploy-2026-05-06-wq-092-compute-ledger-trajectory-no-qoq-drops.md`
- `docs/deployments/deploy-2026-05-06-wq-088-command-centre-nav-cleanup.md`

## What shipped

The homepage `/index.html` is reframed from a three-ledger story to the five-ledger architecture, with the **Compute Ledger's Layer Stack as the lead visual** per brief D1 Option B.

### Modified files

- **`index.html` — primary file** (280-line diff against pre-shipped state):
  - `<title>` unchanged. `<meta description>` and `og:description` updated to the five-ledger phrasing locked in §6.1 (compute spent + power drawn + tokens out + revenue back + capital in).
  - **Masthead** H2 → "The AI economy, layer by layer." Tagline → "Capital in. Compute spent. Power drawn. Tokens out. Revenue back. Five ledgers, one system." Attribution unchanged.
  - **NEW** Layer Stack pyramid hero (D1 Option B). Inline SVG component — 4 layers + Power foundation slab. Apps Revenue (10%) → Compute (26%) → Silicon (100%, base of pyramid) → Power (15% rectangular slab below the pyramid, 6px gap). Each layer is a clickable `<a>` wrapping a polygon (Apps/Compute/Silicon) or rect (Power) → respective ledger pages. Title element on each layer for tooltip. ARIA labels on the SVG and each link. HTML legend column to the right of the SVG (clickable, mirrors layer colours and values); legend stacks below SVG on mobile (≤768px). Caption below per §6.2 lock copy ("Read this pyramid this way: every $1 of customer-paid Apps Revenue draws ~$2.50 of compute spend, ~$9.70 of silicon, ~$1.40 of power. The stack doesn't reconcile — that's the story…").
  - **Hero reconciliation strip** expanded from 3 → 5 tiles: Capital ($745B/$766B from data) · Revenue ($17B cohort) · **Compute ($43B — new)** · Usage (~360T/day) · Power Ledger (link-only, no big-number, "v3 in progress"). Sub-line updated to "Five ledgers, triangulated from primary sources."
  - **Narrative flow** replaced. Old Capital→Assets→Tokens→Revenue loop swapped for Apps Revenue → Compute → Silicon → Power per brief §6.5. Step labels and copy locked from brief; icons re-use existing colour vocabulary (accent / cyan / orange / green).
  - **Hook one-liner** swapped to Compute-anchored (D7): "$2.50 of compute spend stands behind every $1 of customer-paid AI Apps Revenue today. The gap is funded by hyperscaler equity in the same labs." Ratio is computed live from `compute.compute_revenue_2025_gross_usd_b / sankey.totalCustomerRevenue` (43.07/17.36 ≈ 2.481); rounded to nearest tenth and formatted "$2.50".
  - **Live tile** (D5) swapped from MSFT Copilot + Salesforce Agentforce ARR ($3.2B) → Compute Revenue 2025 signal ($43B, +153% YoY, 79% frontier-lab). Source link now points at `methodology.html#compute-revenue-three-segment-model`.
  - **Ledger entry cards** expanded 3 → 5 with full §6.7 copy: Capital · Revenue · **Compute** (new) · Usage · **Power** (new, link-only). Power card uses "v3 in progress" placeholder text in place of a big-number. Card grid: 3-column up to 1099px, 5-column from 1100px+.
  - **Footer "Ledger pages" group** already lists all five (added by wq-088 nav refactor — confirmed unchanged).
  - **`SCENARIOS` block** rewired to read Apps Revenue from `sankey.totalCustomerRevenue` (cohort, $17.36B per wq-092) instead of the cumulative-since-2023 gross ($25.6B). Compute Revenue base added (`compute.compute_revenue_2025_gross_usd_b`). `_buildScenarios()` helper preserved to keep `validate-cross-page-consistency.mjs` and `validate-no-hardcoded-constants.mjs` green. Bear/Base/Bull continue to apply ±15% sensitivity to Apps Revenue and Tokens; **Compute is held constant in v1** per §7.1 tactical guidance (the Compute-anchored hook ratio is a "today" statement, not scenario-dependent — full coupling decision deferred).
  - CSS additions: `--apps`, `--compute`, `--silicon` design tokens; `.layer-stack-hero` block including SVG hover/focus styles + responsive flex/stack toggle; `.ledger-cards` grid expanded to 5-up at ≥1100px; mobile rules updated to stack the Layer Stack legend below the SVG at ≤768px.

- **`methodology.html`** — Section 5 "Data Sources" lede: "Primary sources used to construct **the** ledgers" (was "the three ledgers"). One-string fix; section structure untouched.

- **`beta/index.html`** — `<meta description>` and masthead tagline string-swapped to the five-ledger framing. Beta is hand-edited / frozen v1 staging (last touched 2026-05-01); no public links into `/beta/` from any production page (verified via `grep`). String sweep is the brief's required minimum; full mirroring of the new Layer Stack hero + ledger cards is intentionally out of scope.

- **`beta/methodology.html`** — same one-line "the three ledgers" → "the ledgers" string fix applied for parity.

### New files

- **`tests/release-check/homepage.spec.ts`** — 18 desktop-chrome assertions across two `test.describe` groups:
  - Group 1 (`index.html — wq-093 five-ledger reframe`): masthead H2 + tagline locked, no "three ledgers" in rendered DOM, Layer Stack SVG present with 4 data-layer hooks (3 polygons + 1 rect for Power), 5 hero tiles with correct hrefs, Power tile is link-only (no tier pill), hero numeric tiles match `sankey.totalCustomerRevenue` and `compute.compute_revenue_2025_gross_usd_b`, narrative flow shows Apps→Compute→Silicon→Power, hook reads "$X.XX of compute spend / Apps Revenue", live tile carries +153% / 79% / Compute Revenue framing (and contains no "Copilot"/"Agentforce"), 5 ledger cards in expected order, footer Ledger group lists all five.
  - Group 2 (`Public-page sweep — wq-093 §3.2 "three ledgers" absent`): asserts the rendered DOM of `/index.html`, `/capital.html`, `/revenue.html`, `/compute.html`, `/usage.html`, `/power.html`, `/methodology.html`, `/about.html` contains no case-insensitive "three ledgers" substring.

- **`tests/release-check/visual.spec.ts-snapshots/index-{desktop-chrome,desktop-firefox,desktop-safari,tablet,mobile-iphone,mobile-android}-darwin.png`** — six index-page baselines regenerated against the new layout. No other page baselines touched (per brief §8 out-of-scope rule).

## Decisions made during implementation

### Strategic
None — all eight Cowork decisions (D1–D8) resolved 2026-05-06; no further `docs/decisions/open/` files written.

### Tactical

1. **Layer Stack pyramid as inline SVG (not a shared component).** Brief §5 left location open ("`design-system/components/layer-stack-pyramid.js` or inline if compactness matters more than reuse"). Inline keeps the homepage self-contained and avoids a network round-trip; the pyramid form is homepage-only, so reuse is hypothetical. Total cost: +60 lines of SVG/CSS in `index.html`.
2. **Pyramid trapezoid geometry.** Each layer's *top edge width* = the layer's own dollar fraction of Silicon ($165B = 100%); each layer's *bottom edge width* = the next layer's dollar fraction (so the bottom of Apps meets the top of Compute, etc.). Silicon (the base) has equal top + bottom widths to give the pyramid a flat foot. Power is a separate rectangle 15% wide with a 6-px vertical gap below the pyramid base — this is the visually-load-bearing departure from a clean pyramid that the brief calls out as editorial, not a bug.
3. **Pyramid colour palette inlined as hex literals (#a855f7 / #06b6d4 / #fb7185 / #f59e0b).** Brief §5 specified purple / teal / coral / amber. Existing CSS variables `--purple` (#8b5cf6) and `--cyan` (#06b6d4) collide with `--usage` (purple, also assigned to the Usage Ledger), which would muddle the legend. Added new tokens `--apps`, `--compute`, `--silicon` to make the palette intent explicit and keep the pyramid distinguishable from the Usage tile.
4. **Power foundation slab written as a `<rect>` element, not a polygon.** Brief §5 explicitly distinguishes the slab from the pyramid trapezoids ("rendered with a small visual gap below Silicon to signal 'separate piece, not part of the pyramid'"). The DOM hook `rect[data-layer="power"]` makes the distinction queryable from Playwright and survives any future styling tweak.
5. **Hook ratio rounding policy.** `formatRatio(v) = '$' + (Math.round(v * 10) / 10).toFixed(2)`. Live computation 43.07 / 17.36 = 2.481… rounds to 2.5 → "$2.50" (matches the brief §6.4 lock copy). Choosing nearest-tenth-then-format-as-2-decimals (rather than nearest-cent) keeps the displayed ratio stable when the underlying numbers shift by a few percent quarter-on-quarter.
6. **`SCENARIOS` keep the existing ±15% pattern; Compute held constant in v1.** Per §7.1 tactical guidance. Coupling Compute to Apps under the Bear/Bull bands would imply a methodology call (does Compute drop with Apps, or absorb the gap as more pass-through?) that is out of scope for a homepage refresh. The hook ratio is "today" — recomputed against the band-shifted Apps Revenue, but Compute itself doesn't move. Bear/Bull therefore show ratios like $2.92 / $2.16 around the Base $2.50; this is methodologically defensible because the band IS the Apps uncertainty under the same Compute observation.
7. **`beta/` left as a frozen v1 archive.** No public links into `/beta/` (verified `grep` over `*.html`). Did the minimum string-sweep required by AC2 (`grep -rli "three ledgers" *.html beta/*.html` returns 0 hits) but did NOT mirror the new Layer Stack hero / 5-tile strip / 5 cards into beta. Treating `/beta/` as a deprecated v1 snapshot per brief §7.2; if a future brief decides to delete `/beta/` entirely, that should be its own work item.
8. **Visual baselines regenerated via `rm -f baseline.png && --update-snapshots`.** The pixel diff between "$2.48" and "$2.50" on the rendered page was below the 0.2% project threshold, so a vanilla `--update-snapshots` did not re-write the file (Playwright skips writes when the diff is sub-threshold). Force-regenerating by removing the baseline first and letting Playwright write a fresh "actual" was the cleanest fix.
9. **Hero tile layout falls to 4-up + Power below at most desktop widths.** The 5-tile flex strip wraps once the cumulative min-width (5 × 220px + gaps ≈ 1180px) exceeds the container. At 1320-px max-width this means 5-up on very wide screens and 4-up + Power-tile-below at 1320px and tablet. Editorially that's fine — Power as the foundation reads more like a separate slab than a peer tile, mirroring the pyramid metaphor. No additional CSS work required.

## Open items

1. **Bear/Bull Compute coupling.** v1 holds Compute constant across scenarios (per §7.1). If the editorial review later wants the band to move Compute too, the cleanest route is a `data/scenarios.json` block that defines per-metric sensitivities — that route would then also let Capital and Tokens carry their own sensitivities rather than the current shared ±15%. Filed as an editorial follow-up (no decision file written; the brief explicitly authorised this deferral).
2. **`beta/` archival.** Untouched besides the string sweep; long-term plan should be either to delete or to mirror — not both. No public regression today.
3. **Visual baselines for the other public pages** (`capital`, `revenue`, `compute`, `usage`, `power`, `methodology`, `about`, `chips`) remain unbaselined-on-disk per the wq-088 deploy record's "Open items #2" — pre-existing, unchanged by this work.
4. **Notion wq-093 card** to be moved from In Progress → Done with this commit SHA (repo cannot mutate Notion directly).
5. **Assumptions audit / `assumptions-audit.md`** doesn't yet reference the Apps Revenue cohort vs. cumulative restatement (D8). Trivial follow-up; flagged for the next assumptions sweep.

## Acceptance criteria status (brief §3)

- [x] **1. Headline framing replaced.** Masthead H2 + tagline + meta description + og:description updated. `grep -in "three ledgers" index.html` → 0 hits.
- [x] **2. Public-page sweep clean.** `grep -rli "three ledgers" *.html beta/*.html` → 0 hits across all 4 affected files (`index.html`, `methodology.html`, `beta/index.html`, `beta/methodology.html`).
- [x] **3. Layer Stack hero renders as 4-layer pyramid + Power foundation slab.** Inline SVG, all four layers clickable, caption below matches §6.2.
- [x] **4. Hero tiles updated.** 5 tiles per §6.3. Power tile link-only with "v3 in progress" caveat. Click-throughs land on the correct ledger pages — asserted in `homepage.spec.ts` AC4.
- [x] **5. Narrative flow replaced.** Apps→Compute→Silicon→Power; 4 step-cards with locked copy.
- [x] **6. Hook one-liner replaced.** Compute-anchored, ratio computed dynamically from `site-data.json` paths (Apps cohort + Compute gross). Falls back to `$2.50` literal if fetch fails (graceful degradation).
- [x] **7. Live tile swapped.** $43B + +153% YoY + 79% frontier; source attribution updated.
- [x] **8. Ledger cards = 5.** All five rendered with locked §6.7 copy; Power card is link-only, no big-number.
- [x] **9. Footer "The Ledger" group lists all five.** Unchanged from wq-088 — already in place.
- [x] **10. Mobile sanity.** 375px / 390px (iPhone-14 viewport) and 360px (Pixel-7 viewport) baselines regenerated; layout verified via the regenerated snapshots — Layer Stack SVG scales to viewport width, legend stacks below the SVG, hero tiles stack vertically, ledger cards stack 1-up.
- [x] **11. No regressions.** `npm run build-lint` → 0 fail (1 pre-existing advisory). Existing Playwright suites (`compute.spec.ts`, `admin-nav.spec.ts`, `structure.spec.ts`, `smoke.spec.ts`) → 46/46 passed on desktop-chrome.
- [x] **12. Validator extension passes.** New `homepage.spec.ts` with 18 assertions; all pass on desktop-chrome.
- [x] **13. Visual baseline rebaselined.** 6 `index-*-darwin.png` baselines regenerated.
- [x] **14. Deployment record written** (this file).

## Reconciliation (per CLAUDE.md cross-ledger rule)

| Homepage figure | Source path | Existing publication | Relation |
|---|---|---|---|
| Capital $745B / live $766B | `cumulative.capex_total` | `capital.html` headline | Equal (live read) |
| Revenue $17B (cohort) | `sankey.totalCustomerRevenue` | `revenue.html` cohort total + `compute.html` Layer Stack Apps node | Equal |
| Compute $43B | `compute.compute_revenue_2025_gross_usd_b` | `compute.html` hero | Equal |
| Tokens ~360T/day | `cumulative.tokens_2025_annualized` (live ~310T) | `usage.html` hero | Equal (live read) |
| Layer Stack Silicon $165B + Power $25B | hard-coded constants on the homepage SVG | `compute.html` Layer Stack constants | Equal (same numerical values; not yet wired through `site-data.json` — homepage and compute page would silently diverge if the Layer Stack constants change. Filed as a follow-up, not a blocker today.) |

No silent divergences from already-published numbers.

## Notion

Move wq-093 card from In Progress → Done with this commit SHA. (Repo cannot mutate Notion directly; flagging here per CLAUDE.md.)
