# wq-093 — Homepage refresh: Compute Ledger integration & "five ledgers" reframe

**Stage:** Scoped
**Priority:** M (no broken behaviour, but homepage is materially out of date with shipped product)
**Owner:** Claude Code
**Briefing status:** ready_for_review
**Decisions resolved:** 2026-05-06 (Simon, in Cowork session)
**Companion review doc (Cowork):** `/Users/simonbowker/Documents/Claude/Projects/The AI Ledger/HOMEPAGE-REVISION-2026-05-06.md`
**Parent context:**
- `docs/deployments/deploy-2026-05-06-wq-087-compute-ledger.md`
- `docs/deployments/deploy-2026-05-06-wq-089-compute-ledger-v2.md`
- `docs/deployments/deploy-2026-05-06-wq-091-compute-ledger-segment-sizing-correction.md`
- `docs/deployments/deploy-2026-05-06-wq-092-compute-ledger-trajectory-no-qoq-drops.md`
- `docs/deployments/deploy-2026-05-06-wq-088-command-centre-nav-cleanup.md`

---

## §0 — Context

The Compute Ledger shipped on 2026-05-06 across wq-087 → wq-089 → wq-091 → wq-092. Power Ledger is also live in primary nav (no longer disabled). The site now ships **five public ledgers** but `index.html` still tells the **three-ledger** story across its masthead, hero, narrative, cards, and meta tags.

This brief refreshes `/index.html` to reflect the five-ledger reality, makes the **Compute Ledger's Layer Stack** the homepage's centre of gravity (per Simon's call: hero feature), and removes every "three ledgers" reference from public pages.

---

## §Decisions (resolved 2026-05-06)

> Source: companion review doc `HOMEPAGE-REVISION-2026-05-06.md` D1–D8. All decisions resolved by Simon in Cowork session; Claude Code should implement as below without relitigating.

| # | Decision | Resolved choice |
|---|---|---|
| D1 | Lead frame | **AI Infrastructure Stack — Option I** — five horizontal pill bars descending in size, one per ledger (Capital → Usage → Compute → Power → Revenue), inspired by Simon's Figma concept. Silicon is dropped (it's part of Capital, not its own ledger); Capex replaces it as the lead figure; Usage joins the stack at notional value (~$164B at median OpenRouter output rate) so all five ledgers get a hero-level entry. The bars REPLACE the previously-planned five-tile hero reconciliation strip and the four-step narrative-flow section — they do that work. See §5 for full visual spec, §6 for copy. *(Iteration: Option B pyramid rejected for visual imbalance; Option F type-led editorial accepted, then superseded when Simon mocked up the 5-bar form in Figma 2026-05-06.)* |
| D2 | Headline + tagline | **H2:** "The AI economy, layer by layer." **Tagline:** "Capital in. Compute spent. Power drawn. Tokens out. Revenue back. Five ledgers, one system." (Simon callout 2026-05-06 — original draft missed Power; final tagline enumerates all five.) |
| D3 | Hero numbers basis | **Tile strip dropped** — the 5-bar AI Infrastructure Stack carries the per-ledger figures into the hero. Power's bar shows $25B with a Tier 3C placeholder pill (matches `/compute.html` precedent for Power) rather than a no-number link-only treatment, because the bar layout requires a figure for visual proportionality. The original "no big-number for Power" intent (D6) is preserved on the cards/footer where Power remains link-only without a tier number. |
| D4 | Narrative-flow replacement | **Drop the narrative-flow section entirely.** The original four-step "Capital → Assets → Tokens → Revenue" loop is removed. The 5-bar AI Infrastructure Stack visual at the top of the page tells that story directly with proportional figures and ledger click-throughs; a separate text-narrative section below would be redundant. |
| D5 | Live-tile signal | **Swap to Compute-derived signal** ($43B 2025, +153% YoY, 79% frontier-lab). Replaces the existing Microsoft Copilot + Salesforce Agentforce ARR tile. |
| D6 | Power placement | **Include** in nav (already done by wq-088), footer "The Ledger" group, and the ledger-cards strip; **exclude** from hero numeric tiles until v3 hardens the figure. |
| D7 | Hero hook ratio anchor | **Compute-anchored**: "$2.50 of compute spend stands behind every $1 of customer-paid AI Apps Revenue today. The gap is funded by hyperscaler equity in the same labs." |
| D8 | Revenue figure restatement | Replace "$22B" hero / card / meta with **$17B (2025 cohort, sum-of-quarterlies basis)**. Old $22B was the cumulative-since-2023 framing; new figure aligns with Compute Ledger Layer Stack's `sankey.totalCustomerRevenue`. |

No open decisions. Implement directly.

---

## §1 — Goal

`index.html` and supporting public-page edits reflect the five-ledger architecture, with Compute as a hero feature and the Layer Stack as the lead visual. No "three ledgers" framing anywhere on public pages. All hero figures restated to current methodology basis (post-wq-091/092). New ledger cards and footer entries for Compute (and Power, where applicable).

---

## §2 — Files touched

### Modified
- `index.html` — masthead, hero strip, narrative flow, ledger cards, footer, hook one-liner, live tile, meta tags. **Primary file.**
- `data/site-data.json` — confirm hero values consumed by `applyScenario` reflect the corrected 2025 figures (script uses `compute` block already; Apps cohort = `sankey.totalCustomerRevenue`).
- `capital.html`, `revenue.html`, `usage.html`, `power.html`, `compute.html`, `methodology.html`, `about.html` — sweep for any "three ledgers" / "Three ledgers, one system" string in copy or meta. Replace with the five-ledger framing only where the current copy explicitly enumerates ledger count; do not rewrite ledger-page bodies otherwise.
- `beta/index.html` — same sweep (it mirrors the prod homepage; if it's still hand-edited keep it in sync; if it's deprecated mark it for archive in the deploy record).

### New
- (none required) — Layer Stack visual reuses the chart pattern from `compute.html` (`#layerstack-chart`); see §5 for implementation guidance.

### Validators
- `scripts/release-check.mjs` / Playwright spec — extend the "no raw keys leaked" / structure spec to assert: (a) string "three ledgers" absent from rendered DOM on every public page, (b) `index.html` ledger-cards count = 5, (c) hero-tile count = 5 (or 4 if D6 shifts to omit Power tile entirely from the strip — current choice keeps it as a no-number tile).

---

## §3 — Acceptance criteria

1. **Headline framing replaced.** Masthead reads "The AI economy, layer by layer." Tagline reads "Capital in. Compute spent. Tokens out. Revenue back. Five ledgers, one system." `<meta description>` and `og:description` updated to match. No "three ledgers" or "Three ledgers, one system" string remains anywhere in `index.html` (case-insensitive grep returns 0 hits).
2. **Public-page sweep clean.** `grep -rli "three ledgers" *.html beta/*.html` returns 0 hits across the public set. (If any page has the phrase in a methodology context that's still accurate — e.g. "three ledgers were originally published" — treat as historical and rewrite to "the original three ledgers were Capital, Revenue, and Usage").
3. **AI Infrastructure Stack hero renders (D1 Option I).** A new hero section sits between the masthead and the rest of the page, showing five horizontal pill bars on a dark surface. One bar per ledger, descending in size: Capex (Capital Ledger) $330B 100% width → Usage $164B notional ~50% width → Compute $43.1B ~30% width → Power $25B ~22% width → Apps Revenue $17.4B ~17% width. Each bar is a single clickable target linking to its ledger page. Layout, colour tokens, type, and exact copy per §5 and §6.2.
4. **Tile strip removed.** The originally-planned five-tile hero reconciliation strip is not built — the bars handle that role. (No regression: nothing on the live homepage today depends on the strip; the current 3-tile version was the strip we were going to replace.)
5. **Narrative-flow section removed.** The "Capital → Assets → Tokens → Revenue" four-step loop on the live homepage is deleted, not replaced with another four-step block. Removed entirely; the bars carry the story.
6. **Hook one-liner replaced.** Reads exactly as §6.4. Pulls $2.50 ratio dynamically from `site-data.json` if computable; otherwise hard-coded with a comment pointing at the source values (Apps $17.36B / Compute $43.07B per wq-092 derivation).
7. **Live tile swapped.** Shows the Compute Revenue 2025 signal per §6.6, with appropriate Tier mix and source attribution.
8. **Ledger cards = 5.** Capital, Revenue, Compute, Usage, Power — each with copy from §6.7. Card grid layout: 3-then-2 or 5-across responsive; whichever the existing CSS supports cleanest.
9. **Footer "The Ledger" group** lists all five (Capital, Revenue, **Compute**, Usage, Power) — adding Compute to the existing footer in `index.html`.
10. **Mobile sanity.** Layer Stack visual and 5-tile strip render legibly at 375px. Tile strip should stack vertically as the current 3-tile pattern does. Layer Stack should switch to a vertical bar/waterfall.
11. **No regressions.** `npm run build-lint` passes (0 fail). Existing Playwright specs (admin-nav, compute, methodology, etc.) continue to pass.
12. **Validator extension passes.** New assertions per §2 Validators added to `compute.spec.ts` or a new `homepage.spec.ts` and pass.
13. **Visual baseline rebaselined.** `index.html` desktop + mobile baselines regenerated; deploy record notes the rebaseline.
14. **Deployment record written** at `docs/deployments/deploy-YYYY-MM-DD-wq-093-homepage-compute-ledger-refresh.md` per CLAUDE.md template.

---

## §4 — Implementation outline

### Phase A — Sweep & prepare data
1. Confirm `site-data.json` exposes the values needed for the homepage:
   - Capital cumulative 2023–25 ($745B) — already wired (`site-data.json:cumulative.capex`).
   - Revenue 2025 cohort sum-of-Q ($17.36B) — read from `sankey.totalCustomerRevenue`.
   - Compute 2025 sum-of-Q post-Copilot ($43.07B) — read from `compute.computeGrossSumOfQ` (or whatever path `derive_compute_revenue.py` writes; check `scripts/derive_compute_revenue.py --print-summary` output).
   - Compute YoY (+153%) — same block.
   - Frontier-lab share of Compute (79%) — same block.
   - Layer Stack four values — same block (Apps cohort + Compute net + Silicon $165B + Power $25B).
   - Tokens/day (~360T) — already wired.
2. If any of those paths don't exist, file a `docs/decisions/open/` decision file naming what's missing rather than hardcoding.
3. Sweep public pages for "three ledgers" string. Document hit count in deploy record.

### Phase B — index.html copy + structure
1. Update `<title>`, `<meta description>`, `og:description` per §6.1.
2. Update masthead H2 + tagline per §6.1.
3. Insert new Layer Stack hero section between masthead and existing hero reconciliation strip — see §5 for visual.
4. Replace existing 3-tile hero strip with the 5-tile version per §6.3.
5. Replace narrative flow per §6.5.
6. Replace hook one-liner per §6.4.
7. Update live tile per §6.6.
8. Expand ledger cards from 3 to 5 per §6.7.
9. Update footer "The Ledger" group.
10. Update the data-driven SCENARIOS block at the bottom of `index.html` so Bear/Base/Bull adjusts the new Compute and Apps Revenue numbers in addition to the existing Revenue + Tokens. (See §7 Edge cases — this is the trickiest piece.)

### Phase C — public-page copy sweep
1. Run `grep -li "three ledgers"` across the public-page set. For each hit, rewrite to either remove the count (e.g., "the ledgers" / "our ledgers") or update to "five ledgers" depending on context.
2. Touch only the matched lines + any directly-adjacent copy that becomes inconsistent. **Do not** rewrite ledger pages otherwise — out of scope.

### Phase D — Validators + tests
1. Extend `compute.spec.ts` (or add `homepage.spec.ts`) to assert acceptance criteria 1, 2, 4, 8, 9.
2. Extend `release-check.mjs` to fail if any public-page rendered DOM contains "three ledgers" (case-insensitive).
3. Re-baseline `index.html` visual snapshots (desktop + 6 mobile viewports per existing pattern).

### Phase E — Verify & ship
1. Run `npm run build-lint` — 0 fail expected.
2. Run `npm run release-check` — all wq-093 specs pass; pre-existing failures unchanged.
3. Manual eyeball at desktop + 375px in browser.
4. Write deployment record.
5. Push to `origin/main`.

---

## §5 — Visual: AI Infrastructure Stack (D1 Option I)

A homepage-specific visual: five horizontal pill bars descending in size, one per TAIL ledger. Inspired by Simon's Figma concept (2026-05-06), executed against the Hepburn Advisory design system tokens defined in `design-system/colors_and_type.css` and `design-system/ledger-overlays.css`. **No new colour values, no new type ramps — every value below maps to an existing CSS variable.**

### Form

Five horizontal pill bars stacked vertically, descending in width by ledger value. Each bar is a self-contained clickable hero element with embedded label, multiplier subtitle, and dollar figure.

```
┌─────────────────────────────────────────────────────────────────┐
│ ($) Capex            19× Apps Revenue              $330B        │  ← 100% width
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────┐
│ ($) Usage    9.4× · ~360T/d     $164B │                            ← 50% width
│     notional @ $1.25/M output rate     │
└──────────────────────────────────┘

┌─────────────────────┐
│ ($) Compute  2.5×   │  $43.1B                                       ← 30% width (visibility-boosted)
└─────────────────────┘

┌──────────────┐
│ ($) Power 1.4│  $25B                                                ← 22% width (visibility-boosted)
└──────────────┘

┌─────────┐
│ ($) Rev │  $17.4B                                                   ← 17% width (visibility-boosted)
└─────────┘
```

### Sizing rules

Bar widths normalised against the largest value (Capex $330B = 100% of the visual's content width):

| Ledger | 2025 figure | Linear-proportional width | Rendered width | Why |
|---|---|---|---|---|
| Capital (Capex) | $330B | 100% | **100%** | Lead bar, anchors the top |
| Usage | $164B notional | 49.7% | **~50%** | Second-largest, anchors the visual mass |
| Compute | $43.1B | 13.1% | **~30%** | Visibility-boosted from linear so internal labels remain legible |
| Power | $25B | 7.6% | **~22%** | Visibility-boosted |
| Revenue (Apps) | $17.4B | 5.3% | **~17%** | Visibility-boosted |

Visibility-boosted widths use a non-linear scaling for the smallest three so labels read at desktop and mobile. Choose a function (e.g. `width_pct = max(linear_pct, 17%)` or sqrt-scaled) — implementation detail, but document the choice in the deploy record so future cycles can refresh figures consistently.

For very small bars where the dollar figure can't fit inside the pill, position the figure to the right of the pill (outside the gradient fill) at `--fg-dark-1` rather than white, so it still reads cleanly against the dark background.

### Usage figure — derivation, source, and treatment

This is the load-bearing methodological choice in the visual.

**Calculation:**
```
tokens_per_year = tokens_per_day × 365
                = 360e12 × 365
                = 1.314e17 tokens (131.4 quadrillion)

usage_notional_usd = (tokens_per_year / 1e6) × median_output_price_per_m
                   = 1.314e11 × $1.25
                   = $164.25B
```

**Source paths:**
- Tokens per day: `site-data.json` existing field (already powers the Usage hero number on the live homepage; keep the same path).
- Median output price: `data/signals_<date>.json:openrouter.median_output_price_per_m` (most recent file; current value $1.25/M as of `signals_2026-04-25.json`).

**Treatment:** rendered as **notional value at OpenRouter median output rate**, NOT actual revenue. The bar carries an italic subtext line "notional @ $1.25/M output rate" inline. The accompanying caption (§6.2) makes clear this is operational-throughput value, not collected revenue (which is the Apps Revenue $17.4B bar).

**Why this rate and not blended retail $0.15/M?** Blended retail would size Usage at ~$19.7B — visually indistinguishable from Apps Revenue. The median output rate is defensible (it's a TAIL-published number with a clear method), large enough to anchor the bottom of the visual mass, and editorially aligned with the "what is operational throughput worth at retail?" question. Trade-off documented; if Cowork later prefers blended-retail framing, flip the source field name and the bar shrinks accordingly.

### Colour tokens (per Hepburn Advisory design system)

Every bar uses an existing CSS custom property from `design-system/colors_and_type.css` §2. **Do not introduce new hues.** Gradients are constructed from the canonical accent + a 10–15% lighter stop:

| Bar | CSS variable | Hex | Gradient endpoint suggestion |
|---|---|---|---|
| Capex | `var(--blue)` (Capital) | `#3B82F6` | linear-gradient to `#60A5FA` |
| Usage | `var(--violet)` (Usage) | `#8B5CF6` | linear-gradient to `#A78BFA` |
| Compute | `var(--cyan)` (tertiary; closest unallocated accent) | `#06B6D4` | linear-gradient to `#22D3EE` |
| Power | `var(--amber)` (Power) | `#F59E0B` | linear-gradient to `#FBBF24` |
| Revenue | `var(--green)` (Revenue) | `#10B981` | linear-gradient to `#34D399` |

Note: this departs from Simon's Figma palette (red Capex, pink Silicon, etc.) on purpose — the design system is canonical, the Figma was a layout concept. The gradient approach (left→right with a lighter stop on the right) preserves the Figma's polished look while staying inside the brand.

### Typography (per design system §6 semantic type slots)

| Element | Token | Notes |
|---|---|---|
| Section title above bars | `var(--type-h2)` | "AI Infrastructure Stack" |
| Section subtitle | `var(--type-meta)` colour `var(--fg-dark-3)` | "2025 · Five ledgers, one stack" or similar |
| Bar label (e.g. "Capex") | `--weight-semi` `--text-md` (15px) `var(--font-sans)` colour `#FFFFFF` | Inside bar |
| Bar multiplier subtext (e.g. "19× Apps Revenue") | `--weight-medium` `--text-xs` (11px) colour `rgba(255,255,255,0.75)` | Inside bar |
| Usage notional subtext | `--weight-regular` italic 10px colour `rgba(255,255,255,0.85)` | Only on Usage bar |
| Bar dollar figure | `--weight-bold` `--text-2xl` (24px) `var(--font-sans)` `font-variant-numeric: tabular-nums` letter-spacing `-0.3px` | Right-aligned inside bar OR outside-right for small bars |

### Spacing & layout (per design system §7)

- Outer container: TAIL homepage container width up to 1320px. Visual sits inside `.container` padding (`32px 24px`). On dark background (`var(--bg-dark)`).
- Bar height: 64px (matches Figma).
- Gap between bars: `--space-3` (12px).
- Bar internal padding: `--space-4` (16px) left and right.
- Icon disc (left of label): 36px diameter, `rgba(255,255,255,0.18)` fill, white `$` symbol centred, 16px font-weight semi.
- Bar corner radius: `var(--radius-pill)` (999px) — full pill.
- Top padding above first bar: `--space-7` (32px). Bottom padding below last bar: `--space-7` (32px) before footer stat cards.

### Footer stat cards (3, mirroring Figma footer aesthetic)

Three small cards in a horizontal row beneath the bars:

| Card | Label (eyebrow style) | Value | Source |
|---|---|---|---|
| 1 | "Investment-to-revenue" | "19×" | Capex / Apps Revenue ratio |
| 2 | "Tokens served" | "~360T/day" | Existing `site-data.json` tokens-per-day field |
| 3 | "Largest ledger" | "Capital" | Static, unless ledger ranking shifts |

Card style: `var(--surface-dark)` background, 1px `var(--border-dark)` border, `var(--radius-lg)` corners, padding `--space-5` (20px), label = `var(--type-eyebrow)` colour `var(--fg-dark-3)`, value = `--weight-bold` `--text-xl` (20px) colour `var(--fg-dark-1)`. Equal-width grid (`grid-template-columns: repeat(3, 1fr)`, gap `--space-4`).

### Interactivity

- Each bar is a single clickable target linking to its ledger:
  - Capex bar → `/capital.html`
  - Usage bar → `/usage.html`
  - Compute bar → `/compute.html`
  - Power bar → `/power.html`
  - Revenue bar → `/revenue.html`
- Hover state per design system §10: `--duration-fast` (120ms) `--ease-out` transition; gradient endpoint shifts one stop darker (e.g. `--blue-600` for Capex hover); cursor pointer; subtle 1px ring in the same accent at 30% alpha.
- Focus-visible: `var(--shadow-focus)` (existing token).

### Tier disclosure (Power)

Power's $25B is Tier 3C placeholder pending Power Ledger v3. Render an inline `.pill-mini` `tier-3` chip (per `ledger-overlays.css`) beside the Power figure with text "TIER 3 · v3 PENDING". This honours the D6 spirit of "no soft numbers in the most-quoted real estate" by being explicit about confidence rather than hiding the figure.

### Mobile (<768px)

- Bars stay full-width-of-container (visibility-boosted widths preserved as percentages, but the smallest bars may now extend almost to the right edge).
- Bar height shrinks to 56px.
- Bar dollar figure: `--text-xl` (20px) instead of `--text-2xl`.
- Footer stat cards: stack to 1 column.
- Container padding follows the existing homepage mobile rule (`16px 12px`).

### Implementation notes

- Build inline in `index.html` using HTML + scoped CSS (no SVG, no canvas — native pill DIVs with linear-gradient backgrounds).
- The visual is one self-contained `<section class="ai-infra-stack">` block. CSS goes in the `<style>` block at the top of `index.html` to match the existing page pattern, OR if the section grows, lift to `design-system/components/ai-infra-stack.css` — tactical call.
- All proportional widths defined as CSS custom properties on the section root so quarterly refreshes only need to update the variables, not selectors.
- No animation beyond the hover state. No watermark (homepage is not screenshot-exported).
- Numeric formatting: `Intl.NumberFormat` or hard-coded "$330B / $164B / $43.1B / $25B / $17.4B" — consistent precision (1 decimal where needed, no decimals where whole-billion).

---

## §6 — Final copy (lock these to the page)

### §6.1 Title / meta / masthead

- **`<title>`**: `The AI Ledger — Hepburn Advisory` *(unchanged)*
- **`<meta description>`**: `The AI economy, layer by layer. Capital in. Compute spent. Power drawn. Tokens out. Revenue back. Five ledgers, one system.`
- **`<meta og:description>`**: `$745B of infrastructure investment. $43B of AI compute revenue earned. $17B of customer-paid Apps Revenue. ~360T tokens/day. The full AI economy, triangulated from primary sources.`
- **Masthead H2**: `The AI economy, layer by layer.`
- **Masthead tagline**: `Capital in. Compute spent. Power drawn. Tokens out. Revenue back. Five ledgers, one system.`
- **Masthead attribution**: `— Hepburn Advisory` *(unchanged)*

### §6.2 AI Infrastructure Stack — caption (under the bars, above the footer stat cards)

> **Read this stack this way:** every $1 of customer-paid Apps Revenue is supported by $19 of capital invested, $9.40 of token throughput at retail rates, $2.50 of compute revenue earned by hyperscalers and neoclouds, and $1.40 of power. The stack doesn't reconcile — that's the story. The gap between what's invested and what comes back as revenue is funded by hyperscaler equity in the labs that drive compute demand.
>
> *2025 lookback · capex from Capital Ledger · compute & revenue sum-of-quarterlies post-Copilot · usage notional at OpenRouter median output rate ($1.25/M) · power placeholder pending v3 · click each bar for its ledger.*

### §6.3 Hero reconciliation tile strip — REMOVED

Per D3, the originally-planned five-tile reconciliation strip is not built. The AI Infrastructure Stack bars (§5) carry the per-ledger figures into the hero and obviate the need for a separate strip. The footer stat cards (§5 Footer stat cards) provide three at-a-glance summary numbers beneath the bars.

### §6.4 Hook one-liner (replaces "$34 of infrastructure")

> **`$2.50` of compute spend stands behind every `$1` of customer-paid AI Apps Revenue today. The gap is funded by hyperscaler equity in the same labs.**

*(Capital-anchored alternative if Simon prefers that on review: `$43 of cumulative infrastructure investment stands behind every $1 of 2025 customer-paid AI revenue.` Both are defensible; D7 baked Compute-anchored.)*

### §6.5 Narrative-flow section — REMOVED

Per D4, the four-step narrative-flow block on the live homepage ("Capital In → Assets Built → Tokens Out → Revenue Back") is deleted, not replaced. The 5-bar AI Infrastructure Stack is the narrative — a separate text-card block below it would be redundant. Delete the corresponding HTML and CSS in `index.html`; do not migrate to a new section.

### §6.6 Live tile (key convergence signal)

| Field | Copy |
|---|---|
| Label | `Key convergence signal` |
| Value | `$43B` |
| Subline | `AI compute revenue earned in 2025 — +153% YoY. Frontier labs paid 79% of it.` |
| Source link | "Source: 10-Q filings →" linking to `/methodology.html#compute-revenue-three-segment-model` (or the closest anchor) |
| Update marker | `Updated May 2026` |
| Footer | `We track this quarterly as the leading indicator of supply-side AI economics.` |
| Colour | Re-use the Compute accent (blue or whatever `--compute` resolves to in the design system; if undefined, use `--accent`) |

### §6.7 Ledger entry cards (5)

For each card: keep the existing visual pattern (title, big value, description, tier pills, "Open X Ledger →" link).

```
Card 1 — Capital Ledger (unchanged from current homepage)
  Value: $745B
  Description: Cumulative 2023–25 AI capital expenditure. Where every dollar went — from spender to silicon to current workload state.
  Tier pills: 40% Sourced · 35% Derived · 25% Modeled
  Link: capital.html

Card 2 — Revenue Ledger (figure restated; description tightened)
  Value: $17B
  Description: Customer-paid AI revenue collected by providers in the 2025 measured cohort. Tracks who pays, how, and where it goes.
  Tier pills: 65% Sourced · 25% Derived · 10% Modeled
  Link: revenue.html

Card 3 — Compute Ledger (NEW)
  Value: $43B
  Description: What hyperscalers and neoclouds earned from AI compute in 2025. Three segments — frontier-lab compute (79%), AI workload compute, hosted model APIs. The circular-financing line: most of it goes to the labs hyperscalers also fund.
  Tier pills: 60% Sourced · 30% Derived · 10% Modeled
  Link: compute.html

Card 4 — Usage Ledger (unchanged)
  Value: ~360T/day
  Description: Token volume, pricing trends, model mix, and demand quality. The operational pulse of the AI economy.
  Tier pills: 50% Derived · 50% Modeled
  Link: usage.html

Card 5 — Power Ledger (NEW — link-only, no big-number)
  Value: (none / em-dash placeholder)
  Description: Power infrastructure underpinning AI compute. v3 hardening in progress — see the Power Ledger for current methodology.
  Tier pills: (none until v3)
  Link: power.html
```

---

## §7 — Edge cases & tactical guidance

1. **Bear/Base/Bull scenarios.** Existing `SCENARIOS` block in `index.html` toggles `revenue` and `tokens` with a ±15% sensitivity band. With Compute now in the hero, scenarios should optionally adjust `compute` and `apps` too. **Tactical call for Claude Code:** if the existing scenario script is straightforwardly extensible, extend it. If the math gets ambiguous (e.g. a Bear case for Compute pulls Apps down further, but how much?), ship Compute and Apps as **non-scenario-toggled** values for v1 of this brief and file an `docs/decisions/open/` decision describing the scenario-band methodology for follow-up.
2. **`beta/index.html` divergence.** This file appears to be a v1 / staging copy. If it's still active, mirror the changes; if it's deprecated, archive it under `archive/` and remove the `/beta/` link from the public footer (verify there isn't one).
3. **The "$22B" ghost number.** This figure appears in `og:description`, the hero strip, the narrative flow, the hook, and the Revenue card today. It was the cumulative-2023-25 framing. We're replacing it with $17B (2025 cohort) everywhere on the homepage. If `og:description` was intentionally kept as cumulative for SEO snapshot reasons, document the call in the deploy record but proceed with the cohort number — consistency across the homepage matters more than preserving the old SEO snippet.
4. **Layer Stack values that don't appear on `compute.html`.** Silicon $165B and Power $25B are sourced from `compute.html`'s Layer Stack but written as constants there per the wq-091 derivation. Read the same source on the homepage; don't re-derive. If the values change in the future, the homepage picks them up automatically only if both pages share the same data path.
5. **Revenue cohort vs ecosystem framing.** The homepage will now publish $17B (cohort) and `compute.html` discusses the cohort-vs-ecosystem-apps gap. Don't introduce a new ecosystem-level Apps figure on the homepage — keep it cohort-only for this brief; rationale already documented on `methodology.html`.
6. **Power Ledger headline number.** Per D6 we don't put a number on the hero tile or the card. If Simon overrides D6 and asks for $25B (the placeholder used on the Layer Stack), that's defensible but Tier 3C — flag with appropriate tier pill.
7. **"Three ledgers" SEO sweep — beware false positives.** Methodology / changelog pages may reference "the original three ledgers were Capital, Revenue, and Usage" as historical context. Don't blanket-replace; read each hit and judge.

---

## §8 — Out of scope

- Redesigning the Capital page to surface the new Capital-to-Revenue ratio explicitly. *(Backlog candidate — wq-094.)*
- Changing the Bear/Base/Bull scenario methodology beyond the minimal extension noted in §7.1.
- Updating sub-page (capital, revenue, etc.) hero sections to share the homepage masthead style — they already exist in their own design and a homepage refresh shouldn't cascade.
- Building a new Apps Ledger, Apps Revenue ecosystem extension, or any new data plumbing — homepage reads existing aggregates only.
- Notion card management (Cowork handles).
- Visual baseline rebaselining of pages other than `index.html` (rebaseline only what this brief touches).

---

## §9 — Definition of Done

- Acceptance criteria §3.1–§3.14 all satisfied.
- All "three ledgers" instances removed from public pages and verified by grep.
- Homepage masthead, hero, narrative, cards, footer all reflect the five-ledger framing with the figures and copy locked in §6.
- Layer Stack hero visual renders on desktop + mobile (375px) and click-throughs work.
- New Playwright assertions pass; pre-existing tests unchanged.
- `npm run build-lint` and `npm run release-check` complete with no new failures.
- Deployment record at `docs/deployments/deploy-YYYY-MM-DD-wq-093-homepage-compute-ledger-refresh.md` summarises diff, decisions, open follow-ups, and rebaselined assets.
- Branch merged to `origin/main` (single fast-forward chain; pattern matches the wq-092 ship).

---

## §10 — Reconciliation (per CLAUDE.md cross-ledger rule)

The new homepage figures must be consistent with already-published numbers on the deeper ledgers:

| Homepage figure | Source path | Existing publication | Expected relation |
|---|---|---|---|
| Capital $745B (CY23–25 cumulative) | `site-data.json:cumulative.capex` | `capital.html` headline | Equal |
| Revenue $17B (2025 cohort) | `site-data.json:sankey.totalCustomerRevenue` | `revenue.html` cohort total + `compute.html` Layer Stack Apps node | Equal |
| Compute $43B (2025 sum-of-Q post-Copilot) | `site-data.json:compute.compute_revenue_2025_gross_sum_of_quarterlies_usd_b` (or equivalent — confirm path) | `compute.html` hero | Equal |
| Tokens ~360T/day | `site-data.json` (existing path) | `usage.html` hero | Equal |
| Layer Stack Silicon $165B + Power $25B | `compute.html` constants | `compute.html` Layer Stack | Equal (read same source, don't re-derive) |

If any homepage figure ends up reading from a different path than the deep page, write a `docs/decisions/open/` decision file explaining why; do not silently diverge.

---

## §11 — Test plan

1. **Build-lint clean.** `npm run build-lint` → 0 fail, 1 pre-existing advisory unchanged.
2. **Playwright homepage spec passes.** New `tests/release-check/homepage.spec.ts` (or extension to existing `compute.spec.ts`) asserts: tile count = 5, ledger-card count = 5, masthead H2 string match, "three ledgers" absent, Layer Stack canvas present, footer contains Compute link.
3. **`grep -rli "three ledgers" *.html beta/*.html` returns 0 matches** after the sweep.
4. **Manual eyeball** at desktop (1320px) and mobile (375px), in dark mode (current default). Verify Layer Stack visual is legible, tiles stack correctly, click-throughs land on the right pages.
5. **Visual baseline rebaselined** for `index.html` across the standard 6 viewports.
6. **Cite-this-page button** on the homepage still copies a sensible string after the refresh.
7. **Release-check** completes with no new failures vs the pre-wq-093 baseline (`docs/deployments/deploy-2026-05-06-wq-092-*.md` is the previous baseline reference).

---

## §12 — Handoff prompt for VS Code / Claude Code

Paste this into a fresh Claude Code session in VS Code, working in `/Users/simonbowker/Developer/apac-ai-intel`:

```
Work item: wq-093 — Homepage refresh: Compute Ledger integration & "five ledgers" reframe.

Read the brief at docs/briefs/wq-093-homepage-compute-ledger-refresh.md before doing anything else. All eight decisions (D1–D8) are resolved (Cowork session, 2026-05-06) — implement as specified, do not relitigate.

Parent context to read first:
- docs/deployments/deploy-2026-05-06-wq-087-compute-ledger.md (original Compute Ledger ship)
- docs/deployments/deploy-2026-05-06-wq-092-compute-ledger-trajectory-no-qoq-drops.md (final Compute Ledger numbers — source of truth)
- docs/deployments/deploy-2026-05-06-wq-088-command-centre-nav-cleanup.md (admin-nav refactor; the public-page sweep should respect its boundaries)

Phase A (data prep) → B (index.html) → C (public-page sweep) → D (validators) → E (verify & ship), per brief §4.

Notable specs:
- §5 — Hero visual is the AI INFRASTRUCTURE STACK (Option I): five horizontal pill bars, one per ledger, descending in size — Capex 100% / Usage 50% / Compute 30% / Power 22% / Revenue 17%. Use Hepburn Advisory design system colour tokens (`--blue --violet --cyan --amber --green`), NOT the Figma red/pink/purple palette. Pill radius `--radius-pill`, type per `--type-h2 / --type-meta / --text-md / --text-xs / --text-2xl`. Three footer stat cards beneath. Native HTML+CSS, no SVG, no canvas. Section §5 documents calculation paths, sizing rules, hover/focus states, and mobile rules.
- §5 Usage figure — Usage bar value = `(tokens_per_day × 365 / 1e6) × median_output_price_per_m`, sourced from `data/signals_<latest>.json:openrouter.median_output_price_per_m`. Currently $164B at $1.25/M. Bar carries an inline italic "notional @ $1.25/M output rate" caveat.
- D3, D4 — both removed sections. Tile strip and narrative-flow block are deleted from `index.html`, not replaced. The bars do that work.
- §6.1 — masthead tagline: "Capital in. Compute spent. Power drawn. Tokens out. Revenue back. Five ledgers, one system." (all five ledgers enumerated in causal order).
- §6.4 — hook ratio is Compute-anchored ($2.50 / $1).
- §6.7 — Power Ledger card is link-only (no big-number, no tier pills) until Power v3 hardens. (Power's bar in the AI Infrastructure Stack §5 does carry a $25B figure with a `tier-3` pill — different placement, different convention.)

Strategic decisions go to docs/decisions/open/ — do not relay them to Cowork via Simon. Tactical decisions (component file location, CSS approach, mobile breakpoint behaviour, etc.) make and log in the deployment record.

PUBLISHING GATE — DO NOT SKIP:
Per the TAIL Publishing Gate (CLAUDE.md, TAIL-WORKFLOW-PROTOCOL.md), the public site `ai-index.hepburnadvisory.com.au` must NOT be updated without Simon's explicit chat approval. Required sequence:

1. Build to a feature branch and deploy to staging/preview.
2. Share the staging URL with Simon in chat plus a short "what to verify" checklist (masthead, type-led layer stack, five tiles, Power link-only card, footer Compute entry, no "three ledgers" anywhere).
3. Wait for explicit affirmative approval ("approved", "ship it", "promote", "go live"). Silence is NOT approval. Approval on something else is NOT approval. Prior-session approval does NOT carry forward.
4. Only THEN merge to main / push to live.
5. If staging-first is impossible, write docs/decisions/open/dec-YYYY-MM-DD-publish-gate-exception.md and stop.

When the work is complete (whether or not approval has been received), write the deployment record at docs/deployments/deploy-YYYY-MM-DD-wq-093-homepage-compute-ledger-refresh.md, cite the staging URL and approval timestamp (or note "awaiting approval"), and report the commit SHA.
```
