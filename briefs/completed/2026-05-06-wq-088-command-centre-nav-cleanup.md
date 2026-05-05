---
id: wq-088
title: Command Centre / Admin nav cleanup
stage: Scoped
priority: M
owner: Simon (impl: Claude Code in VS Code)
created: 2026-05-06
status: ready_for_handoff
parent_context: /Users/simonbowker/Documents/Claude/Projects/The AI Ledger/ (Cowork session 2026-05-06)
---

# wq-088 · Command Centre / Admin nav cleanup

## OQ confirmation (Claude Code, 2026-05-06)

- **OQ-1.** `/admin.html` redirects to `/review.html`. Hash is preserved and forwarded to `/<tab>.html` if it matches a known tab name (e.g. `#telemetry` → `/telemetry.html`); otherwise hash is dropped on the final landing.
- **OQ-2.** Per-page password-gate IIFE stays as-is on every admin page. Auth refactor is out of scope. The IIFE remains the first thing in `<head>`, ahead of the nav loader.
- **OQ-3.** Briefs tab is repo-only. Sources are `briefs/active/` and `briefs/completed/`. Cowork drafts in `/Users/simonbowker/Documents/Claude/Projects/The AI Ledger/briefings/` are never surfaced.

## Why this brief exists

The admin/Command Centre at `https://ai-index.hepburnadvisory.com.au/admin.html` has accumulated structural debt:

1. The header brand link points to `dashboard.html`, which is itself a meta-refresh redirect to `index.html`. Two hops where there should be one.
2. The header is hand-rolled and doesn't match the design-system primary nav (`ds-header`) used on every public page.
3. `claims.html` is admin-flavoured (title: "Claim Review Queue — Admin") but is not surfaced in the secondary nav — accessible only by direct URL.
4. The secondary nav uses an iframe-per-tab pattern that hides each child page's own auth gate, makes deep-linking awkward, and means the "back to dashboard" link in each child page conflicts with the outer shell.
5. There is no in-product way to see the briefs Cowork has handed off, and no inventory of the agents/scripts that write to `site-data.json` — both exist as files in the repo (`briefs/`, `data/agents.registry.md`, `scripts/`) but aren't part of the operator surface.

This brief consolidates all of that into a single shipment.

## Decisions Simon has made (do not re-litigate without flagging)

| # | Decision | Confirmed |
|---|---|---|
| D1 | Move admin pages to **standalone pages with a shared nav partial** (no more iframes) | 2026-05-06 |
| D2 | **Auto-render** `briefs/active/` + `briefs/completed/` as a Briefs tab — what's in the repo is what shows | 2026-05-06 |
| D3 | Cowork (this session) **proposes the groupings**; Simon signs off in this brief before Claude Code builds | 2026-05-06 |
| D4 | **Single PR / one shipment** — not phased | 2026-05-06 |
| D5 | `changelog.html` is **public** and stays out of the admin nav | 2026-05-06 |
| D6 | `in-development.html` is **admin-only** — must be removed from every public page footer/nav | 2026-05-06 |

## Open decisions — RESOLVED 2026-05-06

- [x] **OQ-1.** When `/admin.html` is requested → **redirect to `/review.html`** (preserve hash forwarding for `#telemetry` etc.). No hub landing page.
- [x] **OQ-2.** Per-page password gate **stays as-is**. Auth refactor is out of scope for wq-088 and will be scoped separately as a deeper security review.
- [x] **OQ-3.** Briefs tab is **repo-only** — sources are `briefs/active/` and `briefs/completed/`. Cowork drafts in `/Users/simonbowker/Documents/Claude/Projects/The AI Ledger/briefings/` are not surfaced (they're the thinking layer, mutable, and may include pre-handoff or abandoned drafts). Cowork and repo briefs start identical at handoff but diverge after — only the repo copy is the contract.

---

## Scope

### In scope

1. Replace the admin header on every admin page with the design-system primary nav (`.ds-header` from `design-system/ledger-overlays.css`), so the look matches `index.html`.
2. Brand link goes direct to `/index.html` (not `/dashboard.html`).
3. Add `claims.html` to the secondary nav.
4. Restructure the secondary nav into four logical groups (proposed below) plus right-aligned Settings.
5. Convert each admin tab from an iframe target into a standalone page that includes the shared primary + secondary nav via a single partial.
6. Build a new `briefs.html` page that auto-renders the contents of `briefs/active/` + `briefs/completed/` as a list with status filter chips.
7. Build a new `agents.html` page that renders `data/agents.registry.md` + an inventory of `scripts/*.py` (with a one-line purpose pulled from each script's docstring).
8. Update `admin.html` per OQ-1 (default: redirect to `review.html`).
9. Drop `dashboard.html`'s use as the brand-link target everywhere it appears (audit `*.html` for `href="dashboard.html"` and replace with `/index.html` where the intent is "home").
10. **Remove `in-development.html` from every public page** (D6). It is an admin-only operator view. Audit confirms it is currently linked from 11 public pages: `index.html`, `capital.html`, `revenue.html`, `usage.html`, `power.html`, `methodology.html`, `about.html`, `timeline.html`, `openrouter.html`, `changelog.html`, and `in-development.html`'s own footer. Strip the link from each. The page itself stays alive — only reachable via the admin secondary nav after this change.

### Out of scope

- Auth refactor (OQ-2 keeps current password gate behaviour).
- Any change to public pages' nav (capital, revenue, usage, power, methodology, about) — they already use the DS header.
- Mobile-specific redesign of the secondary nav beyond what falls out naturally from the DS components.
- Cleaning up the `sources.html` vs `source-ledger.html` apparent duplication — separate brief if needed.
- Migrating away from per-page `localStorage` auth.

### Secondary-nav groupings — CONFIRMED 2026-05-06

| Group | Pages (in order) | Purpose |
|---|---|---|
| **Inbox & Review** | Inbox (`review.html`) · Claims (`claims.html`) · Add (`add.html`) · Ask (`ask.html`) | Action queues — things waiting on Simon |
| **Sources & Data** | Sources (`sources.html`) · Confidence (`confidence.html`) · Vault (`vault.html`) · Anthropic (`anthropic-spotlight.html`) | Catalogue and reference |
| **Ops & Telemetry** | Status (`status.html`) · Telemetry (`telemetry.html`) · Agents (`agents.html`) — NEW | System health + the agents/scripts that keep it running |
| **Pipeline** | Briefs (`briefs.html`) — NEW · In Dev (`in-development.html`) · Page Archive (`archive.html`) | Lifecycle of work moving through the system: scoped → in build → retired |
| _(right-aligned)_ | Settings (`settings.html`) | — |

Pending review pill on the Inbox tab (driven by `vault-inbox.json`) is preserved.

**Grouping changes from initial draft (Simon, 2026-05-06):**
- Agents moved from "Briefs & Agents" → **Ops & Telemetry** (it's a system-running thing, same family as Status/Telemetry).
- "Briefs & Agents" renamed → **Pipeline**, and now also contains In Dev + Page Archive (which were previously under Ops). Rationale: Briefs (scoped work) → In Dev (work being built) → Page Archive (retired pages) is one coherent lifecycle view.

---

## Files touched

### New
- `design-system/components/admin-nav.html` — single source of truth for the secondary nav markup (rendered into pages via JS fetch + inject; static site has no build step per `package.json`).
- `design-system/components/admin-nav.js` — small loader that fetches the partial, marks the active item by `data-tab` attribute on `<body>`, and wires the Inbox pending-pill.
- `briefs.html` — new page (Briefs tab).
- `agents.html` — new page (Agents tab).
- `scripts/build_briefs_index.py` — generates `data/briefs-index.json` from `briefs/active/` + `briefs/completed/` (filename, title from H1, status, shipped date / commit if completed). Run on demand; release-check picks up its output.
- `scripts/build_agents_index.py` — generates `data/agents-index.json` from `data/agents.registry.md` + `scripts/*.py` docstrings.

### Modified
- `admin.html` → either redirect to `review.html` per OQ-1, or hub landing.
- All existing admin tabs to add the shared nav include and remove their per-page header markup:
  - `review.html`, `sources.html`, `confidence.html`, `archive.html`, `ask.html`, `add.html`, `in-development.html`, `status.html`, `telemetry.html`, `anthropic-spotlight.html`, `page-archive.html`, `settings.html`, `claims.html`, `vault.html`.
- Audit + replace `href="dashboard.html"` → `href="/index.html"` (or `/` ) anywhere the intent is "home". Keep the `dashboard.html` redirect file in place so old bookmarks still work.
- **Public-page footers/nav (D6)** — strip the "In development" link from: `index.html`, `capital.html`, `revenue.html`, `usage.html`, `power.html`, `methodology.html`, `about.html`, `timeline.html`, `openrouter.html`, `changelog.html`, and the footer of `in-development.html` itself if it self-references.
- `data/page-registry.json` — add `briefs.html` and `agents.html`.

### Read-only references
- `design-system/colors_and_type.css`, `design-system/ledger-overlays.css` — primary nav styles to mirror.
- `data/agents.registry.md` — source for Agents page.
- `briefs/README.md` — existing handoff conventions (inform Briefs page copy).

---

## Implementation outline

1. **Shared partial.** Build `design-system/components/admin-nav.html` containing:
   - The `<header class="ds-header">…</header>` block, identical to `index.html` so visual parity is automatic.
   - Below it, a `<nav class="admin-secondary-nav">` block grouping the items per the table above. Use `data-group` and `data-tab` attributes for active-state targeting.
2. **Loader.** `admin-nav.js` does: fetch the partial, inject into a `<div id="admin-nav-mount">` placeholder, find the element matching `body[data-active-tab]`, set `is-active`, and wire the Inbox pending-pill (port the existing `loadReviewBadge` from `admin.html`).
3. **Per-page edit.** On each admin page:
   - Remove the existing inline header markup.
   - Replace with `<div id="admin-nav-mount"></div>` and `<script src="/design-system/components/admin-nav.js"></script>`.
   - Set `<body data-active-tab="…">` so the loader can mark the right item.
4. **Briefs page.** `briefs.html` reads `data/briefs-index.json` and renders a table with filter chips (All · Active · Completed). Each row links to the rendered .md (via a tiny client-side markdown renderer or a `<details>` with `<pre>`) — pick the lighter option that doesn't add a build step.
5. **Agents page.** Similar to Briefs but driven by `data/agents-index.json`; show the registry table plus a "Scripts inventory" section grouped by purpose (claims · enrich · derive · monitor · etc., inferred from filename prefix).
6. **Brand-link sweep.** ripgrep for `dashboard.html` across `*.html`; replace home-intent links with `/index.html`. Keep the `dashboard.html` file (it stays as a redirect for old bookmarks) but no internal page should link to it.
7. **admin.html.** Per OQ-1, replace its body with a meta-refresh to `review.html` (mirroring the dashboard.html pattern for graceful fallback) and a single anchor link.

---

## Acceptance criteria

- [ ] Visiting any admin page shows the same `ds-header` masthead as `index.html` (logo icon, gradient brand, sub-label, primary nav links). Brand click goes to `/index.html` in one hop — verified by network tab showing no 30x.
- [ ] Below the masthead, every admin page shows the same secondary-nav block, grouped per the table above, with the current page's tab highlighted via `is-active`.
- [ ] `claims.html` is reachable from the secondary nav under "Inbox & Review".
- [ ] No admin page contains an `<iframe>` element after the refactor (`grep -l "<iframe" *.html` against the admin set returns empty).
- [ ] `briefs.html` lists every file in `briefs/active/` and `briefs/completed/`, with status chip and ship-date if completed. Adding a new brief and re-running `python3 scripts/build_briefs_index.py` updates the page on next load.
- [ ] `agents.html` shows every row of `data/agents.registry.md` plus a Scripts section listing every `scripts/*.py`.
- [ ] No broken intra-page links: `npm run build-lint` passes, and a manual click-through of the secondary nav from `review.html` reaches every other admin page without 404.
- [ ] On mobile (≤768px) the primary nav scrolls horizontally per `ds-header__nav` mobile rules; the secondary nav also scrolls horizontally (no wrapping that hides content).
- [ ] `grep -rln "in-development\.html" *.html` returns only admin-side pages and `in-development.html` itself. No public page (capital, revenue, usage, power, methodology, about, timeline, openrouter, index, changelog) links to it. (D6)
- [ ] The Inbox pending-pill still appears with the count from `vault-inbox.json`.

---

## Test plan

1. **Visual.** Run `npm run release-check:visual` after taking new baselines for the admin pages (`playwright test ... --update-snapshots`). Add at least: review, claims, briefs, agents, status, settings.
2. **Functional.** Add a Playwright spec under `tests/release-check/` that:
   - Loads `/review.html`, asserts `ds-header` is present and brand href is `/index.html`.
   - Asserts the secondary-nav has 14 expected `data-tab` values across the four groups.
   - Clicks every secondary-nav link and asserts no 404 (`response.status() === 200`).
3. **Build lint.** `npm run build-lint` must pass — no schema diffs, all provenance fields intact.
4. **Manual mobile.** iPhone + Android viewport screenshots in the visual run.

---

## Edge cases

- A user lands on `/admin.html#telemetry` from an old bookmark. Per OQ-1(a) the redirect to `/review.html` will drop the hash; mitigate by having the redirect script preserve the hash and forward to `/<tab>.html` if the hash matches a known tab name. Document in code.
- `briefs.html` runs against an empty `data/briefs-index.json` — render an empty-state card pointing to `briefs/README.md`.
- `agents.html` runs before `data/agents-index.json` exists — same empty-state pattern.
- A brief filename without a leading date (legacy) — `build_briefs_index.py` should fall back to the file's git-log first-commit date.
- Per-page `localStorage` auth: ensure the auth script runs *before* the nav loader (otherwise an unauthenticated user briefly sees the nav before the redirect to dashboard.html). Move the auth IIFE to the very top of `<head>` on every admin page.

---

## Definition of done

- All acceptance criteria checked, locally and in CI.
- `briefs/active/2026-05-06-wq-088-command-centre-nav-cleanup.md` (this file, copied into the repo) updated with a footer "Shipped: <date>, commit <sha>" and moved to `briefs/completed/`.
- `data/agents.registry.md` and `briefs/README.md` reviewed and any contradictions with the new pages reconciled.
- Notion card for wq-088 moved to Done.

---

## Validation rule reminder

Per [feedback memory](../../memory/feedback_validate_rendered_output.md): the §11 release gate must validate the **rendered output**, not the engine's own diff. Specifically, the new Playwright spec must visit every admin URL and assert the DOM, not just `grep` the source files.

---

## Handoff prompt for VS Code / Claude Code

> Implement wq-088 per `briefs/active/2026-05-06-wq-088-command-centre-nav-cleanup.md`.
>
> Start by answering OQ-1, OQ-2, OQ-3 inline at the top of the brief and committing that answer. Then work the §"Implementation outline" in order. Single PR.
>
> Constraints:
> - No new build step. Static site only — partials inject via fetch in the browser.
> - Mirror `index.html`'s `ds-header` exactly; do not invent new header CSS.
> - Preserve the per-page password gate (the IIFE at top of `<head>`) on every admin page.
> - The Inbox pending-pill must still work, driven by `vault-inbox.json`.
> - `npm run build-lint` and `npm run release-check` must pass.
>
> When finished, append a Shipped: footer to the brief and move it from `briefs/active/` to `briefs/completed/`. Update Notion wq-088 to Done.

---

## Change log

- 2026-05-06 — drafted in Cowork; D1–D5 confirmed; ready for repo handoff.
- 2026-05-06 — D6 added (in-development.html → admin-only; strip from 11 public-page footers).
- 2026-05-06 — Grouping revision: Agents moved to Ops & Telemetry; "Briefs & Agents" renamed "Pipeline" and absorbed In Dev + Page Archive. OQ-1/2/3 resolved (redirect / keep gate / repo-only). Status flipped to ready_for_handoff.

---

Shipped: 2026-05-06, commit e8e1b9b
