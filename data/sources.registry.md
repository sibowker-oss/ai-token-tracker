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

---

## Rules

1. Every source cited in `site-data.json` **must** appear here before the entry goes live (§11.2).
2. Sources are **never deleted** from this file. If a source is retired, mark `cadence = "retired"` and add a `retiredOn` note in `notes`. Past values still need their provenance traceable.
3. When adding a new source, prefer tier 1 (primary). Tier 3 entries require a note explaining why no tier 1 or 2 is available.
4. Tier downgrades (e.g. a primary source becomes unreachable and we fall back to a secondary) must be logged in `sources.log.md`, not silently in this file.
