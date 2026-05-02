# APAC AI Intelligence Platform — Complete Assumptions Audit

**Generated:** 2026-04-04
**Source:** Full conversation transcript (b69f5507) + all live code/data files
**Scope:** Every assumption, calculation, estimation, and methodology decision made during development

---

## 1. Revenue Assumptions — Provider Revenue Figures

### 1.1 OpenAI

| Metric | Value | Source | Confidence | Notes |
|--------|-------|--------|------------|-------|
| 2024 actual collected revenue | ~$3.6B | Zitron / Microsoft leaked docs | Estimated | Reverse-engineered from MSFT rev share: $493.8M / 0.20 = ~$2.5B, net of MSFT-OAI payments pushes higher |
| H1 2024 revenue (Zitron method) | ~$2.27B | Zitron / MSFT internal docs showing $454.7M H1 rev share at 20% | Estimated | $454.7M / 0.20 = $2.27B |
| H1 2025 actual collected | ~$4.3B | The Information (cited by Zitron) | Estimated | Zitron's MSFT rev share analysis implies it may be closer to $2.27B — a ~$2B gap. Used $4.3B as the more conservative figure |
| H1 2025 inference spend | $5.022B | Zitron / Microsoft leaked documents | Verified | EXCEEDS H1 revenue of $4.3B. Full 2024-Sep2025 inference total: $12.4B |
| 2025 full-year estimated collected | ~$11.9B | Zitron extrapolation from MSFT docs | Estimated (parked) | Below Altman's claim of "well more than $13B" and far below $20B ARR. Our original Sankey had $6B (too low) |
| **2025 engine output (current, wq-048)** | **$9.31B** | `scripts/derive_collected_revenue.py` | Estimated | Was $7.65B (hand-curated §7.2 weighted consensus). As of 2026-05-02 publishing $9.31B (engine §2 method on $5B start / $20B end ARR with NRR boost 1.075). Editorial position revised upward to reflect documented methodology. See changelog entry 2026-05-02. |
| 2025 end-of-year ARR | $20B | All-In Podcast / Jason Calacanis / multiple reports | Verified | Grown from $2B to $20B in 24 months |
| March 2026 ARR | $25B | Sacra | Estimated | Uses best 4-week period x 12, NOT calendar month x 12 — confirmed by Zitron |
| $25B ARR methodology | Best 4-week period x 12 | Zitron / confirmed methodology | Verified | CRITICAL: inflates figure by 10-15% vs monthly calculation |
| 2025 operating loss | ~$6B | NYT / multiple sources | Estimated | Multiple reports indicate $5-6B annual loss |
| 2026 projected cash burn | ~$25B | The Information / multiple | Unverified | Even as revenue hits $25B ARR |
| 2030 internal revenue forecast | $280B | Fortune | Unverified | 21x growth in 5 years from current ~$13B |
| Spending ratio | $2.25-$2.60 per $1 revenue | Zitron | Estimated | ~60% is inference, rest is R&D ($6.7B H1), sales/marketing ($2B H1) |
| Valuation (Feb 2026) | $840B | CNBC / All-In | Estimated | $120B total funding raised |
| 2026 ad pilot ARR | $100M | CNBC | Unverified (declined) | Hit $100M ARR in under 2 months — declined for Vault |
| Consumer/Business split | 60% consumer / 40% business | Editorial estimate | — | Used in dashboard |

### 1.2 Anthropic

| Metric | Value | Source | Confidence | Notes |
|--------|-------|--------|------------|-------|
| Cumulative collected revenue (all-time through early 2025) | ~$5B | Sworn court affidavit | Verified (95% credibility) | Highest confidence data point. Cumulative, not ARR |
| 2025 actual collected revenue | ~$4.5B | The Information / Sacra | Verified | Cross-referenced with court affidavit. Consensus-confirmed at $4.71B weighted avg |
| **2025 engine output (current, wq-048)** | **$4.71B** (override) | `data/consensus_overrides.json` | Verified | Engine §2 method bottoms out at $2.92B–$3.34B for Anthropic due to fallback haircut (no comparable starting ARR for log_mean). Hand-curated $4.71B per §7.2 weighted consensus pinned via editorial override; expires 2027-01-01 to force re-review. |
| 2025 cash burn | ~$3B | Sacra | Estimated (parked) | Down from $5.6B prior year. Our Sankey had $5.2B operating loss — $3B cash burn may reflect different accounting |
| 2025 operating loss | ~$5.2B | APAC AI Intel (derived) | Estimated | Total system cost $9.7B minus $4.5B customer revenue |
| February 2026 ARR | $14B | Brad Gerstner (Altimeter Capital, investor, All-In Podcast) | Verified | Authoritative — direct investor with board-level access |
| February 2026 monthly revenue | $6B (28-day month) | Brad Gerstner | Verified | Confirms $14B ARR figure (annualized ~$72B but a single peak month) |
| March 2026 ARR | $19B | Sacra | Estimated | Up 1,167% YoY. NOTE: ARR not collected |
| Revenue mix | 70-75% API, 10-15% subs, remainder reserved capacity/enterprise | Sacra | Estimated | Key for Sankey channel allocation |
| Claude Code ARR (Feb 2026) | >$2.5B | Sacra | Estimated | Doubled since start of 2026 (was $500M ARR Sep 2025) |
| Business customers | 300,000+ | Sacra | Estimated | ~80% of revenue. 500 spending >$1M/yr. 8 of Fortune 10 |
| Valuation (Feb 2026) | $380B | Sacra / All-In | Verified | Series G, led by GIC and Coatue. Amazon total $8B |
| Consumer/Business split | 35% consumer / 65% business | Editorial estimate | — | Used in dashboard |
| Revenue per gigawatt | $10B annual revenue per GW | Sarah Friar (Anthropic CFO) via Chamath | Verified | Key metric for DC economics |

**Anthropic Revenue Consensus Result:**
- Weighted consensus: **$4.71B** (for 2025 collected revenue)
- 3 sources, $0.50B spread
- Court filing ($5B) at 95% credibility pulls average up from the two Sacra/Information sources at $4.5B

### 1.3 Google

| Metric | Value | Source | Confidence | Notes |
|--------|-------|--------|------------|-------|
| Google Cloud Q4 2025 revenue | $17.66B (+47.8% YoY) | Alphabet / TrendForce | Verified | $240B cloud backlog doubled YoY |
| Sankey provider total | $2.5B | APAC AI Intel (derived) | Estimated | Vertex AI revenue. Alphabet internal subsidy covers $0.5B loss |
| **2025 engine output (current, wq-048)** | **$2.25B** | `scripts/derive_collected_revenue.py` | Estimated | Hand-curated $2.00B was the customer-revenue node value. Engine §2 method on Google profile (segments 20/50/0/30, NRR 1.20, unknown ARR method 0.93) produces $2.25B from 2025 ARR=$4.2B with no startingARR (fallback to ending_x_0.60). Within ±15% confidence band of hand-curated. |
| Dashboard tokens/day | 90T | Editorial estimate | — | |
| Dashboard ARR | $4.2B | Editorial estimate | — | |

### 1.4 Other Providers

| Provider | Dashboard ARR | Tokens/Day | Source | Notes |
|----------|--------------|------------|--------|-------|
| Meta | $0 | 80T | Editorial | Open model, no direct revenue |
| DeepSeek | $0.3B | 40T | Press reports | |
| Mistral | $0.4B | 15T | Press reports | |
| xAI | $0.5B | 10T | Press reports | |
| Minimax | $0.15B | 30T | Press reports | |
| Moonshot | $0.1B | 8T | Press reports | |
| Others | $1.25B | 134T | Aggregated | |

### 1.5 Traditional SaaS AI Revenue

| Company | Metric | Value | Source | Notes |
|---------|--------|-------|--------|-------|
| Microsoft Copilot | Q2 FY2026 ARR | $13B (full AI business) | Microsoft / Tech-Insider | 15M paid seats = 3.3% of 450M commercial M365 base |
| Salesforce Agentforce | Q4 FY2026 ARR | $800M standalone | Salesforce earnings (official) | Combined AI + Data 360: $2.9B. ~50% deals free |
| ServiceNow Now Assist | Q4 2025 ACV | $600M+ | ServiceNow earnings (official) | Doubled YoY. AI = ~4% of total sub base |
| GitHub Copilot | Subscribers | 4.7M | MSFT earnings | |
| Total Traditional SaaS AI | 2025 actual | $2.8B | APAC AI Intel (deep analysis) | User insisted on keeping this figure despite Zitron skepticism — Zitron had no new data on SaaS specifically |

---

## 2. ARR-to-Revenue Conversion Framework

> **Implementation status (as of 2026-05-02 / wq-048):** This section is now the
> methodology reference; the canonical implementation is
> [`scripts/derive_collected_revenue.py`](scripts/derive_collected_revenue.py).
> Lookup tables are codified in [`data/consensus_config.json`](data/consensus_config.json).
> Editorial overrides live in [`data/consensus_overrides.json`](data/consensus_overrides.json).
> The post-write hook in `apply_decisions.py` re-runs the engine when an
> accepted Q4 ARR claim updates an entity-year (per §5 edge case).
> `release-check.mjs` enforces every `collected_revenue` value has traceable
> provenance (origin ∈ {consensus_engine_derived, editorial_override, accepted,
> editorial_reconciliation}). Two methodology decisions made during wq-048
> Phase A: NRR uses §2.5 formula `nrrBoost = 1.0 + (NRR - 1.0) × 0.25`;
> ARR_METHOD.factor is applied to the growth-method output, not to endingARR
> before growth math.

### 2.1 Segment Collection Factors (SEGMENT_FACTORS)

| Segment | Factor | Billing Logic | Rationale |
|---------|--------|---------------|-----------|
| API / Usage | 1.00 | Collected as consumed | No lag between billing and collection |
| Consumer Subs | 0.95 | Monthly billing | ~5-8% monthly churn |
| SME | 0.90 | Monthly/annual mix | Moderate churn |
| Enterprise | 0.80 | Annual contracts | Long sales cycles, ramp periods |

**Formula:** `adjusted_revenue = base_revenue x SUM(segment_share x segment_factor)`

### 2.2 Company Profiles (COMPANY_PROFILES)

| Company | API % | Consumer % | SME % | Enterprise % | NRR | Notes |
|---------|-------|-----------|-------|-------------|-----|-------|
| Anthropic | 70% | 15% | — | 15% | 1.50 | Sacra: 70-75% API, 10-15% subs. 300K+ biz customers |
| OpenAI | 15% | 40% | 20% | 25% | 1.30 | ChatGPT Plus dominates consumer. Enterprise via Azure |
| Google | 20% | 50% | — | 30% | 1.20 | Gemini consumer + Vertex enterprise. Bundled with Workspace |
| Generic | 40% | 20% | 20% | 20% | 1.15 | Default when company not specified |

### 2.3 ARR Reporting Method Haircuts (ARR_METHODS)

| Method | Factor | Description |
|--------|--------|-------------|
| Monthly x 12 | 1.00 | Calendar month revenue x 12. Standard, most reliable |
| Quarterly x 4 | 0.98 | Calendar quarter x 4. Slight smoothing benefit |
| Best period x 12 | 0.88 | Cherry-picked best 4-week period x 12. Inflates 10-15%. **Confirmed by Zitron for OpenAI** |
| Unknown method | 0.93 | Company hasn't disclosed method. Moderate haircut |

### 2.4 Growth Calculation Methods

| Scenario | Method | Formula |
|----------|--------|---------|
| Quarterly data available (4 snapshots) | Quarterly interpolation | `SUM(qARR x 0.25)` |
| Hyper-growth (ratio > 1.5x) | Logarithmic mean | `(endingARR - startingARR) / ln(endingARR / startingARR)` |
| Moderate growth (ratio <= 1.5x) | Simple average | `(startingARR + endingARR) / 2` |
| Only ending ARR known | 60% haircut | `endingARR x 0.60` |

### 2.5 NRR Boost

**Formula:** `nrrBoost = 1.0 + (profile.nrr - 1.0) x 0.25` (when NRR > 1.0)

This applies a quarter of the excess NRR as an upward adjustment. E.g., Anthropic NRR 1.50 yields nrrBoost = 1.125.

### 2.6 Final Conversion Pipeline

```
Step 0: adjustedEndingARR = endingARR x ARR_METHOD.factor
Step 1: baseRevenue = growth-adjusted calculation (log-mean, simple-avg, or 60% haircut)
Step 2: segmentAdjusted = baseRevenue x blendedSegmentFactor
Step 3: finalEstimate = segmentAdjusted x nrrBoost
Step 4: confidenceBand = finalEstimate x [0.85, 1.15]
```

---

## 3. Source Credibility Scoring

### 3.1 Source Type Weights (SOURCE_WEIGHTS)

| Source Type | Weight | Examples |
|------------|--------|----------|
| SEC Filing | 0.95 | IPO prospectus, 10-K, 10-Q |
| Sworn Affidavit | 0.95 | Court filings under oath |
| Earnings Aggregation | 0.85 | Earnings calls, investor presentations |
| Leaked Internal | 0.80 | Verified internal documents (e.g., Zitron's Microsoft docs) |
| Platform Data | 0.80 | Direct platform stats (OpenRouter, PyPI) |
| Official | 0.75 | Company press releases (not under oath) |
| Reporting | 0.70 | Tier 1 journalism (The Information, Bloomberg) |
| Calculation | 0.55 | APAC AI Intel derived calculations |
| Estimate | 0.45 | Analyst estimates |
| Observation | 0.45 | General observations |
| Scraper | 0.30 | Auto-scraped, unverified |

### 3.2 Confidence Modifiers (CONFIDENCE_MODIFIERS)

| Confidence Level | Modifier |
|-----------------|----------|
| Verified | 1.0 |
| Estimated | 0.8 |
| Speculative | 0.5 |
| Unverified | 0.3 |

### 3.3 Effective Weight Calculation

```
effectiveWeight = SOURCE_WEIGHTS[sourceType] x CONFIDENCE_MODIFIERS[confidence]
```

User can override with `sourceWeightOverride`.

**Credibility Classes:**
- High: weight >= 0.65
- Medium: weight >= 0.35
- Low: weight < 0.35

### 3.4 Example Credibility Scores

| Data Point | Source Type | Confidence | Score | Rating |
|-----------|-----------|-----------|-------|--------|
| Anthropic $5B cumulative (court filing) | sworn-affidavit | verified | 95% | High |
| Zitron's MSFT docs | leaked-internal | verified | 80% | High |
| The Information reporting | reporting | estimated | 56% | Medium |
| Sacra estimates | reporting | estimated | 56% | Medium |
| APAC AI Intel calculations | calculation | estimated | 44% | Medium |
| Speculative estimates | estimate | speculative | 23% | Low |

---

## 4. Sankey Flow Assumptions ("Follow the Dollar")

### 4.1 Top-Level Totals (Final Version in site-data.json)

| Category | Value | Notes |
|----------|-------|-------|
| **Total System** | **$27.27B** | Customer revenue + VC subsidy |
| Total Customer Revenue | $17.47B | What customers actually paid |
| Total VC Subsidy | $9.80B | Operating losses funded by investors |

### 4.2 Column 1: Who Pays (Buyers)

| Buyer | Value | Notes |
|-------|-------|-------|
| Consumer | $5.16B | ChatGPT Plus, Claude Pro, Gemini, etc. |
| SME | $3.37B | Small/medium business subscriptions and API |
| Enterprise | $8.94B | Enterprise contracts, SaaS AI SKUs |
| VC/Investors | $9.80B | Funds operating losses at providers |

### 4.3 Column 2: Channels

| Channel | Value | Notes |
|---------|-------|-------|
| Model Subs | $5.31B | Direct subscription products |
| Model API | $3.40B | Direct API usage |
| Hyperscalers | $2.15B | AWS Bedrock, Azure OpenAI, Google Vertex |
| AI Native Apps | $3.36B | Cursor, Perplexity, etc. |
| IaaS & Aggregators | $0.30B | Together, Fireworks, OpenRouter |
| Traditional SaaS | $2.94B | Microsoft Copilot, Salesforce, ServiceNow |

### 4.4 Column 3: Providers

| Provider | Total Inflow | Customer Revenue | VC Subsidy | Notes |
|----------|-------------|-----------------|-----------|-------|
| OpenAI | $13.65B | $7.65B | $6.00B | Consensus from Zitron + The Information |
| Anthropic | $7.71B | $4.71B | $3.00B | Consensus weighted $4.71B + Sacra $3B burn |
| IaaS | $0.80B | $0.50B | $0.30B | Together/Fireworks/Groq |
| Google | $2.50B | $2.00B | $0.50B | Alphabet internal subsidy |

### 4.5 Column 4: Where It Goes (Outcomes)

| Outcome | Value | Notes |
|---------|-------|-------|
| Inference | $14.03B | GPU compute for serving tokens |
| People/SG&A | $11.08B | R&D teams, sales, marketing |
| Margin | $2.15B | Only Trad SaaS ($1.75B) + Hyperscaler pass-through ($0.40B) — frontier providers have zero margin |

### 4.6 Provider-to-Outcome Flow Splits

| Provider | Inference | People/SG&A | Notes |
|----------|----------|-------------|-------|
| OpenAI | $8.19B (60%) | $5.46B (40%) | Inference includes $5B H1 2025 alone (Zitron) |
| Anthropic | $4.24B (55%) | $3.47B (45%) | |
| IaaS | $0.40B (50%) | $0.40B (50%) | |
| Google | $1.20B (48%) | $1.30B (52%) | |

### 4.7 Flow Rebalancing Algorithm

The Sankey requires exact balance: inflows = outflows at every node. When consensus values changed individual provider totals, the system used proportional rescaling:

1. Update provider totals from consensus engine
2. Proportionally rescale all inflows (channel-to-provider flows) to match new provider total
3. Proportionally rescale all outflows (provider-to-outcome flows) to match new provider total
4. Verify: Buyer totals = Channel totals = Provider totals = Outcome totals

### 4.8 Key Sankey Narrative Points

- **$15:$1 ratio** — for every $1 customers spend on AI, investors spend $15+ building it ($15.6B customer rev vs $250B+ total investment)
- **Zero margin for frontier providers** — all $2.15B of margin goes to Traditional SaaS vendors and hyperscaler pass-through fees
- **Inference EXCEEDS revenue for OpenAI** — $5B H1 inference cost vs $4.3B H1 revenue

### 4.9 Evolution of Sankey Totals

| Version | Customer Rev | VC Subsidy | Total System | Trigger |
|---------|-------------|-----------|-------------|---------|
| V1 (initial) | ~$19B | ~$12B | ~$48B | Original estimates, too high |
| V2 (Zitron) | $15.6B | $12B | $27.6B | Zitron cross-check massively corrected down |
| V3 (consensus) | $17.47B | $9.8B | $27.27B | Consensus engine + Sacra data reduced Anthropic VC subsidy |

---

## 5. Token Volume Estimates

### 5.1 Total Daily Token Estimate

**Final figure: ~565T tokens/day** (revised down from initial ~680T/day)

### 5.2 Triangulation Methods (4 independent)

| Method | Approach | Result | Notes |
|--------|---------|--------|-------|
| Revenue / blended pricing | Total provider revenue / weighted average price per token | — | Top-down from revenue |
| GPU capacity ceiling | ~4.5M H100-equiv x 30-50% utilization x 2500 tok/sec | ~490T/day max | SemiAnalysis GPU utilization data |
| Bottom-up user estimation | User count x sessions/day x tokens/session | — | Per-provider estimation |
| SDK download proxies | PyPI/npm downloads as adoption signal | — | openai PyPI: 224M/month, anthropic: 77M/month (Mar 2026) |

**Key revision:** Previous estimate of ~680T/day revised down to ~565T/day based on GPU utilization cross-check (30-50% utilization, not the higher figures previously assumed).

### 5.3 Per-Provider Token Estimates (site-data.json)

| Provider | T tokens/day | Notes |
|----------|-------------|-------|
| OpenAI | 200 | Revised down from 270 based on GPU utilization |
| Anthropic | 110 | |
| Google/Gemini | 90 | |
| Meta (self-hosted) | 80 | Open model |
| DeepSeek | 40 | |
| Minimax | 30 | |
| Mistral | 15 | |
| xAI | 10 | |
| Moonshot | 8 | |
| Others (self-hosted) | 134 | vLLM, Ollama, HuggingFace |

### 5.4 GPU Utilization Assumptions

- **Hyperscaler GPU utilization:** 30-50% for inference workloads (bursty demand) — SemiAnalysis
- **Estimated H100-equivalent fleet:** ~4.5M GPUs
- Many enterprise-purchased GPUs sit at much lower utilization

### 5.5 Specific Token Consumption Estimates

| Service | Est. Tokens/Day | Method |
|---------|----------------|--------|
| Cursor (coding AI) | ~1.4-1.6T | $1.4M/day spend / $0.98/M blended price |
| Salesforce Agentforce ($800M ARR) | ~5-30B | Shelfware — actual consumption far below booked |
| Klarna "700 AI agents" | ~20B | Specific case study |
| OpenRouter (Mar 2026) | 1T+ | Official — OpenRouter platform data |

---

## 6. Dashboard Data Assumptions

### 6.1 Regional Token Distribution

| Region | % | Growth | Source |
|--------|---|--------|--------|
| North America | 40% | +160% YoY | Editorial estimate |
| Asia-Pacific | 30% | +280% YoY | Editorial estimate |
| Europe | 18% | +140% YoY | Editorial estimate |
| Middle East | 5% | +350% YoY | Editorial estimate |
| Latin America | 4% | +200% YoY | Editorial estimate |
| Africa | 3% | +300% YoY | Editorial estimate |

### 6.2 Industry Distribution

| Industry | % | Source |
|----------|---|--------|
| Software & Tech | 33% | Editorial estimate |
| Financial Services | 16% | Editorial estimate |
| Healthcare | 9% | Editorial estimate |
| Retail & E-commerce | 9% | Editorial estimate |
| Marketing & Ads | 8% | Editorial estimate |
| Customer Service | 7% | Editorial estimate |
| Education | 5% | Editorial estimate |
| Manufacturing | 4% | Editorial estimate |
| Legal & Gov & Other | 9% | Editorial estimate |

### 6.3 Use Case Distribution

| Use Case | % | Source |
|----------|---|--------|
| Coding & Dev Tools | 28% | Editorial estimate |
| Chat & Assistants | 27% | Editorial estimate |
| Content & Writing | 15% | Editorial estimate |
| Enterprise Agents | 10% | Editorial estimate |
| Search & RAG | 10% | Editorial estimate |
| Data Analysis | 7% | Editorial estimate |
| Other | 5% | Editorial estimate |

### 6.4 Demand Type Splits (Revenue)

| Demand Type | Initial % | Revised % | Notes |
|-------------|----------|-----------|-------|
| Consumer Subs | 42% | 40% | |
| API / Developer | 25% | 28% | Increased — real growth signal |
| Enterprise Platform | 23% | 20% | Decreased — shelfware reality |
| Cloud Channel | 10% | 12% | |

### 6.5 Demand Weights Per Provider

| Provider | Consumer Subs | API/Dev | Enterprise Platform | Cloud Channel |
|----------|--------------|---------|-------------------|--------------|
| OpenAI | 0.55 | 0.15 | 0.15 | 0.15 |
| Anthropic | 0.20 | 0.35 | 0.25 | 0.20 |
| Google/Gemini | 0.35 | 0.20 | 0.20 | 0.25 |
| Meta (open) | 0.10 | 0.50 | 0.30 | 0.10 |
| DeepSeek | 0.40 | 0.40 | 0.10 | 0.10 |

### 6.6 Cross-Dimensional Weights (Region x Provider x Industry x UseCase)

Extensive cross-weight matrices in site-data.json map each provider to regional, industry, and use case distributions. All are **editorial estimates** — no source data. Key examples:

- Anthropic skews 50% North America, 45% Software & Tech, 45% Coding & Dev Tools
- Google skews 30% APAC, 30% Chat & Assistants
- DeepSeek skews 55% APAC, 50% Software & Tech
- Mistral skews 45% Europe

### 6.7 Enterprise Reality Check Data

| Company | Metric | Value | Source |
|---------|--------|-------|--------|
| M365 Copilot | Paid seats | 15M (3.3% of 450M base) | Microsoft Q2 FY26 earnings |
| M365 Copilot | Usage rate | 35.8% | Recon Analytics (150K respondents) |
| Enterprise AI | Past pilot stage | Only 5% | Gartner 2025 (187 respondents) |
| Enterprise AI | Tried then kept | 70% tried, 8% kept choosing | Recon Analytics |
| Salesforce Agentforce | ~50% deals free | Derived from quarterly deal counts | Calculation |
| ServiceNow Now Assist | Pro Plus premium | 30-60% | UpperEdge |
| CRM gross margin | Impact of AI COGS | Flat at 77% | Salesforce earnings |
| ServiceNow | Gross margin impact | -1.7pp | ServiceNow earnings |
| Microsoft Cloud | Gross margin impact | -3pp | Microsoft earnings |

---

## 7. Consensus Engine

### 7.1 Algorithm

```javascript
function calcConsensus(dataPoints) {
  weightedSum = SUM(dp.value x getEffectiveWeight(dp))
  totalWeight = SUM(getEffectiveWeight(dp))
  weightedAvg = weightedSum / totalWeight
  // Also returns min, max, spread, source count
}
```

Groups data points by `metricKey`. Only shows groups with 2+ sources.

### 7.2 Specific Consensus Results

**anthropic-revenue-2025:**
- Weighted consensus: **$4.71B**
- 3 sources, $0.50B spread
- Anthropic court filing: $5B at 95% credibility (sworn-affidavit x verified)
- Sacra/The Information: $4.5B at 56% credibility (reporting x estimated)
- The Information: $4.5B at 56% credibility (reporting x estimated)
- The high-credibility court filing (cumulative $5B) pulls the average above the $4.5B reported figures

**openai-revenue-2025:**
- Zitron estimate: $11.9B (leaked-internal, estimated = 64%)
- The Information H1: $4.3B (reporting, estimated = 56%)
- Consensus weighted ~$7.64B customer revenue (used in Sankey as $7.65B)

---

## 8. Zitron Methodology

### 8.1 Core Reverse-Engineering

**Step 1:** Microsoft internal docs obtained showing $454.7M revenue share paid BY Microsoft TO OpenAI in H1 2024.

**Step 2:** At confirmed 20% revenue share rate: $454.7M / 0.20 = ~$2.27B OpenAI H1 2024 revenue

**Step 3:** Separate leaked doc showing $493.8M / 0.20 = ~$2.5B (different period/calculation, net adjustments push total higher to ~$3.6B for full year 2024)

**Step 4:** H1 2025 inference spend: $5.022B (from Microsoft docs) — exceeds $4.3B H1 2025 revenue

### 8.2 Key Zitron Data Points Used

- OpenAI 2024 actual collected: ~$3.6B (vs. publicly claimed $4B+ ARR)
- OpenAI H1 2025 actual collected: ~$4.3B (The Information)
- OpenAI H1 2025 inference spend: $5.022B (exceeds revenue)
- Full 2024-Sep2025 cumulative inference: $12.4B
- OpenAI SBC: ~$6B/yr ($1.5M per employee average) = 46% of revenue
- OpenAI revenue share to Microsoft: 20% of all revenue (~$2.6B/yr)
- By 2026, two-thirds of all AI compute is inference, heading to 70-80% by 2028
- **$25B ARR uses best 4-week period x 12** — confirmed methodology

---

## 9. Hardcoded Percentages and Ratios

### 9.1 Subsidy Clock (subsidy-clock.html)

| Parameter | Value | Source |
|-----------|-------|--------|
| VC Subsidy | $9.8B | From Sankey |
| Capex | $250B | Industry reports + Meta guidance |
| Customer Revenue | $17.47B | From Sankey |
| Inference Cost | $14.03B | From Sankey |
| People/SG&A | $11.08B | From Sankey |
| Margin | $2.15B | From Sankey |
| Total System | $27.27B | From Sankey |
| Annual Investment (capex + VC subsidy) | ~$260B | Ticks the clock |

### 9.2 Inference Cost Ratios by Provider

| Provider | Inference % of Spend | Notes |
|----------|---------------------|-------|
| OpenAI | 60% | $8.19B of $13.65B |
| Anthropic | 55% | $4.24B of $7.71B |
| IaaS | 50% | $0.40B of $0.80B |
| Google | 48% | $1.20B of $2.50B |

### 9.3 Sustainability Path Calculations

| Path | Metric | Value | Source |
|------|--------|-------|--------|
| Inference cost reduction needed | For 30% gross margin | -35% (from $13B to $8.4B) | Calculation |
| Price increase needed | For 30% gross margin | +55% | Calculation |
| Open model workload shift needed | For system breakeven | 20-30% of closed-model workloads | Calculation |
| Token price deflation (actual) | Year-on-year | -80% | Observable from public API pricing |
| Open models cheaper factor | vs frontier | 5-10x cheaper per token | Observation |
| Open models capability gap | vs frontier | ~3 months trailing | Observation |

### 9.4 Hyperscaler/SaaS Margins

| Entity | Margin | Notes |
|--------|--------|-------|
| Hyperscaler cloud pass-through | ~20% | On AI model serving. $0.4B of $2B channel flows |
| Traditional SaaS vendors | ~62% | $1.75B margin on $2.8B revenue |
| IaaS/open model gross margin | 15-35% | Thin positive GM, zero operating margin |
| Frontier model providers | Negative | All lose money on inference |

### 9.5 Investment Ratios

| Metric | Value | Notes |
|--------|-------|-------|
| Investment-to-revenue ratio | $15:$1 | $250B+ investment vs $15.6B customer revenue |
| VC subsidy as % of total system | 36% | $9.8B / $27.27B |
| Inference as % of total system | 51% | $14.03B / $27.27B |

### 9.6 Data Center Economics

| Metric | Value | Source |
|--------|-------|--------|
| DC cost per GW | $50B all-in | Chamath (first-hand, building 1GW DC in Arizona) |
| Revenue per GW | $10B/year | Sarah Friar (Anthropic CFO) |
| DC payback period | 5 years (profit in years 6-8) | Chamath (first-hand) |
| DC protest cancellation rate | 40% (~7GW at risk) | Chamath (speculative) |
| At-risk revenue (from protests) | $70B/year | 7GW x $10B/GW |

---

## 10. Key Vault Data Points Summary

Total data points in vault-data.json: 87+ (dp-001 through dp-087+)
Total inbox items in vault-inbox.json: 30+ items (accepted, declined, or parked)

### 10.1 Highest Confidence Data Points (verified + high-weight source)

| ID | Claim | Value | Credibility |
|----|-------|-------|-------------|
| dp-001 | Anthropic cumulative revenue $5B (sworn affidavit) | $5B | 95% |
| dp-011 | Microsoft H1 2024 rev share to OpenAI: $454.7M | $454.7M | 80% |
| dp-029 | OpenAI ended 2025 at $20B ARR | $20B ARR | 70% |
| dp-026 | Anthropic $14B ARR Feb 2026 | $14B ARR | 70% |
| dp-027 | Anthropic $6B revenue month Feb 2026 | $6B/month | 70% |
| dp-047 | OpenAI H1 2025 inference spend $5.0B | $5.0B | 80% |
| dp-064 | OpenAI $25B ARR uses best 4-week period x 12 | $25B ARR | 80% |

### 10.2 Lowest Confidence but Influential

| ID | Claim | Value | Credibility | Impact |
|----|-------|-------|-------------|--------|
| dp-004 | OpenAI 2025 collected ~$6B | $6B | 44% | Was key Sankey input before Zitron data |
| dp-006 | Anthropic operating loss ~$5.2B | $5.2B | 44% | Revised down to $3B after Sacra data |
| dp-007 | Total AI customer revenue $15.6B | $15.6B | 44% | Foundation of entire Sankey |
| dp-008 | VC operating subsidy ~$12B | $12B | 44% | Later revised to $9.8B |

### 10.3 Parked Data Points (Conflicts Unresolved)

| ID | Claim | Value | Why Parked |
|----|-------|-------|-----------|
| Anthropic $3B cash burn 2025 | $3B | Conflicts with $5.2B operating loss — may be different accounting |
| OpenAI $11.9B 2025 collected (Zitron) | $11.9B | Below Altman's claim, conflicts with The Information $13.1B |

---

## 11. Caveats and Meta-Assumptions

1. **ARR is NOT revenue.** The entire platform is built around this distinction. ARR figures are systematically converted through the framework in Section 2 before being used.

2. **"Actual collected revenue" is the gold standard** throughout the Sankey and financial analysis. This is money that actually changed hands, not run-rate projections.

3. **The VC subsidy represents only operating losses** — it does NOT include training capex or GPU procurement capital. The $250B capex figure is tracked separately in the subsidy clock.

4. **All regional, industry, and use-case splits are editorial estimates** with no sourced data. They provide directional views only.

5. **The 44% credibility of derived calculations** means the entire Sankey model rests on medium-confidence figures. The transcript explicitly acknowledges this: "the core numbers driving the Sankey are all 44% credibility calculations."

6. **Token volume estimates are order-of-magnitude** — the 565T/day figure was revised down from 680T/day after GPU utilization cross-check, but remains approximate.

7. **Enterprise AI consumption is dramatically lower than marketed** — this is a core editorial thesis supported by user's ServiceNow experience and multiple data points showing 3-5% actual usage rates.

8. **The system was built iteratively** — numbers changed significantly through the conversation. The Sankey total system dropped from ~$48B to $27.6B to $27.27B as skeptical sources (Zitron, court filings) were incorporated.

9. **OpenAI's ARR methodology (best-4-week x 12)** means all OpenAI ARR figures should be treated as 10-15% inflated relative to standard monthly x 12 methodology.

10. **Cash burn vs. operating loss** can differ significantly (Anthropic: $3B cash burn vs. $5.2B operating loss for 2025). The Sankey uses operating loss for the VC subsidy calculation.
