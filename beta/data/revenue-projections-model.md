# Revenue Projection Model — Working Tables

**Built:** 2026-04-05
**Status:** DRAFT — for review before applying to Sankey/dashboard
**Method:** ARR-based projection using authoritative anchors, growth rates, market share trends

---

## 1. Model Provider Revenue Projections

### Input data

| Provider | Exit ARR 2025 | Latest ARR (Q1 2026) | Source | Growth rate | Source | Market share trend | Source |
|---|---|---|---|---|---|---|---|
| OpenAI | $20B | $25B (Mar 2026) | Sacra / press release | +150% YoY | Multiple | Stable 40-50% of market | Barclays |
| Anthropic | $4.5B (collected) | $19B (Mar 2026) | Brad Gerstner / Sacra | 14x in 14 months | Observed | Growing: 40%→73% of new spend | Barclays |
| Google/Gemini | ~$4.2B (est.) | ~$4.2B | Editorial | +48% YoY (Cloud) | Alphabet earnings | Stable | — |
| DeepSeek | ~$0.3B | ~$0.3B | Editorial | +800% YoY (est.) | Editorial | Growing in China | — |
| Mistral | ~$0.4B | ~$0.4B | Editorial | +250% YoY (est.) | Editorial | Stable (EU niche) | — |
| xAI | ~$0.5B | ~$0.5B | Editorial | +500% YoY (est.) | Editorial | Small but growing | — |
| Minimax | ~$0.15B | ~$0.15B | Editorial | +400% YoY (est.) | Editorial | Growing in China | — |
| Moonshot/Kimi | ~$0.1B | ~$0.1B | Editorial | +300% YoY (est.) | Editorial | Growing in China | — |

### ARR → Collected Revenue Conversion

| Provider | Q1 2026 ARR | ARR method haircut | Adjusted ARR | Segment mix | Blended collection factor | Notes |
|---|---|---|---|---|---|---|
| OpenAI | $25B | 0.88 (best 4-week) | $22.0B | 15% API, 55% consumer, 15% SME, 15% enterprise | 0.93 | Confirmed methodology |
| Anthropic | $19B | 1.00 (monthly) | $19.0B | 70% API, 15% consumer, 15% enterprise | 0.97 | High API mix → high collection |
| Google | $4.2B | 1.00 | $4.2B | 20% API, 50% consumer, 30% enterprise | 0.92 | Bundled with Workspace |
| Others | varies | 0.93 (unknown) | varies | 40% API, 20% consumer, 20% SME, 20% enterprise | 0.93 | Default profile |

### 2026 Revenue Projection (full year collected)

**Method: Log-mean for hyper-growth providers, simple average for moderate growth**

| Provider | Start ARR (Jan 2026) | End ARR (Dec 2026) | Growth type | Revenue calc method | 2026 collected est. | Confidence |
|---|---|---|---|---|---|---|
| OpenAI | $22.0B (adjusted) | $38.0B (adjusted, tracking to $50B ARR mid-2027) | Hyper (1.7x) | Log-mean: (38-22)/ln(38/22) = $29.3B | **$27.2B** (x0.93 collection) | Medium-High |
| Anthropic | $19.0B | $35.0B (extrapolated, decelerating from 14x) | Hyper (1.8x) | Log-mean: (35-19)/ln(35/19) = $26.0B | **$25.2B** (x0.97 collection) | Medium |
| Google | $4.2B | $6.2B (+48% YoY) | Moderate (1.5x) | Simple avg: (4.2+6.2)/2 = $5.2B | **$4.8B** (x0.92 collection) | Low |
| DeepSeek | $0.3B | $1.2B (+300% est., decelerating from 800%) | Hyper (4x) | Log-mean: (1.2-0.3)/ln(1.2/0.3) = $0.65B | **$0.6B** (x0.93) | Low |
| Mistral | $0.4B | $0.8B (+100% est., decelerating from 250%) | Moderate (2x) | Simple avg: $0.6B | **$0.6B** | Low |
| xAI | $0.5B | $1.5B (+200% est., decelerating from 500%) | Hyper (3x) | Log-mean: $0.91B | **$0.8B** | Low |
| Minimax | $0.15B | $0.4B | Hyper | Log-mean: $0.26B | **$0.2B** | Low |
| Moonshot/Kimi | $0.1B | $0.25B | Hyper | Log-mean: $0.16B | **$0.15B** | Low |
| **Model Provider Total** | | | | | **$59.6B** | |

### 2027 Revenue Projection

| Provider | Start ARR (Jan 2027) | End ARR (Dec 2027) | Revenue calc | 2027 collected est. | Notes |
|---|---|---|---|---|---|
| OpenAI | $38.0B | $50.0B (company target) | Log-mean: $43.6B x 0.93 | **$40.5B** | Decelerating toward $50B target |
| Anthropic | $35.0B | $55.0B (extrapolated, further decel) | Log-mean: $44.2B x 0.97 | **$42.9B** | May overtake OpenAI on collected |
| Google | $6.2B | $9.2B (+48% YoY) | Simple avg: $7.7B x 0.92 | **$7.1B** | Steady cloud growth |
| DeepSeek | $1.2B | $3.0B | Log-mean: $1.96B x 0.93 | **$1.8B** | |
| Mistral | $0.8B | $1.2B | Simple avg: $1.0B | **$0.9B** | |
| xAI | $1.5B | $3.0B | Log-mean: $2.16B x 0.93 | **$2.0B** | |
| Minimax | $0.4B | $0.8B | Log-mean: $0.58B | **$0.5B** | |
| Moonshot/Kimi | $0.25B | $0.5B | Log-mean: $0.36B | **$0.3B** | |
| **Model Provider Total** | | | | **$96.0B** | |

---

## 2. Enterprise SaaS AI Revenue

### Input data

| Company | Product | Latest ARR/ACV | Source | Growth | Source quality |
|---|---|---|---|---|---|
| Microsoft | Copilot (full AI biz) | $13B ARR | Microsoft Q2 FY26 earnings | ~100% YoY | **Authoritative** |
| Salesforce | Agentforce | $800M standalone ARR | Salesforce Q4 FY26 earnings | ~200% YoY | **Authoritative** |
| ServiceNow | Now Assist | $600M+ ACV | ServiceNow Q4 2025 earnings | ~100% YoY (doubled) | **Authoritative** |
| SAP | Joule AI | ~$300M (est.) | Analyst estimates | ~150% YoY | Editorial |
| Adobe | Firefly/GenAI | ~$400M (est.) | Analyst estimates | ~100% YoY | Editorial |

### Enterprise SaaS collection factor
- Enterprise contracts: 0.80 (long sales cycles, ramp periods)
- ~50% of Salesforce deals are free (shelfware reality)
- Microsoft Copilot: 35.8% actual usage rate

### 2026 Revenue Projection

| Company | Start ARR | End ARR | Collection factor | Shelfware adj | 2026 collected |
|---|---|---|---|---|---|
| Microsoft Copilot | $13B | $20B | 0.80 | 0.80 (35.8% usage) | **$10.6B** |
| Salesforce Agentforce | $0.8B | $2.0B | 0.80 | 0.50 (50% free) | **$0.6B** |
| ServiceNow | $0.6B | $1.2B | 0.80 | 0.85 | **$0.6B** |
| SAP | $0.3B | $0.6B | 0.80 | 0.80 | **$0.3B** |
| Adobe | $0.4B | $0.7B | 0.80 | 0.90 | **$0.4B** |
| Others (Zendesk, HubSpot, etc.) | $1.0B | $2.0B | 0.80 | 0.75 | **$0.9B** |
| **Enterprise SaaS Total** | | | | | **$13.4B** |

### 2027 Revenue Projection

| Company | End ARR | 2027 collected | Notes |
|---|---|---|---|
| Microsoft Copilot | $30B | **$16.0B** | Seat penetration growing from 3.3% |
| Salesforce Agentforce | $4.0B | **$1.3B** | Still heavy free tier |
| ServiceNow | $2.0B | **$1.1B** | |
| SAP | $1.2B | **$0.6B** | |
| Adobe | $1.2B | **$0.7B** | |
| Others | $4.0B | **$1.8B** | |
| **Enterprise SaaS Total** | | **$21.5B** | |

---

## 3. AI Native Apps

### Input data (from Forbes AI 50 + Sacra + entities.json)

| App | Category | Latest ARR | Source | Growth est. |
|---|---|---|---|---|
| Cursor (Anysphere) | Coding | ~$300M | Sacra/press | +400% YoY |
| Perplexity | Search | ~$100M | Press reports | +300% YoY |
| Character.ai | Consumer | ~$150M | Press reports | +100% YoY |
| ElevenLabs | Voice | ~$100M | Press reports | +200% YoY |
| Replit | Coding | ~$100M | Press reports | +150% YoY |
| Midjourney | Image | ~$200M | Press reports | +50% YoY |
| Harvey AI | Legal | ~$100M | Press reports | +200% YoY |
| Glean | Enterprise search | ~$100M | Press reports | +200% YoY |
| Jasper | Content | ~$80M | Press reports | +50% YoY |
| Others (30+ apps) | Mixed | ~$1.0B combined | Estimates | +150% YoY |

### AI Native collection factor
- Mostly API/consumer: 0.95-1.00
- High growth = high churn = slightly lower collection

### 2026/2027 Revenue Projection

| | 2025 collected | 2026 collected | 2027 collected |
|---|---|---|---|
| Top 9 apps | ~$1.2B | ~$3.5B | ~$7.0B |
| Long tail (30+ apps) | ~$1.0B | ~$2.5B | ~$5.0B |
| **AI Native Total** | **$2.2B** | **$6.0B** | **$12.0B** |

---

## 4. IaaS / Aggregators / Open Model Serving

### Input data

| Provider | Type | Known data | Revenue est. |
|---|---|---|---|
| OpenRouter | Aggregator | $3.4M/week GMV, 10% take rate | ~$18M ARR |
| Together AI | IaaS | $425M funding, $3.3B val | ~$100M ARR (est.) |
| Fireworks AI | IaaS | $77M funding | ~$50M ARR (est.) |
| Groq | LPU inference | $640M funding, $2.8B val | ~$30M ARR (est.) |
| Replicate | IaaS | $58M funding | ~$20M ARR (est.) |
| Anyscale | IaaS | $260M funding | ~$40M ARR (est.) |
| Others | Mixed | — | ~$100M ARR |

### 2026/2027 Revenue Projection

This channel grows fastest as open models (DeepSeek, Qwen, Llama, Mistral) are served through these platforms.

| | 2025 collected | 2026 collected | 2027 collected | Notes |
|---|---|---|---|---|
| **IaaS/Aggregator Total** | **$0.4B** | **$2.0B** | **$6.0B** | 61% of OpenRouter is open models, 85% of startup tokens on OSS |

---

## 5. Summary: Total Revenue Flow by Year

| Segment | 2025 Actual | 2026 Projected | 2027 Projected | CAGR |
|---|---|---|---|---|
| Model Providers (closed) | $12.4B | $59.6B | $96.0B | 178% |
| Enterprise SaaS | $2.8B | $13.4B | $21.5B | 177% |
| AI Native Apps | $2.2B | $6.0B | $12.0B | 134% |
| IaaS/Open Model | $0.4B | $2.0B | $6.0B | 287% |
| **Total Customer Revenue** | **$17.8B** | **$81.0B** | **$135.5B** | **176%** |

### Revenue by buyer type (derived from provider demand weights)

| Buyer | 2025 | 2026E | 2027E |
|---|---|---|---|
| Consumer | $5.2B (29%) | $20B (25%) | $30B (22%) |
| SME | $3.4B (19%) | $12B (15%) | $20B (15%) |
| Enterprise | $8.9B (50%) | $42B (52%) | $72B (53%) |
| **Total customer** | **$17.5B** | **$74B** | **$122B** |
| VC Subsidy | $9.8B | $7B | $14B |
| **Total system** | **$27.3B** | **$81B** | **$136B** |

### Operating outcome split

| Outcome | 2025 | 2026E | 2027E | Trend |
|---|---|---|---|---|
| Inference | $14.0B (51%) | $38B (47%) | $55B (41%) | Shrinking % — efficiency gains |
| People/SGA | $11.1B (41%) | $28B (35%) | $45B (33%) | Shrinking % — scale leverage |
| Operating Cash Flow | $2.2B (8%) | $15B (19%) | $36B (27%) | Growing — path to sustainability |

---

## 6. Key Assumptions & Risks

**Upside risks (bull case):**
- Anthropic growth doesn't decelerate as fast → could hit $60B+ 2027 ARR
- Enterprise adoption accelerates past 5% pilot stage → SaaS grows faster
- Agentic workflows multiply tokens per task 10-100x → usage-based revenue surges

**Downside risks (bear case):**
- Open models commoditise inference → price war collapses model provider revenue
- Enterprise shelfware persists → SaaS revenue disappoints
- OpenAI misses $50B target → market sentiment shifts
- VC subsidy becomes unsustainable → forced restructuring

**Structural uncertainty:**
- Chinese provider revenue is almost entirely editorial — we have token volume but not revenue
- IaaS/Open growth from $0.4B to $6B is a 15x assumption
- The collection factor framework hasn't been validated against actual results

---

## 7. Data still needed to improve this model

| Data point | Impact | Source to target |
|---|---|---|
| OpenAI 2025 actual collected revenue | Validates the ARR conversion | Zitron / The Information (already have ~$7.65B) |
| Anthropic 2025 actual collected revenue | Validates conversion | Court filings / Sacra (have $4.71B consensus) |
| Microsoft Copilot actual usage-adjusted revenue | Validates shelfware discount | Microsoft earnings deep dive |
| Google AI-specific ARR (not total cloud) | Major gap | Alphabet earnings transcript (src-026) |
| Cursor/Perplexity ARR | Anchors AI native segment | Sacra deep dives (src-033 to 036) |
| Together AI / Fireworks revenue | Anchors IaaS segment | Press reports / fundraising |
| Enterprise AI adoption rate (updated from 5%) | Validates SaaS growth | Gartner / Forrester 2026 |
