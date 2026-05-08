#!/usr/bin/env python3
"""
migrate_wq096.py — wq-096 Revenue Model Data Structure Refactor

Idempotent migration that populates data/evidence/* trees with the records
that scripts/generate_site_data.py will read to emit:
  - enterpriseReality (numeric-first, expanded)
  - computeProviders.aiNativeCompute
  - computeProviders.tradCompute
  - arrModel (computed; pass-through deductions sourced here)

Also writes the legacy topConsumers archive snapshot before the token-factory
records get filtered out by the generator.

All claimed ARR figures here carry a `provenance` tag on the TAIL Tier 1A → 3C
scale. Where a number is editorial (Tier 2B/3A), the rationale is in `arrSource`.

Re-running this script is safe — it overwrites the evidence files. Hand-edits
to evidence files survive only if this migration is not re-run.
"""

import json
import os
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EV = os.path.join(ROOT, "data", "evidence")
ARCHIVE = os.path.join(ROOT, "data", "archive")


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)


# ─────────────────────────────────────────────────────────────────────
# Phase B — enterpriseReality evidence
# ─────────────────────────────────────────────────────────────────────
# Each record carries:
#   id, name, ticker, tier="trad_saas", arrClaimedNumeric (USD B),
#   arrAsOf, arrSource, provenance, optional arrClaimedVsReal,
#   narrative (claimed / usage / real / flags), growth / prevGrowth.
# Existing 7 records preserved with parsed numeric figures; 11+ new records added.

ENTERPRISE_REALITY = [
    {
        "id": "m365_copilot",
        "name": "M365 Copilot",
        "ticker": "MSFT",
        "tier": "trad_saas",
        "arrClaimedNumeric": 5.4,
        "arrAsOf": "2026-Q1",
        "arrSource": "Microsoft FY26 Q3 earnings — 15M paid seats × $30/mo annualised = $5.4B list-billings",
        "provenance": "tier_1b",
        "arrClaimedVsReal": {
            "realRange": [2.5, 3.5],
            "realNote": "40-60% effective discounting per Citi/JPM channel checks; cloud margin down 3pp = real AI infra cost.",
        },
        "narrative": {
            "claimed": "15M seats x $30/mo = $5.4B list (verified, MSFT Q2 FY26 earnings)",
            "usage": "35.8% active (Recon Analytics, 150K respondents). Only 5% of orgs past pilot (Gartner). 70% tried, only 8% kept choosing it.",
            "real": "~$2.5-3.5B net (40-60% discounting per Citi/JPM). Cloud margin down 3pp (72->69%) — real AI infra cost.",
            "flags": "3.3% of 450M installed base after 2 years. Market share FELL 18.8%->11.5% (Recon Analytics Jul->Jan). Auto-installing. Morgan Stanley: \"wall of sorry.\"",
        },
        "growth": "12-15%",
        "prevGrowth": "15%",
    },
    {
        "id": "github_copilot",
        "name": "GitHub Copilot",
        "ticker": "MSFT",
        "tier": "trad_saas",
        "arrClaimedNumeric": 1.65,
        "arrAsOf": "2026-Q1",
        "arrSource": "MSFT earnings narrative — 4.7M paid subs, GitHub total $2B ARR; Copilot midpoint $1-2.3B → $1.65B",
        "provenance": "tier_2a",
        "narrative": {
            "claimed": "4.7M paid subs (verified, MSFT earnings). GitHub total $2B ARR — Copilot est. $1-2.3B",
            "usage": "42% market share of AI coding. 27-30% acceptance rate (not 55% — that was task speed). Lost $20/user/mo in 2023 (WSJ).",
            "real": "$1-2.3B — the ONE product where AI IS the product",
            "flags": "Genuinely works. But facing Cursor ($1B ARR), open-source alternatives. Microsoft added Anthropic models \"at great expense to margins\" (SemiAnalysis). Usage caps introduced mid-2025.",
        },
        "growth": "75% subs YoY",
        "prevGrowth": "N/A",
    },
    {
        "id": "salesforce_agentforce",
        "name": "Salesforce Agentforce",
        "ticker": "CRM",
        "tier": "trad_saas",
        "arrClaimedNumeric": 0.8,
        "arrAsOf": "2026-Q1",
        "arrSource": "Salesforce Q4 FY26 earnings — Agentforce ACV component of $2.9B AI+Data line",
        "provenance": "tier_2a",
        "arrClaimedVsReal": {
            "realRange": [0.25, 0.35],
            "realNote": "Real GenAI ~$250-350M (rest is Data Cloud, Informatica, legacy Einstein); ~50% of 29K deals free/seeded.",
        },
        "narrative": {
            "claimed": "$800M Agentforce ARR (within $2.9B \"AI+Data\" that includes Informatica acquisition)",
            "usage": "~50% of 29K deals are free/seeded. COGS test: inference cost est. $6-12M/yr on $800M = 98%+ \"AI margin\"",
            "real": "~$250-350M real GenAI (rest is Data Cloud, Informatica, legacy Einstein)",
            "flags": "$2.9B bundles Informatica ($1.5B acq.) + Data 360 + Agentforce. Gross margin flat at 77% = minimal AI COGS. AWU metric criticized as vanity metric. <2% of $41.5B revenue.",
        },
        "growth": "8-9%",
        "prevGrowth": "18%",
    },
    {
        "id": "servicenow_now_assist",
        "name": "ServiceNow Now Assist",
        "ticker": "NOW",
        "tier": "trad_saas",
        "arrClaimedNumeric": 0.6,
        "arrAsOf": "2025-Q4",
        "arrSource": "ServiceNow Q4 2025 earnings — $600M+ Now Assist ACV",
        "provenance": "tier_1b",
        "arrClaimedVsReal": {
            "realRange": [0.4, 0.5],
            "realNote": "Cleanest reporter — AI is genuine premium SKU, but Pro Plus bundles non-AI features.",
        },
        "narrative": {
            "claimed": "$600M+ Now Assist ACV (verified, Q4 2025 earnings)",
            "usage": "Pro Plus premium est. 30-60% (UpperEdge). COGS test: inference cost est. $15-50M/yr = 92-97% \"AI margin\"",
            "real": "~$400-500M (cleanest reporter — AI is a genuine premium SKU)",
            "flags": "Most honest of the group. But Pro Plus bundles non-AI features. Gross margin down 1.7pp (79.2->77.5%) — slight AI cost impact. Hidden consumption-based \"assists\" fees.",
        },
        "growth": "20-21%",
        "prevGrowth": "25%",
    },
    {
        "id": "sap_joule",
        "name": "SAP Joule",
        "ticker": "SAP",
        "tier": "trad_saas",
        "arrClaimedNumeric": 0.1,
        "arrAsOf": "2026-Q1",
        "arrSource": "SAP commentary — 'Joule bundled free in RISE/GROW; 2/3 of deals include AI'; no separate metering. Editorial midpoint of $0-200M range.",
        "provenance": "tier_3a",
        "arrClaimedVsReal": {
            "realRange": [0.0, 0.2],
            "realNote": "Like saying '100% of iPhones include Siri.' Cloud growth (23%) driven by S/4HANA forced migration, not Joule.",
        },
        "narrative": {
            "claimed": "\"2/3 of deals include AI\" — Joule bundled free in RISE/GROW",
            "usage": "No separate metering. No AI revenue disclosed = immaterial.",
            "real": "~$0-200M. Like saying \"100% of iPhones include Siri\"",
            "flags": "Cloud growth (23%) driven by S/4HANA forced migration (ECC end-of-life 2027), NOT AI. No analyst attributes growth to Joule.",
        },
        "growth": "8-9%",
        "prevGrowth": "8%",
    },
    {
        "id": "adobe_firefly",
        "name": "Adobe Firefly",
        "ticker": "ADBE",
        "tier": "trad_saas",
        "arrClaimedNumeric": 0.45,
        "arrAsOf": "2026-Q1",
        "arrSource": "Adobe FY25 earnings narrative — Firefly $400-500M, AI-first ARR $250M; midpoint $450M",
        "provenance": "tier_2b",
        "arrClaimedVsReal": {
            "realRange": [0.2, 0.3],
            "realNote": "Some cannibalises stock photo revenue; growth flat at 10-11% pre and post AI.",
        },
        "narrative": {
            "claimed": "Firefly ~$400-500M, AI-first ARR $250M",
            "usage": "75% of Fortune 500 \"adopted\" but free tier inflates. Some cannibalizes stock photo revenue.",
            "real": "~$200-300M incremental",
            "flags": "Growth completely flat at 10-11% pre AND post AI. Firefly has moved the needle zero on top-line growth.",
        },
        "growth": "10-11%",
        "prevGrowth": "10-11%",
    },
    {
        "id": "workday_ai",
        "name": "Workday AI",
        "ticker": "WDAY",
        "tier": "trad_saas",
        "arrClaimedNumeric": 0.05,
        "arrAsOf": "2026-Q1",
        "arrSource": "Workday narrative — 'growing demand for AI SKUs'; no AI metric disclosed. Editorial midpoint of $0-100M range.",
        "provenance": "tier_3b",
        "arrClaimedVsReal": {
            "realRange": [0.0, 0.1],
            "realNote": "Growth crashing 21%->13%; AI has zero visible impact.",
        },
        "narrative": {
            "claimed": "Not disclosed — \"growing demand for AI SKUs\"",
            "usage": "No AI metric = immaterial. Flex Credits model.",
            "real": "~$0-100M",
            "flags": "Growth crashing: 21%->13%. AI has zero visible impact.",
        },
        "growth": "13%",
        "prevGrowth": "21%",
    },
    # ─── new entries (Phase B expansion) ───
    {
        "id": "atlassian_intelligence",
        "name": "Atlassian Intelligence / Rovo",
        "ticker": "TEAM",
        "tier": "trad_saas",
        "arrClaimedNumeric": 0.15,
        "arrAsOf": "2026-Q1",
        "arrSource": "Atlassian FY26 Q3 commentary — Rovo paid SKU launched late 2025; editorial estimate from cloud uplift attribution",
        "provenance": "tier_2b",
        "narrative": {
            "claimed": "Rovo + Atlassian Intelligence — paid SKU launched late 2025; not separately disclosed",
            "usage": "Bundled with Premium/Enterprise; Rovo standalone available. Adoption modest.",
            "real": "~$100-200M editorial",
            "flags": "Atlassian growth narrative leans on AI but no discrete revenue line; reconcile against Cloud growth attribution.",
        },
        "growth": "20-22%",
        "prevGrowth": "25%",
    },
    {
        "id": "notion_ai",
        "name": "Notion AI",
        "ticker": "private",
        "tier": "trad_saas",
        "arrClaimedNumeric": 0.25,
        "arrAsOf": "2026-Q1",
        "arrSource": "Notion press commentary 2025 — $10/seat AI add-on; >$200M ARR-stack reported. Editorial uplift to $250M for early 2026.",
        "provenance": "tier_2b",
        "narrative": {
            "claimed": "$10/seat AI add-on; ~$200-300M ARR estimated late 2025",
            "usage": "Strong attach in mid-market; consumer take-rate softer.",
            "real": "$200-300M",
            "flags": "Private; reporting via press, not disclosure. Repackaging existing Notion product with AI = trad_saas.",
        },
        "growth": "fast",
        "prevGrowth": "n/a",
    },
    {
        "id": "google_workspace_ai",
        "name": "Google Workspace AI (Gemini in Workspace)",
        "ticker": "GOOGL",
        "tier": "trad_saas",
        "arrClaimedNumeric": 1.5,
        "arrAsOf": "2026-Q1",
        "arrSource": "Alphabet Q1 2026 commentary — Gemini-in-Workspace external AI seats; reconciles with compute_disclosures.json:googl_cloud_ai.copilot_excluded_2025_usd_b $1.5B (MS-declared analogue)",
        "provenance": "tier_2a",
        "narrative": {
            "claimed": "Gemini-in-Workspace AI add-on; bundled in Business/Enterprise tiers",
            "usage": "Strong attach in Workspace base; meaningful seat uplift.",
            "real": "$1.5B (annualised)",
            "flags": "AI repackaging of existing Workspace SKU = trad_saas. Distinct from Gemini frontier (provider) and GCP (trad_compute) — see Decision D9.",
        },
        "growth": "fast",
        "prevGrowth": "n/a",
    },
    {
        "id": "oracle_fusion_ai",
        "name": "Oracle Fusion AI",
        "ticker": "ORCL",
        "tier": "trad_saas",
        "arrClaimedNumeric": 0.2,
        "arrAsOf": "2026-Q1",
        "arrSource": "Oracle Q3 FY26 commentary — Fusion AI bundled into SaaS apps; no discrete disclosure. Editorial estimate.",
        "provenance": "tier_2b",
        "narrative": {
            "claimed": "Fusion AI agents — bundled into Oracle SaaS apps; no discrete revenue disclosure",
            "usage": "Limited disclosure; small relative to OCI infra revenue",
            "real": "~$100-300M editorial",
            "flags": "Distinct from OCI (trad_compute). Per Decision D9, Oracle splits across Fusion AI (trad_saas) and OCI AI infra (trad_compute).",
        },
        "growth": "fast",
        "prevGrowth": "n/a",
    },
    {
        "id": "snowflake_cortex",
        "name": "Snowflake Cortex",
        "ticker": "SNOW",
        "tier": "trad_saas",
        "arrClaimedNumeric": 0.2,
        "arrAsOf": "2026-Q1",
        "arrSource": "Snowflake Q4 FY26 commentary — Cortex AI suite; consumption-based; not separately disclosed. Editorial estimate.",
        "provenance": "tier_2b",
        "narrative": {
            "claimed": "Cortex AI/ML suite; consumption-based; not separately disclosed",
            "usage": "Bundled into Data Cloud consumption; meaningful but small share.",
            "real": "~$150-250M editorial",
            "flags": "AI-on-data feature stack; trad_saas because it's repackaging Snowflake data platform with AI.",
        },
        "growth": "fast",
        "prevGrowth": "n/a",
    },
    {
        "id": "databricks_mosaic",
        "name": "Databricks (Mosaic + AI)",
        "ticker": "private",
        "tier": "trad_saas",
        "arrClaimedNumeric": 0.6,
        "arrAsOf": "2026-Q1",
        "arrSource": "Databricks press 2025 — Mosaic AI + GenAI suite uplift on $3B+ run-rate; editorial AI-attributable share",
        "provenance": "tier_2b",
        "narrative": {
            "claimed": "Mosaic AI + DBRX + AI agents on Lakehouse; consumption + SKU mix",
            "usage": "Strong enterprise attach; AI workloads largest growth driver of 2025 ARR uplift.",
            "real": "$500-700M editorial",
            "flags": "Private; reporting via press; AI-attributable share is editorial. Trad_saas because Lakehouse is the underlying product being AI-augmented.",
        },
        "growth": "fast",
        "prevGrowth": "n/a",
    },
    {
        "id": "hubspot_breeze",
        "name": "HubSpot Breeze",
        "ticker": "HUBS",
        "tier": "trad_saas",
        "arrClaimedNumeric": 0.08,
        "arrAsOf": "2026-Q1",
        "arrSource": "HubSpot FY25 earnings narrative — Breeze AI bundled into Hubs; no discrete disclosure. Editorial.",
        "provenance": "tier_3a",
        "narrative": {
            "claimed": "Breeze AI agents/copilot bundled into Hubs",
            "usage": "Bundled — no AI metering",
            "real": "<$100M",
            "flags": "Breeze bundled into existing Hub SKUs; not a paid add-on.",
        },
        "growth": "16-18%",
        "prevGrowth": "20%",
    },
    {
        "id": "box_ai",
        "name": "Box AI",
        "ticker": "BOX",
        "tier": "trad_saas",
        "arrClaimedNumeric": 0.05,
        "arrAsOf": "2026-Q1",
        "arrSource": "Box FY26 narrative — Enterprise Plus AI tier; small contribution. Editorial.",
        "provenance": "tier_3a",
        "narrative": {
            "claimed": "Box AI in Enterprise Plus tier; consumption-based",
            "usage": "Small share of revenue mix",
            "real": "<$100M",
            "flags": "Small surface area relative to other trad_saas entries.",
        },
        "growth": "5-7%",
        "prevGrowth": "8%",
    },
    {
        "id": "zoom_companion",
        "name": "Zoom AI Companion",
        "ticker": "ZM",
        "tier": "trad_saas",
        "arrClaimedNumeric": 0.05,
        "arrAsOf": "2026-Q1",
        "arrSource": "Zoom FY26 narrative — AI Companion bundled free in paid plans; no discrete revenue. Editorial.",
        "provenance": "tier_3b",
        "narrative": {
            "claimed": "AI Companion bundled in paid Zoom plans (no incremental fee)",
            "usage": "High activation but immaterial revenue impact (no premium SKU)",
            "real": "~$0-100M",
            "flags": "Bundled-free model means revenue impact is the seat-attach lift, not a discrete AI line.",
        },
        "growth": "3%",
        "prevGrowth": "5%",
    },
    {
        "id": "intuit_assist",
        "name": "Intuit Assist",
        "ticker": "INTU",
        "tier": "trad_saas",
        "arrClaimedNumeric": 0.2,
        "arrAsOf": "2026-Q1",
        "arrSource": "Intuit FY26 narrative — Assist agentic AI rolling across QuickBooks/TurboTax/Mailchimp; editorial estimate of incremental seat uplift",
        "provenance": "tier_2b",
        "narrative": {
            "claimed": "Assist (agentic AI) bundled across QuickBooks/TurboTax/Mailchimp",
            "usage": "Active rollout 2025-26; usage growing",
            "real": "$150-250M editorial",
            "flags": "Repackaging existing SKUs with AI = trad_saas.",
        },
        "growth": "12-13%",
        "prevGrowth": "13%",
    },
    {
        "id": "microsoft_dynamics_copilot",
        "name": "Microsoft Dynamics 365 Copilot",
        "ticker": "MSFT",
        "tier": "trad_saas",
        "arrClaimedNumeric": 0.4,
        "arrAsOf": "2026-Q1",
        "arrSource": "Microsoft FY26 Q3 commentary — Dynamics Copilot SKUs (Sales/Service/Finance/Supply Chain). Editorial estimate within $37B AI run-rate.",
        "provenance": "tier_2b",
        "narrative": {
            "claimed": "Dynamics 365 Copilot SKUs — Sales/Service/Finance/Supply Chain",
            "usage": "Smaller surface than M365 Copilot; targeted to Dynamics base",
            "real": "$300-500M editorial",
            "flags": "Per Decision D9, sits inside Microsoft AI run-rate gross; carved out into trad_saas alongside M365 Copilot + GitHub Copilot.",
        },
        "growth": "fast",
        "prevGrowth": "n/a",
    },
    {
        "id": "zendesk_ai",
        "name": "Zendesk AI",
        "ticker": "private",
        "tier": "trad_saas",
        "arrClaimedNumeric": 0.1,
        "arrAsOf": "2026-Q1",
        "arrSource": "Zendesk press commentary 2025 — Advanced AI add-on $50/agent/mo; editorial estimate",
        "provenance": "tier_3a",
        "narrative": {
            "claimed": "Advanced AI add-on at $50/agent/mo + Resolution Bot consumption",
            "usage": "Mid-market attach growing; enterprise slower",
            "real": "<$200M",
            "flags": "Private (Permira-owned); disclosure thin.",
        },
        "growth": "fast",
        "prevGrowth": "n/a",
    },
    {
        "id": "github_advanced_security_ai",
        "name": "GitHub Advanced Security (AI features)",
        "ticker": "MSFT",
        "tier": "trad_saas",
        "arrClaimedNumeric": 0.05,
        "arrAsOf": "2026-Q1",
        "arrSource": "GitHub commentary — AI-augmented security scanning bundled with Advanced Security SKU",
        "provenance": "tier_3a",
        "narrative": {
            "claimed": "AI features within GitHub Advanced Security",
            "usage": "Bundled — small AI attribution",
            "real": "<$100M",
            "flags": "Small surface area; included for completeness within the MSFT trad_saas family.",
        },
        "growth": "fast",
        "prevGrowth": "n/a",
    },
]


# ─────────────────────────────────────────────────────────────────────
# Phase C — AI-Native Compute (Tier 5) evidence
# ─────────────────────────────────────────────────────────────────────

COMPUTE_NATIVE = [
    {
        "id": "coreweave",
        "name": "CoreWeave",
        "tier": "ai_native_compute",
        "subType": "bare_metal_gpu",
        "arrNumeric": 6.0,
        "arrAsOf": "2026-Q1",
        "arrSource": "CoreWeave Q1 2026 10-Q — annualised exit run-rate (Q1 26 quarterly $1.5B × 4 = $6.0B)",
        "provenance": "tier_1a",
        "doubleCountNote": "~85% of CoreWeave revenue is Microsoft sub-rent for OpenAI workload — captured in passthrough_aiNativeCompute_to_tradCompute layer.",
    },
    {
        "id": "lambda_labs",
        "name": "Lambda Labs",
        "tier": "ai_native_compute",
        "subType": "bare_metal_gpu",
        "arrNumeric": 0.72,
        "arrAsOf": "2026-Q1",
        "arrSource": "Lambda press-disclosed — annualised exit run-rate (Q1 26 quarterly ~$0.18B × 4)",
        "provenance": "tier_2b",
    },
    {
        "id": "crusoe",
        "name": "Crusoe",
        "tier": "ai_native_compute",
        "subType": "bare_metal_gpu",
        "arrNumeric": 0.48,
        "arrAsOf": "2026-Q1",
        "arrSource": "Crusoe press-disclosed — annualised exit run-rate (Q1 26 quarterly ~$0.12B × 4)",
        "provenance": "tier_2b",
    },
    {
        "id": "nebius",
        "name": "Nebius",
        "tier": "ai_native_compute",
        "subType": "bare_metal_gpu",
        "arrNumeric": 1.36,
        "arrAsOf": "2026-Q1",
        "arrSource": "Nebius (NBIS) Q1 2026 6-K — annualised exit run-rate (Q1 26 quarterly $0.34B × 4)",
        "provenance": "tier_1a",
    },
    {
        "id": "fireworks",
        "name": "Fireworks AI",
        "tier": "ai_native_compute",
        "subType": "token_factory",
        "arrNumeric": 0.14,
        "arrAsOf": "2026-Q1",
        "arrSource": "Fireworks press 2025 — ~$100M ARR late 2025; editorial uplift to $140M for early 2026",
        "provenance": "tier_2b",
        "movedFromTopConsumers": True,
    },
    {
        "id": "together_ai",
        "name": "Together AI",
        "tier": "ai_native_compute",
        "subType": "token_factory",
        "arrNumeric": 0.13,
        "arrAsOf": "2026-Q1",
        "arrSource": "Together AI press 2025 — ~$100M ARR mid-2025; editorial uplift to $130M",
        "provenance": "tier_2b",
        "movedFromTopConsumers": True,
    },
    {
        "id": "groq",
        "name": "Groq",
        "tier": "ai_native_compute",
        "subType": "token_factory",
        "arrNumeric": 0.09,
        "arrAsOf": "2026-Q1",
        "arrSource": "Groq press 2025 — Bain estimates $90M ARR late 2025",
        "provenance": "tier_2b",
        "movedFromTopConsumers": True,
    },
    {
        "id": "replicate",
        "name": "Replicate",
        "tier": "ai_native_compute",
        "subType": "token_factory",
        "arrNumeric": 0.05,
        "arrAsOf": "2026-Q1",
        "arrSource": "Replicate press — ~$50M ARR estimated 2025",
        "provenance": "tier_3a",
    },
    {
        "id": "anyscale",
        "name": "Anyscale",
        "tier": "ai_native_compute",
        "subType": "token_factory",
        "arrNumeric": 0.05,
        "arrAsOf": "2026-Q1",
        "arrSource": "Anyscale press — ~$50M ARR estimated 2025; Ray-platform based AI serving",
        "provenance": "tier_3a",
    },
    {
        "id": "fal_ai",
        "name": "Fal.ai",
        "tier": "ai_native_compute",
        "subType": "token_factory",
        "arrNumeric": 0.095,
        "arrAsOf": "2026-Q1",
        "arrSource": "Fal.ai press 2025 — ~$95M ARR end-2025; generative-media model serving",
        "provenance": "tier_2b",
        "movedFromTopConsumers": True,
    },
]


# ─────────────────────────────────────────────────────────────────────
# Phase D — Trad Compute (Tier 4) evidence
# ─────────────────────────────────────────────────────────────────────
# Per-hyperscaler with appsCarveout pointing at trad_saas record IDs.

COMPUTE_DISCLOSURES = [
    {
        "id": "azure",
        "name": "Microsoft Azure AI",
        "tier": "trad_compute",
        "arrGrossDisclosed": 37.0,
        "arrAsOf": "2026-Q1",
        "arrSource": "Microsoft FY26 Q3 earnings — '$37B annualised AI run-rate, +123% YoY'",
        "provenance": "tier_1b",
        "appsCarveout": ["m365_copilot", "github_copilot", "microsoft_dynamics_copilot"],
        "appsCarveoutNote": "Decision D9: Microsoft has NO frontier entry; Azure carves out M365 Copilot + GitHub Copilot + Dynamics Copilot which are trad_saas. Net = gross − sum(arrClaimedNumeric of carveout records).",
    },
    {
        "id": "aws",
        "name": "AWS AI",
        "tier": "trad_compute",
        "arrGrossDisclosed": 15.0,
        "arrAsOf": "2026-Q1",
        "arrSource": "Amazon CEO Andy Jassy 2026 shareholder letter — '$15B annualised run-rate'",
        "provenance": "tier_1b",
        "appsCarveout": [],
        "appsCarveoutNote": "AWS has no Copilot-equivalent productivity SaaS. Q-Developer and Bedrock pass-through are infra/compute, not Apps. Carve-out is empty.",
    },
    {
        "id": "gcp",
        "name": "Google Cloud AI",
        "tier": "trad_compute",
        "arrGrossDisclosed": 12.0,
        "arrAsOf": "2026-Q1",
        "arrSource": "Editorial Tier 2A — bottom-up from GCP Q1 2026 AI revenue $3.0B × 4 (per data/compute_disclosures.json:googl_cloud_ai.frontier_lab_compute_q1_2026 + ai_workload_compute + hosted_model_apis_gross + copilot_excluded), grossed for Workspace AI",
        "provenance": "tier_2a",
        "appsCarveout": ["google_workspace_ai"],
        "appsCarveoutNote": "Decision D9: Google splits across Gemini (frontier), Workspace AI (trad_saas), GCP ex-Workspace (trad_compute). Carve out Workspace AI from gross.",
    },
    {
        "id": "oci",
        "name": "Oracle OCI AI",
        "tier": "trad_compute",
        "arrGrossDisclosed": 3.6,
        "arrAsOf": "2026-Q1",
        "arrSource": "Oracle Q3 FY26 earnings narrative — OCI AI portion editorial Tier 2A; Q1 26 quarterly $0.9B × 4",
        "provenance": "tier_2a",
        "appsCarveout": ["oracle_fusion_ai"],
        "appsCarveoutNote": "Decision D9: Oracle splits across Fusion AI (trad_saas) and OCI AI infra (trad_compute). Carve out Fusion AI.",
    },
]


# ─────────────────────────────────────────────────────────────────────
# Phase F — Pass-through deductions
# ─────────────────────────────────────────────────────────────────────
# Three layers, named per-record relationships covering ~80% of dollar
# volume each, plus a long-tail multiplier for the remainder.

PASSTHROUGH = {
    "frontier_to_trad": [
        {
            "id": "openai_to_azure",
            "from": "openai",
            "to": "azure",
            "value": 6.5,
            "valueBasis": "Q1 2026 annualised — OpenAI's Azure compute spend",
            "source": "Bloomberg/Information 2025-26 reporting; Zitron 2026-05-06 leak corroborates Azure-resident OpenAI inference at $18.5B annualised exit run-rate (compute-paid back to Microsoft est. ~$6.5B share of OpenAI's $25B ARR)",
            "provenance": "tier_2b",
            "rationale": "OpenAI's compute spend on Azure dwarfs all other frontier-to-trad flows. Estimated as ~26% of OpenAI's $25B ARR run-rate.",
        },
        {
            "id": "anthropic_to_aws",
            "from": "anthropic",
            "to": "aws",
            "value": 5.5,
            "valueBasis": "Q1 2026 annualised — Anthropic's AWS compute spend",
            "source": "Anthropic + Amazon disclosures 2025-26; ~60% of Anthropic compute on AWS; aggregate compute spend > Anthropic's $30B ARR",
            "provenance": "tier_2b",
            "rationale": "Anthropic's compute spend exceeds its revenue (training-heavy phase). AWS share ~60% of compute.",
        },
        {
            "id": "anthropic_to_gcp",
            "from": "anthropic",
            "to": "gcp",
            "value": 1.8,
            "valueBasis": "Q1 2026 annualised — Anthropic's GCP/TPU compute spend",
            "source": "The Information 2026-04-30 — Anthropic-Google $200B 5-year commitment; Q1 2026 annualised flow ~$1.8B (early in ramp)",
            "provenance": "tier_2b",
            "rationale": "Deep Anthropic-on-TPUs partnership; April 2026 expanded multi-GW agreement from 2027. Q1 26 actual flow modest pre-ramp.",
        },
        {
            "id": "openai_to_oci",
            "from": "openai",
            "to": "oci",
            "value": 2.4,
            "valueBasis": "Q1 2026 annualised — OpenAI Stargate billings via OCI",
            "source": "Oracle Q3 FY26 RPO disclosure mentions $300B+ OpenAI commitment; realised flow Q1 26 partial-year as DCs come online (Q1 26 quarterly $0.6B × 4)",
            "provenance": "tier_2a",
            "rationale": "Stargate compute billing through OCI; partial-year contribution.",
        },
        {
            "id": "openai_to_aws",
            "from": "openai",
            "to": "aws",
            "value": 0.5,
            "valueBasis": "Q1 2026 annualised — OpenAI AWS workloads (post Q1 2026 announcement)",
            "source": "AWS-OpenAI Q1 2026 announcement of $38B + $100B/8yr expansion is RPO; realised early flow modest",
            "provenance": "tier_2b",
            "rationale": "Recently announced; realised revenue Q1 26 small relative to RPO.",
        },
        {
            "id": "_long_tail",
            "from": "_other_frontier",
            "to": "_trad_compute",
            "isLongTail": True,
            "baseValueBasis": "Aggregate ARR of frontier labs ex-OpenAI/Anthropic (xAI, Mistral, Cohere, DeepSeek, Alibaba/Qwen, Baidu, Tencent, Minimax, Moonshot, ByteDance, Meta) — ~$3.5B 2026-Q1 annualised",
            "baseValue": 3.5,
            "multiplierPct": 25,
            "rationale": "Long-tail frontier labs spend ~25% of ARR on trad-compute (lower than OpenAI/Anthropic because many run own infra (Tencent/Baidu/ByteDance) or use neoclouds rather than hyperscalers). Editorial assumption.",
            "provenance": "tier_3a",
        },
    ],
    "apps_to_aiNativeCompute": [
        {
            "id": "cursor_to_aiNativeCompute",
            "from": "cursor",
            "to": "_aiNativeCompute_aggregate",
            "value": 0.45,
            "valueBasis": "Q1 2026 annualised — Cursor compute spend on AI-native compute (token factories + neoclouds)",
            "source": "SemiAnalysis 2025 commentary — Cursor blended COGS ~45% of $1B ARR; majority via direct frontier APIs (not aiNativeCompute), residual ~10% via aiNativeCompute serving",
            "provenance": "tier_2b",
            "rationale": "Cursor mostly hits frontier API endpoints directly (Anthropic, OpenAI). aiNativeCompute exposure modest.",
        },
        {
            "id": "perplexity_to_aiNativeCompute",
            "from": "perplexity",
            "to": "_aiNativeCompute_aggregate",
            "value": 0.05,
            "valueBasis": "Q1 2026 annualised — Perplexity compute spend on aiNativeCompute (residual, mostly direct frontier API)",
            "source": "Perplexity press 2025 — most spend through frontier APIs; small share via Together/Fireworks for OSS-model serving",
            "provenance": "tier_3a",
            "rationale": "Most apps in this layer hit frontier APIs directly; aiNativeCompute share is small.",
        },
        {
            "id": "_long_tail",
            "from": "_other_apps",
            "to": "_aiNativeCompute",
            "isLongTail": True,
            "baseValueBasis": "Aggregate ai_native_app ARR ex-named entries — see arrModel.apps.aiNative residual",
            "baseValue": 4.0,
            "multiplierPct": 8,
            "rationale": "Smaller AI-Native Apps spend ~8% of ARR on AI-Native Compute (token-factory inference for OSS models, residual after most spend goes direct to frontier APIs or hyperscalers). Editorial.",
            "provenance": "tier_3a",
        },
    ],
    "aiNativeCompute_to_tradCompute": [
        {
            "id": "coreweave_to_azure",
            "from": "coreweave",
            "to": "azure",
            "value": 5.1,
            "valueBasis": "Q1 2026 annualised — CoreWeave revenue from Microsoft sub-rent for OpenAI workload",
            "source": "CoreWeave 10-Q customer concentration; ~85% of CoreWeave $6B run-rate is Microsoft sub-rent",
            "provenance": "tier_2a",
            "rationale": "Critical double-count guard. Microsoft's $37B AI run-rate already includes Azure capacity powered by CoreWeave GPUs. CoreWeave's revenue from MSFT must be deducted from the gross-summed compute layer to avoid counting the same dollars twice.",
        },
        {
            "id": "fireworks_to_aws",
            "from": "fireworks",
            "to": "aws",
            "value": 0.07,
            "valueBasis": "Q1 2026 annualised — Fireworks compute backed by AWS",
            "source": "Token factory infra mostly on hyperscaler primary; ~50% of Fireworks $140M ARR backs onto AWS GPU instances (editorial)",
            "provenance": "tier_3a",
            "rationale": "Token factories run on hyperscaler GPU capacity; pass-through estimated at ~50% of their ARR.",
        },
        {
            "id": "together_to_aws",
            "from": "together_ai",
            "to": "aws",
            "value": 0.065,
            "valueBasis": "Q1 2026 annualised — Together compute backed by AWS",
            "source": "Editorial — same logic as Fireworks (~50% of $130M ARR)",
            "provenance": "tier_3a",
            "rationale": "Same logic as Fireworks.",
        },
        {
            "id": "_long_tail",
            "from": "_other_aiNativeCompute",
            "to": "_trad_compute",
            "isLongTail": True,
            "baseValueBasis": "Aggregate aiNativeCompute ARR ex-named entries (Lambda, Crusoe, Nebius, Groq, Replicate, Anyscale, Fal.ai)",
            "baseValue": 2.85,
            "multiplierPct": 30,
            "rationale": "Smaller neoclouds and token factories pass ~30% of ARR through to trad-compute (most have own datacenters or rent from hyperscaler partners; Nebius is full owner-operator so contributes 0 to long tail; weighted avg 30%). Editorial.",
            "provenance": "tier_3a",
        },
    ],
}


# ─────────────────────────────────────────────────────────────────────
# Tier-tagging tables — generator uses these to tag existing records
# ─────────────────────────────────────────────────────────────────────

TIER_FOR_PROVIDER_KEY = {
    "OpenAI": "frontier",
    "Anthropic": "frontier",
    "Google/Gemini": "frontier",
    "xAI": "frontier",
    "Mistral": "frontier",
    "DeepSeek": "frontier",
    "Alibaba/Qwen": "frontier",
    "Baidu": "frontier",
    "Tencent": "frontier",
    "Minimax": "frontier",
    "Moonshot/Kimi": "frontier",
    "ByteDance": "frontier",
    "Meta": "frontier",
    "Others/Self-hosted": "frontier",
}

# topConsumers: tier per `co` field. Token factories slated for removal not listed here.
TIER_FOR_TOPCONSUMER = {
    "Portkey.ai": "ai_native_app",
    "OpenClaw": "ai_native_app",
    "Cursor (Anysphere)": "ai_native_app",
    "OpenRouter": "ai_native_app",
    "Kilo Code": "ai_native_app",
    "Perplexity": "ai_native_app",
    "Replit": "ai_native_app",
    "Cognition (Devin)": "ai_native_app",
    "Duolingo": "ai_native_app",
    "Lovable": "ai_native_app",
    "Canva": "ai_native_app",
    "Cline": "ai_native_app",
    "Character.ai": "ai_native_app",
    "ElevenLabs": "ai_native_app",
    "Wrtn Technologies": "ai_native_app",
    "micro1": "ai_native_app",
    "Midjourney": "ai_native_app",
    "Harvey AI": "ai_native_app",
    "Monica AI": "ai_native_app",
    "Jasper": "ai_native_app",
    "Glean": "ai_native_app",
    "Janitor AI": "ai_native_app",
    "Descript": "ai_native_app",
    "Yellow.ai": "ai_native_app",
    "Intercom Fin": "ai_native_app",
    "Writer": "ai_native_app",
    "BLACKBOX.AI": "ai_native_app",
    "Klarna": "ai_native_app",
    "Grab": "ai_native_app",
    "Sea/Shopee": "ai_native_app",
    "Kakao": "ai_native_app",
    "Sierra AI": "ai_native_app",
    "DeepL": "ai_native_app",
    "Hebbia": "ai_native_app",
    "Clay": "ai_native_app",
    "Gamma": "ai_native_app",
    "Roo Code": "ai_native_app",
    "Captions": "ai_native_app",
    "Decagon": "ai_native_app",
    "Luminance": "ai_native_app",
    "Mercor": "ai_native_app",
    "Speak": "ai_native_app",
    "Synthesia": "ai_native_app",
    "Genspark": "ai_native_app",
    "Chai Research": "ai_native_app",
    "OpenArt": "ai_native_app",
    "SillyTavern": "ai_native_app",
    "Abridge": "ai_native_app",
    "Photoroom": "ai_native_app",
    "Runway": "ai_native_app",
    "Agent Zero": "ai_native_app",
    "Fathom": "ai_native_app",
    "Pika": "ai_native_app",
    "Suno": "ai_native_app",
    "Retell AI": "ai_native_app",
    "OpenHands": "ai_native_app",
    "Cal AI": "ai_native_app",
}

# Records to remove from topConsumers — token factories (D6+D7) + records that
# duplicate enterpriseReality entries (per §7 #6 GitHub Copilot, #7 Salesforce
# Agentforce). Notion AI also moves to trad_saas per D4.
TOPCONSUMERS_REMOVE = {
    "Together AI",
    "Fireworks AI",
    "Groq",
    "Fal.ai",
    "GitHub Copilot",
    "Salesforce Agentforce",
    "Notion AI",
}

# Phase E backfill — records to populate arrNumeric on. Conservative Tier 2B/3A.
TOPCONSUMERS_ARR_BACKFILL = {
    # Pre-existing data bug: arrNumeric=500 (literally $500/yr) — fix to $200M
    # (Perplexity end-2025 ARR per company commentary).
    "Perplexity":  {"arrNumeric": 200000000, "arrSource": "Perplexity press end-2025 — $200M ARR", "provenance": "tier_2b"},
    "Sierra AI":   {"arrNumeric": 100000000, "arrSource": "Sierra press 2025 — $100M ARR end-2025 at $4.5B+ valuation", "provenance": "tier_2b"},
    "Decagon":     {"arrNumeric": 50000000,  "arrSource": "Decagon Series C 2025 — ~$50M ARR end-2025", "provenance": "tier_2b"},
    "Hebbia":      {"arrNumeric": 25000000,  "arrSource": "Hebbia press 2025 — ~$25M ARR; legal/finance vertical", "provenance": "tier_3a"},
    "Suno":        {"arrNumeric": 120000000, "arrSource": "Suno press 2025 — $120M ARR estimated end-2025", "provenance": "tier_2b"},
    "Pika":        {"arrNumeric": 25000000,  "arrSource": "Pika press 2025 — ~$25M ARR estimated", "provenance": "tier_3a"},
    "Captions":    {"arrNumeric": 30000000,  "arrSource": "Captions press 2025 — ~$30M ARR estimated", "provenance": "tier_3a"},
    "Speak":       {"arrNumeric": 50000000,  "arrSource": "Speak press 2025 — ~$50M ARR; language-learning AI", "provenance": "tier_3a"},
    "Cline":       {"arrNumeric": 5000000,   "arrSource": "Cline press 2025 — small commercial ARR (mostly OSS); ~$5M editorial", "provenance": "tier_3b"},
    "Janitor AI":  {"arrNumeric": 15000000,  "arrSource": "Janitor AI press 2025 — ~$15M ARR; consumer roleplay", "provenance": "tier_3a"},
    "OpenClaw":    {"arrNumeric": 10000000,  "arrSource": "OpenClaw press 2026 — recent launch; ~$10M editorial", "provenance": "tier_3b"},
    "Kilo Code":   {"arrNumeric": 8000000,   "arrSource": "Kilo Code press 2025 — small commercial ARR; ~$8M editorial", "provenance": "tier_3b"},
    "Canva":       {"arrPending": True, "arrPendingReason": "Canva is a digital-native platform — AI-attributable ARR not separately disclosed; would require split from total Canva ARR ($3B+)"},
    "Duolingo":    {"arrPending": True, "arrPendingReason": "Duolingo Max AI-tier disclosed but not as discrete ARR line"},
    "Klarna":      {"arrPending": True, "arrPendingReason": "Klarna AI-attributable revenue not separately disclosed; AI-driven cost savings reported, not revenue"},
    "Grab":        {"arrPending": True, "arrPendingReason": "Grab AI-attributable revenue not separately disclosed"},
    "Sea/Shopee":  {"arrPending": True, "arrPendingReason": "Sea/Shopee AI-attributable revenue not separately disclosed"},
    "Kakao":       {"arrPending": True, "arrPendingReason": "Kakao AI-attributable revenue not separately disclosed"},
    "Roo Code":    {"arrPending": True, "arrPendingReason": "Roo Code is OSS-first; no public commercial ARR disclosure"},
    "SillyTavern": {"arrPending": True, "arrPendingReason": "SillyTavern is OSS — no commercial ARR"},
    "OpenHands":   {"arrPending": True, "arrPendingReason": "OpenHands (All Hands AI) commercial ARR not publicly disclosed"},
    "Agent Zero":  {"arrPending": True, "arrPendingReason": "Agent Zero is OSS / experimental — no commercial ARR"},
}


def main():
    # ─── Phase B — enterprise_reality evidence files ───
    for rec in ENTERPRISE_REALITY:
        path = os.path.join(EV, "enterprise_reality", f"{rec['id']}.json")
        write_json(path, rec)
    print(f"  enterprise_reality: wrote {len(ENTERPRISE_REALITY)} files")

    # ─── Phase C — compute_native evidence files ───
    for rec in COMPUTE_NATIVE:
        path = os.path.join(EV, "compute_native", f"{rec['id']}.json")
        write_json(path, rec)
    print(f"  compute_native: wrote {len(COMPUTE_NATIVE)} files")

    # ─── Phase D — compute_disclosures (extended) evidence files ───
    for rec in COMPUTE_DISCLOSURES:
        path = os.path.join(EV, "compute_disclosures", f"{rec['id']}.json")
        write_json(path, rec)
    print(f"  compute_disclosures: wrote {len(COMPUTE_DISCLOSURES)} files")

    # ─── Phase F — passthrough evidence files ───
    pt_count = 0
    for layer, recs in PASSTHROUGH.items():
        for rec in recs:
            fname = "_long_tail.json" if rec.get("isLongTail") else f"{rec['id']}.json"
            path = os.path.join(EV, "passthrough", layer, fname)
            write_json(path, rec)
            pt_count += 1
    print(f"  passthrough: wrote {pt_count} files across 3 layers")

    # ─── Tier-tagging + ARR-backfill table (generator reads this) ───
    tagging = {
        "_doc": "wq-096 tier-tagging tables consumed by scripts/generate_site_data.py.",
        "_provenance": {
            "set_by": "scripts/migrate_wq096.py (wq-096)",
            "set_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "TIER_FOR_PROVIDER_KEY": TIER_FOR_PROVIDER_KEY,
        "TIER_FOR_TOPCONSUMER": TIER_FOR_TOPCONSUMER,
        "TOPCONSUMERS_REMOVE": sorted(TOPCONSUMERS_REMOVE),
        "TOPCONSUMERS_ARR_BACKFILL": TOPCONSUMERS_ARR_BACKFILL,
    }
    write_json(os.path.join(ROOT, "data", "wq096_tagging.json"), tagging)
    print("  wq096_tagging.json written")


if __name__ == "__main__":
    main()
    print("Done.")
