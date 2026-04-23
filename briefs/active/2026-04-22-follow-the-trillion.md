# Claims Ledger — In-Dev Page Spec

**Canonical name:** `Claims Ledger` (per GUIDELINES §3.1 `[Noun] Ledger`). The phrase *"Follow the Trillion"* is retained as a hero-copy rhetorical device only — not as the page name.
**Prior working names considered:** `Follow the Trillion`, `Trillion Ledger`, `TAM Ledger`, `$Tn TAM`, `Zoom Out`, `The Denominator`, `Where's the Trillion?`. Decided 2026-04-23.
**Placement:** In-Development page, promoted to main nav at V1.1 alongside `Revenue Ledger` / `Capital Ledger`.
**Dashboard:** https://ai-index.hepburnadvisory.com.au
**Date:** 2026-04-22 (brief), 2026-04-23 (name decision)
**Status:** Draft brief for Claude Code implementation

---

## 1. Purpose

The Ledger currently answers *"How big is AI right now?"* Analysts and vendors answer *"How big will AI be?"* in trillions. This page answers the question underneath both: **if AI revenue hits $X by year Y, what share of the global economy does that imply — and what has to give?**

The pot is not infinite. Every trillion of AI revenue displaces something, is incremental to something, or is paid for out of something measurable. This page makes that arithmetic visible so the reader draws their own conclusion.

## 2. Editorial positioning (matches existing voice)

- Neutral, numbers-first. No "AI bubble" framing, no "this is the future" framing.
- Same transparently-approximate tone: *"Directional comparisons. Benchmarks carry source + review date."*
- Page name conforms to the V2 `[Noun] Ledger` convention (`Revenue Ledger`, `Capital Ledger`, `Claims Ledger`). The "*Follow the* X" construction survives only as hero framing.
- Hero hook in the established style:
  > **"For AI to hit $X by 20YY, it needs to equal Z% of global IT spend, W% of global payroll, or replace Q of today's SaaS market. Pick one."**

## 3. Core interaction

**Primary control:** Year slider `2026 → 2035`, continuous.
**Secondary control:** AI revenue input — dropdown presets (Bear / Base / Bull) + free numeric override.
**Optional control:** Mix toggle — *"Where does it come from?"* three sliders that must sum to 100%:
- % from displacing existing software / SaaS spend
- % from displacing labor cost (wage bill conversion)
- % net-new economic value (productivity / new categories)

As the user moves the slider, every benchmark card recalculates in real time. No page reload.

## 4. Ledger numbers that feed this page

Sourced from the existing `site-data.json` — no new scraping required for the "today" anchor.

| Anchor | Value | Source field |
|---|---|---|
| Current AI-native ARR (booked) | $17.47B | `sankey.totalCustomerRevenue` |
| Current total system revenue | $27.27B | `sankey.totalSystem` |
| VC subsidy gap | $9.8B | `sankey.totalVCSubsidy` |
| Largest single-provider revenue | OpenAI $25B, Anthropic $19B | `dashboard.providers` |
| Current inference spend | $14.03B | `sankey.outcomes` |
| Daily tokens | ~650T | `dashboard.totals` |

Growth curve: use existing Time Machine trajectory to extrapolate a default projection line the user can override.

## 5. Benchmark dataset (new)

New top-level key: `globalBenchmarks` in `site-data.json`. Hybrid static-with-refresh per source-tracking principles.

### Schema

```json
{
  "globalBenchmarks": {
    "lastReviewed": "2026-04-22",
    "nextReview": "2026-07-22",
    "entries": [
      {
        "key": "global_gdp",
        "label": "Global GDP",
        "value": 110000000000000,
        "unit": "USD",
        "year": 2025,
        "source": "World Bank / IMF WEO",
        "sourceUrl": "https://www.imf.org/external/datamapper/NGDPD@WEO",
        "retrievedAt": "2026-04-22",
        "nextReview": "2026-10-22",
        "note": "Nominal USD, rounded",
        "confidence": "High"
      }
    ]
  }
}
```

### Initial benchmarks to populate (all indicative — verify on build)

| Key | Label | ~Value | Why it matters |
|---|---|---|---|
| `global_gdp` | Global GDP | ~$110T | Ultimate denominator |
| `global_services_gdp` | Services-sector GDP | ~$70T | AI predominantly affects services |
| `global_payroll` | Global labor compensation | ~$60T | Displacement math for "AI replaces work" |
| `knowledge_worker_payroll` | Knowledge-worker wage bill | ~$25–30T | The subset genuinely exposed |
| `global_it_spend` | Total global IT spend (Gartner) | ~$5.7T | Direct comparison basket |
| `enterprise_software` | Enterprise software | ~$1.2T | What AI is most likely to cannibalize first |
| `global_saas` | SaaS market | ~$300B | Shelfware / rebundling frame |
| `public_cloud` | Public cloud services | ~$700B | Infrastructure parent market |
| `global_advertising` | Global ad market | ~$1T | Scale reference, not likely displaced |
| `hyperscaler_capex` | Top-5 hyperscaler capex (2025) | ~$350B | Supply side check — is build-out coherent with revenue path |
| `sp500_mcap` | S&P 500 market cap | ~$50T | For valuation sanity |
| `us_gdp` | US GDP | ~$28T | Regional denominator |

Every entry must carry `source`, `sourceUrl`, `retrievedAt`, `nextReview`. This also serves as the data-provenance store referenced in project principles.

## 6. "For That To Be True" (FTBT) computation

For a user-chosen target $T in year Y, the page computes and displays:

1. **Share of GDP** — `T / projected_global_gdp(Y)`
2. **Share of IT spend** — `T / projected_it_spend(Y)` (with a Gartner-style 5% CAGR default, editable assumption)
3. **Multiples of today's SaaS market** — `T / global_saas_today`
4. **Labor equivalence** — `T / knowledge_worker_payroll` → expressed as "equivalent to X% of global knowledge-worker wages"
5. **Revenue per person on earth** — `T / 8.2B`
6. **Implied hyperscaler capex support ratio** — given ongoing `$34 spent per $1 earned` Ledger finding, what capex would be required and does it fit inside global savings?

If the mix-toggle is on:
- **Displacement slice**: show the named SaaS companies/categories that would have to shrink
- **Labor slice**: show the # of knowledge-worker-equivalents at $75K loaded cost
- **Net-new slice**: show historical precedent (mobile, cloud) as calibration

## 7. Visualizations

All dark theme, using existing palette (`--accent #3b82f6`, `--accent2 #8b5cf6`, `--accent3 #06b6d4`, `--orange #f59e0b`).

**V1 (ship first):**
- **Nested treemap / Russian-doll**: AI revenue target sitting inside IT Spend sitting inside Services GDP sitting inside Global GDP. Relative sizes animate with slider.
- **Benchmark ratio cards** (grid of 6): "AI = X% of global payroll", "= Y× SaaS market" etc. Cards flash when user moves slider.

**V1.1 (fast-follow):**
- **Sankey: "Where does $T come from?"** mirroring `Follow the Revenue` style — SaaS displacement / labor displacement / net-new → AI revenue pool. User-adjustable mix sliders feed this directly.
- **Timeline chart**: current Ledger trajectory extended to 2035, with shaded Bear/Base/Bull cones, overlaid against a flat GDP%-share line.

**V2 (later):**
- **Implied wage-bill map**: world map shaded by implied knowledge-worker displacement share by region.

## 8. Hero copy (draft)

Page title renders as **Claims Ledger**. The hero section uses *"Follow the Trillion"* as the rhetorical lead-in, styled as a pre-headline / kicker above the page title.

> *Follow the Trillion —*
> **Claims Ledger**
> The AI Ledger tracks ~$17B of real customer revenue today. The industry's capex implies a destination measured in trillions. This page asks: *for that to be true, what share of the global economy does AI need to own — and where does it come from?*
>
> Drag the year. Pick a revenue target. Watch the denominators.

Methodology caveat (collapsible, matches existing pattern):
> Projections are directional arithmetic, not forecasts. Benchmarks are dated and sourced. AI revenue paths default to extrapolation of Ledger-tracked booked ARR; override any assumption.

## 9. Source tracking & agent log (per project instructions)

- Every `globalBenchmarks.entries[]` item carries a pinned source URL + retrieval date.
- Add `data/sources.log.md` capturing each benchmark fetch/update event (date, operator, prior value, new value, reason).
- If a Claude agent is used to refresh benchmarks, log agent invocation to `data/agents.log.md` with: date, agent name/version, prompt summary, fields touched, commit SHA.
- Quarterly review cadence enforced by `nextReview` dates; build a simple lint that fails the site build if any benchmark is past due.

## 10. Implementation phases

**Phase 0 — Data (1–2 days)**
- Add `globalBenchmarks` block to `site-data.json` with the 12 entries above.
- Populate each with verified value + source URL + `retrievedAt` + `nextReview`.
- Add `data/sources.log.md` and `data/agents.log.md` scaffolds.

**Phase 1 — Static page + hero (1 day)**
- Create `follow-the-trillion.html` on the In-Dev route (filename retained; page title renders as `Claims Ledger`). File rename to `claims-ledger.html` happens at promotion per §3.2.
- Hero copy, methodology collapsible, six benchmark ratio cards rendering against a hardcoded $1T / 2032 default.

**Phase 2 — Interactive slider + calc engine (2–3 days)**
- Year slider 2026–2035.
- Revenue target input (Bear/Base/Bull presets + free entry).
- Real-time recalculation of all six cards.

**Phase 3 — Treemap visualization (2 days)**
- D3 nested-rectangles view. Same color tokens as existing charts.

**Phase 4 — Mix toggle + Sankey (3 days)**
- Three-way mix sliders constrained to 100%.
- Sankey reusing `Follow the Revenue` styling.

**Phase 5 — Promote from In-Dev to main nav (0.5 day)**
- Add nav entry, update `dashboard.html` header hook to reference new page.
- Shareable URL params so slider state is linkable in tweets/LinkedIn posts.

## 11. Open questions

1. Should benchmarks carry a `projectionCAGR` for future years, or keep the page honest by only showing "as % of today's X"? Recommend the latter for V1 — it's more conservative and less contestable.
2. Include an "AI Vintage" variant of the historical trajectory (only ≤5-years-post-ChatGPT companies), consistent with the AI-native filter elsewhere on the site?
3. Embeddable version (iframe snippet) for newsletter/LinkedIn traction — yes/no for V1.1?

---

## Implementation log

Per GUIDELINES §9.3, material scope or status changes during implementation are appended here.

| Date | Status / change | Notes |
|---|---|---|
| 2026-04-22 | Kickoff — spec frozen as contract | `follow-the-trillion.html` committed. Spec frozen as the contract from this date. |
| 2026-04-23 | Brought under formal briefs process | Code pre-dated the §9 handoff process. Brief filed retrospectively into `briefs/active/` to close the gap. The Ledger draft (`The AI Ledger/follow-the-trillion-spec.md`) remains the editable thinking version; this file is the contract. |
| 2026-04-23 | Provenance scaffolding created | Added `data/sources.registry.md`, `data/sources.log.md`, `data/agents.registry.md`, `data/agents.log.md` (all empty, ready for first entries). Closes gap #2. |
| 2026-04-23 | Build lint scaffolded | Added `scripts/build-lint.js` + `scripts/README-build-lint.md`. Implements §5.5 checks: required provenance fields, past-due `nextReview`, slug-like labels, confidence enum, registry presence. Not yet wired into CI. Schema-diff and `dataReferences` checks are TODO. Partially closes gap #4. |
| 2026-04-23 | Name decision pending | Brainstorm completed. Candidates: **Trillion Ledger** (continuity), **Denominator Ledger** (Simon's lean — most precise to purpose), **Scale Ledger**, **Economy Ledger**. Awaiting Simon's pick. Gap #1 still open. |
| 2026-04-23 | Name decided: **Claims Ledger** | Discussed `$Tn TAM`, `TAM Ledger`, `Trillion Ledger`. Rejected TAM framings (frames the page inside vendor-TAM discourse rather than as an audit of vendor claims). Landed on `Claims Ledger` — conforms to §3.1 `[Noun] Ledger`, and names the job of the page (auditing trillion-dollar claims against global denominators). *Follow the Trillion* retained as hero kicker only. Gap #1 closed. |

### Open gaps vs brief & GUIDELINES (as of 2026-04-23)

Flagged for review — items the spec or GUIDELINES call for that may not yet be done. Verify before promotion to live (§3.2 / §11 gate):

1. ~~**Naming decision outstanding.**~~ **Closed 2026-04-23.** Canonical name is **Claims Ledger** (§3.1 `[Noun] Ledger`). *Follow the Trillion* survives as hero kicker only. File rename `follow-the-trillion.html` → `claims-ledger.html` deferred to the §3.2 promotion commit to avoid orphaning the current In-Dev URL mid-iteration.
2. **Provenance scaffolding not yet in repo.** Spec §9 requires `data/sources.registry.md`, `data/sources.log.md`, `data/agents.registry.md`, `data/agents.log.md`. These files do not yet exist under `apac-ai-intel/data/` — only operational logs (`auto_update.log`, `news_monitor.log`, etc.) are present. Required before §11 gate.
3. **`globalBenchmarks` block.** Needs verification in `site-data.json` — all 12 entries with `source`, `sourceUrl`, `retrievedAt`, `nextReview`, `confidence` per GUIDELINES §4.2.
4. **Build lint not yet wired.** §5.5 / spec §9 require a lint that fails on past-due `nextReview`. Open.
5. **Cross-page reconciliation (§5.3.1).** Revenue anchors used in this page (current AI-native ARR $17.47B, etc.) must read from canonical fields in `site-data.json`, not be hardcoded. Verify.

### Promotion readiness

Currently: **In-Dev**, not yet on main nav. Per GUIDELINES §3.2 the page is free to iterate. Promotion requires the §3.2 checklist plus the §11 release gate.
