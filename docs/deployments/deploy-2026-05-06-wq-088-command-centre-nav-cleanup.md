# Deployment: Command Centre / Admin nav cleanup (wq-088)

**Date:** 2026-05-06
**WQ:** wq-088
**Branch/Commit:** main / TBD (filled in after first commit)

## What shipped

- **Shared admin-nav partial** at `design-system/components/admin-nav.html` —
  contains the full `ds-header` (mirrors `index.html`) plus a four-group
  secondary nav (Inbox & Review · Sources & Data · Ops & Telemetry ·
  Pipeline) with right-aligned Settings.
- **Loader** at `design-system/components/admin-nav.js` — fetches the partial
  into `<div id="admin-nav-mount">`, marks the active item by
  `body[data-active-tab]`, ports the Inbox pending-pill from the old
  `loadReviewBadge` so the count from `vault-inbox.json` keeps showing up.
  Inline-injects the secondary-nav CSS so admin pages don't need an extra
  stylesheet.
- **Per-page conversion** of every admin page to use the shared nav (auth
  IIFE preserved at the very top of `<head>`, design-system stylesheets
  added so `ds-header` styles resolve, ad-hoc inline nav blocks removed):
  - `review.html`, `claims.html`, `add.html`, `ask.html`,
  - `sources.html`, `confidence.html`, `vault.html`, `anthropic-spotlight.html`,
  - `status.html`, `telemetry.html`,
  - `in-development.html`, `archive.html`,
  - `settings.html` (auth IIFE added — was missing).
- **`add.html`** and **`settings.html`** — added missing auth IIFE so every
  admin page now has the password gate per the brief constraint.
- **`admin.html`** is now a redirect hub. JS preserves the hash and forwards
  `#telemetry` → `/telemetry.html` etc. (HASH_MAP in the file). Falls through
  to `/review.html` per OQ-1. Includes `<meta http-equiv="refresh">` as a
  no-JS fallback.
- **New `briefs.html`** (Pipeline group) — renders `data/briefs-index.json`
  with status filter chips, expandable rows that lazy-fetch the brief body.
- **New `agents.html`** (Ops & Telemetry group) — renders
  `data/agents.registry.md` (parsed) + every `scripts/*.py` grouped by
  filename prefix, with one-line purpose pulled from each docstring.
- **New generators**:
  - `scripts/build_briefs_index.py` → `data/briefs-index.json` (18 active
    briefs at ship time, 0 completed pending the move of this brief).
  - `scripts/build_agents_index.py` → `data/agents-index.json` (5
    registered agents, 61 Python scripts).
  Both support `--check` for a CI-style "would regen change anything" test.
- **D6 — public-page footer strip**: removed the `In development` link from
  `index.html`, `capital.html`, `revenue.html`, `usage.html`, `power.html`,
  `methodology.html`, `about.html`, `timeline.html`, `openrouter.html`,
  `changelog.html`, `compute.html`. `in-development.html` is no longer
  reachable from public pages — only via the admin Pipeline group.
- **Brand-link sweep**: `href="dashboard.html"` (home-intent) replaced with
  `/index.html` on `ipo-watch.html`, `benchmarks.html`, `subsidy-clock.html`,
  `predictions.html`, `source-ledger.html`. Auth-IIFE failure redirects to
  `dashboard.html` left untouched per OQ-2 (auth refactor out of scope) —
  `dashboard.html` itself stays alive as a meta-refresh redirect for old
  bookmarks.
- **`data/page-registry.json` updates**:
  - Added `briefs.html` and `agents.html` (both `status: admin`).
  - Flipped `in-development.html` from `live` → `admin` (D6).
  - Updated `admin.html` purpose copy (now describes the redirect role).
  - Bumped `last_updated` to `2026-05-06-wq-088`.
- **Playwright spec** at `tests/release-check/admin-nav.spec.ts` (31 tests on
  desktop-chrome): per-page DOM assertion of the rendered `ds-header`,
  primary-nav links, secondary-nav `data-tab` set, active-state marking,
  iframe-absence (with documented exception for content-iframe pages);
  `admin.html` redirect (with and without `#telemetry`); inbox pending-pill
  reflects `vault-inbox.json`; D6 audit visiting every public page and
  asserting no `/in-development.html` anchor remains.

## Decisions made during implementation

1. **Iframe AC interpretation.** AC9 reads "No admin page contains an
   `<iframe>` element after the refactor (`grep -l "<iframe" *.html`
   against the admin set returns empty)." Strict reading would fail
   `in-development.html` (preview thumbnails of `parked/*` prototypes) and
   `archive.html` (preview thumbnails of archived pages). Both are content
   features of the page itself, not the iframe-per-tab nav pattern wq-088
   targets. The spec asserts iframe-absence on every admin page **except**
   those two and adds an explicit assertion that `admin.html` (the actual
   target of the AC — the old iframe shell) contains no `<iframe>` in its
   HTML source.
2. **Auth IIFE redirect target.** Per OQ-2 the auth gate stays as-is, so the
   IIFE's `dashboard.html` failure redirect was left untouched — even
   though the admin nav brand now points to `/index.html`. The existing
   `dashboard.html` stub is a meta-refresh to `index.html`, so the worst
   case for an unauth user is one extra hop that was already there.
3. **Secondary-nav CSS lives in the loader.** Rather than adding a separate
   CSS file or polluting `ledger-overlays.css`, `admin-nav.js` injects a
   `<style id="admin-nav-styles">` block on first load. Keeps the partial
   self-contained — drop in a `<div id="admin-nav-mount">` and load the
   script, no extra stylesheet wiring per page.
4. **`add.html` / `settings.html` auth IIFE added.** Both were missing the
   gate (an inconsistency, not a deliberate exemption). Added the same
   pattern used elsewhere — keeps "every admin page has the gate at the
   top of `<head>`" coherent.
5. **`in-development.html` registry status.** Brief D6 says it stays alive
   but admin-only. Set `status: admin` (matches folder rule — admin pages
   live at `<root>` per `validate_page_registry.py` FOLDER_FOR_STATUS).
6. **Brief body rendering.** `briefs.html` renders the markdown source as a
   `<pre>` inside a `<details>` block instead of pulling in a markdown
   library. Brief constraint "no new build step" + the body is read by an
   operator, not a public reader — preserving wrapping/spacing in monospace
   is fine for the use case.

## Open items

- **Visual baselines for admin pages** are not added in this PR. The brief
  test plan (§Test plan #1) calls for new baselines for review / claims /
  briefs / agents / status / settings, but the existing `visual.spec.ts` is
  driven by `site-data.json.pages` (public pages only). Adding admin
  baselines needs either a separate spec or a config switch. Defer to a
  follow-up: low risk because the structural Playwright spec already
  asserts the DOM contract.
- **Pre-existing release-check failures** unchanged by this PR:
  - `chips.html` 404 (file doesn't exist)
  - Public-page visual baselines missing (need
    `playwright test --update-snapshots`)
  - "raw keys leaked" picks up nav link names (`revenue`, `capital`, …)
  - `data-section="hero"` missing from public pages (structure spec)
  - `validate_page_registry.py` flags `compute.html` (untracked, wq-087
    pending) and two `newsletters/brief-*.html` files not in the registry
    (pre-wq-088 housekeeping).
- **`dashboard.html` stub stays** per the brief — old bookmarks still work.
  No internal page links to it any more (only the auth-IIFE failure
  redirects do, deliberately preserved per OQ-2).

## Acceptance criteria status

- [x] Visiting any admin page shows the same `ds-header` masthead as
  `index.html` (logo, gradient brand, sub-label, primary nav links). Brand
  click goes to `/index.html` in one hop — verified by Playwright assertion
  on `brand getAttribute('href')`.
- [x] Below the masthead, every admin page shows the same secondary-nav
  block, grouped per the brief table, with the current page's tab marked
  `is-active`. Asserted by Playwright on every admin URL.
- [x] `claims.html` is reachable from the secondary nav under
  "Inbox & Review" (`data-tab="claims"` link present in the partial).
- [x] No iframe-per-tab pattern after the refactor. The `admin.html` source
  now contains no `<iframe>`. `in-development.html` and `archive.html`
  retain content-preview iframes — see Decision 1 above.
- [x] `briefs.html` lists every file in `briefs/active/` and
  `briefs/completed/` (verified manually — 18 active rendered at ship
  time). Re-running `python3 scripts/build_briefs_index.py` updates
  `data/briefs-index.json`; the page picks up the new entries on next load.
- [x] `agents.html` shows every row of `data/agents.registry.md` (5 agents)
  plus a Scripts section grouping every `scripts/*.py` (61 scripts in 16
  groups). Verified manually.
- [x] `npm run build-lint` passes (0 fail, 1 advisory — same as baseline).
- [x] `grep -rln "in-development\.html" *.html` returns admin-only pages —
  only `admin.html` (in the redirect HASH_MAP) references it now.
- [x] Inbox pending-pill appears with the count from `vault-inbox.json` —
  asserted by Playwright comparing the rendered text against the JSON.
- [~] Mobile (≤768px) primary-nav scrolls horizontally per
  `ds-header__nav` mobile rules — primary nav inherits unchanged DS
  behaviour. Secondary nav sets `overflow-x:auto` + hides the group labels
  at the breakpoint. Not separately asserted in Playwright; relies on the
  existing DS rules from `ledger-overlays.css`.
- [~] `npm run release-check` produces a report. Pre-existing failures (see
  Open items) are unchanged by this PR. New `tests/release-check/admin-nav.spec.ts`
  passes 31/31 on desktop-chrome.
