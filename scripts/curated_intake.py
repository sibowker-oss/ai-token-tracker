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
LEDGER_CONTEXT_TARGET = 15_000  # tokens, soft target per brief §4.2


SYSTEM_PROMPT = """You are a financial data analyst maintaining The AI Ledger — a public dataset tracking capital flows in the AI industry.

You will receive:
1. A source text (article, newsletter, earnings release, analyst report)
2. The ledger's current position — a compressed summary of every entity and value currently tracked

Your task: compare the source against the ledger and extract ONLY claims that have a specific entity, metric, and numeric value. For each claim, classify it:
- "matches": confirms an existing ledger value (within 5% tolerance)
- "updates": supersedes an existing value (same entity + field, newer or more authoritative source)
- "conflicts": contradicts an existing value by >10% — flag both values
- "new": entity or field not currently in the ledger
- "context": qualitative or non-numeric — useful colour but not a data point

SCOPE — the ledger tracks:
- AI provider revenue, ARR, growth rates, margins, operating loss, cash burn
- Hyperscaler capex on AI infrastructure (data centers, GPU clusters, power)
- Token/inference economics (tokens/day, cost per token, API pricing)
- GPU/compute infrastructure (GPU counts, cluster sizes, chip supply)
- AI company valuations, funding rounds, employee counts
- Enterprise AI adoption spend

DO NOT extract: model benchmark scores (unless tied to revenue impact), vague market commentary, biographical facts, non-AI business metrics.

For each claim, output a JSON object with these fields:
- "claim": verbatim or lightly paraphrased quote (1-2 sentences)
- "category": one of: provider_revenue | token_volume | pricing | gpu_infrastructure | enterprise_adoption | skeptical_bear_case | valuation_funding
- "entity": company or product name
- "metric": what is being measured (e.g. "ARR", "tokens/day", "capex")
- "value": numeric value as a number, or null if unclear
- "unit": unit of value (e.g. "USD", "tokens", "GPUs")
- "value_display": human-readable value string (e.g. "$16.8B", "15M seats")
- "time_period": when this applies (e.g. "Q1 2026", "2025", "as of March 2026")
- "time_period_scope": one of: "annual" | "h1" | "h2" | "q1" | "q2" | "q3" | "q4" | "exit_snapshot" | "monthly_peak" | "point_in_time"
- "period_qualifier_detected": short string quoting the qualifier you matched (e.g. "H1 2025", "exit ARR 2024", "$6B/month February 2026"), or null when scope=annual with no qualifier

  TIME PERIOD SCOPE — RULES (wq-054):

  Rule A — INTERNAL CONSISTENCY:
  If you populate period_qualifier_detected with a non-null value, time_period_scope MUST be the corresponding scope from the qualifier — NOT point_in_time:
    - Qualifier mentions "Q1/Q2/Q3/Q4" → scope must be q1/q2/q3/q4
    - Qualifier mentions "H1/H2/first half/second half" → scope must be h1/h2
    - Qualifier mentions "exit/end of year/year-end run-rate" → scope must be exit_snapshot
    - Qualifier mentions "monthly/per month/$X/month" → scope must be monthly_peak

  Rule B — point_in_time BOUNDARY:
  point_in_time is reserved for ENTITY-CURRENT state metrics: weekly active users, headcount, current model version, current ARR run-rate WHEN explicitly described as "as of today / now / current".
  point_in_time is NOT for funding rounds, valuations, or annual revenue figures — those are scope=annual.

  Rule C — DEFAULT:
  No period qualifier in source → scope=annual, period_qualifier_detected=null.

- "confidence": "high" | "medium" | "low"
- "speaker": author/source name, or null
- "weight": exactly one of:
    "authoritative" — source has direct first-hand knowledge (e.g. company's own earnings release on its own ARR)
    "corroborating" — source cites a specific named primary source (earnings call, official filing, named report)
    "indicative" — market colour, repeated figures, estimates
- "comparison_type": one of: matches | updates | conflicts | new | context
- "existing_value": the ledger's current value for this entity+metric, or null if not tracked
- "delta_pct": percentage change from existing value (signed, e.g. 0.20 for +20%), or null
- "comparison_note": 1-line explanation of the comparison result

Rules:
- Only extract claims with a specific entity + metric + numeric value (or value-bearing categorical fact like a funding round closing). Skip vague statements.
- Fewer high-quality claims are better than many noisy ones.
- A source describing its OWN financials (e.g. Microsoft's investor relations page on Microsoft capex) is weight "authoritative".
- A source quoting another source ("per The Information, OpenAI ARR is $19.5B") is weight "corroborating".
- An analyst's estimate or commentary is weight "indicative".
- For matches/updates/conflicts, populate existing_value and delta_pct from the ledger summary you were given.
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


# ─────────────────────────── ledger context builder ────────────────────────

# Fields worth surfacing in the ledger summary. Keeping this list tight is
# what holds the context under ~15k tokens — the entities.json file as a
# whole is much larger than the model needs to see for comparison.
_CURRENT_FIELDS = (
    "arr", "tokens_per_day", "valuation", "user_count", "subscriber_count",
    "growth_rate", "consumer_pct", "biz_pct", "model_count", "employee_count",
)
_FINANCIAL_FIELDS = (
    "arr", "collected_revenue", "operating_loss", "inference_cost",
    "capex", "capex_ai", "data_center_capex", "total_funding",
    "valuation", "exit_arr", "h1_arr", "q4_arr", "monthly_peak_arr",
    "employees", "gpu_count", "tokens_per_day",
)


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


def _entity_summary_lines(entity: dict) -> list[str]:
    """One block of plain-text summary for a single entity. Skips entities
    with no values so the context stays under target."""
    slug = entity.get("slug", "?")
    name = entity.get("name", slug)
    roles = entity.get("roles") or []
    role_str = ",".join(roles) if roles else "—"

    current_bits = []
    current = entity.get("current") or {}
    for f in _CURRENT_FIELDS:
        v = _format_value(current.get(f))
        if v is not None:
            current_bits.append(f"{f}={v}")

    fin_bits = []
    financials = entity.get("financials") or {}
    # Only most recent two years to keep tokens bounded; older history is
    # rarely the point of comparison and bloats the context window.
    years = sorted(
        (y for y in financials.keys() if re.match(r"^\d{4}$", str(y))),
        reverse=True,
    )[:2]
    for year in years:
        year_block = financials.get(year) or {}
        per_year = []
        for f in _FINANCIAL_FIELDS:
            v = _format_value(year_block.get(f))
            if v is not None:
                per_year.append(f"{f}={v}")
        if per_year:
            fin_bits.append(f"{year}: " + ", ".join(per_year))

    if not current_bits and not fin_bits:
        return []

    lines = [f"## {slug} ({name}) [{role_str}]"]
    if current_bits:
        lines.append("  current: " + ", ".join(current_bits))
    for fb in fin_bits:
        lines.append("  " + fb)
    return lines


def build_ledger_summary() -> tuple[str, dict]:
    """Compress entities.json + site-data providers + schema into a Markdown
    summary the model can compare against. Returns (text, meta)."""
    with open(ENTITIES_PATH) as f:
        entities = json.load(f)
    with open(SCHEMA_PATH) as f:
        schema = json.load(f)
    with open(SITE_DATA_PATH) as f:
        site_data = json.load(f)

    sections = []

    # § Tracked fields — gives the model a sense of what counts as "in scope".
    field_rules = schema.get("field_match_rules", []) or []
    proposed = schema.get("proposed_fields", []) or []
    field_lines = ["# Tracked metric fields (canonical IDs)"]
    seen = set()
    for rule in field_rules:
        fid = rule.get("field")
        if fid and fid not in seen:
            seen.add(fid)
            field_lines.append(f"- {fid}")
    if proposed:
        field_lines.append("")
        field_lines.append("# Proposed (under-evidenced) fields")
        for f in proposed:
            field_lines.append(f"- {f.get('field_id')}: {f.get('description', '')}")
    sections.append("\n".join(field_lines))

    # § Entity rosters — only entities with at least one value, sorted alpha.
    entity_lines = ["# Entities with current ledger values (slug, name, key fields)"]
    companies = sorted(entities.get("companies", []), key=lambda c: c.get("slug", ""))
    for entity in companies:
        entity_lines.extend(_entity_summary_lines(entity))
    sections.append("\n".join(entity_lines))

    # § Provider dashboard — quick lookup for tokens/rev sanity checks.
    providers = (site_data.get("dashboard") or {}).get("providers") or {}
    if providers:
        prov_lines = ["# Dashboard provider snapshot (rev in $B, tokens in T/day)"]
        for name, data in sorted(providers.items()):
            bits = []
            if data.get("rev"):
                bits.append(f"rev=${data['rev']}B")
            if data.get("tokens"):
                bits.append(f"tokens={data['tokens']}T/day")
            if data.get("growth"):
                bits.append(f"growth={data['growth']}")
            if bits:
                prov_lines.append(f"- {name}: " + ", ".join(bits))
        sections.append("\n".join(prov_lines))

    text = "\n\n".join(sections)
    # Cheap token estimate: ~4 chars/token for English prose.
    est_tokens = len(text) // 4
    meta = {
        "ledger_context_chars": len(text),
        "ledger_context_tokens_est": est_tokens,
        "entities_in_summary": sum(
            1 for e in companies if _entity_summary_lines(e)
        ),
    }
    return text, meta


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
                max_tokens=8192,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_msg}],
            )
            raw = response.content[0].text.strip()
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
            claims = json.loads(raw)
            if not isinstance(claims, list):
                claims = []
        except json.JSONDecodeError as e:
            print(f"\n  ⚠ JSON parse error in chunk {i+1}: {e}")
            print(f"     Raw: {raw[:200]}")
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
_COMPARISON_TO_DEDUP = {
    "matches": "confirms",
    "updates": "conflicts",
    "conflicts": "conflicts",
    "new": "new",
    "context": "new",
}


def enrich_claim(claim: dict, source_url: str | None, slug: str,
                 today: str, generated_at: str, entities: dict,
                 schema: dict) -> dict:
    """Stamp source metadata, materiality score, and dedup_status onto a
    raw model claim. Mirrors what extract_claims.py does at write time so
    the review UI sees consistent fields."""
    comparison_type = claim.get("comparison_type") or "context"
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
        "context": sum(1 for c in claims if c.get("comparison_type") == "context"),
    }

    payload = {
        "source": "curated_intake",
        "slug": slug,
        "generated_at": generated_at,
        "model": model,
        "source_url": source_url,
        "source_text_chars": len(source_text),
        "ledger_context_tokens": ledger_meta.get("ledger_context_tokens_est", 0),
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
        "matches":   [c for c in claims if c.get("comparison_type") == "matches"],
        "updates":   [c for c in claims if c.get("comparison_type") == "updates"],
        "conflicts": [c for c in claims if c.get("comparison_type") == "conflicts"],
        "new":       [c for c in claims if c.get("comparison_type") == "new"],
        "context":   [c for c in claims if c.get("comparison_type") == "context"],
    }

    print()
    print(f"── Curated intake: {slug} " + "─" * max(0, 40 - len(slug)))
    print(f"Source: {len(source_text):,} chars │ "
          f"Ledger context: ~{ledger_meta.get('ledger_context_tokens_est', 0):,} tokens "
          f"({ledger_meta.get('entities_in_summary', 0)} entities)")
    print()

    def _line(c):
        ent = c.get("entity") or "?"
        met = c.get("metric") or "?"
        val_disp = c.get("value_display") or c.get("value") or "?"
        period = c.get("time_period") or ""
        return f"     {ent} {met}: {val_disp}" + (f" ({period})" if period else "")

    print(f"Matches ({len(summary['matches'])}):   "
          "claims that confirm existing ledger values")
    for c in summary["matches"][:5]:
        print(_line(c))

    print(f"Updates ({len(summary['updates'])}):   "
          "claims that supersede existing values")
    for c in summary["updates"]:
        ent, met = c.get("entity") or "?", c.get("metric") or "?"
        ev = c.get("existing_value")
        nv = c.get("value_display") or c.get("value")
        delta = c.get("delta_pct")
        delta_str = f"{delta:+.1%}" if isinstance(delta, (int, float)) else "?"
        ev_str = f"${ev}B" if isinstance(ev, (int, float)) else str(ev)
        print(f"     ⚠ {ent} {met}: {ev_str} → {nv} ({delta_str})")

    print(f"Conflicts ({len(summary['conflicts'])}): "
          "claims that contradict existing values")
    for c in summary["conflicts"]:
        ent, met = c.get("entity") or "?", c.get("metric") or "?"
        ev = c.get("existing_value")
        nv = c.get("value_display") or c.get("value")
        delta = c.get("delta_pct")
        delta_str = f"{delta:+.1%}" if isinstance(delta, (int, float)) else "?"
        ev_str = f"${ev}B" if isinstance(ev, (int, float)) else str(ev)
        print(f"     ✗ {ent} {met}: {ev_str} (ledger) vs {nv} (source, {delta_str})")

    print(f"New ({len(summary['new'])}):       "
          "entities or fields not yet tracked")
    for c in summary["new"][:5]:
        print(_line(c))

    print(f"Context ({len(summary['context'])}):   "
          "qualitative, no numeric update")

    print()
    print(f"Written to: {out_path.relative_to(ROOT)}")
    print(f"Review in:  claims.html (load latest candidates — curated entries appear via curated-index.json)")


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

    # 2. Ledger context
    print("  📚 Building ledger context...")
    ledger_summary, ledger_meta = build_ledger_summary()
    print(f"     {ledger_meta['entities_in_summary']} entities, "
          f"~{ledger_meta['ledger_context_tokens_est']:,} tokens")
    if ledger_meta["ledger_context_tokens_est"] > LEDGER_CONTEXT_TARGET * 1.5:
        print(f"     ⚠ Ledger context exceeds soft target "
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
    outputs["context"] = sum(1 for c in claims if c.get("comparison_type") == "context")
    outputs["model"] = args.model
    outputs["output_file"] = str(out_path.relative_to(ROOT))


if __name__ == "__main__":
    main()
