---
id: wq-089
title: Compute Ledger v2 — bucket decomposition, Copilot scope-out, pass-through correction
stage: Scoped
priority: H
owner: Simon (impl: Claude Code in VS Code)
created: 2026-05-06
status: ready_for_handoff
parent_context: /Users/simonbowker/Documents/Claude/Projects/The AI Ledger/ (Cowork session 2026-05-06 — Compute Ledger review)
parent_brief: /Users/simonbowker/Developer/apac-ai-intel/docs/briefs/wq-087-compute-ledger.md
companion_brief: wq-090 — Revenue Ledger Hyperscaler & Who Pays adjustments (depends on this)
---

# wq-089 · Compute Ledger v2 — bucket decomposition, Copilot scope-out, pass-through correction

## Why this brief exists

Cowork review session 2026-05-06 stress-tested the Compute Ledger (`/compute.html`, shipped under wq-087) against the Revenue Ledger and against published hyperscaler economics. Three editorially load-bearing problems surfaced:

1. **Pass-through is overstated by ~10×.** The current page shows model-lab pass-through 2025 = $11.5B. Bottom-up bucket sizing puts the real number at ~$1B. The math in `data/compute_disclosures.json` applies pass-through % to *total* hyperscaler AI revenue — but pass-through only exists on the token-API portion (Bedrock + Azure OpenAI Service + Vertex partner-served), which is a small slice (~$3.5–5.5B 2025 ecosystem).
2. **Copilot is double-counted between Compute and the (eventual) Apps Ledger.** MSFT's $28B 2025 annualised AI line includes ~$4–8B of Copilot products (M365 Copilot, GitHub Copilot, Copilot Studio). These are per-seat productivity SaaS, not Compute. They belong in Apps/Model Revenue, not on the Compute Ledger. The disclosures file's notes acknowledge this but include them anyway with a footnote.
3. **The Layer Stack visual uses an editorial $100B Apps Revenue figure** ($17.4B Revenue Ledger cohort × 5× extension multiplier, "to enterprise SaaS AI ARR"). The 5× is editorial Tier 2A with no provenance trail. The ratio swings ±25% on this single constant. Worse, the Apps figure is ARR-style while the Compute figure is "2025 annualised" hybrid — apples-to-oranges in both scope and time-basis.

These three problems interact. Fixing pass-through requires bucket decomposition. Bucket decomposition exposes that Copilot belongs elsewhere. Once Copilot is stripped and pass-through is corrected, the Layer Stack's editorial point shifts from "$100B Apps → $41B Compute" (smoothed by an editorial multiplier) to "$17.4B measured cohort → $58–62B Compute Net → $165B Silicon" (asymmetric, but the asymmetry IS the story — circular financing made visible).

This brief is the editorial restructure plus the data corrections.

## Decisions Simon has made (do not re-litigate without flagging)

| # | Decision | Confirmed |
|---|---|---|
| D1 | **Bucket decomposition** is the spine. Three buckets: (1) Frontier lab compute, (2) AI workload compute (non-frontier — AI Natives + enterprise + model-serving cos as customers), (3) Token API (Bedrock + AOAI + Vertex partner-served). Pass-through % applies to bucket 3 only. | 2026-05-06 |
| D2 | **Copilot products are scoped OUT of Compute.** Strip Copilot-class revenue (M365 Copilot, GitHub Copilot, Copilot Studio for MSFT; equivalent for GOOGL Gemini-in-Workspace; equivalent embedded-AI-feature lines for AMZN). Estimate from public disclosures, deduct from each provider's AI line. These eventually flow to a future Apps Ledger; for now, they're tracked separately on the methodology page. | 2026-05-06 |
| D3 | **Layer Stack switches to lookback 2025 actuals across all four layers.** Apps = measured cohort total (~$17.4B, Tier 1A-derived from Revenue Ledger). Compute = sum-of-quarterlies, not "annualised hybrid." Silicon = NVIDIA Data Center FY26 calendar 2025 + AMD MI300/MI350 + custom ASIC. Power = current Tier 3C placeholder. **All four layers on the same time-basis.** | 2026-05-06 |
| D4 | **Hero strip:** drop Box 4 (Q1 2026 share shift, a redistribution metric on a market growing 80–120% YoY is near-useless). Replace with **YoY growth headline** (Compute Revenue gross 2025 vs 2024, %). Keep Box 1 (gross), Box 2 (net), Box 3 (Apps→Compute ratio, recalculated against measured cohort). | 2026-05-06 |
| D5 | **Editorial spine recast.** Current page leads on gross/net split + concentration. Corrected page leads on **frontier-lab-compute circular financing** (Model Providers paying hyperscalers ~$25–40B, who report it as AI revenue, while labs are funded partly by hyperscaler equity and partly by selling tokens that re-route compute back). The gross/net distinction stays but is no longer the headline — it's a smaller layer of the story. | 2026-05-06 |
| D6 | **Reconciliation gate added to brief structure** (see §11 and parallel CLAUDE.md update). Every aggregate published on the Compute Ledger must have a §Reconciliation entry naming any other Ledger number describing overlapping reality, with the bridge math. | 2026-05-06 |
| D7 | **wq-089 ships before wq-090.** Compute Ledger corrections happen first; Revenue Ledger reads off the corrected bucket 3 number and adjusts channel weights to land at the same figure. | 2026-05-06 |
| D8 | **Frontier lab roster reuses the Usage Ledger Model Provider taxonomy** — no separate definition. The canonical list is in `usage.html`: `frontierProvs = ['openai','anthropic','google','xai','bytedance','tencent','baidu','minimax','moonshot']` plus `openProvs = ['meta','deepseek','mistral','alibaba','qwen','own','self-hosted','others']`. Bucket 1 sums external compute spend by **any** Model Provider — providers with internal infra (Google on TPUs, Meta on own DC) contribute $0; Chinese labs running on Chinese hyperscalers contribute $0 in Mag3-economy bucket 1. **Microsoft is NOT a Model Provider** — it's a hyperscaler that runs OpenAI's models and ships Copilot apps; MAI is too small to qualify. Synced with wq-090's `entity_archetype: frontier_lab` enum. | 2026-05-06 |
| D9 | **Internal vs public-facing labels.** ⚠ **SUPERSEDED 2026-05-06 by wq-091 D8** — see `docs/briefs/wq-091-compute-ledger-bucket-sizing-correction.md`. The original D9 here allowed "Bucket 1/2/3" as engineering shorthand in schema fields and code variables; wq-091 D8 drops that exception and applies plain-English naming everywhere (page, methodology, briefs, JSON schema fields, deployment records). The original D9 wording was: *"Bucket 1/2/3" stays as engineering shorthand (schema field names in `compute_disclosures.json`, variables in `derive_compute_revenue.py`, deployment records). Page copy, methodology copy, card titles, and any user-facing surface use plain English: bucket 1 → "Frontier lab compute", bucket 2 → "AI workload compute", bucket 3 → "Hosted model APIs". Do NOT ship "Bucket 1" as a card title or chart label.* | 2026-05-06 |

## Open decisions — none

All decisions resolved in the 2026-05-06 Cowork session.

---

## Scope

### In scope

1. **Schema migration on `data/compute_disclosures.json`.** Add three sub-amount fields per component (frontier_lab_compute, non_frontier_workload_compute, token_api) with gross/net split on token_api. Keep existing fields for backward-compat during migration; remove after `derive_compute_revenue.py` is updated.
2. **Re-source bucket sizing per hyperscaler component**, anchored against bottom-up evidence (per-lab revenue × cloud-mix; AOAI/Bedrock/Vertex revenue triangulated against OpenAI/Anthropic rev-share economics). Document each estimate in the disclosures file's `pass_through_basis` field renamed to `bucket_basis`.
3. **Copilot scope-out.** Identify and deduct Copilot-class revenue from each Mag3 component. Add a `copilot_excluded_usd_b` field per component for transparency. The deducted total appears on the methodology page as "tracked-but-excluded; flows to Apps Ledger when that is built."
4. **Pass-through correction.** Recalculate as `bucket 3 × lab_rev_share` (per-component lab rev-share %; default 25% blended where unknown). New 2025 ecosystem total: ~$1B central, ~$0.8–1.5B range. Replace existing $11.5B figure throughout.
5. **`scripts/derive_compute_revenue.py` rewrite.** Aggregator must read new schema fields, sum gross / net / pass-through correctly, expose bucket 1 as a first-class aggregate, and update the D6 verification gate to include "Copilot scope-out applied per D2" and "pass-through scoped to bucket 3 per D1."
6. **Hero strip update on `compute.html`.** Drop Box 4 (share-shift); replace with YoY growth headline on Box 4 (Compute gross 2025 / Compute gross 2024, %). Recalculate Box 3 (Apps→Compute) against new Layer Stack basis (measured cohort apps + sum-of-quarterlies compute). Adjust Box 2 (Net) — number drops materially (from $41B to ~$58–62B once pass-through corrected).
7. **Layer Stack visual update.** Switch all four layers to lookback 2025 actuals on the same time basis. Apps = measured cohort `totalCustomerRevenue` from `site-data.json:sankey` (~$17.36B as of 2026-05-06). Compute = sum-of-quarterlies (~$60–65B gross after Copilot scope-out, ~$58–62B net). Silicon = $165B (already lookback). Power = $25B placeholder (unchanged).
8. **Add bucket 1 as a visible page element.** New card titled **"Frontier lab compute"** (per D9 — never "Bucket 1") surfacing the circular-financing line. Show 2025 lookback total (~$25–40B per D8 — narrower than the original $45–50B once Google/Meta/Chinese labs are correctly counted at $0). Per-lab attribution where defensible: OpenAI→Azure (dominant share), Anthropic→AWS+GCP, xAI→external, Mistral→GCP+others; Google ($0, internal TPUs), Meta ($0, internal infra), and DeepSeek/Chinese labs ($0 in Mag3 economy) shown explicitly as "internal infra — no external hyperscaler spend." This becomes the editorial spine per D5.
9. **WWHBT panel update.** "Pass-through gap" signal recalibrates against new pass-through total. "Compute Revenue covers Mag7 AI capex" updates against new Compute gross. Add new signal: "Bucket 1 / Compute Revenue ratio" — what fraction of compute revenue is the frontier-lab-compute self-loop vs external customer dollars.
10. **Methodology page update.** Document the three-bucket model, the Copilot scope-out rule, the pass-through-applies-to-bucket-3-only rule, and the bridge from cohort Apps to ecosystem Apps (the latter explicitly flagged as a future scope, not on the Compute page).
11. **Reconciliation section** (per D6) added to this brief and verified at acceptance: every aggregate on the corrected page lists its counterpart Ledger number and the bridge math. See §11.

### Out of scope

- Building a separate ecosystem-wide Apps Revenue tracker (the corrected $17.4B is cohort; the wider Apps universe is a future Ledger). Note the gap; don't fill it.
- Sankey/Revenue Ledger channel weight corrections — that's wq-090, ships after this.
- Power Ledger v3 (`wq-006`) — Power figure stays as Tier 3C placeholder.
- Any change to the "principal-everywhere" D6 verification gate from wq-087 — accounting treatment confirmation stays as-is.
- Building a model-serving sub-layer (Baseten/Modal/Together/Fireworks) as its own Ledger view — note their existence on the methodology page; defer.
- Changing the cohort itself (the 9-source / 17-source debate is wq-081 territory, not this brief).

---

## Files touched

### Modified
- `data/compute_disclosures.json` — schema migration (bucket sub-amounts per component); re-sourced bucket figures; Copilot deduction field added; `pass_through_basis` renamed to `bucket_basis` and rewritten per component.
- `scripts/derive_compute_revenue.py` — aggregator rewritten for new schema; bucket 1 surfaced as first-class output; pass-through corrected to bucket 3 only; D6 gate text updated.
- `compute.html` — Hero strip Box 4 swap (share-shift → YoY growth); Box 3 recalculation; Layer Stack lookback basis; new Bucket 1 card; WWHBT signals refreshed.
- `data/methodology_constants.json` — note on the three-bucket model in `compute_revenue` block.
- `methodology.html` — three-bucket explainer; Copilot scope-out rule; pass-through rule; cohort-vs-ecosystem Apps note.
- `site-data.json` — regenerated by `derive_compute_revenue.py --apply` after the changes above; aggregate values shift materially. **This is expected. Do not roll back.**

### Read-only references
- `site-data.json:sankey.totalCustomerRevenue` (~$17.36B) — Apps figure for Layer Stack.
- Per-lab 2025 revenue figures (Anthropic ~$4.71B, OpenAI ~$12–13B calendar) — from existing entity files; do not re-derive.
- NVIDIA Data Center FY26 disclosure — already on Capital Ledger / methodology constants.

### New
- None — all changes are migrations of existing files.

---

## Implementation outline

1. **Branch off main** as `wq-089-compute-ledger-v2`. Single PR, single shipment.
2. **Phase 1 — schema migration on disclosures file.** Add new bucket fields per component without removing old fields yet. Populate from current data so old aggregator still works. Commit.
3. **Phase 2 — bucket re-sourcing.** For each Mag3 + Oracle component:
   - **Bucket 1 (frontier lab compute):** estimate from per-lab revenue × cloud share (OpenAI ~85% Azure, Anthropic ~80% AWS+GCP split, Mistral mixed, smaller labs). Cite in `bucket_basis` field with `tier` (default 2A).
   - **Bucket 2 (non-frontier workload):** residual after bucket 1 + Copilot deduction; cross-check against AWS/GCP IaaS-AI disclosures where available.
   - **Bucket 3 (token API):** independently sized — Bedrock ~$2–3B (Anthropic-via-Bedrock + minor partners), AOAI ~$1–1.5B (enterprise-only at realistic token spend), Vertex ~$0.5–1B. Document each in `bucket_basis`. Apply lab rev-share % to compute pass-through.
   - Tie out: bucket 1 + bucket 2 + bucket 3 + Copilot deducted = original gross AI line. If they don't tie within ±5%, flag and document the residual.
   - Commit per provider for cleaner review.
4. **Phase 3 — aggregator rewrite.** `derive_compute_revenue.py` reads new fields, computes:
   - `bucket_1_2025_usd_b`, `bucket_2_2025_usd_b`, `bucket_3_gross_2025_usd_b`, `bucket_3_pass_through_2025_usd_b`, `bucket_3_net_2025_usd_b`
   - `compute_revenue_2025_gross_usd_b` = bucket 1 + bucket 2 + bucket 3 gross  (Copilot already excluded)
   - `compute_revenue_2025_net_usd_b` = gross − bucket 3 pass-through
   - `model_pass_through_2025_usd_b` = bucket 3 pass-through total (~$1B)
   - Same for Q1 2026 quarter.
   - D6 gate text updated. Commit.
5. **Phase 4 — apply to site-data.** Run `python3 scripts/derive_compute_revenue.py --apply`. Verify the printed summary matches expected ranges (gross ~$60–65B, net ~$58–62B, pass-through ~$1B, bucket 1 ~$45–50B). Commit `site-data.json`.
6. **Phase 5 — page edits.** Hero strip swap (Box 4 share-shift → YoY); Layer Stack lookback basis; new Bucket 1 card; WWHBT updates. Commit.
7. **Phase 6 — methodology page.** Three-bucket explainer, Copilot rule, pass-through rule. Commit.
8. **Phase 7 — release-check.** `npm run build-lint` + `npm run release-check` + visual snapshot update for `/compute.html` and `/methodology.html`. The Layer Stack visual will look materially different — that is the intended change. Take new baselines.
9. **Phase 8 — write deployment record** at `docs/deployments/deploy-2026-05-XX-wq-089-compute-ledger-v2.md` per CLAUDE.md convention.

---

## Acceptance criteria

- [ ] `data/compute_disclosures.json` has new bucket fields per component; old fields removed; `bucket_basis` documents each estimate with tier.
- [ ] `scripts/derive_compute_revenue.py --print-summary` outputs:
  - Bucket 1 (frontier lab compute) 2025: ~$40–55B
  - Bucket 2 (non-frontier workload) 2025: ~$3–10B
  - Bucket 3 (token API) gross 2025: ~$3–6B
  - Bucket 3 pass-through 2025: ~$0.7–1.5B
  - Compute Revenue gross 2025: ~$55–70B (down from $73B)
  - Compute Revenue net 2025: ~$54–69B (UP from $41.45B because pass-through was overstated)
  - Copilot excluded total 2025: ~$8–14B
- [ ] Hero strip on `/compute.html` shows: gross, net, Apps→Compute ratio (recalculated against cohort apps), YoY growth (new Box 4). Share-shift box is gone.
- [ ] Layer Stack visual on `/compute.html` shows all four layers on lookback 2025 actuals with consistent labels. Apps Revenue label reads "Measured cohort — Revenue Ledger basis $17.36B" (or whatever the live `totalCustomerRevenue` is at build time).
- [ ] New "Bucket 1 — frontier lab compute" card on `/compute.html` shows the ~$45–50B figure with per-lab attribution where defensible.
- [ ] WWHBT panel updated: pass-through signal recalibrated (now < 5% of gross, was 22%); new bucket-1-share signal added.
- [ ] Methodology page (`/methodology.html`) has a §"Compute Ledger — three-bucket model" section explaining buckets 1/2/3, the Copilot scope-out rule, the pass-through rule, and the cohort-vs-ecosystem Apps gap.
- [ ] **Reconciliation section verified** (see §11): every aggregate on the corrected Compute Ledger page has a documented bridge to the matching Revenue Ledger number, OR an explicit "no counterpart, scoped only on Compute Ledger" flag.
- [ ] `npm run build-lint` passes; `npm run release-check` passes (with new visual baselines for `/compute.html` and `/methodology.html`).
- [ ] Deployment record at `docs/deployments/` captures the bucket sizes chosen, the Copilot deduction per provider, and any tactical decisions made.

---

## Test plan

1. **Aggregator unit test.** Add `tests/test_derive_compute_revenue.py` covering: schema migration round-trip, bucket sum tie-out (buckets + Copilot = original gross within ±5%), pass-through scoped to bucket 3 only, D6 gate failure case (if any provider isn't principal-treatment-confirmed).
2. **Visual snapshot.** Re-baseline `/compute.html` and `/methodology.html` Playwright snapshots. The Layer Stack will look different (taller Compute and Silicon bars relative to a much smaller Apps bar). Verify on desktop + iPhone + Android viewports.
3. **Reconciliation cross-check.** Manual: open `/compute.html` and `/revenue.html` side by side after wq-089 ships (and before wq-090). Verify the Compute pass-through (~$1B) and Revenue Hyperscalers channel ($3.63B as-is) — gap of ~$2.6B is documented in §11 as "wq-090 will close this." Once wq-090 ships, verify the gap closes to <$0.5B.
4. **Build lint.** `npm run build-lint` must pass — provenance fields preserved on every changed component.
5. **Release-check screenshots** of the rendered Layer Stack at 800×400 verify it's still screenshot-quotable per wq-087 D2 carry-over.

---

## Edge cases

- **Copilot scope-out for AMZN.** Less obvious than MSFT/GOOGL — AWS doesn't have a "Copilot product" per se but does have AI features embedded in non-AI products. Default: deduct nothing for AMZN unless a specific embedded-AI line is identifiable in 10-Q.
- **Per-lab cloud-share data.** OpenAI→Azure is well-documented; Anthropic→AWS+GCP split is partly disclosed; Mistral and smaller labs are inferred. Where inference is required, set tier 2B and document the basis.
- **AOAI rev-share** assumed 20% (Zitron-leaked methodology). If the leak is wrong by ±10pp, pass-through swings ±$0.2B — not material at the headline level. Document tier 2A.
- **Tie-out failure.** If buckets + Copilot don't sum to the original gross AI line within ±5% for any provider, write a `docs/decisions/open/` decision file documenting the residual and asking Cowork to resolve. Don't paper over.
- **VC subsidy and circular-financing math.** Bucket 1 surfaces "frontier labs paying hyperscalers" — but a portion of that is *re-routed VC + hyperscaler equity money*. Don't try to net this out on the Compute Ledger; flag on the methodology page that bucket 1 is gross of equity-funded inflows. Capital Ledger is the place to net it; that's a future cross-Ledger concern.
- **Mistral / xAI / DeepSeek / Cohere** — smaller labs with thin disclosure. Group as "Other frontier" within bucket 1 if individual sizing is too speculative.

---

## Definition of done

- All acceptance criteria checked.
- This brief copied to `docs/briefs/wq-089-compute-ledger-v2.md` in the repo (already done at handoff).
- Deployment record written.
- Notion card for wq-089 moved to Done. (If Cowork doesn't have Notion access at deploy time, note in deployment record that the card needs updating.)
- Companion brief wq-090 unblocked (it's `addBlockedBy: wq-089` and reads off the bucket 3 figure and corrected channel mappings).

---

## §11 Reconciliation (per D6 / new CLAUDE.md rule)

Every aggregate published on the corrected Compute Ledger must list any other Ledger number describing the same or overlapping reality, with a bridge.

| Compute Ledger figure (post-wq-089) | Matching Ledger figure | Expected relationship | Bridge |
|---|---|---|---|
| Bucket 3 pass-through 2025 (~$1B) | Revenue Ledger Hyperscalers channel × (1 − channel margin) | Equal at the cohort-subset level; Compute is ecosystem total | Compute pass-through = ecosystem-wide; Revenue Ledger Hyperscalers (corrected per wq-090) ≈ cohort subset of bucket 3 customers. Gap = non-cohort enterprise spend. **wq-090 corrects Revenue Ledger api_pct/enterprise_pct weights so the cohort-side flow drops to ~$1.2–1.6B; gap to Compute pass-through becomes ~$0–0.5B (within tier 2A noise).** |
| Compute gross 2025 (~$60–65B) | None — this is the ecosystem-wide compute layer, not present on Revenue Ledger | Disjoint scope | Revenue Ledger only sees customer-paid dollars from the cohort, not provider-recognised AI revenue. No bridge needed; flag explicitly on methodology. |
| Bucket 1 (~$45–50B) | Future Capital Ledger circular-financing analysis | Bucket 1 ⊂ Capital Ledger AI capex, partly | Some of bucket 1 is funded by hyperscaler equity in labs (e.g. MSFT→OpenAI). Capital Ledger should show this on the equity-investment side. wq-089 surfaces bucket 1; future capital-side cross-ref happens on a separate brief. |
| Apps Revenue on Layer Stack ($17.36B) | Revenue Ledger `totalCustomerRevenue` ($17.36B) | Identical | Layer Stack pulls live from `site-data.json:sankey.totalCustomerRevenue`. Reconciles by construction. |
| Copilot excluded total (~$8–14B) | Future Apps Ledger | Will be subset of Apps Ledger when built | Tracked on methodology page only until Apps Ledger is built; flagged as "out of scope for current Ledger views." |

---

## Handoff prompt for VS Code / Claude Code

> Implement wq-089 per `docs/briefs/wq-089-compute-ledger-v2.md`.
>
> This is an editorial restructure plus data correction on the Compute Ledger (`/compute.html`). Three load-bearing problems are fixed: (1) pass-through was overstated ~10× because it was applied to total AI revenue instead of bucket 3 only, (2) Copilot is double-counted between Compute and Apps and should be scoped out, (3) Layer Stack used a fabricated $100B Apps figure (5× editorial multiplier on cohort) and is being switched to lookback 2025 measured cohort.
>
> Work the §"Implementation outline" in order — it's eight phases, single PR, single shipment. The schema migration (Phase 1) and bucket re-sourcing (Phase 2) are the load-bearing technical pieces; everything downstream falls out cleanly once those are right.
>
> All seven decisions (D1–D7) are resolved at the top of the brief — do not re-litigate.
>
> Constraints:
> - Use `--print-summary` after each aggregator change to verify ranges before applying to site-data.
> - Validate rendered output (per CLAUDE.md): the Playwright spec must visit `/compute.html` and assert on rendered DOM, not just check that `derive_compute_revenue.py` reports correct numbers.
> - The Layer Stack visual will look very different after this change — Compute and Silicon bars get much taller relative to Apps. That's the intended editorial point. Take new visual baselines.
> - The §11 Reconciliation table is part of acceptance criteria — verify each row before declaring done.
> - If a per-provider tie-out fails (buckets + Copilot ≠ original gross within ±5%), do NOT paper over — write a `docs/decisions/open/dec-2026-05-XX-wq-089-tie-out-residual.md` and stop that branch.
>
> When finished:
> - Append a "Shipped: <date>, commit <sha>" footer to this brief.
> - Write `docs/deployments/deploy-2026-05-XX-wq-089-compute-ledger-v2.md` per CLAUDE.md.
> - Move Notion wq-089 card to Done (or note in deployment record if access isn't available).
> - wq-090 (Revenue Ledger Hyperscaler & Who Pays) is now unblocked — its brief is at `docs/briefs/wq-090-revenue-ledger-hyperscaler-and-who-pays.md`. Do not start it in this session; new session preferred for clarity.

---

## Change log

- 2026-05-06 — drafted in Cowork following two-hour stress-test of the Compute Ledger against Revenue Ledger and against published hyperscaler economics. D1–D7 confirmed in same session. Ready for repo handoff.

---

**Shipped: 2026-05-06, commit a43a9fb** — bucket decomposition, Copilot scope-out, and pass-through correction landed on /compute.html. Layer Stack switched to lookback 2025 actuals with live cohort apps. Methodology page documents the three-bucket model + Copilot rule + cohort-vs-ecosystem gap. Deploy record at `docs/deployments/deploy-2026-05-06-wq-089-compute-ledger-v2.md`. wq-090 unblocked.

**Companion shipped: 2026-05-07, commit edad551 (PR #5 merged as dffcaff)** — wq-090 (Revenue Ledger Hyperscaler & Who Pays) landed on `/revenue.html`. Hyperscalers channel corrected $3.63B → $1.70B; Who Pays relabeled to Consumer / AI Natives / Enterprises & Govs / VC-Investors; AI Natives buyer-provider split (45/45/10 to OpenAI/Anthropic/Google) surfaced in a new panel below the Sankey. §11 reconciliation now end-to-end: Compute Hosted-model-APIs pass-through ~$1.0B reconciles with Revenue Hyperscalers chPass ~$1.36B within Tier-2A noise. Deploy record at `docs/deployments/deploy-2026-05-07-wq-090-revenue-ledger-archetype.md`.
