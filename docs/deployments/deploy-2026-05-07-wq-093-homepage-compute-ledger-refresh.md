# Deployment: Homepage refresh — Compute Ledger integration & "five ledgers" reframe (wq-093)

**Date:** 2026-05-07
**WQ:** wq-093
**Branch:** `wq-093-homepage-compute-ledger-refresh-v2` (this work, awaiting Simon's approval before merge)
**Supersedes (on this same branch):** the prior commit `0fdec64` which shipped D1 Option F (type-led editorial Layer Stack). The brief was updated 2026-05-06 — Option F is "superseded when Simon mocked up the 5-bar form in Figma 2026-05-06" — and now mandates D1 Option I (the AI Infrastructure Stack: five horizontal pill bars). This deployment replays wq-093 against the resolved Option I spec.
**Replaces (by intent):** the further-back reverted attempt on `1c81e59` (Option B — inline-SVG pyramid; reverted by `3e9ef65` 2026-05-06).
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

- **`index.html`** — primary file. D1 Option I AI Infrastructure Stack hero per brief §5; tile strip + narrative-flow deleted per D3 and D4.
  - **CSS** — replaced the prior Option F `.layerstack-*` block, the `.hero` reconciliation strip styles, and the `.narrative` + `.flow-*` styles with a single `.ai-infra-stack` block. New section uses Hepburn Advisory design tokens canonical to `/design-system/colors_and_type.css`: `--blue / --violet / --cyan / --amber / --green` for the per-bar gradients (NOT the Figma red/pink/purple palette); `--radius-pill` for bar shape; `--type-h2 / --type-meta / --type-eyebrow` for type slots; `--text-md / --text-xs / --text-2xl / --text-xl` for size slots; `--space-3 / --space-4 / --space-7` for spacing; `--shadow-focus` for keyboard focus ring; `--duration-fast / --ease-out` for hover transition. Each bar's gradient endpoint follows the brief's "10–15% lighter stop" suggestion (`#60A5FA / #A78BFA / #22D3EE / #FBBF24 / #34D399`).
  - **HTML** — the masthead now flows directly into `<section class="ai-infra-stack">`. Structure: `.ais-head` (h2 "AI Infrastructure Stack" + subtitle "2025 · Five ledgers, one stack"), `.ais-bars` (5 anchor-tag pill bars), `.ais-caption` (the §6.2 "Read this stack this way" lock copy + the italic source-meta line), `.ais-footer-stats` (3 cards: Investment-to-revenue 19×, Tokens served ~360T/day, Largest ledger Capital). The Power bar carries an inline `.pill-mini.tier-3` chip with text "TIER 3 · v3 PENDING" placed beside its outside-figure $25B per brief §5 Tier disclosure.
  - **Bar widths (locked per brief §5):** Capex `--bar-w:100%;` · Usage `--bar-w:50%;` · Compute `--bar-w:30%;` · Power `--bar-w:22%;` · Revenue `--bar-w:17%;`. Each is set as an inline custom property so a quarterly refresh only edits the 5 inline values, not selectors.
  - **Figure placement:** inside the pill (right-aligned, white) for Capex (100%) and Usage (50%); outside the pill (right of pill via absolute positioning, `--fg-dark-1` colour) for Compute, Power, Revenue per brief §5 "for very small bars where the dollar figure can't fit inside the pill".
  - **Removed sections (per D3/D4):** the prior 5-tile hero reconciliation strip (`<section class="hero">…</section>` with `#hero-numbers`, 5 `.hero-tile` anchors, `.hero-sub` copy "Five ledgers, triangulated from primary sources.") and the prior 4-step narrative-flow loop (`<section class="narrative">…</section>` with `.flow-steps` + 4 `.flow-step` cards: Apps Revenue → Compute → Silicon → Power) are deleted, not replaced. The bars carry both jobs.
  - **Sections kept (unchanged copy):** masthead H2 + tagline + meta description + `og:description` (already on five-ledger framing); scenario what-if strip (Bear/Base/Bull live recompute); hero hook one-liner ($2.50 of compute / $1 Apps, Compute-anchored, ratio computed from `compute / sankey.totalCustomerRevenue`); live tile ($43B Compute Revenue 2025 signal); 5 ledger entry cards (Capital, Revenue, Compute, Usage, Power link-only); footer "Ledger pages" group with all five.
  - **`SCENARIOS` block** — write list trimmed to match the new structure. `applyScenario` now writes only to: `#ais-revenue-figure` (Apps cohort, ±15% band), `#ais-usage-sub` (multiplier + tokens/day sub-line), `#ais-stat-tokens` (footer stat card), `#card-capex / #card-revenue / #card-compute / #card-tokens` (ledger card values), `#hook-ratio` (Compute-anchored hook), `#strip-label` + scenario strip body. Compute, Capex, Power held constant in v1 per brief §7.1 (Bear/Bull coupling deferred). Writes to deleted IDs (`#hero-*`, `#ls-*`, `#nar-*`) removed.

- **`tests/release-check/homepage.spec.ts`** — rewritten to match Option I. 21 desktop-chrome assertions across two `test.describe` groups:
  - Group 1 — `index.html — wq-093 five-ledger reframe (Option I)`: AC1 masthead H2 + tagline + "three ledgers" absent; AC3 (×5 sub-tests) AI Infrastructure Stack renders 5 pill bars with correct hrefs / locked widths / Power tier-3 pill / 3 footer stat cards / §6.2 caption lock copy; AC3-data Compute and Revenue bar figures match `site-data.json` cohort fields; AC4 hero reconciliation tile strip absent (no `.hero-numbers`, no `.hero-tile`); AC5 narrative-flow section absent (no `.flow-steps`, no `.flow-step`); AC6 hook is Compute-anchored `$X.XX` / "compute spend" / "apps revenue"; AC7 live tile = $43B + +153% + 79% + no Copilot/Agentforce; AC8 ledger cards = 5 + Power link-only; AC9 footer Ledger group lists all five.
  - Group 2 — public-page sweep across `/index.html`, `/capital.html`, `/revenue.html`, `/compute.html`, `/usage.html`, `/power.html`, `/methodology.html`, `/about.html`: rendered DOM contains no case-insensitive "three ledgers" substring.

- **(prior cross-page sweep retained from `0fdec64`)** — `methodology.html`, `beta/index.html`, `beta/methodology.html` had their "three ledgers" → five-ledger string fixes done in the prior Option F commit and remain valid (the sweep is layout-independent).

### New files

- (none new in this commit — `homepage.spec.ts` was added in the prior Option F commit and is rewritten here.)

### Test results (local, on the running preview at `:4173`)

- `npm run build-lint` → **0 fail, 1 advisory** (pre-existing `dataReferences map absent`, unchanged).
- `npx playwright test tests/release-check/homepage.spec.ts --project desktop-chrome` → **21/21 passed**.
- Regression: `compute.spec.ts + admin-nav.spec.ts + structure.spec.ts + smoke.spec.ts --project desktop-chrome` → **46 passed, 11 skipped, 0 failed** (the 11 skips are the existing `chips`/`about`-without-collapsible pattern; same baseline as the prior Option F run).
- Manual eyeball:
  - Desktop 1440×900 (Chrome): all 5 bars render in descending size with correct gradient accents; Capex and Usage show figures inside the pill, Compute / Power / Revenue show figures outside-right; Power tier-3 pill renders inline beside `$25B`; 3 footer stat cards in a 3-column grid below the caption. Screenshot at `/tmp/wq093-option-i-desktop.png`.
  - Mobile 375×812 (iPhone 14): bars collapse to full-container width with figures right-aligned inside (Power tier-3 pill remains inline); footer stats stack to 1 column; caption legible. Screenshot at `/tmp/wq093-mobile-clipped.png`.

## Decisions made during implementation

### Strategic
None — all eight Cowork decisions (D1–D8) resolved 2026-05-06. No `docs/decisions/open/` files written.

### Tactical

1. **Visibility-boost function — locked discrete steps per brief §5.** Bar widths are 100/50/30/22/17 % per the brief's locked sizing table. This is logically a piecewise function: linear above 50% (Capex passes through unchanged at 100%, Usage's 49.7% rounds to 50%), then a 17% floor with stepped values for the three smallest bars (30/22/17) so labels remain legible at desktop. Implemented as inline `style="--bar-w:X%;"` on each bar so a quarterly refresh only needs the 5 inline values updated, not selectors. Equivalent to `width_pct = max(linear_pct, 17%)` + a single 30% snap for Compute.
2. **Figure placement — inside-vs-outside split at 50%.** Capex (100%) and Usage (50%) carry their dollar figures inside the pill, right-aligned, in white. Compute (30%), Power (22%), Revenue (17%) carry their figures outside the pill via absolute positioning at `left:calc(100% + 12px)` with colour `--fg-dark-1` so the figure reads against the dark surface rather than the gradient fill. This honours the brief §5 "for very small bars where the dollar figure can't fit inside the pill" rule with a clean, deterministic threshold.
3. **`.ais-bars { padding-right: 120px }` desktop reservation.** The bar container reserves 120px of right-padding so the absolute-positioned outside figures (which extend `100% + 12px` to the right of each bar's right edge) never overflow the section's 1320px container. On mobile this reservation drops to 0 since bars collapse to full width.
4. **Mobile bars collapse to full width — divergence from a literal reading of brief §5 mobile.** Brief §5 says "visibility-boosted widths preserved as percentages, but the smallest bars may now extend almost to the right edge". That description is mathematically inconsistent: 17% of a 351px container = 60px (not "almost to the right edge"), and at 60px the bar can't fit even the icon disc. Tactical call: at ≤768px, all bars stretch to 100% container width; the multiplier sublines ("19×", "9.4×", "2.5×", "1.4×", "1×") carry the descending-ratio story numerically while the visual stack stays legible. Power's tier-3 pill stays inline beside its dollar figure on mobile too. The desktop descending-ratio visual is the canonical Option I form; mobile is a graceful degradation of it.
5. **Italic "notional @ $1.25/M output rate" line dropped on mobile.** Brief §5 "Mobile" section doesn't speak to the `.ais-note` italic line; at 375px it costs an extra wrapped line on the Usage bar without adding new information beyond the §6.2 caption. Hidden via `.ais-note { display: none }` at the mobile breakpoint.
6. **Power tier-3 pill uses canonical `.pill-mini.tier-3` from `ledger-overlays.css`.** Brief §5 explicitly references this token. The class resolves to `var(--violet-tint)` background + `var(--violet)` text, which is the canonical TAIL tier-3 colour even when placed beside an amber Power bar. Visually contrasting on purpose — tier convention beats per-bar accent.
7. **Usage figure locked to brief lock copy ($164B at $1.25/M output rate) despite the latest signals file reading $1.20/M.** The brief's §5 derivation references `data/signals_<latest>.json:openrouter.median_output_price_per_m` and notes the value is "$1.25/M as of `signals_2026-04-25.json`". The most recent signals file actually present in the working tree is `signals_2026-04-03.json` with `median_output_price_per_m: 1.20`; `signals_2026-04-25.json` does not yet exist. Recomputing at $1.20/M would yield ~$157.7B, but the brief's locked editorial copy in §5 and §6.2 explicitly cites $164B and "$1.25/M output rate". Followed the brief's lock copy; flag for follow-up: when the next OpenRouter sweep lands, reconcile the rate and refresh both the visible figure and the §6.2 caption together.
8. **`#ais-stat-capex-ratio = "19×"` is a static value.** Computed as Capex / Apps = 330 / 17.36 = 19.01 → "19×". Static rather than scenario-react because brief §7.1 holds Capex constant in Bear/Bull v1; if a future revision moves Capex under the scenario band, the stat card can be wired through the same `_setText('ais-stat-capex-ratio', …)` pattern.
9. **`.ais-footer-stats` is a 3-column grid with `--space-4` gap on desktop.** Brief §5 calls for an "equal-width grid (`grid-template-columns: repeat(3, 1fr)`, gap `--space-4`)" — implemented exactly. Mobile collapses to `grid-template-columns: 1fr` with `gap: 12px`.
10. **Mobile bar height uses `min-height:56px` with `height:auto`.** Brief §5 mobile says 56px. Implementation uses `min-height` so multi-line labels (Capex's "19× Apps Revenue · 2025 calendar" sub-line is the longest at small widths) don't clip; bars without multi-line content render at exactly 56px. Trade-off: bars are not all uniform-height on mobile, but the editorial story survives wrap.
11. **Visual baselines NOT regenerated.** Same call as the Option F attempt — defer rebaselining until Simon approves the staging build, so we don't ship dead snapshots if Option I needs further visual revision. Rebaseline immediately after approval, before the merge.

## Open items

1. **Visual snapshot rebaseline for `index.html`** (6 viewports) — pending approval. Will run `playwright test tests/release-check/visual.spec.ts --update-snapshots --project <each>` after Simon green-lights the layout.
2. **Bear/Bull Compute coupling** (§7.1 deferral, carried over from Option F) — v1 holds Compute constant. If editorial review later wants the band to move Compute, Capex, and Power too, build a `data/scenarios.json` block defining per-metric sensitivities. Filed as a follow-up; no decision file written; the brief explicitly authorised this deferral.
3. **OpenRouter rate refresh.** Visible Usage figure is locked at $164B at $1.25/M per brief lock copy. Latest signals file reads $1.20/M. When the next signals sweep brings the rate forward, refresh `#ais-usage-figure` (`$164B`) AND the `.ais-caption-meta` line (`$1.25/M`) AND the multiplier sub on the Usage bar (`9.4×`) together. Flagged as a tactical follow-up, not a blocker.
4. **`beta/` archival** — long-term plan should be either delete or fully mirror — not both. The Option F string-sweep changes to `beta/index.html` and `beta/methodology.html` from `0fdec64` remain valid; `/beta/` was not re-mirrored to Option I (out of scope — the brief's §7.2 treats beta as a frozen v1 archive).
5. **Notion wq-093 card** to be moved In Progress → Done with the post-merge SHA (repo cannot mutate Notion directly).

## Acceptance criteria status (brief §3)

- [x] **1. Headline framing replaced.** Masthead H2 + tagline + meta description + og:description updated. `grep -in "three ledgers" index.html` → 0 hits.
- [x] **2. Public-page sweep clean.** `grep -rli "three ledgers" *.html beta/*.html` → 0 hits across the public set; asserted via Playwright Group 2 across 8 public pages.
- [x] **3. AI Infrastructure Stack hero renders (D1 Option I).** New `<section class="ai-infra-stack">` between masthead and the rest of the page; 5 horizontal pill bars on a dark surface with the locked widths (100/50/30/22/17 %); Hepburn Advisory canonical accents (--blue/--violet/--cyan/--amber/--green); each bar a single clickable target landing on its ledger; footer stat cards beneath; §6.2 caption lock copy in place. Asserted by `homepage.spec.ts` AC3 sub-tests.
- [x] **4. Tile strip removed.** No `.hero-numbers` / `.hero-tile` anywhere on the page; asserted by `homepage.spec.ts` AC4.
- [x] **5. Narrative-flow section removed.** No `.flow-steps` / `.flow-step` anywhere on the page; asserted by `homepage.spec.ts` AC5.
- [x] **6. Hook one-liner replaced.** Compute-anchored, ratio computed dynamically from `compute.compute_revenue_2025_gross_usd_b / sankey.totalCustomerRevenue`. Falls back to `$2.50` literal if fetch fails.
- [x] **7. Live tile swapped.** $43B + +153% YoY + 79% frontier; source attribution updated.
- [x] **8. Ledger cards = 5.** All five rendered with locked §6.7 copy; Power card link-only.
- [x] **9. Footer "The Ledger" group lists all five.** Unchanged from wq-088 — already in place.
- [/] **10. Mobile sanity.** Renders cleanly at 375px (manual eyeball pass). **Visual screenshot pass deferred** until rebaselining (see Open items #1). Tactical divergence from a literal reading of brief §5 mobile documented in Tactical #4.
- [x] **11. No regressions.** `npm run build-lint` → 0 fail (1 pre-existing advisory). `compute.spec.ts + admin-nav.spec.ts + structure.spec.ts + smoke.spec.ts` → 46 passed, 11 skipped, 0 failed on desktop-chrome.
- [x] **12. Validator extension passes.** Updated `homepage.spec.ts` 21/21 on desktop-chrome.
- [/] **13. Visual baseline rebaselined.** Deferred to post-approval per Tactical #11.
- [x] **14. Deployment record written** (this file).

## Reconciliation (per CLAUDE.md cross-ledger rule)

| Homepage figure | Source path | Existing publication | Relation |
|---|---|---|---|
| Capex 2025 $330B (AIS Capex bar) | `market.2025.total_capex` (live read; current value 330) | `capital.html` 2025 capex headline | Equal (live read) |
| Usage notional $164B (AIS Usage bar) | derived: `tokens_per_day × 365 / 1e6 × $1.25` (locked per brief; latest signals reads $1.20/M — see Tactical #7) | new on this page; not yet published elsewhere | Documented derivation; brief lock copy honoured |
| Compute $43.1B (AIS Compute bar) | `compute.compute_revenue_2025_gross_usd_b` (~$43.07B per wq-092) | `compute.html` hero | Equal |
| Power $25B (AIS Power bar — Tier 3 placeholder) | hard-coded constant | `compute.html` Layer Stack constant | Equal — same numerical value; not yet wired through `site-data.json` |
| Revenue $17.4B (AIS Revenue bar) | `sankey.totalCustomerRevenue` (~$17.36B) | `revenue.html` cohort total + `compute.html` Layer Stack Apps node | Equal |
| Capital $766B (Capital ledger card; live read) | `cumulative.capex_total` | `capital.html` cumulative headline | Equal (live read) |
| Tokens ~360T/day (AIS Usage sub + footer stat + Usage card) | hard-coded display constant; engine reads `cumulative.tokens_2025_annualized = 310.0` | `usage.html` hero | Documented divergence: site-data carries 310 but the front-end keeps the ~360T display per the engine's `_doc` note (`derive_cumulative_aggregates.py` falls back to a hardcoded ~360T display where annual aggregation isn't yet wired). Inherited from prior `index.html`; not new in this brief. |

No silent divergences from already-published numbers. The Usage notional figure is new editorial material with documented derivation per brief §5.

## Publishing Gate

**Status: awaiting approval.** Per CLAUDE.md (TAIL Publishing Gate, hard stop):

1. ✅ Built on feature branch.
2. ✅ Staging URL: `http://localhost:4173/index.html` (Node `http-server` running locally).
3. ⏳ **Awaiting Simon's explicit affirmative in chat** ("approved" / "ship it" / "promote" / "go live").
4. ❌ Not yet merged to `main`; not yet on the live site.
5. n/a — staging-first is feasible; no exception decision file required.

**Approval timestamp:** _TBD — to be filled in immediately on receipt of approval, alongside the merge SHA._

### What to verify on staging

1. **Masthead** — H2 reads "The AI economy, layer by layer."; tagline reads "Capital in. Compute spent. Power drawn. Tokens out. Revenue back. Five ledgers, one system."
2. **AI Infrastructure Stack** (the 5-bar hero) — bars descend Capex → Usage → Compute → Power → Revenue with widths 100% / 50% / 30% / 22% / 17%; Hepburn Advisory canonical colours (Capex blue, Usage violet, Compute cyan, Power amber, Revenue green); Capex and Usage carry figures inside the pill; Compute, Power, Revenue carry figures outside-right.
3. **Power bar** — the "TIER 3 · v3 PENDING" pill renders inline beside `$25B`.
4. **Footer stat cards** — three cards beneath the bars: "Investment-to-revenue 19×" · "Tokens served ~360T/day" · "Largest ledger Capital".
5. **Caption** — "Read this stack this way…" lock copy in place; the italic source-meta line ("2025 lookback · capex from Capital Ledger · …") below it.
6. **No "three ledgers" string** anywhere on the homepage or any of the 8 swept public pages (case-insensitive).
7. **Ledger card grid** — 5 cards (Capital, Revenue, Compute, Usage, Power) with Power link-only ("v3 in progress", no big number, no tier pills).
8. **No regression on the rest of the page** — hook one-liner ("$2.50 of compute spend stands behind every $1 of customer-paid AI Apps Revenue today."), live tile ($43B Compute Revenue 2025 signal), Bear/Base/Bull scenario toggle, footer.
9. **Mobile (375px)** — bars stack legibly; tier-3 pill stays inline beside $25B; footer stats single-column.
