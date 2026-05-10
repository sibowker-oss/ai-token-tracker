# Numbers Changelog

Last build: 2026-05-10 08:29 UTC

## State summary

- **37** numbers rendered from live engine values (sourced)
- **17** numbers rendered from editorial fallback (path stub — engine extension needed)
- **105** numbers preserved as fixed editorial (tier mixes, methodology constants, narrative prose)

## Sourced (live)

| Page | ID | Editorial → Rendered | Source path |
|---|---|---|---|
| `capital.html` | `capital.lag_raw.2023.totalCapex` | `$160B` → `$167B` | `entities.market_aggregates.2023.total_capex` |
| `capital.html` | `capital.lag_raw.2024.revenue` | `$4B` → `$5.9B` | `entities.market_aggregates._cumulative_2023_2025.by_year.2024.customer_revenue_gross` |
| `capital.html` | `capital.lag_raw.2024.totalCapex` | `$280B` → `$269B` | `entities.market_aggregates.2024.total_capex` |
| `capital.html` | `capital.lag_raw.2025.revenue` | `$17B` → `$19B` | `site-data.sankey.totalCustomerRevenue_gross` |
| `capital.html` | `capital.lag_raw.2025.totalCapex` | `$380B` → `$330B` | `entities.market_aggregates.2025.total_capex` |
| `capital.html` | `capital.market_aggregate_capex_cumulative.766b_infrastructure_investment_ndash` | `$766B` ≡ `$766B` | `site-data.capital_sankey.total` |
| `capital.html` | `capital.market_aggregate_capex_cumulative.lhs_source_buckets_cumulative` | `$766B` ≡ `$766B` | `site-data.capital_sankey.total` |
| `capital.html` | `capital.market_aggregate_capex_cumulative.total_capex_reached_approximately` | `$380B` → `$330B` | `entities.market_aggregates.2025.total_capex` |
| `capital.html` | `capital.market_aggregate_capex_cumulative.total_capex_reached_approximately_2` | `$17.5B` → `$19B` | `site-data.sankey.totalCustomerRevenue_gross` |
| `capital.html` | `capital.market_aggregate_power.idle_68b_mdash_commissioned` | `$68B` ≡ `$68B` | `site-data.arrModel.compute.tradCompute.totalGross` |
| `capital.html` | `capital.market_aggregate_revenue.customer_revenue_must_grow` | `$17.5B` → `$19B` | `site-data.sankey.totalCustomerRevenue_gross` |
| `capital.html` | `capital.per_entity_metric_revenue.inference_paid_50b_mdash` | `$50B` → `$51B` | `site-data.capital_sankey.utilization.Inference (Paid)` |
| `capital.html` | `capital.uncategorised.inference_free_tier_32b` | `$32B` → `$33B` | `site-data.capital_sankey.utilization.Inference (Free Tier)` |
| `capital.html` | `capital.uncategorised.inference_platform_201b_mdash` | `$201B` → `$207B` | `site-data.capital_sankey.utilization.Inference (Ad Platform)` |
| `capital.html` | `capital.uncategorised.model_training_84b_mdash` | `$84B` → `$87B` | `site-data.capital_sankey.utilization.Model Training` |
| `index.html` | `index.dom.ais_capex_figure` | `$330B` ≡ `$330B` | `entities.market_aggregates.2025.total_capex` |
| `index.html` | `index.dom.ais_capex_sub` | `19×` → `17.1×` | `site-data.compute.layer_stack_ratios.capex_to_apps_gross_x` |
| `index.html` | `index.dom.ais_compute_figure` | `$43.1B` → `$43B` | `site-data.compute.compute_revenue_2025_gross_usd_b` |
| `index.html` | `index.dom.ais_power_figure` | `$25B` ≡ `$25B` | `site-data.compute.layer_stack_ratios.power_revenue_2025_usd_b` |
| `index.html` | `index.dom.ais_revenue_figure` | `$19.3B` → `$19B` | `site-data.sankey.totalCustomerRevenue_gross` |
| `index.html` | `index.dom.ais_usage_figure` | `$164B` → `$141B` | `site-data.compute.layer_stack_ratios.usage_notional_2025_usd_b` |
| `index.html` | `index.dom.ais_usage_sub` | `~360T/day` → `~310T/day` | `site-data.cumulative.tokens_2025_annualized` |
| `index.html` | `index.dom.ais_usage_sub_2` | `9.4×` → `7.3×` | `site-data.compute.layer_stack_ratios.usage_notional_to_apps_gross_x` |
| `index.html` | `index.dom.card_capex` | `$745B` → `$766B` | `site-data.cumulative.capex_total` |
| `index.html` | `index.dom.card_compute` | `$43B` ≡ `$43B` | `site-data.compute.compute_revenue_2025_gross_usd_b` |
| `index.html` | `index.dom.card_revenue` | `$19.3B` → `$19B` | `site-data.sankey.totalCustomerRevenue_gross` |
| `index.html` | `index.dom.card_tokens` | `~360T/day` → `~310T/day` | `site-data.cumulative.tokens_2025_annualized` |
| `index.html` | `index.dom.hook_ratio` | `$2.50` → `$2.23` | `site-data.compute.layer_stack_ratios.compute_per_dollar_apps_gross` |
| `index.html` | `index.dom.lt_subline` | `+153%` → `+153.4%` | `site-data.compute.yoy_growth_pct` |
| `index.html` | `index.dom.lt_value` | `$43B` ≡ `$43B` | `site-data.compute.compute_revenue_2025_gross_usd_b` |
| `index.html` | `index.market_aggregate_tokens.value` | `$745B` → `$766B` | `site-data.cumulative.capex_total` |
| `index.html` | `index.market_aggregate_tokens.value_2` | `$43B` ≡ `$43B` | `site-data.compute.compute_revenue_2025_gross_usd_b` |
| `index.html` | `index.market_aggregate_tokens.value_3` | `$17B` → `$19B` | `site-data.sankey.totalCustomerRevenue_gross` |
| `index.html` | `index.market_aggregate_tokens.value_4` | `~360T` → `~310T` | `site-data.cumulative.tokens_2025_annualized` |
| `index.html` | `index.percentage_uncategorised.hyperscalers_neoclouds_earned_compute` | `79%` → `79.1%` | `site-data.arrModel.combined.ai_native_total` |
| `index.html` | `index.ratio_derived.apps_revenue` | `2.5×` → `2.2×` | `site-data.compute.layer_stack_ratios.compute_to_apps_gross_x` |
| `index.html` | `index.ratio_derived.apps_revenue_2` | `1.4×` → `1.3×` | `site-data.compute.layer_stack_ratios.power_to_apps_gross_x` |

## Needs source (path nominated, engine doesn't emit)

Stage 2 falls back to the literal until engine extends. Listed for follow-on briefs.

| Page | ID | Literal | Source path |
|---|---|---|---|
| `capital.html` | `capital.dom.sens_ads_val` | `$170B` | `site-data.capital_sankey.sensitivity_defaults.ads_capex_b` |
| `capital.html` | `capital.dom.sens_china_val` | `100%` | `site-data.capital_sankey.sensitivity_defaults.china_share_pct` |
| `capital.html` | `capital.dom.sens_idle_val` | `$50B` | `site-data.capital_sankey.sensitivity_defaults.idle_capex_b` |
| `capital.html` | `capital.dom.sens_ratio_display` | `$35` | `site-data.capital_sankey.sensitivity_defaults.ratio_display_usd` |
| `capital.html` | `capital.market_aggregate_capex_annual.build_transit_310b_mdash` | `$310B` | `site-data.capital_sankey.utilization.In Build / In Transit` |
| `capital.html` | `capital.market_aggregate_capex_annual.meta_google_microsoft_allocate` | `$170B` | `entities.market_aggregates._counterfactual.ad_self_funded_capex_b` |
| `capital.html` | `capital.market_aggregate_capex_cumulative.anchored_nvidia_revenue_356b` | `$356B` | `entities.market_aggregates._cumulative_2023_2025.nvidia_dc_revenue_b` |
| `capital.html` | `capital.per_entity_metric_revenue.infrastructure_current_revenue` | `$1.00` | `entities.companies[3].provenance.2026.capex.claim_count` |
| `capital.html` | `capital.per_entity_metric_revenue.middle_nodes_mdash_money` | `$303B` | `entities.market_aggregates._cumulative_2023_2025.nvidia_dc_revenue_b` |
| `capital.html` | `capital.percentage_uncategorised.value` | `85%` | `entities.companies[12].financials.2025.microsoft_backlog_share_at_2025_start_pct` |
| `capital.html` | `capital.ratio_derived.bridge_revenue_paid_consumer` | `$82B` | `entities.companies[2].provenance.Q4 2025.tokens_per_day.claims[0].value` |
| `capital.html` | `capital.ratio_derived.bridge_revenue_paid_consumer_3` | `5.9×` | `site-data.capital_sankey.fleet_to_cogs_ratio_x` |
| `capital.html` | `capital.ratio_derived.revenue_inference_spend_cross` | `4×` | `site-data.dashboard.enterpriseReality[4].postureScores.acceleration` |
| `compute.html` | `compute.market_aggregate_compute_revenue.why_separate_trajectory_chart` | `$200B` | `entities.market_aggregates._narrative.google_rpo_b` |
| `compute.html` | `compute.market_aggregate_compute_revenue.why_separate_trajectory_chart_2` | `$718B` | `entities.market_aggregates._narrative.google_rpo_b` |
| `index.html` | `index.dom.lt_subline_2` | `79%` | `site-data.compute.frontier_lab_share_2025_pct` |
| `power.html` | `power.market_aggregate_power.value` | `95 GW` | `(none)` |

## Fixed editorial (intentional, no supersession)

105 entries — see `data/numbers-manifest.json` for the full list.
