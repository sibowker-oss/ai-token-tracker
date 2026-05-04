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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coerce_date import coerce_or_keep  # noqa: E402
from log_run import logged_run  # noqa: E402
from score_materiality import score as score_materiality  # noqa: E402  (wq-040)
TRANSCRIPT_DIR = os.path.join(BASE_DIR, 'transcripts')
OUTPUT_DIR = os.path.join(BASE_DIR, 'data-updates')
PROCESSED_FILE = os.path.join(OUTPUT_DIR, '.processed')
SITE_DATA_PATH = os.path.join(BASE_DIR, 'site-data.json')

# Claude model to use for extraction
MODEL = 'claude-sonnet-4-6'
# Max chars per chunk sent to Claude (leave room for system prompt + output)
CHUNK_SIZE = 40_000

SYSTEM_PROMPT = """You are a financial data extraction assistant specialising in the AI industry.

Your task: read a podcast transcript and extract ONLY data points directly relevant to tracking the AI/ML inference economy — specifically AI provider revenue, token/API volumes, model pricing, GPU/compute infrastructure costs, and enterprise AI adoption spend.

SCOPE — extract claims about:
- AI provider financials: revenue, ARR, growth rates, margins for companies whose primary business is AI/ML (OpenAI, Anthropic, Google DeepMind/Gemini, Meta AI, Mistral, Cohere, xAI, Perplexity, Stability, Midjourney, etc.)
- Cloud AI services: AWS Bedrock, Azure OpenAI, GCP Vertex AI spend and usage
- Token/inference economics: tokens/day, API call volumes, cost per token, inference pricing
- GPU/compute infrastructure: GPU counts, cluster sizes, training costs, data center power for AI workloads, chip supply (NVIDIA, AMD, TSMC, etc.)
- Enterprise AI adoption: AI spend as % of IT budget, seats/licenses for AI tools, AI-driven revenue
- AI model metrics: benchmark scores, context windows, throughput — only when tied to commercial impact
- AI valuations/funding: only for AI-native companies

DO NOT extract:
- Historical financials predating 2023 (e.g. "Google did $86M revenue in 2001") — unless explicitly compared to current AI metrics
- Non-AI business metrics (defense contracts, banking revenue, retail sales, oil production, etc.) even if mentioned by a tech investor
- General macroeconomic claims (GDP, interest rates, government spending) unless directly about AI policy/investment
- Company metrics for non-AI businesses (Anduril defense, traditional SaaS, fintech, crypto) unless specifically about their AI/ML division
- Biographical facts, headcounts, or org charts unless tied to an AI spending figure
- Vague market commentary without specific numbers

For each concrete claim found, output a JSON object with these fields:
- "claim": verbatim or lightly paraphrased quote (1-2 sentences)
- "category": one of: provider_revenue | token_volume | pricing | gpu_infrastructure | enterprise_adoption | skeptical_bear_case | valuation_funding (pick the closest match — do NOT use "other")
- "entity": company or product name (e.g. "OpenAI", "Claude", "Copilot")
- "metric": what is being measured (e.g. "ARR", "tokens/day", "seats", "H100 count")
- "value": numeric value as a number, or null if unclear
- "unit": unit of value (e.g. "USD", "tokens", "seats", "GPUs")
- "value_display": human-readable value string (e.g. "$16.8B", "15M seats")
- "time_period": when this applies (e.g. "Q1 2026", "2025", "as of March 2026")
- "time_period_scope": one of: "annual" | "h1" | "h2" | "q1" | "q2" | "q3" | "q4" | "exit_snapshot" | "monthly_peak" | "point_in_time"
- "period_qualifier_detected": short string quoting the qualifier you matched (e.g. "H1 2025", "best 4-week × 12", "Feb 2026 monthly peak"), or null when scope is "annual" with no qualifier

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
- When in doubt about relevance, SKIP the claim — fewer high-quality extractions are better than a large noisy set
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


# wq-041 — source-excerpt extraction
# Find the claim's value or first words of its text in the source chunk and
# return ~200 chars of surrounding context with the matched value bolded.
# Best-effort: returns None if no anchor can be located. Used by the review UI
# (review.html) to show source context inline without a click-out.

_NUM_FORMATS = [
    lambda v: f"{v:.0f}",
    lambda v: f"{v:.1f}",
    lambda v: f"{v:.2f}",
    lambda v: f"{v:,.0f}",
    lambda v: f"{v:,.1f}",
]
_EXCERPT_CONTEXT_CHARS = 200


def _format_value_candidates(value):
    """Build a list of plausible string forms a number might take in source text.

    Returned list is sorted longest-first so the matching loop prefers the
    most specific form. Without this, an integer value's bare "7" candidate
    could match "$7 billion" elsewhere in the chunk before the more accurate
    "$6.9 billion" form for value=6900000000 was tried.

    Covers digit forms ($14B, 14B, 14.5B), spelled-out forms ($14 billion,
    14 billion, $14.5 billion, 14 million, etc.), and bare integers. Spelled-
    out forms matter most — they're the dominant pattern in podcast/news
    transcripts. wq-041 tuning fix 2026-05-02 (was hitting 39% on podcasts).
    """
    if value is None:
        return []
    candidates = set()
    try:
        for fmt in _NUM_FORMATS:
            candidates.add(fmt(value))
    except (TypeError, ValueError):
        pass
    if isinstance(value, (int, float)):
        # Digit-suffix forms ($14B, 14B, $14.5B, 14M, etc.)
        for unit, divisor in (('B', 1e9), ('M', 1e6), ('T', 1e12), ('K', 1e3)):
            if abs(value) >= divisor:
                scaled = value / divisor
                for fmt in _NUM_FORMATS[:3]:
                    candidates.add(f"{fmt(scaled)}{unit}")
                    candidates.add(f"${fmt(scaled)}{unit}")
        # Spelled-out unit forms — the dominant pattern in podcast transcripts.
        # Examples generated: "$20 billion", "20 billion", "$6.9 billion",
        # "950 million", "$2 trillion".
        for unit_word, divisor in (('billion', 1e9), ('million', 1e6),
                                    ('trillion', 1e12), ('thousand', 1e3)):
            if abs(value) >= divisor:
                scaled = value / divisor
                for fmt in _NUM_FORMATS[:3]:
                    scaled_str = fmt(scaled)
                    candidates.add(f"{scaled_str} {unit_word}")
                    candidates.add(f"${scaled_str} {unit_word}")
        # Bare integer for small numbers
        if abs(value) < 1e9 and float(value).is_integer():
            candidates.add(str(int(value)))
    # Drop empty / pathological short candidates that would over-match,
    # then sort longest-first so the matcher prefers more specific forms.
    return sorted(
        (c for c in candidates if c and len(c) >= 2),
        key=lambda c: (-len(c), c),
    )


def _extract_excerpt(chunk_text, claim, context_chars=_EXCERPT_CONTEXT_CHARS):
    if not chunk_text or not isinstance(chunk_text, str):
        return None
    value = claim.get('value')
    claim_text = claim.get('claim') or ''

    # Try the value forms first — they're the most distinctive anchor.
    for candidate in _format_value_candidates(value):
        idx = chunk_text.find(candidate)
        if idx < 0:
            # Try case-insensitive for unit-suffixed forms ($14B vs $14b)
            idx = chunk_text.lower().find(candidate.lower())
        if idx >= 0:
            start = max(0, idx - context_chars)
            end = min(len(chunk_text), idx + len(candidate) + context_chars)
            excerpt = chunk_text[start:end].strip()
            # Bold the matched value in the excerpt (markdown rendered by review.html)
            return excerpt.replace(candidate, f"**{candidate}**", 1)

    # Fallback: first 30 chars of claim text (lowercased compare for robustness)
    snippet = claim_text[:30].strip()
    if len(snippet) >= 8:
        idx = chunk_text.lower().find(snippet.lower())
        if idx >= 0:
            start = max(0, idx - 80)
            end = min(len(chunk_text), idx + context_chars * 2)
            return chunk_text[start:end].strip()

    return None


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
                # wq-041: extract source excerpt from the chunk so the
                # review UI can show context inline without a click-out.
                claim['source_excerpt'] = _extract_excerpt(chunk, claim)

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


# Entities and keywords used for post-extraction relevance filtering
AI_ENTITIES = {
    'openai', 'anthropic', 'google', 'deepmind', 'gemini', 'microsoft', 'azure', 'meta',
    'amazon', 'aws', 'bedrock', 'nvidia', 'deepseek', 'mistral', 'cohere', 'stability',
    'midjourney', 'perplexity', 'claude', 'gpt', 'llama', 'databricks', 'snowflake',
    'salesforce', 'oracle', 'bytedance', 'baidu', 'alibaba', 'tencent', 'xai', 'grok',
    'inflection', 'adobe', 'palantir', 'hugging face', 'huggingface', 'together ai',
    'groq', 'cerebras', 'replicate', 'ai21', 'character.ai', 'runway', 'openrouter',
    'samsung', 'tsmc', 'intel', 'amd', 'broadcom', 'asml', 'arm', 'qualcomm',
    'sk hynix', 'micron', 'copilot', 'chatgpt', 'vertex', 'sagemaker',
}
AI_KEYWORDS = {
    'artificial intelligence', 'machine learning', 'llm', 'large language model',
    'neural network', 'transformer', 'token', 'inference', 'training run',
    'gpu cluster', 'data center', 'compute', 'fine-tun', 'embedding', 'chatbot',
    'copilot', 'ai agent', 'generative ai', 'foundation model', 'model api',
    'ai spend', 'ai revenue', 'ai infrastructure', 'gpu', 'h100', 'h200', 'b200',
    'gb200', 'tpu', 'ai chip', 'accelerator',
}
AI_CATEGORIES = {
    'provider_revenue', 'token_volume', 'pricing', 'gpu_infrastructure',
    'enterprise_adoption', 'skeptical_bear_case', 'valuation_funding',
}


def filter_relevant_claims(claims):
    """Post-extraction filter: drop claims that aren't about AI/ML industry.

    This catches anything the model extracted despite the scoping instructions.
    Returns only claims where the entity, claim text, or category signals AI relevance.
    """
    kept = []
    dropped = 0
    for claim in claims:
        entity = (claim.get('entity') or '').lower()
        text = (claim.get('claim') or '').lower()
        category = (claim.get('category') or '').lower()

        is_relevant = (
            category in AI_CATEGORIES
            or any(e in entity for e in AI_ENTITIES)
            or any(e in text for e in AI_ENTITIES)
            or any(k in text for k in AI_KEYWORDS)
        )

        # Extra check: reject "other" category unless text has strong AI signal
        if category == 'other' and not any(k in text for k in AI_KEYWORDS) and not any(e in text for e in AI_ENTITIES):
            is_relevant = False

        if is_relevant:
            # Drop the "other" category — force re-bucket into a real category
            if category == 'other':
                claim['category'] = 'enterprise_adoption'
            kept.append(claim)
        else:
            dropped += 1

    if dropped:
        print(f"     🔍 Relevance filter: kept {len(kept)}, dropped {dropped} off-topic")
    return kept


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
    with logged_run("extract_claims.py") as outputs:
        _main_impl(outputs)


def _main_impl(outputs):
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
        outputs["transcripts_found"] = 0
        outputs["claims_added"] = 0
        return

    processed = set() if args.all else load_processed()
    to_process = [f for f in files if f not in processed]

    print(f"Transcripts found: {len(files)} total, {len(to_process)} unprocessed")
    outputs["transcripts_found"] = len(files)
    outputs["transcripts_processed"] = len(to_process)
    outputs["dry_run"] = bool(args.dry_run)

    if args.dry_run:
        for f in to_process:
            print(f"  Would process: {f}")
        return

    if not to_process:
        print("Nothing new to process. Use --all to re-process everything.")
        outputs["claims_added"] = 0
        return

    all_claims = []
    for filepath in to_process:
        claims = extract_from_transcript(filepath, client)
        all_claims.extend(claims)
        processed.add(filepath)
        save_processed(processed)

    if not all_claims:
        print("\nNo claims extracted.")
        outputs["claims_added"] = 0
        outputs["claims_extracted_pre_filter"] = 0
        return

    # Filter out off-topic claims before dedup
    pre_count = len(all_claims)
    all_claims = filter_relevant_claims(all_claims)
    print(f"\n🔍 Relevance filter: {pre_count} → {len(all_claims)} claims")

    if not all_claims:
        print("No relevant claims after filtering.")
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

    # wq-040 — load entities + schema once for materiality scoring per item
    try:
        with open(os.path.join(BASE_DIR, 'entities.json')) as f:
            _entities = json.load(f)
        with open(os.path.join(BASE_DIR, 'metric-schema.json')) as f:
            _schema = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        _entities, _schema = {"companies": []}, {}

    date_str = today.replace('-', '')
    added = 0
    for i, claim in enumerate(all_claims):
        claim_id = f"podcast-{date_str}-{i+1}"
        # Skip if already in inbox
        if any(item['id'] == claim_id for item in inbox['items']):
            continue
        new_item = {
            "id": claim_id,
            "claim": claim.get("claim", ""),
            "value": claim.get("value"),
            "unit": claim.get("unit", ""),
            "sourceUrl": claim.get("source_url", ""),
            "sourceType": "podcast_discussion",
            "sourceAuthor": claim.get("speaker") or claim.get("source_podcast", ""),
            "confidence": {"high": "verified", "medium": "estimated", "low": "speculative"}.get(claim.get("confidence", "medium"), "estimated"),
            "dateOfClaim": coerce_or_keep(claim.get("source_date") or claim.get("time_period") or today, today),
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
            # wq-041: source grounding for review UI. Reduces mis-interpretation
            # by surfacing the surrounding text and primary-source signals.
            "sourceExcerpt": claim.get("source_excerpt"),
            "isPrimarySource": claim.get("is_primary_source"),
            "originalSourceCited": claim.get("original_source_cited"),
            # wq-054 — sub-period attribution. apply_decisions.py routes per
            # scope so H1/Q3/exit-snapshot/monthly-peak don't pollute annual.
            "timePeriodScope": claim.get("time_period_scope") or "annual",
            "periodQualifier": claim.get("period_qualifier_detected"),
        }
        # wq-040: score materiality at write time so review.html lane filter works.
        try:
            new_item["materiality"] = score_materiality(new_item, _entities, _schema)
        except Exception:
            pass
        inbox['items'].append(new_item)
        added += 1

    inbox["lastProcessed"] = today
    with open(inbox_path, 'w') as f:
        json.dump(inbox, f, indent=2)

    print(f"\n✅ {added} claim(s) added to vault-inbox.json as pending")
    print(f"   Total inbox items: {len(inbox['items'])}")
    outputs["claims_added"] = added
    outputs["claims_extracted_pre_filter"] = pre_count
    outputs["inbox_total"] = len(inbox['items'])

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
