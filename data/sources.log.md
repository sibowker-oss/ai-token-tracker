# Sources Log

**Purpose:** Append-only log of every value update, source change, or provenance event on The AI Ledger. Per GUIDELINES §4.7 and §5.4, no value changes silently.

**Rules:**
- Append-only. Never edit or delete past entries.
- One row per value change or source event.
- If a change affects multiple fields, one row per field.
- Agent-driven updates: the agent name/version goes in `operator`; a human reviewer must still sign off before merge (§6.2).

---

## Columns

| Field | Meaning |
|---|---|
| `date` | ISO date (YYYY-MM-DD) of the change |
| `field` | Dotted path into `site-data.json` (e.g. `globalBenchmarks.entries[global_gdp].value`) |
| `priorValue` | Value before the change — `null` if new entry |
| `newValue` | Value after the change |
| `reason` | Why the change was made (new filing, quarterly refresh, correction, etc.) |
| `sourceId` | `id` from `sources.registry.md` |
| `operator` | Human name, or `agent:<name>@<version>` |
| `reviewer` | Human who approved the merge (required for agent changes) |
| `commit` | Git commit SHA after merge |

---

## Log

| date | field | priorValue | newValue | reason | sourceId | operator | reviewer | commit |
|---|---|---|---|---|---|---|---|---|
| 2026-04-23 | `power.projects` | (absent) | `[]` | Pre-seed for wq-014 structured claim target; non-destructive bootstrap so front-end can assume key exists. | _(n/a — schema bootstrap)_ | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `hiring.snapshots` | (absent) | `{}` | Pre-seed for wq-014 structured claim target. | _(n/a — schema bootstrap)_ | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `patents.snapshots` | (absent) | `{}` | Pre-seed for wq-014 structured claim target. | _(n/a — schema bootstrap)_ | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-017].status` | `pending_first_extraction` | `deprecated_duplicate` | Duplicate of src-016 (openai.com/index/accelerating-the-next-phase-ai/). Per wq-015 §3.1. | src-017 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-018].status` | `pending_first_extraction` | `deprecated_duplicate` | Duplicate of src-016. Per wq-015 §3.1. | src-018 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-019].status` | `pending_first_extraction` | `deprecated_duplicate` | Duplicate of src-016. Per wq-015 §3.1. | src-019 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-020].status` | `active` | `deprecated_duplicate` | Duplicate of src-016. Per wq-015 §3.1. | src-020 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-021].status` | `active` | `deprecated_duplicate` | Duplicate of src-016. Per wq-015 §3.1. | src-021 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-022].status` | `active` | `deprecated_duplicate` | Duplicate of src-016. Per wq-015 §3.1. | src-022 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-025].url` | `...company=openai&CIK=...` | `...company=&CIK=...` (broadened) | Scope broadened from OpenAI-only to multi-ticker scan driven by `data/edgar-tickers.json`. Per wq-015 §2.2. | src-025 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-024].status` | `pending_first_extraction` | `deferred` | Seeking Alpha deferred per wq-015 §2.6 — paywall. | src-024 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-050].status` | `pending_first_extraction` | `deferred` | Crunchbase deferred per wq-015 §9 — paid source, budget review. | src-050 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-051].status` | `pending_first_extraction` | `deferred` | Dealroom deferred per wq-015 §9 — paid source, budget review. | src-051 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-055]` | null | FLI EU AI Act Tracker (pending_first_extraction) | New source per wq-015 §2.3. Set `status=pending_first_extraction` and `next_check=2026-05-23` so daily cron does not auto-fire. | src-055 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-056]` | null | Alibaba Group IR (pending_first_extraction) | New Chinese hyperscaler IR per wq-015 §2.4. | src-056 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-057]` | null | Tencent Holdings IR (pending_first_extraction) | New Chinese hyperscaler IR per wq-015 §2.4. | src-057 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-058]` | null | Baidu IR (pending_first_extraction) | New Chinese hyperscaler IR per wq-015 §2.4. | src-058 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `sources-registry.json[src-059]` | null | ByteDance press room (pending_first_extraction) | New; ByteDance private so IR is substituted with corporate newsroom. Per wq-015 §2.4. | src-059 | Simon | Simon | _(this commit)_ |
| 2026-04-23 | `data/edgar-tickers.json` | (absent) | 16 seed tickers | New ticker-seed file for the broadened SEC EDGAR scan. Per wq-015 §2.2 and Phase 1 decision #9. | n/a | Simon | Simon | _(this commit)_ |
