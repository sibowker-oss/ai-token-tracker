# Decision: Triangulation apply semantics

**WQ:** wq-083 (raised during v2 ship); follow-up scoped as wq-086
**Date raised:** 2026-05-05
**Date resolved:** 2026-05-05
**Status:** Resolved
**Context:** wq-083 v2 produces structured `triangulates` claims with `target_nodes`, `derivation`, `implied_value`, and `confidence_impact`. The review UI renders the derivation card. But `apply_decisions.py` has no awareness of the `triangulation` block — it only reads `entity` + `metric` + `value`. A triangulated claim like Menlo "Enterprise GenAI = $37B" (entity = "Enterprise Generative AI Market", not a real ledger entity) currently lands in `skipped_no_entity` on apply. Result: accepting a triangulation in `claims.html` produces zero change to published numbers OR provenance. Simon is blocked from accepting Menlo's 8 triangulations until the apply path is scoped.

## The core question

When a reviewer Accepts a `triangulates` claim, what should change in `entities.json` / `site-data.json`? Three sub-questions Cowork should resolve:

1. **Provenance attachment** — should the source claim be appended to the provenance block of every `target_nodes` field? Does it count toward the field's confidence tier?
2. **Value changes** — should `implied_value` ever update a target node's number, or are triangulations always commentary-only?
3. **Reviewer affordances** — what does Accept / Decline / Park mean for a triangulation in the interim, before the apply path lands?

## Options

### Option A — Commentary-only

Accepting a triangulation logs it to `data/triangulations.jsonl` (a new file) and nothing else. `entities.json` is untouched. The triangulation is queryable for editorial purposes (citations, methodology pages) but doesn't feed confidence or values.

- ✓ Simplest. Preserves the invariant "only direct claims move numbers or provenance."
- ✓ Zero risk of bad derivations propagating into the ledger.
- ✗ Wastes the structured triangulation data — the confidence-tier signal in the flow model never sees the lift it should from strengthening triangulations.
- ✗ Doesn't match what the brief implies (`confidence_impact` exists for a reason).

### Option B — Multi-target provenance, no value change

Accepting a triangulation appends a provenance entry to **every** field named in `target_nodes`, tagged `role: "triangulates"`. The entry stores the derivation as `note` and the source claim id. The confidence-tier model (`_provenance_confidence` in `curated_intake.py` and equivalent in `apply_decisions.py`) is updated to count triangulation entries at a fractional weight (e.g. 0.5 of a corroborating claim — strengthening; -0.5 — weakening).

Numbers never change from triangulation alone — only provenance diversity / confidence tier moves.

- ✓ Most aligned with the brief's spirit.
- ✓ Lets the flow-model context the next curated intake produces reflect prior triangulations (e.g. nodes that were `[low]` in 2026-05 might read `[medium]` in 2026-06 after several strengthening triangulations).
- ✓ Reviewer always knows what they're getting: more provenance, no number changes.
- ✗ Needs new code in `apply_decisions.py` (a triangulation branch) + provenance schema migration (new `role: "triangulates"` field on prov entries) + `_provenance_confidence` weighting update + a UI surface in vault.html / source-ledger.html so triangulation provenance is visible but distinct from direct claims.
- ✗ Two open sub-questions: how is the fractional-weight chosen (0.5 is a guess), and does a `weakens` triangulation actually downgrade an existing field's confidence — or just record contradictory evidence without moving the tier?

### Option C — Provenance + opt-in value update via `implied_value`

Option B, plus: when `triangulation.implied_value` is non-null and the delta vs current value crosses the materiality threshold (≥10%), the reviewer is shown a "promote implied_value to update" checkbox in the claim card. If checked at accept time, an additional update record is generated targeting that single node, with the derivation as the comparison_note.

Default off — reviewer must opt in per claim.

- ✓ Captures the "Menlo implies abridge ARR is 2x undercounted" case where the derivation is clean enough to act on.
- ✓ Conservative by default — needs explicit reviewer action to move a number.
- ✗ Doubles the apply-path code complexity. Risks: a confidently-stated but wrong derivation gets one-click accepted.
- ✗ Triangulations often span multiple target_nodes; `implied_value` is single-valued by design. Has to be clearly defined when this option is even available.

### Option D — Defer to direct re-extraction

Triangulations stay commentary-only in the apply path forever. When a triangulation `weakens` an existing position, the editorial response is to dispatch a *direct* extraction against the original source's primary references — not to mutate the ledger from the triangulation itself.

- ✓ Strictest data-integrity stance: every published number traces back to a direct claim against a primary source.
- ✓ No new code in apply_decisions.py at all.
- ✗ Throws away the confidence-tier signal entirely.
- ✗ The "indirect evidence improves confidence" idea — the entire reason for `confidence_impact` in v2 — gets dropped.

## Recommendation (Claude Code, 2026-05-05)

**Option B as the v3 target, with a small interim change for v2.**

The reasoning:

- The flow-model context in v2 already uses provenance confidence to flag triangulation targets. If triangulations never feed back into that confidence, the flow model's signal degrades over time as direct claims accumulate but indirect evidence doesn't. Option B closes that loop without letting derivations move published numbers.
- Option C is a useful escalation valve but doesn't need to ship at the same time. Add it if reviewer behavior shows that triangulations with clean `implied_value` are routinely being mirrored manually anyway.
- Option D is too strict — it ignores that the brief explicitly designed `confidence_impact` to mean *something*.
- Option A is too lossy.

The fractional-weight question (0.5? 0.33? 1.0?) is the one editorial call Cowork should make explicitly. My instinct is 0.5 for `strengthens`, -0.25 for `weakens` (asymmetric so a single weakening triangulation doesn't tank a well-sourced position, but several together can flag a node for review).

### Interim change for v2 — until v3 lands

Right now, an Accepted triangulation silently no-ops. That's bad: Simon can't tell which triangulations he's "accepted" vs lost. Two options:

- **Block accept on triangulations** in `claims.html` — disable the Accept button when `dedup_status == "triangulates"` until the apply path lands. Park is the only positive action; the derivation card stays visible.
- **Soft-park on accept** — in `apply_decisions.py`, recognise `comparison_type == "triangulates"`, route to a `decisions/triangulations-pending.json` log instead of attempting a normal apply. When the apply path lands in v3, this file is replayed.

The second option is preferable — it preserves Simon's accept signal so v3 can replay it.

## Resolution

**Resolved:** 2026-05-05 (Cowork session, post-v2 ship)
**Decided by:** Simon
**Follow-up:** wq-086 (apply path + provenance migration + UI surfaces)

### 1. Option

**Option B — multi-target provenance, no value change.**

A and D throw away the `confidence_impact` signal that v2 was explicitly designed to produce — choosing either makes the derivation block dead scaffolding. C doubles apply-path complexity for an edge case: most triangulations span multiple `target_nodes`, so `implied_value` is null on most of the Menlo 8. The single-target, clean-implied-value case (e.g. abridge ARR) is the exception, not the rule. Add C as a follow-on only if reviewer behaviour shows triangulations with clean `implied_value` are routinely being mirrored manually.

### 2. Fractional weights for confidence-tier contribution

| `confidence_impact` | Weight contribution | Notes |
|---|---|---|
| `strengthens`  | **+0.5** | Half a corroborating direct claim |
| `widens_range` | **+0.25** | Partial validation — different methodologies landing in the same neighbourhood IS evidence of directional accuracy when the underlying number is poorly observed |
| `weakens`      | **−0.25** | Asymmetric — single weakening shouldn't tank a well-sourced position |

**Editorial principle behind `widens_range = +0.25` (not 0):** For numbers where the ground truth is largely unobserved externally (e.g. "Enterprise GenAI market size"), an independent methodology landing in the same neighbourhood as the ledger value IS partial corroboration, not scope ambiguity. The Menlo $37B Enterprise GenAI vs our $28.9B is the canonical case: bottom-up sankey vs top-down survey arriving directionally aligned is editorially meaningful. Defaulting `widens_range` to 0 throws that signal away.

**Reviewer override (Cowork addition):** The model's `confidence_impact` classification is a guide, not a verdict. `claims.html` must let the reviewer flip the classification at accept time (e.g. promote a `widens_range` to `strengthens`, or downgrade an over-confident `strengthens` to `widens_range`). The accepted classification — including the override flag and reviewer note — is what gets written to the provenance entry, not the model's first pass.

**Hard cap (Cowork addition to Code's recommendation):** Triangulations alone **cannot promote a field past `medium` confidence.** "High" confidence requires either ≥1 authoritative direct claim or ≥2 corroborating direct claims. Indirect evidence may lift `low → medium`; it must not lift `medium → high`. This preserves the existing invariant that the highest tier is reserved for direct, primary-source evidence.

**`weakens` interaction:** A single weakening triangulation does not move tier on its own. Two or more weakening triangulations against the same field set `needs_review: true` on the field's provenance block (visible in vault.html). This avoids cascading downgrades from one indirect contradiction while still surfacing a pattern when one emerges.

**`widens_range` interaction:** Records the provenance entry with +0.25 weight. The reviewer can additionally tag the field for the `scope_uncertain` surface in vault.html if they want to revisit the boundary later — but this is an explicit action, not a default.

### 3. Routing model (Cowork clarification)

Direct claims route via `entity_match_rules` + `field_match_rules` (regex on claim text). **Triangulations must route via `target_nodes` paths** (e.g. `sankey.buyers.Enterprise`, `market.2025.enterprise_capex`) — the existing matcher will silently drop them, which is exactly the v2 → apply_decisions.py gap. wq-086 should add a parallel apply path keyed on `target_nodes`, not bolt a branch onto the existing matcher. The brief should be explicit about this.

### 4. Interim behaviour (until wq-086 lands)

**Soft-park, shipped as commit 1 of the wq-086 branch.**

`apply_decisions.py` recognises `comparison_type == "triangulates"` (or `dedup_status == "triangulates"`) and routes the claim to `data/triangulations-pending.json` instead of attempting normal apply. The accepted-but-unapplied claim is still logged with full payload (decision id, target_nodes, derivation, confidence_impact) so the full apply path in wq-086 can replay the file with no signal loss.

If wq-086 is delayed beyond the next session for any reason, lift the soft-park into its own small commit and ship it standalone — do not fall back to disabling Accept in claims.html. Simon's triage signal from the Menlo 8 (and future curated intakes) is too valuable to drop on the floor.

### 5. Schema migration (informational — full spec in wq-086)

Provenance entries gain an optional `role` discriminator (alongside the existing `role: "supports"` field added by `apply_accepted`):

- `role: "supports"` — direct claim (existing)
- `role: "triangulates"` — indirect claim with arithmetic derivation (new)

Triangulation entries additionally store: `confidence_impact`, `derivation`, `target_node` (the specific path this entry attaches to — split out from the source claim's full `target_nodes` array), `implied_value` (preserved for future Option C work, ignored at apply time today).

### 6. What wq-086 has to deliver

1. Triangulation apply branch in `apply_decisions.py` (target_nodes-keyed routing)
2. Provenance schema migration — new `role` discriminator + triangulation fields (including the reviewer's accepted `confidence_impact` and any override flag)
3. `_provenance_confidence` weighted-tier calc (apply_decisions.py and curated_intake.py both — they must agree)
4. Tier-promotion cap (`medium` ceiling for triangulation-only contributions)
5. `needs_review` flag on field provenance (auto: ≥2 weakens triangulations; manual: reviewer-set scope_uncertain)
6. **`claims.html` reviewer override** — UI control to flip `confidence_impact` (strengthens / widens_range / weakens) before accepting; accepted value is what gets written to provenance
7. vault.html surface for triangulation entries (distinct visual from direct claims)
8. source-ledger.html surface for the `data/triangulations-pending.json` replay record
9. Replay path: on first run after wq-086 lands, drain `triangulations-pending.json` through the new apply branch
10. Soft-park branch as commit 1 (above)

### 7. Out of scope for wq-086

- Option C (opt-in `implied_value` updates) — separate brief if/when needed
- Re-extraction-against-primary-sources workflow (Option D's editorial fallback for `weakens` triangulations) — orthogonal feature
- Auto-regenerating site-data.json from new triangulation provenance — wq-086 should write to entities.json provenance only; downstream renderers pick up on next normal run
