# Sources Log

**Purpose:** Append-only log of every value update, source change, or provenance event on The AI Ledger. Per GUIDELINES §4.7 and §5.4, no value changes silently.

**Rules:**
- Append-only. Never edit or delete past entries.
- One row per value change or source event.
- If a change affects multiple fields, one row per field.
- Agent-driven updates: the agent name/version goes in `operator`; a human reviewer must still sign off before merge (§6.2).

---

## Columns

| Field | Meaning |
|---|---|
| `date` | ISO date (YYYY-MM-DD) of the change |
| `field` | Dotted path into `site-data.json` (e.g. `globalBenchmarks.entries[global_gdp].value`) |
| `priorValue` | Value before the change — `null` if new entry |
| `newValue` | Value after the change |
| `reason` | Why the change was made (new filing, quarterly refresh, correction, etc.) |
| `sourceId` | `id` from `sources.registry.md` |
| `operator` | Human name, or `agent:<name>@<version>` |
| `reviewer` | Human who approved the merge (required for agent changes) |
| `commit` | Git commit SHA after merge |

---

## Log

| date | field | priorValue | newValue | reason | sourceId | operator | reviewer | commit |
|---|---|---|---|---|---|---|---|---|
| 2026-04-23 | `power.projects` | (absent) | `[]` | Pre-seed for wq-014 structured claim target; non-destructive bootstrap so front-end can assume key exists. | _(n/a — schema bootstrap)_ | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `hiring.snapshots` | (absent) | `{}` | Pre-seed for wq-014 structured claim target. | _(n/a — schema bootstrap)_ | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `patents.snapshots` | (absent) | `{}` | Pre-seed for wq-014 structured claim target. | _(n/a — schema bootstrap)_ | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-017].status` | `pending_first_extraction` | `deprecated_duplicate` | Duplicate of src-016 (openai.com/index/accelerating-the-next-phase-ai/). Per wq-015 §3.1. | src-017 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-018].status` | `pending_first_extraction` | `deprecated_duplicate` | Duplicate of src-016. Per wq-015 §3.1. | src-018 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-019].status` | `pending_first_extraction` | `deprecated_duplicate` | Duplicate of src-016. Per wq-015 §3.1. | src-019 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-020].status` | `active` | `deprecated_duplicate` | Duplicate of src-016. Per wq-015 §3.1. | src-020 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-021].status` | `active` | `deprecated_duplicate` | Duplicate of src-016. Per wq-015 §3.1. | src-021 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-022].status` | `active` | `deprecated_duplicate` | Duplicate of src-016. Per wq-015 §3.1. | src-022 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-025].url` | `...company=openai&CIK=...` | `...company=&CIK=...` (broadened) | Scope broadened from OpenAI-only to multi-ticker scan driven by `data/edgar-tickers.json`. Per wq-015 §2.2. | src-025 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-024].status` | `pending_first_extraction` | `deferred` | Seeking Alpha deferred per wq-015 §2.6 — paywall. | src-024 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-050].status` | `pending_first_extraction` | `deferred` | Crunchbase deferred per wq-015 §9 — paid source, budget review. | src-050 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-051].status` | `pending_first_extraction` | `deferred` | Dealroom deferred per wq-015 §9 — paid source, budget review. | src-051 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-055]` | null | FLI EU AI Act Tracker (pending_first_extraction) | New source per wq-015 §2.3. Set `status=pending_first_extraction` and `next_check=2026-05-23` so daily cron does not auto-fire. | src-055 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-056]` | null | Alibaba Group IR (pending_first_extraction) | New Chinese hyperscaler IR per wq-015 §2.4. | src-056 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-057]` | null | Tencent Holdings IR (pending_first_extraction) | New Chinese hyperscaler IR per wq-015 §2.4. | src-057 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-058]` | null | Baidu IR (pending_first_extraction) | New Chinese hyperscaler IR per wq-015 §2.4. | src-058 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-059]` | null | ByteDance press room (pending_first_extraction) | New; ByteDance private so IR is substituted with corporate newsroom. Per wq-015 §2.4. | src-059 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `data/edgar-tickers.json` | (absent) | 16 seed tickers | New ticker-seed file for the broadened SEC EDGAR scan. Per wq-015 §2.2 and Phase 1 decision #9. | n/a | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-002].next_check` | 2026-04-02 | 2026-04-30 | Past-due cleanup (wq-015 §3.2). Extraction handled by `scrape_podcasts.py`, not `monitor_sources.py` — registry freshness is a hygiene bump, not a re-extraction. | src-002 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-003].next_check` | 2026-04-02 | 2026-04-30 | Past-due cleanup (wq-015 §3.2). Handled by `scrape_podcasts.py`. | src-003 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-004].next_check` | 2026-04-02 | 2026-04-30 | Past-due cleanup (wq-015 §3.2). Handled by `scrape_podcasts.py`. | src-004 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-005].next_check` | 2026-04-01 | 2026-04-24 | Past-due cleanup (wq-015 §3.2). Handled by `scrape_signals.py`. | src-005 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-006].next_check` | 2026-04-01 | 2026-04-24 | Past-due cleanup (wq-015 §3.2). Handled by `scrape_signals.py`. | src-006 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-007].next_check` | 2026-04-01 | 2026-04-24 | Past-due cleanup (wq-015 §3.2). Handled by `scrape_signals.py`. | src-007 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-011].next_check` | 2026-04-07 | 2026-05-23 | Past-due (pending_first_extraction since registration). Pushed per wq-015 Phase 2 posture — first extraction on manual trigger. Review for deprecation if dead. | src-011 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-032].next_check` | 2026-04-04 | 2026-05-23 | Past-due (Meta IR, pending_first_extraction). Pushed per wq-015 Phase 2 posture. | src-032 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-041].next_check` | 2026-04-04 | 2026-05-23 | Past-due (Bessemer Atlas). Pushed per wq-015 Phase 2 posture. | src-041 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-045].next_check` | 2026-04-19 | 2026-05-23 | Past-due (Cloudflare Radar). Pushed per wq-015 Phase 2 posture. | src-045 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-037].language` | null | `zh` | Tagged Chinese source for translation-aware extraction prompt per wq-015 §4. Next_check bumped from 2026-04-23 to 2026-05-23. | src-037 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-038].language` | null | `zh` | Tagged Chinese source. Next_check bumped from 2026-04-23 to 2026-05-23. | src-038 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-042].language` | null | `zh` | Tagged Chinese source (Cyberspace Administration of China). | src-042 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-060]` | null | ERCOT GIS + Large Load Integration (pending_first_extraction) | New Stream 2 power source per wq-012 §1. US primary ISO queue. | src-060 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-061]` | null | PJM New Services Queue (pending_first_extraction) | New Stream 2 power source per wq-012 §1. Post-2025 co-location rule. | src-061 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-062]` | null | EIA API 860M/930/STEO (pending_first_extraction) | New Stream 2 gov API per wq-012 §1. Free API key. | src-062 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-063]` | null | NESO TEC Register UK (pending_first_extraction) | New Stream 2 UK ISO queue per wq-012 §1. OGL licence, best cadence. | src-063 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-064]` | null | Epoch AI Frontier Data Centers Hub (pending_first_extraction) | New Stream 2 attribution dataset per wq-012 §1. CC-BY. Seeds `data/datacenter-attribution-map.json`. | src-064 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `data/datacenter-attribution-map.json` | (absent) | 36 `by_project` entries seeded from Epoch AI CSV | First real extraction against src-064. Full Epoch AI Frontier Data Centers table (36 facilities) seeded with multi-operator support. by_llc section empty, awaiting ISO-queue extractions. Per wq-012 §7.1. | src-064 | agent:stream-2-power-monitor@0.1.0 | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-065]` | null | USPTO PatentSearch API (pending_first_extraction) | New Stream 3 discovery source per wq-013 §3.1. Public REST API, CPC filter from §10. | src-065 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-066]` | null | Google Patents BigQuery (pending_credentials) | New Stream 3 discovery source per wq-013 §3.1. STUBBED pending GCP creds (Phase 1 decision #4). International patent coverage. | src-066 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-067]` | null | EPO OPS (pending_first_extraction) | New Stream 3 EU patent API per wq-013 §3.1. Requires OAuth registration. | src-067 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-068]` | null | DoL OFLC LCA quarterly (pending_first_extraction) | New Stream 3 hiring-intent source per wq-013 §3.2. Quarterly XLSX. | src-068 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-069]` | null | Greenhouse Job Board API (pending_first_extraction) | New Stream 3 ATS per wq-013 §3.6. Public JSON. | src-069 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-070]` | null | Lever Postings API (pending_first_extraction) | New Stream 3 ATS per wq-013 §3.6. | src-070 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-071]` | null | Ashby Public Job Posting API (pending_first_extraction) | New Stream 3 ATS per wq-013 §3.6. | src-071 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-072]` | null | Workable Jobs widget API (pending_first_extraction) | New Stream 3 ATS per wq-013 §3.6. | src-072 | Simon | Simon | _(this commit)_ |
