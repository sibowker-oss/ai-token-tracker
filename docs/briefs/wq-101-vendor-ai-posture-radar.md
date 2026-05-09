# wq-101 — Vendor AI Posture Radar in Usage Ledger

**Stage:** In Progress (D1/D3/D4 resolved 2026-05-09; D5 deferred)
**Priority:** M (editorial enhancement of existing table; no pipeline impact)
**Owner:** Claude Code
**Briefing status:** decisions_resolved
**Companion prototype:** `/Users/simonbowker/Documents/Claude/Projects/The AI Ledger/saas-ai-transition-posture-prototype-v4.html` (visual spec — open in browser)
**Repo copy (canonical):** `/Users/simonbowker/Developer/apac-ai-intel/docs/briefs/wq-101-vendor-ai-posture-radar.md`
**Cowork copy:** `/Users/simonbowker/Documents/Claude/Projects/The AI Ledger/briefings/wq-101-vendor-ai-posture-radar.md`
**Parent context:** Cowork session 2026-05-09 — design conversation across v1 → v4 prototypes
**Touches:** `usage.html` SECTION 5 (Enterprise AI Adoption table), `site-data.json:enterpriseReality`

---

## §0 — Context

The Usage Ledger has an "Enterprise AI Adoption" table at `usage.html` SECTION 5 that compares claimed AI ARR vs estimated real consumption across 12 trad-SaaS products. The table works editorially but the watch signals (the `flags` field per row) are wordy and don't visually separate companies that are actually transitioning from those that are mostly marketing.

**This brief replaces the existing tabular layout** with a posture-radar visualisation alongside the existing claimed-vs-real spine. The radar scores each product on five axes (Disclosure, Bundling, Pricing Model, AI Cost Realisation, Acceleration), gives readers an at-a-glance read of vendor posture, and creates a quarterly progress signal that updates each earnings cycle.

**The editorial point of the new view:** most trad-SaaS AI products score 1–2 across most axes. Only one or two are actually executing on transition (ServiceNow Now Assist, GitHub Copilot stand out). Salesforce Agentforce is the asymmetric case — bold pricing posture without observable workload. The radars make this visually obvious without requiring the reader to parse prose.

The existing claimed-vs-real ARR analysis stays — it's the editorial spine of the page. The radars sit alongside, not instead.

---

## §Decisions

| # | Decision | Status | Recommended | Notes |
|---|---|---|---|---|
| D1 | Section rename | **RESOLVED 2026-05-09** | "SaaS AI Transition Map" (chosen, option c) | Section title changes from "Enterprise AI Adoption" to "SaaS AI Transition Map." Subhead retained as: "Twelve trad-SaaS AI products scored on five posture axes." |
| D2 | Cohort scope | RESOLVED | Keep existing 12 trad-SaaS from `enterpriseReality` | Already classified `tier: trad_saas` per wq-097 D9. The 12 cohort entries are flagged via `postureScores` presence so the view stays cohort-agnostic per §5 #3. The other 8 trad_saas long-tail entries (Atlassian, SAP, Zendesk, HubSpot, Box, GH Adv. Sec., Workday, Zoom) remain in `enterpriseReality` but do not render in the new posture view until they are scored. |
| D3 | Methodology disclosure | **RESOLVED 2026-05-09** | Inline footnote only (chosen) | No standalone methodology page — keep the rubric inline in the section as an expandable accordion (preferred) or always-visible footnote. Reduces surface area to maintain; rubric travels with the table. |
| D4 | Source verification process | **RESOLVED 2026-05-09** | Path (b) — Claude Code drafts citations alongside scores; Simon validates at staging | Bundling/Cost editorial scores carry `_prototype: true` until Simon clears the flag at staging review. Each watch note already cites `arrSource`. Posture banner stays on the section until all `_prototype` flags are cleared. |
| D5 | Quarterly update protocol | **RESOLVED 2026-05-09** | Manual editorial review, documented playbook, visible "last reviewed" date on the surface (chosen) | Auto-derivation rejected as unreliable: BNDL / PRICE / COST / ACCEL aren't extractable from claim text with sufficient confidence. Resolution: editor (or Claude in editorial mode) follows `docs/playbooks/vendor-posture-quarterly-review.md` once per earnings cycle; `vendorPostureMethodology.lastEditorialReview` is bumped on commit; the section header surfaces the date so readers know how stale the radars are. The numeric ARR cells and watch-note copy continue to refresh automatically through the existing claims pipeline between editorial cycles. |
| D6 | Where this lives | RESOLVED | Usage Ledger (current home) | Simon directed in 2026-05-09 Cowork session. Not extending to Frontier ledger. |
| D7 | Share-of-revenue denominator | RESOLVED | Business unit revenue where one exists, parent total only as fallback | GitHub Copilot scored against GitHub ARR (~82%) not MSFT total (~0.5%). Trade-off: scores not strictly cross-comparable but each tells a more honest single-product story. |

~~**Open decisions D1, D3, D4 must be resolved before Phase A starts.** D5 can be deferred to post-launch.~~ Resolved 2026-05-09: D1=`SaaS AI Transition Map`; D3=inline footnote only (no standalone methodology page); D4=path (b) Claude Code drafts citations + Simon validates at staging. D5 deferred.

---

## §1 — Goal

Replace the existing Enterprise AI Adoption table layout with a posture-radar view that:

1. Renders a 5-axis pentagon radar per product
2. Preserves the claimed-vs-real ARR analysis as the editorial spine
3. Makes "which vendors are actually transitioning" visually obvious without reading prose
4. Surfaces share-of-revenue per product so readers can see materiality
5. Updates quarterly as new earnings disclosures shift the scores

---

## §2 — Files touched

### Modified
- `usage.html` — replace `renderEnterpriseTable()` (currently around lines 667–680). Replace section heading per D1. Add radar SVG generator. Add per-row commentary block.
- `site-data.json` — extend each `enterpriseReality` entry with new fields (see §4). Add a top-level `vendorPostureMethodology` block referencing the rubric.

### Validators
- `scripts/release-check.mjs` — assert: (a) radar SVG renders for all 12 products, (b) all required new fields present per row, (c) GM-NA treatment correct for private companies (Databricks, Notion).

---

## §3 — Acceptance criteria

1. Pentagon radar renders for all 12 trad-SaaS products from `enterpriseReality`.
2. Private companies (`ticker: "private"`) render 4-axis radar with COST axis dashed and labelled `COST·NA`.
3. Existing claimed-vs-real ARR data preserved per row (including `arrSource` provenance trail).
4. Each row shows: nameplate (product / parent / ticker / archetype), radar, claimed → real → share data block, growth indicator with prev comparison, source-confidence dot.
5. Watch notes consolidated below the table per row, with `arrSource` citation.
6. Section renamed per D1.
7. Methodology rubric available per D3.
8. Mobile responsive at 375px (single-column stack).
9. Staging URL provided at `/beta/usage.html` for Simon's chat approval per publishing gate.
10. Deployment record at `docs/deployments/deploy-YYYY-MM-DD-wq-101-vendor-ai-posture.md`.
11. No regression on other usage.html sections (Sankey, demand matrix, top consumers).

---

## §4 — Implementation outline

### Phase A — Data structure extensions in site-data.json (0.25 session)

Extend each `enterpriseReality` entry with:

```json
{
  ...existing fields...,
  "archetype": "string — 3–6 word editorial label",
  "arrShare": {
    "value": "string — e.g., '50–82%'",
    "denominator": "string — e.g., 'GitHub ARR (~$2B)'",
    "denominatorType": "business_unit | parent_total"
  },
  "postureScores": {
    "disclosure": 1-5,
    "bundling": 1-5,
    "pricing": 1-5,
    "cost": 0-5,
    "acceleration": 1-5,
    "_prototype": true,
    "_lastVerified": "2026-Q1"
  },
  "gmUnavailable": boolean,
  "watchSignals": "string — narrative paragraph (replaces or augments existing flags)"
}
```

Initial scores from v4 prototype (see Companion prototype HTML). All Bundling and Cost Realisation scores carry `_prototype: true` until D4 source verification removes the flag.

Add at top of `site-data.json`:
```json
"vendorPostureMethodology": {
  "version": "1.0",
  "axesCount": 5,
  "axes": ["disclosure", "bundling", "pricing", "cost", "acceleration"],
  "lastUpdated": "YYYY-MM-DD",
  "sourceBrief": "wq-101-vendor-ai-posture-radar"
}
```

### Phase B — Radar SVG generator in usage.html (0.5 session)

Port `renderRadar(scores, opts)` from the v4 prototype HTML. Pentagon math (5 axes at 0°, 72°, 144°, 216°, 288°). Handle GM-NA treatment per private-company branch. Match existing usage.html visual language (colors, type, spacing) — do **not** ship the prototype's editorial palette as-is.

### Phase C — Replace renderEnterpriseTable() (0.5 session)

Rewrite the section render to use the new layout:
- Grid: nameplate (240px) | radar (220px) | claimed→real→share (1fr) | growth (110px) | source-confidence dot (90px)
- Below table: per-row watch notes with source citation
- Section rename per D1
- Methodology link per D3

### Phase D — Inline methodology footnote (0.15 session)

Per D3: add an expandable methodology accordion (preferred) OR always-visible footnote inline in the section, documenting the 5-axis rubric verbatim per §6 below. No standalone methodology page.

### Phase E — Verify, stage, ship (0.25 session)

1. `npm run build-lint` passes.
2. `npm run release-check` passes including new assertions.
3. Push to `beta`. Manually verify at `/beta/usage.html` and at 375px.
4. **Provide staging URL in chat. Wait for Simon's explicit approval per publishing gate.**
5. Promote to main after approval.
6. Write deployment record.

**Total estimate: ~1.65 sessions.**

---

## §5 — Edge cases

1. **Microsoft trio shares parent GM.** M365 Copilot, GitHub Copilot, Dynamics Copilot all score 5 on Cost Realisation because Microsoft cloud margin compression is shared across products. Correct (one company, one GM) but visually creates three identical Cost spikes. Acceptable — call out in the watch notes for each.

2. **Private companies (Databricks, Notion).** Render 4-axis radar with COST axis dashed and labelled `COST·NA`. Polygon collapses to a quadrilateral on the remaining four points. Watch note states "GM not publicly available."

3. **Cohort expansion.** Data structure must be cohort-agnostic — adding a 13th product should require only a new entry in `enterpriseReality`, not a code change.

4. **Score updates between earnings.** Between quarters, scores stay constant. Disclosure score may shift quarter-over-quarter as share-of-revenue changes post-earnings. Document in methodology.

5. **Provenance dot key.** Source-confidence dot uses existing TAIL provenance tiers (1b filled, 2a half-opacity, 2b hollow). Consistent with other usage.html surfaces.

6. **First-pass score caveat.** Until D4 source verification complete, methodology footnote and section header banner state: "Posture scores in initial release are first-pass editorial estimates pending source verification per TAIL publishing standards." Banner removed once `_prototype: true` flags cleared.

---

## §6 — Scoring rubric (canonical reference)

**Disclosure (DISC)** — Combines provenance tier with AI ARR as share of relevant business-unit revenue.
- 5 = directly disclosed in earnings (tier_1b) AND material share of host business (>5%)
- 4 = tier_1b + 1–5% share, OR tier_2a + >5% share
- 3 = tier_2a + 1–5% share, OR tier_1b + <1% share
- 2 = tier_2b + 1–5% share, OR tier_2a + <1% share
- 1 = tier_2b + <1% share

**Bundling (BNDL)** — Whether AI is priced as a premium add-on or absorbed.
- 5 = aggressive separate pricing (premium add-on)
- 3 = mixed (some bundled, some premium)
- 1 = baked into existing SKUs at no upcharge

**Pricing Model (PRICE)** — Whether the company has changed how revenue scales with AI use.
- 5 = new commercial model (per-action, per-agent, outcome-based) is the only way they sell
- 3 = credit / consumption layer added on top of seat pricing, OR usage option exists alongside seat pricing
- 2 = AI premium SKU added on existing pricing model (tier upgrade)
- 1 = no change, AI absorbed into existing SKUs

**AI Cost Realisation (COST)** — Whether AI inference cost is visibly hitting parent gross margin.
- 5 = clear AI-attributable margin compression (proof of real workload)
- 4 = some AI-attributable compression visible
- 3 = some movement, ambiguous attribution
- 2 = minimal observable signal
- 1 = no observable AI cost in margins
- 0 = NA (private company, no public GM)

Reads counter-intuitively: stable margins on a heavily-marketed AI product is a tell, not a strength.

**Acceleration (ACCEL)** — Whether parent top-line growth has inflected since AI product GA.
- 5 = materially accelerated
- 3 = no inflection (flat)
- 1 = decelerated since AI launches

---

## §7 — Initial scores (from v4 prototype, all subject to D4 verification)

| Product | Parent | DISC | BNDL | PRICE | COST | ACCEL | Archetype |
|---|---|---|---|---|---|---|---|
| M365 Copilot | MSFT | 4 | 4 | 2 | 5 | 3 | Real workload, real cost, small share |
| GitHub Copilot | MSFT | 5 | 5 | 2 | 5 | 5 | AI is the product *(Disc rises from 2→5 with GitHub-ARR denominator per D7)* |
| Google Workspace AI | GOOGL | 3 | 2 | 1 | 2 | 3 | Bundled at scale *(Disc rises from 2→3 with Workspace denominator)* |
| Salesforce Agentforce | CRM | 3 | 5 | 3 | 1 | 1 | Bold pricing, no real cost, no lift |
| Databricks Mosaic | private | 3 | 4 | 2 | NA | 4 | Private momentum, opaque margins |
| ServiceNow Now Assist | NOW | 5 | 5 | 2 | 4 | 3 | Cleanest disclosure, real share |
| Adobe Firefly | ADBE | 2 | 2 | 3 | 1 | 1 | Credits without lift |
| Dynamics 365 Copilot | MSFT | 3 | 4 | 2 | 5 | 3 | Niche scale, shared infra cost *(Disc rises from 1→3 with Dynamics denominator)* |
| Notion AI | private | 3 | 5 | 2 | NA | 4 | Private add-on momentum |
| Intuit Assist | INTU | 2 | 1 | 1 | 2 | 2 | Bundled, stable, invisible |
| Oracle Fusion AI | ORCL | 2 | 1 | 1 | 2 | 3 | Hidden in the bundle *(Disc rises from 1→2 with ORCL Apps denominator)* |
| Snowflake Cortex | SNOW | 3 | 2 | 3 | 2 | 3 | Consumption-bundled |

Italics indicate score updates from v4 prototype reflecting the D7 business-unit denominator decision (the v4 file uses parent-total denominator for Microsoft and Google products — Phase A must apply the corrected denominators).

---

## §8 — Test plan

1. Manual visual inspection: load `/beta/usage.html`, verify all 12 radars render correctly. Verify private-company GM-NA treatment (Databricks, Notion).
2. Mobile sanity at 375px — radar scales to fit, single-column layout.
3. Source-confidence dot key visually consistent with rest of page.
4. Watch notes section: every row has notes + arrSource citation.
5. release-check: new assertions pass.
6. Methodology link works (per D3).
7. Microsoft trio: confirm all three products show identical Cost score (5) — this is correct, not a bug.

---

## §9 — Out of scope

- Cohort expansion beyond existing 12 trad-SaaS products. Separate brief.
- Cross-ledger embedding (radar on Revenue ledger or Frontier page). Per D6, stays in Usage only.
- Auto-updating scores from earnings calls. Manual editorial process per D5.
- Score change history / time-series view (radar morphing quarter over quarter). Useful future feature; out of scope for v1.
- AI-Native challenger comparison view (Glean, Writer, Hebbia). Most are private; separate methodology required.
- Replacing the existing Bundling/Disclosure approach in other ledgers.
- Renaming or restructuring the broader Usage Ledger page. Section-only rename per D1.

---

## §10 — Definition of done

1. All §3 acceptance criteria met.
2. All decisions D1–D7 resolved 2026-05-09 (D5 deferred). Implementation can start immediately.
3. Per D4 (path b): Claude Code drafts source citations alongside scores in Phase A; Simon validates each citation at staging review before main push.
4. Staging URL approved by Simon in chat per publishing gate.
5. Deployment record written.
6. Branch merged to main.
7. Notion Kanban card created and moved to Done.

---

## §11 — Handoff prompt for VS Code / Claude Code

> Paste the block below into a fresh VS Code Claude Code session.

```
Implement wq-101 — Vendor AI Posture Radar in Usage Ledger.

Read in order:
1. /Users/simonbowker/Developer/apac-ai-intel/CLAUDE.md
2. /Users/simonbowker/Developer/apac-ai-intel/docs/briefs/wq-101-vendor-ai-posture-radar.md (canonical brief)
3. /Users/simonbowker/Documents/Claude/Projects/The AI Ledger/saas-ai-transition-posture-prototype-v4.html (visual spec — open in browser to see target layout and pentagon radar)

Context: The Usage Ledger Enterprise AI Adoption table is being replaced with a posture-radar view. Five axes (Disclosure, Bundling, Pricing Model, AI Cost Realisation, Acceleration), pentagon radar per product, alongside the existing claimed-vs-real ARR spine. Scoring rubric in §6 of the brief.

The v4 prototype HTML is the visual reference — port the renderRadar() function and layout grid. Match existing usage.html colors and typography (do NOT ship the prototype's editorial palette as-is).

All decisions D1–D7 resolved (see brief §Decisions). Section name = "SaaS AI Transition Map" (D1). Methodology = inline only, no standalone page (D3). Source verification = Claude Code drafts citations alongside scores in Phase A, Simon validates at staging (D4). D5 deferred to post-launch.

Critical:
- Publish-gated. Staging URL required + Simon's chat approval before any push to main.
- Per D4 (path b): in Phase A, draft a source citation (earnings call, 10-K, pricing page) for each Bundling and Cost Realisation score and surface it in the data structure (e.g., as a `_citation` sibling to the score value). Simon validates each citation at staging review before main push.
- Microsoft's three products correctly share the same Cost score (parent GM is shared). Don't try to differentiate.
- Private companies (Databricks, Notion) render 4-axis radar with COST dashed and labelled NA.
- Existing claimed-vs-real spine stays — radar sits alongside, not instead.
- Disclosure scores per D7 use business-unit denominator where one exists. §7 of the brief notes which scores need updating from the v4 prototype's parent-total denominator.

When done, push to beta, share the staging URL in chat, wait for approval, then promote to main and write deployment record.
```

---

*End of brief.*
