# Sources Registry

**Purpose:** Authoritative list of every external source used by The AI Ledger. Per GUIDELINES §5.4, every data source that feeds `site-data.json` must be registered here.

**Maintained by:** Simon / Hepburn Advisory
**Last updated:** 2026-04-23

---

## Columns

| Field | Meaning |
|---|---|
| `id` | Short stable identifier used in `site-data.json` entries |
| `name` | Issuing body / publisher (human-readable) |
| `tier` | Per GUIDELINES §4.3: **1** primary machine-readable, **2** secondary authoritative, **3** tertiary event-driven |
| `url` | Root URL for the source (not the per-datapoint link — that lives on the datapoint) |
| `handler` | Agent or person responsible for fetch/review |
| `cadence` | Review frequency (monthly / quarterly / annual / ad-hoc) |
| `licence` | Usage terms / attribution requirements |
| `method` | How data is fetched (API, scraper, manual copy, CSV download) |
| `addedOn` | ISO date registered |
| `notes` | Caveats, scope, limits |

---

## Registry

| id | name | tier | url | handler | cadence | licence | method | addedOn | notes |
|---|---|---|---|---|---|---|---|---|---|
| _None registered yet._ Populate as sources are added to `site-data.json`. | | | | | | | | | |

---

## Rules

1. Every source cited in `site-data.json` **must** appear here before the entry goes live (§11.2).
2. Sources are **never deleted** from this file. If a source is retired, mark `cadence = "retired"` and add a `retiredOn` note in `notes`. Past values still need their provenance traceable.
3. When adding a new source, prefer tier 1 (primary). Tier 3 entries require a note explaining why no tier 1 or 2 is available.
4. Tier downgrades (e.g. a primary source becomes unreachable and we fall back to a secondary) must be logged in `sources.log.md`, not silently in this file.
