# Decision: Publish-gate exception — inbox rebase-stomp recovery

**WQ:** wq-103
**Date:** 2026-05-13
**Context:** After completing the inbox recovery (3 vault dps minted from
backfilled src-107 items + admin_server hardening), Simon explicitly
invoked the publish step in chat with "push live pls" → "no, I'm
explicitly am asking you to ship it" before any staging-preview deploy.

## Why staging-first was bypassed

1. **Visible delta is zero.** The only entity-level change is
   `Mistral.financials.2026.valuation = 12.85` in `entities.json`.
   `ipo-watch.html` carries Mistral as hardcoded JS literal at $6.2B
   and reads from that array, not from `entities.json` /
   `site-data.json` — so the new value does not surface on any
   rendered public page. OpenAI 2026.arr and Anthropic 2026.arr were
   `[OK-EQUAL]` per `data/apply_pipeline.log` (already at value).
   The remaining changes are: vault-inbox status flips, vault-data
   provenance for 3 dps, regenerated site-data.json with no moved
   rendered numbers, internal audit docs, decision-trail JSON, the
   admin_server.py hardening (local dev tool — not deployed), and
   the deployment record itself.
2. **No realistic preview path for this changeset.** The repo's only
   preview surface (`/beta/` via `deploy-beta.yml`) is itself served
   from `ai-index.hepburnadvisory.com.au/beta/` — already public.
   Local `python3 -m http.server` is the only true non-public preview,
   and Simon waived it on visible-delta-zero grounds.
3. **Operator gave explicit, in-session, repeated affirmative.** "push
   live pls" then "no, I'm explicitly am asking you to ship it" after
   I laid out the gate, the visible-impact analysis, and the proposed
   staging path.

## Mitigations applied

- Pre-commit verification: confirmed via grep that `12.85` does not
  appear in any root `*.html` and that ipo-watch's Mistral row reads
  from a JS literal, not from data files.
- Two-commit structure for review legibility (data recovery vs admin
  server hardening).
- Deployment record (`docs/deployments/deploy-2026-05-13-inbox-rebase-
  stomp-recovery.md`) carries the publish timestamp.

## Resolution

Approved by Simon in chat 2026-05-13. Logged here so the audit trail
records that this push bypassed staging-first deliberately rather than
through process drift, in line with the "If the staging-first sequence
is impossible" clause of the Publishing Gate.

[LEFT BLANK — confirm in next Cowork session whether this should move
to resolved/ or whether process should change to permit visible-delta-
zero data-only pushes without exception files.]
