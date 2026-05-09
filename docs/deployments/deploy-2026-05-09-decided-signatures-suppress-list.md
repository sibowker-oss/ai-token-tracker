# Deployment: server-side decided-claims suppress list

**Date:** 2026-05-09
**WQ:** none (operational fix, surfaced during the same 2026-05-09 review session as the LaunchAgent deploy)
**Branch/Commit:** main (uncommitted at time of writing)

## What shipped

A signature-based suppress list that stops claims.html (and review.html, by
extension) from resurfacing items the user has already decided. Closes the
"I emptied my inbox an hour ago, why is it still full?" gap discovered in
the same session.

### Symptom that triggered this

User submitted decisions on the curated + candidates pool ~12:31. Pipeline
applied 11 datapoint writes, vault-inbox.json statuses updated correctly,
site-data.json regenerated. But on next page load claims.html re-loaded the
same 71 candidate claims from the same files (which are never pruned) and
showed them as pending again — because the only "have I seen this?" check
was the browser localStorage decisions blob, which gets cleared on successful
submit. State wasn't broken; the loader just had no server-side memory.

### Files changed

- `scripts/_decided_signatures.py` (NEW)
  - `claim_signature(c)`: stable fingerprint = `entity|metric|value_display|source_url|time_period`
    (lowercased, whitespace-stripped). Falls back to `claim:<first 200 chars>`
    if no structured fields present.
  - `claim_signature_fallback(c)`: claim-text-only signature, emitted alongside
    the structured one so historical decisions (which only carried `id+claim+note`
    for declined/parked) still match items loaded with full structured fields.
  - `record_decisions(payload)`: idempotent append to
    `data-updates/decided-signatures.json` keyed by signature, with
    `{decision, decided_at}` value.

- `scripts/admin_server.py`
  - After saving the decision file, calls `record_decisions()` so the index
    is current before apply_pipeline runs and well before the user reloads.
    Wrapped in try/except — index write failure is non-fatal and warns to
    stderr; the decision itself still goes through.

- `scripts/backfill_decided_signatures.py` (NEW)
  - One-time seed: walks every file in `data-updates/decisions/` and records
    signatures into the index. Idempotent — safe to re-run any time.
  - Already executed once: indexed 346 signatures across 3 historical
    decision files (116 accepted, 228 declined, 2 parked).

- `claims.html`
  - Added `claimSignature()` and `claimSignatureFallback()` functions —
    identical logic to the Python helper. Comment in both files cross-references
    the other so they stay in sync.
  - `loadClaims()` now fetches `data-updates/decided-signatures.json`, builds
    a Set, and filters out matching items before they hit the renderer.
    Index missing → graceful no-op (first run, no decisions yet).
  - `writeApprovedClaims()` now sends the full claim object for declined/parked
    decisions instead of just `{id, claim, note}`, so server-side signature
    emission can fingerprint them the same way it does accepted ones.
    `_sync_inbox_status` only reads `.id` so the extra fields are inert there.

- `data-updates/decided-signatures.json` (NEW data file)
  - Flat dict `{signature: {decision, decided_at}}`.
  - Initial content seeded by the backfill: 346 signatures.

## Decisions made during implementation

- **Fingerprint composition.** Chose `entity|metric|value|source_url|time_period`
  over a content hash because (a) it's human-readable for incident debugging,
  (b) the file stays diff-friendly in git, (c) the fields are present on every
  claim path (curated, candidates, structured, narrative). Collision risk
  exists (two different items with identical entity/metric/value/source/period)
  but in practice such items are *the same claim duplicated* and should be
  suppressed together.

- **Dual signature (structured + fallback).** Historical declined/parked
  decisions only carried `claim` text. Without a fallback they wouldn't match
  the structured signature computed at page-load. Emitting both signatures per
  item costs a few KB and removes a sharp edge.

- **Server-side suppress list, not entry pruning.** Considered the
  user-pre-authorised "move processed curated files into data-updates/processed/"
  approach but it only covers 3 curated files; ~70 of the resurfacing items
  came from the candidates path. User reconfirmed the wider approach
  before I proceeded.

- **Filter at load time, not via curated-index editing.** Edits to
  curated-index.json would be lossy — once a file is marked processed, the
  page can't show partial-decision pending items from inside it. Filtering
  at the item level handles partial sessions cleanly.

- **Async index fetch, optional.** If `decided-signatures.json` is missing
  (404) the page loads as before. No hard dependency. Same defensive posture
  as the existing fetches in claims.html.

- **Wrapped admin_server import in try/except.** A bug in the signature module
  (or a future field-rename ripple) shouldn't be able to block decision submits.
  Decisions get written first; signatures are recorded best-effort. Logged to
  stderr (visible in `~/Library/Logs/tail-admin-server.error.log`).

- **No changes to apply_pipeline.py.** The pipeline's contract is "vault-inbox
  → entities → site-data" and is unaffected by the suppress list. Keeping the
  fix isolated to admin_server + the UI prevents accidental coupling.

## Open items

- **review.html not yet wired up.** This deploy fixes claims.html. review.html
  has the same architectural pattern (loads from vault-inbox + filters by
  status) but its load path is different — it filters by inbox `status` field
  rather than the candidate-pool pattern. The suppress list is harmless to
  apply there too but unnecessary for the user's current pain. Defer until
  symptom reported.

- **Index has no expiry.** Signatures accumulate indefinitely. Today: 346.
  At ~50 decisions/week that's ~2,500/year. Not a problem in absolute terms
  (file would be ~500KB after a year, well within fetch tolerance) but the
  flat dict shape will eventually deserve a bucket-by-month structure.
  Defer until the file crosses 1MB.

- **No way to "un-suppress" a claim.** If a user wants to revisit a decided
  claim, they currently have to manually delete the signature from the file.
  An override path exists for accepted writes (admin_server `/api/override`)
  but not a "re-litigate this declined claim" path. Out of scope today.

- **`scripts/_decided_signatures.py` is now a shared helper.** Underscore
  prefix signals "internal". If apply_pipeline ever needs the same fingerprint
  for its own purposes, importing it is fine. Watch for drift from the JS
  copy — the docstring + the comment in claims.html flag the dual-write
  contract.

## Acceptance criteria status

- [x] admin_server appends signatures on every successful POST /api/decision
- [x] Backfill seeds historical decisions (346 signatures from 3 files)
- [x] claims.html fetches the index and filters loaded claims
- [x] Filter is server-authoritative — survives localStorage clears, browser
      switches, machine swaps
- [x] Failure to write the index does NOT block decision submission
- [x] End-to-end simulation: of 71 candidate claims loaded, 71 are suppressed
      (matches the 71 decided in the prior session) — Simon should now see an
      empty claims.html on reload
- [ ] User-confirmed empty page on reload (pending — Simon to verify)
