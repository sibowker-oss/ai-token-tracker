# Session log: wq-086 — Triangulation Apply Path

**Date:** 2026-05-05
**Branch:** main
**Commits:** 7 feature commits (1/8–7/8) + this docs commit

## What shipped

The full triangulation pipeline:

1. **Soft-park** (commit 1) — `apply_decisions.py` intercepts
   `comparison_type/dedup_status == "triangulates"` accepts and writes
   them to `data/triangulations-pending.json` instead of letting them
   silently no-op via the `entity_match_rules` matcher. Pushed first to
   unblock the Menlo 8.
2. **Target_node resolver** (commit 2) — maps flow-model paths to
   concrete entities.json/market_aggregates targets. 15 of 20 Menlo
   target_nodes resolve cleanly; the 5 skips are
   `sankey.channels.*` aggregates with no stable provenance home.
3. **`apply_triangulation`** (commit 3) — for each accepted claim,
   resolves every target_node and appends a `role: "triangulates"`
   provenance entry. Idempotent on (decision_id, target_node).
   Numbers never mutate.
4. **Weighted confidence calc** (commit 4) — `compute_provenance_tier`
   and `compute_needs_review` shared between apply_decisions and
   curated_intake. `strengthens=+0.5`, `widens_range=+0.25`,
   `weakens=-0.25`. Triangulations alone capped at `medium`.
5. **Reviewer override** (commit 5) — claims.html select on every
   triangulation card. Default is the model's classification.
   `accepted_confidence_impact` flows through to provenance; original
   model value preserved as `model_classified_as` when overridden.
6. **Vault + source-ledger surfaces** (commit 6) — Triangulations tab in
   vault.html (violet accent, needs_review banner); pending + applied
   panel in source-ledger.html.
7. **Replay path** (commit 7) — `replay_triangulations_pending` runs on
   every `apply_decisions.py` invocation. Clean drain → file moves to
   `.replayed-<ts>.bak`. Failures stay in residual for retry.
8. **Docs** (this commit) — ARCHITECTURE.md gains an "Apply:
   Triangulation path" section.

## Tests run

- `is_triangulation` + soft-park smoke test (commit 1)
- `resolve_target_node` against all 20 Menlo target_nodes + 5 bad
  inputs (commit 2)
- `apply_triangulation` headline Menlo $37B test: 3 prov entries land,
  no values mutate, replay is idempotent (commit 3)
- `compute_provenance_tier` against 13 invariants from brief §3.4 — all
  pass (commit 4)
- HTML balance sanity on claims.html / vault.html / source-ledger.html
  (commits 5, 6)
- Full softpark→drain end-to-end on a deep-copy of entities.json: 1
  drained, 3 prov entries written, file moved to .bak, idempotent
  re-run (commit 7)

## Tactical decisions logged

- Market provenance lives at `entities.market_aggregates.provenance` —
  mirrors company entity convention so the same code path reads both.
- Bare-slug `target_nodes` (LLM emitting non-canonical paths) are
  tolerated as `<slug>.<claim_year>.arr` rather than dropped.
- Drain runs every apply, not one-shot — same-run accepts soft-park
  then immediately drain.
- Fresh provenance blocks default to `confidence: "unsourced"` (was
  the misleading `"low"`).

## Known limitations

- 5 of 20 Menlo target_nodes (`sankey.channels.*`) skip by design.
  Acceptable — channels are computed aggregates. If the pattern
  becomes recurring across future intakes, promote
  `total_per_channel.<channel>` to a stored field.
- The reviewer override select doesn't persist across page reloads
  unless the reviewer also sets a decision (Accept/Decline/Park).
  This matches how notes work (existing pattern).
- `apply_triangulation` does not currently surface `scope_uncertain`
  flagging via the UI — vault.html will render the tag if a reviewer
  manually adds it to the prov block, but there's no UI affordance to
  set it. Out of scope for wq-086 per brief §6.

## End-to-end verification still pending

Simon to run:

1. Reload `claims.html`, click Accept on the 8 Menlo triangulations
   (override `widens_range` → `strengthens` on any if appropriate).
2. Run `python3 scripts/apply_decisions.py` (or with the explicit
   decisions file path).
3. Check the apply log for `TRIANGULATION:` lines per target_node.
4. Open vault.html → Triangulations tab → confirm Menlo entries
   appear at market_aggregates 2025.total_segment_enterprise,
   total_segment_sme, enterprise_capex (headline) plus the 7 other
   triangulations across providers and entities.
5. Confirm site-data.json regenerates without error.

## Notion tracker

wq-086 needs to be moved to **Done / Briefing Status: complete** in
the work tracker after Simon confirms the end-to-end verification
succeeds.
