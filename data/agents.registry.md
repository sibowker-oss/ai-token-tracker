# Agents Registry

**Purpose:** Every agent that writes to `site-data.json` or operates on Ledger data is registered here. Per GUIDELINES §6.3.

**Maintained by:** Simon / Hepburn Advisory
**Last updated:** 2026-04-23

---

## Columns

| Field | Meaning |
|---|---|
| `name` | Agent identifier (kebab-case) |
| `version` | Semver — bump on prompt or scope change |
| `purpose` | One sentence. What this agent does. |
| `sources` | `sources.registry.md` ids this agent reads from |
| `fieldsTouched` | JSON paths this agent may write (patch) |
| `outputSchema` | Link to schema / example patch |
| `cadence` | How often this agent runs (on-demand / daily / weekly / quarterly) |
| `owner` | Human responsible for review |
| `promptLocation` | Path to the agent's prompt / spec |
| `briefLocation` | Path to the brief in `briefs/` that authorised this agent |
| `createdOn` | ISO date |
| `status` | `active` / `paused` / `retired` |

---

## Registry

| name | version | purpose | sources | fieldsTouched | outputSchema | cadence | owner | promptLocation | briefLocation | createdOn | status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| release-check | 1.0.0 | Run the §11 release gate — Playwright suite + provenance validator + §11.5 editorial read-through. Read-only audit. | all (read-only across `site-data.json` and every rendered page) | _none — read-only; emits report only_ | `tests/reports/<iso>/report.md` + `report.json` | on-demand (local `/release-check`, PR via GitHub Actions) | Simon | `.claude/agents/release-check.md` | `briefs/active/2026-04-23-testing-runbook.md` | 2026-04-23 | active |
| stream-1-activation-monitor | 0.1.0 | Drive the Stream 1 registered-but-inert sources from `pending_first_extraction` → live via `monitor_sources.py`. Currently wired for IR pages (src-026..032), SEC EDGAR broad scan (src-025 + data/edgar-tickers.json), FLI EU AI Act (src-055), Chinese sources (src-037/038/042), and the four Chinese hyperscaler IRs (src-056..059). | src-001, src-025, src-026..032, src-037/038/042, src-055..059 | none during catalogue pass; `data-updates/<date>-candidates.json` + `data-updates/<date>-source-<id>.json` patches for downstream Accept/Decline in `claims.html` (existing flow). | per-source candidates JSON + `data/snapshots/<source-id>/<YYYY-MM-DD>/` raw artefact | on-demand (manually triggered per source via `python3 scripts/monitor_sources.py --force src-NNN`) | Simon | `scripts/monitor_sources.py` (adapters: `ir_page_extract`, `sec_edgar_scan`, `web_extract` with language='zh' hint) | `briefs/active/2026-04-23-stream-1-activation.md` | 2026-04-23 | active (no extractions triggered yet) |
| structured-claims-applier | 1.1.0 | Accept-side routing of the four wq-014 structured claim types (power_project / hiring_snapshot / patent_snapshot / company_surfaced) from `claims.html` into `site-data.json` / `companies.json`. Not a monitor — runs when Simon clicks Submit in claims.html. | any source that emits a structured claim (Streams 2/3 adapters in future; manual CLI today) | `site-data.json.power.projects[]`, `site-data.json.hiring.snapshots.<slug>.<window>`, `site-data.json.patents.snapshots.<slug>.<window>`, `companies.json.candidates[]`, `data/company-surfaced.log.json`, `data/sources.log.md` | patched `site-data.json` / `companies.json` via the existing `apply_claims.py` flow; row-per-write on `sources.log.md` | on-demand (Accept in `claims.html` → `apply_claims.py`) | Simon | `scripts/apply_claims.py` (STRUCTURED_APPLIERS dispatch) | `briefs/active/2026-04-23-structured-claim-schema.md` | 2026-04-23 | active |
| stream-2-power-monitor | 0.1.0 | Drive Stream 2 power sources from `pending_first_extraction` → live. Emits `power_project` structured claims (wq-014) per ISO queue entry. Consults `data/datacenter-attribution-map.json` for LLC / facility → AI-operator resolution. | src-060 (ERCOT), src-061 (PJM), src-062 (EIA), src-063 (NESO TEC), src-064 (Epoch AI) | `data-updates/<date>-source-<id>.json` (per-source candidates) + `data/datacenter-attribution-map.json` (map refresh) + `data/snapshots/<source-id>/<YYYY-MM-DD>/` | structured `power_project` claims → reviewed in `claims.html` → routed by `structured-claims-applier` into `site-data.json.power.projects[]` | on-demand (manual trigger: `python3 scripts/monitor_sources.py --force src-NNN`) | Simon | `scripts/monitor_sources.py` (adapters: `iso_queue_ercot`, `iso_queue_pjm`, `eia_api`, `neso_tec`, `epoch_frontier`) | `briefs/active/2026-04-23-stream-2-energy.md` | 2026-04-23 | active (attribution map seeded 2026-04-23; no queue extractions yet) |
| company-discovery | 0.1.0 | Drive Stream 3 hiring + patent discovery. Fans out to per-company ATS endpoints (Greenhouse / Lever / Ashby / Workable) and patent APIs (PatentsView, optionally BigQuery / EPO OPS). Emits `hiring_snapshot`, `patent_snapshot`, and `company_surfaced` structured claims (wq-014). Consults `data/company-alias-map.json` for entity resolution. | src-065..072 | `data-updates/<date>-source-<id>.json` (per-source candidates, one per company target) + `data/company-alias-map.json` (updated as candidates are accepted) + `data/snapshots/<source-id>-<slug>/<YYYY-MM-DD>/` | structured hiring/patent claims → `claims.html` → `structured-claims-applier` → `site-data.json.{hiring,patents}.snapshots.<slug>.<window>` | on-demand (manual trigger: `python3 scripts/monitor_sources.py --force src-NNN`; recommended cadence per wq-013 §7: weekly for ATS, monthly for patents) | Simon | `scripts/monitor_sources.py` (adapters: `greenhouse_board`, `lever_postings`, `ashby_public`, `workable_jobs`, `patentsview_search`, `google_patents_bq`, `epo_ops`, `dol_lca_xlsx`) + `scripts/ai_native_density.py` + `scripts/discovery_validation.py` | `briefs/active/2026-04-23-stream-3-hiring-patents.md` | 2026-04-23 | active (alias map seeded with 31-company validation set; no ATS or patent extractions yet) |

---

## Rules

1. Every agent that writes to `site-data.json` must be registered before its first run (§11.2).
2. Agents emit **JSON patches**, not direct writes. The patch is merged by a human (§6.2).
3. Every agent run is logged to `agents.log.md`. Any write to `site-data.json` is also logged to `sources.log.md`.
4. A prompt change bumps the patch version; a scope change (new fields, new sources) bumps the minor version; a full redesign bumps the major version.
5. An agent without a corresponding brief in `briefs/` fails the §11 gate.
