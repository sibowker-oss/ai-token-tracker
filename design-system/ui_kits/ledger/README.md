# Ledger UI Kit

Dark, data-first kit for **The AI Ledger** (`ai-index.hepburnadvisory.com.au`).

## What's in here
- `index.html` — a single-page kit showing the full grammar: nav, hero with one-number hook, four-ledger tiles (Capital / Revenue / Usage / Power), Sankey, quarterly charts, Claims Ledger cards, filter bar, issuer table, methodology strip.

## Key patterns
- **Hero-hook** — declarative one-number framing, reader supplies the answer. Gradient clip-text on the emphasised fragment only; never the full headline.
- **Four-tile row** — always in the order Capital, Revenue, Usage, Power. Each colour-keyed to its semantic accent.
- **Sankey** — capital sources → middle nodes → revenue destinations. Annotated with the reconciled ratio.
- **Claims card** — issuer quote in Source Serif italic + arithmetic reconciliation strip + tier pill + link to sources.
- **Filter bar** — sticky, blurred, pill chips for category + input for freeform. Matches live site.
- **Table** — freshness dot in the first column; value right-aligned tabular-nums; ∆ vs Hepburn's reconciled number coloured green/amber/red.
- **Methodology strip** — always bottom of page, monospace reconciliation timestamp.

## Non-negotiables
- No emoji. No hype verbs. Tier + confidence on every number.
- Max width 1400px. Gradient allowed **only** on the wordmark and Sankey flows.
