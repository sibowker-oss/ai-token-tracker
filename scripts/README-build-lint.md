# Build lint

> **Superseded 2026-04-23.** `scripts/build-lint.js` has been replaced by `scripts/validate-provenance.mjs`, which implements everything below plus ISO date shape checks, `revenueType` for revenue entries (§4.5), source-registry cross-reference (§11.2), and `dataReferences` reconciliation (§5.3.1). The `npm run build-lint` alias now points to the new validator. This file is retained for reference; the legacy script will be removed in a follow-up commit.
>
> Installed as part of the §11 release-check runbook — see `TESTING.md` and `briefs/active/2026-04-23-testing-runbook.md`.

---

`scripts/build-lint.js` is the GUIDELINES §5.5 enforcement script.

## What it checks

For every datapoint in `site-data.json` (any object with a `source` field and a `value`/`min|max|medianMonths`):

1. **Required provenance fields** present and non-empty: `value`, `label`, `unit`, `year`, `source`, `sourceUrl`, `retrievedAt`, `nextReview`, `confidence`. (Lead-time ranges swap `value` for `min|max|medianMonths`.)
2. **`nextReview` not in the past** — per §5.5, a past-due review fails the build.
3. **Labels are publish-ready** — flags label values that look like slugs (`ai_application`, `global-gdp`) per §5.6.
4. **Confidence enum** — must be `High | Med | Low` per §4.4.
5. **Sources registry exists** at `data/sources.registry.md`.

## What it does NOT yet check (planned)

- **Backfill-on-new-field** (§5.2) — requires a schema diff vs a previous canonical version. TODO: add a pinned schema snapshot.
- **Cross-page reconciliation** (§5.3.1) — requires `meta.dataReferences` map in `site-data.json`. TODO: populate `dataReferences` and add a consistency check.
- **Link checker** on `sourceUrl` — external HTTP; run in a separate CI job to avoid flaky builds (see §11.4).
- **Sources-log correspondence** — every changed value should have a row in `sources.log.md`. TODO when the log file is no longer empty.

## Usage

```bash
# Default — fails on any issue
node scripts/build-lint.js

# Report issues but don't fail (useful locally)
node scripts/build-lint.js --warn

# Silent on success
node scripts/build-lint.js --quiet
```

## Wiring into CI

Add to `.github/workflows/`:

```yaml
- name: Data integrity lint
  run: node scripts/build-lint.js
```

Keep it as a required check on the branch that publishes to Pages.

## Running locally before promotion

Per GUIDELINES §3.2, any In-Dev → live promotion must pass the lint. Run it from the repo root before merging the promotion PR.
