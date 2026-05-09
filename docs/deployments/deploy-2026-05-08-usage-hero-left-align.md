# Deployment: Usage Ledger hero left-aligned

**Date:** 2026-05-08
**WQ:** ad-hoc UI tweak (no brief)
**Branch/Commit:** main / 0c7f2c9

## What shipped

- `usage.html` — changed `.hero-strip` from `text-align:center` to `text-align:left` so the `Usage Ledger` h1, the `Token volume…` sub, and the `Data refreshed…` line all left-align.
- Reconciliation notes inside the hero retain their inline `text-align:center` (untouched).

## Decisions made during implementation

- Scope kept to the live page only; `beta/usage.html` not modified (user request was specific to the live ledger).
- Approach: single CSS rule change rather than per-element overrides — minimal diff, no inline styles added.

## Open items

- If the centered reconciliation notes look mismatched against the now-left-aligned heading, follow up to left-align them too.
- `beta/usage.html` will drift from live until similarly updated.

## Acceptance criteria status

- [x] `Usage Ledger` heading left-aligned
- [x] `Token volume…` sub left-aligned
- [x] `Data refreshed…` line left-aligned

## Publishing gate

- Staging preview: localhost http-server on :8765, shared 2026-05-08
- Approval: explicit "push to live please" from Simon, 2026-05-08
- Production publish: `git push origin main` → GitHub Pages auto-deploy to ai-index.hepburnadvisory.com.au
