#!/usr/bin/env python3
"""wq-101 — augment site-data.json with vendor posture data.

Extends each of 12 cohort entries in dashboard.enterpriseReality with:
  archetype, arrShare {value, denominator, denominatorType},
  postureScores {disclosure, bundling, pricing, cost, acceleration,
                 _prototype, _lastVerified},
  gmUnavailable (bool, only when COST=NA),
  watchSignals (narrative paragraph).

Adds top-level dashboard.vendorPostureMethodology block.

Idempotent: re-running overwrites the same fields cleanly. Other entries
left untouched.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE_DATA = ROOT / "site-data.json"

# 12-product cohort. Scores per brief §7 (D7-corrected business-unit
# denominators applied to GitHub/Workspace/Dynamics/Oracle disclosure).
POSTURE = {
    "m365_copilot": {
        "product": "M365 Copilot",
        "parent": "Microsoft",
        "archetype": "Real workload, real cost, small share",
        "arrShare": {
            "value": "1.0–1.4%",
            "denominator": "MSFT total revenue (~$245B FY24)",
            "denominatorType": "parent_total",
        },
        "aiArr": {
            "value": "~$2.5–3.5B",
            "basis": "real, net of discounting",
        },
        "postureScores": {"disclosure": 4, "bundling": 5, "pricing": 2, "cost": 5, "acceleration": 3},
        "scoreCitations": {
            "bundling": "Distinct $30/user/mo product line with its own SKU, marketed as a flagship Microsoft surface alongside Windows and Office at top-of-company messaging.",
            "cost": "Microsoft FY26 Q3 earnings — Cloud gross margin down 3pp explicitly attributed to AI infrastructure costs.",
        },
        "watchSignals": (
            "3.3% of 450M installed base after two years. Market share fell 18.8% → 11.5% "
            "(Recon Analytics). Auto-installing across tenants. Morgan Stanley described "
            "enterprise reception as a “wall of sorry.” Cloud margin down 3pp directly "
            "attributed to AI infra cost. Disclosure tier_1b but only ~1% of parent revenue."
        ),
    },
    "github_copilot": {
        "product": "GitHub Copilot",
        "parent": "Microsoft",
        "archetype": "AI is the product, but small at parent scale",
        "arrShare": {
            "value": "50–82%",
            "denominator": "GitHub ARR (~$2B)",
            "denominatorType": "business_unit",
        },
        "aiArr": {
            "value": "$1–2.3B",
            "basis": "AI is the product",
        },
        # D7: with GitHub-ARR denominator, disclosure rises 2 → 5
        "postureScores": {"disclosure": 5, "bundling": 5, "pricing": 2, "cost": 5, "acceleration": 5},
        "scoreCitations": {
            "bundling": "Separately-priced product line with three tiers ($10 Pro / $19 Business / $39 Enterprise), branded as the headline AI developer product across GitHub and Microsoft messaging.",
            "cost": "SemiAnalysis Aug-2025 — Microsoft added Anthropic models 'at great expense to margins.' Usage caps introduced mid-2025 are explicit cost-control signal.",
        },
        "watchSignals": (
            "42% market share of AI coding. Acceptance rate 27–30% (not the 55% headline — "
            "that was task speed). Microsoft added Anthropic models “at great expense to "
            "margins” (SemiAnalysis) — explicit AI cost attribution. Usage caps introduced "
            "mid-2025. Real product, real cost, real growth — but still <1% of MSFT total "
            "revenue, ~50–82% of GitHub-ARR base."
        ),
    },
    "google_workspace_ai": {
        "product": "Google Workspace AI",
        "parent": "Alphabet",
        "archetype": "Bundled at scale, immaterial at parent",
        "arrShare": {
            "value": "~5%",
            "denominator": "Workspace ARR (~$30B est.)",
            "denominatorType": "business_unit",
        },
        "aiArr": {
            "value": "~$1.5B",
            "basis": "annualised",
        },
        # D7: with Workspace denominator, disclosure rises 2 → 3
        "postureScores": {"disclosure": 3, "bundling": 2, "pricing": 1, "cost": 2, "acceleration": 3},
        "scoreCitations": {
            "bundling": "Gemini repackaged into existing Business Standard/Plus and Enterprise tiers since Jan-2025; no standalone AI SKU and only modest brand prominence inside Workspace.",
            "cost": "Alphabet Q1 2026 earnings call — no explicit AI-attributable margin compression in Cloud GM commentary; mostly capex-driven.",
        },
        "watchSignals": (
            "Strong attach in Workspace base; meaningful seat uplift. Repackaging of "
            "existing Workspace SKUs — no pricing model change. Scoped narrowly to "
            "Workspace AI seats, separate from Gemini's frontier model business and "
            "from Google Cloud infrastructure revenue. No explicit AI cost attribution "
            "in Alphabet gross margin commentary."
        ),
    },
    "salesforce_agentforce": {
        "product": "Salesforce Agentforce",
        "parent": "Salesforce",
        "archetype": "Bold pricing, no real cost, no lift",
        "arrShare": {
            "value": "0.6–1.9%",
            "denominator": "CRM total revenue ($41.5B FY25)",
            "denominatorType": "parent_total",
        },
        "aiArr": {
            "value": "~$250–350M",
            "basis": "real GenAI only",
        },
        "postureScores": {"disclosure": 3, "bundling": 5, "pricing": 3, "cost": 1, "acceleration": 1},
        "scoreCitations": {
            "bundling": "Sold as a distinct $2-per-conversation product line, separate from Sales/Service Cloud SKUs, and used as the headline platform message company-wide.",
            "cost": "Salesforce Q4 FY26 earnings — non-GAAP gross margin flat at 77%; no observable AI-attributable compression despite Agentforce launch.",
        },
        "watchSignals": (
            "$2 / conversation pricing exists but isn’t exclusive — traditional Sales Cloud "
            "still the dominant commercial model. Gross margin flat at 77% = minimal AI "
            "COGS — high pricing posture without observable workload. ~50% of 29K deals "
            "are free or seeded. Agentforce represents under 2% of $41.5B revenue."
        ),
    },
    "databricks_mosaic": {
        "product": "Databricks (Mosaic + AI)",
        "parent": "Databricks",
        "archetype": "Private momentum, opaque margins",
        "arrShare": {
            "value": "~17–23%",
            "denominator": "Databricks ARR (~$3B+ run-rate)",
            "denominatorType": "business_unit",
        },
        "aiArr": {
            "value": "$500–700M",
            "basis": "editorial estimate",
        },
        "postureScores": {"disclosure": 3, "bundling": 4, "pricing": 2, "cost": 0, "acceleration": 4},
        "scoreCitations": {
            "bundling": "Mosaic AI Model Serving, Vector Search and Agent Bricks priced as discrete consumption SKUs under a unified Mosaic AI brand at the top of Databricks platform messaging.",
            "cost": "NA — Databricks is private; no public gross margin disclosure.",
        },
        "gmUnavailable": True,
        "watchSignals": (
            "Strong enterprise attach. AI workloads called out as largest growth driver of "
            "2025 ARR uplift. Already consumption-based — AI doesn’t change the model. "
            "Reporting via press, not disclosure. Trad_saas because Lakehouse is the "
            "underlying product being AI-augmented. GM not publicly available."
        ),
    },
    "servicenow_now_assist": {
        "product": "ServiceNow Now Assist",
        "parent": "ServiceNow",
        "archetype": "Cleanest disclosure, real share",
        "arrShare": {
            "value": "~3.6–4.5%",
            "denominator": "NOW total revenue (~$11B FY24)",
            "denominatorType": "parent_total",
        },
        "aiArr": {
            "value": "~$400–500M",
            "basis": "premium-SKU ACV",
        },
        "postureScores": {"disclosure": 5, "bundling": 4, "pricing": 2, "cost": 4, "acceleration": 3},
        "scoreCitations": {
            "bundling": "Now Assist is the differentiator inside the new Pro Plus premium tier rather than a standalone SKU — heavily marketed, but the AI capability is sold by upgrading the existing platform tier.",
            "cost": "ServiceNow Q4 2025 earnings — non-GAAP gross margin down 1.7pp (79.2% → 77.5%) with explicit AI / inference cost attribution in management commentary.",
        },
        "watchSignals": (
            "Pro Plus premium take est. 30–60% (UpperEdge) — but still a tier upgrade on "
            "the existing seat model, not a new pricing model. Inference cost est. "
            "$15–50M/yr on $600M+ ACV = 92–97% “AI margin.” Gross margin down 1.7pp "
            "(79.2 → 77.5%) with explicit AI attribution. Highest share-of-parent in the "
            "cohort and the cleanest disclosure trail."
        ),
    },
    "adobe_firefly": {
        "product": "Adobe Firefly",
        "parent": "Adobe",
        "archetype": "Credits without lift",
        "arrShare": {
            "value": "0.9–1.4%",
            "denominator": "ADBE total revenue (~$22B FY24)",
            "denominatorType": "parent_total",
        },
        "aiArr": {
            "value": "~$200–300M",
            "basis": "incremental",
        },
        "postureScores": {"disclosure": 2, "bundling": 2, "pricing": 3, "cost": 1, "acceleration": 1},
        "scoreCitations": {
            "bundling": "Firefly generative credits absorbed into Creative Cloud tiers with no standalone subscription; a secondary Firefly Premium add-on exists but does not anchor Adobe's SKU stack.",
            "cost": "Adobe FY25 earnings — non-GAAP gross margin stable at ~88%; no AI-attributable compression in management commentary.",
        },
        "watchSignals": (
            "75% of Fortune 500 “adopted” but free tier inflates. Generative credits "
            "represent a real pricing model layer (usage-tied) even though credits are "
            "bundled into Creative Cloud tiers. Growth completely flat at 10–11% pre AND "
            "post AI. GM stable at 88% — no observable AI cost in margins. Firefly has "
            "moved the needle zero on top-line growth."
        ),
    },
    "microsoft_dynamics_copilot": {
        "product": "Dynamics 365 Copilot",
        "parent": "Microsoft",
        "archetype": "Niche scale, shared infra cost",
        "arrShare": {
            "value": "~7–8%",
            "denominator": "Dynamics 365 ARR (~$5–6B)",
            "denominatorType": "business_unit",
        },
        "aiArr": {
            "value": "$300–500M",
            "basis": "editorial estimate",
        },
        # D7: with Dynamics denominator, disclosure rises 1 → 3
        "postureScores": {"disclosure": 3, "bundling": 4, "pricing": 2, "cost": 5, "acceleration": 3},
        "scoreCitations": {
            "bundling": "Copilot add-ons for Sales/Service/Finance/Supply Chain priced as $30–50/user/mo premium SKUs on top of existing Dynamics modules under the Copilot product brand.",
            "cost": "Microsoft FY26 Q3 earnings — Cloud GM compression (-3pp) is parent-level AI infra cost; Dynamics inherits the same shared GM by construction (Microsoft trio shares parent GM).",
        },
        "watchSignals": (
            "Smaller surface than M365 Copilot, targeted to Dynamics base. Sits inside "
            "Microsoft's reported AI run-rate gross. Inherits parent-level AI cost "
            "realisation (Microsoft cloud margin -3pp) — the Microsoft Copilot trio shares parent GM, "
            "by design. Editorial estimate, immaterial at parent scale."
        ),
    },
    "notion_ai": {
        "product": "Notion AI",
        "parent": "Notion",
        "archetype": "Private add-on momentum",
        "arrShare": {
            "value": "~20–30%",
            "denominator": "Notion ARR (~$1B est.)",
            "denominatorType": "business_unit",
        },
        "aiArr": {
            "value": "$200–300M",
            "basis": "estimated late 2025",
        },
        "postureScores": {"disclosure": 3, "bundling": 4, "pricing": 2, "cost": 0, "acceleration": 4},
        "scoreCitations": {
            "bundling": "$10/user/month add-on attached to existing Plus/Business/Enterprise seats — discrete in price but positioned as a feature add-on rather than a separate Notion product line.",
            "cost": "NA — Notion is private; no public gross margin disclosure.",
        },
        "gmUnavailable": True,
        "watchSignals": (
            "Strong attach in mid-market; consumer take-rate softer. $10/seat AI add-on — "
            "premium tier on existing seat model. High share of own (private) ARR. "
            "Repackaging existing Notion product with AI. Reporting via press, not "
            "disclosure. GM not publicly available."
        ),
    },
    "intuit_assist": {
        "product": "Intuit Assist",
        "parent": "Intuit",
        "archetype": "Bundled, stable, invisible",
        "arrShare": {
            "value": "0.9–1.6%",
            "denominator": "INTU total revenue (~$16B FY24)",
            "denominatorType": "parent_total",
        },
        "aiArr": {
            "value": "$150–250M",
            "basis": "editorial estimate",
        },
        "postureScores": {"disclosure": 2, "bundling": 1, "pricing": 1, "cost": 2, "acceleration": 2},
        "scoreCitations": {
            "bundling": "Assist absorbed into existing QuickBooks, TurboTax and Mailchimp tiers at no upcharge — no separate AI SKU and limited top-line brand prominence.",
            "cost": "Intuit FY26 narrative — non-GAAP gross margin ~83–84%, minimal AI-attributable movement; bundled inference cost not broken out.",
        },
        "watchSignals": (
            "Active rollout 2025–26; usage growing. Repackaging existing SKUs with AI — "
            "no pricing model change, no premium tier, no separate disclosure. Growth "
            "flat vs pre-AI baseline. No observable AI cost in Intuit GM."
        ),
    },
    "oracle_fusion_ai": {
        "product": "Oracle Fusion AI",
        "parent": "Oracle",
        "archetype": "Hidden in the bundle",
        "arrShare": {
            "value": "~1.3%",
            "denominator": "Oracle Cloud Applications (~$15B)",
            "denominatorType": "business_unit",
        },
        "aiArr": {
            "value": "~$100–300M",
            "basis": "editorial estimate",
        },
        # D7: with ORCL Apps denominator, disclosure rises 1 → 2
        "postureScores": {"disclosure": 2, "bundling": 1, "pricing": 1, "cost": 2, "acceleration": 3},
        "scoreCitations": {
            "bundling": "Fusion AI agents rolled into existing Cloud Apps SKUs with no discrete AI tier or distinct product brand at the Oracle messaging level.",
            "cost": "Oracle Q3 FY26 earnings — gross margin pressure visible at parent but driven by OCI capex/depreciation, not Fusion AI inference cost.",
        },
        "watchSignals": (
            "Distinct from OCI infrastructure revenue: Oracle's AI footprint splits across "
            "Fusion AI (the SaaS apps line) and OCI AI infrastructure (the compute line), "
            "which sit in separate cohorts. Limited public disclosure — bundled into Oracle "
            "SaaS without a discrete revenue line. Margin pressure visible at parent but mostly "
            "OCI capex, not Fusion AI software cost."
        ),
    },
    "snowflake_cortex": {
        "product": "Snowflake Cortex",
        "parent": "Snowflake",
        "archetype": "Consumption-bundled",
        "arrShare": {
            "value": "~4.3–7.1%",
            "denominator": "SNOW total revenue (~$3.5B FY25)",
            "denominatorType": "parent_total",
        },
        "aiArr": {
            "value": "~$150–250M",
            "basis": "editorial estimate",
        },
        "postureScores": {"disclosure": 3, "bundling": 2, "pricing": 3, "cost": 2, "acceleration": 3},
        "scoreCitations": {
            "bundling": "Cortex AI/ML functions metered inside existing Data Cloud consumption credits with no separate SKU; Cortex is branded but the catalog structure is unchanged.",
            "cost": "Snowflake Q4 FY26 earnings — non-GAAP product gross margin stable; AI inference cost hidden inside total platform consumption with no discrete AI margin call-out.",
        },
        "watchSignals": (
            "Bundled into Data Cloud consumption — AI extends an already-consumption-based "
            "model. Material share of SNOW total revenue (~5%). AI-on-data feature stack "
            "repackages Snowflake’s existing platform. Margin stable; AI cost hidden "
            "inside total platform consumption."
        ),
    },
}

LAST_VERIFIED = "2026-Q1"

VENDOR_POSTURE_METHODOLOGY = {
    "version": "1.0",
    "axesCount": 5,
    "axes": ["disclosure", "bundling", "pricing", "cost", "acceleration"],
    "axisLabels": {
        "disclosure": "DISC",
        "bundling": "PKG",
        "pricing": "PRICE",
        "cost": "GM",
        "acceleration": "ACCEL",
    },
    "lastUpdated": "2026-05-09",
    "lastEditorialReview": "2026-05-09",
    "reviewCadence": "per_earnings_cycle",
    "reviewPlaybook": "docs/playbooks/vendor-posture-quarterly-review.md",
    "sourceBrief": "wq-101-vendor-ai-posture-radar",
    "rubricLocation": "inline-accordion",
}


def apply(site):
    # Mutates site dict in place. Importable from generate_site_data.py so the
    # cohort posture scores survive every regenerate of enterpriseReality.
    dash = site["dashboard"]
    dash["vendorPostureMethodology"] = VENDOR_POSTURE_METHODOLOGY

    er = dash["enterpriseReality"]
    found = set()
    for entry in er:
        eid = entry.get("id")
        if eid not in POSTURE:
            continue
        found.add(eid)
        spec = POSTURE[eid]
        if spec.get("product"):
            entry["product"] = spec["product"]
        if spec.get("parent"):
            entry["parent"] = spec["parent"]
        entry["archetype"] = spec["archetype"]
        entry["arrShare"] = spec["arrShare"]
        if spec.get("aiArr"):
            entry["aiArr"] = dict(spec["aiArr"])
        scores = dict(spec["postureScores"])
        # D4 path-b: drafted citations for Bundling and Cost editorial scores;
        # Simon validates each at staging review before clearing _prototype.
        if spec.get("scoreCitations"):
            scores["_citations"] = dict(spec["scoreCitations"])
        scores["_prototype"] = True
        scores["_lastVerified"] = LAST_VERIFIED
        entry["postureScores"] = scores
        if spec.get("gmUnavailable"):
            entry["gmUnavailable"] = True
        else:
            # ensure stale gmUnavailable doesn't persist if we re-run after a tier change
            entry.pop("gmUnavailable", None)
        entry["watchSignals"] = spec["watchSignals"]

    missing = set(POSTURE.keys()) - found
    if missing:
        raise SystemExit(f"FATAL: cohort entries missing from enterpriseReality: {sorted(missing)}")

    return len(found)


def main():
    text = SITE_DATA.read_text(encoding="utf-8")
    data = json.loads(text)
    count = apply(data)
    SITE_DATA.write_text(
        json.dumps(data, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"OK: extended {count}/12 cohort entries; vendorPostureMethodology block written.")


if __name__ == "__main__":
    main()
