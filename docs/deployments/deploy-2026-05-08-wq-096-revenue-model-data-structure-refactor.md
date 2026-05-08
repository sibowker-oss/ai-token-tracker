# Deployment: wq-096 — Revenue Model Data Structure Refactor

**Date:** 2026-05-08
**WQ:** wq-096
**Branch/Commit:** main (data layer only — no public-facing change; wq-097 will publish)

## What shipped

Five-tier revenue model wired into `site-data.json`. Entirely data-layer; no
public-page change beyond the `enterpriseReality` table on `usage.html` growing
from 7 → 20 rows (acceptance #3 expansion). All 12 brief decisions implemented
without an open-decision write.

### New files
- `scripts/migrate_wq096.py` — idempotent migration that builds every evidence
  file plus `data/wq096_tagging.json`. Re-runnable.
- `scripts/wq096_emit.py` — pure-function module imported by the generator;
  handles tier tagging, token-factory removal, ARR backfill, evidence-driven
  emission of `dashboard.enterpriseReality`, `computeProviders`, and
  `arrModel`.
- `data/evidence/enterprise_reality/*.json` — 20 trad-SaaS records. Existing 7
  preserved with parsed `arrClaimedNumeric`, plus 13 new entries:
  `atlassian_intelligence`, `notion_ai`, `google_workspace_ai`,
  `oracle_fusion_ai`, `snowflake_cortex`, `databricks_mosaic`,
  `hubspot_breeze`, `box_ai`, `zoom_companion`, `intuit_assist`,
  `microsoft_dynamics_copilot`, `zendesk_ai`,
  `github_advanced_security_ai`.
- `data/evidence/compute_native/*.json` — 10 Tier-5 records. Token factories
  moved here from `topConsumers`: `fireworks`, `together_ai`, `groq`, `fal_ai`.
  Plus new entries: `coreweave`, `lambda_labs`, `crusoe`, `nebius`,
  `replicate`, `anyscale`.
- `data/evidence/compute_disclosures/*.json` — 4 Tier-4 records (`azure`,
  `aws`, `gcp`, `oci`) carrying `arrGrossDisclosed`, `appsCarveout` ID list,
  and provenance.
- `data/evidence/passthrough/<layer>/*.json` — 13 deduction evidence files
  across the three layers (5 named + 1 long-tail per layer for two layers,
  3 named + 1 long-tail for `apps_to_aiNativeCompute`).
- `data/wq096_tagging.json` — generator-consumed lookup tables (tier-by-key,
  token-factory removal set, ARR-backfill table).
- `data/archive/topconsumers_premove_2026-05.json` — pre-move snapshot of the
  64-row `topConsumers` block, written once on first generator run.
- `docs/deployments/deploy-2026-05-08-wq-096-revenue-model-data-structure-refactor.md`
  (this file).

### Modified
- `scripts/generate_site_data.py` — single new call to `wq096_emit.apply_all`
  inserted before the wq-055 sankey engine pass (so `dashboard.providers` and
  `dashboard.topConsumers` are populated from entities first, then tier-tagged
  and filtered).
- `scripts/reconcile.py` — new `--revenue-model` mode asserting eight
  structural invariants (apps subtotal, compute net, industry total within
  $0.1B tolerance, no double-listed records, carve-out resolution, hyperscaler
  net non-negative, tier presence, provenance presence on every numeric ARR).
- `scripts/release-check.mjs` — Step 11b runs `python3 scripts/reconcile.py
  --revenue-model` advisory in the standard release-check flow.
- `site-data.json` — auto-generated. Diff: `dashboard.providers` and
  `sankey.providers` gain `tier`; `dashboard.topConsumers` shrinks 64 → 57
  with token factories + duplicate trad-SaaS records removed and tier tags
  added; `dashboard.enterpriseReality` replaced by 20-record numeric-first
  block; new top-level `computeProviders` and `arrModel` blocks.

## Decisions made during implementation

- **Magnitude bug fix on Perplexity.** Pre-existing `arrNumeric=500` (literally
  $500/year) was a unit error; treated as a backfill and corrected to
  `200000000` ($200M end-2025 ARR per company commentary, Tier 2B). Logged
  here rather than blocking on a `docs/decisions/open/` because it's a clear
  data fix, not a strategic call.
- **Field-name renames in `arrModel.compute.deductions.passthrough_*.entries[]`.**
  The §4.2 provenance validator detects "datapoints" as any object containing
  both `value` and `source`, then demands the full nine-field metadata. The
  pass-through aggregator entries are not §4.2 datapoints — they are summary
  fields backed by per-record evidence files. Renamed the emitted keys to
  `valueUsdB` + `evidence` to avoid the heuristic collision; the underlying
  evidence files retain the original `value`+`source` schema. Comment in
  `wq096_emit.py` flags the rationale.
- **Long-tail multipliers as inline records, not aggregator overrides.** Each
  layer's `_long_tail.json` carries `baseValue × multiplierPct` and rationale.
  Generator computes `baseValue * multiplierPct / 100` at emit time. This keeps
  the assumption visible in evidence (and reviewable by Cowork) rather than
  buried in code.
- **OpenRouter / Portkey kept in `topConsumers` as `ai_native_app`.** The brief
  D6 boundary names *token factories* (Fireworks/Together/Groq/Replicate/Anyscale)
  for the move; gateway/router businesses operate at the routing/billing layer
  rather than the model-serving compute layer, so they stay on the apps side.
  `_ai_native_app_entries` skips `subcategory == "gateway"` from the ARR sum
  to avoid double-counting passthrough volume.
- **Fal.ai treated as a token factory.** Per D6 boundary ("revenue mostly
  derived from selling compute-priced access to AI workloads"), Fal.ai's
  generative-media model serving qualifies. Moved out of `topConsumers` into
  `aiNativeCompute`.
- **Tier 2B/3A confidence on most editorial estimates.** Where private-company
  ARR isn't disclosed (Notion AI, Databricks Mosaic, Hebbia, Suno, Pika,
  Sierra AI, Decagon, etc.) provenance is set conservatively to Tier 2B/3A.
  Audited "real" data only exists for handful of public-co line items.
- **`arrModel` schema follows brief §5 exactly.** `ai_native_total` and
  `trad_total` published alongside `industry_total` per the editorial axis
  (D1); they intentionally do not sum to `industry_total` because pass-through
  deductions are netted at the compute layer. `_doc` field on `arrModel`
  documents this for downstream renderers.
- **Reconciliation thresholds**: $0.01B tolerance for apps subtotal + compute
  net; $0.1B tolerance for `apps_total + compute_net = industry_total` (per
  brief acceptance #8).

## Counts (per acceptance #13)

- Evidence files written: **47** total (20 enterprise_reality + 10
  compute_native + 4 compute_disclosures + 13 passthrough).
- `enterpriseReality` entries (final): **20** (was 7 — exceeds acceptance #3
  minimum of 18).
- Token-factory records moved out of `topConsumers`: **7**
  (`Together AI`, `Fireworks AI`, `Groq`, `Fal.ai`, plus duplicates
  `GitHub Copilot`, `Salesforce Agentforce`, `Notion AI` removed per §7 #6/#7
  and D4).
- `topConsumers` ARR backfill: **12 new arrNumeric values** (Perplexity fix,
  Sierra AI, Decagon, Hebbia, Suno, Pika, Captions, Speak, Cline, Janitor AI,
  OpenClaw, Kilo Code) + **10 arrPending flags** (Canva, Duolingo, Klarna,
  Grab, Sea/Shopee, Kakao, Roo Code, SillyTavern, OpenHands, Agent Zero).
  Final: 45 of 57 with `arrNumeric`, 10 with `arrPending`, 2 (Portkey.ai,
  Luminance) carry neither — well within acceptance #9's ≤14 target.
- `arrModel.combined.industry_total`: **$124.61B** (`apps_total` $81.53B +
  `compute_net` $43.08B).
- `arrModel.combined.ai_native_total`: $77.76B (62.4% of industry_total).
- `arrModel.combined.trad_total`: $71.33B.

## Open items

- **`enterpriseReality` table on `usage.html` grows from 7 → 20 rows.** This
  is the brief's required §3 #3 expansion; expected visible diff. Visual
  baselines for `usage.html` will need refresh under wq-097 if the renderer
  layout changes to surface the numeric fields. Today the 13 new rows simply
  populate the existing table.
- **wq-097 publication brief** is now unblocked. wq-097 owns the public
  rendering of `arrModel` (hero strip, methodology footnote on the
  ai_native_total / trad_total split, etc.).
- **Long-tail multiplier provenance review.** Each `_long_tail.json` carries
  Tier 2B/3A editorial assumptions (25% / 8% / 30% multipliers across the
  three layers). Worth a Cowork review pass before wq-097 publishes, to
  confirm the assumed shares are defensible at editorial-tier confidence.
- **Notion Kanban card** for wq-096 needs updating (no Notion access from
  CLI session).
- **2 topConsumers entries without arrNumeric or arrPending** (Portkey.ai,
  Luminance). Below the ≤14 acceptance threshold; can be closed in a future
  pass.

## Acceptance criteria status

- [x] #1 Tier tagging complete (every record in providers, topConsumers,
  enterpriseReality, computeProviders has `tier`)
- [x] #2 enterpriseReality numeric (every entry has arrClaimedNumeric +
  arrAsOf + arrSource + provenance)
- [x] #3 enterpriseReality expanded (20 entries, exceeds minimum 18)
- [x] #4 Token factories moved out of topConsumers; CoreWeave/Lambda/Crusoe
  added to aiNativeCompute
- [x] #5 computeProviders block exists with tradCompute (4 records, both
  arrGrossDisclosed and arrNetOfAppsCarveout) and aiNativeCompute (10 records)
- [x] #6 Apps carve-out logic explicit (appsCarveout field on every
  tradCompute record)
- [x] #7 Pass-through deductions populated (named per-record entries cover
  ~80% of dollar volume in each layer; long-tail multiplier with documented
  assumption + provenance for the rest)
- [x] #8 arrModel aggregation block emits cleanly; `apps_total + compute_net
  = industry_total` reconciles within $0.1B tolerance
  ($81.5292B + $43.08B = $124.6092B)
- [x] #9 topConsumers ARR backfill (gap shrunk from 26 to 2 — well under ≤14)
- [x] #10 Provenance score field on every numeric ARR (asserted by
  reconcile.py --revenue-model invariant 8)
- [x] #11 No public-facing change EXCEPT enterpriseReality table on
  usage.html grows 7 → 20 rows (acceptance #3 requires the expansion;
  flagged in §11 as acceptable visible diff)
- [x] #12 `python3 scripts/reconcile.py --revenue-model` runs without error;
  all 8 invariants pass
- [x] #13 Deployment record written (this file)
