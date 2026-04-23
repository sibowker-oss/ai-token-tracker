# Brief: Structured claim schema extension

> **Handoff metadata (per GUIDELINES §9.3)**
> - **Source draft:** `The AI Ledger/structured-claim-schema-brief.md`
> - **Handoff date:** 2026-04-23
> - **Work queue:** wq-014
> - **Parent:** wq-009 (widen-source-data-brief.md)
> - **Blocks:** wq-012 (Stream 2 power), wq-013 (Stream 3 hiring/patents)
> - This repo copy is the **immutable contract**. Append Implementation log below when starting work; do not edit §1–§6 without going back to the Ledger draft and handing off again.

**Status:** Scoped
**Priority:** H — implement first, unblocks the other two streams.

---

## 1. Why

Current claim extraction (`extract_claims.py`) produces claims from textual sources — podcast transcripts, articles, reports. Shape is suited to "Dario Amodei said Anthropic's ARR is $X" — a textual claim with provenance and confidence.

Streams 2 and 3 produce different kinds of claims: **structured numeric signals** with a typed shape. Examples:

- "ERCOT queue project #AA1-567 requests 300 MW, attributed to AWS, stage FIS_signed, target COD 2027-06-01"
- "Anthropic has 97 open AI-titled roles as of 2026-04-23 via Greenhouse"
- "Mistral filed 11 AI-CPC patent applications in trailing 12 months"

These don't fit the free-text claim shape. Schema extension required before Streams 2 and 3 can hand off cleanly.

## 2. Proposed claim types

Four new structured types. Each keeps the existing provenance fields (`source`, `url`, `retrievedAt`, `nextReview`, `confidence`) and adds a `type`-specific payload.

### 2.1 `power_project`

```json
{
  "type": "power_project",
  "company_slug": "amazon-aws",
  "attribution_confidence": "medium",
  "attribution_sources": ["https://epoch.ai/..."],
  "queue_market": "ERCOT",
  "queue_id": "GIS-2024-045",
  "poi": "Spruce 345kV",
  "county": "Williamson, TX",
  "stage": "screening",
  "mw_requested": 300,
  "mw_approved": null,
  "mw_in_service": null,
  "requested_cod": "2027-06-01",
  "llc_of_record": "Silver Queen LLC",
  "source": { "url": "...", "retrievedAt": "...", "nextReview": "...", "confidence": "high" }
}
```

### 2.2 `hiring_snapshot`

```json
{
  "type": "hiring_snapshot",
  "company_slug": "anthropic",
  "window": "2026-W17",
  "metrics": {
    "open_roles_total": 214,
    "open_roles_ai_titled": 97,
    "open_roles_prompt_engineer": 3,
    "ai_titled_share": 0.453,
    "new_ai_roles_7d": 11
  },
  "by_function": {"research": 41, "engineering": 112, "go_to_market": 38, "ops": 23},
  "source": { "type": "greenhouse", "token": "anthropic", "url": "...", "retrievedAt": "...", "nextReview": "...", "confidence": "high" }
}
```

### 2.3 `patent_snapshot`

```json
{
  "type": "patent_snapshot",
  "company_slug": "anthropic",
  "assignee_ids": ["pv_assignee_123456"],
  "window": "2026-04",
  "metrics": {
    "applications_published_last_30d": 4,
    "applications_published_trailing_12m": 38,
    "grants_last_30d": 1,
    "grants_trailing_12m": 9,
    "ai_cpc_share_trailing_12m": 0.89
  },
  "top_cpc_subclasses": [{"code":"G06N 20/00","n":18}],
  "source": { "type": "patentsview_search", "url": "...", "retrievedAt": "...", "nextReview": "...", "confidence": "high" }
}
```

### 2.4 `company_surfaced` (discovery-specific)

Emitted when a patent/H-1B/news mention references a company not in `companies.json`. Review in `claims.html` accepts or declines — Accept adds to master list.

```json
{
  "type": "company_surfaced",
  "candidate_name": "Moonshot AI",
  "candidate_aliases": ["Moonshot AI, Inc.", "月之暗面"],
  "first_seen_signal": {
    "kind": "patent_application",
    "cpc": "G06N 20/00",
    "application_id": "US-20260012345-A1",
    "filing_date": "2024-11-18"
  },
  "density_score_estimate": 72,
  "source": { "url": "...", "retrievedAt": "...", "confidence": "medium" }
}
```

## 3. Where the schema lives

- Update `metric-schema.json` (already exists in repo) with the four new types.
- Update `extract_claims.py` prompt templates per type.
- Update `claims.html` to render each type appropriately (power_project gets a map preview; hiring/patent get a sparkline; company_surfaced gets name + first-signal).
- Update `apply_claims.py` to route accepted claims into `site-data.json` sections by type.

## 4. Why this is a shared dependency

Both Streams 2 and 3 block on this. Doing it once, centrally, stops each stream reinventing its own claim shape. Opens the door for future streams (M&A events, IPO filings, etc.) to reuse the same four types or extend with new ones.

## 5. Implementation package

1. Schema extension in `metric-schema.json` (4 new types).
2. Prompt templates in `extract_claims.py` (4 new prompts, one per type).
3. `claims.html` renderer updates (4 new card layouts).
4. `apply_claims.py` routing (4 new `site-data.json` target paths).
5. Validation tests — synthetic input → expected structured claim output.
6. Migration plan if existing free-text claims overlap with new structured types.

## 6. Open decisions

None at scoping. Implementation decisions deferred.

---

## Implementation log

*(Append entries here when work starts. Leave §1–§6 above untouched.)*

### 2026-04-23 — Phase 1 foundation shipped

Four commits on `main`, in dependency order:

- `ab3910a` Add structured claim types to metric-schema (wq-014)
- `6012851` Add structured claim extractor (wq-014)
- `3ca98f4` Render structured claim types in claims.html (wq-014)
- `ed833e1` Route structured claim types in apply_claims.py (wq-014)

**What landed**

- `metric-schema.json` v2.2 — new top-level `claim_types` block with
  `power_project`, `hiring_snapshot`, `patent_snapshot`, `company_surfaced`.
  Each type carries label / description / required / optional / fields /
  source_block / site_data_target. Existing `roles` / `proposed_fields` /
  `derived_fields` / match-rule arrays untouched.
- `scripts/extract_structured_claims.py` — new sibling to
  `extract_claims.py`. Deterministic builders for typed input (ISO rows,
  ATS JSON, USPTO JSON), LLM prompt templates as module constants for
  narrative fallback (not wired in Phase 1). Writes to
  `data-updates/{date}-structured-candidates.json`. Self-test CLI is
  green against all four fixtures.
- `claims.html` — type-branched rendering. Structured claims load from
  the parallel candidates file and are normalised on load so the existing
  card shell / sort / filter / stats machinery stays in one code path.
  One helper per type for the body (metric grid + source/retrieval block).
  Small CSS additions for per-type badges and metric grid. Free-text
  card path is unchanged and remains the default branch. Also renders
  the optional `source_excerpt_original` field (needed by wq-015 China
  sources; lands there, not here).
- `scripts/apply_claims.py` — type-dispatch at the top of the accepted
  claim loop. Per-type appliers translate the nested `source` block to
  flat `sourceUrl` / `retrievedAt` / `nextReview` per GUIDELINES §4.2,
  capitalise `high|medium|low` → `High|Med|Low` per §4.4 / §5.6, and
  append one row per write to `data/sources.log.md`. `_ensure_path`
  helper creates nested target containers on demand so first-use
  populations of `site.power.projects`, `site.hiring.snapshots`, and
  `site.patents.snapshots` just work. `company_surfaced` appends to a
  new `candidates` block in `companies.json` plus an append-only
  `data/company-surfaced.log.json`; re-accepting the same name is a
  no-op.

**Validation**

- `tests/test_claim_schema.py` — plain-Python validator, green for all
  four fixtures (required / unknown / source-block completeness).
- `scripts/extract_structured_claims.py --self-test` — green for all
  four round trips.
- In-memory integration test against a tempdir sandbox with all four
  fixtures as accepted claims: site-data writes, provenance
  translation, confidence casing, idempotent upsert, sources.log.md
  rows, company-surfaced dedup — all pass.

**Divergence from brief §5 implementation package**

1. §5.2 prompt templates — brief said "prompt templates in
   `extract_claims.py`". Shipped as module constants in the new sibling
   `extract_structured_claims.py` instead. Simon confirmed the sibling
   approach in the handoff thread. `extract_claims.py` is untouched —
   the podcast/free-text path doesn't share enough with typed-input
   extraction to justify one file.
2. §5.6 migration — no migration was needed. Existing podcast claims in
   `data-updates/*-candidates.json` use the free-text shape; structured
   types are additive and land in a parallel
   `*-structured-candidates.json` file.

**Not done in Phase 1, deferred to the dependent streams**

- Stream 2 (wq-012) wires power-source adapters in `monitor_sources.py`
  that emit `power_project` claims using these builders.
- Stream 3 (wq-013) wires ATS / USPTO / LCA adapters and the
  `ai_native_density` scoring module.
- BigQuery patent coverage is stubbed pending Simon enabling GCP creds
  (brief wq-013 §3.1 / Phase 1 decision #4).

**Carry-along on commit `ab3910a`** — a pre-staged `feed.html → parked/feed.html`
rename was in the index when Phase 1.1 committed and got swept into the
commit. Not my work; functionally harmless (feed.html was already a
parked page per the reference memory). Flagging for audit; no action
taken since amending is destructive. Every subsequent commit in Phase 1
checked `git status` and `git diff --cached --stat` first to confirm
only my files were staged.

**Pausing for review before Phase 2 (wq-015 activation).**

