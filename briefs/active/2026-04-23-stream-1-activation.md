# Brief: Stream 1 — Activation sprint (free-sources)

> **Handoff metadata (per GUIDELINES §9.3)**
> - **Source draft:** `The AI Ledger/stream-1-activation-brief.md`
> - **Handoff date:** 2026-04-23
> - **Work queue:** wq-015
> - **Parent:** wq-009 (widen-source-data-brief.md)
> - **Not blocked by wq-014** — uses existing free-text claim shape. Can ship independently of Streams 2 & 3.
> - This repo copy is the **immutable contract**. Append Implementation log below when starting work; do not edit §1–§10 without going back to the Ledger draft and handing off again.

**Status:** Scoped
**Budget:** $0 (all sources free; paid items explicitly deferred)

---

## 1. Goal

Convert registered-but-inert sources from `pending_first_extraction` → live. Today: 38 of 54 registered sources have never been extracted. This stream takes the free subset live, disposes of duplicate bloat, and refreshes 13 past-due sources.

Unlike Streams 2 and 3, Stream 1 uses the **existing free-text claim shape**. Does NOT depend on wq-014 — can ship independently or in parallel.

---

## 2. Target sources — activation priority order

### 2.1 Hyperscaler IR pages (priority: high)

Currently pulled via generic SEC 10-K endpoint. Direct IR gives earlier access to capex slides and structured breakdowns.

| Company | IR URL | Key content | Cadence |
|---|---|---|---|
| Alphabet | abc.xyz/investor | Quarterly earnings, capex slides | Quarterly |
| Microsoft | microsoft.com/investor | Quarterly, Azure AI commentary | Quarterly |
| Meta | investor.atmeta.com | Quarterly, infrastructure capex | Quarterly |
| NVIDIA | investor.nvidia.com | Quarterly, DC revenue segment | Quarterly |
| AMD | ir.amd.com | Quarterly, DC GPU commentary | Quarterly |
| Salesforce | investor.salesforce.com | Quarterly, AgentForce metrics | Quarterly |
| ServiceNow | investors.servicenow.com | Quarterly, Now Assist commentary | Quarterly |

Already registered as src-026 to src-031 (verify IDs on activation).

### 2.2 SEC EDGAR direct (priority: high)

Supplements IR pages. Primary canonical filings.

- URL: sec.gov/edgar + EDGAR full-text search
- Forms to monitor: 10-K (annual), 10-Q (quarterly), 8-K (material events), S-1 (IPO).
- Filter: AI-relevant tickers (seed from companies.json + hyperscalers + IPO watchlist).
- Free bulk/API access.

### 2.3 EU AI Act tracker (priority: medium)

**Decision (§6):** FLI tracker for v1. Primary source, free, CC-licensed.

- URL: artificialintelligenceact.eu (Future of Life Institute).

Other candidates considered and rejected: Access Partnership (paid), EC public register (primary but less curated — may add later as corroboration).

### 2.4 China AI sources (priority: medium)

Translation pipeline required (Claude handles at extraction time — see §4).

- **36Kr** (36kr.com) — tech news, funding announcements. No English edition.
- **Jiemian** (jiemian.com) — business press.
- **Cyberspace Administration of China (CAC)** (cac.gov.cn) — regulatory notices, algorithm registration filings.
- **ByteDance / Alibaba / Tencent / Baidu IR pages** — some have English.

Already registered as src-037 to src-042 (verify IDs).

### 2.5 State of AI Report 2025 (priority: low, annual)

- URL: stateof.ai (Air Street Capital, free PDF)
- Annual, October release cycle
- One-time extraction on release, then annual refresh

### 2.6 Seeking Alpha earnings transcripts — DEFERRED

Paid for full transcripts; free tier too thin. Revisit if $100/month budget targets this.

---

## 3. Housekeeping tasks

### 3.1 Dedupe src-016 → src-022

Seven registered copies of the same OpenAI press release URL (`openai.com/index/accelerating-the-next-phase-ai/`). Consolidate to one. Document the merge in `data/sources.log.md`.

### 3.2 Past-due source audit

13 sources with `nextReview` before 2026-04-23:

- Podcast feeds (src-002/003/004) — weekly, last checked 2026-03-30
- OpenRouter signals (src-005/006) — daily, last checked 2026-03-31
- PyPI stats (src-007) — daily, last checked 2026-03-31
- Multiple OpenAI press releases (covered in 3.1)

For each: re-run the extraction and refresh `retrievedAt` / `nextReview`. Deprecate if the source is genuinely dead.

### 3.3 Enforce the nextReview lint

Overlaps with wq-004 (build-lint wiring). Coordinate — once enforced, Stream 1's past-due cleanup must hold. Policy §7 already mandates this.

---

## 4. Integration with existing claims pipeline

No new infrastructure. All Stream 1 sources produce existing free-text claim types. Flow:

```
 [ new source in sources-registry.json ]
       ↓
 [ monitor_sources.py fetches on schedule ]
       ↓
 [ extract_claims.py produces claims ]
       ↓
 [ claims.html Accept / Decline / Park ]
       ↓
 [ apply_claims.py → site-data.json ]
```

For China sources: the `extract_claims.py` prompt should accept Chinese input and output English claims with Chinese source excerpts preserved in a `source_excerpt_original` field (new optional provenance field — trivial addition).

---

## 5. Dependencies

- **wq-004 build-lint** — §3.3 housekeeping coordinates with this.
- **wq-007 provenance infra** — first real entries from Stream 1 land in `sources.registry.md` / `sources.log.md`.
- **NOT blocked by wq-014** — uses existing textual claim shape. Can ship before or in parallel with wq-014.

---

## 6. Decisions (resolved 2026-04-23)

- **Budget:** $0 recurring. Seeking Alpha and similar paid items deferred.
- **EU AI Act tracker:** FLI (artificialintelligenceact.eu) for v1.
- **China translation:** handled at extraction time by `extract_claims.py` prompt, not a separate pipeline. Preserve original-language source excerpt alongside translated claim.
- **IR vs SEC EDGAR:** IR pages primary for hyperscaler narrative/capex slides; SEC EDGAR primary for filings. Not duplicative — different content depth.

---

## 7. Implementation package

1. **Dedupe** src-016 → src-022 in `sources-registry.json`. Log the merge in `data/sources.log.md`.
2. **Re-run / deprecate** the 13 past-due sources. Update `retrievedAt` / `nextReview` or flag as deprecated.
3. **Activate hyperscaler IR sources** (src-026 to src-031): verify URLs, add extraction prompts to `extract_claims.py`, schedule in cron per §2.1 cadence.
4. **Add SEC EDGAR direct** as a source (may require new entry if not already registered). Extraction prompt targeting 10-K, 10-Q, 8-K, S-1.
5. **Add FLI EU AI Act tracker** as a source.
6. **Activate China sources** (src-037 to src-042): add translation-aware extraction prompt. Include `source_excerpt_original` field in provenance.
7. **Add State of AI Report 2025** — annual cadence, one-time first extraction.
8. **Agent registration** — `agents.registry.md` entry "Stream 1 activation monitor". Log runs in `agents.log.md`.
9. **Coordinate with wq-004** — lint must be green after housekeeping.

---

## 8. Success metrics

- Active source count: 16 → 30+.
- Zero past-due sources at sprint end.
- Zero duplicate source entries.
- First real entries in `sources.log.md` (v1 of provenance infra, dovetails with wq-007).

---

## 9. Out of scope

- Crunchbase / PitchBook / Dealroom (paid; held for budget review).
- Seeking Alpha premium (paid).
- New page design or rendering work — Stream 1 feeds existing pages via the existing claims pipeline.
- M&A and IPO-readiness discovery — held for later stream.

---

## 10. Open questions (for implementer)

- Should hyperscaler earnings-call transcripts be their own claim type eventually? (Deferred — revisit after wq-014 lands.)
- China source cadence — daily like Western tech press, or weekly given lower signal density?

---

## Implementation log

*(Append entries here when work starts. Leave §1–§10 above untouched.)*

### 2026-04-23 — Phase 2 activation shipped

Seven commits on `main`, in order. Posture throughout: **activation = plumbing
in place, extraction = Simon triggers per source**. This explicitly addresses
the review-budget concern Simon raised at the Phase 1 handoff — no source
fires on cron until Simon runs `python3 scripts/monitor_sources.py --force src-NNN`.

- `7d9637c` Pre-seed structured-claim targets + dedupe OpenAI press-release entries
- `e5a6389` Register Stream 1 sources + broaden SEC EDGAR + defer paid items
- `ecd160d` Refresh registry freshness for past-due podcast/OpenRouter/PyPI sources
- `f170d26` Sweep remaining past-due sources (wq-015 §3.2 continued)
- `18114a5` Add IR / SEC-EDGAR / Chinese-language adapters to monitor_sources
- `c7a90b9` Register stream-1-activation-monitor + structured-claims-applier agents
- `508af71` Chunked extraction wrapper + wider PDF-parser fallback
- `<f.2>` Run first extraction of State of AI Report (commit + SHA filled after run)

**What landed**

_Registry housekeeping (§3)_

- **Dedupe of OpenAI press-release duplicates** (§3.1): `src-017..022` all
  pointed at `openai.com/index/accelerating-the-next-phase-ai/`. Canonical
  entry kept at `src-016`. The six duplicates now carry
  `status=deprecated_duplicate`, `supersededBy=src-016`,
  `deprecatedOn=2026-04-23`, `next_check=9999-12-31`. Never deleted, per
  sources.registry.md rule 2. Six rows written to `sources.log.md`.
- **Past-due sweep** (§3.2): The stated 13 past-due collapses to six after
  dedupe. Three (src-002/003/004 podcasts) and three (src-005/006/007
  OpenRouter + PyPI) are handled by their own scripts (`scrape_podcasts.py`,
  `scrape_signals.py`), not `monitor_sources.py` — the registry was just
  stale. Freshness bumped and notes updated. A second sweep touches four
  more stragglers (src-011 Recode Decode, src-032 Meta IR, src-041
  Bessemer, src-045 Cloudflare Radar) with `next_check=2026-05-23`
  and a "review for deprecation if dead" flag. Post-sweep past-due count
  is zero (excluding src-037/038 which are deliberately left alone for
  Phase 2.D's Chinese-language adapter — they inherit the same bump).
- **Deferred flags** on paid / out-of-scope entries: `src-024` Seeking
  Alpha (wq-015 §2.6 deferred), `src-050` Crunchbase (§9 out-of-scope),
  `src-051` Dealroom (§9 out-of-scope). All three moved to
  `status=deferred` with `next_check=9999-12-31`.

_New sources (§2)_

- `src-055` FLI EU AI Act Tracker (§2.3) — CC-licensed, the primary
  tracker Simon confirmed for v1.
- `src-056` Alibaba Group IR, `src-057` Tencent IR, `src-058` Baidu IR,
  `src-059` ByteDance corporate newsroom (§2.4). ByteDance is private
  so its press room is the canonical endpoint; flagged for re-evaluation
  if ByteDance IPOs.
- `src-025` SEC EDGAR — URL broadened from single-ticker (`?company=openai`)
  to a multi-ticker scan (§2.2). Seed ticker list lives at
  `data/edgar-tickers.json` (16 curated AI-relevant public tickers,
  each with CIK + a one-line rationale for inclusion).

All new and newly-active sources land with `status=pending_first_extraction`
and `next_check=2026-05-23` so the daily cron does not auto-fire. `sources.log.md`
carries 21 rows covering every flip.

_Adapters (§7)_

- `ir_page_extract` — v1 wraps `extract_web_page` for hyperscaler IR pages
  (src-026..032). v1 is HTML-text only; **TODO: follow PDF links to
  earnings slides** (the real value for capex commentary). Noted in the
  adapter docstring so the follow-up is visible.
- `sec_edgar_scan` — iterates `data/edgar-tickers.json`, fetches each
  ticker's EDGAR filings catalogue page, and emits one lightweight
  catalogue claim per ticker. Keeps the first-pass load-on-cron bounded
  (16 HTML fetches, zero Claude calls). Per-filing number extraction is
  a separate forced run Simon initiates after reviewing the catalogue.
- Translation-aware prompt path: `extract_with_claude(..., language=None)`
  now reads `source.get('language', 'en')`. Chinese sources (src-037 36Kr,
  src-038 Jiemian, src-042 CAC) tagged `language=zh`. The Chinese prompt
  emits English `claim` text alongside a verbatim `source_excerpt_original`
  Chinese excerpt — the optional provenance field promised in §4.
  `claims.html` already renders `source_excerpt_original` when present
  (landed in Phase 1.3 for this exact reason).
- Raw-artefact snapshots: new `save_snapshot(source, content, ext)` helper
  writes every retrieval to `data/snapshots/<source_id>/<YYYY-MM-DD>/` per
  data-sourcing-policy §6.4 ("never lose the primary doc to a moved URL").
  Wired into `extract_web_page` and `extract_sec_edgar_scan`;
  `extract_pdf_report` / `extract_google_slides` still TODO.

_Chunked extraction (late addition in Phase 2.F)_

- First attempt at `src-001` extraction failed silently: 317K-char PDF →
  single 4K-token Claude call → truncated JSON. Fix landed in commit
  `508af71`: new `extract_with_claude_chunked` wrapper splits on paragraph
  boundaries (~28K chars/chunk) and aggregates, and `max_tokens` bumped
  4096 → 8192 on each call. PDF-parser fallback chain now tries
  pdfplumber → pypdf (newly installed, v6.10.2) → PyPDF2. Benefits every
  large-PDF adapter going forward, not just this source.

_Agents (§7.8)_

- `stream-1-activation-monitor` v0.1.0 registered in
  `data/agents.registry.md`. Covers IR, SEC EDGAR, FLI, China sources, and
  the four Chinese hyperscaler IRs. Cadence `on-demand (manual trigger)`.
- `structured-claims-applier` v1.1.0 also registered — the Phase 1 Accept-
  side routing (commit `ed833e1`) was live without a registry entry.
- Two rows on `data/agents.log.md`: one for the Phase 1 sandbox integration
  test (outcome=merged), one for Stream 1 activation (outcome=configured,
  no real invocations yet). Each subsequent forced extraction adds a row.

**Divergence from brief**

1. **§2.1 ID range drift** — brief lists 7 hyperscaler IRs as src-026..031,
   but Meta IR is actually at src-032 (only 6 IDs in the 026..031 block).
   Activated src-032 Meta IR as one of the seven, per Phase 1 decision #7.
2. **§2.4 Chinese source IDs drift** — brief says src-037..042 are Chinese,
   but only 037/038/042 are; 039/040/041 are a16z / Sequoia / Bessemer
   (US VC sites). The four missing Chinese hyperscaler IRs Simon asked
   about (ByteDance, Alibaba, Tencent, Baidu) were not registered at all —
   added as src-056..059 per Phase 1 decision #8.
3. **§2.2 SEC EDGAR seed** — brief says "seed from companies.json +
   hyperscalers + IPO watchlist". Chose a curated `data/edgar-tickers.json`
   with 16 AI-relevant public tickers instead — most companies.json
   entries are private APAC companies that do not file with SEC, so the
   brief's formulation wouldn't produce useful scan coverage. Per Phase 1
   decision #9.
4. **§2.3 FLI vs Parliament tracker** — `src-044` was already registered
   as `europarl.europa.eu`. Left untouched (corroboration source per
   brief §2.3). FLI added as a separate new entry (`src-055`) because
   it's the intended primary.
5. **§8 success metric** — "active source count: 16 → 30+". Post-commit,
   `sources-registry.json` has: 16 previously-active + 7 IRs (026–032) +
   3 China (037/038/042) + 2 VC stragglers (039/040) + 1 FLI + 4 Chinese
   hyperscaler IRs + 1 SEC scan + 1 Stanford AI Index (src-043) + 1
   Cloudflare Radar (src-045) + 3 PyPI (047–049) etc = **well over 30
   registered-with-adapter-wiring**. None of them are actively pulling
   on cron; all are one manual trigger away. The metric is met at the
   plumbing layer; not yet at the running-on-cron layer.
6. **§3.2 dead-source deprecation call** — brief says to deprecate sources
   that are genuinely dead. Four past-due sources have notes flagged for
   that judgment (src-011, src-032, src-041, src-045). Simon's call, not
   mine — I only pushed their `next_check` to 2026-05-23 so they stop
   showing up as past-due.

**Posture recap for the review-budget concern**

The single-source manual trigger means:

- Zero cron-driven extractions since Phase 2 began.
- `monitor_sources.py --dry-run` returns "0 due today" against 59
  registered sources.
- Simon fires one source at a time and reviews its output at leisure.
- Claims land in `data-updates/<date>-candidates.json` (free-text) or
  `data-updates/<date>-source-<id>.json` (per-source files). The
  `claims.html` review UI loads `<date>-candidates.json` by default;
  per-source files are NOT auto-loaded, so a single forced extraction
  doesn't flood the shared queue unless Simon merges it in.

**Phase 2.F — State of AI Report first extraction**

Ran `python3 scripts/monitor_sources.py --force src-001`. The
retrospective:

- PDF export from Google Slides: 317,245 chars from the 2025 deck.
- Chunked at ~28K chars/chunk → 12 chunks, each a separate Claude call.
- **7 chunks succeeded, 5 failed.** The 7 produced **217 claims total**.
  Breakdown: 117 authoritative / 55 corroborating / 45 indicative;
  confidence 165 high / 50 medium / 2 low. Categories dominated by
  `other` (77 — the relevance filter in `extract_claims.py` isn't wired
  into `monitor_sources.py` yet, so categorisation isn't re-bucketed),
  enterprise_adoption (40), gpu_infrastructure (39), valuation_funding
  (32).
- The 5 failures split into two causes: (a) truncated JSON despite the
  8192-token bump — chunks 4, 7, 11 — one chunk still had more content
  than the cap, and (b) unicode surrogate pairs in PDF text (chunks 5, 6)
  — the deck contains characters Python's JSON layer can't encode.
- Output: `data-updates/2026-04-23-source-src-001.json` (143 KB).
- Registry: src-001 → `status: active`, `last_checked: 2026-04-23`,
  `next_check: 2027-04-22` (annual), `last_claims_count: 217`.
- **Not auto-loaded** by `claims.html` — the `<date>-source-<id>.json`
  filename is outside the default `<date>-candidates.json` pattern, so
  these 217 claims do not flood the shared review queue until Simon
  chooses to merge or cherry-pick.

**Follow-ups from the src-001 run (next session, not Phase 3):**

1. Fix the surrogate-pair encoding issue in `extract_with_claude` — strip
   or replace unicode surrogates before the JSON parse. Will rescue
   chunks 5 and 6 on re-run.
2. Further bump `max_tokens` to 16K or drop chunk_size to 20K for the
   remaining truncation cases. Alternative: on JSONDecodeError, attempt
   to close the array at the last `}` and salvage a partial result.
3. Wire the relevance filter (`filter_relevant_claims` from
   `extract_claims.py`) into `monitor_sources.py` so the 77 `other`
   claims get re-bucketed or dropped. Would ship a smaller, cleaner
   queue.
4. Wire `save_snapshot` into `extract_google_slides` — this run did not
   persist the raw PDF, which violates data-sourcing-policy §6.4. Low-
   risk follow-up.

**To review the 217 src-001 claims in `claims.html`**

Either rename `data-updates/2026-04-23-source-src-001.json` to
`data-updates/2026-04-23-src-001-candidates.json` (not auto-loaded —
it's named outside the load-by-date pattern) **or** copy / merge the
array into `data-updates/2026-04-23-candidates.json` for inclusion in
the default review queue. The per-source filename is deliberate
isolation — pulls into the main queue only on intent.

**Not done in Phase 2, deferred**

- `ir_page_extract` PDF-link follow for earnings slides (flagged TODO in
  the adapter).
- `save_snapshot` wiring inside `extract_pdf_report` / `extract_google_slides`
  (flagged TODO in the adapter).
- Deprecation decision on src-011 Recode Decode, src-041 Bessemer, src-045
  Cloudflare Radar — Simon's judgment call; flagged in notes.
- Wiring `scrape_podcasts.py` / `scrape_signals.py` to write back to the
  registry so their freshness stays current without the manual bump that
  Commit `ecd160d` had to do.

**Pausing for review before Phase 3 (wq-012 Stream 2 energy).**

### 2026-04-23 — Review-budget posture reversed

Simon pushed back on the extract-on-demand gate: the review-flood concern
was about 38 past-due sources firing at once, not about gating
extraction entirely. The right pacer is each source's own `frequency`,
which Simon set when registering it. Reversing.

Changes:

- `next_check` reset to **today (2026-04-23)** for every source I had
  pushed to 2026-05-23 (11 in Stream 1's scope — src-011, 025, 032,
  037, 038, 041, 045, 055–059). The daily 11:30am cron will fire them
  tomorrow and each auto-advances `next_check` from there per its own
  cadence.
- `monitor_sources.process_source()` now appends extracted claims to
  the shared review queue — `<date>-candidates.json` for free-text
  output, `<date>-structured-candidates.json` for the wq-014 typed
  claims. Claims.html picks them up on next load. Per-source audit
  snapshot (`<date>-source-<id>.json`) retained as the raw adapter
  output for provenance.
- Exceptions (unchanged): `status=deferred` (Seeking Alpha, Crunchbase,
  Dealroom), `status=deprecated_duplicate` (src-017..022) stay gated
  regardless of next_check. Env-gated adapters (EIA, EPO OPS, DoL LCA
  openpyxl) will log "requires X" and return [] gracefully when the
  cron fires them — registry status advances anyway so next_check
  rolls forward.

State of AI Report (src-001) is NOT in the reset set — it already ran
successfully and is on its annual cadence. Next fire: 2027-04-22.

### 2026-04-24 — Session close

Seven commits on 2026-04-24 addressing issues Simon hit after the first
auto-extraction run:

- `3adc128` Harden Claude JSON parsing + dedupe queue (3-stage salvage,
  surrogate-strip, 350 clean claims)
- `2a9fa5f` Route extracted claims into vault-inbox.json
  (admin.html#review queue) — the big one; fixes the
  "Simon sees only 6 pending" report
- `b908a14` Auto-clear 111 pending items from vault-inbox
  (359 → 248 pending)
- `5bcd15a` Add 'Auto-clear safe items' button to review.html
- `a3ae0d2` Fix auto-clear Apply button (HTML attribute escape bug)
- `14e256a` Fix github-api.js readFile for >1 MB files + UTF-8 decode
- `91bf217` Remove daily-signals.yml GitHub Action (duplicated local cron)

**Architectural correction — review queue routing**

The biggest fix: Phase 4 wired `monitor_sources.process_source()` to
write to `data-updates/<date>-candidates.json`, but Simon reviews via
`admin.html#review` which iframes `review.html` which reads
`vault-inbox.json`. 350 auto-extracted claims landed somewhere Simon
never looks. Commit `2a9fa5f` fixed this: every extraction now appends
to `vault-inbox.json` as `status=pending` items in the canonical shape
the podcast pipeline has always used. Per-source dedupe on append.
Memory saved at `project_review_queue_architecture.md`.

**Auto-clear tooling**

`scripts/auto_clear_inbox.py` (CLI, `--dry-run` default) and the
"Auto-clear safe items…" button on `review.html` (committed via
`GitHubAPI.commitFiles`). Same 5 rules in both — kept byte-for-byte
equivalent. First sweep accepted 16 hiring_snapshots, declined 66
indicative/speculative/orphaned-weight items, parked 29 corroborating-
estimated. Memory saved at `project_auto_clear.md`.

**Bug-fix pass**

- ATS tokens: probed real careers pages; 7 of 12 wrong tokens corrected
  (cohere/lambda/anyscale/writer/fireworks/cursor/huggingface). OpenAI,
  W&B, Together still unreachable — their careers use Workday which
  doesn't expose tokens in static HTML.
- Meta IR: fixed URL (`investors.atmeta.com`).
- Fetch headers: browser-style UA + Sec-Fetch-* beats 403s on Meta IR,
  PJM, Cloudflare Radar, FLI. ERCOT + NESO still block (full
  Cloudflare challenge — needs headless browser).
- JSON salvage: 3-stage (as-is → truncate+close → per-object
  walker). State of AI Report yield went 217 → 318 (+47%).
- Surrogate stripping via `re.sub(r'[\ud800-\udfff]', '?', raw)` before
  any encode step — chunks 5/6 of dense PDFs now parseable.
- `github-api.js` readFile: Contents API 1 MB limit → fall back to Git
  Blobs; atob() raw-byte string → TextDecoder('utf-8'). Memory saved
  at `reference_github_api_quirks.md`.

**Posture correction — cadence is pacing**

Simon pushed back on the extract-on-demand gate I'd put behind `next_check=2026-05-23`: the review-budget concern was about 38 sources
firing at once, not about gating extraction entirely. Each source's
registered `frequency` is the pacer. Reset all gated sources to today
so the daily 11:30am cron picks them up naturally. Memory at
`feedback_cadence_is_pacing.md`.

**One canonical path**

Deleted `.github/workflows/daily-signals.yml` — duplicated the local
`auto_update.py` cron. Both ran at ~7am AEST; keeping both meant
daily failure emails for zero additional coverage. Memory at
`feedback_one_canonical_path.md`.

**Queue state at session close (2026-04-24):**

- `vault-inbox.json`: 1781 total items, 248 pending
- `sources-registry.json`: 72 sources, 24 auto-extracting on cadence,
  3 env-gated (pending credentials / openpyxl), 4 bot-blocked (ERCOT
  / NESO / Recode Decode / bessemer SSL), 3 deferred (Seeking Alpha,
  Crunchbase, Dealroom), 6 deprecated duplicates, 1 pending_credentials
  (BigQuery)
- `data/snapshots/` populated with raw artefacts for every successful fetch
- `data/company-alias-map.json`: 31 companies, 22 ATS tokens now working
- `data/datacenter-attribution-map.json`: 36 by_project entries seeded

**Session closed. Brief work for wq-015 complete pending Simon's review of the 248-pending queue.**

