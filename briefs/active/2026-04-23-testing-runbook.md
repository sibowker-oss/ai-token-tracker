# Brief — `TESTING.md` + `release-check` agent

**Status:** Frozen contract. Implementation landed 2026-04-23.
**Date handed off:** 2026-04-23
**Governed by:** `GUIDELINES.md` §4, §5, §6, §7.5, §11.
**Mechanics live in:** `TESTING.md` (repo root).
**Agent lives at:** `.claude/agents/release-check.md`.
**Thinking version:** `The AI Ledger/testing-brief.md` (remains editable for V2).

---

## 1. Interview decisions

| Question | Decision |
|---|---|
| Agent scope | Scripted checks, screenshot baselines, link-checker config, mobile device matrix, CI wiring, local-run instructions. Functional/visual + link + responsive + CI + local. |
| Runtime | Claude Code subagent orchestrating Playwright scripts. Local-first via `/release-check`; CI as backstop (to be decided post-draft). |
| Failure mode | **Advisory only.** Agent always reports, never blocks. Operator decides. |
| `TESTING.md` scope | What gets tested & why · how to run the agent · data source register format. Not a release checklist (that's §11). |
| Tooling | **Playwright** — covers headless browser, screenshot baselines, device emulation, console capture in one toolchain. |
| Source register | Already specified in GUIDELINES.md §4.2 (schema) + §5.4 (`data/sources.registry.md`, `data/sources.log.md`, `data/agents.log.md`, `data/agents.registry.md`, `data/<page>/` snapshots). `TESTING.md` documents the validation rules, not a new schema. |
| Artefact storage | Baselines in-repo under `tests/__screenshots__/` versioned with code; diffs visible in PRs. Report output to `tests/reports/<iso-date>/` (gitignored). |
| Device matrix | Per GUIDELINES §7.5: **iPhone 14/15 Safari 390×844** · **Android Chrome 360×800**. Plus **Desktop 1440×900** · **iPad 768×1024** as breakpoint midpoints. Browsers for smoke: Chrome, Safari, Firefox (§11.4). |
| Agent form | `.claude/agents/release-check.md` — Claude Code subagent. Runs Playwright scripts, reads `site-data.json`, validates provenance, emits pass/fail report, logs to `data/agents.log.md` per §6.2. |

---

## 2. `TESTING.md` — proposed structure

1. **Purpose** — one paragraph, point to §11 as the governance bar, this doc as the runbook.
2. **What gets tested and why** — each check mapped to the GUIDELINES section it enforces:
   - Provenance schema (§4.2) → JSON validator
   - `nextReview` in past (§5.5) → date check
   - Labels present, no raw keys (§5.6) → DOM scan for known key patterns
   - Cross-page reconciliation (§5.3.1) → `dataReferences` audit
   - Freshness dots coloured correctly (§7.2) → DOM + date math check
   - Page structure order (§7.3) → DOM section-order check
   - Mobile rules (§7.5) — no horizontal scroll, 44px tap targets, chart legibility at 375px, hero fits two viewports at 390×844
   - Smoke test (§11.4) — no console errors, links resolve, URL params round-trip
3. **Data source register — format & validation** — reference §4.2 table, show a validator invocation, link to the JSON schema file.
4. **How to run**
   - Local: `npm run release-check` (deterministic script)
   - Claude Code: `/release-check` (subagent — adds editorial §11.5 read-through)
   - Output location and how to read the report
5. **Playwright setup** — project config excerpt showing the four device projects.
6. **Link checker** — config targeting every `sourceUrl` in `site-data.json` + internal nav links.
7. **Screenshot baselines** — where they live, how to update, review workflow on intentional visual change.
8. **CI wiring** — GitHub Action that runs the deterministic script on PR (advisory comment, not blocking).
9. **Appendix — mapping to GUIDELINES §11** — table showing each §11.2/§11.3/§11.4 item → check that enforces it.

---

## 3. `release-check` agent — proposed shape

Location: `.claude/agents/release-check.md` (Claude Code subagent).

Responsibilities:
- Run the deterministic Playwright + JSON validator suite.
- Parse the report, summarise pass/fail by GUIDELINES section.
- Perform the editorial §11.5 read-through against §2 voice rules.
- Log the invocation to `data/agents.log.md` with: date, agent version, commit SHA, sections checked, findings count, report path.
- Register itself in `data/agents.registry.md` per §6.3 on first use.
- **Never writes to `site-data.json`.** Read-only per §6.2 spirit (this agent audits, doesn't collect).
- Advisory output only — exit code always 0; findings are informational.

---

## 4. Resolved items (closed during install)

- Inspected repo file layout: no pre-existing `package.json`, no `tests/`, no Playwright. Nine existing GitHub Actions workflows for data pipelines.
- Deployment target confirmed: `ai-index.hepburnadvisory.com.au` (CNAME) via GitHub Pages — static HTML served from repo root. `package.json` scripts reflect this (`preview` uses `http-server`, no build step).
- CI host: GitHub Actions (consistent with existing workflows).
- `site-data.json` structure: could not fully verify field names (`globalBenchmarks`, `dataReferences`, `sankey.*`) during install — mount deadlock. Deferred to first `npm run release-check` run; validator is advisory so this is safe.
- Relationship to existing `scripts/build-lint.js`: superseded. `npm run build-lint` aliases to the new `validate-provenance.mjs`. Old file kept in place with a deprecation note in `scripts/README-build-lint.md`.

---

## Implementation log

| Date | Status / change | Notes |
|---|---|---|
| 2026-04-23 | Brief frozen and installed | Pack drafted in `The AI Ledger/release-check-pack/` and copied to repo. `package.json`, `TESTING.md`, `playwright.config.ts`, `scripts/release-check.mjs`, `scripts/validate-provenance.mjs`, `tests/release-check/*`, `.claude/agents/release-check.md`, `.github/workflows/release-check.yml` all created. |
| 2026-04-23 | Agent registered | `release-check@1.0.0` added to `data/agents.registry.md` per §6.3. |
| 2026-04-23 | `build-lint.js` deprecated | `scripts/README-build-lint.md` updated to point to `validate-provenance.mjs`. Old file retained for reference until a follow-up commit removes it. |

### Known open items (not blockers for advisory mode)

These are expected to surface as advisory findings on the first CI run. They are tracked by the brief, not by the runner:

1. **DOM `data-*` attributes not yet present** on existing pages (`data-section`, `data-freshness-dot`, `data-canonical-ref`, `data-hepburn-wordmark`, etc.). Pack README documents this. Structure/freshness/mobile/reconciliation specs will fail loudly until the attributes ship. Ship them as part of whichever page PR next touches the affected pages — cheap, stable selectors.
2. **`site-data.json` shape alignment.** The validator expects a `meta.dataReferences` map and the `[Noun] Ledger` v2 structure with provenance-bearing datapoints. Current `site-data.json` predates this. First run will enumerate the gaps; they get closed one page at a time, logged in `data/sources.log.md`.
3. **First promotion test.** Once the Trillion/Claim Ledger page is ready for promotion from In-Dev, run `/release-check` and treat the report as the §11 gate artefact. Archive the report alongside the promotion commit.

### Promotion readiness

Runner is live in advisory mode. Operator discretion on how strictly to gate promotions until the site-wide `data-*` attribute rollout lands.
