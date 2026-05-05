# CLAUDE.md — The AI Ledger (apac-ai-intel)

> Place this file at the root of the apac-ai-intel repo.

---

## Project

The AI Ledger (TAIL) — an authoritative, data-first publication on the economics of AI.  
Site: `ai-index.hepburnadvisory.com.au`  
Owner: Simon Bowker (sibowker@gmail.com)

---

## Workflow Protocol

This project uses a two-context workflow. **Cowork** (Claude Desktop) handles strategy, specs, and decisions. **Claude Code** (you) handles implementation. Communication between contexts is via files in this repo — Simon is not a relay.

### At session start, always:

1. Read the brief referenced in the handoff prompt (`docs/briefs/wq-NNN-*.md`)
2. Check `docs/decisions/resolved/` for any decisions relevant to the current work
3. Check `docs/deployments/` for recent context on what has shipped

### During implementation:

- **Tactical decisions** (library choice, naming, file structure): make the call, log it in your deployment record
- **Strategic decisions** (scope change, architecture affecting other wq-IDs, business/editorial trade-offs): write a decision file to `docs/decisions/open/` and stop that branch of work. Do NOT ask Simon to relay information to Cowork.

### Decision file format (`docs/decisions/open/dec-YYYY-MM-DD-short-name.md`):

```markdown
# Decision: [short title]

**WQ:** wq-NNN
**Date:** YYYY-MM-DD
**Context:** [1-2 sentences on what prompted this]

## Options

1. **Option A** — [description, trade-offs]
2. **Option B** — [description, trade-offs]

## Recommendation

[Your best-guess recommendation and reasoning]

## Resolution

[LEFT BLANK — resolved in Cowork]
```

### After shipping code, always write a deployment record:

File: `docs/deployments/deploy-YYYY-MM-DD-short-name.md`

```markdown
# Deployment: [short title]

**Date:** YYYY-MM-DD
**WQ:** wq-NNN
**Branch/Commit:** [ref]

## What shipped

[Concise — files changed, behaviour added/modified]

## Decisions made during implementation

[Tactical calls you made and why]

## Open items

[Bugs noticed, scope deferred, follow-ups needed]

## Acceptance criteria status

- [x] Criterion 1
- [x] Criterion 2
- [ ] Criterion 3 (deferred — reason)
```

### Notion

The work tracker lives in Notion. When you complete work:
- Update the card status if you have access
- If not, note in the deployment record that the Notion card needs updating

Card stages: Idea → Scoped → In Progress → Done

---

## Coding Conventions

### General

- Python for data pipeline scripts (`scripts/`)
- JavaScript/Node for site generation
- All data flows through: extract → inbox → review → vault → entities → site-data.json → renderer

### Data integrity

- Every claim must have provenance (source, date, confidence)
- Never overwrite vault data — append or version
- Site-data.json is generated, never hand-edited

### Testing & validation

- Validate rendered output, not just engine reports
- If the brief includes acceptance criteria, verify each one against actual rendered state
- Run the site build and check the output before declaring done

---

## File structure reference

```
docs/
├── briefs/              ← Read your brief here
├── decisions/
│   ├── open/            ← Write strategic decisions here
│   └── resolved/        ← Check for resolved decisions here
└── deployments/         ← Write deployment records here

scripts/                 ← Python pipeline (extract, enrich, score, etc.)
src/                     ← Site source
data/                    ← Vault, inbox, entities
```

---

## What NOT to do

- Don't ask Simon to copy information to Cowork — write a file
- Don't make sessions longer than necessary — one brief per session where possible
- Don't skip the deployment record — it's how Cowork knows what happened
- Don't hand-edit site-data.json
- Don't overwrite vault entries without versioning
