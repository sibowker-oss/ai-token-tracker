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
| 2026-04-24 | stream-1-activation-monitor | 0.1.0 | Phase 2 activation sweep — flipped 23 remaining pending_first_extraction sources to active via one `monitor_sources.py` pass after setting their `next_check` to today. Also deduped src-053 → src-052 (nextplatform.com Coreweave duplicate). | 23 × `sources-registry.json[src-XXX]` (status/last_checked/last_claims_count/next_check) + `sources-registry.json[src-053]` (→ deprecated_duplicate) + `vault-inbox.json` (+331 pending items across 17 sources) + 17 × `data-updates/2026-04-24-source-src-XXX.json` (per-source audit) + `data/snapshots/src-XXX/2026-04-24/` raw artefacts | Simon | _(this commit)_ | partial | 331 claims across 17 producing sources (top hitters: Sacra OpenAI 63, Sacra Anthropic 53, apoorv03 42, Sacra Cursor 33, Coreweave 30, OpenAI press 30, Sacra Perplexity 26, AMD IR 16, 36Kr 12; tail: Jiemian 6, Platformonomics/PyPI x3/NVIDIA all 4). 6 sources returned 0 claims because the landing page is a JS shell (Alphabet/Microsoft/Salesforce/ServiceNow IR, a16z essay index, Stanford AI Index, CAC, europarl AI Act page). 2 sources fetched 404 (Sequoia articles URL rot, SimilarWeb taxonomy removed). Follow-ups: ir_page_extract v2 PDF-link follow; replace src-040 Sequoia URL; deprecate or replace src-046 SimilarWeb; deep-link child paths for src-042 CAC and src-043 Stanford AI Index; depth-1 link-follow for src-039 a16z. |
| 2026-04-26 | structured-claims-applier | 1.1.0 | wq-021 P1 — added defensive `safe_str()` guard to `scripts/apply_decisions.py` to clean single-pass U+00E2 + U+0080 mojibake on the way INTO `vault-data.json`. Also pinned `load_json` / `save_json` to `encoding="utf-8"`. Root cause is upstream (hosted-admin JS write path at commit 249cffe), not apply_decisions itself — see brief Implementation log §0. | `scripts/apply_decisions.py` (safe_str helper + load/save encoding=utf-8 + safe_str applied to dataPoint claim/sourceAuthor/notes + provenance.claims source/claim) + `tests/test_apply_decisions_encoding.py` (new, 9 cases) | Simon | _(this commit)_ | merged | wq-021 §4. Test file passes 9/9 (clean passthrough, mojibake cleanup, partial-marker no-op, undecodable safe-fallback, end-to-end apply_accepted contract, save/load round-trip). Build-lint 0 failures. Phase 2 (one-shot vault-data + archive cleanup) and Phase 3 (synthetic accept verify) follow in subsequent commits per Mac git hang quirk. Follow-ups: vault-inbox.json itself still has 392 markers (out of brief scope); upstream JS write path in github-api.js / review.html may still re-introduce mojibake on every hosted-admin commit. |
