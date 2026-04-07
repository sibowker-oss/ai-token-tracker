# Revenue Projection Methodology

**Created:** 2026-04-07
**Status:** Documented logic for deriving forward revenue projections from ARR data
**Used in:** Sankey Forward Look, Timeline Forward, Revenue Projection Review

---

## 1. Overview

We project future collected revenue (actual cash received) from three inputs per provider:
1. **Exit ARR** — the most recent authoritative annualised run-rate
2. **Growth rate** — company-specific, observed or guided
3. **Market share trajectory** — whether share is growing, stable, or declining

Revenue is NOT the same as ARR. ARR is a snapshot of the current run-rate; revenue is what actually gets collected over a period. The conversion from ARR to collected revenue accounts for growth trajectories, reporting methodology biases, and the reality that different buyer segments pay at different rates.

---

## 2. Step-by-Step Conversion

### Step 0: ARR Method Haircut

Not all ARR figures are calculated the same way. Apply a haircut based on known methodology:

| Reporting method | Factor | Description |
|---|---|---|
| Monthly x 12 | 1.00 | Calendar month revenue x 12. Most reliable |
| Quarterly x 4 | 0.98 | Slight smoothing benefit |
| Best 4-week x 12 | 0.88 | Cherry-picks the best period. Inflates 10-15%. **Confirmed for OpenAI by Zitron** |
| Unknown method | 0.93 | Moderate haircut when method not disclosed |

**Example:** OpenAI $25B ARR x 0.88 = $22.0B adjusted ARR

### Step 1: Growth-Adjusted Revenue Calculation

The starting ARR is NOT the full year's revenue — the company is growing throughout the year. We need to calculate the average revenue rate across the year.

| Growth scenario | Ratio (end/start) | Method | Formula |
|---|---|---|---|
| Hyper-growth | >1.5x | Logarithmic mean | `(endARR - startARR) / ln(endARR / startARR)` |
| Moderate growth | 1.0x - 1.5x | Simple average | `(startARR + endARR) / 2` |
| Only ending ARR known | — | 60% haircut | `endARR x 0.60` |

**Why log-mean for hyper-growth?** Simple average overestimates when growth is exponential. A company that starts at $10B and ends at $40B doesn't average $25B — the log-mean gives $19.5B, reflecting that most of the year was spent at lower run-rates.

**Example:** OpenAI 2026: start $22B, end $38B (1.7x = hyper-growth)
`(38 - 22) / ln(38/22) = 16 / 0.547 = $29.3B` pre-collection revenue

### Step 2: Buyer Segment Collection Factors

Not all ARR converts to cash equally. **Buyer segments** (who pays) determine collection rates — not channels (how they access).

| Buyer segment | Collection factor | Why |
|---|---|---|
| **Consumer** | 0.95 | Monthly subscription billing. ~5% monthly churn |
| **SME** | 0.90 | Small/medium businesses, AI-native apps, startups buying via API. Moderate churn, some failed payments |
| **Enterprise** | 0.80 | Large contracts. Long sales cycles (3-6 months), ramp periods, POCs that don't convert, delayed procurement |

**Important:** API is a **channel**, not a buyer segment. Most API revenue comes from SMEs (AI-native startups building products). Enterprise API usage is growing but is still the minority of API volume.

### Step 3: Blended Collection Factor

Each provider has a different buyer mix. The blended collection factor is:

`blended = (consumer_pct x 0.95) + (sme_pct x 0.90) + (enterprise_pct x 0.80)`

| Provider | Consumer % | SME % | Enterprise % | Blended | Rationale |
|---|---|---|---|---|---|
| OpenAI | 55% | 25% | 20% | 0.91 | 900M WAU, 50M paid subs drive consumer. Enterprise >40% of rev but consumer still majority of volume |
| Anthropic | 15% | 45% | 40% | 0.87 | 70-75% of revenue via API, but API buyers are mostly SME/AI-native (45%) and enterprise (40%). Small consumer base |
| Google | 50% | 20% | 30% | 0.90 | Large Gemini consumer app. Vertex serves enterprise. Workspace bundles complicate |
| Others (default) | 30% | 40% | 30% | 0.89 | Default profile for providers without detailed mix data |

### Step 4: Final Collected Revenue

`collected_revenue = growth_adjusted_revenue x blended_collection_factor`

**Example:** OpenAI 2026: $29.3B x 0.91 = **$26.7B collected**

### Step 5 (Optional): NRR Boost

If net revenue retention >100% (existing customers spending more), apply a small uplift:

`nrr_boost = 1.0 + (nrr - 1.0) x 0.25`

Only applied when NRR is known and >1.10. Currently only Anthropic has disclosed NRR (1.50), giving boost of 1.125. **Not currently applied in projections** — the growth rate already captures expansion.

---

## 3. Projecting End-of-Year ARR

To use the log-mean method, we need both start and end ARR for each year. End-of-year ARR is estimated from:

### Priority 1: Company guidance
- OpenAI: $50B ARR target by 2027 (press release)
- This anchors the end-2027 ARR directly

### Priority 2: Observed growth rate with deceleration
- Take the most recent growth rate (e.g., Anthropic: 14x in 14 months)
- Apply deceleration: growth rates slow as companies scale
- Rule of thumb: hyper-growth companies decelerate ~30-50% per year on the rate itself

**Example:** Anthropic
- Recent: 14x in 14 months (Dec 2024 $1B → Mar 2026 $19B)
- Implied annual rate: ~10x
- With 50% deceleration: ~5x in the next 12 months
- End 2026: $19B x (5x ^ (9/12)) = ~$35B ARR (9 months remaining in 2026)
- End 2027: $35B x (2.5x ^ 1) = ~$55B (further deceleration to 2.5x)

### Priority 3: Market share x market growth
- If the total market grows at G% and the provider's share trend is known:
- `end_ARR = start_ARR x (1 + G%) x share_adjustment`
- Used for providers without direct guidance (DeepSeek, Mistral, etc.)

---

## 4. Revenue by Buyer Segment (Sankey "Who Pays")

Once total collected revenue per provider is calculated, split by buyer segment using each provider's mix:

| Buyer | 2025 | 2026E | 2027E | Trend |
|---|---|---|---|---|
| Consumer | ~29% | ~25% | ~22% | Shrinking % as enterprise grows |
| SME | ~19% | ~22% | ~23% | Growing — AI-native apps scaling |
| Enterprise | ~50% | ~52% | ~53% | Growing — OpenAI enterprise >40% and targeting parity by EOY 2026 |

**Key insight:** Enterprise grows in share but has the lowest collection factor (0.80). This means the industry's aggregate collection factor slightly declines as enterprise grows — ARR growth overstates actual cash growth.

---

## 5. Revenue by Channel (Sankey "How They Buy")

Channels describe how buyers access AI, not who they are:

| Channel | What flows through it | 2025 | Growth driver |
|---|---|---|---|
| Model Subs | Consumer subscriptions (ChatGPT Plus, Claude Pro, Gemini) | $5.3B | User growth |
| Model API (direct) | Direct API from model providers (OpenAI, Anthropic) | $3.4B | Developer/SME adoption |
| Hyperscalers | Azure OpenAI, AWS Bedrock, GCP Vertex | $2.2B | Enterprise procurement preference |
| AI Native Apps | Cursor, Perplexity, etc. — they buy API and resell as product | $3.4B | New app category |
| IaaS & Open Model API | Together, Fireworks, Groq, OpenRouter — serve open models | $0.3B | Open model adoption (61% of OpenRouter) |
| Traditional SaaS | Microsoft Copilot, Salesforce Agentforce, ServiceNow | $2.9B | Enterprise seat expansion |

**The IaaS channel is where Chinese/open model revenue flows.** DeepSeek, Qwen, Llama, Mistral are served to customers via IaaS providers. As open models grow, this channel grows disproportionately.

---

## 6. Operating Outcomes (Sankey "Where It Goes")

Total system cost = customer revenue + VC subsidy. This splits into:

| Outcome | What it covers | 2025 share | Trend |
|---|---|---|---|
| Inference | GPU compute cost of serving tokens | 51% | Shrinking % — efficiency gains, token price deflation |
| People/SGA | Engineers, researchers, sales, marketing, ops | 41% | Shrinking % — operating leverage at scale |
| Operating Cash Flow | Revenue minus operating costs (pre-capex depreciation) | 8% | Growing — path to sustainability |

**Operating Cash Flow ≠ Profit.** It does not account for the $250B+ in capex being depreciated over 5-6 years. True profitability requires cash flow to exceed annual capex depreciation — which is not projected within this model's timeframe.

**VC Subsidy** is the plug: `VC_subsidy = total_operating_cost - customer_revenue`. It represents investor-funded losses. As operating cash flow grows, the subsidy shrinks as a percentage of the system.

---

## 7. Key Decisions Made During Review (Apr 7 2026)

### Microsoft split
- Microsoft reports $13B "AI business" ARR — but this includes both Azure OpenAI (~$7-8B) and Copilot M365 (~$5B)
- **Azure OpenAI** sits in the Hyperscaler channel → flows to OpenAI as provider revenue. NOT counted in Enterprise SaaS.
- **Copilot M365** sits in Enterprise SaaS at ~$5B ARR
- Standard enterprise collection factor (0.80) applies to Copilot. **Shelfware/low usage does NOT reduce collection** — enterprises pay their invoices regardless of user adoption. Low usage affects **future growth/renewal rates**, not current cash collection.

### Google three roles
- **Model Provider** (Gemini): consumer app + direct API. ~$6B starting ARR. Sits in Provider column.
- **Hyperscaler** (GCP Vertex): resells Anthropic, Llama, Mistral etc. Sits in Hyperscaler channel. Separate flow.
- **Search AI** (AI Overviews): ad-monetised. Not counted as direct AI revenue — different business model.
- Google AI-specific revenue growing faster than Cloud total (48% YoY) — estimated 80% YoY for AI specifically.

### API is a channel, not a buyer segment
- Buyer segments are: **Consumer** (0.95), **SME** (0.90), **Enterprise** (0.80)
- API is HOW SMEs and enterprises buy — most API revenue comes from SMEs/AI-native apps
- Anthropic's 70-75% API mix means heavy SME/enterprise buyer base (45% SME, 40% enterprise), NOT high collection

### IaaS channel growth
- Chinese open models (DeepSeek, Qwen, Mistral) flow through IaaS providers (Together, Fireworks, Groq, OpenRouter)
- ByteDance excluded from revenue Sankey — massive token volume (110T/day) but zero external revenue (all internal to Douyin/TikTok)
- IaaS channel grows from $0.3B (2025) to $2B (2026E) to $6B (2027E) as open model adoption accelerates

### Balanced flows
- Sankey must balance: Buyers = Channels = Providers = Outcomes at each year
- VC subsidy is the plug: `VC_subsidy = total_operating_cost - customer_revenue`
- Operating Cash Flow (not "Margin") is pre-capex depreciation — does not imply profitability

---

## 8. What This Model Does NOT Cover

- **Capex** — GPU purchases, data centre construction. Tracked on Compute Stack page, not in the revenue flow
- **Training costs** — $30-50B/year. Separate from inference (operating) costs
- **Chinese provider revenue** — Almost entirely editorial estimates. Token volume is known (ByteDance 120T/day) but revenue is not
- **Self-hosted inference** — 20-40T tokens/day with zero revenue attribution
- **Token volume projections** — Handled separately in the timeline forward model using growth rates from the multi-model survey

---

## 8. How to Update This Model

When new data arrives:

1. **New ARR figure** → Update the provider's start/end ARR in the projection tables
2. **New growth rate** → Recalculate end-of-year ARR using the deceleration formula
3. **New buyer mix data** → Update the collection factor calculation
4. **New market share data** → Adjust relative growth rates between providers
5. **New collection factor data** → If actual collected revenue is disclosed, validate the factor

All changes should be logged in the revision log of model-assumptions.md (Section 15).
