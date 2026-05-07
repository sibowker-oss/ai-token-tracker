---
id: wq-090
title: Revenue Ledger — Hyperscaler channel correction & Who Pays relabel
stage: Scoped
priority: H
owner: Simon (impl: Claude Code in VS Code)
created: 2026-05-06
status: ready_for_handoff
parent_context: /Users/simonbowker/Documents/Claude/Projects/The AI Ledger/ (Cowork session 2026-05-06 — Compute Ledger review)
parent_brief: /Users/simonbowker/Developer/apac-ai-intel/docs/briefs/wq-089-compute-ledger-v2.md
depends_on: wq-089 (must ship first — Hyperscaler channel reconciles to corrected Hosted model APIs figure)
---

# wq-090 · Revenue Ledger — Hyperscaler channel correction & Who Pays relabel

## Why this brief exists

The Compute Ledger review (Cowork session 2026-05-06) surfaced two structural issues on the Revenue Ledger Sankey that became visible only when reconciling against the corrected Compute Ledger numbers:

1. **The Hyperscalers channel is overstated for the AI Native cohort.** Current channel mapping in `data/sankey_cost_structure.json` applies a flat **70/30 Model API → Hyperscaler split** to every provider's `api_pct` revenue. That's roughly right for enterprise customers (who buy via Bedrock/AOAI/Vertex for compliance/procurement reasons) but wrong for AI Natives (who go ~95% direct to OpenAI/Anthropic API for cost and speed). The cohort is mostly AI Natives, so the flat 30% Hyperscaler weight inflates the Hyperscalers channel ($3.63B today, should be ~$1.5–2B for the cohort). Once corrected, Compute Ledger pass-through (~$1B per wq-089) and Revenue Ledger Hyperscalers channel implied pass-through (~$1.2–1.6B) reconcile within tier 2A noise.
2. **The Who Pays column groups AI Natives under "SME"** alongside small businesses. AI Natives have fundamentally different cost dynamics — heavy API consumption, light headcount, no traditional SaaS revenue base — and their inclusion under SME hides what's actually happening in the demand side. Customer-archetype split (Consumer / AI Natives / Enterprises & Govs) beats size-based split (Consumer / SME / Enterprise) for an AI-revenue Ledger.

Both fixes are mechanical once the framework is decided. Both surface on the same page (`/revenue.html`). Both depend on wq-089 having shipped (so the Hyperscalers reconciliation target is the corrected Hosted model APIs number, not the inflated $11.5B pass-through figure that's currently on the Compute Ledger).

## Decisions Simon has made (do not re-litigate without flagging)

| # | Decision | Confirmed |
|---|---|---|
| D1 | **Per-archetype channel weights** replace the flat `channel_mapping`. Each provider gets an `entity_archetype` field (`frontier_lab` / `ai_native` / `enterprise_saas` / `hyperscaler` / `iaas` / `consumer_app`). The engine routes `api_pct` and `enterprise_pct` through archetype-specific weights, not a global flat split. | 2026-05-06 |
| D2 | **Archetype weights for `api_pct → Hyperscalers`:** AI Native ~10%, Frontier Lab ~5%, Enterprise SaaS ~50%, Consumer App ~0% (consumer apps don't buy through Hyperscalers). For `enterprise_pct → Hyperscalers`: AI Native ~20%, Enterprise SaaS ~60%. All Tier 2A editorial; document in `_provenance` with reasoning. | 2026-05-06 |
| D3 | **Who Pays column relabel:** `Consumer / AI Natives / Enterprises & Govs / VC-Investors`. SME segment is removed. Existing cohort entities are reclassified per their archetype (most AI Natives go to "AI Natives" segment; small business consumption of AI rolls into "Enterprises & Govs" or stays unallocated). VC-Investors stays as-is. | 2026-05-06 |
| D4 | **Reconciliation target:** post-wq-090 Hyperscalers channel value (corrected) must reconcile with wq-089's Hosted model APIs pass-through estimate within ±25% (tier 2A noise band). If it doesn't reconcile, write a `docs/decisions/open/` decision file before adjusting weights further. | 2026-05-06 |
| D5 | **Reconciliation gate** added to brief structure and CLAUDE.md (per wq-089 D6). §11 of this brief documents the cross-Ledger bridge. | 2026-05-06 |

## Open decisions — none

All decisions resolved in 2026-05-06 Cowork session.

---

## Scope

### In scope

1. **Add `entity_archetype` field** to every entity in `data/entities/*.json` (or wherever provider metadata lives). One of: `frontier_lab` / `ai_native` / `enterprise_saas` / `hyperscaler` / `iaas` / `consumer_app`. Default for existing un-tagged providers based on observed channel mix; document each archetype assignment.
2. **Schema migration on `data/sankey_cost_structure.json`:**
   - Replace flat `channel_mapping.api_pct` and `channel_mapping.enterprise_pct` with per-archetype weight tables.
   - Replace flat `segment_composition.api_to_sme/api_to_enterprise` with per-archetype splits that route into the new buyer segments.
   - Add `_provenance` entries for each archetype × channel weight, tier 2A.
3. **Sankey balancing engine update** (`scripts/derive_sankey.py` or wherever wq-062 routing logic lives — locate first). Engine reads `entity_archetype` per provider and applies the matching weights from the archetype table. Falls back to the previous flat weights for any provider without `entity_archetype` set, so the migration can be incremental.
4. **Buyer-segment relabel.** Update Sankey buyer labels: Consumer / **AI Natives** (replaces SME) / **Enterprises & Govs** (replaces Enterprise) / VC-Investors. Update colors if needed for clarity. Existing buyer values redistribute per the new archetype-routed segment composition.
5. **Re-derive `site-data.json:sankey`.** After schema and engine updates, run the full pipeline and verify:
   - Hyperscalers channel value drops from $3.63B to ~$1.5–2B (cohort scope).
   - AI Natives buyer segment appears with non-trivial value (sum of cohort AI Native customer-paid revenue, e.g. via consumption of OpenAI/Anthropic APIs).
   - Enterprises & Govs segment aggregates traditional enterprise SaaS AI buyers + government/regulated.
6. **Renderer updates on `/revenue.html`.** New buyer labels in legend and tooltips; Hyperscalers channel size visibly smaller; provenance line on the page methodology callout updated to reflect per-archetype routing.
7. **Methodology page update** (`/methodology.html`). Document the entity archetype taxonomy, per-archetype routing weights, and the rationale for relabeling SME → AI Natives. Link from Revenue Ledger page methodology callout.
8. **Reconciliation section §11** verifying corrected Hyperscalers channel reconciles to wq-089 Hosted model APIs pass-through within tier 2A noise (±25%).

### Out of scope

- Changing the Sankey topology (still 4 columns, same flow logic).
- Modifying provider-side entity records beyond adding `entity_archetype` (no rev-share or financial restatements).
- Building a separate AI Native segment analysis page (just the relabeling).
- Capital Ledger or Compute Ledger changes (Compute is wq-089; Capital is future).
- The `marginPcts.Hyperscalers: 0.20` channel margin — stays as-is. (Per Cowork session: 20% is roughly defensible across both AI Native and enterprise routing through Hyperscalers; not load-bearing on the relabel.)
- VC subsidy methodology — out of scope.

---

## Files touched

### Modified
- `data/sankey_cost_structure.json` — schema migration: per-archetype routing weights replace flat splits; `_provenance` updated; segment_composition rewritten per archetype.
- `data/entities/*.json` (or central provider registry — locate) — add `entity_archetype` per entity. Audit list: every entity that currently appears as a provider in the Sankey.
- `scripts/derive_sankey.py` (or equivalent — wq-062 introduced the routing engine; locate first) — read `entity_archetype` and apply archetype-specific weights.
- `revenue.html` — buyer labels updated (legend, tooltips, any hardcoded references); methodology callout text refreshed.
- `methodology.html` — new §"Revenue Ledger — entity archetype taxonomy" section.
- `site-data.json` — regenerated by the pipeline; Sankey buyers + channels values shift. **Expected. Do not roll back.**

### Read-only references
- `docs/briefs/wq-062-sankey-assembly-per-provider-routing.md` — original per-provider routing logic; retains as the framework wq-090 extends.
- `docs/briefs/wq-089-compute-ledger-v2.md` — provides the Hosted model APIs pass-through reconciliation target.
- Each entity's existing `revenue_by_channel` block — input to the routing engine; not modified by this brief.

### New
- None — schema migration and value updates only.

---

## Implementation outline

1. **Branch off main** as `wq-090-revenue-ledger-hyperscaler-archetype`. Single PR.
2. **Phase 1 — locate routing engine.** Find the script that consumes `data/sankey_cost_structure.json:channel_mapping` and writes `site-data.json:sankey` (likely `scripts/derive_sankey.py` or sankey-related script under wq-062). Confirm before editing.
3. **Phase 2 — entity archetype audit.** Walk every entity that appears as a Sankey provider, decide its archetype, populate the `entity_archetype` field. Default heuristics:
   - OpenAI, Anthropic, Google/Gemini, Mistral, xAI, Cohere, DeepSeek → `frontier_lab`
   - AI-Native scale-ups (Glean, Cursor, Harvey, ElevenLabs, Perplexity, Suno, Runway, Character, Midjourney, Cohere-app-side, etc.) → `ai_native`
   - Microsoft, Google Cloud, AWS, Oracle Cloud, IBM Cloud → `hyperscaler`
   - CoreWeave, Lambda, Crusoe, Nebius → `neocloud` (treat as `hyperscaler` for routing)
   - Together, Fireworks, Groq, Replicate, Modal, Baseten → `iaas`
   - Salesforce, ServiceNow, Workday, SAP, Adobe (traditional SaaS layering AI features) → `enterprise_saas`
   - ChatGPT consumer revenue, Claude.ai consumer revenue → `consumer_app` (these flow under the parent frontier_lab entity but with consumer-app-style channel mix)
   - Document each assignment briefly. Commit.
4. **Phase 3 — schema migration on cost structure.** Restructure `channel_mapping`:

   ```json
   "channel_mapping": {
     "subscription_pct": [{"channel": "Model Subs", "weight": 1.0}],
     "api_pct_by_archetype": {
       "frontier_lab":     [{"channel": "Model API", "weight": 0.95}, {"channel": "Hyperscalers", "weight": 0.05}],
       "ai_native":        [{"channel": "Model API", "weight": 0.90}, {"channel": "Hyperscalers", "weight": 0.10}],
       "enterprise_saas":  [{"channel": "Model API", "weight": 0.50}, {"channel": "Hyperscalers", "weight": 0.50}],
       "consumer_app":     [{"channel": "Model API", "weight": 1.00}, {"channel": "Hyperscalers", "weight": 0.00}],
       "_default":         [{"channel": "Model API", "weight": 0.85}, {"channel": "Hyperscalers", "weight": 0.15}]
     },
     "enterprise_pct_by_archetype": {
       "ai_native":        [{"channel": "Trad. SaaS", "weight": 0.80}, {"channel": "Hyperscalers", "weight": 0.20}],
       "enterprise_saas":  [{"channel": "Trad. SaaS", "weight": 0.40}, {"channel": "Hyperscalers", "weight": 0.60}],
       "_default":         [{"channel": "Trad. SaaS", "weight": 0.50}, {"channel": "Hyperscalers", "weight": 0.50}]
     }
   }
   ```

   Update `_provenance` for each new weight tier 2A with reasoning. Commit.
5. **Phase 4 — segment composition migration.** Replace `segment_composition.api_to_sme/api_to_enterprise` with per-archetype splits that route into the new buyer segments:

   ```json
   "segment_composition_by_archetype": {
     "frontier_lab":     {"subscription_to": "consumer", "api_to_ai_natives": 0.70, "api_to_ents_govs": 0.30, "enterprise_to_ents_govs": 1.0},
     "ai_native":        {"subscription_to": "consumer", "api_to_ai_natives": 0.30, "api_to_ents_govs": 0.70, "enterprise_to_ents_govs": 1.0},
     "enterprise_saas":  {"subscription_to": "consumer", "api_to_ents_govs": 1.0,   "enterprise_to_ents_govs": 1.0}
   }
   ```

   Document in `_provenance`. Commit.
6. **Phase 5 — engine update.** Modify the routing engine to:
   - Read each provider's `entity_archetype` from its entity record.
   - Look up the matching `api_pct_by_archetype` and `enterprise_pct_by_archetype` weights.
   - Apply to that provider's `revenue_by_channel.api_pct` and `enterprise_pct` values when computing channel routing.
   - Aggregate by buyer segment using `segment_composition_by_archetype`.
   - Fall back to `_default` if `entity_archetype` is missing on an entity.
   - Commit.
7. **Phase 6 — buyer relabel.** Search `revenue.html` and any sankey-rendering code for hardcoded references to "SME" and "Enterprise" buyer labels. Replace with "AI Natives" and "Enterprises & Govs" respectively. Update colors if the relabel makes existing colors ambiguous. Commit.
8. **Phase 7 — re-derive site-data.** Run the full pipeline. Verify Hyperscalers channel value drops to ~$1.5–2B and AI Natives buyer segment appears with sensible value. If Hyperscalers >$2.5B or <$1B after re-derivation, stop and write a decision file (per D4).
9. **Phase 8 — methodology page.** Add §"Revenue Ledger — entity archetype taxonomy" with table of archetypes and their channel-routing logic. Link from `/revenue.html` methodology callout.
10. **Phase 9 — release-check + visual baseline.** Re-snapshot `/revenue.html`. Sankey will look different (smaller Hyperscalers ribbon, new AI Natives segment). Take new baselines on desktop + mobile.
11. **Phase 10 — deployment record + Notion update.**

---

## Acceptance criteria

- [ ] `data/sankey_cost_structure.json` has new `api_pct_by_archetype` and `enterprise_pct_by_archetype` blocks with `_provenance` per archetype × channel.
- [ ] Every Sankey-relevant entity has an `entity_archetype` field set.
- [ ] Routing engine reads `entity_archetype` and routes per-archetype weights; falls back to `_default` on missing archetype.
- [ ] `site-data.json:sankey.channels` shows Hyperscalers value at **~$1.5–2B** (was $3.63B). If outside range, decision file written before adjusting weights.
- [ ] `site-data.json:sankey.buyers` shows the four new labels: Consumer / AI Natives / Enterprises & Govs / VC-Investors. SME label is gone everywhere.
- [ ] `/revenue.html` renders the new buyer labels in legend and tooltips. Sankey ribbon to Hyperscalers is visibly smaller.
- [ ] Methodology page has new archetype-taxonomy section explaining the routing rules.
- [ ] **§11 Reconciliation** verified: corrected Hyperscalers channel × (1 − margin) = ~$1.2–1.6B, reconciles with wq-089 Hosted model APIs pass-through ~$1B within ±25% (tier 2A noise).
- [ ] `npm run build-lint` passes; `npm run release-check` passes (with new visual baselines).
- [ ] Deployment record at `docs/deployments/` documents archetype assignments and any tactical decisions.

---

## Test plan

1. **Engine unit test.** Add tests for the new per-archetype routing — at least one entity per archetype, verify correct channel routing, verify fall-through to `_default` for missing archetype.
2. **Reconciliation test.** Cross-reference: pull `site-data.json:sankey.channels[Hyperscalers].value` and `site-data.json:compute.hosted_model_apis_pass_through_2025_usd_b`. Assert ratio is within ±50% (allowing for cohort scoping difference). This becomes a permanent release-check.
3. **Visual snapshot.** Re-baseline `/revenue.html` and `/methodology.html` Playwright snapshots (desktop + iPhone + Android viewports).
4. **Build lint.** `npm run build-lint` — provenance fields preserved on every changed entity record.
5. **Manual cross-page check.** After both wq-089 and wq-090 ship, open `/compute.html` and `/revenue.html` side by side. Verify the Compute pass-through (~$1B), Revenue Hyperscalers (~$1.7B), and the Compute methodology callout's reconciliation note all tell the same story.

---

## Edge cases

- **Entities with mixed archetypes.** Some providers operate as both frontier lab AND consumer app (OpenAI = frontier_lab + ChatGPT consumer; Anthropic = frontier_lab + Claude.ai consumer). Handle by routing each entity's `revenue_by_channel.subscription_pct` separately (always to `consumer_app` channel routing) from its `api_pct` (to `frontier_lab` archetype routing). Document in implementation notes.
- **Hyperscalers' OWN AI revenue (Azure AI, GCP AI, AWS AI).** This is the dollar-side flow tracked in the Compute Ledger; it shouldn't appear as a "buyer paying through Hyperscalers" because hyperscalers are the seller of compute, not a customer here. Confirm the Sankey treats hyperscalers as providers only, not as buyer-side entities.
- **Default for un-tagged entities.** Set conservatively to skew toward direct (Model API/Trad. SaaS) rather than Hyperscalers — under-counting Hyperscalers is editorially safer than over-counting (which is the bug we're fixing).
- **Reconciliation outside ±25%.** Per D4: do NOT silently re-tune weights to hit the target. Write a decision file naming the gap and the candidate explanations (cohort scope, archetype assignment, weight calibration).
- **Backward compatibility.** Existing Notion cards, prior briefs, and any external references to the SME label remain valid as historical record. Don't rewrite history; just forward-going the label changes.

---

## Definition of done

- All acceptance criteria checked.
- Brief copied to `docs/briefs/wq-090-revenue-ledger-hyperscaler-and-who-pays.md` (already done at handoff).
- Deployment record written.
- Notion card moved to Done.
- Cross-Ledger reconciliation between Compute (wq-089) and Revenue (wq-090) verified end-to-end at the rendered-page level.

---

## §11 Reconciliation (per CLAUDE.md cross-Ledger rule)

| Revenue Ledger figure (post-wq-090) | Matching Ledger figure | Expected relationship | Bridge |
|---|---|---|---|
| Hyperscalers channel value (~$1.5–2B) | Compute Ledger Hosted model APIs segment gross 2025 (per wq-089: ~$3.5–5.5B ecosystem) | Revenue Ledger Hyperscalers (cohort) ⊂ Compute Ledger Hosted model APIs segment (ecosystem) | Cohort subset of Hosted model APIs customers. Gap of ~$2–3.5B is non-cohort enterprise spend (Fortune 500 buying Bedrock/AOAI outside the 9-source cohort). Documented on methodology page; not covered by Revenue Ledger. |
| Hyperscalers channel × (1 − margin 20%) ≈ $1.2–1.6B implied pass-through | Compute Ledger Hosted model APIs segment pass-through (~$1B) | Approximately equal at the cohort-subset level | Both are estimates of "lab share of cloud-resold token API" within the cohort scope. Reconciles within tier 2A noise (±25%). |
| AI Natives buyer segment | Sum of cohort entity AI Native customer-paid revenue | Equal by construction | The buyer segment aggregates per-entity customer-paid amounts after archetype routing. No external reconciliation needed; it's a direct re-classification of existing cohort data. |
| `totalCustomerRevenue` (~$17.36B) | Compute Ledger Layer Stack Apps figure | Identical | Layer Stack pulls live from this field per wq-089 D3. Reconciles by construction. |

---

## Handoff prompt for VS Code / Claude Code

> Implement wq-090 per `docs/briefs/wq-090-revenue-ledger-hyperscaler-and-who-pays.md`.
>
> **Pre-flight:** wq-089 must be shipped first. Verify by running `python3 scripts/derive_compute_revenue.py --print-summary` and confirming pass-through 2025 = ~$1B (not $11.5B). If still $11.5B, wq-089 hasn't shipped — stop and resume wq-089 first.
>
> This brief introduces per-archetype channel routing on the Revenue Ledger Sankey, replacing the flat 70/30 api_pct→Model API/Hyperscalers split (which is right for enterprise but wrong for AI Native cohorts). It also relabels the Who Pays column from SME/Enterprise to AI Natives/Enterprises & Govs.
>
> Work the §"Implementation outline" in order — ten phases, single PR, single shipment. Phase 1 (locate routing engine) and Phase 2 (entity archetype audit) are the load-bearing pieces; everything downstream is mechanical.
>
> All five decisions (D1–D5) are resolved at the top of the brief.
>
> Constraints:
> - Per D4: Hyperscalers channel must land at $1.5–2B post-correction. If outside that range, write `docs/decisions/open/dec-2026-05-XX-wq-090-hyperscalers-target-miss.md` before adjusting weights further. Do NOT silently re-tune.
> - Validate rendered output (per CLAUDE.md): Playwright spec must visit `/revenue.html` and assert the new buyer labels appear and the Hyperscalers ribbon is visibly smaller.
> - The §11 Reconciliation table is part of acceptance criteria — verify the cross-Ledger bridge against the live `/compute.html` post-wq-089.
>
> When finished:
> - Append a "Shipped: <date>, commit <sha>" footer to this brief.
> - Write `docs/deployments/deploy-2026-05-XX-wq-090-revenue-ledger-archetype.md`.
> - Move Notion wq-090 to Done.
> - The cross-Ledger reconciliation between Compute (wq-089) and Revenue (wq-090) is now end-to-end. Document any residual gap in the deployment record.

---

## Change log

- 2026-05-06 — drafted in Cowork as the companion to wq-089. D1–D5 confirmed. `addBlockedBy: wq-089`. Ready for repo handoff.

---

**Shipped:** 2026-05-07 — branch `wq-090-revenue-ledger-hyperscaler-archetype`, commit `edad551`. Hyperscalers channel landed at $1.70B (within D4 $1.5–2B band). Deployment record: `docs/deployments/deploy-2026-05-07-wq-090-revenue-ledger-archetype.md`.
