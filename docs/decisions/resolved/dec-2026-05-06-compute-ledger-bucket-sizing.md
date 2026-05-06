# Decision: Compute Ledger revenue segment sizing — derivation memo

**Date:** 2026-05-06
**Stage:** Resolved (Cowork session 2026-05-06)
**WQ:** Drives wq-091 (deploy correction)
**Related:** wq-087 (original Compute Ledger), wq-089 (Compute Ledger v2 — segment framework introduced; shipped 2026-05-06)
**Status:** Locked. Numbers in §"Final locked table" are the agreed estimates as of 2026-05-06; revisit with each hyperscaler quarterly cycle.

## Naming convention

The Compute Ledger decomposes hyperscaler/neocloud AI revenue into three plain-English revenue segments:

- **Frontier lab compute** — what Model Providers (per Usage Ledger taxonomy) pay external hyperscalers/neoclouds for raw GPU/instance capacity to train and serve their own foundation models. The circular-financing line.
- **AI workload compute** — what AI Natives (running open models or own models), enterprises (running internal AI workloads), model-serving infrastructure cos, and sovereign/regulated workloads pay for raw cloud capacity.
- **Hosted model APIs** — what hyperscalers earn from packaged token APIs (AWS Bedrock, Azure OpenAI Service, Google Vertex partner-served). Pass-through to model labs only exists here.

Plus a fourth flow that is **scoped out** of the Compute Ledger because it's economically Apps:

- **Copilot-class products** — per-seat productivity SaaS (M365 Copilot, GitHub Copilot, Copilot Studio, Gemini-in-Workspace SKUs). Booked in vendors' AI revenue lines but belongs in the future Apps Ledger.

## Why this memo exists

wq-087 shipped the Compute Ledger in early May 2026. wq-089 amended it the same day with revenue-segment decomposition + Copilot scope-out + corrected pass-through. The Cowork review session 2026-05-06 stress-tested wq-089's shipped numbers against published hyperscaler economics and against the Revenue Ledger; the segment framework held but the **per-segment sizing** — particularly per-hyperscaler AI-share weights — turned out to be materially overstated. wq-089 shipped with hyperscaler AI 2025 totaling $73.45B; this memo's bottom-up derivation lands at ~$54.45B, a ~$20B downward restatement. wq-091 implements the correction.

This memo captures the full derivation rationale so future revisits (next quarterly refresh, or someone reading the data file in 6 months) can see clearly *how* the numbers were arrived at — not just what they are.

## Context — what shipped under wq-089

Per `docs/deployments/deploy-2026-05-06-wq-089-compute-ledger-v2.md`:

| Provider | wq-089 shipped 2025 AI line | Editorial basis |
|---|---|---|
| MSFT | $28B annualised | Microsoft self-disclosed run-rate ($37B Q1 2026) reverse-engineered |
| AMZN | $18B annualised | 15% of AWS revenue (editorial AI-share weight) |
| GOOGL | $18B annualised | 30% of Google Cloud revenue (editorial AI-share weight) |
| ORCL | $3B annualised | 10% of OCI (editorial AI-share weight) |
| Neoclouds (CRWV+NBIS+LMBD+CRSE) | $6.45B | 95%+ AI by definition; well-disclosed |
| **Total** | **$73.45B** | — |

Segment decomposition shipped:
- Frontier lab compute: **$50.55B** — included $5B "Google equity-cycle" line (internal recursion)
- AI workload compute: **$10.40B**
- Hosted model APIs: **$4.50B**
- Pass-through 2025: **$1.025B** (corrected from prior $11.5B)
- Copilot scope-out: **$8B** (MSFT $5B + GOOGL $3B)
- Compute gross post-Copilot: **$65.45B**
- Compute net: **$64.42B**

The 2026-05-06 Cowork review identified five places where these numbers were materially off, walked through each, and locked corrected figures.

## Issue 1 — Hosted model APIs sizing was too high → pass-through inherited the error

### Original sizing argument

I had Hosted model APIs at $8–12B, anchored on:
- AOAI: $5–8B (~25% of MSFT $28B AI line as Azure OpenAI Service portion)
- Bedrock: $2–3B
- Vertex partner-served: $0.5–1B

Pass-through (Hosted model APIs × ~25% lab rev-share) implied ~$2–3B.

### Simon's pushback

OpenAI's total 2025 calendar revenue is ~$12–13B. If AOAI = $5–8B at 20% rev-share, OpenAI's share of AOAI is ~$1–1.6B — plausible but a tight share of OpenAI's reported revenue. More importantly, **who is buying $5–8B of AOAI**?

- AI Natives don't (they go direct to OpenAI API — cheaper, faster, no Azure premium)
- Enterprise IT does (compliance, FedRAMP, EU residency, Microsoft EAs) — but in 2025 most enterprises were still pilot-stage

Token economics test: $2M/year/enterprise on AOAI = 400B tokens/year = 1.1B tokens/day. That's production-scale, not pilot. The number of enterprises actually doing that in 2025 is small (~100–200 globally).

### Corrected sizing

Bottom-up:
- AOAI: ~$1–1.5B (~50–100 mega-users at $2–10M each + ~200 production users at $500K–2M + pilot tail + PTU reservations + gov contracts)
- Bedrock: ~$2–3B (Anthropic-via-Bedrock ~$1B + minor partners)
- Vertex partner-served: ~$0.5–1B
- **Hosted model APIs total: ~$3.5–5.5B**, central **~$4.5B**

Pass-through ~$1B.

### Why the original was wrong

The original AOAI estimate anchored on **80% AOAI weight × MSFT $28B** = $22.4B implied AOAI revenue, with pass-through math then applied. This was structurally wrong: AOAI is probably **~5% of MSFT $28B**, not 80%. Frontier lab compute (OpenAI consuming Azure compute for ChatGPT/o3 hosting) is the dominant share — $18B out of $28B.

## Issue 2 — Pass-through anchor was wrong from the start

### Original method

`data/compute_disclosures.json` calculated pass-through as ~16% of *total* hyperscaler AI revenue. With $73B gross, this implied $11.5B pass-through to model labs.

### Why this was wrong

Pass-through (lab share of hyperscaler-resold model API) only exists in the **Hosted model APIs** segment. The other two segments have no pass-through:
- Frontier lab compute: frontier lab is the *customer*; the lab pays the hyperscaler. No pass-through.
- AI workload compute: AI Native or enterprise buying raw GPU capacity. No model-lab involvement. No pass-through.
- Hosted model APIs: hyperscaler resells third-party model via token API; rev-shares with lab. **Only here.**

Applying pass-through to total AI revenue grosses up Frontier lab compute + AI workload compute by a phantom lab-rev-share that doesn't exist.

### Corrected method

Pass-through = Hosted model APIs × lab rev-share (default 25% blended; tighter per-provider).
- AWS Bedrock × 25% ≈ $0.6B
- AOAI × 20% ≈ $0.3B
- Vertex × 20% ≈ $0.1B
- **Total pass-through 2025: ~$1B**, range $0.7–1.5B

This collapses the gross/net Compute distinction from $11.5B to ~$1B — significant editorial implication on the page (gross/net split is no longer the headline).

## Issue 3 — Copilot was double-counted between Compute and the eventual Apps Ledger

### What was happening

MSFT's $28B 2025 annualised AI line includes Copilot products (M365 Copilot, GitHub Copilot, Copilot Studio). These are per-seat productivity SaaS, billed in Microsoft's Productivity & Business Processes segment (not Azure). Economically: Apps revenue, not Compute revenue.

GOOGL's $18B AI line equivalently includes Gemini-in-Workspace SKUs and embedded Gemini features — also Apps not Compute.

wq-089 shipped a Copilot scope-out of $8B ($5B MSFT + $3B GOOGL). Investigation against entity records and Usage Ledger derivation suggests the scope-out should be larger and per a different basis.

### Two valid Copilot numbers

There are two legitimate Copilot numbers serving different purposes:

**MS-declared Copilot 2025 (~$7.4B):**
- M365 Copilot list billings: 15M paid seats × $30/mo × 12 = $5.4B
- GitHub Copilot ARR: $1.65B (Tier 2A editorial)
- Sundry Copilot SKUs (Studio, Sales, Service): ~$0.4B

**TAIL-derived "real" Copilot 2025 (~$4–5B):**
- M365 Copilot net of bundling discount (40–60% of list because Microsoft uplifts E5+Copilot bundles where customer's net spend barely moves): ~$2.5–3.5B
- GitHub Copilot real (~$1–2.3B per Usage Ledger)
- Sundry: ~$0.3–0.5B

### Which to use where

For wq-091 Compute Ledger scope-out: **use MS-declared $7.4B** (not $5B as shipped, not $4–5B TAIL-derived). Logic: the deduction is from Microsoft's *reported* AI line, which includes Copilot at MS-declared value. Stripping only $4–5B would leave $2.4–3.4B of Copilot still mixed into the Compute number.

For the future Apps Ledger: use **TAIL-derived** (~$4–5B) plus the bundling-overstatement gap as an editorial point ("Copilot ARR claimed at $7.4B, real incremental is $4–5B; the gap is bundling effect").

### GOOGL Copilot equivalent

Originally sized at $3B Gemini-in-Workspace. Investigation suggests this was **inflated by mis-attribution** — half of what was being labelled "Gemini-in-Workspace Apps" was actually frontier-lab compute consumption (Anthropic on TPUs, OpenAI on GCP) being mis-categorised. Real Gemini-in-Workspace external Apps revenue: **~$1.5B**, not $3B. The other $1.5B reclassifies to Frontier lab compute (see Issue 4 below).

### Stale entity record

`entities.json:microsoft-copilot.products[m365-copilot]` has `ai_arr: $13B` — this is almost certainly a stale Microsoft-total-AI-ARR figure from Jan 2026 (per `wheresyouredat-claims-vs-tail.html` audit which flags it as stale) mislabeled against M365 Copilot. Should be cleaned up; wq-091 corrects.

## Issue 4 — AWS AI line was 80% too high; Andy Jassy's disclosure pins the ceiling

### Original sizing

`data/compute_disclosures.json` had AMZN AI line 2025 = $18B, anchored on 15% of AWS total revenue. Editorial AI-share weight, Tier 2A.

### The Jassy disclosure

Amazon CEO Andy Jassy in his early 2026 shareholder letter explicitly stated: AWS's AI revenue had crossed a **$15B annualized run rate**. That's a hard, CEO-level disclosure — not editorial.

Working backward from Q1 2026 run-rate to 2025 calendar:
- $15B annualized = $3.75B/quarter exit run-rate (early-mid 2026)
- AI/Anthropic growth pattern through 2025 was very steep (Anthropic itself went from ~$1B run-rate Q1 2025 to ~$5–6B Q4 2025)
- Apply similar shape to AWS AI: Q1 ~$1.5B, Q2 ~$2B, Q3 ~$2.5–3B, Q4 ~$3.5B
- **2025 calendar AWS AI = ~$9–11B**, central ~$10B

### Segment decomposition for AWS at $10B

- Copilot: $0 (no AWS Copilot product)
- Frontier lab compute (Anthropic + minor labs): ~$7B (Anthropic 2025 was $4.71B, ~80% on AWS infra including training compute → AWS Frontier lab compute from Anthropic ~$5–6B, plus minor labs $1–2B)
- Hosted model APIs (Bedrock token API): ~$2.5B
- AI workload compute (non-frontier residual): ~$0.5B

The Anthropic-on-AWS sizing was raised relative to my original estimate ($3–5B → $5–6B+) because Anthropic's *training* compute on AWS is in addition to inference compute — both are Frontier lab compute.

## Issue 5 — GCP AI line was 60% too high; bottom-up derivation pins ~$7B

### Original sizing

`data/compute_disclosures.json` had GOOGL AI line 2025 = $18B, anchored on 30% of Google Cloud total revenue. Editorial AI-share weight, Tier 2A.

### Disclosed numbers (Q1 2026 earnings + recent earnings calls)

- Q1 2026 Google Cloud revenue: $20.03B, +63% YoY
- Cloud backlog: $460B (up from $240B at Cloud Next earlier)
- Calendar 2025 Google Cloud (sum-of-quarters): ~$58B
- End-2025 run-rate: >$70B
- "13 product lines now exceed $1B annual run rate" (Q2 2025 commentary)
- "70% of existing Cloud customers using Google's AI products"
- "Revenue from products built on Google's generative models grew nearly 800% YoY" (Q1 2026 narrative)
- **No discrete GCP AI revenue number disclosed** — all narrative, no $X figure

### The Anthropic-equity-gain confounder

Q1 2026 Alphabet had a $36.9B gain on equity securities, primarily Anthropic stake mark-up. Fortune ran a piece noting "half of Google's and Amazon's blowout AI profits came from a stake in Anthropic — not from their actual business." Important: this is investment gain, not Cloud operating revenue. Doesn't flow to GCP AI revenue. The Cloud P&L is tighter than the AI-narrative implies.

### Bottom-up GCP AI derivation

If 4–5 of "13 product lines >$1B" are predominantly AI-driven (Vertex AI Platform, Gemini API, AI Hypercomputer, AI agent/search products, AI-driven analytics), each at $1.0–1.5B mid-2025 run-rate = ~$5–7B AI-products run-rate mid-2025. Calendar 2025 averaging Q1-Q4 (start lower, end higher): **~$6–8B**.

Locked at **$7B central**, range $6–8.5B.

### Segment decomposition for GCP at $7B

Initial decomposition (with original Copilot at $3B):

- Copilot: $3B
- Frontier lab compute (Anthropic on TPUs + Mistral + others): ~$2B
- Hosted model APIs (Vertex partner-served): ~$0.5B
- AI workload compute (non-frontier residual): ~$1.5B

Then corrected (Issue 6 below): Copilot drops to $1.5B; Frontier lab compute grows to $3.5B because Anthropic-on-GCP and OpenAI-on-GCP were under-sized.

## Issue 6 — Anthropic and OpenAI compute on GCP were under-sized / missed

### What was missing

Original GCP Frontier lab compute at $2B included Anthropic on TPUs (~$1B) + Mistral + others. Two material flows missed:

1. **Anthropic-on-GCP is much bigger than $1B.** Anthropic has a deep partnership with Google. Press disclosures: April 2026 Anthropic signed expanded TPU agreement with multi-GW capacity from 2027. 2025 spend on TPUs likely $1.5–2B (significant primary training/inference customer). Was previously under-sized.

2. **OpenAI started using GCP in 2025** for ChatGPT and API in specific regions. Per CNBC 2025-07-16, OpenAI began diversifying compute onto Google Cloud. Partial-year 2025 spend ~$0.5–1B. Was missed entirely.

So GCP Frontier lab compute should be:
- Anthropic on TPUs: $1.5–2B (was $1B)
- OpenAI on GCP: $0.5–1B (was $0)
- Mistral + Cohere + AI21 + others: ~$1B (unchanged)
- **GCP Frontier lab compute total: ~$3.5B**

The $1.5B addition relative to original sizing ($2B → $3.5B) reclassifies from where it was previously being absorbed — partly into the bloated $3B "Gemini-in-Workspace Copilot" line. The original $3B Copilot scope-out for GCP was masking real Frontier lab compute consumption as Apps revenue.

So **GCP Copilot drops from $3B to $1.5B; GCP Frontier lab compute grows from $2B to $3.5B; GCP tie-out at $7B unchanged.**

### Cross-check: OpenAI compute distribution

Sanity check on the new picture — if OpenAI's 2025 compute spend totals across segments:

| Cloud | OpenAI 2025 spend |
|---|---|
| Microsoft Azure | ~$18B (~80%) |
| Oracle Stargate | ~$1.5B (~7%, ramp) |
| GCP | ~$0.5–1B (~4%, new diversification) |
| **OpenAI total compute spend 2025** | **~$22B** |

(Note: CoreWeave's $3.8B Microsoft sub-rent for OpenAI is captured in CRWV's Frontier lab compute separately to avoid double-counting at the OpenAI line.)

That tracks plausibly with public reporting that OpenAI is diversifying ~15–20% off Azure.

## Definitional decisions baked in

### Frontier lab definition (kept strict — unchanged from wq-089 D8)

> Frontier lab compute sums external compute spend by Model Providers (per Usage Ledger taxonomy `frontierProvs` + `openProvs`), where the Model Provider pays a **separate** hyperscaler/neocloud (external transaction). Internal-recursion (Google's own Gemini compute on GCP, Meta's LLaMA on own DC, Microsoft's MAI on own Azure) contributes **$0**. Chinese labs running on Chinese hyperscalers contribute $0 in Mag3-economy Frontier lab compute.

The temptation during this session was to loosen this to let Google's internal Gemini compute count (because the economic activity is the same). We kept the strict definition on the basis that:
- "External" is observable and auditable; "internal" is editorial
- The actual GCP Frontier lab compute needed correcting via real external flows (Anthropic + OpenAI on GCP), not via internal recursion
- A strict definition keeps the segment sizing methodology defensible

Microsoft is **not** a Model Provider (MAI is too small to be material). Microsoft sits as pure hyperscaler.

### Naming convention (kept clean)

> Page copy / methodology / chart labels / brief content / decision memos all use plain English: **Frontier lab compute / AI workload compute / Hosted model APIs**. Engineering shorthand ("Bucket 1/2/3") is dropped from all writing — past and future. JSON schema field names get renamed in wq-091 to match (`frontier_lab_compute_2025_usd_b`, etc.).

### Quarterly trajectory back-cast methodology (added 2026-05-06 mid-session)

The wq-089 shipped quarterly array (Q1 25 through Q1 26 per provider) was anchored on the same editorial AI-share weights that wq-091 corrects for the annualised numbers — they were never re-derived. Result: in the trajectory chart, with the corrected calendar 2025 totals applied as a sum-tie, the implied per-quarter shape becomes inconsistent with disclosed run-rates. Specifically, AWS Q4 2025 ≈ Q1 2026 (because Jassy's "$15B annualized" is exit-quarter run-rate ÷ 4 = $3.75B/quarter, against a back-cast Q4 25 of similar size when 2025 calendar is $10B).

Three-anchor method for re-deriving quarterlies per provider:

1. **Q1 2026 anchor:** disclosed run-rate ÷ 4 where available
   - MSFT: $9.25B (= $37B/4 from MSFT Q3 FY26 self-disclosure; holds from existing data)
   - AMZN: $3.75B (= $15B/4 from Andy Jassy 2026 shareholder letter; restated DOWN from $5.60B)
   - GOOGL: ~$3.5B (run-rate-implied from "products built on gen AI grew nearly 800% YoY" + Q1 25 anchor)
   - ORCL: $0.9B (holds)
   - Neoclouds: hold (well-disclosed at entity level per wq-087)

2. **Q1 2025 anchor:** disclosed YoY growth back-cast where available
   - MSFT: $4.15B (holds; ties to Q1 26 $9.25B at +123% YoY per Microsoft commentary)
   - AMZN: ~$0.75B (Tier 2A back-cast from Anthropic's ~5× annual growth pattern, since Anthropic-on-AWS is the dominant share of AWS AI)
   - GOOGL: ~$0.5B (Tier 2A back-cast from "+800% YoY on gen AI products" narrative)
   - ORCL: $0.5B (holds)
   - Neoclouds: hold

3. **2025 calendar sum-tie:** corrected wq-091 totals
   - MSFT $28B, AMZN $10B, GOOGL $7B, ORCL $3B, neoclouds $6.45B

4. **Interior quarters (Q2-Q4 2025):** smoothed via exponential ramp constrained so the four 2025 quarters sum to the corrected calendar total.

Per-provider trajectory shapes (post-back-cast, illustrative):

| Provider | Q1 25 | Q2 25 | Q3 25 | Q4 25 | Q1 26 |
|---|---|---|---|---|---|
| MSFT | $4.15 | ~$5.5 | ~$7.2 | ~$8.4 | $9.25 |
| AMZN | ~$0.75 | ~$1.5 | ~$2.7 | ~$3.8 | $3.75 |
| GOOGL | ~$0.5 | ~$1.0 | ~$2.0 | ~$3.0 | ~$3.5 |
| ORCL | $0.5 | $0.65 | $0.85 | $0.95 | $0.9 |
| Neoclouds (sum) | $1.20 | $1.37 | $1.62 | $1.86 | $2.14 |

**Q4 25 → Q1 26 transition handling — UPDATED 2026-05-06 (wq-092):**

The wq-091 deployed quarterly trajectory anchored 2025 calendar to **annualised run-rate basis** (~$28B MSFT, $10B AMZN, $7B GOOGL — derived from CEO disclosures of full-year run-rate × 4) AND Q1 26 to **literal quarterly basis** ($37B/4, $15B/4). When growth accelerates through a year, sum-of-quarterlies < annualised, so forcing the quarterly array to sum to the annualised number balloons Q4 25 above Q1 26.

Result on the deployed chart:
- MSFT: Q4 25 $10.50B → Q1 26 $9.25B (–12%)
- AMZN: Q4 25 $3.75B → Q1 26 $3.75B (flat)
- GOOGL: Q4 25 $3.65B → Q1 26 $2.50B (–32%)

**This visibly contradicted the AI growth narrative.** Simon called it: "we can't have a chart that showing a drop q over q on AI revs - that's dumb."

**wq-092 corrects** by switching the 2025 calendar tie-out to **sum-of-quarterlies basis** (the lower of the two interpretations). This lets each provider's quarterly array grow monotonically into Q1 26 while preserving Q1 26 anchors at literal disclosed run-rates ÷ 4.

Final locked trajectory (per wq-092):

| Provider | Q1 25 | Q2 25 | Q3 25 | Q4 25 | Q1 26 | 2025 sum | Q4→Q1 |
|---|---|---|---|---|---|---|---|
| MSFT | $4.15 | $5.50 | $7.20 | $8.40 | $9.25 | $25.25B | +10% |
| AMZN | $1.50 | $2.20 | $2.70 | $3.60 | $3.75 | $10.00B | +4% |
| GOOGL | $0.70 | $1.40 | $2.10 | $2.80 | $3.00 | $7.00B | +7% |
| ORCL | $0.50 | $0.65 | $0.85 | $0.95 | $0.90 | $2.95B | -5% (Stargate timing) |
| Neoclouds (sum) | $1.20 | $1.37 | $1.62 | $1.86 | $2.14 | $6.05B | +15% |

The annualised run-rate numbers ($28B MSFT, $10B AMZN, $7B GOOGL) are preserved as separate context fields in `data/compute_disclosures.json` (`value_2025_annualised_run_rate_basis_usd_b`) but no longer constrain the trajectory.

Headline numbers shift slightly downward as a result: Compute gross post-Copilot ~$43.5B (was $45.55B), Compute net ~$42.5B (was $44.5B). Editorial trade is small dollar amount in exchange for a chart that visibly tells the AI growth story.

**Methodological lesson:** "Annualised run-rate" disclosures and "calendar sum-of-quarterlies" are different numbers when growth is non-linear. The Compute Ledger uses sum-of-quarterlies for trajectory + Layer Stack lookback because that's what calendar accounting reflects. The annualised run-rate is preserved as context but doesn't constrain the year-end calendar number.

Tier annotations:
- Q1 26 anchors: 1B for MSFT/AMZN (CEO/run-rate disclosures); 2A for GOOGL (run-rate-implied from narrative)
- Q1 25 anchors: 1A for MSFT (ties to current data); 2A for AMZN/GOOGL (back-cast from growth narrative — accepted)
- Interior quarters: 2A (smoothed)

## Final locked table (2026-05-06)

| Provider | AI line 2025 | Copilot | Frontier lab compute | Hosted model APIs | AI workload compute |
|---|---|---|---|---|---|
| MSFT | $28B | $7.4B | $18B | $1.5B | $1.1B |
| AMZN | $10B (Jassy-anchored) | $0 | $7B | $2.5B | $0.5B |
| GOOGL | $7B (bottom-up) | $1.5B | $3.5B | $0.5B | $1.5B |
| ORCL | $3B | $0 | $2B | $0 | $1B |
| Neoclouds (CRWV+NBIS+LMBD+CRSE) | $6.45B | $0 | $5.5B | $0 | $1B |
| **TOTAL ECOSYSTEM** | **$54.45B** | **$8.9B** | **$36B** | **$4.5B** | **$5.1B** |

- **Compute gross post-Copilot: $45.55B**
- **Pass-through (Hosted model APIs × ~23% blended): ~$1.05B**
- **Compute net 2025: ~$44.5B**
- **Frontier lab compute share of compute: 79%** (the circular-financing line dominates)

vs wq-089 shipped:

| Metric | Shipped (wq-089) | Locked (this memo) | Δ |
|---|---|---|---|
| Total AI line declared 2025 | $73.45B | $54.45B | **–$19B** |
| Copilot scope-out | $8B | $8.9B | +$0.9B |
| Compute gross post-Copilot | $65.45B | $45.55B | **–$19.9B** |
| Frontier lab compute | $50.55B | $36B | –$14.5B |
| AI workload compute | $10.40B | $5.1B | –$5.3B |
| Hosted model APIs gross | $4.50B | $4.5B | ~0 |
| Pass-through | $1.025B | $1.05B | ~0 |
| Compute net | $64.42B | $44.5B | **–$19.9B** |

## Sources cited in derivation

- **Andy Jassy** — Amazon CEO 2026 shareholder letter, "$15B annualized AI run rate" (early 2026). Hard ceiling for AWS AI 2025 calendar.
- **Microsoft Q3 FY26 earnings press release / call commentary** — "$37B AI run-rate, +123% YoY" Q1 2026.
- **Alphabet Q1 2026 earnings release + earnings call** — Google Cloud +63% YoY, $460B backlog, "13 product lines >$1B run-rate," "AI products grew nearly 800% YoY" — qualitative AI commentary, no discrete $ AI revenue figure.
- **Anthropic Q1 2026 disclosures** — 2025 revenue $4.71B; April 2026 expanded Google TPU agreement with multi-GW capacity from 2027.
- **CNBC 2025-07-16** — OpenAI taps Google Cloud for ChatGPT in specific regions.
- **Fortune 2026-04-30** — "Half of Google's and Amazon's blowout AI profits came from a stake in Anthropic — not from their actual business." Important: confirms Anthropic equity gain is non-operating; doesn't inflate Cloud AI revenue.
- **Ed Zitron / wheresyouredat** — leaked Microsoft methodology on Azure OpenAI Service rev-share (~20% to OpenAI).
- **TAIL Usage Ledger** (`usage.html:697–698`) — `frontierProvs = ['openai', 'anthropic', 'google', 'xai', 'bytedance', 'tencent', 'baidu', 'minimax', 'moonshot']`; `openProvs = ['meta', 'deepseek', 'mistral', 'alibaba', 'qwen', 'own', 'self-hosted', 'others']`. Canonical Model Provider taxonomy.
- **TAIL `wheresyouredat-claims-vs-tail.html`** — flags `entities.json:microsoft-copilot[m365-copilot].ai_arr=$13B` as stale Jan 2026 figure mislabelled.
- **TAIL Usage Ledger COGS test** — vendors claim ~$52B Trad SaaS AI; real incremental is ~$9–13B across the whole market (3.5–5% of enterprise SaaS); 0 of 10 vendors show AI-driven growth acceleration. M365 Copilot net ~$2.5–3.5B after 40–60% bundling discount; GitHub Copilot $1–2.3B; SF Agentforce $250–350M real (vs $800M claimed); NOW Assist $400–500M real.

## What this implies for wq-091

Implementation work in `wq-091-compute-ledger-bucket-sizing-correction.md`:

1. Restate `data/compute_disclosures.json` per-provider AI lines: AMZN $18B → $10B; GOOGL $18B → $7B; MSFT $28B unchanged.
2. Restate per-provider segment allocations and Copilot deductions per the Final Locked Table above.
3. Update `bucket_basis` provenance fields with new anchors (Jassy quote, GCP no-disclosure caveat, Anthropic+OpenAI on GCP, MS-declared Copilot reasoning). Rename `bucket_basis` → `segment_basis` while editing.
4. Rename JSON schema field names from `bucket_1_*` / `bucket_2_*` / `bucket_3_*` to `frontier_lab_compute_*` / `ai_workload_compute_*` / `hosted_model_apis_*`. Aggregator and validator update to match.
5. Update `entities.json:microsoft-copilot[m365-copilot].ai_arr` — drop the stale $13B label or replace with seat-math derivation.
6. Run `python3 scripts/derive_compute_revenue.py --apply` and verify summary matches Final Locked Table.
7. Update `compute.html` (most numbers propagate from site-data; verify hero strip and Frontier lab compute card render correctly with new values; ensure no "Bucket 1" / "B1" appears anywhere on the rendered page).
8. Update YoY 2024 reference number — proportional restatement of 2024 down to ~$15–18B (from $30B that shipped); YoY 2025 vs 2024 = ~+150–200% rather than +103%. This is a more aggressive (but more accurate) growth headline.
9. Update methodology page with the bottom-up segment sizing methodology and the AWS-Jassy / GCP-bottom-up anchors. Section title "three-bucket model" → "three-segment model" (or "Compute Revenue segments").
10. Update WWHBT panel: capex coverage threshold against $44.5B not $64B (Mag7 AI capex ~$320B / Compute $44.5B = 14% — falls below "tracking" threshold; this strengthens the circular-financing editorial thread).

## Reopen criteria

This memo locks numbers as of 2026-05-06. Triggers to revisit:

- Any major hyperscaler quarterly earnings disclosure that includes a discrete AI revenue figure (would tighten editorial dependency)
- Anthropic, OpenAI, or another frontier lab disclosing 2025 calendar compute spend by cloud
- Substantial change to the OpenAI cloud diversification mix (GCP / Oracle / CoreWeave shares)
- Microsoft, Google, or Amazon explicitly disclosing Copilot-class revenue separately from Compute AI
- AOAI / Bedrock / Vertex revenue disclosures that differ materially from current $4.5B Hosted model APIs ecosystem estimate

## Future memos this references

- `dec-YYYY-MM-DD-apps-ledger-copilot-real-vs-declared.md` — when the Apps Ledger is built, the MS-declared vs TAIL-derived Copilot gap and the COGS-test vendor-claim-vs-real analysis become the editorial spine. This memo records the inputs.
- `dec-YYYY-MM-DD-frontier-lab-compute-circular-financing.md` — if/when the Capital Ledger surfaces the Frontier lab compute → equity flow loop (Microsoft equity in OpenAI funding OpenAI's Azure spend), this memo's segment sizing is the input.
