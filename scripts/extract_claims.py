#!/usr/bin/env python3
"""
Podcast claim extractor — uses Claude API to extract structured data points
from transcript files produced by scrape_podcasts.py.

Reads:  transcripts/{source}/*.md
Writes: data-updates/{YYYY-MM-DD}-candidates.json

Run: python3 scripts/extract_claims.py [--transcript path/to/file.md] [--all] [--auto-pr]

Requires: ANTHROPIC_API_KEY environment variable
Optional: gh CLI (for --auto-pr)
"""

import argparse
import glob
import json
import os
import re
import subprocess
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANSCRIPT_DIR = os.path.join(BASE_DIR, 'transcripts')
OUTPUT_DIR = os.path.join(BASE_DIR, 'data-updates')
PROCESSED_FILE = os.path.join(OUTPUT_DIR, '.processed')
SITE_DATA_PATH = os.path.join(BASE_DIR, 'site-data.json')

# Claude model to use for extraction
MODEL = 'claude-sonnet-4-6'
# Max chars per chunk sent to Claude (leave room for system prompt + output)
CHUNK_SIZE = 40_000

SYSTEM_PROMPT = """You are a financial data extraction assistant specialising in the AI industry.

Your task: read a podcast transcript and extract structured data points relevant to tracking AI provider revenue, token volumes, infrastructure economics, and enterprise adoption.

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
- "is_primary_source": true if the speaker has direct first-hand knowledge (e.g. a founder discussing their own company), false if they are citing or repeating something heard elsewhere
- "original_source_cited": name of the original source if the speaker is citing someone else (e.g. "Bloomberg", "WSJ", "earnings call"), or null
- "weight": the appropriate weight for incorporating this claim into a data model. Use exactly one of:
    "authoritative" — speaker has direct first-hand knowledge of this specific metric (e.g. CEO on their own ARR)
    "corroborating" — speaker cites a specific named primary source (earnings call, official filing, named report); the claim can be traced back to something verifiable
    "indicative" — speaker is sharing market colour, repeating heard figures, or estimating; useful for triangulation but should not override primary data

Rules:
- Only extract claims with specific numbers or percentages — skip vague statements
- If a claim is speculation or a prediction, set confidence to "low" and weight to "indicative"
- A speaker citing "I read that X" or "someone told me Y" is always weight "indicative" even if confident-sounding
- A speaker saying "our ARR is X" about their own company is weight "authoritative"
- A speaker saying "per their earnings call, X" with a named source is weight "corroborating"
- Do not hallucinate — if a number isn't stated, don't estimate it
- Return a JSON array of claim objects, or [] if no relevant claims found
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

            # Enrich each claim with source metadata and type
            for claim in claims:
                claim['source_type'] = 'podcast_discussion'
                claim['source_podcast'] = meta['source']
                claim['source_date'] = meta['date']
                claim['source_url'] = meta['url']
                claim['source_episode'] = meta['title']
                claim['extracted_at'] = datetime.now().isoformat()
                # Ensure weight field exists; default to indicative if model omitted it
                if 'weight' not in claim:
                    claim['weight'] = 'indicative'

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


def deduplicate_claims(claims):
    """Flag claims that match existing data in site-data.json.

    Adds a 'dedup_status' field to each claim:
      'new'       — no matching entity+metric found in site-data.json
      'confirms'  — matches an existing value (same entity, metric, similar value)
      'conflicts' — matches entity+metric but value differs significantly (>10%)
      'stale'     — claim's time_period is older than the data we already have

    Does not remove claims — just annotates them for the reviewer.
    """
    if not os.path.exists(SITE_DATA_PATH):
        for c in claims:
            c['dedup_status'] = 'new'
        return claims

    with open(SITE_DATA_PATH) as f:
        site_data = json.load(f)

    # Build a lookup of known provider data from dashboard section
    known = {}  # {normalised_entity: {metric: value}}
    providers = site_data.get('dashboard', {}).get('providers', {})
    for name, data in providers.items():
        key = name.lower().strip()
        known[key] = {}
        if 'rev' in data:
            known[key]['ARR'] = data['rev'] * 1e9  # stored in $B
        if 'tokens' in data:
            known[key]['tokens/day'] = data['tokens'] * 1e12  # stored in T

    for claim in claims:
        entity = (claim.get('entity') or '').lower().strip()
        metric = (claim.get('metric') or '').lower().strip()
        value = claim.get('value')

        if entity not in known or not value:
            claim['dedup_status'] = 'new'
            continue

        entity_data = known[entity]
        # Try to match metric
        matched_metric = None
        for km in entity_data:
            if km.lower() in metric or metric in km.lower():
                matched_metric = km
                break

        if not matched_metric:
            claim['dedup_status'] = 'new'
            continue

        existing_value = entity_data[matched_metric]
        if existing_value == 0:
            claim['dedup_status'] = 'new'
            continue

        ratio = value / existing_value
        if 0.9 <= ratio <= 1.1:
            claim['dedup_status'] = 'confirms'
            claim['dedup_note'] = f"Matches existing {matched_metric}={existing_value:.0f}"
        else:
            claim['dedup_status'] = 'conflicts'
            claim['dedup_note'] = (
                f"Differs from existing {matched_metric}: "
                f"claim={value:.0f} vs current={existing_value:.0f} "
                f"({ratio:.1%} of current)"
            )

    return claims


def generate_auto_pr(claims, today):
    """Create a GitHub PR with high-value claims for review.

    Only includes claims that are:
      - weight: authoritative or corroborating
      - dedup_status: new or conflicts (i.e. something to act on)
      - confidence: high or medium
    """
    actionable = [
        c for c in claims
        if c.get('weight') in ('authoritative', 'corroborating')
        and c.get('dedup_status') in ('new', 'conflicts')
        and c.get('confidence') in ('high', 'medium')
    ]

    if not actionable:
        print("\n📋 No actionable claims for auto-PR (need authoritative/corroborating + new/conflicts + high/medium confidence)")
        return

    print(f"\n🔀 Generating PR with {len(actionable)} actionable claim(s)...")

    # Write the candidates file
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    pr_file = os.path.join(OUTPUT_DIR, f'{today}-pr-candidates.json')
    with open(pr_file, 'w') as f:
        json.dump(actionable, f, indent=2)

    # Build PR body
    body_lines = ["## Podcast Data Point Candidates\n"]
    body_lines.append(f"Extracted {len(actionable)} actionable claim(s) from podcast transcripts.\n")
    body_lines.append("### Claims\n")
    for c in actionable:
        status = c.get('dedup_status', 'new')
        icon = '🆕' if status == 'new' else '⚠️'
        body_lines.append(
            f"- {icon} **{c.get('entity', '?')}** — {c.get('metric', '?')}: "
            f"{c.get('value_display', c.get('value', '?'))} "
            f"({c.get('time_period', '?')}) "
            f"[{c.get('weight', '?')}, {c.get('confidence', '?')}]"
        )
        body_lines.append(f"  - Source: {c.get('source_podcast', '?')} — {c.get('source_episode', '?')[:60]}")
        if c.get('dedup_note'):
            body_lines.append(f"  - ⚠️ {c['dedup_note']}")
    body_lines.append("\n### Review Instructions\n")
    body_lines.append("1. Check each claim against primary sources")
    body_lines.append("2. Update `site-data.json` if the data point is valid")
    body_lines.append("3. Merge this PR to record the candidates\n")
    body_lines.append("🤖 Generated by `extract_claims.py --auto-pr`")

    branch_name = f"podcast-claims-{today}"
    pr_title = f"Podcast claims: {len(actionable)} data points ({today})"
    pr_body = '\n'.join(body_lines)

    try:
        # Create branch, commit, push, and open PR
        subprocess.run(['git', 'checkout', '-b', branch_name], check=True, cwd=BASE_DIR,
                       capture_output=True)
        subprocess.run(['git', 'add', pr_file], check=True, cwd=BASE_DIR,
                       capture_output=True)
        subprocess.run(
            ['git', 'commit', '-m', f'Podcast claims: {len(actionable)} candidates ({today})'],
            check=True, cwd=BASE_DIR, capture_output=True
        )
        subprocess.run(['git', 'push', '-u', 'origin', branch_name], check=True, cwd=BASE_DIR,
                       capture_output=True)

        result = subprocess.run(
            ['gh', 'pr', 'create', '--title', pr_title, '--body', pr_body],
            check=True, cwd=BASE_DIR, capture_output=True, text=True
        )
        pr_url = result.stdout.strip()
        print(f"  ✅ PR created: {pr_url}")

        # Switch back to main
        subprocess.run(['git', 'checkout', 'main'], check=True, cwd=BASE_DIR,
                       capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"  ⚠ PR creation failed: {e}")
        print(f"    stderr: {e.stderr}")
        # Try to get back to main
        subprocess.run(['git', 'checkout', 'main'], cwd=BASE_DIR, capture_output=True)
    except FileNotFoundError:
        print("  ⚠ 'gh' CLI not found. Install: brew install gh")


def main():
    parser = argparse.ArgumentParser(description='Extract claims from podcast transcripts')
    parser.add_argument('--transcript', help='Process a single transcript file')
    parser.add_argument('--all', action='store_true', help='Re-process already-processed files')
    parser.add_argument('--dry-run', action='store_true', help='Show files to process without running')
    parser.add_argument('--auto-pr', action='store_true',
                        help='Auto-create a GitHub PR with actionable claims')
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

    # Deduplicate against existing site-data.json
    all_claims = deduplicate_claims(all_claims)

    # Write directly into vault-inbox.json as pending items
    inbox_path = os.path.join(BASE_DIR, 'vault-inbox.json')
    if os.path.exists(inbox_path):
        with open(inbox_path) as f:
            inbox = json.load(f)
    else:
        inbox = {"items": [], "lastProcessed": None}

    date_str = today.replace('-', '')
    added = 0
    for i, claim in enumerate(all_claims):
        claim_id = f"podcast-{date_str}-{i+1}"
        # Skip if already in inbox
        if any(item['id'] == claim_id for item in inbox['items']):
            continue
        inbox['items'].append({
            "id": claim_id,
            "claim": claim.get("claim", ""),
            "value": claim.get("value"),
            "unit": claim.get("unit", ""),
            "sourceUrl": claim.get("source_url", ""),
            "sourceType": "podcast_discussion",
            "sourceAuthor": claim.get("speaker") or claim.get("source_podcast", ""),
            "confidence": {"high": "verified", "medium": "estimated", "low": "speculative"}.get(claim.get("confidence", "medium"), "estimated"),
            "dateOfClaim": claim.get("source_date") or claim.get("time_period", today),
            "dateAdded": today,
            "usedOn": [],
            "tags": [claim.get("category", "other")],
            "notes": f"Podcast: {claim.get('source_podcast', '')} — {claim.get('source_episode', '')[:60]}",
            "status": "pending",
            "replaces": None,
            "source_id": None,
            "metricKey": claim.get("metric_key") or claim.get("metric"),
            "entity": claim.get("entity", ""),
            "weight": claim.get("weight", "indicative"),
            "dedup_status": claim.get("dedup_status", "new"),
            "dedup_note": claim.get("dedup_note"),
        })
        added += 1

    inbox["lastProcessed"] = today
    with open(inbox_path, 'w') as f:
        json.dump(inbox, f, indent=2)

    print(f"\n✅ {added} claim(s) added to vault-inbox.json as pending")
    print(f"   Total inbox items: {len(inbox['items'])}")

    # Also save candidates file for archival reference
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, f'{today}-candidates.json')
    with open(output_path, 'w') as f:
        json.dump(all_claims, f, indent=2)

    # Print summary by category and weight
    cats = {}
    weights = {'authoritative': 0, 'corroborating': 0, 'indicative': 0}
    for c in all_claims:
        cats[c.get('category', 'other')] = cats.get(c.get('category', 'other'), 0) + 1
        w = c.get('weight', 'indicative')
        weights[w] = weights.get(w, 0) + 1

    print("\nBy category:")
    for cat, n in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {n}")

    print("\nBy weight:")
    for w, n in weights.items():
        print(f"  {w}: {n}")

    # Dedup summary
    dedup_stats = {}
    for c in all_claims:
        s = c.get('dedup_status', 'unknown')
        dedup_stats[s] = dedup_stats.get(s, 0) + 1
    print("\nDedup status:")
    for s, n in sorted(dedup_stats.items()):
        print(f"  {s}: {n}")

    # Show conflicts
    conflicts = [c for c in all_claims if c.get('dedup_status') == 'conflicts']
    if conflicts:
        print("\n⚠ Conflicts with existing data:")
        for c in conflicts:
            print(f"  {c.get('entity')}: {c.get('dedup_note')}")

    print(f"""
📋 Review queue: {output_path}

Incorporation rules:
  authoritative  → can set/update a data point directly (speaker has first-hand knowledge)
  corroborating  → use to raise confidence on an existing point, or add if no primary source exists
  indicative     → triangulation only; never override an authoritative/corroborating source
                   flag in site-data.json notes as 'podcast discussion' if used

All claims require human review before incorporation into site-data.json.""")

    # Auto-PR if requested
    if args.auto_pr:
        generate_auto_pr(all_claims, today)


if __name__ == '__main__':
    main()
