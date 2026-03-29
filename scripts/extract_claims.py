#!/usr/bin/env python3
"""
Podcast claim extractor — uses Claude API to extract structured data points
from transcript files produced by scrape_podcasts.py.

Reads:  transcripts/{source}/*.md
Writes: data-updates/{YYYY-MM-DD}-candidates.json

Run: python3 scripts/extract_claims.py [--transcript path/to/file.md] [--all]

Requires: ANTHROPIC_API_KEY environment variable
"""

import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANSCRIPT_DIR = os.path.join(BASE_DIR, 'transcripts')
OUTPUT_DIR = os.path.join(BASE_DIR, 'data-updates')
PROCESSED_FILE = os.path.join(OUTPUT_DIR, '.processed')

# Claude model to use for extraction
MODEL = 'claude-sonnet-4-6'
# Max chars per chunk sent to Claude (leave room for system prompt + output)
CHUNK_SIZE = 40_000

SYSTEM_PROMPT = """You are a financial data extraction assistant specialising in the AI industry.

Your task: read a podcast transcript and extract structured data points that are relevant to tracking AI provider revenue, token volumes, infrastructure economics, and enterprise adoption.

For each concrete claim found, output a JSON object with these fields:
- "claim": verbatim or lightly paraphrased quote (1-2 sentences)
- "category": one of: provider_revenue | token_volume | pricing | gpu_infrastructure | enterprise_adoption | skeptical_bear_case | valuation_funding | other
- "entity": company or product name (e.g. "OpenAI", "Claude", "Copilot")
- "metric": what is being measured (e.g. "ARR", "tokens/day", "seats", "H100 count")
- "value": numeric value as a number, or null if unclear
- "unit": unit of value (e.g. "USD", "tokens", "seats", "GPUs")
- "value_display": human-readable value string (e.g. "$16.8B", "15M seats")
- "time_period": when this applies (e.g. "Q1 2026", "2025", "as of March 2026")
- "confidence": "high" | "medium" | "low"
- "speaker": name of speaker making the claim, or null
- "is_primary_source": true if speaker has direct knowledge, false if citing another source
- "original_source_cited": name of the original source if speaker is citing someone else, or null

Rules:
- Only extract claims with specific numbers or percentages — skip vague statements
- If a claim is clearly speculation or a prediction, set confidence to "low"
- If the speaker explicitly says they heard it from another source, set is_primary_source to false
- Do not hallucinate — if a number isn't stated, don't estimate it
- Return a JSON array of claim objects, or an empty array [] if no relevant claims found
- Return ONLY the JSON array, no other text"""


def load_processed():
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE) as f:
            return set(json.load(f))
    return set()


def save_processed(processed):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(PROCESSED_FILE, 'w') as f:
        json.dump(sorted(processed), f, indent=2)


def get_transcript_files(specific=None):
    """Return list of transcript .md files to process."""
    if specific:
        return [specific] if os.path.exists(specific) else []
    return sorted(glob.glob(os.path.join(TRANSCRIPT_DIR, '**', '*.md'), recursive=True))


def parse_transcript_meta(filepath):
    """Extract metadata from transcript file header."""
    meta = {'source': '', 'date': '', 'url': '', 'title': ''}
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line.startswith('# '):
                meta['title'] = line[2:].strip()
            elif line.startswith('**Source:**'):
                meta['source'] = line.replace('**Source:**', '').strip()
            elif line.startswith('**Date:**'):
                meta['date'] = line.replace('**Date:**', '').strip()
            elif line.startswith('**URL:**'):
                meta['url'] = line.replace('**URL:**', '').strip()
            elif line == '---':
                break
    return meta


def chunk_transcript(text, chunk_size=CHUNK_SIZE):
    """Split transcript into overlapping chunks, breaking on paragraph boundaries."""
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            # Break at last paragraph boundary before end
            last_para = text.rfind('\n\n', start, end)
            if last_para > start + chunk_size // 2:
                end = last_para
        chunks.append(text[start:end])
        start = end - 500  # 500-char overlap to catch claims spanning chunk boundaries
    return chunks


def extract_from_transcript(filepath, client):
    """Run Claude extraction on a transcript file. Returns list of claim dicts."""
    meta = parse_transcript_meta(filepath)
    print(f"\n  📄 {os.path.basename(filepath)}")
    print(f"     Source: {meta['source']} | Date: {meta['date']}")

    with open(filepath) as f:
        full_text = f.read()

    # Strip the header block (metadata before ---)
    body_start = full_text.find('---\n\n')
    transcript_text = full_text[body_start + 5:] if body_start >= 0 else full_text

    if len(transcript_text) < 200:
        print(f"     ⚠ Transcript too short, skipping")
        return []

    chunks = chunk_transcript(transcript_text)
    print(f"     Processing {len(chunks)} chunk(s) (~{len(transcript_text):,} chars total)")

    all_claims = []
    for i, chunk in enumerate(chunks):
        if len(chunks) > 1:
            print(f"     Chunk {i+1}/{len(chunks)}...", end=' ', flush=True)

        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                messages=[{
                    'role': 'user',
                    'content': f"Extract data points from this transcript chunk:\n\n{chunk}"
                }]
            )
            raw = response.content[0].text.strip()

            # Strip markdown code fences if present
            raw = re.sub(r'^```(?:json)?\s*', '', raw)
            raw = re.sub(r'\s*```$', '', raw)

            claims = json.loads(raw)
            if not isinstance(claims, list):
                claims = []

            # Enrich each claim with source metadata
            for claim in claims:
                claim['source_podcast'] = meta['source']
                claim['source_date'] = meta['date']
                claim['source_url'] = meta['url']
                claim['source_episode'] = meta['title']
                claim['extracted_at'] = datetime.now().isoformat()

            if len(chunks) > 1:
                print(f"{len(claims)} claim(s)")
            all_claims.extend(claims)

        except json.JSONDecodeError as e:
            print(f"\n     ⚠ JSON parse error in chunk {i+1}: {e}")
            print(f"     Raw response: {raw[:200]}")
        except Exception as e:
            print(f"\n     ⚠ API error in chunk {i+1}: {e}")

    print(f"     ✅ {len(all_claims)} claim(s) extracted")
    return all_claims


def main():
    parser = argparse.ArgumentParser(description='Extract claims from podcast transcripts')
    parser.add_argument('--transcript', help='Process a single transcript file')
    parser.add_argument('--all', action='store_true', help='Re-process already-processed files')
    parser.add_argument('--dry-run', action='store_true', help='Show files to process without running')
    args = parser.parse_args()

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
    except ImportError:
        print("❌ anthropic package not installed. Run: pip install anthropic")
        sys.exit(1)

    today = datetime.now().strftime('%Y-%m-%d')
    print(f"🔍 Podcast Claim Extractor — {today}\n{'='*50}")

    files = get_transcript_files(args.transcript)
    if not files:
        print("No transcript files found. Run scrape_podcasts.py first.")
        sys.exit(0)

    processed = set() if args.all else load_processed()
    to_process = [f for f in files if f not in processed]

    print(f"Transcripts found: {len(files)} total, {len(to_process)} unprocessed")

    if args.dry_run:
        for f in to_process:
            print(f"  Would process: {f}")
        return

    if not to_process:
        print("Nothing new to process. Use --all to re-process everything.")
        return

    all_claims = []
    for filepath in to_process:
        claims = extract_from_transcript(filepath, client)
        all_claims.extend(claims)
        processed.add(filepath)
        save_processed(processed)

    if not all_claims:
        print("\nNo claims extracted.")
        return

    # Save to review queue
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, f'{today}-candidates.json')

    # Append to existing file for today if it exists
    existing = []
    if os.path.exists(output_path):
        with open(output_path) as f:
            existing = json.load(f)

    combined = existing + all_claims
    with open(output_path, 'w') as f:
        json.dump(combined, f, indent=2)

    print(f"\n✅ {len(all_claims)} claim(s) written to {output_path}")
    print(f"   Total in today's queue: {len(combined)}")

    # Print summary by category
    cats = {}
    for c in all_claims:
        cat = c.get('category', 'other')
        cats[cat] = cats.get(cat, 0) + 1
    print("\nBy category:")
    for cat, n in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {n}")

    print(f"\n📋 Review queue: {output_path}")
    print("   Edit/approve claims, then incorporate into site-data.json manually.")


if __name__ == '__main__':
    main()
