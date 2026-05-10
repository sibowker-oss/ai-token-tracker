# Deployment: Revenue Sankey — per-provider cost reconciliation + projection-year ratio propagation

**Date:** 2026-05-10
**WQ:** ad-hoc bug report (Simon, in-session)
**Branch/Commit:** main (this commit)
**Approval timestamp (publishing gate):** 2026-05-10, in-chat "looks good push live" after staging-URL review at http://127.0.0.1:8765/revenue.html

## What shipped

Three coupled changes on `revenue.html` (root + `/beta/` mirror) and the underlying engine, plus two new editorial operating_loss claims.

### 1. Sankey renderer — segments now reconcile to inflows

**Bug:** Segment heights and labels in the "Where It Goes" column were drawn from `outcomes[].value` (engine bottom-up sum of per-provider `inference_cost` + `opex`), while inflow ribbons were computed via `provider.value × flat costParams.inferencePct`. As per-provider cost data diverged from the flat 0.57 rate, the chart visibly disagreed with itself — Inference segment showed $9B but tooltip inflows summed to $15B.

**Fix:**
- `beta/revenue.html` (and root mirror): renderer now reads per-provider `inference_cost` / `opex` from the data when present and draws each `provider → Inference` and `provider → Other Op Cost` ribbon at the engine value. Falls back to `value × INFERENCE_PCT` when fields absent (older data files).
- `scripts/generate_site_data.py:_apply_sankey_engine_output`: provider entries written to `sankey-projections.json` now carry per-provider `inference_cost` and `opex`, including the "Other Model Providers" aggregation block (sum of constituents).
- `scripts/derive_sankey.py:aggregate_small_providers` + `apply_market_aggregates`: Other-aggregation block now sums member `inference_cost` and `opex`.

### 2. Anthropic op_loss now drives opex (TIER 2b path in `resolve_opex`)

**Issue:** Anthropic has sourced `operating_loss = $5.2B` (dp-006, APAC AI Intel derived) but no entity-field `inference_cost`. The 2026-05-03 "Interpretation A" rule made TIER 2 in `resolve_opex` require entity-field `inf` — so Anthropic dropped to TIER 3 size-band and the engine ignored its sourced op_loss, understating Anthropic total cost by $2.6B.

**Fix:** New TIER 2b path: `resolve_opex` now accepts the resolved inference value (from `resolve_inference_cost`, which may be a TIER 3 estimate) and computes `opex = max(0, op_loss + ref_revenue - resolved_inf)` whenever op_loss is sourced. Origin tagged as `derived_with_estimated_inf` so downstream tier-badging doesn't over-claim confidence.

Effect on Anthropic 2025: opex 4.71 → **7.32**; total value 7.30 → **9.91**; vc_subsidy plug 2.59 → **5.20** (= operating_loss).

Other entities affected: only Anthropic (only entity in the database with op_loss but no entity-field inf as of run time).

### 3. Editorial operating_loss claims for Google AI and xAI

Per Simon ("we should aim to get them right" for major providers; "use approx Opex rate as a ratio of revenue" for the rest), added two editorial-estimate operating_loss claims with explicit provenance:

- **Google (Gemini AI division)** — `dp-243`: $4.0B operating loss (mid-range of public DeepMind cost estimates $4–5B; Bloomberg, Sacra). Confidence: low. Effect: total value 2.93 → **6.25**; opex 2.25 → **5.58** (op_loss-driven via TIER 2b).
- **xAI** — `dp-244`: $4.5B operating loss (Bloomberg/Reuters reporting on Nov-2024 $6B raise + mid-2025 $10B rumor; Musk-disclosed burn ~$5B/yr). Confidence: low. Effect: total value 0.46 → **4.77**; opex 0.32 → **4.64**.

Both claims carry full provenance (`source`, `date`, `reference_revenue`, `reference_revenue_set_at`) and are flagged confidence=low so future overwrite by sourced numbers is straightforward.

DeepSeek / Mistral / Minimax / Moonshot left at size-band estimates (Simon: aggregated into "Other Model Providers" anyway; per-claim guesses don't add audit value).

### 4. 2025 ratios propagate to 2026E / 2027E projection years

**Issue:** Projection-year sankeys had editorial `costParams.providerRates` (set before 2025 data was complete) that didn't reflect 2025 reality. Switching the year toggle showed inflow/segment reconciliation by accident — both used the same flat-rate fallback — but the underlying cost ratios were detached from any anchor.

**Fix:** New build step `_apply_2025_ratios_to_projection_years` in `generate_site_data.py`:
- Computes per-provider 2025 `inf_ratio` and `opex_ratio` from `entities.json:market_aggregates.2025.providers` (unaggregated dict, so providers like IaaS/Open that get rolled into "Other" for 2025 display are still individually available for projection-year lookup).
- For each non-2025 year in `sankey-projections.json`, applies those ratios per-provider and rewrites the year's outcomes column (Inference, Other Op Cost, Generated Cashflow) so segment heights match inflow sums.
- Honours per-year per-provider overrides from `data/sankey_cost_structure.json:cost_trajectory_overrides` (schema documented inline). No overrides set in this deploy — defaults everywhere.
- "Other Model Providers" projection bucket falls back to `costParams.inferencePct` because the 2025 "Other" basket has different composition (post-xAI promotion, 2025 Other includes IaaS).

**Effect on projection sankeys:**
- 2026E: Inference $38.2B → **$26.8B**; Other Op Cost $42.3B → **$54.5B**; Generated Cashflow $8.5B → **$7.7B** (channel margins only; no provider surplus under 2025 ratios).
- 2027E: Inference $47.3B → **$33.2B**; Other Op Cost $51.4B → **$67.4B**; Generated Cashflow $16.1B → **$14.2B**.

## Decisions made during implementation

- **Interpretation A (2026-05-03) reversed for the Anthropic case** — TIER 2b path uses the resolved inference value (which may be TIER 3 estimated) when entity-field inf is absent, rather than discarding sourced op_loss entirely. New origin tag `derived_with_estimated_inf` flags the dependency for tier-aware downstream consumers.
- **Editorial op_loss claims for Google and xAI written directly to `entities.json` with `confidence: low`** — chosen over per-provider rate overrides in `cost_structure.json` because (a) the data shape is auditable per-claim with provenance, (b) supersession works normally if a real number arrives, and (c) the new TIER 2b path picks them up automatically.
- **Both inference AND opex use 2025 ratios for projection years** (Simon's option 3) — keeps the chart self-consistent (inflow ribbons exactly match segment values) while leaving the override hook available for future per-year scenario overlays.
- **No projection-year overrides set in this deploy** — defaults to "projections inherit 2025 cost structure unchanged." Override schema documented in code; populate when scenario work resumes.

## Open items

- Anthropic's inference_cost is still TIER 3 estimated (`cr × 0.55`). When a sourced inference number lands, opex automatically recomputes via TIER 2a (sourced inf) path and the editorial estimate gets superseded.
- Google AI and xAI op_loss values are editorial mid-range estimates. Promote to higher tier when better sources arrive (Sacra revenue signals, public earnings disclosures, etc.).
- "Other Model Providers" projection bucket uses flat `costParams.inferencePct` rather than 2025 ratios because basket composition diverges. If we want it ratio-grounded, expose a synthetic "Other" 2025 ratio in `_apply_2025_ratios_to_projection_years`.

## Acceptance criteria status

- [x] Inference segment height = sum of provider→Inference inflows (2025, 2026E, 2027E)
- [x] Other Op Cost segment height = sum of provider→Other Op Cost inflows (2025, 2026E, 2027E)
- [x] Generated Cashflow segment height = channel margins + provider surplus (all three years)
- [x] Anthropic sourced operating_loss ($5.2B) drives engine opex output
- [x] Google + xAI op_loss claims carry full provenance with confidence=low
- [x] `validate-sankey-conservation.mjs` passes
- [x] Projection-year ratios traceable via `_cost_basis` field on each provider entry
- [x] Override hook installed for future per-year per-provider scenario overlays

## Cross-Ledger reconciliation note

This deploy raises 2025 total VC subsidy $8.45B → **$18.69B** and total system $25.81B → **$36.05B**, both surfaced on the revenue.html hero strip and in the page subtitle. The Compute Ledger and other pages publish related figures; per CLAUDE.md cross-ledger rule the bridge is:

- The $18.69B VC subsidy = sum of per-provider `vc_subsidy` plugs, which now equals each provider's reported operating loss (or the engine-derived plug for providers without sourced op_loss). Customer revenue ($17.36B) is unchanged.
- Compute Ledger pass-through ($11.5B per wq-089/wq-090) is the AI-attributable hyperscaler IaaS revenue stream — disjoint from the providers' VC subsidy. No new conflict introduced.
- Cumulative capex on the homepage hero ($766B) is unrelated to per-provider operating losses; same scope.

If a follow-on cross-ledger audit surfaces a contradiction, file `docs/decisions/open/dec-...md` per the rule.
