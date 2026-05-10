# Deployment: Public-pages site-jargon cleanup

**Date:** 2026-05-11
**WQ:** ad-hoc (in-session directive — not from a brief)
**Branch/Commit:** `main` working tree (uncommitted at time of write)

## What shipped

Visible copy and view-source comments on every public-facing page rewritten so that internal work-tracker IDs, file paths, internal documentation references, and process language no longer appear. Functional code (e.g. `fetch('site-data.json')` calls, variable names like `wq090Routing`) is left intact — out of scope and would have introduced regression risk.

**Files modified (each in both `/` and `/beta/`):**

- `methodology.html` — heaviest rewrite. Section 3 (Compute three-segment model + segment sizing + calendar basis + cohort-vs-ecosystem), Section 4 (Revenue archetype taxonomy), Cross-Ledger Reconciliation block (a/b/c bridges), Copilot three-band block, ARR-vs-collected revenue block. Removed: every WQ ID in headings and body (`wq-087`/`089`/`090`/`091`/`092`/`094`/`032`/`028`/`035`); decision codes (`D6`/`D3`/`P1B`/`P1.6`/`F2`); file paths (`data/compute_disclosures.json`, `data/methodology_constants.json`, `data/sankey_cost_structure.json`, `entities.json:microsoft-copilot.products[m365-copilot]`, etc.); script names (`scripts/derive_compute_revenue.py`, `scripts/derive_sankey.py`); brief paths (`docs/briefs/wq-092-…md`); references to `CLAUDE.md` and `SKILL.md hard rule #6`. Process language ("the wq-087 page", "post-wq-091 segment sizing", "locked wq-092 2026-05-06", "at ship") rewritten as straightforward business-logic prose ("an earlier version of the page", "the corrected page", "before publication").
- `changelog.html` — three trailing WQ tags removed from entries; `site-data.json gains an entityDirectory section…` rewritten as "An entity directory now lists all 103 tracked entities…".
- `usage.html` — visible copy: `Per SKILL.md hard rule #6` → "ARR and collected revenue measure different things and are never interchangeable". CSS comment + JS section header WQ refs removed.
- `capital.html` — visible copy: `Source: <code>data/depreciation.json</code>` → "Sourced from each issuer's quarterly PP&E and depreciation disclosures". Comment-level: WQ refs stripped from JS comments around scenarios, FLOWS hydration, lag chart projection, capital-sankey fetch handler, depreciation watch and ratio hydration.
- `compute.html` — visible copy: `Source: <code>data/compute_disclosures.json:forward_commitments</code>` → "Sourced from issuer disclosures of remaining performance obligations and announced multi-year compute commitments". Comment-level: CSS / HTML / JS section headers cleaned; the leading file-path comment block rewritten as plain prose.
- `revenue.html` — visible JS-injected DOM string `wq-090 editorial — see methodology` → `Editorial routing — see methodology`. Comment-level: WQ refs stripped from scenario data, color aliases, narrative hydration, hero customer-revenue calc, secondary line, buyer-provider routing panel, channel rendering and node-color rendering.
- `index.html` — CSS / HTML / JS comment WQ refs stripped (5 hits; Layer Stack accents, hero section banner, ledger entry cards, Stay Informed, mobile rules, hydration and hook-ratio comments).
- `timeline.html` — HTML + JS comment WQ refs stripped (FY revenue surface).

`openrouter.html`, `about.html`, `power.html` — no jargon hits found, no edits required.

## Decisions made during implementation

- **Scope of "site jargon"** confirmed with Simon mid-pass: all visible body copy, plus CSS / HTML / JS comments (view-source-only). NOT JS variable names like `wq090Routing` or `buyerChannelMatrix` — renaming those is functional refactoring with regression risk and not requested.
- **`fetch('site-data.json')` calls left intact.** Removing the literal would break the page; "site-data.json" as a URL is plumbing, not editorial language.
- **Methodology page numbers and structure preserved.** Every numerical claim, every percentage, every ASC 606 reference, every provider sub-segment kept verbatim — only the wrapping process language was rewritten.
- **Mirror strategy.** Where root + beta were identical (`index`, `methodology`, `changelog`, `usage`, `timeline`, `openrouter`), edited beta and `cp` to root. Where they diverged (`capital`, `revenue`, `compute` — root has the live `meta.generatedAt` timestamp wiring beta lacks), edited each side independently with the same Edit operations to preserve the divergence.
- **`review.html` deferred.** It is linked only from internal admin pages (`admin`, `add`, `vault`, `sources`), not from the public nav, so the WQ ref in its JS-injected DOM string stays for now. If the public surface ever links to it, this needs a follow-up.

## Open items

- **No deploy.** Per Simon's instruction, the work is held locally. He will review and approve before any production push. CLAUDE.md Publishing Gate applies.
- **JS variable / function name cleanup deferred.** Names like `wq090Routing`, `buyerChannelMatrix`, `pre-wq-062 proportional logic` (in inline-string warnings) still embed work-tracker semantics. If editorial cleanup is wanted there, that is a separate refactor with regression-test scope.
- **The other ~25 internal/admin pages** (`admin`, `vault`, `review`, `telemetry`, `status`, `claims`, `source-ledger`, `dashboard`, `settings`, `add`, `agents`, `anthropic-spotlight`, `archive`, `ask`, `benchmarks`, `briefs`, `confidence`, `follow-the-trillion`, `in-development`, `ipo-watch`, `page-archive`, `posture-review`, `predictions`, `sources`, `subsidy-clock`) were not touched. They are not linked from the public nav and are functionally internal tooling, but if any are ever promoted to the public surface, the same rule applies.
- Memory written: [feedback_no-site-jargon-public-pages.md](`/Users/simonbowker/.claude/projects/-Users-simonbowker-Developer-apac-ai-intel/memory/feedback_no-site-jargon-public-pages.md`) so future work doesn't reintroduce these patterns.

## Acceptance criteria status

- [x] Methodology page contains zero WQ IDs, file paths, script names, brief refs, or internal-doc refs in visible copy
- [x] Same rule applied to every public-facing page in the nav (Capital, Revenue, Compute, Usage, Power, Methodology, About) plus Timeline, Live pricing, Changelog
- [x] Comment-level cleanup completed (per Simon's mid-session direction)
- [x] Functional code untouched — no fetch calls broken, no variable renames
- [x] Visible-content audit returns zero hits across all 11 priority pages, both root and beta
- [ ] Simon-approved publish to live (held — Publishing Gate)
