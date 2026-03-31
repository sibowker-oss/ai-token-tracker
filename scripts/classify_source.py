#!/usr/bin/env python3
"""
Source classifier — given a URL, determine type, extraction method, and frequency.

Used by:
  - vault.html Quick Add (via CLI: python3 scripts/classify_source.py URL)
  - monitor_sources.py (for new sources added to registry)

Run: python3 scripts/classify_source.py "https://example.com/report.pdf"
     python3 scripts/classify_source.py --add "https://example.com/report.pdf" "Title here"
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta
from urllib.request import urlopen, Request
from urllib.error import URLError

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(BASE_DIR, 'sources-registry.json')

# URL pattern → source type classification
PATTERNS = [
    # Slide decks
    (r'docs\.google\.com/presentation', 'slide_deck', 'pdf_export', 'annual'),
    (r'slideshare\.net/', 'slide_deck', 'web_extract', 'one_time'),
    (r'speakerdeck\.com/', 'slide_deck', 'web_extract', 'one_time'),

    # Documents
    (r'docs\.google\.com/document', 'document', 'web_extract', 'one_time'),
    (r'notion\.so/', 'document', 'web_extract', 'monthly'),

    # PDFs
    (r'\.pdf(\?|$)', 'pdf_report', 'pdf_extract', 'one_time'),
    (r'arxiv\.org/', 'research_paper', 'pdf_extract', 'one_time'),

    # Newsletters / Blogs
    (r'\.substack\.com/', 'newsletter', 'rss_feed', 'weekly'),
    (r'medium\.com/', 'blog', 'web_extract', 'weekly'),
    (r'mirror\.xyz/', 'blog', 'web_extract', 'weekly'),

    # Social
    (r'(twitter\.com|x\.com)/.+/status/', 'social_thread', 'thread_extract', 'one_time'),
    (r'(twitter\.com|x\.com)/[^/]+$', 'social_profile', 'rss_feed', 'weekly'),

    # Video
    (r'youtube\.com/watch', 'video', 'youtube_captions', 'one_time'),
    (r'youtu\.be/', 'video', 'youtube_captions', 'one_time'),

    # SEC filings
    (r'sec\.gov/', 'sec_filing', 'sec_extract', 'quarterly'),
    (r'edgar', 'sec_filing', 'sec_extract', 'quarterly'),

    # GitHub
    (r'github\.com/[^/]+/[^/]+$', 'github_repo', 'github_api', 'weekly'),
    (r'github\.com/.+/releases', 'github_releases', 'github_api', 'weekly'),

    # APIs / data sources
    (r'api\.|/api/', 'api', 'api_fetch', 'daily'),

    # Podcasts (various hosts)
    (r'(anchor\.fm|megaphone\.fm|transistor\.fm|simplecast\.com|libsyn\.com|buzzsprout\.com)', 'podcast_feed', 'podcast_scraper', 'weekly'),
    (r'podcasts\.(apple|google)\.com', 'podcast_listing', 'podcast_scraper', 'weekly'),
    (r'happyscribe\.com/', 'podcast_transcript', 'web_extract', 'weekly'),

    # Reports / research
    (r'(mckinsey|gartner|forrester|idc|statista|ark-invest)\.com', 'research_report', 'web_extract', 'quarterly'),
    (r'(a16z|sequoiacap|benchmark)\.com', 'vc_research', 'web_extract', 'quarterly'),

    # News
    (r'(bloomberg|wsj|ft\.com|reuters|theinformation|cnbc|techcrunch|venturebeat)\.com', 'news_article', 'web_extract', 'one_time'),

    # Crunchbase / PitchBook
    (r'crunchbase\.com/', 'company_data', 'web_extract', 'monthly'),
    (r'pitchbook\.com/', 'company_data', 'web_extract', 'monthly'),
]

# Extraction method descriptions
METHOD_INFO = {
    'pdf_export': 'Export as PDF → Claude extracts data per page (~$0.01/page)',
    'pdf_extract': 'Download PDF → text extraction → Claude claim extraction',
    'web_extract': 'Fetch HTML → Claude extracts structured claims',
    'rss_feed': 'Monitor RSS feed → extract new items → claim extraction',
    'podcast_scraper': 'Already handled by scrape_podcasts.py',
    'signal_scraper': 'Already handled by scrape_signals.py',
    'youtube_captions': 'YouTube transcript API → claim extraction',
    'thread_extract': 'Unroll thread → claim extraction',
    'github_api': 'GitHub API → stars, releases, README data',
    'sec_extract': 'EDGAR API → filing text → AI revenue claim extraction',
    'api_fetch': 'Direct API call → structured data',
}

FREQUENCY_DAYS = {
    'daily': 1, 'weekly': 7, 'monthly': 30, 'quarterly': 90, 'annual': 365, 'one_time': 99999,
}


def classify_url(url):
    """Classify a URL and return source metadata."""
    url_lower = url.lower()

    source_type = 'web_page'
    extraction_method = 'web_extract'
    frequency = 'one_time'

    for pattern, stype, method, freq in PATTERNS:
        if re.search(pattern, url_lower):
            source_type = stype
            extraction_method = method
            frequency = freq
            break

    # Try to detect RSS feeds
    if source_type == 'web_page':
        try:
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urlopen(req, timeout=10) as resp:
                content_type = resp.headers.get('Content-Type', '')
                first_bytes = resp.read(500).decode('utf-8', errors='replace')
                if 'xml' in content_type or 'rss' in content_type or '<rss' in first_bytes or '<feed' in first_bytes:
                    source_type = 'rss_feed'
                    extraction_method = 'rss_feed'
                    frequency = 'weekly'
        except Exception:
            pass

    # Calculate next check date
    days = FREQUENCY_DAYS.get(frequency, 99999)
    next_check = (datetime.now() + timedelta(days=min(days, 365))).strftime('%Y-%m-%d')

    # Estimate relevance based on URL keywords
    relevance_keywords = ['ai', 'llm', 'token', 'revenue', 'arr', 'funding', 'model', 'gpu',
                          'inference', 'openai', 'anthropic', 'google', 'meta', 'deepseek']
    relevance_score = sum(1 for kw in relevance_keywords if kw in url_lower)
    relevance = 'high' if relevance_score >= 3 else 'medium' if relevance_score >= 1 else 'low'

    return {
        'type': source_type,
        'extraction_method': extraction_method,
        'extraction_info': METHOD_INFO.get(extraction_method, 'Standard web extraction'),
        'frequency': frequency,
        'next_check': next_check,
        'relevance': relevance,
    }


def add_to_registry(url, title, classification):
    """Add a classified source to the registry."""
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH) as f:
            registry = json.load(f)
    else:
        registry = {'meta': {'version': '1.0', 'lastUpdated': '', 'description': ''}, 'sources': []}

    # Check for duplicate
    for s in registry['sources']:
        if s['url'] == url:
            print(f"  Already in registry as {s['id']}: {s['title']}")
            return s['id']

    # Generate ID
    next_id = len(registry['sources']) + 1
    source_id = f'src-{next_id:03d}'

    entry = {
        'id': source_id,
        'url': url,
        'title': title,
        'type': classification['type'],
        'author': '',
        'organization': '',
        'added': datetime.now().strftime('%Y-%m-%d'),
        'tags': [],
        'extraction_method': classification['extraction_method'],
        'frequency': classification['frequency'],
        'next_check': classification['next_check'],
        'last_checked': None,
        'last_claims_count': 0,
        'status': 'pending_first_extraction',
    }

    registry['sources'].append(entry)
    registry['meta']['lastUpdated'] = datetime.now().strftime('%Y-%m-%d')

    with open(REGISTRY_PATH, 'w') as f:
        json.dump(registry, f, indent=2)

    print(f"  Added as {source_id}")
    return source_id


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/classify_source.py URL [--add TITLE]")
        print("       python3 scripts/classify_source.py --json URL  (machine-readable)")
        sys.exit(1)

    json_mode = '--json' in sys.argv
    add_mode = '--add' in sys.argv

    # Get URL
    url = [a for a in sys.argv[1:] if not a.startswith('--')][0]

    classification = classify_url(url)

    if json_mode:
        print(json.dumps(classification, indent=2))
        return

    print(f"\n🔍 Source Classification")
    print(f"   URL: {url}")
    print(f"   Type: {classification['type']}")
    print(f"   Extraction: {classification['extraction_method']}")
    print(f"   Method: {classification['extraction_info']}")
    print(f"   Frequency: {classification['frequency']}")
    print(f"   Next check: {classification['next_check']}")
    print(f"   Relevance: {classification['relevance']}")

    if add_mode:
        args = [a for a in sys.argv[1:] if not a.startswith('--')]
        title = args[1] if len(args) > 1 else url.split('/')[-1]
        print(f"\n   Adding to registry...")
        add_to_registry(url, title, classification)


if __name__ == '__main__':
    main()
