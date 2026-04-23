# The AI Ledger — Guidelines

> **Repo-local copy.** The editable source of truth lives at `The AI Ledger/GUIDELINES.md` (the thinking-layer project folder). This copy is synced into the repo so Claude Code has the rules inline. Last synced: **2026-04-23**. If you edit this file, edit the Ledger version too, or the two will drift.

**Status:** Canonical rulebook. All content, data, and agent work on the AI Ledger must conform.
**Scope:** Applies to `ai-index.hepburnadvisory.com.au`, `site-data.json`, all specs, and any agent that writes to the site.
**Last updated:** 2026-04-23
**Change policy:** Additive edits only without a note in the change log at the bottom. Removals require a rationale.

---

## 1. Purpose & positioning

The AI Ledger is an authoritative, data-first view on the economics of AI. Two jobs, in this order:

1. Be quoted. Give journalists, analysts, and operators numbers they can lift with confidence.
2. Promote Hepburn Advisory's expertise through credibility, not copy.

Positioning is **clear-eyed insider authority** — not an AI sceptic, not a booster. The voice is of someone who reads the filings and does the arithmetic.

The numbers form the opinion. The reader reaches the conclusion.

---

## 2. Editorial voice

### 2.1 Voice rules

- Neutral, numbers-first, declarative.
- Short sentences. Plain words. No adjective stacks.
- Every claim is either a sourced fact, a sourced estimate with method shown, or a derived calculation with assumptions visible.
- Interpretive verbs are allowed when they describe the arithmetic, not the vibe: *"implies"*, *"requires"*, *"reconciles to"*. Avoid *"shows"*, *"proves"*, *"reveals the truth about"*.
- Transparently approximate. Say "~$17B", "directional", "Med confidence" — don't pretend to precision the data doesn't have.

### 2.2 Banned framings

- **Hype**: "revolutionary", "transformative", "changes everything", "the AI era", "unprecedented".
- **Doom**: "AI bubble", "AI winter", "hits the wall", "the reckoning".
- **Consultancy filler**: "unlock", "leverage", "empower", "seamless", "end-to-end", "holistic".
- **Prediction**: the Ledger does not forecast. It publishes current state and directional arithmetic with the reader's inputs.

### 2.3 Hero hook pattern

Every substantive page leads with a provocative, numerate framing that forces a denominator into view. Pattern:

> **"For AI to hit $X by 20YY, it needs to equal Z% of [denominator]. Pick one."**
>
> **"Announced AI compute requires ~X GW of new load by 20YY. Today's queue clears at ~Y GW/year. The rest is on paper."**

The hook is a question in declarative form. The reader supplies the answer.

### 2.4 Methodology caveat (required, collapsible, per-page)

Every page with derived numbers carries a collapsible methodology block. Template:

> Projections are directional arithmetic, not forecasts. Benchmarks are dated and sourced. [Derived metric] defaults to [method]; every assumption is editable.

### 2.5 Chart & table titles

State what is measured. Not what it means.

- Good: *"US data-centre interconnection queue, by ISO (GW, 2025)"*
- Bad: *"The AI grid crunch in one chart"*

Interpretation belongs in methodology, tooltips, or clearly-marked callouts — never the title.

---

## 3. Naming conventions

### 3.1 Page names

- **`[Noun] Ledger`** is the canonical pattern for all live pages — e.g. `Revenue Ledger`, `Capital Ledger`, `Power Ledger`.
- Two words. Noun + `Ledger`. No colons, no taglines in the name itself.
- **V1 → V2 rename history** (do not revert):
  - `Sankey` / `Follow the Revenue` → **`Revenue Ledger`**
  - `Chips` / `Follow the CapEx` → **`Capital Ledger`**
  - `Follow the Trillion` → **`Claims Ledger`** (decided 2026-04-23; names the audit-of-trillion-dollar-claims job rather than the discourse it lives inside)
- The `Follow the [X]` construction is retained only inside hero copy and section headers as a rhetorical device ("follow the dollar") — never as a page name. *Follow the Trillion* is the sanctioned hero kicker above `Claims Ledger`.

### 3.2 In-Dev vs live — the promotion rule

Pages on the **In-Development** route are Simon's workspace. They may carry working titles, placeholder copy, hardcoded numbers, and experimental framings. None of the rules in this document are binding while a page lives under In-Dev.

**Before a page is promoted to the live site** (main nav, public URL, indexable), it must pass the following checklist:

- Name conforms to §3.1 (`[Noun] Ledger`).
- Hero copy conforms to §2 voice rules and §2.3 hook pattern.
- All numbers sourced to §4 standards — no hardcoded values; every datapoint in `site-data.json` with full provenance fields.
- Collapsible methodology block present (§2.4).
- Page structure matches §7.3 standard order.
- Freshness dots active on time-sensitive data (§7.2).
- Hepburn brand treatment conforms to §8.
- Entry added to `data/sources.registry.md` for any new sources.
- Build lint passes (§5.5).

A spec file (§9) must exist for the page before promotion, even if the In-Dev version was built without one.

### 3.2 One-line page descriptor

Every page carries an italic sub-line under the title that names the binding constraint or question.

> *"Grid capacity, substation lead times, gas turbine orders — the binding constraint."*
> *"What share of the global economy does AI need to own to hit its targets?"*

### 3.3 Metric & index naming

When inventing a proprietary metric, name it in two to four plain words, no ™, no ALL-CAPS, no "index" unless it genuinely aggregates.

- `Revenue yield per token` — good.
- `Hepburn AI Token Price Index` — acceptable; use sparingly and only when the metric is defensible and worth citing by name.

---

## 4. Sourcing & provenance — the hard rules

### 4.1 Every number is sourced

No number appears on the site, in a spec, or in a chart without a traceable source. No exceptions. This is the rule that makes the Ledger quotable.

### 4.2 Required fields on every datapoint

Every entry in `globalBenchmarks`, `powerLedger`, or any new data block carries:

| Field | Required | Notes |
|---|---|---|
| `value` | yes | Numeric. Units live in the sibling `unit` field, not the value |
| `label` | yes | Human-readable, publish-ready display name. See §5.6 |
| `unit` | yes | e.g. "USD", "GW", "TWh/yr", "tokens/day" |
| `year` | yes | The reference year the number describes |
| `source` | yes | Human-readable short name of the issuing body |
| `sourceUrl` | yes | Direct link to the primary artefact |
| `retrievedAt` | yes | ISO date of fetch |
| `nextReview` | yes | ISO date. Build lint fails if past due |
| `confidence` | yes | `High` \| `Med` \| `Low` (see 4.4) |
| `note` | optional | Caveats, rounding, scope |

For lead-time-style ranges, replace `value` with `minMonths` / `maxMonths` / `medianMonths` and record every contributing source in a `sources` array.

### 4.3 Source tier hierarchy

1. **Primary, machine-readable** — SEC EDGAR, FERC, EIA, ISO queue reports, vendor IR filings, Epoch AI CSV, OpenRouter. Preferred.
2. **Secondary, authoritative** — IEA/BNEF/Gartner/IDC reports, earnings-call transcripts, reputable press reporting on primary filings. Allowed; must be labelled.
3. **Tertiary, event-driven** — press releases, LinkedIn posts, podcast transcripts. Treat as *leading indicators*. Must be confirmed by a primary source before being written into a benchmark card.

Never cite a secondary summary of a primary source when the primary is available.

### 4.4 Confidence scoring — strict definitions

- **High** — primary-source filing or regulator-published dataset, within the last two review cycles.
- **Med** — triangulated from two or more secondary sources, or a primary source older than two cycles.
- **Low** — single secondary source, single tertiary source, or estimate with limited corroboration.

Confidence must be set honestly. Downgrade aggressively when in doubt.

### 4.5 ARR vs booked revenue — always labelled

The Ledger tracks both. They are not interchangeable.

- **Booked revenue (TTM)** is what customers paid in the trailing twelve months.
- **ARR / run-rate** is what the vendor claims as annualised current revenue.

Every revenue figure states which one. If the figure is an annualised extrapolation of a partial period, call it a run-rate.

### 4.6 AI-native vs rebrand filter

A company is classified as **AI-native** only if it was founded within five years before ChatGPT's launch (i.e. founded ≥ 2017). Companies older than that are **Enterprise Software** or **Digital Native**, regardless of AI product launches. The `AI Vintage` toggle filters to `founded >= 2023`.

This filter is not editorial — it is a taxonomy rule. Apply it consistently.

### 4.7 No silent updates

Every change to a published value is logged to `data/sources.log.md` with prior value, new value, reason, operator, and date. Agent-driven updates require a human review before merge. No auto-overwrites to `site-data.json`.

---

## 5. Data architecture

### 5.1 Master data file

`site-data.json` is the canonical source of truth for all dashboard pages. Read from it, don't duplicate.

### 5.2 Schema rules

- **Additive only.** New fields may be added; existing fields are never renamed or removed without a migration note and a backward-compatibility shim.
- **Backfill before extending.** When adding a new field, backfill existing entries (with a sensible default or explicit `null`) in the same change.
- **Layer tagging.** Multi-page benchmarks carry a `layer` field for filtering (e.g. `compute-power`, `electric-power`, `time-to-build`, `investment`, `denominator`).

### 5.3 Derived metrics are computed, not stored

Ratios, percentages, growth rates, implied GW, $/W — calculate at render time from raw stored values. Rationale: avoids stale derivations when inputs change. Each derived metric exposes its formula and assumptions in a tooltip or inline note.

### 5.3.1 One concept, one canonical field — cross-page consistency

When the same underlying concept appears on more than one page, both pages must read from the **same field** in `site-data.json`. Do not duplicate values.

- **Example of the bug to avoid:** 2025 AI-native revenue was derived and displayed on the Revenue Ledger, then hardcoded into Capital Ledger as a cascade input. The two numbers drifted. This cannot happen again.
- Every "concept" (e.g. `2025 AI-native booked revenue`, `hyperscaler capex`, `US DC interconnection queue`) has exactly one canonical entry in `site-data.json`. Every consuming page references that entry by key.
- If a page needs a *derivation* of a canonical number (e.g. a subset, a cascade input, a rebased figure), it computes that derivation at render time — it does not copy the number into a new field.
- If two fields look like they represent the same concept, they must be reconciled: either unified into one, or renamed with an explicit scope distinction (`revenue_booked_ttm` vs `revenue_run_rate`) and both must cite the same primary source.
- A `dataReferences` map in `site-data.json.meta` lists, for each canonical field, the pages and components that consume it. Updating a value surfaces every downstream render.
- When a value is used as input to another page's visualisation (a "cascade"), the consuming page must show its source in the tooltip: *"Cascade input: `revenue_booked_ttm_2025` from Revenue Ledger, retrieved 2026-04-23"*.

### 5.4 Companion provenance files

The repo must maintain, alongside `site-data.json`:

- `data/sources.registry.md` — authoritative list of every source used, with handler, cadence, licence, and fetch method.
- `data/sources.log.md` — append-only log of every value update (date, operator/agent, field, prior → new, reason).
- `data/agents.log.md` — append-only log of every agent invocation (date, agent name/version, prompt summary, fields touched, commit SHA).
- `data/<page>/` — raw snapshots of primary documents (PDFs, CSV extracts, 10-Q excerpts) by retrieval date. The site must never lose the primary artefact to a moved URL.

### 5.5 Build lint (required)

The site build fails if:

- any `nextReview` date is in the past,
- any datapoint is missing a required provenance field,
- any new field is introduced without a backfill value on existing entries,
- any entry referenced by a rendered component is missing its `label` (see §5.6).

### 5.6 Publish-ready labels — no raw keys on screen

Every value that renders on the public site must resolve to a **human-readable, publish-ready label**. JSON keys, internal identifiers, and schema slugs are for machines and must never appear in UI.

- Every data entry carries a `label` field (see §4.2). This is what the site displays.
- Keys like `global_dc_electricity_twh`, `hyperscaler_capex`, `anthropic`, `openai`, `ai-application` are **internal only**. They must resolve to a display label (`"Global data-centre electricity consumption"`, `"Anthropic"`, `"AI Application"`) before render.
- Controlled vocabularies — provider arrays, category enums, subcategory tags, ISO codes, status values — each have a published `labels` dictionary in `site-data.json` that the UI reads through. No hardcoded key-to-label mapping in JavaScript.
- Column headers, filter dropdowns, chart legends, tooltip titles, axis labels, table cells — all subject to this rule. Read from `label`, never from the key.
- Casing and formatting on display values must be publish-ready: `"High"`, not `"HIGH"` or `"1"`; `"Under construction"`, not `"wip"`.
- If a new key is added without a corresponding label, the build fails.

This rule exists because early V1 updates rendered raw keys (`anthropic`, `ai-application`) in the UI where labels should have been. That cannot happen on the live site.

---

## 6. Agents & automation

### 6.1 One agent, one source

Each data-collection agent targets exactly one source (one ISO queue, one vendor 10-Q, one regulator dataset). Avoid omnibus scrapers.

### 6.2 Agent contract

Every agent must:

- Log invocation to `data/agents.log.md` with date, agent name/version, prompt summary, fields touched, commit SHA.
- Produce a JSON patch against `site-data.json` rather than a direct write.
- Emit a human-reviewable diff. The patch is merged by a human; no silent commits.
- Update `retrievedAt` and `nextReview` on every touched entry.

### 6.3 Agent register

When a new agent is created, add it to `data/agents.registry.md` with: name, purpose, sources touched, output schema, cadence, owner, prompt location, and date created.

---

## 7. Visual design

### 7.1 Theme & palette

Dark theme. Fixed accent palette:

| Token | Hex | Use |
|---|---|---|
| `--accent` | `#3b82f6` | Primary |
| `--accent2` | `#8b5cf6` | Secondary series |
| `--accent3` | `#06b6d4` | Tertiary / contrast |
| `--orange` | `#f59e0b` | Emphasis, warnings, gap-to-target |

Do not introduce new accent colours without a note in the change log.

### 7.2 Freshness dots

Every table row that carries time-sensitive data shows a freshness dot driven by `retrievedAt`:

- Green — ≤30 days
- Yellow — 31–90 days
- Grey — >90 days

### 7.3 Page structure (standard)

Every substantive page follows this order:

1. **Hero** — noun-ledger/follow-the-X title, italic one-liner, hero hook.
2. **Headline metric** — one number, large, with a three-state treatment where it fits (*deployed / under construction / announced*, or equivalent).
3. **Benchmark cards** — six cards as the default grid, one metric each, with source + `retrievedAt` visible on hover or inline.
4. **Primary visualisation** — the signature chart. One per page.
5. **Supporting visualisations** — max three.
6. **Methodology (collapsible)** — caveats, formulas, assumptions, source review cadence.
7. **Open questions** — explicit list of what the page does not yet resolve.
8. **Last updated footer** — ISO date + link to the spec that governs the page.

### 7.4 Shareable state

Pages with interactive controls (sliders, toggles) must encode state in URL params so any configuration is linkable in social posts.

### 7.5 Mobile optimisation

Mobile is a first-class render target. A meaningful share of social traffic (LinkedIn, X) opens on phone. If a page doesn't read on mobile, it doesn't get quoted.

**Breakpoints:**

- `≥1024px` — desktop, full layout as designed.
- `768–1023px` — tablet; multi-column grids collapse to two columns, navigation may condense.
- `<768px` — mobile; single-column, navigation collapses to hamburger or a minimal strip.

**Mobile rules:**

- **No horizontal scroll.** Ever. Includes tables, charts, hero copy, footnotes.
- **Tables** — convert wide tables (>4 columns) to a stacked card layout on `<768px`, or provide a horizontally-scrollable container with a visible affordance (shadow edge + "swipe" hint) and a sticky first column.
- **Charts** — every chart must render legibly at 375px width. Use responsive SVG, not fixed dimensions. Test legend, axis labels, and tooltips at phone width. Complex visualisations (Sankey, nested treemap, stack diagrams) may ship a simplified mobile variant — disclose this via a small "Tap for full view" affordance that opens the desktop layout in a modal or landscape-locked view.
- **Interactive controls** — sliders, toggles, dropdowns must be thumb-sized (minimum 44×44px tap target). Continuous sliders that are hard to control on touch devices should expose a numeric input fallback.
- **Hero copy** — hook must fit within two viewport heights on a 390×844 screen without requiring scroll to reach the headline metric.
- **Freshness dots, confidence badges, source links** — these must remain visible on mobile. They are the credibility signal. Do not hide them behind expand/tap affordances unless the full data is still discoverable in one tap.
- **Font sizing** — body copy ≥16px, headline metric scales down but remains the visually dominant element on the page.
- **Methodology collapsibles** — must render correctly on touch; no hover-only reveals anywhere on the site.

**Mobile test bar (part of §11 release gate):**

- Page passes on iPhone 14/15 Safari and Android Chrome at 390×844 and 360×800.
- No layout shift on orientation change.
- All charts legible without zoom.
- All CTAs tappable without mis-fire.

---

## 8. Hepburn Advisory brand presence

The brand is present via credibility, not copy.

- **Header / footer** carry Hepburn Advisory wordmark + link to the advisory site on every page.
- **Per-page byline** — "Prepared by Hepburn Advisory" sits under the methodology block, not above the fold.
- **Advisory CTAs** are allowed in one location per page, below the primary content, and must be clearly separated from the data. Preferred patterns: *"Get the underlying dataset"* (email capture), *"Talk to Hepburn Advisory"* (contact link).
- **No in-line promotion.** The data, charts, and methodology carry no advisory copy.
- **"Hepburn view" callouts** are permitted sparingly. When used, they must be visually distinct from data blocks, prefixed "Hepburn view:" or "Analyst note:", and carry a signed-off date. They are opinion, and must be labelled as such.

---

## 9. Specs & briefs

Every non-trivial change ships with a spec. Spec structure (established pattern):

1. Working name, placement, dashboard URL, date, status.
2. Purpose (one paragraph, answers a single question).
3. Editorial positioning — explicit restatement of what voice this page is in and what framings it avoids.
4. Core interaction (if applicable).
5. Data audit — what exists, what needs collecting.
6. Data collection plan — sourced, tiered, prioritised.
7. Schema extension — additive JSON patches, example payloads.
8. Visualisation plan — V1 / V1.1 / V2 scope.
9. Source tracking & agent log requirements (per section 4, 5, 6 above).
10. Implementation phases with day estimates.
11. Open questions.
12. Last-updated line referencing prior conventions.

Specs are implementation-ready for Claude Code. They are the contract.

### 9.1 Two homes — thinking vs contract

Briefs live in two folders. The distinction is load-bearing.

- **`The AI Ledger/` (Claude project folder)** — the **thinking layer**. Drafts, discussions, exploratory specs. Freely editable. Nothing here is binding on the code.
- **`apac-ai-intel/briefs/` (code repo)** — the **contract layer**. Frozen specs that have been handed off to implementation. Append-only edits; changes carry a change-log entry.

A brief exists in one place or both, never neither. If code in `apac-ai-intel` implements something, a brief for it must exist in `apac-ai-intel/briefs/`.

### 9.2 Folder structure in the code repo

```
apac-ai-intel/briefs/
├── README.md       # handoff process, filename convention
├── active/         # briefs currently being implemented
├── completed/      # briefs whose scope has shipped
└── archive/        # briefs abandoned or superseded
```

Filename convention: `YYYY-MM-DD-short-name.md` — date is the handoff date (move into `active/`), not the draft start.

### 9.3 Handoff process

1. **Draft & discuss** in `The AI Ledger/`. Iterate freely.
2. **Freeze** the brief when it conforms to §9 spec structure and is implementation-ready.
3. **Copy** (do not move) the frozen brief into `briefs/active/`. The Ledger copy stays as the editable thinking version; the repo copy is the immutable contract.
4. **Implement** against the brief. Material scope changes during implementation are recorded in-place with a change-log entry at the bottom of the brief.
5. **Complete** — when the scope has shipped and passed §11, move from `active/` to `completed/` and append `Shipped: <date>, commit <sha>`.
6. **Archive** — abandoned or superseded briefs move to `archive/` with a one-line reason.

### 9.4 Agent briefs

Agent specs follow the same flow. The brief in `briefs/` captures the *why* and the design; `data/agents.registry.md` (per §6.3) tracks *what is currently running*. The two must not drift — a registered agent without a brief, or a shipped brief not reflected in the registry, both fail the §11 gate.

---

## 10. Don'ts — quick reference

- No unsourced numbers.
- No hype or doom framings (see 2.2).
- No editorial chart titles.
- No cherry-picked time windows. Justify every x-axis range in methodology.
- No silent value updates. Every change logged.
- No derived values stored as facts. Compute at render.
- No raw JSON keys or internal slugs on screen. Every rendered value reads from a publish-ready `label`.
- No agent writing directly to `site-data.json`. Patches go through human review.
- No in-line promotional copy inside data sections.
- No cross-page duplication of data; read from `site-data.json`.
- No hardcoded cascade inputs. If Page B uses a number from Page A, it reads the canonical field — never a copy (§5.3.1).
- No new accent colours, no new naming patterns, no new provenance schemas without a change-log entry here.

---

## 11. Release testing — the go-live gate

This section defines **what must be true** before any major page, dataset, or schema change goes live. The **mechanics** — test scripts, CI hooks, screenshot diffs, the release-check agent — live in a separate `TESTING.md` (to be created). This section is the governance bar; `TESTING.md` is the runbook.

### 11.1 Scope — what triggers the gate

Apply the full gate when any of the following ships:

- A new public page (promotion from In-Dev per §3.2).
- A change to page structure, hero, or primary visualisation on an existing live page.
- A schema change to `site-data.json` (new top-level block, new field on existing entries).
- A new agent writing to `site-data.json`.
- A bulk data refresh (>10 entries updated in one commit).

Minor copy edits, single-datapoint corrections, and styling tweaks do not require the full gate — but they do require the §11.4 smoke test.

### 11.2 Data & provenance checks

- Every new or changed datapoint has all required fields per §4.2 (`value`, `label`, `unit`, `year`, `source`, `sourceUrl`, `retrievedAt`, `nextReview`, `confidence`).
- Every new source is registered in `data/sources.registry.md`.
- Every changed value has a corresponding entry in `data/sources.log.md` with prior → new.
- Every agent run is logged in `data/agents.log.md`.
- No `nextReview` date in the past on any rendered entry.
- Confidence ratings set honestly per §4.4.
- ARR vs booked revenue labelled clearly per §4.5.
- AI-native filter applied consistently per §4.6.
- **Cross-page reconciliation passes (§5.3.1).** For every canonical field consumed by more than one page, the displayed value matches across all consumers. Any page carrying a cascaded/derived version of another page's number must read from the canonical field, not a local copy. Reconciliation audit run against `dataReferences` before promotion — any drift fails the gate.

### 11.3 Rendering & UX checks

- No raw JSON keys visible anywhere (§5.6).
- All `label` fields present and publish-ready.
- Freshness dots active and correctly coloured.
- Page structure matches §7.3 (hero → headline metric → cards → viz → methodology → open questions → footer).
- Methodology collapsible present and functional.
- Mobile gate passes per §7.5 test bar.
- Accent palette unchanged or palette change noted in change log.
- Hepburn brand treatment per §8 — footer wordmark, byline under methodology, max one CTA below the fold, no in-line promotion.

### 11.4 Smoke test (minimum bar, applies to every change)

Before any commit to `main`:

- Page loads without console errors on Chrome, Safari, Firefox.
- All links resolve (no 404s, no dead `sourceUrl`s — link-checker run against `site-data.json`).
- Shareable URL params round-trip (§7.4).
- Build lint passes (§5.5).

### 11.5 Editorial sign-off

One human read-through against §2 (voice, banned framings, hero hook, methodology caveat, chart titles) before promotion. The read-through is logged in the spec's implementation log, noting reviewer and date.

### 11.6 Rollback

Every promotion ships behind a reversible commit. If a post-go-live issue is found, roll back first, fix second. A silent in-place fix to a published dataset is not acceptable — the rollback itself must be entered in `data/sources.log.md`.

### 11.7 Separate artefacts (not in this doc)

- `TESTING.md` — the runbook. Scripted checks, screenshot baselines, link-checker config, mobile device matrix, CI wiring, how to run the checks locally.
- `release-check` agent — an agent that runs §11.2–§11.4 against a pending commit and emits a pass/fail report. Logged to `data/agents.log.md` per §6.

When `TESTING.md` and the agent exist, this section stays unchanged — it defines the bar, not the procedure.

---

## 12. Change log

| Date | Change | Rationale |
|---|---|---|
| 2026-04-23 | Initial codification | Consolidates conventions established in `follow-the-trillion-spec.md`, `power-ledger-spec.md`, `top-consumers-expansion-spec.md` |
| 2026-04-23 | §3 naming correction | V2 rename: `Follow the Revenue` → `Revenue Ledger`; `Follow the CapEx` → `Capital Ledger`. Canonical pattern is `[Noun] Ledger`. |
| 2026-04-23 | §3.2 In-Dev rule | Working titles allowed on In-Dev; strict conformance required at promotion. |
| 2026-04-23 | §5.6 labels rule | Publish-ready labels required; no raw JSON keys in UI. Fixes issue observed in early V1. |
| 2026-04-23 | §7.5 mobile | Mobile is a first-class render target. Breakpoints, rules, test bar. |
| 2026-04-23 | §11 release testing | Go-live gate codified. Runbook lives in separate `TESTING.md` (to be created). |
| 2026-04-23 | §5.3.1 cross-page consistency | One concept, one canonical field. Fixes the Revenue Ledger → Capital Ledger cascade drift seen in earlier iteration. `dataReferences` map + reconciliation audit added to §11.2 gate. |
| 2026-04-23 | §9.1–9.4 briefs handoff | Two-folder model codified: `The AI Ledger/` = thinking layer, `apac-ai-intel/briefs/` = contract layer. Added `active/completed/archive/` structure, filename convention, handoff steps, and agent-brief linkage to §6.3 registry. |
| 2026-04-23 | §3.1 Claims Ledger | `Follow the Trillion` resolved to canonical **`Claims Ledger`** under the `[Noun] Ledger` convention. Names the job (auditing trillion-dollar claims against global denominators) rather than the TAM discourse. *Follow the Trillion* retained as hero kicker. |
