#!/usr/bin/env python3
"""
audit_sources.py — Reprocess all sources and compare against current entity data.

Fetches all active sources, extracts claims using the full field schema,
then compares against entities.json to find gaps and discrepancies.

Output: data/audit-report-{date}.json
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from urllib.request import urlopen, Request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = "claude-sonnet-4-6"

EXTRACT_PROMPT = """You are auditing AI industry data. Extract ALL quantitative claims from this content.

We track these fields for companies:
- Revenue: ARR, collected_revenue, subscription_revenue, api_revenue, enterprise_revenue
- Costs: operating_loss, cash_burn, inference_cost, capex, cogs_ratio
- Scale: tokens_per_day, customer_count, user_count, employee_count, gpu_count
- Growth: growth_rate
- Funding: valuation, total_funding
- Market: market_share_pct

For each claim found, return a JSON object:
{{
  "entity": "company name",
  "field": "closest field name from list above",
  "value": <numeric value>,
  "unit": "e.g. $B, $M, %, count, T tokens/day",
  "display": "human-readable e.g. $3.4B ARR",
  "period": "e.g. 2025, Q1 2026, as of March 2026",
  "confidence": "high|medium|low",
  "claim": "verbatim or paraphrased quote"
}}

Return ONLY a valid JSON array. No markdown. If no claims, return [].

CONTENT:
{text}"""


def fetch_page(url):
    """Fetch and strip HTML."""
    text = None
    try:
        result = subprocess.run(
            ["curl", "-sL", "-m", "15",
             "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
             "-H", "Accept: text/html", url],
            capture_output=True, text=True, timeout=20
        )
        if result.returncode == 0 and len(result.stdout) > 200 and "Just a moment" not in result.stdout[:500]:
            text = result.stdout
    except Exception:
        pass

    if not text:
        try:
            req = Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml",
            })
            with urlopen(req, timeout=15) as resp:
                text = resp.read().decode("utf-8", errors="replace")
        except Exception:
            pass

    if not text or len(text) < 200:
        return None

    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&[a-z]+;', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()[:12000]


def extract_claims(text, client):
    prompt = EXTRACT_PROMPT.format(text=text)
    try:
        response = client.messages.create(
            model=MODEL, max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.content[0].text.strip()
        raw = re.sub(r'^```(?:json)?\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        return json.loads(raw.strip())
    except Exception as e:
        print(f"    ⚠ Error: {e}")
        return []


def load_json(path):
    with open(path) as f:
        return json.load(f)


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
        sys.exit(1)

    import anthropic
    client = anthropic.Anthropic(api_key=api_key)

    today = datetime.now().strftime("%Y-%m-%d")
    print(f"🔍 Source Audit — {today}\n{'=' * 60}")

    # Load current data
    registry = load_json(os.path.join(BASE_DIR, "sources-registry.json"))
    entities = load_json(os.path.join(BASE_DIR, "entities.json"))
    inbox = load_json(os.path.join(BASE_DIR, "vault-inbox.json"))

    # Build current entity data lookup: {slug: {field: value}}
    current_data = {}
    for c in entities.get("companies", []):
        slug = c["slug"]
        current_data[slug] = {}
        for section in ["current", "financials"]:
            for key, val in c.get(section, {}).items():
                if isinstance(val, (int, float)):
                    current_data[slug][key] = val
                elif isinstance(val, dict) and "value" in val:
                    current_data[slug][key] = val["value"]

    # Also include accepted inbox claims
    accepted_claims = [i for i in inbox["items"] if i.get("status") == "accepted"]

    # Fetch and extract from all active web sources
    fetchable = [
        s for s in registry["sources"]
        if s.get("extraction_method") in ("web_extract", "pdf_export")
        and s.get("status") in ("active", "pending_first_extraction")
        and s.get("url")
    ]

    # Deduplicate by URL
    seen_urls = set()
    unique_sources = []
    for s in fetchable:
        if s["url"] not in seen_urls:
            seen_urls.add(s["url"])
            unique_sources.append(s)

    print(f"Sources to audit: {len(unique_sources)} unique URLs\n")

    all_fresh_claims = []

    for source in unique_sources:
        print(f"  📄 {source['title']}")
        text = fetch_page(source["url"])
        if not text:
            print(f"     ⚠ Could not fetch")
            continue

        print(f"     Fetched {len(text)} chars...")
        claims = extract_claims(text, client)
        print(f"     → {len(claims)} claims")

        for claim in claims:
            claim["source_id"] = source["id"]
            claim["source_title"] = source["title"]
            claim["source_url"] = source["url"]
        all_fresh_claims.extend(claims)

    # Also process transcript files if they exist
    transcript_dir = os.path.join(BASE_DIR, "transcripts")
    if os.path.exists(transcript_dir):
        import glob
        transcripts = glob.glob(os.path.join(transcript_dir, "**", "*.md"), recursive=True)
        print(f"\n  📝 {len(transcripts)} transcripts found")
        for t in transcripts[:10]:  # Limit to 10 most recent
            name = os.path.basename(t)
            print(f"  📄 {name}")
            with open(t) as f:
                text = f.read()
            body_start = text.find("---\n\n")
            if body_start >= 0:
                text = text[body_start + 5:]
            text = text[:12000]
            if len(text) < 200:
                continue
            claims = extract_claims(text, client)
            print(f"     → {len(claims)} claims")
            for claim in claims:
                claim["source_id"] = "transcript"
                claim["source_title"] = name
            all_fresh_claims.extend(claims)

    # Now compare fresh claims vs current entity data
    print(f"\n{'=' * 60}")
    print(f"AUDIT RESULTS")
    print(f"{'=' * 60}")
    print(f"Fresh claims extracted: {len(all_fresh_claims)}")

    # Normalise entity names to slugs
    name_to_slug = {}
    for c in entities.get("companies", []):
        name_to_slug[c["name"].lower()] = c["slug"]
        name_to_slug[c["slug"]] = c["slug"]

    # Group fresh claims by entity
    by_entity = {}
    for claim in all_fresh_claims:
        entity = (claim.get("entity") or "").strip()
        entity_lower = entity.lower().replace(" ", "-").replace(".", "")
        slug = name_to_slug.get(entity.lower()) or name_to_slug.get(entity_lower)
        if not slug:
            # Try partial match
            for name, s in name_to_slug.items():
                if entity.lower() in name or name in entity.lower():
                    slug = s
                    break
        claim["matched_slug"] = slug
        key = slug or entity
        by_entity.setdefault(key, []).append(claim)

    # Compare
    gaps = []      # Fields we have claims for but no entity data
    conflicts = [] # Fields where claim value differs significantly
    confirms = []  # Fields where claim matches
    unmatched = [] # Claims for entities we don't track

    for entity_key, claims in by_entity.items():
        entity_data = current_data.get(entity_key, {})

        for claim in claims:
            field = claim.get("field", "")
            value = claim.get("value")
            if value is None:
                continue

            record = {
                "entity": claim.get("entity"),
                "slug": claim.get("matched_slug"),
                "field": field,
                "fresh_value": value,
                "display": claim.get("display", ""),
                "period": claim.get("period", ""),
                "confidence": claim.get("confidence", ""),
                "source": claim.get("source_title", ""),
                "claim": claim.get("claim", ""),
            }

            if not claim.get("matched_slug"):
                unmatched.append(record)
                continue

            current_val = entity_data.get(field)
            if current_val is None:
                record["current_value"] = None
                gaps.append(record)
            else:
                record["current_value"] = current_val
                if current_val == 0:
                    gaps.append(record)
                else:
                    ratio = value / current_val if current_val != 0 else 999
                    if 0.9 <= ratio <= 1.1:
                        confirms.append(record)
                    else:
                        record["ratio"] = round(ratio, 2)
                        record["pct_diff"] = f"{(ratio - 1) * 100:+.0f}%"
                        conflicts.append(record)

    print(f"\nBy entity: {len(by_entity)} entities mentioned")
    print(f"  Confirms existing data: {len(confirms)}")
    print(f"  Gaps (we're missing):   {len(gaps)}")
    print(f"  Conflicts (differs):    {len(conflicts)}")
    print(f"  Unmatched entities:     {len(unmatched)}")

    if conflicts:
        print(f"\n--- TOP CONFLICTS ---")
        for c in sorted(conflicts, key=lambda x: abs(x.get("ratio", 1) - 1), reverse=True)[:15]:
            print(f"  {c['entity']}.{c['field']}: ours={c['current_value']} vs fresh={c['fresh_value']} ({c['pct_diff']}) — {c['source']}")

    if gaps:
        print(f"\n--- TOP GAPS (fields we could fill) ---")
        for g in gaps[:15]:
            print(f"  {g['entity']}.{g['field']}: {g['display']} ({g['period']}) — {g['source']}")

    # Save full report
    report = {
        "date": today,
        "sources_audited": len(unique_sources),
        "total_fresh_claims": len(all_fresh_claims),
        "confirms": len(confirms),
        "gaps": len(gaps),
        "conflicts": len(conflicts),
        "unmatched": len(unmatched),
        "conflict_details": conflicts,
        "gap_details": gaps,
        "unmatched_details": unmatched[:50],
        "confirm_details": confirms,
        "all_claims": all_fresh_claims,
    }

    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
    report_path = os.path.join(BASE_DIR, "data", f"audit-report-{today}.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📋 Full report saved: {report_path}")


if __name__ == "__main__":
    main()
