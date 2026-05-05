# wq-083 — Curated Source Intake

**Session date:** 2026-05-05
**Brief:** `briefings/wq-083-curated-intake.md` (Stage: Scoped, Priority: H)
**Files touched:**
- new `scripts/curated_intake.py`
- updated `claims.html` (curated-index.json discovery)
- updated `ARCHITECTURE.md` (4-paths section + extraction diagram)
- new `data-updates/curated-index.json` (manifest, auto-maintained)
- new `data-updates/2026-05-05-curated-smoke-test-may2026.json` (smoke test output)

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

## Acceptance criteria coverage (brief §3)

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
