# APAC BD Prospector — Project Brief

## Purpose

A local-first web app (React + SQLite/JSON backend) that serves as a combined **research engine, CRM, and outreach tool** for Inceptron's APAC business development. It should help Simon identify, enrich, track, and engage partnership and customer targets across the APAC region.

---

## Target Company Categories

### 1. GPU Clouds / Neo Clouds
Companies that own or lease GPU infrastructure and sell compute. These are **partnership targets** — Inceptron can white-label AI Studio and/or license the Compiler to help them optimise utilisation and offer managed inference.

**Why they matter:** Tier 2/3 cloud providers need optimised inference stacks to compete with hyperscalers. Inceptron offers 40% OPEX reduction + new revenue via white-label AI Studio.

**Examples to seed:** NEXTDC (AU), Macquarie Cloud Services (AU), SCX.ai / Southern Cross AI (AU), Keppel DC (SG), ST Telemedia (SG), GDS Holdings (CN), Chindata (CN), Bridge Data Centres (SG/MY), Yotta (IN), E2E Networks (IN), Nxtra by Airtel (IN).

### 2. AI Natives — Potential Customers of AI Studio / Compiler
Mid-sized companies building AI-first products, processing >2B tokens/month, running or building their own inference stack, and experiencing cost/performance/scaling friction.

**Why they matter:** These are direct customers for AI Studio's developer velocity value prop. ICP: Series A–C, 50–500 employees, building AI-first products.

**Examples to seed:** Dify.AI (SG-founded), EaseMate/EaseUS (CN, Chengdu), ClawX, Harrison.ai (AU), Canva AI team (AU), Airwallex AI (AU/HK), Grab AI (SG), GoTo AI (ID), Razorpay AI (IN), Yellow.ai (IN), Ola Krutrim (IN), SenseTime (CN/HK), Zhipu AI (CN), Moonshot AI (CN), MiniMax (CN), Baichuan (CN).

### 3. Inference Providers / Aggregators / Routing Platforms
Companies that route, aggregate, or resell inference. These are **distribution channel** targets — Inceptron should be listed as a provider.

**Why they matter:** Being listed = PLG demand generation. OpenRouter model but across APAC-centric platforms.

**Examples to seed:** Portkey.ai (APAC-adjacent), Together AI, SiliconFlow (CN), Novita AI (CN/SG), AnyScale (now Anyscale), modelscope (Alibaba), PAI (Alibaba), Volcengine/ByteDance MaaS (CN), Hugging Face APAC presence.

---

## Focus Markets

| Priority | Market | Notes |
|----------|--------|-------|
| 1 | **Australia / NZ** | Home market. Sovereign AI angle. SCX.ai opportunity. |
| 2 | **Singapore / SEA** | Inceptron's planned APAC hub (Singapore office H1 2026). Dify, Grab, GoTo. |
| 3 | **China / HK** | Open-weight model epicentre (DeepSeek, Qwen, etc). EaseUS target. Opaque market — needs creative sourcing. |
| 4 | **India** | Fast-growing AI ecosystem. E2E Networks, Yellow.ai, Krutrim. |

---

## Core Features

### Company Database
- **Fields:** Company name, domain, category (GPU Cloud / AI Native / Inference Aggregator), sub-category, HQ country, market (ANZ/SG-SEA/CN-HK/IN), estimated size (employees), funding stage, estimated monthly token volume (if known), current inference provider(s), tech stack notes, partnership fit score (1-5), status (Researched / Contacted / In Conversation / Partner / Declined), notes.
- **Seed data:** Pre-populate with the examples listed above.
- **Bulk import:** CSV upload for adding companies in batch.

### Contact Database
- **Fields:** Name, title, company (FK), LinkedIn URL, email (if known), seniority (C-level / VP / Director / Manager / IC), role type (Technical / Business / Product), source (LinkedIn / event / referral / cold), relationship status (Unknown / Connected / Warm / Active Conversation), last contacted date, notes.
- **Link contacts to companies** (many-to-one).

### Conversation / Interaction Log
- **Fields:** Date, company, contact(s), channel (email / LinkedIn / call / meeting / event), summary, next steps, follow-up date, attachments/links.
- **Timeline view** per company showing all interactions.

### Automated Research (dual-mode: Manual or API)

The app supports two modes, controlled by a **Settings page** toggle and the presence of `ANTHROPIC_API_KEY` in the environment (or a settings field in the UI):

#### Mode A: Manual (no API key — default)
- **"Research" button** on each company detail page:
  1. Copies a pre-formatted research prompt to clipboard (including company name, domain, category)
  2. The user pastes this into Claude Code (or Claude.ai with web search), gets back structured JSON
  3. The app has a **"Paste Research" text area** where the user pastes the JSON response
  4. The app parses the JSON and populates the structured fields automatically
- **Batch mode**: "Export Research Prompts" button on the company list page exports all un-researched companies as a single prompt. User runs it in Claude Code, gets back a JSON array, pastes into a batch import textarea.

#### Mode B: API (when `ANTHROPIC_API_KEY` is set)
- **"Research" button** calls the Anthropic API directly from the backend:
  - Model: `claude-sonnet-4-20250514`
  - Tools: `web_search` enabled for live enrichment
  - Parses the structured JSON response and writes directly to the DB
- **"Research All" button** on company list page batch-enriches all un-researched companies sequentially (with a progress indicator and rate-limit-friendly delays)
- Estimated cost: ~$0.01–0.05 per company research call (Sonnet at $3/$15 per MTok)

#### Research prompt template (used by both modes):
```
Research this company for a B2B partnership/sales assessment:
Company: {name} | Domain: {domain} | Category: {category}

Return ONLY a JSON object with these fields:
{
  "employees_est": number,
  "funding_stage": "Seed/A/B/C/D+/Public/Bootstrapped",
  "monthly_tokens_est": "string estimate or 'Unknown'",
  "current_providers": "comma-separated list or 'Unknown'",
  "tech_stack_notes": "brief summary of AI/ML stack",
  "fit_score": 1-5,
  "fit_reasoning": "one sentence",
  "suggested_contacts": [
    {"title": "CTO", "why": "technical decision maker"}
  ],
  "summary": "2-3 sentence company overview relevant to AI inference"
}
```

### Outreach Drafting (dual-mode: Manual or API)

Same dual-mode pattern as Research:

#### Mode A: Manual (no API key — default)
- **"Draft Outreach" button** on each contact detail page:
  1. Copies a pre-formatted outreach prompt to clipboard (including company profile, category, contact details, any prior interactions)
  2. The user pastes this into Claude Code, gets back email/LinkedIn variants
  3. The app has a **"Paste Drafts" text area** where the user pastes the response
  4. The app parses and stores each variant in the `outreach_drafts` table

#### Mode B: API (when `ANTHROPIC_API_KEY` is set)
- **"Draft Outreach" button** calls the API directly, generates variants, and stores them in-app immediately
- **"Draft All Pending" button** on dashboard generates outreach for all contacts that have a company researched but no drafts yet

#### Outreach prompt template (used by both modes):
Auto-populates with:
- Company context (name, category, market, fit score, research summary)
- Contact context (name, title, seniority)
- Interaction history (if any)
- Category-specific angle:
  - **AI Studio path:** "Ship AI products 3x faster" — for AI Native targets
  - **Neo Cloud path:** "Optimize costs AND generate new revenue" — for GPU Cloud targets
  - **Distribution path:** "Listed provider" pitch — for Inference Aggregators
- Request format: 2-3 email variants + 1 LinkedIn note, returned as JSON

Each draft should have **copy-to-clipboard** functionality for quick use.

### Follow-Up Tracker
- Dashboard showing:
  - Companies needing follow-up (by date)
  - Pipeline by category and market
  - Contacts with no activity in 14+ days
  - New companies added but not yet contacted

---

## Tech Stack (Recommended)

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Frontend | React + Tailwind | Fast to build, Claude Code handles well |
| Backend | Node.js + Express (or Next.js API routes) | Simple, single-language stack |
| Database | SQLite via `better-sqlite3` (local) | No infra needed, portable, easy to query |
| AI (Manual mode) | Claude Code copy-prompt / paste-JSON | Default — no API key needed |
| AI (API mode) | Anthropic API via `@anthropic-ai/sdk` | Optional — set `ANTHROPIC_API_KEY` to enable. Uses Sonnet 4.6 ($3/$15 per MTok) with `web_search` tool |
| Auth | None (local tool, single user) | Simplicity |
| Deployment | Local dev server initially | Can move to Vercel/Railway later |

---

## Data Model (SQLite)

```sql
CREATE TABLE companies (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  domain TEXT,
  category TEXT CHECK(category IN ('GPU Cloud', 'AI Native', 'Inference Aggregator')),
  sub_category TEXT,
  hq_country TEXT,
  market TEXT CHECK(market IN ('ANZ', 'SG-SEA', 'CN-HK', 'IN', 'Other')),
  employees_est INTEGER,
  funding_stage TEXT,
  monthly_tokens_est TEXT,
  current_providers TEXT,
  tech_stack_notes TEXT,
  fit_score INTEGER CHECK(fit_score BETWEEN 1 AND 5),
  status TEXT DEFAULT 'Researched' CHECK(status IN ('Researched', 'Contacted', 'In Conversation', 'Partner', 'Declined')),
  research_summary TEXT,
  research_raw TEXT,
  notes TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE contacts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_id INTEGER REFERENCES companies(id),
  name TEXT NOT NULL,
  title TEXT,
  linkedin_url TEXT,
  email TEXT,
  seniority TEXT CHECK(seniority IN ('C-level', 'VP', 'Director', 'Manager', 'IC')),
  role_type TEXT CHECK(role_type IN ('Technical', 'Business', 'Product', 'Other')),
  source TEXT,
  relationship_status TEXT DEFAULT 'Unknown' CHECK(relationship_status IN ('Unknown', 'Connected', 'Warm', 'Active Conversation')),
  last_contacted DATE,
  notes TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE interactions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_id INTEGER REFERENCES companies(id),
  contact_id INTEGER REFERENCES contacts(id),
  interaction_date DATE NOT NULL,
  channel TEXT CHECK(channel IN ('Email', 'LinkedIn', 'Call', 'Meeting', 'Event', 'Other')),
  summary TEXT,
  next_steps TEXT,
  follow_up_date DATE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE outreach_drafts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_id INTEGER REFERENCES companies(id),
  contact_id INTEGER REFERENCES contacts(id),
  draft_type TEXT CHECK(draft_type IN ('Cold Email', 'LinkedIn Note', 'Follow-Up Email')),
  variant_label TEXT,
  subject TEXT,
  body TEXT,
  status TEXT DEFAULT 'Draft' CHECK(status IN ('Draft', 'Sent', 'Archived')),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## Build Phases

### Phase 1: Core Database + UI (Day 1)
- Set up project scaffolding (React + Express + SQLite)
- Company CRUD with list/detail views
- Contact CRUD linked to companies
- Interaction log with timeline view
- Basic dashboard (counts by category, market, status)
- Seed data for ~30 companies across the 4 markets

### Phase 2: AI Research Workflow (Day 1-2)
- Settings page with API key field + mode toggle (Manual / API)
- **Manual mode:** "Research" button → copies prompt to clipboard; "Paste Research" textarea → parses JSON into fields; batch export prompt for multiple companies
- **API mode:** "Research" button → calls Anthropic API with web_search → auto-populates fields; "Research All" batch button with progress indicator
- Store parsed results + raw response in DB for both modes

### Phase 3: Outreach Engine (Day 2)
- **Manual mode:** "Draft Outreach" button → copies context-rich prompt to clipboard; "Paste Drafts" textarea → parses and stores variants
- **API mode:** "Draft Outreach" button → calls API → stores variants directly; "Draft All Pending" batch button
- LinkedIn note generator
- Follow-up generator (includes interaction history as context)
- Copy-to-clipboard for each stored draft

### Phase 4: Follow-Up Dashboard (Day 2)
- Overdue follow-ups view
- "Stale" contacts (no activity in 14+ days)
- Pipeline kanban by status
- Filter/sort by market, category, fit score

### Phase 5 (Future): Automation & Integrations
- Google Sheets / CSV export
- LinkedIn Sales Navigator integration (manual for now)
- Email sending via Gmail API
- Slack notifications for follow-up reminders
- Notion/Google Drive sync for meeting notes

---

## Inceptron Context (for prompt templates)

The app's prompt templates should include this context so Claude Code has full background when researching or drafting:

```
Inceptron is an AI inference infrastructure company. Two products:

1. AI Studio — A managed inference platform that lets AI-native companies ship 
   AI products 3x faster. Includes an Agentic Optimiser for automated performance 
   and cost improvement. Target: CTOs/Product Leads at mid-market AI companies 
   (Series A-C, 50-500 employees, >2B tokens/month).

2. Compiler — Optimises model execution across GPU, CPU, and alternative silicon 
   (AMD, Intel, custom ASICs, AWS Inferentia). Extracts maximum throughput from 
   hardware. Target: Neo Clouds and chip makers.

Geographic focus: APAC (ANZ, Singapore/SEA, China/HK, India) with existing 
presence in EMEA.

Partnership models:
- Neo Clouds: White-label AI Studio + integrate Compiler for 40% OPEX reduction
- Inference Aggregators: Get listed as a provider for PLG demand generation
- AI Natives: Direct customer of AI Studio platform

Key differentiators: Agentic Optimiser (automated, continuous), unified 
experiment-to-production workflow, hardware-agnostic Compiler.
```

---

## Success Metrics

- **Coverage:** 50+ companies profiled across 4 markets within 2 weeks
- **Outreach velocity:** 10+ personalised outreach drafts per week
- **Pipeline:** 15+ companies in "Contacted" or "In Conversation" within 30 days
- **Follow-up discipline:** Zero overdue follow-ups older than 7 days

---

## Notes for Claude Code

- This is a **single-user local tool** — no auth, no multi-tenancy.
- Prioritise speed of build over polish. Functional > beautiful.
- **Dual-mode AI features:** The app must work fully without an API key (manual copy/paste mode). When `ANTHROPIC_API_KEY` is set (via `.env` file or entered in a Settings page), AI features switch to direct API calls automatically.
- **Mode detection:** On app startup, check for `ANTHROPIC_API_KEY`. Show a banner/indicator in the UI: "🟢 API Mode" or "🟡 Manual Mode". The Settings page should let the user enter/update the key without restarting.
- **API implementation:** Use `@anthropic-ai/sdk` npm package. Model: `claude-sonnet-4-20250514`. For research calls, enable the `web_search` tool. Handle rate limits gracefully with exponential backoff on batch operations.
- SQLite is preferred over a hosted DB for portability and simplicity.
- The app should work fully offline — AI features just won't have fresh research without Claude Code or API access.
- **Batch mode (manual):** Export un-researched companies as a single mega-prompt that Claude Code can process, returning a JSON array to import back in one paste.
- **Batch mode (API):** Sequential processing with 2-second delays between calls, progress bar in UI, ability to cancel mid-batch.
