# wq-087 — Bulk-pipeline routing for indirect/aggregate claims (stub)

**Stage:** Idea (not yet scoped)
**Priority:** TBD (likely M — gap exists, magnitude unknown)
**Owner:** TBD
**Briefing status:** stub — needs Cowork pass to scope
**Category:** Pipeline
**Parent context:** wq-083 (curated intake v2), wq-086 (triangulation apply path)
**Created:** 2026-05-05

---

## The gap

wq-086 built triangulation routing for the **curated-intake** path (`curated_intake.py` → `claims.html` → `apply_decisions.py:apply_triangulation`). That path is the right cadence for analyst reports — Menlo, Bain, McKinsey, a16z — where the source makes aggregate market claims that need ledger comparison.

But the **bulk extraction pipelines** (`extract_claims.py`, `monitor_sources.py`, `news_monitor.py`) have no equivalent affordance. When a podcast or news article mentions an aggregate claim ("the AI infrastructure market is $80B in 2025", "enterprise GenAI spend tripled YoY"), the bulk extractor:

1. Tries to match an `entity_match_rule` → fails (no entity = "AI Infrastructure Market")
2. Lands the claim in `skipped_no_entity` on apply
3. The claim effectively disappears from the ledger

This is the same "indirect claim with no clean home" problem triangulation solves on the curated side, but happening silently on the bulk side. We don't know the volume — there's no instrumentation surfacing how many bulk claims hit this dead-end.

## Why it might matter

- Bulk pipelines process hundreds of items weekly; even a 5% indirect-claim rate = dozens of dropped signals per week
- Some of these are likely *high-signal* (a CEO interview snippet that triangulates against our market_aggregates is editorially valuable)
- Right now you have no way of knowing what's being dropped — the triangulation surfaces (claims.html / vault.html Triangulations tab) only see curated-intake output

## Possible shapes (Cowork to pick)

### Option A — instrumentation only
Add a counter + log block to `apply_decisions.py` for `skipped_no_entity` claims. Surface them in review.html or source-ledger.html so you can eyeball the dead-letter pile and decide whether the volume justifies more work.

- ✓ Cheap, fast, gives data to size the problem
- ✗ Doesn't fix the gap, just measures it

### Option B — manual routing queue
Surface the dead-letter pile in `review.html` as a "needs editorial routing" tab. Each item gets Accept / Decline / Park / **Triangulate** options. The Triangulate action opens a small modal where you pick `target_nodes` from a dropdown of valid flow-model paths and a `confidence_impact` value.

- ✓ Reuses the wq-086 apply path — once you triangulate via the modal, the claim flows through `apply_triangulation_softpark` exactly like a curated-intake one
- ✓ Keeps Opus out of the loop for the bulk path (no extra inference cost)
- ✗ Adds reviewer effort per item

### Option C — auto-triangulate on bulk fail
Detect when a bulk-extracted claim fails entity_match_rules AND looks like it's about a market aggregate (regex on "market", "industry", "sector", aggregate $-values + year). Re-route through a lightweight triangulation pass with the flow-model context loaded. Surface in claims.html alongside curated entries.

- ✓ Closes the gap without manual intervention
- ✗ ~3-5× cost per re-routed claim (loading flow-model context)
- ✗ Pattern detection is fragile — false positives waste budget

### Option D — defer (status quo + monitor)
Keep skipped_no_entity → log line. Revisit if curated-intake throughput drops or if a specific incident surfaces a high-value claim that was silently dropped.

## Open questions for Cowork

1. **Scope estimation** — how often do bulk extractors hit `skipped_no_entity` today? Need 1-2 weeks of instrumentation to size before scoping. **A is the precondition for B/C.**
2. **Editorial principle** — is "every claim from a credible source should land somewhere in provenance" the right invariant? Or is silent drop acceptable for low-quality bulk items?
3. **Cost ceiling** — what's the budget for indirect-claim routing? wq-086 (curated only) is essentially free since manual runs are infrequent. Wiring this into bulk could meaningfully shift monthly Opus spend.

## Out of scope (assumed unless Cowork says otherwise)

- Reworking `entity_match_rules` to be more permissive — that's an orthogonal classifier-quality problem
- Adding triangulation generation to extract_claims.py / news_monitor.py prompts — that's the wrong level (per-claim extractors don't have flow-model context)
- Backfilling historical `skipped_no_entity` claims — out of scope; this is a forward-looking instrumentation + routing brief

---

## Suggested first move

**Ship Option A first** as a 1-hour instrumentation commit. Run for 1-2 weeks, then re-scope B vs C vs D based on actual volume.
