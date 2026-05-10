# wq-102 — Source-path gap report

Generated 2026-05-10 by `scripts/build_numbers_manifest.py`.

## Summary

- Total manifest entries: **153**
- Auto-resolved (`source_path` populated): **48**
- Intentionally fixed editorial (no path needed, `source_state=fixed`): **104**
- **Auto-resolution rate (path or fixed): 99.3%** (target ≥40%)
- Needs manual path assignment: **1**
- No path candidate at all: **0** (0.0%) (target ≤10%)

## Entries needing manual `source_path` assignment

Entries below were extracted but the resolver couldn't pick a unique path. Where candidates exist, they're listed for human selection; where blank, the value isn't currently in `site-data.json` / `entities.json` and may need engine extension.

### `power.html` — 1 unresolved

| Line | Raw | Semantic | Anchor | Candidate paths | Context |
|---|---|---|---|---|---|
| 115 | `95 GW` | `market_aggregate.power` | — | site-data.computeProviders.aiNativeCompute[3].arrNumeric<br>site-data.arrModel.compute.aiNativeCompute.entries[3].arr<br>entities.companies[0].provenance.Q4 2024.tokens_per_day.claims[0].value | <div style="font-size:36px;font-weight:800;color:var(--orange);">95 GW</div> |

## Intentionally fixed editorial entries (no source_path expected)

104 entries flagged as `source_state=fixed` (tier-mix percentages, methodology constants, regulatory ids, etc.). Build skips supersession but routes the literal through the formatter.

| Page | Line | Raw | Semantic | Context |
|---|---|---|---|---|
| index.html | 235 | `$1.25` | `methodology_constant` | <span class="ais-note">notional @ $1.25/M output rate</span> |
| index.html | 279 | `$1` | `ratio_derived` | <div class="hook-number"><span id="hook-ratio">$2.50</span> of compute spend stands behind every $1  |
| index.html | 303 | `40%` | `percentage_uncategorised` | <span class="tier-pill tier-1">40% Sourced</span> |
| index.html | 304 | `35%` | `percentage_uncategorised` | <span class="tier-pill tier-2">35% Derived</span> |
| index.html | 305 | `25%` | `percentage_uncategorised` | <span class="tier-pill tier-3">25% Modeled</span> |
| index.html | 314 | `65%` | `percentage_uncategorised` | <span class="tier-pill tier-1">65% Sourced</span> |
| index.html | 315 | `25%` | `percentage_uncategorised` | <span class="tier-pill tier-2">25% Derived</span> |
| index.html | 316 | `10%` | `percentage_uncategorised` | <span class="tier-pill tier-3">10% Modeled</span> |
| index.html | 325 | `60%` | `percentage_uncategorised` | <span class="tier-pill tier-1">60% Sourced</span> |
| index.html | 326 | `30%` | `percentage_uncategorised` | <span class="tier-pill tier-2">30% Derived</span> |
| index.html | 327 | `10%` | `percentage_uncategorised` | <span class="tier-pill tier-3">10% Modeled</span> |
| index.html | 336 | `50%` | `percentage_uncategorised` | <span class="tier-pill tier-2">50% Derived</span> |
| index.html | 337 | `50%` | `percentage_uncategorised` | <span class="tier-pill tier-3">50% Modeled</span> |
| capital.html | 820 | `$1B` | `market_aggregate.revenue` | LAG_RAW[0] year='2023' revenue=1.0 |
| capital.html | 820 | `$48B` | `per_entity_metric.revenue` | LAG_RAW[0] year='2023' nvidia=48.0 |
| capital.html | 820 | `$0B` | `per_entity_metric.depreciation` | LAG_RAW[0] year='2023' nvDep=0.0 |
| capital.html | 820 | `$0B` | `market_aggregate.depreciation` | LAG_RAW[0] year='2023' totalDep=0.0 |
| capital.html | 821 | `$115B` | `per_entity_metric.revenue` | LAG_RAW[1] year='2024' nvidia=115.0 |
| capital.html | 821 | `$12B` | `per_entity_metric.depreciation` | LAG_RAW[1] year='2024' nvDep=12.0 |
| capital.html | 821 | `$22B` | `market_aggregate.depreciation` | LAG_RAW[1] year='2024' totalDep=22.0 |
| capital.html | 822 | `$194B` | `per_entity_metric.revenue` | LAG_RAW[2] year='2025' nvidia=194.0 |
| capital.html | 822 | `$41B` | `per_entity_metric.depreciation` | LAG_RAW[2] year='2025' nvDep=41.0 |
| capital.html | 822 | `$74B` | `market_aggregate.depreciation` | LAG_RAW[2] year='2025' totalDep=74.0 |
| capital.html | 827 | `$850B` | `market_aggregate.capex_annual` | LAG_RAW[3] year='2026E' totalCapex=850.0 |
| capital.html | 827 | `$64B` | `market_aggregate.revenue` | LAG_RAW[3] year='2026E' revenue=64.0 |
| capital.html | 827 | `$311B` | `per_entity_metric.revenue` | LAG_RAW[3] year='2026E' nvidia=311.0 |
| capital.html | 827 | `$89B` | `per_entity_metric.depreciation` | LAG_RAW[3] year='2026E' nvDep=89.0 |
| capital.html | 827 | `$160B` | `market_aggregate.depreciation` | LAG_RAW[3] year='2026E' totalDep=160.0 |
| capital.html | 828 | `$1100B` | `market_aggregate.capex_annual` | LAG_RAW[4] year='2027E' totalCapex=1100.0 |
| capital.html | 828 | `$115B` | `market_aggregate.revenue` | LAG_RAW[4] year='2027E' revenue=115.0 |

_(74 more …)_

## Editorial-level bugs flagged for Stage 2

Bugs spotted during Stage 1 review that are NOT manifest entries — they're label / wording fixes needed in the HTML directly. Logged here so they don't fall through Stage 2:

- **`capital.html:607`** — third hero card *Infrastructure per $1 revenue* shows `<div class="kpi-period">2025</div>` but the math (`v.t0` = cumulative CapEx ÷ `sc.revenue`) actually reflects 2023–25. Should read `2023–25` to match the first two cards. Fix: replace literal `2025` with `2023&ndash;25` in the JS template string at line 607. Discovered during wq-102 Stage 1 review (Simon).

## Notes

- An entry resolved via `<script>` binding mining is marked with `binding_hint` in its `_capture` block — these were trusted directly and are NOT in the gap list above.
- Cross-page duplicates (same `source_path`, value, format) are collapsed into a single entry with `pages: [...]`.
- `editorial_fallback.value` is captured verbatim from the HTML at scan time. The supersession story lives in the gap between this fallback and the resolved live value: Stage 2 build picks the live value when its provenance clears the threshold, else the fallback.