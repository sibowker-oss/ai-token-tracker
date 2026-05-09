# Decision: Publish-gate exception — 2026-05-09 main push without staging

**WQ:** none (operational)
**Date:** 2026-05-09
**Context:** During the 2026-05-09 review session, Simon authorised a direct push to `main` (which auto-deploys to `ai-index.hepburnadvisory.com.au` via GitHub Pages) without going through the prescribed staging-first sequence (push to `beta`, review at `/beta/`, then promote). This decision file documents the exception per CLAUDE.md §"If the staging-first sequence is impossible / improvise around the gate."

## What changed in this push

Two distinct work streams batched into one push:

1. **Review-pipeline output from the 12:31 apply run** — accepted decisions on 11 datapoints applied by `apply_pipeline.py`:
   - OpenAI 2026.arr → $25B (already at value)
   - OpenAI 2026.revenue_annualised_from_m → $24B
   - OpenAI current.user_count → 800M (was 900M)
   - Anthropic 2026.arr → $30B (already at value)
   - Anthropic current.business_customer_count → 300,000
   - Anthropic 2024.burn_metric → 5.6
   - Cursor (Anysphere) 2026.valuation → $60B (was $50B)
   - Perplexity 2026.arr → $0.5B (was $0.2B)
   - CoreWeave current.user_count → 24
   - Super.com 2026.arr → $0.15B
   - OpenRouter current.tokens_per_week_t → 4.65
   - topConsumers[Perplexity].arrNumeric → $500M (was $200M)
   - `site-data.json` regenerated to match.

2. **Tooling fixes (claims-review workflow)**:
   - `admin_server.py` LaunchAgent for auto-start on login; SSL_CERT_FILE self-heal; `--no-browser` flag.
   - Server-side decided-claims signature suppress list (claims.html no longer resurfaces decided items).
   - One-time backfill of 346 historical signatures.
   - Two deployment records.

## Why staging was skipped

Three considerations:

1. **Tooling changes don't surface to the public.** The LaunchAgent is local-only. `admin_server.py` doesn't run on production. `decided-signatures.json` is consumed by admin pages (`claims.html`) which are localStorage-auth-gated. Staging can't show a meaningful difference for these.

2. **Data changes (the 11 datapoints) had already been reviewed by Simon in the claims.html UI** as part of the 12:31 session, with the impact-preview modal showing every major change before submission. The "preview" step the gate prescribes is partially fulfilled by the in-app impact preview (an admittedly weaker version of a true staging URL).

3. **Time pressure was minimal but real.** Simon was actively in a review session; rolling staging in mid-flow would have meant a context switch and a follow-up turn. The trade-off (skip staging, accept residual risk) was made knowingly with full visibility into the diff scope.

## Recommendation

This push proceeds. Mitigations applied:

1. The two commits are kept separate so the data change can be reverted independently of the tooling fix if a regression surfaces.
2. Both deployment records list the affected files and acceptance criteria.
3. Post-push verification: spot-check the four ledger pages whose numbers changed (Revenue, Capital, Usage if Perplexity ARR is surfaced there, top-consumers strip on the homepage).
4. **For next time**: the staging path (push to `beta`, deploy-beta workflow, review `/beta/`, then promote to `main`) is the documented norm. Today's exception is not a precedent.

## Resolution

Approved by Simon in chat 2026-05-09, after being shown:

- That `main` push is the production deploy (no separate publish step exists).
- That the diff includes the 12:31 review batch in addition to the tooling fixes.
- That the gate normally requires staging-first.
- The three-option choice (beta-first / main-direct-with-exception / split-tooling-only). Simon selected "Push main now, accept the gate exception."

[LEFT BLANK — resolution context for Cowork.]
