# New Sections — Feature Spec

**Date:** 2026-03-31
**Status:** Scoping (for review before build)

---

## 1. Prediction Tracker

### What we have to power it
- 42 vault data points with dated claims, sources, and confidence levels
- 9 timeline events with quarterly narratives
- 7 Enterprise Reality Check rows (growth rates, claimed vs real revenue)
- 2 IPO-related vault claims (Jensen expects both to IPO 2026, OpenAI Q4 2026 per WSJ)
- Sankey data: $9.8B VC subsidy, $15 invested per $1 customer revenue
- Podcast claims with bear case data (Chamath: zero enterprise ROI, token spend 3x with no gains)
- Weekly automated pipeline to detect when predictions resolve (reconcile.py flags changes)

### Scope
**Page:** `predictions.html` (admin section, behind auth)
**Data:** New `predictions` array in site-data.json

```json
{
  "predictions": [
    {
      "id": "pred-001",
      "prediction": "OpenAI will not be gross-margin positive by end 2026",
      "date_made": "2026-03-31",
      "category": "provider_economics",
      "target_date": "2026-12-31",
      "status": "pending",
      "confidence": "high",
      "basis": "Sankey analysis: inference costs exceed revenue at gross margin level. $15 invested per $1 customer revenue. No path to GM+ without 35% inference cost reduction or 55% price increase.",
      "evidence_for": ["Sankey shows negative gross margin on inference", "Every token costs more to serve than customers pay"],
      "evidence_against": ["Revenue growing 150%+ YoY could outpace costs", "Hardware costs falling"],
      "resolution": null,
      "resolution_date": null,
      "resolution_source": null
    }
  ]
}
```

### Seed predictions (derivable from current data)

| # | Prediction | Basis from our data | Target |
|---|-----------|-------------------|--------|
| 1 | OpenAI won't be gross-margin positive by end 2026 | Sankey: inference costs > revenue at GM level | Q4 2026 |
| 2 | Open model share will exceed 40% of production inference by Q3 2026 | Currently ~20-25% (OpenRouter data). Growth rate +100% YoY. | Q3 2026 |
| 3 | M365 Copilot active usage won't exceed 50% by end 2026 | Currently 35.8% (Recon Analytics). Auto-install inflates seats. | Q4 2026 |
| 4 | Anthropic will IPO or file S-1 in 2026 | Jensen/Gerstner both stated expectation. $14B ARR. $380B valuation. | Q4 2026 |
| 5 | At least 2 of the Enterprise Reality Check vendors will stop reporting AI-specific revenue metrics | SAP/Workday already don't disclose. Salesforce's AWU metric criticized. | Q4 2026 |
| 6 | Total AI industry VC subsidy will exceed $15B in 2026 | $9.8B in 2025 with lower revenue base. Revenue growing but costs growing faster. | Q4 2026 |
| 7 | Cursor will exceed GitHub Copilot in daily token consumption by Q4 2026 | Cursor: 800B/day growing fast. Copilot: 1T/day but growth slower. Agent-first tools consume more tokens per session. | Q4 2026 |
| 8 | Chinese model providers (Minimax, Moonshot, DeepSeek) will account for >30% of OpenRouter volume | Currently ~35% combined. Xiaomi alone 20%. Growing fastest. | Q3 2026 |
| 9 | At least one "AI-native" company at >$500M ARR will fail or down-round significantly | High burn rates, negative gross margins at scale. Replit gross margin swings -14% to 36%. | Q4 2026 |
| 10 | The "coding agent" category will consolidate from 10+ tools to 3-4 dominant players | Cursor, Claude Code, GitHub Copilot, Windsurf currently. Kilo Code, Roo Code, Cline, OpenHands fragmented. | Q4 2026 |

### Build effort
- **Data:** Add predictions array to site-data.json (manual seed, 10 predictions)
- **Page:** New HTML page matching vault styling. Simple card layout with status badges.
- **Automation:** reconcile.py can flag when prediction-relevant data changes (e.g., new Copilot usage data comes in → flag prediction #3 for review)
- **Estimate:** 1 session to build

---

## 2. AI IPO Watch

### What we have to power it
- 54 private/pre-IPO companies in topConsumers with founded year, category, funding
- 21 companies with valuation data
- 13 companies with ARR >$100M (IPO-relevant scale)
- 2 vault claims about specific IPO timelines (OpenAI Q4 2026, both expected IPO 2026)
- 5 public companies tracked (can use as comps: Duolingo, Grab, Sea/Shopee, Kakao, C3.ai)

### Scope
**Page:** `ipo-watch.html` (public page)
**Data:** Extends topConsumers with IPO-specific fields

New fields per company:
```json
{
  "ipoStatus": "rumored",        // rumored | filed | priced | withdrawn | unlikely
  "ipoTimeline": "Q4 2026",      // rumored quarter
  "ipoTimelineSource": "WSJ",
  "lastValuation": "$840B",
  "revenueMultiple": "42x",       // valuation / ARR
  "comparablePublicComp": "Palantir (20x rev)",
  "ipoReadiness": "high"          // high / medium / low based on ARR scale + profitability
}
```

### Seed companies for IPO Watch

| Company | Valuation | ARR | Multiple | Timeline | Readiness |
|---------|-----------|-----|----------|----------|-----------|
| OpenAI | $840B | $20B | 42x | Q4 2026 (WSJ) | High |
| Anthropic | $380B | $14B | 27x | 2026 (Jensen) | High |
| Databricks | $62B | ~$2.4B | 26x | 2026 rumored | High |
| CoreWeave | $35B | ~$2.3B | 15x | Filed Mar 2025 | Filed |
| Stripe | $91B | ~$4B+ | 23x | Rumored | High |
| Cursor (Anysphere) | $10B+ | $1B+ | 10x | Not yet | Medium |
| Scale AI | $14B | Unknown | — | Rumored | Medium |
| Perplexity | $18B | $200M | 90x | Not yet | Low (margin) |
| Replit | $9B | $252M | 36x | Not yet | Low (margin) |
| Harvey | $11B | $190M | 58x | Not yet | Medium |
| ElevenLabs | $3.3B | $330M | 10x | Not yet | Medium |
| Mistral AI | $6.2B | $400M | 16x | Possible | Medium |

### Comparable public comps (for the multiples column)
Already in our data:
- Duolingo (DUOL): ~$500M rev, ~$10B mcap = 20x
- C3.ai (AI): ~$310M rev, ~$3.7B mcap = 12x
- Grab (GRAB): public, but mostly non-AI
- Plus external: Palantir (PLTR), Snowflake (SNOW), Cloudflare (NET)

### Build effort
- **Data:** Add ipoStatus fields to ~12 topConsumers entries
- **Page:** New HTML page with sortable table. Card view for top 5 most likely.
- **Automation:** Podcast claim extraction already picks up IPO mentions. reconcile.py can flag new valuation/timeline claims.
- **Estimate:** 1 session to build

---

## 3. Founder Benchmarks

### What we have to power it
- 37 companies with both ARR and token consumption data (benchmark dataset)
- 5 COGS ratios by category (ai-application: 30%, vertical-ai: 25%, etc.)
- 3 calculator product groups with activation rates and token conversion metrics
- Complete provider pricing data (model pricing table with input/output prices)
- Category breakdown: 42 ai-applications, 7 infra, 7 digital-native, 5 vertical-ai

### Scope
**Page:** `benchmarks.html` (public page — this is the lead-gen page)
**Data:** Uses existing topConsumers + calculator data. No new data needed.

### How it works

User inputs:
1. **Stage:** Seed / Series A / Series B / Series C / Growth
2. **ARR:** Slider or input ($1M — $1B)
3. **Monthly token spend:** ($1K — $500K)
4. **Primary provider(s):** Checkboxes
5. **Category:** AI Application / Vertical AI / Infrastructure / Digital Native

Output:
- **Percentile rank** vs the 37 benchmarked companies (by ARR, by tokens, by COGS ratio)
- **COGS health check:** "Your token spend is X% of revenue. Similar companies average Y%."
- **Provider mix comparison:** "You use 100% Anthropic. Similar-stage companies use 65% frontier / 35% open."
- **Growth rate benchmark:** "At your ARR, the median AI company grew X% QoQ"
- **Comparable companies:** Show 3-5 most similar companies from the dataset

### Benchmark percentile calculations

From our 37 companies with both data points:

| Percentile | ARR | Daily Tokens | COGS % |
|-----------|-----|-------------|--------|
| P25 | $36M | 8B | 15% |
| P50 | $100M | 25B | 25% |
| P75 | $252M | 100B | 35% |
| P90 | $400M | 200B | 50% |

### Lead-gen CTA at bottom
"Want a deeper analysis of your AI economics? Book a 30-min call with our advisory team."
→ Link to Calendly or Formspree form

### Build effort
- **Data:** No new data needed — all derived from existing topConsumers
- **Page:** Interactive HTML with input form + dynamic output. Similar to calculator.html.
- **Automation:** Benchmarks auto-update as topConsumers data changes.
- **Estimate:** 1-2 sessions to build (interactive form + percentile math + comparable matching)

---

## 4. The Subsidy Clock

### What we have to power it
- 2025 VC subsidy: $9.8B (from Sankey data)
- 2025 total system cost: $27.27B
- 2025 customer revenue: $17.47B
- Inference cost: $14.03B
- People/SG&A: $11.08B
- Margin: $2.15B (goes to trad SaaS/hyperscalers, not model providers)
- Capex data from vault claims: $250B+ industry total, Meta $115-135B alone
- Existing parked/counter.html prototype (live token counter — adapt for subsidy)
- Existing parked/capex.html prototype (capex vs revenue gap analysis)

### Scope
**Page:** `subsidy-clock.html` (public page — the shareable/viral one)
**Data:** Derived from Sankey + capex data. One key calculation:

```
Daily VC burn rate = $9.8B / 365 = $26.8M/day = $1.12M/hour = $18,630/minute
```

Including capex (not just operating subsidy):
```
Daily total AI industry burn = ($250B capex + $9.8B operating subsidy) / 365 = $711M/day
```

### What the page shows

**Hero counter:** Large animated number ticking up in real-time
```
$XXX,XXX,XXX,XXX
Total AI industry investment since Jan 1, 2025
```

**Rate cards:**
- $711M per day
- $29.6M per hour
- $493K per minute
- $8.2K per second

**Context cards:**
- "That's $15 invested for every $1 customers paid"
- "The VC subsidy alone ($9.8B) exceeds the entire revenue of 6 out of 8 tracked providers"
- "At current burn rates, the industry needs $X in customer revenue by [date] to break even"

**Break-even countdown:**
Using growth rates from our data:
- Customer revenue growing ~150% YoY (from $17.5B → ~$44B by end 2026)
- If costs grow at 80% YoY, break-even at gross margin level: ~Q2 2028
- If costs grow at 120% YoY (more realistic with capex ramp): never (at current trajectory)

### Build effort
- **Data:** One calculation block in the page JS. Uses Sankey data + capex claims.
- **Page:** Adapt from parked/counter.html (already has the animated counter). Add rate cards and context.
- **Automation:** Values update when Sankey data changes (annual refresh).
- **Estimate:** Half a session — mostly adapting existing prototype

---

## Implementation Priority

| # | Feature | Data readiness | Build effort | Traffic potential | POV value |
|---|---------|---------------|-------------|-------------------|-----------|
| 1 | **Subsidy Clock** | Ready (Sankey + capex) | Half session | Highest (viral, shareable) | High |
| 2 | **Prediction Tracker** | Ready (seed 10 predictions from existing data) | 1 session | Medium (bookmarkable) | Highest (reputation) |
| 3 | **AI IPO Watch** | 80% ready (add 12 IPO fields) | 1 session | High (VC/investor traffic) | Medium |
| 4 | **Founder Benchmarks** | Ready (37 companies benchmarkable) | 1-2 sessions | Medium (lead-gen) | Medium |

### Recommended order: 1 → 2 → 3 → 4

Subsidy Clock ships fastest and has the highest viral potential. Prediction Tracker builds reputation. IPO Watch captures investor audience. Benchmarks generates leads.

---

## Data gaps to fill

| Feature | What's missing | How to get it |
|---------|---------------|--------------|
| IPO Watch | ipoStatus, ipoTimeline fields on 12 companies | Manual research (1 hour) |
| IPO Watch | Public company comps (Palantir, Snowflake multiples) | Quick web scrape or manual |
| Prediction Tracker | Initial 10 predictions with basis text | Write from existing analysis (1 hour) |
| Subsidy Clock | 2026 capex estimate (for the running total) | Use Meta $125B + estimates from All-In podcast |
| Benchmarks | Nothing missing — all derived from existing data | — |
