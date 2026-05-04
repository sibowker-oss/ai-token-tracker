# Observed issues — known but not actioned

Append-only register of issues spotted during routine work that are NOT yet wq-numbered. Each row should be small enough to fix in <0.5 day; larger items get a wq-XXX tracking number instead.

Per GUIDELINES §5.4 — append-only. Don't edit past entries; resolve by adding a "resolved" row referencing the original.

| date | observed-by | area | issue | discovered-during | resolution-notes |
|---|---|---|---|---|---|
| 2026-05-04 | Claude (wq-081 source-collation Phase 1.1) | `site-data.json:entityDirectory` | Duplicate slug in entityDirectory: both `together` and `together-ai` carry `qualifies_for_detail_page=true`, double-counting Together AI in the rendered-entity total (57 → effectively 56 unique). Both list 4–8 fields with `medium` confidence; one of the two is the legacy slug from before the entity registry consolidation. Not in wq-081 scope to fix (would touch entities.json and the renderer). | wq-081 §1 of receipt — computing the 57-entity rendered list. | Untouched in Phase 1.1. Worth a 0.25-day cleanup wq-XXX in the next housekeeping window: pick canonical slug (`together-ai` is more consistent with other slug forms), redirect the legacy slug, ensure `apply_decisions.py` migrates any orphan claims. |
