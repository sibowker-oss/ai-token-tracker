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
ATTRIBUTION_MAP_FILE = os.path.join(BASE_DIR, 'data', 'datacenter-attribution-map.json')


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
            max_tokens=8192,
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
