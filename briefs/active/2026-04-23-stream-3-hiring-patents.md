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
