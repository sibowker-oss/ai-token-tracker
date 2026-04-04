# AI Market Model — Assumptions & Estimation Framework

**Created:** 2026-03-28 (v1)
**Last updated:** 2026-04-04
**Status:** v3 — Multi-model consensus synthesis + authoritative anchors
**Previous versions:** assumptions-audit.md (v1), model-assumptions.md (v2)

---

## How to use this document

This is the single source of truth for every number in the dashboard and Sankey model. Each estimate has:
- **Classification:** Authoritative / Corroborated / Derived / Editorial
- **Source:** Where it came from
- **Date:** When it was valid
- **Revision history:** What changed and why

When new facts arrive, update the relevant section, add to the revision log (Section 15), and flag downstream numbers that need recalculation.

### Classification system

| Level | Definition | Dashboard treatment |
|---|---|---|
| **Authoritative** | First-party disclosure, court filing, earnings call, government data, official press release | Use directly. Anchor for derived estimates |
| **Corroborated** | Multiple independent sources agree within 15% | Use with confidence band |
| **Derived** | Calculated from authoritative inputs using documented methodology | Show methodology. Flag as derived |
| **Editorial** | Team estimate, no external source. Directional only | Flag clearly. Priority for replacement |

---

## 1. Revenue — Provider Level

### 1.1 OpenAI

| Metric | Value | Classification | Source | Date |
|---|---|---|---|---|
| 2024 collected revenue | ~$3.6B | Corroborated | Zitron/MSFT leaked docs | 2024 |
| H1 2025 collected revenue | ~$4.3B | Corroborated | The Information / Zitron | H1 2025 |
| H1 2025 inference spend | $5.022B | Authoritative | Zitron / MSFT leaked docs | H1 2025 |
| 2025 EOY ARR | $20B | Corroborated | All-In / multiple | End 2025 |
| Mar 2026 ARR | $25B | Corroborated | Sacra | Mar 2026 |
| Mar 2026 monthly revenue | $2B/month | **Authoritative** | OpenAI press release | Mar 2026 |
| Revenue growth | 4x Alphabet/Meta | **Authoritative** | OpenAI press release | Mar 2026 |
| 2025 operating loss | ~$6B | Corroborated | NYT / multiple | 2025 |
| 2026 cash burn | ~$25B | Editorial | The Information | 2026 |
| Valuation | $852B post-money | **Authoritative** | OpenAI press release | Mar 2026 |
| Total funding | $122B committed | **Authoritative** | OpenAI press release | Mar 2026 |
| Credit facility | $4.7B revolving (undrawn) | **Authoritative** | OpenAI press release | Mar 2026 |
| Ad pilot ARR | $100M+ in <6 weeks | **Authoritative** | OpenAI press release | Mar 2026 |
| Enterprise % of revenue | >40% | **Authoritative** | OpenAI press release | Mar 2026 |
| Consumer/business split | ~58/42 | Derived | Press release ">40%" enterprise | Mar 2026 |
| ARR reporting method | Best 4-week x 12 | **Authoritative** | Confirmed by Zitron | 2026 |
| ARR method haircut | 0.88 (inflates 10-15%) | Derived | Methodology analysis | 2026 |

### 1.2 Anthropic

| Metric | Value | Classification | Source | Date |
|---|---|---|---|---|
| Cumulative collected (through early 2025) | ~$5B | **Authoritative** | Sworn court affidavit | 2025 |
| 2025 collected revenue | ~$4.5B (consensus $4.71B) | Corroborated | The Information / Sacra / court filing | 2025 |
| Feb 2026 ARR | $14B | **Authoritative** | Brad Gerstner (investor) | Feb 2026 |
| Feb 2026 monthly revenue | $6B (28-day) | **Authoritative** | Brad Gerstner | Feb 2026 |
| Mar 2026 ARR | $19B | Corroborated | Sacra | Mar 2026 |
| Revenue mix | 70-75% API, 10-15% subs | Corroborated | Sacra | 2025 |
| Claude Code ARR | >$2.5B | Corroborated | Sacra | Feb 2026 |
| Business customers | 300,000+ | Corroborated | Sacra | 2026 |
| Valuation | $380B | Corroborated | Sacra / All-In | Feb 2026 |
| Revenue per GW | $10B/year | **Authoritative** | Sarah Friar (Anthropic CFO) | 2026 |
| Enterprise inference leader | Yes | Corroborated | Barclays analyst (Oct 2025) | 2025 |

### 1.3 Google

| Metric | Value | Classification | Source | Date |
|---|---|---|---|---|
| Cloud Q4 2025 revenue | $17.66B (+47.8% YoY) | **Authoritative** | Alphabet earnings | Q4 2025 |
| Vertex AI revenue | $2.5B | Derived | APAC AI Intel | 2025 |
| Cloud backlog | $240B (doubled YoY) | **Authoritative** | Alphabet earnings | 2025 |

### 1.4 Other Providers

| Provider | ARR | Classification | Source |
|---|---|---|---|
| Meta | $0 (open model) | N/A | No direct revenue |
| DeepSeek | $0.3B | Editorial | Press reports |
| Mistral | $0.4B | Editorial | Press reports |
| xAI | $0.5B | Editorial | Press reports |
| Minimax | $0.15B | Editorial | Press reports |
| Moonshot | $0.1B | Editorial | Press reports |

---

## 2. Token Volume — Multi-Model Consensus (v3)

### 2.1 Methodology: how these estimates were built

On April 4 2026, we solicited independent token volume estimates from 7 AI models (Claude Opus, Gemini Pro, DeepSeek, Grok, OpenAI-free, Kimi, Minimax) with no shared context. Each model was asked to estimate daily token throughput for the top 10 global providers with full methodology and sources.

We then:
1. Collected all authoritative anchor points cited across all responses
2. Compared estimates per provider across all 7 models
3. Weighted toward models with better China data (DeepSeek, Grok, Kimi) for Chinese providers
4. Anchored on authoritative disclosures where available
5. Cross-checked totals against independent methods (GPU ceiling, revenue back-calc, OpenRouter extrapolation)

### 2.2 Authoritative anchor points (hard data)

These are the foundation — everything else is derived or estimated relative to these.

| Data point | Value | Source | Date | Cited by |
|---|---|---|---|---|
| OpenAI API throughput | 15B tokens/min = **21.6T/day** | OpenAI press release | Mar 2026 | All 7 models |
| OpenAI API (earlier) | 6B tokens/min = **8.6T/day** | OpenAI Dev Day | Oct 2025 | 5 models |
| Google monthly tokens | 1.3 quadrillion/month = **43.3T/day** | Google Cloud / Sundar Pichai | Oct 2025 | 5 models |
| Google (earlier) | 980T/month = **32.7T/day** | Alphabet Q2 2025 earnings | Jul 2025 | 2 models |
| Google (earlier) | 480T/month = **16T/day** | Google | Apr 2025 | 1 model (Minimax) |
| Google throughput rate | 500M tokens/second = **43.2T/day** | Google infrastructure | Oct 2025 | 1 model (Kimi) |
| ByteDance/Doubao | **120T/day** | Volcano Engine / 36Kr | Mar 2026 | 4 models |
| ByteDance (earlier) | 50T/day | Volcano Engine | Dec 2025 | 3 models |
| ByteDance CNY peak | 63.3B tokens/min sustained | Volcano Engine | Feb 2026 | 1 model (Kimi) |
| China national total | **>140T/day** | National Data Administration | Mar 2026 | 2 models (Grok, Kimi) |
| Microsoft Foundry APIs | 500T+ tokens in H1 2025 = ~2.7T/day | Microsoft Q4 FY2025 earnings | Jul 2025 | 2 models |
| OpenRouter total | 22.38T/week = **3.2T/day** | OpenRouter signals (scraped) | Apr 2026 | Our data |
| OpenRouter blended price | $0.15/M tokens | OpenRouter | Apr 2026 | Our data |
| OpenAI WAU | 900M (50M paid subscribers) | OpenAI press release | Mar 2026 | All models |
| Baidu ERNIE | 1T/day | Baidu reports | Aug 2024 | 1 model (Kimi) |
| Alibaba external | ~5T/day (targeting 15-20T) | Alibaba Cloud statements | 2025 | 2 models |
| Alibaba internal | 16-17T (targeting 100T) | Alibaba Cloud statements | 2025 | 2 models |
| Barclays: OpenAI consumer | 2x Gemini consumer app tokens | Barclays analyst (Ross Sandler) | Oct 2025 | 2 models |
| Barclays: Anthropic enterprise | Leads enterprise inference share | Barclays analyst | Oct 2025 | 2 models |
| Llama downloads | 1.2B+ | Meta | 2025 | Our data |
| Open models on OpenRouter | 61% of volume | OpenRouter / Dataconomy | Feb 2026 | Our data |
| Startup tokens on open models | 85% | Jason Calacanis (All-In, portfolio observation) | Mar 2026 | Our data |

### 2.3 Raw estimates from all 7 models

| Provider | Opus | Gemini Pro | DeepSeek | Grok | OAI-free | Kimi | Minimax | Anchors |
|---|---|---|---|---|---|---|---|---|
| ByteDance | — | 60-80 | 120 | 110-130 | 2-4 | 100-120 | 0.1-0.5 | 120T (auth) |
| Google | 50-65 | 50-70 | 43 | 40-50 | 45-65 | 40-45 | 8-16 | 43T/day (auth) |
| Alibaba/Qwen | 5-12 | — | — | 15-30 | — | 20-30 | — | 5T ext + 16T int (auth) |
| OpenAI | 30-50 | 50-60 | 15-20 | 12-18 | 12-18 | 12-15 | 2-4 | 21.6T API (auth) |
| Tencent | — | 5-10 | — | — | — | 8-12 | — | No anchor |
| Baidu | — | 10-15 | — | — | — | 6-10 | — | 1T/day Aug 2024 |
| Meta | 15-30 | 20-30 | 8-10 | 5-12 | 5-9 | 4-6 | 1.5-3 | No direct anchor |
| Anthropic | 5-15 | 8-12 | 3-4 | 2-5 | 6-10 | 3-5 | 0.8-1.5 | Revenue-derivable |
| DeepSeek | 5-10 | 10-15 | 12-14 | 3-8 | 1.5-3 | — | 0.4-0.8 | No anchor |
| xAI | 2-5 | 2-5 | — | 0.5-2 | 2-4 | 1-2 | 0.1-0.3 | No anchor |
| Minimax | 3-8 | — | 5-6 | 3-7 | — | — | — | OR: 0.32T/day |
| Mistral | 1-3 | — | — | — | — | — | 0.08-0.2 | No anchor |
| Moonshot/Kimi | — | — | — | — | — | — | — | OR: small |
| **Total** | **150-250** | **255-347** | **220-280** | **250-350** | **90-140** | **200-230** | **15-35** | |

**Notes on outliers:**
- **Minimax model** gave estimates 10x lower than all others — appears to be using 2025 data, not April 2026. Excluded from consensus.
- **OpenAI-free** significantly underestimated China (ByteDance 2-4T vs 120T authoritative). China-adjusted estimate would be ~230-280T.
- **Gemini Pro** and **Grok** had the best China coverage.

### 2.4 Consensus estimates (v3)

Built by: anchoring on authoritative data where available, taking the median of the China-aware models (DeepSeek, Grok, Kimi, Gemini Pro) for Chinese providers, and using revenue/SDK cross-checks for Western providers.

| Provider | v1 (Mar 28) | v2 (Apr 4 AM) | **v3 Consensus** | Classification | Basis |
|---|---|---|---|---|---|
| **ByteDance** | — | — | **100-120T** | **Authoritative** | Volcano Engine 120T disclosure, confirmed by 4/7 models |
| **Google** | 90T | 10-20T | **43-55T** | **Authoritative** | 1.3Q/month (Oct 2025) + growth. 5/7 models agree |
| **Alibaba/Qwen** | — | — | **20-30T** | Corroborated | 5T external + 16-17T internal (company statements). 2/7 models |
| **OpenAI** | 200T | 25-30T | **25-35T** | **Derived** | 21.6T API (auth) + 4-10T consumer (derived from 900M WAU) |
| **Tencent** | — | — | **8-12T** | Editorial | Market share inference from China 140T total. 2/7 models |
| **Baidu** | — | — | **6-10T** | Derived | 1T/day Aug 2024 (auth) + 33x annual growth extrapolation |
| **Meta** | 80T | 20-50T | **8-15T** | Editorial | First-party only. Wide disagreement across models (4-30T). Conservative |
| **Anthropic** | 110T | 5-15T | **4-8T** | Derived | Revenue back-calc: $14B ARR x 75% API / ~$4/M blended = ~7T/day pre-discount |
| **DeepSeek** | 40T | 5-15T | **5-12T** | Editorial | Strong China domestic + global API. Wide range reflects uncertainty |
| **Minimax** | 30T | 3-5T | **3-6T** | Derived | OR: 0.32T/day. OR is ~3-5% of total usage. China domestic adds volume |
| **xAI** | 10T | 2-5T | **1-4T** | Editorial | Grok + X integration. Models agree on small scale |
| **Mistral** | 15T | 2-5T | **1-3T** | Editorial | EU-focused, efficient models. All models agree small |
| **Moonshot/Kimi** | 8T | 1-3T | **2-4T** | Derived | OR presence + China domestic |
| **Other closed** | — | — | **5-10T** | Editorial | Cohere, AI21, smaller Chinese labs, Samsung on-device, Apple Intelligence |
| **Self-hosted open models** | 134T | 20-50T | **20-40T** | Editorial | Llama/Qwen/Mistral on vLLM/Ollama/enterprise GPU. Unmeasurable. See S2.7 |
| | | | | | |
| **GLOBAL TOTAL** | **717T** | **100-200T** | **~280-370T** | **Derived** | v3 consensus |

### 2.5 Regional token distribution (revised)

| Region | v1 % | v3 % | Classification | Basis |
|---|---|---|---|---|
| China | (included in APAC 30%) | **~50%** | Derived | China NDA: 140T/day + ByteDance 120T + Alibaba/Tencent/Baidu/DeepSeek |
| North America | 40% | **~25-30%** | Derived | OpenAI + Anthropic + Meta first-party |
| Rest of Asia-Pacific | (in APAC) | **~8-10%** | Editorial | India growing fast, Japan/Korea/SEA |
| Europe | 18% | **~8-10%** | Editorial | Mistral + enterprise adoption |
| Middle East | 5% | **~2-3%** | Editorial | Saudi $100B AI investment |
| Latin America | 4% | **~2-3%** | Editorial | |
| Africa | 3% | **~1-2%** | Editorial | |

**Key revision:** China's share is dramatically higher than v1 assumed. ByteDance alone (120T) exceeds all non-Chinese providers combined (~110-160T). The China NDA figure of 140T appears to exclude ByteDance consumer or uses different measurement.

### 2.6 Cross-checks

| Method | Result | Consistent? |
|---|---|---|
| China NDA (140T) + ByteDance (120T) + non-China (~130T) | ~390T (if NDA excludes ByteDance) or ~270T (if includes) | Yes, within range |
| OpenAI (25T) as ~8-10% of global (consensus market share) | 250-310T | Yes |
| GPU ceiling: ~3M inference GPUs x 40% util x 1500 tok/sec | ~155T/day theoretical max (Western only) | Supports non-China portion |
| Revenue back-calc: ~$40B global AI rev / $0.30/M blended | ~365T/day | Upper end of range |
| All 7 models median (excl. Minimax outlier) | ~225-290T | Yes |
| OpenRouter (3.2T/day) as ~1% of global | ~320T | Yes |

### 2.7 Self-hosted / open model estimation

Self-hosted tokens are processed on infrastructure not controlled by the model provider. Three layers:

| Layer | Measurable? | Estimate | Basis |
|---|---|---|---|
| **Routed** (OpenRouter, LiteLLM, Portkey) | Yes | ~5-8T/day | OpenRouter 3.2T + others. 61% open models = ~2T open on OR |
| **IaaS-hosted** (Llama on AWS Bedrock, Azure, GCP) | Partially | ~8-15T/day | Cloud provider revenues for model hosting |
| **True self-hosted** (vLLM/Ollama on own GPUs) | No | ~10-20T/day | 85% of startup tokens on OSS (Calacanis). Ollama 4M downloads. LiteLLM 95M installs |
| **Total self-hosted** | | **~20-40T/day** | |

### 2.8 Why v1 was too high (717T) and v2 was too low (100-200T)

**v1 (717T) problems:**
- OpenAI at 200T was ~7x too high (actual ~25-35T)
- Did not track ByteDance, Alibaba, Tencent, Baidu separately
- "Others" at 134T was a residual plug, not independently estimated
- GPU ceiling assumed full fleet for inference; ~50% is training
- Per-user token estimates were too high

**v2 (100-200T) problems:**
- Correctly anchored on OpenAI API (21.6T) but didn't account for ByteDance (120T)
- Didn't include Chinese providers beyond DeepSeek
- Consumer estimates were too conservative
- Was built before the multi-model survey revealed China data

**v3 (280-370T) is anchored on:**
- 3 authoritative disclosures (OpenAI 21.6T API, Google 43T, ByteDance 120T)
- 1 government figure (China NDA 140T)
- Cross-validated against 6 independent AI model estimates
- Revenue back-calculation and GPU ceiling checks

---

## 3. OpenAI Detailed Breakdown

### 3.1 Token volume decomposition

| Segment | Volume | Classification | Method |
|---|---|---|---|
| API (direct + Azure) | 21.6T/day | **Authoritative** | 15B tokens/min x 1440 min/day |
| Consumer (ChatGPT) | 4-10T/day | Derived | See below |
| **Total** | **25-35T/day** | Derived | |

**Consumer derivation (multiple methods):**

| Method | Result |
|---|---|
| Bottom-up: 315M DAU x 5K tokens = 1.6T; 50M paid x 50K = 2.5T | ~4T/day |
| Kimi/DeepSeek models estimate | 4-8T consumer |
| Barclays: OpenAI consumer = 2x Gemini consumer. Google ~43T total, maybe ~10T consumer → OpenAI ~20T? | Seems high |
| OpenAI-free model: 150M DAU x 5K tokens = 0.75T consumer | Too low |
| **Working estimate** | **4-10T/day** |

### 3.2 Product metrics (all Authoritative — OpenAI press release, Mar 2026)

| Metric | Value |
|---|---|
| Weekly active users | 900M |
| Paid subscribers | 50M |
| Web visits vs #2 AI app | 6x monthly |
| AI time spent vs #2 | 4x next largest |
| AI time spent vs all others | 4x all others combined |
| Search usage | Nearly tripled in a year |
| Codex weekly users | 2M (up 5x in 3 months) |
| Codex growth | 70% month-over-month |
| Revenue trajectory | $1B yr1 → $1B/quarter EOY2024 → $2B/month Mar 2026 |
| Approaching 1B WAU | "soon" |

---

## 4. Chinese Providers — New in v3

China represents ~40-50% of global token volume. This was entirely missing from v1/v2.

### 4.1 China macro

| Metric | Value | Classification | Source |
|---|---|---|---|
| National daily tokens | >140T/day | **Authoritative** | China National Data Administration, Mar 2026 |
| Growth | 1,000x since early 2024 | **Authoritative** | China NDA |
| Enterprise tokens | 37T/day | Corroborated | Frost & Sullivan, H2 2025 |

### 4.2 ByteDance/Doubao

| Metric | Value | Classification | Source |
|---|---|---|---|
| Daily tokens | 120T | **Authoritative** | Volcano Engine / 36Kr / AAStocks, Mar-Apr 2026 |
| Growth | Doubled in 3 months (50T Dec 2025 → 120T Mar 2026) | **Authoritative** | Volcano Engine |
| Growth since launch | 1,000x (120B/day May 2024 → 120T/day) | **Authoritative** | Volcano Engine |
| Peak throughput | 63.3B tokens/min (CNY 2026) | **Authoritative** | Volcano Engine |
| Consumer app MAU | 175M+ | Corroborated | Multiple reports |

### 4.3 Alibaba/Qwen

| Metric | Value | Classification | Source |
|---|---|---|---|
| External customer usage | ~5T/day (2025), targeting 15-20T | Corroborated | Alibaba Cloud executive statements |
| Internal usage | 16-17T/day, targeting 100T | Corroborated | Alibaba Cloud executive statements |
| China enterprise share | ~32% | Corroborated | Frost & Sullivan |
| HuggingFace downloads | 400M+ | **Authoritative** | HuggingFace |
| Chinese OSS models vs US | Overtook US in total downloads | Corroborated | HuggingFace / GetAIBook |

### 4.4 Other Chinese providers

| Provider | Estimate | Classification | Notes |
|---|---|---|---|
| Tencent/Hunyuan | 8-12T/day | Editorial | WeChat ecosystem, gaming. Market inference from China total |
| Baidu/ERNIE | 6-10T/day | Derived | 1T/day Aug 2024 + 33x annual growth (Baidu disclosure) |
| DeepSeek | 5-12T/day | Editorial | Aggressive pricing, strong on global aggregators |
| Minimax | 3-6T/day | Derived | OR #1 at 0.63T/day. Domestic adds volume |
| Moonshot/Kimi | 2-4T/day | Derived | Long-context specialist, strong OR presence |

---

## 5. ARR-to-Revenue Conversion Framework

*Unchanged from v1. See assumptions-audit.md Section 2 for full detail.*

Key parameters:
- API/Usage: 1.00 | Consumer Subs: 0.95 | SME: 0.90 | Enterprise: 0.80
- OpenAI ARR haircut: 0.88 (best 4-week x 12)
- Anthropic NRR: 1.50 → nrrBoost: 1.125

---

## 6. Source Credibility Scoring

*Unchanged from v1. See assumptions-audit.md Section 3.*

Key levels: SEC/Sworn (0.95), Leaked Internal (0.80), Platform Data (0.80), Official (0.75), Reporting (0.70), Calculation (0.55), Estimate (0.45)

---

## 7. Sankey Flow Model ("Follow the Dollar")

### 7.1 Top-level totals (unchanged from v1)

| Category | Value | Notes |
|---|---|---|
| Total System | $27.27B | Customer revenue + VC subsidy |
| Customer Revenue | $17.47B | |
| VC Subsidy | $9.80B | Operating losses funded by investors |
| Inference | $14.03B | GPU compute for serving tokens |
| People/SGA | $11.08B | |
| Margin | $2.15B | Only Trad SaaS + hyperscaler pass-through |

### 7.2 Provider flows

| Provider | Customer Revenue | VC Subsidy | Total |
|---|---|---|---|
| OpenAI | $7.65B | $6.00B | $13.65B |
| Anthropic | $4.71B | $3.00B | $7.71B |
| Google | $2.00B | $0.50B | $2.50B |
| IaaS | $0.50B | $0.30B | $0.80B |

*See assumptions-audit.md Section 4 for full Sankey detail.*

---

## 8. Dashboard Distribution Assumptions

### 8.1 Industry distribution (Editorial — unchanged)

| Industry | % |
|---|---|
| Software & Tech | 33% |
| Financial Services | 16% |
| Healthcare | 9% |
| Retail & E-commerce | 9% |
| Marketing & Ads | 8% |
| Customer Service | 7% |
| Education | 5% |
| Manufacturing | 4% |
| Legal & Gov & Other | 9% |

### 8.2 Use case distribution

| Use Case | % | Supporting data |
|---|---|---|
| Coding & Dev Tools | 28% | OpenRouter: programming >50% of volume (was 11% in 2024) |
| Chat & Assistants | 27% | |
| Content & Writing | 15% | |
| Enterprise Agents | 10% | |
| Search & RAG | 10% | OpenAI: search usage tripled |
| Data Analysis | 7% | |
| Other | 5% | |

---

## 9. Data Center Economics

| Metric | Value | Classification | Source |
|---|---|---|---|
| DC cost per GW | $50B all-in | **Authoritative** | Chamath (building 1GW DC) |
| Revenue per GW | $10B/year | **Authoritative** | Sarah Friar (Anthropic CFO) |
| DC payback | 5 years (profit years 6-8) | **Authoritative** | Chamath |
| DC protest risk | 40% (~7GW at risk) | Editorial | Chamath |
| At-risk revenue | $70B/year | Derived | 7GW x $10B |

---

## 10. Enterprise Reality Check

| Metric | Value | Classification | Source |
|---|---|---|---|
| M365 Copilot seats | 15M (3.3% of 450M) | **Authoritative** | Microsoft Q2 FY26 |
| Copilot usage rate | 35.8% | Corroborated | Recon Analytics |
| Enterprise past pilot | 5% | Corroborated | Gartner 2025 |
| Tried then kept | 70% tried, 8% kept | Corroborated | Recon Analytics |
| Organizations using AI | 78% (up from 55%) | Corroborated | Stanford AI Index 2025 |
| Token price deflation | -80% YoY | **Authoritative** | Observable API pricing |
| Inference cost drop | 280x (GPT-3.5 equiv: $20→$0.07/M) | **Authoritative** | Epoch AI / Stanford |
| Open vs frontier gap | 8% → 1.7% | Corroborated | Stanford AI Index |

---

## 11. Market Context (Stanford AI Index 2025)

| Metric | Value | Source |
|---|---|---|
| Corporate AI investment 2024 | $252.3B (+26% YoY) | Stanford AI Index |
| Private AI investment 2024 | +44.5% YoY | Stanford AI Index |
| Generative AI investment 2024 | $33.9B (+18.7% YoY) | Stanford AI Index |
| US private AI investment | $109.1B (12x China) | Stanford AI Index |
| Hardware performance growth | 43% annually (doubles every 1.9 years) | Stanford AI Index |
| Training compute doubles | Every 5 months | Stanford AI Index |
| AI share of CS publications | 41.8% (was 21.6% in 2013) | Stanford AI Index |
| DeepSeek V3 training cost | $6M (vs GPT-4 $79M) | Stanford AI Index |
| China AI patents | 69.7% of global grants | Stanford AI Index |

---

## 12. Key Uncertainties & Open Questions

| Question | Current basis | What would resolve it | Priority |
|---|---|---|---|
| ByteDance 120T — does China NDA 140T include or exclude this? | Unclear — if excludes, total China is 260T+ | China NDA methodology disclosure | **Critical** |
| OpenAI consumer token volume | 4-10T derived from DAU math | OpenAI disclosure | **High** |
| Meta first-party Llama inference | 8-15T editorial. Models ranged 4-30T | Meta disclosure | **High** |
| Self-hosted open model volume | 20-40T unmeasurable | Infrastructure analysis | **High** |
| Tencent/Baidu actual volumes | Editorial estimates from market share | Company disclosures | Medium |
| Blended token price (all providers) | $0.15-0.50/M depending on segment | More provider revenue/volume pairs | Medium |
| Input/output token ratio globally | ~3:1 to 5:1 assumed | Provider disclosures | Low |

---

## 13. Multi-Model Survey — Full Source References

Sources cited across the 7 AI model responses:

| Source | Data point | Cited by |
|---|---|---|
| Alphabet Q2 2025 Earnings (Jul 2025) | 980T tokens/month | Opus, OAI-free |
| Google Cloud event (Oct 2025) | 1.3Q tokens/month; 500M tokens/sec | Gemini Pro, Grok, Kimi, DeepSeek |
| OpenAI Dev Day (Oct 2025) | 6B tokens/min API; 800M+ WAU | All except Minimax |
| OpenAI Press Release (Mar 2026) | 15B tokens/min; 900M WAU; $2B/month; $122B funding; $852B val | Our primary source |
| Barclays — Ross Sandler (Oct 2025) | OpenAI 2x consumer vs Gemini; Anthropic leads enterprise | Opus, Gemini Pro |
| ByteDance / Volcano Engine (Mar 2026) | 120T/day; doubled in 3 months; 1000x since launch | DeepSeek, Grok, Kimi, Gemini Pro |
| ByteDance CNY peak (Feb 2026) | 63.3B tokens/min sustained | Kimi |
| China National Data Admin (Mar 2026) | >140T/day national total | Grok, Kimi |
| Frost & Sullivan | China enterprise 37T/day; Alibaba 32% share | Grok |
| Alibaba Cloud statements | 5T external, 16-17T internal, targeting 100T | Grok, Kimi |
| Microsoft Q4 FY2025 Earnings (Jul 2025) | 500T+ tokens H1 2025 via Foundry | Gemini Pro, Opus |
| Baidu ERNIE reports (Aug 2024) | 1T/day; 33x annual growth | Kimi |
| Reportify (Feb 2026) | OpenAI 560M DAU, Google 130M, Anthropic 10M | DeepSeek |
| Goldman Sachs (Jan 2026) | ByteDance 30T+/day; $500B+ AI capex 2026 | Gemini Pro |
| OpenRouter Rankings (Apr 2026) | 22T+ weekly; MiMo #1; Chinese 61%+ | Our data + multiple models |
| Stanford AI Index 2025 | Investment, adoption, cost metrics | Our data |
| Zitron / Microsoft leaked docs | OpenAI inference spend, revenue methodology | Our data (v1) |
| Sacra | Anthropic/OpenAI revenue, ARR | Our data (v1) |
| Anthropic court affidavit | $5B cumulative revenue | Our data (v1) |
| Brad Gerstner (All-In, Altimeter) | Anthropic $14B ARR, $6B/month | Our data (v1) |

---

## 14. Comparison: v1 → v2 → v3

| Metric | v1 (Mar 28) | v2 (Apr 4 AM) | v3 (Apr 4 PM) |
|---|---|---|---|
| OpenAI tokens | 200T | 25-30T | 25-35T |
| Google tokens | 90T | 10-20T | 43-55T |
| ByteDance | Not tracked | Not tracked | 100-120T |
| Alibaba | Not tracked | Not tracked | 20-30T |
| Global total | 717T (dashboard) / 565T (model) | 100-200T | **280-370T** |
| China % of global | ~10% (implicit) | ~15% (implicit) | **~45-50%** |
| Number of providers tracked | 9 + Others | 10 + Others | **14 + Others** |
| Methodology | GPU ceiling + bottom-up | OpenAI API anchor + revision | Multi-model consensus + authoritative anchors |
| Sources consulted | 1 session, ~20 sources | + OpenAI press release + audit | + 7 AI models + 30+ sources |

---

## 15. Revision Log

| Date | Section | Change | Trigger |
|---|---|---|---|
| 2026-04-04 PM | Token volumes (S2) | **v3: 280-370T/day.** Multi-model consensus from 7 AI model estimates. Added ByteDance (120T), Alibaba (20-30T), Tencent, Baidu. Revised Google to 43-55T. China now ~50% of global. | Multi-model survey + authoritative disclosures |
| 2026-04-04 PM | Chinese providers (S4) | New section with ByteDance, Alibaba, Tencent, Baidu, DeepSeek detail | Multi-model survey |
| 2026-04-04 PM | Regional distribution (S2.5) | China revised from ~10% to ~50% of global tokens | China NDA 140T + ByteDance 120T |
| 2026-04-04 PM | Cross-checks (S2.6) | Added 6 independent validation methods | Multi-model analysis |
| 2026-04-04 PM | Sources (S13) | Full source catalogue from all 7 model responses | Survey compilation |
| 2026-04-04 PM | Market context (S11) | Added Stanford AI Index 2025 data | User provided report |
| 2026-04-04 AM | Token volumes (S2) | v2: 100-200T/day. OpenAI from 200T to 25-30T | OpenAI press release: 15B tokens/min API |
| 2026-04-04 AM | OpenAI revenue (S1.1) | Added $2B/month, $122B funding, $852B valuation, 900M WAU, 50M subs | OpenAI press release |
| 2026-04-04 AM | Valuation | Updated from $840B to $852B | OpenAI press release |
| 2026-04-04 AM | Classification system | Added 4-tier system | Audit review |
| 2026-03-28 | All | v1 created | Initial build session (b69f5507) |
