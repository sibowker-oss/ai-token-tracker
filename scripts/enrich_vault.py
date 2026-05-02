#!/usr/bin/env python3
"""
Enrich vault data points that only have a URL + title.

Fetches the linked page, extracts text, and uses Claude API to
populate structured fields (claim, value, entity, metric, confidence, etc).

Falls back to a simpler regex-based extraction if no API key is available.

Run: python3 scripts/enrich_vault.py
     python3 scripts/enrich_vault.py --dry-run

Processes vault-data.json entries where status='pending_enrichment'.
"""

import json
import os
import re
import sys
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from log_run import logged_run  # noqa: E402
VAULT_PATH = os.path.join(BASE_DIR, 'vault-data.json')

# Patterns for extracting financial data from text
MONEY_PATTERN = re.compile(
    r'(?:(?:USD|US\$|\$)\s*)?(\d+(?:\.\d+)?)\s*(billion|million|B|M|bn|mn|T|trillion)',
    re.IGNORECASE
)
ARR_PATTERN = re.compile(
    r'(?:ARR|annualized run rate|annual recurring revenue|revenue run rate)[^\d]{0,30}(?:(?:USD|US\$|\$)\s*)?(\d+(?:\.\d+)?)\s*(billion|million|B|M|bn|mn)',
    re.IGNORECASE
)
VALUATION_PATTERN = re.compile(
    r'(?:valued at|valuation|worth)[^\d]{0,30}(?:(?:USD|US\$|\$)\s*)?(\d+(?:\.\d+)?)\s*(billion|million|B|M|bn|mn)',
    re.IGNORECASE
)
FUNDING_PATTERN = re.compile(
    r'(?:raised|funding|series [A-Z]|round)[^\d]{0,30}(?:(?:USD|US\$|\$)\s*)?(\d+(?:\.\d+)?)\s*(billion|million|B|M|bn|mn)',
    re.IGNORECASE
)
TOKEN_PATTERN = re.compile(
    r'(\d+(?:\.\d+)?)\s*(trillion|billion|T|B)\s*tokens?\s*(?:per|/)\s*(?:day|week|month)',
    re.IGNORECASE
)
COMPANY_PATTERN = re.compile(
    r'(?:OpenAI|Anthropic|Google|Meta|DeepSeek|Mistral|xAI|Minimax|Moonshot|'
    r'Cursor|Perplexity|Replit|Harvey|Midjourney|ElevenLabs|Cohere|'
    r'Lovable|Character\.ai|Together AI|Fireworks|Groq|Scale AI|'
    r'Microsoft|Salesforce|ServiceNow|GitHub Copilot|Databricks|Snowflake)',
    re.IGNORECASE
)

UNIT_MAP = {
    'billion': 1e9, 'B': 1e9, 'bn': 1e9,
    'million': 1e6, 'M': 1e6, 'mn': 1e6,
    'trillion': 1e12, 'T': 1e12,
}


def fetch_page_text(url):
    """Fetch a URL and extract plain text."""
    try:
        req = Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; VaultEnricher/1.0)',
        })
        with urlopen(req, timeout=20) as resp:
            html = resp.read().decode('utf-8', errors='replace')
    except (URLError, Exception) as e:
        print(f"    ⚠ Failed to fetch {url}: {e}")
        return None

    # Strip scripts, styles, tags
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&[a-z]+;', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_with_regex(text, title=''):
    """Extract structured data from page text using regex patterns."""
    findings = {
        'entities': [],
        'arr_mentions': [],
        'valuation_mentions': [],
        'funding_mentions': [],
        'token_mentions': [],
        'money_mentions': [],
    }

    # Find company mentions
    for m in COMPANY_PATTERN.finditer(text):
        entity = m.group(0)
        if entity not in findings['entities']:
            findings['entities'].append(entity)

    # Find ARR/revenue
    for m in ARR_PATTERN.finditer(text):
        val = float(m.group(1)) * UNIT_MAP.get(m.group(2), 1)
        ctx = text[max(0, m.start()-80):m.end()+80].strip()
        findings['arr_mentions'].append({'value': val, 'context': ctx})

    # Find valuations
    for m in VALUATION_PATTERN.finditer(text):
        val = float(m.group(1)) * UNIT_MAP.get(m.group(2), 1)
        ctx = text[max(0, m.start()-80):m.end()+80].strip()
        findings['valuation_mentions'].append({'value': val, 'context': ctx})

    # Find funding
    for m in FUNDING_PATTERN.finditer(text):
        val = float(m.group(1)) * UNIT_MAP.get(m.group(2), 1)
        ctx = text[max(0, m.start()-80):m.end()+80].strip()
        findings['funding_mentions'].append({'value': val, 'context': ctx})

    # Find token volumes
    for m in TOKEN_PATTERN.finditer(text):
        val = float(m.group(1)) * UNIT_MAP.get(m.group(2), 1)
        ctx = text[max(0, m.start()-80):m.end()+80].strip()
        findings['token_mentions'].append({'value': val, 'context': ctx})

    # Find general money mentions
    for m in MONEY_PATTERN.finditer(text):
        val = float(m.group(1)) * UNIT_MAP.get(m.group(2), 1)
        ctx = text[max(0, m.start()-50):m.end()+50].strip()
        findings['money_mentions'].append({'value': val, 'context': ctx})

    return findings


def enrich_with_claude(text, title, url):
    """Use Claude API to extract structured data (if API key available)."""
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        return None

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
    except ImportError:
        return None

    # Truncate text to fit context
    text_chunk = text[:30000]

    prompt = f"""Extract ALL structured financial/AI data points from this article.

Title: {title}
URL: {url}

Article text:
{text_chunk}

For each data point found, return a JSON object with:
- "claim": verbatim or lightly paraphrased quote (1-2 sentences)
- "entity": company name
- "metric": what is measured (ARR, valuation, tokens/day, seats, etc)
- "value": numeric value
- "unit": USD, tokens, seats, etc
- "value_display": human-readable (e.g. "$14B")
- "confidence": high/medium/low
- "sourceType": one of: sec-filing, earnings-aggregation, official, reporting, estimate, observation
- "tags": relevant tags as array

Return a JSON array. Return [] if no data points found.
Return ONLY the JSON array."""

    try:
        response = client.messages.create(
            model='claude-sonnet-4-6',
            max_tokens=4096,
            messages=[{'role': 'user', 'content': prompt}]
        )
        raw = response.content[0].text.strip()
        raw = re.sub(r'^```(?:json)?\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        return json.loads(raw)
    except Exception as e:
        print(f"    ⚠ Claude API error: {e}")
        return None


def build_data_point(dp, findings, claude_extractions, text):
    """Update a vault data point with extracted data."""
    title = dp.get('claim', dp.get('notes', ''))

    # If Claude gave us extractions, use the first one as primary
    if claude_extractions and len(claude_extractions) > 0:
        best = claude_extractions[0]
        dp['claim'] = best.get('claim', title)
        dp['value'] = best.get('value')
        dp['unit'] = best.get('unit', '')
        dp['sourceType'] = best.get('sourceType', 'reporting')
        dp['confidence'] = best.get('confidence', 'estimated')
        dp['tags'] = best.get('tags', [])
        if best.get('entity'):
            dp['notes'] = (dp.get('notes', '') + f" Entity: {best['entity']}").strip()
        if best.get('metric'):
            dp['metricKey'] = re.sub(r'[^a-z0-9]+', '-', f"{best.get('entity','')}-{best['metric']}".lower()).strip('-')

        # Store additional extractions as notes
        if len(claude_extractions) > 1:
            additional = [f"{e.get('entity','?')}: {e.get('value_display','?')} ({e.get('metric','?')})"
                         for e in claude_extractions[1:5]]
            dp['notes'] = (dp.get('notes', '') + '\nAdditional: ' + '; '.join(additional)).strip()

    # Regex fallback
    else:
        # Use best ARR mention if available
        if findings['arr_mentions']:
            best = findings['arr_mentions'][0]
            dp['value'] = best['value']
            dp['unit'] = '$'
            dp['claim'] = best['context'][:200]
            dp['sourceType'] = 'reporting'
            dp['confidence'] = 'estimated'

        elif findings['valuation_mentions']:
            best = findings['valuation_mentions'][0]
            dp['value'] = best['value']
            dp['unit'] = '$ valuation'
            dp['claim'] = best['context'][:200]
            dp['sourceType'] = 'reporting'
            dp['confidence'] = 'estimated'

        elif findings['funding_mentions']:
            best = findings['funding_mentions'][0]
            dp['value'] = best['value']
            dp['unit'] = '$ funding'
            dp['claim'] = best['context'][:200]
            dp['sourceType'] = 'reporting'
            dp['confidence'] = 'estimated'

        elif findings['money_mentions']:
            best = findings['money_mentions'][0]
            dp['value'] = best['value']
            dp['unit'] = '$'
            dp['claim'] = best['context'][:200]
            dp['sourceType'] = 'reporting'
            dp['confidence'] = 'speculative'

        # Add entity tags
        if findings['entities']:
            dp['tags'] = list(set(e.lower() for e in findings['entities'][:5]))

        # Set sourceType based on URL
        url = dp.get('sourceUrl', '')
        if 'sec.gov' in url or 'edgar' in url:
            dp['sourceType'] = 'sec-filing'
        elif 'earnings' in url.lower() or 'investor' in url.lower():
            dp['sourceType'] = 'earnings-aggregation'
        elif any(d in url for d in ['bloomberg.com', 'wsj.com', 'ft.com', 'reuters.com', 'theinformation.com']):
            dp['sourceType'] = 'reporting'
        elif any(d in url for d in ['twitter.com', 'x.com', 'reddit.com']):
            dp['sourceType'] = 'observation'

    # Always set these
    dp['dateAdded'] = datetime.now().strftime('%Y-%m-%d')
    dp['status'] = 'pending'  # Ready for human review
    dp['sourceAuthor'] = dp.get('sourceAuthor', '')

    return dp


def main():
    with logged_run("enrich_vault.py") as outputs:
        _main_impl(outputs)


def _main_impl(outputs):
    dry_run = '--dry-run' in sys.argv

    print(f"🔍 Vault Enrichment — {datetime.now().strftime('%Y-%m-%d')}")

    with open(VAULT_PATH) as f:
        vault = json.load(f)

    to_enrich = [dp for dp in vault['dataPoints'] if dp.get('status') == 'pending_enrichment']

    if not to_enrich:
        print("  No entries with status='pending_enrichment'. Nothing to do.")
        print("  Add entries via the Quick Add form in vault.html.")
        outputs["items_enriched"] = 0
        outputs["items_to_enrich"] = 0
        return

    print(f"  Found {len(to_enrich)} entries to enrich\n")

    has_api = bool(os.environ.get('ANTHROPIC_API_KEY'))
    if has_api:
        print("  Using Claude API for extraction\n")
    else:
        print("  No ANTHROPIC_API_KEY — using regex fallback\n")

    for dp in to_enrich:
        url = dp.get('sourceUrl', '')
        title = dp.get('claim', dp.get('notes', 'Untitled'))
        print(f"  📄 {title[:60]}")
        print(f"     URL: {url}")

        if not url:
            print("     ⚠ No URL — skipping")
            dp['status'] = 'pending'
            continue

        # Fetch page
        text = fetch_page_text(url)
        if not text or len(text) < 100:
            print(f"     ⚠ Could not fetch content ({len(text) if text else 0} chars)")
            dp['status'] = 'pending'
            continue

        print(f"     Fetched {len(text):,} chars")

        # Extract with regex (always)
        findings = extract_with_regex(text, title)
        print(f"     Regex: {len(findings['arr_mentions'])} ARR, {len(findings['valuation_mentions'])} valuation, "
              f"{len(findings['funding_mentions'])} funding, {len(findings['entities'])} entities")

        # Try Claude API
        claude_data = None
        if has_api and not dry_run:
            claude_data = enrich_with_claude(text, title, url)
            if claude_data:
                print(f"     Claude: {len(claude_data)} data points extracted")

        if not dry_run:
            build_data_point(dp, findings, claude_data, text)
            print(f"     ✅ Enriched → status=pending, value={dp.get('value')}, type={dp.get('sourceType')}")
        else:
            print(f"     [DRY RUN] Would enrich with {len(findings['arr_mentions'])} ARR mentions")

    if not dry_run:
        vault['meta']['lastUpdated'] = datetime.now().strftime('%Y-%m-%d')
        with open(VAULT_PATH, 'w') as f:
            json.dump(vault, f, indent=2)
        print(f"\n✅ Vault updated ({len(to_enrich)} entries enriched)")
    else:
        print(f"\n[DRY RUN] Would update {len(to_enrich)} entries")

    outputs["items_enriched"] = len(to_enrich) if not dry_run else 0
    outputs["items_to_enrich"] = len(to_enrich)
    outputs["dry_run"] = dry_run


if __name__ == '__main__':
    main()
