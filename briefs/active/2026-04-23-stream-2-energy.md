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
