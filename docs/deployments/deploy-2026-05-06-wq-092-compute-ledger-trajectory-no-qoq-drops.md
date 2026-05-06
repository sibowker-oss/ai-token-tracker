# Deployment: wq-092 — Compute Ledger trajectory no-Q-o-Q drops

**Date:** 2026-05-06
**WQ:** wq-092 (deploy correction to wq-091)
**Branch/Commit:** wq-092-compute-ledger-trajectory-no-qoq-drops · 5170a59
**Parent deployment:** `docs/deployments/deploy-2026-05-06-wq-091-compute-ledger-segment-sizing-correction.md`
**Derivation memo:** `docs/decisions/resolved/dec-2026-05-06-compute-ledger-bucket-sizing.md` (addendum + Q4 25 → Q1 26 transition handling section already updated by Cowork mid-session before code handoff)

## Why this corrects wq-091

wq-091 shipped per-provider 2025 calendar values on **annualised run-rate basis** (MSFT $28B per Microsoft self-disclosed $37B run-rate × ratio; AMZN $10B per Jassy back-cast; GOOGL $7B bottom-up; ORCL $3B). Quarterly array was back-cast to sum to those annualised totals while Q1 2026 was anchored at literal disclosed run-rate ÷ 4 (MSFT $9.25B = $37B/4; AWS $3.75B = $15B/4 per Jassy).

When growth accelerates through a year, sum-of-quarterlies < annualised exit × 4. So forcing the four 2025 quarters to sum to the annualised totals balloons Q4 25 above Q1 26, producing visible Q-o-Q drops on the trajectory chart that contradict the AI growth narrative:

| Provider | wq-091 shipped Q4 25 | wq-091 shipped Q1 26 | Q-o-Q |
|---|---|---|---|
| MSFT | $10.50B | $9.25B | **–12%** |
| AMZN | $3.75B | $3.75B | flat |
| GOOGL | $3.65B | $2.50B | **–32%** |

The chart visibly showed AI revenue dropping into Q1 2026 — directly contradicting +123% YoY MSFT, +170% Bedrock Q-o-Q AMZN, +800% YoY gen-AI GOOGL narratives.

## What shipped

### Calendar basis switch (D1)
Per-provider 2025 calendar values switched to **sum-of-quarterlies basis**. Annualised run-rate values preserved per provider in new field `value_2025_annualised_run_rate_basis_usd_b` so the editorial-context number is not lost.

| Provider | wq-091 annualised | wq-092 sum-of-Q | Δ |
|---|---|---|---|
| MSFT | $28.00B | **$25.25B** | –$2.75B (growth-acceleration gap) |
| AMZN | $10.00B | $10.00B | 0 (Jassy implies; bases coincide) |
| GOOGL | $7.00B | $7.00B | 0 (bottom-up; bases coincide) |
| ORCL | $3.00B | $2.95B | –$0.05B |
| CRWV | $4.50B | $4.23B | –$0.27B |
| NBIS | $0.95B | $0.89B | –$0.06B |
| LMBD | $0.60B | $0.56B | –$0.04B |
| CRSE | $0.40B | $0.37B | –$0.03B |
| **TOTAL** | **$54.45B** | **$51.25B** | **–$3.20B** |

### Final Locked Trajectory (D2, D3, D4)
Every major provider grows monotonically Q1 25 → Q1 26:

| Provider | Q1 25 | Q2 25 | Q3 25 | Q4 25 | Q1 26 | Sum 2025 | Q4→Q1 26 |
|---|---|---|---|---|---|---|---|
| MSFT | 4.15 | 5.50 | 7.20 | 8.40 | 9.25 | $25.25B | **+10%** |
| AMZN | 1.50 | 2.20 | 2.70 | 3.60 | 3.75 | $10.00B | **+4%** |
| GOOGL | 0.70 | 1.40 | 2.10 | 2.80 | 3.00 | $7.00B | **+7%** |
| ORCL | 0.50 | 0.65 | 0.85 | 0.95 | 0.90 | $2.95B | –5% (informational) |
| CRWV | 0.92 | 0.98 | 1.11 | 1.22 | 1.50 | $4.23B | +23% |
| NBIS | 0.09 | 0.19 | 0.25 | 0.36 | 0.34 | $0.89B | –6% (informational) |
| LMBD | 0.09 | 0.12 | 0.15 | 0.20 | 0.18 | $0.56B | –10% (informational) |
| CRSE | 0.07 | 0.09 | 0.10 | 0.11 | 0.12 | $0.37B | +9% |
| **TOTAL** | **8.05** | **11.12** | **14.47** | **17.61** | **19.04** | **$51.25B** | **+8%** |

GOOGL Q1 26 raised from $2.50B (wq-091) to $3.00B (wq-092 D4) — re-derived from +800% YoY gen-AI-products narrative back-cast (Tier 2A editorial), ensures monotonic growth from Q4 25 ($2.80B).

### Per-provider segment allocations rescaled (D3)
Where 2025 calendar shifted (MSFT, ORCL, neoclouds), segment values rescaled proportionally:

- **MSFT** (× 25.25/28 = 0.902): Frontier lab compute $18.0B → $16.23B; AI workload $1.1B → $0.99B; Hosted model APIs gross $1.5B → $1.35B; pass-through $0.30B → $0.27B; Copilot excluded $7.4B → $6.67B. Tie-out: $25.24B ≈ $25.25B ✓
- **ORCL** (× 2.95/3.0 = 0.983): Frontier lab compute $2.0B → $1.97B; AI workload $1.0B → $0.98B. Tie-out: $2.95B ✓
- **CRWV** (× 4.23/4.5 = 0.94): Frontier $4.0B → $3.76B; Workload $0.5B → $0.47B
- **NBIS / LMBD / CRSE**: scaled identically per their factor

AMZN and GOOGL segments unchanged ($10B and $7B sum-of-Q = annualised).

### Page edits (D5)
- **`compute.html` Quarterly Trajectory caption simplified** per D5: replaced the wq-091 orange-flagged AWS-flatness/GOOGL-dip apologetics with a single methodology line — "2025 calendar = sum-of-quarterlies basis; Q1 2026 anchored at disclosed run-rates ÷ 4 (MSFT $9.25B = $37B/4; AWS $3.75B = $15B/4 per Jassy). Every major provider grows monotonically into Q1 2026."
- **`methodology.html` new sub-section** "Calendar basis: sum-of-quarterlies, not annualised run-rate (locked wq-092, 2026-05-06)" — two paragraphs explaining the basis choice, what the gap is, why we don't lose the annualised number.

### Validator update
- **New Check 10 in `validate-compute-revenue.mjs`**: no Q-o-Q drops Q4 25 → Q1 26 for major providers (MSFT/AMZN/GOOGL → fail). ORCL, NBIS, LMBD, CRSE emit advisory only because quarterly noise on a small base is editorially acceptable.
- **`AI_LINE_TARGETS_2025` updated** to sum-of-quarterlies values per Final Locked Trajectory.

## Decisions made during implementation

- **"Major provider" defined as MSFT/AMZN/GOOGL only.** D2 says "every major provider must show Q1 26 > Q4 25" but the Final Locked Trajectory itself shows ORCL Q4 25 = $0.95B → Q1 26 = $0.90B (–5%). Resolved by treating ORCL and individual neoclouds as informational-only in the validator (advisory severity); the major-provider strict check applies to MSFT/AMZN/GOOGL where the AI growth narrative is most load-bearing.
- **Quarterly array per neocloud rescaled by aggregate ratio.** Neoclouds aggregate sum-of-Q = $6.05B (target per Final Locked Trajectory) vs $6.46B existing. Each provider's 2025 quarterlies scaled by the aggregate ratio (~0.937), then minor manual adjustments to land per-quarter aggregate within ±0.05B of the target. Q1 26 quarterlies unchanged from wq-091 (already correct; aggregate Q1 26 = $2.14B).
- **Per-provider segment values hold three decimals where rescale produces non-clean numbers.** MSFT Frontier lab compute = $16.23B (= $18B × 0.902 to two decimals). The aggregator outputs round to two decimals at the headline; ±2% tolerance on per-provider tie-out covers any sub-decimal drift.
- **2024 reference held at $17B.** Per brief edge case, doesn't need restatement — already on a different basis. YoY recomputes to +153% (was +168% under wq-091 annualised basis).

## Headline numbers (wq-092 vs wq-091 vs wq-089)

| Metric | wq-089 | wq-091 | wq-092 | Δ from 091 |
|---|---|---|---|---|
| 2025 calendar gross pre-Copilot | $73.45B | $54.45B | **$51.25B** | –$3.20B |
| Copilot scope-out | $8.0B | $8.90B | **$8.17B** | –$0.73B |
| Compute gross post-Copilot | $65.45B | $45.55B | **$43.07B** | –$2.48B |
| Compute net 2025 | $64.42B | $44.53B | **$42.08B** | –$2.45B |
| Frontier lab compute | $50.55B | $35.95B | **$33.82B** | –$2.13B |
| AI workload compute | $10.40B | $5.10B | **$4.90B** | –$0.20B |
| Hosted model APIs gross | $4.50B | $4.50B | **$4.35B** | –$0.15B |
| Pass-through | $1.025B | $1.025B | **$0.995B** | ~0 |
| YoY 2025 vs 2024 | +103% | +168% | **+153%** | –15 pts |
| WWHBT capex coverage | ~20% | ~14% | **~13%** | –1 pt |

Frontier-lab share of compute holds at 79% (the circular-financing line still dominates).

## Open items

- **wq-090 (Revenue Ledger Hyperscaler & Who Pays).** Still independent of this correction. Pass-through target ($1B) barely moved (was $1.025B, now $0.995B). Reconciliation target unaffected.
- **Future Apps Ledger.** Copilot scope-out shifts from $8.90B → $8.17B but the editorial framing (MS-declared vs TAIL-derived) is unchanged.
- **Visual snapshot baselines.** compute.html quarterly trajectory chart line shapes change materially; hero strip values shift slightly. New baselines required in next release-check pass.
- **labels.spec.ts pre-existing failures.** Unrelated to wq-091/wq-092; carried over.

## Acceptance criteria status

- [x] `data/compute_disclosures.json` quarterly arrays match Final Locked Trajectory per provider within ±0.05B
- [x] Per-provider 2025 calendar values restated to sum-of-Q basis; new `value_2025_annualised_run_rate_basis_usd_b` field preserves annualised reference per provider
- [x] Per-provider segment allocations sum to new calendar value within ±2% (validator passes)
- [x] `derive_compute_revenue.py --print-summary` shows: Compute gross $43.07B (~$43.5B target), Compute net $42.08B (~$42.5B target), per-major-provider Q1 26 > Q4 25
- [x] `/compute.html` quarterly trajectory chart will render with monotonic growth on every major provider line (visual baseline pending follow-up)
- [x] Hero strip Box 1 (gross) ~$43.07B; Box 2 (net) ~$42.08B; Box 3 (ratio) recalculates from new ratios; Box 4 (YoY) +153%
- [x] Caption beneath trajectory chart simplified per D5 (single methodology line; no apologetics)
- [x] `/methodology.html` has new paragraph explaining sum-of-Q vs annualised basis choice
- [x] `validate-compute-revenue.mjs` includes no-Q-o-Q-drop assertion (Check 10) for MAJOR providers; passes
- [x] `npm run build-lint` passes (0 fail, 1 advisory unchanged from baseline)
- [ ] `npm run release-check` — wq-091/wq-092 compute.spec.ts assertions pass; visual snapshot baselines need rebaseline in follow-up
- [x] Deployment record cross-references wq-091 record as parent (this file)

## Notion

Move wq-092 card from In Progress → Done. (Repo cannot mutate Notion directly; flagging here.)
