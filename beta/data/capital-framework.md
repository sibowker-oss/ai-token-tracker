# AI Industry Capital Framework — Full Cost Structure

**Created:** 2026-04-08
**Purpose:** Map the complete capital flow from GPU silicon → data centres → training → inference → revenue, with cross-checks against NVIDIA sales and provider burn rates.

---

## 1. The Framework

The revenue Sankey tracks operating flows (customer $ in → provider costs out). This framework tracks the FULL capital picture:

```
                    CAPITAL SOURCES
                    ┌─────────────┐
                    │  VC/Private  │ $120B+ raised (OpenAI $122B, Anthropic $30B, etc.)
                    │  Equity      │
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │  Hyperscaler │ $250B+ Mag 7 capex
                    │  Capex       │ (Meta $115-135B, MSFT $55B, GOOG $50B, AMZN $40B)
                    └──────┬──────┘
                           │
                           ▼
              ┌────────────────────────┐
              │      GPU PURCHASES     │  ← Cross-check: NVIDIA $130B DC revenue
              │  Training + Inference  │     AMD $12B, Custom chips (TPU, Trainium)
              └────────┬───────────────┘
                       │
            ┌──────────┴──────────┐
            │                     │
            ▼                     ▼
    ┌───────────────┐    ┌────────────────┐
    │   TRAINING    │    │   INFERENCE    │
    │  $30-50B/yr   │    │   $14B/yr      │  ← Revenue Sankey captures this
    │  (one-off per │    │  (ongoing,     │
    │   model gen)  │    │   serves tokens)│
    └───────────────┘    └────────────────┘
                                │
                                ▼
                    ┌───────────────────┐
                    │  CUSTOMER REVENUE │  $17.5B (2025)
                    │  (what we track   │
                    │   in the Sankey)  │
                    └───────────────────┘
```

---

## 2. Provider-Level Capital Table (2025)

### What we know vs need

| Provider | Customer Rev | Operating Loss | Inference Cost | Training Cost | GPU Spend | Total Capital Need | VC Raised | Source Quality |
|---|---|---|---|---|---|---|---|---|
| OpenAI | $7.65B | $6.0B | $10.0B | $10-15B | ? | $25-30B | $122B cumulative | Zitron (inference), multiple (loss) |
| Anthropic | $4.71B | $3-5.2B | $4-5B | $3-5B | ? | $10-15B | $30B cumulative | Court filing (rev), Sacra (loss) |
| Google (Gemini) | $2.0B | subsidised | ? | $5-10B | ? | ? | Internal (Alphabet) | Earnings (cloud rev) |
| Meta (Llama) | $0 | N/A | ? | $5-10B | ? | $38B capex | Internal | Earnings (capex) |
| DeepSeek | $0.3B | ? | ? | $0.006B (V3) | ? | ? | ? | Press (V3 cost) |
| Mistral | $0.4B | ? | ? | ? | ? | ? | $0.6B raised | Press |
| xAI | $0.5B | ? | ? | ? | ? | ? | $12B raised | Press |
| **Totals** | **$15.6B** | **$9-11B** | **$14-15B** | **$30-50B** | **$130B NVIDIA** | | | |

### The cross-check triangle

```
NVIDIA DC Revenue ($130B) should ≈ 
  Provider GPU purchases for inference ($40-60B)
  + Provider GPU purchases for training ($30-50B)  
  + Hyperscaler GPU for cloud hosting ($20-30B)
  + Enterprise GPU purchases ($10-20B)
  = $100-160B ← Range brackets NVIDIA's $130B ✓
```

---

## 3. Full Capital Structure Per Provider

### OpenAI (2025)

| Line item | Value | Source | Confidence |
|---|---|---|---|
| **Revenue** | | | |
| Customer revenue (collected) | $7.65B | Consensus | Corroborated |
| | | | |
| **Operating costs** | | | |
| Inference compute | $10.0B | Zitron (H1=$5.022B x2) | Authoritative |
| People/R&D | $13.4B | Zitron (H1=$6.7B R&D) | Authoritative |
| Sales & marketing | $4.0B | Zitron (H1=$2B) | Authoritative |
| Stock-based comp | $6.0B | Zitron ($1.5M/employee avg) | Authoritative |
| Other operating | $2.0B | Estimate | Editorial |
| **Total operating** | **$35.4B** | | |
| **Operating loss** | **-$27.8B** | | |
| | | | |
| **Capital costs** | | | |
| Training compute (GPT-5 etc) | $10-15B | Estimate based on GPT-4 $79M x scaling | Editorial |
| GPU capex (purchased/leased) | ? | Unknown — mostly via Azure | |
| DC construction share | ? | Via Microsoft partnership | |
| **Total capital need** | **$45-55B** | | |
| | | | |
| **Funded by** | | | |
| Customer revenue | $7.65B | | |
| Microsoft (Azure credits/infra) | ~$10-15B | Estimated | Editorial |
| VC/equity raised | $122B cumulative | Authoritative | |
| Debt (credit facility) | $4.7B available | Authoritative | |

### Anthropic (2025)

| Line item | Value | Source | Confidence |
|---|---|---|---|
| Customer revenue | $4.71B | Consensus | Corroborated |
| Inference compute | $4-5B | Derived (55% of system cost) | Derived |
| People/R&D/SGA | $3-4B | Estimate | Editorial |
| Operating loss | $3-5.2B | Sacra ($3B cash burn) / derived ($5.2B) | Mixed |
| Training compute | $3-5B | Estimate | Editorial |
| Total capital need | $12-18B | | |
| AWS partnership | $8B (Amazon total) | Authoritative | |
| VC raised | $30B cumulative | | |

---

## 4. Industry-Level Capital Flow (2025)

### Sources of capital

| Source | Amount | What it funds |
|---|---|---|
| Customer revenue | $17.5B | Operating costs (partially) |
| VC/private equity raised | $33.9B (2024 GenAI) | Operating losses + training |
| Hyperscaler capex | $250B+ | GPU purchases, DC construction |
| Debt/credit facilities | ~$10B+ | Working capital |
| **Total capital deployed** | **~$310B+** | |

### Uses of capital

| Use | Amount | Cross-check |
|---|---|---|
| **Inference compute** | $14B | Revenue Sankey outcome |
| **People/SGA/R&D** | $11B | Revenue Sankey outcome |
| **Training compute** | $30-50B | Epoch AI, model cost estimates |
| **GPU hardware purchases** | $130B+ | NVIDIA DC revenue = $130B |
| **DC construction** | $50-80B | $50B/GW x 1-2GW built in 2025 |
| **Operating margin (SaaS)** | $2.3B | Revenue Sankey outcome |
| **Cash reserves/runway** | $20-30B | Unspent VC |
| **Total** | **~$310B+** | |

### The NVIDIA cross-check

| GPU buyer category | Estimated spend | % of NVIDIA $130B |
|---|---|---|
| Hyperscaler own-use (training) | $40-50B | 35% |
| Hyperscaler resale (cloud GPU) | $30-40B | 27% |
| AI providers direct (inference) | $20-30B | 19% |
| Enterprise/other | $15-20B | 13% |
| Neo-cloud (CoreWeave etc) | $8-12B | 8% |
| **Total** | **$115-150B** | Brackets $130B ✓ |

---

## 5. Depreciation & Amortisation Model

GPUs and DC infrastructure depreciate over different periods:

| Asset | Useful life | Annual depreciation rate | Industry spend | Annual depreciation |
|---|---|---|---|---|
| GPUs (H100/B200) | 3-4 years | 25-33% | $130B purchased in 2025 | $33-43B/yr starting 2026 |
| Data centres | 15-20 years | 5-7% | $50-80B built in 2025 | $3-5B/yr |
| Training models | 12-18 months | 67-100% | $30-50B spent in 2025 | $30-50B (fully expensed or 1yr amort) |

### Impact on "true profitability"

```
Generated Cashflow (from Sankey)           $2.3B (2025)
- GPU depreciation (from 2024+2025 buys)  -$50B+ 
- DC depreciation                          -$4B
- Training amortisation                    -$40B
= True economic profit                    -$92B (massive loss)
```

This is why VC subsidy looks small in the revenue Sankey ($9.8B) — it only covers the operating gap. The capital gap ($250B+ in capex) is funded separately and depreciated over years.

**The path to true profitability requires:**
1. Revenue growing to cover operating costs (happening — Sankey shows Operating Cash emerging by 2026)
2. Revenue ALSO growing to cover annual depreciation on cumulative capex (NOT happening — $50B+/yr depreciation far exceeds any foreseeable operating cash)
3. OR: capex creates an asset (GPU fleet, DC portfolio) that generates returns beyond the AI revenue flow (cloud hosting, enterprise infrastructure)

---

## 6. What Data We Need to Complete This

| Data point | Impact | Potential source |
|---|---|---|
| OpenAI total GPU spend (own vs Azure) | Completes OpenAI capital stack | Zitron, leaked docs |
| Anthropic total GPU spend (own vs AWS) | Completes Anthropic capital stack | AWS partnership disclosures |
| Google AI-specific capex (split from total) | Major gap | Alphabet earnings deep dive |
| Training cost per model generation | Validates $30-50B industry training | Model cards, research papers |
| GPU depreciation policies per provider | Validates depreciation model | SEC filings (CoreWeave S-1) |
| Hyperscaler GPU resale margin | Validates cloud GPU economics | Cloud pricing analysis |

---

## 7. Visual Concept: Capital Sankey

The revenue Sankey shows operating flows. A "Capital Sankey" would show the full picture:

**Column 1: Capital Sources**
- Customer Revenue ($17.5B)
- VC/Equity ($34B)
- Hyperscaler Capex ($250B)
- Debt ($10B)

**Column 2: What It Buys**
- GPU Hardware ($130B)
- Data Centres ($60B)
- People/Operations ($25B)
- Training Compute ($40B)
- Cash Reserves ($25B)

**Column 3: Who Uses It**
- OpenAI ($45B)
- Anthropic ($15B)
- Google ($50B internal)
- Meta ($38B capex)
- Hyperscaler cloud ($40B)
- Others ($20B)

**Column 4: What It Produces**
- Inference capacity (320T tokens/day)
- Training capability (next-gen models)
- DC infrastructure (X GW capacity)
- Revenue ($17.5B flowing back)

This would sit alongside the revenue Sankey as the "infrastructure view" on the Compute Stack page.
