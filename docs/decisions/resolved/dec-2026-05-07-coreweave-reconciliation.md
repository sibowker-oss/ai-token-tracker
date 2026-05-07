# Decision: CoreWeave reconciliation — TAIL vs Ed (Zitron) vs filed 10-Q/10-K

**WQ:** wq-094
**Date:** 2026-05-07
**Context:** wq-094 ingested Zitron 2026-05-06 and added forward commitments + capacity figures across compute providers, including CoreWeave. The Zitron piece challenges the TAIL CoreWeave numbers on two points (Microsoft customer concentration % and total 2025 revenue). The next-session task was to pull the most recent CoreWeave SEC filing and apply whichever figure is filed-anchored.

## Inputs reconciled

| Field | TAIL pre-wq-094 | Ed (Zitron 2026-05-06) | Filed 10-K (FY2025) / 10-Q (Q3 2025) |
|---|---|---|---|
| Microsoft customer concentration | **85%** of revenue | **67%** of 2025 revenue | **67%** of FY2025 revenue (10-K, full-year 2025 actuals) |
| 2025 total revenue | $4.5B annualised exit run-rate / $4.23B sum-of-quarterlies | $5.15B | **$5.10B** FY2025 actual (10-K) |
| Q3 2025 revenue | derived $1.11B in trajectory | not directly cited | **$1.36B** (10-Q for quarter ended 2025-09-30) |
| 9M 2025 revenue (Jan–Sep) | derived $3.01B (sum of Q1+Q2+Q3) | not directly cited | **$3.56B** (10-Q YTD) |
| Q4 2025 implied revenue | derived $1.22B in trajectory | not directly cited | **$1.54B** (= 10-K $5.10B − 10-Q YTD $3.56B) |
| Backlog Q3 2025 | not separately tracked | $55.6B referenced | **$55.6B** (10-Q) |
| 2025 ARR / collected_revenue (entities.json) | 2025.arr = 1.9 / 2025.collected_revenue = 1.023 | n/a | $1.92B is FY2024 (S-1 disclosed; mis-attributed in TAIL); FY2025 = $5.10B |

## Sources

- **CoreWeave Form 10-Q for the quarter ended Sep 30, 2025** — SEC filing crwv-20250930 (filed Nov 2025): Q3 2025 revenue $1,364,676k; nine months ended Sep 30, 2025 revenue $3,559,096k; revenue backlog $55.6B.
- **CoreWeave Form 10-K for FY2025** — SEC filing (filed Q1 2026): full-year 2025 revenue $5.1B; Microsoft customer concentration 67% of 2025 revenue (vs 62% in 2024, ramping with 85% backlog at start-of-2025 falling to 35% by Q3 2025 as new contracts diversified the order book).
- **CoreWeave Q3 2025 earnings release** (investors.coreweave.com): confirms Q3 revenue $1.36B, backlog $55.6B, full-year 2025 guidance reduced to $5.05–5.15B from prior $5.15–5.35B due to data-centre construction delays.
- **CoreWeave Q1 2026 earnings** are reported 2026-05-07 (today); no Q1 2026 10-Q is filed yet at decision time. Refresh next quarterly cycle.

## Reconciliation

### Microsoft customer concentration: **apply 67%**

TAIL's 85% figure was a backlog snapshot at start-of-2025 (Microsoft was 85% of CoreWeave's contract backlog at the IPO, dropping to 35% by Q3 2025 as new OpenAI / Meta / others contracts came in). That is a different basis from revenue concentration. The 10-K's 67% is the FY2025 revenue concentration — Microsoft generated 67% of CoreWeave's $5.1B FY2025 revenue. Both numbers are correct on their own basis but they describe different things; TAIL's 85% should not have been published as a revenue-concentration figure.

**Filed-anchored: 67%** (FY2025 revenue concentration, 10-K).
**Bridge to the 85%:** TAIL's 85% will be retained as `microsoft_backlog_share_at_2025_start_pct` on the CoreWeave entity (separate field, separate basis). The published Microsoft-concentration number on rendered pages = 67%.

### Total 2025 revenue: **apply $5.10B**

TAIL's $4.23B sum-of-quarterlies / $4.5B annualised run-rate was anchored on Q3 2025 trajectory before Q4 actuals were known. Ed's $5.15B was the high end of CoreWeave's lowered guidance range. The 10-K filed FY2025 actual is **$5.10B** — within Ed's guidance band, materially above TAIL's sum-of-Q.

**Filed-anchored: $5.10B FY2025 actual** (10-K).

The gap vs TAIL's $4.23B sum-of-Q is $0.87B. Decomposing:
- TAIL Q3 25 = $1.11B vs filed $1.36B → +$0.25B
- TAIL Q4 25 = $1.22B vs implied $1.54B → +$0.32B
- Q1+Q2 25 trajectory under-counts vs ramp implied by full-year reconciliation → +$0.30B (residual)

The Q4 25 surge (+$0.32B vs trajectory) is consistent with the construction-delay narrative: deliveries were back-end loaded once data-centre commissioning cleared.

## Entity changes applied (this decision)

`entities.json:coreweave`:

- `financials.2024.arr` and `.collected_revenue` set to `1.92` (S-1 disclosed; previously mis-attributed to 2025).
- `financials.2025.arr` updated to `5.10` (FY2025 actual, 10-K).
- `financials.2025.collected_revenue` updated to `5.10` (FY2025 actual, 10-K).
- `financials.2025.microsoft_concentration_pct` added: `67` (10-K, FY2025 revenue basis).
- `financials.2025.microsoft_backlog_share_at_2025_start_pct` added: `85` (carried from prior TAIL figure on its correct basis).
- `current.backlog_q3_2025_usd_b` added: `55.6` (10-Q).
- `provenance` entries added/refreshed pointing at the 10-K and 10-Q SEC URLs.

## Items deferred (out of scope for this decision)

- `data/compute_disclosures.json:components.coreweave` quarterly trajectory + per-segment Frontier-lab/AI-workload split refresh from $4.23B sum-of-Q to $5.10B filed. Doing this requires re-running `scripts/derive_compute_revenue.py` and re-validating Layer Stack tie-outs (per Cross-Ledger Reconciliation rule). Tracked as wq-095 follow-up: `compute_disclosures.json` CoreWeave trajectory refresh + tie-out re-validation post Q1 2026 10-Q (filed after 2026-05-07 earnings).
- The Microsoft-sub-rent-share-of-CoreWeave-revenue figure (TAIL: ~85% per the segment_basis comment) needs revisiting separately under the filed 10-K disclosures around Microsoft-attributable revenue mix — that figure governs the Layer Stack circular-financing callout, not the headline concentration number.

## Resolution

**Applied.** Filed-anchored values updated in `entities.json:coreweave`. Decision marked resolved on landing.
