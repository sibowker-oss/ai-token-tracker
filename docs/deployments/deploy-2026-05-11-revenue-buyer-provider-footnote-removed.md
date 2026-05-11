# Deployment: Remove buyer/provider split footnote from Revenue page

**Date:** 2026-05-11
**WQ:** —
**Branch/Commit:** main

## What shipped

Removed the buyer/provider methodology footnote that rendered beneath the AI-Natives × Provider revenue table on the Revenue page. The paragraph leaked site/build jargon onto a public surface:

- File path: `data/sankey_cost_structure.json:channel_mapping.buyer_provider_split`
- Internal field names: `subscription_pct`, `customer_revenue`
- Implementation terms: "engine-derived", "back-solves", "editorial per"

Files changed:
- `revenue.html` — paragraph + the two-line comment that only existed to explain the paragraph's overflow-wrap styling
- `beta/revenue.html` — same change

## Decisions made during implementation

- Removed the orphan comment block (`overflow-wrap:anywhere lets long inline <code> paths break…`) along with the paragraph since the comment only justified styling that no longer exists.
- Did not replace with a sanitised version — the rule is no site/build jargon on public surfaces, and a plain-English restatement of "AI Natives split is editorial, Consumer is data-derived, Enterprises back-solves" would still be expressing implementation provenance to a reader who has no context for it. If a public-facing methodology note is wanted later, it belongs in a dedicated `/methodology` page, not a 10px footnote on the chart.

## Open items

None.

## Acceptance criteria status

- [x] Paragraph removed from both `revenue.html` and `beta/revenue.html`
- [x] No remaining references to "AI Natives split" / "45/45/10" / "back-solves" / "buyer_provider_split" in either file
- [x] Deployment record written
