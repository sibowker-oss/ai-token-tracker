# Deployment: wq-102 — Numbers binding & editorial supersession

**Date:** 2026-05-10
**WQ:** wq-102
**Branch/Commit:** `feature/wq-102-stage2-binding` → merged to `main` as `fbf83ca`
**Staging URL:** http://localhost:4173/beta/ (local preview, served via http-server during review)
**Approval timestamp:** 2026-05-10 ~08:35 UTC — Simon "Approved, ship it" in chat
**Live URL after promote:** https://ai-index.hepburnadvisory.com.au/beta/

## What shipped

The binding-and-supersession layer for the six priority pages (`index.html`, `capital.html`, `revenue.html`, `compute.html`, `usage.html`, `power.html` in `/beta/`). Every visible numeric literal on those pages is now catalogued in `data/numbers-manifest.json`, anchored in HTML with `data-num="<id>"`, and resolved at build time against `site-data.json` / `entities.json`. Stale editorial figures now flip to live engine values automatically when the engine emits the path; otherwise the editorial fallback (the literal at scan time) is preserved.

### New scripts

- `scripts/build_numbers_manifest.py` — extractor + auto-resolver. Walks priority pages, captures every numeric literal with line/col, classifies semantic, attempts to bind via 4-step ladder: JS hydration hints → `data-narrative=...` map → proximity-ranked semantic phrase rules → value-index match.
- `scripts/anchor_html.py` — installs `data-num="<id>"` anchors. Single-occupant DOM ids get the attribute on the existing element; otherwise the literal is wrapped in a new `<span>`.
- `scripts/render_numbers.py` — runs after `generate_site_data.py`. Resolves each manifest entry, formats via the manifest format string, rewrites HTML data-num elements / JS array literals / og:description content. Emits `data/numbers-changelog.md`.
- `scripts/derive_layer_stack_ratios.py` — computes gross-anchored ratios (capex/usage/compute/power × Apps Revenue gross) + usage notional ($141B). Wired into the build between `generate_site_data.py` and `render_numbers.py`.
- `scripts/validate-numbers-anchored.mjs` — release-gate. Walks the six priority pages and rejects any visible numeric literal not anchored, with an allowlist for years and tier-letter codes (1A/1B, 2A/2B, 3A/3B/3C). Wired into `release-check.mjs` step 11g and `build-lint.yml` as a CI step.
- `scripts/preview_numbers_supersession.py` — Stage-1.5 dry-run that diffs editorial fallback vs live engine state per entry. Used during review.

### Manifest

- `data/numbers-manifest.json` — 159 entries across 6 pages
- `schemas/numbers-manifest.schema.json` — JSON-Schema for the manifest
- `data/wq-102-source-path-gaps.md` — gap report (1 known gap: power.html 95 GW)
- `data/wq-102-supersession-preview.md` — dry-run diff
- `data/wq-102-notion-id-map.json` — Number ID → Notion page ID map
- `data/numbers-changelog.md` — emitted by render at every build

### Live flips on first build

| Surface | Editorial → Live |
|---|---|
| Cumulative capex (homepage card, capital narrative) | $745B → $766B |
| 2025 capex (capital narrative + LAG_RAW + og:description) | $380B → $330B |
| Customer revenue gross | $17.5B → $19B |
| Tokens annualised | ~360T → ~310T |
| Compute YoY growth | +153% → +153.4% |
| Layer Stack ratios (vs Apps Revenue gross): | |
| · Capex | 19× → 17.1× |
| · Usage | 9.4× → 7.3× |
| · Compute | 2.5× → 2.2× |
| · Power | 1.4× → 1.3× |
| Usage notional figure | $164B → $141B |
| Hook ratio (compute/apps gross) | $2.50 → $2.23 |
| Capital sankey utilization buckets | 2-3% drift each |

### Counts

- 159 manifest entries
- 37 sourced (live engine)
- 17 editorial fallback (path stub awaiting engine extension)
- 105 fixed editorial (intentional — tier mixes, methodology constants, narrative prose)
- **1 gap**: `power.html:115` — `95 GW` US data centre interconnection queue placeholder. Power Ledger v3 pending; engine has no path yet.

### Notion

All 159 entries synced to "TAIL Numbers Audit" DB at `collection://960e3a90-4c9e-4744-9070-ad0ff2d2f62b`. `notion_id` backfilled into manifest for every entry. wq-102 Notion card needs status update to **Done** (no programmatic write in this session).

### CLAUDE.md additions

- **Numbers Binding Contract** section: rules for adding new numbers to priority pages, build sequence, release-gate behaviour.
- **JS hydration vs `data-num`** sub-section: contract that JS-hydrated elements must read the same engine paths the manifest binds (else flicker); JS-driven interactive elements diverge by design.

## Decisions made during implementation

- **Cross-page dedupe disabled** (Stage 1.5 commit `6118e70`) — was silently dropping JS-array entries when an HTML anchor with the same value existed elsewhere. Each anchor is now a distinct render target.
- **JS data-array mining** (`LAG_RAW`) added to Stage 1 mid-flight per Simon's catch — 40 cells × 5 columns of capital.html's three-stage lag chart now catalogued.
- **Token-fixed phrase windows widened** from 30 → 80 chars to absorb Stage 2's anchor-span wrapping. Phrase must precede the token (rhetorical "behind every $1") or follow ("1× baseline"), but not be claimed bidirectionally.
- **Layer-stack ratios anchored on GROSS apps revenue** (not net) per Simon's catch that the visible Revenue pill shows gross — keeps the page internally consistent. Old `apps_to_compute_2025` etc. (net-anchored) preserved for backwards compat.
- **`_hydrate(FALLBACK)` removed at startup** to eliminate flash-of-stale on hard refresh. Data-num literals are now the editorial fallback during the fetch round-trip.
- **Editorial bug deferred for follow-up**: `capital.html:607` `kpi-period` says "2025" but the math is cumulative 2023-25. Manual HTML label fix; logged in `data/wq-102-source-path-gaps.md`.

## Open items

- **Power Ledger v3 pending** — `95 GW` figure stays editorial until engine extends.
- **Stub paths (17 entries)** — `compute.layer_stack_ratios.*_per_dollar_apps_gross` exists; other stubs (`capital_sankey.sensitivity_defaults.*`, `capital_sankey.fleet_to_cogs_ratio_x`, `compute.frontier_lab_share_2025_pct`, `entities.market_aggregates._cumulative_2023_2025.nvidia_dc_revenue_b`, `entities.market_aggregates._counterfactual.ad_self_funded_capex_b`, `entities.market_aggregates._narrative.google_rpo_b`) await engine extension. Stage 2 falls back to literal until they land.
- **Capital.html L607 kpi-period label fix** — change `2025` to `2023&ndash;25` to match the cumulative math the card displays.
- **Follow-on sweep** for the other ~30 pages outside priority six (candidate `wq-103`).
- **Notion card status** — wq-102 in Notion needs to be moved to **Done**; no programmatic access in this session.

## Acceptance criteria status

Stage 1 (§3.4):
- [x] `data/numbers-manifest.json` exists with one entry per data-driven number on each of the six priority pages
- [x] `data/wq-102-source-path-gaps.md` lists every entry where `source_path` could not be auto-resolved
- [x] Notion DB "TAIL Numbers Audit" populated with one row per manifest entry; `notion_id` backfilled
- [x] Manifest validates against `schemas/numbers-manifest.schema.json`
- [x] No HTML changes during Stage 1 (Stage 1 was read-only)

Stage 2 (§4.4):
- [x] All six priority pages have every catalogued number anchored (`data-num="…"`)
- [x] `render_numbers.py` runs cleanly; deterministic output (running it twice yields no diff)
- [x] `data/numbers-changelog.md` accurately reports the supersession state
- [x] Visual regression check: rendered numbers match either engine value (when threshold met) or editorial_fallback
- [x] Staging URL produced; Simon reviewed before promotion
- [x] CLAUDE.md updated with the binding contract
- [x] Release-gate addition rejecting unanchored literals on the priority pages

## Stop conditions

None hit. Auto-resolution rate 99.4% (target ≥40%); no-candidate rate 0.6% (target ≤10%). Visual diff on staging matched expected manifest-driven flips with no unintended changes.
