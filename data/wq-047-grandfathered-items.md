# wq-047 — grandfathered telemetry items in vault-inbox.json

Snapshot taken **2026-05-03** at the moment the telemetry router (`scripts/_telemetry_router.py`) shipped. These items were already in `vault-inbox.json` before the router existed and would have routed to `data/telemetry-feed.json` under the new rules. They are **not migrated** — per brief §3 #6 they age out via the existing materiality lane (wq-040).

The release-check `telemetry-routing` validator emits these as `advisory` until **2026-06-01**, then promotes to `fail`. By that date all six should have aged out (current `status=raw_pool`, surfaced in context lane only).

## Counts

- Total queueable items in `vault-inbox.json`: **991**
- Telemetry-shaped items: **6** (~0.6% of queue)
- All are `hiring_snapshot` from `ats_api` sources

## Per-source breakdown

| Source | Count | Items |
|---|---|---|
| `src-069` | 1 | `auto-20260501-src-069-1` (anthropic hiring) |
| `src-070` | 1 | `auto-20260501-src-070-1` (mistral hiring) |
| `src-071` | 4 | `auto-20260501-src-071-7` (perplexity), `-8` (elevenlabs), `-9` (runway), and one more |

All have `status=raw_pool` — they are not in the active review queue, just in the materiality context lane.

## What happens next

1. **No migration**: existing items stay in `vault-inbox.json`; consumers who care about historical hiring data can still find them via the inbox API
2. **New scrapes route via `is_telemetry()`**: anything matching `sourceType ∈ TELEMETRY_SOURCE_TYPES` or `metricKey ∈ TELEMETRY_METRIC_KEYS` lands in `data/telemetry-feed.json` from now on
3. **2026-06-01**: `validate-telemetry-routing.mjs` switches from advisory to fail; if any of these six are still in inbox by then, they need manual archival or the materiality lane needs a sweep

## Detection logic verification

Sample run of the validator on this snapshot:

```
telemetry-routing: 0 fail · 4 advisory
  [advisory] vault-inbox.json — 1 telemetry item(s) from src-069 routed to inbox …
  [advisory] vault-inbox.json — 1 telemetry item(s) from src-070 routed to inbox …
  [advisory] vault-inbox.json — 4 telemetry item(s) from src-071 routed to inbox …
  [advisory] vault-inbox.json — mode: transitional until 2026-06-01 · 6 total offender(s) across 3 source(s)
```

Reproducer: `node scripts/validate-telemetry-routing.mjs`.
