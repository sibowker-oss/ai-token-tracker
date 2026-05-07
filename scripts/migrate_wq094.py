#!/usr/bin/env python3
"""wq-094 — Zitron 2026-05-06 ingest migration.

Single-pass, idempotent. Applies all data changes from
docs/briefs/wq-094-zitron-2026-05-06-ingest.md plus the
Copilot announced-vs-actual reconciliation resolved in chat.

Files touched:
  - data/compute_disclosures.json (extend; add forward_commitments + 1B-leaked tier + msft_ai.openai_inference_quarterly)
  - entities.json (refresh + extend selected entities)
  - data/depreciation.json (new file)
  - data/datacenter-attribution-map.json (add power_mw_energised_2026 to Project Rainier)
  - assumptions-audit.md (clean stale row 12)

Idempotent: re-running is safe — checks for existing values before writing.

Open decisions resolved 2026-05-07:
  O1: Add openai.financials.2026.total_compute_commitment_usd_b: 50; keep inference_cost: 14.1
  O2: Anthropic ARR headline = 30 (Apr 6); carry 44 (SemiAnalysis) as low-confidence external estimate
  O3: Project Rainier — keep 1092 MW nameplate; add power_mw_energised_2026 (null)
  O4: SKIP — capex bridge work deferred (public data; doesn't change 2023–25 totals)
  O5: M365 Copilot published value = leaked actual band ($1.2–1.5B); render list + bundling-adjusted as context
  O6: GitHub Copilot tokens_per_day = remove 1000.0 (unsourced); replace with sensible editorial ~1.0 T/day low-confidence

Run from repo root:
  python3 scripts/migrate_wq094.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parent.parent
ENTITIES = REPO / "entities.json"
COMPUTE_DISC = REPO / "data" / "compute_disclosures.json"
DEPRECIATION = REPO / "data" / "depreciation.json"
DC_MAP = REPO / "data" / "datacenter-attribution-map.json"
AUDIT_MD = REPO / "assumptions-audit.md"

WQ_TAG = "wq-094"
TODAY = "2026-05-07"

LOG: list[str] = []


def log(msg: str) -> None:
    LOG.append(msg)
    print(msg)


def load_json(p: Path):
    with p.open() as f:
        return json.load(f)


def save_json(p: Path, data) -> None:
    with p.open("w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def find_company(entities_doc, slug):
    for c in entities_doc.get("companies", []):
        if c.get("slug") == slug:
            return c
    return None


def ensure_dict(parent, key):
    if key not in parent or not isinstance(parent[key], dict):
        parent[key] = {}
    return parent[key]


# ──────────────────────────────────────────────────────────────────────
# 1. compute_disclosures.json — forward_commitments block + tier + Q-trajectory
# ──────────────────────────────────────────────────────────────────────


def migrate_compute_disclosures():
    doc = load_json(COMPUTE_DISC)

    # --- Add 1B-leaked tier definition to schema if not present ---
    schema = doc.get("_schema", {})
    tiers_text = schema.get("tiers", "")
    if "1B-leaked" not in tiers_text:
        schema["tiers"] = (
            tiers_text
            + " 1B-leaked = own-mouth via insider (e.g. Azure billing source); higher than 2A editorial but not externally verifiable; treat as anchor candidate cross-checked at next earnings cycle (introduced wq-094)."
        )
        log("[compute_disclosures] added 1B-leaked tier definition")

    # --- forward_commitments block ---
    fc_existing = doc.get("forward_commitments", {})
    fc = {
        "_doc": "wq-094 ingest of Zitron 2026-05-06 piece + The Information Anthropic-Google deal disclosure. Forward commitments are reported GROSS, separately from realised revenue. Per Cross-Ledger Reconciliation rule (CLAUDE.md 2026-05-06), these dollars are NOT rolled into the Compute Ledger 2025 sum-of-Q calendar totals or Q1 26 quarterly bars.",
        "lab_to_hyperscaler": {
            "anthropic_google_5yr": {
                "commitment_usd_b": 200,
                "duration_years": 5,
                "commitment_period_start": "2026",
                "tier": "1B",
                "source": "The Information 2026-04-30; Anthropic + Google joint statement",
                "share_of_google_rpo_q1_2026_pct": 42.7,
            },
            "anthropic_broadcom_tpu_2026": {
                "commitment_usd_b": 21,
                "year": 2026,
                "tier": "1B",
                "source": "CNBC 2026-04 / Anthropic-Broadcom announcement",
                "destination_note": "Broadcom-built TPUs deployed in Google data centres; Anthropic pays Google to rent.",
            },
            "anthropic_broadcom_tpu_2027": {
                "commitment_usd_b": 42,
                "year": 2027,
                "tier": "1B",
                "source": "CNBC 2026-04",
            },
            "aws_openai_2026": {
                "commitment_usd_b": 38,
                "duration_years": 1,
                "tier": "1B",
                "source": "AWS-OpenAI announcement Q1 2026",
            },
            "aws_openai_8yr_expansion": {
                "commitment_usd_b": 100,
                "duration_years": 8,
                "tier": "1B",
                "source": "AWS-OpenAI announcement Q1 2026",
            },
            "oracle_openai_stargate": {
                "commitment_usd_b": 300,
                "tier": "1B",
                "source": "Oracle Q3 FY26 RPO disclosure",
                "already_in_oracle_notes": True,
            },
        },
        "hyperscaler_to_lab_investment": {
            "google_anthropic_cumulative": {
                "invested_usd_b": 43,
                "tier": "1B",
                "breakdown": {
                    "prior_rounds_through_2025": 33,
                    "feb_2026_round_share": None,
                    "apr_2026_round": 10,
                },
                "source": "Google + Anthropic disclosures; The Information 2026-04",
            },
            "amazon_anthropic_cumulative": {
                "invested_usd_b": 33,
                "tier": "1B",
                "breakdown": {
                    "prior_through_2025": 13,
                    "apr_2026_round": 5,
                    "contingent_additional": 15,
                },
                "source": "Amazon + Anthropic disclosures; Reuters 2026-04",
            },
            "aws_openai_feb_2026": {
                "invested_usd_b": 13,
                "contingent_additional_usd_b": 20,
                "tier": "1B",
                "source": "Amazon Q4 2025 announcement; The Information 2026-02",
            },
        },
        "hyperscaler_dc_backstops": {
            "google_fluidstack_cipher": {
                "backstop_usd_b": 1.4,
                "tier": "1B",
                "operator_serving": "Anthropic",
                "source": "The Information / Zitron 2026-05-06",
            },
            "google_terawulf": {
                "backstop_usd_b": 1.8,
                "tier": "1B",
                "operator_serving": "Anthropic",
                "source": "The Information / Zitron 2026-05-06",
            },
            "google_hut8": {
                "backstop_usd_b": None,
                "tier": "2A",
                "operator_serving": "Anthropic",
                "source": "Zitron 2026-05-06",
            },
        },
        "hyperscaler_backlog": {
            "google_rpo": {
                "q4_2025_usd_b": 242.8,
                "q1_2026_usd_b": 467.8,
                "qoq_jump_usd_b": 225.0,
                "tier": "1A",
                "source": "Alphabet Q1 2026 10-Q",
            },
            "mag3_ai_lab_share_of_backlog_pct": 50,
            "anthropic_plus_openai_committed_to_mag3_usd_b": 718,
            "tier_aggregate": "2A",
            "source_aggregate": "The Information chart 2026-04-30",
        },
        "_provenance": {
            "set_by": f"scripts/migrate_wq094.py ({WQ_TAG})",
            "set_at": TODAY,
            "supersedes": None,
        },
    }
    if fc_existing != fc:
        doc["forward_commitments"] = fc
        log("[compute_disclosures] wrote forward_commitments block")

    # --- msft_ai.openai_inference_quarterly ---
    msft = doc["components"]["msft_ai"]
    oai_q = {
        "2025Q1": 1.467,
        "2025Q2": 2.075,
        "2025Q3": 3.648,
        "2025Q4_estimate": 4.625,
        "tier": "1B-leaked",
        "source": "Zitron 2026-05-06 — sources with direct knowledge of Azure revenue",
        "caveat": "Ed cites $2.075B in one paragraph and $2.947B in another for Q3 FY25 (= 2025Q1 calendar in TAIL labelling); $2.075B used here as the consistent quarterly figure. 2025Q4 estimate from Ed's narrative 'annualised hit over $18.5B by year-end'. Treat as anchor candidates; cross-check at Q2 2026 earnings.",
        "calendar_note": "Quarter labels are CALENDAR quarters per TAIL convention. Ed's 'Q2 FY25' = MSFT fiscal = calendar Q4 2024 (pre-dates this array).",
    }
    if msft.get("openai_inference_quarterly") != oai_q:
        msft["openai_inference_quarterly"] = oai_q
        log("[compute_disclosures] wrote msft_ai.openai_inference_quarterly")

    # --- Annotation on copilot_excluded explaining cross-ledger reconciliation ---
    note = msft.get("copilot_excluded_basis_note", "")
    new_note = "wq-094: copilot_excluded_2025_usd_b = MS-declared scope-out from MSFT AI line ($6.67B). This is NOT the same basis as entities.json:microsoft-copilot.products[m365-copilot] published value (which is leaked-actual basis post-wq-094, ~$1.35B midpoint). The two describe overlapping reality on different bases: Compute Ledger uses what MSFT reports excluded; Trad SaaS uses leaked Azure billing actuals. Bridge: MSFT scopes out list-billings ($6.67B = M365 Copilot list ~$5.4B-$7.2B + GitHub Copilot ~$1.65B + Studio/Sales/Service residual); actual collected revenue is materially lower per Zitron 2026-05-06 leak."
    if note != new_note:
        msft["copilot_excluded_basis_note"] = new_note
        log("[compute_disclosures] wrote msft_ai.copilot_excluded_basis_note")

    save_json(COMPUTE_DISC, doc)


# ──────────────────────────────────────────────────────────────────────
# 2. entities.json — many edits
# ──────────────────────────────────────────────────────────────────────


def migrate_entities():
    doc = load_json(ENTITIES)
    doc["meta"]["lastUpdated"] = TODAY

    # ---------- microsoft-copilot / M365 Copilot ----------
    msc = find_company(doc, "microsoft-copilot")
    if msc and msc.get("products"):
        m365 = next((p for p in msc["products"] if p.get("slug") == "m365-copilot"), None)
        if m365:
            m365["paid_seats"] = 20_000_000  # was 15M; refreshed to MSFT-disclosed 20M
            m365["seat_count_source"] = "MSFT Q1 FY26 disclosure (Apr 2026); cited Zitron 2026-05-06"
            # Three-bands published structure
            m365["list_billings_2025_usd_b"] = 7.2  # 20M × $30 × 12
            m365["incremental_real_2025_usd_b_low"] = 2.5
            m365["incremental_real_2025_usd_b_high"] = 3.5
            m365["actual_leaked_2025_usd_b_low"] = 1.2
            m365["actual_leaked_2025_usd_b_high"] = 1.5
            m365["published_2025_usd_b"] = 1.35  # midpoint of leaked-actual band; PRIMARY published value (O5 resolution)
            m365["published_basis"] = "leaked_actual_midpoint"
            m365["leaked_actual_quarterly_usd_b"] = {
                "2025Q1_calendar": 0.367,  # MSFT Q2 FY25 disclosed Jan 2025
                "2025Q2_calendar": 0.300,  # MSFT Q3 FY25; declined Q-o-Q
                "tier": "1B-leaked",
                "source": "Zitron 2026-05-06 — leaked Azure billing",
            }
            m365["confidence"] = "Med"  # leaked actual is grounded; ±20% band
            # Replace the legacy derived_arr_2025_usd_b notes with corrected reasoning
            m365["notes"] = (
                "wq-094 (2026-05-07) — published value restated from $5.4B list-billings to $1.35B (midpoint of leaked-actual band $1.2–1.5B per Zitron 2026-05-06 Azure billing leak). "
                "Three bands now stored: list ($7.2B at 20M × $30 × 12), bundling-adjusted incremental ($2.5–3.5B), leaked actual ($1.2–1.5B). Published basis = leaked actual. "
                "Legacy 'derived_arr_2025_usd_b: 5.4' retained as reference but no longer the published number. "
                "MS-declared Compute Ledger scope-out remains $6.67B per wq-091 D4 — different basis (what MSFT excludes) describing overlapping reality. See compute_disclosures.json:msft_ai.copilot_excluded_basis_note for the bridge. "
                "Stale ai_arr: 13.0 was misattributed (full MSFT AI ARR, not M365 Copilot specifically) — flagged by wq-091 audit."
            )
            log("[entities] updated microsoft-copilot.products[m365-copilot] (3-band structure; published = $1.35B leaked midpoint)")

    # ---------- github-copilot ----------
    gh = find_company(doc, "github-copilot")
    if gh:
        cur = ensure_dict(gh, "current")
        # O6: remove unsourced 1000.0 T/day; replace with editorial ~1.0 T/day low-confidence
        cur["tokens_per_day"] = 1.0
        cur["tokens_per_day_basis"] = "editorial_estimate"
        cur["tokens_per_day_methodology"] = (
            "Editorial estimate: ~4.7M paid seats (MSFT Q4 FY25 earnings) × ~50–70% active × ~50–200 requests/day × ~1–5K tokens/req → ~0.5–1.5 T/day; central 1.0 T/day. "
            "Cross-check: GitHub Copilot reported as 2nd largest customer of Anthropic models (Zitron 2026-05-06). Anthropic total ~6 T/day → if GitHub is ~10–20% of Anthropic volume that's 0.6–1.2 T/day from Anthropic alone, plus residual OpenAI portion. "
            "Replaces unsourced 1000.0 T/day legacy value — wq-094 cleanup."
        )
        cur["tokens_per_day_confidence"] = "low"
        cur["tokens_per_day_date"] = TODAY
        cur["paid_seats"] = 4_700_000
        cur["paid_seats_source"] = "MSFT Q4 FY25 earnings (cited assumptions-audit.md row 12)"
        cur["anthropic_customer_rank"] = 2
        cur["anthropic_customer_rank_source"] = "Zitron 2026-05-06"
        cur["compute_subsidy_relationship"] = True
        cur["compute_subsidy_note"] = (
            "Microsoft subsidises customer compute spend on GitHub Copilot — published ARR overstates economic margin. "
            "June 2026 token-based billing transition will alter both revenue trajectory and margin disclosure. Watch Q3 2026 earnings."
        )
        cur["june_2026_token_billing_transition"] = True
        log("[entities] updated github-copilot.current (tokens_per_day 1000→1.0 editorial; +Anthropic rank, subsidy flag, June 2026 transition)")

    # ---------- anthropic ----------
    ant = find_company(doc, "anthropic")
    if ant:
        cur = ensure_dict(ant, "current")
        cur["arr"] = 30.0  # was 19; refreshed per Apr 6 disclosure (O2)
        cur["arr_date"] = "2026-04"
        cur["arr_source"] = "Anthropic disclosure 2026-04-06"
        # External estimate carried separately at low confidence (O2)
        cur["arr_external_estimate"] = {
            "value_usd_b": 44,
            "confidence": "low",
            "as_of": "2026-04-30",
            "source": "SemiAnalysis estimate",
            "methodology_note": (
                "Anthropic calculates annualised revenue as last 4 weeks of API revenue × 13 + monthly chatbot subscription revenue (single-day active subs anchor) × 12 (per The Information). "
                "Selecting a single-day anchor and 4-week-window can inflate vs steady-state. Published number on TAIL = $30B (Anthropic-disclosed); $44B carried as external estimate only."
            ),
        }
        # Funding history
        fin = ensure_dict(ant, "financials")
        fh = fin.get("funding_history") or []
        # Idempotent add
        seen = {(x.get("date"), x.get("round")) for x in fh}
        for entry in [
            {"date": "2025-09", "round": "Series F", "amount_usd_b": 13},
            {"date": "2026-02", "round": "Series G", "amount_usd_b": 30, "valuation_usd_b": 380},
            {"date": "2026-04", "round": "AWS strategic", "amount_usd_b": 5},
            {"date": "2026-04", "round": "Google strategic", "amount_usd_b": 10},
            {"date": "2026-Q2", "round": "in_talks", "amount_usd_b": 50, "status": "rumoured"},
        ]:
            key = (entry["date"], entry["round"])
            if key not in seen:
                fh.append(entry)
                seen.add(key)
        fin["funding_history"] = fh
        fin["total_raised_through_2026_04_usd_b"] = 58

        # 2026 financials refresh
        f26 = ensure_dict(fin, "2026")
        f26["arr"] = 30  # was 18; aligned to current.arr
        f26["projected_loss_2026_usd_b"] = 11
        f26["projected_loss_2027_usd_b"] = 11
        f26["projected_loss_source"] = "The Information 2026-04 (leak of Anthropic internal projection)"

        # Notes
        notes = ensure_dict(ant, "notes")
        notes["github_copilot_concentration"] = "GitHub Copilot is 2nd largest customer of Anthropic models (Zitron 2026-05-06)"
        notes["projected_loss_2026_27"] = "$11B/yr both 2026 and 2027 per The Information leak of Anthropic internal projection"

        # Capacity commitments
        cap = ensure_dict(ant, "compute_access_commitment_gw")
        cap["aws_up_to"] = 5.0
        cap["google_2026_at_least"] = 1.0
        cap["google_2027_plus"] = "multiple"
        cap["tier"] = "1B"
        cap["source"] = "Anthropic + Amazon + Google announcements 2025-2026"

        log("[entities] updated anthropic — ARR 19→30, +external-estimate $44B, funding_history, projected_loss 2026/2027 $11B, capacity commitments")

    # ---------- openai ----------
    oai = find_company(doc, "openai")
    if oai:
        f26 = ensure_dict(ensure_dict(oai, "financials"), "2026")
        f26["total_compute_commitment_usd_b"] = 50  # O1 — keep inference_cost: 14.1
        f26["total_compute_commitment_source"] = "Zitron 2026-05-06 (\"OpenAI plans to burn $50 billion on compute in 2026 alone\")"
        f26["total_compute_commitment_basis"] = "all-in: training + capacity-prepay + inference. NOT to be confused with inference_cost ($14.1B) which is a narrower line."
        log("[entities] updated openai.financials.2026.total_compute_commitment_usd_b = $50B (O1)")

        # Compute access (CFO disclosure)
        oai_cap = ensure_dict(oai, "compute_access_gw")
        oai_cap["end_2025"] = 1.9
        oai_cap["tier"] = "1B"
        oai_cap["source"] = "OpenAI CFO disclosure end-2025; cited Zitron 2026-05-06"

    # ---------- meta ----------
    meta = find_company(doc, "meta")
    if meta:
        f26 = ensure_dict(ensure_dict(meta, "financials"), "2026")
        f26["capex"] = 145  # was 125
        f26["capex_source"] = "Meta Q1 2026 guidance refresh; range $145B–$170B per multiple sources"
        f26["reality_labs_q1_loss_usd_b"] = 4
        cumulative = ensure_dict(ensure_dict(meta, "financials"), "cumulative")
        cumulative["reality_labs_loss_usd_b"] = 86
        cumulative["reality_labs_loss_period"] = "all-time through Q1 2026"

        notes = ensure_dict(meta, "notes")
        notes["gem_token_burn"] = "60T tokens / 30 days, ~$330M cost (The Information / Zitron 2026-05-06); 80% of that was cache reads per Meta-spend sources"
        notes["gem_lift_q2_2025"] = "5% IG conv lift, 3% FB conv lift (Meta Q2 2025 disclosure)"
        notes["gem_lift_q4_2025"] = "3.5% FB click lift, >1% IG conv lift (Meta Q4 2025 disclosure) — different metric basis vs Q2; conversion lift declined ~4 percentage points"
        log("[entities] updated meta — 2026 capex 125→145, Reality Labs Q1 loss $4B + cumulative $86B, GEM notes")

    # ---------- aws ----------
    aws = find_company(doc, "aws")
    if aws:
        cap = ensure_dict(aws, "compute_capacity_gw")
        cap["end_2025"] = 1.67
        cap["tier"] = "2A"
        cap["source"] = "Editorial estimate; cited Zitron 2026-05-06"
        notes = ensure_dict(aws, "notes")
        notes["history_2003_2017"] = "$52B capex 2003–2017 (inflation-adjusted); profitable in ~10 years. Editorial control point for AI-era capex/payback comparison."
        log("[entities] updated aws — compute_capacity_gw=1.67, history note")

    # ---------- azure ----------
    az = find_company(doc, "azure")
    if az:
        cap = ensure_dict(az, "compute_capacity_gw")
        cap["end_2025"] = 2.0
        cap["tier"] = "2A"
        cap["source"] = "Epoch AI estimate; cited Zitron 2026-05-06"
        log("[entities] updated azure — compute_capacity_gw=2.0")

        # M365 Copilot 20M subs anchor on the parent product
        for prod in az.get("products", []) or []:
            if prod.get("slug", "").lower() in ("copilot-365", "m365-copilot", "copilot365"):
                prod["subscriber_count_m"] = 20
                prod["subscriber_count_source"] = "MSFT Q1 FY26 disclosure (Apr 2026)"
                log("  └ azure.products[copilot-365].subscriber_count_m=20 set")

    # ---------- gcp ----------
    gcp = find_company(doc, "gcp")
    if gcp:
        cap = ensure_dict(gcp, "compute_capacity_gw")
        cap["end_2025"] = 2.95
        cap["tier"] = "2A"
        cap["source"] = "Editorial estimate; cited Zitron 2026-05-06"
        log("[entities] updated gcp — compute_capacity_gw=2.95")

    # ---------- coreweave ----------
    cw = find_company(doc, "coreweave")
    if cw:
        cap = ensure_dict(cw, "compute_capacity_gw")
        cap["end_2025"] = 0.480
        cap["tier"] = "2A"
        cap["source"] = "Editorial; cited Zitron 2026-05-06"
        log("[entities] updated coreweave — compute_capacity_gw=0.480")

    # ---------- market_aggregates.quarterly_capex ----------
    agg = ensure_dict(doc, "market_aggregates")
    qc = ensure_dict(agg, "quarterly_capex")
    qc.setdefault("_doc", "Per-hyperscaler quarterly capex. Currently sparse — populate from 10-Qs each cycle.")
    qc["2025Q3"] = {
        "msft_usd_b": 21.4,
        "tier": "1A",
        "source": "MSFT Q1 FY26 10-Q (Q3 calendar 2025)",
    }
    qc["2025Q4"] = {
        "msft_usd_b": 37.5,
        "tier": "1A",
        "source": "MSFT Q2 FY26 10-Q (Q4 calendar 2025); cited Zitron 2026-05-06",
    }
    log("[entities] updated market_aggregates.quarterly_capex — MSFT Q3 25 $21.4B + Q4 25 $37.5B")

    save_json(ENTITIES, doc)


# ──────────────────────────────────────────────────────────────────────
# 3. depreciation.json — new file
# ──────────────────────────────────────────────────────────────────────


def write_depreciation():
    doc = {
        "_doc": "wq-094 — depreciation watch. Quarterly hyperscaler depreciation + WSJ 2030 % of net income projection. Renders on /capital.html below the existing time-bomb section.",
        "lastUpdated": TODAY,
        "set_by": "scripts/migrate_wq094.py (wq-094)",
        "quarterly": {
            "2026Q1": {
                "msft_usd_b": 10.1,
                "googl_usd_b": 6.48,
                "amzn_usd_b": 18.94,
                "meta_usd_b": 5.9,
                "tier": "1A",
                "source": "Q1 2026 10-Qs",
            }
        },
        "wsj_2030_projection_pct_net_income": {
            "meta": 58,
            "msft": 40,
            "googl": 38,
            "tier": "2B",
            "source": "WSJ 2026 projection cited Zitron 2026-05-06",
        },
    }
    if DEPRECIATION.exists():
        existing = load_json(DEPRECIATION)
        if existing == doc:
            log("[depreciation.json] already up to date")
            return
    save_json(DEPRECIATION, doc)
    log(f"[depreciation.json] wrote new file at {DEPRECIATION.relative_to(REPO)}")


# ──────────────────────────────────────────────────────────────────────
# 4. datacenter-attribution-map.json — Project Rainier energised-MW field
# ──────────────────────────────────────────────────────────────────────


def migrate_dc_map():
    doc = load_json(DC_MAP)
    rainier = doc.get("by_project", {}).get("Anthropic-Amazon New Carlisle")
    if rainier and "power_mw_energised_2026" not in rainier:
        rainier["power_mw_energised_2026"] = None
        rainier["power_mw_energised_note"] = (
            "Nameplate capacity = 1092 MW (TAIL Tier 1A, sourced from AWS press release + Cat generator filings + Anthropic property docs). "
            "Zitron 2026-05-06 cites 500 MW for Project Rainier — likely the energised-today figure vs full nameplate. "
            "wq-094: field added (null) for future population once a verifiable energised-MW datapoint is available. Do not downgrade the 1092 nameplate."
        )
        save_json(DC_MAP, doc)
        log("[datacenter-attribution-map] added power_mw_energised_2026 (null) to Project Rainier")
    else:
        log("[datacenter-attribution-map] Project Rainier already has energised-MW field or not found")


# ──────────────────────────────────────────────────────────────────────
# 5. assumptions-audit.md — clean stale row 12 (Microsoft Copilot $13B)
# ──────────────────────────────────────────────────────────────────────


def migrate_audit_md():
    text = AUDIT_MD.read_text()
    stale_row = "| Microsoft Copilot | Q2 FY2026 ARR | $13B (full AI business) | Microsoft / Tech-Insider | 15M paid seats = 3.3% of 450M commercial M365 base |"
    new_row = (
        "| M365 Copilot | 2025 published (leaked-actual basis) | $1.35B (band $1.2–1.5B) | Zitron 2026-05-06 leaked Azure billing — Q2 FY25 $367M / Q3 FY25 $300M | wq-094 (2026-05-07) restated from $5.4B list-billings (15M × $30 × 12) to leaked-actual midpoint. Three bands stored in entities.json. Stale '$13B (full AI business)' row removed — that was misattributed MSFT total AI ARR, not M365 Copilot specifically. |"
    )
    if stale_row in text:
        text = text.replace(stale_row, new_row)
        AUDIT_MD.write_text(text)
        log("[assumptions-audit.md] replaced stale Microsoft Copilot $13B row with wq-094 leaked-actual restatement")
    else:
        log("[assumptions-audit.md] stale row not found — already migrated or text drift")


# ──────────────────────────────────────────────────────────────────────
# Driver
# ──────────────────────────────────────────────────────────────────────


def main():
    log(f"=== wq-094 migration starting {datetime.now(timezone.utc).isoformat()} ===")
    migrate_compute_disclosures()
    migrate_entities()
    write_depreciation()
    migrate_dc_map()
    migrate_audit_md()
    log("=== wq-094 migration complete ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
