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

---

## Rules

1. Every agent that writes to `site-data.json` must be registered before its first run (§11.2).
2. Agents emit **JSON patches**, not direct writes. The patch is merged by a human (§6.2).
3. Every agent run is logged to `agents.log.md`. Any write to `site-data.json` is also logged to `sources.log.md`.
4. A prompt change bumps the patch version; a scope change (new fields, new sources) bumps the minor version; a full redesign bumps the major version.
5. An agent without a corresponding brief in `briefs/` fails the §11 gate.
