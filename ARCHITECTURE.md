# The AI Ledger — Data Architecture

## The Core Problem This Solves

AI industry data is fragmented across earnings calls, podcast discussions, API observations, developer download stats, and research reports. No single source is authoritative. This system **triangulates** across all of them to produce a coherent, continuously updated picture.

---

## How Data Flows Through the System

```
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL SOURCES                          │
│                                                              │
│  APIs          Podcasts       News         Reports/URLs     │
│  (PyPI, npm,   (8 feeds,     (5 RSS       (State of AI,    │
│  HuggingFace,  transcripts)  feeds)       Forbes AI 50,    │
│  OpenRouter,                              research, any    │
│  GitHub,                                  URL you paste)   │
│  Docker Hub)                                                │
└──────┬──────────────┬──────────────┬──────────────┬────────┘
       │              │              │              │
       ▼              ▼              ▼              ▼
┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐
│scrape_signals││scrape_podcast││news_monitor  ││monitor_source│
│   .py        ││   s.py       ││   .py        ││   s.py       │
│              ││              ││              ││classify_sourc│
│Daily 7am     ││Wed 10am      ││Daily 8am     ││   e.py       │
│              ││              ││              ││Daily 11:30am │
└──────┬───────┘└──────┬───────┘└──────┬───────┘└──────┬───────┘
       │               │               │               │
       ▼               ▼               ▼               ▼
┌──────────────────────────────────────────────────────────────┐
│                    RAW DATA LAYER                             │
│                                                              │
│  signals_latest.json    transcripts/*.md    news_alerts.json │
│  signals_YYYY-MM-DD     (8 source dirs)     source extracts  │
│  signals_history.jsonl                                       │
└──────────────────────────────────────────────────────────────┘
       │                      │
       ▼                      ▼
┌──────────────┐    ┌──────────────────────────────────────────┐
│auto_update.py│    │           CLAIM EXTRACTION               │
│              │    │                                          │
│Daily 7am     │    │  Bulk pipeline (cron, broad coverage):   │
│Updates:      │    │  extract_claims.py    Wed 10:45am        │
│- dashboard   │    │  enrich_vault.py      Daily 11am         │
│- site-data   │    │  monitor_sources.py   Daily 11:30am      │
│- apply_claims│    │                                          │
└──────┬───────┘    │  Curated intake (manual, focused):       │
       │            │  curated_intake.py    on-demand (wq-083) │
       │            │  → URL or stdin → Opus comparison →      │
       │            │    matches/updates/conflicts/new/context │
       │            └──────────────┬───────────────────────────┘
       │                           │
       ▼                           ▼
┌──────────────────────────────────────────────────────────────┐
│                  CLAIM PIPELINE                               │
│                                                              │
│  data-updates/*-candidates.json                              │
│  Each claim has: entity, metric, value, weight, confidence,  │
│  source, speaker, dedup_status                               │
│                                                              │
│  Weight tiers:                                               │
│  ┌─────────────────┐ ┌───────────────────┐ ┌──────────────┐ │
│  │ AUTHORITATIVE   │ │ CORROBORATING     │ │ INDICATIVE   │ │
│  │ First-hand      │ │ Cites named       │ │ Market       │ │
│  │ knowledge       │ │ primary source    │ │ colour,      │ │
│  │ (CEO on own ARR)│ │ (earnings call)   │ │ estimates    │ │
│  │ CAN override    │ │ CAN raise conf.   │ │ NEVER        │ │
│  │ existing data   │ │ or add new        │ │ overrides    │ │
│  └─────────────────┘ └───────────────────┘ └──────────────┘ │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                  HUMAN REVIEW GATE                            │
│                                                              │
│  claims.html — Accept / Decline / Park each claim            │
│                                                              │
│  Impact preview: shows what changes in site-data.json        │
│  Safety gate: changes >15% require explicit confirmation     │
│  Downloads approved-claims.json → picked up by next cron     │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                  AUTHORITATIVE DATA STORES                    │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────────────────────┐  │
│  │ site-data.json   │  │ vault-data.json                  │  │
│  │                  │  │                                  │  │
│  │ What the public  │  │ Full provenance for every claim: │  │
│  │ sees:            │  │ source URL, author, confidence,  │  │
│  │ - Provider ARR   │  │ date, weight, metric key         │  │
│  │ - Token volumes  │  │                                  │  │
│  │ - Top consumers  │  │ 42 accepted data points          │  │
│  │ - Timeline data  │  │ (and growing with each review)   │  │
│  │ - Sankey flows   │  │                                  │  │
│  └────────┬─────────┘  └──────────────────────────────────┘  │
│           │                                                   │
│  ┌────────┴─────────┐  ┌──────────────────────────────────┐  │
│  │ sources-registry │  │ companies.json                   │  │
│  │ .json            │  │                                  │  │
│  │ 10 sources with  │  │ 25 companies with funding,       │  │
│  │ type, method,    │  │ contacts, enrichment data        │  │
│  │ frequency,       │  │                                  │  │
│  │ next check date  │  │ Updated weekly by enrich.py      │  │
│  └──────────────────┘  └──────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                  PUBLIC PAGES                                 │
│                                                              │
│  Dashboard    Follow the $    Time Machine    Live Pricing   │
│  (provider    (Sankey:        (quarterly      (OpenRouter    │
│  cards,       $15/$1 ratio,   revenue/token   gateway        │
│  charts,      revenue flows,  animation,      comparison,    │
│  consumers)   Editor's View)  what-changed)   model prices)  │
│                                                              │
│  Subsidy Clock   Predictions   IPO Watch   Benchmarks       │
│  (live ticker,   (10 dated     (12 pre-    (input your      │
│  $711M/day)      forecasts)    IPO cos)    ARR → rank)      │
│                                                              │
│  Weekly Feed                                                 │
│  (parked; Formspree decommissioned wq-034 — signup via       │
│   hepburnadvisory.com.au/contact/?subscribe=ledger)          │
└──────────────────────────────────────────────────────────────┘

                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                  RECONCILIATION (feedback loop)               │
│                                                              │
│  reconcile.py (Wed 10:30am)                                  │
│                                                              │
│  Compares: claim ARR → COGS ratio → implied tokens           │
│  vs: current site-data.json token estimates                  │
│                                                              │
│  Flags: "Lovable ARR changed $75M→$400M, tokens should be   │
│  100B not 20B" → feeds back into claim pipeline              │
└──────────────────────────────────────────────────────────────┘
```

---

## The 4 Data Stores (and what each is for)

| Store | What | Who writes | Who reads | How often |
|-------|------|-----------|-----------|-----------|
| **site-data.json** | What the public sees — provider ARR, token volumes, timeline, Sankey flows, consumer list | `auto_update.py`, `apply_claims.py` | All public HTML pages | Daily (signals), weekly (claims) |
| **vault-data.json** | Source-of-truth claims with full provenance — the evidence behind every number | `apply_claims.py`, `enrich_vault.py` | `vault.html` (admin) | As claims are accepted |
| **sources-registry.json** | What to monitor, how to extract, how often to check | `classify_source.py`, `monitor_sources.py` | `monitor_sources.py`, `sources.html` | As you add sources |
| **companies.json** | Company enrichment data (funding, contacts, GitHub stats) | `enrich.py` | `newsletter.py`, admin pages | Weekly |

---

## Adding a New Data Point (4 paths)

### Path 1: Automated bulk (podcast/signal — zero effort)
```
Cron scrapes podcast → Claude extracts claims → claims.html review → Accept → site-data.json updated
```

### Path 2: Quick Add (paste a URL — 10 seconds)
```
Vault Quick Add → paste URL → auto-classify → Add Source → monitor_sources.py extracts → claims pipeline
```

### Path 3: Curated intake (editorial source, on-demand — wq-083)
```
curated_intake.py --url ... --slug ...   (or pipe text)
  → loads ledger position (entities + schema + providers)
  → Opus compares source against ledger
  → writes data-updates/<date>-curated-<slug>.json + curated-index.json
  → claims.html merges into review queue
  → Accept → site-data.json updated
```
Use this for newsletters (Zitron etc.), earnings releases, analyst reports —
where the value is "what does this source change about what we know?" rather
than blind extraction. Output classifies each claim as
`matches | updates | conflicts | new | context`. Slow path: bulk pipeline is
broad and noisy; curated is focused and fast.

### Path 4: Manual (direct edit — for corrections)
```
Edit site-data.json directly → git commit → live
```

---

## Source Classification (what happens when you paste a URL)

| URL Pattern | Detected Type | Extraction | Check Frequency |
|-------------|--------------|------------|-----------------|
| `docs.google.com/presentation` | Slide deck | PDF export → Claude | Annual |
| `*.pdf` | PDF report | Download → text → Claude | One-time |
| `*.substack.com` | Newsletter | RSS monitoring | Weekly |
| `twitter.com/*/status/*` | Social thread | Thread unroll → Claude | One-time |
| `youtube.com/watch` | Video | YouTube captions | One-time |
| `sec.gov` | SEC filing | Filing text → Claude | Quarterly |
| `github.com/org/repo` | GitHub repo | API → stars/releases | Weekly |
| `bloomberg.com`, `wsj.com` | News article | Fetch HTML → Claude | One-time |
| `gartner.com`, `mckinsey.com` | Research report | Web extract → Claude | Quarterly |
| RSS feed (auto-detected) | RSS feed | Monitor + extract | Weekly |

---

## Daily Schedule

| Time | Script | What happens |
|------|--------|-------------|
| 7:00am | `auto_update.py` | Signal scrape → dashboard update → apply pending claims → push |
| 7:30am | `sync_ideas.py` | Project Ideas folder → In Development page |
| 8:00am | `news_monitor.py` | RSS keyword alerts |
| 11:00am | `enrich_vault.py` | Claude enriches Quick Add URLs |
| 11:30am | `monitor_sources.py` | Check registry, extract due sources |

## Weekly Schedule

| Day | Time | Script | What happens |
|-----|------|--------|-------------|
| Mon | 9:00am | `enrich.py` + `newsletter.py` | Company enrichment + HTML brief |
| Wed | 10:00am | `scrape_podcasts.py` | Transcripts from 8 sources |
| Wed | 10:30am | `reconcile.py` | Flag stale estimates |
| Wed | 10:45am | `extract_claims.py --auto-pr` | Claude extracts claims → PR |

---

## Cost

| Process | Frequency | Est. cost |
|---------|-----------|-----------|
| Claim extraction (podcasts) | Weekly | $0.10-0.30 |
| Vault URL enrichment | Per URL | $0.02-0.05 |
| Source monitor extractions | Per source | $0.02-0.10 |
| **Total** | **Monthly** | **~$8-15** |
