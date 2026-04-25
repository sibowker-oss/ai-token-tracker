# Audit — orphan accepts in vault-inbox.json
Generated 2026-04-25 for wq-022 / wq-023 Phase 0.
Brief: briefs/active/2026-04-25-raw-pool-status.md §2

## Headline
- **Total accepted in vault-inbox.json:** 161
- **Metric-known** (`metricKey` set and not "unknown"): **71**
- **Metric-unknown** (`metricKey` missing/empty/"unknown"): **90**  ← Phase 3 migration target

## Strict-criterion split (per brief §2)

| Bucket | Count | Notes |
|---|---|---|
| Metric-known | 71 | `metricKey` populated |
| Metric-unknown | 90 | no `metricKey` — these are the migration candidates |
| **Total** | **161** | |

## Richer view — does the metricKey actually surface?
Claims with a `metricKey` that does **not** match any `vault-data.json` `dataPoints[].metricKey` are *de facto* orphans even though they pass the strict criterion: status=accepted, but no consumer.

| Bucket | Count |
|---|---|
| Metric-known **and** matches a vault-data dp | 36 |
| Metric-known but **no** matching vault-data dp | 35 |
| No metricKey at all | 90 |
| **Total accepted** | **161** |

So the *effective* orphan count under the richer rule is **125 / 161** (77%). The brief's §5 migration only catches the 90 with no metricKey; the 35 with a non-matching key are a follow-up question (out of scope here).

## Recent batch (46 most recently accepted)
Brief §2 Q1 referenced "wq-018 first batch — accept dates 2026-04-25", but no items have been accepted on 2026-04-25 yet (Simon hasn't cleared the new chip's queue). The 46 most recently accepted are the 30 from `accepted_at=2026-04-20` (legacy podcast-claims pass) plus the 16 from `decidedAt=2026-04-24` (the auto-clear rule run on hiring snapshots).

- 2026-04-20: 30 items (all metric-known)
- 2026-04-24: 16 items (all metric-known — auto-clear rule 1 only accepts `hiring_snapshot` types, which always carry a metricKey)
- **All 46 are metric-known.** None match the migration criterion.

## Spot-check — do recent metric-known accepts actually update site-data?

Brief §2 Q2: confirm 3 metric-known recent accepts updated their corresponding entries in site-data.json.

### `auto-20260423-src-069-1` — metricKey=`anthropic-hiring_snapshot`
- Accepted: 2026-04-24
- Claim: "anthropic — 144 AI roles / 448 total (2026-W17)..."
- Value: `144 AI roles`
- vault-data.json has matching dataPoint with this metricKey? **NO**
- site-data.json mentions claim id or metricKey? **NO**

### `auto-20260423-src-069-2` — metricKey=`glean-hiring_snapshot`
- Accepted: 2026-04-24
- Claim: "glean — 11 AI roles / 178 total (2026-W17)..."
- Value: `11 AI roles`
- vault-data.json has matching dataPoint with this metricKey? **NO**
- site-data.json mentions claim id or metricKey? **NO**

### `auto-20260423-src-069-3` — metricKey=`databricks-hiring_snapshot`
- Accepted: 2026-04-24
- Claim: "databricks — 130 AI roles / 838 total (2026-W17)..."
- Value: `130 AI roles`
- vault-data.json has matching dataPoint with this metricKey? **NO**
- site-data.json mentions claim id or metricKey? **NO**

**Finding:** all 3 spot-checked items are hiring snapshots from the 2026-04-24 auto-clear pass. Each carries a `<entity>-hiring_snapshot` metricKey, but vault-data.json has no dataPoints with that key, and site-data.json doesn't reference the items by id or metricKey. They're effectively orphans even though they pass the strict criterion. Hiring-snapshot data lives in a different shape (per `apply_decisions.py` and the chips/in-development pages) so the metricKey naming convention doesn't line up with the vault-data dataPoint catalogue. This validates §1 of the brief — a metricKey alone doesn't guarantee surfacing.

## Producers contributing to the orphan-Accept pile

| Producer | Orphan count |
|---|---|
| OpenAI | 15 |
| Sacra | 9 |
| The Information | 6 |
| ChatGPT | 5 |
| CNBC | 3 |
| Bloomberg | 3 |
| Super.com | 3 |
| OpenRouter | 2 |
| GPUnex | 2 |
| Crunchbase News | 2 |
| U.S. businesses | 2 |
| TechCrunch / Bloomberg | 2 |
| Ed Zitron | 1 |
| Ed Zitron / confirmed methodology | 1 |
| The Information / multiple | 1 |
| Fortune | 1 |
| Microsoft / Tech-Insider | 1 |
| Salesforce / Business Wire | 1 |
| ServiceNow | 1 |
| Seeking Alpha | 1 |

## Migration candidate list (Phase 3 input) — 90 items

Items in vault-inbox.json with `status=accepted` AND no `metricKey`. These are what `scripts/migrate_orphan_accepts.py` will move to `status=raw_pool`.

```
email-20260328-a1x
email-20260328-c3z
email-20260328-d4w
email-20260328-f6u
email-20260328-g7t
email-20260328-h8s
email-20260328-i9r
email-20260328-j0q
extract-20260402-src-021-1
extract-20260402-src-021-10
extract-20260402-src-021-13
extract-20260402-src-021-15
extract-20260402-src-021-18
extract-20260402-src-021-19
extract-20260402-src-021-2
extract-20260402-src-021-20
extract-20260402-src-021-7
extract-20260402-src-021-9
extract-20260402-src-022-1
extract-20260402-src-022-11
extract-20260402-src-022-12
extract-20260402-src-022-13
extract-20260402-src-022-14
extract-20260402-src-022-15
extract-20260402-src-022-18
extract-20260402-src-022-2
extract-20260402-src-022-6
extract-20260402-src-022-8
scan-20260330-b2c
scan-20260330-c3d
scan-20260330-d4e
scan-20260330-e5f
scan-20260330-f6g
scan-20260330-g7h
scan-20260330-h8i
scan-20260330-i9j
scan-20260330-j0k
scan-20260330-k1l
scan-20260331-a1b
scan-20260331-b2c
scan-20260331-c3d
scan-20260331-d4e
scan-20260331-e5f
scan-20260331-f6g
scan-20260331-g7h
scan-20260401-a1b
scan-20260401-b2c
scan-20260401-c3d
scan-20260401-d4e
scan-20260401-e5f
scan-20260401-f6g
scan-20260401-g7h
scan-20260401-h8i
scan-20260403-src-009-1
scan-20260403-src-009-2
scan-20260403-src-009-7
scan-20260403-src-010-1
scan-20260403-src-010-2
scan-20260403-src-010-3
scan-20260403-src-010-4
scan-20260403-v1a
scan-20260403-v1c
scan-20260403-v1d
scan-20260403-v1e
scan-20260404-c3d
scan-20260404-d4e
scan-20260405-a1b
scan-20260405-b2c
scan-20260405-d4e
scan-20260405-e5f
scan-20260406-a1b
scan-20260406-b2c
scan-20260406-c3d
scan-20260406-d4e
scan-20260407-b2c
scan-20260407-c3d
scan-20260408-b2c
scan-20260408-d4e
scan-20260409-a1b
scan-20260409-b2c
scan-20260409-c3d
scan-20260410-a1x
scan-20260410-c3z
scan-20260410-d4w
scan-20260410-e5v
scan-20260411-a1b
scan-20260411-b2c
scan-20260411-d4e
zitron-20260328-e5
zitron-20260328-f6
```
