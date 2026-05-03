# wq-068 Remaining Gaps Report

Generated: 2026-05-03  ·  After: token refresh (v3) + 565→330 correction + mag7 capex 2023+2024 backfill

## What wq-068 closed

| Refresh | Before | After | Source |
|---|---|---|---|
| 9 model_providers tokens_per_day (sum) | 164 T/day | 117 T/day | model-assumptions.md §2.4 v3 consensus midpoints |
| `market_aggregates.2025.tokens_per_day_total` | 565 (wq-066 §5.1 backfill) | 330 (v3 global midpoint) | model-assumptions.md §2.4 |
| `market_aggregates.2023.mag7_capex` | 0 / null | $152B | public 10-Ks (Meta + MSFT + GOOG + AMZN + AAPL) |
| `market_aggregates.2024.mag7_capex` | 0 / null | $226B | public 10-Ks (same five) |

Engine cumulative capex sum across 2023+2024+2025: **$152B + $226B + $252.58B = $630.58B**
(Override held at $745B — gap explained below.)

## Override resolution pass

| Override | Engine value | Override value | Δ% | Auto-removed? |
|---|---|---|---|---|
| `_cumulative_2023_2025.capex_total` | $630.58B | $745B | -15.4% | ✗ stays held |
| `_cumulative_2023_2025.customer_revenue_gross` | $23.94B | $28B | -14.5% | ✗ stays held |
| `_cumulative_2023_2025.tokens_2025_annualized` | null | 360 | n/a | ✗ stays held |

Per Simon's 2026-05-03 confirmation: none expected to remove given the structural gaps documented below.

## Top gap requiring Simon input — wq-070 candidate

**Add ByteDance / Alibaba / Tencent / Baidu / self-hosted as model_provider entities.**
This is the single biggest unblock. v3 consensus global is 280-370T/day, broken down per model-assumptions.md §2.4:

| Provider | v3 midpoint | In entities.json? |
|---|---|---|
| ByteDance | 110 T/day | ✗ missing |
| Google | 49 T/day | ✓ refreshed |
| OpenAI | 30 T/day | ✓ refreshed |
| Alibaba/Qwen | 25 T/day | ✗ missing |
| Anthropic | 6 T/day | ✓ refreshed |
| Tencent | 10 T/day | ✗ missing |
| Baidu | 8 T/day | ✗ missing |
| DeepSeek | 8.5 T/day | ✓ refreshed |
| Meta | 11.5 T/day | ✓ refreshed |
| Minimax | 4.5 T/day | ✓ refreshed |
| Moonshot/Kimi | 3 T/day | ✓ refreshed |
| Mistral | 2 T/day | ✓ refreshed |
| xAI | 2.5 T/day | ✓ refreshed |
| Other closed | 7.5 T/day | ✗ aggregated |
| Self-hosted open | 30 T/day | ✗ missing as entity |
| **Sum** | **~307** | (Western 9 = 117) |

Adding ByteDance + Alibaba + Tencent + Baidu (~153 T/day combined) would lift engine `tokens_per_day_total` from 117 → 270, well within ±20% of the 330 v3 global. Sufficient for the cumulative tokens override to remove.

## Capex source backfills still pending

To retire the `capex_total` override ($745B), engine needs $115B more capex from non-mag7 sources:

| Source bucket | 2023 | 2024 | 2025 | Total needed |
|---|---|---|---|---|
| `neocloud_capex` | null | null | $2.58B (engine est) | ~$15-25B (CoreWeave + Lambda + Crusoe + Nebius across 3 yrs) |
| `sovereign_capex` | null | null | 0 (no entities) | ~$30-50B (G42 / SDA / Humain / Scaleway) |
| `enterprise_capex` | null | null | $4.66B (engine est) | ~$50-80B (per-entity capex disclosures) |
| **Total non-mag7 needed** | | | | ~$95-155B |

If non-mag7 capex backfills land within that range, engine cumulative reaches ~$725-785B — directly inside ±5% of the $745B override.

## 2024 collected_revenue per provider

Engine has 2024 collected_revenue for OpenAI ($2.58B) + Anthropic ($1.5B) only. Missing:

- google.financials.2024.collected_revenue (audit only has 2025 Google revenue; 2024 standalone never extracted)
- meta.financials.2024.collected_revenue (audit shows $0 for 2025; 2024 not stated)
- All other model_providers' 2024 figures (deepseek, mistral, xai, minimax, moonshot)

Filling these would lift the cumulative `customer_revenue_gross` engine value from $23.94B toward $28B.

## Suggested follow-on briefs

- **wq-070 — Add Chinese + self-hosted model_provider entities** (highest leverage; retires tokens override)
- **wq-071 — Non-mag7 capex backfill** (neocloud + sovereign + enterprise per year; retires capex override)
- **wq-072 — 2024 collected_revenue per provider** (google + meta + small-cap model_providers; retires customer_revenue_gross override)

Once all three land, the entire `_cumulative_2023_2025` override block becomes empty and engine output IS the published headline.
