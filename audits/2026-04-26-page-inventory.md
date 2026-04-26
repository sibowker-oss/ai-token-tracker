# Page Inventory — wq-031 Phase 0

Source: brief §4.1 confirmed table (Simon, 2026-04-26) + filesystem inventory at HEAD `ab97a10`.
Output: `data/page-registry.json` — 87 entries covering every .html in the repo
outside `node_modules/`, `tests/reports/`, `data/snapshots/`, `data-updates/archive/`.

## By status

| Status | Count | Folder |
|---|---|---|
| `live` | 12 | repo root |
| `admin` | 11 | repo root + `data-updates/` |
| `concept` | 5 | repo root |
| `retired` | 6 | repo root (4 pending move) + `archive/` (1) + repo root (1 in-place) |
| `parked` | 10 | `parked/` |
| `beta` | 38 | `beta/` |
| `newsletter` | 5 | `newsletters/` |
| **Total** | **87** | |

## Deltas vs brief §4.1

The brief listed approximate counts that diverge from the actual filesystem; using the actual count for the registry.

| What | Brief §4.1 | Actual | Note |
|---|---|---|---|
| `/beta/*.html` | 49 | 38 | Brief over-counted. Registered 38. |
| `/parked/*.html` | 9 | 10 | Brief under-counted. Registered all 10 (calculator, capex, capital-sankey, compute-stack, counter, estimator, feed, projection-review, timeline-forward, workforce). |
| Live (root) | 11 | 12 | `follow-the-trillion.html` not in §4.1. See ambiguity #1. |
| Admin (root) | 9 | 10 | `review.html` not in §4.1. See ambiguity #2. Plus the §4.1 admin list (admin, add, ask, claims, vault, source-ledger, sources, settings, archive). |

## Ambiguities — newly discovered, defaulted with provenance

These are .html files in the repo not classified in brief §4.1. The registry
has each one classified with my best default + a `_provenance` field naming
this audit. Flag for Simon's confirm.

### Ambiguity 1 — `follow-the-trillion.html` not in brief §4.1

- **Default:** `live`.
- **Reasoning:** Public-facing FTBT chart page (Follow the Trillion). Has a hero `<h1>` and links into the Ledger — same shape as capital.html / revenue.html / etc. Cited by the wq-016 audit (line 252, `$34T` literal in a `.ftbt-value` tile). First commit 2026-04-22, same wave as the v2 ledger pages.
- **Risk if wrong:** If it should be `concept`, build-lint will surface the `$34T` literal as a dataReferences warning that it currently doesn't (concept skips dataReferences). Easy registry edit to flip.

### Ambiguity 2 — `review.html` not in brief §4.1

- **Default:** `admin`.
- **Reasoning:** The hosted-admin review queue UI — accept/decline/park/raw_pool over `vault-inbox.json`. The same `review.html` traced by the wq-021 P0 byte-level analysis and targeted by the wq-029 brief. Title tag is `Daily Review — Admin`. Calls `GitHubAPI.commitFiles`.
- **Risk if wrong:** None likely — the function and naming both point at admin.

### Brief §4.1 transcribed verbatim with no ambiguity

| Path | Status from §4.1 | In registry? |
|---|---|---|
| `index.html` | live | ✓ |
| `capital.html` | live | ✓ |
| `revenue.html` | live | ✓ |
| `usage.html` | live | ✓ |
| `power.html` | live | ✓ |
| `openrouter.html` | live | ✓ |
| `in-development.html` | live | ✓ |
| `timeline.html` | live | ✓ |
| `about.html` | live | ✓ |
| `methodology.html` | live | ✓ |
| `changelog.html` | live + `lintExclusions: ["dataReferences"]` | ✓ (with exclusion) |
| `admin.html` | admin | ✓ |
| `add.html` | admin | ✓ |
| `ask.html` | admin | ✓ |
| `claims.html` | admin | ✓ |
| `vault.html` | admin | ✓ |
| `source-ledger.html` | admin | ✓ |
| `sources.html` | admin | ✓ |
| `settings.html` | admin | ✓ |
| `archive.html` | admin | ✓ |
| `ipo-watch.html` | concept | ✓ |
| `subsidy-clock.html` | concept | ✓ |
| `predictions.html` | concept | ✓ |
| `benchmarks.html` | concept | ✓ |
| `confidence.html` | concept | ✓ |
| `dashboard.html` | retired → archive/dashboard-v1.html | ✓ (`pendingMove: true`) |
| `chips.html` | retired → archive/chips-v1.html | ✓ (`pendingMove: true`) |
| `sankey.html` | retired → archive/sankey-v2.html | ✓ (`pendingMove: true`) |
| `v1-review.html` | retired → archive/v1-review.html | ✓ (`pendingMove: true`) |
| `page-archive.html` | retired-or-merge | ✓ (status=retired, no pendingMove — folded into archive.html during P4 instead) |
| `archive/sankey-v1.html` | retired (already in archive/) | ✓ |
| `data-updates/review-consumers.html` | admin | ✓ |
| `/beta/*.html` (49) | beta | ✓ (38 actual) |
| `/parked/*.html` (9) | parked | ✓ (10 actual) |
| `/newsletters/brief-*.html` (5) | newsletter | ✓ |

## The transition shape — `pendingMove` field

P0 freezes the registry against the **target** lifecycle for each page, but
four pages (dashboard, chips, sankey, v1-review) physically move during P2.
The registry expresses this transition state so the validator (Phase 1)
passes against the P0 state:

```json
{
  "path": "chips.html",
  "status": "retired",
  "pendingMove": true,
  "pendingMoveTo": "archive/chips-v1.html",
  ...
}
```

- `path` is the **current filesystem location** (root) — keeps the rule "every .html in repo appears once" intact.
- `pendingMove: true` flags the entry as transitional — the validator skips the strict folder-vs-status check for entries with this flag set.
- `pendingMoveTo` is the **target archive path**.

After the P2 commit moves the file, the registry entry is rewritten:
- `path` becomes `archive/<name>-v1.html`
- `pendingMove` and `pendingMoveTo` removed
- Folder-status rule then enforces normally.

## Cross-reference graph

`supersedes` / `supersededBy` chains in the P0 registry:

- `index.html` ← `archive/dashboard-v1.html` (post-P2: `dashboard.html` until then)
- `capital.html` ← `archive/chips-v1.html` (post-P2: `chips.html` until then)
- `revenue.html` ← `archive/sankey-v2.html` (post-P2: `sankey.html` until then), `archive/sankey-v1.html`
- `archive.html` ← `page-archive.html` (folded in P4)

`supersedes` / `supersededBy` rule deferred to Phase 1's validator. P0
registry uses `null`/`""` consistently and the validator resolves both
sides.

## Excluded from registry (per brief §3.2)

- `node_modules/**` — vendor
- `tests/reports/**` — test output
- `data/snapshots/**` — source-scrape artefacts
- `data-updates/archive/**` — archived review-decisions payloads

These are reachable filesystem paths but **not** registry-tracked. Phase 3's
build-lint root-page-fail rule will only fire on root-level .html files
absent from the registry; nested directories still escape.

## Phase 0 acceptance — open

- [x] Registry covers every .html outside excluded dirs (87 entries)
- [x] Every entry has `path`, `status`, `title`, `purpose`, `supersedes[]`, `supersededBy`, `addedOn`, `retiredOn`, `lastReviewed`
- [x] Retired entries have `supersededBy` + `retiredReason`
- [x] Pending-move entries flagged with `pendingMove: true` + `pendingMoveTo`
- [x] Concept entries documented with one-liner purpose
- [x] All ambiguities written here, not into the registry as silent guesses
- [ ] Validator runs clean (lands in Phase 1; this acceptance is bound to it)
- [ ] Simon confirms ambiguities (#1 follow-the-trillion = live, #2 review.html = admin)

## Notes for follow-on phases

- **P1 validator** must understand the `pendingMove` transition state (skip folder check when set; insist `pendingMoveTo` resolves to a folder allowed by `status`).
- **P2 commits** rewrite the four registry entries: drop `pendingMove` / `pendingMoveTo`, set `path` to the archive path. Each P2 commit should change the registry in lockstep with the `git mv`.
- **P3 build-lint** also needs to handle `pendingMove` on read — until P2 is fully done, the registry briefly has retired-pending entries at root paths. The dataReferences gating uses status, not folder, so this is automatic; the unregistered-root-page-fail rule needs to count an entry's current `path` (not `pendingMoveTo`) as the registered identity.
- **P4 archive.html** renders Concepts / Retired / Parked sections from the registry. The `page-archive.html` entry is `status: retired` without `pendingMove` because §4.1 calls it "retired-or-merge" (folded in, not moved); P4 either deletes the file or stubs it.
