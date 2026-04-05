#!/usr/bin/env python3
"""
scan_sources.py — Daily scan of all active web sources for new claims.

Loops through sources-registry.json, fetches each active URL,
sends to Claude for claim extraction, and adds new claims to
vault-inbox.json as pending.

Run: python3 scripts/scan_sources.py
Requires: ANTHROPIC_API_KEY environment variable
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from urllib.request import urlopen, Request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(BASE_DIR, "sources-registry.json")
INBOX_PATH = os.path.join(BASE_DIR, "vault-inbox.json")
MODEL = "claude-sonnet-4-6"

EXTRACT_PROMPT = """Extract ALL specific quantitative claims from this web page. Focus on:
- Revenue figures (ARR, annual revenue, monthly revenue, collected revenue)
- User/customer counts
- Growth rates
- Financial projections, targets, or guidance
- Token volumes, API usage stats
- Funding, valuation
- Cost figures, margins, losses
- Employee counts

For each claim, return a JSON array. Each item:
{{
  "claim": "ALWAYS start with the company name, e.g. 'OpenAI ended 2024 with $3.4B revenue'",
  "entity": "company name this is about",
  "value": <numeric value — use billions for $B, millions for $M, raw number for counts>,
  "unit": "unit — e.g. $B, $B ARR, %, count, T tokens/day",
  "confidence": "verified|estimated|speculative",
  "dateOfClaim": "YYYY-MM-DD or best guess",
  "tags": ["relevant", "tags"]
}}

Return ONLY a valid JSON array. No markdown, no explanation. If no claims found, return [].

PAGE CONTENT:
{text}"""


def load_json(path):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def fetch_page(url):
    """Fetch URL content, strip HTML, return plaintext."""
    text = None

    # Strategy 1: curl (better at bypassing bot detection)
    try:
        result = subprocess.run(
            ["curl", "-sL", "-m", "15",
             "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
             "-H", "Accept: text/html",
             url],
            capture_output=True, text=True, timeout=20
        )
        if result.returncode == 0 and len(result.stdout) > 200 and "Just a moment" not in result.stdout[:500]:
            text = result.stdout
    except Exception:
        pass

    # Strategy 2: urllib
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

    # Strip HTML to plaintext
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&[a-z]+;', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()[:8000]


def extract_claims(text, source_title, client):
    """Send text to Claude, return list of claim dicts."""
    prompt = EXTRACT_PROMPT.format(text=text)

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.content[0].text.strip()
        raw = re.sub(r'^```(?:json)?\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        claims = json.loads(raw.strip())
        return claims if isinstance(claims, list) else []
    except Exception as e:
        print(f"    ⚠ Claude error: {e}")
        return []


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
        sys.exit(1)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
    except ImportError:
        print("❌ anthropic not installed. Run: pip install anthropic")
        sys.exit(1)

    today = datetime.now().strftime("%Y-%m-%d")
    date_str = today.replace("-", "")
    print(f"🔍 Source Scanner — {today}\n{'=' * 50}")

    registry = load_json(REGISTRY_PATH)
    if not registry or not registry.get("sources"):
        print("No sources found.")
        return

    inbox = load_json(INBOX_PATH)
    if not inbox:
        inbox = {"items": [], "lastProcessed": None}

    # Get existing claim IDs to avoid duplicates
    existing_ids = {item["id"] for item in inbox["items"]}

    # Filter to sources that are due for scanning
    fetchable_methods = {"web_extract", "pdf_export"}
    freq_days = {
        "daily": 1,
        "weekly": 7,
        "monthly": 30,
        "quarterly": 90,
        "annual": 365,
        "one_time": 999999,  # never re-scan
    }

    all_fetchable = [
        s for s in registry["sources"]
        if s.get("extraction_method") in fetchable_methods
        and s.get("status") in ("active", "pending_first_extraction")
        and s.get("url")
    ]

    sources = []
    skipped = 0
    for s in all_fetchable:
        freq = s.get("frequency", "daily")
        last = s.get("last_checked")
        interval = freq_days.get(freq, 1)

        # Always scan pending_first_extraction
        if s.get("status") == "pending_first_extraction":
            sources.append(s)
            continue

        # Skip one_time sources that have already been scanned
        if freq == "one_time" and last:
            skipped += 1
            continue

        # Check if enough time has passed since last scan
        if last:
            from datetime import datetime as _dt
            try:
                last_date = _dt.strptime(last, "%Y-%m-%d")
                days_since = (datetime.now() - last_date).days
                if days_since < interval:
                    skipped += 1
                    continue
            except ValueError:
                pass  # bad date format, scan anyway

        sources.append(s)

    print(f"Sources to scan: {len(sources)} (of {len(all_fetchable)} fetchable, {skipped} skipped — not due yet)\n")

    total_added = 0
    sources_updated = 0

    for source in sources:
        sid = source["id"]
        url = source["url"]
        title = source["title"]
        print(f"  📄 {title}")
        print(f"     {url}")

        # Fetch page
        text = fetch_page(url)
        if not text:
            print(f"     ⚠ Could not fetch — skipping")
            continue

        print(f"     Fetched {len(text)} chars, extracting claims...")

        # Extract claims via Claude
        claims = extract_claims(text, title, client)
        if not claims:
            print(f"     No claims found")
            source["last_checked"] = today
            freq = source.get("frequency", "daily")
            interval = freq_days.get(freq, 1)
            from datetime import timedelta
            source["next_check"] = (datetime.now() + timedelta(days=interval)).strftime("%Y-%m-%d")
            sources_updated += 1
            continue

        # Add new claims to inbox
        added = 0
        for i, claim in enumerate(claims):
            claim_id = f"scan-{date_str}-{sid}-{i + 1}"
            if claim_id in existing_ids:
                continue

            # Check for duplicate claims by content
            claim_text = claim.get("claim", "").lower().strip()
            is_dupe = any(
                item.get("claim", "").lower().strip() == claim_text
                for item in inbox["items"]
                if item.get("status") == "pending"
            )
            if is_dupe:
                continue

            inbox["items"].append({
                "id": claim_id,
                "claim": claim.get("claim", ""),
                "value": claim.get("value"),
                "unit": claim.get("unit", ""),
                "sourceUrl": url,
                "sourceType": "reporting",
                "sourceAuthor": claim.get("entity", title),
                "confidence": claim.get("confidence", "estimated"),
                "dateOfClaim": claim.get("dateOfClaim", today),
                "dateAdded": today,
                "usedOn": [],
                "tags": claim.get("tags", []),
                "notes": f"Auto-scanned from {title}",
                "status": "pending",
                "replaces": None,
                "source_id": sid,
                "metricKey": None,
            })
            existing_ids.add(claim_id)
            added += 1

        total_added += added
        sources_updated += 1
        source["last_checked"] = today
        source["last_claims_count"] = len(claims)
        if source["status"] == "pending_first_extraction":
            source["status"] = "active"

        # Set next_check based on frequency
        freq = source.get("frequency", "daily")
        interval = freq_days.get(freq, 1)
        from datetime import timedelta
        next_date = datetime.now() + timedelta(days=interval)
        source["next_check"] = next_date.strftime("%Y-%m-%d")

        print(f"     ✅ {added} new claim(s) added to inbox")

    # Save updated files
    inbox["lastProcessed"] = today
    save_json(INBOX_PATH, inbox)
    save_json(REGISTRY_PATH, registry)

    print(f"\n{'=' * 50}")
    print(f"✅ Scan complete: {total_added} new claims from {sources_updated} sources")
    print(f"   Total inbox items: {len(inbox['items'])}")


if __name__ == "__main__":
    main()
