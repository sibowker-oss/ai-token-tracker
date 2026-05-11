# Deployment: Usage page — restore SaaS AI Transition Map radars + strip jargon from cohort notes

**Date:** 2026-05-11
**WQ:** wq-101 follow-up (regression fix)
**Branch/Commit:** main / single commit

## What shipped

Restored the 12 vendor radar rows on `usage.html`'s SaaS AI Transition Map
section, and made the regression structurally impossible to recur.

- `scripts/wq101_extend_posture.py` — split into `apply(site)` (in-memory
  mutation) + `main()` (standalone file-IO wrapper). Standalone invocation
  still works for the editorial quarterly review playbook.
- `scripts/generate_site_data.py` — now calls `wq101_extend_posture.apply(site)`
  immediately after `wq096_emit.apply_all(site)`. Posture scores are
  reapplied on every regenerate; the cohort can no longer be silently
  wiped by an unrelated builder run.
- `data/evidence/enterprise_reality/{google_workspace_ai,microsoft_dynamics_copilot,oracle_fusion_ai}.json`
  (+ beta mirrors) — rewrote `arrSource` and `narrative.flags` strings to
  drop work-tracker IDs, internal decision labels, and a file-path
  reference. Same field rewrites for `watchSignals` in
  `scripts/wq101_extend_posture.py`.
- `site-data.json` and `beta/site-data.json` regenerated from the wired
  pipeline; 12/12 cohort entries carry `postureScores`.

## Decisions made during implementation

- **Wire posture extension into `generate_site_data.py` rather than into
  `wq096_emit.apply_all`.** The posture data sits one logical layer above
  the wq-096 revenue-model emit (it depends on enterpriseReality being
  fully rebuilt first, but conceptually it belongs with editorial cohort
  decoration, not with revenue-model emit). Keeping it as a peer call in
  the top-level builder makes the dependency explicit.
- **Kept `_prototype: true` and `_lastVerified: 2026-Q1` on each
  postureScores block.** These are internal flags consumed by the
  validator and admin posture-review surface, not user-facing copy.
- **Did not strip `reviewPlaybook` / `sourceBrief` from the
  `vendorPostureMethodology` block.** They're not rendered on the public
  page (only `lastEditorialReview` is). Following the precedent set by
  `3b9674d` (public-pages jargon cleanup focused on visible copy +
  view-source HTML, not on internal metadata in the data layer).
- **Rewrote `narrative.flags` even though it's currently rendered only
  as a fallback for empty `watchSignals`.** `flags` is in the served
  JSON and would resurface immediately if anyone ever changed the
  render priority. Defence in depth.
- **Did not run a publish-time `scripts/release-check.mjs` sweep.**
  Step 11f (vendor-posture validator) is the gate for this specific
  cohort; ran it directly. The full release-check covers many other
  pages that this commit doesn't touch.

## Open items

- The cleaner long-term fix is to move postureScores into the evidence
  JSON files themselves (`data/evidence/enterprise_reality/*.json`),
  rather than maintaining them in a separate Python dict in
  `scripts/wq101_extend_posture.py`. That would eliminate the
  apply-after-emit dependency entirely. Left as someday-cleanup.
- Same jargon-scrub principle should be applied to the **other 8**
  non-cohort `enterpriseReality` entries (atlassian_intelligence,
  box_ai, github_advanced_security_ai, hubspot_breeze, sap_joule,
  workday_ai, zendesk_ai, zoom_companion). They're not rendered on
  usage.html today, but the same fields exist and may be surfaced in
  future pages. Not in scope for this fix.

## Acceptance criteria status

- [x] SaaS AI Transition Map renders all 12 vendor rows with radar charts on `beta/usage.html`.
- [x] `scripts/validate-vendor-posture.mjs` reports 5 pass / 0 fail.
- [x] No `wq-NNN`, `Decision DNN`, or `.json` / repo-path references in user-visible cohort notes (watchSignals, flags, arrSource, citations).
- [x] Re-running `python3 scripts/generate_site_data.py` preserves postureScores without a separate manual step.
- [x] Approval obtained in-chat before push to live (2026-05-11).
