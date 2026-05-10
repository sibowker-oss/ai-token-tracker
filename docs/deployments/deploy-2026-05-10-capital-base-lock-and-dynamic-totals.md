# Deployment: Capital Ledger — lock to Base scenario + dynamic narrative total

**Date:** 2026-05-10
**WQ:** none (ad-hoc fix triggered by user-reported desktop/mobile inconsistency)
**Branch/Commit:** wq-101-vendor-ai-posture (uncommitted)

## What shipped

`capital.html` only.

1. **Scenario locked to Base for every device.** Removed the URL `?s=` and `localStorage['ai-ledger-scenario']` reads from the `currentScenario` initialiser. The Capital Ledger now always renders the Base scenario regardless of what a visitor previously selected on Revenue Ledger / beta pages. `setScenario()` is left in place (no UI on this page calls it; harmless if invoked by future code).
2. **Inline `$745B` narrative defaults updated to `$766B`** (lines 194 + 344). These spans were already hydrated dynamically via `hydrateNarrative` against `site-data.json:capital_sankey.total`, but the inline fallback text was the legacy rounded figure — so any pre-hydration flash showed a stale number. Inline now matches engine output.
3. **Sensitivity panel base derived from live FLOWS.** `updateSensitivity()` previously hardcoded `const adjusted = 745 + …`. Replaced with `validate().t0` (engine FLOWS sum) so the sensitivity calc tracks the same cumulative total as the hero card and narrative.
4. **`sens-ratio-display` inline default** updated `$34 → $35` and detail string `$745B total → $766B total` for visual consistency on first paint.

## Decisions made during implementation

- **Why lock at the page level, not strip the localStorage key globally.** The `ai-ledger-scenario` key is shared by Revenue / Power / Methodology / Usage / beta/* pages, and the bear/bull picker is a legitimate editorial affordance there. Capital Ledger is the only page where user feedback explicitly said "should default to and stay on Base", so the fix is scoped to capital.html. No other pages touched.
- **Did not delete `setScenario()`.** No UI on capital.html invokes it, but leaving the function avoids a runtime ReferenceError if a future shared component or stale browser tab tries to call it.
- **`SCENARIOS[*].totalCapex:745` left untouched.** Field is unread anywhere in the page (only `.revenue` and `.label` are consumed). Touching it would be cosmetic-only and risks drift with `data/scenarios.json`.

## Open items

- The `data/scenarios.json` file still defines bear/bull entries for `capex_view`. They're now unreachable from capital.html (always Base). Not removing — other consumers may exist, and the file documents the intended scenario bands. Worth a follow-up if we want to retire the bear/bull capex-view scenarios entirely.
- Other pages that read the same localStorage key (`revenue.html`, `power.html`, `usage.html`, etc.) are unchanged and will continue to honor the user's bear/bull selection. Only Capital is locked.

## Acceptance criteria status

- [x] Capital Ledger renders Base scenario on every device, regardless of prior localStorage state or `?s=` URL param.
- [x] Hero "Infrastructure per $1 revenue" now consistently reads `$35` (= round(766 / 22)) on desktop and mobile.
- [x] Narrative copy ("$766B of AI infrastructure investment") matches the hero's "2023-25 AI CapEx" card.
- [x] Sensitivity panel base total tracks the engine FLOWS sum, not a hardcoded 745.
- [ ] **Publishing Gate:** NOT yet shipped to live. Awaiting Simon's approval after staging/preview check.
