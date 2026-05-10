# wq-102 — Numbers binding & editorial supersession (catalogue + bind, six-page priority sweep)

**Parent context:**
- wq-064 produced a site-wide audit of hardcoded numbers (report at `data/wq-064-hardcoded-audit.md`). Audit was report-only; no binding architecture was built. Follow-on briefs (wq-067 / 073 / 074 / 077 / 078 / 087-093) addressed individual rewires but never the systematic layer.
- wq-066 backfilled editorial values into `entities.json:market_aggregates` so the engine can reproduce published headline figures.
- wq-093 reframed the homepage around the five-ledger Layer Stack (Capex, Compute, Power, Usage, Revenue).
- The pipeline (`source → claim → vault-inbox → review → vault-data.json → entities.json → site-data.json → public HTML`) is now mature enough that nightly source ingestion will progressively replace editorial estimates with verified-source-derived values. The site must surface that improvement automatically; it cannot silently keep stale editorial numbers.

**Stage:** Scoped — ready for VS Code pickup
**Priority:** H (every public number on six priority pages is at risk of going stale; this brief installs the dynamic-binding architecture)
**Owner:** Claude Code (implementation), Simon (staging review, publish gate)
**Status:** Scoped — all decisions locked, ready for Claude Code pickup
**Estimated effort:** Large (2–3 sessions; Stage 1 catalogue ≈ 1 session, Stage 2 binding + supersession ≈ 1–2 sessions)
**Files touched (anticipated):**
- New: `scripts/build_numbers_manifest.py`, `data/numbers-manifest.json`, `scripts/render_numbers.py`, `data/numbers-changelog.md`
- Modified: each of the six priority HTML pages (replace literal numbers with `data-number-id="..."` anchors), `generate_site_data.py` (publish supersession state), CLAUDE.md (add binding contract)
- Read-only inputs: `data/wq-064-hardcoded-audit.md`, `entities.json`, `site-data.json`, `vault-data.json`, `data/consensus_overrides.json`, `assumptions-audit.md`

---

## 0. Decisions

**Locked (Simon, 2026-05-10):**
- D1 — Supersession rule: **auto-replace at build time** when a sourced value clears the threshold. Build emits `data/numbers-changelog.md` so every number movement is auditable.
- D2 — Catalogue lives in **two places**: `data/numbers-manifest.json` (machine-readable; canonical for build) + a Notion DB row per number (human tracking; mirrors manifest). Notion is canonical for *workflow*; manifest is canonical for *build*.
- D3 — Page scope: **Home, Capital, Revenue, Compute, Usage, Power**. Maps to `index.html`, `capital.html`, `revenue.html`, `compute.html`, `usage.html`, `power.html` in `/beta/`. Other ~30 pages out of scope for wq-102; addressed in a follow-on sweep once the pattern proves out.
- D4 — **Supersession threshold:** a sourced value supersedes editorial when `provenance_score ≥ 0.7` AND `consensus_weight ∈ {indicative, robust}`. Same threshold the existing pipeline uses for site-publishable claims. Below threshold, editorial fallback holds. Stage 2 dry-run will surface anything that flips unexpectedly; threshold can be tuned then.
- D5 — **Render mode: build-time render.** The site is static HTML on GitHub Pages; the build resolves manifest entries against `site-data.json` / `entities.json` and writes the final value into the HTML. Preserves SEO and first-paint speed; matches existing pattern.
- D6 — **No visible editorial-vs-sourced tag on the public site.** State is tracked in source-code comments (`<!-- num: hp.capex.cumulative — sourced 2026-MM-DD -->`) and the build changelog. Public-facing visual treatment ("estimate" pip etc.) is a separate methodology decision and out of scope for wq-102.

**No open decisions.** Ready for Claude Code pickup.

---

## 1. Why this exists

The wq-038 → wq-064 → wq-066 chain established that the site mixes engine-derived and editorial numbers without a systematic boundary. Eight months of wire-by-wire fixes have addressed roughly 30% of the hardcoded surface, but every new page (wq-093 homepage refresh, wq-097 revenue model publication) reintroduces hardcoded literals because there is no binding contract for how a number reaches the page.

The pipeline has now matured to the point where new sources land daily (wq-098/099/100 pipeline program shipped 2026-05-08). Editorial numbers that were defensible six months ago are progressively being superseded by sourced numbers with provenance. **Without a binding-and-supersession layer, the site will increasingly display stale editorial figures while the underlying data has moved on.**

This brief installs that layer for the six highest-traffic / highest-number-density pages.

## 2. Architectural shape

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ entities.json   │    │ site-data.json  │    │ numbers-        │
│ vault-data.json │───>│ (engine output) │───>│ manifest.json   │
│ consensus_      │    │                 │    │ (binding spec)  │
│ overrides.json  │    └─────────────────┘    └─────────────────┘
└─────────────────┘                                    │
                                                       v
                                          ┌─────────────────────┐
                                          │ render_numbers.py    │
                                          │  - resolve each id   │
                                          │  - apply supersession│
                                          │  - rewrite HTML      │
                                          │  - emit changelog    │
                                          └─────────────────────┘
                                                       │
                                                       v
                                          ┌─────────────────────┐
                                          │ /beta/{page}.html   │
                                          │ (built artefact)    │
                                          └─────────────────────┘
```

The contract: **every number on the six priority pages has an `id` in `numbers-manifest.json`**. The page source carries an anchor (e.g. `<span data-num="hp.capex.cumulative">$745B</span>`). The build resolves the id against the manifest, applies supersession logic, and writes the canonical value.

## 3. Stage 1 — Catalogue (numbers-manifest.json)

### 3.1 Manifest schema

```json
{
  "version": "1.0",
  "generated": "2026-05-10",
  "entries": [
    {
      "id": "hp.capex.cumulative",
      "page": "index.html",
      "anchor_selector": "[data-num='hp.capex.cumulative']",
      "current_rendered_value": "$745B",
      "semantic": "market_aggregate.capex_cumulative_2023_2025",
      "source_state": "editorial",
      "source_path": "entities.market_aggregates.cumulative_2023_2025.capex_total",
      "editorial_fallback": {
        "value": 745,
        "unit": "$B",
        "origin": "editorial_audit_doc_backfill",
        "audit_ref": "assumptions-audit.md §Capex"
      },
      "supersession_threshold": {
        "provenance_score_min": 0.7,
        "consensus_weight_min": "indicative"
      },
      "format": "currency_b_compact",
      "last_changed": null,
      "notion_id": "<filled by sync>"
    }
  ]
}
```

Key fields:
- `id` — stable, dotted; `<page>.<topic>.<facet>`. Survives content rewrites.
- `source_path` — JSON pointer (or path expression) into `site-data.json` / `entities.json`. Resolves at build.
- `source_state` — `editorial` | `sourced` | `computed`. Stage 2 build flips this.
- `editorial_fallback` — what gets rendered when no qualifying sourced value exists. **The supersession story lives here**: rendered value comes from sourced when threshold met, else from editorial_fallback.
- `format` — one of a small enum (`currency_b_compact`, `currency_m_compact`, `tokens_compact`, `percentage_1dp`, `ratio_x_to_1`, `count_compact`, `text_passthrough`). Centralises formatting so a number doesn't render as `$745B` on one page and `$745 B` on another.

### 3.2 Page-by-page catalogue work

For each of the six priority pages, do the following:

1. Read every numeric value (script defined in §3.3).
2. Classify per wq-064 categories: market_aggregate / per_entity_metric / scenario_assumption / methodology_constant / factual_reference / ui_default.
3. For each entry that should be data-driven:
   - Assign a stable `id`.
   - Trace the `source_path` (which key in `site-data.json` / `entities.json` already produces this value, OR mark `source_path: null` if no pipeline path exists yet).
   - Capture the current rendered value as `editorial_fallback`.
   - Add the entry to `numbers-manifest.json`.
4. Add a corresponding row to the Notion "Numbers Audit" DB (link via `notion_id` field).

### 3.3 Catalogue script

`scripts/build_numbers_manifest.py`:
- Walk the six priority pages.
- Reuse the regex / classifier from wq-064's `audit_hardcoded_numbers.py` (avoid rebuilding what works).
- For each candidate value, attempt automatic source-path resolution by matching value + context against `site-data.json` keys. Where it resolves, populate `source_path`; where it doesn't, leave null and surface in a gap report (`data/wq-102-source-path-gaps.md`).
- Emit `numbers-manifest.json` (skeleton); Simon + Claude Code complete `source_path` fields where auto-resolution failed.

### 3.4 Stage 1 acceptance criteria

1. `data/numbers-manifest.json` exists with one entry per data-driven number on each of the six priority pages.
2. `data/wq-102-source-path-gaps.md` lists every entry where `source_path` could not be auto-resolved, with a recommended path or a `needs research` flag.
3. Notion DB "TAIL Numbers Audit" populated with one row per manifest entry; columns: id, page, current_value, semantic, source_state, source_path, editorial_fallback_value, status.
4. Manifest validates against a JSON schema (also new: `schemas/numbers-manifest.schema.json`).
5. **No HTML changes yet.** Stage 1 is read-only on the site.

## 4. Stage 2 — Binding + supersession (build-time render)

### 4.1 Anchor the HTML

For each manifest entry, replace the literal in the HTML with an anchor:

```html
<!-- before -->
<span class="hook-number">$745B</span>

<!-- after -->
<span class="hook-number" data-num="hp.capex.cumulative">$745B</span>
```

The literal stays as a defensive default (for a viewer with JS disabled mid-build, or a build failure). The build overwrites it with the resolved value.

### 4.2 Build script

`scripts/render_numbers.py`:
1. Load `numbers-manifest.json`.
2. For each entry:
   - Resolve `source_path` against `site-data.json` / `entities.json`.
   - If resolved value's provenance clears `supersession_threshold` → **sourced**, render that value.
   - Else → render `editorial_fallback.value` formatted via `format`.
   - Track resolution outcome.
3. Open each affected HTML page; for each `data-num="<id>"` element, replace inner text with the resolved value (preserving surrounding markup).
4. Emit `data/numbers-changelog.md` summarising:
   - Numbers that flipped from editorial → sourced this build.
   - Numbers whose sourced value moved by ≥5% since last build.
   - Numbers still editorial (with a "needs source" call-to-action).
5. Emit a JSON build log `data/numbers-build-<date>.json` for diff inspection.

### 4.3 Wire into existing build

`render_numbers.py` runs **after** `generate_site_data.py` and **before** any deploy step. Add to the existing build sequence (CI workflow + local makefile or equivalent — Claude Code to identify the canonical entry point and integrate).

### 4.4 Stage 2 acceptance criteria

1. All six priority pages have every catalogued number anchored (`data-num="..."`).
2. `render_numbers.py` runs cleanly; produces a deterministic HTML output (running it twice yields no diff).
3. `data/numbers-changelog.md` accurately reports the supersession state for every manifest entry.
4. **Visual regression check**: rendered numbers on each priority page match either (a) the engine-derived value when threshold met, or (b) the editorial_fallback when not. No silent drift.
5. **Staging URL produced** per the TAIL Publishing Gate. Simon reviews before promotion.
6. CLAUDE.md updated with the binding contract: any new number on a priority page must be added to `numbers-manifest.json`; literals without `data-num` on those pages fail a release-gate check.
7. Release-gate addition: a check that walks the six priority pages and rejects any numeric literal not anchored to a manifest id (regex similar to wq-064's, allowlist for non-data numerics).

## 5. Edge cases

- **Numbers inside JS scenario objects** (e.g. `index.html` SCENARIOS). The current pattern stores all three scenarios as literals and toggles via JS. Two paths: (a) keep SCENARIOS literal but populate it from manifest at build (preferred — JS keeps working), (b) refactor to a JSON file. Default to (a); flag (b) as a future cleanup.
- **Cumulative values that depend on multiple entities**. `source_path` may need to resolve to a computed key (e.g. `entities.market_aggregates.cumulative_2023_2025.capex_total`). If the engine doesn't compute it, the manifest entry's `source_path` points at a stub and the entry stays editorial until the engine is extended (out of scope for wq-102; logged as future brief).
- **Approximation indicators** (`~`, `≈`). Format strings carry an `approx_prefix` flag; manifest preserves authorial intent.
- **Numbers shared across pages** (e.g. cumulative capex on both home and capital). Single manifest entry, multiple anchors via `pages: [...]` array, one resolution applied to all. Eliminates cross-page drift.
- **Meta tags / og:description**. Index.html has hardcoded numbers in `<meta property="og:description">`. These are also anchorable via attribute substitution (`data-num` on a hidden tag the build reads). Include in scope — meta tags are a known stale-number hotspot.
- **Editorial numbers that are intentionally fixed** (founding dates, methodology constants). Mark `source_state: "fixed"` in manifest; build skips supersession but still routes through formatter for consistency.

## 6. Test plan

1. **Unit**: `render_numbers.py` round-trip — anchor a test page, run, confirm output matches expected for both sourced and editorial paths.
2. **Idempotence**: run twice; second run produces zero diff.
3. **Threshold sweep**: stub a manifest entry with a sourced value just above and just below threshold; confirm correct branch chosen.
4. **Visual diff**: pre/post HTML diff on each of the six priority pages. Every change should match an expected manifest-driven flip OR be intentional editorial.
5. **Cross-page consistency**: shared ids resolve to identical rendered text on every page they appear.
6. **Release gate**: introduce an unanchored literal `$999B` on a priority page; confirm release gate fails.
7. **Changelog accuracy**: artificially flip three entries from editorial to sourced in the manifest; confirm changelog lists exactly those three.

## 7. Out of scope for wq-102

- The other ~30 pages outside the priority six (follow-on brief, candidate id wq-103).
- Standalone `compute.html` page build (D4 dependent).
- Visual treatment of editorial vs. sourced values on the public surface (D7 — separate methodology brief).
- Engine extension to compute aggregates that don't yet exist (logged as gaps; brief follows).
- Migrating `index.html` SCENARIOS object out of HTML JS into a JSON file (cleanup, not blocker).

## 8. Definition of done

- Stage 1: manifest, gap report, Notion DB rows exist; no HTML touched.
- Stage 2: anchors in place, render script integrated into build, changelog produced, release-gate check active, staging URL shared in chat per the Publishing Gate, Simon's explicit approval received before promotion to `ai-index.hepburnadvisory.com.au`.
- CLAUDE.md updated with the binding contract.
- A deployment record is written to `docs/deployments/dep-<date>-wq-102.md` per the TAIL Workflow Protocol, citing the staging URL and approval timestamp.

---

## 9. Handoff prompt — VS Code / Claude Code

````
Pick up wq-102 from /Users/simonbowker/Developer/apac-ai-intel/docs/briefs/wq-102-numbers-binding-and-supersession.md.

This is a TWO-STAGE brief. Do NOT advance to Stage 2 until Simon has reviewed Stage 1 outputs in chat.

Before starting: §0 has no open decisions — all six (D1–D6) are locked. If anything in the brief looks ambiguous, write a decision file to docs/decisions/open/dec-2026-05-10-wq-102-D{N}.md per the TAIL-WORKFLOW-PROTOCOL and stop. Do not guess.

Stage 1 — catalogue:
1. Build scripts/build_numbers_manifest.py per §3.3. Reuse wq-064's audit script as a starting point.
2. Walk the six priority pages: index.html, capital.html, revenue.html, compute.html, usage.html, power.html.
3. Emit data/numbers-manifest.json (per §3.1 schema), schemas/numbers-manifest.schema.json, and data/wq-102-source-path-gaps.md.
4. Sync manifest entries into the Notion "TAIL Numbers Audit" DB (Simon will create the DB and provide the database id; if not yet provided, write entries to a CSV at data/wq-102-notion-import.csv and flag).
5. Stop. Post a Stage 1 summary in chat: how many entries, % auto-resolved, gap list, three illustrative manifest entries. Wait for Simon's go-ahead before Stage 2.

Stage 2 — binding + supersession (next session):
1. Anchor every manifest entry in HTML (§4.1). Preserve the literal as fallback.
2. Build scripts/render_numbers.py per §4.2.
3. Wire into the existing build sequence after generate_site_data.py.
4. Add the release-gate check per §4.4 item 7.
5. Update CLAUDE.md with the binding contract.
6. BUILD TO STAGING ONLY. Share the staging URL in chat with: how many numbers flipped sourced vs. editorial, three illustrative diffs, the changelog excerpt. Do NOT publish to ai-index.hepburnadvisory.com.au until Simon replies "approved" / "ship it" / "go live". Silence is not approval.
7. After approval, promote and write docs/deployments/dep-2026-MM-DD-wq-102.md citing the staging URL and approval timestamp.

Branching:
- Stage 1: feature/wq-102-stage1-manifest
- Stage 2: feature/wq-102-stage2-binding (branched from main after Stage 1 merges)

Stop conditions:
- Anything in the brief looks ambiguous → decision file + stop.
- Manifest auto-resolution rate <40% → stop, escalate to Simon. The pattern isn't ready and we'd be hand-curating most entries.
- More than 10% of manifest entries have no source_path candidate → stop. This means the engine is missing too many keys; needs a precursor brief.
- Visual diff on Stage 2 staging shows any unintended number changes → stop, do not promote, post the diff in chat.

Reference inputs (read-only):
- data/wq-064-hardcoded-audit.md — prior audit; harvest classification logic
- entities.json, site-data.json — source-of-truth for source_path resolution
- data/consensus_overrides.json — where engine output is overridden; manifest entries should call this out
- assumptions-audit.md — origin of editorial values

Notion: wq-102 → in_progress on Stage 1 start; → ready_for_review at end of each stage with summary in card comment.
````
