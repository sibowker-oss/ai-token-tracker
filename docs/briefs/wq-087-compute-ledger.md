# wq-087 — Compute Ledger (new public page)

**Working name:** `Compute Ledger`. Public URL: `/compute.html`.
**Date:** 2026-05-05
**Status:** Ready for review. Decisions D1–D5 resolved 2026-05-05 in Cowork session.
**Stage:** Scoped → ready for In Progress
**Priority:** H — direct link to credibility/advisory positioning per strategy doc 2026-05-05; Q1 hyperscaler earnings cycle just landed and Mag3 AI cloud disclosures are fresh.
**Owner:** Claude Code (build, §10 handoff prompt)
**Parent strategy:** `/Users/simonbowker/Documents/Claude/Projects/The AI Ledger/strategy-2026-05-05-stack-and-commercial-value.md`
**Companion conversation transcript:** Cowork session 2026-05-05 — Menlo "Apps + Infra" framing × Q1 hyperscaler earnings × user observation that Menlo Infra ≈ Mag7 hyperscaler AI cloud revenue.

---

## 1. Decisions — RESOLVED 2026-05-05

All five resolved in Cowork session 2026-05-05. Recorded here for downstream reference.

**D1 — Page name.** ✅ **Compute Ledger.** URL: `/compute.html`. Symmetrical with Capital/Revenue/Usage/Power.

**D2 — Hero framing.** ✅ **Distribution chart with concentration headline.** The lead is *who's winning the AI compute layer*, not the aggregate $ total. Hero: a chart showing Mag3 vs neocloud vs Oracle share of Compute Revenue, with a one-line headline like "Microsoft + Google + Amazon capture X% of all AI compute revenue." Total $ is a sub-stat. Rationale: the aggregate isn't surprising to anyone reading earnings; the *distribution and concentration* is the operator/investor-relevant insight (vendor concentration matters for procurement; concentration risk matters for capital allocation).

**D3 — Direct frontier API revenue.** ✅ **OUT of Compute.** Revised after Simon's pushback identified the accounting issue: when Bedrock resells Claude, AWS keeps a margin (that's Compute Revenue) and Anthropic gets the rest (that's Model revenue, paid by AWS to Anthropic). These are two slices of one bill, not double-counted. When someone calls Anthropic direct, 100% is Model revenue (Anthropic's), with the underlying compute showing up on AWS/GCP P&Ls separately as part of their AI cloud line. So **Compute Revenue = revenue earned by entities providing compute capacity (Mag3 + neoclouds + Oracle)**. Direct API revenue stays in the existing Apps/Model Revenue Ledger. The recycling is shown on the Layer-Stack Multiplier visual (§4.4).

**D4 — Recycling visual.** ✅ **Primary visual — Layer-Stack Multiplier as signature chart.** The $1 Apps → $X Compute → $Y Silicon → $Z Power flow is a custom visual that becomes the page's signature. This is the chart nobody else publishes and is the original-IP justification for the page existing.

**D5 — Launch coordination.** ✅ **Coordinated launch with TAIL View Q1 in Week 3** (per strategy doc 2026-05-05, four-week plan). Pacing only — does not affect build scope.

**D6 — Gross vs net Compute Revenue.** ✅ **Publish both, side by side.** Added 2026-05-05 after Simon's accounting question caught a real issue. Hyperscalers reselling frontier models (Bedrock reselling Claude, Azure OpenAI Service, Vertex partner models) almost certainly use principal treatment under ASC 606 — they report **gross** revenue on their P&L with model-lab payments as COGS. This means at the ecosystem level there IS double-counting if you sum hyperscaler gross AI revenue + model-lab revenue, because the customer's $1 shows up on both P&Ls.

The page resolves this by publishing two numbers explicitly:
- **Compute Revenue (gross-disclosed)** — sum of hyperscaler AI lines as filed. Tier 1A. The number that's directly cite-able to 10-Qs.
- **Compute Revenue (net of model pass-through)** — gross minus estimated pass-through to model labs. Tier 2A (the pass-through estimate is editorial). The economically meaningful number for layer value-capture.

The gap is labelled "model lab pass-through" and is itself a publishable insight — almost no other publication surfaces this distinction. The same gross/net visibility should appear on the Apps/Model Revenue Ledger side ("of OpenAI's $XB API revenue, $YB is direct customer billing, $ZB shows up on Microsoft's AI line as principal-treatment Azure OpenAI Service revenue").

**Verification gate before publication:** Confirm principal/agent treatment for Bedrock, Azure OpenAI Service, and Vertex AI partner models by reading the accounting policy notes in the most recent 10-Q for AWS, MSFT, and GOOGL respectively. If any uses agent treatment (net revenue recognition), the aggregation rule changes for that line. See §9.

---

## 2. Purpose

The Ledger currently shows:
- **Capital** — cumulative AI capex (the stock)
- **Revenue** — end-customer AI dollars to providers (the demand-side flow)
- **Usage** — token volumes and demand quality (the operational pulse)
- **Power** — physical constraints (placeholder; v3)

What it does **not** show is the *intra-stack revenue flow*: the dollars that flow between layers of the AI value chain. Specifically: enterprise + frontier-lab dollars to hyperscalers + neoclouds for compute capacity. This is the layer Menlo VC's research is calling "Infra spend" and the layer that Q1 2026 hyperscaler earnings calls reported as "surging AI demand."

The Compute Ledger answers a single question: **what are the world's compute providers earning from AI-attributable cloud and inference workloads, and how is it growing?**

That number is publishable from filings within ~48 hours of each major hyperscaler's quarterly earnings — making this the single highest-news-clock-cadence page on TAIL.

---

## 3. Editorial positioning (matches existing voice)

- Same `[Noun] Ledger` + italic one-liner pattern as other layer pages: *"Hyperscaler AI cloud, neocloud GPU rental, frontier API — what compute providers are earning from AI."*
- Numbers-first. No "AI bubble exposed" framing, no "demand explodes" framing. Show the disclosed quarterly numbers, show the trajectory, let the reader draw the conclusion.
- Continues the source-pinning pattern: every number on the page has `source`, `sourceUrl`, `retrievedAt`, `nextReview`, `confidence`, `tier`. Aggregate Compute Revenue is computed by `derive_compute_revenue.py` (new) with provenance traceable to component disclosures.
- Hero draft (per D2 — distribution + concentration lead):
  > **"Microsoft, Google, and Amazon capture ~X% of all AI compute revenue. Neoclouds Y%. Oracle Z%. ~$NB total in 2025, 80%+ from 10-Q disclosures."**

---

## 4. Page structure

Mirroring the cadence and components established by `capital.html` and `revenue.html`. Five sections.

### 4.1 Hero strip — distribution-led (per D2), gross + net (per D6)

Lead with the distribution, not the total. Publish gross and net side-by-side.

1. **Concentration headline** — "Mag3 capture X%, neoclouds Y%, Oracle Z%" with the actual share split. This is the page's H1 number. (Concentration math uses gross-disclosed for comparability with filings.)
2. **Compute Revenue (gross-disclosed) 2025 annualised** — what the 10-Qs say. Tier 1A.
3. **Compute Revenue (net of model pass-through) 2025 annualised** — what the layer actually keeps after passing through to model labs. Tier 2A. The gap between (2) and (3) is labelled "model lab pass-through" and explicitly named.
4. **Per $1 of Apps Revenue, $W flows to Compute** — the layer-stack ratio that anchors the §4.4 visual. Tier 2A (derived). Use net for this ratio (the layer's actual capture).
5. **Quarter-on-quarter share-shift** — newsiest, refreshes each earnings cycle. "Neocloud share grew from A% to B% in Q1 2026."

Hero layout: stats 1 + 2 + 3 above the fold (distribution + the gross/net pair); 4 + 5 in a secondary row.

### 4.2 Distribution chart (primary visual, per D2)

The hero visual is a stacked bar or treemap showing share of Compute Revenue by provider over time. Default view: most-recent-quarter share. Toggle to: 4-quarter trend, year-over-year shift.

Provider segmentation (left to right by share):
- **Mag3 hyperscalers**: Microsoft Azure AI, Google Cloud AI, AWS AI
- **Oracle Cloud AI**
- **Public neoclouds**: CoreWeave, Nebius (NBIS)
- **Private neoclouds**: Lambda Labs, Crusoe, plus aggregated "other"

Interaction: click a segment to lock its detail in a sidebar showing the underlying disclosure (filing URL, date, quoted line, tier badge).

A secondary view (toggle): the *flow* Sankey showing which buyer types feed which sellers (frontier labs → MSFT/AWS/GCP, enterprise direct → all sellers, etc.). Build this only if buyer-attribution is defensible from filings; otherwise drop it. The distribution chart is the must-ship; the flow Sankey is the nice-to-have.

### 4.3 Quarterly trajectory chart

Line chart, Q1 2024 → most recent quarter, one line per major seller. This is the chart that will get screenshot-quoted by press after each earnings cycle. **Must be designed screenshot-first** — legible at 800×400 thumbnail, brand watermark visible, source disclosure in the chart itself (not as a caption).

### 4.4 The Layer-Stack Multiplier (the original-IP visual)

A single chart, custom for this page, that shows the $1 → $X recycling per the strategy-doc framing. Three or four bars or a flow diagram:
- $1.00 of Apps Revenue (end customer)
- → $0.YY flows down to Compute (paid by Apps providers + direct enterprise)
- → $0.ZZ flows down to Silicon (paid by Compute providers)
- → $0.WW flows down to Power (paid by Silicon + Compute)

This is the chart nobody else publishes. It's *the* reason this page exists from a credibility standpoint. Treat it as the page's signature visual.

### 4.5 What Would Have to Be True (mirrors Revenue page)

Convergence signals: at current trajectory, when does Compute Revenue cross $X / cover Mag7 AI capex / produce 30% gross margins on inference / etc. Each signal has a defined threshold, current observed value, and a tier badge.

---

## 5. Data model

### 5.1 New `site-data.json` block: `compute`

```json
{
  "compute": {
    "lastReportedQuarter": "2026Q1",
    "annualised_revenue_2025_gross": <number>,
    "annualised_revenue_2025_net": <number>,
    "model_pass_through_2025": <number>,
    "concentration": {
      "mag3_share_pct": <number>,
      "oracle_share_pct": <number>,
      "public_neocloud_share_pct": <number>,
      "private_neocloud_share_pct": <number>,
      "other_share_pct": <number>
    },
    "components": {
      "msft_ai": {
        "value_gross": ..., "value_net": ..., "pass_through_estimate": ...,
        "tier_gross": "1A", "tier_net": "2A",
        "principal_agent_confirmed": true,
        "source": "MSFT 10-Q FY26 Q3", "sourceUrl": "...", "retrievedAt": "...", ...
      },
      "googl_cloud_ai": { ... },
      "amzn_aws_ai": { ... },
      "oracle_cloud_ai": { ... },
      "coreweave": { ... },
      "nebius": { ... },
      "lambda_labs": { ... },
      "crusoe": { ... }
    },
    "quarterly": [
      { "quarter": "2024Q1", "msft_ai": ..., "googl_cloud_ai": ..., ... },
      ...
    ],
    "layer_stack_ratios": {
      "apps_to_compute_2025": ...,
      "compute_to_silicon_2025": ...,
      "silicon_to_power_2025": ...
    },
    "_notes": "Direct frontier API revenue (OpenAI API, Anthropic API) is OUT of compute per D3 — lives in existing Apps/Model Revenue Ledger. Bedrock/Vertex/Azure-hosted reseller revenue is split: cloud margin is in compute (Mag3 lines), model labs' share stays in Apps/Model. See methodology page."
  }
}
```

### 5.2 New aggregator script: `scripts/derive_compute_revenue.py`

Pattern: same as `derive_cumulative_aggregates.py` (wq-063) and `derive_collected_revenue.py` (wq-048). Reads `entities.json` + a new `data/compute_disclosures.json` (filings extracts), applies the aggregation rule, writes `site-data.json:compute.*`.

Aggregation rule (precise — per D3 + D6 resolutions):

**Direct frontier API revenue is OUT** (D3). OpenAI API and Anthropic API revenue stay in the existing Apps/Model Revenue Ledger.

**For each component, compute BOTH gross and net** (D6):

| Component | Gross (Tier 1A) | Net = Gross − Pass-through | Pass-through estimate basis |
|---|---|---|---|
| MSFT Azure AI | Disclosed AI revenue line from 10-Q | Gross − Azure OpenAI Service pass-through to OpenAI | Estimated from OpenAI's reported revenue × MSFT-OAI rev share split (per assumptions-audit §1.1: Zitron's 20% rev share methodology). Tier 2A. |
| GOOGL Cloud AI | Disclosed AI-contribution-to-Cloud-growth derived line | Gross − Vertex partner-model pass-through (Anthropic, Mistral, others on Vertex) | Estimated from Anthropic Vertex revenue + smaller partner lines. Tier 2A. Document low-precision flag if disclosure is thin. |
| AMZN AWS AI | Disclosed AI revenue narrative ("multi-billion run-rate") | Gross − Bedrock pass-through (predominantly Anthropic, plus Meta Llama, Mistral) | Estimated from Anthropic's AWS revenue + Bedrock partner lines. Tier 2A. |
| Oracle OCI AI | AI-attributable portion of OCI (editorial estimate) | Gross − OpenAI compute pass-through (Stargate workload begins billing) | Tier 2A both ways given disclosure thinness. |
| CoreWeave | Total revenue (filed) | Same as gross (CoreWeave is the cloud, no pass-through to model labs in this direction; ~85% concentration to MSFT customer is buyer-side, not pass-through) | Tier 1A. |
| Nebius | Total revenue (filed) | Same as gross | Tier 1A. |
| Lambda Labs | Total revenue (press-disclosed) | Same as gross | Tier 1B/2A. |
| Crusoe | Total revenue (press-disclosed) | Same as gross | Tier 1B/2A. |

**Aggregate row:** Compute Revenue (gross) = sum of components' gross values. Compute Revenue (net) = sum of components' net values. Pass-through total = gross − net. Document the pass-through total as a publishable number in its own right.

**Verification gate (D6):** Before publication, confirm principal/agent treatment for AWS Bedrock, Azure OpenAI Service, and Vertex AI partner models in the most recent 10-Qs' accounting policy notes. If any uses agent (net) treatment, that line's gross = net (no transformation needed) and the rule above changes accordingly. Document the confirmed treatment per entity in `data/methodology_constants.json`.

### 5.3 Source pipeline additions

These extend the existing `data/sources.registry` rather than replace.

| Source | Method | Cadence | Tier | Notes |
|---|---|---|---|---|
| MSFT 10-Q (Azure AI segment commentary) | EDGAR scan (already active) | Quarterly | 1A | Need extractor enhancement to capture "AI contribution to Azure growth" specifically |
| GOOGL 10-Q (Google Cloud segment) | EDGAR scan (already active) | Quarterly | 1A | Same — extractor enhancement for AI-attributable line |
| AMZN 10-Q (AWS segment) | EDGAR scan (already active) | Quarterly | 1A | Same |
| ORCL 10-Q (OCI segment) | EDGAR scan — **Oracle ticker not yet in scan list per data/edgar-tickers.json**; ADD | Quarterly | 1A | New — but trivially — see edgar-tickers-deferred.md |
| CoreWeave 10-Q (post-IPO) | EDGAR scan — confirm in list | Quarterly | 1A | |
| Nebius (NBIS) 6-K | EDGAR scan | Quarterly | 1A | |
| Lambda Labs (private, S-1 if filed) | Manual / press | Event-driven | 2A | |
| Crusoe (private) | Press releases, IR statements | Event-driven | 2A | |
| OpenAI API revenue | Existing consensus engine | Quarterly editorial | 1B/2A | Pulled from `derive_collected_revenue.py` segments |
| Anthropic API revenue | Existing consensus engine | Quarterly editorial | 1B/2A | Same |

---

## 6. Files touched

### New files
- `compute.html` (new public page, mirroring `revenue.html` structure conventions)
- `scripts/derive_compute_revenue.py` (aggregator)
- `data/compute_disclosures.json` (filings extracts feeding the aggregator)

### Modified files
- `index.html` — add Compute Ledger to nav (4 → 5 stack pages), update hero from 3 → 4 stats (or replace one of the existing per D2)
- `power.html`, `capital.html`, `revenue.html`, `usage.html` — nav update only (add Compute link)
- `site-data.json` — new `compute` block per §5.1
- `data/edgar-tickers.json` — add ORCL if not present
- `methodology.html` — new section on Compute Revenue methodology + double-counting
- `data/methodology_constants.json` — document the aggregation rule and double-counting choice
- `entities.json` — confirm Oracle Cloud entity exists; add if missing
- `data/render_config.json` — add page registration

### Reference but do NOT modify
- `data/sources-policy.md` (live in TAIL project folder as `data-sourcing-policy.md`) — Compute Ledger inherits provenance schema, no new types
- `assumptions-audit.md` — references for current Mag3 AI revenue disclosures already documented

---

## 7. Acceptance criteria

The page ships when **all** of these are true:

1. **Headline number defensible.** The Compute Revenue 2025 number can be reproduced by reading `data/compute_disclosures.json` and running `derive_compute_revenue.py`. Every component value cites its 10-Q filing (or equivalent) by URL and retrieval date.
2. **Provenance complete.** Every number rendered on the page (hero, Sankey/bar, trajectory chart, layer-stack ratios) carries `source`, `sourceUrl`, `retrievedAt`, `nextReview`, `confidence`, `tier`. `release-check.mjs` extended to enforce.
3. **Layer-Stack Multiplier visual works.** §4.4 chart is built, the math is documented in methodology, and the visual is screenshot-legible at 800×400.
4. **News-clock cadence demonstrated.** A first quarterly update is performed manually within the build window — pulling MSFT FY26 Q3, GOOGL Q1 2026, AMZN Q1 2026 disclosures — to validate the aggregator produces a sensible aggregate. Document the time taken end-to-end (filing-drop → page-update). Target: <48 hours.
5. **Methodology page updated.** Compute Revenue methodology section added, with explicit treatment of the double-counting question (per D4) and the aggregation rule.
6. **Nav consistent.** All five layer pages (Capital / Revenue / Compute / Usage / Power) carry Compute in nav. The home page hero accommodates the new tile.
7. **Mobile-render check.** All four primary visuals legible on a 375px viewport.
8. **No regressions.** Existing site-data.json hash + render_config registry pass `release-check.mjs`.

---

## 8. Edge cases and risks

1. **MSFT bundles Copilot + Azure AI in their AI revenue line.** Copilot is arguably Apps, not Compute. Brief recommendation: include MSFT's full AI revenue line in Compute (gross), footnote that ~$Y of it is Copilot (Apps-side, not infra), surface that in the Layer-Stack Multiplier visual. Decision is in the methodology page, not the brief.
2. **Google Cloud AI is a calculated portion of total Google Cloud.** Alphabet doesn't disclose AI as a standalone segment. The page must use the most-recent disclosed AI-contribution-to-Cloud-growth language and tag tier 2A for any derived split.
3. **AWS is similarly opaque.** AWS Bedrock revenue is not separately disclosed; Amazon talks about "multi-billion-dollar AI revenue run-rate" in earnings narrative. Same approach — extract the most specific disclosure available, tag tier accordingly.
4. **CoreWeave / Nebius / Lambda are largely AI-pure, but customer concentration is the story.** Consider a callout: "85% of CoreWeave revenue is from one customer (Microsoft, who is in turn passing OpenAI workload through)" — this is the circular-financing thread. Keep it factual.
5. **Oracle's $300B OpenAI commitment is contractual, not realised revenue yet.** The page must NOT count contracted-but-unbilled revenue. Realised quarterly billings only. Footnote contracted commitments separately if useful.
6. **Pass-through estimation precision.** The net Compute Revenue depends on estimating model-lab pass-through (D6). Where the underlying disclosures are thin (Vertex partner revenue, Bedrock model mix), the net number is tier 2A and the precision should be flagged in the tooltip. Document the methodology so a sceptical reader can reproduce the math.
7. **Principal/agent treatment risk (D6 verification gate).** If any of Bedrock / Azure OpenAI Service / Vertex AI uses agent treatment (net revenue recognition) rather than principal (gross), that component's aggregation rule changes and the gross/net distinction collapses for that line. Must verify in 10-Q accounting policy notes before publication. See §9.5.
8. **Quarterly cadence ≠ annual cadence.** The aggregator must handle "we have Q1 from MSFT but not yet from GOOGL" gracefully — partial-quarter rendering with explicit "awaiting [N] disclosures" badge.
9. **Apps/Model Revenue Ledger sister update.** D6 implies a parallel update on the existing Revenue Ledger to surface the pass-through visibility on that side ("of OpenAI's $XB API revenue, $YB shows up on Microsoft's Azure AI line as principal-treatment Azure OpenAI Service revenue"). This is OUT of scope for wq-087 build but should be filed as a follow-on Notion card.

---

## 9. Test plan

1. **Aggregator unit test.** `scripts/derive_compute_revenue.py` reproduces a known-good aggregate (both gross and net) from a fixed `data/compute_disclosures.json` snapshot.
2. **Provenance lint.** Extend `release-check.mjs` to fail if any `compute.*` value lacks the full provenance block. For pass-through fields, require an explicit `pass_through_basis` field documenting the estimation method.
3. **Render check.** Per memory `feedback_validate_rendered_output`: validate the rendered `compute.html` after build, not just the engine output. Take a screenshot, eyeball the Layer-Stack Multiplier, confirm both gross and net hero numbers match `site-data.json:compute.annualised_revenue_2025_gross` / `_net`.
4. **News-clock dry run.** Manually replay the most recent MSFT/GOOGL/AMZN disclosure cycle. Document the time from disclosure to live-page-update. If >48h, identify the bottleneck and brief a fix.
5. **Principal/agent verification (D6 gate).** Before publication, read and document the revenue recognition policy notes from the most recent 10-Q for AWS, MSFT (Azure), GOOGL (Cloud), and ORCL (OCI). For each, confirm whether reseller revenue (Bedrock / Azure OpenAI Service / Vertex partner / OCI partner) is recognised gross (principal) or net (agent). Record findings in `data/methodology_constants.json` with the filing URL and retrieval date. If any uses agent treatment, update the aggregation rule for that component before shipping.
6. **Mobile screenshot.** 375px Safari + Chrome.
7. **Cross-page link integrity.** All 5 layer pages link to all others in the nav.
8. **Distribution chart fallback.** Toggle the data-shape between current and synthetic-sparse — confirm the chart degrades gracefully if a quarter is missing.

---

## 10. Out of scope (do NOT do in this brief)

- Building a `silicon.html` page (separate brief; strategy doc §3.2)
- Restructuring `capital.html` to remove silicon-layer content (separate decision)
- Adding power-layer revenue to the Layer-Stack Multiplier (Power is still placeholder; defer to wq-006 Power Ledger build)
- Touching `Revenue Ledger` Sankey structure (its existing job is fine; Compute is parallel, not a restructure)
- Building the press kit / launch package (separate Cowork session — strategy doc Week 3)
- Adding a "Quote this number" button (separate item per strategy doc §3.4 / 4-week plan Tier 4)

---

## 11. Definition of Done

- Page live at `https://ai-index.hepburnadvisory.com.au/compute.html`
- All 5 layer pages cross-link in nav
- Methodology page documents the aggregation rule, double-counting handling, and Layer-Stack Multiplier math
- `derive_compute_revenue.py` runs in the existing cron / signal pipeline
- `release-check.mjs` extended and passing
- Deployment record written to `docs/deployments/deploy-2026-MM-DD-wq-087-compute-ledger.md` per `TAIL-WORKFLOW-PROTOCOL.md`
- Notion card updated to Done with deploy commit SHA

---

## 12. Handoff prompt for VS Code / Claude Code

Copy-paste this into a new Claude Code session in VS Code:

```
Read /Users/simonbowker/Developer/apac-ai-intel/docs/briefs/wq-087-compute-ledger.md in full. The §1 Decisions are all RESOLVED — confirm you understand:
- D1: Page name = Compute Ledger (URL /compute.html)
- D2: Hero is distribution-led with concentration headline (NOT total $)
- D3: Direct frontier API revenue is OUT (lives in existing Apps/Model Revenue Ledger)
- D4: Layer-Stack Multiplier is the page's signature visual
- D5: Coordinated launch with TAIL View Q1 in Week 3 (pacing only)
- D6: Publish BOTH gross and net Compute Revenue, side by side; verify principal/agent treatment in 10-Q accounting notes before publication (this is a gate, not a footnote)

Check /Users/simonbowker/Developer/apac-ai-intel/docs/decisions/open/ for any wq-087 decisions filed by Simon since brief was written.

Build plan:
1. **Phase A — accounting verification (D6 gate). Do this FIRST before any other work.** Read the revenue recognition policy notes in the most recent 10-Q for AWS (Amazon), MSFT (Azure), GOOGL (Google Cloud), ORCL (Oracle). For each, confirm whether reseller revenue (Bedrock / Azure OpenAI Service / Vertex partner / OCI) uses principal (gross) or agent (net) treatment. Document findings in data/methodology_constants.json with filing URL and retrieval date. If anything other than principal-everywhere, FILE A DECISION FILE to docs/decisions/open/ and pause for Simon — the aggregation rule changes.
2. Phase B — data layer. Add Oracle to data/edgar-tickers.json if missing. Confirm/add Oracle Cloud entity in entities.json. Create data/compute_disclosures.json with the most recent quarterly disclosures for MSFT, GOOGL, AMZN, ORCL, CoreWeave, Nebius, Lambda, Crusoe (use the source-pinning schema from data-sourcing-policy.md, capture both gross and pass-through estimate per §5.2 table). Write scripts/derive_compute_revenue.py following the pattern of derive_cumulative_aggregates.py and derive_collected_revenue.py — must compute both gross and net aggregates. Wire it into auto_update.py.
3. Phase C — page build. Create compute.html mirroring revenue.html structure conventions. Hero strip (5 stats per §4.1, gross + net side-by-side). Primary distribution chart per §4.2. Quarterly trajectory chart (screenshot-first — see §4.3). Layer-Stack Multiplier visual per §4.4 — this is the page's signature visual, do not skimp. WWHBT panel per §4.5.
4. Phase D — integration. Add Compute to nav across all 5 layer pages + index.html. Update methodology.html with the new section including the gross/net distinction and pass-through methodology. Update data/render_config.json. Extend release-check.mjs per §7 acceptance criteria (including the pass_through_basis field requirement).
5. Phase E — validation. Run the news-clock dry run per §9.4. Take and view screenshots per §9.3. Confirm mobile render. Write deployment record per §11.

If at any step a strategic decision arises that wasn't anticipated in the brief, write a decision file to docs/decisions/open/ per TAIL-WORKFLOW-PROTOCOL.md and stop that phase. Tactical decisions (variable names, file structure, exact visual implementation) — make them and log in the deployment record.

Validate the rendered page after build per memory feedback_validate_rendered_output (do not trust engine reports alone). Update the Notion card (WQ ID wq-087) to In Progress when starting and Done with the deploy commit SHA when shipped.
```

---

*End of brief. Save copy to `/Users/simonbowker/Developer/apac-ai-intel/docs/briefs/wq-087-compute-ledger.md` per TAIL-WORKFLOW-PROTOCOL.md before starting build.*
