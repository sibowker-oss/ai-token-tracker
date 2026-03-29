#!/usr/bin/env python3
"""
Podcast transcript scraper — Tier 1 + Tier 2 sources.

Tier 1 (full transcripts on the web):
  - Latent Space (www.latent.space) — Substack
  - Acquired (www.acquired.fm) — Webflow, transcript after "Transcript:" marker
  - All-In Podcast (podcasts.happyscribe.com) — free speaker-labelled transcripts

Tier 2 (YouTube auto-captions):
  - BG2Pod (@Bg2Pod)

Tier 3 (deferred — needs STT/Whisper):
  - 20VC (audio-only on Libsyn, YouTube channel is clips only)

Saves raw transcripts as markdown to:
  transcripts/{source}/{YYYY-MM-DD}-{slug}.md

Tracks seen episodes in transcripts/.seen to avoid re-fetching.

Run: python3 scripts/scrape_podcasts.py [--limit N] [--source SOURCE|all]

Requires: youtube-transcript-api (pip install youtube-transcript-api) for Tier 2 sources.
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import xml.etree.ElementTree as ET

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANSCRIPT_DIR = os.path.join(BASE_DIR, 'transcripts')
SEEN_FILE = os.path.join(TRANSCRIPT_DIR, '.seen')

# ---------------------------------------------------------------------------
# Source registry — each entry describes how to discover + extract episodes
# ---------------------------------------------------------------------------
SOURCES = {
    # ----- Tier 1: full transcripts published -----
    'latent-space': {
        'label': 'Latent Space',
        'dir': 'latent-space',
        'tier': 1,
        'discovery': 'rss',
        'rss': 'https://www.latent.space/feed',
        'skip_title_patterns': [r'^\[AINews\]'],
        'extractor': 'substack_html',
    },
    'acquired': {
        'label': 'Acquired',
        'dir': 'acquired',
        'tier': 1,
        'discovery': 'rss',
        'rss': 'https://feeds.transistor.fm/acquired',
        'skip_title_patterns': [],
        'extractor': 'acquired_html',
    },
    'all-in': {
        'label': 'All-In Podcast',
        'dir': 'all-in',
        'tier': 1,
        'discovery': 'happyscribe',
        'happyscribe_index': 'https://podcasts.happyscribe.com/all-in-with-chamath-jason-sacks-friedberg',
        'skip_title_patterns': [],
        'extractor': 'happyscribe_html',
    },
    # ----- Tier 2: YouTube auto-captions -----
    'bg2pod': {
        'label': 'BG2Pod',
        'dir': 'bg2pod',
        'tier': 2,
        'discovery': 'rss',
        'rss': 'https://anchor.fm/s/f06c2370/podcast/rss',
        'skip_title_patterns': [],
        'extractor': 'youtube_captions',
        'youtube_channel_id': 'UC-yRDvpR99LUc5l7i7jLzew',
    },
    # 20VC: YouTube channel posts short clips (not full episodes), so
    # auto-captions don't work. Full episodes are audio-only on Libsyn.
    # Requires STT (Whisper) — deferred to Phase 3.
    # RSS: https://rss.libsyn.com/shows/61840/destinations/240976.xml
    # YouTube channel: UCf0PBRjhf0rF8fWBIxTuoWA
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
    """Polite HTTP GET with User-Agent."""
    time.sleep(delay)
    req = Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (compatible; PodcastTranscriptBot/1.0)',
    })
    try:
        with urlopen(req, timeout=30) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except (URLError, HTTPError) as e:
        print(f"  ⚠ Fetch failed for {url}: {e}")
        return None


# ---------------------------------------------------------------------------
# HTML → plain text conversion
# ---------------------------------------------------------------------------

def html_to_text(html_fragment):
    """Convert an HTML fragment to readable plain text."""
    text = re.sub(r'<script[^>]*>.*?</script>', '', html_fragment, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<h[1-3][^>]*>(.*?)</h[1-3]>', r'\n## \1\n', text, flags=re.DOTALL)
    text = re.sub(r'<p[^>]*>', '\n', text)
    text = re.sub(r'</p>', '\n', text)
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    for old, new in [
        ('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'), ('&nbsp;', ' '),
        ('&#39;', "'"), ('&quot;', '"'), ('&ldquo;', '\u201c'),
        ('&rdquo;', '\u201d'), ('&lsquo;', '\u2018'), ('&rsquo;', '\u2019'),
        ('&#x27;', "'"), ('&apos;', "'"),
    ]:
        text = text.replace(old, new)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()


# ---------------------------------------------------------------------------
# Discovery: how to find episodes for each source
# ---------------------------------------------------------------------------

def discover_rss(cfg, limit):
    """Discover episodes from an RSS feed."""
    xml_text = fetch(cfg['rss'])
    if not xml_text:
        return []

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
        enclosure_el = item.find('enclosure')

        title = title_el.text.strip() if title_el is not None and title_el.text else 'unknown'
        url = link_el.text.strip() if link_el is not None and link_el.text else ''
        rss_content = (content_el.text or '') if content_el is not None else ''

        # Parse date
        date_str = 'unknown'
        if pub_el is not None and pub_el.text:
            try:
                from email.utils import parsedate_to_datetime
                dt = parsedate_to_datetime(pub_el.text)
                date_str = dt.strftime('%Y-%m-%d')
            except Exception:
                date_str = pub_el.text[:10]

        slug = url.rstrip('/').split('/')[-1] or re.sub(r'[^a-z0-9]+', '-', title.lower())[:60]

        audio_url = ''
        if enclosure_el is not None:
            audio_url = enclosure_el.get('url', '')

        if url:
            episodes.append({
                'title': title, 'url': url, 'date': date_str,
                'slug': slug, 'rss_content': rss_content,
                'audio_url': audio_url,
            })

    # Return generously — scrape_source handles skip patterns + limiting
    return episodes[:limit * 10]


def discover_happyscribe(cfg, limit):
    """Discover episodes from the Happy Scribe podcast page (paginated)."""
    base_url = cfg['happyscribe_index']
    episodes = []
    pages_needed = max(1, (limit + 19) // 20)  # 20 eps per page

    for page in range(1, pages_needed + 1):
        url = base_url if page == 1 else f"{base_url}?page={page}"
        html = fetch(url, delay=1.5)
        if not html:
            break

        # Episode links: <a href="/all-in-with-.../episode-slug">
        for m in re.finditer(
            r'<a[^>]+href="(/all-in-with-chamath-jason-sacks-friedberg/([^"]+))"[^>]*>',
            html
        ):
            ep_path, slug = m.group(1), m.group(2)
            # Skip pagination and non-episode links
            if slug.startswith('?') or slug == '':
                continue
            ep_url = f"https://podcasts.happyscribe.com{ep_path}"
            if ep_url not in {e['url'] for e in episodes}:
                episodes.append({
                    'title': slug.replace('-', ' ').title(),
                    'url': ep_url,
                    'date': 'unknown',
                    'slug': slug[:60],
                    'rss_content': '',
                    'audio_url': '',
                })

    print(f"  Found {len(episodes)} episodes on Happy Scribe")
    return episodes[:limit * 3]


# ---------------------------------------------------------------------------
# Extractors: how to get transcript text for each source type
# ---------------------------------------------------------------------------

def extract_substack_html(ep, cfg):
    """Fetch a Substack page and extract the body markup."""
    html = fetch(ep['url'], delay=2.0)
    if not html:
        return None

    marker = 'class="body markup"'
    idx = html.find(marker)
    if idx == -1:
        art = re.search(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)
        if art:
            return html_to_text(art.group(1))
        body = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
        return html_to_text(body.group(1) if body else html)

    content_start = html.find('>', idx) + 1
    content_html = html[content_start:content_start + 300_000]

    for stop in ['class="paywall-content"', 'class="subscription-widget"',
                 'id="comments"', 'class="comments-section"']:
        stop_idx = content_html.find(stop)
        if 0 < stop_idx < len(content_html) - 5000:
            content_html = content_html[:stop_idx]

    return html_to_text(content_html)


def extract_acquired_html(ep, cfg):
    """Fetch an Acquired FM episode page and extract the transcript section."""
    html = fetch(ep['url'], delay=2.0)
    if not html:
        return None

    # Acquired pages have show notes first, then "Transcript:" heading, then content
    # in a w-richtext container
    transcript_idx = html.find('Transcript:')
    if transcript_idx == -1:
        transcript_idx = html.find('Transcript</')
    if transcript_idx == -1:
        # No transcript on this page (some older eps don't have one)
        return None

    # Take everything from "Transcript:" onwards up to 500KB
    content_html = html[transcript_idx:transcript_idx + 500_000]

    # Trim at footer / comments / nav sections
    for stop in ['class="footer', 'class="comments', 'class="w-nav',
                 'id="footer"', 'class="section-footer']:
        stop_idx = content_html.find(stop)
        if stop_idx > 500:
            content_html = content_html[:stop_idx]

    return html_to_text(content_html)


def extract_happyscribe_html(ep, cfg):
    """Fetch a Happy Scribe episode page and extract transcript text."""
    html = fetch(ep['url'], delay=2.0)
    if not html:
        return None

    # Extract date from structured data
    date_match = re.search(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})', html)
    if date_match and ep['date'] == 'unknown':
        ep['date'] = date_match.group(1)

    # Extract real title
    title_match = re.search(r'"name"\s*:\s*"Transcript of ([^"]+)"', html)
    if title_match:
        ep['title'] = f"Transcript of {title_match.group(1)}"

    # Convert full page to text first
    text = html_to_text(html)

    # The transcript starts at the first timestamp (00:00:00 pattern)
    ts_match = re.search(r'\n\s*\d{2}:\d{2}:\d{2}\s*\n', text)
    if ts_match:
        text = text[ts_match.start():]
    else:
        # Fallback: look for "Transcribed from audio" marker
        marker_idx = text.find('Transcribed from audio')
        if marker_idx > 0:
            text = text[marker_idx:]
            # Skip past that line
            nl = text.find('\n')
            if nl > 0:
                text = text[nl:]

    # Trim footer noise (Happy Scribe promo, navigation)
    for stop in ['Want to transcribe', 'Generate Podcast Notes',
                 'All-In with Chamath, Jason, Sacks & Friedberg',
                 'Powered by Happy Scribe']:
        stop_idx = text.rfind(stop)
        if stop_idx > len(text) * 0.8:  # only if in the last 20% of text
            text = text[:stop_idx]

    return text.strip()


def _build_youtube_video_index(channel_id):
    """Fetch the YouTube channel RSS and return {normalised_title: video_id}."""
    yt_rss_url = f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'
    xml_text = fetch(yt_rss_url, delay=1.0)
    if not xml_text:
        return {}
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return {}

    ns = {'atom': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015'}
    index = {}
    for entry in root.findall('atom:entry', ns):
        vid_el = entry.find('yt:videoId', ns)
        title_el = entry.find('atom:title', ns)
        if vid_el is not None and title_el is not None:
            norm = re.sub(r'[^a-z0-9]+', ' ', (title_el.text or '').lower()).strip()
            index[norm] = vid_el.text
    return index


# Module-level cache for YouTube channel indexes (avoid re-fetching per episode)
_yt_index_cache = {}


def extract_youtube_captions(ep, cfg):
    """Get YouTube auto-captions for an episode.

    Resolution order for video ID:
    1. YouTube link in RSS content or episode page HTML
    2. Title-match against the YouTube channel RSS feed (channel_id in config)
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        print("    ⚠ youtube-transcript-api not installed. Run: pip install youtube-transcript-api")
        return None

    # Strategy 1: find YouTube URL in RSS content or episode page
    video_id = None
    for text in [ep.get('rss_content', ''), ep.get('url', ''), ep.get('audio_url', '')]:
        m = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([\w-]{11})', text)
        if m:
            video_id = m.group(1)
            break

    if not video_id:
        html = fetch(ep['url'], delay=2.0)
        if html:
            m = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([\w-]{11})', html)
            if m:
                video_id = m.group(1)

    # Strategy 2: match episode title against YouTube channel RSS
    if not video_id and cfg.get('youtube_channel_id'):
        ch_id = cfg['youtube_channel_id']
        if ch_id not in _yt_index_cache:
            print(f"    Building YouTube index for channel {ch_id}...")
            _yt_index_cache[ch_id] = _build_youtube_video_index(ch_id)
        yt_index = _yt_index_cache[ch_id]

        ep_norm = re.sub(r'[^a-z0-9]+', ' ', ep['title'].lower()).strip()
        # Try exact match first, then substring match
        for yt_title, vid in yt_index.items():
            if ep_norm == yt_title or ep_norm[:40] in yt_title or yt_title[:40] in ep_norm:
                video_id = vid
                break

    if not video_id:
        print(f"    ⚠ No YouTube video ID found")
        return None

    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_data = ytt_api.fetch(video_id)
        lines = [entry.text for entry in transcript_data]
        text = ' '.join(lines)
        text = re.sub(r'\[Music\]', '', text)
        text = re.sub(r'\[Applause\]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    except Exception as e:
        print(f"    ⚠ YouTube transcript fetch failed (video={video_id}): {e}")
        return None


# Map extractor names to functions
EXTRACTORS = {
    'substack_html': extract_substack_html,
    'acquired_html': extract_acquired_html,
    'happyscribe_html': extract_happyscribe_html,
    'youtube_captions': extract_youtube_captions,
}

# Map discovery methods to functions
DISCOVERERS = {
    'rss': discover_rss,
    'happyscribe': discover_happyscribe,
}


# ---------------------------------------------------------------------------
# Main scraper loop
# ---------------------------------------------------------------------------

def scrape_source(source_key, limit=5, seen=None):
    """Fetch and save new transcripts for a source. Returns list of saved paths."""
    cfg = SOURCES[source_key]
    print(f"\n🎙 {cfg['label']} (Tier {cfg['tier']})")

    # Discover episodes
    discoverer = DISCOVERERS[cfg['discovery']]
    episodes = discoverer(cfg, limit)
    if not episodes:
        print("  ⚠ No episodes found")
        return []

    if cfg['discovery'] == 'rss':
        print(f"  Found {len(episodes)} episodes in feed")

    out_dir = os.path.join(TRANSCRIPT_DIR, cfg['dir'])
    os.makedirs(out_dir, exist_ok=True)

    skip_patterns = [re.compile(p) for p in cfg.get('skip_title_patterns', [])]
    extractor = EXTRACTORS[cfg['extractor']]

    saved = []
    skipped = 0
    for ep in episodes:
        if any(p.search(ep['title']) for p in skip_patterns):
            continue

        ep_id = f"{source_key}::{ep['slug']}"
        if seen is not None and ep_id in seen:
            skipped += 1
            continue

        if len(saved) >= limit:
            break

        print(f"  ↓ [{ep['date']}] {ep['title'][:70]}")

        transcript = extractor(ep, cfg)

        if not transcript or len(transcript) < 500:
            chars = len(transcript) if transcript else 0
            print(f"    ⚠ Transcript too short ({chars} chars), skipping")
            if seen is not None:
                seen.add(ep_id)
            continue

        # Write markdown file
        date_prefix = ep['date'] if ep['date'] != 'unknown' else datetime.now().strftime('%Y-%m-%d')
        filename = f"{date_prefix}-{ep['slug'][:60]}.md"
        filepath = os.path.join(out_dir, filename)
        with open(filepath, 'w') as f:
            f.write(f"# {ep['title']}\n\n")
            f.write(f"**Source:** {cfg['label']}  \n")
            f.write(f"**Date:** {ep['date']}  \n")
            f.write(f"**URL:** {ep['url']}  \n")
            f.write(f"**Tier:** {cfg['tier']}  \n\n")
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
    source_choices = ['all', 'tier1', 'tier2'] + list(SOURCES.keys())
    parser.add_argument('--source', default='all', choices=source_choices,
                        help='Which source to scrape (default: all)')
    parser.add_argument('--limit', type=int, default=5,
                        help='Max episodes per source to fetch (default: 5)')
    parser.add_argument('--refetch', action='store_true',
                        help='Re-fetch even if already seen')
    args = parser.parse_args()

    today = datetime.now().strftime('%Y-%m-%d')
    print(f"🎙 Podcast Transcript Scraper — {today}\n{'='*50}")

    seen = set() if args.refetch else load_seen()

    if args.source == 'all':
        sources = list(SOURCES.keys())
    elif args.source == 'tier1':
        sources = [k for k, v in SOURCES.items() if v['tier'] == 1]
    elif args.source == 'tier2':
        sources = [k for k, v in SOURCES.items() if v['tier'] == 2]
    else:
        sources = [args.source]

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
