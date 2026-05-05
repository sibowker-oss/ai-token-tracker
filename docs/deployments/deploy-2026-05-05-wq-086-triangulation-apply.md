# Deployment: wq-086 Triangulation apply path + provenance migration

**Date:** 2026-05-05
**WQ:** wq-086
**Branch/Commits:** main · 41700c1, 3e82835, 7653772, b337c7d, d11a54e, aa94516, 8c42aca (+ docs commit)

## What shipped

End-to-end triangulation pipeline: accept in `claims.html` → soft-park to
`data/triangulations-pending.json` → drain via `apply_decisions.py` →
`role: "triangulates"` provenance entries on every resolved `target_node`.
Numbers are never mutated (Option B per resolved decision). Reviewer
override on `confidence_impact` flows from UI → decision payload →
provenance entry. Vault and source-ledger surfaces render the pending +
applied triangulations.

### Files changed

- `scripts/apply_decisions.py` — soft-park hook (commit 1), `resolve_target_node`
  (commit 2), `apply_triangulation` + provenance writes (commit 3),
  `compute_provenance_tier` / `compute_needs_review` shared helpers
  (commit 4), `replay_triangulations_pending` + drain hook in `_main_impl`
  (commit 7).
- `scripts/curated_intake.py` — `_provenance_confidence` delegates to the
  shared helper so flow-model context shows the same tiers
  `apply_decisions.py` writes.
- `claims.html` — reviewer override select on every triangulation card;
  `accepted_confidence_impact` carried into the submitted JSON payload
  (commit 5).
- `vault.html` — new "Triangulations" tab with violet-accented rows by
  (entity, prov_key); `needs_review` banner; `scope_uncertain` tag (commit 6).
- `source-ledger.html` — pending + applied triangulation panel above the
  per-source list (commit 6).
- `ARCHITECTURE.md` — new "Apply: Triangulation path" section (commit 8).
- `docs/briefs/wq-086-triangulation-apply-path.md`, `docs/decisions/resolved/dec-2026-05-05-triangulation-apply-semantics.md`
  — moved into structured docs.

## Decisions made during implementation

- **Market provenance home**: triangulation provenance for market-level
  fields is stored at `entities.market_aggregates.provenance.<year>.<field>`
  — flat dotted key, mirrors the company entity convention. Avoids
  collision with the existing `_market_provenance` per-year block which
  serves a different purpose (engine-derived origin records).
- **Bare-slug fallback**: the LLM occasionally emits non-canonical bare-
  slug `target_nodes` (e.g. `abridge` instead of `abridge.2025.arr`).
  Resolver tolerates these as `<slug>.<claim_year>.arr` rather than
  dropping them — preserves ~half the Menlo 8 target attachments.
- **`sankey.channels.*` / `sankey.outcomes.*` skipped**: these are
  computed aggregates from buyer × routing weights, not stored fields,
  so they have no stable provenance home. Logged + counted.
- **Drain runs every apply**: rather than a one-shot replay on first run
  after ship, `replay_triangulations_pending` runs on every
  `apply_decisions.py` invocation. Same-run accepts soft-park then
  immediately drain — single steady-state path.
- **Default fresh prov tier = "unsourced"** (was "low"). Recompute via
  `compute_provenance_tier` happens immediately, so the visible default
  was misleading and produced confusing "low → unsourced" tier-move logs.

## Open items

- **End-to-end Menlo 8 verification** still pending — Simon needs to click
  Accept on the 8 triangulations in claims.html, run
  `python3 scripts/apply_decisions.py`, and confirm the headline $37B
  Enterprise GenAI claim lands as 3 prov entries (Enterprise sankey, SME
  sankey, market.2025.enterprise_capex) at impact=widens_range.
- The ~5 `sankey.channels.*` target_nodes across the Menlo 8 will skip
  cleanly (counted, no errors). If these become a recurring pattern,
  consider promoting `total_per_channel.<channel>` to a stored field.
- `claims_extracted: 0` on one earlier curated_intake run for Menlo
  (run id 17504d0e) — irrelevant now (the 23af45dc run that produced the
  current 8 triangulations is the canonical one), but worth checking
  the prompt didn't regress.
- 5 of 20 Menlo target_nodes are `sankey.channels.*` and will be skipped
  by design — the headline $37B claim is not affected.

## Acceptance criteria status

- [x] Soft-park lands first (commit 1) — Simon unblocked
- [x] Triangulation apply branch (`apply_triangulation`)
- [x] `resolve_target_node` covers sankey, market_aggregates, slug.year.field, slug.current.field, capex.bucket
- [x] Weighted confidence calc agreed between `apply_decisions.py` and `curated_intake.py`
- [x] Tier-promotion cap enforced (medium ceiling on triangulation-only)
- [x] `needs_review` flag set on ≥2 weakens against same field
- [x] Reviewer override control in claims.html; accepted value flows through
- [x] vault.html renders triangulation entries distinctly with needs_review/scope_uncertain
- [x] source-ledger.html surfaces pending + applied triangulations
- [x] Replay path drains data/triangulations-pending.json on every run
- [ ] Menlo 8 end-to-end test passes — Simon to verify
- [x] ARCHITECTURE.md updated; deployment record written
- [ ] Notion tracker updated: wq-086 → Stage: Done, Briefing Status: complete
- [x] Session wrap-up summary in `data/session-logs/wq-086-triangulation-apply.md`
