# AI Token Tracker — Enhancement Briefing v2

## Context
This briefing packages all discussions from the Claude.ai advisory session for porting into a Claude Code desktop session. The app is published at:
https://sibowker-oss.github.io/ai-token-tracker/dashboard.html

The app has multiple views: Dashboard, Follow the $ (Sankey), Shelfware Calculator, Time Machine, Live Pricing (OpenRouter), and Weekly Feed.

## Goal
Evolve from a static estimates dashboard into a **living, data-driven intelligence product** that:
1. Drives real interest and leads for an advisory business
2. Helps startup clients in their AI journey
3. Differentiates via accuracy, freshness, and depth that competitors can't easily replicate

---

## 1. KEY INSIGHT: THE AI-NATIVE ILLUSION

We applied a simple filter: **any company that pre-dates ChatGPT (Nov 2022) by more than 5 years is Enterprise Software, not AI-native.** The result is striking:

| Category | Count |
|---|---|
| AI Infrastructure (picks & shovels) | 17 |
| **AI-Native (truly, public)** | **8** |
| Enterprise SaaS + AI (added AI features) | 24 |
| Enterprise Software + AI (rebranded as AI) | 30 |
| Foundation Model Providers (hyperscalers) | 8 |
| IPO Pipeline (private, mostly AI-native) | 18 |
| Physical AI (autonomous/robotics) | 4 |
| **Total** | **109** |

**Only 8 truly AI-native companies are publicly traded.** The other 91 "AI stocks" are legacy software companies riding the narrative. The real AI-native wave (18 companies) is still in the IPO pipeline.

### The 8 Truly AI-Native Public Companies:
1. **CoreWeave (CRWV)** — Founded 2017, pivoted to AI GPU cloud 2019; IPO Mar 2025; $1.9B rev
2. **Astera Labs (ALAB)** — Founded 2017; AI connectivity chips; IPO Mar 2024; $396M rev
3. **Serve Robotics (SERV)** — Founded 2021; autonomous delivery robots; $2M rev (pre-revenue)
4. **Aurora Innovation (AUR)** — Founded 2017; autonomous trucking; $40M rev (pre-revenue)
5. **BigBear.ai (BBAI)** — Formed 2020 via SPAC merger; defense AI; $155M rev
6. **Credo Technology (CRDO)** — Founded 2008 but AI-pivoted; data center connectivity; $250M rev
7. **Rubrik (RBRK)** — Founded 2014 (borderline); AI data security; IPO Apr 2024; $920M rev
8. **Reddit (RDDT)** — Founded 2005 (not AI-native by rule, but AI data/content play); $1.3B rev

### Notable Reclassifications (NOT AI-native):
- **Palantir (PLTR)** — Founded 2003. Data analytics company that launched AIP in 2023.
- **C3.ai (AI)** — Founded 2009 by Tom Siebel. IoT/analytics pivot to AI branding.
- **SoundHound (SOUN)** — Founded 2005. Voice recognition company rebranded as AI.
- **CrowdStrike (CRWD)** — Founded 2011. Always used ML but marketed as AI post-2023.
- **Databricks** — Founded 2013. Enterprise Software by our rule, despite being AI-adjacent.
- **Scale AI** — Founded 2016. Enterprise Software by our rule.

---

## 2. DATA ACCURACY IMPROVEMENTS

### Current Methodology (already in app)
- Provider revenue from public filings + press
- Token volumes triangulated from 4 methods
- Self-hosted tokens from HuggingFace + PyPI
- Enterprise reality checks from earnings
- Live data from OpenRouter API, PyPI, npm, HuggingFace

### New Signals to Add (priority order)

**Tier 1 — Free, automatable:**
- SEC EDGAR filings API — revenue/ARR/guidance for all 109 companies
- Cloudflare Radar — independent AI API traffic signal
- Ollama GitHub releases — self-hosted channel currently missing
- Docker Hub pulls for vLLM, TGI, llama.cpp
- Artificial Analysis API — throughput benchmarks

**Tier 2 — Free, needs LLM parsing:**
- Earnings call transcripts via RSS — extract with Claude
- Company blog posts / press releases via RSS
- OECD AI Policy Observatory — country-level CSVs

**Tier 3 — Freemium:**
- SimilarWeb (free tier) — DAU/session depth
- Crunchbase basic API — funding rounds

**Tier 4 — Paywalled (manual citation only):**
- Morgan Stanley / UBS / Piper Sandler analyst reports
- Okta Businesses at Work
- Gartner / IDC

---

## 3. COMPANY DATA STRUCTURE

Full data in `ai_companies_reclassified.json` (109 companies). Each record:

```json
{
  "category": "AI-Native | Enterprise Software + AI | Enterprise SaaS + AI | AI Infrastructure | Foundation Model Providers | Physical AI | IPO Pipeline (AI-Native)",
  "company": "Company Name",
  "ticker": "TICK",
  "status": "Public | Pre-IPO",
  "founded": 2022,
  "ai_native": true,
  "cy_revenue_m": 1000,
  "cy_rev_growth_pct": 50,
  "cy_period": "CY24",
  "py_revenue_m": 667,
  "py_period": "CY23",
  "employees": 500,
  "ai_revenue_est_m": 1000,
  "ai_pct_of_total": 100,
  "notes": "Key context"
}
```

### Key ARR Reporters (from earnings — capture both ARR and Revenue):
| Company | Ticker | CY ARR ($M) | Growth | PY ARR ($M) |
|---------|--------|-------------|--------|-------------|
| CrowdStrike | CRWD | 4,240 | 23% | 3,440 |
| Zscaler | ZS | 3,015 | 22% | 2,462 |
| Datadog | DDOG | 3,800 | 28% | 2,970 |
| Adobe | ADBE | 16,990 | 11% | 15,330 |
| Workday | WDAY | 8,430 | 16% | 7,256 |
| HubSpot | HUBS | 2,780 | 20% | 2,320 |
| UiPath | PATH | 1,666 | 14% | 1,464 |
| Dynatrace | DT | 1,700 | 19% | 1,430 |
| SentinelOne | S | 860 | 29% | 664 |
| OpenAI | Pre-IPO | 16,800 | 200% | 5,600 |
| Anthropic | Pre-IPO | 14,000 | 233% | 4,200 |
| Databricks | Pre-IPO | 4,500 | 65% | 2,700 |

### Revenue per Employee Leaderboard:
| Company | Rev/Employee ($K) | Category |
|---------|-------------------|----------|
| OpenAI | 4,200 | IPO Pipeline |
| NVIDIA | 3,625 | AI Infrastructure |
| Cursor | 3,333 | IPO Pipeline |
| Anthropic | 2,800 | IPO Pipeline |
| Meta | 2,230 | Foundation Model |
| Arista | 1,667 | AI Infrastructure |
| CoreWeave | 1,324 | AI-Native |
| ElevenLabs | 1,100 | IPO Pipeline |
| Palantir | 1,098 | Enterprise Software |
| Avg SaaS | 300-500 | — |

---

## 4. IPO PIPELINE — 18 COMPANIES

| Company | Founded | AI-Native? | Expected | Est. Valuation |
|---------|---------|------------|----------|---------------|
| Databricks | 2013 | No | Q2 2026 | $105-134B |
| OpenAI | 2015 | Yes* | Q4 2026 | $800B-1T |
| Anthropic | 2021 | Yes | TBD 26-27 | $350B+ |
| xAI | 2023 | Yes | Mid-2026 | $1.5T (w/ SpaceX) |
| Cerebras | 2016 | No | 2026 | $8B+ |
| ElevenLabs | 2022 | Yes | TBD | $11B |
| Perplexity | 2022 | Yes | TBD | $18B+ |
| Cursor | 2022 | Yes | TBD | $10B+ |
| Mistral | 2023 | Yes | TBD | $6B+ |
| Glean | 2019 | Yes | TBD | $4.6B |
| Cohere | 2019 | Yes | TBD | $5.5B+ |
| Harvey AI | 2022 | Yes | TBD | $3B+ |
| Figure AI | 2022 | Yes | TBD | $3.2B+ |
| Together AI | 2022 | Yes | TBD | $3.2B+ |
| Scale AI | 2016 | No | TBD | $14B+ |
| Hugging Face | 2016 | No | TBD | $4.5B+ |
| SymphonyAI | 2017 | Yes | 2025-26 | TBD |
| Shield AI | 2015 | No | TBD | $5B+ |

---

## 5. FILES IN THIS PACKAGE

| File | Purpose |
|------|---------|
| `BRIEFING_v2.md` | This file — master context for Claude Code |
| `ai_companies_reclassified.json` | **PRIMARY DATA** — 109 companies, reclassified |
| `data_sources.json` | Automatable data sources with API endpoints |
| `ai_companies_financials_v2.xlsx` | Full spreadsheet with ARR + prior year (reference) |
| `ai_companies_universe.xlsx` | Original universe (reference, superseded by JSON) |

---

## 6. SUGGESTED IMPLEMENTATION ORDER

1. **AI-Native vs Enterprise Software view** — The killer feature. Show the "AI illusion" — only 8 truly AI-native public companies exist.
2. **Company financials explorer** — Filterable/sortable table of 109 companies
3. **Revenue per employee leaderboard** — AI-native efficiency vs legacy enterprise
4. **IPO pipeline tracker** — 18 upcoming AI IPOs with timeline
5. **SEC EDGAR automation** — Agent pulling quarterly earnings
6. **Expand triangulation signals** — Cloudflare, Docker Hub, Ollama
7. **"Last updated" freshness indicator** — Per data source
8. **ARR vs Revenue gap analysis** — Bookings vs recognized revenue

---

## 7. NARRATIVE FOR ADVISORY LEADS

**"Everyone trades AI stocks. We show you only 8 AI-native companies are actually public."**

The reclassification is the hook:
- 91 of 109 "AI companies" are legacy software with AI marketing
- The real AI-native wave is still private (18 in IPO pipeline)
- $3T+ combined expected float when they go public
- Enterprise "AI adoption" metrics inflated by shelfware

Target audiences:
- **Startup founders** — "Are you actually AI-native or AI-washed?"
- **Enterprise CIOs** — Separate AI-native vendors from rebranded legacy
- **Investors** — IPO pipeline timing, AI-native premium question
