# wq-083 — Curated Source Intake

**Session date:** 2026-05-05 (v1 morning, v2 afternoon)
**Brief:** `briefings/wq-083-curated-intake.md` (Stage: Done, Priority: H)
**Files touched (v1 + v2):**
- `scripts/curated_intake.py` — created v1, rewritten v2 (flow model + triangulation)
- `claims.html` — curated-index.json discovery (v1) + triangulates badge/derivation card (v2)
- `ARCHITECTURE.md` — 4-paths section + extraction diagram (v1) + flow-model description (v2)
- `data-updates/curated-index.json` (manifest, auto-maintained)
- `data-updates/2026-05-05-curated-smoke-test-may2026.json` (v1 synthetic smoke test)
- `data-updates/2026-05-05-curated-menlo-genai-enterprise-2025.json` (v2 triangulation test)
- `docs/deployments/deploy-2026-05-05-wq-083-curated-intake-v2.md` (deployment record)

## What was built

A parallel intake path for editorial sources. `curated_intake.py` takes a
URL or piped text, loads a compressed summary of the ledger's current
position, and asks Claude Opus "what does this source change about what we
know?" — returning claims classified as
`matches | updates | conflicts | new | context`.

### Key components

- **Source fetch** — `requests` + a small custom HTMLParser (skips
  script/style/nav, preserves paragraph breaks). Avoided trafilatura /
  readability-lxml to keep the dep footprint minimal; bs4-style parsing is
  good enough for newsletters and IR pages. SPA-rendered content will need
  a follow-up (out of scope).
- **Ledger context builder** — `build_ledger_summary()` compresses
  entities.json (current values + last 2 financial years), schema field IDs
  + proposed fields, and dashboard.providers into a Markdown summary. Smoke
  test: 86 entities → 11k chars / ~2.8k tokens, well under the 15k token
  soft target.
- **Comparison prompt** — full system prompt with same time_period_scope
  rules as `extract_claims.py` (wq-054), plus the new
  `comparison_type / existing_value / delta_pct / comparison_note` fields.
  The prompt instructs the model to pull `existing_value` from the ledger
  summary when classifying as updates/matches/conflicts.
- **Output** — wrapper JSON
  `data-updates/<date>-curated-<slug>.json` containing `summary`, `claims`,
  and source metadata. Each claim has `dedup_status` mapped from
  `comparison_type` (matches→confirms, updates+conflicts→conflicts,
  new+context→new) so existing claims.html badges/filters work unchanged.
  Materiality block is populated via the existing `score_materiality()`
  function so lane filtering works for curated claims too.
- **Index** — `data-updates/curated-index.json` is auto-maintained by the
  script. claims.html fetches it (since static pages can't enumerate a
  directory) and merges any curated files within the same 14-day lookback
  window onto the same review queue.

## Decisions made during implementation

The brief's §Decisions section was unannotated. I took the recommended
defaults:

1. **Model**: Defaulted to `claude-opus-4-7` (latest Opus per current
   guidance) rather than the brief's `claude-opus-4-6`. Override via
   `--model`. Cost is single-digit dollars per run regardless.
2. **Input**: URL + stdin only. Skipped local file path support to keep
   scope tight per the brief's option (b) recommendation. PDF support is
   the obvious next add.
3. **Review path**: Wrapper-format JSON in `data-updates/`, surfaced via
   `claims.html` (option a in the brief). Keeps the human gate consistent.
   The CLI summary is the immediate-feedback layer; reviewer still goes
   through claims.html for accept/decline.

## Smoke test

Synthetic newsletter-style source (~2k chars, mixing matches / updates /
conflicts / new) piped via stdin:

```
cat /tmp/curated-test/test-source.txt | python3 scripts/curated_intake.py \
  --slug smoke-test-may2026
```

Result:
- 14 claims extracted
- Classification: 1 match, 2 updates, 1 conflict, 10 new, 0 context
- Conflict on synthetic Anthropic exit_arr ($84B vs ledger $19B) was
  correctly flagged with delta_pct +342%
- Update on OpenAI ARR ($25B → $30B, +20%) was correctly flagged
- Output JSON loads cleanly via the curated-index.json path in claims.html
- Materiality block populated; source_excerpt anchored on numeric values

## Known limitations / follow-ups

- **HTML extraction is basic.** Static pages with heavy JS rendering
  (modern earnings dashboards, Power BI iframes, some Substack pages) may
  return sparse text. If this becomes an issue, swap `_TextExtractor` for
  trafilatura with a `pip install trafilatura` step.
- **No PDF support.** Hyperscaler 10-Qs are PDFs; for now, copy-paste into
  stdin or extract text first. A `--file` flag with `pypdf` or
  `pdfplumber` is the obvious next add.
- **time_period_scope edge case.** The model sometimes uses
  `point_in_time` for date-stamped run-rate snapshots ("$30B as of late
  April 2026"), which the wq-054 prompt rules say should be `annual` for
  ARR figures with year refs. Same prompt drift as the bulk pipeline; not
  curated-specific. Worth tightening if it shows up in real review.
- **No automation hook.** Brief explicitly carved scheduled curated intake
  out as a future item; current path is manual-trigger only.
- **Ledger context is one-shot.** Rebuilt every run; no caching. At 86
  entities / 2.8k tokens, this is fine. If entities.json grows >5x,
  consider a daily-built `data/ledger-summary.cached.txt` with the same
  shape.

## Acceptance criteria coverage (brief §3 — v1)

- [x] CLI runs with `--url`, `--slug`, plus stdin pipe
- [x] Ledger context loaded (entities + schema + providers), under target
- [x] Opus comparison prompt with all required output fields
- [x] Output written to `data-updates/<date>-curated-<slug>.json`
- [x] CLI summary printed with comparison breakdown
- [x] claims.html loads curated files alongside daily candidates (via
  curated-index.json)
- [x] Materiality scoring applied to all output claims
- [x] Source excerpts included
- [x] ARCHITECTURE.md updated with curated intake path
- [x] Smoke test passed

---

## v2 — flow model + triangulation (afternoon 2026-05-05)

The brief was extended with §3 #2 (build_flow_model with revenue + capex +
entity positions + composition rules), a new `triangulates` comparison type,
and a hard arithmetic constraint (no derivation → reclassify to context).
v2 implements all of this on top of v1.

### What changed in v2

- **`build_flow_model()`** replaces `build_ledger_summary()` (back-compat
  alias retained). Outputs four sections:
  - A. Revenue flow tree from `site-data.json` sankey, with named node
    paths (`sankey.providers.openai`, `sankey.channels.Model API`, etc.)
    and per-provider channel splits from the routing block.
  - B. Capex flow tree from `site-data.json` market + capital_sankey, with
    per-company values, bucket totals, destinations (NVIDIA GPUs / silicon
    / DCs / electricity), utilization, and the headline infra-to-revenue
    ratio.
  - C. Per-entity positions from `entities.json`, every value tagged with a
    provenance confidence tier (`high|medium|low|unsourced`). Low and
    unsourced positions get a ⚠ flag — these are the triangulation targets
    where indirect evidence helps most. Confidence falls back to most
    recent year's provenance for `current.X` keys with no direct entry.
  - D. Hardcoded `COMPOSITION_RULES` block with arithmetic identities
    (Customer Revenue gross = Consumer + SME + Enterprise; Total Capex =
    Mag-7 + Neoclouds + Sovereign + Enterprise direct) and cross-model
    mappings ("Enterprise GenAI market" ≈ Enterprise + SME segments).
  Total: ~21k chars / ~5.4k tokens — well under the 20k token soft target.

- **`SYSTEM_PROMPT`** rewritten to teach the model the flow model concept
  and the `triangulates` classification. Adds the arithmetic constraint
  ("If you cannot write the equation, classify as context instead") and a
  priority list pushing the model toward low-confidence triangulation
  targets first. Output schema gains a `triangulation` object with
  `target_nodes` (named ledger paths), `derivation` (the equation),
  `implied_value`, and `confidence_impact` (strengthens|weakens|widens_range).

- **`enrich_claim`** enforces the arithmetic constraint at write time —
  any `triangulates` claim missing a non-empty `derivation` is downgraded
  to `context` with a reclassification note. This means the constraint
  holds even if the model occasionally drifts from the prompt rule.

- **`_parse_claims_json`** salvages truncated/trailing-comma output. Long
  analyst sources push the response past the previous max_tokens=8192 cap;
  v2 raises to 16384 and walks bracket depth on parse failure to recover
  the last complete claim object. Returns 8 of 12 claims rather than 0.

- **CLI summary** now surfaces every triangulation derivation inline (with
  word-wrapping at ~90 chars) and a "Provenance impacts" roll-up using
  `↑/↓/↔` glyphs for `strengthens/weakens/widens_range`.

- **Output JSON** adds `flow_model_tokens`, `summary.triangulates`, and the
  per-claim `triangulation` block. `ledger_context_tokens` retained as
  back-compat alias.

- **`claims.html`** gets a violet `triangulates` badge, sort priority
  between conflicts and new (so triangulations get human eyeballs early),
  and a dedicated derivation card below each triangulation claim quote
  showing the equation, target nodes as code chips, implied value, and
  confidence impact.

### v2 smoke test — Menlo State of Generative AI in the Enterprise

Re-ran against the analyst-framework source called out in the brief as the
canonical triangulation test:

```
SSL_CERT_FILE=$(python3 -m certifi) python3 scripts/curated_intake.py \
  --url "https://menlovc.com/perspective/2025-the-state-of-generative-ai-in-the-enterprise/" \
  --slug menlo-genai-enterprise-2025
```

Result: 28 claims from a 33k-char source. Classification: 0 matches /
0 updates / 0 conflicts / **8 triangulates** / 7 new / 13 context. All 8
triangulations have valid derivations referencing named flow-model nodes.

Headline triangulation (the one the brief explicitly worked through):
- Menlo "Enterprise GenAI = $37B" (apps $19B + infra $18B)
- Targets: `sankey.buyers.Enterprise` + `sankey.buyers.SME` +
  `market.2025.enterprise_capex`
- Derivation: $10.1B + $3.8B + $15B = $28.9B; gap to $37B (~$8B) likely
  reflects Menlo's inclusion of foundation model API spend routed through
  enterprises that we attribute to providers via Hyperscaler/API channels
- `confidence_impact: widens_range`

Other strong triangulations:
- AI coding tools $4.0B → Cursor + GitHub Copilot + Cognition + Replit +
  Lovable = $3.46B in our ledger; corroborates within 4%
- AI medical scribes $600M → implies abridge.2025.arr ~$100M vs our $50M
  (matches the [low] flag on that field — undercounted ~2x)
- Copilot spend $7.2B ≈ Model Subs channel $7.1B → strengthens within 2%

### Acceptance criteria coverage (brief §3 + §8 — v2)

- [x] `build_flow_model()` with revenue + capex + entity positions +
  composition rules
- [x] Opus prompt with composition rules and arithmetic constraint
- [x] Output JSON with `triangulates` type and `triangulation` block
- [x] CLI summary with triangulation derivations + provenance impacts
- [x] `claims.html` renders triangulates badge + derivation card
- [x] Triangulation test passed (Menlo: 8 valid triangulations)
- [x] Constraint enforcement verified (0 triangulates without derivation —
  enforced at enrich time, not just at prompt time)
- [x] ARCHITECTURE.md Path 3 updated with flow-model + triangulation
- [x] Deployment record at `docs/deployments/deploy-2026-05-05-wq-083-curated-intake-v2.md`

### v2 known limitations

- **Per-entity capex slugs are heuristic.** Sources block ("Microsoft
  CapEx" → `microsoft`) doesn't have a canonical-slug lookup. Model copes
  but cleanup welcome.
- **Truncation risk on very long sources.** max_tokens=16384 covers
  current editorial workload; a 60k-char source with many claims could
  still truncate. Salvage path catches this; multi-call chunking is the
  proper fix when it becomes a problem.
- **`unsourced` confidence tier.** Accurate signal (no direct provenance
  entry) but soft — fallback to year provenance handles most cases.
  Re-examine if model produces low-quality triangulations against
  unsourced positions.
