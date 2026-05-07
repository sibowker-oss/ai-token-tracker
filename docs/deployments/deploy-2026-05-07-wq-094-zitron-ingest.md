# Deployment: wq-094 Zitron 2026-05-06 ingest — single-pass data update

**Date:** 2026-05-07
**WQ:** wq-094
**Branch/Commit:** main / 43d0514
**Author:** Cowork (data write only — no HTML / build / publish)

## What shipped

Data-layer changes only. No HTML edited; no site build run; no publish. The Publishing Gate is intact — VS Code Claude Code session must build, stage, and obtain Simon's explicit approval before production publish.

### Files written

| File | Change |
|---|---|
| `scripts/migrate_wq094.py` | NEW — idempotent migration script that applied all changes |
| `data/compute_disclosures.json` | Extended: `_schema.tiers` adds 1B-leaked tier; new top-level `forward_commitments` block; `msft_ai.openai_inference_quarterly` block; `msft_ai.copilot_excluded_basis_note` |
| `entities.json` | `meta.lastUpdated` bumped; refreshes + extensions across microsoft-copilot, github-copilot, anthropic, openai, meta, aws, azure, gcp, coreweave, market_aggregates |
| `data/depreciation.json` | NEW — Q1 2026 hyperscaler depreciation + WSJ 2030 % net income projection |
| `data/datacenter-attribution-map.json` | Added `power_mw_energised_2026: null` to Project Rainier with bridge note |
| `assumptions-audit.md` | Replaced stale "Microsoft Copilot Q2 FY2026 ARR $13B" row with wq-094 leaked-actual restatement |

### Field-level summary (entities.json)

**M365 Copilot** (in `microsoft-copilot.products[m365-copilot]`):
- `paid_seats`: 15M → 20M (MSFT-disclosed)
- New three-band structure replacing single $5.4B published value:
  - `list_billings_2025_usd_b`: 7.2 (20M × $30 × 12)
  - `incremental_real_2025_usd_b_low/high`: 2.5–3.5 (bundling-adjusted)
  - `actual_leaked_2025_usd_b_low/high`: 1.2–1.5 (Zitron leaked Azure billing)
  - `published_2025_usd_b`: **1.35** (midpoint of leaked-actual band — PRIMARY)
  - `published_basis`: "leaked_actual_midpoint"
  - `leaked_actual_quarterly_usd_b`: Q1 cal 25 $0.367B, Q2 cal 25 $0.300B (declined Q-o-Q)
- `confidence`: Med
- Notes rewritten to explain three-band reasoning + Compute Ledger scope-out bridge

**GitHub Copilot** (in `github-copilot.current`):
- `tokens_per_day`: 1000.0 → **1.0** (editorial estimate, low confidence — replaced unsourced legacy value)
- `paid_seats`: 4.7M (MSFT Q4 FY25 earnings)
- `anthropic_customer_rank`: 2
- `compute_subsidy_relationship`: true
- `compute_subsidy_note`: subsidy reality flagged
- `june_2026_token_billing_transition`: true

**Anthropic**:
- `current.arr`: 19 → 30 (Apr 6 2026 disclosure)
- `current.arr_external_estimate`: $44B (SemiAnalysis), low confidence, with methodology note
- `financials.funding_history`: 5 rounds — Sep 2025 $13B / Feb 2026 $30B / Apr 2026 AWS $5B / Apr 2026 Google $10B / 2026-Q2 in-talks $50B
- `financials.total_raised_through_2026_04_usd_b`: 58
- `financials.2026.arr`: 18 → 30
- `financials.2026.projected_loss_2026_usd_b` / `_2027_`: 11 / 11 (Information leak)
- `compute_access_commitment_gw`: AWS up-to 5.0, Google 2026 ≥1.0, Google 2027+ "multiple"
- Notes added: GitHub Copilot concentration, projected loss provenance

**OpenAI**:
- `financials.2026.total_compute_commitment_usd_b`: 50 (NEW field — Zitron all-in commitment; basis explained)
- `financials.2026.inference_cost`: 14.1 (UNCHANGED)
- `compute_access_gw.end_2025`: 1.9 (CFO disclosure)

**Meta**:
- `financials.2026.capex`: 125 → 145
- `financials.2026.reality_labs_q1_loss_usd_b`: 4
- `financials.cumulative.reality_labs_loss_usd_b`: 86
- Notes: GEM token burn, Q2 vs Q4 2025 conversion-lift change

**AWS / Azure / GCP / CoreWeave**:
- `compute_capacity_gw.end_2025` set: AWS 1.67, Azure 2.0, GCP 2.95, CoreWeave 0.480 (all Tier 2A, Zitron-cited)
- AWS notes: 2003–2017 history control point ($52B inflation-adj, profitable in ~10 years)
- Azure: M365 Copilot subscriber_count_m=20 set on the parent product entry where present

**market_aggregates.quarterly_capex**:
- 2025Q3 MSFT $21.4B, 2025Q4 MSFT $37.5B (Tier 1A, 10-Q sourced)

### compute_disclosures.json — forward_commitments block

New top-level block. Reports forward commitments GROSS, separately from realised revenue, per Cross-Ledger Reconciliation rule. Structure:

- `lab_to_hyperscaler`: Anthropic-Google $200B/5yr (42.7% of Google Q1 26 RPO); Anthropic-Broadcom TPU $21B 2026 + $42B 2027; AWS-OpenAI $38B + $100B/8yr; Oracle-OpenAI Stargate $300B+ (already noted)
- `hyperscaler_to_lab_investment`: Google→Anthropic cumulative $43B; Amazon→Anthropic cumulative $33B (incl. contingent); AWS→OpenAI Feb 2026 $13B + up-to $20B more
- `hyperscaler_dc_backstops`: Google→Fluidstack/Cipher $1.4B; Google→TeraWulf $1.8B; Google→Hut8 unspecified
- `hyperscaler_backlog`: Google RPO Q4 25 $242.8B → Q1 26 $467.8B (+$225B QoQ); MAG3 AI-lab share ~50%; Anthropic+OpenAI committed to MAG3 $718B

## Decisions made during implementation

All deferred to Cowork session decisions; nothing unilateral.

| # | Decision | Resolution |
|---|---|---|
| O1 | OpenAI 2026 compute spend | Add `total_compute_commitment: 50` as new field; keep `inference_cost: 14.1` unchanged |
| O2 | Anthropic ARR headline | $30B published (Apr 6); $44B carried as `arr_external_estimate` low-confidence |
| O3 | Project Rainier MW | Keep 1,092 nameplate; add `power_mw_energised_2026` field (null) |
| O4 | MSFT/AWS cumulative capex bridge | DEFERRED — public data, doesn't change 2023–25 totals; revisit later |
| O5 | M365 Copilot published basis | LEAKED ACTUAL ($1.35B midpoint); list + bundling-adjusted as comparison context |
| O6 | GitHub Copilot tokens_per_day | Replace unsourced 1000.0 with editorial ~1.0 T/day, low confidence + methodology note |

## Open items

### For next Claude Code session (VS Code) — required before publish

1. **Build site + verify rendered output** per CLAUDE.md "Validate rendered output, not engine reports" rule.
2. **Surface new data on rendered pages** — currently only the data layer is updated:
   - `compute.html`: surface `forward_commitments.hyperscaler_backlog.google_rpo` and `anthropic_plus_openai_committed_to_mag3_usd_b` somewhere (likely a new "forward commitments" block below the trajectory chart)
   - `capital.html`: render `data/depreciation.json` as a small "depreciation watch" block below existing time-bomb section; refresh 2026E capex chart from $550B → $850B; add 2027E at $1.1T
   - `methodology.html`: add Cross-Ledger Reconciliation paragraph for forward-commitments vs realised compute; lab-investment vs realised capex; Copilot announced-vs-actual three-band structure
   - Decide where the Anthropic `arr_external_estimate` $44B surfaces — recommended: a "external estimates" footnote under the Anthropic ARR card, NOT the headline number
3. **CoreWeave reconciliation** — pull most recent CoreWeave 10-Q. Compare disclosed Microsoft customer-concentration % to TAIL's 85% and Ed's 67%; compare disclosed total revenue to TAIL's $4.5B annualised and Ed's $5.15B. Apply whichever is filed-anchored. Document outcome in `docs/decisions/resolved/dec-2026-05-07-coreweave-reconciliation.md`.
4. **Stage URL share + explicit Simon approval** before any production publish (CLAUDE.md Publishing Gate).

### Deferred (not this session)

- Capex bridge documentation (O4) — public data, doesn't materially change 2023–2025 totals.
- Forward-commitments Sankey visualisation — wq-095 (separate scope).
- Apps Ledger (token-burn / Copilot-class productivity SaaS layer) — future scope.

## Acceptance criteria status

- [x] `data/compute_disclosures.json` validates; new `forward_commitments` block tied out; `msft_ai.openai_inference_quarterly` populated
- [x] `entities.json` validates; capacity blocks added; `quarterly_capex` populated; Anthropic ARR + Meta capex + funding_history refreshed; OpenAI total_compute_commitment added
- [x] `data/depreciation.json` exists with required structure
- [x] CoreWeave reconciliation — DEFERRED to next Claude Code session (requires 10-Q pull)
- [ ] `capital.html` 2026E forecast updated to $850B / 2027E added — DEFERRED (Claude Code task)
- [ ] `methodology.html` cross-ledger reconciliation block updated — DEFERRED (Claude Code task)
- [ ] Build runs clean — DEFERRED (Claude Code task)
- [ ] Staging URL shared + explicit Simon approval — DEFERRED (Claude Code task)

## Notion card status

Notion card update — needs to happen manually OR in next Cowork session. Card stage should move from `Idea` → `In Progress` (data layer landed; HTML/render work still pending in VS Code).
