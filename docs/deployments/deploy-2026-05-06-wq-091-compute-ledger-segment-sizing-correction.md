# Deployment: wq-091 — Compute Ledger segment sizing correction

**Date:** 2026-05-06
**WQ:** wq-091 (deploy correction to wq-089)
**Branch/Commit:** wq-091-compute-ledger-segment-sizing-correction · d091964
**Derivation memo:** `docs/decisions/resolved/dec-2026-05-06-compute-ledger-bucket-sizing.md`

## What shipped

Three concurrent changes in a single commit:

### 1. Per-provider AI line restatement (D1, D2, D3)
- **AMZN AI 2025**: $18B → **$10B** (anchored on Andy Jassy CEO disclosure of "$15B annualised AI run rate" Q1 2026; Tier 1B). 2025 calendar walked back via observed Anthropic growth shape (Q1 ~$1.5B → Q4 ~$3.5B).
- **GOOGL AI 2025**: $18B → **$7B** (bottom-up — no discrete GCP AI revenue figure disclosed; anchored on "13 product lines >$1B" + identifiable AI lines Vertex AI Platform / Gemini API / AI Hypercomputer / AI agent products / AI-driven analytics).
- **MSFT AI 2025**: $28B holds (self-disclosed run-rate basis is the tightest of the four).
- **ORCL AI 2025**: $3B holds (per-segment internal reallocation: Stargate moves to Frontier lab compute).
- **Neoclouds aggregate**: $6.45B holds.

### 2. Per-segment reallocation (D4, D5, D6)
- **MSFT Copilot scope-out**: $5B → **$7.4B** (MS-declared seat-math: 15M paid M365 Copilot seats × $30/mo × 12 = $5.4B + GitHub Copilot $1.65B + sundry ~$0.4B).
- **GOOGL Copilot scope-out**: $3B → **$1.5B** (the other $1.5B reclassifies to Frontier lab compute as Anthropic+OpenAI-on-GCP were under-sized).
- **GCP Frontier lab compute**: $11.5B → **$3.5B** (strict definition holds — drop the $5B internal-recursion per D5; recognise Anthropic on TPUs $1.5–2B + OpenAI on GCP $0.5–1B + Mistral/Cohere/AI21/others $1B).
- **AWS Frontier lab compute**: $13B → **$7B** (Anthropic on AWS infra $5–6B + minor labs $1–2B).
- **AI workload compute ecosystem**: $10.4B → **$5.1B** (residuals tighter under bottom-up sizing).
- **2024 reference**: $30B → **$17B** (proportional restatement; YoY 2025 vs 2024 = +168% rather than +103%).

### 3. JSON schema rename — bucket_* → plain English (D8)
Replaced engineering-shorthand keys throughout `data/compute_disclosures.json`, `data/methodology_constants.json`, aggregator output (`scripts/derive_compute_revenue.py` writes site-data.json:compute), and validator assertions:

| Old key | New key |
|---|---|
| `bucket_1_2025_usd_b` | `frontier_lab_compute_2025_usd_b` |
| `bucket_2_2025_usd_b` | `ai_workload_compute_2025_usd_b` |
| `bucket_3_gross_2025_usd_b` | `hosted_model_apis_gross_2025_usd_b` |
| `bucket_3_pass_through_2025_usd_b` | `hosted_model_apis_pass_through_2025_usd_b` |
| `bucket_3_net_2025_usd_b` | `hosted_model_apis_net_2025_usd_b` |
| `bucket_basis` | `segment_basis` |
| `tier_bucket_1/2/3` | `tier_frontier_lab_compute / tier_ai_workload_compute / tier_hosted_model_apis` |
| `bucket_model_doc` | `segment_model_doc` |

(Q1 2026 mirrors of the segment fields renamed identically.)

### Page-level changes
- **`compute.html`**: "Bucket 1 — Frontier-lab compute spend" card retitled to **"Frontier lab compute"** (drop the engineering-shorthand prefix). Concentration-headline lede now leads on Frontier lab compute; hero strip values propagate from new site-data; WWHBT signals rebuilt — "Bucket 1 share" → "Frontier lab compute share — circular-financing self-loop", "Pass-through gap (bucket 3 only)" → "Pass-through gap (Hosted model APIs only)". Side-panel and tier annotations use plain-English labels.
- **`methodology.html`**: §"Compute Revenue — three-bucket model" → §"Compute Revenue — three-segment model"; added sub-section **"Segment sizing methodology"** (bottom-up segment sizing approach + AWS-Jassy anchor + GCP no-disclosure caveat + Copilot MS-declared vs TAIL-derived split + reference to derivation memo).

### Headline numbers (post-wq-091)
| Metric | wq-089 shipped | wq-091 shipped | Δ |
|---|---|---|---|
| Total AI line declared 2025 | $73.45B | $54.45B | –$19B |
| Copilot scope-out | $8B | $8.9B | +$0.9B |
| Compute gross post-Copilot | $65.45B | **$45.55B** | **–$19.9B** |
| Frontier lab compute | $50.55B | **$36.0B** | –$14.6B |
| AI workload compute | $10.40B | **$5.1B** | –$5.3B |
| Hosted model APIs gross | $4.5B | $4.5B | ~0 |
| Pass-through | $1.025B | $1.025B | ~0 |
| Compute net | $64.42B | **$44.5B** | **–$19.9B** |
| YoY 2025 vs 2024 | +103% | **+168%** | +65 pts |
| WWHBT capex coverage | ~20% (tracking) | **~14% (below pace)** | intentional |

## Decisions made during implementation

- **Quarterly time series rebalanced.** Quarterly aggregates restated proportionally so sum-of-quarterlies pre-Copilot 2025 matches the corrected $54.45B annualised pre-Copilot. Specifically: AMZN quarterly trajectory rewritten Q1 ~$1.5B → Q4 ~$3.5B per memo Issue 4 anchor; GOOGL rewritten $1.20B Q1 → $2.30B Q4 to land $7B sum-of-Q. ORCL Q4 nudged to 1.00 (was 0.95) to land $3.0B sum-of-Q exactly. Neocloud quarterlies adjusted to land per-provider AI line totals at the Final Locked Table values. This was a tactical call — the brief asked for proportional Q1 2026 mirrors but didn't prescribe quarterly trajectory; rebuilding the trajectory keeps sum-of-Q ≈ annualised so the Layer Stack Compute net value (which the aggregator computes as sum-of-Q post-Copilot − pass-through) lands at $44.5B as the brief requires (Phase 5).

- **Per-segment neocloud reallocation.** The Final Locked Table specifies neocloud aggregate $5.5B Frontier / $1B Workload but the per-component subtotals weren't fully prescribed. Per-provider tie-out preserved (CRWV $4.5B, NBIS $0.95B, LMBD $0.6B, CRSE $0.4B — all unchanged at the AI-line level); per-segment shifted slightly toward Frontier-heavy to align with $5.5B/$1B aggregate. CoreWeave Frontier raised to 4.0 (was 3.8) to reflect the editorial point that ~85% of CoreWeave is Microsoft-sub-rent for OpenAI workloads (frontier).

- **Tier upgrades on AWS.** AMZN's Frontier lab compute and Hosted model APIs tier annotations upgraded from 2A to **1B** because Andy Jassy's CEO shareholder-letter disclosure is Tier 1B (own-mouth) and now serves as the load-bearing anchor.

- **Validator tie-out tightened to ±2%.** Per brief acceptance criteria — wq-089 used ±5% (looser, to allow editorial weights). The bottom-up segment sizing should be tighter; if any provider missed ±2% the brief required writing a `docs/decisions/open/` decision file. All eight providers tied out within ±0.1% — comfortable margin.

- **AI line targets baked into validator.** Added per-provider `AI_LINE_TARGETS_2025` constants in `validate-compute-revenue.mjs` that assert segment sum + copilot ≈ Final Locked Table value within ±2%. This codifies the brief's tie-out requirement so future quarterly refreshes can't silently drift.

- **Filename "bucket-sizing.md" preserved.** The brief explicitly retains the filename of the derivation memo and this brief because they are cross-references in commits and decision history. The Playwright spec asserts no "Bucket 1/2/3" or "B1/B2/B3" strings in the rendered DOM but ignores filename references in copy.

- **Tactical: no decision file needed.** All eight per-provider AI line tie-outs landed at exactly the Final Locked Table value (within ±0.1%) — no provider missed ±2% so no `docs/decisions/open/` file was written.

## Open items

- **wq-090 (Revenue Ledger Hyperscaler & Who Pays).** Independent of this correction. Pass-through target ($1.05B) unchanged from wq-089 ship — Hosted model APIs sizing barely moved under wq-091. wq-090 remains unblocked at the same target.
- **Future Apps Ledger.** The MS-declared vs TAIL-derived Copilot gap ($7.4B declared vs $4–5B real after 40–60% bundling discount) is captured in the derivation memo for future build. Tracked as `dec-YYYY-MM-DD-apps-ledger-copilot-real-vs-declared.md` placeholder reference.
- **Capital Ledger circular-financing cross-build.** Frontier lab compute ($36B) surfaces the geometry but the cross-Ledger build (equity flow loop: Microsoft equity in OpenAI funds OpenAI's Azure spend) is a separate brief.
- **Visual snapshot baselines.** Compute and methodology pages have new visual baselines required (numbers across the page change materially; Frontier lab compute card title changes; WWHBT signal status changes). Existing pre-wq-091 snapshots will fail until rebaselined; this is expected and not a regression. Rebaseline in a follow-up release-check pass.
- **labels.spec.ts pre-existing failures.** The "no raw keys visible" Playwright spec was already flagging common English words (revenue, capital, methodology, compute, segment, providers, etc.) as JSON keys leaking to UI on multiple pages prior to wq-091. These failures are unrelated to this work and pre-date this branch.

## Acceptance criteria status

- [x] `data/compute_disclosures.json` per-provider AI lines restated: MSFT $28B (unchanged); AMZN **$10B**; GOOGL **$7B**; ORCL $3B; neoclouds $6.45B
- [x] Per-provider segment allocations match Final Locked Table within ±2% tie-out (validator passes)
- [x] No `bucket_1` / `bucket_2` / `bucket_3` / `bucket_basis` / `bucket_model_doc` keys remain anywhere in `data/compute_disclosures.json`, `data/methodology_constants.json`, or any other data file (validator asserts)
- [x] `segment_basis` field for every component contains new provenance text per derivation memo
- [x] Tier annotations updated: AMZN Frontier lab compute / Hosted model APIs → 1B; GOOGL bottom-up annotations refreshed
- [x] Q1 2026 mirrors per provider remain consistent with annual numbers (proportional)
- [x] `yoy_reference.compute_revenue_2024_gross_usd_b` restated to $17B with `segment_basis` text
- [x] `derive_compute_revenue.py --print-summary` matches Final Locked Table within 2%, using plain-English labels (verified):
  - Compute gross post-Copilot 2025: $45.55B ✓
  - Compute net 2025: $44.53B ✓
  - Frontier lab compute 2025: $35.95B ✓
  - AI workload compute 2025: $5.10B ✓
  - Hosted model APIs gross 2025: $4.50B ✓
  - Pass-through 2025: $1.025B ✓
  - Copilot excluded 2025: $8.90B ✓
  - YoY 2025 vs 2024: +168% ✓
- [x] `entities.json:microsoft-copilot[m365-copilot]` no longer contains the mislabelled `ai_arr: 13.0`. Replaced with `derived_arr_2025_usd_b: 5.4` seat-math + notes field linking to derivation memo
- [x] `/compute.html` Frontier lab compute card (renamed from "Bucket 1 — frontier lab compute") shows per-lab attribution including new GCP entries (OpenAI on GCP, Anthropic on TPUs uplifted)
- [x] `/compute.html` WWHBT capex coverage signal recalibrates against new $44.5B; falls into "Below pace" status (~14% vs 20% threshold)
- [x] `/compute.html` rendered DOM contains no "Bucket 1/2/3" or "B1/B2/B3" strings (validated by Playwright spec — passes)
- [x] `/methodology.html` has new sub-section "Segment sizing methodology" under §"Compute Revenue — three-segment model" linking to derivation memo. Section title is "three-segment model"
- [x] `validate-compute-revenue.mjs` tightened to ±2% tie-out tolerance and updated for new JSON keys; passes
- [x] `npm run build-lint` passes (0 fail, 1 advisory unchanged from baseline)
- [ ] `npm run release-check` — wq-091 compute.spec.ts assertions pass; visual snapshot baselines need rebaseline pass (separate follow-up — pre-existing labels.spec.ts failures unrelated to wq-091)
- [x] Deployment record documents per-provider segment changes, schema rename, and tactical decisions (this file)

## Notion

Move wq-091 card from In Progress → Done. (Repo cannot mutate Notion directly; flagging here.)
