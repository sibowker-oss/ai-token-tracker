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

---

## Rules

1. Every agent that writes to `site-data.json` must be registered before its first run (§11.2).
2. Agents emit **JSON patches**, not direct writes. The patch is merged by a human (§6.2).
3. Every agent run is logged to `agents.log.md`. Any write to `site-data.json` is also logged to `sources.log.md`.
4. A prompt change bumps the patch version; a scope change (new fields, new sources) bumps the minor version; a full redesign bumps the major version.
5. An agent without a corresponding brief in `briefs/` fails the §11 gate.
