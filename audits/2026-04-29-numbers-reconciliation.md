# 5-numbers reconciliation — wq-033 P5

**Date:** 2026-04-29
**Owner:** Track A (Claude Code in `apac-ai-intel`)
**Brief:** [briefs/active/2026-04-27-ha-references-design.md §4.5](../briefs/active/2026-04-27-ha-references-design.md)
**Methodology lock:** [briefs/active/2026-04-27-cross-launch-spec.md §4.5](../briefs/active/2026-04-27-cross-launch-spec.md) — Revenue uses Ledger collected-revenue methodology; Anthropic = court-derived ~$4.5B (NOT Dario exit-ARR ~$9–10B). ±$2B tolerance from HA's $22B.
**Status:** **LAUNCH-BLOCKING FINDINGS** — F1 and F2 below. Per Simon's instruction, halting before any further chaining.

---

## Audit table

| # | Metric | HA value | Ledger field path | Ledger value | Match? | Provenance source | Notes |
|---|---|---|---|---|---|---|---|
| 1 | Capital committed | $745B | _no canonical field_ | $745B (hardcoded in `capital.html` JS) | ⚠ MISSING | `capital.html:440-442` (`base.totalCapex:745`) + body literals | F3 — HA and capital.html agree on the value but site-data.json has no canonical anchor; closest is `globalBenchmarks.entries[hyperscaler_capex] = $350B` (top-5 hyperscalers only, ~47% of HA's claim) |
| 2 | Revenue booked | $22B | `sankey.totalCustomerRevenue` | $17.47B | ✗ DIVERGE | `site-data.json` `sankey.title = "2025 Actual Revenue Collected"`; `meta.notes = "Fully rebalanced from consensus. All flows verified."` | **F1 — LAUNCH-BLOCKING.** $4.53B gap (26% above Ledger), exceeds ±$2B tolerance. Ledger field is correctly labelled "Collected" per the lock but the aggregate is materially below HA. |
| 2a | …Anthropic component | (HA does not break out) | `sankey.providers[1].value` | $7.71B | ✗ DIVERGE | sankey.providers list, 2025 collected sankey | **F2 — METHODOLOGY-LOCK BREACH.** Lock target is court-derived ~$4.5B. Ledger Anthropic value $7.71B is +71% above the lock target. The sankey title says "Collected" but the Anthropic value isn't court-anchored. Note: dashboard.providers.Anthropic.rev=19.0 is a different measure (likely ARR or run-rate) — not the canonical "collected" field, but it exists in the same data file and could mislead consumers. |
| 3 | Ratio capital:revenue | 33.7:1 (≈$34:$1) | derived | depends on revenue base | ⚠ DIVERGE | derived: $745B / revenue | **F6.** HA's 33.7:1 = $745 / $22 — internally consistent for HA. Against Ledger collected ($17.47B): $745 / $17.47 = **42.6:1 (≈$43:$1)**. Against Ledger sankey provider sum ($24.66B): 30.2:1. Headline ratio depends on which revenue base — moves materially across the three options. |
| 4 | Usage | ~650T tok/day | _no canonical aggregate field_ | ~228T (provider rollup, Q1 2026) | ✗ DIVERGE | Sum of `timeline.tokenData[8]` across 14 providers = 228 (units = T tok/day per `timeline.events[0].body`: "Total market: ~18T tokens/day"). Removed methodology copy referenced 280–370T (project memory v3 token model). | **F4.** No published canonical field for "global daily token volume" in site-data.json. Timeline rollup at Q1 2026 = 228T; methodology v3 model says 280–370T; HA shows ~650T. Three different numbers, all in circulation. ~650T is ~2.8× the timeline rollup. |
| 5 | Power contracted | 92 GW | _no canonical field_ | 95 GW (hardcoded in `power.html` body) | ✗ DIVERGE | `power.html:122` body literal: "95 GW · US data centre interconnection queue · Up ~40% YoY · ERCOT + PJM filings, Q1 2026" | **F5.** site-data.json `power.projects` is empty. power.html displays 95 GW (hardcoded). HA shows 92 GW. 3 GW gap (3.3%). Within tolerance for soft alignment but inconsistent with each other. |

---

## Findings

### F1 — Revenue divergence (LAUNCH-BLOCKING)

**Status:** Material divergence beyond ±$2B tolerance. **Stop before further chaining** per Simon's launch-blocking criterion ("<$18B or >$25B").

- HA published value: **$22B**
- Ledger canonical field `sankey.totalCustomerRevenue`: **$17.47B**
- Gap: **$4.53B** (HA is 26% above Ledger)
- Lock states: Revenue uses collected-revenue methodology; the Ledger field is correctly named "totalCustomerRevenue" and titled "2025 Actual Revenue Collected" — methodology label is correct.

**Where HA's $22B comes from:** Not from `site-data.json`. It's hardcoded in the Ledger's own [capital.html](../capital.html) at line 441:
```
base:  { totalCapex:745, revenue:22, ratio:34, label:'Base case' },
```
HA appears to be sourcing $22B from this same hardcoded JS object (or has independently arrived at it). So both surfaces show $22B because they share the literal — but the canonical sankey field disagrees by $4.53B.

**Three remediation paths per brief §4.5:**
1. **HA fixes its number** to $17.47B (Ledger collected-revenue is canonical) → ratio updates to ~$43:$1, not $34:$1. Headline shifts.
2. **Ledger fixes `sankey.totalCustomerRevenue`** to align with $22B → requires either (a) widening the period to T12M ending Q1 2026 vs. CY 2025, or (b) re-pricing Anthropic / OpenAI at higher anchors, which conflicts with F2.
3. **Restate methodology** to a different aggregation (e.g. trailing-12-month ending Q1 2026 collected revenue instead of CY 2025) → may reconcile the two numbers but requires the Ledger to recompute the sankey.

**Recommendation for cross-project decision:** Path 1 (HA updates to $17.47B + ratio to ~$43:$1) is the cleanest preservation of the methodology lock. Path 3 is workable if the period definition is the real disagreement (CY 2025 vs. T12M). Path 2 is risky — re-pricing Anthropic conflicts with F2.

---

### F2 — Anthropic methodology-lock breach (LAUNCH-BLOCKING)

**Status:** Ledger's Anthropic value in the canonical "collected" sankey doesn't match the court-derived target locked in wq-035 §4.5.

- Methodology lock target (court-derived collected, per wq-035 §4.5): **~$4.5B**
- Ledger `sankey.providers[1].value` (Anthropic): **$7.71B**
- Gap: **+$3.21B** (+71% above lock target)
- Ledger has a SECOND Anthropic value: `dashboard.providers.Anthropic.rev = 19.0`. This is presumably ARR/run-rate (much higher than collected). Coexistence in the same data file is itself a labelling risk per SKILL.md hard rule #6 ("ARR and booked revenue are never interchangeable. Always label which.").

**Implications:**
- The Ledger sankey title says "Collected" but the Anthropic value isn't court-anchored. Either the source backing $7.71B isn't the court record, or the methodology lock's $4.5B figure refers to a narrower scope (e.g. specific period of court records).
- If we update sankey Anthropic from $7.71 → $4.5, the new `totalCustomerRevenue` becomes $17.47 − $7.71 + $4.5 = **$14.26B** — widening the gap with HA to $7.74B.
- The dashboard.Anthropic.rev=$19B should at minimum be relabelled as "ARR" / "run-rate" wherever it surfaces in the UI, per hard rule #6. (Phase 1 audit didn't flag any current UI surfaces consuming this field, but the field's existence in site-data.json without an explicit method label is itself a defect.)

**Recommendation for cross-project decision:** Don't quietly update sankey Anthropic to $4.5B without first deciding F1 — the two interact. If HA accepts Ledger's $17.47B (F1 path 1), then we still need to decide whether the sankey's $7.71B Anthropic is the right number or should be retargeted to $4.5B (and the rest of the sankey rebalanced). Both questions are cross-project.

---

### F3 — Capital field missing from site-data.json

**Status:** No canonical anchor field; both HA and capital.html use the same hardcoded literal $745B.

- HA value: $745B
- capital.html scenario JS (line 440-442): `bear/base/bull = 745B`
- capital.html body copy (line 198): "$745B of AI infrastructure investment, 2023–2025"
- site-data.json: no field carries 745B. Closest canonical: `globalBenchmarks.entries[hyperscaler_capex] = $350B` (top-5 hyperscalers only).

**Implication:** Both surfaces happen to agree but neither traces to a canonical Ledger field. If $745B ever needs revision, two places must be updated by hand. This is a §5.3.1 violation (cross-page consistency requires a canonical field). Out of Phase 5 scope to fix; flagging for wq-016 dataReferences cleanup.

---

### F4 — Usage volume: three different numbers in circulation

**Status:** No canonical aggregate field; three different values in three places.

- HA published: ~650T tok/day
- methodology copy (project memory v3 token model): 280–370T tok/day
- timeline rollup (sum of `timeline.tokenData[Q1 2026]` across 14 providers): ~228T tok/day
- site-data.json: no aggregate "global daily token volume" field

**Implication:** HA's 650T is ~2.8× the Ledger's published provider rollup. Ledger's own methodology page (after Phase 3) no longer asserts 280–370T (per Phase 3, hardcoded literal removed) but the underlying v3 model still produces that range, and the timeline data produces ~228T. The right fix is downstream of wq-016 — establish a canonical `dashboard.totalDailyTokens` or similar field, derive it from a defined methodology, and have HA + Ledger both consume it.

**Recommendation:** Cross-project decision needed on which methodology HA's 650T is anchored to. Possibilities: (a) HA includes internal inference not exposed via API (per the methodology page's "Token volume is a lower bound" caveat); (b) HA uses a higher-end provider sample; (c) HA's number is stale.

---

### F5 — Power: small divergence + missing canonical field

**Status:** Two surfaces, two values, no canonical anchor.

- HA value: 92 GW
- power.html body literal (line 122): 95 GW
- site-data.json `power.projects`: empty list

**Implication:** 3 GW gap (3.3%) — soft, but inconsistent. The brief at §4.5 explicitly noted "wq-012 Stream 2 may not have emitted yet" — and indeed `power.projects` is empty, so the canonical field hasn't been populated. Until wq-012 ships, the published value is whichever surface's hardcode you trust.

**Recommendation:** Pick one of {92, 95} for V2 launch (suggest 95 GW — the power.html body cites ERCOT + PJM filings as source; HA's 92 may be stale). Update HA, leave power.html as-is, document in F5 resolution.

---

### F6 — Ratio: depends on revenue base

**Status:** HA's 33.7:1 is internally consistent with HA's own $745B / $22B. Against the Ledger's collected-revenue field, the ratio shifts to ~42.6:1.

- HA: 33.7:1 (≈$34:$1) — derived from $745B / $22B
- Against Ledger collected ($17.47B): **42.6:1 (≈$43:$1)**
- Against Ledger sankey provider sum ($24.66B): 30.2:1

**Implication:** The "$34 per $1 of revenue" headline that's in the canonical Ledger ui_kit (`Claude Design - Design System/Hepburn Advisory Design System/ui_kits/ledger/index.html` line 230) and on HA's homepage materially shifts depending on F1's resolution.

If F1 resolves toward HA's $22B, ratio holds at 33.7:1.
If F1 resolves toward Ledger's $17.47B, ratio updates to ~42.6:1 — and the ui_kit annotation copy and HA homepage copy need to update.

**Recommendation:** Decide F1 first; ratio falls out automatically.

---

## Severity summary

| Finding | Severity | Action owner |
|---|---|---|
| F1 — Revenue $4.53B gap | **LAUNCH-BLOCKING** | Cross-project (Simon) |
| F2 — Anthropic methodology-lock breach | **LAUNCH-BLOCKING** | Cross-project (Simon) |
| F3 — Capital missing canonical field | wq-016 follow-up | Track A |
| F4 — Usage 3-way disagreement | wq-012 / wq-016 follow-up | Cross-project |
| F5 — Power 3 GW gap | Minor; pre-launch fix | HA-side or Ledger-side |
| F6 — Ratio derives from F1 | Resolves automatically | — |

---

## What was NOT done

Per Simon's explicit instruction:
- **No silent updates** to site-data.json or to HA's build.
- **No fixes applied** to any of F1–F6.
- **Halted before chaining to wq-034** — Phase 5 audit reports findings only; remediation is cross-project.

## Next step

Awaiting Simon's call on F1 (Revenue) and F2 (Anthropic methodology). Both are launch-blocking per the contract; neither can be resolved without a cross-project decision.
