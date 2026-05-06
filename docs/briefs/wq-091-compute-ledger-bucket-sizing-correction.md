---
id: wq-091
title: Compute Ledger — revenue segment sizing correction (deploy correction to wq-089)
stage: Scoped
priority: H
owner: Simon (impl: Claude Code in VS Code)
created: 2026-05-06
status: ready_for_handoff
parent_context: /Users/simonbowker/Documents/Claude/Projects/The AI Ledger/ (Cowork session 2026-05-06 — Compute Ledger review, post-wq-089 ship)
parent_brief: /Users/simonbowker/Developer/apac-ai-intel/docs/briefs/wq-089-compute-ledger-v2.md
derivation_memo: /Users/simonbowker/Developer/apac-ai-intel/docs/decisions/resolved/dec-2026-05-06-compute-ledger-bucket-sizing.md
companion_brief: wq-090 — Revenue Ledger Hyperscaler & Who Pays adjustments (independent — pass-through target unchanged)
---

# wq-091 · Compute Ledger — revenue segment sizing correction

## Naming convention (locked)

The Compute Ledger decomposes hyperscaler/neocloud AI revenue into three plain-English segments. Use these names everywhere — page copy, methodology, briefs, JSON schema fields, deployment records. **Do not use "Bucket 1/2/3" anywhere going forward.**

- **Frontier lab compute** — Model Providers paying external hyperscalers/neoclouds for compute to train and serve their own foundation models. Circular-financing line.
- **AI workload compute** — AI Natives (open models / own models), enterprises (internal AI workloads), model-serving infra cos, sovereign/regulated workloads — all buying raw cloud capacity.
- **Hosted model APIs** — packaged token APIs (AWS Bedrock, Azure OpenAI Service, Google Vertex partner-served). Pass-through to model labs only exists here.

Plus Copilot-class products (M365 Copilot, GitHub Copilot, Copilot Studio, Gemini-in-Workspace) which are **scoped out** of Compute as Apps revenue.

## Why this brief exists

wq-089 shipped earlier on 2026-05-06 with the segment framework correctly introduced (3 segments + Copilot scope-out + corrected pass-through scope) but with **per-provider segment sizing materially overstated**. The Cowork review session 2026-05-06 (post-ship) walked through the numbers segment-by-segment against published hyperscaler economics and found:

- AMZN AI line: $18B (editorial 15% of AWS) — Andy Jassy disclosed $15B Q1 2026 run-rate, working backward to **2025 calendar ~$10B**
- GOOGL AI line: $18B (editorial 30% of GCP) — bottom-up from "13 product lines >$1B" + Anthropic/OpenAI/Mistral GCP consumption + Vertex partner-served lands at **2025 calendar ~$7B**
- MSFT AI line: $28B — holds (Microsoft self-disclosed run-rate basis)
- ORCL AI line: $3B — holds
- Neoclouds: $6.45B — holds

Plus per-segment corrections within those totals:
- MSFT Copilot scope-out: $5B → **$7.4B** (use MS-declared, not TAIL-derived; M365 Copilot list billings $5.4B + GitHub Copilot $1.65B + sundry ~$0.4B)
- GOOGL Copilot scope-out: $3B → **$1.5B** (the other $1.5B was actually Frontier lab compute consumption mis-attributed as Workspace Apps)
- GCP Frontier lab compute: $11.5B → **$3.5B** (drop the $5B Google internal recursion per strict definition; recognise Anthropic on TPUs ~$1.5–2B + OpenAI on GCP ~$0.5–1B + Mistral/others ~$1B)
- AWS Frontier lab compute: was $13B → **$7B** (Anthropic ~$5–6B inference + training + minor labs $1–2B; rest goes to Bedrock/residual)
- AI workload compute ecosystem: was $10.40B → **$5.1B** (per-provider residuals each ~$0.5–1.5B, total tighter)

Net headline impact: **Compute gross post-Copilot drops from $65.45B (shipped) to $45.55B (corrected)** — a ~$20B downward restatement (~30% of shipped headline). Compute net ~$44.5B.

This is the right answer; the editorial AI-share weights baked into the original disclosures file were doing too much work, and the bottom-up segment sizing collapses them. wq-091 ships the correction.

**The full derivation rationale lives in `docs/decisions/resolved/dec-2026-05-06-compute-ledger-bucket-sizing.md`.** This brief is the implementation; the memo is the why.

## Decisions Simon has made (do not re-litigate without flagging)

| # | Decision | Confirmed |
|---|---|---|
| D1 | **Restate AMZN AI 2025 from $18B to $10B**, anchored on Andy Jassy's "$15B Q1 2026 annualized run-rate" disclosure backed out to 2025 calendar via observed AI/Anthropic growth pattern. Tier 1B (CEO disclosure). | 2026-05-06 |
| D2 | **Restate GOOGL AI 2025 from $18B to $7B**, anchored on bottom-up sum of identifiable AI revenue lines: Vertex AI Platform + Gemini API + AI Hypercomputer + Frontier lab compute consumption + Gemini-in-Workspace. Tier 2A bottom-up. | 2026-05-06 |
| D3 | **MSFT AI 2025 = $28B holds.** Microsoft self-disclosed AI run-rate basis is the tightest of the four; no restatement needed. | 2026-05-06 |
| D4 | **Copilot scope-out uses MS-declared (not TAIL-derived).** MSFT Copilot $7.4B; GOOGL Gemini-in-Workspace $1.5B. The $1.5B reduction in GOOGL Copilot reclassifies to Frontier lab compute (Anthropic + OpenAI on GCP under-sized previously). | 2026-05-06 |
| D5 | **Frontier lab definition stays strict.** Internal-recursion (Google's own Gemini compute on GCP) contributes $0 to Frontier lab compute. The increase on GCP is from real external Anthropic + OpenAI flows that were under-sized, not internal recursion. | 2026-05-06 |
| D6 | **2024 reference for YoY proportionally restated.** With 2025 calendar dropping $73B → $54B, 2024 should also restate down (the editorial weights that were wrong for 2025 were wrong for 2024 too). Restate 2024 from $30B to ~$15–18B; YoY 2025 vs 2024 ≈ +150–200%. | 2026-05-06 |
| D7 | **Stale entity record cleanup.** `entities.json:microsoft-copilot[m365-copilot].ai_arr=$13B` is mislabelled; it's a stale Jan 2026 Microsoft total AI ARR, not M365 Copilot specifically. Drop the $13B label; replace with seat-math derivation ($5.4B list billings) plus a parent-AI-line provenance link. | 2026-05-06 |
| D8 | **Plain-English segment names everywhere.** Drop "Bucket 1/2/3" from all writing — page copy, methodology, briefs, deployment records, AND JSON schema fields. Rename JSON keys: `bucket_1_2025_usd_b` → `frontier_lab_compute_2025_usd_b`; `bucket_2_*` → `ai_workload_compute_*`; `bucket_3_gross_*` → `hosted_model_apis_gross_*`; `bucket_3_pass_through_*` → `hosted_model_apis_pass_through_*`; `bucket_3_net_*` → `hosted_model_apis_net_*`; `bucket_basis` → `segment_basis`; `bucket_model_doc` → `segment_model_doc`. Aggregator and validator follow. | 2026-05-06 |

## Open decisions — none

All decisions resolved in the 2026-05-06 Cowork review session.

---

## Scope

### In scope

1. **`data/compute_disclosures.json` per-provider restatement.** AMZN AI line $18B → $10B; GOOGL AI line $18B → $7B; per-segment allocations restated per Final Locked Table in derivation memo.
2. **JSON schema field rename (per D8)** in `data/compute_disclosures.json`:
   - `bucket_1_2025_usd_b` → `frontier_lab_compute_2025_usd_b`
   - `bucket_2_2025_usd_b` → `ai_workload_compute_2025_usd_b`
   - `bucket_3_gross_2025_usd_b` → `hosted_model_apis_gross_2025_usd_b`
   - `bucket_3_pass_through_2025_usd_b` → `hosted_model_apis_pass_through_2025_usd_b`
   - `bucket_3_net_2025_usd_b` → `hosted_model_apis_net_2025_usd_b`
   - `bucket_basis` → `segment_basis` (per-component field)
   - `tier_bucket_1` / `tier_bucket_2` / `tier_bucket_3` → `tier_frontier_lab_compute` / `tier_ai_workload_compute` / `tier_hosted_model_apis`
   - Q1 2026 mirrors of all the above
   - `bucket_model_doc` → `segment_model_doc` in `data/methodology_constants.json`
3. **`data/compute_disclosures.json:segment_basis` rewrites.** Each component's `segment_basis` field gets new provenance text reflecting the new anchors: Jassy quote for AMZN; bottom-up GCP derivation; Anthropic-on-TPUs and OpenAI-on-GCP for GCP Frontier lab compute; MS-declared Copilot reasoning. Tier annotations updated.
4. **`data/compute_disclosures.json:layer_stack_inputs.compute_revenue_2025_net_usd_b` updated** to ~$44.5B (was $59.88B sum-of-quarterlies post-wq-089).
5. **`data/compute_disclosures.json:yoy_reference.compute_revenue_2024_gross_usd_b` proportionally restated** from $30B to ~$15–18B with new `segment_basis` text. Tier 2A editorial restatement, anchored against MSFT FY24 exit run-rate ~$13B + corrected AWS/GCP 2024 based on growth shape.
6. **`scripts/derive_compute_revenue.py` rewrite for new schema field names.** Aggregator reads renamed fields, computes:
   - `compute_revenue.frontier_lab_compute_2025_usd_b`
   - `compute_revenue.ai_workload_compute_2025_usd_b`
   - `compute_revenue.hosted_model_apis_gross_2025_usd_b`
   - `compute_revenue.hosted_model_apis_pass_through_2025_usd_b`
   - `compute_revenue.hosted_model_apis_net_2025_usd_b`
   - `compute_revenue.compute_revenue_2025_gross_usd_b` = frontier lab compute + AI workload compute + hosted model APIs gross (Copilot already excluded)
   - `compute_revenue.compute_revenue_2025_net_usd_b` = gross − hosted model APIs pass-through
   - `--print-summary` output uses plain English labels too (no "Bucket 1" anywhere)
7. **`entities.json:microsoft-copilot[m365-copilot]` clean-up.** Drop the mislabelled `ai_arr: $13B` field; replace with seat-math derivation. Add a `notes` field linking to the derivation memo.
8. **`compute.html` rewrite for plain-English labels and corrected numbers.** Most numbers propagate from `site-data.json:compute`. Specifically:
   - Hero strip Box 1 (gross) reads ~$45.55B post-Copilot
   - Hero strip Box 2 (net) reads ~$44.5B
   - Hero strip Box 3 (Apps→Compute ratio) recalculates against the new compute total
   - Hero strip Box 4 (YoY growth) reads ~+150–200% (per D6 2024 restatement)
   - **"Bucket 1 — frontier lab compute" card renamed to "Frontier lab compute"** (drop the "Bucket 1" prefix entirely). Per-lab attribution reflects new GCP makeup (Anthropic on TPUs + OpenAI on GCP)
   - Concentration headline: Mag3 share recalculates (smaller AWS+GCP relative to MSFT means MSFT's share grows; verify Mag3 % updates correctly)
   - WWHBT signals: capex coverage recalibrates (Mag7 AI capex ~$320B / Compute $44.5B = ~14%, falls below 20% "tracking" threshold — this is editorially intentional, strengthens circular-financing thread)
   - **No "Bucket 1/2/3" or "B1/B2/B3" anywhere on the rendered page** — chart labels, tooltips, side panels, info text all use plain-English segment names
9. **`methodology.html` section rename + new sub-section.** §"Compute Revenue — three-bucket model & principal/agent gate" renamed to **§"Compute Revenue — three-segment model & principal/agent gate"**. Inside that, add a sub-section titled **"Segment sizing methodology"** explaining:
   - Bottom-up segment sizing approach (vs editorial AI-share weights)
   - The AWS-Jassy anchor for AMZN
   - The GCP no-disclosure caveat with bottom-up approach
   - The Copilot MS-declared vs TAIL-derived split with link to future Apps Ledger
   - Reference `docs/decisions/resolved/dec-2026-05-06-compute-ledger-bucket-sizing.md` for full derivation
10. **`scripts/validate-compute-revenue.mjs` updated.** Schema-key assertions updated to match new field names. Add a new assertion: per-component segment sums must match the as-disclosed AI line within ±2% (tighter than the previous 5%, because the new derivation is more rigorous).
11. **Visual baselines re-snapshot** for `/compute.html` (numbers across the page change materially; new baseline) and `/methodology.html` (new sub-section + section title change).
12. **§11 reconciliation** — verify wq-090's pass-through reconciliation target (~$1B) still holds (unchanged from wq-089 ship — Hosted model APIs size barely moved). wq-090 is independent and unblocked by this correction.

### Out of scope

- Changing the segment framework itself (3 segments + Copilot stays).
- Changing the frontier-lab definition from wq-089 D8 (it stays strict; this brief's D5 confirms).
- Renaming the brief filename or decision memo filename — the filenames contain "bucket" as historical artifacts but content is the source of truth. Don't churn on that.
- Building the Apps Ledger (the MS-declared vs TAIL-derived Copilot gap is captured in the derivation memo but the Apps Ledger is a future work item).
- Capital Ledger circular-financing cross-Ledger work — Frontier lab compute surfaces it but the cross-Ledger build is a separate brief.
- Sankey / Revenue Ledger changes — wq-090 is independent and reads off the same Hosted model APIs pass-through (~$1B) which doesn't move.

---

## Files touched

### Modified
- `data/compute_disclosures.json` — per-provider AI lines + segment allocations + Copilot + segment_basis text + 2024 reference + JSON field renames. Largest change.
- `data/methodology_constants.json` — `bucket_model_doc` → `segment_model_doc`; doc text updated to plain English.
- `entities.json` — `microsoft-copilot[m365-copilot]` `ai_arr` field cleanup.
- `compute.html` — hero strip recalculates from new site-data; Frontier lab compute card retitled; verify no "Bucket 1/2/3" or "B1/B2/B3" anywhere in rendered page.
- `methodology.html` — section title rename ("three-bucket model" → "three-segment model"); new sub-section "Segment sizing methodology".
- `scripts/derive_compute_revenue.py` — read/write renamed JSON fields; `--print-summary` uses plain English; first-class output keys renamed.
- `scripts/validate-compute-revenue.mjs` — schema-key assertions updated; tightened tie-out tolerance (±5% → ±2%).
- `site-data.json` — regenerated by `derive_compute_revenue.py --apply` after data updates.

### Read-only references
- `docs/decisions/resolved/dec-2026-05-06-compute-ledger-bucket-sizing.md` — derivation rationale, sources, alternatives considered. Read this first; it explains the why for every number in the data file changes.
- `docs/briefs/wq-089-compute-ledger-v2.md` — segment framework + frontier-lab definition still hold.
- `docs/deployments/deploy-2026-05-06-wq-089-compute-ledger-v2.md` — what shipped under wq-089; this brief corrects it.
- `usage.html` lines 697–698 — frontierProvs / openProvs canonical lists.

### New
- None.

---

## Implementation outline

1. **Branch off main** as `wq-091-compute-ledger-segment-sizing-correction`. Single PR.
2. **Phase 1 — read derivation memo end-to-end.** `docs/decisions/resolved/dec-2026-05-06-compute-ledger-bucket-sizing.md`. The Final Locked Table at the bottom is the target state for `data/compute_disclosures.json`. Every number in that table has segment_basis text in the memo; transcribe it.
3. **Phase 2 — JSON schema field renames.** First pass-through: rename keys throughout `data/compute_disclosures.json` per D8. No value changes yet — just keys. Update `data/methodology_constants.json:compute_revenue.bucket_model_doc` → `segment_model_doc`. Commit "rename: bucket_* → plain English segment names."
4. **Phase 3 — restate `data/compute_disclosures.json` per provider.** For each component (msft_ai, googl_cloud_ai, amzn_aws_ai, oracle_cloud_ai, coreweave, nebius, lambda, crusoe):
   - Update top-line `value_*_2025_*` fields to reflect new AI line totals
   - Update segment fields per Final Locked Table
   - Rewrite `segment_basis` per the derivation memo's per-provider sub-sections (Issues 4, 5, 6 in the memo)
   - Update tier annotations: AMZN frontier lab compute / hosted model APIs → 1B (Jassy CEO disclosure anchor); GOOGL bottom-up still 2A; MSFT/ORCL/neoclouds unchanged
   - Update Q1 2026 mirrors proportionally to maintain quarterly consistency
   - Commit per provider for cleanest review.
5. **Phase 4 — restate `yoy_reference.compute_revenue_2024_gross_usd_b`** from $30B to ~$15–18B central. Add `segment_basis` text explaining the proportional restatement.
6. **Phase 5 — restate `layer_stack_inputs.compute_revenue_2025_net_usd_b`** to ~$44.5B; update source/tier text.
7. **Phase 6 — clean up entity record.** `entities.json:microsoft-copilot[m365-copilot]`: drop `ai_arr: 13.0`; replace with seat-math derivation field (e.g., `derived_arr_2025_usd_b: 5.4` with provenance pointing at seat × price × 12). Add `notes` field linking to derivation memo.
8. **Phase 7 — aggregator rewrite for renamed fields.** `scripts/derive_compute_revenue.py` reads renamed JSON keys, writes plain-English first-class output keys (`frontier_lab_compute_2025_usd_b`, etc.), `--print-summary` uses plain English. Commit.
9. **Phase 8 — validator update.** `scripts/validate-compute-revenue.mjs`: rename assertions to use new keys; tighten tie-out tolerance to ±2%. Commit.
10. **Phase 9 — apply aggregator.** Run `python3 scripts/derive_compute_revenue.py --apply`. Verify `--print-summary` matches Final Locked Table within 2%. If any per-component tie-out fails by >2%, write `docs/decisions/open/` decision file and stop.
11. **Phase 10 — update `compute.html`.** Hero strip values propagate from new site-data; verify renders correctly. Rename "Bucket 1 — frontier lab compute" card to "Frontier lab compute". Audit ALL chart labels, tooltips, side panels, info text — replace any "Bucket 1/2/3" or "B1/B2/B3" with plain-English names. Commit.
12. **Phase 11 — methodology page.** Rename §"Compute Revenue — three-bucket model & principal/agent gate" to "three-segment model & principal/agent gate"; add new "Segment sizing methodology" sub-section. Link to derivation memo. Commit.
13. **Phase 12 — release-check.** `npm run build-lint` + `npm run release-check` + visual snapshot update for `/compute.html` and `/methodology.html`. The Frontier lab compute card title changes; numbers across the page change; new baselines.
14. **Phase 13 — write deployment record** at `docs/deployments/deploy-2026-05-XX-wq-091-compute-ledger-segment-sizing-correction.md`.

---

## Acceptance criteria

- [ ] `data/compute_disclosures.json` per-provider AI lines restated:
  - MSFT $28B (unchanged); AMZN **$10B** (was $18B); GOOGL **$7B** (was $18B); ORCL $3B (unchanged); neoclouds $6.45B (unchanged)
- [ ] Per-provider segment allocations match Final Locked Table in derivation memo within ±2% tie-out:
  - MSFT: Frontier lab compute $18B / Hosted model APIs $1.5B / AI workload compute $1.1B / Copilot $7.4B
  - AMZN: Frontier lab compute $7B / Hosted model APIs $2.5B / AI workload compute $0.5B / Copilot $0
  - GOOGL: Frontier lab compute $3.5B / Hosted model APIs $0.5B / AI workload compute $1.5B / Copilot $1.5B
  - ORCL: Frontier lab compute $2B / Hosted model APIs $0 / AI workload compute $1B / Copilot $0
  - Neoclouds aggregate: Frontier lab compute $5.5B / AI workload compute $1B / Hosted model APIs $0 / Copilot $0
- [ ] **No "bucket_1" / "bucket_2" / "bucket_3" / "bucket_basis" / "bucket_model_doc" keys remain anywhere** in `data/compute_disclosures.json`, `data/methodology_constants.json`, or any other data file. Replaced with plain-English schema names.
- [ ] `segment_basis` field for every component contains new provenance text per derivation memo's Issue 4/5/6 sections.
- [ ] Tier annotations updated: AMZN Frontier lab compute / Hosted model APIs → 1B; GOOGL bottom-up annotations refreshed.
- [ ] Q1 2026 mirrors per provider remain consistent with annual numbers (proportional).
- [ ] `yoy_reference.compute_revenue_2024_gross_usd_b` restated to ~$15–18B with `segment_basis` text.
- [ ] `derive_compute_revenue.py --print-summary` matches Final Locked Table within 2%, **using plain-English labels in output** (no "Bucket"):
  - Compute gross post-Copilot 2025: ~$45.55B
  - Compute net 2025: ~$44.5B
  - Frontier lab compute 2025: ~$36B
  - AI workload compute 2025: ~$5.1B
  - Hosted model APIs gross 2025: ~$4.5B
  - Pass-through 2025: ~$1.05B
  - Copilot excluded 2025: ~$8.9B
  - YoY 2025 vs 2024: ~+150–200%
- [ ] `entities.json:microsoft-copilot[m365-copilot]` no longer contains the mislabelled `ai_arr: 13.0`. Replaced with seat-math derivation + provenance link.
- [ ] `/compute.html` Frontier lab compute card (renamed from "Bucket 1 — frontier lab compute") shows per-lab attribution including new GCP entries (OpenAI on GCP, Anthropic on TPUs uplifted).
- [ ] `/compute.html` WWHBT capex coverage signal recalibrates against new $44.5B; falls into "Below pace" status (~14% vs 20% threshold) — intentional editorial outcome.
- [ ] `/compute.html` rendered DOM contains **no "Bucket 1/2/3" or "B1/B2/B3"** strings (validated by Playwright spec).
- [ ] `/methodology.html` has new sub-section "Segment sizing methodology" under §"Compute Revenue — three-segment model" linking to derivation memo. Section title is "three-segment model" (renamed from "three-bucket model").
- [ ] `validate-compute-revenue.mjs` tightened to ±2% tie-out tolerance and updated for new JSON keys; passes.
- [ ] `npm run build-lint` passes; `npm run release-check` passes with new baselines.
- [ ] Deployment record documents per-provider segment changes, schema rename, and any tactical decisions.

---

## Test plan

1. **Aggregator tie-out.** After data updates and `--apply`, the printed summary must match the Final Locked Table values within 2%. Per-component segment sums must equal AI line within 2% (asserted by `validate-compute-revenue.mjs`).
2. **Schema-rename validation.** A grep across `data/`, `scripts/`, `compute.html`, `methodology.html` for `bucket_1` / `bucket_2` / `bucket_3` / `Bucket 1` / `Bucket 2` / `Bucket 3` / ` B1 ` / ` B2 ` / ` B3 ` returns zero matches (asserted by build-lint or a release-check test).
3. **Visual snapshot.** Re-baseline `/compute.html` — every hero stat changes; Frontier lab compute card title changes; WWHBT signal status changes (capex coverage drops below threshold). Take baselines on desktop + iPhone + Android viewports.
4. **Reconciliation cross-check.** Open `/compute.html` and `/revenue.html` side-by-side; verify Compute pass-through ($1.05B unchanged) and Revenue Hyperscalers channel relationship (wq-090 still applies; this brief doesn't affect that reconciliation). The §11 row about Copilot excluded ($8.9B vs future Apps Ledger) flags the Apps work as still future scope.
5. **Build lint.** `npm run build-lint` — provenance fields preserved on every changed component; new schema keys present.
6. **Manual page audit.** Read through `/compute.html` end-to-end. All numbers should hang together: Frontier lab compute + AI workload compute + Hosted model APIs + Copilot = headline AI line per provider; ecosystem totals reconcile. No "Bucket" anywhere.

---

## Edge cases

- **2024 restatement is editorial.** The proportional walk-back from $30B to ~$15–18B is itself Tier 2A — no audited 2024 calendar disclosure exists in the same segment framework. Document explicitly in `segment_basis`.
- **OpenAI on GCP partial-year 2025.** OpenAI started using GCP for ChatGPT in specific regions per CNBC 2025-07-16. So GCP Frontier lab compute OpenAI portion is partial-year. Q1 2026 mirrors should reflect a higher OpenAI-on-GCP component than 2025 calendar (as the diversification matures). Document in segment_basis.
- **Anthropic 2025 on TPUs vs AWS split.** Anthropic 2025 revenue $4.71B; Frontier lab compute = compute spend not revenue. Anthropic compute spend on AWS + GCP combined likely ~$3–4B 2025 (compute spend > revenue; subsidised by raised capital). Split AWS:GCP roughly 60:40. Document.
- **CoreWeave double-count risk.** CoreWeave Frontier lab compute (~$3.8B of CRWV's $4.5B AI line) is largely Microsoft-sub-rent for OpenAI. The same OpenAI compute consumption is captured separately under MSFT Frontier lab compute ($18B). To avoid double-counting at the OpenAI-line level, the `segment_basis` for both MSFT and CRWV must explicitly note that each represents a different leg of the same flow (Microsoft books gross revenue from CoreWeave; CoreWeave books gross revenue from Microsoft). This is the principal-treatment ASC 606 reality — both are real revenue lines on each entity's P&L, but the aggregate ecosystem flow is gross-of-double-count by definition.
- **Tighter ±2% tie-out tolerance.** wq-089 used ±5%. The bottom-up sizing should be tighter; if any provider misses ±2%, write a decision file rather than ship a bad tie-out.
- **Filenames keep "bucket-sizing" for historical continuity.** The brief filename `wq-091-compute-ledger-bucket-sizing-correction.md` and the decision memo filename `dec-2026-05-06-compute-ledger-bucket-sizing.md` retain "bucket-sizing" because they're identifiers in cross-references. Don't churn on filenames; the *content* uses plain English.

---

## §11 Reconciliation

| wq-091 figure | Matching figure | Expected | Bridge |
|---|---|---|---|
| Compute net 2025 ~$44.5B | Compute net 2025 wq-089 shipped $64.42B | wq-091 corrects wq-089 downward by ~$20B | Per derivation memo Issues 4 (AMZN Jassy correction) + 5 (GCP bottom-up) + 6 (GCP Frontier lab compute Anthropic+OpenAI better-sized). All three issues tied to editorial AI-share weights being too aggressive. |
| Hosted model APIs pass-through 2025 ~$1.05B | wq-090 Hyperscalers channel (cohort) corrected target ~$1.2–1.6B | Cohort subset of Hosted model APIs customers | Unchanged from wq-089 — Hosted model APIs size barely moves under wq-091 corrections, so wq-090 reconciliation target is unaffected. |
| Compute gross 2025 ~$45.55B | Capital Ledger AI capex Mag7 ~$320B | Compute revenue covers what fraction of capex | Drops from ~20% (wq-089) to ~14% (wq-091). Editorially: strengthens circular-financing thread (most capex is NOT covered by current compute revenue; it's funded by hyperscaler equity stakes in labs + parent-co cashflow + customer-revenue-prepaid commits). |
| Apps Revenue Layer Stack ($17.36B) | Revenue Ledger `totalCustomerRevenue` | Identical | Reads live; no change. |
| Copilot excluded total ~$8.9B | Future Apps Ledger | Will be subset; with TAIL-derived discount of 30–40% the real Copilot Apps revenue is $5–6B | Tracked in derivation memo for future Apps Ledger build. |

---

## Definition of done

- All acceptance criteria checked.
- This brief copied to `docs/briefs/wq-091-compute-ledger-bucket-sizing-correction.md`.
- Derivation memo at `docs/decisions/resolved/dec-2026-05-06-compute-ledger-bucket-sizing.md` referenced from this brief and from `segment_basis` text where appropriate.
- Deployment record written.
- Notion card moved to Done.

---

## Handoff prompt for VS Code / Claude Code

> Implement wq-091 per `docs/briefs/wq-091-compute-ledger-bucket-sizing-correction.md`.
>
> **Pre-flight:** Read `docs/decisions/resolved/dec-2026-05-06-compute-ledger-bucket-sizing.md` end-to-end first. The Final Locked Table at the bottom of that memo is your implementation target. Every number has provenance in the memo.
>
> This is a deploy correction to wq-089. The segment framework (3 segments + Copilot scope-out + Hosted-model-APIs-only pass-through) is unchanged; what changes is per-provider segment sizing. Headline restatement: ~$20B downward on Compute gross post-Copilot ($65.45B → ~$45.55B). That's intentional and is the right answer; the editorial AI-share weights baked into wq-087's original `data/compute_disclosures.json` were doing too much work.
>
> ALSO: drop "Bucket 1/2/3" terminology entirely (per D8 of this brief). Rename JSON schema keys to `frontier_lab_compute_*` / `ai_workload_compute_*` / `hosted_model_apis_*`. Update all human-readable text — page copy, methodology, briefs, deployment records — to use plain English (Frontier lab compute / AI workload compute / Hosted model APIs).
>
> All eight decisions (D1–D8) are resolved at the top of the brief — do not re-litigate.
>
> Work the §"Implementation outline" in order — thirteen phases, single PR. Phase 2 (schema rename) runs first cleanly so subsequent value changes happen against the new keys. Phase 3 (per-provider value restatement) is the load-bearing piece. Tighter ±2% tie-out tolerance — if a provider misses, write a `docs/decisions/open/` file rather than paper over.
>
> Constraints:
> - Do NOT change the segment framework or the frontier-lab definition (D5).
> - WWHBT capex coverage signal will move to "Below pace" (~14% vs 20% threshold). Intentional. Don't auto-adjust the threshold.
> - Layer Stack visual: Apps stays at $17.36B; Compute drops from $58–62B shipped to ~$44.5B. Take new visual baselines.
> - Reference the derivation memo from new `segment_basis` text where helpful: "see dec-2026-05-06-compute-ledger-bucket-sizing.md §X for full provenance."
> - The Playwright release-check spec for `/compute.html` should assert that the rendered DOM contains no "Bucket 1/2/3" or "B1/B2/B3" strings.
>
> When finished:
> - Append "Shipped: <date>, commit <sha>" footer to this brief.
> - Write `docs/deployments/deploy-2026-05-XX-wq-091-compute-ledger-segment-sizing-correction.md`.
> - Move Notion wq-091 card to Done.
> - wq-090 (Revenue Ledger Hyperscaler & Who Pays) is independent of this correction and remains unblocked at the same target as before — corrected pass-through ~$1B unchanged.

---

## Change log

- 2026-05-06 — drafted in Cowork following segment-by-segment walk-through against published economics and Andy Jassy's $15B disclosure. D1–D7 confirmed in same session. D8 (plain-English naming everywhere) added on 2026-05-06 after Simon flagged that "Bucket 1/2/3" should not appear in any artefact, internal or external. Derivation memo at `docs/decisions/resolved/dec-2026-05-06-compute-ledger-bucket-sizing.md` is the load-bearing record. Ready for repo handoff.
