# Deployment: Capital Sankey — round stage totals

**Date:** 2026-05-10
**WQ:** none (ad-hoc fix triggered by user-reported $765.9999999B display artefact)
**Branch/Commit:** wq-101-vendor-ai-posture → main (`43a23b8`)
**Staging approval:** N/A — user explicitly directed "push straight to live site" after the fix was described.
**Live promote approval:** 2026-05-10 ("once fixed push straight to live site")

## What shipped

`capital.html` only — single-line change at line 682.

The Sankey "Who Spent It / What It Bought / Current State" stage totals were rendered with raw string concatenation:

```js
.text('$'+total+'B');   // → "$765.9999999B" when total accumulates float noise
```

Replaced with the page-wide currency formatter:

```js
.text(formatCurrency(total));   // → "$766B"
```

`formatCurrency` already governs every other monetary value on the page (hero cards, narrative copy, sensitivity panel, node labels at line 708). This one stage-total label was the lone holdout, exposing float-accumulation noise from `nodes.reduce((s,n) => s + n.value, 0)`.

## Decisions made during implementation

- **Publishing Gate exception (logged here, not in `/decisions/open/`).** User explicitly directed direct-to-live push after the fix description. Single-line trivial swap to a unit-tested helper, on a behaviour the user had just been viewing. Staging would have rendered identical output. Preserving the gate's intent (no surprise live changes) — the change was described, approved, and shipped with explicit chat affirmative. The `/decisions/open/` exception path in CLAUDE.md is scoped to "staging-first impossible" infra cases, which this is not.
- Pushed beta branch to the same commit (`--force-with-lease`) so `/beta/capital.html` doesn't drift from live.

## Open items

None.

## Acceptance criteria status

- [x] Sankey stage totals on capital.html render via `formatCurrency` and round to whole billions (no decimal noise).
- [x] Live at `ai-index.hepburnadvisory.com.au/capital.html`.
- [x] `/beta/` mirror in sync.
