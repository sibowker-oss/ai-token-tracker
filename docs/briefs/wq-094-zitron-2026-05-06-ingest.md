---
id: wq-094
title: Zitron 2026-05-06 ingest — single-pass Compute Stack data update
stage: Scoped
priority: H
owner: Simon (impl: Claude Code in VS Code)
created: 2026-05-07
status: ready_for_handoff
parent_context: /Users/simonbowker/Documents/Claude/Projects/The AI Ledger/ (Cowork session 2026-05-07)
parent_brief: /Users/simonbowker/Developer/apac-ai-intel/docs/briefs/wq-092-compute-ledger-trajectory-no-qoq-drops.md
input_artefacts:
  - /Users/simonbowker/Documents/Claude/Projects/The AI Ledger/zitron-vs-tail-briefing-2026-05-07.docx
  - /Users/simonbowker/Documents/Claude/Projects/The AI Ledger/zitron-vs-tail-2026-05-07.xlsx
---

# wq-094 · Zitron 2026-05-06 ingest — single-pass Compute Stack data update

## Why this brief exists

Ed Zitron published a long-form piece on 2026-05-06 covering hyperscaler AI revenues, frontier-lab concentration, capex, capacity, forward commitments and the circular-financing geometry. A full data-point comparison (see `input_artefacts`) found:

- **No thesis-level conflict** with TAIL post-wq-091/092. Ed's "OpenAI/Anthropic = ~70%+ of hyperscaler AI revenue, ~50% of forward backlog, system circularly funded" is directionally identical to what TAIL publishes.
- **Net-new data on forward commitments** (Google RPO, $200B Anthropic-Google deal, Anthropic-Broadcom TPU buys, Google data-centre backstops, etc.) — these are the meaningful additions.
- **Three numbers needing reconciliation** — CoreWeave 2025 revenue, CoreWeave % from MSFT, Project Rainier MW.
- **One stale number** — Anthropic ARR ($19B Mar → $30B Apr 6 disclosure).
- **One forecast that needs a refresh** — 4-hyperscaler 2026 capex (TAIL $550B vs consensus $800–900B).

This brief consolidates all of it into a single-pass update. No new ledger; existing files extended.

---

## Decisions Simon has made (do not re-litigate without flagging)

| # | Decision | Rationale |
|---|---|---|
| D1 | **Single brief, single wq.** All adds + refreshes + reconciliations land in one Claude Code session. No fan-out across multiple wq cards. | Cowork preference 2026-05-07 — keeps the ingest atomic and the change record clean. |
| D2 | **No new top-level ledger file for forward commitments.** Extend `data/compute_disclosures.json` with a new top-level `forward_commitments` block. | Keeps everything in one file; aggregator already loads it; Layer Stack can reference it. |
| D3 | **Forward commitments are reported gross, separately from realised revenue.** Do NOT roll RPO/commitment dollars into the 2025 sum-of-Q calendar totals or Q1 26 quarterly bars. | Per Cross-Ledger Reconciliation rule (CLAUDE.md). RPO = future revenue contracted, not earned. Confusing the two would inflate the trajectory chart and contradict wq-092 D1. |
| D4 | **Fiscal-vs-calendar quarter labelling stays as-is** in the trend chart. No tooltip change. Analysts working with Microsoft fiscal disclosures vs TAIL calendar are expected to translate. | Cowork explicit 2026-05-07. |
| D5 | **CoreWeave revenue + % from MSFT — reconcile during this session, not next.** Pull most recent CoreWeave 10-Q customer-concentration disclosure inside this brief's scope. If 10-Q confirms TAIL ($4.5B annualised, 85% MSFT) → keep. If 10-Q matches Ed ($5.15B, 67% MSFT) → restate. If neither matches → flag in deployment record and resolve in next session. | Both numbers nominally cite the 10-Q; one of us is wrong. Cheaper to resolve now than carry the conflict. |

## Open decisions — Simon to resolve before Claude Code starts

These need a one-line answer in chat before handoff. Recommended resolutions in italics; push back if you disagree.

| # | Decision | Recommended | Why |
|---|---|---|---|
| O1 | **OpenAI 2026 compute spend definition.** TAIL `openai.financials.2026.inference_cost = $14.1B` (inference only). Ed says "$50B in 2026 alone" — covers training + capacity-prepay + inference. Do we widen TAIL's definition or keep inference-only and add a parallel `total_compute_commitment` field? | *Add `total_compute_commitment_usd_b: 50` as a new field; keep `inference_cost: 14.1` unchanged so historic sankey and revenue-projection model don't shift unexpectedly.* | Less disruptive than redefining `inference_cost`. The bigger number lives where forward commitments live. |
| O2 | **Anthropic ARR headline.** TAIL shows $19B (Mar 2026). Three updates in two months: Apr 6 → $30B annualised (Anthropic disclosure); Apr 30 → $44B (SemiAnalysis estimate). Ed openly sceptical of $44B. | *Use $30B as the on-page headline; carry $44B as `arr_external_estimate` with `confidence: low` and a methodology note explaining the four-week × 13 calculation Ed flagged. Do NOT use $44B as the live number on cards.* | Ed already cites Anthropic's CFO sworn-affidavit at $5B cumulative — direct disclosure beats third-party estimate. |
| O3 | **Project Rainier MW.** TAIL = 1,092 MW (Tier 1A property docs + Cat generators). Ed = 500 MW. Likely energised-today vs full-nameplate distinction. | *Keep TAIL's 1,092 MW as `power_mw` (nameplate). Add `power_mw_energised_2026` field (initially null; populate when verifiable). Footnote on the DC card.* | TAIL's number is hard-sourced; Ed's is editorial. Don't downgrade to match a softer source. |
| O4 | **MSFT cumulative capex headline (capital.html).** TAIL 2023–2025 = $176.3B; Ed cites $293.8B "through latest quarter." Adding Q1 2026 (~$37.5B) gets to ~$214B; still $80B short of Ed. The gap is likely 2022 + scope drift. | *Extend TAIL cumulative window to include Q1 2026 actuals where disclosed. Footnote that the TAIL window is "AI-relevant capex 2023+ inclusive" and that gross-corp-capex through latest quarter (Ed's basis) lands at $293.8B for MSFT, $298.3B for AWS. Show both views, don't pick one.* | The two numbers measure different things; readers deserve both with the bridge documented. |

If you don't push back on any of O1–O4 within the next session, Claude Code will proceed with the recommended resolutions.

---

## Scope

### In scope

#### A. ADDS — forward commitments (new section in `data/compute_disclosures.json`)

Add top-level `forward_commitments` block with three sub-blocks: `lab_to_hyperscaler` (the $200B / $718B / Broadcom TPU lines), `hyperscaler_to_lab_investment` (Google's and Amazon's investments in Anthropic; AWS in OpenAI), and `hyperscaler_dc_backstops` (Fluidstack/Cipher etc.).

```
forward_commitments:
  lab_to_hyperscaler:
    anthropic_google_5yr:
      commitment_usd_b: 200
      duration_years: 5
      commitment_period_start: "2026"
      tier: "1B"  # Information citation, anchored to Anthropic disclosure
      source: "The Information 2026-04-30; Anthropic + Google joint statement"
      share_of_google_rpo_q1_2026_pct: 42.7  # = 200 / 467.8
    anthropic_broadcom_tpu_2026:
      commitment_usd_b: 21
      year: 2026
      tier: "1B"
      source: "CNBC 2026-04 / Anthropic-Broadcom announcement"
      destination_note: "Broadcom-built TPUs deployed in Google data centres; Anthropic pays Google to rent."
    anthropic_broadcom_tpu_2027:
      commitment_usd_b: 42
      year: 2027
      tier: "1B"
      source: "CNBC 2026-04"
    aws_openai_2026:
      commitment_usd_b: 38
      duration_years: 1
      tier: "1B"
      source: "AWS-OpenAI announcement Q1 2026"
    aws_openai_8yr_expansion:
      commitment_usd_b: 100
      duration_years: 8
      tier: "1B"
      source: "AWS-OpenAI announcement Q1 2026"
    oracle_openai_stargate:
      commitment_usd_b: 300
      tier: "1B"
      source: "Oracle Q3 FY26 RPO disclosure"
      already_in_oracle_notes: true
  hyperscaler_to_lab_investment:
    google_anthropic_cumulative:
      invested_usd_b: 43
      tier: "1B"
      breakdown:
        prior_rounds_through_2025: 33  # cumulative pre-2026
        feb_2026_round_share: null     # confirm
        apr_2026_round: 10
      source: "Google + Anthropic disclosures; The Information 2026-04"
    amazon_anthropic_cumulative:
      invested_usd_b: 33
      tier: "1B"
      breakdown:
        prior_through_2025: 13
        apr_2026_round: 5
        contingent_additional: 15  # "as much as $20B more"
      source: "Amazon + Anthropic disclosures; Reuters 2026-04"
    aws_openai_feb_2026:
      invested_usd_b: 13
      contingent_additional_usd_b: 20
      tier: "1B"
      source: "Amazon Q4 2025 announcement; The Information 2026-02"
  hyperscaler_dc_backstops:
    google_fluidstack_cipher:
      backstop_usd_b: 1.4
      tier: "1B"
      operator_serving: "Anthropic"
      source: "Information / Zitron 2026-05-06"
    google_terawulf:
      backstop_usd_b: 1.8
      tier: "1B"
      operator_serving: "Anthropic"
      source: "Information / Zitron 2026-05-06"
    google_hut8:
      backstop_usd_b: null  # unspecified
      tier: "2A"
      operator_serving: "Anthropic"
      source: "Zitron 2026-05-06"
  hyperscaler_backlog:
    google_rpo:
      q4_2025_usd_b: 242.8
      q1_2026_usd_b: 467.8
      qoq_jump_usd_b: 225.0
      tier: "1A"  # 10-Q disclosure
      source: "Alphabet Q1 2026 10-Q"
    mag3_ai_lab_share_of_backlog_pct: 50  # editorial 2A from Information chart
    anthropic_plus_openai_committed_to_mag3_usd_b: 718  # Information chart
    tier_aggregate: "2A"
```

**Tie-out check (rendered on `methodology.html` for transparency):** Anthropic-Google $200B / Google Q1 26 RPO $467.8B = 42.7%. The Information chart's "~50% AI labs" should reconcile to 40–50% range across the three hyperscalers in aggregate.

#### B. ADDS — capacity totals (new fields per hyperscaler in `entities.json`)

Add `compute_capacity_gw` block to MSFT, AWS, GCP, OpenAI entities. CoreWeave too.

```
azure.compute_capacity_gw:
  end_2025: 2.0
  source: "Epoch AI estimate; cited in Zitron 2026-05-06"
  tier: "2A"
aws.compute_capacity_gw:
  end_2025: 1.67
  source: "Editorial estimate; Zitron 2026-05-06"
  tier: "2A"
gcp.compute_capacity_gw:
  end_2025: 2.95
  source: "Editorial estimate; Zitron 2026-05-06"
  tier: "2A"
coreweave.compute_capacity_gw:
  end_2025: 0.480
  source: "Editorial; Zitron 2026-05-06"
  tier: "2A"
openai.compute_access_gw:
  end_2025: 1.9
  source: "OpenAI CFO disclosure end-2025"
  tier: "1B"
anthropic.compute_access_commitment_gw:
  aws_up_to: 5.0
  google_2026_at_least: 1.0
  google_2027_plus: "multiple"
  tier: "1B"
  source: "Anthropic + Amazon + Google announcements 2025-2026"
```

#### C. ADDS — quarterly capex per hyperscaler (extends `entities.json:market_aggregates`)

Add a `quarterly_capex` block to `market_aggregates` keyed by quarter, with per-hyperscaler values where disclosed. Seeded with what Ed's piece exposes:

```
market_aggregates.quarterly_capex:
  2025Q3:
    msft_usd_b: 21.4    # Ed; MSFT Q3 FY25 calendar — verify against 10-Q
    tier: "1A"
  2025Q4:
    msft_usd_b: 37.5    # Ed; MSFT Q4 calendar — verify against 10-Q
    tier: "1A"
```

Leave 2025Q1, 2025Q2, 2026Q1 as null — populate from 10-Qs in the same session if quick.

#### D. ADDS — depreciation block (new file `data/depreciation.json` + capital.html section)

Per Ed and WSJ, this is the slow-burn time-bomb in the capex story. Worth surfacing as a small dedicated block.

```
{
  "lastUpdated": "2026-05-07",
  "quarterly": {
    "2026Q1": {
      "msft_usd_b": 10.1,
      "googl_usd_b": 6.48,
      "amzn_usd_b": 18.94,
      "meta_usd_b": 5.9,
      "tier": "1A",
      "source": "Q1 2026 10-Qs"
    }
  },
  "wsj_2030_projection_pct_net_income": {
    "meta": 58,
    "msft": 40,
    "googl": 38,
    "tier": "2B",
    "source": "WSJ 2026 projection cited Zitron 2026-05-06"
  }
}
```

Render a small "depreciation watch" block on `capital.html` below the existing time-bomb section. Two stat tiles: latest quarter + 2030 projected.

#### E. ADDS — OpenAI Azure inference quarterly trajectory (extends `compute_disclosures.json:msft_ai`)

```
msft_ai.openai_inference_quarterly:
  2025Q1:    1.467  # MSFT Q2 FY25 = calendar Q4 2024; Ed leaked
  2025Q2:    2.075  # MSFT Q3 FY25; Ed leaked (note Ed cites $2.075B in one paragraph and $2.947B in another — flag inconsistency in field comment)
  2025Q3:    3.648  # Ed
  2025Q4:    4.625  # Ed estimate "annualised hit over $18.5B by year-end"
  tier: "1B-leaked"  # Azure billing source; not externally verifiable
  source: "Zitron 2026-05-06 — sources with direct knowledge of Azure revenue"
  caveat: "1B-leaked tier introduced for this update — own-mouth via insider, higher than 2A editorial but not externally verifiable. Treat as anchor candidate; cross-check at Q2 2026 earnings."
```

#### F. ADDS — narrative anchors (Notes + content fields, no tracker math)

| Field | Where | Value |
|---|---|---|
| `azure.products[copilot_365].subscriber_count_m` | entities.json | 20 (Ed; MSFT-disclosed) |
| `anthropic.notes.github_copilot_concentration` | entities.json | "GitHub Copilot is 2nd largest Anthropic customer (Ed 2026-05-06)" |
| `meta.notes.gem_token_burn` | entities.json | "60T tokens / 30 days, ~$330M cost (The Information / Ed)" |
| `meta.notes.gem_lift_q2_2025` | entities.json | "5% IG conv lift, 3% FB conv lift" |
| `meta.notes.gem_lift_q4_2025` | entities.json | "3.5% FB click lift, >1% IG conv lift — different metric basis vs Q2" |
| `meta.financials.2026.reality_labs_q1_loss_usd_b` | entities.json | 4 |
| `meta.financials.cumulative.reality_labs_loss_usd_b` | entities.json | 86 |
| `aws.notes.history_2003_2017` | entities.json | "$52B capex 2003–2017 (inflation-adjusted); profitable in ~10 years. Editorial control point for AI-era capex/payback comparison." |
| `anthropic.notes.projected_loss_2026_27` | entities.json | "$11B/yr both 2026 and 2027 per The Information leak of Anthropic internal projection" |

#### G. REFRESH — updated values

| Field | From | To | Source |
|---|---|---|---|
| `anthropic.current.arr` | 19 | 30 | Anthropic disclosure 2026-04-06 |
| `anthropic.current.arr_date` | "2026-03" | "2026-04" | — |
| `anthropic.financials.2026.arr` | 18 | 30 | — |
| `anthropic.arr_external_estimate.value` | (new) | 44 | SemiAnalysis 2026-04-30 |
| `anthropic.arr_external_estimate.confidence` | (new) | "low" | Per O2; methodology footnote required |
| `meta.financials.2026.capex` | 125 | 145 | Meta Q1 2026 guidance refresh |
| `capital.html capex chart 2026E.totalCapex` | 550 | 850 | Consensus / WSJ; 4-hyperscaler aggregate |
| `capital.html capex chart 2027E.totalCapex` | (new) | 1100 | Consensus / WSJ |
| `entities.json:market_aggregates._cumulative_2023_2027.capex_total` | (new) | ~2000 | Consensus / WSJ |

Anthropic raises history (add to `anthropic.financials.funding_history`):

```
funding_history:
  - { date: "2025-09", round: "Series F", amount_usd_b: 13 }
  - { date: "2026-02", round: "Series G", amount_usd_b: 30, valuation: 380 }
  - { date: "2026-04", round: "AWS strategic", amount_usd_b: 5 }
  - { date: "2026-04", round: "Google strategic", amount_usd_b: 10 }
  - { date: "2026-Q2", round: "in_talks", amount_usd_b: 50, status: "rumoured" }
total_raised_through_2026_04: 58
```

OpenAI 2026 compute commitment (per O1 recommended resolution):

```
openai.financials.2026.total_compute_commitment_usd_b: 50  # Ed-cited OpenAI plan
openai.financials.2026.inference_cost: 14.1  # unchanged
```

#### H. RECONCILE — CoreWeave + Project Rainier

1. Pull CoreWeave's most recent 10-Q (Q1 2026 if filed, else Q4 2025).
2. Find customer-concentration disclosure (typically in Risk Factors or Revenue Recognition note).
3. Compare disclosed Microsoft % to TAIL's 85% and Ed's 67%.
4. Compare disclosed total revenue to TAIL's $4.5B annualised and Ed's $5.15B.
5. Apply whichever is filed-anchored. If both numbers reconcile to a third value, restate to 10-Q.
6. Document the reconciliation in `docs/decisions/resolved/dec-2026-05-07-coreweave-reconciliation.md`.

For Project Rainier (per O3 recommended resolution): add `power_mw_energised_2026` field initialised null. No restatement.

#### I. CROSS-LEDGER RECONCILIATION (per CLAUDE.md rule, mandatory)

Before this brief ships, the reconciliation block in `methodology.html` must include:

- **`forward_commitments` vs realised compute revenue** — explicit statement that backlog/RPO/commitments are NOT included in the Compute Ledger 2025 sum-of-Q or Q1 26 quarterly bars. Bridge: 2025 sum-of-Q $51.25B (realised) vs $718B (Anthropic+OpenAI committed) is a >14× gap reflecting that the realised compute revenue is dwarfed by the contracted future flow.
- **`hyperscaler_to_lab_investment` vs realised hyperscaler capex** — investment in labs is NOT included in capex ($176.3B MSFT etc.). Bridge: Google $43B invested in Anthropic + Anthropic's $200B 5-yr commitment back to Google = circular flow visualised in a Sankey-style annotation on capital.html.
- **Capex bridge MSFT $176.3B (TAIL 2023–2025) → $293.8B (Ed through latest Q)** — show both with the time-window + scope difference annotated.

### Out of scope

- New ledger files beyond the small `depreciation.json`. Everything else extends existing files.
- New visualisations beyond the small "depreciation watch" tile and the reconciliation block. The big circular-financing Sankey is wq-095 (separate brief, scoped after this lands).
- Restating 2025 sum-of-Q quarterly trajectory. Per D3 + wq-092 D1, that basis is locked.
- The OpenAI/MSFT and Anthropic/AWS concentration % restatements. Those numbers are already correct on TAIL's published basis (sum-of-Q) and the apples-to-apples agreement with Ed has been documented in this session's comparison docs. No code change needed.
- Anything Meta-Reality-Labs beyond the two notes fields in §F.
- Building a new Apps Ledger to capture token-burn data (Meta GEM 60T tokens etc.) — that's a future scope, not this session.

---

## Acceptance criteria

1. `data/compute_disclosures.json` validates against existing `_schema`; new `forward_commitments` block tied out per §A; `msft_ai.openai_inference_quarterly` populated per §E.
2. `entities.json` validates; new `compute_capacity_gw` blocks per §B; `quarterly_capex` per §C; refreshed Anthropic ARR + Meta capex + funding_history per §G; OpenAI `total_compute_commitment` per O1.
3. `data/depreciation.json` exists with §D structure; `capital.html` renders a depreciation-watch tile pulling from it.
4. `capital.html` 2026E forecast updated to $850B (4-hyperscaler) per O4 / §G; 2027E added at $1.1T.
5. `methodology.html` cross-ledger reconciliation block updated per §I — explicit bridge prose for forward-commitments, lab-investment, and capex-window mismatches.
6. CoreWeave reconciliation per §H executed; decision file written to `docs/decisions/resolved/`.
7. Build runs clean; rendered output verified per CLAUDE.md "Validate rendered output, not engine reports" rule.
8. Staging URL shared in chat; explicit Simon approval received before production publish per CLAUDE.md Publishing Gate.
9. Deployment record `docs/deployments/deploy-2026-05-XX-wq-094-zitron-ingest.md` written with what shipped, decisions made, open items.

---

## Source provenance

Primary input: Ed Zitron, "Where's Your Ed At" newsletter, 2026-05-06.

Tier note for this brief: Ed's leaked Azure billing figures are tagged **`1B-leaked`** — a new tier introduced here for "own-mouth via insider, higher than 2A editorial but not externally verifiable." Document in `_schema.tiers` of `compute_disclosures.json`. Treat as anchor candidates that should be cross-checked at the next earnings cycle.

Secondary inputs: The Information chart of MAG3 backlog by customer; CNBC Anthropic-Broadcom coverage; Anthropic / Google / Amazon official disclosures and SEC filings; Q1 2026 10-Qs.

TAIL prior art: wq-091 (segment sizing), wq-092 (sum-of-Q trajectory), wq-093 (homepage refresh), `assumptions-audit.md` (Zitron already cited as primary source for OpenAI ARR-method haircut, MSFT-OpenAI rev share, OpenAI H1 2025 inference, Anthropic court-filing).

Comparison artefacts (read these first):

- `/Users/simonbowker/Documents/Claude/Projects/The AI Ledger/zitron-vs-tail-briefing-2026-05-07.docx`
- `/Users/simonbowker/Documents/Claude/Projects/The AI Ledger/zitron-vs-tail-2026-05-07.xlsx`
