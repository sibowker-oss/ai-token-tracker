# Deployment: wq-083 curated intake v2 — flow model + triangulation

**Date:** 2026-05-05
**WQ:** wq-083
**Branch/Commit:** main / (this commit)

## What shipped

Upgraded `scripts/curated_intake.py` from the v1 flat-summary approach to the
brief's v2 flow-model approach with arithmetic-grounded triangulation.

**Files changed**
- `scripts/curated_intake.py` — full rewrite of context builder + prompt;
  new triangulation classification; output + summary updates
- `claims.html` — `triangulates` badge style + dedup_status sort priority +
  inline derivation block on claim cards
- `ARCHITECTURE.md` — Path 3 description updated to describe flow model and
  triangulation
- `data-updates/2026-05-05-curated-menlo-genai-enterprise-2025.json` —
  rewritten by smoke test (28 claims: 8 triangulates, 7 new, 13 context)
- `data-updates/curated-index.json` — auto-updated

**Behaviour added/modified**
- `build_flow_model()` replaces `build_ledger_summary()` (back-compat alias
  retained). Outputs four sections: A. revenue flow tree (sankey), B. capex
  flow tree (market + capital_sankey), C. per-entity positions tagged with
  provenance confidence (`high|medium|low|unsourced` plus ⚠ flag for
  triangulation targets), D. hardcoded composition rules.
  Output ~21k chars / ~5.4k tokens for current ledger (well under the 20k
  token soft target).
- `SYSTEM_PROMPT` rewritten to introduce the `triangulates` classification
  and the arithmetic constraint: a triangulation claim MUST include a
  `triangulation.derivation` field with an equation referencing specific
  named flow-model nodes (e.g. `sankey.buyers.Enterprise`,
  `market.2025.mag7_capex`). No equation → reclassify as `context`.
- `enrich_claim` now downgrades any `triangulates` claim missing a
  derivation to `context` and stamps the dedup_status accordingly. This
  enforces the brief's hard constraint at write time, not just at prompt time.
- `_parse_claims_json` recovers from truncated/trailing-comma JSON. Long
  analyst sources (32k chars) push the response past the previous 8192 token
  cap; v2 raises max_tokens to 16384 and salvages the last well-formed claim
  boundary on parse failure.
- CLI summary now surfaces triangulation derivations inline (with
  word-wrapping) and a "Provenance impacts" roll-up showing
  `↑/↓/↔` glyphs for `strengthens/weakens/widens_range`.
- Output JSON adds `flow_model_tokens`, `summary.triangulates`, and per-claim
  `triangulation` block. `ledger_context_tokens` retained as alias.
- `claims.html` adds a violet `triangulates` badge, sort priority above
  `new` (so triangulations get a human eyeball before generic new-entity
  claims), and an inline derivation card showing the equation, target
  nodes (as code chips), implied value, and confidence impact.

## Decisions made during implementation

The brief's §Decisions section was unannotated — I took the recommended
defaults (Opus, URL + stdin, candidates-format output through claims.html).
Tactical decisions made during implementation:

1. **Provenance confidence tier — fall back to year provenance for
   `current.X` keys.** Initial implementation reported "untracked" for
   current.arr / current.valuation when there was no `current.arr`
   provenance entry, even though every entity has year-keyed provenance for
   the same field. Fixed to fall back to the most recent year's provenance
   and renamed the no-provenance tier from "untracked" → "unsourced" (more
   accurate — the value is tracked but the provenance record is implicit).
   Both `low` and `unsourced` tiers get the ⚠ flag in the entity positions
   section so the model treats both as triangulation targets.

2. **JSON salvage on truncation rather than failure.** Long analyst reports
   (Menlo at 33k chars) push response output past max_tokens. Instead of
   dropping the whole chunk on a parse error, `_parse_claims_json` walks
   the bracket depth and salvages up to the last complete claim object,
   logging `stop_reason` for visibility. Better to return 8 of 12 claims
   than 0.

3. **`triangulates` gets its own `dedup_status` value rather than mapping
   to `conflicts` or `new`.** This let me give it a distinct violet badge
   and a dedicated card layout in `claims.html` for the derivation block,
   without overloading the conflict-flag visual semantics. Reviewers should
   audit derivations differently from data conflicts.

4. **CLI summary derivation wrapping.** The derivations Opus produces are
   often 200-400 chars with multiple sentences. Print them word-wrapped at
   ~90 chars rather than as a single long line — keeps the terminal output
   readable without truncating the arithmetic.

5. **Kept `claude-opus-4-7` as default model.** The brief's example output
   showed `claude-opus-4-6`; I've defaulted to 4-7 (latest Opus per current
   guidance) — matches the v1 default and produced strong results in the
   smoke test. Override via `--model` if needed.

## Smoke test

Re-ran against the Menlo State of Generative AI in the Enterprise 2025
report (the canonical analyst-framework triangulation source called out in
the brief):

```
SSL_CERT_FILE=$(python3 -m certifi) python3 scripts/curated_intake.py \
  --url "https://menlovc.com/perspective/2025-the-state-of-generative-ai-in-the-enterprise/" \
  --slug menlo-genai-enterprise-2025
```

Result:
- 28 claims extracted from a 33k-char source
- Classification: 0 matches, 0 updates, 0 conflicts, **8 triangulates**,
  7 new, 13 context
- Every triangulation has a valid `derivation` field with arithmetic
  referencing named flow-model nodes (target_nodes populated, no empty
  derivations after enforcement)
- Headline triangulation matched the brief's worked example: Menlo
  "Enterprise GenAI = $37B" → `sankey.buyers.Enterprise` + `sankey.buyers.SME`
  + `market.2025.enterprise_capex` = $28.9B in our model, gap ~$8B
  attributed to scope difference (Menlo includes foundation model API spend
  routed through enterprises)
- Other strong triangulations: AI coding tools $4.0B (corroborates our
  Cursor/Copilot/Cognition/Replit/Lovable ARRs to within 4%); AI medical
  scribes implies abridge.2025.arr undercounts at $50M vs ~$100M (matches
  the [low] flag on that field); copilot $7.2B ≈ Model Subs $7.1B
  (strengthens our channel sizing within 2%)
- Output loads cleanly via `curated-index.json` in claims.html, derivation
  card renders inline below claim quote with violet styling

## Open items

- **Per-entity capex slugs in the flow model are derived heuristically.**
  `Microsoft CapEx` → `microsoft`, `Sovereign / Gov` → `sovereign_/_gov`.
  The model doesn't seem to mind, but a lookup table for canonical slugs
  would be cleaner. Low priority.
- **Truncation risk on very long sources.** Even with max_tokens=16384, a
  60k-char source with many claim candidates can still truncate. The
  salvage path catches this, but the right fix is to chunk and run multiple
  Opus calls then re-merge. Adding to follow-up list — not blocking for
  current editorial-source workload.
- **`unsourced` confidence tier is a soft signal.** It's accurate (no direct
  provenance entry for `current.X`) but slightly misleading because for
  most entities the current value tracks the most recent year's value. The
  fallback to year provenance handles 90% of cases, but a few entities show
  `unsourced` because their year financials are sparse. Re-examine if the
  model produces low-quality triangulations against unsourced positions.
- **Notion update.** The wq-083 card in the Work Tracker should reflect
  that v2 (flow model + triangulation) is now shipped. See "Acceptance
  criteria status" below for what to flip.

## Acceptance criteria status (brief §3 + §8)

- [x] CLI runs with `--url`, `--slug`, plus stdin pipe (unchanged from v1)
- [x] `build_flow_model()` outputs structural context from sankey + market
      + entities with provenance confidence
- [x] Opus prompt includes composition rules and arithmetic constraint
      for triangulation
- [x] Output file written to `data-updates/` in candidates-compatible format
      (with `triangulates` type and `triangulation` block)
- [x] CLI summary printed with comparison breakdown including triangulation
      derivations and provenance impacts roll-up
- [x] `claims.html` loads curated intake files alongside regular candidates
      and renders the derivation block inline
- [x] Materiality scoring applied to all output claims (28/28 in smoke test)
- [x] Source excerpts included per wq-041 (24/28 — short numeric values
      can fail the excerpt anchor; non-blocking)
- [x] Triangulation test passes: 8 triangulates claims with valid derivations
      from the Menlo analyst report
- [x] Constraint enforcement verified: 0 triangulates claims without
      derivation field (enforced at enrich time)
- [x] ARCHITECTURE.md updated with flow-model and triangulation description
- [x] Smoke test passes against a real editorial source
- [ ] Notion tracker: wq-083 → Stage: Done, Briefing Status: complete (this
      record flags it; update separately)
- [x] Session wrap-up summary in `data/session-logs/wq-083-curated-intake.md`
      (updated below)
