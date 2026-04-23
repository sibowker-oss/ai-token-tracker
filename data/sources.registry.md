# Sources Registry

**Purpose:** Authoritative list of every external source used by The AI Ledger. Per GUIDELINES §5.4, every data source that feeds `site-data.json` must be registered here.

**Maintained by:** Simon / Hepburn Advisory
**Last updated:** 2026-04-23

---

## Columns

| Field | Meaning |
|---|---|
| `id` | Short stable identifier used in `site-data.json` entries |
| `name` | Issuing body / publisher (human-readable) |
| `tier` | Per GUIDELINES §4.3: **1** primary machine-readable, **2** secondary authoritative, **3** tertiary event-driven |
| `url` | Root URL for the source (not the per-datapoint link — that lives on the datapoint) |
| `handler` | Agent or person responsible for fetch/review |
| `cadence` | Review frequency. Match the scanner enum: `daily` / `weekly` / `monthly` / `quarterly` / `annual` / `one_time`. If the source is already in `sources-registry.json` (the daily scanner's source list), mirror its `frequency` value. |
| `licence` | Usage terms / attribution requirements |
| `method` | How data is fetched (API, scraper, manual copy, CSV download) |
| `addedOn` | ISO date registered |
| `notes` | Caveats, scope, limits |

---

## Registry

| id | name | tier | url | handler | cadence | licence | method | addedOn | notes |
|---|---|---|---|---|---|---|---|---|---|
| wb-imf-weo | World Bank / IMF WEO | 1 | https://www.imf.org/external/datamapper/NGDPD@WEO | Simon | quarterly | Public data, attribution required | manual copy | 2026-04-23 | Nominal global GDP reference. IMF WEO revised April/October. |
| wb-national-accounts | World Bank national accounts | 1 | https://data.worldbank.org/indicator/NV.SRV.TOTL.CD | Simon | annual | CC BY 4.0 | manual copy | 2026-04-23 | Services share of GDP. |
| ilo-oecd-wages | ILO Global Wage Report / OECD | 1 | https://www.ilo.org/global/research/global-reports/global-wage-report | Simon | annual | Public, attribution required | manual copy | 2026-04-23 | Global labour compensation. Wage Report itself biennial; annual enum covers intervening stat releases. |
| ilo-mckinsey-mgi | ILO / McKinsey Global Institute | 2 | https://www.mckinsey.com/mgi/our-research | Simon | annual | Report-level attribution | manual copy | 2026-04-23 | Knowledge-worker wage bill. MGI reports derived, not primary. |
| gartner-it-spend | Gartner IT Spending Forecast | 2 | https://www.gartner.com/en/newsroom/press-releases | Simon | quarterly | Press-release excerpts only; full report paywalled | manual copy | 2026-04-23 | Total global IT spend. Headline numbers only — never quote paywalled detail. |
| gartner-idc | Gartner / IDC | 2 | https://www.gartner.com/en/newsroom/press-releases | Simon | quarterly | Press-release excerpts | manual copy | 2026-04-23 | Enterprise software market size. |
| synergy-gartner-cloud | Synergy Research / Gartner | 2 | https://www.srgresearch.com | Simon | quarterly | Press-release excerpts | manual copy | 2026-04-23 | SaaS and public-cloud market sizing. |
| groupm-warc | GroupM / WARC | 2 | https://www.groupm.com/this-year-next-year | Simon | annual | Report summaries | manual copy | 2026-04-23 | Global ad market. This Year Next Year drops twice/yr but annual is close enough for governance cadence. |
| edgar-10k-hyperscaler | Company 10-K filings (MSFT, GOOG, AMZN, META, ORCL) | 1 | https://www.sec.gov/cgi-bin/browse-edgar | Simon | quarterly | Public (EDGAR), no restriction | manual copy | 2026-04-23 | Hyperscaler capex roll-up. Recompute each quarter from filed 10-Qs / 10-Ks. |
| sp-global | S&P Global | 1 | https://www.spglobal.com/spdji/en/indices/equity/sp-500 | Simon | daily | Public headline data; constituent detail paywalled | manual copy | 2026-04-23 | S&P 500 aggregate market cap. Headline index value publishes daily. |
| bea-imf-weo | BEA / IMF WEO | 1 | https://www.bea.gov/data/gdp/gross-domestic-product | Simon | quarterly | Public data | manual copy | 2026-04-23 | US GDP. BEA advance/second/third estimates. |
| fli-eu-ai-act | Future of Life Institute — EU AI Act Tracker | 1 | https://artificialintelligenceact.eu/ | Simon | monthly | CC-licensed | web_extract | 2026-04-23 | Primary EU AI Act status tracker per wq-015 §2.3. Mirrored as `src-055` in sources-registry.json. Pending first extraction. |
| sec-edgar-ai-scan | SEC EDGAR — AI company 10-K/10-Q/8-K scan | 1 | https://www.sec.gov/cgi-bin/browse-edgar | Simon | quarterly | Public (EDGAR) | sec_edgar_scan | 2026-04-23 | Broadened from OpenAI-only (was `src-025`). Scans tickers in `data/edgar-tickers.json` (seed 15). |
| alibaba-ir | Alibaba Group — Investor Relations | 1 | https://www.alibabagroup.com/en-US/ir | Simon | quarterly | Public | ir_page_extract | 2026-04-23 | Chinese hyperscaler IR per wq-015 §2.4. `src-056`. |
| tencent-ir | Tencent Holdings — Investor Relations | 1 | https://www.tencent.com/en-us/investors.html | Simon | quarterly | Public | ir_page_extract | 2026-04-23 | Chinese hyperscaler IR per wq-015 §2.4. `src-057`. |
| baidu-ir | Baidu — Investor Relations | 1 | https://ir.baidu.com/ | Simon | quarterly | Public | ir_page_extract | 2026-04-23 | Chinese hyperscaler IR per wq-015 §2.4. Ernie/Wenxin commentary. `src-058`. |
| bytedance-press | ByteDance — Corporate Newsroom | 2 | https://www.bytedance.com/en/news | Simon | monthly | Public | web_extract | 2026-04-23 | ByteDance is private (no IR). Press room used as canonical endpoint per wq-015 §2.4. `src-059`. Re-evaluate if ByteDance IPOs. |
| ercot-gis | ERCOT GIS + Large Load Integration | 1 | https://www.ercot.com/mp/data-products/data-product-details?id=pg7-200-er | Simon | monthly | Public (ERCOT) | iso_queue_ercot | 2026-04-23 | Largest US AI-DC concentration per wq-012 §1. XLSX monthly. `src-060`. |
| pjm-queue | PJM New Services Queue | 1 | https://www.pjm.com/planning/services-requests/interconnection-queues | Simon | quarterly | Public (PJM) | iso_queue_pjm | 2026-04-23 | 32 GW load forecast, ~30 GW DC. Post-2025 co-location rule forces end-customer naming. Pair with Virginia DEQ + SCC. `src-061`. |
| eia-api | EIA API (860M / 930 / STEO) | 1 | https://www.eia.gov/opendata/ | Simon | daily | Public domain | eia_api | 2026-04-23 | Requires `EIA_API_KEY` env var. STEO now explicitly attributes DC load. `src-062`. |
| neso-tec | NESO TEC Register (UK) | 1 | https://www.neso.energy/data-portal/transmission-entry-capacity-tec-register | Simon | weekly | OGL | neso_tec | 2026-04-23 | Twice-weekly upstream (Tue/Fri) — weekly at Ledger level. Gate 1 / Gate 2 classifier from Nov 2025. `src-063`. |
| epoch-frontier-dc | Epoch AI — Frontier Data Centers Hub | 2 | https://epoch.ai/data/data-centers | Simon | monthly | CC-BY | epoch_frontier | 2026-04-23 | Primary source for LLC → AI-lab attribution map. Seeds `data/datacenter-attribution-map.json`. `src-064`. |
| uspto-patentsview | USPTO PatentSearch API | 1 | https://search.patentsview.org/api/v1/patent/ | Simon | monthly | Public (USPTO) | patentsview_search | 2026-04-23 | Rate-limited REST. CPC filter per wq-013 §10. `src-065`. |
| google-patents-bq | Google Patents BigQuery | 1 | https://github.com/google/patents-public-data | Simon | monthly | Google Cloud ToS | google_patents_bq | 2026-04-23 | STUBBED — requires GCP credentials. International patent coverage (CN/EU). `src-066`. |
| epo-ops | EPO Open Patent Services | 1 | https://ea.espacenet.com/ | Simon | monthly | EPO OPS Fair Use Charter | epo_ops | 2026-04-23 | Free to 250 req/week. Env-gated on `EPO_OPS_CLIENT_ID` / `_SECRET`. `src-067`. |
| dol-oflc-lca | DoL OFLC LCA quarterly disclosure | 1 | https://www.dol.gov/agencies/eta/foreign-labor/performance | Simon | quarterly | Public | dol_lca_xlsx | 2026-04-23 | AI-engineer regex filter per wq-013 §9. XLSX. Requires openpyxl. `src-068`. |
| ats-greenhouse | Greenhouse Job Board API | 2 | https://boards-api.greenhouse.io/v1/boards/ | Simon | weekly | Public | greenhouse_board | 2026-04-23 | Public JSON per-company-token. `src-069`. |
| ats-lever | Lever Postings API | 2 | https://api.lever.co/v0/postings/ | Simon | weekly | Public | lever_postings | 2026-04-23 | Public JSON per-company-slug. `src-070`. |
| ats-ashby | Ashby Public Job Posting API | 2 | https://api.ashbyhq.com/posting-api/job-board/ | Simon | weekly | Public | ashby_public | 2026-04-23 | Public JSON per-company-token. `src-071`. |
| ats-workable | Workable Jobs widget API | 2 | https://apply.workable.com/api/v1/widget/accounts/ | Simon | weekly | Public | workable_jobs | 2026-04-23 | Public widget JSON per-account. `src-072`. |

## Deferred (paid or out-of-scope for wq-015)

| id | name | status | reason |
|---|---|---|---|
| seeking-alpha | Seeking Alpha — AI earnings transcripts (`src-024`) | deferred | Full transcripts paywalled per wq-015 §2.6. |
| crunchbase-ai | Crunchbase — Top AI companies (`src-050`) | deferred | Held for paid-source budget review per wq-015 §9. |
| dealroom-ai | Dealroom — AI landscape (`src-051`) | deferred | Held for paid-source budget review per wq-015 §9. |

## Deprecated duplicates (per sources.registry.md rule 2, never deleted)

| id | supersededBy | deprecatedOn | reason |
|---|---|---|---|
| `src-017` → `src-022` | `src-016` | 2026-04-23 | All six rows pointed at the same OpenAI "Accelerating the Next Phase of AI" URL. Per wq-015 §3.1. |

---

## Rules

1. Every source cited in `site-data.json` **must** appear here before the entry goes live (§11.2).
2. Sources are **never deleted** from this file. If a source is retired, mark `cadence = "retired"` and add a `retiredOn` note in `notes`. Past values still need their provenance traceable.
3. When adding a new source, prefer tier 1 (primary). Tier 3 entries require a note explaining why no tier 1 or 2 is available.
4. Tier downgrades (e.g. a primary source becomes unreachable and we fall back to a secondary) must be logged in `sources.log.md`, not silently in this file.
