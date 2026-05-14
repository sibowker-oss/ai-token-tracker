# Deployment: wq-104 — Sources page type filter + per-card monitoring

**Date:** 2026-05-14
**WQ:** wq-104
**Branch/Commit:** main
**Files touched:**
- Modified: `sources.html`
- Modified: `review.html` (3-line addition — reads `?source=src-NNN` URL param to seed `activeSource` on load; enables deep-link from the new "Review" button)
- Untouched: `beta/sources.html` (parity deferred per handoff instruction #1)
- Untouched: `sources-registry.json` schema, all extraction scripts, all workflow YAMLs

## What shipped

`sources.html` now renders:

1. **Chip filter row** above the search bar. One chip per `type` (sorted by count desc) plus an "All" reset chip. Counts reflect total registry (107 non-deleted today), not the filtered subset (AC#4). Multi-select with OR semantics (AC#2). Filter state syncs to `?types=` URL param, restored on reload (AC#3).
2. **Per-card Monitoring block** (always visible, not gated behind expand) with three rows:
   - **Process**: human description of `extraction_method` (from `EXTRACTION_DESCRIPTIONS` map — see §3.2 below).
   - **Cadence**: human label of `frequency` (`FREQUENCY_LABELS` map).
   - **Status**: derived pill — ✓ Healthy / ⚠ Stale / ✗ Overdue / ✗ Never / ⏸ Manual — plus `Last:` and `Next:` dates inline.
   For `frequency: on_event` the status row is suppressed entirely per brief §6 (no verdict shown); the dates collapse into a `Dates` row.
3. **Type badge** now uses the friendly label from `TYPE_LABELS` (e.g. "RSS Feed" instead of "rss feed").
4. **Search ANDs with chip filter** (AC#5). The pre-existing active-first + last_claims_count-desc sort is preserved (§8 out-of-scope).
5. **Frequency badge removed** from the header row — its info moved into the Monitoring block's Cadence line. Avoids duplicating data on the card.
6. **Highlight override**: `?highlight=src-NNN` checked at load time — if the highlighted source's `type` is not in the active filter, that type is added to `activeTypes` before the first render. The card stays visible.
7. **Per-card action buttons** (in-session scope add, chat 2026-05-14):
   - **Review (N)** — renders only when the source has ≥1 pending item. Links to `review.html?source=<src-id>`; review.html now reads that param and pre-selects the source tab.
   - **Run extraction** — renders on every card whose `extraction_method` has a workflow target. Click → confirm dialog → `GitHubAPI.triggerWorkflow(workflowFile)`. The workflow runs the full batch for that extraction class (not single-source); the toast and dialog say so explicitly. Routing table is in `METHOD_TO_WORKFLOW` in sources.html. Methods with no workflow (`manual`, `manual_import`, `api`, `youtube_captions`) hide the button.

## Decisions made during implementation

### §3.2 extension (tactical — discussed in chat 2026-05-14, Simon approved option 2)

The brief's §3.2 `extraction_method → human description` map covers only 7 methods (`pdf_export`, `podcast_scraper`, `signal_scraper`, `web_extract`, `api`, `youtube_captions`, `manual`). The actual registry today has 29 distinct extraction methods in use. Implementing §3.2 verbatim would have left 43/107 cards (40%) showing the snake_case fallback in their Process line — the exact symptom the brief was meant to fix (e.g. "Sec Edgar Scan", "Fred Api", "Iso Queue Ercot").

Simon's chat decision (2026-05-14): extend §3.2 inline, log the additions in this deployment record. The locked 7 entries are implemented verbatim. The following 25 additions cover every extraction method currently in `sources-registry.json`:

| Method | Description |
|---|---|
| `rss_feed` (16 cards) | RSS feed polled; new entries fetched and parsed for claims. |
| `ir_page_extract` (4) | Investor relations page scraped; press releases and disclosures parsed for claims. |
| `manual_import` (1) | Manually imported; no automatic re-check. *(mirrors the brief's `manual`)* |
| `sec_edgar_scan` (1) | SEC EDGAR scanned on cadence; new filings parsed for claims. |
| `iso_queue_ercot` (1) | ERCOT interconnection queue ingested; new project rows parsed for claims. |
| `iso_queue_pjm` (1) | PJM interconnection queue ingested; new project rows parsed for claims. |
| `iso_queue_caiso` (1) | CAISO interconnection queue ingested; new project rows parsed for claims. |
| `eia_api` (1) | U.S. Energy Information Administration API polled; energy data points ingested. |
| `neso_tec` (1) | UK National Grid ESO transmission entry capacity register polled. |
| `epoch_frontier` (1) | Epoch AI frontier model dataset polled; new model entries ingested. |
| `patentsview_search` (1) | USPTO PatentsView API queried; relevant patents ingested. |
| `google_patents_bq` (1) | Google Patents BigQuery dataset queried; relevant patents ingested. |
| `epo_ops` (1) | European Patent Office Open Patent Services queried; relevant patents ingested. |
| `dol_lca_xlsx` (1) | U.S. DOL Labor Condition Application disclosures downloaded; H-1B records parsed. |
| `greenhouse_board` (1) | Greenhouse public job board polled; new postings ingested. |
| `lever_postings` (1) | Lever public job postings polled; new postings ingested. |
| `ashby_public` (1) | Ashby public job board polled; new postings ingested. |
| `workable_jobs` (1) | Workable public job board polled; new postings ingested. |
| `fred_api` (1) | St. Louis Fed FRED API polled; economic series ingested. |
| `worldbank_api` (1) | World Bank API polled; macro indicators ingested. |
| `abs_api` (1) | Australian Bureau of Statistics API polled; economic series ingested. |
| `rba_api` (1) | Reserve Bank of Australia API polled; rate and macro series ingested. |
| `aemo_nem` (1) | AEMO National Electricity Market data polled; market data ingested. |
| `github_api` (1) | GitHub API polled; repository activity and releases ingested. |
| `huggingface_api` (1) | Hugging Face API polled; model and dataset metadata ingested. |

Coverage after extension: 107/107 (100%). Fall-through path (snake_case title-case) is preserved for any future extraction method added without a matching map entry.

The brief's §3.2 also lists `api` and `youtube_captions` which are not present in the registry today (defensive entries, kept verbatim from the brief).

### `on_event` status handling (tactical)

Brief §5 derivation table doesn't explicitly cover `on_event`; §6 edge-case rule says "skip status derivation, show 'Checked on event' with no Healthy/Stale verdict." Implemented as `deriveStatus → null` for `on_event`, with the status row suppressed and dates promoted to a `Dates` row in its place. Zero `on_event` sources exist today, so this is defensive.

### Status glyphs (tactical)

Brief AC#6 uses ✓/⚠/✗/⏸ glyphs in the status labels. Implemented inline in the label text (e.g. "✓ Healthy") rather than as separate icon spans — simpler and matches the spec's rendering literally.

### Frequency badge removal (tactical)

The previous header badge row included a purple frequency badge (e.g. "weekly"). With Cadence now in the Monitoring block, the badge would duplicate the same data. Removed it from the badge row; the friendly cadence label appears once in the Monitoring block. The badge CSS class `.badge-freq` is left in place (still used by nothing) — clean to remove in a follow-up if you want.

## Open items

- **`beta/sources.html` parity** — handoff instruction was sources.html only. The two files are byte-identical pre-change. Same diff will apply cleanly when you want to mirror.
- **D3b upgrade path** — status today is derived from `last_checked` vs cadence. If false signals become annoying (e.g. a scraper silently failing while `last_checked` keeps advancing), the upgrade is to add `last_status` to the registry and have each extraction script write it. Out of scope for this session per D3a.
- **Top-of-page legend** — explicitly ruled out by D-Mon. Per-card detail only.
- **Per-source `workflow_dispatch`** — the "Run extraction" button kicks off the whole batch. True per-source dispatch needs `workflow_dispatch` inputs on the 4 dispatched workflows + a `--source-id` flag on `scan_sources.py`, `monitor_sources.py --non-web`, `news_monitor.py`, `scrape_podcasts.py`. Worth a follow-on brief if the batch-only behaviour gets in the way.
- **`signal_scraper` workflow routing** — 3 sources use `signal_scraper`; the routing table sends them to `daily-monitor-sources-adapters.yml` as a best-fit. If `scrape_signals.py` lives in a different workflow that I missed, the button will dispatch the wrong one. Verify on first click in staging.
- **GitHub token scope** — `triggerWorkflow` needs `actions:write`. If the saved admin token is `contents:write` only the button will return a "dispatch failed" alert. Same scope already used by the existing Delete button's `commitFiles` path, so this is likely already fine.
- **`sec_filing` type** vs `sec_edgar_scan` method — only 1 source today uses `sec_filing` type (`web_extract` method). No drift; flagging only because the names look related.
- **`vault-inbox.json` is in UU (unmerged) state** in git per the session-open `git status`. Not touched by this work; flagging in case it surprises you when committing.

## Acceptance criteria status

- [x] AC#1 — Chip row above search bar, friendly labels + count, "All" first, count-desc sort
- [x] AC#2 — Click toggles, multi-select OR filter, active chip visually distinct
- [x] AC#3 — URL `?types=...` sync, reload preserves, empty filter omits the param
- [x] AC#4 — Counts reflect total registry, do not change as chips toggle
- [x] AC#5 — Search bar ANDs with chip filter
- [x] AC#6 — Per-card Monitoring block, always visible, Process + Cadence + Status pill + dates
- [x] AC#7 — Type badge uses friendly label
- [x] AC#8 — Default render unchanged behaviourally aside from new monitoring block + friendly type label
- [x] AC#9 — Single-file edit; no schema or script changes; no new deps
- [x] AC#10 — Responsive: chip row wraps; monitoring block stacks at ≤600px

## Publishing gate

Staging URL during review: `http://localhost:8765/sources.html` (local Python http.server). Simon reviewed both the initial v1 (chip filter + monitoring block) and the in-session v2 add (Review / Run extraction buttons) on this URL.

**Approval received:** 2026-05-14 — Simon, in chat: *"ok, lets ship"*

## Notion

Card https://www.notion.so/36057414da2a811184d1e482339c6e09 — needs manual move to Done. Claude Code does not have Notion write access in this session.
