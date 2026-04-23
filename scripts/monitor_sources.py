#!/usr/bin/env python3
"""
Source monitor — checks registry for due sources and runs extraction.

Reads sources-registry.json, finds sources where next_check <= today,
runs the appropriate extraction adapter, saves claims to data-updates/.

Run: python3 scripts/monitor_sources.py
     python3 scripts/monitor_sources.py --dry-run
     python3 scripts/monitor_sources.py --force src-001  (force extract specific source)

Cron: daily 11:30am
"""

import json
import os
import re
import sys
import tempfile
from datetime import datetime, timedelta
from urllib.request import urlopen, Request
from urllib.error import URLError

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(BASE_DIR, 'sources-registry.json')
OUTPUT_DIR = os.path.join(BASE_DIR, 'data-updates')
LOG_FILE = os.path.join(BASE_DIR, 'data', 'monitor_sources.log')

FREQUENCY_DAYS = {
    'daily': 1, 'weekly': 7, 'monthly': 30, 'quarterly': 90, 'annual': 365, 'one_time': 99999,
}

SNAPSHOT_ROOT = os.path.join(BASE_DIR, 'data', 'snapshots')
EDGAR_TICKERS_FILE = os.path.join(BASE_DIR, 'data', 'edgar-tickers.json')


def save_snapshot(source, content, ext='html'):
    """Per data-sourcing-policy §6.4, persist the raw artefact of every retrieval
    to data/snapshots/<source_id>/<YYYY-MM-DD>/. Never lose the primary doc to a
    moved URL. content may be str (written as utf-8) or bytes (written raw)."""
    date = datetime.now().strftime('%Y-%m-%d')
    dest_dir = os.path.join(SNAPSHOT_ROOT, source['id'], date)
    os.makedirs(dest_dir, exist_ok=True)
    fname = f"{source['id']}.{ext}"
    mode = 'wb' if isinstance(content, (bytes, bytearray)) else 'w'
    path = os.path.join(dest_dir, fname)
    with open(path, mode) as f:
        f.write(content)
    return path


def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')


def fetch_page(url):
    """Fetch URL and return text content."""
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; AILedgerBot/1.0)'})
        with urlopen(req, timeout=20) as resp:
            html = resp.read().decode('utf-8', errors='replace')
        # Strip tags for text extraction
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'&[a-z]+;', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip(), html
    except Exception as e:
        log(f"  Fetch failed: {e}")
        return None, None


def fetch_pdf(url):
    """Download PDF and extract text."""
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, timeout=30) as resp:
            pdf_data = resp.read()
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(pdf_data)
            return tmp.name
    except Exception as e:
        log(f"  PDF download failed: {e}")
        return None


def extract_with_claude(text, source, max_chars=30000, language=None):
    """Use Claude API to extract claims from text.

    language: optional ISO code. When 'zh' (Chinese), uses a translation-aware
    prompt that emits English claims with the original-language excerpt
    preserved in a `source_excerpt_original` field per wq-015 §4.
    Defaults to the source's own `language` field, then 'en'.
    """
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        log("  No ANTHROPIC_API_KEY — skipping Claude extraction")
        return []

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
    except ImportError:
        log("  anthropic package not installed")
        return []

    if language is None:
        language = source.get('language', 'en')

    text_chunk = text[:max_chars]

    if language == 'zh':
        prompt = f"""The content below is in Chinese. Extract specific data points relevant to tracking AI industry economics.

Source: {source['title']} ({source['url']})
Type: {source['type']}
Language: Chinese (translate claim text to English; preserve the original Chinese excerpt verbatim).

Content:
{text_chunk}

For each data point, return a JSON object with:
- "claim": the specific statement, translated to English (1-2 sentences)
- "source_excerpt_original": the verbatim Chinese text the claim is translated from (do not translate this field)
- "category": provider_revenue | token_volume | pricing | gpu_infrastructure | enterprise_adoption | skeptical_bear_case | valuation_funding | other
- "entity": company or product name (canonical English form where possible; include Chinese original in parentheses the first time it appears)
- "metric": what is measured
- "value": numeric value or null
- "unit": USD, CNY, tokens, percent, etc
- "value_display": human-readable (e.g. "¥10B" or "$1.4B")
- "time_period": when this applies
- "confidence": high | medium | low
- "weight": authoritative | corroborating | indicative

Return a JSON array. Return [] if no relevant data points found.
Return ONLY the JSON array."""
    else:
        prompt = f"""Extract ALL specific data points from this content that are relevant to tracking AI industry economics.

Source: {source['title']} ({source['url']})
Type: {source['type']}

Content:
{text_chunk}

For each data point, return a JSON object with:
- "claim": the specific statement (1-2 sentences)
- "category": provider_revenue | token_volume | pricing | gpu_infrastructure | enterprise_adoption | skeptical_bear_case | valuation_funding | other
- "entity": company or product name
- "metric": what is measured (ARR, valuation, tokens/day, etc)
- "value": numeric value or null
- "unit": USD, tokens, percent, etc
- "value_display": human-readable (e.g. "$14B")
- "time_period": when this applies
- "confidence": high | medium | low
- "weight": authoritative | corroborating | indicative

Return a JSON array. Return [] if no relevant data points found.
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
        claims = json.loads(raw)
        if isinstance(claims, list):
            # Enrich with source metadata
            for c in claims:
                c['source_type'] = source['type']
                c['source_url'] = source['url']
                c['source_title'] = source['title']
                c['extracted_at'] = datetime.now().isoformat()
            return claims
    except Exception as e:
        log(f"  Claude extraction error: {e}")

    return []


def extract_google_slides(source):
    """Export Google Slides as PDF and extract."""
    url = source['url']
    # Extract presentation ID
    m = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if not m:
        log("  Could not extract presentation ID from URL")
        return []

    pres_id = m.group(1)
    pdf_url = f'https://docs.google.com/presentation/d/{pres_id}/export/pdf'
    log(f"  Exporting slides as PDF: {pdf_url}")

    pdf_path = fetch_pdf(pdf_url)
    if not pdf_path:
        # Fallback: try the published HTML
        log("  PDF export failed, trying stateof.ai HTML fallback")
        text, _ = fetch_page('https://www.stateof.ai/')
        if text:
            return extract_with_claude(text, source)
        return []

    # Extract text from PDF (basic approach — works for text-heavy slides)
    try:
        # Try pdfplumber or PyPDF2 if available
        try:
            import pdfplumber
            text = ''
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += (page.extract_text() or '') + '\n\n'
        except ImportError:
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(pdf_path)
                text = '\n\n'.join(page.extract_text() or '' for page in reader.pages)
            except ImportError:
                log("  No PDF library available (install pdfplumber or PyPDF2)")
                os.unlink(pdf_path)
                return []

        os.unlink(pdf_path)
        log(f"  Extracted {len(text):,} chars from PDF")

        if len(text) < 500:
            log("  PDF text too short — may be image-heavy slides")
            return []

        return extract_with_claude(text, source, max_chars=50000)

    except Exception as e:
        log(f"  PDF text extraction failed: {e}")
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)
        return []


def extract_web_page(source):
    """Fetch web page and extract claims. Honours source['language'] when set
    (e.g. 'zh' for 36Kr, Jiemian, CAC)."""
    text, html = fetch_page(source['url'])
    if not text or len(text) < 200:
        log(f"  Page content too short ({len(text) if text else 0} chars)")
        return []
    log(f"  Fetched {len(text):,} chars")
    # Snapshot the raw artefact before parsing (data-sourcing-policy §6.4)
    try:
        save_snapshot(source, html or text, ext='html')
    except Exception as e:
        log(f"  Snapshot failed: {e}")
    return extract_with_claude(text, source)


def extract_ir_page(source):
    """Hyperscaler IR pages (wq-015 §2.1). v1 is a thin wrapper over
    extract_web_page — it scrapes the HTML and runs the standard prompt.
    v2 should follow PDF links for earnings slides; noted in the brief's
    implementation log as follow-up."""
    log("  [ir_page_extract] v1 — HTML text only; PDF-slide follow TODO")
    return extract_web_page(source)


def extract_sec_edgar_scan(source):
    """SEC EDGAR multi-ticker scan (wq-015 §2.2). Iterates
    data/edgar-tickers.json, fetches each ticker's EDGAR filings-index page,
    and emits one lightweight claim per ticker describing the most recent
    filing. Does NOT fetch the filings themselves — the filings-catalogue
    pass is the trigger for a deeper per-filing extract, which Simon
    initiates manually after reviewing the catalogue."""
    if not os.path.exists(EDGAR_TICKERS_FILE):
        log(f"  {EDGAR_TICKERS_FILE} missing — cannot run SEC EDGAR scan")
        return []

    with open(EDGAR_TICKERS_FILE) as f:
        seed = json.load(f)
    tickers = seed.get('tickers', [])
    if not tickers:
        log("  edgar-tickers.json has no tickers")
        return []

    claims = []
    for t in tickers:
        cik = t.get('cik')
        ticker = t.get('ticker')
        if not cik:
            continue
        # EDGAR's browse-edgar endpoint returns an HTML filings catalogue per CIK
        url = (f'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany'
               f'&CIK={cik}&type=10-K,10-Q,8-K&dateb=&owner=include&count=5')
        text, html = fetch_page(url)
        if not text:
            log(f"  {ticker}: filings catalogue fetch failed")
            continue
        # Save per-ticker snapshot so the catalogue page is preserved
        try:
            ticker_src = dict(source)
            ticker_src['id'] = f"{source['id']}-{ticker}"
            save_snapshot(ticker_src, html or text, ext='html')
        except Exception as e:
            log(f"  {ticker}: snapshot failed: {e}")
        # Lightweight catalogue claim — no API call
        claims.append({
            'claim': f"SEC EDGAR filings catalogue fetched for {t.get('company', ticker)} ({ticker}).",
            'category': 'filings_catalogue',
            'entity': t.get('company', ticker),
            'metric': 'recent_filings',
            'value': None,
            'unit': 'filings',
            'value_display': 'catalogue',
            'time_period': datetime.now().strftime('%Y-%m-%d'),
            'confidence': 'high',
            'weight': 'authoritative',
            'source_type': source['type'],
            'source_url': url,
            'source_title': f"SEC EDGAR — {t.get('company', ticker)} filings catalogue",
            'extracted_at': datetime.now().isoformat(),
            'ticker': ticker,
            'cik': cik,
            'notes': t.get('why', ''),
        })
        log(f"  {ticker}: catalogue fetched")
    return claims


def extract_pdf_report(source):
    """Download PDF and extract claims."""
    pdf_path = fetch_pdf(source['url'])
    if not pdf_path:
        return []

    try:
        try:
            import pdfplumber
            text = ''
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages[:50]:  # Max 50 pages
                    text += (page.extract_text() or '') + '\n\n'
        except ImportError:
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(pdf_path)
                text = '\n\n'.join((page.extract_text() or '') for page in reader.pages[:50])
            except ImportError:
                log("  No PDF library available")
                os.unlink(pdf_path)
                return []

        os.unlink(pdf_path)
        log(f"  Extracted {len(text):,} chars from PDF")
        return extract_with_claude(text, source, max_chars=50000)

    except Exception as e:
        log(f"  PDF extraction error: {e}")
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)
        return []


# Extraction adapter dispatch
ADAPTERS = {
    'pdf_export': extract_google_slides,
    'pdf_extract': extract_pdf_report,
    'web_extract': extract_web_page,
    # Stream 1 (wq-015) adapters:
    'ir_page_extract': extract_ir_page,
    'sec_edgar_scan': extract_sec_edgar_scan,
    # These are handled by existing scripts, not this monitor:
    'podcast_scraper': lambda s: [],   # scrape_podcasts.py
    'signal_scraper': lambda s: [],    # scrape_signals.py
    'rss_feed': extract_web_page,      # fetch latest item
    'youtube_captions': lambda s: [],  # scrape_podcasts.py handles this
    'thread_extract': extract_web_page,
    'github_api': lambda s: [],        # enrich.py handles this
    'sec_extract': extract_web_page,   # legacy single-ticker path; sec_edgar_scan is the multi-ticker replacement
    'api_fetch': lambda s: [],         # scrape_signals.py handles this
}


def process_source(source, dry_run=False):
    """Process a single source through its extraction adapter."""
    log(f"\n📄 {source['title']} ({source['type']})")
    log(f"   Method: {source['extraction_method']}, URL: {source['url'][:80]}")

    if dry_run:
        log("   [DRY RUN] Would extract")
        return 0

    adapter = ADAPTERS.get(source['extraction_method'])
    if not adapter:
        log(f"   Unknown extraction method: {source['extraction_method']}")
        return 0

    claims = adapter(source)
    log(f"   Extracted {len(claims)} claim(s)")

    if claims:
        # Save to data-updates
        today = datetime.now().strftime('%Y-%m-%d')
        output_path = os.path.join(OUTPUT_DIR, f'{today}-source-{source["id"]}.json')
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(claims, f, indent=2)
        log(f"   Saved to {output_path}")

    return len(claims)


def main():
    dry_run = '--dry-run' in sys.argv
    force_id = None
    if '--force' in sys.argv:
        idx = sys.argv.index('--force')
        force_id = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None

    today_str = datetime.now().strftime('%Y-%m-%d')
    log(f"\n{'='*60}")
    log(f"📡 Source Monitor — {today_str}")

    if not os.path.exists(REGISTRY_PATH):
        log("  No sources-registry.json found")
        return

    with open(REGISTRY_PATH) as f:
        registry = json.load(f)

    sources = registry['sources']
    log(f"  Registry: {len(sources)} sources")

    # Find due sources
    due = []
    for s in sources:
        if force_id and s['id'] != force_id:
            continue
        if force_id:
            due.append(s)
            continue
        if s['status'] == 'disabled':
            continue
        next_check = s.get('next_check', '2099-01-01')
        if next_check <= today_str:
            due.append(s)

    log(f"  Due for extraction: {len(due)}")

    if not due:
        log("  Nothing due today")
        return

    total_claims = 0
    for source in due:
        claims_count = process_source(source, dry_run)
        total_claims += claims_count

        if not dry_run:
            # Update registry
            source['last_checked'] = today_str
            source['last_claims_count'] = claims_count
            source['status'] = 'active' if claims_count >= 0 else 'error'
            # Set next check
            freq_days = FREQUENCY_DAYS.get(source['frequency'], 7)
            source['next_check'] = (datetime.now() + timedelta(days=freq_days)).strftime('%Y-%m-%d')

    if not dry_run:
        registry['meta']['lastUpdated'] = today_str
        with open(REGISTRY_PATH, 'w') as f:
            json.dump(registry, f, indent=2)

    log(f"\n{'='*60}")
    log(f"✅ Done — {len(due)} sources processed, {total_claims} total claims extracted")


if __name__ == '__main__':
    main()
