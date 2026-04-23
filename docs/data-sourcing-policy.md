# The AI Ledger — Data Sourcing Policy

> **Repo-local copy.** The editable source of truth lives at `The AI Ledger/data-sourcing-policy.md`. This copy is synced into the repo so Claude Code has the rules inline. Last synced: **2026-04-23**. If you edit this file, edit the Ledger version too.

**Version:** 1.0
**Date:** 2026-04-23
**Status:** Canonical. All new pages and data additions reference this document rather than restate it.
**Scope:** Every data point rendered anywhere on ai-index.hepburnadvisory.com.au.

---

## 1. Purpose

The AI Ledger's positioning rests on a single claim: **the numbers are traceable**. This policy is what makes that claim defensible. It defines how every data point is sourced, stored, reviewed, and labelled so that any reader, journalist or analyst can reach the underlying filing, report or announcement in one click.

Pages describe *what* is shown. This document describes *how the data got there*.

## 2. Core principle

> Every number on the site carries a source, a retrieval date, a review date, and a confidence label — or it doesn't ship.

No exceptions. Hardcoded numbers, hero stats, chart axes, benchmark cards — all of them. If a value cannot be cited back to a primary or named secondary source, it does not enter `site-data.json`.

## 3. Provenance schema

Every data entry — scalar benchmark, series row, company record, project entry — carries this block:

```json
{
  "value": ...,
  "unit": "...",
  "year": 2025,
  "source": "Publisher or filing name",
  "sourceUrl": "https://...",
  "retrievedAt": "2026-04-23",
  "nextReview": "2026-10-23",
  "confidence": "High | Med | Low",
  "note": "Optional caveats, assumptions, methodology notes"
}
```

Record-type-specific fields (e.g. `co`, `label`, `iso`, `plannedGW`) sit alongside. The provenance block is universal.

Where a figure is genuinely triangulated from multiple sources, `source` becomes `sources` (array) and each entry carries its own `sourceUrl` and `retrievedAt`. `confidence` reflects the weakest link.

## 4. Confidence rubric

Confidence is not a mood. It has explicit rules.

| Label | Criteria |
|---|---|
| **High** | Primary source — SEC filing, central bank / statistics agency, ISO filing, published academic dataset, direct-from-publisher CSV. Retrieval is reproducible by the reader. |
| **Med** | Authoritative secondary — IEA, IMF, Gartner, IDC, BNEF, Rystad, SemiAnalysis, or earnings-call transcript where the number is stated verbatim. Includes triangulated estimates where all inputs are independently sourced. |
| **Low** | Single press or analyst reference with no underlying primary document accessible. Rumour-adjacent. Used sparingly, never for headline numbers. |

Headline stats at the top of any page must be `High` or `Med`. Cards with `Low` confidence must be visually distinct (e.g. dashed border, muted tint).

## 5. Source tiers

What can be cited, and how.

### Tier 1 — Primary, machine-readable, free

Preferred. Default choice when available.

- SEC EDGAR (10-K, 10-Q, 8-K)
- FERC Form 1 / Form 715
- EIA (Form 861, AEO)
- ISO/RTO interconnection queue reports (ERCOT, PJM, MISO, CAISO, NYISO, SPP)
- EPA air permits
- Central bank / national statistics agencies
- World Bank / IMF / OECD open data
- Epoch AI (CC-BY)
- OpenRouter public rankings
- Nvidia / AMD / TSMC investor relations pages

### Tier 2 — Authoritative named analyst

Citable with a named source and retrieval date. Do not paraphrase as fact — always attribute inline.

- IEA, IMF WEO, Gartner, IDC, BNEF, Rystad, Wood Mackenzie, Dell'Oro, DC Byte, 451 Research, SemiAnalysis
- Bloomberg, Reuters, FT, WSJ desk reporting where an analyst or filing is named in the piece
- Podcast transcripts from the established priority tier (Latent Space, Acquired, All-In, Odd Lots)

Quoting a Tier 2 number from press coverage is acceptable when the primary report is paywalled — cite the coverage URL, not a fabricated report URL.

### Tier 3 — Event-driven, leading indicator

Does not enter `site-data.json` directly. Lands in an `inbox` file first, gets promoted only after corroboration.

- Company press releases and blog posts
- LinkedIn posts from named executives
- Analyst tweets / threads
- Utility IR decks

### Not citable

- Anonymous forum posts, Reddit comments, unnamed "sources familiar with the matter" without a primary document
- LLM-generated estimates that are not grounded in a specific input
- Paywalled reports the operator has not personally accessed

## 6. File structure

Every project follows this layout. Path is relative to repo root.

```
site-data.json                      — canonical data, read by the site
data/
  sources.registry.md               — master list of sources (see 6.1)
  sources.log.md                    — append-only update events (see 6.2)
  agents.log.md                     — agent invocations (see 6.3)
  snapshots/<page>/<YYYY-MM-DD>/    — raw PDFs / HTML / CSV at time of retrieval
  inbox/                            — Tier 3 holding area, one file per page
```

### 6.1 `sources.registry.md`

Master list of every source the site relies on. One row per source. Columns: `source_id`, `name`, `publisher`, `url`, `tier`, `licence`, `cadence`, `handler` (human name or agent id), `last_fetched`.

This is the document a journalist asks for when they want to know "where do your numbers come from." Keep it public and tidy.

### 6.2 `sources.log.md`

Append-only. One entry per data update, regardless of whether a human or agent made it.

Required fields: date, operator, field path in `site-data.json`, prior value, new value, source_id (from registry), reason.

### 6.3 `agents.log.md`

Append-only. One entry per agent invocation that touches data.

Required fields: date, agent name/version, prompt summary, fields touched, source_ids consulted, commit SHA.

### 6.4 Snapshots

Every retrieval saves the raw artefact (PDF, HTML, CSV) to `data/snapshots/<page>/<YYYY-MM-DD>/`. This is non-negotiable: source URLs rot, filings move, analysts revise. The snapshot is the audit trail.

## 7. Review cadence

Every benchmark carries a `nextReview` date. Default cadences:

- ISO queue data, 10-Q capex, OpenRouter rankings — **quarterly**
- IEA / EIA / World Bank annuals, hyperscaler 10-K, Epoch datasets — **annual**
- Lead times, structural ranges — **semi-annual to annual**
- Event-driven items (announced projects) — updated when status changes

Enforcement: a build-time lint fails the site build if any entry's `nextReview` is in the past. This is the only way the cadence survives contact with a busy quarter.

## 8. Agent rules

When any Claude or Claude Code agent touches data:

1. **Patch, don't overwrite.** Agents produce a JSON patch or diff. They never write directly to `site-data.json` in a way that bypasses review.
2. **Log every run.** `data/agents.log.md` gets an entry before the patch is written.
3. **Log every update.** `data/sources.log.md` gets an entry for each field changed, with prior and new value.
4. **Human review gate** for the first 2–3 successful cycles per agent. Once the agent has a clean track record, review can relax to spot-checks — but logging never stops.
5. **Snapshots always.** The agent saves raw source material to `data/snapshots/` before parsing.
6. **No silent confidence changes.** An agent may propose a confidence change; a human approves it.

## 9. Editorial guardrails

Data sourcing is inseparable from editorial voice.

- **Numbers first.** The number leads, the framing follows. No card ships with adjectives doing the work a value should do.
- **No editorial position.** The data informs the opinion; the Ledger does not supply it. "The build-out is unsustainable" is not a Ledger claim; "capex / revenue = 34×" is.
- **Triangulation beats single-source certainty.** Where two independent methods agree, confidence rises. Where they disagree, show both and explain.
- **Assumptions are visible.** Every derived metric exposes its inputs and assumptions inline or in a tooltip. No invisible constants.
- **Uncertainty is labelled, not hidden.** "Unknown" and "Low confidence" are first-class states. A missing value is honest; a guessed value is not.

## 10. How new pages use this policy

A new page spec should describe:

- What the page is (purpose, editorial framing)
- What metrics it shows
- Where those metrics sit in `site-data.json` (schema additions, if any)
- Which sources from the registry it uses, and any new sources it requires
- The visualisations and interactions

A new page spec should **not** re-describe the provenance schema, the confidence rubric, the log files, the agent rules, or the review cadence. Those live here. Reference this document by path.

## 11. Changes to this policy

Material changes (new confidence tier, schema field, log structure) are versioned at the top of this file and announced in the site changelog. Minor clarifications are in-place edits.

---

*Version 1.0 — 2026-04-23. Applies to all pages including the Token Dashboard, Follow the Dollar, Follow the Trillion, Power Ledger, Time Machine, Live Pricing and any future additions.*
