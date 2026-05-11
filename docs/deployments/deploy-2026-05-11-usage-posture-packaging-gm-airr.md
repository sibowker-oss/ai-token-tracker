## Deployment: Usage page — SaaS AI Transition Map axis renames, score rescale, AI ARR column, sort by rank

**Date:** 2026-05-11
**WQ:** wq-101 follow-up (editorial refinements)
**Branch/Commit:** main / single commit (to follow)
**Approval:** Simon, in-chat ("looks good. ship it.") 2026-05-11

## What shipped

Editorial pass on the SaaS AI Transition Map radar table on `usage.html`:

- **Bundling → Packaging (PKG).** Axis renamed and rubric rewritten around how the AI product is sold (separate SKU + top-of-company branding = 5; advanced features in a premium tier = 3; rolled into existing SKUs = 1). Three scores moved against the new criteria: M365 Copilot 4 → 5 (flagship product line); ServiceNow Now Assist 5 → 4 (Pro Plus is a premium tier, not its own SKU line); Notion AI 5 → 4 (add-on, not a standalone product line). All 12 bundling citations rewritten in the SKU + marketing frame.
- **AI Cost Realisation → GM impact (GM).** Axis renamed; rubric text and intro paragraph updated. Internal data key stays `cost` so historical citations and the `gmUnavailable` flag still resolve.
- **Archetype tagline removed** from each posture row (e.g. "Real workload, real cost, small share"). CSS class dropped too; underlying `archetype` field kept in data.
- **Growth column replaced with AI ARR.** New `aiArr` field on each cohort entry (`{ value, basis }`) — e.g. M365 Copilot `~$2.5–3.5B / real, net of discounting`. Old `growth`/`prevGrowth` rendering and the `postureGrowthArrow` / `postureGrowthDir` helpers removed; underlying fields kept in data.
- **Radar column shifted left.** Nameplate column narrowed 240 → 180px; the radar now sits visually closer to the product/parent text with even spacing on both sides.
- **Cohort sorted by sum of posture axes, descending.** Stable sort, so ties preserve original document order. Applied at render time via new `postureSortedCohort()` helper used by both the radar table and the notes section.

Files changed:

- `beta/usage.html` — axis labels, rubric body, intro paragraph, column header, render block, CSS, sort helper, removed archetype + growth helpers.
- `scripts/wq101_extend_posture.py` — score updates, citation rewrites, axisLabels (BNDL → PKG, COST → GM), added `aiArr` block per cohort entry, switched JSON write to ASCII-escaped to match `generate_site_data.py` convention.
- `site-data.json` + `beta/site-data.json` — regenerated.

## Decisions made during implementation

- **Kept internal data keys `bundling` and `cost` unchanged.** Renamed labels are user-facing only; the data schema, validators (`scripts/validate-vendor-posture.mjs`), and citation lookups (`cit.bundling`, `cit.cost`) keep working without migration.
- **Added `aiArr` as a separate field** rather than parsing the prose `arrReal` string. Cleaner editorial control; the existing Real row in the data block (verbose, with sources) stays untouched.
- **Sort by sum, not average.** Recommended over averaging for privates because the radar is read as an area, not a normalised score. Privates lose 1 axis worth of theoretical maximum but the order is stable and easy to defend. Footnote already in place ("higher rank ≠ better").
- **Synced `beta/site-data.json` manually with `cp`.** The standalone `wq101_extend_posture.py` only writes to root; the staging copy in `beta/` was stale on first reload and the Share-of-parent column rendered empty. See open item below.

## Open items

- **`wq101_extend_posture.py` writes to root only.** Should either write to both roots or be invoked through `generate_site_data.py` (which has the same single-root limitation in its `__main__` block). Manual `cp` after running is the current workaround. Worth tightening in a follow-up so the staging copy never drifts.
- **`shareOfParent` field was added then removed** within the session. The data schema no longer references it; no consumer ever read it. Mentioned only so future-me doesn't dig for it in git history.
- **`archetype` field still in data** but no longer rendered. Safe to leave for now — it's the editorial seed phrase per vendor and may be useful when the cohort gets rewritten or split. Remove during next cohort-wide refactor if still unused.

## Acceptance criteria status

- [x] Bundling renamed to Packaging on radar, rubric, citations, axis labels block.
- [x] Scoring rubric body matches Simon's 5/3/1 anchors (distinct product line / premium-tier feature / rolled in).
- [x] Scores rescaled against new criteria (3 of 12 moved).
- [x] COST renamed to GM impact (GM) on radar, rubric, intro paragraph, axisLabels.
- [x] Archetype tagline removed from each posture row.
- [x] Growth column replaced with AI ARR (with basis subtext).
- [x] Radar column moved left for even spacing.
- [x] Cohort sorted by radar-area rank, desc.
- [x] Validator passes (`node scripts/validate-vendor-posture.mjs` — 5 pass / 0 fail).
- [x] Approval logged.

## Notion

Notion card update — not done in this session; flag for Cowork side.
