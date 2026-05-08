# Decision: D7 — defer dashboard.providers / dashboard.topConsumers removal

**WQ:** wq-099
**Date:** 2026-05-09
**Context:** wq-099 D7 instructs me to delete `dashboard.providers` and
`dashboard.topConsumers` from `site-data.json`, framed as cleanup since they
were "emptied by wq-096" and "no longer written by the wq-098 apply
pipeline". Investigation against the actual repo state shows the brief's
premise is wrong — both blocks are populated and actively read/written:

- `site-data.json:dashboard.providers` has 10 entries (OpenAI, Anthropic,
  Google/Gemini, ByteDance, Alibaba/Qwen, Tencent, Meta, Baidu, DeepSeek,
  Minimax) carrying `tokens / arrNumeric / arrAsOf / arrSource / provenance`
  used by both providers-table renders and `auto_update.py`'s self-hosted
  ("Others") tokens calibration.
- `site-data.json:dashboard.topConsumers` has 57 entries with
  `arrNumeric / tokensNumeric / providers / arr / valuation` — written by
  `apply_pipeline.py:update_top_consumers` (the wq-098 deployment record
  explicitly cites `dashboard.topConsumers[Cursor (Anysphere)].arrNumeric =
  2_000_000_000` as acceptance criterion #5) and read by `vault.html`
  in five places.
- The "new structures" the brief's §6.4 references (top-level `providers` /
  `topConsumers` blocks per wq-096) **do not exist in `site-data.json`**.
  There is no destination to redirect consumers to.

Active writers I'd need to retire to remove these blocks:

| Path | Role |
|---|---|
| `scripts/apply_pipeline.py:390-433` | `update_top_consumers` |
| `scripts/apply_handlers/arr.py:103-108` | usedOn marker for ai_app + model_provider |
| `scripts/wq096_emit.py:66-69, 217+` | tier-tags providers, builds frontier ARR entries |
| `scripts/generate_site_data.py:352, 452` | refreshes `dashboard.providers` from entity snapshots |
| `scripts/auto_update.py:169-179` | writes `dashboard.providers.Others.tokens` from Docker pulls |

Active readers I'd need to repoint:

| Path | Role |
|---|---|
| `vault.html:1946,1948,1970,2029,2174,2226` | sort, edit, lookup |
| `beta/vault.html` | same |

## Options

1. **Option A — Defer D7.** Ship wq-099 Phases A/B/C/D minus D7. Treat the
   removal as a separate work item once a destination structure exists.
   Pros: unblocks the visibility surface today; matches the brief's own
   §8 out-of-scope spirit (don't churn working code). Cons: legacy blocks
   linger.

2. **Option B — Migrate now.** Build the top-level `providers` /
   `topConsumers` structures the brief assumed, repoint all writers and
   readers (5 scripts, 7 read-sites), then delete the dashboard.* blocks.
   Pros: ledger-cleanliness goal achieved. Cons: ~1 session of work that
   is itself wq-098-shaped (apply pipeline + render contract); high risk of
   silently breaking provider widgets / vault.html if a consumer is
   missed; entirely orthogonal to wq-099's actual goal (visibility +
   reconciliation + alerts).

3. **Option C — Empty in place.** Set `dashboard.providers = {}` and
   `dashboard.topConsumers = []` to "delete the data" without deleting
   the keys. Pros: superficial cleanup, avoids breaking key-readers.
   Cons: drops live entity ARR / token data that vault.html and
   auto_update.py depend on; would need manual repopulation; no
   meaningful difference from what wq-096 would have done if it had
   actually emptied them.

## Recommendation

**Option A — defer D7.** Three reasons:

1. The brief's premise is factually wrong — these blocks aren't empty,
   they're load-bearing. Acting on a false premise risks silent breakage.
2. wq-098 (which shipped yesterday) explicitly writes to and depends on
   these structures. Removing them undoes the wq-098 contract.
3. The visibility-surface goal of wq-099 is independent of legacy
   removal. Phases A–D ship cleanly without touching D7.

If you want the cleanup, I'd write it up as a fresh brief (e.g.
"wq-099b — providers / topConsumers contract migration") with explicit
producer→consumer repoint plan and a destination schema. That brief
would benefit from clarity on whether the new top-level structures
should mirror today's shape exactly or take the opportunity to
restructure (per-period rather than a flat `current` snapshot, etc.).

## Resolution

[LEFT BLANK — resolved in Cowork]
