# Feature: Podcast Transcript Data Pipeline

## Context
The AI Token Tracker dashboard (https://sibowker-oss.github.io/ai-token-tracker/dashboard.html) uses manually sourced data points from public filings, earnings calls, press reports & developer surveys. This feature automates the discovery of new data points from podcast transcripts.

## Goal
Build a pipeline that scrapes podcast transcripts, extracts structured data points relevant to the dashboard's methodology, and surfaces them for review/incorporation into the dataset.

---

## Podcast Sources (Ranked by Scrapability)

### Tier 1 — Full Transcripts Published (Direct Scrape)

| Podcast | Transcript URL Pattern | Format | Relevance |
|---------|----------------------|--------|-----------|
| **Latent Space** | `https://www.latent.space/p/{slug}` (Substack) | HTML with full transcript inline | Inference costs, token economics, model pricing, GPU utilization |
| **Acquired** | `https://www.acquired.fm/episodes/{slug}` | HTML transcript on episode page | Company financials, ARR figures, valuation multiples, business model deep dives |
| **All-In Podcast** | `https://allintranscripts.substack.com/` (community-run) | Substack posts | AI capex vs revenue gap, macro AI spend, enterprise adoption skepticism |
| **Odd Lots (Bloomberg)** | Available via Metacast (`metacast.app`) and Bloomberg | HTML | Macro AI investment thesis, "too much spend" analysis |

### Tier 2 — Third-Party Transcripts Available

| Podcast | Transcript Source | Notes |
|---------|------------------|-------|
| **20VC** | TranscriptForest, SimonSays AI | Not official; third-party generated. Covers ARR milestones, round sizes, SaaS multiples |
| **BG2Pod** | PodClips (`podclips.com`), Podscribe (`app.podscribe.com/series/2349338`) | Clips + transcripts. Covers AI capex, GPU economics, enterprise AI reality |

### Tier 3 — Audio-Only (Requires STT Processing)

| Podcast | RSS Feed | Relevance |
|---------|----------|-----------|
| **SaaStr Podcast** | Public RSS | M365 Copilot seats, Agentforce data, enterprise SaaS AI SKU metrics |
| **Cognitive Revolution** | Public RSS | AI infrastructure, compute costs |
| **Cloud Giants (Bessemer)** | Public RSS | Cloud index, NRR, efficiency metrics |
| **Stratechery / Dithering** | Paywalled RSS (subscriber only) | Enterprise adoption reality vs hype |
| **Pivot (Kara Swisher)** | Public RSS | Earnings call commentary, big tech AI spend |
| **Gradient Dissent (W&B)** | Public RSS | ML deployment costs, compute benchmarks |

**STT approach for Tier 3:** Use OpenAI Whisper or Deepgram on downloaded audio from public RSS feeds. Budget ~$0.006/min (Whisper API) or run locally with `whisper.cpp`.

---

## Data Points to Extract

The pipeline should look for claims matching these categories, which map to existing dashboard sections:

### Provider Revenue & ARR
- Pattern: `{company} + {revenue/ARR/run rate} + {dollar amount} + {time period}`
- Examples: "OpenAI is at $16.8B ARR", "Anthropic hit $14B annualized"
- Dashboard target: Token Volume & Revenue by Provider

### Token Volume & Pricing
- Pattern: `{tokens/day|requests/day|queries} + {volume} + {provider}`
- Pattern: `{model} + {price per token|cost per million tokens}`
- Dashboard target: Model Pricing & Estimated Volume

### GPU / Infrastructure Economics  
- Pattern: `{GPU count|H100|B200} + {utilization|capacity} + {percentage}`
- Pattern: `{capex|infrastructure spend} + {dollar amount}`
- Dashboard target: Methodology cross-checks (GPU capacity ceiling)

### Enterprise Adoption Metrics
- Pattern: `{product} + {seats/users/subscribers} + {count}`
- Pattern: `{adoption rate|retention|churn} + {percentage}`
- Pattern: `{pilot|POC|production} + {percentage|count}`
- Examples: "Copilot has 15M seats", "only 5% past pilot", "35.8% usage rate"
- Dashboard target: Enterprise AI Reality Check

### Skeptical / Bear Case Data
- Pattern: `{fail rate|project failure} + {percentage}`
- Pattern: `{shelfware|unused|underutilized} + {metric}`
- Dashboard target: Token Demand Quality Matrix, Enterprise Reality Check

### Valuation & Funding
- Pattern: `{company} + {valuation|raised|round} + {dollar amount}`
- Useful for: Contextualizing provider scale, advisory business reference points

---

## Proposed Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Scraper Layer   │────▶│  Extraction  │────▶│  Review Queue   │
│                  │     │   (LLM)      │     │                 │
│ - RSS monitors   │     │              │     │ - JSON output   │
│ - Web scrapers   │     │ - Classify   │     │ - Confidence    │
│ - STT (Tier 3)   │     │ - Extract    │     │   scores        │
│                  │     │ - Attribute  │     │ - Source links   │
└─────────────────┘     └──────────────┘     └─────────────────┘
                                                      │
                                                      ▼
                                              ┌───────────────┐
                                              │ Dashboard     │
                                              │ Data Update   │
                                              │ (manual merge │
                                              │  or auto PR)  │
                                              └───────────────┘
```

### 1. Scraper Layer
- **Tier 1:** HTTP fetch + HTML parse (BeautifulSoup or Cheerio)
- **Tier 2:** Same, different URL patterns
- **Tier 3:** Download MP3 from RSS → Whisper STT → text
- **Scheduling:** GitHub Actions cron (weekly) or local cron
- **Storage:** Raw transcripts as markdown in `/transcripts/{source}/{date}-{slug}.md`

### 2. Extraction Layer (LLM-powered)
- Feed transcript chunks to Claude API (or local model)
- System prompt: extract structured claims matching the categories above
- Output format per claim:
```json
{
  "claim": "OpenAI is at $16.8B ARR as of Q1 2026",
  "category": "provider_revenue",
  "entity": "OpenAI",
  "metric": "ARR",
  "value": 16800000000,
  "unit": "USD",
  "time_period": "Q1 2026",
  "source_podcast": "All-In Podcast",
  "source_episode": "E178",
  "source_date": "2026-03-15",
  "source_url": "https://allintranscripts.substack.com/p/...",
  "confidence": "high",
  "speaker": "Chamath Palihapitiya",
  "is_primary_source": false,
  "original_source_cited": "WSJ"
}
```

### 3. Review Queue
- Output: `data-updates/{date}-candidates.json`
- Human reviews before merging into dashboard data files
- Optional: auto-generate PR to the GitHub Pages repo with proposed data.js updates

---

## Implementation Priority

1. **Phase 1 (MVP):** Scrape Latent Space + All-In transcripts only. Extract to JSON. Manual review.
2. **Phase 2:** Add Acquired + Odd Lots. Add GitHub Actions scheduling.
3. **Phase 3:** Add Tier 2 sources. Add STT for high-value Tier 3 (SaaStr, BG2Pod audio).
4. **Phase 4:** Auto-PR generation. Confidence scoring. Deduplication against existing data points.

---

## Tech Stack Suggestion
- **Scraping:** Python (requests + BeautifulSoup) or Node (cheerio)
- **STT:** OpenAI Whisper API or whisper.cpp (local)
- **Extraction:** Claude API (claude-sonnet-4-20250514) — cost-effective for structured extraction
- **Scheduling:** GitHub Actions (free tier covers weekly runs)
- **Storage:** JSON files in repo, or SQLite for local dev

---

## Key Risks & Mitigations
- **Transcript availability changes:** Monitor RSS feeds; fall back to STT
- **LLM hallucination in extraction:** Always require source URL + confidence score; human review gate
- **Stale data:** Claims may reference older data repeated in new episodes — track `original_source_cited` to detect
- **Rate limits:** Substack/Metacast may throttle — add polite delays, cache aggressively
- **Copyright:** Store transcripts locally for processing only; never republish. Dashboard cites original sources, not transcripts.
