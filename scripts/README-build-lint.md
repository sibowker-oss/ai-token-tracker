# Build lint

> **Status — 2026-04-24 (wq-004).** `scripts/build-lint.js` is back in active use as the blocking CI gate, wired via [`.github/workflows/build-lint.yml`](../.github/workflows/build-lint.yml). It now complements (rather than being superseded by) `scripts/validate-provenance.mjs`:
>
> - **`validate-provenance.mjs`** remains the §4.2 / §4.4 / §4.5 / §5.5 / §5.6 / §11.2 datapoint-level validator. `npm run build-lint` still aliases to it.
> - **`build-lint.js`** owns the checks that need repo-wide context — schema diffs against `origin/main` and cross-page number reconciliation.
>
> Both scripts run in the release-gate workflow; either one failing blocks the merge. Installed as part of the §11 release-check runbook — see `TESTING.md` and `briefs/active/2026-04-23-testing-runbook.md`.

---

`scripts/build-lint.js` enforces GUIDELINES §5.5 plus two §11 release-gate checks added 2026-04-24.

## What it checks

### Per-datapoint (§5.5)

For every datapoint in `site-data.json` (any object with a `source` field and a `value`/`min|max|medianMonths`):

1. **Required provenance fields** present and non-empty: `value`, `label`, `unit`, `year`, `source`, `sourceUrl`, `retrievedAt`, `nextReview`, `confidence`. (Lead-time ranges swap `value` for `min|max|medianMonths`.)
2. **`nextReview` not in the past** — per §5.5, a past-due review fails the build.
3. **Labels are publish-ready** — flags label values that look like slugs (`ai_application`, `global-gdp`) per §5.6.
4. **Confidence enum** — must be `High | Med | Low` per §4.4.
5. **Sources registry exists** at `data/sources.registry.md`.

### Schema-diff (§11 scope trigger) — **error**

Compares the top-level keys of `site-data.json` against the version on `origin/main` (falls back to `main`). If any top-level key has been added or removed, the script requires that `changelog.html` contains a mention of that key. Fails with a message listing each unaccompanied add/remove.

- Requires full git history (`fetch-depth: 0` in CI). Silently skipped if no baseline ref is reachable.
- Matches verbatim: if you rename `sankey` → `capitalSankey`, both names must appear in the changelog body.

### `dataReferences` reconciliation (§5.3.1) — **warning**

Scans every `*.html` file at the repo root for large-number literals:

- currency amounts (`$17.47`, `$745B`, `$1.07T`)
- magnitude-suffixed numbers (`360T`, `1.2 billion`, `27 trillion`)

For each literal, the script tries to match it against any numeric value reachable anywhere in `site-data.json` — raw, or scaled up by 1K / 1M / 1B / 1T to handle the common case of storing `17.47` to mean `$17.47B`. Displayed numbers rounded to 2dp are also treated as a match.

Anything that doesn't match is emitted as a warning pointing the author at §5.3.1 ("no cross-page duplication; read from the canonical field"). **Currently advisory only** — the exit code is unaffected. It will be promoted to error once the current hits are cleaned up.

## What it does NOT yet check (planned)

- **Backfill-on-new-field** (§5.2) — requires a schema snapshot more granular than top-level keys. TODO: add a pinned schema snapshot and diff nested field sets.
- **Link checker** on `sourceUrl` — external HTTP; runs in a separate CI job to avoid flaky builds (see §11.4).
- **Sources-log correspondence** — every changed value should have a row in `sources.log.md`. TODO when the log file is no longer empty.

## Usage

```bash
# Default — fails on any error (warnings do not affect exit code)
node scripts/build-lint.js

# Report issues but don't fail (useful locally)
node scripts/build-lint.js --warn

# Silent on success
node scripts/build-lint.js --quiet
```

## Wiring in CI

[`.github/workflows/build-lint.yml`](../.github/workflows/build-lint.yml) is the blocking gate:

```yaml
- name: Build lint (§5.5 + schema-diff + dataReferences)
  run: node scripts/build-lint.js

- name: Provenance validator
  run: node scripts/validate-provenance.mjs

- name: Release check (strict mode)
  env:
    CHECK_MODE: strict
  run: node scripts/release-check.mjs
```

Any non-zero exit blocks the merge. Keep `fetch-depth: 0` on the checkout so the schema-diff step can see `origin/main`.

## Running locally before promotion

Per GUIDELINES §3.2, any In-Dev → live promotion must pass the lint. Run it from the repo root before merging the promotion PR.

```bash
npm ci
node scripts/build-lint.js
node scripts/validate-provenance.mjs
CHECK_MODE=strict node scripts/release-check.mjs
```
