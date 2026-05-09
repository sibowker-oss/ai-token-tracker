# Deployment: Claims review — fix unit mismatch in impact strip

**Date:** 2026-05-09
**WQ:** (none — drive-by bug fix surfaced during review of wq-098 pipeline output)
**Branch/Commit:** main (uncommitted)

## What shipped

- [claims.html](../../claims.html) — rewrote `getImpact()` to prefer the structured comparison fields the wq-098 extractor already emits (`existing_value`, `value`, `value_display`, `unit`, `delta_pct`, `comparison_type`). Added a small `fmtClaimValue(value, unit)` helper that formats by unit string ("USD_B", "USD_M", "MW", "%", etc.).
- [beta/claims.html](../../beta/claims.html) — same patch for parity (the beta surface has an identical copy of `getImpact()`).
- The legacy siteData-lookup branch (provider ARR / consumer ARR) is preserved as a fallback for older claim shapes that lack structured comparison fields, but it now sits behind the structured path so modern claims never hit it.

## The bug

The inline impact strip on a claim card (`old $X · new $Y · ±Z%`) was rendering `new $0.0B · -100.0%` for any claim with `unit: "USD_B"` and a numeric `value` already scaled to billions.

Root cause: `getImpact()` ignored the structured `existing_value` / `value_display` the upstream pipeline already computed, and instead re-derived from `siteData.dashboard.providers`, doing `claim.value / 1e9` — which assumes raw dollars. For `value=30` (already in $B), that produces `3e-8 → "$0.0B"`. The "old $25B" half looked correct only by coincidence, because `siteData.providers.OpenAI.rev = 25` (already in B).

The dedup-note row at the bottom of the same card was always correct (`"Updates ledger ARR of $25B to $30B …"`) because it used the pipeline's own `dedup_note` string verbatim.

Verified against the OpenAI / $30B claim in [data-updates/2026-05-05-curated-smoke-test-may2026.json](../../data-updates/2026-05-05-curated-smoke-test-may2026.json):

| Field | Before patch | After patch |
| --- | --- | --- |
| `current` | `$25B` (right by accident) | `$25B` |
| `proposed` | `$0.0B` | `$30B` |
| `pctChange` | `-100.0` | `20.0` |

## Decisions made during implementation

- **Use structured fields, don't try to fix unit-conversion in the legacy path.** The pipeline already does the comparison correctly; making the UI re-derive units from siteData is brittle (every new unit added to the pipeline is a new way for the UI to drift). The legacy path stays only as a safety net.
- **Kept `fmtClaimValue` deliberately small** — it covers the unit strings the pipeline currently emits (`USD_B`, `USD_M`, `MW`, `%`) and falls through to `value + ' ' + unit` for anything else. No attempt to be a generic formatter.
- **Did not touch `beta/review.html`** — its `getImpact()` reads from `entity.financials[year][fieldId]` directly and never assumes a dollar denomination, so it is not affected by this bug.
- **Patched `beta/claims.html` in lockstep** with the live `claims.html` since both surfaces share the same code path; leaving beta broken would just confuse the next person who diffs them.

## Open items

- This is an admin-only surface (password-gated by SHA-256 in [claims.html:7-20](../../claims.html#L7-L20)) so the Publishing Gate does not apply — no production deploy step needed.
- Worth a follow-up audit: any other admin surface that consumes inbox claims and renders them with assumed units (e.g. impact-preview modal in `submitDecisions()` at [claims.html:747-759](../../claims.html#L747-L759)) — that modal also calls `getImpact()`, so it inherits the fix automatically. No code change needed there, just worth confirming visually next time the reviewer hits a major-change accept.
- No regression test — the review queue currently has no JS test harness. If wq-099/wq-100 add one, this would be a good first fixture (claim with structured comparison fields → assert the rendered impact strip).

## Acceptance criteria status

- [x] Inline impact strip on the OpenAI / $30B card shows `old $25B · new $30B · +20.0%` (matches the pipeline's `comparison_note`)
- [x] First-time claims (no `existing_value`) still render the `first-time` badge — structured path is skipped, legacy fallback returns null, render falls through to the `else if (c.value != null)` branch
- [x] Same-value claims (`delta_pct: 0`, e.g. the OpenAI biz_pct=42 confirmer in the same intake file) render as `0.0%` rather than misleading numbers
- [x] beta/claims.html patched identically
