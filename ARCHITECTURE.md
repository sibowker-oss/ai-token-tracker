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
│                                                              │
│  Triangulations (wq-086): claims with comparison_type=       │
│  "triangulates" follow a parallel apply path —               │
│  see §Apply: Triangulation path below.                       │
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
  → builds FLOW MODEL context (revenue flow + capex flow + entity
    positions w/ provenance confidence + composition rules) — ~5k tokens
  → Opus reasons about source against the flow model, including
    arithmetic-derived triangulations against named ledger nodes
  → writes data-updates/<date>-curated-<slug>.json + curated-index.json
  → claims.html merges into review queue (with derivation surfaced inline)
  → Accept → site-data.json updated
```
Use this for newsletters (Zitron etc.), earnings releases, analyst reports —
where the value is "what does this source change about what we know?" rather
than blind extraction. Output classifies each claim as
`matches | updates | conflicts | new | triangulates | context`.

The **flow model** distinguishes this path from bulk extraction. Instead of
matching claims to fields by lookup, the model receives the structural shape
of the ledger (Sankey trees + composition rules like
"Customer Revenue (gross) = Consumer + SME + Enterprise") and reasons about
where a novel claim fits. Claims that use a different framework than our
schema (e.g. "Enterprise GenAI market = $37B" vs our segment splits) are
connected through arithmetic — `triangulates` claims must include a
`derivation` equation referencing specific named nodes
(e.g. `sankey.buyers.Enterprise + sankey.buyers.SME + market.2025.enterprise_capex`)
or they get reclassified to `context`. Slow path: bulk pipeline is broad and
noisy; curated is focused and fast.

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

---

## Apply: Triangulation path (wq-086)

Curated intake (`curated_intake.py`, wq-083 v2) emits `triangulates` claims —
indirect arithmetic against ledger nodes (e.g. "Menlo says Enterprise GenAI =
$37B; our buyer-segment + capex sum is $28.9B"). These don't fit the direct
`entity_match_rules` matcher because the source `entity` is a market segment
("Enterprise Generative AI Market"), not a real ledger entity. They route via
a parallel apply branch keyed on `target_nodes` paths.

```
claims.html [Accept]                     data/triangulations-pending.json
       │                                              ▲
       ▼                                              │ soft-park (commit 1)
review-decisions-{date}.json   ──►  apply_decisions.py
                                              │
                     ┌────────────────────────┼────────────────────────┐
                     ▼                        ▼                        ▼
            (existing direct path)   (NEW triangulation path)   (existing decline/park)
                     │                        │
                     ▼                        ▼
            entities.json (entity-keyed)   entities.json (target_node-keyed)
            provenance: role=supports     provenance: role=triangulates
                                          + confidence_impact, derivation
```

**Apply semantics** (per
`docs/decisions/resolved/dec-2026-05-05-triangulation-apply-semantics.md`):

- **Option B**: triangulations append provenance entries to every field named
  in `target_nodes` but never mutate values. Numbers stay direct-claim-only.
- **Confidence weights**: `strengthens=+0.5`, `widens_range=+0.25`,
  `weakens=-0.25`. Triangulations alone can lift `low → medium`; they cannot
  lift `medium → high` (cap reserved for direct evidence).
- **`needs_review` flag**: ≥2 weakens against the same field (does not
  downgrade tier on its own — flagged in vault.html for editorial review).
- **Reviewer override**: claims.html lets the reviewer flip
  `confidence_impact` at accept time. The accepted value is what gets
  written to provenance; the model's classification is preserved as
  `model_classified_as` when overridden.

**Routing** — `resolve_target_node(path, claim_year)` maps flow-model paths
to concrete (entities.market_aggregates | entities.companies[slug]) targets:

| path                           | resolves to                                              |
|--------------------------------|----------------------------------------------------------|
| `market.<year>.<field>`        | `market_aggregates[year][field]`                          |
| `sankey.buyers.<Segment>`      | `market_aggregates[year].total_segment_<seg>`             |
| `sankey.providers.<slug>`      | `companies[slug].financials[year].arr`                    |
| `capex.<bucket>.<key>`         | `market_aggregates[year].<bucket>_capex`                  |
| `<slug>.<year>.<field>`        | `companies[slug].financials[year][field]`                 |
| `<slug>.current.<field>`       | `companies[slug].current[field]`                          |
| `<slug>` (bare)                | `companies[slug].financials[year].arr` (fallback)         |

`sankey.channels.*` and `sankey.outcomes.*` are computed aggregates with no
stable provenance home — the resolver returns `None` and the entry is
skipped with a logged counter.

**Drain cycle** — every `apply_decisions.py` invocation (with or without a
fresh decisions file) runs `replay_triangulations_pending(entities)`. Soft-
parked entries get applied; on a clean drain the pending file moves to
`data/triangulations-pending.json.replayed-<ts>.bak`. Entries with
unresolvable target_nodes stay in a residual pending file for retry.

**Surfaces** — `vault.html` has a Triangulations tab listing every
role=triangulates entry by (entity, prov_key) with violet accent and
`needs_review` banner. `source-ledger.html` shows pending + applied
triangulations as a panel above the per-source ledger.
