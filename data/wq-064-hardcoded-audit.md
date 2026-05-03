# wq-064 Hardcoded Number Audit Report

Generated: audit_hardcoded_numbers.py

## Summary

- **Total HTML files scanned:** 22
- **Total numeric values found:** 547
- **Source state:**
  - hardcoded literals: 476 (87%)
  - hardcoded literal inside script (textContent/innerHTML): 0 (0%)
  - HTML element with id (likely wired by JS): 64 (12%)
  - script-derived: 7 (1%)
  - unclear: 0 (0%)
- **Should be derived:**
  - YES (rewire candidates): 333 (61%)
  - NO (intentionally editorial / factual): 1 (0%)
  - UNCLEAR (needs human judgment): 213 (39%)
- **Semantic category breakdown:**
  - `per_entity_metric`: 203
  - `other`: 117
  - `percentage`: 96
  - `market_aggregate`: 94
  - `ratio_derived`: 22
  - `methodology_constant`: 9
  - `scenario_assumption`: 5
  - `factual_reference`: 1

## Top 20 highest-priority rewire candidates

Ranked by visual prominence heuristic (hero text > nav > body > footer) and
hardcoded-literal status.

| # | Page | Line | Value | Context | Why it matters |
|---|---|---|---|---|---|
| 1 | `index.html` | 206 | `$745B` | "color:var(--capital);" id="hero-capex">$745B</div> | market_aggregate → should-be-derived; appears in 1 location(s) |
| 2 | `index.html` | 211 | `$22B` | olor:var(--revenue);" id="hero-revenue">$22B</div> | per_entity_metric → should-be-derived; appears in 1 location(s) |
| 3 | `index.html` | 216 | `~360T` | ="color:var(--usage);" id="hero-tokens">~360T</div> | per_entity_metric → should-be-derived; appears in 1 location(s) |
| 4 | `methodology.html` | 216 | `$22B` | <td>Home page hero ("$22B of AI revenue earned, CY23–25") and <a | per_entity_metric → should-be-derived; appears in 1 location(s) |
| 5 | `revenue.html` | 310 | `$17B` | th compounding', threshold: '3.5x+ YoY ($17B to $64B)', observed: 'On pace if H2 | per_entity_metric → should-be-derived; appears in 1 location(s) |
| 6 | `revenue.html` | 310 | `$64B` | unding', threshold: '3.5x+ YoY ($17B to $64B)', observed: 'On pace if H2 ramp su | per_entity_metric → should-be-derived; appears in 1 location(s) |
| 7 | `timeline.html` | 164 | `1M` | <h2>Blended Token Price ($/1M tokens, 70% input + 30% output, most-us | per_entity_metric → should-be-derived; appears in 1 location(s) |
| 8 | `timeline.html` | 164 | `70%` | <h2>Blended Token Price ($/1M tokens, 70% input + 30% output, most-used model)</ | per_entity_metric → should-be-derived; appears in 1 location(s) |
| 9 | `timeline.html` | 164 | `30%` | d Token Price ($/1M tokens, 70% input + 30% output, most-used model)</h2> | per_entity_metric → should-be-derived; appears in 1 location(s) |
| 10 | `usage.html` | 213 | `$1` | Actual 2025 collected revenue. Not all "$1 of AI revenue" is equal.</span></h2> | per_entity_metric → should-be-derived; appears in 1 location(s) |
| 11 | `index.html` | 11 | `$745B` | meta property="og:description" content="$745B of infrastructure investment. $22B | per_entity_metric → should-be-derived; appears in 1 location(s) |
| 12 | `openrouter.html` | 234 | `1M` | :400;color:var(--text-dim);">— output $/1M tokens, live</span></h2> | per_entity_metric → should-be-derived; appears in 2 location(s) |
| 13 | `index.html` | 236 | `$745B` | e="color:var(--accent);" id="nar-capex">$745B</div> | market_aggregate → should-be-derived; appears in 1 location(s) |
| 14 | `index.html` | 248 | `~360T` | ="color:var(--purple);" id="nar-tokens">~360T/day</div> | per_entity_metric → should-be-derived; appears in 1 location(s) |
| 15 | `index.html` | 254 | `$22B` | ="color:var(--green);" id="nar-revenue">$22B</div> | per_entity_metric → should-be-derived; appears in 1 location(s) |
| 16 | `index.html` | 284 | `$745B` | ="color:var(--accent);" id="card-capex">$745B</div> | market_aggregate → should-be-derived; appears in 1 location(s) |
| 17 | `index.html` | 295 | `$22B` | "color:var(--green);" id="card-revenue">$22B</div> | per_entity_metric → should-be-derived; appears in 1 location(s) |
| 18 | `index.html` | 306 | `~360T` | "color:var(--purple);" id="card-tokens">~360T/day</div> | per_entity_metric → should-be-derived; appears in 1 location(s) |
| 19 | `capital.html` | 189 | `100%` | ks up through 2026-27. Revenue grows 80-100% annually.">Base</button> | per_entity_metric → should-be-derived; appears in 4 location(s) |
| 20 | `capital.html` | 190 | `200%` | ive step-change in usage. Revenue grows 200%+.">Bull</button> | per_entity_metric → should-be-derived; appears in 4 location(s) |

## Suggested follow-on briefs

Grouped by data source / category. Each can become its own brief once Simon
prioritises which class to attack first.

- **Brief A: Wire methodology page constants.** `methodology_constant` candidates appear in 3 file(s) (capital.html, in-development.html, methodology.html). Move shared rates / percentages into a config file the renderer reads.
- **Brief B: Wire per-entity metric blocks.** `per_entity_metric` candidates in 15 file(s). Replace hand-edited valuations / user counts / ARR with reads from entities.json:companies[*].current.
- **Brief C: Wire remaining market aggregates.** `market_aggregate` candidates in 14 file(s). Wire to entities.json:market_aggregates.<year> or :_cumulative_2023_2025 (extends wq-063 cumulative aggregator pattern).
- **Brief D: Move scenario assumptions to data file.** `scenario_assumption` candidates in 4 file(s). Lift bear/base/bull / projection assumptions out of inline HTML into data/scenarios.json so they version-control cleanly.
- **Brief E: Compute derived ratios in JS, not literals.** `ratio_derived` candidates in 5 file(s). Ratios should be computed at render time from the values they reference, never typed in directly.

## Per-page inventory

### `about.html` (3 values)

- YES (should derive): 2
- NO (factual / fixed): 0
- UNCLEAR: 1

| Line | Value | Context | Semantic |
|---|---|---|---|
| 154 | `$5M` | inance &amp; Supply Chain business from $5M to $130M+ ARR in FY25. Bef | market_aggregate |
| 154 | `$130M` | &amp; Supply Chain business from $5M to $130M+ ARR in FY25. Before Ser | market_aggregate |

### `add.html` (3 values)

- YES (should derive): 2
- NO (factual / fixed): 0
- UNCLEAR: 1

| Line | Value | Context | Semantic |
|---|---|---|---|
| 48 | `100%` | eave empty to auto-fetch." style="width:100%;padding:10px 14px;backgro | scenario_assumption |
| 155 | `$3.4B` | pany name, e.g. 'OpenAI ended 2024 with $3.4B revenue' not 'We ended 2 | per_entity_metric |

### `ask.html` (4 values)

- YES (should derive): 2
- NO (factual / fixed): 0
- UNCLEAR: 2

| Line | Value | Context | Semantic |
|---|---|---|---|
| 117 | `$15` | uick(this)">What's the evidence for the $15:$1 investment ratio?</butt | ratio_derived |
| 117 | `$1` | (this)">What's the evidence for the $15:$1 investment ratio?</button> | ratio_derived |

### `benchmarks.html` (9 values)

- YES (should derive): 7
- NO (factual / fixed): 0
- UNCLEAR: 2

| Line | Value | Context | Semantic |
|---|---|---|---|
| 118 | `$1` | <option value="a">Series A ($1-10M ARR)</option> | per_entity_metric |
| 118 | `10M` | <option value="a">Series A ($1-10M ARR)</option> | per_entity_metric |
| 119 | `$10` | <option value="b" selected>Series B ($10-50M ARR)</option> | per_entity_metric |
| 119 | `50M` | option value="b" selected>Series B ($10-50M ARR)</option> | per_entity_metric |
| 120 | `$50` | <option value="c">Series C ($50-200M ARR)</option> | per_entity_metric |
| 120 | `200M` | <option value="c">Series C ($50-200M ARR)</option> | per_entity_metric |
| 121 | `$200M` | <option value="growth">Growth ($200M+ ARR)</option> | per_entity_metric |

### `capital.html` (83 values)

- YES (should derive): 54
- NO (factual / fixed): 0
- UNCLEAR: 29

| Line | Value | Context | Semantic |
|---|---|---|---|
| 188 | `30%` | trajectory continues. Revenue grows 20-30% annually.">Bear</button> | per_entity_metric |
| 189 | `100%` | ks up through 2026-27. Revenue grows 80-100% annually.">Base</button> | per_entity_metric |
| 190 | `200%` | ive step-change in usage. Revenue grows 200%+.">Bull</button> | per_entity_metric |
| 198 | `$745B` | <strong>$745B of AI infrastructure investment, 2023&n | market_aggregate |
| 200 | `$356B` | nchored from <strong>NVIDIA DC revenue: $356B cumulative</strong> (Tie | market_aggregate |
| 228 | `$170B` | e, and Microsoft allocate approximately $170B of AI CapEx to ad rankin | market_aggregate |
| 230 | `$34` | e ratio from <strong id="cf-ratio-from">$34:$1</strong> to <strong id= | per_entity_metric |
| 230 | `$1` | tio from <strong id="cf-ratio-from">$34:$1</strong> to <strong id="cf- | per_entity_metric |
| 230 | `$13` | 1</strong> to <strong id="cf-ratio-to">~$13:$1</strong>. | per_entity_metric |
| 230 | `$1` | trong> to <strong id="cf-ratio-to">~$13:$1</strong>. | per_entity_metric |

### `changelog.html` (20 values)

- YES (should derive): 20
- NO (factual / fixed): 0
- UNCLEAR: 0

| Line | Value | Context | Semantic |
|---|---|---|---|
| 134 | `$7.65B` | strong>OpenAI</strong> customer revenue $7.65B → $9.31B (+22%), provid | market_aggregate |
| 134 | `$9.31B` | enAI</strong> customer revenue $7.65B → $9.31B (+22%), provider node S | market_aggregate |
| 134 | `22%` | ong> customer revenue $7.65B → $9.31B (+22%), provider node STABLE at  | market_aggregate |
| 134 | `$13.65B` | $9.31B (+22%), provider node STABLE at $13.65B, vc_subsidy $5.20B → $4 | market_aggregate |
| 134 | `$5.20B` | ider node STABLE at $13.65B, vc_subsidy $5.20B → $4.34B (the architect | market_aggregate |
| 134 | `$4.34B` | STABLE at $13.65B, vc_subsidy $5.20B → $4.34B (the architectural inten | market_aggregate |
| 134 | `$2.00B` | strong>Google</strong> customer revenue $2.00B → $2.25B and provider n | market_aggregate |
| 134 | `$2.25B` | ogle</strong> customer revenue $2.00B → $2.25B and provider node $2.50 | market_aggregate |
| 134 | `$2.50B` | venue $2.00B → $2.25B and provider node $2.50B → $2.93B (+17%), engine | market_aggregate |
| 134 | `$2.93B` | 00B → $2.25B and provider node $2.50B → $2.93B (+17%), engine-estimate | market_aggregate |

### `claims.html` (4 values)

- YES (should derive): 0
- NO (factual / fixed): 0
- UNCLEAR: 4

### `confidence.html` (2 values)

- YES (should derive): 0
- NO (factual / fixed): 0
- UNCLEAR: 2

### `follow-the-trillion.html` (34 values)

- YES (should derive): 4
- NO (factual / fixed): 0
- UNCLEAR: 30

| Line | Value | Context | Semantic |
|---|---|---|---|
| 252 | `$34T` | ass="ftbt-value val-red" id="val-capex">$34T</div> | market_aggregate |
| 253 | `$1` | detail-capex-ratio">34</span> capex per $1 earned = $<span id="detail- | market_aggregate |
| 336 | `$34` | const CAPEX_RATIO = 34; // $34 capex per $1 AI revenue (Ledger finding | per_entity_metric |
| 336 | `$1` | onst CAPEX_RATIO = 34; // $34 capex per $1 AI revenue (Ledger finding) | per_entity_metric |

### `in-development.html` (11 values)

- YES (should derive): 11
- NO (factual / fixed): 0
- UNCLEAR: 0

| Line | Value | Context | Semantic |
|---|---|---|---|
| 143 | `$200B` | <p>Interactive analysis of the $200B+ gap between AI infrastructure sp | per_entity_metric |
| 195 | `$260B` | king counter of AI industry investment: $260B/yr ($711M/day). Rate car | methodology_constant |
| 195 | `$711M` | er of AI industry investment: $260B/yr ($711M/day). Rate cards, cost b | methodology_constant |
| 195 | `$15` | ). Rate cards, cost breakdown, and the "$15 per $1" context.</p> | methodology_constant |
| 195 | `$1` | cards, cost breakdown, and the "$15 per $1" context.</p> | methodology_constant |
| 250 | `$218` | prise SaaS and AI-specific SKU revenue. $218-465B market breakdown wit | market_aggregate |
| 250 | `465B` | SaaS and AI-specific SKU revenue. $218-465B market breakdown with ente | market_aggregate |
| 322 | `$310B` | <p>Full $310B capital flow from GPU silicon to tokens | per_entity_metric |
| 322 | `$130B` | Cross-checks against NVIDIA DC revenue ($130B). Shows depreciation rea | per_entity_metric |
| 335 | `90%` | ns to revenue. GPU supply chain (NVIDIA 90% share), data centre econom | market_aggregate |

### `index.html` (45 values)

- YES (should derive): 29
- NO (factual / fixed): 0
- UNCLEAR: 16

| Line | Value | Context | Semantic |
|---|---|---|---|
| 11 | `$745B` | meta property="og:description" content="$745B of infrastructure invest | per_entity_metric |
| 11 | `$22B` | nt="$745B of infrastructure investment. $22B of AI revenue. ~360T toke | per_entity_metric |
| 11 | `~360T` | ructure investment. $22B of AI revenue. ~360T tokens/day. The full AI  | per_entity_metric |
| 189 | `30%` | trajectory continues. Revenue grows 20-30% annually, tokens follow.">B | per_entity_metric |
| 190 | `100%` | ks up through 2026-27. Revenue grows 80-100% annually.">Base</button> | per_entity_metric |
| 191 | `200%` | ive step-change in usage. Revenue grows 200%+.">Bull</button> | per_entity_metric |
| 206 | `$745B` | "color:var(--capital);" id="hero-capex">$745B</div> | market_aggregate |
| 211 | `$22B` | olor:var(--revenue);" id="hero-revenue">$22B</div> | per_entity_metric |
| 216 | `~360T` | ="color:var(--usage);" id="hero-tokens">~360T</div> | per_entity_metric |
| 236 | `$745B` | e="color:var(--accent);" id="nar-capex">$745B</div> | market_aggregate |

### `ipo-watch.html` (18 values)

- YES (should derive): 18
- NO (factual / fixed): 0
- UNCLEAR: 0

| Line | Value | Context | Semantic |
|---|---|---|---|
| 124 | `$64B` | 'Foundation Model', hq: 'US', funding: '$64B', note: 'Jensen expects I | per_entity_metric |
| 125 | `$17B` | 'Foundation Model', hq: 'US', funding: '$17B', note: '$6B revenue in F | per_entity_metric |
| 125 | `$6B` | del', hq: 'US', funding: '$17B', note: '$6B revenue in February alone. | per_entity_metric |
| 125 | `$380B` | , note: '$6B revenue in February alone. $380B valuation at 27x ARR. IP | per_entity_metric |
| 126 | `$19B` | egory: 'Data + AI', hq: 'US', funding: '$19B', note: 'Unity Catalog an | per_entity_metric |
| 127 | `$1.6B` | egory: 'GPU Cloud', hq: 'US', funding: '$1.6B', note: 'Filed S-1 March | per_entity_metric |
| 128 | `$9.4B` | ry: 'Fintech + AI', hq: 'US', funding: '$9.4B', note: 'Not pure AI but | per_entity_metric |
| 129 | `$1.6B` | AI Infrastructure', hq: 'US', funding: '$1.6B', note: 'Data labeling s | per_entity_metric |
| 130 | `$900M` | ory: 'AI Dev Tool', hq: 'US', funding: '$900M', note: '$1B+ ARR in 2 y | per_entity_metric |
| 130 | `$1B` | ol', hq: 'US', funding: '$900M', note: '$1B+ ARR in 2 years. 10x reven | per_entity_metric |

### `methodology.html` (34 values)

- YES (should derive): 15
- NO (factual / fixed): 0
- UNCLEAR: 19

| Line | Value | Context | Semantic |
|---|---|---|---|
| 185 | `55%` | lings. Silicon represents approximately 55% of total CapEx; the remain | market_aggregate |
| 195 | `50%` | sures. China accounts for approximately 50% of global volume. No singl | methodology_constant |
| 199 | `1B` | n 2b: ARR vs collected revenue (wq-032 P1B closes wq-035 F2) --> | per_entity_metric |
| 216 | `$22B` | <td>Home page hero ("$22B of AI revenue earned, CY23–25") and <a | per_entity_metric |
| 221 | `$25B` | ample, OpenAI's reported ARR was around $25B (Q1 2026 run-rate) while  | per_entity_metric |
| 221 | `$4.3B` | e its 2025 collected revenue was around $4.3B — the same company, two  | per_entity_metric |
| 222 | `$6B` | . Anthropic's 2026 collected revenue at $6B from the wq-028 P1.6 repla | per_entity_metric |
| 222 | `1B` | tile, by editorial choice (wq-032 Phase 1B). The dashboard tile is int | per_entity_metric |
| 251 | `1B` | <tr><td class="tier-code">1B</td><td class="tier-label">Corroborated | methodology_constant |
| 251 | `15%` | dent reporting sources agreeing within ~15%</td></tr> | methodology_constant |

### `openrouter.html` (40 values)

- YES (should derive): 24
- NO (factual / fixed): 0
- UNCLEAR: 16

| Line | Value | Context | Semantic |
|---|---|---|---|
| 152 | `1.9T` | olor:var(--text-dim);"> Portkey handles 1.9T tokens/day for enterprise | per_entity_metric |
| 152 | `3,200B` | hrough 2-3 providers. OpenRouter serves 3,200B+ tokens/day across 400+ | per_entity_metric |
| 182 | `85,247` | im);padding:2px 8px;background:rgba(168,85,247,0.1);border-radius:4px; | per_entity_metric |
| 182 | `1.9T` | gba(168,85,247,0.1);border-radius:4px;">1.9T tokens/day · $1.3M/day</s | per_entity_metric |
| 182 | `$1.3M` | );border-radius:4px;">1.9T tokens/day · $1.3M/day</span> | per_entity_metric |
| 210 | `24K` | ortkey serves enterprise/production AI (24K orgs) while OpenRouter ske | per_entity_metric |
| 210 | `2.5M` | le OpenRouter skews developer/prosumer (2.5M users). Comparing their m | per_entity_metric |
| 210 | `30%` | Key finding: Claude dominates Portkey (~30% of traffic) while OpenRout | per_entity_metric |
| 217 | `1M` | /div><div class="lbl">Cheapest Output $/1M</div></div> | ratio_derived |
| 218 | `1M` | </div><div class="lbl">Most Expensive $/1M</div></div> | ratio_derived |

### `power.html` (1 values)

- YES (should derive): 0
- NO (factual / fixed): 0
- UNCLEAR: 1

### `predictions.html` (55 values)

- YES (should derive): 38
- NO (factual / fixed): 0
- UNCLEAR: 17

| Line | Value | Context | Semantic |
|---|---|---|---|
| 131 | `$14B` | s exceed revenue at gross margin level. $14B inference cost vs $17.5B  | market_aggregate |
| 131 | `$17.5B` | ss margin level. $14B inference cost vs $17.5B total customer revenue  | market_aggregate |
| 132 | `80%` | en customers see it', 'Price deflation ~80%/yr makes margin harder not | market_aggregate |
| 133 | `150%` | evidence_against: ['Revenue growing 150%+ YoY could outpace costs', 'H | per_entity_metric |
| 137 | `40%` | ediction: 'Open model share will exceed 40% of production inference to | per_entity_metric |
| 143 | `35%` | 'OpenRouter data shows open models at ~35% of token volume and growing | per_entity_metric |
| 143 | `85%` | rowing fastest. Jason Calacanis reports 85% of startup tokens now on o | per_entity_metric |
| 144 | `54%` | Xiaomi + MiniMax + DeepSeek + Stepfun = 54% of non-frontier volume', ' | market_aggregate |
| 144 | `85%` | Stepfun = 54% of non-frontier volume', '85% of startup tokens on open  | market_aggregate |
| 145 | `28%` | haven\'t closed yet', 'Coding use case (28% of all tokens) strongly fa | market_aggregate |

### `revenue.html` (69 values)

- YES (should derive): 59
- NO (factual / fixed): 0
- UNCLEAR: 10

| Line | Value | Context | Semantic |
|---|---|---|---|
| 110 | `30%` | trajectory continues. Revenue grows 20-30% annually.">Bear</button> | per_entity_metric |
| 111 | `100%` | ks up through 2026-27. Revenue grows 80-100% annually.">Base</button> | per_entity_metric |
| 112 | `200%` | ive step-change in usage. Revenue grows 200%+.">Bull</button> | per_entity_metric |
| 140 | `20%` | el Providers &mdash; Hyperscalers clip ~20%, Trad. SaaS ~60%. That ret | per_entity_metric |
| 140 | `60%` | sh; Hyperscalers clip ~20%, Trad. SaaS ~60%. That retained margin flow | per_entity_metric |
| 162 | `30%` | revenue: 17, label: 'Bear', growth: '20-30%', multiplier: { '2025': 1. | per_entity_metric |
| 163 | `100%` | revenue: 22, label: 'Base', growth: '80-100%', multiplier: { '2025': 1 | per_entity_metric |
| 164 | `200%` | { revenue: 27, label: 'Bull', growth: '200%+', multiplier: { '2025': 1 | per_entity_metric |
| 275 | `1B` | +scenarioTier+' '+tierPill(yr==='2025'?'1B':'3C')+'</div><div class="k | per_entity_metric |
| 277 | `1B` | +scenarioTier+' '+tierPill(yr==='2025'?'1B':'3A')+'</div><div class="k | market_aggregate |

### `review.html` (15 values)

- YES (should derive): 0
- NO (factual / fixed): 0
- UNCLEAR: 15

### `subsidy-clock.html` (10 values)

- YES (should derive): 10
- NO (factual / fixed): 0
- UNCLEAR: 0

| Line | Value | Context | Semantic |
|---|---|---|---|
| 150 | `$260B` | DATA.capex + DATA.vcSubsidy) * 1e9; // ~$260B | market_aggregate |
| 190 | `$1` | + ratio + ' invested', desc: 'for every $1 of customer revenue collect | market_aggregate |
| 191 | `$125B` | r infrastructure in 2025 alone. Meta\'s $125B is the single largest li | market_aggregate |
| 192 | `$2.15B` | rovider loses money serving tokens. The $2.15B of "margin" in the syst | market_aggregate |
| 215 | `$250B` | g>Methodology:</strong> Capex estimate ($250B) from industry reports,  | market_aggregate |
| 215 | `$115` | industry reports, Meta public guidance ($115-135B), and All-In podcast | market_aggregate |
| 215 | `135B` | try reports, Meta public guidance ($115-135B), and All-In podcast clai | market_aggregate |
| 215 | `$50B` | B), and All-In podcast claims (Chamath: $50B/GW data centre cost). ' + | market_aggregate |
| 216 | `$9.8B` | 'VC subsidy ($9.8B) is the gap between customer revenue an | per_entity_metric |
| 217 | `$17.47B` | 'Customer revenue ($17.47B) is consensus-weighted from public fili | per_entity_metric |

### `timeline.html` (11 values)

- YES (should derive): 7
- NO (factual / fixed): 0
- UNCLEAR: 4

| Line | Value | Context | Semantic |
|---|---|---|---|
| 164 | `1M` | <h2>Blended Token Price ($/1M tokens, 70% input + 30% output, most-us | per_entity_metric |
| 164 | `70%` | <h2>Blended Token Price ($/1M tokens, 70% input + 30% output, most-use | per_entity_metric |
| 164 | `30%` | d Token Price ($/1M tokens, 70% input + 30% output, most-used model)</ | per_entity_metric |
| 168 | `1B` | <!-- wq-032 P1B: FY revenue surface — audited fiscal-ye | per_entity_metric |
| 258 | `1M` | kGrid, title: { display: true, text: '$/1M output tokens (log)' } }, x | per_entity_metric |
| 377 | `16,185,129` | (c === 'high') return 'background:rgba(16,185,129,0.15);color:#10b981; | scenario_assumption |
| 378 | `245,158` | c === 'medium') return 'background:rgba(245,158,11,0.15);color:#f59e0b | scenario_assumption |

### `usage.html` (35 values)

- YES (should derive): 12
- NO (factual / fixed): 0
- UNCLEAR: 23

| Line | Value | Context | Semantic |
|---|---|---|---|
| 185 | `30%` | trajectory continues. Revenue grows 20-30% annually.">Bear</button> | per_entity_metric |
| 186 | `100%` | ks up through 2026-27. Revenue grows 80-100% annually.">Base</button> | per_entity_metric |
| 187 | `200%` | ive step-change in usage. Revenue grows 200%+.">Bull</button> | per_entity_metric |
| 201 | `$22B` | latform workloads). The home page shows $22B customer revenue (CY23–25 | market_aggregate |
| 213 | `$1` | Actual 2025 collected revenue. Not all "$1 of AI revenue" is equal.</s | per_entity_metric |
| 288 | `80%` | n">Token volume growth compounding &ge; 80% YoY</div> | per_entity_metric |
| 506 | `1B` | 4 <span class="tier-pill tier-2a">Tier 1B/2A</span></div><div class="k | market_aggregate |
| 513 | `2013370T` | lti-model consensus range: <strong>280\u2013370T/day</strong> (v3 mode | market_aggregate |
| 513 | `~280T` | g> (v3 model, Apr 2026). Bear scenario (~280T) reflects possible overc | market_aggregate |
| 513 | `~500T` | ) reflects possible overcounting; Bull (~500T) reflects unmeasured sel | market_aggregate |

### `vault.html` (41 values)

- YES (should derive): 19
- NO (factual / fixed): 1
- UNCLEAR: 21

| Line | Value | Context | Semantic |
|---|---|---|---|
| 298 | `16,185,129` | 200px;padding:16px 20px;background:rgba(16,185,129,0.08);border:1px so | ratio_derived |
| 298 | `16,185,129` | (16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);border-radius: | ratio_derived |
| 302 | `92,246` | x;padding:16px 20px;background:rgba(139,92,246,0.08);border:1px solid  | ratio_derived |
| 302 | `92,246` | ,92,246,0.08);border:1px solid rgba(139,92,246,0.2);border-radius:10px | ratio_derived |
| 306 | `59,130,246` | 200px;padding:16px 20px;background:rgba(59,130,246,0.08);border:1px so | ratio_derived |
| 306 | `59,130,246` | (59,130,246,0.08);border:1px solid rgba(59,130,246,0.2);border-radius: | ratio_derived |
| 310 | `6,182,212` | 200px;padding:16px 20px;background:rgba(6,182,212,0.08);border:1px sol | ratio_derived |
| 310 | `6,182,212` | a(6,182,212,0.08);border:1px solid rgba(6,182,212,0.2);border-radius:1 | ratio_derived |
| 409 | `$600M` | ontext (optional): e.g. 'AI ARR is only $600M, not total company reven | market_aggregate |
| 409 | `100%` | ot total company revenue'" style="width:100%;padding:8px 12px;backgrou | market_aggregate |


---

## Heuristic limitations

- Classifier conflates dollar values inside CSS/SVG `viewBox` attrs with data
  values when they're not stripped. Style/SVG blocks are excluded but inline
  fragments may still leak through; spot-check before treating any single
  value as authoritative.
- "HTML element with id (likely wired)" is inferred from `id=` presence on
  the same line; doesn't actually verify a JS file populates the element.
- `should_be_derived=UNCLEAR` is a hold-back when keyword cues don't fire.
  Especially common for percentages, where some are methodology constants
  and some are composition splits.
- `factual_reference` matches on a small keyword list ("founded", "since",
  "year:") — newly-phrased facts will fall to `other`.
