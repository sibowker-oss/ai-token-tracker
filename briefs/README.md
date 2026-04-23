# Briefs

Implementation-ready specs for The AI Ledger, copied here from `The AI Ledger/` (Claude project) at the point of handoff to implementation.

## Why this folder exists

The AI Ledger project folder is where briefs are drafted and discussed. This folder is where they live once they are the contract for code changes. The purpose is traceability: every page, schema change, or agent in the repo should map back to a brief in this folder, so future-us can answer "why was this built?"

## Structure

```
briefs/
├── README.md              # this file
├── active/                # briefs currently being implemented
├── completed/             # briefs whose scope has shipped
└── archive/               # briefs abandoned or superseded
```

## Filename convention

`YYYY-MM-DD-short-name.md` — the date is the date the brief was handed off (moved into `active/`), not the date drafting began.

Examples:
- `2026-04-22-power-ledger.md`
- `2026-04-22-follow-the-trillion.md`
- `2026-04-23-testing-runbook.md`

## Handoff process

1. **Draft & discuss** in `The AI Ledger/` (Claude project folder). Iterate freely. Nothing here is binding.
2. **Freeze** the brief when it is implementation-ready — it conforms to GUIDELINES.md §9 spec structure (purpose, data audit, schema extension, source tracking, phases, open questions).
3. **Copy** (do not move) the frozen brief into `briefs/active/` with the filename convention above. The AI Ledger copy remains as the editable thinking version; the repo copy is the immutable contract for implementation.
4. **Implement** against the brief. If scope changes materially during implementation, update the brief in-place in `active/` with a change-log entry at the bottom.
5. **Complete** — when the brief's scope has shipped and passed the §11 release gate, move the file from `active/` to `completed/` and append a one-line "Shipped: <date>, commit <sha>" footer.
6. **Archive** — if a brief is abandoned or superseded, move to `archive/` with a one-line note explaining why.

## Relationship to `The AI Ledger/`

- `The AI Ledger/` = thinking layer. Living drafts, discussions, exploratory specs. Editable.
- `briefs/` = contract layer. Frozen specs tied to code commits. Append-only edits with change-log.

A brief that has shipped is the authoritative record of what was agreed. The Ledger draft may continue to evolve for a V2; that is fine — it will become its own dated brief when it is next handed off.

## Agents

Agent specs follow the same flow. Per GUIDELINES §6.3, every agent is also registered in `data/agents.registry.md` — the brief explains the *why*; the registry tracks the *what is running now*.
