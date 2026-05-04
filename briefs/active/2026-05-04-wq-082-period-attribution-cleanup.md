# Brief: wq-082 — period-attribution claim cleanup (entities.json migration residue from wq-054)

> **Handoff metadata (per GUIDELINES §9.3)**
> - **Handoff date:** 2026-05-04
> - **Work queue:** wq-082
> - **Parent:** wq-054 (period-attribution rules introduction)
> - **Discovered during:** wq-081 Phase 1.1 source collation, in CI build-lint strict-mode `Release check (§11 orchestrator)` step
> - This repo copy is the contract. Append an Implementation log below when starting work.

**Status:** Scoped
**Budget:** $0 — script work + per-claim editorial decisions, no external calls

---

## 1. Goal

Resolve the **117 flagged claims** in `data/wq-054-existing-misroutes.md` so the strict-mode `validate-period-attribution.mjs` runs clean and `build-lint.yml` goes green on `main`.

These are claims whose text contains a sub-period qualifier (`H1`, `Q3`, `exit_snapshot`, `monthly_peak`, etc.) but were written into a field path implying a different scope (usually `annual`). When wq-054 introduced the period-attribution rules, the audit identified these as pre-existing misroutes and explicitly **did not auto-move** them — the call was that each one needs an editorial decision (retire / move to sub-period field / annotate as ambiguous).

Those decisions never happened. The pile has rolled forward unfixed, and `build-lint.yml` strict mode now fails on every PR for reasons unrelated to the PR. The wq-081 Phase 1.1 PR (#1) was merged anyway because the failures pre-date wq-081 and `entities.json` is untouched in that branch — but that escape hatch only works as long as no PR changes `entities.json`.

## 2. Scope

The 117 claims, per `data/wq-054-existing-misroutes.md`:

| Entity | Flagged claims |
|---|---|
| `openai` | 41 |
| `anthropic` | 20 |
| `google` | 10 |
| `meta` | 9 |
| `mistral` | 9 |
| `xai` | 8 |
| `deepseek` | 7 |
| `minimax` | 6 |
| `moonshot` | 6 |
| `nvidia` | 1 |
| **Total** | **117** |

Each claim falls into one of three classes:
- **(a) Genuine sub-period claim attached to the wrong field** — the value belongs in (e.g.) `openai.Q1 2024.arr`, not `openai.2024.arr`. Move to sub-period field.
- **(b) Annual claim where the sub-period qualifier in the text is contextual rather than structural** — e.g. "OpenAI grew through Q4 2024 to end the year at $X". Retire the qualifier from the claim text or annotate the claim as `period_qualifier_is_contextual: true` (schema add).
- **(c) Ambiguous** — flag for retire-and-resource.

## 3. Approach

1. Read `data/wq-054-existing-misroutes.md` row-by-row.
2. For each, classify (a)/(b)/(c) — Simon's call.
3. For (a): use `apply_decisions.py` (or a new helper) to migrate the claim to the sub-period field. Preserve provenance.
4. For (b): edit the claim text or add the schema annotation, depending on what the validator's regex actually triggers on.
5. For (c): mark the claim retired in `vault-inbox.json` historical record; remove the value from `entities.json`.
6. Re-run `validate-period-attribution.mjs` strict — must reach 0 fail.
7. Update `RELEASE_CHECK_PERIOD_ATTRIBUTION_JSON_OUT` baseline if it lives in the repo.

Do **not** disable the validator or weaken the regex. The whole point of wq-054 was to enforce this rule.

## 4. Out of scope

- Adding new claims (this is cleanup of existing).
- Changing the `validate-period-attribution.mjs` rule (out of scope; rule is correct).
- Touching the wq-081 Phase 1.1 sources (different concern).

## 5. Success criteria

- `CHECK_MODE=strict node scripts/validate-period-attribution.mjs` exits 0 on `main`.
- `build-lint.yml` strict-mode step goes green.
- `data/wq-054-existing-misroutes.md` records the disposition (a/b/c + commit SHA) for each of the 117 claims so the audit trail is reconstructable.

## 6. Implementation log

_(append rows when starting work — date, decision summary, commit SHA)_

---

*Drafted 2026-05-04 in the wq-081 Phase 1.1 ship-pause when the build-lint failure on a PR-touching-no-entities-fields surfaced the orphaned audit pile.*
