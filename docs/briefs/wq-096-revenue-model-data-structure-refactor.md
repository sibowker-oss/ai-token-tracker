# wq-096 — Revenue Model Data Structure Refactor

**Stage:** Scoped
**Priority:** H (load-bearing for wq-097 combined run-rate publication; nothing public ships until this lands)
**Owner:** Claude Code
**Briefing status:** ready_for_review
**Decisions resolved:** 2026-05-08 (Simon, in Cowork session)
**Companion review (Cowork):** N/A — decisions captured in §Decisions below
**Repo copy (canonical for Claude Code):** `/Users/simonbowker/Developer/apac-ai-intel/docs/briefs/wq-096-revenue-model-data-structure-refactor.md`
**Parent context:**
- `docs/deployments/deploy-2026-05-06-wq-087-compute-ledger.md` (gross/net accounting precedent)
- `docs/deployments/deploy-2026-05-06-wq-093-homepage-compute-ledger-refresh.md` (five-ledger architecture)
- Cowork session 2026-05-08 — full revenue model design conversation
- Successor brief: **wq-097 Combined Run-Rate Publication** (gated on this brief shipping cleanly)

> **Note:** This is the Cowork-side mirror of the brief. The canonical copy lives in the repo at `docs/briefs/wq-096-revenue-model-data-structure-refactor.md` for Claude Code to consume. If the two diverge, the repo copy wins.

---

## §0 — Context

The Usage page hero stat "Combined Provider ARR (run-rate) — $63.3B" is currently sourced from the `providers` block (14 frontier-lab/foundation-model entries). It is *not* a combined Compute + AI run-rate, and the site has no defensible aggregation that combines the two ledgers.

In a 2026-05-08 Cowork session, Simon designed a four-tier revenue model that:
- Distinguishes **Frontier** (foundation-model companies) from **AI-Native Apps** (pure AI software built on top) from **Trad SaaS** (incumbents repackaging existing software with AI) — three Apps-side tiers
- Splits Compute into **Trad Compute** (AWS, Azure, GCP, Oracle Cloud) and **AI-Native Compute** (CoreWeave, Lambda, Fireworks, Together, Groq, Replicate, Anyscale)
- Reclassifies **token factories / model-API resellers** from AI-Native Apps to AI-Native Compute (their unit economics are infra, not application)
- Sets a single editorial axis — **AI-Native vs. Trad** — that works on both Apps and Compute sides
- Adds explicit deduction logic for the three-layer pass-through (frontier → trad-compute, apps → ai-native-compute, ai-native-compute → trad-compute) so the combined number doesn't double-count

This brief delivers the **data layer** for that model. **Nothing public-facing changes.** Publication of the combined run-rate is wq-097.

---

## §Decisions (resolved 2026-05-08)

> All decisions resolved by Simon in Cowork. Implement as below without relitigating.

| # | Decision | Resolved choice |
|---|---|---|
| D1 | Editorial axis | **AI-Native vs. Trad**, not Apps-vs-Compute. The same Trad/AI-Native split runs across both sides of the model. AI-Native side = Frontier + AI-Native Apps + AI-Native Compute. Trad side = Trad SaaS + Trad Compute. |
| D2 | Tier 1 — Frontier definition | Companies whose primary commercial product is a proprietary frontier-class foundation model. Includes: OpenAI, Anthropic, Google/Gemini (product line, not parent), xAI, Mistral, Cohere, DeepSeek, Alibaba/Qwen, Baidu, Tencent, Minimax, Moonshot, ByteDance (Doubao), Meta (Llama serving where monetised). |
| D3 | Tier 2 — AI-Native Apps definition | Companies built on top of frontier models where AI is the reason the company exists, AND the commercial product is software (not model-serving infrastructure). Includes Cursor, Lovable, ElevenLabs, Replit, Harvey, Sierra, Hebbia, Perplexity, Glean, GitHub Copilot's competitors, etc. |
| D4 | Tier 3 — Trad SaaS definition | Incumbent software companies repackaging existing SaaS products with AI features. The classifier is "is this AI-washing of a pre-existing product?" Includes M365 Copilot, GitHub Copilot, Salesforce Agentforce, ServiceNow Now Assist, SAP Joule, Adobe Firefly, Workday AI, Atlassian Intelligence, Notion AI, **Google Workspace AI**, **Oracle Fusion AI**, Snowflake Cortex, Databricks Mosaic, HubSpot Breeze, Box AI, Zoom Companion, Intuit Assist. |
| D5 | Tier 4 — Trad Compute definition | Hyperscaler cloud providers' AI infrastructure revenue, **net of any Apps revenue (Trad SaaS or otherwise) bundled into their disclosed AI numbers.** Includes AWS (Bedrock + EC2 AI infra), Azure (AI infra ex-M365 Copilot ex-GitHub Copilot), GCP (AI infra ex-Workspace AI), Oracle Cloud (OCI AI infra ex-Oracle Fusion AI). |
| D6 | Tier 5 — AI-Native Compute definition | Compute providers whose business is AI-specific. Two sub-types collapsed into one tier: (a) bare-metal GPU rental (CoreWeave, Lambda, Crusoe), (b) token-factory / model-API resellers (Fireworks, Together, Groq, Replicate, Anyscale). The boundary rule for inclusion: **revenue is mostly derived from selling compute-priced access to AI workloads, regardless of whether they ship their own model.** |
| D7 | Frontier vs. Token Factory boundary | If a company **ships and operates a proprietary frontier-class model as their primary commercial product**, they are Frontier (Tier 1). If their commercial product is **serving other people's models** (with or without their own as a sideline), they are Token Factory in AI-Native Compute (Tier 5). Mistral and Cohere → Frontier. Together, Fireworks, Groq, Replicate, Anyscale → AI-Native Compute. |
| D8 | Provenance approach | Use **claimed ARR** as the headline value, with a `provenance` tier signalling confidence. We will not have audited "real" data for most companies (mostly private — fundraising statements + commentary). Optional `arrClaimedVsReal` callout for the small subset where audited data exists. Provenance scale aligns with existing TAIL Tier 1A/1B/2A/2B/3A/3B/3C convention used on Compute Ledger. |
| D9 | Multi-entity companies | Microsoft, Google, Oracle each split across multiple tiers. **Google:** Gemini → Frontier; Workspace AI → Trad SaaS; GCP (ex-Workspace AI) → Trad Compute. **Microsoft:** no Frontier entry (uses OpenAI); M365 Copilot + GitHub Copilot → Trad SaaS; Azure (ex-Copilot) → Trad Compute. **Oracle:** Fusion AI → Trad SaaS; OCI AI infra → Trad Compute. |
| D10 | Pass-through deduction structure | Three explicit deduction layers in `arrModel.compute.deductions`: `passthrough_frontier_to_trad`, `passthrough_apps_to_aiNativeCompute`, `passthrough_aiNativeCompute_to_tradCompute`. Each layer is sourced as **named per-record estimates for the top ~80% of dollar volume**, with an explicit `longTailMultiplier` field handling the remainder (e.g., "small AI-Native Apps spend ~50% of ARR on AI-Native Compute, applied to apps below the top-N cutoff"). The multiplier carries its own provenance and assumption documentation. Combined run-rate (wq-097) uses post-deduction `netExternal`. |
| D11 | Anthropic $30B / OpenAI $25B integrity | These are the highest-quality figures currently in TAIL with provenance scores attached. The latest highest Anthropic figure (single-source, low quality) is **parked**, not used. The provenance system handles ongoing integrity — no additional verification task in this brief. |
| D12 | Token factory reclassification location | Records currently in `topConsumers` for Fireworks, Together, Groq, Replicate, Anyscale (and any other companies meeting D6+D7) are **moved** out of `topConsumers` and into `computeProviders.aiNativeCompute`. They no longer appear in the AI-Native Apps total. |

No open decisions. Implement directly. Any data-quality issues or sourcing gaps surface as `docs/decisions/open/` files per the TAIL workflow protocol.

---

## §1 — Goal

`site-data.json` exposes a clean, aggregable, provenance-tagged revenue model with five tiers (Frontier, AI-Native Apps, Trad SaaS, AI-Native Compute, Trad Compute), explicit pass-through deductions, and a calculated `arrModel` aggregation block. The data layer can answer: "What's the combined external-customer AI run-rate at Q1 2026 annualised, broken down by AI-Native vs. Trad on both Apps and Compute sides?" — without any rendering changes shipping yet.

---

## §2 — Files touched

### Modified
- `data/site-data.json` — primary file. Tier tagging on existing blocks, numeric conversion of `enterpriseReality`, expansion of `enterpriseReality` from 7 → ~20 entries, removal of token-factory records from `topConsumers`. New top-level `computeProviders` block. New top-level `arrModel` aggregation block.
- `scripts/generate_site_data.py` — generator emits the new blocks. Add tier tagging logic. Add `arrModel` aggregation calc with deduction logic. Source `enterpriseReality` numeric ARR from new evidence files (see §4 Phase B).
- `scripts/derive_compute_revenue.py` — already produces hyperscaler revenue figures. Extend to emit tier-tagged + Apps-carveout-aware figures consumable by `computeProviders.tradCompute`.
- `scripts/reconcile.py` — extend reconciliation to assert the deduction logic produces a non-negative `netExternal` and that `apps_total + compute_net = industry_total`.
- `data/compute_disclosures.json` — already exists. Extend records with `appsCarveout` field (per-hyperscaler list of which Apps-side records get deducted from the gross AI run-rate to produce Trad Compute net).

### New
- `data/evidence/enterprise_reality/*.json` — one file per Trad SaaS entity (~20 files), each with claimed ARR, provenance, source URLs, asOf date. Generator reads these to populate `enterpriseReality` block.
- `data/evidence/compute_native/*.json` — one file per AI-Native Compute entity (~10 files: CoreWeave, Lambda, Crusoe, Fireworks, Together, Groq, Replicate, Anyscale, etc.).
- `data/evidence/passthrough/*.json` — one file per pass-through estimate, three sub-folders: `frontier_to_trad/`, `apps_to_aiNativeCompute/`, `aiNativeCompute_to_tradCompute/`.

### Validators
- `scripts/release-check.mjs` — extend to assert: (a) every revenue-bearing record has a `tier` field, (b) every numeric ARR has a `provenance` and `arrAsOf` field, (c) `arrModel.combined.industry_total` reconciles to the sum of its components, (d) no record exists in both `topConsumers` and `computeProviders.aiNativeCompute` (token-factory move is clean), (e) `compute.netExternal >= 0` for every hyperscaler.

---

## §3 — Acceptance criteria

1. **Tier tagging complete.** Every record in `providers`, `topConsumers`, `enterpriseReality`, and the new `computeProviders` block has a `tier` field with one of five values: `frontier`, `ai_native_app`, `trad_saas`, `ai_native_compute`, `trad_compute`.
2. **enterpriseReality numeric.** Every entry in `enterpriseReality` has `arrClaimedNumeric` (USD billions, decimal), `arrAsOf` (YYYY-Qn or YYYY-MM-DD), `arrSource` (string with citation), `provenance` (Tier 1A through 3C). The narrative `claimed`/`real` strings are preserved as supplementary fields, not the primary numeric source.
3. **enterpriseReality expanded.** `enterpriseReality` contains at least 18 entries covering at minimum: Microsoft 365 Copilot, GitHub Copilot, Salesforce Agentforce, ServiceNow Now Assist, SAP Joule, Adobe Firefly, Workday AI, Atlassian Intelligence, Notion AI, Google Workspace AI, Oracle Fusion AI, Snowflake Cortex, Databricks Mosaic, HubSpot Breeze, Box AI, Zoom Companion, Intuit Assist, plus any others the research surfaces with tier-2B-or-better provenance.
4. **Token factories moved.** Records for Fireworks, Together, Groq, Replicate, Anyscale (and any other companies meeting D6+D7) no longer appear in `topConsumers`. They appear in `computeProviders.aiNativeCompute` with full numeric ARR + provenance. CoreWeave, Lambda, Crusoe added to the same block.
5. **computeProviders block exists.** New top-level block with two sub-arrays: `tradCompute` (AWS, Azure, GCP, Oracle Cloud) and `aiNativeCompute` (CoreWeave + token factories). Each `tradCompute` entry has both `arrGrossDisclosed` (the company-disclosed AI run-rate) and `arrNetOfAppsCarveout` (gross minus the named Trad SaaS records that are bundled inside).
6. **Apps carve-out logic explicit.** For each `tradCompute` record, the `appsCarveout` field lists the specific Trad SaaS record IDs whose ARR is deducted to produce the net figure. Example: Azure `appsCarveout: ["m365_copilot", "github_copilot"]`.
7. **Pass-through deductions populated.** Three deduction blocks under `arrModel.compute.deductions` are populated with named per-record estimates covering at least ~80% of estimated dollar volume in each layer (e.g., `openai_to_azure`, `anthropic_to_aws`, `cursor_to_fireworks`, `fireworks_to_aws`). The remainder of each layer carries a `longTailMultiplier` field with explicit assumption + provenance, applied to the unnamed long tail.
8. **arrModel aggregation block emits cleanly.** Top-level `arrModel` block has the structure in §5, calculated by `generate_site_data.py` from the constituent records (not hand-edited). `apps_total + compute_net = industry_total` reconciles to within $0.1B tolerance.
9. **topConsumers ARR backfill.** At least 50 of the 64 `topConsumers` entries have `arrNumeric` populated (target: shrink the "—" gap from 26 entries today to ≤14). Where ARR cannot be sourced at Tier 3B or better, leave null with `arrPending: true` flag.
10. **Provenance score field present everywhere.** Every numeric ARR field (across providers, topConsumers, enterpriseReality, computeProviders, deductions) carries a `provenance` field on the existing TAIL scale.
11. **No public-facing change.** `index.html`, `revenue.html`, `compute.html`, `usage.html`, etc. render identically before and after this brief. `npm run release-check` visual baselines unchanged. The only acceptable visible diff is in pages that already happened to display fields that were hand-edited and are now generator-emitted (none expected, but log if any).
12. **Reconciliation passes.** `python scripts/reconcile.py --revenue-model` runs without error and asserts the structural invariants in §2 Validators.
13. **Deployment record written** at `docs/deployments/deploy-YYYY-MM-DD-wq-096-revenue-model-data-structure-refactor.md` per CLAUDE.md template, including: count of new evidence files, list of every `enterpriseReality` entry added, list of every token-factory record moved, and total `arrModel.combined.industry_total` value.

---

## §4 — Implementation outline

### Phase A — Schema definition + tier tagging (no value changes)

1. Define the five-tier schema in `scripts/generate_site_data.py` as a constant. Add a `tier` field to the record templates for `providers`, `topConsumers`, `enterpriseReality`.
2. Tag every existing record per the boundary rules in §Decisions D2–D7. Spot-check the boundary cases:
   - Mistral, Cohere → `frontier` (own model is the product)
   - Google/Gemini provider record → `frontier` (the product line)
   - Workspace AI (when added) → `trad_saas`
   - GCP (when added to computeProviders) → `trad_compute`
   - Microsoft has no Frontier entry — confirm absence
3. Run generator + diff against pre-change output. Only metadata fields should change. Commit as a single tier-tagging change.

### Phase B — enterpriseReality numeric conversion + expansion

1. For each of the 7 existing `enterpriseReality` entries, create `data/evidence/enterprise_reality/<slug>.json` with:
   - `arrClaimedNumeric` (parsed from current narrative `claimed` field; e.g., M365 Copilot "$5.4B list" → 5.4)
   - `arrAsOf` (best estimate from current narrative; e.g., "Q4 2025" → "2025-Q4")
   - `arrSource` (citation string, copied from current narrative `flags` field where possible)
   - `provenance` (assign on the TAIL scale based on disclosure quality)
   - `arrClaimedVsReal` (optional callout where the current narrative includes a "real" estimate, e.g., M365 Copilot net $2.5–3.5B becomes `{ realRange: [2.5, 3.5], realNote: "40-60% discounting per Citi/JPM" }`)
2. Research and create evidence files for the 11+ new entries: Atlassian Intelligence, Notion AI, Google Workspace AI, Oracle Fusion AI, Snowflake Cortex, Databricks Mosaic, HubSpot Breeze, Box AI, Zoom Companion, Intuit Assist, plus any others surfacing with Tier 2B or better. Use the same evidence schema.
3. Update `generate_site_data.py` to emit `enterpriseReality` from these evidence files instead of the hand-coded narrative.
4. Acceptance: `enterpriseReality` is now numeric-first, with narrative as supplementary text. Spot-check three records to confirm `arrClaimedNumeric` is present and matches a reasonable parse of the original claim.

### Phase C — Token factory reclassification

1. Identify token-factory records currently in `topConsumers` per D6+D7: Fireworks, Together, Groq, Replicate, Anyscale, plus any other companies whose primary product is model-serving (research as part of this phase).
2. For each, create `data/evidence/compute_native/<slug>.json` with the same evidence schema as Phase B.
3. **Remove** these records from `topConsumers` in the generator output (do not delete the source data — preserve in `data/archive/topconsumers_premove_2026-XX.json` for audit).
4. Add CoreWeave, Lambda, Crusoe evidence files (these are not currently anywhere in the data layer).
5. Generator emits new `computeProviders.aiNativeCompute` array sourced from these files.

### Phase D — computeProviders.tradCompute creation

1. For each hyperscaler (AWS, Azure, GCP, Oracle Cloud), create / extend `data/evidence/compute_disclosures/<slug>.json` with:
   - `arrGrossDisclosed` (the company-disclosed AI run-rate; e.g., Azure $37B Q1 2026)
   - `arrAsOf`
   - `arrSource`
   - `provenance`
   - `appsCarveout` (array of Trad SaaS record IDs that are bundled inside the disclosed gross — e.g., Azure: `["m365_copilot", "github_copilot"]`)
2. Generator computes `arrNetOfAppsCarveout` = `arrGrossDisclosed − sum(arrClaimedNumeric for each id in appsCarveout)`.
3. Edge case: if a hyperscaler discloses only a partial slice (e.g., GCP doesn't break out AI revenue cleanly), use a Tier 2B/3A estimate with explicit assumption documented in the evidence file. Flag in `docs/decisions/open/` if no defensible estimate exists.
4. Generator emits new `computeProviders.tradCompute` array.

### Phase E — topConsumers ARR backfill

1. Sweep the 26 `topConsumers` entries currently lacking `arrNumeric`. For each, attempt to source ARR from public reporting / fundraising commentary at Tier 3B or better.
2. Where successful, populate `arrNumeric` + `arrSource` + `provenance` + `arrAsOf` directly in the source data.
3. Where unsuccessful, set `arrPending: true` with a `arrPendingReason` field explaining the gap. Do not invent a number.
4. Target: shrink the "—" gap from 26 entries to ≤14.

### Phase F — arrModel aggregation block

1. Add `compute_arr_model()` function to `generate_site_data.py` that:
   - Reads all five tier blocks
   - Reads all three pass-through deduction folders
   - Computes the schema in §5
   - Reconciles `apps_total + compute_net = industry_total`
   - Emits `arrModel` as a top-level key in `site-data.json`
2. Pass-through deduction sourcing: for each of the three layers, create per-record evidence files in `data/evidence/passthrough/<layer>/<from>_to_<to>.json`. Example: `data/evidence/passthrough/frontier_to_trad/openai_to_azure.json` with `{ value: 6.5, valueBasis: "Q1 2026 annualised", source: "...", provenance: "tier_2b" }`. Cover the named relationships responsible for at least ~80% of estimated dollar volume in each layer.
3. For the long tail, create one `longTailMultiplier` evidence file per layer at `data/evidence/passthrough/<layer>/_long_tail.json` with `{ baseValue: <unnamed-tail-ARR>, multiplierPct: <e.g. 50>, rationale: "...", provenance: "tier_2b_or_3a" }`. Generator computes the long-tail deduction as `baseValue * multiplierPct/100`.
4. Generator sums per-record values + long-tail multiplier to produce each layer's deduction total. Document which named relationships exist and which sit in the long tail in the deployment record.

### Phase G — Validators + reconciliation

1. Extend `scripts/release-check.mjs` to assert all structural invariants in §2 Validators.
2. Extend `scripts/reconcile.py` with a `--revenue-model` mode that asserts:
   - `apps.frontier + apps.aiNative + apps.tradSaas = apps_total`
   - `compute.tradCompute (sum of arrNetOfAppsCarveout) + compute.aiNativeCompute (sum of arrNumeric) − compute.deductions.passthrough_frontier_to_trad − compute.deductions.passthrough_apps_to_aiNativeCompute − compute.deductions.passthrough_aiNativeCompute_to_tradCompute = compute_net`
   - `apps_total + compute_net = industry_total` (tolerance: $0.1B)
   - No record exists in both `topConsumers` and `computeProviders.aiNativeCompute`
   - Every `tradCompute.appsCarveout` ID resolves to a real `trad_saas` record
3. Add unit tests for the new generator functions.

### Phase H — Verify & ship

1. Run `npm run build-lint` — 0 fail.
2. Run `npm run release-check` — all passes; visual baselines unchanged (no public-facing change).
3. Run `python scripts/reconcile.py --revenue-model` — all assertions pass.
4. Diff `site-data.json` before and after. Verify only `arrModel`, `computeProviders`, `enterpriseReality` (numeric fields), and `tier` tags have changed. `providers` and `topConsumers` unchanged except for tier tags + token-factory records removed.
5. Write deployment record per §3 acceptance #13.
6. Push to `origin/main` after Simon's chat approval. **No staging URL needed for this brief — it's data-layer only with no public-facing change.** (wq-097 will require staging gate per Publishing Gate.)

---

## §5 — `arrModel` schema

```json
{
  "arrModel": {
    "asOf": "2026-Q1-annualised",
    "basis": "trailing_quarter_x4_or_disclosed_run_rate",
    "currency": "USD_B",
    "apps": {
      "frontier": {
        "total": 63.35,
        "entries": [
          { "id": "openai", "arr": 25.0, "provenance": "tier_1b", "tier": "frontier" },
          { "id": "anthropic", "arr": 30.0, "provenance": "tier_2a", "tier": "frontier" }
        ]
      },
      "aiNative": {
        "total": null,
        "entries": [ /* sourced from topConsumers tier=ai_native_app */ ]
      },
      "tradSaas": {
        "total": null,
        "entries": [ /* sourced from enterpriseReality */ ]
      },
      "subtotal": null
    },
    "compute": {
      "tradCompute": {
        "totalGross": null,
        "totalNet": null,
        "entries": [ /* sourced from computeProviders.tradCompute */ ]
      },
      "aiNativeCompute": {
        "total": null,
        "entries": [ /* sourced from computeProviders.aiNativeCompute */ ]
      },
      "deductions": {
        "passthrough_frontier_to_trad": { "total": null, "entries": [] },
        "passthrough_apps_to_aiNativeCompute": { "total": null, "entries": [] },
        "passthrough_aiNativeCompute_to_tradCompute": { "total": null, "entries": [] },
        "totalDeductions": null
      },
      "netExternal": null,
      "subtotal": null
    },
    "combined": {
      "apps_total": null,
      "compute_net": null,
      "industry_total": null,
      "ai_native_total": null,
      "trad_total": null,
      "ai_native_share_pct": null
    }
  }
}
```

The `ai_native_total` and `trad_total` fields cross-cut the apps/compute split to express the editorial axis. `ai_native_total = apps.frontier + apps.aiNative + compute.aiNativeCompute (gross, pre-deduction)`. `trad_total = apps.tradSaas + compute.tradCompute.totalNet`. These two **do not** sum to `industry_total` because pass-through deductions are netted at the compute layer. Both views are published; methodology footnote explains the two reconciliations.

---

## §6 — Tier classification reference (canonical)

| Tier | Tag | Examples (non-exhaustive) | Where it lives |
|---|---|---|---|
| 1 — Frontier | `frontier` | OpenAI, Anthropic, Google/Gemini, xAI, Mistral, Cohere, DeepSeek, Alibaba/Qwen, Baidu, Tencent, Minimax, Moonshot, ByteDance/Doubao, Meta/Llama (where monetised) | `providers` block |
| 2 — AI-Native Apps | `ai_native_app` | Cursor, Lovable, ElevenLabs, Replit, Harvey, Sierra, Hebbia, Perplexity, Glean, Magic, Codeium (non-Microsoft) | `topConsumers` block |
| 3 — Trad SaaS | `trad_saas` | M365 Copilot, GitHub Copilot, Salesforce Agentforce, ServiceNow Now Assist, SAP Joule, Adobe Firefly, Workday AI, Atlassian Intelligence, Notion AI, Google Workspace AI, Oracle Fusion AI, Snowflake Cortex, Databricks Mosaic, HubSpot Breeze, Box AI, Zoom Companion, Intuit Assist | `enterpriseReality` block |
| 4 — AI-Native Compute | `ai_native_compute` | CoreWeave, Lambda, Crusoe, Fireworks, Together, Groq, Replicate, Anyscale | `computeProviders.aiNativeCompute` (new) |
| 5 — Trad Compute | `trad_compute` | AWS, Azure, GCP, Oracle Cloud | `computeProviders.tradCompute` (new) |

---

## §7 — Edge cases

1. **Multi-tier companies (Google, Microsoft, Oracle).** Each has multiple records across tiers. Use composite IDs (`google_gemini`, `google_workspace_ai`, `gcp` — three records for Google) and ensure no double-counting in the parent disclosure. Microsoft's $37B Q1 2026 AI run-rate is the gross, but only `azure` (Trad Compute) gets the AI infra portion; M365 Copilot and GitHub Copilot are separate `trad_saas` records that get deducted from gross to produce `azure.arrNetOfAppsCarveout`.

2. **Frontier vs. Token Factory boundary fuzziness.** Mistral and Cohere both ship proprietary models AND offer some inference services. Per D7, primary commercial product determines tier — both are Frontier. If Together adds a proprietary model that becomes their primary product (unlikely but possible), reclassify in a future cycle, not this brief.

3. **Meta and ByteDance with `rev: 0` in current `providers`.** They serve enormous token volumes but don't monetise tokens directly. Tag them `frontier` for completeness but `arrNumeric: 0` is correct for the run-rate aggregation. Their tokens still drive the Usage Ledger story; revenue contribution to `arrModel` is zero.

4. **Pass-through estimation for private companies.** OpenAI's compute spend with Microsoft is reported in commentary, not financial statements. Anthropic's compute spend with AWS/GCP is similar. Use the most authoritative source (Bloomberg/Information/SemiAnalysis estimates) with provenance Tier 2B and document the assumption. Do not fabricate.

5. **CoreWeave double-count risk.** CoreWeave's revenue is largely Microsoft and Meta as customers. Microsoft's $37B AI run-rate already includes the Azure capacity that's powered by CoreWeave GPUs. Including CoreWeave in `aiNativeCompute` and Azure in `tradCompute` without netting would double-count. Solution: a `passthrough_aiNativeCompute_to_tradCompute` deduction estimating the portion of CoreWeave's revenue that flows through Microsoft's reported AI revenue. This is the trickiest deduction layer and the most fragile estimate; document the assumption visibly.

6. **GitHub Copilot in two tiers historically.** Currently in both `topConsumers` (as `$1.65B`) and `enterpriseReality` (as MSFT-owned). Per D9, GitHub Copilot is `trad_saas` — Microsoft is repackaging GitHub. Remove from `topConsumers`, keep in `enterpriseReality`. This is one of the records that gets `appsCarveout`-deducted from Azure's gross.

7. **Salesforce Agentforce in two tiers historically.** Currently in both `topConsumers` ($0.30B) and `enterpriseReality` ($0.8B claimed / $0.25–0.35B real). Per D9, Agentforce is `trad_saas`. Remove from `topConsumers`, keep in `enterpriseReality`. Use the `enterpriseReality` figure (richer narrative + provenance).

---

## §8 — Test plan

1. Unit test for `compute_arr_model()` aggregator: pass synthetic input with known totals; assert output schema and reconciliation.
2. Integration test: run full `generate_site_data.py` against fixture data; diff output against expected golden file; assert only the new keys (`arrModel`, `computeProviders`) and tier annotations differ.
3. Visual regression: `npm run release-check` — all existing baselines unchanged. If any baseline shifts, investigate before assuming acceptable.
4. Manual eyeball: load `site-data.json` in browser/jq; confirm `arrModel.combined.industry_total` is a sane positive number; confirm `arrModel.combined.ai_native_share_pct` is between 0 and 100.

---

## §9 — Out of scope (explicit)

- Any rendering of `arrModel` on public pages — that's wq-097.
- Any change to existing hero stats, charts, tables — they continue to read their existing fields.
- Methodology page edits — wq-097 will add the combined run-rate methodology section.
- Any homepage changes — wq-097 may propose hero stat additions, but not this brief.
- Backfilling more than 50 of `topConsumers` — current target is 50/64, not 64/64. Remaining gaps are wq-098+.
- Compute Ledger page changes — none. The existing $43.07B Compute revenue figure on `compute.html` is unaffected; that's a different aggregation (sum-of-quarterlies, post-Copilot) that lives separately from `arrModel`.

---

## §10 — Definition of done

1. All §3 acceptance criteria met.
2. `python scripts/reconcile.py --revenue-model` passes.
3. `npm run release-check` passes; visual baselines unchanged.
4. Deployment record written per §3 #13.
5. Branch merged to `main` after Simon's chat approval.
6. Notion Kanban card moved to "Done".
7. Memory updated: add a memory file noting the model is shipped and wq-097 is unblocked.

---

## §11 — Handoff prompt for VS Code / Claude Code

> Paste the block below into a fresh VS Code Claude Code session.

```
Implement wq-096 — Revenue Model Data Structure Refactor.

Read in order:
1. /Users/simonbowker/Developer/apac-ai-intel/CLAUDE.md
2. /Users/simonbowker/Developer/apac-ai-intel/TAIL-WORKFLOW-PROTOCOL.md
3. /Users/simonbowker/Developer/apac-ai-intel/docs/briefs/wq-096-revenue-model-data-structure-refactor.md (canonical brief)

The brief is fully scoped — all decisions resolved 2026-05-08. Implement Phases A through H sequentially. Open a `docs/decisions/open/` decision file only if you hit a blocker that needs Cowork resolution; otherwise log tactical decisions in the eventual deployment record.

Critical reminders:
- Data layer only. No public-facing changes. Visual baselines must be unchanged.
- Token factories (Fireworks, Together, Groq, Replicate, Anyscale) move OUT of topConsumers and into computeProviders.aiNativeCompute. Confirm no record exists in both blocks after the move.
- Multi-tier companies (Google, Microsoft, Oracle) split into separate records per tier per Decision D9 in the brief. Microsoft has NO frontier entry.
- Pass-through deductions: cover ~80% of dollar volume in each layer with named relationships (e.g., openai_to_azure); apply a long-tail multiplier with documented assumption + provenance for the rest.
- Provenance fields required on every numeric ARR.
- Reconciliation must hold: apps_total + compute_net = industry_total within $0.1B tolerance.

When done, push to main after my chat approval and update the Notion Kanban card.
```

---

*End of brief.*
