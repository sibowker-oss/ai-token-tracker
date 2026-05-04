# EDGAR tickers — deferred (no clean SEC-filing ADR)

_Last updated: 2026-05-04 (wq-081 Phase 1.1 source collation)._

These tickers were proposed in the Phase 1.1 brief (`source-collation-phase1-brief.md` §10) for inclusion in `data/edgar-tickers.json`, but verification against `https://www.sec.gov/files/company_tickers.json` on 2026-05-04 confirmed each is **not** an active SEC filer. Per the brief instruction — "If a foreign ticker has no clean EDGAR ADR, log it in `data/edgar-tickers-deferred.md` and skip — don't fabricate a ticker." — they are deferred here rather than added to the seed.

| Pseudo-ticker | Underlying entity | Listing | Why deferred | Alternative coverage path |
|---|---|---|---|---|
| `TCEHY` | Tencent Holdings (700.HK) | OTC pink sheets, Hong Kong primary | Sponsored ADR programme; Tencent does not file 10-K/10-Q/20-F/6-K with SEC | Already covered via `src-057` (Tencent IR page extract, quarterly cadence) |
| `SKHYY` | SK Hynix (000660.KS) | OTC pink sheets, KRX primary | Korean primary; no SEC filings | KRX disclosure portal (KIND) — future P2 candidate; not in Phase 1 |
| `SSNLF` | Samsung Electronics (005930.KS) | OTC pink sheets, KRX primary | Korean primary; no SEC filings | KRX disclosure portal (KIND) — future P2 candidate; not in Phase 1 |
| `SBGSY` | Schneider Electric (SU.PA) | OTC pink sheets, Euronext Paris primary | French primary; no SEC filings | AMF (Autorité des marchés financiers) URD documents — future P2 candidate; not in Phase 1 |
| `SMNEY` | Siemens Energy (ENR.DE) | OTC pink sheets, XETRA primary | German primary; no SEC filings | BaFin disclosure register — future P2 candidate; not in Phase 1 |

## What this means for coverage

- **Tencent**: covered by registry source `src-057` (IR page). No data gap.
- **SK Hynix / Samsung**: HBM supply commentary partially picked up via Micron (MU) earnings calls and SemiAnalysis (Phase 2 candidate per §10b). Direct primary source coverage requires KRX integration — out of Phase 1 scope.
- **Schneider Electric / Siemens Energy**: switchgear and turbine backlog commentary partially picked up via Vertiv (VRT), Eaton (ETN), and GE Vernova (GEV) earnings calls. Direct primary source coverage requires European disclosure-portal integration — out of Phase 1 scope.

## Re-evaluation triggers

Add to `edgar-tickers.json` only if any of the underlying entities files a Form 20-F or 6-K with SEC (which would change their `company_tickers.json` status). Periodic re-check cadence: annual, by the Phase 1.1 maintainer.
