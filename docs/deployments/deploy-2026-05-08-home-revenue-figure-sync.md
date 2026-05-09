# Deployment: home page revenue figure — sync to gross customer revenue

**Date:** 2026-05-08
**WQ:** none (small fix flagged ad-hoc by Simon)
**Branch/Commit:** main / 9dc4e53

## What shipped

`index.html` only. Two surfaces on the home page that displayed conflicting revenue numbers ($17.4B on the top "AI Industry Stack" bar, $17B on the Revenue Ledger card) are now both wired to `site-data.json:sankey.totalCustomerRevenue_gross` (currently 19.279) and rendered with a 1-decimal formatter, so both read **$19.3B** and stay in sync on data refresh.

Specific edits:

- `ais-revenue-figure` (top bar) — was hardcoded `$17.4B`, now hydrated from `appsGross` via new `fmt$1` formatter (1-decimal precision; `formatCurrency` rounds ≥10 to whole-billions and would lose the .3).
- `--bar-w` on the revenue bar — 17% → 19% to track the new value visually.
- `card-revenue` (Revenue Ledger card further down) — was hydrated from `d.sankey.totalCustomerRevenue` (net, 17.36) rendering "$17B", now reads the same gross field as the bar.
- Hardcoded fallback literal in markup updated `$17B → $19.3B` so no flash of stale value before fetch resolves.
- `FALLBACK` const gained `appsGross: 19.28`.

## Decisions made during implementation

- **Rounding path: $19.3B not $19.4B.** Simon initially asked for $19.4B based on adding rounded buyer-row labels on the sankey (7.1 + 5.1 + 7.2). The precise sum of `Consumer + AI Natives + Enterprises & Govs` is 19.279 → $19.3B with 1-decimal precision. The 19.4 was an additive-rounding artifact, not a rounded-down view of an underlying 19.4. Switched to $19.3B after walking through the math.
- **Use gross, not net.** The bar previously showed net (17.36 → "$17.4B") and the ledger hero shows gross. Aligned the home bar + card on gross because that's the ledger-cohort total a casual reader gets when they sum the Revenue sankey buyer columns; net is the post-pass-through figure providers receive. Both are real, gross is more intuitive at a glance.
- **Card-revenue formatter switched from `fmt$` (formatCurrency) to `fmt$1`.** Introduces a small inconsistency vs. `card-capex` ($745B integer) and `card-compute` ($43B integer), which still use formatCurrency. Accepted because the $19.3B precision was the explicit ask; the other cards have less need for 1-decimal at their magnitudes.
- **Hook ratio left on net.** The `Compute / Apps` ratio at the top of the page still divides by `totalCustomerRevenue` (net), so $2.50 stays. Switching to gross would change it to ~$2.23. The hook copy ("customer-paid AI Apps Revenue") arguably suggests gross would be more linguistically accurate, but that's an editorial/methodology call and out of scope for a number-sync fix. Flagged to Simon, no decision taken.

## Open items

- **Revenue ledger hero still renders "$19B"** (formatCurrency on 19.279 rounds to whole-billion). Home bar + card now show $19.3B. Same underlying number, different precision rules between home and ledger surfaces. Not fixed in this commit — would require either bumping ledger-side `formatCurrency` to allow 1-decimal on this stat (wider blast radius — affects every ledger page) or a per-stat override on revenue.html.
- **Hook ratio gross-vs-net editorial decision** (see above). Hold for Simon.
- **Bar widths still hardcoded** (`--bar-w` is a literal in the markup). The other bars (capex, usage, compute, power) are also static literals. Out of scope; flagged for a future "drive bar widths from data" pass if the figures move materially.
- **`beta` branch is 476 commits behind `main`.** Surfaced when proposing the staging path for this change. The repo's documented staging mechanism (`deploy-beta.yml`) is effectively unusable until beta is resynced. Used local `npm run preview` for the staging gate this time (port 4173 already had a Python SimpleHTTPServer running on the same directory, which served the updated HTML correctly). Worth a follow-up to either resync beta or formally adopt local-preview as the staging path.

## Acceptance criteria status

User asked "update the home bar from 17.4 to 19.4" and approved a wider scope mid-flight (sync bar + card, wire to data).

- [x] Home bar revenue figure no longer shows $17.4B
- [x] Home bar + Revenue Ledger card on the home page render the same number
- [x] Both surfaces read from `site-data.json` (no hardcoded literal in JS, fallback only)
- [x] Number is data-correct ($19.3B = `totalCustomerRevenue_gross` to 1 decimal)
- [x] Verified rendered output on local preview before publishing
- [x] Explicit "ship it" approval received in chat after preview
- [x] Pushed to `main`; `pages-build-deployment` workflow queued (run 25541953083)
- [ ] Revenue ledger hero parity ($19B vs $19.3B) — deferred, see open items

## Notion

No card opened for this — small ad-hoc fix. Mentioning here so Cowork has the context.
