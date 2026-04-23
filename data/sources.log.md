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
