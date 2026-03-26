# APAC AI Company Intelligence Database

Tracking APAC-based AI companies: who they are, what models they buy, from whom, and who to talk to.

## Quick Stats
- **Companies tracked:** 25
- **Last updated:** 2026-03-26
- **Countries covered:** China (7), India (7), US/APAC (4), Japan (3), South Korea (2), Singapore (2)
- **Very High volume buyers:** 12
- **Top providers by demand:** OpenAI (18 companies), Anthropic (12), Google (10), DeepSeek (4)

## Companies

### Very High Volume

| Company | HQ | Category | Volume Signal | Providers |
|---------|-----|----------|--------------|-----------|
| [Portkey](companies/portkey.md) | US/India | AI Gateway | 1T+ tokens/day, $180M+ AI spend | 40+ providers |
| [API7.ai](companies/api7.md) | China | AI Gateway | 10T+ API requests/day | OpenAI, Anthropic, Google, DeepSeek |
| [Wrtn](companies/wrtn.md) | Korea | Consumer Aggregator | 6.5M MAU, ~$100M ARR | OpenAI, Anthropic |
| [Monica AI](companies/monica-ai.md) | China/Singapore | Consumer Aggregator | 10M+ users | OpenAI, Anthropic, Google, DeepSeek |
| [MiniMax](companies/minimax.md) | China | Model Provider/App | 212M users, $150M+ cloud bills | Anthropic, OpenAI |
| [Moonshot AI](companies/moonshot-ai.md) | China | Model Provider/App | $18B valuation, 4x API growth | Anthropic |
| [Yellow.ai](companies/yellow-ai.md) | India | Enterprise Conversational | 1,300+ clients, $79.5M rev | OpenAI, Google |
| [Gupshup](companies/gupshup.md) | India | Enterprise Messaging | 120B+ messages/year, $1.4B unicorn | OpenAI |
| [Haptik](companies/haptik.md) | India | Enterprise Conversational | 2B+ conversations, Reliance Jio backed | OpenAI |
| [BLACKBOX.AI](companies/blackboxai.md) | US | Dev Tools | 20M+ devs, $31.7M rev | OpenAI, Anthropic, Google |
| [Zhipu AI](companies/zhipu-ai.md) | China | Model Provider | 2.7M paying devs, HKEX IPO | Proprietary |
| [Baichuan AI](companies/baichuan-ai.md) | China | Model Provider | $2.7B valuation, 12+ LLMs | Proprietary |

### High Volume

| Company | HQ | Category | Volume Signal | Providers |
|---------|-----|----------|--------------|-----------|
| [Dify](companies/dify.md) | CN/US | LLM Orchestration | 280+ enterprise clients, 1.4M deployments | OpenAI, Anthropic, Google |
| [Classmethod](companies/classmethod.md) | Japan | Cloud/AI Integration | 15,000+ AWS accounts, 3,000+ companies | Anthropic |
| [Sakana AI](companies/sakana-ai.md) | Japan | AI Research | $2.65B valuation, $379M raised | OpenAI, Google |
| [Sarvam AI](companies/sarvam-ai.md) | India | Sovereign AI | India gov partnership, UIDAI/Aadhaar | Mistral, OpenAI |
| [Upstage](companies/upstage.md) | Korea | Model Provider/DocAI | Samsung client, $157M raised | AWS |
| [CoRover.ai](companies/corover-ai.md) | India | Enterprise/Gov | 1B+ users, Indian Railways, 70+ banks | Google, NVIDIA |
| [Skit.ai](companies/skit-ai.md) | India | Enterprise Voice | 1M+ calls/week automated | OpenAI |
| [Reka AI](companies/reka-ai.md) | Singapore | Model Provider | $1B unicorn, Snowflake integration | Proprietary |

### Medium Volume

| Company | HQ | Category | Volume Signal | Providers |
|---------|-----|----------|--------------|-----------|
| [EaseUS/EaseMate](companies/easeus-easemate.md) | China | Consumer Aggregator | 5-10M users, $11.2M rev | OpenAI, Google, DeepSeek |
| [Cinnamon AI](companies/cinnamon-ai.md) | Japan | Enterprise DocAI | 50+ enterprise clients, $16.8M rev | OpenAI, Anthropic |
| [Nurix AI](companies/nurix-ai.md) | India | Enterprise Voice | 60+ enterprise clients | OpenAI, Anthropic |
| [Katalon](companies/katalon.md) | Vietnam/US | Dev Tools/Testing | Gartner Visionary | OpenAI |

### Unknown Volume

| Company | HQ | Category | Notes | Providers |
|---------|-----|----------|-------|-----------|
| [ClawX](companies/clawx-valuecell.md) | China | AI Agent Desktop | Deliberately opaque, OpenClaw ecosystem | OpenAI, Anthropic, Google |

## Provider Demand Heatmap

```
OpenAI     ██████████████████ 18/25 companies (72%)
Anthropic  ████████████       12/25 companies (48%)
Google     ██████████         10/25 companies (40%)
DeepSeek   ████                4/25 companies (16%)
Mistral    ███                 3/25 companies (12%)
AWS        █                   1/25 companies  (4%)
NVIDIA     █                   1/25 companies  (4%)
```

## Automation

```bash
# Enrich all companies (scrape GitHub, websites)
python3 scripts/enrich.py --all

# Add a new company
python3 scripts/enrich.py --add "Company Name" --url "https://example.com"

# Generate newsletter (markdown or HTML)
python3 scripts/newsletter.py --format markdown
python3 scripts/newsletter.py --format html

# Monitoring report (stale entries, incomplete data, outreach pipeline)
python3 scripts/monitor.py --report

# Database stats
python3 scripts/enrich.py --stats
```

**Scheduled:** Weekly enrichment + newsletter runs every Monday at 9am.

## File Structure
```
apac-ai-intel/
  companies.json          # Structured database (machine-readable)
  README.md               # This file
  companies/              # 25 detailed company profiles
  scripts/
    enrich.py             # Enrichment pipeline (GitHub, web scraping)
    newsletter.py         # Newsletter generator (markdown, HTML, text)
    monitor.py            # Monitoring & staleness alerts
  newsletters/            # Generated newsletter output
  reports/                # Monitoring reports
```
