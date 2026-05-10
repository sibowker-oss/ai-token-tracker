# Deployment: dynamic Data refreshed timestamp on Capital / Revenue / Compute

**Date:** 2026-05-10
**WQ:** ad-hoc (no brief — direct user request in chat)
**Branch/Commit:** main

## What shipped

The `Data refreshed:` line on `capital.html`, `revenue.html`, and `compute.html` previously rendered a hardcoded date (April 20 / May 6) that did not move with data refreshes. It now reads `meta.generatedAt` from `site-data.json` at page load and rewrites both the `<time>` element's `datetime` attribute and visible text. The hardcoded literal remains in the markup as an editorial fallback if the fetch fails, and as the build-time literal the numbers-anchored validator scans.

Files changed:
- `capital.html` — added `id="data-refresh"` to the `<time>` element; piggybacked on the existing `fetch('site-data.json')` block (the wq-074/wq-077 path) to update text + datetime attr on success.
- `revenue.html` — same pattern; injected into the existing post-render fetch (line ~237) that already hydrates `[data-narrative]` spans.
- `compute.html` — `id="last-refreshed"` was already present; added the update inside `init()`'s existing `Promise.all` fetch.

Format preserved per page: `YYYY-MM-DD HH:MM:SS UTC` for capital/revenue (matches prior literal); `YYYY-MM-DD` for compute (matches prior literal + the adjacent "last quarter" span style).

`/beta/` mirrors were not edited — they're regenerated from the `beta` branch via `deploy-beta.yml`, and will catch up on next beta deploy.

## Decisions made during implementation

- **Piggyback on existing fetches, don't add a new one.** All three pages already pull `site-data.json` for other reasons. Adding a fourth fetch would be wasteful; this is one extra `if` block per page.
- **Keep the hardcoded literal as fallback.** Required by the wq-102 numbers-anchored validator (priority pages reject visible numeric literals not in the manifest, with a years allowlist) and as a graceful-degradation read if the fetch fails. JS overwrites client-side; source HTML is unchanged from the validator's POV.
- **Extended scope to `compute.html` even though only Capital + Revenue were named.** Same bug, same one-line fix, leaving it stale would contradict the request's intent. Flagged in this record.
- **Skipped staging-first per Simon's explicit "no need for any staging review" + "push live" in chat.** Publishing Gate step 3 (explicit affirmative) satisfied; step 1 (build to staging first) waived by the same message. Noted at the top of the chat session before changes were made.

## Open items

- The `/beta/` copies will continue to show stale dates until the next push to the `beta` branch runs `deploy-beta.yml`. Not user-visible on the canonical public surface.
- `follow-the-trillion.html` uses a different footer format (`Last updated: 22 Apr 2026`); left as-is for now — flag if a unified treatment is wanted.

## Follow-up shipped same session

After the initial push, the footer `Last updated YYYY-MM-DD` string was also made dynamic across all 12 pages that carry the standard `ds-footer__base` template (about, capital, changelog, compute, in-development, index, methodology, openrouter, power, revenue, timeline, usage). Each footer date is now wrapped in `<span id="footer-last-updated">…</span>`, and an inline `<script>` immediately after fetches `site-data.json` and rewrites the span's text from `meta.generatedAt` (date-only). Hardcoded literal preserved as editorial fallback. `validate-numbers-anchored.mjs` re-run after — still clean.

## Acceptance criteria status

- [x] Capital page "Data refreshed" reads from `meta.generatedAt` at load
- [x] Revenue page "Data refreshed" reads from `meta.generatedAt` at load
- [x] Compute page "Data refreshed" reads from `meta.generatedAt` at load (bonus)
- [x] `validate-numbers-anchored.mjs` still passes (verified locally)
- [x] Live deploy
