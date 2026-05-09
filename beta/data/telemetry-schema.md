# Telemetry feed schema (`data/telemetry-feed.json`)

Append-only structured log for **operational telemetry / triangulation signals** scraped from automated sources (hiring counts, package downloads, GitHub stats, SEC filings monitoring). These are inputs — they do not enter the human review queue and they do not directly mutate entity records.

Distinct from `data/vault-inbox.json`, which holds human-extractable claims that flow through the review/decision pipeline.

Origin: brief `wq-047`. Confirmed Option B (separate bucket) on 2026-05-03.

---

## File shape

```json
{
  "items": [
    {
      "id": "tel-20260503-coreweave-hiring-001",
      "type": "hiring_snapshot",
      "entity": "coreweave",
      "source_id": "src-XXX",
      "source_url": "https://...",
      "scraped_at": "2026-05-03T10:00:00Z",
      "data": {
        "open_roles_total": 245,
        "open_roles_ai_titled": 0,
        "ai_titled_pct": 0.0
      },
      "metric_key": "X-hiring_snapshot"
    }
  ],
  "lastWritten": "2026-05-03T10:30:00Z"
}
```

### Per-item fields

| Field | Required | Notes |
|---|---|---|
| `id` | yes | `tel-{YYYYMMDD}-{source_id}-{nnn}` — globally unique, monotonic per file |
| `type` | yes | Telemetry category — see *Types* below |
| `entity` | optional | Canonical slug if known; empty string when source isn't entity-scoped |
| `source_id` | yes | `src-XXX` from `sources.json` |
| `source_url` | yes | Concrete URL the scraper hit (page or API endpoint) |
| `scraped_at` | yes | ISO-8601 UTC timestamp |
| `data` | yes | Free-form payload — depends on `type` (see below) |
| `metric_key` | optional | Original metric tag from extractor (`X-hiring_snapshot`, `pypi_downloads`, etc.) |

`lastWritten` is set on every append.

---

## Types

| Type | Source-types that produce it | Typical `data` payload |
|---|---|---|
| `hiring_snapshot` | `ats_api` | `open_roles_total`, `open_roles_ai_titled`, `ai_titled_pct` |
| `package_downloads` | `package_index` | `daily`, `weekly`, `monthly` |
| `github_repo` | `github_repo` | `stars`, `forks`, `open_issues`, `last_commit` |
| `sec_filing` | `sec_filing` | `form_type`, `filing_date`, `accession`, `summary` |
| `patent_snapshot` | `patent_index` | `count_total`, `count_ai_titled`, `recent` |
| `power_project` | `permit_db` | `mw`, `commission_year`, `region` |

New types: extend `TELEMETRY_METRIC_KEYS` / `TELEMETRY_SOURCE_TYPES` in `scripts/_telemetry_router.py`, document here.

---

## Routing rules (what enters this feed vs vault-inbox)

A claim routes here if **any** of:

1. `source.type` ∈ `{ats_api, package_index, github_repo, sec_filing, patent_index, permit_db}`
2. `claim.metric_key` ∈ `{X-hiring_snapshot, X-patent_snapshot, X-power_project, pypi_downloads, npm_downloads, docker_pulls, github_stars, recent_filings}`
3. `claim.metric_key` starts with `X-` or ends with `_downloads`

Otherwise → `vault-inbox.json` (human review queue).

Detection lives in `scripts/_telemetry_router.py:is_telemetry()`. Router function `route_or_inbox()` is the single entry point used by `monitor_sources.py` and `scan_sources.py`.

---

## Inspection

Read-only admin view at `telemetry.html` (password-gated, same SHA pattern as `review.html`). Filterable by entity / type / date. Linked from `admin.html` Command Centre nav.

Telemetry **never** enters `review.html`. There is no per-item decision required.

---

## Lifecycle

- **Append-only**: items are never edited or removed in place
- **No automated migration** of existing telemetry-shaped items already in `vault-inbox.json` — they age out via the materiality lane (wq-040)
- **Release gate** (`scripts/release-check.mjs`): after 2026-06-01 the `telemetry-routing` validator fails the build if any `vault-inbox.json` item matches the routing rules above (transitional grace until then)
- **Archival**: when this file exceeds ~5 MB, plan a separate brief — out of scope for v1

---

## Consumers (future)

Telemetry doesn't auto-update entity records. Specific consumer scripts may opt in to enrich (e.g. populate `entities.json:current.tokens_per_day` from PyPI download trends). Each enrichment lives behind its own brief; this schema does not prescribe consumer behavior.
