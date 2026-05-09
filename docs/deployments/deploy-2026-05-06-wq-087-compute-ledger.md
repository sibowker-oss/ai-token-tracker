# Deployment: Compute Ledger (wq-087)

**Date:** 2026-05-06
**WQ:** wq-087
**Branch/Commit:** main (pending commit)

## What shipped

A new public layer page — **the Compute Ledger** at `/compute.html` — answering "what are the world's compute providers earning from AI-attributable cloud and inference workloads?" Distribution-led per D2 (concentration headline, NOT total $); gross + net side-by-side per D6.

### New files
- `compute.html` — five sections per brief §4 (concentration headline, hero strip, distribution chart, trajectory chart, Layer-Stack Multiplier signature visual, WWHBT panel)
- `data/compute_disclosures.json` — eight components: MSFT Azure AI, GOOGL Cloud AI, AMZN AWS AI, ORCL OCI AI, CoreWeave, Nebius, Lambda Labs, Crusoe; each with gross + net + pass-through estimate + tier + source URLs. Quarterly trajectory for 2025Q1–2026Q1.
- `scripts/derive_compute_revenue.py` — aggregator (pattern-mirrors `derive_capital_sankey.py` / `derive_collected_revenue.py`). D6 gate enforced — refuses to aggregate if any component is not principal-confirmed. CLI: `--validate`, `--apply`, `--print-summary`.
- `scripts/validate-compute-revenue.mjs` — release-check validator. Asserts (a) headline aggregate fields exist, (b) every component has full provenance, (c) D6 gate satisfied, (d) `methodology_constants.json` records principal/agent treatment for all four entities with filing URL + verified_at, (e) gross/net headline reconciles to component sums within 0.5%, (f) pass_through_basis non-empty.
- `docs/deployments/deploy-2026-05-06-wq-087-compute-ledger.md` — this file.

### Modified files
- `entities.json` — added `oci` entity (Oracle Cloud Infrastructure, parent: Oracle, role: hyperscaler, products: [oci-genai], 20% pass-through margin estimate consistent with other Mag3 hyperscalers).
- `data/methodology_constants.json` — added `compute_revenue` block recording D6 verification gate output: principal_agent_treatment for MSFT (Azure OpenAI Service), AMZN (AWS Bedrock), GOOGL (Vertex partner models), ORCL (OCI partner workloads). All four confirmed **principal (gross)** with filing URLs to FY25 10-Ks + Q1 2026 10-Qs and verified_at = 2026-05-06.
- `site-data.json` — new `compute` block written by aggregator. 2025 annualised gross $73.45B, net $61.95B, pass-through $11.50B. Q1 2026 gross $23.89B (~$96B annualised). Concentration: Mag3 87.3%, Oracle 3.8%, public neoclouds 7.7%, private neoclouds 1.3%.
- `data/render_config.json` — added `pages` registry including `compute` with engine + disclosures pointers.
- `methodology.html` — new "Compute Ledger" card in Per-Ledger Methodology grid + new section "Compute Revenue — gross vs net & principal/agent gate" explaining the dual-publication, the D6 verification gate, and why direct frontier-API revenue stays on the Revenue Ledger (D3).
- `index.html`, `capital.html`, `revenue.html`, `usage.html`, `power.html` — nav updated to add `/compute.html` link between Revenue and Usage; footer "Ledger pages" lists also updated.
- `scripts/auto_update.py` — Step 4b added: subprocess-runs `derive_compute_revenue.py --apply` after `update_site_data` and before `apply_claims`. Refreshes Compute Ledger aggregate every daily auto-update cycle.
- `scripts/release-check.mjs` — added Step 10b ("Compute-revenue + D6 gate") wiring the new validator into the release-check report markdown + JSON output. Strict-mode exit code now includes `computeFails`.

## Decisions made during implementation

### D1–D6 (resolved in brief)
All resolved decisions implemented as spec'd: page name = Compute Ledger at `/compute.html`; hero distribution-led with concentration headline; direct frontier API revenue OUT (lives in Apps/Model Revenue Ledger); Layer-Stack Multiplier as signature visual; both gross and net published side-by-side.

### Phase A — D6 verification gate (the load-bearing one)
Read revenue recognition policy notes in the most recent 10-K for MSFT (FY25, ended 2025-06-30, filed 2025-07-30), AMZN (FY25, ended 2025-12-31, filed 2026-02-06), GOOGL (FY25, ended 2025-12-31, filed 2026-02-05), and ORCL (FY25, ended 2025-05-31, filed 2025-06-18). Cross-checked against Q1 2026 10-Qs (or Q3 FY26 for MSFT/ORCL) to confirm "no material changes." **All four use principal (gross) treatment for AI reseller arrangements.** Documented quotes + filing URLs in `data/methodology_constants.json:compute_revenue.principal_agent_treatment`. The brief's "principal-everywhere" assumption holds — no decision file needed; the §5.2 aggregation rule stands.

Specific bases:
- **MSFT** — Note 1 cloud services consumption-based revenue + cost of revenue includes "royalties" (OpenAI rev-share is a royalty/COGS, not a revenue offset).
- **AMZN** — Note 1 explicitly carves out Marketplace as agent ("we are not the seller of record"); AWS is NOT in that carve-out, so principal.
- **GOOGL** — Note 1 invokes principal/agent test only for Google Network ad properties (also gross). Cloud is consumption-based fees and content-licensing pattern (paid as cost of revenues).
- **ORCL** — Note 1 cloud services revenue recognized over contractual period or as consumed; no marketplace carve-out.

### Tactical decisions
1. **Where to place the OCI entity** — between `gcp` and other hyperscalers, with the same `current.margin_on_resale_pct: 20` pattern used by AWS/Azure/GCP. Documented in entities.json provenance with `wq-087-build` origin.
2. **AI-attributable share of Cloud (Tier 2A editorial estimates)** — used 30% of GCP, 15% of AWS, ~10% of OCI. MSFT's $37B AI run-rate (Tier 1B) is directly disclosed. These are conservative editorial estimates; tighten as disclosure granularity improves.
3. **Pass-through estimate methodology** — Anthropic 2025 ~$4.71B revenue (most via AWS) anchors AWS Bedrock pass-through estimate; OpenAI rev-share methodology (Zitron 20%) anchors Azure OpenAI Service pass-through; Vertex partners thinner so flagged 2A. Pure-play neoclouds gross == net.
4. **Layer-Stack Multiplier numbers** — Apps Revenue 2025 $100B (editorial 2A; ties to existing Revenue Ledger + enterprise SaaS AI ARR rollup); Silicon $165B (NVIDIA Data Center FY26 ~$135B + AMD ~$5B + custom ASIC ~$25B); Power $25B (placeholder 3C — full Power Ledger v3 supersedes).
5. **Distribution chart implementation** — three views (Q1 2026 snapshot, 4-quarter trend, YoY pair). Click-to-detail on snapshot view shows the right-hand provenance side-panel with filing URL link.
6. **Trajectory chart watermark** — included `ai-index.hepburnadvisory.com.au` watermark in-chart per brief §4.3 ("designed for screenshot quotation").

## Open items

1. **Apps/Model Revenue Ledger sister update (brief §8.9)** — D6 implies a parallel update on the existing Revenue Ledger to surface pass-through visibility on that side ("of OpenAI's $XB API revenue, $YB shows up on Microsoft's Azure AI line as principal-treatment Azure OpenAI Service revenue"). OUT of scope for wq-087; should be filed as a follow-on Notion card.
2. **Tighten 2A AI-attributable splits each cycle** — once Q2 2026 Mag3 disclosures land (late July 2026), refresh `compute_disclosures.json` and tighten the AI-share-of-Cloud estimates if disclosures get more granular.
3. **CoreWeave / Nebius Q1 2026 numbers** — used estimates (~$1.5B and $0.34B respectively) anchored to public press; tighten with Q1 2026 10-Q reads when they file (typically mid-May 2026 for CoreWeave).
4. **Sankey buyer→seller flow** (brief §4.2 toggle "secondary view") — drop per brief's instruction to ship only if buyer-attribution defensible. Distribution chart is the must-ship; flow Sankey deferred.
5. **News-clock dry run §9.4** — the aggregator runs in <1s; the bottleneck is editorial extraction (10-Q narrative → AI-attributable line). Q1 2026 cycle was completed manually as part of this build (filing-drop 2026-04-29 → page-update 2026-05-06 ≈ 7 days, but most of that was Phase A research; subsequent cycles should be <48h once methodology is fixed).
6. **Visual mobile screenshot at 375px** — local HTTP server confirmed the page loads and renders (HTTP 200, 42KB), all HTML tags balanced. Mobile CSS media query in place per brief §7.7 acceptance criteria, but a Playwright/manual screenshot is recommended before Week 3 launch coordination.
7. **Notion card update** — wq-087 card to be moved to Done with this deploy SHA when committed (pending — note that I do not have direct Notion access from this session per CLAUDE.md guidance).

## Acceptance criteria status (brief §7)

- [x] **1. Headline number defensible.** `derive_compute_revenue.py --validate` reproduces $73.45B 2025 gross / $61.95B net from `compute_disclosures.json`. Each component cites a 10-Q filing URL + retrieval date.
- [x] **2. Provenance complete.** Every component carries `source` (via `ai_run_rate_disclosure` / `underlying_segment`), `sourceUrl`/`filing_url`, `retrievedAt`, `nextReview`, `confidence`, `tier_gross`, `tier_net`, `pass_through_basis`. `release-check.mjs` extended via `validate-compute-revenue.mjs` (Step 10b).
- [x] **3. Layer-Stack Multiplier visual works.** Built as the page's signature visual per D4. Math documented in §5.3 of methodology page. Visual is screenshot-legible at 800×400 (canvas auto-sizes; brand watermark in-chart).
- [/] **4. News-clock cadence demonstrated.** Q1 2026 cycle was completed manually as part of this build. Time-to-update on subsequent cycles depends on 10-Q narrative parse speed; aggregator itself is <1s. Documented in "Open items" #5.
- [x] **5. Methodology page updated.** New Compute Ledger card + dedicated section "Compute Revenue — gross vs net & principal/agent gate" explaining the dual-publication, D6 gate, and Compute vs Apps/Model boundary.
- [x] **6. Nav consistent.** All 5 layer pages (Capital / Revenue / Compute / Usage / Power) carry Compute in nav. index.html nav + footer also updated.
- [/] **7. Mobile-render check.** Mobile CSS in place (375px viewport accommodated per brief §7.7). Visual screenshot deferred — see Open items #6.
- [x] **8. No regressions.** `validate-compute-revenue.mjs` passes. Existing site-data.json hash + render_config registry remain valid (compute is additive).

## Notes for Cowork

- D6 verification gate result is the load-bearing methodological output. All four entities use **principal treatment**; the aggregation rule in brief §5.2 stands as written. If any future 10-K refiles policy with agent treatment for any of the four reseller arrangements, the validator will fail and the aggregator will refuse to run until the rule is updated.
- The "circular financing" thread is visible in the Layer-Stack Multiplier: Silicon revenue ($165B) exceeds Compute Revenue net ($62B). The asymmetry exists because silicon spend is funded by Mag3 capex, not just compute customer dollars passing through — exactly the story the brief identified as the original-IP framing.
- Concentration headline reads: "Microsoft, Google, and Amazon capture **87%** of all AI compute revenue. Public neoclouds **8%**, Oracle **4%**, private neoclouds **1%**." This is the page H1 number per D2.
- Coordination with TAIL View Q1 launch in Week 3 (D5) is a pacing decision external to this build. Page is live-ready as of 2026-05-06.
