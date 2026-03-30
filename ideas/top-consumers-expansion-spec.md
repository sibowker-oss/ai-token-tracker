# Top Token Consumers — Expansion Spec

**File:** Master data JSON (contains `dashboard.topConsumers`)  
**Dashboard:** https://sibowker-oss.github.io/ai-token-tracker/dashboard.html  
**Date:** 2026-03-30  
**Purpose:** Expand the existing 21-company `topConsumers` array with new fields and new companies. Single source for dashboard display and future pages.

---

## 1. Current Schema (unchanged fields)

```json
{
  "co": "Cursor (Anysphere)",
  "hq": "US",
  "type": "AI Dev Tool",
  "tokens": "~800B/day",
  "prov": "Anthropic, OpenAI",
  "ev": "Evidence string...",
  "conf": "Med-High"
}
```

---

## 2. New Fields to Add

Add these to every `topConsumers` entry. All are optional — populate what's known, leave `null` for unknowns.

```json
{
  "co": "Cursor (Anysphere)",
  "hq": "US",
  "type": "AI Dev Tool",
  "tokens": "~800B/day",
  "prov": "Anthropic, OpenAI",
  "ev": "Evidence string...",
  "conf": "Med-High",

  "founded": 2022,
  "category": "ai-application",
  "subcategory": "coding",
  "providers": ["anthropic", "openai"],
  "tokensNumeric": 800000000000,
  "arr": "$500M-1B",
  "arrNumeric": 750000000,
  "valuation": "$10B+",
  "valuationNumeric": 10000000000,
  "totalFunding": "$900M+",
  "status": "private",
  "website": "https://cursor.com",
  "employeeCount": null,
  "lastUpdated": "2026-03-30"
}
```

### Field Definitions

| Field | Type | Purpose |
|-------|------|---------|
| `founded` | number | Year founded. Powers age calc + AI Vintage toggle |
| `category` | string | One of: `foundation-model`, `ai-application`, `ai-infrastructure`, `ai-cloud`, `vertical-ai`, `digital-native`, `enterprise-saas` |
| `subcategory` | string | Freeform: `coding`, `search`, `legal`, `design`, `gateway`, `messaging`, `fintech`, `edtech`, etc. |
| `providers` | string[] | Lowercase provider keys matching `dashboard.providers`. Fixes the Multi-provider filter bug — company shows under ANY listed provider |
| `tokensNumeric` | number | Daily tokens as raw number. Enables sorting/charting. Null if unknown |
| `arr` | string | Human-readable ARR estimate with ranges |
| `arrNumeric` | number | Midpoint ARR in USD for sorting. Null if unknown |
| `valuation` | string | Human-readable valuation |
| `valuationNumeric` | number | Midpoint valuation in USD for sorting. Null if unknown |
| `totalFunding` | string | Total funding raised |
| `status` | string | One of: `private`, `pre-ipo`, `public`, `acquired`, `subsidiary` |
| `website` | string | Primary URL |
| `employeeCount` | number | Headcount if known |
| `lastUpdated` | string | ISO date of last data refresh for this entry |

### Backward Compatibility

- `prov` (string) is kept for existing dashboard rendering
- `providers` (array) is the new canonical field for filtering logic
- `tokens` (string) is kept for display
- `tokensNumeric` (number) is added for sorting/charting
- No existing fields are removed or renamed

---

## 3. Companies to Add (~25-30 new entries)

### AI Applications

| Company | Founded | Category | Tokens Est. | Providers | ARR | Confidence |
|---------|---------|----------|-------------|-----------|-----|------------|
| Jasper | 2021 | Content | ~30B/day | OpenAI, Anthropic | ~$130M | Low-Med |
| Copy.ai | 2020 | Content/GTM | ~15B/day | OpenAI, Anthropic | ~$30M | Low |
| Writer | 2020 | Enterprise writing | ~25B/day | Own + OpenAI | ~$100M | Low-Med |
| Midjourney | 2021 | Image gen | ~10B/day | Own | ~$300M | Med |
| Runway | 2018 | Video gen | ~8B/day | Own | ~$100M | Low |
| Pika | 2023 | Video gen | ~5B/day | Own | Unknown | Low |
| Suno | 2023 | Music gen | ~5B/day | Own | Unknown | Low |
| Character.ai | 2021 | AI characters | ~60B/day | Own | ~$150M | Low-Med |
| Lovable | 2023 | App builder | ~20B/day | Anthropic, OpenAI | ~$100M | Low-Med |
| Bolt.new | 2024 | App builder | ~15B/day | Anthropic, OpenAI | Unknown | Low |
| ElevenLabs | 2022 | Voice AI | ~15B/day | Own | ~$330M | Med |
| Synthesia | 2017 | Video avatars | ~10B/day | Own + OpenAI | ~$100M | Low |
| Tome | 2020 | Presentations | ~8B/day | OpenAI | ~$30M | Low |
| Glean | 2019 | Enterprise search | ~30B/day | OpenAI, Anthropic, Google | ~$100M | Low-Med |
| Sierra AI | 2023 | Customer agents | ~20B/day | OpenAI, Anthropic | Unknown | Low |
| Intercom Fin | 2011 | CS automation | ~25B/day | OpenAI, Anthropic | ~$50M AI-specific | Med |

### AI Infrastructure

| Company | Founded | Category | Tokens Est. | Providers | ARR | Confidence |
|---------|---------|----------|-------------|-----------|-----|------------|
| Together AI | 2022 | Inference | ~100B/day | Meta, Mistral, open models | ~$100M | Low-Med |
| Fireworks AI | 2022 | Inference | ~60B/day | Meta, Mistral, open models | Unknown | Low |
| LangChain | 2022 | Framework | N/A (orchestrator) | All | Unknown | N/A |
| Groq | 2016 | LPU inference | ~40B/day | Own hardware | Unknown | Low |
| Cerebras | 2016 | AI chips | ~30B/day | Own hardware | Unknown | Low |
| CoreWeave | 2017 | GPU cloud | N/A (IaaS) | All | ~$2.3B | Med |

### Foundation Model Providers (as consumers of their own + others' tokens)

| Company | Founded | Category | Tokens Est. | Providers | ARR | Confidence |
|---------|---------|----------|-------------|-----------|-----|------------|
| Mistral AI | 2023 | Foundation model | ~15B/day (API served) | Own | ~$400M | Low-Med |
| Cohere | 2019 | Enterprise LLM | ~20B/day | Own | ~$100M | Low |
| AI21 Labs | 2017 | Enterprise LLM | ~10B/day | Own | Unknown | Low |
| DeepSeek | 2023 | Foundation model | ~40B/day (API) | Own | ~$300M | Low |

### Vertical AI

| Company | Founded | Category | Tokens Est. | Providers | ARR | Confidence |
|---------|---------|----------|-------------|-----------|-----|------------|
| Mercor | 2023 | AI hiring | ~10B/day | OpenAI, Anthropic | ~$100M | Low |
| Abridge | 2018 | Clinical AI | ~8B/day | OpenAI | ~$50M | Low |
| Hebbia | 2020 | Financial AI | ~15B/day | OpenAI, Anthropic | Unknown | Low |

---

## 4. Updated `meta.company_types`

Expand the existing `company_types` array in the file's `meta` block to include the new categories:

```json
"company_types": [
  "AI Startup",
  "AI Cloud",
  "Digital Native",
  "AI Infrastructure",
  "Enterprise AI",
  "AI Model Provider",
  "Global High-Volume Consumer",
  "AI Application",
  "Vertical AI",
  "Enterprise SaaS",
  "AI Dev Tool",
  "Consumer AI",
  "Foundation Model"
]
```

---

## 5. Dashboard UI Changes

### 5.1 Filter Bar (above the table)

- **Category dropdown:** All | AI Application | AI Infrastructure | Foundation Model | Vertical AI | Digital Native | Enterprise SaaS
- **Provider filter:** Uses `providers` array (not `prov` string). Company appears under ANY matching provider. Solves the current "Multi" bug.
- **Founded range:** All | Pre-2020 | 2020-2022 | 2023+ (the "AI Vintage" toggle)
- **Confidence filter:** All | High | Med+ | Med | Low+
- **Search:** Free text across `co`, `type`, `ev`

### 5.2 Table Columns

| Column | Source | Sortable |
|--------|--------|----------|
| Company | `co` | Alpha |
| Type / Category | `type` + `category` badge | Yes |
| Founded | `founded` | Yes |
| Est. Tokens/Day | `tokens` display, sort by `tokensNumeric` | Yes (default) |
| Providers | `providers` as icon chips | No |
| ARR | `arr` display, sort by `arrNumeric` | Yes |
| Confidence | `conf` as color badge | Yes |

### 5.3 Expansion Row

Click a row to show:
- Full evidence text (`ev`)
- Valuation + funding
- Website link
- Last updated + freshness dot (green <30d, yellow 31-90d, grey 90d+)

### 5.4 Summary Stats (above table)

- **Companies tracked:** {count}
- **Combined est. tokens/day:** {sum of tokensNumeric}
- **Provider split:** mini donut from `providers` arrays

### 5.5 AI Vintage Toggle

A prominent toggle/switch:
- **All Companies** — full list
- **AI-Era Only (post-Nov 2022)** — filters to `founded >= 2023`

This is the reclassification insight applied to startups. Only ~15-20 of the 45+ companies will survive this filter — telling the story that most token consumption comes from companies that predate the AI era.

---

## 6. Data Maintenance

### Adding a new company

1. Add entry to `dashboard.topConsumers` array in the master JSON
2. Populate all known fields, set unknowns to `null`
3. Set `lastUpdated` to today
4. Set `conf` honestly
5. Commit → GitHub Pages auto-deploys

### Quarterly review

- Re-estimate `tokensNumeric` using triangulation methodology
- Update `arr` / `arrNumeric` from press/earnings
- Update `conf` if new evidence emerges
- Check `founded` for any newly founded entrants
- Update `lastUpdated`

### Future automation path

- Earnings transcript parser → auto-flag ARR changes
- OpenRouter API → auto-detect new high-volume models/consumers
- Crunchbase/PitchBook scraping → funding/valuation updates

---

## 7. Implementation Priority

### Phase 1 — Ship this
1. Add new fields to existing 21 entries (backfill `founded`, `providers`, `tokensNumeric`, `category`, etc.)
2. Add ~15 highest-profile new companies (Jasper, Midjourney, Character.ai, ElevenLabs, Lovable, Together AI, Mistral, etc.)
3. Update dashboard JS to use `providers` array for filtering
4. Add `founded` column + sort

### Phase 2 — Enhanced
5. Full ~45-50 company list
6. Filter bar with category/provider/founded/confidence
7. AI Vintage toggle
8. Summary stats bar
9. Expansion row with full detail

### Phase 3 — Lead gen
10. "Get the full dataset" CTA → email capture
11. Shareable filter URLs (`?category=coding&founded=2023`)
12. "Advisory analysis" CTA → Webflow site link
