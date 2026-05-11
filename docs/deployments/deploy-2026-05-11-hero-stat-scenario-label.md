# Deployment: Hero stat scenario label drift fix

**Date:** 2026-05-11
**WQ:** (none — ad-hoc bug fix raised by Simon in chat)
**Branch/Commit:** main / dff4f1a
**Approval:** Simon, in-chat "push live, no beta" (2026-05-11)

## What shipped

Two files changed on live surface (root *.html):

- `revenue.html` — locked `currentScenario = 'base'` and short-circuited `getScenario()` to always return `'base'` (was reading URL `?s=` then localStorage `ai-ledger-scenario`). Stripped `scenarioData.label+scenarioTier+' '+` from the three hero-stat detail lines (Customer Revenue, VC Operating Subsidy, Generated Cashflow). Rewrote the 2026E/2027E page subtitle to drop the "Base case:" framing.
- `capital.html` — stripped `${sc.label} &middot; ` from the "2023-25 AI CapEx" hero-stat detail.

## Root cause

The Bear/Base/Bull toggle UI was removed in 75f4cc6 (2026-05-08) but the supporting JS that read scenario state from localStorage was deliberately left in place. Browsers with stale localStorage entries (`ai-ledger-scenario = 'bull'` etc.) kept rendering the cached label in hero-stat detail lines and the projected-year subtitle. Underlying numbers were unaffected because the multiplier for non-2025 years collapsed to 1.0 with no UI to change it — but the **label** still varied per-device. Simon saw "Base" on desktop, "Bull" on mobile.

## Decisions made during implementation

- **Lock `getScenario()` to `'base'` rather than ripping the scenario JS out.** Capital ledger already uses this pattern (line 449 with explanatory comment). Less surgery; matches existing convention; the dead `setScenario` / `SCENARIOS` object becomes harmless. Full removal is broader and can be its own work item if Simon wants the cleanup.
- **Kept the `scenarioData.growth` reference in the 2026E/2027E subtitle.** The numeric growth band ("80-100% annually") is still useful editorial context even without a case label; only the "Base case:" prefix was removed.
- **Reverted the parallel edits I made to `/beta/revenue.html` and `/beta/capital.html`.** Simon said "push live, no beta" — interpreted as: do not commit the beta-folder copies. Root is the live surface per c753442 ("wq-102 follow-up: extend binding to root *.html (live surface)").

## Open items

- The `/beta/` copies of `revenue.html` and `capital.html` still carry the bug. If `/beta/` is reachable publicly they'll continue showing the drift. Worth confirming whether `/beta/` is still served — and if so, either deleting the folder or applying the same fix.
- Dead JS on `revenue.html` (`setScenario`, `getScenario`, scenarios fetch, `SCENARIOS` object) remains as no-op code. Separate cleanup if desired.
- Same scenario JS lingers on `power.html` and `usage.html` per the 75f4cc6 commit message — neither renders a case label in hero stats so no user-visible bug, but the dead code is consistent across the ledger set.

## Acceptance criteria status

- [x] Hero stat boxes on `revenue.html` no longer show "Base" / "Bull" / "Bear" next to values
- [x] Hero stat boxes on `capital.html` no longer show "Base case" in the 2023-25 AI CapEx detail
- [x] Displayed numbers identical across desktop and mobile regardless of cached localStorage state
- [x] Pushed to `main` per Simon's explicit approval ("push live, no beta")
