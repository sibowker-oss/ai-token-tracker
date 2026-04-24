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
| 2026-04-23 | `data/company-alias-map.json` | (absent) | 31 validation-set entries + 22 known ATS tokens | New alias map for Stream 3 entity resolution per wq-013 §12.2. Seeded from §6 validation set. patent_assignee_ids empty — populate via PatentsView lookup follow-up. 9 ATS tokens unknown; Simon confirms. | n/a | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[*].next_check` | `2026-05-23` | `2026-04-23` | Reversed the Phase 2–4 review-budget gate. 24 sources reset to today so the daily 11:30am cron picks them up at their own registered cadence (daily/weekly/monthly/quarterly). Affects src-011, 025, 032, 037, 038, 041, 045, 055–059, 060–064, 065, 067, 068, 069, 070, 071, 072. Also: `process_source()` now appends extracted claims to `<date>-candidates.json` (free-text) and `<date>-structured-candidates.json` (typed) so claims.html picks them up automatically. Per-source audit snapshot at `<date>-source-<id>.json` retained. | 24 sources | Simon | Simon | _(this commit)_ |
| 2026-04-24 | `sources-registry.json[src-053].status` | `pending_first_extraction` | `deprecated_duplicate` | Duplicate of src-052 (both point at nextplatform.com `coreweave-takes-as-much-financial-engineering...`). Same §3.1 pattern as src-017..022 — canonical winner is src-052, deprecated row preserved never-deleted. Per wq-015 Phase 2 housekeeping. | src-053 | agent:stream-1-activation-monitor@0.1.0 | Simon | _(this commit)_ |
| 2026-04-24 | `sources-registry.json[src-016]` | pending_first_extraction | active, last_claims_count=30 | First extraction via `monitor_sources.py` (web_extract). 30 free-text claims appended to vault-inbox.json; audit snapshot at `data-updates/2026-04-24-source-src-016.json`; raw HTML at `data/snapshots/src-016/2026-04-24/`. | src-016 | agent:stream-1-activation-monitor@0.1.0 | Simon | _(this commit)_ |
| 2026-04-24 | `sources-registry.json[src-023]` | pending_first_extraction | active, last_claims_count=42 | First extraction (apoorv03 economics of AI). 42 claims to vault-inbox. | src-023 | agent:stream-1-activation-monitor@0.1.0 | Simon | _(this commit)_ |
| 2026-04-24 | `sources-registry.json[src-026]` | pending_first_extraction | active, last_claims_count=0 | First extraction (Alphabet IR). 0 claims — landing page returns only 1.5KB of shell HTML; real capex lives behind JS-loaded earnings tabs. Follow-up: ir_page_extract v2 needs to follow PDF links to earnings slides (noted in adapter docstring). Page snapshot captured regardless. | src-026 | agent:stream-1-activation-monitor@0.1.0 | Simon | _(this commit)_ |
| 2026-04-24 | `sources-registry.json[src-027]` | pending_first_extraction | active, last_claims_count=0 | First extraction (Microsoft IR). 0 claims — 5KB shell; same JS-loaded-earnings issue as src-026. Follow-up: PDF-slide follow. | src-027 | agent:stream-1-activation-monitor@0.1.0 | Simon | _(this commit)_ |
| 2026-04-24 | `sources-registry.json[src-028]` | pending_first_extraction | active, last_claims_count=4 | First extraction (NVIDIA IR). 4 data-center revenue / capex commentary claims. | src-028 | agent:stream-1-activation-monitor@0.1.0 | Simon | _(this commit)_ |
| 2026-04-24 | `sources-registry.json[src-029]` | pending_first_extraction | active, last_claims_count=16 | First extraction (AMD IR). 16 claims — DC GPU commentary, MI300 revenue. | src-029 | agent:stream-1-activation-monitor@0.1.0 | Simon | _(this commit)_ |
| 2026-04-24 | `sources-registry.json[src-030]` | pending_first_extraction | active, last_claims_count=0 | First extraction (Salesforce IR). 0 claims — 2.7KB shell; AgentForce metrics live behind JS. Follow-up: PDF-slide follow. | src-030 | agent:stream-1-activation-monitor@0.1.0 | Simon | _(this commit)_ |
| 2026-04-24 | `sources-registry.json[src-031]` | pending_first_extraction | active, last_claims_count=0 | First extraction (ServiceNow IR). 0 claims — 2.6KB shell. Follow-up: PDF-slide follow. | src-031 | agent:stream-1-activation-monitor@0.1.0 | Simon | _(this commit)_ |
| 2026-04-24 | `sources-registry.json[src-033]` | pending_first_extraction | active, last_claims_count=53 | First extraction (Sacra — Anthropic deep dive). 53 claims. | src-033 | agent:stream-1-activation-monitor@0.1.0 | Simon | _(this commit)_ |
| 2026-04-24 | `sources-registry.json[src-034]` | pending_first_extraction | active, last_claims_count=63 | First extraction (Sacra — OpenAI deep dive). 63 claims. | src-034 | agent:stream-1-activation-monitor@0.1.0 | Simon | _(this commit)_ |
| 2026-04-24 | `sources-registry.json[src-035]` | pending_first_extraction | active, last_claims_count=33 | First extraction (Sacra — Cursor deep dive). 33 claims. | src-035 | agent:stream-1-activation-monitor@0.1.0 | Simon | _(this commit)_ |
| 2026-04-24 | `sources-registry.json[src-036]` | pending_first_extraction | active, last_claims_count=26 | First extraction (Sacra — Perplexity deep dive). 26 claims. | src-036 | agent:stream-1-activation-monitor@0.1.0 | Simon | _(this commit)_ |
| 2026-04-24 | `sources-registry.json[src-039]` | pending_first_extraction | active, last_claims_count=0 | First extraction (a16z AI essays). 0 claims — 19KB fetched but the page is the essay-index, no extractable data points without following essay links. Follow-up: depth-1 link-follow adapter. | src-039 | agent:stream-1-activation-monitor@0.1.0 | Simon | _(this commit)_ |
| 2026-04-24 | `sources-registry.json[src-040]` | pending_first_extraction | active, last_claims_count=0 | First extraction (Sequoia articles). 0 claims — HTTP 404 on registered URL. URL rot. Follow-up: replace with `https://www.sequoiacap.com/` or `/article/` (plural → singular). | src-040 | agent:stream-1-activation-monitor@0.1.0 | Simon | _(this commit)_ |
| 2026-04-24 | `sources-registry.json[src-042]` | pending_first_extraction | active, last_claims_count=0 | First extraction (CAC — Cyberspace Administration of China). 0 claims on Chinese-prompt path — landing page returns only directory links; the algorithm-registration tables live at child paths. Follow-up: register deep-link(s) to `algorithmRegistration/...` index as separate sources. | src-042 | agent:stream-1-activation-monitor@0.1.0 | Simon | _(this commit)_ |
| 2026-04-24 | `sources-registry.json[src-043]` | pending_first_extraction | active, last_claims_count=0 | First extraction (Stanford AI Index). 0 claims — 7.5KB landing page, no real data until a specific report-chapter URL. Follow-up: switch to chapter-wise PDF adapter path. | src-043 | agent:stream-1-activation-monitor@0.1.0 | Simon | _(this commit)_ |
| 2026-04-24 | `sources-registry.json[src-044]` | pending_first_extraction | active, last_claims_count=0 | First extraction (Europarl EU AI Act page). 0 claims — single article, no quantitative data points Claude could extract. Reinforces wq-015 §2.3 decision: FLI (src-055) is the primary; europarl stays as corroboration. | src-044 | agent:stream-1-activation-monitor@0.1.0 | Simon | _(this commit)_ |
| 2026-04-24 | `sources-registry.json[src-046]` | pending_first_extraction | active, last_claims_count=0 | First extraction (SimilarWeb AI rankings). 0 claims — HTTP 404. SimilarWeb appears to have removed or restructured this taxonomy page. Follow-up: Simon to confirm new URL or deprecate. | src-046 | agent:stream-1-activation-monitor@0.1.0 | Simon | _(this commit)_ |
| 2026-04-24 | `sources-registry.json[src-047]` | pending_first_extraction | active, last_claims_count=4 | First extraction (PyPI Stats — OpenAI SDK). 4 claims. | src-047 | agent:stream-1-activation-monitor@0.1.0 | Simon | _(this commit)_ |
| 2026-04-24 | `sources-registry.json[src-048]` | pending_first_extraction | active, last_claims_count=4 | First extraction (PyPI Stats — Anthropic SDK). 4 claims. | src-048 | agent:stream-1-activation-monitor@0.1.0 | Simon | _(this commit)_ |
| 2026-04-24 | `sources-registry.json[src-049]` | pending_first_extraction | active, last_claims_count=4 | First extraction (PyPI Stats — Google GenAI SDK). 4 claims. | src-049 | agent:stream-1-activation-monitor@0.1.0 | Simon | _(this commit)_ |
| 2026-04-24 | `sources-registry.json[src-052]` | pending_first_extraction | active, last_claims_count=30 | First extraction (Coreweave data points — nextplatform.com). 30 claims. Canonical winner of the src-052/053 dedupe. | src-052 | agent:stream-1-activation-monitor@0.1.0 | Simon | _(this commit)_ |
| 2026-04-24 | `sources-registry.json[src-054]` | pending_first_extraction | active, last_claims_count=4 | First extraction (Platformonomics — Hyperscaler CapEx Tracker). 4 claims. Thin landing page — most substance lives in individual posts. Follow-up: post-level fetch. | src-054 | agent:stream-1-activation-monitor@0.1.0 | Simon | _(this commit)_ |
