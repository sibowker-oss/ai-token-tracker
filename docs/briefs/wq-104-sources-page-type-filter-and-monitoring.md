# wq-104 — Sources page: type-based filtering + per-source monitoring detail

**Parent context:**
- Chat decision, 2026-05-14. Simon: *"we have a set of source categories and each one has a different type of monitoring. Can we adjust the source page so that it shows and enables filtering by category and in addition shows the monitoring process."*
- Current `sources.html` (admin-only, password-gated) renders a flat list of every source in `sources-registry.json` (~140 entries), sorted active-first then by `last_claims_count` desc. Search-by-text works; **there is no filter dimension**.
- The registry has no explicit `category` field. Simon's call (2026-05-14) is to use the existing **`type`** field as the category axis. ~20 distinct `type` values exist today: `slide_deck`, `rss_feed`, `podcast_feed`, `web_page`, `web_scrape`, `api`, `gov_api`, `gov_dataset`, `iso_queue`, `ir_page`, `earnings_aggregation`, `sec_filing`, `regulatory_tracker`, `press_room`, `curated_dataset`, `cloud_dataset`, `ats_api`, `github_repo`, `package_index`, `newsletter`, `pdf`.
- Each `type` is monitored by a different process. `extraction_method` + `frequency` + `last_checked` + `next_check` already encode the monitoring shape, but the page doesn't expose any of it usefully — `extraction_method` shows as raw snake_case ("podcast_scraper") with no explanation of what that means.

**Stage:** Scoped — ready for VS Code pickup (pending D1/D3/D4 confirmation below)
**Priority:** M (admin diagnostic UX; no public-site impact)
**Owner:** Claude Code (implementation), Simon (D1/D3/D4 decisions, staging review)
**Status:** Scoped — awaiting_decisions on D1/D3/D4
**Estimated effort:** Small (single session; UI-only changes to one file plus a small JS constant map)
**Files touched (anticipated):**
- Modified: `sources.html` (filter UI, per-card monitoring block, type→label + extraction→description constant maps, freshness status derivation)
- Read-only inputs: `sources-registry.json`, `vault-data.json`, `vault-inbox.json`
- Possibly modified: `beta/sources.html` (if Simon wants the beta mirror updated in the same session)
- Not touched: `sources-registry.json` schema. No new fields. No backfill.

---

## 0. Decisions

**Locked (Simon, 2026-05-14):**
- **D-Cat — Category axis:** Use the existing `type` field as the category. No new `category` field, no schema migration. Friendly labels rendered at display time only.
- **D-Mon — Monitoring surface:** Per-card detail (no top-of-page legend). Each card must answer *"how is this source monitored?"* on its own.
- **D-Handoff — Workflow:** Full brief → Notion task → Claude Code in VS Code. Standard TAIL protocol.

**Open — need Simon's call before code lands:**

- **D1 — Filter UX shape.** Three options:
  - **D1a — Chip row (multi-select).** Horizontal row of chips above the list: "All (140)", "RSS Feed (28)", "Web Page (40)", etc. Click to toggle. Multiple chips can be active (OR filter). Counts always reflect total registry, not filtered set.
  - **D1b — Single dropdown.** A `<select>` with one type at a time. Cheapest implementation, but worse for scanning the spread of the registry.
  - **D1c — Collapsible grouped sections.** Replace the flat list with a section per type, collapsed by default. No filter — categories become structural. Search still works across all.
  - **Recommendation:** D1a. Multi-select chips give you the spread at a glance and let you say "show me everything that's API-shaped: `api` + `gov_api` + `ats_api`." D1c looks tidy but hides the long tail and breaks the active-first sort that today's page leans on.

- **D3 — Monitoring health indicator.** Two options:
  - **D3a — Derive from data.** Compute status at render time: ✓ Healthy if `last_checked` is within 1.5× `frequency`; ⚠ Stale if older; ✗ Never checked if `last_checked` is null; ⏸ Manual for `frequency: one_time` or `annual` (status is informational only). No registry change.
  - **D3b — Add `last_status` field to registry.** Each extraction script writes success/failure/error_message. UI reads it directly. More accurate, but requires touching every extraction script (`scrape_podcasts.py`, `scrape_signals.py`, `monitor_sources.py`, etc.) to write the field.
  - **Recommendation:** D3a for v1. Derived signal is right ~90% of the time and ships in one file. If false signal becomes annoying, follow-on brief upgrades to D3b.

- **D4 — Lock the friendly-label maps in this brief, or let Claude Code propose them?**
  - **D4a — Lock now.** §3 below defines the full `type → display label` map and the full `extraction_method → human description` map. Claude Code implements verbatim.
  - **D4b — Let Claude Code propose.** Claude Code drafts the maps, surfaces them for review, and edits after Simon's feedback. Adds one round-trip.
  - **Recommendation:** D4a. The maps are short, you can react to them here in the brief, and locking them now saves a session bounce.

---

## 1. Why this exists

The Sources page is the admin diagnostic for *"what's feeding the ledger and is it healthy?"* It answers two questions today:
1. How many sources exist, how many are active, how many claims have they produced. (Stats row.)
2. For a given search term, which sources match. (Text search.)

It doesn't answer the diagnostic questions that actually matter when something looks off:
- *"Are all my podcasts being scraped?"* — requires scrolling 140 entries and squinting at badges.
- *"Which government data feeds haven't been checked in a month?"* — same.
- *"What does `signal_scraper` even do, and when did it last run for OpenRouter?"* — the field is shown as raw snake_case with no explanation.

This brief makes the page answer those questions directly: filter to a category in one click, and read each source's monitoring story (process + cadence + freshness) on the card itself.

---

## 2. Architectural shape

```
sources-registry.json (unchanged)
        │
        │  type, extraction_method, frequency,
        │  last_checked, next_check, last_claims_count
        v
┌────────────────────────────────────────────────┐
│ sources.html                                    │
│                                                 │
│  Constants (new):                               │
│    TYPE_LABELS:        type → friendly label    │
│    EXTRACTION_DESCRIPTIONS:                     │
│                     extraction_method → prose   │
│    FREQUENCY_LABELS:   frequency → human cadence│
│                                                 │
│  Render:                                        │
│    1. Compute type counts → render chip row     │
│    2. Apply active-chip filter to source list   │
│    3. Per card:                                 │
│         - friendly type label badge             │
│         - Monitoring block (always visible):    │
│             • Process: <EXTRACTION_DESCRIPTIONS>│
│             • Cadence: <FREQUENCY_LABELS>       │
│             • Status: ✓ / ⚠ / ✗ / ⏸  (derived)  │
│             • Last: <date> · Next: <date>       │
│                                                 │
│  State:                                         │
│    activeTypes: Set<string>   (URL-synced)      │
└────────────────────────────────────────────────┘
```

URL state: filter persisted via `?types=rss_feed,podcast_feed` query param so the page is deep-linkable and reload-safe.

---

## 3. Friendly-label maps (D4a — pending lock)

### 3.1 `type` → display label

| Raw `type` | Display label |
|---|---|
| `slide_deck` | Slide Deck |
| `pdf` | PDF Report |
| `rss_feed` | RSS Feed |
| `podcast_feed` | Podcast Feed |
| `newsletter` | Newsletter |
| `web_page` | Web Page |
| `web_scrape` | Live Web Signal |
| `api` | API |
| `gov_api` | Government API |
| `gov_dataset` | Government Dataset |
| `cloud_dataset` | Cloud Dataset |
| `curated_dataset` | Curated Dataset |
| `iso_queue` | ISO Queue |
| `ir_page` | Investor Relations |
| `earnings_aggregation` | Earnings Aggregation |
| `sec_filing` | SEC Filing |
| `regulatory_tracker` | Regulatory Tracker |
| `press_room` | Press Room |
| `ats_api` | ATS API |
| `github_repo` | GitHub Repo |
| `package_index` | Package Index |

Fallback for unknown future `type` values: title-case the raw token with underscores → spaces.

### 3.2 `extraction_method` → human description

| Raw `extraction_method` | Human description |
|---|---|
| `pdf_export` | PDF exported and parsed on update. |
| `podcast_scraper` | RSS polled; episodes downloaded, transcribed, and parsed for claims. |
| `signal_scraper` | Page scraped for live metric snapshots on each cycle. |
| `web_extract` | Page fetched on cadence; text extracted and claims parsed. |
| `api` | API polled; structured records ingested directly. |
| `youtube_captions` | Captions fetched; transcript parsed for claims. |
| `manual` | Manually added; no automatic re-check. |

Fallback for unknown method: render the raw token with underscores → spaces.

### 3.3 `frequency` → human cadence

| Raw `frequency` | Human cadence |
|---|---|
| `daily` | Checked daily |
| `weekly` | Checked weekly |
| `monthly` | Checked monthly |
| `quarterly` | Checked quarterly |
| `annual` | Checked annually |
| `one_time` | One-time ingest |
| `on_event` | Checked on event |

---

## 4. Acceptance criteria

1. Chip row renders above the search bar. Chips show friendly label + count `(N)`. Chips ordered by count desc, with "All" first.
2. Clicking a chip toggles its active state. Multiple chips can be active simultaneously (OR filter). Active chip is visually distinct (filled vs. outline).
3. Filter state is reflected in URL as `?types=rss_feed,podcast_feed`. Reload preserves filter. Empty filter omits the param.
4. Counts on chips reflect the **total** registry, not the filtered set. (Counts must not change as chips toggle.)
5. Search bar still works and ANDs with the chip filter.
6. Each source card shows a "Monitoring" block (always visible, not gated behind expand). The block contains:
   - One-line monitoring process description (from §3.2).
   - Cadence line (from §3.3).
   - Status pill: ✓ Healthy / ⚠ Stale / ✗ Never / ⏸ Manual. Derivation rules in §5.
   - Last checked + Next check dates, when available.
7. Type badge on the card uses the friendly label from §3.1, not the raw snake_case.
8. Page works for an admin user with no active filter (default behaviour identical to today's render aside from the new monitoring block on each card).
9. No changes to `sources-registry.json` schema. No changes to extraction scripts. No new dependencies. Single-file edit to `sources.html`.
10. Mobile / narrow-window rendering: chip row wraps; monitoring block stacks below the source meta row without overlapping the badges.

---

## 5. Status derivation rules (D3a — pending lock)

```
status =
  if frequency in ('one_time','annual')      → ⏸ Manual
  elif last_checked is null                  → ✗ Never
  elif age(last_checked) <= cadence_days     → ✓ Healthy
  elif age(last_checked) <= 1.5*cadence_days → ⚠ Stale
  else                                       → ✗ Overdue

cadence_days =
  daily:1, weekly:7, monthly:30, quarterly:90,
  annual:365, on_event:NaN (skip)
```

`⏸ Manual` is informational only — does not flag for attention.

---

## 6. Edge cases

- Source with `type` not in the §3.1 map → render raw token title-cased, still gets its own chip.
- Source with `extraction_method` not in §3.2 → render raw token title-cased as the process line.
- Source with `frequency: on_event` → skip status derivation, show "Checked on event" with no Healthy/Stale verdict.
- `last_checked: null` and `frequency: one_time` → status is ⏸ Manual, not ✗ Never.
- URL has `?types=foo` where `foo` doesn't match any source → no sources render, chip row still shows; no error.
- Highlight flow (`?highlight=src-NNN`) must still work — if the source's type isn't in the active filter, override the filter to include that type so the highlighted card is visible.
- `beta/sources.html` mirror — out of scope unless Simon flags it; flag at handoff time.

---

## 7. Test plan

- Manual smoke: load page, confirm chips render with counts matching `Array.from(new Set(sources.map(s=>s.type)))` in console.
- Toggle each chip individually, confirm list filters correctly and counts on chips do not change.
- Toggle multiple chips, confirm OR filter (union).
- Toggle filter + type in search, confirm AND of search ∩ chip filter.
- Reload page with `?types=podcast_feed` — confirm chip is pre-selected and list is filtered.
- Open `?highlight=src-002&types=slide_deck` — confirm `src-002` (an `rss_feed`) is still visible (override rule).
- Manually mutate a source's `last_checked` to a date >1.5×cadence ago in browser memory — confirm ⚠ Stale renders.
- Pick a `frequency: one_time` source — confirm ⏸ Manual renders, not ✗ Never.
- Narrow viewport to 400px — confirm chip row wraps cleanly and monitoring block doesn't overflow.

---

## 8. Out of scope

- Schema change to `sources-registry.json` (no new `category` or `last_status` field this session).
- Backfill of any registry fields.
- Changes to extraction scripts (`scrape_podcasts.py`, `scrape_signals.py`, `monitor_sources.py`).
- Public-site sources page (none exists today; this is admin-only).
- A category-level legend or methodology explainer at the top of the page (D-Mon rules it out).
- Sorting changes — keep current sort (active-first, then `last_claims_count` desc).
- `beta/sources.html` parity — flagged separately.

---

## 9. Definition of done

- `sources.html` updated per §3, §4, §5.
- Manual test plan in §7 passes.
- Staging URL pasted into chat for Simon's review **before** any merge that affects the production admin page. (Publishing gate applies to admin pages too per `feedback_publish_gate.md` if behaviour is observable to anyone other than Simon — confirm at staging step.)
- `docs/deployments/deploy-2026-05-14-wq-104-sources-page.md` written summarising what changed and what was deliberately deferred (e.g., D3b upgrade path).
- Notion task moved to Done with brief outcome note.

---

## 10. Handoff prompt for VS Code / Claude Code

```
Pick up wq-104. Brief: docs/briefs/wq-104-sources-page-type-filter-and-monitoring.md

Decisions D-Cat, D-Mon, D-Handoff are locked. Decisions D1, D3, D4 are
flagged "Open" in §0 — Simon has resolved them as follows (paste from
Cowork chat at handoff time):

  D1 = [paste Simon's call: D1a / D1b / D1c]
  D3 = [paste Simon's call: D3a / D3b]
  D4 = [paste Simon's call: D4a / D4b — if D4b, propose maps and stop
        for Simon's review before implementing]

Implementation:
  1. Touch only sources.html (and beta/sources.html if Simon explicitly
     says yes at handoff).
  2. Add the three constant maps (§3.1, §3.2, §3.3 of the brief).
  3. Build the chip row, the multi-select filter logic, the URL sync.
  4. Add the per-card Monitoring block per §4 item 6.
  5. Implement status derivation per §5.
  6. Run through the test plan in §7. Capture before/after screenshots.

Constraints:
  - No schema change to sources-registry.json.
  - No changes to extraction scripts.
  - Publishing gate applies — staging URL + Simon's chat approval
    before any production deploy. Protocol: TAIL-WORKFLOW-PROTOCOL.md.

Stop and ask if anything is unclear. Especially flag any mismatch
between the friendly-label maps in §3 and the actual `type` values
present in sources-registry.json today.
```
