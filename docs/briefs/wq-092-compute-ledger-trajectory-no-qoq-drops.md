---
id: wq-092
title: Compute Ledger — eliminate Q-o-Q drops in quarterly trajectory (deploy correction to wq-091)
stage: Scoped
priority: H
owner: Simon (impl: Claude Code in VS Code)
created: 2026-05-06
status: ready_for_handoff
parent_context: /Users/simonbowker/Documents/Claude/Projects/The AI Ledger/ (Cowork session 2026-05-06)
parent_brief: /Users/simonbowker/Developer/apac-ai-intel/docs/briefs/wq-091-compute-ledger-bucket-sizing-correction.md
derivation_memo: /Users/simonbowker/Developer/apac-ai-intel/docs/decisions/resolved/dec-2026-05-06-compute-ledger-bucket-sizing.md
---

# wq-092 · Compute Ledger — eliminate Q-o-Q drops in quarterly trajectory

## Why this brief exists

wq-091 shipped 2026-05-06 with the D9 quarterly back-cast applied. The deployed trajectory has every major provider showing a Q4 2025 → Q1 2026 decline:

| Provider | Q4 25 (shipped) | Q1 26 (shipped) | Q-o-Q |
|---|---|---|---|
| MSFT | $10.50B | $9.25B | **–12%** (no caption) |
| AMZN | $3.75B | $3.75B | flat (captioned) |
| GOOGL | $3.65B | $2.50B | **–32%** (captioned as "backlog timing") |

The chart visibly shows AI revenue dropping into Q1 2026 — directly contradicting Microsoft's +123% YoY narrative, Amazon's "+170% Bedrock Q-o-Q" disclosure, and Google's "+800% YoY on gen AI products" commentary.

Root cause: wq-091 anchored 2025 calendar to the **annualised run-rate basis** (~$28B MSFT, $10B AMZN, $7B GOOGL — derived from CEO disclosures of full-year run-rate × 4) AND Q1 26 to the **literal quarterly basis** ($37B/4, $15B/4). When growth accelerates through a year, sum-of-quarterlies < annualised, so forcing the quarterly array to sum to the annualised number balloons Q4 25 above Q1 26.

The fix: switch the 2025 calendar tie-out to **sum-of-quarterlies basis**, smaller in absolute terms, which lets each provider's quarterly trajectory grow monotonically into Q1 26.

## Decisions Simon has made (do not re-litigate without flagging)

| # | Decision | Confirmed |
|---|---|---|
| D1 | **2025 calendar basis = sum-of-quarterlies, NOT annualised run-rate × 4.** Where there's tension between the two, sum-of-quarterlies wins for the trajectory + Layer Stack lookback. The annualised run-rate number is retained as a separate reference field in `data/compute_disclosures.json` for context but does not constrain the quarterly array. | 2026-05-06 |
| D2 | **Quarterly trajectory must show monotonic growth Q1 25 → Q1 26 for every major provider.** No Q4 25 ≥ Q1 26 anywhere. Accept slightly lower 2025 calendar totals (sum-of-quarterlies basis vs annualised) as the cost of editorial coherence with the AI growth narrative. | 2026-05-06 |
| D3 | **Restated 2025 calendar (sum-of-quarterlies) per provider:** MSFT ~$25.25B (was $28B annualised); AMZN ~$10B (holds — Jassy ramp shape works); GOOGL ~$7B (holds — boost Q1 26 to fix); ORCL $2.95B (holds); neoclouds ~$6.05B (holds). | 2026-05-06 |
| D4 | **Q1 26 anchors stay literal where disclosed:** MSFT $9.25B ($37B/4 per Q1 26 earnings), AMZN $3.75B ($15B/4 per Jassy). GOOGL Q1 26 raised from $2.50B (shipped) to $3.00B — re-derived from "+800% YoY on gen AI products" narrative back-cast against bottom-up GCP AI line, ensures growth from Q4 25. | 2026-05-06 |
| D5 | **Caption framing on chart removed for AWS/GOOGL** (no longer needed since neither flatlines or drops). MSFT trajectory needs no caption. Methodology page adds a paragraph explaining run-rate vs sum-of-quarterlies basis choice. | 2026-05-06 |

## Open decisions — none

---

## Final locked trajectory (2026-05-06)

| Provider | Q1 25 | Q2 25 | Q3 25 | Q4 25 | Q1 26 | 2025 sum |
|---|---|---|---|---|---|---|
| MSFT | $4.15 | $5.50 | $7.20 | $8.40 | $9.25 | **$25.25B** |
| AMZN | $1.50 | $2.20 | $2.70 | $3.60 | $3.75 | **$10.00B** |
| GOOGL | $0.70 | $1.40 | $2.10 | $2.80 | $3.00 | **$7.00B** |
| ORCL | $0.50 | $0.65 | $0.85 | $0.95 | $0.90 | $2.95B |
| Neoclouds (sum) | $1.20 | $1.37 | $1.62 | $1.86 | $2.14 | $6.05B |
| **Quarterly TOTAL** | **$8.05** | **$11.12** | **$14.47** | **$17.61** | **$19.04** | **$51.25B** |

Q-o-Q growth check: every major provider grows Q4 25 → Q1 26 (MSFT +10%, AMZN +4%, GOOGL +7%). ORCL holds (Stargate ramp). Neoclouds grow (CoreWeave + others continue ramp).

## Headline numbers (post-wq-092)

| Metric | wq-091 shipped | wq-092 corrected | Δ |
|---|---|---|---|
| 2025 calendar sum (gross, pre-Copilot) | $54.45B | **$51.25B** | –$3.2B |
| Copilot scope-out (sum-of-Q basis) | $8.9B | **~$7.7B** | –$1.2B (Copilot grew through year — sum-of-Q < annualised) |
| Compute gross post-Copilot 2025 | $45.55B | **~$43.5B** | –$2.0B |
| Compute net 2025 | $44.5B | **~$42.5B** | –$2.0B |
| Frontier lab compute share | 79% | ~79% (unchanged) | — |
| YoY 2025 vs 2024 | +168% (per Code's deployed) | recompute (~+150–170%) | small adjust |

The headline restatement is small (~$2B downward); the editorial fix is large (chart shows monotonic AI growth, no Q-o-Q drops).

---

## Scope

### In scope

1. **`data/compute_disclosures.json` quarterly array restatement** per provider per Final Locked Trajectory above.
2. **`data/compute_disclosures.json` per-provider 2025 calendar field updates** to sum-of-quarterlies basis. Add new `value_2025_annualised_run_rate_basis_usd_b` field per provider preserving the annualised number for context (MSFT $28B, AMZN $10B, GOOGL $7B). The `value_*_2025_*` fields used by aggregator switch to sum-of-quarterlies.
3. **`data/compute_disclosures.json` per-provider segment allocations rescaled** to match new sum-of-quarterlies calendar totals. Frontier lab compute / AI workload compute / Hosted model APIs / Copilot per provider proportionally adjust. Verify each provider's segments sum to new calendar value within ±2%.
4. **`scripts/derive_compute_revenue.py` no functional change** — aggregator already reads quarterly array correctly. Verify summary matches Final Locked Trajectory after `--apply`.
5. **`compute.html` rendering verification:**
   - Quarterly trajectory chart shows monotonic growth Q1 25 → Q1 26 for every line
   - Hero strip Box 1 (gross post-Copilot) reads ~$43.5B
   - Hero strip Box 2 (net) reads ~$42.5B
   - Hero strip Box 3 (Apps→Compute ratio) recalculates
   - Hero strip Box 4 (YoY growth) recalculates (~+150–170%)
   - **Caption beneath quarterly trajectory chart removed/rewritten** — no longer needs to apologize for AWS flatness or GOOGL dip; replace with a single methodology line: "2025 calendar sum-of-quarterlies basis; Q1 2026 anchored at disclosed run-rates ÷ 4."
6. **`methodology.html` updates:**
   - Add a paragraph explaining the calendar-basis choice (sum-of-quarterlies for Layer Stack and trajectory; annualised run-rate as separate context). Reference the derivation memo.
   - Remove or update the AWS Q4≈Q1 caption text from wq-091.
7. **`scripts/validate-compute-revenue.mjs` updates:**
   - Add assertion: per-provider Q1 26 quarterly value > Q4 25 quarterly value (no Q-o-Q drops).
   - Tie-out tolerance ±2% per provider on new calendar totals.

### Out of scope

- Changing the segment framework, frontier-lab definition, or naming convention from wq-091.
- Re-litigating Copilot scope-out values (just rescale per quarter).
- Capital Ledger / Apps Ledger work.
- Sankey / Revenue Ledger changes (wq-090 still independent).
- The annualised run-rate numbers ($28B MSFT, $10B AMZN, $7B GOOGL) — preserved as context fields.

---

## Files touched

### Modified
- `data/compute_disclosures.json` — quarterly array per provider, calendar field updates, segment allocations rescaled, new `value_2025_annualised_run_rate_basis_usd_b` field per provider.
- `compute.html` — caption beneath trajectory chart updated/removed.
- `methodology.html` — calendar-basis paragraph added.
- `scripts/validate-compute-revenue.mjs` — new no-Q-o-Q-drop assertion.
- `site-data.json` — regenerated by `derive_compute_revenue.py --apply`.

### Read-only references
- `docs/decisions/resolved/dec-2026-05-06-compute-ledger-bucket-sizing.md` — derivation rationale (will be appended in this brief's deployment record).
- `docs/briefs/wq-091-compute-ledger-bucket-sizing-correction.md` — parent; framework still holds.
- `docs/deployments/deploy-2026-05-06-wq-091-compute-ledger-segment-sizing-correction.md` (when written) — what wq-091 shipped.

### New
- None.

---

## Implementation outline

1. **Branch off main** as `wq-092-compute-ledger-trajectory-no-qoq-drops`. Single PR.
2. **Phase 1 — restate quarterly arrays.** For each provider in `data/compute_disclosures.json`, replace the five quarterly values per Final Locked Trajectory above. Commit per provider.
3. **Phase 2 — restate 2025 calendar fields per provider.** Update `value_*_2025_*` fields to sum-of-quarterlies basis (MSFT $25.25B, AMZN $10B, GOOGL $7B, ORCL $2.95B, neoclouds $6.05B aggregate). Add new `value_2025_annualised_run_rate_basis_usd_b` field per provider preserving the run-rate-basis number. Document basis choice in `segment_basis`. Commit.
4. **Phase 3 — rescale per-provider segment allocations.** Frontier lab compute / AI workload compute / Hosted model APIs / Copilot per provider adjust proportionally so each provider's segments sum to new calendar value. Tie-out within ±2%. Commit.
5. **Phase 4 — apply aggregator.** Run `python3 scripts/derive_compute_revenue.py --apply`. Verify `--print-summary` shows:
   - 2025 quarterly TOTAL Q1: ~$8.05B / Q2: ~$11.12B / Q3: ~$14.47B / Q4: ~$17.61B / Q1 26: ~$19.04B
   - Compute gross post-Copilot 2025: ~$43.5B
   - Compute net 2025: ~$42.5B
   - Per-provider Q1 26 > Q4 25 (no drops anywhere)
6. **Phase 5 — page edits.** Update `compute.html` chart caption (per D5: simple "2025 calendar sum-of-quarterlies basis; Q1 2026 anchored at disclosed run-rates ÷ 4"). Verify hero strip + WWHBT + Layer Stack render correctly with new numbers.
7. **Phase 6 — methodology page.** Add a short paragraph (~100 words) explaining the calendar-basis choice. Reference derivation memo.
8. **Phase 7 — validator update.** Add no-Q-o-Q-drop assertion to `validate-compute-revenue.mjs`.
9. **Phase 8 — release-check.** `npm run build-lint` + `npm run release-check`. Re-baseline visual snapshots (trajectory chart line shapes change; hero numbers shift slightly).
10. **Phase 9 — deployment record** at `docs/deployments/deploy-2026-05-XX-wq-092-compute-ledger-trajectory-no-qoq-drops.md`. Cross-reference wq-091's deployment record as parent.

---

## Acceptance criteria

- [ ] `data/compute_disclosures.json` quarterly arrays match Final Locked Trajectory per provider within ±0.05B.
- [ ] Per-provider 2025 calendar values restated to sum-of-quarterlies basis; new `value_2025_annualised_run_rate_basis_usd_b` field preserves annualised reference.
- [ ] Per-provider segment allocations sum to new calendar value within ±2%.
- [ ] `derive_compute_revenue.py --print-summary` shows: Compute gross ~$43.5B, Compute net ~$42.5B, per-provider Q1 26 > Q4 25 everywhere (no drops).
- [ ] `/compute.html` quarterly trajectory chart renders with monotonic growth on every provider line.
- [ ] Hero strip Box 1 (gross) ~$43.5B; Box 2 (net) ~$42.5B; Box 3 (ratio) recalculates; Box 4 (YoY) ~+150–170%.
- [ ] Caption beneath trajectory chart updated per D5 (simpler methodology line; no AWS flatness/GOOGL dip apologetics).
- [ ] `/methodology.html` has new paragraph explaining sum-of-quarterlies vs annualised basis choice.
- [ ] `validate-compute-revenue.mjs` includes no-Q-o-Q-drop assertion; passes.
- [ ] `npm run build-lint` passes; `npm run release-check` passes with new baselines.
- [ ] Deployment record cross-references wq-091's record as parent.

---

## Test plan

1. **Aggregator tie-out.** `--print-summary` matches Final Locked Trajectory; per-provider segment sums tie to new calendar totals within ±2%.
2. **No-Q-o-Q-drop assertion.** New validator check: for each provider, `quarterly_value[Q1_2026] >= quarterly_value[Q4_2025]`. Asserts no future regression.
3. **Visual snapshot.** Re-baseline `/compute.html` quarterly trajectory chart — line shapes change (no flatlines, no drops). Take baselines on desktop + iPhone + Android viewports.
4. **Build lint.** `npm run build-lint` — provenance fields preserved.
5. **Manual page audit.** Read `/compute.html`. The trajectory chart story should match the +123% YoY MSFT / +170% Bedrock Q-o-Q / +800% YoY GOOGL gen AI growth narratives without apology captions.

---

## Edge cases

- **Tie-out tolerance.** Per-provider segment sums to new calendar values must hit ±2%. If a provider misses, write `docs/decisions/open/` decision file; do not silently re-tune.
- **Annualised vs sum-of-quarterlies framing on methodology page.** Be careful to explain WHY both numbers exist and which is used where. Reader should see: "MSFT annualised AI run-rate basis: $28B (Microsoft self-disclosed) / MSFT 2025 calendar (sum of four reported quarters): ~$25.25B. Layer Stack and trajectory chart use sum-of-quarterlies; the run-rate number is shown as context." Don't bury this.
- **GOOGL Q1 26 raised from $2.50B to $3.00B** — re-derived from "+800% YoY on gen AI products" narrative back-cast. Tier 2A. Document in `segment_basis`.
- **AMZN Q-o-Q tightness.** AMZN Q4 25 ($3.60B) → Q1 26 ($3.75B) is +4%, modest growth. This is honest given Jassy's run-rate disclosure ties Q1 26 to $3.75B exactly. If we wanted more growth, we'd need to lower Q4 25 further (dropping 2025 calendar below $10B), which the brief avoids.
- **2024 reference number unchanged from wq-091** ($15–18B). Doesn't need restatement — already on a different basis.

---

## §11 Reconciliation

| wq-092 figure | Matching figure | Expected | Bridge |
|---|---|---|---|
| Compute gross 2025 ~$43.5B (sum-of-Q basis) | wq-091 shipped ~$45.55B (annualised basis) | wq-092 lower because sum-of-quarterlies basis | Switch from annualised run-rate basis to sum-of-quarterlies basis lowers calendar 2025 by ~$2-3B because growth accelerated through 2025 (sum < exit-rate × 4). |
| Per-provider Q1 26 quarterly | Disclosed run-rate ÷ 4 (where available) | Equal | MSFT $9.25 = $37B/4; AMZN $3.75 = $15B/4. GOOGL $3.00 = back-cast from "+800% YoY narrative" (Tier 2A). |
| Hosted model APIs pass-through 2025 ~$1B | wq-090 Hyperscalers channel reconciliation target | Unchanged from wq-091 | Hosted model APIs total barely moves under wq-092 (2-3% lower); wq-090 reconciliation target unaffected. |
| All other figures (Layer Stack apps, Copilot scope-out, etc.) | wq-091 values | Marginally lower (sum-of-Q basis) | Proportional rescale; no editorial change. |

---

## Definition of done

- All acceptance criteria checked.
- Brief copied to `docs/briefs/wq-092-compute-ledger-trajectory-no-qoq-drops.md`.
- Derivation memo updated with wq-092 trajectory rationale (append paragraph).
- Deployment record cross-references wq-091 as parent.
- Notion card moved to Done.

---

## Handoff prompt for VS Code / Claude Code

> Implement wq-092 per `docs/briefs/wq-092-compute-ledger-trajectory-no-qoq-drops.md`.
>
> This is a deploy correction to wq-091. Single issue: wq-091 shipped a quarterly trajectory where MSFT (–12%), AMZN (flat), and GOOGL (–32%) all show Q4 2025 ≥ Q1 2026. Visually contradicts the AI growth narrative (+123% YoY MSFT, etc.). wq-092 fixes by switching the 2025 calendar basis from annualised run-rate to sum-of-quarterlies, allowing each provider's quarterly trajectory to grow monotonically into Q1 26.
>
> All five decisions (D1–D5) resolved at the top of the brief.
>
> Work the §"Implementation outline" — nine phases, single PR. Phase 1 (quarterly array restatement per Final Locked Trajectory table) is the load-bearing piece; everything else flows.
>
> Constraints:
> - Do NOT change segment framework, frontier-lab definition, naming convention from wq-091.
> - Per D2: every major provider must show Q1 26 > Q4 25. Zero tolerance for Q-o-Q drops on the chart.
> - Per D5: remove the AWS-flatness and GOOGL-backlog captions from `/compute.html`. Replace with a single methodology line.
> - New validator assertion (no Q-o-Q drops) becomes a permanent check.
>
> When finished:
> - Append "Shipped: <date>, commit <sha>" footer to brief.
> - Write `docs/deployments/deploy-2026-05-XX-wq-092-compute-ledger-trajectory-no-qoq-drops.md`. Cross-reference wq-091's deployment record as parent.
> - Move Notion wq-092 card to Done.

---

## Change log

- 2026-05-06 — drafted in Cowork after wq-091 shipped trajectory with Q4→Q1 drops on MSFT (-12%), AWS (flat), GOOGL (-32%). D1–D5 confirmed in same session. Single-PR follow-up.

---

Shipped: 2026-05-06, commit 5170a59
