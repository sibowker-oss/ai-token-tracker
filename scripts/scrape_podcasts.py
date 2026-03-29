#!/usr/bin/env python3
"""
Podcast transcript scraper — Phase 1 (Tier 1 sources).

Fetches full transcripts from:
  - Latent Space (www.latent.space) — Substack
  - All-In Transcripts (allintranscripts.substack.com) — Substack

Saves raw transcripts as markdown to:
  transcripts/{source}/{YYYY-MM-DD}-{slug}.md

Tracks seen episodes in transcripts/.seen to avoid re-fetching.

Run: python3 scripts/scrape_podcasts.py [--limit N] [--source latent-space|all-in|all]
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError
import xml.etree.ElementTree as ET

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANSCRIPT_DIR = os.path.join(BASE_DIR, 'transcripts')
SEEN_FILE = os.path.join(TRANSCRIPT_DIR, '.seen')

SOURCES = {
    'latent-space': {
        'rss': 'https://www.latent.space/feed',
        'label': 'Latent Space',
        'dir': 'latent-space',
        # AINews daily digests are short newsletter items, not podcast transcripts
        'skip_title_patterns': [r'^\[AINews\]'],
        'rss_content': False,  # fetch full page for transcript
    },
    'all-in': {
        # The community Substack only has YouTube embeds on the web page.
        # The RSS content:encoded field contains the actual transcript text.
        'rss': 'https://allintranscripts.substack.com/feed',
        'label': 'All-In Podcast',
        'dir': 'all-in',
        'skip_title_patterns': [],
        'rss_content': True,  # extract transcript from RSS content:encoded
    },
}


def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()


def save_seen(seen):
    with open(SEEN_FILE, 'w') as f:
        json.dump(sorted(seen), f, indent=2)


def fetch(url, delay=1.0):
    """Polite HTTP GET with a User-Agent header."""
    time.sleep(delay)
    req = Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (compatible; PodcastTranscriptBot/1.0)',
    })
    try:
        with urlopen(req, timeout=20) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except URLError as e:
        print(f"  ⚠ Fetch failed for {url}: {e}")
        return None


def parse_rss(xml_text):
    """Return list of {title, url, date, slug, rss_content} from an RSS feed."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        print(f"  ⚠ RSS parse error: {e}")
        return []

    CONTENT_NS = 'http://purl.org/rss/1.0/modules/content/'
    episodes = []
    for item in root.iter('item'):
        title_el = item.find('title')
        link_el = item.find('link')
        pub_el = item.find('pubDate')
        content_el = item.find(f'{{{CONTENT_NS}}}encoded')

        title = title_el.text.strip() if title_el is not None else 'unknown'
        url = link_el.text.strip() if link_el is not None else ''
        rss_content = content_el.text or '' if content_el is not None else ''

        # Parse date → YYYY-MM-DD
        date_str = 'unknown'
        if pub_el is not None and pub_el.text:
            try:
                from email.utils import parsedate_to_datetime
                dt = parsedate_to_datetime(pub_el.text)
                date_str = dt.strftime('%Y-%m-%d')
            except Exception:
                date_str = pub_el.text[:10]

        # Derive slug from URL
        slug = url.rstrip('/').split('/')[-1] or re.sub(r'[^a-z0-9]+', '-', title.lower())[:60]

        if url:
            episodes.append({
                'title': title,
                'url': url,
                'date': date_str,
                'slug': slug,
                'rss_content': rss_content,
            })

    return episodes


def html_to_text(html_fragment):
    """Convert an HTML fragment to plain text."""
    text = re.sub(r'<script[^>]*>.*?</script>', '', html_fragment, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<h[1-3][^>]*>(.*?)</h[1-3]>', r'\n## \1\n', text, flags=re.DOTALL)
    text = re.sub(r'<p[^>]*>', '\n', text)
    text = re.sub(r'</p>', '\n', text)
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>') \
               .replace('&nbsp;', ' ').replace('&#39;', "'").replace('&quot;', '"') \
               .replace('&ldquo;', '\u201c').replace('&rdquo;', '\u201d') \
               .replace('&lsquo;', '\u2018').replace('&rsquo;', '\u2019') \
               .replace('&#x27;', "'").replace('&apos;', "'")
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()


def extract_transcript_html(html, url):
    """
    Extract the main article/transcript text from a Substack post HTML.

    Substack wraps post body in:  <div class="body markup">...</div>
    We find that marker, take a large slice of HTML after it (the nested
    divs are too complex to close-match via regex), then strip all tags.
    We trim at the comments/footer section to avoid noise.
    """
    # Find start of body markup div
    marker = 'class="body markup"'
    idx = html.find(marker)
    if idx == -1:
        # Fall back: article tag or full body
        art = re.search(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)
        if art:
            return html_to_text(art.group(1))
        body = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
        return html_to_text(body.group(1) if body else html)

    # Take up to 300KB of content after the marker (covers even long transcripts)
    content_start = html.find('>', idx) + 1
    content_html = html[content_start:content_start + 300_000]

    # Trim at the subscriber wall / comments section if present
    for stop_marker in [
        'class="paywall-content"',
        'class="subscription-widget"',
        'id="comments"',
        'class="comments-section"',
        'data-component-name="AudioPlayer"',  # stop before embedded player footer
    ]:
        stop_idx = content_html.find(stop_marker)
        if 0 < stop_idx < len(content_html) - 5000:
            content_html = content_html[:stop_idx]

    return html_to_text(content_html)


def scrape_source(source_key, limit=5, seen=None):
    """Fetch and save new transcripts for a source. Returns list of saved paths."""
    cfg = SOURCES[source_key]
    print(f"\n🎙 {cfg['label']} (RSS: {cfg['rss']})")

    rss_xml = fetch(cfg['rss'])
    if not rss_xml:
        return []

    episodes = parse_rss(rss_xml)
    print(f"  Found {len(episodes)} episodes in feed")

    out_dir = os.path.join(TRANSCRIPT_DIR, cfg['dir'])
    os.makedirs(out_dir, exist_ok=True)

    skip_patterns = [re.compile(p) for p in cfg.get('skip_title_patterns', [])]
    use_rss_content = cfg.get('rss_content', False)

    saved = []
    skipped = 0
    for ep in episodes[:limit * 3]:  # fetch more candidates to account for filtered ones
        # Title filter (e.g. skip AINews digest posts)
        if any(p.search(ep['title']) for p in skip_patterns):
            continue

        ep_id = f"{source_key}::{ep['slug']}"
        if seen is not None and ep_id in seen:
            skipped += 1
            continue

        if len(saved) >= limit:
            break

        print(f"  ↓ [{ep['date']}] {ep['title'][:70]}")

        if use_rss_content:
            # Use transcript text embedded in RSS content:encoded
            transcript = html_to_text(ep['rss_content'])
        else:
            html = fetch(ep['url'], delay=2.0)
            if not html:
                continue
            transcript = extract_transcript_html(html, ep['url'])

        if len(transcript) < 500:
            print(f"    ⚠ Transcript too short ({len(transcript)} chars), skipping")
            if seen is not None:
                seen.add(ep_id)  # mark as seen so we don't retry
            continue

        # Write markdown file
        filename = f"{ep['date']}-{ep['slug'][:60]}.md"
        filepath = os.path.join(out_dir, filename)
        with open(filepath, 'w') as f:
            f.write(f"# {ep['title']}\n\n")
            f.write(f"**Source:** {cfg['label']}  \n")
            f.write(f"**Date:** {ep['date']}  \n")
            f.write(f"**URL:** {ep['url']}  \n\n")
            f.write("---\n\n")
            f.write(transcript)

        print(f"    ✅ Saved {filename} ({len(transcript):,} chars)")
        saved.append(filepath)
        if seen is not None:
            seen.add(ep_id)

    if skipped:
        print(f"  ⏭ Skipped {skipped} already-seen episodes")

    return saved


def main():
    parser = argparse.ArgumentParser(description='Scrape podcast transcripts')
    parser.add_argument('--source', default='all', choices=['all', 'latent-space', 'all-in'],
                        help='Which source to scrape (default: all)')
    parser.add_argument('--limit', type=int, default=5,
                        help='Max episodes per source to fetch (default: 5)')
    parser.add_argument('--refetch', action='store_true',
                        help='Re-fetch even if already seen')
    args = parser.parse_args()

    today = datetime.now().strftime('%Y-%m-%d')
    print(f"🎙 Podcast Transcript Scraper — {today}\n{'='*50}")

    seen = set() if args.refetch else load_seen()
    sources = list(SOURCES.keys()) if args.source == 'all' else [args.source]

    all_saved = []
    for source_key in sources:
        saved = scrape_source(source_key, limit=args.limit, seen=seen)
        all_saved.extend(saved)

    save_seen(seen)

    print(f"\n✅ Done — {len(all_saved)} new transcript(s) saved to {TRANSCRIPT_DIR}/")
    if all_saved:
        print("\nNext step: run python3 scripts/extract_claims.py to extract data points")

    return all_saved


if __name__ == '__main__':
    main()
