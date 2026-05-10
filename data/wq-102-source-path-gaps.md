# wq-102 — Source-path gap report

Generated 2026-05-10 by `scripts/build_numbers_manifest.py`.

## Summary

- Total manifest entries: **108**
- Auto-resolved (`source_path` populated): **39**
- Intentionally fixed editorial (no path needed, `source_state=fixed`): **68**
- **Auto-resolution rate (path or fixed): 99.1%** (target ≥40%)
- Needs manual path assignment: **1**
- No path candidate at all: **0** (0.0%) (target ≤10%)

## Entries needing manual `source_path` assignment

Entries below were extracted but the resolver couldn't pick a unique path. Where candidates exist, they're listed for human selection; where blank, the value isn't currently in `site-data.json` / `entities.json` and may need engine extension.

### `power.html` — 1 unresolved

| Line | Raw | Semantic | Anchor | Candidate paths | Context |
|---|---|---|---|---|---|
| 115 | `95 GW` | `market_aggregate.power` | — | site-data.computeProviders.aiNativeCompute[3].arrNumeric<br>site-data.arrModel.compute.aiNativeCompute.entries[3].arr<br>entities.companies[0].provenance.Q4 2024.tokens_per_day.claims[0].value | <div style="font-size:36px;font-weight:800;color:var(--orange);">95 GW</div> |

## Intentionally fixed editorial entries (no source_path expected)

68 entries flagged as `source_state=fixed` (tier-mix percentages, methodology constants, regulatory ids, etc.). Build skips supersession but routes the literal through the formatter.

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
| capital.html | 222 | `$170B` | `uncategorised` | <label for="cf-check">Ad-platform counterfactual: exclude $170B of self-funded ad/cloud infrastructu |
| capital.html | 226 | `$34` | `ratio_derived` | Excluding them reduces the infrastructure-to-revenue ratio from <strong id="cf-ratio-from" data-rati |
| capital.html | 226 | `$1` | `ratio_derived` | Excluding them reduces the infrastructure-to-revenue ratio from <strong id="cf-ratio-from" data-rati |
| capital.html | 226 | `$13` | `ratio_derived` | Excluding them reduces the infrastructure-to-revenue ratio from <strong id="cf-ratio-from" data-rati |
| capital.html | 226 | `$1` | `ratio_derived` | Excluding them reduces the infrastructure-to-revenue ratio from <strong id="cf-ratio-from" data-rati |
| capital.html | 245 | `$24B` | `per_entity_metric.revenue` | <tr><td>Revenue growth rate vs. depreciation</td><td>3&ndash;4x annual growth to cover depreciation< |
| capital.html | 245 | `$17.5B` | `per_entity_metric.revenue` | <tr><td>Revenue growth rate vs. depreciation</td><td>3&ndash;4x annual growth to cover depreciation< |
| capital.html | 245 | `$41B` | `per_entity_metric.revenue` | <tr><td>Revenue growth rate vs. depreciation</td><td>3&ndash;4x annual growth to cover depreciation< |
| capital.html | 245 | `4x` | `ratio_derived` | <tr><td>Revenue growth rate vs. depreciation</td><td>3&ndash;4x annual growth to cover depreciation< |
| capital.html | 246 | `~$170B` | `market_aggregate.capex_annual` | <tr><td>Ad/cloud workloads covering their share</td><td>Existing business models justify the CapEx</ |
| capital.html | 247 | `$368B` | `market_aggregate.capex_annual` | <tr><td>CapEx growth trajectory</td><td>New purchases stabilise so depreciation levels</td><td class |
| capital.html | 250 | `$1T` | `market_aggregate.revenue` | <strong>NVIDIA $1T target:</strong> cumulative AI-chip revenue through CY2027 = ~$1.07T at projected |
| capital.html | 250 | `~$1.07T` | `market_aggregate.revenue` | <strong>NVIDIA $1T target:</strong> cumulative AI-chip revenue through CY2027 = ~$1.07T at projected |
| capital.html | 250 | `$1T` | `market_aggregate.revenue` | <strong>NVIDIA $1T target:</strong> cumulative AI-chip revenue through CY2027 = ~$1.07T at projected |
| capital.html | 308 | `$766B` | `ratio_derived` | <div class="sens-label" id="sens-ratio-detail" style="margin-top:4px;">$766B total &middot; $22B rev |
| capital.html | 308 | `$22B` | `ratio_derived` | <div class="sens-label" id="sens-ratio-detail" style="margin-top:4px;">$766B total &middot; $22B rev |
| capital.html | 320 | `4x` | `ratio_derived` | <div class="cp-title">Revenue compounds at 3&ndash;4x annually</div> |

_(38 more …)_

## Notes

- An entry resolved via `<script>` binding mining is marked with `binding_hint` in its `_capture` block — these were trusted directly and are NOT in the gap list above.
- Cross-page duplicates (same `source_path`, value, format) are collapsed into a single entry with `pages: [...]`.
- `editorial_fallback.value` is captured verbatim from the HTML at scan time. The supersession story lives in the gap between this fallback and the resolved live value: Stage 2 build picks the live value when its provenance clears the threshold, else the fallback.