# TESTING.md — The AI Ledger release runbook

**Status:** Runbook. The governance bar lives in `GUIDELINES.md` §11.
**Scope:** `site-data.json`, every public page on `ai-index.hepburnadvisory.com.au`, every agent that writes to the site.
**Failure mode:** **Advisory only.** The runner always reports; it never blocks a release. The operator decides what to ship.
**Last updated:** 2026-04-23.

---

## 1. What this doc is for

`GUIDELINES.md` §11 defines the release gate — what must be true before a page, dataset, or schema change goes live. This document is the runbook that enforces that gate in code: scripted checks, screenshot baselines, link-checker config, mobile device matrix, CI wiring, and how to run the checks locally. Every check maps back to the GUIDELINES section it enforces.

The release-check agent (`.claude/agents/release-check.md`) is the orchestrator. It runs the scripts in this doc, performs the §11.5 editorial read-through, and logs its invocation to `data/agents.log.md` per §6.2.

---

## 2. What gets tested, and why

| Check | Enforces | Script |
|---|---|---|
| Provenance schema — every datapoint has all required fields | §4.2, §4.4, §4.5 | `scripts/validate-provenance.mjs` |
| `nextReview` is not in the past | §5.5 | `scripts/validate-provenance.mjs` |
| New fields have been backfilled on existing entries | §5.2, §5.5 | `scripts/validate-provenance.mjs` |
| Controlled vocabularies resolve to labels (no raw keys in render) | §5.6 | `tests/release-check/labels.spec.ts` |
| Cross-page reconciliation — one concept, one canonical field | §5.3.1 | `tests/release-check/reconciliation.spec.ts` |
| Freshness dots coloured correctly against `retrievedAt` | §7.2 | `tests/release-check/freshness.spec.ts` |
| Page structure follows the standard order | §7.3 | `tests/release-check/structure.spec.ts` |
| Mobile rules — no horizontal scroll, 44px tap targets, hero fits two viewports at 390×844 | §7.5 | `tests/release-check/mobile.spec.ts` |
| Smoke — no console errors on Chrome / Safari / Firefox | §11.4 | `tests/release-check/smoke.spec.ts` |
| Links — every `sourceUrl` and internal link resolves | §11.4 | `tests/release-check/links.spec.ts` |
| Shareable URL params round-trip | §7.4, §11.4 | `tests/release-check/smoke.spec.ts` |
| Visual baseline — screenshot diff per page per device | §11.3 | `tests/release-check/visual.spec.ts` |
| Agent log entry written after every run | §6.2 | release-check subagent |

Editorial §11.5 (voice, banned framings, hero hook) is a human read-through performed by the release-check subagent, not a deterministic script. It is logged to the report as `advisory` notes.

---

## 3. Data source register — format and validation

The register is defined in GUIDELINES.md §4.2 (entry schema) and §5.4 (companion files). `TESTING.md` does not redefine it — it validates it.

### 3.1 Required fields per datapoint

```json
{
  "value": 17000000000,
  "label": "OpenAI booked revenue (TTM, 2025)",
  "unit": "USD",
  "year": 2025,
  "source": "OpenAI S-1",
  "sourceUrl": "https://www.sec.gov/...",
  "retrievedAt": "2026-04-18",
  "nextReview": "2026-07-18",
  "confidence": "High",
  "note": "Booked revenue, not run-rate. Trailing twelve months to Q4 2025."
}
```

Range entries substitute `minMonths` / `maxMonths` / `medianMonths` for `value` and carry a `sources` array.

### 3.2 Companion files

- `data/sources.registry.md` — every source used, with handler, cadence, licence, fetch method.
- `data/sources.log.md` — append-only log of every value update (date, operator/agent, field, prior → new, reason).
- `data/agents.log.md` — append-only log of every agent invocation, including each release-check run.
- `data/agents.registry.md` — every agent, with purpose, sources touched, output schema, cadence, owner, prompt location.
- `data/<page>/` — raw snapshots of primary documents, dated by retrieval.

### 3.3 Validator

`scripts/validate-provenance.mjs` runs against `site-data.json` and fails if:

- any entry is missing a required field from §4.2,
- any `nextReview` is in the past,
- any new field was introduced without a backfill value on existing entries (detected by schema diff against the previous committed version),
- any entry referenced by `site-data.json.meta.dataReferences` is missing its `label`,
- any confidence value is not one of `High` / `Med` / `Low`,
- any revenue entry is unlabelled as to booked vs run-rate (§4.5).

The validator is also the basis for the §5.5 build lint. Same script, same failure conditions, same exit codes. It supersedes the earlier `scripts/build-lint.js`; the `npm run build-lint` alias points here.

---

## 4. How to run

### 4.1 Local — deterministic script

```bash
npm install
npm run release-check               # full suite, advisory report to tests/reports/
npm run release-check:provenance    # just the JSON validator
npm run release-check:mobile        # just the mobile device matrix
npm run release-check:visual        # screenshot diffs only
npm run release-check:update-baselines   # accept current screenshots as new baselines
```

Exit code is always `0`. Findings are written to `tests/reports/<iso-timestamp>/report.md` and surfaced in the console summary.

### 4.2 Claude Code — subagent

```
/release-check
```

Invokes `.claude/agents/release-check.md`. The subagent runs the deterministic script, parses the report, performs the §11.5 editorial read-through against any pages modified in the working tree, and appends an entry to `data/agents.log.md`.

Use the subagent rather than the raw script when:

- a page's hero copy or methodology block was edited (editorial read-through matters),
- a spec file was updated alongside the data,
- the run will be logged to the agent ledger for a formal promotion.

Use the raw script when iterating locally on a chart or a single datapoint.

### 4.3 Report format

Reports land in `tests/reports/<iso-timestamp>/`:

```
report.md              — human-readable summary, sections mapped to GUIDELINES §11
report.json            — machine-readable findings
screenshots/           — current run screenshots
diff/                  — visual diffs against baseline (if any)
trace/                 — Playwright traces for failing checks
```

The console prints the summary and the path to `report.md`.

---

## 5. Playwright setup

`playwright.config.ts` at repo root. Six device projects covering GUIDELINES §7.5 and §11.4:

| Project | Viewport | Browser | Purpose |
|---|---|---|---|
| `desktop-chrome` | 1440×900 | Chromium | Primary laptop render (§11.4) |
| `desktop-safari` | 1440×900 | WebKit | Safari smoke (§11.4) |
| `desktop-firefox` | 1440×900 | Firefox | Firefox smoke (§11.4) |
| `tablet` | 768×1024 | Chromium (iPad UA) | §7.5 tablet breakpoint midpoint |
| `mobile-iphone` | 390×844 | WebKit (iPhone 14) | §7.5 Safari mobile bar |
| `mobile-android` | 360×800 | Chromium (Android UA) | §7.5 Android mobile bar |

Chart legibility is verified at 375px width via a dedicated test in `mobile.spec.ts`.

---

## 6. Link checker

`tests/release-check/links.spec.ts` reads `site-data.json`, extracts every `sourceUrl` and every internal nav link in the rendered DOM, and fires a `HEAD` (falling back to `GET`) at each. It fails on 4xx or 5xx; it warns on redirects to a different host.

`sourceUrl`s are checked against the live target by default. Set `RELEASE_CHECK_LINKS=offline` to skip network checks during flaky connectivity.

---

## 7. Screenshot baselines

Baselines live at `tests/__screenshots__/<project>/<spec>/<name>.png`, versioned in Git so diffs appear in PRs. Accepted tolerance: **0.2% pixel diff** per snapshot (Playwright `threshold: 0.002`).

### 7.1 When a visual change is intentional

```bash
npm run release-check:update-baselines
git add tests/__screenshots__
git commit -m "baseline: update snapshots for <page/change>"
```

The PR review must include a visual diff before the baseline update is merged. An intentional redesign requires a note in `GUIDELINES.md` §7 or the page spec.

### 7.2 Storage rationale

Baselines are in-repo because the AI Ledger is a small single-page-app and the baseline count stays bounded (pages × devices, currently tens, not hundreds). If the baseline set exceeds 500 images, move to a Git LFS setup.

---

## 8. CI wiring

`.github/workflows/release-check.yml` runs on every pull request and on push to `main`.

Behaviour:

- Install deps, install Playwright browsers, start a local static server against repo root.
- Run `npm run release-check`.
- Always post the report as a PR comment. Never fails the build.
- Uploads `tests/reports/<iso>` and `tests/__screenshots__` as artefacts.

The report comment format mirrors the local `report.md`, with failing checks called out by GUIDELINES section. Operators read the comment and decide whether to ship.

If at some future point you decide to make a specific check blocking, flip the `CHECK_MODE` env var in the workflow from `advisory` to `strict` — the runner respects it.

---

## 9. Agent log integration

Every release-check run writes an entry to `data/agents.log.md` with:

- ISO date and timestamp
- Agent name and version (`release-check@<semver>`)
- Invocation source (`local-cli`, `claude-code`, `ci-github`)
- Commit SHA at time of run
- Report path (or CI artefact URL)
- Summary line (e.g. `7 checks passed, 2 advisory findings, 0 hard failures`)

The raw CLI writes a minimal entry; the Claude Code subagent writes a richer entry including which §11.5 editorial findings it raised.

---

## 10. Appendix — check to §11 gate item mapping

| §11 item | Enforced by |
|---|---|
| §11.2 All provenance fields present | `validate-provenance.mjs` |
| §11.2 Source registered in `data/sources.registry.md` | `validate-provenance.mjs` (cross-references registry) |
| §11.2 Value changes logged in `data/sources.log.md` | `validate-provenance.mjs` (Git diff vs log) |
| §11.2 Agent runs logged in `data/agents.log.md` | release-check subagent writes its own entry |
| §11.2 No past `nextReview` dates | `validate-provenance.mjs` |
| §11.2 Confidence set honestly | Advisory — flagged in editorial pass |
| §11.2 ARR vs booked labelled | `validate-provenance.mjs` checks `revenueType` field |
| §11.2 AI-native filter consistent | Advisory — flagged if `founded >= 2023` filter disagrees |
| §11.2 Cross-page reconciliation | `reconciliation.spec.ts` against `dataReferences` |
| §11.3 No raw JSON keys | `labels.spec.ts` |
| §11.3 Labels publish-ready | `validate-provenance.mjs` + `labels.spec.ts` |
| §11.3 Freshness dots active | `freshness.spec.ts` |
| §11.3 Page structure order | `structure.spec.ts` |
| §11.3 Methodology collapsible functional | `structure.spec.ts` |
| §11.3 Mobile gate | `mobile.spec.ts` |
| §11.3 Palette unchanged | `visual.spec.ts` (screenshot diff catches any accent change) |
| §11.3 Hepburn brand treatment | `structure.spec.ts` (footer wordmark, one CTA per page) |
| §11.4 Smoke | `smoke.spec.ts` |
| §11.4 Links resolve | `links.spec.ts` |
| §11.4 URL params round-trip | `smoke.spec.ts` |
| §11.4 Build lint | `validate-provenance.mjs` (same script) |
| §11.5 Editorial read-through | release-check subagent (Claude, advisory) |
| §11.6 Rollback logged | Operator responsibility; runner does not enforce |

---

## 11. Change log

| Date | Change |
|---|---|
| 2026-04-23 | Initial runbook. Maps every §11 gate item to a scripted or advisory check. |
