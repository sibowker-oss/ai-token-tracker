# wq-086 — Triangulation Apply Path + Provenance Migration

**Parent context:** wq-083 v2 (curated intake — flow model + triangulation) shipped 2026-05-05 producing structured `triangulates` claims with `target_nodes`, `derivation`, `implied_value`, and `confidence_impact`. The review UI renders the derivation card. But `apply_decisions.py` has no awareness of the `triangulation` block — it only reads `entity` + `metric` + `value` and routes via `entity_match_rules`. Triangulated claims (where the source `entity` is a market segment like "Enterprise Generative AI Market", not a real ledger entity) currently fall into `skipped_no_entity` on apply. Result: accepting a triangulation in `claims.html` produces zero change to published numbers OR provenance. Simon's 8 Menlo triangulations are blocked from acceptance until this lands.

**Resolution doc:** `docs/decisions/resolved/dec-2026-05-05-triangulation-apply-semantics.md` — read this first. It picks Option B (multi-target provenance, no value change), sets fractional weights (+0.5 / +0.25 / -0.25), caps tier promotion at `medium`, and specifies a reviewer override on `confidence_impact` at accept time.

**Stage:** Scoped
**Priority:** H (blocking acceptance of valid Menlo triangulations; further curated intakes will produce more triangulations that also can't apply)
**Owner:** Claude Code (implementation), Simon (review UX feel + final accept on Menlo 8 once shipped)
**Briefing status:** complete
**Category:** Pipeline
**Estimated effort:** 1 Claude Code session (medium-large)
**Files touched:**
- `scripts/apply_decisions.py` — new triangulation branch, target_nodes-keyed routing, weighted confidence calc
- `scripts/curated_intake.py` — `_provenance_confidence` updated to read triangulation entries with weighted contributions; tier-cap logic
- `claims.html` — reviewer override control on `confidence_impact` for triangulates claims
- `vault.html` — surface triangulation provenance entries (distinct visual from direct claims); show `needs_review` and `scope_uncertain` flags
- `source-ledger.html` — surface `data/triangulations-pending.json` replay record
- `data/triangulations-pending.json` — new file (created by soft-park branch in commit 1)
- `ARCHITECTURE.md` — add triangulation apply path to the §Apply section
- `metric-schema.json` — optionally add a `target_node_match_rules` block if mapping is needed (TBD during implementation; may be unnecessary if `target_nodes` paths are already canonical)

---

## §Decisions — already resolved (no Simon input needed)

All editorial calls are settled in the Resolution doc. Implementation should follow these without re-litigating:

1. **Option B** (multi-target provenance, no value change) — triangulations don't move numbers, only confidence and provenance.
2. **Weights:** `strengthens` +0.5, `widens_range` +0.25, `weakens` -0.25. `widens_range` is a small positive because partial overlap from a credible outside source on a poorly-observed number is editorial validation.
3. **Tier-promotion cap:** triangulations alone cannot promote a field past `medium` confidence. `low → medium` allowed; `medium → high` requires direct claim evidence.
4. **`weakens` interaction:** single weakens does not move tier; ≥2 weakens against same field sets `needs_review: true` on the prov block.
5. **Routing model:** triangulations route via `target_nodes` paths, NOT via `entity_match_rules`. New code path; do not bolt onto existing matcher.
6. **Soft-park first.** Commit 1 of this branch is the soft-park behaviour (route `dedup_status == "triangulates"` to `data/triangulations-pending.json`). Everything else builds on that.
7. **Reviewer override.** `claims.html` lets the reviewer flip `confidence_impact` before accepting. The accepted value is what gets written to the provenance entry.
8. **`implied_value` is preserved on the provenance entry but ignored at apply time.** This leaves the door open for a future Option C without locking us in.

---

## 1. Why this exists

v2 produces a structured `triangulation` block on each `triangulates` claim. The review UI shows it. But the apply step throws it on the floor. The fix is to:

1. Stop silently dropping triangulations on accept (soft-park).
2. Build the apply branch that reads `target_nodes` and writes provenance entries with the `triangulates` role.
3. Update the confidence calc to count those entries at the right weight.
4. Surface them in vault.html so reviewers and readers can see what's been triangulated against what.

## 2. Architecture

```
claims.html [Accept]                       data/triangulations-pending.json
       │                                              ▲
       ▼                                              │ commit 1: soft-park
review-decisions-{date}.json   ──►  apply_decisions.py
                                              │
                     ┌────────────────────────┼────────────────────────┐
                     ▼                        ▼                        ▼
            (existing direct path)   (NEW triangulation path)   (existing decline/park)
                     │                        │
                     ▼                        ▼
            entities.json (entity-keyed)   entities.json (target_node-keyed)
            provenance: role=supports     provenance: role=triangulates
                                          + confidence_impact, derivation, target_node
```

Key structural points:

- The triangulation path runs **per `target_node` in the source claim's `target_nodes` array**, not once per claim. A single Menlo triangulation with 3 target_nodes writes 3 provenance entries (one per target).
- Each entry stores: `id` (derived from the source claim id + target_node hash), `role: "triangulates"`, `confidence_impact`, `derivation`, `target_node`, `implied_value`, plus the standard provenance fields (claim, source, date, etc.).
- The confidence calc reads BOTH `role: "supports"` and `role: "triangulates"` entries but applies the cap and the fractional weights to triangulating ones.

## 3. Acceptance criteria

The work is done when:

1. **Soft-park lands first (commit 1).** `apply_decisions.py` detects `comparison_type == "triangulates"` (or `dedup_status == "triangulates"`) and routes the full claim payload to `data/triangulations-pending.json` instead of attempting normal apply. The pending file accumulates an array of pending entries with full claim, decision metadata, and accept timestamp. Logged clearly in `apply_decisions.log` so the audit trail shows the soft-park.

2. **Triangulation apply branch.** `apply_decisions.py` gains a function (e.g. `apply_triangulation`) that:
   - Reads the source claim's `triangulation.target_nodes` array
   - For each target_node, resolves it to an `entities.json` field (parse `sankey.buyers.Enterprise` → which entity holds Enterprise sankey data; parse `market.2025.enterprise_capex` → market_aggregates 2025 enterprise_capex; parse `<slug>.<year>.<field>` → entity slug + year + field)
   - Appends a provenance entry with `role: "triangulates"` and the fields listed in §2
   - Recalculates confidence with the weighted rule (§3.4)
   - Emits a clear log line per target_node written

3. **Target_node resolver.** A helper (e.g. `resolve_target_node(path)`) that takes a flow-model path string and returns `(entity_slug | "market_aggregates", year_key | None, field_key)`. Should handle:
   - `sankey.buyers.<segment>` — routes to the sankey entity (likely `entities.json` market_aggregates or a dedicated sankey holder; check what curated_intake.py wrote for these in the smoke output)
   - `market.<year>.<field>` — routes to `market_aggregates[year][field]`
   - `<slug>.<year>.<field>` — routes to entity by slug, financials[year][field]
   - `<slug>.current.<field>` — routes to entity by slug, current[field]
   - Unknown paths: log + skip cleanly, increment a counter visible in the apply summary

4. **Weighted confidence calc.** `_provenance_confidence` updated in BOTH `curated_intake.py` AND `apply_decisions.py` (they must agree — the curated intake reads the same provenance the apply path writes). Algorithm:
   ```
   direct_strong = count(role==supports, weight in [authoritative, corroborating])
   if direct_strong >= 1 and weight==authoritative present  → "high"  (existing rule)
   if direct_strong >= 2                                    → "high"  (existing rule)
   triangulation_score = sum(weights of role==triangulates entries) where:
       strengthens  = +0.5
       widens_range = +0.25
       weakens      = -0.25
   tentative_tier = existing_tier_from_direct
   if tentative_tier == "low" and triangulation_score >= 0.5  → "medium"
   if tentative_tier in ("low","medium") and tentative_tier promoted by triangulations → cap at "medium"
   if count(weakens triangulations) >= 2                    → set needs_review = true (does NOT downgrade tier on its own)
   ```
   The cap rule is the editorial invariant: indirect evidence cannot promote `medium → high`.

5. **Reviewer override in claims.html.** For claims where `dedup_status == "triangulates"`, render a small control next to the existing derivation card that lets the reviewer set `accepted_confidence_impact` to one of `strengthens | widens_range | weakens` (default = the model's `triangulation.confidence_impact`). The decision payload written to `review-decisions-{date}.json` includes `accepted_confidence_impact`. `apply_decisions.py` reads `accepted_confidence_impact` first; falls back to `triangulation.confidence_impact` if absent. Provenance entry stores `confidence_impact` from the accepted value AND a `model_classified_as` field if the reviewer overrode.

6. **vault.html surface.** Triangulation provenance entries render with a distinct visual from direct claims (suggest: violet accent matching the claims.html badge, "[triangulates: <impact>]" prefix or icon). Fields with `needs_review: true` get a "review needed — multiple weakens triangulations" banner. Fields the reviewer manually flagged scope_uncertain get a smaller "scope uncertain" tag.

7. **source-ledger.html surface.** A new section (or expansion of an existing one) lists triangulations that are queued in `data/triangulations-pending.json` AND triangulations that have been applied. Show: source, target_nodes, confidence_impact, accept date, derivation excerpt.

8. **Replay path.** On first run of `apply_decisions.py` after this brief ships, the script drains `data/triangulations-pending.json` through the new triangulation apply branch — same logic as fresh accepts, just sourced from the pending file instead of `review-decisions-{date}.json`. After successful drain, the pending file is moved to `data/triangulations-pending.json.replayed-{timestamp}.bak` (don't delete; audit). If any pending entries fail to apply (e.g. unresolvable target_node), they're left in a residual `data/triangulations-pending.json` and logged for review.

9. **ARCHITECTURE.md updated.** Add the triangulation apply path to the §Apply section. Reference the resolution doc.

10. **End-to-end test using Menlo 8.** After implementation:
    - Click Accept on the 8 Menlo triangulations in claims.html
    - Run `python3 scripts/apply_decisions.py --decisions review-decisions-2026-05-05.json`
    - Verify: 8 source claims produce N provenance entries (where N = sum of len(target_nodes) across the 8); confidence tiers move on the strengthens/widens_range targets; nothing in `skipped_no_entity` for any of these claims
    - Verify the headline Menlo $37B Enterprise GenAI triangulation lands correctly: 3 prov entries (Enterprise sankey, SME sankey, market.2025.enterprise_capex), each with role=triangulates and the accepted confidence_impact

## 4. Implementation outline

### 4.1 Commit 1 — soft-park (ship first, get Simon unblocked)

Smallest possible change in `apply_decisions.py`:

```python
def apply_triangulation_softpark(claim, decision_id):
    """Park a triangulation accept until the full apply path lands.

    Writes the full claim payload + decision metadata to
    data/triangulations-pending.json so wq-086 can replay it.
    """
    pending_path = REPO_ROOT / "data" / "triangulations-pending.json"
    pending = []
    if pending_path.exists():
        pending = json.loads(pending_path.read_text())
    pending.append({
        "decision_id": decision_id,
        "soft_parked_at": datetime.now().isoformat(),
        "claim": claim,
    })
    pending_path.write_text(json.dumps(pending, indent=2))
    log(f"  TRIANGULATION-SOFTPARK: parked decision={decision_id} "
        f"target_nodes={claim.get('triangulation',{}).get('target_nodes',[])}")
```

Hook this into the accept dispatch BEFORE `apply_accepted` runs:

```python
if (claim.get("comparison_type") == "triangulates"
        or claim.get("dedup_status") == "triangulates"):
    apply_triangulation_softpark(claim, decision_id)
    continue  # don't fall through to apply_accepted
```

That's it for commit 1. Get this in, push, let Simon click Accept on the Menlo 8 immediately. The full apply path can land in the next commits without him being blocked.

### 4.2 Commit 2 — target_node resolver

Build `resolve_target_node(path: str) -> tuple[str, str|None, str] | None` that maps flow-model paths to entities.json field locations. Test with the 8 Menlo target_nodes and any others in the smoke test JSON.

### 4.3 Commit 3 — apply_triangulation function + entities.json provenance writes

Mirror `apply_accepted` but write `role: "triangulates"` provenance entries. No value updates. Multi-target loop.

### 4.4 Commit 4 — weighted confidence calc

Update `_provenance_confidence` in both `apply_decisions.py` and `curated_intake.py`. Add unit tests if there's an existing test harness; otherwise verify by replaying the Menlo 8 and inspecting tier moves manually.

### 4.5 Commit 5 — reviewer override in claims.html

Small UI control on the derivation card. JS writes `accepted_confidence_impact` into the decision payload.

### 4.6 Commit 6 — vault.html + source-ledger.html surfaces

Render triangulation provenance distinctly. Show needs_review and scope_uncertain flags.

### 4.7 Commit 7 — replay + pending-file drain

Add the replay path to `apply_decisions.py`'s entry point. Run once. Move pending file to `.replayed-{ts}.bak`.

### 4.8 Commit 8 — ARCHITECTURE.md, README, deployment record

Document the new path. Write deploy-2026-MM-DD-wq-086-triangulation-apply.md.

## 5. Edge cases

- **Triangulation with empty `target_nodes` array** (shouldn't happen but Opus has been wrong before): log + skip + increment a counter; do NOT write a provenance entry with no target.
- **`target_node` resolves to a field that doesn't exist yet** (e.g. `coreweave.2025.arr` when CoreWeave doesn't have a 2025 financial block): create the field with a null value AND attach the triangulation provenance, so the field exists for future direct claims to land on. Log a "TRIANGULATION-CREATED-EMPTY-FIELD" line.
- **Same source claim accepted twice** (soft-park then full apply replay, or duplicate decision file): use `decision_id + target_node` as the dedup key; idempotent writes only.
- **Reviewer override absent in decision payload** (e.g. older decision file from before the override UI shipped): default to the model's `triangulation.confidence_impact`. No regression for replay.
- **`needs_review` race condition** when multiple weakens land in the same apply run: set the flag in a single pass after all writes are done, not incrementally.

## 6. Out of scope

- **Option C (opt-in `implied_value` updates).** Separate brief if/when reviewer behaviour shows it's needed.
- **Auto-regenerating site-data.json from triangulation provenance.** wq-086 writes to entities.json provenance only. Downstream renderers pick up on next normal `generate_site_data.py` run.
- **Re-extraction-against-primary-sources workflow** for Option D's editorial fallback on weakens triangulations. Orthogonal feature.
- **Bulk pipeline changes.** This brief is curated-intake apply only. The bulk extraction path doesn't produce triangulations.

## 7. Test plan

1. **Soft-park test (after commit 1):** Accept one Menlo triangulation in claims.html. Run apply_decisions.py. Confirm `data/triangulations-pending.json` exists with the parked entry; confirm `entities.json` is unchanged for the target_nodes; confirm log line `TRIANGULATION-SOFTPARK` appears.

2. **Resolver test (after commit 2):** Unit-call `resolve_target_node` on the 8 distinct target_node strings from the Menlo smoke output. All 8 should resolve cleanly. Add 2-3 deliberately bad strings (typo, unknown slug) and confirm graceful skip.

3. **Apply test (after commit 3):** Replay the soft-parked Menlo accept. Confirm provenance entries land on the right fields with `role: "triangulates"`. Confirm no value changes anywhere in entities.json.

4. **Confidence calc test (after commit 4):** For a target field at `low` tier with no direct claims, accept 1 strengthens triangulation. Confirm tier becomes `medium` (low + 0.5 ≥ promotion threshold). Accept a 2nd strengthens. Confirm tier stays `medium` (cap). Add 1 direct corroborating claim. Confirm tier becomes `high` (direct path).

5. **Override test (after commit 5):** Accept a `widens_range` Menlo triangulation with override → `strengthens`. Confirm the provenance entry stores `confidence_impact: strengthens` and `model_classified_as: widens_range`. Confirm the contribution to the confidence calc is +0.5, not +0.25.

6. **Surface test (after commit 6):** Open vault.html for an entity with triangulation provenance. Confirm violet accent / role="triangulates" rendering. Open source-ledger.html. Confirm pending and applied triangulations are listed.

7. **Replay test (after commit 7):** Pre-populate `data/triangulations-pending.json` with the Menlo 8. Run apply_decisions.py with no decisions file. Confirm all 8 drain through the apply branch and the pending file is renamed to `.replayed-{ts}.bak`.

8. **End-to-end test:** Fresh run from claims.html through to vault.html using a new curated intake source (ideally a different analyst report than Menlo so the test isn't circular). Confirm the loop works end-to-end.

## 8. Definition of done

- [ ] Commit 1 (soft-park) shipped — Simon unblocked on Menlo 8 within the first commit
- [ ] Triangulation apply branch in `apply_decisions.py`
- [ ] Target_node resolver covers sankey, market_aggregates, entity-by-slug paths
- [ ] Weighted confidence calc agrees between curated_intake.py and apply_decisions.py
- [ ] Tier-promotion cap enforced (triangulations cannot push past medium)
- [ ] `needs_review` flag set on ≥2 weakens against same field
- [ ] Reviewer override control in claims.html; accepted value flows through to provenance
- [ ] vault.html renders triangulation entries distinctly with needs_review and scope_uncertain flags
- [ ] source-ledger.html surfaces pending + applied triangulations
- [ ] Replay path drains data/triangulations-pending.json on first run
- [ ] Menlo 8 end-to-end test passes
- [ ] ARCHITECTURE.md updated; deployment record written
- [ ] Notion tracker updated: wq-086 → Stage: Done, Briefing Status: complete
- [ ] Session wrap-up summary in `data/session-logs/wq-086-triangulation-apply.md`

---

## §9 Session wrap-up protocol

**After all acceptance criteria are met:**

1. Run the end-to-end test using a fresh curated intake source — verify the loop.
2. Write `data/session-logs/wq-086-triangulation-apply.md` covering: what shipped, what was tested, decisions made during implementation, known limitations.
3. Update ARCHITECTURE.md.
4. Commit and push with messages tagged `feat(wq-086): ...` per commit; final commit message: `feat(wq-086): triangulation apply path + provenance migration + reviewer override`.
5. Write deployment record at `docs/deployments/deploy-{date}-wq-086-triangulation-apply.md`.
6. Update Notion Work Tracker — wq-086 → Stage: Done, Briefing Status: complete.
7. Print final summary to console.

---

## §10 Handoff prompt for VS Code / Claude Code

```
Read the brief at /Users/simonbowker/Documents/Claude/Projects/The AI Ledger/briefings/wq-086-triangulation-apply-path.md AND the resolution doc at docs/decisions/resolved/dec-2026-05-05-triangulation-apply-semantics.md before starting. The resolution settles all editorial calls (Option B, weights +0.5/+0.25/-0.25, medium tier cap, reviewer override) — do not re-litigate them.

The work has 8 commits, ordered. Commit 1 (soft-park) ships first and unblocks Simon on 8 pending Menlo triangulations sitting in data-updates/2026-05-05-curated-menlo-genai-enterprise-2025.json. Get that committed and pushed before you start commit 2 — Simon can click Accept on the Menlo 8 immediately after commit 1 and his accepts will queue cleanly in data/triangulations-pending.json for replay later.

Key structural point: triangulations route via target_nodes paths, NOT via the existing entity_match_rules. Build a parallel apply branch (apply_triangulation), don't bolt onto apply_accepted.

Follow the §9 wrap-up protocol when done. Ping Simon to verify the Menlo 8 land correctly in the end-to-end test before closing the WQ in Notion.
```
