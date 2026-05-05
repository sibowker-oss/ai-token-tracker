# Decision: Triangulation apply semantics

**WQ:** wq-083 (raised during v2 ship); resolution likely scoped as a new wq-ID
**Date:** 2026-05-05
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

## Recommendation

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

[LEFT BLANK — resolved in Cowork]
