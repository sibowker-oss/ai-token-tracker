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
| 2026-04-23 | stream-2-power-monitor | 0.1.0 | First attribution-map seed from Epoch AI Frontier Data Centers CSV (src-064). Fetched via stdlib; parsed 36 rows. | `data/datacenter-attribution-map.json` (by_project seeded, by_llc empty), `data/snapshots/src-064/2026-04-23/data_centers.csv` | Simon | 3fb80d1 | merged | Confidence distribution preserved from Epoch (29 confident / 1 likely / 1 speculative / 5 unset for owners; 15 / 11 / 5 / 5 for operators). Two multi-operator projects parsed correctly (Microsoft Fairwater, Fluidstack Lake Mariner). |
| 2026-04-23 | stream-2-power-monitor | 0.1.0 | Registered per wq-012 §7. Five adapters wired (ercot / pjm / eia / neso / epoch). | _(none — registration only)_ | Simon | _(this commit)_ | configured | ERCOT and PJM need openpyxl to do row-level XLSX parse — v1 stubs surface the download URLs and save landing-page snapshots. EIA needs EIA_API_KEY env var. NESO is fully functional (CSV + stdlib). Simon fires per-source via `--force`. |
| 2026-04-23 | company-discovery | 0.1.0 | Seeded data/company-alias-map.json with 31-company validation set (wq-013 §6). patent_assignee_ids empty; 22/31 ATS tokens known. | `data/company-alias-map.json` (new file; 31 entries) | Simon | 0c14e79 | merged | Ran scripts/discovery_validation.py to verify coverage: 31/31 surfaced by ≥1 signal (all have lca_names); 0 recall gaps. |
| 2026-04-23 | company-discovery | 0.1.0 | Registered per wq-013 §12.7. Eight adapters wired (greenhouse / lever / ashby / workable / patentsview_search / google_patents_bq / epo_ops / dol_lca_xlsx). | _(none — registration only)_ | Simon | _(this commit)_ | configured | ATS adapters fully functional (public JSON, no auth). PatentsView needs assignee_ids populated. BigQuery stubbed pending GCP creds. EPO OPS env-gated. DoL LCA needs openpyxl. Simon fires per-source via `--force`; AI-engineer regex from §9 classifies roles. |
