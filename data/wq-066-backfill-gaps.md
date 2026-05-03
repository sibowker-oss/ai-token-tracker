# wq-066 Editorial Backfill — Gap Report

Generated: 2026-05-03  ·  Source: assumptions-audit.md  ·  Extractor: scripts/extract_audit_values.py

## Backfill summary

- **Written:** 1 fields
- **Skipped (engine has authoritative value):** 7 fields
- **Overrides removed (engine now within ±5%):** 0

### Written values
- 2025.tokens_per_day_total: None → 565.0

### Skipped (engine value preserved)
- 2025.total_customer_revenue: existing engine value=17.557 preserved (audit=17.47)
- 2025.total_vc_subsidy: existing engine value=8.4479 preserved (audit=9.8)
- 2025.total_system_cost: existing engine value=27.27 preserved (audit=27.27)
- 2025.mag7_capex: existing engine value=250 preserved (audit=250.0)
- 2025.total_inference_cost: existing engine value=14.03 preserved (audit=14.03)
- 2025.total_people_cost: existing engine value=11.08 preserved (audit=11.08)
- 2025.total_margin: existing engine value=2.15 preserved (audit=2.15)

## Gaps requiring Simon input

### Per-year market aggregates

#### 2023
- **total_customer_revenue**: not documented in audit. Question for Simon: what was total customer revenue in 2023?
- **total_customer_revenue_gross**: not documented in audit. Question for Simon: what was total customer revenue gross in 2023?
- **total_vc_subsidy**: not documented in audit. Question for Simon: what was total vc subsidy in 2023?
- **mag7_capex**: not documented in audit. Question for Simon: what was mag7 capex in 2023?
- **neocloud_capex**: not documented in audit. Question for Simon: what was neocloud capex in 2023?
- **sovereign_capex**: not documented in audit. Question for Simon: what was sovereign capex in 2023?
- **enterprise_capex**: not documented in audit. Question for Simon: what was enterprise capex in 2023?
- **tokens_per_day_total**: not documented in audit. Question for Simon: what was tokens per day total in 2023?
  > Audit note: audit doc has no 2023-specific market aggregates; entities.json has no 2023 collected_revenue per provider

#### 2024
- **total_customer_revenue**: not documented in audit. Question for Simon: what was total customer revenue in 2024?
- **total_customer_revenue_gross**: not documented in audit. Question for Simon: what was total customer revenue gross in 2024?
- **total_vc_subsidy**: not documented in audit. Question for Simon: what was total vc subsidy in 2024?
- **mag7_capex**: not documented in audit. Question for Simon: what was mag7 capex in 2024?
- **neocloud_capex**: not documented in audit. Question for Simon: what was neocloud capex in 2024?
- **sovereign_capex**: not documented in audit. Question for Simon: what was sovereign capex in 2024?
- **enterprise_capex**: not documented in audit. Question for Simon: what was enterprise capex in 2024?
- **tokens_per_day_total**: not documented in audit. Question for Simon: what was tokens per day total in 2024?
  > Audit note: audit doc has 2024 entity-level revenue refs but no aggregated market totals or capex/tokens

#### 2025
- **total_customer_revenue_gross**: not documented in audit. Question for Simon: what was total customer revenue gross in 2025?
- **neocloud_capex**: not documented in audit. Question for Simon: what was neocloud capex in 2025?
- **sovereign_capex**: not documented in audit. Question for Simon: what was sovereign capex in 2025?
- **enterprise_capex**: not documented in audit. Question for Simon: what was enterprise capex in 2025?

### Per-entity 2024 revenue
- **anthropic.2024.collected_revenue** = 0.5 (derived). audit doesn't explicitly state 2024 standalone — derived from cumulative minus 2025
- **google.2024.collected_revenue**: audit only has 2025 Google revenue.
- **meta.2024.collected_revenue**: audit shows $0 for 2025; 2024 not stated.

### Per-provider tokens (entities.json refresh candidate)
- Audit §5.3 sums to 717T/day across 9 model_providers + others.
- entities.json model_provider tokens_per_day sums to ~164T/day (stale).
- entities.json model_provider tokens_per_day are stale — OpenAI=30 vs audit=200, Anthropic=6 vs 110, etc. Refresh candidate.
- Suggested follow-on brief: refresh entities.json:companies[*].current.tokens_per_day for model_providers from latest signals (audit §5.3 + recent provider disclosures).

### Cumulative (2023–2025) overrides held
- $745B cumulative capex + $28B cumulative customer revenue + 360T cumulative tokens NOT documented in audit; held as wq-063 editorial overrides pending external sourcing
- These remain held in data/consensus_overrides.json (expires 2026-09-01).

---

Each gap above can become its own backfill ticket once Simon answers. Engine ingests his answer via a single edit to consensus_overrides.json (cumulative-level) or direct entity field write (per-entity).