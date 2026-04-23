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
| _No invocations yet._ | | | | | | | | |
