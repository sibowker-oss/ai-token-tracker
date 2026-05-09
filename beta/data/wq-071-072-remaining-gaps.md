# wq-071 + wq-072 Remaining Gaps Report

Generated: 2026-05-03  ·  After: non-mag7 capex backfill (wq-071) + 2024 collected_revenue per provider (wq-072)

## What landed

### wq-071 — non-mag7 capex by year

| Source | 2023 | 2024 | 2025 | Source pattern |
|---|---|---|---|---|
| `neocloud_capex` | $8B | $25B | $45B | CoreWeave + Lambda + Crusoe + Nebius + smaller |
| `sovereign_capex` | $3B | $10B | $20B | UAE G42 + Saudi PIF + Stargate (prorated) |
| `enterprise_capex` | $4B | $8B | $15B | F500 direct AI infra outside hyperscaler resale |

### wq-072 — 2024 collected_revenue per provider

| Slug | 2024 collected_revenue | Source | Engine value before |
|---|---|---|---|
| openai | $3.6B | Zitron / MSFT leaked docs (audit §1.1) | $2.58B (engine; superseded) |
| anthropic | $1.5B | audit §1.2 | $1.5B (already at value) |
| google | $0.8B | editorial estimate (Gemini ramp) | null |
| meta | $0.0B | Meta AI not commercialized 2024 | null |

## Override retirement results

| Override | Engine value | Override value | Δ% | Status after wq-071+072 |
|---|---|---|---|---|
| `_cumulative_2023_2025.capex_total` | $766B | $745B | +2.8% | ✓ **REMOVED** (cleared at engine $739, well within ±15%) |
| `_cumulative_2023_2025.customer_revenue_gross` | $25.76B | $28B | -8.0% | ✓ **REMOVED** (cleared in wq-070 prune at $23.94B; engine now even closer at $25.76B) |
| `_cumulative_2023_2025.tokens_2025_annualized` | 300 T/day | 360 T/day | -16.7% | · STAYS HELD (just outside ±15%) |

**2 of 3 cumulative overrides retired.** Only `tokens_2025_annualized` remains.

## Why tokens override stays held (and what would retire it)

Engine 300 T/day = sum of 9 Western model_providers (117) + 4 Chinese (153) + self-hosted (30).
Override 360 T/day = published headline anchored to v3 GLOBAL midpoint.
Gap = 60 T/day = 16.7%, just outside the ±15% retirement threshold.

Three paths to retire:
1. **Editorial decision** — manually remove the override; site headline becomes 300 T/day (data-honest)
2. **Refine self-hosted estimate upward** — current 30 T/day is mid-range of v3's 20-40T; if updated to 40T+ engine lands at ~310-320T (still outside ±15%)
3. **Add "Other closed" category** as another synthetic entity — v3 lists Cohere/AI21/Samsung/Apple Intelligence at ~5-10T combined; would push engine to ~308-310T

Either way, headline 360 → 300-320 is a small editorial story that may itself merit a methodology note.

## Remaining gaps surfaced post-wq-071+072

### Per-source capex confidence

- `neocloud_capex 2025 = $45B` is the lowest-confidence value (CoreWeave guidance is $20-23B alone; rest scaling — survey-based for the smaller players)
- `sovereign_capex 2025 = $20B` involves Stargate $500B proration — editorial choice (could plausibly be $30-50B if Stargate lands faster)
- `enterprise_capex` survey-based across all years — confidence low

### 2023 + 2024 customer revenue still incomplete

- Smaller model_providers (deepseek, mistral, xai, minimax, moonshot) still have null 2024 collected_revenue. Brief notes: "2024 revenue probably zero or trivial; skip unless documented." If they are non-zero (e.g. DeepSeek had ~$20-50M of inference API revenue 2024) it would lift the cumulative gross slightly.
- All entities have null 2023 collected_revenue. 2023 cumulative gross stays null.

### Per-entity capex attribution

- All non-mag7 capex is at the source-bucket level. Per-entity breakdown (which neocloud spent how much in which year) would enable better entity Sankey nodes — out of scope for wq-071.

## Suggested follow-on briefs

1. **wq-073 — refine self-hosted token methodology** to retire the last cumulative override. Editorial choice between (a) raise the synthetic estimate, (b) add "Other closed" category, (c) accept engine 300T as the new published figure.
2. **wq-074 — small-cap model_provider 2024 revenue backfill** (deepseek/mistral/xai/minimax/moonshot). Probably retrieves only $0.1-0.5B combined; minor improvement.
3. **wq-075 — per-entity neocloud capex attribution** (CoreWeave, Lambda, Crusoe, Nebius separately) so Sankey can show neocloud as standalone provider rather than aggregated bucket.
