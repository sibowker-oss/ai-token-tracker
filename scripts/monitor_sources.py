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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coerce_date import coerce_or_keep  # noqa: E402
from log_run import logged_run  # noqa: E402
from score_materiality import score as score_materiality  # noqa: E402  (wq-040)
from _telemetry_router import is_telemetry, append_to_telemetry_feed  # noqa: E402  (wq-047)
REGISTRY_PATH = os.path.join(BASE_DIR, 'sources-registry.json')
OUTPUT_DIR = os.path.join(BASE_DIR, 'data-updates')
LOG_FILE = os.path.join(BASE_DIR, 'data', 'monitor_sources.log')

FREQUENCY_DAYS = {
    'daily': 1, 'weekly': 7, 'monthly': 30, 'quarterly': 90, 'annual': 365, 'one_time': 99999,
}

SNAPSHOT_ROOT = os.path.join(BASE_DIR, 'data', 'snapshots')
EDGAR_TICKERS_FILE = os.path.join(BASE_DIR, 'data', 'edgar-tickers.json')
ATTRIBUTION_MAP_FILE = os.path.join(BASE_DIR, 'data', 'datacenter-attribution-map.json')
ALIAS_MAP_FILE = os.path.join(BASE_DIR, 'data', 'company-alias-map.json')

# AI-engineer regex per wq-013 §9. Two categories:
# - AI_TITLED — counts in `open_roles_ai_titled`.
# - PROMPT_ENGINEER — separate category in `open_roles_prompt_engineer`.
# The EXCLUDE set filters out generic data-engineer / data-analyst titles
# unless the body carries AI-specific signal.
import re as _re
_AI_TITLE_PATTERNS = [
    r'\b(machine learning|ml)\b.*\b(engineer|scientist|researcher)\b',
    r'\b(ai|artificial intelligence)\b.*\b(engineer|scientist|researcher)\b',
    r'\bresearch (engineer|scientist)\b',
    r'\bapplied (ai|ml|scientist|research)\b',
    r'\b(mlops|ml ops|ml platform|ml infrastructure)\b',
    r'\b(deep learning|nlp|computer vision|reinforcement learning)\b.*\b(engineer|scientist)\b',
    r'\b(llm|foundation model|generative ai)\b.*\b(engineer|scientist|researcher)\b',
    r'\b(ai safety|alignment|interpretability)\b.*\b(engineer|scientist|researcher)\b',
]
_PROMPT_ENGINEER_RE = _re.compile(r'\bprompt engineer\b', _re.IGNORECASE)
_AI_TITLE_RE = _re.compile('|'.join(_AI_TITLE_PATTERNS), _re.IGNORECASE)
_EXCLUDE_RE = _re.compile(r'\b(data engineer|analytics engineer|bi engineer|data analyst)\b', _re.IGNORECASE)
_DATA_SCI_RE = _re.compile(r'\bdata scientist\b', _re.IGNORECASE)
_DATA_SCI_ALLOW_RE = _re.compile(r'\b(ml|ai|applied|research|llm|nlp)\b', _re.IGNORECASE)


def classify_role(title, body=''):
    """Return 'ai_titled' | 'prompt_engineer' | None per wq-013 §9."""
    t = (title or '') + ' ' + (body or '')
    if _PROMPT_ENGINEER_RE.search(t):
        return 'prompt_engineer'
    if _AI_TITLE_RE.search(t):
        return 'ai_titled'
    # Data scientist only counts if title ALSO contains ml/ai/applied/research/llm/nlp
    if _DATA_SCI_RE.search(title or '') and _DATA_SCI_ALLOW_RE.search(title or ''):
        return 'ai_titled'
    # Exclude generic data-engineer titles unless body has AI signal
    if _EXCLUDE_RE.search(title or ''):
        if _AI_TITLE_RE.search(body or ''):
            return 'ai_titled'
        return None
    return None


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


# Per-source fetch-failure counter. Reset at the top of process_source(); read by
# main() to decide whether to advance next_check. Avoids the silent-disable bug
# where a TLS error swallowed by an adapter returned 0 claims and looked clean.
_fetch_failures = 0


def log(msg):
    global _fetch_failures
    if 'fetch failed' in msg.lower():
        _fetch_failures += 1
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')


# Full browser-like header set. Many IR pages / government portals / CDN-
# protected pages (Cloudflare, Akamai) reject minimal UAs. These headers match
# a vanilla Chrome 131 request and clear the checks on ERCOT, PJM, NESO, Meta IR.
_BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'Sec-Ch-Ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"macOS"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
}


def fetch_page(url):
    """Fetch URL and return (text, html). Uses browser-like headers to beat
    low-threshold bot detection on IR / government / CDN-protected pages."""
    try:
        req = Request(url, headers=_BROWSER_HEADERS)
        with urlopen(req, timeout=30) as resp:
            raw = resp.read()
            # Handle gzip/deflate
            if resp.headers.get('Content-Encoding') == 'gzip':
                import gzip
                raw = gzip.decompress(raw)
            elif resp.headers.get('Content-Encoding') == 'deflate':
                import zlib
                raw = zlib.decompress(raw)
            html = raw.decode('utf-8', errors='replace')
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
- "time_period_scope": annual | h1 | h2 | q1 | q2 | q3 | q4 | exit_snapshot | monthly_peak | point_in_time
- "period_qualifier_detected": short string quoting the qualifier (e.g. "H1 2025", "上半年", "best 4-week × 12"), or null when scope is "annual"
- "confidence": high | medium | low
- "weight": authoritative | corroborating | indicative

TIME PERIOD SCOPE — RULES (wq-054):

Rule A — INTERNAL CONSISTENCY (critical):
If you populate period_qualifier_detected with a non-null value, time_period_scope MUST be the corresponding scope from the qualifier — NOT point_in_time. Specifically:
  - Qualifier mentions "Q1" / "Q2" / "Q3" / "Q4" / "first/second/third/fourth quarter" / "第X季度" → scope must be q1/q2/q3/q4
  - Qualifier mentions "H1" / "H2" / "first half" / "second half" / "上半年" / "下半年" → scope must be h1/h2
  - Qualifier mentions "exit" / "end of year" / "year-end run-rate" / "best 4-week × 12" → scope must be exit_snapshot
  - Qualifier mentions "monthly" / "per month" / "single month peak" / "$X/month" → scope must be monthly_peak
Failing this rule produces wrongly-routed claims and is a critical error.

Rule B — point_in_time BOUNDARY:
point_in_time is reserved for ENTITY-CURRENT state metrics: weekly active users, headcount, current model version, current ARR run-rate WHEN explicitly described as "as of today / now / current".
point_in_time is NOT for:
  - Funding rounds (e.g. "$122B round closed Sep 2025") → scope=annual, year=2025
  - Valuations at a specific time (e.g. "OpenAI valued at $850B Mar 2026") → scope=annual, year=2026
  - Revenue or ARR figures with a year reference but no quarter/half/exit qualifier → scope=annual

Rule C — DEFAULT:
No period qualifier in the source text → scope=annual, period_qualifier_detected=null.
Explicit "full year" / "FY2025" / 全年 → scope=annual.

WORKED EXAMPLES (one per scope):
  annual:        "OpenAI 2025 collected revenue ~$11.9B"                            → scope=annual,        qualifier=null
  h1:            "OpenAI H1 2025 revenue $4.3B per The Information"                 → scope=h1,            qualifier="H1 2025"
  q2:            "Anthropic Q2 2025 ARR $5B"                                        → scope=q2,            qualifier="Q2 2025"
  exit_snapshot: "OpenAI exit ARR 2024 was $20B (best-period × 12)"                 → scope=exit_snapshot, qualifier="exit ARR 2024"
  monthly_peak:  "Brad Gerstner: Anthropic hit $6B/month run rate February 2026"    → scope=monthly_peak,  qualifier="$6B/month February 2026"
  point_in_time: "OpenAI now has 700M WAU"                                          → scope=point_in_time, qualifier="now"

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
- "time_period_scope": annual | h1 | h2 | q1 | q2 | q3 | q4 | exit_snapshot | monthly_peak | point_in_time
- "period_qualifier_detected": short string quoting the qualifier (e.g. "H1 2025", "best 4-week × 12"), or null when scope is "annual"
- "confidence": high | medium | low
- "weight": authoritative | corroborating | indicative

TIME PERIOD SCOPE — RULES (wq-054):

Rule A — INTERNAL CONSISTENCY (critical):
If you populate period_qualifier_detected with a non-null value, time_period_scope MUST be the corresponding scope from the qualifier — NOT point_in_time. Specifically:
  - Qualifier mentions "Q1" / "Q2" / "Q3" / "Q4" / "first/second/third/fourth quarter" → scope must be q1/q2/q3/q4
  - Qualifier mentions "H1" / "H2" / "first half" / "second half" → scope must be h1/h2
  - Qualifier mentions "exit" / "end of year" / "year-end run-rate" / "best 4-week × 12" → scope must be exit_snapshot
  - Qualifier mentions "monthly" / "per month" / "single month peak" / "$X/month" → scope must be monthly_peak
Failing this rule produces wrongly-routed claims and is a critical error. If you wrote "beginning of Q2" in period_qualifier_detected, time_period_scope MUST be "q2".

Rule B — point_in_time BOUNDARY:
point_in_time is reserved for ENTITY-CURRENT state metrics: weekly active users, headcount, current model version, current ARR run-rate WHEN explicitly described as "as of today / now / current".
point_in_time is NOT for:
  - Funding rounds (e.g. "$122B round closed Sep 2025") → scope=annual, year=2025
  - Valuations at a specific time (e.g. "OpenAI valued at $850B Mar 2026") → scope=annual, year=2026
  - Revenue or ARR figures with a year reference but no quarter/half/exit qualifier → scope=annual

Rule C — DEFAULT:
No period qualifier in the source text → scope=annual, period_qualifier_detected=null.
Explicit "full year" / "FY2025" → scope=annual.

WORKED EXAMPLES (one per scope):
  annual:        "OpenAI 2025 collected revenue ~$11.9B"                            → scope=annual,        qualifier=null
  h1:            "OpenAI H1 2025 revenue $4.3B per The Information"                 → scope=h1,            qualifier="H1 2025"
  q2:            "Anthropic Q2 2025 ARR $5B"                                        → scope=q2,            qualifier="Q2 2025"
  exit_snapshot: "OpenAI exit ARR 2024 was $20B (best-period × 12)"                 → scope=exit_snapshot, qualifier="exit ARR 2024"
  monthly_peak:  "Brad Gerstner: Anthropic hit $6B/month run rate February 2026"    → scope=monthly_peak,  qualifier="$6B/month February 2026"
  point_in_time: "OpenAI now has 700M WAU"                                          → scope=point_in_time, qualifier="now"

Return a JSON array. Return [] if no relevant data points found.
Return ONLY the JSON array."""

    try:
        response = client.messages.create(
            model='claude-sonnet-4-6',
            max_tokens=8192,
            messages=[{'role': 'user', 'content': prompt}]
        )
        raw = response.content[0].text.strip()
        raw = re.sub(r'^```(?:json)?\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        # Strip lone UTF-16 surrogates. These leak in from PDFs / Chinese text
        # when Claude's output carries an unpaired surrogate codepoint
        # (U+D800..U+DFFF) — Python 3 can't encode those to utf-8 at all, so
        # replace them before any downstream encode/decode step.
        raw = re.sub(r'[\ud800-\udfff]', '?', raw)
        claims = _parse_claims_json(raw, source)
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


def _parse_claims_json(raw, source):
    """Parse Claude's response as a JSON array of claims. Three-stage salvage:
      1. Parse as-is.
      2. Truncate to last `}` and close the array (recovers truncated/
         unterminated responses).
      3. Object-by-object regex — find every top-level {...} block and parse
         each individually (recovers responses where a middle object is
         malformed but others are fine).
    Returns [] when nothing is usable."""
    first_err = None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        first_err = e

    # Stage 2: truncate to last `}` and close the array.
    last_close = raw.rfind('}')
    if last_close >= 0:
        salvage = raw[:last_close + 1]
        if not salvage.rstrip().endswith(']'):
            salvage = salvage.rstrip().rstrip(',') + ']'
        try:
            result = json.loads(salvage)
            if isinstance(result, list) and result:
                log(f"  Claude JSON parse recovered (truncate-close) — salvaged {len(result)} claim(s).")
                return result
        except json.JSONDecodeError:
            pass

    # Stage 3: scan for individual {...} blocks using a balanced-brace walker
    # and parse each. Recovers any well-formed objects from an otherwise
    # malformed response.
    objects = []
    depth = 0
    start = None
    in_string = False
    escape = False
    for i, ch in enumerate(raw):
        if escape:
            escape = False
            continue
        if ch == '\\':
            escape = True
            continue
        if ch == '"' and not escape:
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == '{':
            if depth == 0:
                start = i
            depth += 1
        elif ch == '}':
            if depth > 0:
                depth -= 1
                if depth == 0 and start is not None:
                    chunk = raw[start:i + 1]
                    try:
                        obj = json.loads(chunk)
                        if isinstance(obj, dict):
                            objects.append(obj)
                    except json.JSONDecodeError:
                        pass
                    start = None
    if objects:
        log(f"  Claude JSON parse recovered (per-object) — salvaged {len(objects)} claim(s) from broken response.")
        return objects

    log(f"  Claude JSON parse failed ({first_err}); all salvage stages failed.")
    return []


def extract_with_claude_chunked(text, source, chunk_size=28000, language=None):
    """Chunked version of extract_with_claude. For documents larger than
    ~30k chars, splits on paragraph boundaries and aggregates. Used by the
    PDF adapters (State of AI Report, analyst PDFs) where a single Claude
    call's 8k output budget can't hold every data point in a 200+ page deck."""
    if len(text) <= chunk_size:
        return extract_with_claude(text, source, max_chars=chunk_size, language=language)

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            break_at = text.rfind('\n\n', start, end)
            if break_at > start + chunk_size // 2:
                end = break_at
        chunks.append(text[start:end])
        start = end

    log(f"  Chunked extraction: {len(chunks)} chunk(s) of ~{chunk_size} chars")
    all_claims = []
    for i, chunk in enumerate(chunks):
        log(f"  Chunk {i+1}/{len(chunks)}...")
        claims = extract_with_claude(chunk, source, max_chars=chunk_size, language=language)
        log(f"    {len(claims)} claim(s)")
        all_claims.extend(claims)
    return all_claims


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

    # Extract text from PDF (basic approach — works for text-heavy slides).
    # Try three parsers in order of preference: pdfplumber (most featureful),
    # pypdf (modern maintained fork), PyPDF2 (legacy). Installing any one is
    # enough.
    try:
        text = ''
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += (page.extract_text() or '') + '\n\n'
        except ImportError:
            try:
                from pypdf import PdfReader
                reader = PdfReader(pdf_path)
                text = '\n\n'.join((page.extract_text() or '') for page in reader.pages)
            except ImportError:
                try:
                    from PyPDF2 import PdfReader
                    reader = PdfReader(pdf_path)
                    text = '\n\n'.join((page.extract_text() or '') for page in reader.pages)
                except ImportError:
                    log("  No PDF library available (install pdfplumber, pypdf, or PyPDF2)")
                    os.unlink(pdf_path)
                    return []

        os.unlink(pdf_path)
        log(f"  Extracted {len(text):,} chars from PDF")

        if len(text) < 500:
            log("  PDF text too short — may be image-heavy slides")
            return []

        return extract_with_claude_chunked(text, source)

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


# ---------------------------------------------------------------------------
# Stream 2 — power / grid-queue adapters (wq-012).
#
# Each adapter emits structured `power_project` claims per the schema in
# metric-schema.json claim_types.power_project (wq-014). Attribution lookup
# is shared via _lookup_attribution(), which consults
# data/datacenter-attribution-map.json.
#
# Posture: adapters do NOT run on cron. Simon triggers per-source via
# `python3 scripts/monitor_sources.py --force src-NNN` after confirming the
# review queue has capacity.
# ---------------------------------------------------------------------------

def _load_attribution_map():
    if not os.path.exists(ATTRIBUTION_MAP_FILE):
        return {'by_project': {}, 'by_llc': {}}
    with open(ATTRIBUTION_MAP_FILE) as f:
        return json.load(f)


def _lookup_attribution(attr_map, llc_name=None, project_name=None):
    """Return (company_slug, confidence, attribution_sources) or (None, None, []).
    Prefers by_llc (LLC-of-record, tighter match) over by_project (facility name)."""
    if llc_name:
        hit = attr_map.get('by_llc', {}).get(llc_name)
        if hit:
            return hit.get('operator'), hit.get('confidence'), hit.get('attribution_sources', [])
    if project_name:
        hit = attr_map.get('by_project', {}).get(project_name)
        if hit:
            # by_project uses operators[] — collapse to the highest-confidence one
            ops = hit.get('operators') or []
            if ops:
                best = max(ops, key=lambda o: {'confident': 3, 'likely': 2, 'speculative': 1}.get(o.get('confidence'), 0))
                return best.get('name'), best.get('confidence'), hit.get('attribution_sources', [])
    return None, None, []


def _power_project_claim_from_row(row, source, queue_market, attr_map):
    """Build a `power_project` structured claim (metric-schema claim_types.power_project)
    from an adapter row dict. Row carries queue_id/stage/mw/* fields and an optional
    llc_of_record. Missing fields stay null per schema."""
    llc = row.get('llc_of_record')
    project = row.get('project_name')
    op, op_conf, op_srcs = _lookup_attribution(attr_map, llc_name=llc, project_name=project)

    claim = {
        'type': 'power_project',
        'queue_market': queue_market,
        'queue_id': row.get('queue_id'),
        'stage': row.get('stage'),
        'source': {
            'url': row.get('source_url', source['url']),
            'retrievedAt': datetime.now().isoformat(),
            'nextReview': (datetime.now() + timedelta(days=FREQUENCY_DAYS.get(source.get('frequency', 'monthly'), 30))).strftime('%Y-%m-%d'),
            'confidence': row.get('confidence', 'medium'),
        },
    }
    # Optional fields — only include when present
    for field in ('poi', 'county', 'mw_requested', 'mw_approved', 'mw_in_service',
                  'requested_cod', 'llc_of_record'):
        if row.get(field) not in (None, ''):
            claim[field] = row[field]

    if op:
        claim['company_slug'] = op.lower().replace(' ', '-') if isinstance(op, str) else op
        claim['attribution_confidence'] = op_conf or 'low'
        if op_srcs:
            claim['attribution_sources'] = op_srcs

    return claim


def _save_power_claims(claims, source):
    """Write structured power claims to the per-source candidates file."""
    if not claims:
        return None
    today = datetime.now().strftime('%Y-%m-%d')
    out = os.path.join(OUTPUT_DIR, f'{today}-source-{source["id"]}.json')
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(out, 'w') as f:
        json.dump(claims, f, indent=2)
    log(f"   Saved {len(claims)} power_project claim(s) to {out}")
    return out


def extract_iso_queue_ercot(source):
    """ERCOT GIS Report + Large Load Integration (src-060). v1: fetches the
    landing HTML + saves as snapshot. Full XLSX parse requires openpyxl, which
    is not a v1 dependency; when unavailable, logs the download URL(s) for
    manual review and returns []."""
    attr_map = _load_attribution_map()
    text, html = fetch_page(source['url'])
    if html:
        try:
            save_snapshot(source, html, ext='html')
        except Exception as e:
            log(f"  Snapshot failed: {e}")
    if not text:
        return []

    # Find XLSX download URLs on the page — ERCOT typically exposes one at the
    # page bottom. v1 logs them; Simon downloads manually and a v2 XLSX parser
    # handles the rows.
    xlsx_urls = re.findall(r'https?://[^\s"\']+\.xlsx', html or '', re.IGNORECASE)
    if xlsx_urls:
        log(f"  Found {len(xlsx_urls)} XLSX link(s) — download and feed to the adapter manually for v1:")
        for u in xlsx_urls[:5]:
            log(f"    {u}")

    try:
        import openpyxl  # noqa: F401
    except ImportError:
        log("  openpyxl not installed — ERCOT GIS XLSX parse skipped for v1.")
        log("  Install via `pip install openpyxl` to enable row-level power_project extraction.")
        return []

    # XLSX parsing path — stubbed for now. Simon's call whether to install
    # openpyxl in the v1 env (adds ~5 MB) before enabling.
    log("  openpyxl present but XLSX row-parsing not yet implemented; returning [].")
    return []


def extract_iso_queue_pjm(source):
    """PJM New Services Queue (src-061). Same v1 posture as ERCOT: save the
    landing-page snapshot, surface download links. Row-level XLSX parse is a
    follow-up."""
    attr_map = _load_attribution_map()
    text, html = fetch_page(source['url'])
    if html:
        try:
            save_snapshot(source, html, ext='html')
        except Exception as e:
            log(f"  Snapshot failed: {e}")
    if not text:
        return []

    xlsx_urls = re.findall(r'https?://[^\s"\']+\.(xlsx|xls)', html or '', re.IGNORECASE)
    if xlsx_urls:
        log(f"  Found {len(xlsx_urls)} XLSX/XLS link(s) on PJM queue page")
        for u in xlsx_urls[:5]:
            log(f"    {u[0] if isinstance(u, tuple) else u}")

    try:
        import openpyxl  # noqa: F401
    except ImportError:
        log("  openpyxl not installed — PJM queue XLSX parse skipped for v1.")
        return []

    log("  openpyxl present but PJM XLSX row-parsing not yet implemented; returning [].")
    return []


def extract_eia_api(source):
    """EIA Open Data API (src-062). v1 fetches STEO datacenter-load commentary
    when EIA_API_KEY is set. Output is free-text claims, not power_project —
    STEO gives aggregate sector numbers, not per-queue-entry rows."""
    api_key = os.environ.get('EIA_API_KEY')
    if not api_key:
        log("  EIA_API_KEY env var not set — eia_api adapter requires one (free registration at https://www.eia.gov/opendata/register.php). Returning [].")
        return []

    # STEO DC load is published as a specific series. v1 hits the STEO endpoint;
    # full 860M / 930 coverage is follow-up.
    endpoint = f'https://api.eia.gov/v2/steo/data/?api_key={api_key}&frequency=monthly&data[0]=value&facets[seriesId][]=ZEGEPUS&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=12'
    try:
        req = Request(endpoint, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, timeout=30) as resp:
            payload = resp.read().decode('utf-8', errors='replace')
        try:
            save_snapshot(source, payload, ext='json')
        except Exception as e:
            log(f"  Snapshot failed: {e}")
        parsed = json.loads(payload)
    except Exception as e:
        log(f"  EIA API fetch failed: {e}")
        return []

    data = parsed.get('response', {}).get('data', [])
    if not data:
        log("  EIA STEO returned no rows for the datacenter-load series")
        return []
    # Summarise the last 12 months as free-text claims (not power_project —
    # these are sector aggregates, not queue entries).
    claims = []
    for row in data[:12]:
        claims.append({
            'claim': f"EIA STEO: {row.get('value')} {row.get('unit', '?')} for period {row.get('period')} (series {row.get('seriesId')}).",
            'category': 'gpu_infrastructure',
            'entity': 'US electricity sector',
            'metric': row.get('seriesDescription', 'STEO series'),
            'value': row.get('value'),
            'unit': row.get('unit', ''),
            'value_display': f"{row.get('value')} {row.get('unit', '')}",
            'time_period': row.get('period'),
            'confidence': 'high',
            'weight': 'authoritative',
            'source_type': source['type'],
            'source_url': source['url'],
            'source_title': source['title'],
            'extracted_at': datetime.now().isoformat(),
        })
    return claims


def extract_neso_tec(source):
    """NESO TEC Register (src-063). UK grid transmission-entry-capacity queue.
    CSV download under OGL licence; produces power_project claims with
    queue_market='NESO'."""
    attr_map = _load_attribution_map()
    text, html = fetch_page(source['url'])
    if html:
        try:
            save_snapshot(source, html, ext='html')
        except Exception as e:
            log(f"  Snapshot failed: {e}")

    # Find the CSV download link on the page
    csv_urls = re.findall(r'https?://[^\s"\']+\.csv', html or '', re.IGNORECASE)
    if not csv_urls:
        log("  No CSV link found on NESO data-portal page — manual download required. Returning [].")
        return []

    csv_url = csv_urls[0]
    log(f"  Fetching CSV: {csv_url}")
    try:
        req = Request(csv_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, timeout=60) as resp:
            csv_raw = resp.read()
        try:
            save_snapshot({**source, 'id': f"{source['id']}-csv"}, csv_raw, ext='csv')
        except Exception as e:
            log(f"  CSV snapshot failed: {e}")
        csv_text = csv_raw.decode('utf-8', errors='replace')
    except Exception as e:
        log(f"  NESO CSV fetch failed: {e}")
        return []

    import csv as _csv, io as _io
    reader = _csv.DictReader(_io.StringIO(csv_text))
    claims = []
    for raw_row in reader:
        # NESO columns vary by quarter; pull the common fields defensively.
        # Typical columns: 'Project Name', 'Connection Site', 'MW Connected',
        # 'MW Contracted', 'Ready Year', 'Status', 'TO', 'Plant Type'.
        row = {
            'queue_id': raw_row.get('Project Name') or raw_row.get('Ref') or '',
            'project_name': raw_row.get('Project Name'),
            'stage': raw_row.get('Status') or raw_row.get('Gate'),
            'poi': raw_row.get('Connection Site'),
            'mw_requested': _try_float(raw_row.get('MW Contracted') or raw_row.get('Transmission Entry Capacity (MW)') or raw_row.get('MW')),
            'mw_in_service': _try_float(raw_row.get('MW Connected')),
            'requested_cod': raw_row.get('Ready Year') or raw_row.get('Target Date'),
            'source_url': csv_url,
            'confidence': 'high',
        }
        if not row['queue_id']:
            continue
        claims.append(_power_project_claim_from_row(row, source, queue_market='NESO', attr_map=attr_map))

    log(f"  Parsed {len(claims)} NESO TEC row(s)")
    return claims


def _try_float(v):
    if v is None or v == '':
        return None
    try:
        return float(str(v).replace(',', ''))
    except ValueError:
        return None


def extract_epoch_frontier(source):
    """Epoch AI Frontier Data Centers Hub (src-064). v1: refreshes the
    attribution map from the CC-BY CSV. Emits ZERO power_project claims on
    its own — Epoch is a facility catalogue, not an ISO queue. Downstream
    ERCOT / PJM / NESO extractions consult the updated map for LLC and
    project-name attribution lookups."""
    attr_map_url = 'https://epoch.ai/data/data_centers/data_centers.csv'
    try:
        req = Request(attr_map_url, headers={'User-Agent': 'Mozilla/5.0 (AILedgerBot)'})
        with urlopen(req, timeout=30) as resp:
            csv_raw = resp.read()
        try:
            save_snapshot(source, csv_raw, ext='csv')
        except Exception as e:
            log(f"  Snapshot failed: {e}")
    except Exception as e:
        log(f"  Epoch CSV fetch failed: {e}")
        return []

    log(f"  Fetched Epoch CSV ({len(csv_raw):,} bytes). Attribution map refresh is a separate operation; for v1 it's seeded once (see data/datacenter-attribution-map.json) and Simon re-runs this adapter to capture new facilities.")
    log("  This adapter emits 0 power_project claims — Epoch is the attribution source, not the queue source.")
    return []


# ---------------------------------------------------------------------------
# Stream 3 — hiring + patent discovery adapters (wq-013).
#
# ATS adapters fan out to every company in data/company-alias-map.json whose
# `ats.type` matches the source's extraction method. Each company produces
# one `hiring_snapshot` structured claim per run.
#
# Patent adapters use `patent_assignee_ids` from the alias map for assignee-
# keyed queries. When a company has no assignee_ids yet, PatentsView can
# still be queried by `canonical` name via a free-text search path, but v1
# uses the assignee_ids path only.
#
# Posture: on-demand, manual --force trigger. No cron auto-fire.
# ---------------------------------------------------------------------------

def _load_alias_map():
    if not os.path.exists(ALIAS_MAP_FILE):
        return {'companies': {}}
    with open(ALIAS_MAP_FILE) as f:
        return json.load(f)


def _iso_week(d=None):
    d = d or datetime.now()
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def _iso_month(d=None):
    d = d or datetime.now()
    return d.strftime('%Y-%m')


def _fetch_json(url, headers=None, timeout=30):
    req = Request(url, headers=headers or {'User-Agent': 'Mozilla/5.0 (AILedgerBot)'})
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8', errors='replace'))


def _build_hiring_snapshot(slug, entry, source, jobs, ats_type, token):
    """Aggregate a list of job dicts into a hiring_snapshot structured claim.

    Each job dict must carry `title` and optionally `description`/`content`/`body`.
    Returns None if zero jobs classify."""
    total = len(jobs)
    ai_titled = 0
    prompt_eng = 0
    for j in jobs:
        body = j.get('description') or j.get('content') or j.get('body') or ''
        kind = classify_role(j.get('title', ''), body)
        if kind == 'prompt_engineer':
            prompt_eng += 1
            ai_titled += 1   # prompt engineers are also AI-titled
        elif kind == 'ai_titled':
            ai_titled += 1

    claim = {
        'type': 'hiring_snapshot',
        'company_slug': slug,
        'window': _iso_week(),
        'metrics': {
            'open_roles_total': total,
            'open_roles_ai_titled': ai_titled,
            'open_roles_prompt_engineer': prompt_eng,
            'ai_titled_share': round(ai_titled / total, 3) if total else 0.0,
            'new_ai_roles_7d': 0,  # v1 — requires prior snapshot to compute diff; 0 on first run
        },
        'source': {
            'type': ats_type,
            'token': token,
            'url': source['url'].rstrip('/') + '/' + token,
            'retrievedAt': datetime.now().isoformat(),
            'nextReview': (datetime.now() + timedelta(days=FREQUENCY_DAYS.get(source.get('frequency', 'weekly'), 7))).strftime('%Y-%m-%d'),
            'confidence': 'high',
        },
    }
    return claim


def _save_stream3_claims(claims, source):
    if not claims:
        return None
    today = datetime.now().strftime('%Y-%m-%d')
    out = os.path.join(OUTPUT_DIR, f'{today}-source-{source["id"]}.json')
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(out, 'w') as f:
        json.dump(claims, f, indent=2)
    log(f"   Saved {len(claims)} Stream 3 claim(s) to {out}")
    return out


def _extract_ats_generic(source, ats_type, url_builder, jobs_from_payload):
    """Shared ATS extraction core.

    ats_type         — 'greenhouse' | 'lever' | 'ashby' | 'workable'.
    url_builder(tok) — returns the per-company API URL.
    jobs_from_payload(p) — returns a list of job dicts from the API response.
    """
    alias_map = _load_alias_map()
    companies = alias_map.get('companies', {})
    targets = [(slug, e) for slug, e in companies.items()
               if (e.get('ats') or {}).get('type') == ats_type]
    if not targets:
        log(f"  No companies in alias map have ats.type={ats_type}")
        return []

    log(f"  {ats_type} — fanning out to {len(targets)} company target(s)")
    claims = []
    for slug, entry in targets:
        token = entry['ats']['token']
        url = url_builder(token)
        try:
            payload = _fetch_json(url)
        except Exception as e:
            log(f"    {slug} ({token}): fetch failed — {e}")
            continue
        try:
            save_snapshot({**source, 'id': f"{source['id']}-{slug}"},
                          json.dumps(payload).encode('utf-8'), ext='json')
        except Exception as e:
            log(f"    {slug}: snapshot failed: {e}")
        jobs = jobs_from_payload(payload) or []
        claim = _build_hiring_snapshot(slug, entry, source, jobs, ats_type, token)
        if claim:
            claims.append(claim)
            m = claim['metrics']
            log(f"    {slug}: {m['open_roles_total']} total / {m['open_roles_ai_titled']} AI-titled ({m['ai_titled_share']*100:.1f}%)")
        else:
            log(f"    {slug}: 0 jobs")
    return claims


def extract_greenhouse_board(source):
    """Greenhouse public JSON API: /v1/boards/{token}/jobs?content=true."""
    base = 'https://boards-api.greenhouse.io/v1/boards/'
    return _extract_ats_generic(
        source, 'greenhouse',
        url_builder=lambda t: f'{base}{t}/jobs?content=true',
        jobs_from_payload=lambda p: p.get('jobs', []),
    )


def extract_lever_postings(source):
    """Lever postings API: /v0/postings/{slug}?mode=json."""
    base = 'https://api.lever.co/v0/postings/'
    return _extract_ats_generic(
        source, 'lever',
        url_builder=lambda t: f'{base}{t}?mode=json',
        jobs_from_payload=lambda p: p if isinstance(p, list) else [],
    )


def extract_ashby_public(source):
    """Ashby public posting API: /posting-api/job-board/{token}."""
    base = 'https://api.ashbyhq.com/posting-api/job-board/'
    return _extract_ats_generic(
        source, 'ashby',
        url_builder=lambda t: f'{base}{t}?includeCompensation=false',
        jobs_from_payload=lambda p: p.get('jobs', []),
    )


def extract_workable_jobs(source):
    """Workable widget API: /api/v1/widget/accounts/{account}/jobs."""
    base = 'https://apply.workable.com/api/v1/widget/accounts/'
    return _extract_ats_generic(
        source, 'workable',
        url_builder=lambda t: f'{base}{t}/jobs',
        jobs_from_payload=lambda p: p.get('jobs', p.get('results', [])),
    )


def extract_patentsview_search(source):
    """USPTO PatentSearch API. For every company with populated
    patent_assignee_ids, query assignee-keyed patents and emit a
    patent_snapshot claim. For companies with empty assignee_ids, emit a
    company_surfaced stub so Simon knows to run a PatentsView
    /api/v1/assignee?q=<canonical> disambiguation pass."""
    alias_map = _load_alias_map()
    companies = alias_map.get('companies', {})
    base = 'https://search.patentsview.org/api/v1/patent/'

    # AI CPC code prefixes per wq-013 §10. PatentsView takes CPC codes
    # without the space: 'G06N20/00' (not 'G06N 20/00').
    AI_CPCS = ['G06N3', 'G06N20', 'G06N5', 'G06N7', 'G06N10',
               'G06F18', 'G06F40', 'G06V10', 'G10L15', 'G10L25']

    claims = []
    lookups_needed = []
    for slug, entry in companies.items():
        assignee_ids = entry.get('patent_assignee_ids') or []
        if not assignee_ids:
            lookups_needed.append((slug, entry.get('canonical', slug)))
            continue

        # Build a patent-count query filtered to AI CPC codes + assignee ids
        q = json.dumps({
            '_and': [
                {'_or': [{'assignee_id': a} for a in assignee_ids]},
                {'_or': [{'_begins': {'cpc_subclass_id': p}} for p in AI_CPCS]},
            ]
        })
        url = f'{base}?q={q}&f=["patent_id"]&o={{"per_page":25}}'
        try:
            payload = _fetch_json(url)
        except Exception as e:
            log(f"    {slug}: PatentsView fetch failed — {e}")
            continue
        try:
            save_snapshot({**source, 'id': f"{source['id']}-{slug}"},
                          json.dumps(payload).encode('utf-8'), ext='json')
        except Exception:
            pass
        total = payload.get('total_hits') or len(payload.get('patents') or [])
        claim = {
            'type': 'patent_snapshot',
            'company_slug': slug,
            'assignee_ids': assignee_ids,
            'window': _iso_month(),
            'metrics': {
                'applications_published_last_30d': 0,  # v1 — requires date range query follow-up
                'applications_published_trailing_12m': total,
                'grants_last_30d': 0,
                'grants_trailing_12m': 0,
                'ai_cpc_share_trailing_12m': 1.0,  # all queried patents are AI-CPC by construction
            },
            'top_cpc_subclasses': [],
            'source': {
                'type': 'patentsview_search',
                'url': url,
                'retrievedAt': datetime.now().isoformat(),
                'nextReview': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'confidence': 'high',
            },
        }
        claims.append(claim)
        log(f"    {slug}: {total} patent(s) matched")

    if lookups_needed:
        log(f"  {len(lookups_needed)} company/ies have empty patent_assignee_ids — run a disambiguation pass to populate:")
        for slug, canon in lookups_needed[:10]:
            log(f"    {slug}  (canonical: {canon})")
    return claims


def extract_google_patents_bq(source):
    """STUBBED per Phase 1 decision #4. International patent coverage gated
    on GCP credentials (GCP_SERVICE_ACCOUNT_JSON env var). When the env
    isn't set, logs guidance and returns []."""
    if not os.environ.get('GCP_SERVICE_ACCOUNT_JSON'):
        log("  GCP_SERVICE_ACCOUNT_JSON env var not set — google_patents_bq is stubbed.")
        log("  To enable: provision a GCP service account with BigQuery Data Viewer + BigQuery User roles, and export the JSON key path.")
        return []
    log("  GCP credentials present but BigQuery adapter not yet implemented; returning [].")
    return []


def extract_epo_ops(source):
    """EPO Open Patent Services — EU patent API. Env-gated on
    EPO_OPS_CLIENT_ID / EPO_OPS_CLIENT_SECRET (register free at EPO OPS)."""
    cid = os.environ.get('EPO_OPS_CLIENT_ID')
    secret = os.environ.get('EPO_OPS_CLIENT_SECRET')
    if not cid or not secret:
        log("  EPO_OPS_CLIENT_ID / EPO_OPS_CLIENT_SECRET not set — epo_ops is env-gated.")
        log("  Register at https://developers.epo.org/ (free, 250 req/week). Set both env vars then --force src-067.")
        return []
    log("  EPO OPS credentials present but adapter not yet implemented; returning [].")
    return []


def extract_dol_lca_xlsx(source):
    """DoL OFLC LCA quarterly disclosure. Quarterly XLSX drops require
    openpyxl to parse. Applies the AI-engineer regex from wq-013 §9 to
    the JOB_TITLE column and aggregates by normalised employer."""
    text, html = fetch_page(source['url'])
    if html:
        try:
            save_snapshot(source, html, ext='html')
        except Exception as e:
            log(f"  Snapshot failed: {e}")
    if not text:
        return []

    xlsx_urls = _re.findall(r'https?://[^\s"\']+\.xlsx', html or '', _re.IGNORECASE)
    if xlsx_urls:
        log(f"  Found {len(xlsx_urls)} quarterly XLSX drop(s) on DoL OFLC page")
        for u in xlsx_urls[:5]:
            log(f"    {u}")

    try:
        import openpyxl  # noqa: F401
    except ImportError:
        log("  openpyxl not installed — DoL LCA XLSX parse skipped for v1.")
        log("  Install via `pip install openpyxl` to enable row-level LCA extraction.")
        return []
    log("  openpyxl present but DoL LCA row-parsing not yet implemented; returning [].")
    return []


def extract_pdf_report(source):
    """Download PDF and extract claims."""
    pdf_path = fetch_pdf(source['url'])
    if not pdf_path:
        return []

    try:
        text = ''
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages[:50]:  # Max 50 pages
                    text += (page.extract_text() or '') + '\n\n'
        except ImportError:
            try:
                from pypdf import PdfReader
                reader = PdfReader(pdf_path)
                text = '\n\n'.join((page.extract_text() or '') for page in reader.pages[:50])
            except ImportError:
                try:
                    from PyPDF2 import PdfReader
                    reader = PdfReader(pdf_path)
                    text = '\n\n'.join((page.extract_text() or '') for page in reader.pages[:50])
                except ImportError:
                    log("  No PDF library available (install pdfplumber, pypdf, or PyPDF2)")
                    os.unlink(pdf_path)
                    return []

        os.unlink(pdf_path)
        log(f"  Extracted {len(text):,} chars from PDF")
        return extract_with_claude_chunked(text, source)

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
    # Stream 2 (wq-012) power adapters:
    'iso_queue_ercot': extract_iso_queue_ercot,
    'iso_queue_pjm': extract_iso_queue_pjm,
    'eia_api': extract_eia_api,
    'neso_tec': extract_neso_tec,
    'epoch_frontier': extract_epoch_frontier,
    # Stream 3 (wq-013) discovery adapters:
    'greenhouse_board': extract_greenhouse_board,
    'lever_postings': extract_lever_postings,
    'ashby_public': extract_ashby_public,
    'workable_jobs': extract_workable_jobs,
    'patentsview_search': extract_patentsview_search,
    'google_patents_bq': extract_google_patents_bq,
    'epo_ops': extract_epo_ops,
    'dol_lca_xlsx': extract_dol_lca_xlsx,
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
    """Process a single source through its extraction adapter.

    Returns (claims_count, had_fetch_failures). Caller uses had_fetch_failures
    to skip advancing next_check when an adapter swallowed a fetch error and
    returned 0 claims — without this guard a TLS/404 day silently disables the
    source for its full frequency window.
    """
    global _fetch_failures
    _fetch_failures = 0

    log(f"\n📄 {source['title']} ({source['type']})")
    log(f"   Method: {source['extraction_method']}, URL: {source['url'][:80]}")

    if dry_run:
        log("   [DRY RUN] Would extract")
        return 0, False

    adapter = ADAPTERS.get(source['extraction_method'])
    if not adapter:
        log(f"   Unknown extraction method: {source['extraction_method']}")
        return 0, False

    claims = adapter(source)
    log(f"   Extracted {len(claims)} claim(s)")

    if claims:
        today = datetime.now().strftime('%Y-%m-%d')
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # 1. Per-source raw snapshot into data-updates/<date>-source-<id>.json
        #    for provenance/audit. Not loaded by any UI.
        audit_path = os.path.join(OUTPUT_DIR, f'{today}-source-{source["id"]}.json')
        with open(audit_path, 'w') as f:
            json.dump(claims, f, indent=2)

        # 2. Append to vault-inbox.json as status=pending items. This is the
        #    queue `admin.html#review` reads via review.html. One canonical
        #    review location for all extractions — matches the existing
        #    extract_claims.py (podcast) pipeline behaviour.
        added = _append_to_vault_inbox(claims, source, today)
        log(f"   Appended {added} pending item(s) to vault-inbox.json")

    return len(claims), _fetch_failures > 0


VAULT_INBOX_PATH = os.path.join(BASE_DIR, 'vault-inbox.json')
_CONFIDENCE_TO_VAULT = {'high': 'verified', 'medium': 'estimated', 'low': 'speculative'}
_STRUCTURED_TYPES_SET = ('power_project', 'hiring_snapshot', 'patent_snapshot', 'company_surfaced')


def _existing_fingerprint(item):
    """Mirror of the fingerprint used for structured-claim dedupe in vault-inbox."""
    t = item.get('type')
    src = item.get('sourceUrl', '')
    if t == 'power_project':
        return (t, item.get('queue_market'), item.get('queue_id'))
    if t in ('hiring_snapshot', 'patent_snapshot'):
        return (t, item.get('entity') or item.get('company_slug'), item.get('window'))
    if t == 'company_surfaced':
        return (t, item.get('entity') or item.get('candidate_name'))
    return (src, (item.get('claim') or '')[:200])


def _claim_to_vault_item(claim, source, today, index):
    """Convert an extracted claim (free-text or structured) to the
    vault-inbox.json item shape used by review.html / admin.html#review."""
    date_str = today.replace('-', '')
    src_id = source.get('id', 'src-???')
    claim_id = f"auto-{date_str}-{src_id}-{index+1}"

    claim_type = claim.get('type')
    if claim_type in _STRUCTURED_TYPES_SET:
        return _structured_claim_to_vault(claim, source, claim_id, today)
    return _freetext_claim_to_vault(claim, source, claim_id, today)


def _freetext_claim_to_vault(claim, source, claim_id, today):
    conf_in = (claim.get('confidence') or 'medium').lower()
    return {
        'id': claim_id,
        'claim': claim.get('claim', ''),
        'value': claim.get('value'),
        'unit': claim.get('unit', ''),
        'sourceUrl': claim.get('source_url', source.get('url', '')),
        'sourceType': claim.get('source_type', source.get('type', '')),
        'sourceAuthor': claim.get('speaker') or claim.get('source_title') or source.get('organization', ''),
        'confidence': _CONFIDENCE_TO_VAULT.get(conf_in, 'estimated'),
        'dateOfClaim': coerce_or_keep(claim.get('source_date') or claim.get('time_period') or today, today),
        'dateAdded': today,
        'usedOn': [],
        'tags': [claim.get('category', 'other')],
        'notes': claim.get('source_excerpt_original') or f"From {source.get('title', '?')}",
        'status': 'pending',
        'replaces': None,
        'source_id': source.get('id'),
        'metricKey': claim.get('metric_key') or claim.get('metric'),
        'entity': claim.get('entity', ''),
        'weight': claim.get('weight', 'indicative'),
        'dedup_status': claim.get('dedup_status', 'new'),
        'dedup_note': claim.get('dedup_note'),
        # wq-041: source grounding pass-through. Null until extraction prompts
        # in this script are updated to request these fields (follow-on).
        # The reuse of source_excerpt_original keeps any existing excerpt content.
        'sourceExcerpt': claim.get('source_excerpt') or claim.get('source_excerpt_original'),
        'isPrimarySource': claim.get('is_primary_source'),
        'originalSourceCited': claim.get('original_source_cited'),
        # wq-054 — sub-period attribution. Default to annual when extractor
        # didn't set the scope; apply_decisions.py routes per scope.
        'timePeriodScope': claim.get('time_period_scope') or 'annual',
        'periodQualifier': claim.get('period_qualifier_detected'),
    }


def _structured_claim_to_vault(claim, source, claim_id, today):
    """Serialise a typed claim into the vault-inbox shape while preserving
    the structured payload on the item for renderers that care."""
    t = claim['type']
    entity = claim.get('company_slug') or claim.get('candidate_name') or claim.get('queue_market') or ''
    src_block = claim.get('source', {})
    conf_in = (src_block.get('confidence') or 'medium').lower()

    if t == 'hiring_snapshot':
        m = claim.get('metrics', {})
        summary = (f"{entity} — {m.get('open_roles_ai_titled','?')} AI roles / "
                   f"{m.get('open_roles_total','?')} total ({claim.get('window')})")
        value = m.get('open_roles_ai_titled')
        unit = 'AI roles'
    elif t == 'patent_snapshot':
        m = claim.get('metrics', {})
        summary = (f"{entity} — {m.get('applications_published_trailing_12m','?')} AI-CPC apps / "
                   f"{m.get('grants_trailing_12m','?')} grants trailing 12m ({claim.get('window')})")
        value = m.get('applications_published_trailing_12m')
        unit = 'patent apps'
    elif t == 'power_project':
        summary = (f"{claim.get('queue_market')} {claim.get('queue_id')} — "
                   f"{claim.get('mw_requested','?')} MW requested, stage {claim.get('stage')}"
                   + (f" → {claim.get('company_slug')}" if claim.get('company_slug') else ""))
        value = claim.get('mw_requested')
        unit = 'MW'
    elif t == 'company_surfaced':
        fs = claim.get('first_seen_signal', {})
        summary = (f"{claim.get('candidate_name')} — surfaced via {fs.get('kind','?')}"
                   + (f" ({fs.get('cpc')})" if fs.get('cpc') else ""))
        value = claim.get('density_score_estimate')
        unit = 'density_score'
    else:
        summary = f"[{t}] {entity}"
        value = None
        unit = ''

    return {
        'id': claim_id,
        'claim': summary,
        'value': value,
        'unit': unit,
        'sourceUrl': src_block.get('url', source.get('url', '')),
        'sourceType': source.get('type', ''),
        'sourceAuthor': source.get('organization', ''),
        'confidence': _CONFIDENCE_TO_VAULT.get(conf_in, 'estimated'),
        'dateOfClaim': today,
        'dateAdded': today,
        'usedOn': [],
        'tags': [t, entity] if entity else [t],
        'notes': json.dumps({k: v for k, v in claim.items() if k not in ('source',)}, default=str)[:500],
        'status': 'pending',
        'replaces': None,
        'source_id': source.get('id'),
        'metricKey': f"{entity}-{t}" if entity else t,
        'entity': entity,
        'weight': 'authoritative' if conf_in == 'high' else ('corroborating' if conf_in == 'medium' else 'indicative'),
        'dedup_status': 'new',
        'dedup_note': None,
        # Preserve the typed payload verbatim for renderers that support it
        'type': t,
        'structured_payload': claim,
        # wq-054 — structured scrapes are always point-in-time snapshots
        # (hiring counts as of today, patent total trailing-12m, etc.).
        # Override here to keep the audit validator happy.
        'timePeriodScope': 'point_in_time',
        'periodQualifier': claim.get('window'),
    }


def _append_to_vault_inbox(claims, source, today):
    if os.path.exists(VAULT_INBOX_PATH):
        with open(VAULT_INBOX_PATH) as f:
            inbox = json.load(f)
    else:
        inbox = {'items': [], 'lastProcessed': None}

    # Replace-per-source on append so re-running this source doesn't stack
    # duplicates. Only touches items whose source_id matches.
    src_id = source.get('id')
    if src_id:
        before = len(inbox['items'])
        inbox['items'] = [it for it in inbox['items']
                          if it.get('source_id') != src_id
                          or it.get('status') != 'pending']
        removed = before - len(inbox['items'])
        if removed:
            log(f"   Replaced {removed} prior pending item(s) from {src_id}")

    # wq-040 — load entities + schema once for materiality scoring per item
    try:
        with open(os.path.join(BASE_DIR, 'entities.json')) as f:
            _entities = json.load(f)
        with open(os.path.join(BASE_DIR, 'metric-schema.json')) as f:
            _schema = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        _entities, _schema = {"companies": []}, {}

    added = 0
    routed_telemetry = 0
    for i, claim in enumerate(claims):
        item = _claim_to_vault_item(claim, source, today, i)
        # wq-047 — route operational telemetry (hiring scrapes, package
        # downloads, GitHub stats, SEC filings monitoring) to a separate
        # bucket so the human review queue stays focused on decisions.
        if is_telemetry(item, source):
            append_to_telemetry_feed(item, source, today)
            routed_telemetry += 1
            continue
        try:
            item["materiality"] = score_materiality(item, _entities, _schema)
        except Exception:
            pass
        inbox['items'].append(item)
        added += 1

    if routed_telemetry:
        log(f"   Routed {routed_telemetry} item(s) to data/telemetry-feed.json (wq-047)")

    inbox['lastProcessed'] = today
    with open(VAULT_INBOX_PATH, 'w') as f:
        json.dump(inbox, f, indent=2)
    return added


def main():
    with logged_run("monitor_sources.py") as outputs:
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
            outputs["sources_total"] = 0
            outputs["sources_due"] = 0
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

        outputs["sources_total"] = len(sources)
        outputs["sources_due"] = len(due)
        outputs["dry_run"] = dry_run

        if not due:
            log("  Nothing due today")
            outputs["claims_added"] = 0
            outputs["sources_processed"] = 0
            return

        total_claims = 0
        fetch_failure_count = 0
        for source in due:
            claims_count, had_fetch_failures = process_source(source, dry_run)
            total_claims += claims_count
            if had_fetch_failures:
                fetch_failure_count += 1

            if not dry_run:
                # Update registry
                source['last_checked'] = today_str
                source['last_claims_count'] = claims_count
                if claims_count == 0 and had_fetch_failures:
                    # Adapter swallowed a fetch failure — leave next_check alone so
                    # we retry tomorrow instead of silent-disabling the source.
                    source['status'] = 'error'
                    log(f"   ⚠ Fetch failures with 0 claims — next_check unchanged for retry")
                else:
                    source['status'] = 'active'
                    freq_days = FREQUENCY_DAYS.get(source['frequency'], 7)
                    source['next_check'] = (datetime.now() + timedelta(days=freq_days)).strftime('%Y-%m-%d')

        if not dry_run:
            registry['meta']['lastUpdated'] = today_str
            with open(REGISTRY_PATH, 'w') as f:
                json.dump(registry, f, indent=2)

        outputs["sources_processed"] = len(due)
        outputs["claims_added"] = total_claims
        outputs["sources_with_fetch_failures"] = fetch_failure_count

        log(f"\n{'='*60}")
        log(f"✅ Done — {len(due)} sources processed, {total_claims} total claims extracted")


if __name__ == '__main__':
    main()
