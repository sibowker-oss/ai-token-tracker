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
| _No entries yet._ First entries will land when `globalBenchmarks` is populated for the Trillion/Denominator Ledger. | | | | | | | | |
