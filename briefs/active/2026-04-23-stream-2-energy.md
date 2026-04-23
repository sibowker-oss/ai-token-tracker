# Brief: Stream 2 — Energy/power sourcing

> **Handoff metadata (per GUIDELINES §9.3)**
> - **Source draft:** `The AI Ledger/stream-2-energy-brief.md`
> - **Handoff date:** 2026-04-23
> - **Work queue:** wq-012
> - **Parent:** wq-009 (widen-source-data-brief.md)
> - **Pairs with:** wq-006 Power Ledger page
> - This repo copy is the **immutable contract**. Append Implementation log below when starting work; do not edit §1–§9 without going back to the Ledger draft and handing off again.

**Status:** Scoped
**Budget:** $0 recurring (all sources free)

---

## 1. Shortlist — start here

| # | Source | Cadence | Type | Why |
|---|---|---|---|---|
| 1 | **ERCOT** — GIS Report + Large Load queue (LLWG) | Monthly | Primary | Largest US AI-DC concentration. 226 GW requests, ~77% datacenter. Explicit load-type flag. |
| 2 | **PJM** — New Services Queue + LLAW workshop decks | Quarterly clusters + monthly refresh | Primary | 32 GW load forecast, ~30 GW data centers. Post-2025 co-location rule forces end-customer naming. |
| 3 | **EIA API** — 860M, 930, STEO | Daily (930) / Monthly (860M, STEO) | Primary | Public-domain backbone. STEO now explicitly attributes datacenter load. Free API key, 5000 rows/req. |
| 4 | **NESO TEC Register (UK)** | Twice-weekly (Tue/Fri) | Primary | Best-in-class cadence. CSV, OGL licence. Gate 1/Gate 2 classifier from Nov 2025. |
| 5 | **Epoch AI Frontier Data Centers Hub** | Ongoing | Primary/Secondary | Already does the hard LLC → AI-lab attribution via permits + satellite imagery. CC-BY. |

Pair with **Virginia DEQ air permits** + **Virginia SCC docket search** when a PJM LLC filing needs deanonymizing.

## 2. Unit of analysis

Track three stages for every queue entry: **MW requested / MW approved / MW in-service (delivered)**. Most ISOs track only two — flag the missing one explicitly in provenance. Time series matters: "requested" is leading, "delivered" is validated, the gap is the pipeline.

## 3. Company attribution

Default state: LLC front. Three tiers of resolution:

1. **Self-attributed** — NYISO energy-intensive list, ERCOT LLIS form (load-type flag), post-2025 PJM co-location filings. Use these first.
2. **Derived** — Epoch AI's published mapping, FERC eLibrary, state utility IRPs with customer-named exhibits.
3. **Manual** — Virginia DEQ permits + SCC dockets, Loudoun/PW/Fairfax planning portals, Texas PUC Interchange. Labor-intensive, top-20 only.

## 4. Schema shape (site-data.json)

```json
"power_projects": [
  {
    "id": "pjm-aa1-567",
    "queue_market": "PJM",
    "queue_id": "AA1-567",
    "point_of_interconnection": "Aspen 230kV",
    "county": "Loudoun, VA",
    "stage": "FIS_signed",
    "mw_requested": 300,
    "mw_approved": 300,
    "mw_in_service": null,
    "requested_cod": "2027-06-01",
    "applicant_lei_or_llc": "Silver Queen LLC",
    "attributed_operator": "Amazon Web Services",
    "attribution_confidence": "medium",
    "attribution_source": "epoch.ai/data/data-centers#aspen-230kv",
    "load_type_disclosed": "data_center",
    "source": {
      "url": "https://www.pjm.com/planning/services-requests/interconnection-queues",
      "retrievedAt": "2026-04-23T08:00:00Z",
      "nextReview": "2026-05-23T08:00:00Z",
      "confidence": "high"
    }
  }
]
```

## 5. International — second wave

After US shortlist is live:

- **ENTSO-E Transparency Platform** — free bearer-token API, load/generation by BA across EU.
- **EirGrid (Ireland)** — CRU LEU Policy: datacenter share rising from 22% (2024) to ~31% (2034) of Irish demand.
- **UK NESO** already in shortlist.

## 6. Dependencies

- **wq-006 Power Ledger page** runs in lockstep. Schema decisions in §4 feed the page design.
- **wq-007 provenance infrastructure** — first real entries in `sources.registry.md` and `agents.registry.md` should come from this stream.
- **wq-004 build-lint** — once enforced, ensures cadences here don't rot.
- **wq-014 structured claim schema** — blocking dependency for `power_project` claim type.

## 7. Integration with existing claims pipeline

The site already has a claims extraction pipeline: `monitor_sources.py` + `extract_claims.py` + `claims.html` review UI + `apply_claims.py`. This brief does NOT build new review queue infrastructure. It extends the existing pipeline.

**Only new infrastructure needed:**

### 7.1 LLC → operator attribution layer

The claims extractor prompt alone cannot reliably attribute ERCOT/PJM LLC filings to parent AI operators. Attribution needs its own dedicated step before claims extraction.

- New file: `data/datacenter-attribution-map.json`
- Seed from: Epoch AI Frontier Data Centers Hub (published LLC → operator mapping)
- Extend via: manual review using Virginia DEQ permits, SCC dockets, FERC eLibrary, state utility IRPs, county planning records
- Structure:
  ```json
  {
    "Silver Queen LLC": {
      "operator": "Amazon Web Services",
      "confidence": "high",
      "attribution_sources": [
        "https://epoch.ai/data/data-centers#silver-queen",
        "https://scc.virginia.gov/docketsearch/..."
      ],
      "last_verified": "2026-04-23"
    }
  }
  ```
- `extract_claims.py` consults this map when generating power claims from ISO queue data.

### 7.2 Structured power-claim schema

See wq-014 (`2026-04-23-structured-claim-schema.md`). Power claims (MW requested/approved/delivered per project) are one instance.

## 8. Implementation package

1. Add ERCOT, PJM, EIA, NESO, Epoch AI to `sources-registry.json` (5 entries with provenance fields).
2. Extend `monitor_sources.py` to handle each source's format (XLSX, CSV, HTML table, API).
3. Build the attribution map (§7.1) — seed it, document the manual extension process.
4. Extend `extract_claims.py` with prompts for power claims — consume the attribution map.
5. New structured claim type `power_project` (depends on wq-014).
6. Wire into Power Ledger page (wq-006).
7. Register the power-source monitoring agent in `agents.registry.md` per project rule.
8. Log new claim types under `data/sources.log.md` for provenance trail.

## 9. Decisions (resolved 2026-04-23)

- **CN coverage:** accept gap for v1. Revisit later.
- **Water data:** capture where it appears (Google/Microsoft publish WUE), but not in scope for v1 renderings. Store alongside power data in schema so future view can switch it on.
- **Capex-per-MW layer:** yes, in v1 scope. Layer Digital Realty / Equinix / Uptime quarterly reports on top of MW data to derive $/MW economics.

---

## Implementation log

*(Append entries here when work starts. Leave §1–§9 above untouched.)*

### 2026-04-23 — Phase 3 plumbing shipped

Four commits on `main`:

- `41b87c5` Register Stream 2 power sources (wq-012)
- `3fb80d1` Seed datacenter-attribution-map from Epoch AI CSV (wq-012)
- `dd8cd64` Add Stream 2 power extraction adapters to monitor_sources (wq-012)
- `63a6b5b` Register stream-2-power-monitor agent (wq-012)

**What landed**

_Sources (§8.1)_

- Five new registry entries (src-060 ERCOT, src-061 PJM, src-062 EIA,
  src-063 NESO TEC, src-064 Epoch AI). All
  `status=pending_first_extraction`, `next_check=2026-05-23`. Daily cron
  won't auto-fire; Simon triggers per source. Mirror rows in
  `data/sources.registry.md`; five rows in `data/sources.log.md`.

_Attribution map (§7.1)_

- Per Simon's Q3 answer, ingested the **full Epoch AI Frontier Data
  Centers CSV** — 36 facilities, not a 15-20 sample. Saved at
  `data/datacenter-attribution-map.json` with two top-level blocks:
  - `by_project`: 36 entries keyed by facility name (e.g.
    `"Anthropic-Amazon New Carlisle"`). Each has `owners[]` and
    `operators[]` lists with Epoch's confidence tags preserved
    (`#confident` / `#likely` / `#speculative` → `confidence` enum).
    Multi-operator projects (Microsoft Fairwater with OpenAI + Microsoft;
    Fluidstack Lake Mariner with Anthropic + G42) kept as multi-entry
    lists rather than flattened.
  - `by_llc`: empty on seed. Populated as ERCOT / PJM extractions land
    and as manual research via Virginia DEQ + SCC docket search
    attributes specific LLCs. This is the table the brief §7.1 spec
    originally describes (LLC-keyed). Epoch's data is project-keyed;
    the two tables cohabit.
- Raw artefact snapshotted at
  `data/snapshots/src-064/2026-04-23/data_centers.csv` (44 KB) per
  data-sourcing-policy §6.4.
- `_meta` block names the source CSV URL, licence (CC-BY 4.0), pull
  date, and row count so the map is fully traceable.

_Adapters (§8.2)_

Five entries wired into `monitor_sources.ADAPTERS`. Posture is
**activation = plumbing in place; extraction = Simon triggers per
source**. Per-adapter state:

- `extract_neso_tec` (src-063) — **fully functional**. Fetches
  data-portal HTML → finds CSV download link → pulls CSV with stdlib
  `urllib` → parses rows with stdlib `csv` → emits
  `power_project` claims with `queue_market='NESO'`. HTML + CSV
  snapshots saved. No external dependencies required. Recommended
  first manual trigger: `monitor_sources.py --force src-063`.
- `extract_epoch_frontier` (src-064) — **fully functional**. Refreshes
  the Epoch CSV on demand and saves the snapshot. Emits zero
  `power_project` claims itself (Epoch is a catalogue, not a queue).
  Rebuilding `datacenter-attribution-map.json` after a new CSV pull is
  a one-line Python call Simon can run against the already-snapshotted
  CSV — a periodic refresh pattern rather than a cron-fired overwrite.
- `extract_eia_api` (src-062) — **env-gated**. Requires
  `EIA_API_KEY` (free registration at
  https://www.eia.gov/opendata/register.php). When absent, logs the
  registration URL and returns `[]`. When present, hits the STEO
  monthly endpoint for DC-load series ZEGEPUS and emits 12 free-text
  claims (sector aggregates — doesn't fit the `power_project` shape).
  JSON snapshot saved.
- `extract_iso_queue_ercot` (src-060) and `extract_iso_queue_pjm`
  (src-061) — **stubbed**. v1 fetches the landing HTML, saves a
  snapshot, surfaces XLSX download links in the log, and returns `[]`.
  Row-level XLSX parse is gated on `import openpyxl` (not in v1 env);
  when openpyxl is absent the adapter logs 'install openpyxl to
  enable' and exits cleanly. Simon's call whether to install (adds
  ~5 MB; reversible). ISO-specific column-name schemas still to be
  written when we enable.

_Shared helpers (§7.2 wiring)_

- `_load_attribution_map()` and `_lookup_attribution(llc_name,
  project_name)` on `monitor_sources`. Prefers `by_llc` (tight match
  from ISO filings) over `by_project` (Epoch's facility-name keyed
  index). Returns `(company_slug, confidence, attribution_sources)` or
  `(None, None, [])` when unresolved — leaves the claim's
  `company_slug` empty so the review queue shows it as unattributed.
- `_power_project_claim_from_row(row, source, queue_market, attr_map)`
  builds a schema-conformant `power_project` claim from an adapter
  row. Threads `nextReview` through the source's declared
  `frequency`. When the attribution lookup resolves, attaches
  `company_slug`, `attribution_confidence`, and `attribution_sources`;
  otherwise the fields stay absent per schema.
- `_save_power_claims(claims, source)` — per-source candidates file
  writer. Isolation preserved: lands at
  `data-updates/<date>-source-<id>.json`, not the shared
  `<date>-candidates.json` review queue. Same pattern as Stream 1.

_Agent registration (§8.7)_

- `stream-2-power-monitor` v0.1.0 added to `data/agents.registry.md`.
  Covers src-060..064. Cadence `on-demand (manual --force trigger)`.
- Two rows on `data/agents.log.md`: one for the attribution-map seed
  (commit `3fb80d1`, outcome `merged`, 36 rows); one for agent
  registration (outcome `configured`, no extractions yet).

**Divergence from brief**

1. **§7.1 attribution map schema** — brief specifies `by_llc` shape with
   `{operator, confidence, attribution_sources, last_verified}`.
   Implementation has the same shape for `by_llc` AND a sibling
   `by_project` block because Epoch's data is project-keyed. The two
   tables cohabit with distinct lookup paths in
   `_lookup_attribution()`. When `by_llc` gets populated from ISO
   filings, it takes precedence over `by_project` matches.
2. **§7.2 power_project structured schema** — brief wq-014 §2.1
   specifies the exact payload. Implementation matches literally, with
   the helpful addition that `_power_project_claim_from_row` fills
   `nextReview` from the source's own `frequency` so the build-lint
   isn't immediately stale after an extraction.
3. **§5 capex-per-MW layer** — Simon confirmed "yes in v1 scope" in
   decision §9. Not implemented this commit — Digital Realty / Equinix /
   Uptime quarterly reports aren't sources yet. Flagged as follow-up:
   register those three as new sources, emit $/MW derived claims in a
   separate commit once the MW data lands.
4. **§3 attribution tiers** — brief lists three tiers (self-attributed /
   derived / manual). The Epoch seed fills tier 2 (derived via Epoch's
   own LLC-to-lab mapping). Tier 1 (self-attributed via NYISO
   energy-intensive list, ERCOT LLIS form, PJM co-location filings) is
   accessible once ERCOT and PJM adapters actually parse XLSX rows.
   Tier 3 (manual Virginia DEQ + SCC + Texas PUC) is left as Simon's
   ongoing research pipeline; `by_llc` is the write-target for any
   manual tier 3 attribution.

**Follow-ups from Phase 3**

1. Install `openpyxl` and wire ERCOT + PJM row-level XLSX parse.
   Requires per-ISO column-name mapping because ISOs name fields
   differently.
2. Add a map-refresh helper: given a fresh Epoch CSV snapshot, rebuild
   `data/datacenter-attribution-map.json` with diff-logging to
   `data/sources.log.md` row-by-row (so confidence flips are visible).
   v1 has a one-time seed only; the refresh path is a manual Python
   one-liner today.
3. Register Digital Realty / Equinix / Uptime Institute quarterly
   reports as sources and implement the $/MW derived claim (brief
   decision §9.3 "capex-per-MW layer").
4. Wire Virginia DEQ air permits and SCC docket search as tier-3 manual
   sources (brief §1 footnote + §3).

**Not done in Phase 3, deferred**

- §5 international second-wave sources (ENTSO-E, EirGrid). Brief says
  "after US shortlist is live"; the US shortlist isn't yet _live_ in
  the producing-claims sense.
- Wiring Power Ledger page to read `site-data.json.power.projects[]`.
  Out of scope for this brief — that's wq-006.
- Hiring / patent streams (wq-013). Phase 4.

**Pausing for review before Phase 4 (wq-013 Stream 3 discovery).**


---

## Sources

- [ERCOT GIS Report](https://www.ercot.com/mp/data-products/data-product-details?id=pg7-200-er)
- [ERCOT Large Load Integration](https://www.ercot.com/services/rq/large-load-integration)
- [PJM New Services Queue](https://www.pjm.com/planning/services-requests/interconnection-queues)
- [PJM Large Load Additions Workshop](https://www.pjm.com/committees-groups/workshops/llaw)
- [MISO GI Queue](https://www.misoenergy.org/planning/resource-utilization/GI_Queue/)
- [CAISO Public Queue Report](https://www.caiso.com/library/public-queue-report)
- [SPP GI Active Portal](https://opsportal.spp.org/Studies/GIActive)
- [ISO-NE IRTT](https://irtt.iso-ne.com/reports/external)
- [NYISO Energy-Intensive Projects](https://www.nyiso.com/-/energy-intensive-projects-in-nyiso-s-interconnection-queue)
- [EIA API](https://www.eia.gov/opendata/)
- [EIA Form 860M](https://www.eia.gov/electricity/data/eia860m/)
- [EIA STEO](https://www.eia.gov/outlooks/steo/)
- [NESO TEC Register](https://www.neso.energy/data-portal/transmission-entry-capacity-tec-register)
- [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/)
- [EirGrid Generation Capacity Statement](https://www.eirgrid.ie/industry/general-industry-information/generation-capacity-statement)
- [Epoch AI Frontier Data Centers](https://epoch.ai/data/data-centers)
- [Google 2025 Environmental Report](https://sustainability.google/reports/google-2025-environmental-report/)
- [Microsoft 2025 Environmental Data Fact Sheet](https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/microsoft/msc/documents/presentations/CSR/2025-Microsoft-Environmental-Data-Fact-Sheet-PDF.pdf)
- [Meta 2025 Sustainability](https://sustainability.atmeta.com/)
- [Amazon 2024 Sustainability](https://sustainability.aboutamazon.com/reporting)
- [Virginia DEQ Data Center Air Permits](https://www.deq.virginia.gov/news-info/shortcuts/permits/air/issued-air-permits-for-data-centers)
- [Virginia SCC Docket Search](https://www.scc.virginia.gov/docketsearch)
- [FERC eLibrary](https://elibrary.ferc.gov/)
- [gridstatus library (ISO normaliser)](https://opensource.gridstatus.io/en/latest/interconnection_queues.html)
- [Interconnection.fyi daily snapshots](https://www.interconnection.fyi/)
