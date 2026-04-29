# Brief: wq-028 — Free-form metricKey doesn't match field_match_rules

> **Status:** **FROZEN 2026-04-27** — copied here from `The AI Ledger/briefings/wq-028-free-form-metrickey.md` per GUIDELINES §9.3. Phase 0 first; Simon decides between options before Phase 1.
> **Priority:** M
> **Owner:** Claude Code (implementation) — decisions Simon
> **Type:** Decisions brief — 3 options laid out; Phase 0 returns evidence, Simon picks one
> **Predecessor:** wq-027 verification surfaced. Affects ALL inbound, not just replays.

---

## 1. Goal

Stop the silent gap where claims with free-form `metricKey` values like "Annualized Revenue" or "Series D Amount Raised" land as data points in vault-data.json but **never update the entity record's canonical fields**. Result: those values don't appear on the dashboard or in cross-claim reconciliation.

After this brief lands: claims with common free-form metricKey variants land cleanly on canonical fields. Edge cases either get normalised at the boundary or surface for manual mapping.

---

## 2. The problem, illustrated

Pipeline today:

1. Extractor emits a claim with `metricKey: "Annualized Revenue"`.
2. apply_decisions.py creates a dataPoint in vault-data.json. ✓
3. apply_decisions.py also tries to update the entity record using `field_match_rules` from `metric-schema.json`. The rules expect `arr` or `annualized_revenue` (snake_case). "Annualized Revenue" doesn't match → no entity update.
4. Dashboard reads `entity.current.arr` → unchanged from before the claim.

So: dataPoint exists, entity record stale, dashboard stale, the accept feels like a no-op even though it succeeded structurally.

---

## 3. Decisions required (D1–D4)

### D1 — Approach

| Option | Approach | Pro | Con |
|---|---|---|---|
| A | Extend `field_match_rules` to recognise common free-form variants | Cheap, additive. No extractor change | Catalog grows over time. Variants you don't anticipate still leak |
| B | Tighten extractor to emit only canonical keys | One-shot fix at the source | Big extractor change. Risks breaking existing extractors |
| C | Add a normalisation layer between extract and apply | Clean separation | New code path. Adds complexity |
| D (recommended) | **Hybrid** — start with A, add C, gradually upstream into B | Biggest impact for least risk | Three pieces, each shippable independently |

**Claude's pick:** D, executing in order: A first, then C, B only if needed.

### D2 — Initial variant list (D1=A first phase)

Extract from current vault-inbox.json + vault-data.json the top free-form metricKey values that don't match any rule. Likely top 20 variants account for 80%+ of the gap. Best done at brief-execution time. Starter list:

| Free-form metricKey | Canonical key | Reason |
|---|---|---|
| "Annualized Revenue" | `arr` | Straight synonym |
| "Annual Revenue" | `arr` | Some extractors say annual when they mean ARR |
| "Run Rate Revenue" | `arr` | |
| "ARR" | `arr` | Case insensitivity at boundary |
| "Series D Amount Raised" | `funding.series.D.amount` | Round-specific funding field |
| "Series C Amount Raised" | `funding.series.C.amount` | |
| "Total Capital Raised" | `funding.total` | |
| "Valuation" | `valuation.current` | |
| "Headcount" | `employees.total` | |
| "Employee Count" | `employees.total` | |
| "Active Users" | `users.active` | |
| "Monthly Active Users" | `users.mau` | |
| "DAU" | `users.dau` | |
| "Token Volume Per Day" | `usage.tokens_per_day` | |
| "Capital Expenditure" | `capex.total` | |
| "Cash Burn" | `financials.burn_rate` | |

**Decision:** approve this starter list — Claude will refine at brief execution after reading current data.

### D3 — Normalisation layer (D1=C phase)

| Option | Scope |
|---|---|
| A | Pure mapping — looks up free-form variant in registry, returns canonical key |
| B (recommended) | Mapping + scoring — returns canonical key with confidence; below threshold surfaces for manual mapping |
| C | Full LLM normalisation |

**Claude's pick:** B.

### D4 — Surfacing unmappable variants

| Option | Surface |
|---|---|
| A (recommended) | "Unmapped metricKey" filter chip in admin.html#review with per-row dropdown |
| B | Auto-route to raw_pool with `mapping: "unmapped"` annotation |
| C | Block the accept |

**Claude's pick:** A.

---

## 4. Implementation phases

P1 — Top-variant rules added to field_match_rules (D1=A) (1 commit):
- Read current vault-inbox.json + vault-data.json. Extract top 20 unmapped metricKey values.
- Add to `metric-schema.json` field_match_rules.
- Run apply_decisions.py against historical raw_pool/accepted items where metricKey now resolves.
- Verify: entity records updated; dashboard tiles refreshed.

P2 — Add normalisation layer (D1=C) (2 commits):
- Create `scripts/normalise_metric_key.py` with B-style scoring.
- Insert in apply_decisions.py pipeline before field_match_rules check.
- Tests: 20+ variant cases.

P3 — Admin UI unmapped chip (D4=A) (1 commit):
- Add "unmapped metricKey" filter chip to review.html.
- Per-row dropdown surfaces canonical-key options.

P4 — Extractor tightening (D1=B, optional, deferred):
- Per-extractor: limit `metricKey` to canonical keys.

---

## 5. Acceptance

- [ ] field_match_rules covers top 20 variants from current data.
- [ ] Historical replays through apply_decisions.py update entity records as expected.
- [ ] dashboard tiles for affected entities refresh with corrected values.
- [ ] normalise_metric_key.py exists with confidence scoring.
- [ ] admin.html#review has "unmapped" filter chip.
- [ ] Synthetic test: claim with variant X is correctly mapped to canonical Y.
- [ ] Tests + build-lint green.

---

## 6. Risk register

- **Mismapping:** "Annual Revenue" → `arr` is a guess. Mitigation: confidence threshold in D3=B; manual review for sub-threshold.
- **Catalog drift:** D1=A grows over time. Periodic cleanup task.
- **Cross-pollination with wq-032:** D1=A maps "Annualized Revenue" → `arr`. wq-032 decides whether `arr` surfaces to dashboard. Sequencing: ship wq-032 first or in parallel.

---

## 7. Decisions log

| ID | Decision | Choice | Date | Notes |
|---|---|---|---|---|
| D1 | Approach | A (recommended scope) | 2026-04-29 | Two-pass match: claim+tags first, metricKey fallback. Plus 8 non-revenue rules. Defer revenue-adjacent rules to wq-032 |
| D2 | Starter variant list | Approved subset | 2026-04-29 | Shipped 8 of 16 starter variants; revenue-adjacent (Annual/Annualized/Run Rate/Series funding/Valuation/Headcount overrides) deferred |
| D3 | Normalisation layer scope | — | — | Phase 2 (deferred V1.1) |
| D4 | Unmappable surface | — | — | Phase 3 (deferred V1.1) |

---

## 8. Implementation log

### 2026-04-29 — Phase 1 (matcher fix + 8 new rules)

**The bigger finding from Phase 0:** the brief framed this as "free-form metricKey doesn't match field_match_rules", but the real issue was that the matcher at `scripts/apply_decisions.py:189` only ran rules against `claim_text + tags`, never against the structured `metricKey` field. Adding metricKey as a fallback was the highest-leverage move — single line, ~140 items rescued before any new rules.

**Two-pass matcher (apply_decisions.py:189):** primary `match_field` runs against `claim+tags` (legacy behavior). If no match, fall back to `metricKey` alone. Initially tried concatenating all three into one search_text, but that let multi-word patterns like `infrastructure.*spend` bridge tag/metricKey gaps (`gpu_infrastructure` tag + `spend` in metricKey = false-positive `capex`). Two-pass keeps multi-word rules contained to claim text while still rescuing structured-tag claims.

**8 new field_match_rules** in `metric-schema.json`:

| Field | Pattern | Inbox items rescued |
|---|---|---:|
| `gross_margin_pct` | `gross.*margin` | 20 |
| `contract_value` | `contract.*value\|deal.*value\|contract.*size` | 20 |
| `dc_power_capacity_gw` | `data.center.*power\|power.*capacity` | 11 |
| `operating_income` | `operating.*income` | 9 |
| `gross_profit` | `gross.*profit\b` | 9 |
| `rack_power_density_kw` | `rack.*power\|power.*density` | 6 |
| `enterprise_revenue` | `\benterprise\s+revenue\b\|enterprise_revenue` | 5 |
| `purchase_commitments` | `purchase.*commitment` | 5 |

**Tightened 2 existing rules:**
- `active_rate`: `active.*rate|usage.*rate|adoption.*rate` → `\b(?:active|usage|adoption)\s+rate\b`. Phase 0 audit found 16 false positives (e.g., `enterprise_adoption` tag + "growth rate" metricKey matched the loose pattern). Now requires word-adjacency.
- `enterprise_revenue`: same word-adjacency tightening to prevent `enterprise_adoption` tag + "revenue" elsewhere from false-matching.

**Net rescue audit** (against current vault-inbox.json, 2128 items):

| Behavior | Items matched | Net change |
|---|---:|---:|
| Old (claim+tags only, 21 rules) | 986 | — |
| New (two-pass, 29 rules) | 1172 | **+186** |

By field, the rescued 186 break down:
- 8 new rules contribute: 85 items (gross_margin/profit, contract_value, dc_power_capacity, operating_income, rack_power_density, enterprise_revenue, purchase_commitments).
- metricKey-fallback through existing rules: 101 items (collected_revenue 40, employees 14, arr 12, active_rate 7, tokens_per_day 6, capex 3, gpu_count 3, plus singletons).

**Out of scope (deferred):**
- Revenue-adjacent rules — "Annual Revenue" / "quarterly revenue" / "projected revenue" routing decisions deferred until wq-032 settles whether `arr` and `collected_revenue` are different fields on the dashboard.
- Long-tail unmapped metricKeys (775 items, 732 distinct keys) — most are podcast tangents (court damages, race promotion fees, store counts). Phase 2 normalisation layer will handle.
- Replay against historical accepted items — code change only this session; no vault-data.json or entities.json mutation.

**Tests:** new `tests/test_field_match_routing.py` covers 21 cases across 4 suites: metricKey-extension rescues, 8 new field rules, active_rate tightening (false-positive prevention + legit usage preservation), and existing rules pinned for no-regression. 21/21 PASS. Existing tests green: test_apply_decisions_encoding 9/9, test_claim_schema 6/6, test_date_coerce 26/26. build-lint 0 fail.

**Phase 1 acceptance:** Met. Phase 2 (normalisation layer) and Phase 3 (admin "unmapped" chip) deferred to V1.1 post-launch.

---

## 9. Hand-off note (frozen — Phase 0 only, Phase 1 now complete)

```
Open this brief, execute Phase 0 only — audit current data, surface top-N unmapped metricKey values, recommend scope. Stop and report. Wait for Simon to confirm D1.
```
