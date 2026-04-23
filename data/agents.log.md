# Agents Log

**Purpose:** Append-only record of every agent invocation. Per GUIDELINES §6.2.

**Rules:**
- Append-only. Never edit or delete past entries.
- One row per agent invocation (one run = one row, even if multiple fields patched).
- Corresponding field-level changes are also logged in `sources.log.md` — this file records the *invocation*, that file records the *data change*.

---

## Columns

| Field | Meaning |
|---|---|
| `date` | ISO date (YYYY-MM-DD) of invocation |
| `agent` | Agent `name` from `agents.registry.md` |
| `version` | Agent version at time of run |
| `promptSummary` | One-line summary of the prompt/task |
| `fieldsTouched` | JSON paths actually patched this run |
| `reviewer` | Human who approved the merge |
| `commit` | Git commit SHA after merge |
| `outcome` | `merged` / `rejected` / `partial` / `error` |
| `notes` | Anomalies, follow-ups, caveats |

---

## Log

| date | agent | version | promptSummary | fieldsTouched | reviewer | commit | outcome | notes |
|---|---|---|---|---|---|---|---|---|
| 2026-04-23 | structured-claims-applier | 1.1.0 | Phase 1 fixture integration test against a tempdir sandbox — four accepted claims (one per type) + idempotency re-run. | `site.power.projects[0]`, `site.hiring.snapshots.anthropic.2026-W17`, `site.patents.snapshots.anthropic.2026-04`, `companies.candidates[Moonshot AI]` (sandbox only; real files untouched) | Simon | ed833e1 | merged | Sandbox-only test; no mutation to real `site-data.json` / `companies.json`. Validated provenance flattening, confidence capitalisation, idempotent upsert, `sources.log.md` rows, and `company_surfaced` dedup. |
| 2026-04-23 | stream-1-activation-monitor | 0.1.0 | Registered per wq-015 §7.8. No extractions invoked; adapters ready behind manual trigger. | _(none — registration only)_ | Simon | _(this commit)_ | configured | First real invocation will land when Simon runs `python3 scripts/monitor_sources.py --force src-NNN`. Priority order documented in the wq-015 brief implementation log. |
| 2026-04-23 | stream-1-activation-monitor | 0.1.0 | First extraction: State of AI Report 2025 (src-001) via `extract_google_slides` + chunked Claude calls. | `data-updates/2026-04-23-source-src-001.json` (217 claims, not auto-loaded), `sources-registry.json[src-001]` → status=active, last_claims_count=217 | Simon | _(this commit)_ | partial | 12 chunks; 7 succeeded (217 claims), 5 failed (JSON truncation + unicode surrogate pair issues). 7 follow-ups logged in wq-015 brief implementation log. Not merged into `<date>-candidates.json`; isolation preserved per review-budget posture. |
