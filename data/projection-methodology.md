# Revenue Projection & Sankey Flow Methodology

**Created:** 2026-04-07
**Last updated:** 2026-04-07
**Status:** Final logic for the Sankey "Follow the Dollar" (live + v2 forward projections)

---

## 1. Overview

We project future collected revenue (actual cash received) from three inputs per provider:
1. **Exit ARR** — the most recent authoritative annualised run-rate
2. **Growth rate** — company-specific, observed or guided
3. **Market share trajectory** — whether share is growing, stable, or declining

Revenue is NOT the same as ARR. ARR is a snapshot of the current run-rate; revenue is what actually gets collected over a period.

---

## 2. ARR → Collected Revenue Conversion

### Step 0: ARR Method Haircut

| Reporting method | Factor | Description |
|---|---|---|
| Monthly x 12 | 1.00 | Standard, most reliable |
| Quarterly x 4 | 0.98 | Slight smoothing |
| Best 4-week x 12 | 0.88 | Cherry-picks best period. **Confirmed for OpenAI by Zitron** |
| Unknown method | 0.93 | Default when method not disclosed |

### Step 1: Growth-Adjusted Revenue

| Growth scenario | Ratio (end/start) | Method | Formula |
|---|---|---|---|
| Hyper-growth | >1.5x | Log-mean | `(endARR - startARR) / ln(endARR / startARR)` |
| Moderate growth | 1.0x-1.5x | Simple average | `(startARR + endARR) / 2` |
| Only ending ARR known | — | 60% haircut | `endARR x 0.60` |

### Step 2: Buyer Segment Collection Factors

**Buyer segments (who pays), NOT channels (how they buy). API is a channel, not a segment.**

| Buyer segment | Collection factor | Why |
|---|---|---|
| **Consumer** | 0.95 | Monthly subscription, ~5% churn |
| **SME** | 0.90 | AI-native apps, startups buying API. Moderate churn |
| **Enterprise** | 0.80 | Long sales cycles, ramp periods, delayed procurement |

### Step 3: Blended Collection Factor per Provider

| Provider | Consumer % | SME % | Enterprise % | Blended |
|---|---|---|---|---|
| OpenAI | 55% | 25% | 20% | 0.91 |
| Anthropic | 15% | 45% | 40% | 0.87 |
| Google (Gemini) | 60% | 20% | 20% | 0.91 |
| Others (default) | 30% | 40% | 30% | 0.89 |

### Step 4: Final Collected Revenue

`collected_revenue = growth_adjusted_revenue x blended_collection_factor`

---

## 3. Projecting End-of-Year ARR

### Priority 1: Company guidance
- OpenAI: $50B ARR target by 2027

### Priority 2: Observed growth with deceleration
- Take most recent growth rate, apply ~30-50% annual deceleration on the rate itself
- Example: Anthropic 10x annual → 5x next year → 2.5x the year after

### Priority 3: Market share x market growth
- Used for providers without guidance (DeepSeek, Mistral, etc.)

---

## 4. Sankey Flow Rules

The Sankey has 4 columns: **Who Pays → Channels → Providers → Where It Goes**

### Rule 1: Column balancing

| Column | Must sum to |
|---|---|
| Buyers | Total System (= Customer Revenue + VC Subsidy) |
| Channels | Customer Revenue only (VC bypasses channels) |
| Providers | Channel pass-through + VC (NOT total system — margin stays in channels) |
| Outcomes | Total System (= Providers + Operating Cash from channels) |

### Rule 2: VC Subsidy bypasses Channels

VC/Investors flows **directly from Buyers (col 1) to Providers (col 3)**, skipping Channels entirely. VC money doesn't go through a sales channel — it funds operating losses directly.

### Rule 3: Channel margins bypass Providers

Hyperscalers and Traditional SaaS have inherent margins that flow **directly from Channels (col 2) to Operating Cash (col 4)**, skipping Providers. These businesses resell AI at a markup — not every dollar they receive gets passed to model providers.

| Channel | Margin % | Pass-through to Providers | Direct to Operating Cash |
|---|---|---|---|
| Hyperscalers | 20% | 80% of channel value | 20% of channel value |
| Trad. SaaS | 60% | 40% of channel value | 60% of channel value |
| All others | 0% | 100% of channel value | $0 |

### Rule 4: Providers receiving VC cannot generate Operating Cash

If a provider receives VC subsidy, ALL their inflow goes to Inference + People/SGA. They are loss-making by definition — the VC subsidy exists precisely because their costs exceed their revenue. No provider flow goes to Operating Cash.

**Operating Cash comes ONLY from channel margins** (Hyperscalers + Trad SaaS).

### Rule 5: Provider total = Channel pass-through + VC

Providers receive money from two sources:
1. Channel pass-through (channel revenue minus channel margins)
2. VC subsidy (direct from Buyers)

`Provider total = SUM(channel_value x (1 - margin%)) + VC_subsidy`

Providers then spend ALL of this on Inference + People/SGA:
`Inference + People/SGA = Provider total` (nothing left over)

### Rule 6: Operating Cash calculation

`Operating Cash = SUM(channel_value x margin%)` for margin channels only

This is pre-capex depreciation. It does NOT imply profitability. The $250B+ in annual capex is depreciated over 5-6 years and sits on balance sheets, not in this operating flow.

---

## 5. Sankey Column Definitions

### Column 1: Who Pays (Buyers)

| Buyer | Description |
|---|---|
| Consumer | Individual subscribers (ChatGPT Plus, Claude Pro, Gemini) |
| SME | Small/medium businesses, AI-native apps, startups |
| Enterprise | Large enterprise contracts |
| VC/Investors | Investor-funded operating losses. Bypasses channels. |

### Column 2: Channels

| Channel | What flows through it | Margin |
|---|---|---|
| Model Subs | Consumer subscriptions direct to providers | 0% — all goes to provider |
| Model API | Direct API from any model provider (OpenAI, Anthropic, DeepSeek, Mistral) | 0% |
| Hyperscalers | Azure OpenAI, AWS Bedrock, GCP Vertex — reselling models | **20% margin** |
| AI Native Apps | Cursor, Perplexity etc. — buy API, resell as product | 0% (pass-through to providers) |
| IaaS & Agg. | Together, Fireworks, Groq, OpenRouter — host open models | 0% |
| Trad. SaaS | Copilot M365, Agentforce, Now Assist — AI features in SaaS | **60% margin** |

**Key distinctions:**
- Hyperscalers resell other providers' models with a ~20% margin
- Trad. SaaS builds AI features on top of models — ~60% of their AI revenue is retained as margin (existing infrastructure, sales force, brand)
- API is a channel, not a buyer segment

### Column 3: Providers

| Provider | Description |
|---|---|
| OpenAI | Direct model revenue + pass-through from hyperscalers/SaaS |
| Anthropic | Same |
| Google (Gemini) | Gemini model revenue only. GCP Vertex hyperscaler role is in Channels. |
| IaaS/Open | Together, Fireworks, Groq — host open-weight models (Llama, Qwen) |
| Other Model Providers | DeepSeek, Mistral, xAI etc. — sell tokens via their own API |

**Microsoft split:**
- **Azure OpenAI** (~$7-8B) sits in the Hyperscaler channel → flows to OpenAI as provider
- **Copilot M365** (~$5B) sits in Trad. SaaS channel
- These are NOT double-counted

**Google split:**
- **Google (Gemini)** in Providers = their own model revenue (consumer app + direct API)
- **GCP Vertex** in Channels = hyperscaler reselling of Anthropic/Llama/Mistral
- **Search AI Overviews** = ad-monetised, not counted as direct AI revenue

### Column 4: Where It Goes (Outcomes)

| Outcome | Receives from | Description |
|---|---|---|
| Inference | Providers | GPU compute cost of serving tokens |
| People/SG&A | Providers | Engineers, researchers, sales, ops |
| Operating Cash | Channels (margin bypass) | Hyperscaler + Trad SaaS margins. Pre-capex. |

---

## 6. Explicit Flow Connections

### Flows that BYPASS columns:

| Flow | From (col) | To (col) | Skips | Why |
|---|---|---|---|---|
| VC/Investors → Providers | 1 | 3 | Channels | VC doesn't go through sales channels |
| Hyperscaler margin → Operating Cash | 2 | 4 | Providers | Hyperscaler keeps 20% margin |
| Trad SaaS margin → Operating Cash | 2 | 4 | Providers | SaaS keeps 60% margin |

### Normal flows (adjacent columns):

| Flow | From | To |
|---|---|---|
| Consumer/SME/Enterprise → all channels | Buyers → Channels | Proportional |
| Model Subs/API/AI Native/IaaS → Providers | Channels → Providers | 100% pass-through |
| Hyperscalers → Providers | Channels → Providers | 80% (after margin) |
| Trad SaaS → Providers | Channels → Providers | 40% (after margin) |
| All Providers → Inference + People/SGA | Providers → Outcomes | 100% (providers are loss-making) |

---

## 7. Shelfware & Usage

**Shelfware does NOT reduce current collection.** Enterprises pay their invoices regardless of whether users adopt the product. Low usage (e.g., Copilot 35.8% usage rate) affects:
- Future **renewal rates** (may not renew)
- Future **growth rates** (slower seat expansion)
- NOT current **collected revenue**

The enterprise collection factor (0.80) reflects sales cycle delays and ramp periods, not usage rates.

---

## 8. What This Model Does NOT Cover

- **Capex** — GPU purchases, data centre construction ($250B+). On balance sheets, not operating flow
- **Training costs** — $30-50B/year. Separate from inference costs
- **Chinese provider revenue** — ByteDance (120T tokens/day) has zero external revenue. Excluded from Sankey.
- **Self-hosted inference** — 20-40T tokens/day with zero revenue attribution
- **Token volume projections** — Separate model (see model-assumptions.md Section 2)

---

## 9. How to Update

| New data arrives | What to change | Downstream impact |
|---|---|---|
| New ARR figure | Update provider start/end ARR | Recalculate collected revenue |
| New growth rate | Recalculate end-of-year ARR | Affects all forward projections |
| New buyer mix | Update collection factor | Changes collected revenue |
| New channel margin data | Update margin % | Changes Operating Cash split |
| Provider becomes profitable | Remove from VC subsidy | Flows to Operating Cash from providers |

All changes should be logged in the revision log of model-assumptions.md (Section 15).

---

## 10. Verified Balance Rules (Automated Check)

Run this check after any data change:

```
For each year:
  1. Buyers sum = totalSystem                    ✓
  2. Channels sum = totalCustomerRevenue         ✓
  3. Customer buyers sum = Channels sum          ✓
  4. VC buyer = totalVCSubsidy                   ✓
  5. Providers = channel_pass_through + VC       ✓
  6. Inference + People = Provider total         ✓
  7. Operating Cash = SUM(channel margins)       ✓
  8. Outcomes sum = totalSystem                  ✓
  9. No provider flows to Operating Cash         ✓
```
