#!/usr/bin/env python3
"""wq-083 — curated source intake.

A focused, parallel intake path for editorial sources (newsletters, earnings
releases, analyst reports). Where the bulk pipeline (extract_claims.py +
monitor_sources.py) sweeps RSS/podcasts on a daily cron, this tool runs
single-source, on-demand: paste a URL or pipe text, get back a comparison
of what the source changes about the ledger's current position.

Workflow:
    1. Fetch / read source text (URL or stdin)
    2. Build a compressed summary of the ledger's current position
       (entities.json + metric-schema.json + site-data.json providers)
    3. Send both to Claude Opus with a comparison prompt
    4. Write a candidates-format JSON to data-updates/, plus update an
       index file so claims.html can discover and load curated files
    5. Print a CLI summary (matches / updates / conflicts / new / context)

Output is loaded by claims.html alongside daily candidates so the human
review gate stays consistent.

Run:
    cat zitron-may2026.txt | python3 scripts/curated_intake.py --slug zitron-may2026
    python3 scripts/curated_intake.py --url "https://..." --slug msft-q1-2026
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from coerce_date import coerce_or_keep  # noqa: E402
from log_run import logged_run  # noqa: E402
from score_materiality import score as score_materiality  # noqa: E402
from extract_claims import _extract_excerpt  # noqa: E402  (wq-041 helper)

ENTITIES_PATH = ROOT / "entities.json"
SCHEMA_PATH = ROOT / "metric-schema.json"
SITE_DATA_PATH = ROOT / "site-data.json"
OUTPUT_DIR = ROOT / "data-updates"
INDEX_PATH = OUTPUT_DIR / "curated-index.json"

DEFAULT_MODEL = "claude-opus-4-7"
# A single Opus call gets the whole source; chunk only if it overflows.
CHUNK_SIZE = 60_000
LEDGER_CONTEXT_TARGET = 20_000  # tokens, soft target per brief §4.2 (flow model)


SYSTEM_PROMPT = """You are a financial analyst maintaining The AI Ledger — a public dataset that models capital flows through the AI economy. You understand the ledger's flow model completely: how revenue flows from buyers through channels to providers, how capex flows from companies to infrastructure, and how all the numbers compose.

You will receive:
1. A source text (article, newsletter, earnings release, analyst report)
2. The ledger's FLOW MODEL — not just current values, but the structural relationships between them: revenue flow tree, capex flow tree, per-entity positions with provenance confidence, and explicit composition rules.

Your task: read the source and ask yourself — "What does each quantitative claim tell me about any node, edge, subtotal, or relationship in the flow model?" Use the composition rules to reason about claims that don't map 1:1 to a ledger field.

CLASSIFICATION — for each claim with a numeric value, classify as exactly one of:

"matches" — confirms an existing ledger value (within 5% tolerance). Direct map.
"updates" — supersedes an existing value (same entity + field, newer or more authoritative source). Flag the delta.
"conflicts" — contradicts an existing value by >10%. Flag both values.
"new" — entity or metric not currently in the flow model. Could expand the ledger.
"triangulates" — does NOT map directly to any single ledger field, but provides INDIRECT evidence about one or more positions through arithmetic. This is for claims that use a different measurement framework than the ledger (e.g. "Enterprise GenAI market = $37B" vs our segment splits) but can be connected through derivation.
"context" — qualitative, non-numeric, or numeric but with no traceable connection to the flow model. Useful colour, not actionable.

CRITICAL RULE FOR TRIANGULATION:
You MUST show the arithmetic. The derivation field must reference specific named nodes from the flow model (e.g. "market.2025.total_segment_enterprise", "sankey.providers.openai", "capex.mag7.microsoft") and write the equation that connects the source's number to those nodes. If you cannot write a specific equation tracing back to named nodes, classify as "context" instead. This prevents hallucinated connections.

SCOPE — the flow model tracks:
- Revenue: who pays (Consumer/SME/Enterprise/VC), through what channel (Subs/API/Hyperscaler/Apps/SaaS), to which provider (OpenAI/Anthropic/Google/IaaS/Other), and where it goes (Inference/People/Cash flow)
- Capital: who spends (Mag-7/Neoclouds/Sovereign/Enterprise direct), how much, on what (NVIDIA GPUs/Other silicon/Networking/DC costs/Power)
- Per-entity: ARR, capex, valuation, total_funding, employees, tokens/day, growth rates, operating_loss

DO NOT extract: model benchmark scores (unless tied to revenue impact), vague market commentary, biographical facts, non-AI business metrics, anything without a specific numeric value.

PRIORITY — when a source contains many claims, prioritise:
1. Anything that triangulates against a LOW-CONFIDENCE position in the flow model (entries flagged "low" or "single-source" in the entity positions section)
2. Capex and revenue claims (the ledger's core value proposition)
3. Claims that conflict with existing positions (most actionable)
4. New entities or fields that would expand coverage
5. Matches that strengthen provenance on existing positions

Fewer high-quality claims with clear reasoning beat many noisy ones. A good triangulation with clean arithmetic is MORE valuable than a direct match.

For each claim, output a JSON object with these fields:
- "claim": verbatim or lightly paraphrased quote (1-2 sentences)
- "category": one of: provider_revenue | token_volume | pricing | gpu_infrastructure | enterprise_adoption | skeptical_bear_case | valuation_funding
- "entity": company, product, or aggregate label (e.g. "Enterprise GenAI Market")
- "metric": what is being measured (e.g. "ARR", "tokens/day", "capex", "enterprise_revenue")
- "value": numeric value as a number, or null if unclear
- "unit": unit of value (e.g. "USD_B", "USD_T_per_day", "GPUs", "pct")
- "value_display": human-readable value string (e.g. "$16.8B", "15M seats", "42%")
- "time_period": when this applies (e.g. "Q1 2026", "2025", "as of March 2026")
- "time_period_scope": one of: "annual" | "h1" | "h2" | "q1" | "q2" | "q3" | "q4" | "exit_snapshot" | "monthly_peak" | "point_in_time"
- "period_qualifier_detected": short string quoting the qualifier you matched, or null when scope=annual with no qualifier

  TIME PERIOD SCOPE — RULES (wq-054):

  Rule A — INTERNAL CONSISTENCY:
  If you populate period_qualifier_detected with a non-null value, time_period_scope MUST be the corresponding scope from the qualifier — NOT point_in_time:
    - Qualifier mentions "Q1/Q2/Q3/Q4" → scope must be q1/q2/q3/q4
    - Qualifier mentions "H1/H2/first half/second half" → scope must be h1/h2
    - Qualifier mentions "exit/end of year/year-end run-rate" → scope must be exit_snapshot
    - Qualifier mentions "monthly/per month/$X/month" → scope must be monthly_peak

  Rule B — point_in_time BOUNDARY:
  point_in_time is reserved for ENTITY-CURRENT state metrics: WAU, headcount, current model version, current ARR run-rate WHEN explicitly described as "as of today / now / current".
  point_in_time is NOT for funding rounds, valuations, or annual revenue figures — those are scope=annual.

  Rule C — DEFAULT:
  No period qualifier in source → scope=annual, period_qualifier_detected=null.

- "confidence": "high" | "medium" | "low"
- "speaker": author/source name, or null
- "weight": exactly one of:
    "authoritative" — source has direct first-hand knowledge (e.g. Microsoft IR page on Microsoft capex)
    "corroborating" — source cites a specific named primary source (earnings call, official filing, named report)
    "indicative" — market colour, repeated figures, estimates
- "comparison_type": one of: matches | updates | conflicts | new | triangulates | context
- "existing_value": the ledger's current value for this entity+metric, or null if not tracked / not directly mappable
- "delta_pct": signed percentage change from existing value (e.g. 0.20 for +20%), or null
- "comparison_note": 1-line explanation of the comparison result

ADDITIONAL FIELD — for comparison_type="triangulates" ONLY (omit otherwise, or set to null):
- "triangulation": object with these fields:
    - "target_nodes": array of strings naming the ledger nodes this claim triangulates against. Use dotted paths from the flow model (e.g. ["market.2025.total_segment_enterprise", "market.2025.total_segment_sme"], ["sankey.providers.openai", "sankey.providers.anthropic"], ["capex.mag7.microsoft", "capex.bucket_totals.mag7"]).
    - "derivation": the arithmetic showing how the source claim maps to those nodes. Format: "Source says X = $Y. In our model, X ≈ Node_A ($A) + Node_B ($B) = $C. Delta: $D / +Z%. [optional scope-difference explanation.]" The equation MUST be specific.
    - "implied_value": what the source implies our ledger node should be, if the derivation is clean. Number, or null when the source spans multiple nodes and a single implied value isn't meaningful.
    - "confidence_impact": one of "strengthens" | "weakens" | "widens_range" — what this triangulation does to confidence in the target node(s).

Rules:
- Only extract claims with a specific entity + metric + numeric value. Skip vague statements.
- A source describing its OWN financials (e.g. Microsoft IR page on Microsoft capex) is weight "authoritative".
- A source quoting another source ("per The Information, OpenAI ARR is $19.5B") is weight "corroborating".
- An analyst's estimate or commentary is weight "indicative".
- For matches/updates/conflicts, populate existing_value and delta_pct from the flow model context you were given.
- For triangulates, the triangulation.derivation field is MANDATORY. No equation → reclassify as context.
- Return a JSON array of claim objects, or [] if no relevant claims found.
- Return ONLY the JSON array, no other text."""


# ─────────────────────────── HTML / source fetching ────────────────────────

class _TextExtractor(HTMLParser):
    """Cheap article text extractor — strips script/style, keeps paragraph
    structure. We avoid trafilatura/readability to keep the dep footprint
    minimal; this is good enough for newsletters, earnings pages, and most
    article HTML. Heavy/SPA pages may need a follow-up tool."""

    SKIP_TAGS = {"script", "style", "noscript", "svg", "header", "footer",
                 "nav", "aside", "form", "button"}
    BLOCK_TAGS = {"p", "div", "section", "article", "li", "h1", "h2", "h3",
                  "h4", "h5", "h6", "br", "tr", "td", "th"}

    def __init__(self):
        super().__init__()
        self._skip_depth = 0
        self._chunks = []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP_TAGS:
            self._skip_depth += 1
        elif tag in self.BLOCK_TAGS and self._skip_depth == 0:
            self._chunks.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP_TAGS:
            self._skip_depth = max(0, self._skip_depth - 1)
        elif tag in self.BLOCK_TAGS and self._skip_depth == 0:
            self._chunks.append("\n")

    def handle_data(self, data):
        if self._skip_depth == 0 and data.strip():
            self._chunks.append(data)

    def text(self):
        out = "".join(self._chunks)
        out = re.sub(r"[ \t]+", " ", out)
        out = re.sub(r"\n[ \t]+", "\n", out)
        out = re.sub(r"\n{3,}", "\n\n", out)
        return out.strip()


def fetch_url(url: str) -> str:
    """Fetch a URL and return readable text."""
    import requests
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36 AILedger/curated-intake"
        )
    }
    resp = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
    resp.raise_for_status()
    ctype = (resp.headers.get("content-type") or "").lower()
    if "html" in ctype or url.endswith((".html", ".htm")) or "<html" in resp.text[:500].lower():
        parser = _TextExtractor()
        parser.feed(resp.text)
        return parser.text()
    return resp.text


def fetch_source(url: str | None, use_stdin: bool) -> tuple[str, str | None]:
    """Resolve source text. Returns (text, url)."""
    if use_stdin:
        text = sys.stdin.read()
        if not text.strip():
            print("❌ stdin was empty.", file=sys.stderr)
            sys.exit(1)
        return text, url
    if url:
        print(f"  🌐 Fetching {url}")
        text = fetch_url(url)
        return text, url
    print("❌ Provide --url or pipe text to stdin.", file=sys.stderr)
    sys.exit(1)


# ─────────────────────────── flow model builder ────────────────────────────
#
# wq-083 v2: the model needs more than a flat list of values. It needs the
# *structure* — how revenue flows from buyers through channels to providers,
# how capex composes by spender category, and what the arithmetic identities
# are between them. With that structural context, claims that don't map 1:1
# to a ledger field can still be triangulated through equations.

# Per-entity fields surfaced in the entity positions block.
_CURRENT_FIELDS = (
    "arr", "tokens_per_day", "valuation", "user_count", "subscriber_count",
    "growth_rate", "consumer_pct", "biz_pct", "model_count", "employee_count",
)
_FINANCIAL_FIELDS = (
    "arr", "collected_revenue", "operating_loss", "inference_cost",
    "capex", "capex_ai", "data_center_capex", "total_funding",
    "valuation", "exit_arr", "h1_arr", "q4_arr", "monthly_peak_arr",
    "employees", "employee_count", "gpu_count", "tokens_per_day",
    "market_share_pct", "subscription_revenue", "cash_burn",
)


# These are structural truths about the ledger, not data. Hardcoded so the
# model has explicit equations to reach for when reasoning about claims that
# use a different framework than our schema.
COMPOSITION_RULES = """COMPOSITION RULES — how ledger numbers relate (use these for triangulation arithmetic):

Revenue identities:
- Customer Revenue (gross) = Consumer + SME + Enterprise (buyer segments)
- Customer Revenue (net / provider-received) = gross minus channel margins (Hyperscaler ~20%, Trad. SaaS ~60%)
- Total System Inflow = Customer Revenue (net) + VC Subsidy
- Per-provider revenue = sum of all channel flows routing to that provider (see routing block)
- VC Subsidy ≈ operating loss covered by funding (NOT equal to total_funding)

Capex identities:
- Total Capex = Mag-7 + Neoclouds + Sovereign + Enterprise direct
- Individual company capex figures are TOTAL company capex (includes non-AI); AI-share estimated
- Infra-to-Revenue ratio = Total Capex / Customer Revenue (gross)

Cross-model relationships (use when a source uses different terminology):
- "Enterprise GenAI market" / "Enterprise AI" (analysts) ≈ Enterprise + SME segments in our model (sometimes + portion of Trad. SaaS AI features)
- "AI infrastructure market" (analysts) overlaps BOTH capex AND Hyperscaler channel revenue — partial overlap
- "Foundation model revenue" / "Foundation model TAM" (analysts) ≈ sum of provider ARR (sankey.providers)
- "Inference market" (analysts) ≈ Model API channel + portion of Hyperscaler channel
- "AI application revenue" (analysts) ≈ AI Native Apps channel + Trad. SaaS channel
- Company-reported "AI revenue" typically includes BOTH direct model revenue AND AI-feature upsell

Segment mapping notes:
- Our "Consumer" = ChatGPT Plus/Pro, Claude Pro, Gemini Advanced, etc.
- Our "SME" = small team subscriptions, individual API developers
- Our "Enterprise" = large contracts, custom deployments, committed spend
- External "B2B" typically = our Enterprise + SME + portions of Trad. SaaS
- External "B2C" typically = our Consumer only

Channel routing (per-provider revenue split for 2025) is shown explicitly in the revenue flow block — use those numbers when the source talks about a specific provider's channel mix.
"""


def _format_value(v) -> str | None:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        # Avoid implying false precision; entities.json stores arr/capex in $B.
        if isinstance(v, float) and not v.is_integer():
            return f"{v:g}"
        return str(int(v) if isinstance(v, float) else v)
    if isinstance(v, str):
        return v
    return None


def _fmt_dollars(v, suffix="B") -> str:
    """Format a $-value to 1 dp where useful, no decimals where integer."""
    if v is None:
        return "—"
    try:
        f = float(v)
    except (TypeError, ValueError):
        return str(v)
    if abs(f) >= 100:
        return f"${f:,.0f}{suffix}"
    return f"${f:,.1f}{suffix}"


def _provenance_confidence(entity: dict, prov_key: str) -> str:
    """Return 'high' | 'medium' | 'low' | 'unsourced' for a given prov key.

    Used to flag low-confidence positions to the model — these are the
    triangulation targets where indirect evidence helps most. Tier follows
    apply_decisions.WEIGHT_RANK and claim count: ≥2 corroborating/authoritative
    claims = high; 1 corroborating/authoritative or ≥2 indicative = medium;
    1 indicative = low; nothing = unsourced.

    For 'current.X' keys with no direct provenance, fall back to the most
    recent year's provenance for the same field — current values are usually
    propagated from a year's data without a separate provenance record.
    """
    prov_block = entity.get("provenance") or {}
    prov = prov_block.get(prov_key)
    if not prov or not prov.get("claims"):
        # Fall back: for current.X, look at the most recent year's
        # provenance for the same field (X).
        if prov_key.startswith("current."):
            field = prov_key.split(".", 1)[1]
            year_keys = [k for k in prov_block.keys()
                         if re.match(r"^\d{4}\." + re.escape(field) + r"$", k)]
            if year_keys:
                year_keys.sort(reverse=True)
                prov = prov_block.get(year_keys[0])
        if not prov or not prov.get("claims"):
            return "unsourced"
    weights = [(c.get("weight") or "indicative") for c in prov["claims"]]
    n = len(weights)
    strong = sum(1 for w in weights if w in ("authoritative", "corroborating"))
    if strong >= 2:
        return "high"
    if strong == 1 or n >= 2:
        return "medium"
    return "low"


def build_revenue_flow(sankey: dict) -> str:
    """Section A — revenue flow tree. Mirrors the sankey shape so the model
    can refer to nodes by name when triangulating."""
    if not sankey:
        return "REVENUE FLOW MODEL: (sankey not loaded)"

    lines = ["A. REVENUE FLOW MODEL (2025 collected, all values $B):"]
    total_system = sankey.get("totalSystem") or 0
    cust_net = sankey.get("totalCustomerRevenue") or 0
    cust_gross = sankey.get("totalCustomerRevenue_gross") or 0
    vc = sankey.get("totalVCSubsidy") or 0

    lines.append(f"  Total System Inflow: {_fmt_dollars(total_system)}")
    lines.append(f"  ├── Customer Revenue (net to providers): {_fmt_dollars(cust_net)}")
    lines.append(f"  │   Customer Revenue (gross from buyers): {_fmt_dollars(cust_gross)}")

    # Buyers (excluding the VC bucket — surfaced separately for clarity).
    buyers = [b for b in (sankey.get("buyers") or [])
              if (b.get("label") or "").lower() not in ("vc/investors", "vc", "vc subsidy")]
    if buyers:
        lines.append("  │   Buyer segments (gross):")
        for b in buyers:
            lines.append(f"  │   ├── {b.get('label')}: {_fmt_dollars(b.get('value'))}  (sankey.buyers.{b.get('label')})")

    channels = sankey.get("channels") or []
    if channels:
        lines.append("  │   Channels (where buyer revenue lands):")
        for ch in channels:
            lines.append(f"  │   ├── {ch.get('label')}: {_fmt_dollars(ch.get('value'))}  (sankey.channels.{ch.get('label')})")

    providers = sankey.get("providers") or []
    routing = sankey.get("routing") or {}
    if providers:
        lines.append("  │   Providers receiving revenue:")
        for p in providers:
            slug = p.get("slug", "?")
            row = f"  │   ├── {p.get('label')}: {_fmt_dollars(p.get('value'))}  (sankey.providers.{slug})"
            channel_split = routing.get(slug) or {}
            if channel_split:
                bits = ", ".join(f"{c}={_fmt_dollars(v)}" for c, v in channel_split.items())
                row += f"\n  │   │     channel split: {bits}"
            lines.append(row)

    outcomes = sankey.get("outcomes") or []
    if outcomes:
        lines.append("  │   Where provider revenue goes (outcomes):")
        for o in outcomes:
            lines.append(f"  │   ├── {o.get('label')}: {_fmt_dollars(o.get('value'))}  (sankey.outcomes.{o.get('label')})")

    lines.append(f"  └── VC Subsidy: {_fmt_dollars(vc)}  (sankey.totalVCSubsidy)")

    return "\n".join(lines)


def build_capex_flow(market: dict, capital_sankey: dict) -> str:
    """Section B — capex flow tree (cumulative + 2025 breakdown)."""
    lines = ["B. CAPEX FLOW MODEL (cumulative 2023-2025, all values $B):"]
    if not market and not capital_sankey:
        lines.append("  (capex data not loaded)")
        return "\n".join(lines)

    # Yearly headline
    years = sorted([y for y in (market or {}).keys() if re.match(r"^\d{4}$", str(y))])
    yearly = []
    for y in years:
        yblock = market[y] or {}
        tot = yblock.get("total_capex")
        yoy = yblock.get("yoy_total_capex_growth_pct")
        if tot is not None:
            piece = f"{y}: {_fmt_dollars(tot)}"
            if yoy is not None:
                piece += f" ({yoy:+.1f}% YoY)"
            yearly.append(piece)
    if yearly:
        lines.append("  " + " │ ".join(yearly))

    # Cumulative
    if capital_sankey and capital_sankey.get("total"):
        lines.append(f"  Cumulative 2023-2025: {_fmt_dollars(capital_sankey['total'])}  (capex.total_cumulative)")

    # 2025 by spender category
    m25 = (market or {}).get("2025") or {}
    if m25:
        lines.append(f"  2025 breakdown by spender category (market.2025):")
        for label, key in (("Mag-7 Hyperscalers", "mag7_capex"),
                           ("Neoclouds", "neocloud_capex"),
                           ("Sovereign / Gov", "sovereign_capex"),
                           ("Enterprise direct", "enterprise_capex")):
            v = m25.get(key)
            if v is not None:
                lines.append(f"    ├── {label}: {_fmt_dollars(v)}  (market.2025.{key})")

    # Per-company capex from capital_sankey.sources
    sources = (capital_sankey or {}).get("sources") or {}
    if sources:
        lines.append("  Per-company capex (cumulative, capex.sources.*):")
        for label, value in sorted(sources.items(), key=lambda kv: -float(kv[1] or 0)):
            slug = re.sub(r"\s+capex$", "", label, flags=re.I).strip().lower().replace(" ", "_")
            lines.append(f"    ├── {label}: {_fmt_dollars(value)}  (capex.sources.{slug})")

    # Where capex flows (destinations) and bucket totals
    bucket_totals = (capital_sankey or {}).get("bucket_totals") or {}
    if bucket_totals:
        bits = ", ".join(f"{k}={_fmt_dollars(v)}" for k, v in bucket_totals.items())
        lines.append(f"  Bucket totals (cumulative): {bits}  (capex.bucket_totals.*)")

    destinations = (capital_sankey or {}).get("destinations") or {}
    if destinations:
        lines.append("  Capex destinations (cumulative, where the money buys things):")
        for label, value in sorted(destinations.items(), key=lambda kv: -float(kv[1] or 0)):
            slug = label.lower().replace(" ", "_").replace("/", "_").replace("&", "and")
            lines.append(f"    ├── {label}: {_fmt_dollars(value)}  (capex.destinations.{slug})")

    util = (capital_sankey or {}).get("utilization") or {}
    if util:
        lines.append("  Utilisation of installed compute:")
        for label, value in util.items():
            lines.append(f"    ├── {label}: {_fmt_dollars(value)}  (capex.utilization.{label})")

    # Headline ratio
    ratio = m25.get("infra_to_revenue_ratio")
    if ratio is not None:
        lines.append(f"  Key ratio: Infra-to-Revenue (2025) = {ratio:.1f}x  (market.2025.infra_to_revenue_ratio)")

    # Token volume
    if m25.get("tokens_per_day_total") is not None:
        lines.append(f"  Token volume (2025): {m25['tokens_per_day_total']:.1f}T tokens/day  (market.2025.tokens_per_day_total)")

    return "\n".join(lines)


def _entity_position_lines(entity: dict, schema_field_map: dict) -> list[str]:
    """One block of plain-text summary for a single entity, with a confidence
    tag per field. Skips entities with no values."""
    slug = entity.get("slug", "?")
    name = entity.get("name", slug)
    roles = entity.get("roles") or []
    role_str = ",".join(roles) if roles else "—"

    out = []
    current = entity.get("current") or {}
    for f in _CURRENT_FIELDS:
        v = _format_value(current.get(f))
        if v is None:
            continue
        conf = _provenance_confidence(entity, f"current.{f}")
        flag = " ⚠ low_confidence" if conf in ("low", "unsourced") else ""
        out.append(f"    current.{f}={v} [{conf}]{flag}")

    financials = entity.get("financials") or {}
    years = sorted(
        (y for y in financials.keys() if re.match(r"^\d{4}$", str(y))),
        reverse=True,
    )[:2]  # most recent 2 years per entity to keep token budget bounded
    for year in years:
        year_block = financials.get(year) or {}
        for f in _FINANCIAL_FIELDS:
            v = _format_value(year_block.get(f))
            if v is None:
                continue
            conf = _provenance_confidence(entity, f"{year}.{f}")
            flag = " ⚠ low_confidence" if conf in ("low", "unsourced") else ""
            out.append(f"    {year}.{f}={v} [{conf}]{flag}")

    if not out:
        return []
    return [f"  ## {slug} ({name}) [{role_str}]"] + out


def build_entity_positions(entities: dict, schema: dict) -> str:
    """Section C — per-entity positions with provenance confidence tags."""
    schema_field_map = {f.get("field"): f for f in (schema.get("field_match_rules") or []) if f.get("field")}
    lines = ["C. PER-ENTITY POSITIONS (with provenance confidence tier; ⚠ flags low-confidence triangulation targets):"]
    companies = sorted(entities.get("companies", []), key=lambda c: c.get("slug", ""))
    rendered = 0
    for entity in companies:
        block = _entity_position_lines(entity, schema_field_map)
        if block:
            lines.extend(block)
            rendered += 1
    return "\n".join(lines), rendered


def build_flow_model() -> tuple[str, dict]:
    """Build the structural flow-model context. Returns (text, meta).

    The flow model has four sections — revenue flow, capex flow, per-entity
    positions with provenance confidence, and the composition rules. Together
    these let the model reason about claims that don't map 1:1 to a ledger
    field by writing the equation that connects them.
    """
    with open(ENTITIES_PATH) as f:
        entities = json.load(f)
    with open(SCHEMA_PATH) as f:
        schema = json.load(f)
    with open(SITE_DATA_PATH) as f:
        site_data = json.load(f)

    revenue_flow = build_revenue_flow(site_data.get("sankey") or {})
    capex_flow = build_capex_flow(site_data.get("market") or {},
                                  site_data.get("capital_sankey") or {})
    entity_positions, n_entities = build_entity_positions(entities, schema)

    text = "\n\n".join([revenue_flow, capex_flow, entity_positions, COMPOSITION_RULES])
    est_tokens = len(text) // 4
    meta = {
        "ledger_context_chars": len(text),
        "ledger_context_tokens_est": est_tokens,
        "entities_in_summary": n_entities,
    }
    return text, meta


# Back-compat alias for callers / tests that imported the v1 name.
build_ledger_summary = build_flow_model


# ─────────────────────────── Opus comparison call ──────────────────────────

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list[str]:
    if len(text) <= chunk_size:
        return [text]
    out = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        if end < len(text):
            boundary = text.rfind("\n\n", start, end)
            if boundary > start + chunk_size // 2:
                end = boundary
        out.append(text[start:end])
        start = end - 500  # overlap to catch cross-chunk claims
    return out


def _parse_claims_json(raw: str, stop_reason: str | None = None) -> list[dict]:
    """Parse a model JSON response, recovering from common edge cases.

    The model occasionally returns truncated output (when it hits max_tokens
    on a long source) or stray trailing commas. We try a strict parse first,
    then fall back to: trailing-comma cleanup, then a salvage that finds the
    last complete claim object boundary and parses up to there. Better to
    return a partial list than drop the whole chunk."""
    raw = raw.strip()
    if not raw:
        return []
    # Strip trailing commas before ] or }
    cleaned = re.sub(r",(\s*[\]}])", r"\1", raw)
    try:
        data = json.loads(cleaned)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        pass

    # Salvage: find the last "}," or "}\n" inside the array and close after it.
    if cleaned.startswith("["):
        # Walk through and track brace depth at top level (depth 1 = inside array)
        depth = 0
        in_str = False
        esc = False
        last_complete = -1
        for idx, ch in enumerate(cleaned):
            if esc:
                esc = False
                continue
            if ch == "\\" and in_str:
                esc = True
                continue
            if ch == '"':
                in_str = not in_str
                continue
            if in_str:
                continue
            if ch in "[{":
                depth += 1
            elif ch in "]}":
                depth -= 1
                if depth == 1 and ch == "}":
                    last_complete = idx
        if last_complete > 0:
            salvaged = cleaned[: last_complete + 1] + "]"
            try:
                data = json.loads(salvaged)
                if isinstance(data, list):
                    print(f"\n  ⚠ JSON salvaged {len(data)} claim(s) "
                          f"(stop_reason={stop_reason}, output likely truncated)")
                    return data
            except json.JSONDecodeError:
                pass

    # Re-raise the original error so the caller can log fully.
    json.loads(cleaned)
    return []


def call_opus(client, model: str, ledger_summary: str, source_text: str,
              source_url: str | None) -> list[dict]:
    """Run the comparison prompt over the source. Chunks if needed; dedups
    across chunks by claim text."""
    chunks = chunk_text(source_text)
    all_claims: list[dict] = []
    seen_keys: set[tuple] = set()

    for i, chunk in enumerate(chunks):
        if len(chunks) > 1:
            print(f"  Chunk {i+1}/{len(chunks)}...", end=" ", flush=True)

        user_msg = (
            "## Ledger current position\n\n"
            f"{ledger_summary}\n\n"
            "---\n\n"
            "## Source text\n\n"
            + (f"URL: {source_url}\n\n" if source_url else "")
            + chunk
            + "\n\n---\n\nReturn the JSON array of claims now."
        )

        try:
            response = client.messages.create(
                model=model,
                max_tokens=16384,  # v2 outputs can be longer (triangulation block adds ~150 tokens/claim)
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_msg}],
            )
            raw = response.content[0].text.strip()
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
            stop_reason = getattr(response, "stop_reason", None)
            claims = _parse_claims_json(raw, stop_reason)
            if not isinstance(claims, list):
                claims = []
        except json.JSONDecodeError as e:
            print(f"\n  ⚠ JSON parse error in chunk {i+1}: {e}")
            print(f"     stop_reason={stop_reason!r} raw_len={len(raw)}")
            print(f"     Raw head: {raw[:300]}")
            print(f"     Raw tail: {raw[-300:]}")
            continue
        except Exception as e:
            print(f"\n  ⚠ API error in chunk {i+1}: {e}")
            continue

        # Attach source excerpt + dedup across chunks.
        for claim in claims:
            key = (
                (claim.get("entity") or "").lower().strip(),
                (claim.get("metric") or "").lower().strip(),
                claim.get("value"),
                (claim.get("time_period") or "").lower().strip(),
            )
            if key in seen_keys:
                continue
            seen_keys.add(key)
            claim["source_excerpt"] = _extract_excerpt(chunk, claim)
            all_claims.append(claim)

        if len(chunks) > 1:
            print(f"{len(claims)} claim(s)")

    return all_claims


# ─────────────────────────── output / formatting ───────────────────────────

# Map the comparison_type taxonomy to dedup_status so the existing claims.html
# rendering (badges, filters, conflict highlighting) keeps working without a
# parallel code path. updates+conflicts both flag — reviewer should look.
# triangulates gets its own dedup_status so the review UI can render the
# derivation block; claims.html knows about this status (wq-083 v2).
_COMPARISON_TO_DEDUP = {
    "matches": "confirms",
    "updates": "conflicts",
    "conflicts": "conflicts",
    "new": "new",
    "triangulates": "triangulates",
    "context": "new",
}


def enrich_claim(claim: dict, source_url: str | None, slug: str,
                 today: str, generated_at: str, entities: dict,
                 schema: dict) -> dict:
    """Stamp source metadata, materiality score, and dedup_status onto a
    raw model claim. Mirrors what extract_claims.py does at write time so
    the review UI sees consistent fields."""
    comparison_type = claim.get("comparison_type") or "context"

    # Arithmetic constraint enforcement (brief §3 #3 — wq-083 v2):
    # if the model returned triangulates without a derivation, the claim is
    # not actionable as a triangulation — downgrade to context per the brief.
    if comparison_type == "triangulates":
        triangulation = claim.get("triangulation") or {}
        derivation = (triangulation.get("derivation") or "").strip()
        if not derivation:
            claim["comparison_type"] = "context"
            claim["comparison_note"] = (
                (claim.get("comparison_note") or "")
                + " [Reclassified to context: triangulates requires derivation arithmetic.]"
            ).strip()
            comparison_type = "context"

    claim["dedup_status"] = _COMPARISON_TO_DEDUP.get(comparison_type, "new")
    if claim.get("comparison_note"):
        claim["dedup_note"] = claim["comparison_note"]

    claim["source_type"] = "curated_intake"
    claim["source_url"] = source_url or ""
    claim["source_slug"] = slug
    claim["source_title"] = f"Curated intake — {slug}"
    claim["extracted_at"] = generated_at

    # Materiality — score against entities + schema so claims.html lane
    # filtering works for curated claims too. Build the minimal item shape
    # score_materiality() expects (mirrors extract_claims write-time path).
    item_for_scoring = {
        "claim": claim.get("claim", ""),
        "entity": claim.get("entity", ""),
        "tags": [claim.get("category", "")],
        "metricKey": claim.get("metric") or "",
        "value": claim.get("value"),
        "unit": claim.get("unit") or "",
        "dateAdded": today,
        "dateOfClaim": coerce_or_keep(
            claim.get("time_period") or today, today
        ),
        "weight": claim.get("weight", "indicative"),
    }
    try:
        claim["materiality"] = score_materiality(
            item_for_scoring, entities, schema
        )
    except Exception:
        # Best-effort: a scoring failure should not drop the claim.
        pass

    return claim


def write_output(slug: str, source_url: str | None, source_text: str,
                 ledger_meta: dict, model: str, claims: list[dict],
                 today: str, generated_at: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    summary = {
        "matches": sum(1 for c in claims if c.get("comparison_type") == "matches"),
        "updates": sum(1 for c in claims if c.get("comparison_type") == "updates"),
        "conflicts": sum(1 for c in claims if c.get("comparison_type") == "conflicts"),
        "new": sum(1 for c in claims if c.get("comparison_type") == "new"),
        "triangulates": sum(1 for c in claims if c.get("comparison_type") == "triangulates"),
        "context": sum(1 for c in claims if c.get("comparison_type") == "context"),
    }

    payload = {
        "source": "curated_intake",
        "slug": slug,
        "generated_at": generated_at,
        "model": model,
        "source_url": source_url,
        "source_text_chars": len(source_text),
        "flow_model_tokens": ledger_meta.get("ledger_context_tokens_est", 0),
        "ledger_context_tokens": ledger_meta.get("ledger_context_tokens_est", 0),  # back-compat alias
        "ledger_entities_in_summary": ledger_meta.get("entities_in_summary", 0),
        "summary": summary,
        "claims": claims,
    }

    out_path = OUTPUT_DIR / f"{today}-curated-{slug}.json"
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)

    # Maintain a small index claims.html can fetch to discover curated files
    # without doing directory listing (which a static page can't do anyway).
    update_index(out_path.name, slug, today, generated_at, summary, source_url)

    return out_path


def update_index(filename: str, slug: str, date: str, generated_at: str,
                 summary: dict, source_url: str | None) -> None:
    """Append/update an entry in data-updates/curated-index.json."""
    if INDEX_PATH.exists():
        with open(INDEX_PATH) as f:
            index = json.load(f)
    else:
        index = {"files": []}

    entry = {
        "file": filename,
        "slug": slug,
        "date": date,
        "generated_at": generated_at,
        "summary": summary,
        "source_url": source_url,
    }
    # Replace existing entry for the same filename, else append.
    files = [e for e in index.get("files", []) if e.get("file") != filename]
    files.append(entry)
    files.sort(key=lambda e: (e.get("date", ""), e.get("generated_at", "")),
               reverse=True)
    index["files"] = files
    with open(INDEX_PATH, "w") as f:
        json.dump(index, f, indent=2)


def print_summary(slug: str, source_text: str, ledger_meta: dict,
                  claims: list[dict], out_path: Path) -> None:
    summary = {
        "matches":      [c for c in claims if c.get("comparison_type") == "matches"],
        "updates":      [c for c in claims if c.get("comparison_type") == "updates"],
        "conflicts":    [c for c in claims if c.get("comparison_type") == "conflicts"],
        "new":          [c for c in claims if c.get("comparison_type") == "new"],
        "triangulates": [c for c in claims if c.get("comparison_type") == "triangulates"],
        "context":      [c for c in claims if c.get("comparison_type") == "context"],
    }

    print()
    print(f"── Curated intake: {slug} " + "─" * max(0, 40 - len(slug)))
    print(f"Source: {len(source_text):,} chars │ "
          f"Flow model context: ~{ledger_meta.get('ledger_context_tokens_est', 0):,} tokens "
          f"({ledger_meta.get('entities_in_summary', 0)} entities)")
    print()

    def _line(c):
        ent = c.get("entity") or "?"
        met = c.get("metric") or "?"
        val_disp = c.get("value_display") or c.get("value") or "?"
        period = c.get("time_period") or ""
        return f"     {ent} {met}: {val_disp}" + (f" ({period})" if period else "")

    print(f"Matches ({len(summary['matches'])}):       "
          "confirm existing ledger values")
    for c in summary["matches"][:5]:
        print(_line(c))

    print(f"Updates ({len(summary['updates'])}):       "
          "supersede existing values")
    for c in summary["updates"]:
        ent, met = c.get("entity") or "?", c.get("metric") or "?"
        ev = c.get("existing_value")
        nv = c.get("value_display") or c.get("value")
        delta = c.get("delta_pct")
        delta_str = f"{delta:+.1%}" if isinstance(delta, (int, float)) else "?"
        ev_str = f"${ev}B" if isinstance(ev, (int, float)) else str(ev)
        print(f"     ⚠ {ent} {met}: {ev_str} → {nv} ({delta_str})")

    print(f"Conflicts ({len(summary['conflicts'])}):     "
          "contradict existing values")
    for c in summary["conflicts"]:
        ent, met = c.get("entity") or "?", c.get("metric") or "?"
        ev = c.get("existing_value")
        nv = c.get("value_display") or c.get("value")
        delta = c.get("delta_pct")
        delta_str = f"{delta:+.1%}" if isinstance(delta, (int, float)) else "?"
        ev_str = f"${ev}B" if isinstance(ev, (int, float)) else str(ev)
        print(f"     ✗ {ent} {met}: {ev_str} (ledger) vs {nv} (source, {delta_str})")

    # Triangulations — the v2 headline. Show the derivation inline so the
    # arithmetic is visible at a glance, before the reviewer opens claims.html.
    print(f"Triangulates ({len(summary['triangulates'])}): "
          "indirect evidence against ledger positions (derivation included)")
    for c in summary["triangulates"]:
        ent = c.get("entity") or "?"
        nv = c.get("value_display") or c.get("value") or "?"
        tri = c.get("triangulation") or {}
        targets = tri.get("target_nodes") or []
        targets_str = ", ".join(targets[:3]) + (" …" if len(targets) > 3 else "")
        impact = tri.get("confidence_impact") or "?"
        derivation = (tri.get("derivation") or "").strip()
        print(f"     △ {ent}: {nv} → targets [{targets_str}] · {impact}")
        if derivation:
            # Indent + word-wrap-ish at sentence boundaries so it stays readable.
            lines = re.findall(r".{1,90}(?:[ ,.] |$)", derivation)
            for ln in lines:
                ln = ln.strip()
                if ln:
                    print(f"       {ln}")

    print(f"New ({len(summary['new'])}):           "
          "entities or fields not yet tracked")
    for c in summary["new"][:5]:
        print(_line(c))

    print(f"Context ({len(summary['context'])}):       "
          "qualitative, no numeric update")

    # Provenance impacts — a roll-up of confidence_impact from triangulations
    # plus the obvious bumps from updates/matches on previously low-confidence
    # positions. This is the "did the ledger get more confident" line.
    impacts = []
    for c in summary["triangulates"]:
        tri = c.get("triangulation") or {}
        impact = tri.get("confidence_impact")
        targets = tri.get("target_nodes") or []
        if impact and targets:
            tgt = targets[0] if targets else "?"
            impacts.append(f"     {_impact_glyph(impact)} {tgt}: triangulation {impact}")
    for c in summary["matches"]:
        ent = (c.get("entity") or "?")
        met = (c.get("metric") or "?")
        impacts.append(f"     ↑ {ent} {met}: match adds provenance")
    if impacts:
        print()
        print("Provenance impacts:")
        for line in impacts[:8]:
            print(line)

    print()
    print(f"Written to: {out_path.relative_to(ROOT)}")
    print(f"Review in:  claims.html (load latest candidates — curated entries appear via curated-index.json)")


def _impact_glyph(impact: str) -> str:
    return {
        "strengthens": "↑",
        "weakens": "↓",
        "widens_range": "↔",
    }.get(impact or "", "·")


# ─────────────────────────── main ──────────────────────────────────────────

def main():
    with logged_run("curated_intake.py") as outputs:
        _main_impl(outputs)


def _main_impl(outputs):
    parser = argparse.ArgumentParser(
        description="Curated source intake — single-source comparison against the ledger."
    )
    parser.add_argument("--url", help="URL to fetch and analyse")
    parser.add_argument("--slug", required=True,
                        help="Short identifier for the source (e.g. zitron-may2026, msft-q1-2026)")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help=f"Anthropic model id (default: {DEFAULT_MODEL})")
    parser.add_argument("--stdin", action="store_true",
                        help="Read source text from stdin (auto-detected if no --url)")
    args = parser.parse_args()

    # Slug sanity — used in the output filename, so allow alnum + hyphen only.
    if not re.match(r"^[a-z0-9][a-z0-9\-]{1,60}$", args.slug):
        print(f"❌ Invalid --slug '{args.slug}'. Use lowercase alnum + hyphens, "
              f"2-61 chars.", file=sys.stderr)
        sys.exit(2)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    try:
        import anthropic
    except ImportError:
        print("❌ anthropic package not installed. Run: pip install anthropic",
              file=sys.stderr)
        sys.exit(1)

    today = datetime.now().strftime("%Y-%m-%d")
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    print(f"🔍 Curated intake — {args.slug} ({today})")
    print("=" * 50)

    # 1. Source text
    use_stdin = args.stdin or (not args.url and not sys.stdin.isatty())
    source_text, source_url = fetch_source(args.url, use_stdin)
    print(f"  📄 Source: {len(source_text):,} chars")
    outputs["source_chars"] = len(source_text)
    outputs["source_url"] = source_url
    outputs["slug"] = args.slug

    if len(source_text) < 200:
        print("❌ Source text too short — cannot run comparison.", file=sys.stderr)
        sys.exit(1)

    # 2. Flow model context (revenue flow + capex flow + entity positions + composition rules)
    print("  📚 Building flow-model context...")
    ledger_summary, ledger_meta = build_flow_model()
    print(f"     {ledger_meta['entities_in_summary']} entities, "
          f"~{ledger_meta['ledger_context_tokens_est']:,} tokens")
    if ledger_meta["ledger_context_tokens_est"] > LEDGER_CONTEXT_TARGET * 1.5:
        print(f"     ⚠ Flow model context exceeds soft target "
              f"({LEDGER_CONTEXT_TARGET} tokens); consider tightening "
              f"_CURRENT_FIELDS / _FINANCIAL_FIELDS in curated_intake.py.")

    # 3. Opus call
    print(f"  🤖 Sending to {args.model}...")
    client = anthropic.Anthropic(api_key=api_key)
    raw_claims = call_opus(client, args.model, ledger_summary, source_text, source_url)
    print(f"  ✅ {len(raw_claims)} claim(s) extracted")

    # 4. Enrich
    with open(ENTITIES_PATH) as f:
        entities = json.load(f)
    with open(SCHEMA_PATH) as f:
        schema = json.load(f)
    claims = [
        enrich_claim(c, source_url, args.slug, today, generated_at,
                     entities, schema)
        for c in raw_claims
    ]

    # 5. Write
    out_path = write_output(
        args.slug, source_url, source_text, ledger_meta,
        args.model, claims, today, generated_at,
    )

    # 6. Summary
    print_summary(args.slug, source_text, ledger_meta, claims, out_path)

    outputs["claims_extracted"] = len(claims)
    outputs["matches"] = sum(1 for c in claims if c.get("comparison_type") == "matches")
    outputs["updates"] = sum(1 for c in claims if c.get("comparison_type") == "updates")
    outputs["conflicts"] = sum(1 for c in claims if c.get("comparison_type") == "conflicts")
    outputs["new"] = sum(1 for c in claims if c.get("comparison_type") == "new")
    outputs["triangulates"] = sum(1 for c in claims if c.get("comparison_type") == "triangulates")
    outputs["context"] = sum(1 for c in claims if c.get("comparison_type") == "context")
    outputs["model"] = args.model
    outputs["output_file"] = str(out_path.relative_to(ROOT))


if __name__ == "__main__":
    main()
