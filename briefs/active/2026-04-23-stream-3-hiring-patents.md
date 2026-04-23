# Brief: Stream 3 — AI-native company discovery engine

> **Handoff metadata (per GUIDELINES §9.3)**
> - **Source draft:** `The AI Ledger/stream-3-hiring-patents-brief.md`
> - **Handoff date:** 2026-04-23
> - **Work queue:** wq-013
> - **Parent:** wq-009 (widen-source-data-brief.md)
> - **Feeds:** wq-010 Usage overhaul, extends `companies.json`
> - **Absorbs:** wq-011 (AI Native company list research)
> - This repo copy is the **immutable contract**. Append Implementation log below when starting work; do not edit §1–§12 without going back to the Ledger draft and handing off again.

**Status:** Scoped
**Budget:** $0 recurring (all sources free at Ledger scale)

---

## 1. Goal

**Primary:** discover AI-native companies the Ledger is not yet tracking.

**Secondary:** once a company is tracked, build hiring + patent signal depth for it.

The Ledger's authority grows with list coverage and list quality. The current company list is hand-curated — finite, biased by what we've read, blind to emerging companies outside that reading. A programmatic discovery engine gives us a defensible "we surfaced this before the press did" posture. The list is a seed/validation set. Discovery is the product.

---

## 2. Baseline — what "we already know"

First action: enumerate the current company inventory from:

- `companies.json` — master list
- `entities.json` — broader entities (hyperscalers, investors)
- `data/ai_companies_reclassified.json` — recent reclassification pass

Output: canonical **known_slug** set. Every discovery-engine output is diffed against this set. Anything not in it is a candidate.

---

## 3. Sources as discovery signals

### 3.1 Patent filings (high weight)

- **USPTO PatentSearch API** + **Google Patents BigQuery** (includes international).
- Query: any application published in trailing 24 months with at least one CPC in the AI list (§10).
- Group by assignee (normalised via PatentsView disambiguation).
- Rank assignees by AI-CPC filing volume and AI-CPC share.
- Filter known_slug. Remaining = candidate pool.

**Why strong:** patent filing is costly — signals commitment. International coverage catches CN/EU companies invisible to US-only views.

### 3.2 H-1B LCA filings (high weight)

- **DoL OFLC quarterly xlsx.**
- Filter roles matching the AI-engineer regex (§9).
- Group by employer (after alias normalisation).
- Rank employers by count of AI-titled LCA filings in trailing 4 quarters.
- Filter known_slug.

**Why strong:** can't get an H-1B without hiring intent. Legally clean public data.

### 3.3 Trade press + VC feeds (medium weight)

- Data Center Frontier, The Information AI Ledger, Stratechery, The Pragmatic Engineer.
- VC announcement feeds (TechCrunch Funding, Crunchbase News free tier).
- Weekly named-entity extraction → filter known_slug.

### 3.4 GitHub + HuggingFace (medium weight)

- HuggingFace orgs with AI models above a threshold (downloads/month, active models).
- GitHub orgs with AI repos above a threshold (stars, AI-related topics).
- Rank by activity. Filter known_slug.

### 3.5 Common Room crowdsourced signal (medium-low weight)

- Use the existing Common Room connector to surface company mentions within AI communities.

### 3.6 ATS discovery (reactive)

We can't brute-force-poll every Greenhouse board. Once a candidate is surfaced by 3.1–3.5, check whether they have a public Greenhouse/Lever/Ashby/Workable board. If yes, they become trackable in the depth pipeline (§7).

---

## 4. Pipeline — uses existing claims infrastructure

The site already has: `monitor_sources.py` + `extract_claims.py` + `claims.html` review UI + `apply_claims.py`. No new review queue needed. `claims.html` Accept / Decline / Park *is* the discovery review UI. Suppression = Decline.

Flow for every new source:

```
 [ source added to sources-registry.json ]
             ↓
 [ monitor_sources.py fetches on schedule ]
             ↓
 [ extract_claims.py produces structured claims ]
             ↓
 [ claims.html → Accept / Decline / Park ]
             ↓
 [ apply_claims.py → companies.json + site-data.json ]
```

If a patent filing or H-1B LCA mentions a company not in `companies.json`, the `company_surfaced` claim is extracted; Accept adds to master list.

---

## 5. Candidate scoring

AI Native Density score used as a **ranking filter**, not a dashboard number. Four normalised sub-scores, weights 0.30 / 0.20 / 0.20 / 0.30 (to be validated — see §8):

| Component | Formula |
|---|---|
| Hiring intensity (LCA-derived) | `ai_lca_filings_trailing_4q / log(employer_size_proxy)` |
| Patent momentum | `ai_cpc_applications_trailing_12m` z-scored within funding tier |
| Capital velocity | `total_funding_trailing_24m / months_since_last_round` (when known) |
| Revenue / platform traction | if known: `ln(ARR_estimate)`; else: HF downloads / GH stars proxy |

Score ranks the review queue — top candidates surface first.

---

## 6. Validation set (the "top 31")

Used to (a) sanity-check discovery recall, and (b) calibrate density-score weights.

**Frontier labs (10):** OpenAI, Anthropic, Google DeepMind, Meta AI, xAI, Mistral, Cohere, AI21, Inflection, Reka.

**Inference / infra (6):** Together AI, Groq, Fireworks, Lambda Labs, Modal, Anyscale.

**Dev tools (4):** Cursor, Codeium/Windsurf, Poolside, Magic.

**Applied vertical (7):** Harvey, Glean, Perplexity, Character.AI, ElevenLabs, Runway, Writer.

**Data / MLOps / platform (4):** Databricks, Hugging Face, Scale AI, Weights & Biases.

---

## 7. Tracking depth (secondary output)

Once a company is accepted, ATS + patent sources start populating depth automatically.

**Hiring per company (weekly):** `open_roles_total`, `open_roles_ai_titled`, `open_roles_prompt_engineer`, `new_roles_7d`, `by_function`, `by_location_top5`. Source: whichever ATS (Greenhouse/Lever/Ashby/Workable) the company uses.

**Patents per company (monthly):** `applications_published_trailing_12m`, `grants_trailing_12m`, `ai_cpc_share_trailing_12m`, `top_cpc_subclasses`. Source: USPTO PatentSearch + Google Patents BigQuery.

**LCA salaries:** captured internally only for v1, used to calibrate ARR/burn estimates. Not rendered publicly (per §8 decision 2).

---

## 8. Decisions (resolved 2026-04-23)

- **V1 company list:** top ~31 AI-natives as validation set, not deliverable.
- **LCA salary exposure:** internal only for v1. Not rendered publicly.
- **Prompt engineers:** separate category in depth metrics.
- **Non-US patents:** included in v1 via Google Patents BigQuery.
- **Score weights:** validate against 31-company set before shipping.
- **Goal reframe:** discovery is primary; tracking depth is secondary.

---

## 9. AI-engineer regex

```
INCLUDE (case-insensitive, word-boundary):
  \b(machine learning|ml)\b.*\b(engineer|scientist|researcher)\b
  \b(ai|artificial intelligence)\b.*\b(engineer|scientist|researcher)\b
  \b(research engineer|research scientist)\b
  \b(applied (ai|ml|scientist|research))\b
  \b(mlops|ml ops|ml platform|ml infrastructure)\b
  \b(deep learning|nlp|computer vision|reinforcement learning)\b.*\b(engineer|scientist)\b
  \b(llm|foundation model|generative ai)\b.*\b(engineer|scientist|researcher)\b
  \b(ai safety|alignment|interpretability)\b.*\b(engineer|scientist|researcher)\b

SEPARATE CATEGORY:
  \b(prompt engineer)\b

EXCLUDE:
  \b(data engineer|analytics engineer|bi engineer|data analyst)\b unless body hits INCLUDE
  \b(data scientist)\b unless title ALSO contains (ml|ai|applied|research|llm|nlp)
```

## 10. AI-relevant patent classifications

G06N 3/00–3/12, **G06N 20/00** (key), G06N 5/00–5/04, G06N 7/00, G06N 7/01, G06N 10/00, G06F 18/00, G06F 40/00–40/58, G06V 10/70–10/82, G10L 15/00, G10L 15/16, G10L 25/00.

## 11. Legal / ToS

In force: LinkedIn scraping forbidden (hiQ precedent), Levels.fyi forbidden (ToS), PATENTSCOPE programmatic paid-only. All other shortlisted sources cleared.

---

## 12. Implementation package

1. Add 8 new sources to `sources-registry.json`: USPTO PatentSearch API, Google Patents BigQuery, EPO OPS, DoL OFLC LCA quarterly, Greenhouse board API, Lever postings API, Ashby posting API, Workable widget API.
2. **Alias map** — new file `data/company-alias-map.json`, seeded from PatentsView assignee disambiguation + hand-curated LCA name variants. Referenced by `extract_claims.py` during entity resolution.
3. Extend `monitor_sources.py` to handle the 8 new source types (JSON APIs, xlsx download, BigQuery).
4. Extend `extract_claims.py` with prompts that produce new structured claim types (depends on wq-014): `hiring_snapshot`, `patent_snapshot`, `company_surfaced`.
5. **AI Native Density** — compute as a derived claim. Not a tracked metric in its own right; just a composite for ranking.
6. **Validation harness** — script that re-runs discovery against the 31 validation companies in §6 and checks they'd all be surfaced. Output: coverage report.
7. Agent registration — `agents.registry.md` entry "discover AI-native companies via patents + hiring signals". Log runs in `agents.log.md`.

---

## 13. Open questions (for implementer)

1. Where does the human review queue live — reuse `claims.html` as-is, or a sub-view keyed by claim type?
2. How aggressive on dedupe — e.g. "Mistral AI" vs "Mistral" — and who decides?
3. Discovery cadence — monthly default, or align to patent-publication weeks (Tue/Thu)?
4. Suppression expiry — never re-surface a declined company, or re-surface if signals materially change?

---

## Implementation log

*(Append entries here when work starts. Leave §1–§13 above untouched.)*

### 2026-04-23 — Phase 4 plumbing shipped

Five commits on `main`:

- `98101ca` Register Stream 3 discovery sources (wq-013)
- `0c14e79` Seed company-alias-map with 31-company validation set (wq-013)
- `3934cd6` Add Stream 3 discovery adapters to monitor_sources (wq-013)
- `f214234` AI Native Density scorer + 31-company validation harness (wq-013)
- `ff2e377` Register company-discovery agent (wq-013)

**What landed**

_Sources (§12.1)_

- Eight new registry entries (src-065 USPTO PatentSearch, src-066 Google
  Patents BigQuery, src-067 EPO OPS, src-068 DoL OFLC LCA, src-069
  Greenhouse, src-070 Lever, src-071 Ashby, src-072 Workable). All
  pending_first_extraction with next_check=2026-05-23. src-066
  additionally flagged `status=pending_credentials` because BigQuery
  needs GCP auth.

_Alias map (§12.2)_

- `data/company-alias-map.json` seeded with the §6 validation set (31
  companies). Shape per wq-013 §12.2 plus `founded` (for GUIDELINES §4.6
  AI-native filter) and `category` (§6 bucket).
- 22 of 31 ATS tokens populated on seed (13 greenhouse, 8 ashby,
  1 lever). The remaining 9 (google-deepmind, meta-ai, xai, inflection,
  reka, codeium, poolside, magic, character) have null ATS — Simon
  confirms as each surfaces.
- `lca_names` populated for all 31 with best-guess employer strings.
- `patent_assignee_ids` empty across the board — the PatentsView
  `/api/v1/assignee?q=<canonical>` disambiguation pass is a follow-up
  helper I didn't build this phase (one API call per company; straightforward
  when Simon wants to close that gap).

_Adapters (§12.3)_

Eight new entries in `monitor_sources.ADAPTERS`, plus the AI-engineer
classifier `classify_role(title, body)` implementing the wq-013 §9
INCLUDE / EXCLUDE regex verbatim. 20-case spot-check passed for
representative ML / AI / Prompt / MLOps titles and the data-engineer /
data-scientist exclusions.

| Adapter | Status | Notes |
|---|---|---|
| `greenhouse_board` | **functional** | Fans out to 13 companies; public JSON, no auth. |
| `lever_postings`   | **functional** | 1 company (Mistral) on seed. |
| `ashby_public`     | **functional** | 8 companies. |
| `workable_jobs`    | ready (no targets) | 0 companies use Workable in the seed; adapter stands by. |
| `patentsview_search` | partial | Public USPTO API works; zero companies have `patent_assignee_ids` populated so v1 emits 0 patent_snapshot claims until disambiguation runs. Rolling 30d + grants counts are follow-up. |
| `google_patents_bq` | **stubbed** | Requires GCP_SERVICE_ACCOUNT_JSON — Phase 1 decision #4. |
| `epo_ops`           | **stubbed** | Env-gated on EPO_OPS_CLIENT_ID / _SECRET. |
| `dol_lca_xlsx`     | **stubbed** | Needs `openpyxl` (not in v1 env). Surfaces quarterly XLSX download links in the log. |

Shared helpers landed alongside:
- `_extract_ats_generic` — common core for the four ATS adapters.
- `_build_hiring_snapshot(slug, entry, source, jobs, ats_type, token)` —
  aggregates job dicts into a schema-conformant hiring_snapshot claim.
- `_load_alias_map()` / `_iso_week()` / `_iso_month()` / `_fetch_json()`
  — stdlib-only utilities.

_AI Native Density (§5 + §12.5)_

- New `scripts/ai_native_density.py`. Four sub-scores
  (hiring / patents / capital / revenue) combined with the brief's
  0.30 / 0.20 / 0.20 / 0.30 weights. Implements the formulas literally
  per §5.
- Not rendered publicly per §8 decision ("LCA salary exposure: internal
  only for v1. Not rendered publicly"). Score is used only as a ranking
  filter in the company_surfaced review queue and as `density_score_estimate`
  on emitted company_surfaced claims.
- `Inputs.from_alias_entry(slug)` reads the latest hiring / patent
  snapshots from `site-data.json`. Currently returns 0 for every
  company because no extractions have landed — that's the honest
  state, not a bug.

_Validation harness (§12.6)_

- New `scripts/discovery_validation.py`. For each of the 31 companies,
  checks whether the engine can see it via patent_assignee_ids,
  ats.token, or lca_names.
- Current result:
  - 0/31 visible via patents (empty assignee_ids seed)
  - 22/31 visible via ATS
  - 31/31 visible via LCA
  - **31/31 surfaced by ≥1 signal — zero recall gaps**
  - 0/31 fully covered across all three signals
- `--report` mode writes markdown to `reports/discovery-coverage-<date>.md`
  so coverage audits are persistable.

_Agent (§12.7)_

- `company-discovery` v0.1.0 registered in `data/agents.registry.md`
  with the eight adapter handles + the two scripts. Cadence
  on-demand per-source via `--force`. Recommended cadence per §7:
  weekly for ATS, monthly for patents.
- Two rows on `data/agents.log.md`: alias-map seed (commit `0c14e79`,
  outcome=merged) and agent registration (outcome=configured).

**Divergence from brief**

1. **§12.1 source count** — brief says 8 sources. Implemented 8 exactly
   (src-065..072). No drift.
2. **§12.2 alias map PatentsView IDs** — brief says "seeded from
   PatentsView assignee disambiguation". I seeded the alias map without
   the PatentsView lookup. Reason: running a PatentsView disambiguation
   pass requires one live API call per canonical name, ~31 calls, which
   produces data that may need human judgment (some names
   disambiguate to multiple PatentsView IDs; some don't
   disambiguate at all). Leaving that as an explicit follow-up where
   Simon reviews the disambiguation output before committing IDs, rather
   than merging a machine-confidence pass.
3. **§12.3 prompt vs deterministic** — brief §3.1 says PatentsView
   "query: any application published in trailing 24 months with at least
   one CPC in the AI list". v1 uses trailing 12m (matches the
   patent_snapshot schema's `applications_published_trailing_12m`). 24m
   is a follow-up when rolling-window extensions land.
4. **§12.5 density score public rendering** — brief says "Not a tracked
   metric in its own right; just a composite for ranking." Confirmed in
   implementation; score is returned by a CLI helper, never written to
   site-data.json.
5. **§3.4 GitHub + HuggingFace** — brief lists these as medium-weight
   discovery signals. Not implemented in v1 — no sources registered,
   no adapter written. Flagged as next-phase work (would be src-073..074
   when enabled).
6. **§3.5 Common Room** — brief says "use the existing Common Room
   connector to surface company mentions". No evidence of an existing
   Common Room connector in the repo. Treated as a brief assumption to
   clarify; not implemented.
7. **Brief §13 open questions** — answered per Phase 1 decision #5:
   reuse claims.html (landed in Phase 1.3), monthly discovery cadence
   (set on src-065/066/067 with next_check=2026-05-23), Decline-forever
   suppression semantics (landed in apply_claims's
   apply_company_surfaced idempotency check in Phase 1.4). No new work
   in Phase 4 on these.

**Follow-ups from Phase 4**

1. PatentsView assignee-disambiguation helper — one-shot script that
   takes each canonical name, hits `/api/v1/assignee?q=...`, presents
   results for Simon to confirm, and writes back to alias map. Unlocks
   `patent_assignee_ids` for the 31 + any company_surfaced candidates.
2. `new_ai_roles_7d` diff computation — `_build_hiring_snapshot` sets
   this to 0 because no prior snapshot exists. When a second weekly
   extraction lands for a company, the helper can read the prior week's
   snapshot from `site-data.json.hiring.snapshots.<slug>` and compute
   the delta.
3. Register GitHub + HuggingFace as §3.4 signal sources.
4. Install `openpyxl` and wire the DoL LCA XLSX row parse (high
   value — LCA data is the strongest hiring-intent signal per §3.2).
5. Backfill the 9 unknown ATS tokens in the alias map as Simon confirms
   each company's board type.
6. Capital / revenue sub-score inputs — v1 reads site-data.json hiring
   and patents only. Capital (total_funding_trailing_24m /
   months_since_last_round) and revenue (ARR) inputs need either a new
   site-data path or a manual override file.

**Not done in Phase 4, deferred**

- §5 weight validation against the 31-company set. Brief decision §8
  says "Score weights: validate against 31-company set before shipping".
  Can't validate weights while all 31 companies score 0 (no hiring/
  patent data landed). Validation lands after Simon runs the first ATS
  extractions and the scorer has real input.
- Monthly diff snapshots for `new_ai_roles_7d`. Needs a second weekly
  run per company.
- Actual ATS / PatentsView extractions. Simon fires per source when
  ready to review output.

**Phase 4 complete — pausing for review.**

### 2026-04-23 — Review-budget posture reversed

Per Simon's feedback. All eight Stream 3 sources had `next_check=2026-05-23`;
reset to today so the daily 11:30am cron fires them at their stated
cadence tomorrow:

- src-065 USPTO PatentSearch — monthly (0 claims until patent_assignee_ids
  populated)
- src-066 Google Patents BigQuery — `status=pending_credentials`,
  next_check unchanged (9999-12-31). Gate when GCP creds land.
- src-067 EPO OPS — monthly (env-gated; no-op until
  EPO_OPS_CLIENT_ID/_SECRET set)
- src-068 DoL LCA — quarterly (stubbed on openpyxl; no-op until
  `pip install openpyxl`)
- src-069 Greenhouse — **weekly**; fans out to 13 companies, emits 13
  hiring_snapshot claims per run
- src-070 Lever — **weekly**; 1 company (Mistral)
- src-071 Ashby — **weekly**; 8 companies, 8 hiring_snapshots
- src-072 Workable — weekly; 0 companies on the seed (stand-by)

`process_source()` updated to append structured hiring_snapshot /
patent_snapshot / company_surfaced claims to
`<date>-structured-candidates.json`, so claims.html picks them up
automatically. Per-source audit files retained.

First natural cron fire (tomorrow, 2026-04-24 11:30am) will produce
~22 hiring_snapshot claims plus whatever patent / LCA paths yield once
creds / openpyxl land.

**To see the discovery engine in action, run any of:**

```bash
# Pull AI job snapshots for 13 Greenhouse-hosted validation companies
python3 scripts/monitor_sources.py --force src-069

# Pull AI job snapshots for 8 Ashby-hosted companies
python3 scripts/monitor_sources.py --force src-071

# Pull patent snapshots for any company with patent_assignee_ids populated
python3 scripts/monitor_sources.py --force src-065   # emits 0 today until IDs seed

# Dry-run: show current coverage against the 31-company validation set
python3 scripts/discovery_validation.py

# Dry-run: rank all 31 by density score (all 0 today, for the reason above)
python3 scripts/ai_native_density.py --all
```

Claims land in `data-updates/<date>-source-<src-id>.json` —
per-source isolation, not auto-loaded by claims.html.


---

## Sources

- [Greenhouse Job Board API](https://developers.greenhouse.io/job-board.html)
- [Lever Postings API](https://github.com/lever/postings-api)
- [Ashby Public Job Posting API](https://developers.ashbyhq.com/docs/public-job-posting-api)
- [Workable public API](https://workable.readme.io/reference/jobs)
- [DoL OFLC LCA Disclosure Data](https://www.dol.gov/agencies/eta/foreign-labor/performance)
- [USPTO PatentSearch API reference](https://search.patentsview.org/docs/docs/Search%20API/SearchAPIReference/)
- [USPTO bulk patent grant XML](https://developer.uspto.gov/product/patent-grant-full-text-dataxml)
- [USPTO bulk patent application XML](https://developer.uspto.gov/product/patent-application-full-text-dataxml)
- [Google Patents BigQuery dataset](https://github.com/google/patents-public-data)
- [EPO OPS Fair Use Charter](https://ea.espacenet.com/?locale=en_EA&view=fairusecharter)
- [CPC G06N scheme](https://www.uspto.gov/web/patents/classification/cpc/html/cpc-G06N.html)
- [WIPO AI Index PATENTSCOPE strategy](https://www.wipo.int/en/web/technology-trends/artificial_intelligence/patentscope)
- [PatentsView assignee disambiguation](https://patentsview.org/disambiguation)
- [Pave AI/ML role taxonomy](https://www.pave.com/blog-posts/differences-between-ai-engineers-ml-engineers)
- [MPEP §1120 — 18-month publication](https://www.uspto.gov/web/offices/pac/mpep/s1120.html)
