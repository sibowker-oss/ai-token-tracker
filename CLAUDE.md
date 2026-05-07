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

## Publishing Gate — Live Site (HARD STOP)

The live public site is **`ai-index.hepburnadvisory.com.au`**. Any change that becomes visible to the public there — new pages, page edits, navigation changes, copy edits, data refreshes that surface on rendered pages, or any action that promotes content from staging/preview to production — is gated by Simon's explicit approval.

This rule is non-negotiable. It applies regardless of how small, confident, or reversible the change appears. It applies even if the brief says "ship it when done" — the brief authorises the **work**, not the **publish step**.

### Required sequence before anything reaches the live site

1. **Build to staging/preview first.** Deploy the change to a preview URL (Vercel/Netlify preview, branch deploy, or local + tunnelled staging). Never run a production publish/deploy command first.
2. **Share the staging URL in chat.** State exactly what changed, which pages to check, and what to verify.
3. **Wait for explicit approval from Simon.** A clear affirmative in chat is required (e.g. "approved", "ship it", "promote", "go live"). Silence is not approval. "Looks good" on something else is not approval. An approval given in a previous session does not carry forward.
4. **Only then run the production publish.** Log the approval timestamp in the deployment record.

### If the staging-first sequence is impossible

If the only way to render the change is in production (e.g. infra change with no preview path), STOP. Write a `docs/decisions/open/dec-YYYY-MM-DD-publish-gate-exception.md` describing why staging is not feasible and what mitigations are proposed. Do not improvise around the gate.

### Why this rule exists

Two separate incidents up to 2026-05-06 saw draft pages reach the live site without approval. Both required corrective work. A 5-minute approval round-trip is cheaper than unwinding a bad publish.

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

### Cross-Ledger Reconciliation (added 2026-05-06 per wq-089/wq-090 review)

Before defining or changing any aggregate that gets published on the site (totals on Capital, Revenue, Compute, Usage, Power Ledgers; any hero-strip number; any layer-stack figure), check whether another Ledger or page already publishes a number describing overlapping reality. If so, the brief's `§11 Reconciliation` section must:

1. Name the matching figure and where it lives.
2. State the expected relationship (equal / subset / superset / disjoint).
3. Provide the bridge math — explicit numerical reconciliation, or a documented reason the gap exists (cohort scoping, ecosystem vs measured, time basis).

If a new aggregate contradicts an existing higher-tier published number with no bridge, the new aggregate is blocked from shipping. Tier of the new number is capped at one below the conflicting existing number until reconciled. Do not silently re-tune to hit a target — write a `docs/decisions/open/` decision file and stop that branch.

This rule exists because the Compute Ledger and Revenue Ledger shipped in late April / early May 2026 with materially different views of the same hyperscaler-AI flow (Compute pass-through ~$11.5B vs Revenue Hyperscalers channel ~$3.6B for what is essentially overlapping economic reality). The Cowork review session 2026-05-06 caught the gap; wq-089 and wq-090 fix it; this rule prevents recurrence.

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

- **Never publish to the live site without Simon's explicit approval** (see Publishing Gate above). No production deploys, no Webflow publish, no `main` push if `main` auto-deploys, no rendering action that surfaces unseen pages on `ai-index.hepburnadvisory.com.au`.
- Don't ask Simon to copy information to Cowork — write a file
- Don't make sessions longer than necessary — one brief per session where possible
- Don't skip the deployment record — it's how Cowork knows what happened
- Don't hand-edit site-data.json
- Don't overwrite vault entries without versioning
