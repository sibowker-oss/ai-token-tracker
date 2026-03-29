#!/usr/bin/env python3
"""
Daily/weekly signal scraper for AI Token Dashboard.
Pulls real data from public APIs to track trends and validate estimates.

Sources:
- PyPI download stats (openai, anthropic, langchain, litellm, vllm, etc.)
- npm download stats (openai, @anthropic-ai/sdk, ai, etc.)
- HuggingFace model download counts (Llama, DeepSeek, Mistral, etc.)
- OpenRouter model count and pricing
- GitHub release download counts (Ollama, vLLM, llama.cpp — binary installs)
- Docker Hub pull counts (vLLM, text-generation-inference — container deployments)

Run: python3 scripts/scrape_signals.py
Output: data/signals_YYYY-MM-DD.json + data/signals_latest.json
"""

import json
import os
import re
import sys
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_json(url, timeout=15):
    """Fetch JSON from a URL."""
    try:
        req = Request(url, headers={'User-Agent': 'AI-Token-Tracker/1.0'})
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"  ⚠ Failed: {url} — {e}")
        return None

def scrape_pypi():
    """Fetch monthly download counts from PyPI."""
    packages = [
        'openai', 'anthropic', 'langchain-core', 'litellm',
        'google-generativeai', 'vllm', 'transformers', 'ollama',
        'mistralai', 'cohere', 'together', 'groq',
    ]
    results = {}
    print("📦 PyPI downloads (last month):")
    for pkg in packages:
        data = fetch_json(f'https://pypistats.org/api/packages/{pkg}/recent?period=month')
        if data and 'data' in data:
            count = data['data'].get('last_month', 0)
            results[pkg] = count
            print(f"  {pkg}: {count:,}")
        else:
            results[pkg] = None
    return results

def scrape_npm():
    """Fetch monthly download counts from npm."""
    packages = [
        'openai', '@anthropic-ai/sdk', '@langchain/core', 'ai',
        '@google/generative-ai', 'ollama', '@mistralai/mistralai',
        'cohere-ai', 'groq-sdk',
    ]
    results = {}
    print("\n📦 npm downloads (last month):")
    for pkg in packages:
        data = fetch_json(f'https://api.npmjs.org/downloads/point/last-month/{pkg}')
        if data and 'downloads' in data:
            count = data['downloads']
            results[pkg] = count
            print(f"  {pkg}: {count:,}")
        else:
            results[pkg] = None
    return results

def scrape_huggingface():
    """Fetch 30-day download counts for key open-source models."""
    models = [
        'meta-llama/Llama-3.1-8B-Instruct',
        'meta-llama/Llama-3.1-70B-Instruct',
        'meta-llama/Llama-4-Scout-17B-16E-Instruct',
        'deepseek-ai/DeepSeek-R1',
        'deepseek-ai/DeepSeek-V3',
        'mistralai/Mistral-7B-Instruct-v0.3',
        'Qwen/Qwen2.5-72B-Instruct',
        'google/gemma-2-9b-it',
    ]
    results = {}
    print("\n🤗 HuggingFace model downloads (30d):")
    for model_id in models:
        data = fetch_json(f'https://huggingface.co/api/models/{model_id}')
        if data and 'downloads' in data:
            count = data['downloads']
            results[model_id] = count
            short = model_id.split('/')[-1]
            print(f"  {short}: {count:,}")
        else:
            results[model_id] = None
    return results

def scrape_github():
    """Fetch release download counts for key self-hosted AI tools from GitHub API.

    Uses unauthenticated API (60 req/hr limit) — we make ~3 calls, well within budget.
    Captures binary install counts, which are more representative of actual deployments
    than PyPI package downloads (which include CI, scripted installs, etc.).
    """
    repos = [
        ('ollama/ollama', 'ollama'),
        ('vllm-project/vllm', 'vllm'),
        ('ggml-org/llama.cpp', 'llama_cpp'),
        ('huggingface/text-generation-inference', 'tgi'),
    ]
    results = {}
    print("\n🐙 GitHub release downloads:")
    for repo, key in repos:
        data = fetch_json(f'https://api.github.com/repos/{repo}/releases?per_page=5')
        if not data:
            results[key] = None
            continue
        total_downloads = 0
        latest_tag = None
        for release in data:
            if release.get('prerelease') or release.get('draft'):
                continue
            if latest_tag is None:
                latest_tag = release.get('tag_name', 'unknown')
            for asset in release.get('assets', []):
                total_downloads += asset.get('download_count', 0)
        results[key] = {'total_downloads': total_downloads, 'latest_tag': latest_tag}
        print(f"  {key}: {total_downloads:,} total release downloads (latest: {latest_tag})")
    return results


def scrape_docker_hub():
    """Fetch container pull counts from Docker Hub for key AI inference runtimes.

    Container pulls are a strong signal for enterprise/production self-hosted deployments —
    organisations running vLLM in production almost always use the official Docker image.
    Note: TGI is tracked via GitHub releases (hosted on ghcr.io, not Docker Hub).
    """
    images = [
        ('vllm/vllm-openai', 'vllm'),
    ]
    results = {}
    print("\n🐳 Docker Hub pulls:")
    for image, key in images:
        data = fetch_json(f'https://hub.docker.com/v2/repositories/{image}/')
        if data and 'pull_count' in data:
            count = data['pull_count']
            results[key] = count
            print(f"  {key}: {count:,} pulls")
        else:
            results[key] = None
    return results


def scrape_openrouter():
    """Fetch model count and pricing summary from OpenRouter."""
    print("\n🔀 OpenRouter:")
    data = fetch_json('https://openrouter.ai/api/v1/models')
    if not data or 'data' not in data:
        return None

    models = data['data']
    total = len(models)
    providers = set()
    prices = []
    free_count = 0

    for m in models:
        provider = m.get('id', '').split('/')[0]
        providers.add(provider)
        out_price = float(m.get('pricing', {}).get('completion', '0') or '0')
        per_million = out_price * 1_000_000
        if per_million == 0:
            free_count += 1
        else:
            prices.append(per_million)

    result = {
        'total_models': total,
        'providers': len(providers),
        'free_models': free_count,
        'min_output_price_per_m': min(prices) if prices else 0,
        'max_output_price_per_m': max(prices) if prices else 0,
        'median_output_price_per_m': sorted(prices)[len(prices)//2] if prices else 0,
    }

    print(f"  Models: {total}, Providers: {len(providers)}, Free: {free_count}")
    print(f"  Output $/1M: min ${result['min_output_price_per_m']:.3f}, median ${result['median_output_price_per_m']:.2f}, max ${result['max_output_price_per_m']:.1f}")
    return result


def scrape_openrouter_rankings():
    """Fetch weekly token volume by provider from the OpenRouter rankings page.

    The rankings page is a Next.js App Router app — data lives in RSC
    self.__next_f.push() script chunks, not in a public JSON API.

    The time-series chart chunk contains entries like:
      {"x": "2026-03-22", "ys": {"google": 2959651689841, "anthropic": 2859450564998, ...}}

    We take the second-to-last entry (most recent COMPLETE week) and sum all
    provider token counts.  The last entry is the current in-progress week.

    GMV is estimated using a blended output price of $0.15/M tokens — a
    conservative estimate given the mix of cheap (minimax, stepfun, xiaomi)
    and expensive (anthropic, openai) models.  OpenRouter's take rate is ~10%.
    """
    OPENROUTER_TAKE_RATE = 0.10
    BLENDED_PRICE_PER_M = 0.15  # $/M tokens, conservative blended estimate

    print("\n📊 OpenRouter rankings (weekly token volume):")
    try:
        req = Request(
            'https://openrouter.ai/rankings',
            headers={'User-Agent': 'Mozilla/5.0 (compatible; AI-Token-Tracker/1.0)'},
        )
        with urlopen(req, timeout=20) as resp:
            html = resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f"  ⚠ Failed to fetch rankings page: {e}")
        return None

    # Extract all RSC push chunks — the chart data is a JSON-encoded string
    chunks_raw = re.findall(
        r'self\.__next_f\.push\(\[1,(.*?)\]\)</script>', html, re.DOTALL
    )

    # Find the provider-level time-series chart chunk.
    # The page contains multiple {x, ys} series: one aggregated by provider
    # (keys like "google", "anthropic") and several by model
    # (keys like "google/gemini-2.0-flash-001").  We search all chunks and
    # collect the series whose ys keys contain no "/" (provider-level).
    data_points = []
    for raw in chunks_raw:
        try:
            decoded = json.loads(raw)
        except Exception:
            continue
        if not isinstance(decoded, str):
            continue
        if '"x":"20' not in decoded or '"ys":{' not in decoded:
            continue
        pts = re.findall(r'\{"x":"([\d-]+)","ys":\{([^}]+)\}\}', decoded)
        provider_pts = [
            (d, ys) for d, ys in pts
            if not re.search(r'"[^"]+/[^"]+":', ys)
        ]
        if len(provider_pts) > len(data_points):
            data_points = provider_pts  # keep the longest provider-level series

    if len(data_points) < 2:
        print(f"  ⚠ Could not locate provider-level time-series data ({len(data_points)} pts)")
        return None

    # Use second-to-last = most recent complete week (last entry is partial)
    week_date, ys_raw = data_points[-2]
    providers = {}
    for m in re.finditer(r'"([^"]+)":(\d+)', ys_raw):
        providers[m.group(1)] = int(m.group(2))

    weekly_tokens_total = sum(providers.values())
    gmv_usd = weekly_tokens_total / 1e6 * BLENDED_PRICE_PER_M
    arr_estimate_usd = gmv_usd * 52 * OPENROUTER_TAKE_RATE

    top_providers = sorted(providers.items(), key=lambda x: -x[1])[:5]

    result = {
        'week_date': week_date,
        'weekly_tokens_total': weekly_tokens_total,
        'weekly_tokens_total_T': round(weekly_tokens_total / 1e12, 2),
        'weekly_gmv_usd': round(gmv_usd),
        'arr_estimate_usd': round(arr_estimate_usd),
        'blended_price_per_m_usd': BLENDED_PRICE_PER_M,
        'take_rate': OPENROUTER_TAKE_RATE,
        'top_providers': {k: v for k, v in top_providers},
        'total_providers_in_week': len(providers),
    }

    print(f"  Week: {week_date}")
    print(f"  Total tokens: {weekly_tokens_total/1e12:.2f}T")
    print(f"  Est. GMV: ${gmv_usd/1e6:.1f}M/week (@ ${BLENDED_PRICE_PER_M}/M blended)")
    print(f"  Est. ARR (10% take): ${arr_estimate_usd/1e6:.1f}M")
    print(f"  Top providers: {', '.join(f'{k} ({v/1e9:.1f}B)' for k,v in top_providers)}")
    return result


def compute_derived(pypi, npm, hf, github=None, docker=None):
    """Compute derived signals from raw data.

    self_hosted_total now incorporates four channels:
      1. PyPI vllm + ollama (Python SDK installs / CI)
      2. npm ollama (JS SDK installs)
      3. GitHub release binary downloads for Ollama, vLLM, llama.cpp
      4. Docker Hub pulls for vLLM and TGI container images
    """
    derived = {}
    github = github or {}
    docker = docker or {}

    # Combined SDK downloads (PyPI + npm)
    if pypi.get('openai') and npm.get('openai'):
        derived['openai_total'] = pypi['openai'] + npm['openai']
    if pypi.get('anthropic') and npm.get('@anthropic-ai/sdk'):
        derived['anthropic_total'] = pypi['anthropic'] + npm['@anthropic-ai/sdk']
    if pypi.get('google-generativeai') and npm.get('@google/generative-ai'):
        derived['google_total'] = pypi['google-generativeai'] + npm['@google/generative-ai']

    # Anthropic/OpenAI ratio (market share proxy)
    if derived.get('openai_total') and derived.get('anthropic_total'):
        derived['anthropic_openai_ratio'] = round(derived['anthropic_total'] / derived['openai_total'], 3)

    # Self-hosted signal — SDK layer (PyPI + npm)
    # Basis: monthly download rate. Inflated by CI/CD; best read as developer adoption velocity.
    vllm_pypi = pypi.get('vllm', 0) or 0
    ollama_py = pypi.get('ollama', 0) or 0
    ollama_npm = npm.get('ollama', 0) or 0
    derived['self_hosted_sdk'] = vllm_pypi + ollama_py + ollama_npm
    derived['self_hosted_sdk_basis'] = 'monthly_rate'

    # Self-hosted signal — binary installs (GitHub release downloads)
    # Basis: cumulative downloads across last 5 releases (NOT a monthly rate).
    # Ollama is the cleanest signal here — actual human installer downloads.
    gh_ollama = (github.get('ollama') or {}).get('total_downloads', 0) or 0
    gh_vllm = (github.get('vllm') or {}).get('total_downloads', 0) or 0
    gh_llama_cpp = (github.get('llama_cpp') or {}).get('total_downloads', 0) or 0
    gh_tgi = (github.get('tgi') or {}).get('total_downloads', 0) or 0
    derived['self_hosted_github'] = gh_ollama + gh_vllm + gh_llama_cpp + gh_tgi
    derived['self_hosted_github_basis'] = 'cumulative_last_5_releases'

    # Self-hosted signal — container deployments (Docker Hub)
    # Basis: all-time cumulative pull count (NOT a monthly rate).
    # Inflated by CI/CD re-pulls; use as enterprise deployment floor, not volume.
    # TGI tracked via GitHub releases (hosted on ghcr.io, not Docker Hub).
    docker_vllm = docker.get('vllm', 0) or 0
    derived['self_hosted_docker'] = docker_vllm
    derived['self_hosted_docker_basis'] = 'cumulative_alltime'

    # Total HF downloads as open-source adoption signal
    hf_total = sum(v for v in hf.values() if v)
    derived['hf_total_downloads'] = hf_total

    # Proxy routing signal (litellm = multi-provider routing)
    derived['litellm_downloads'] = pypi.get('litellm', 0) or 0

    print("\n📊 Derived signals:")
    for k, v in derived.items():
        print(f"  {k}: {v:,}" if isinstance(v, int) else f"  {k}: {v}")

    return derived

def main():
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"🔍 AI Signal Scraper — {today}\n{'='*50}")

    pypi = scrape_pypi()
    npm = scrape_npm()
    hf = scrape_huggingface()
    openrouter = scrape_openrouter()
    openrouter_rankings = scrape_openrouter_rankings()
    github = scrape_github()
    docker = scrape_docker_hub()
    derived = compute_derived(pypi, npm, hf, github, docker)

    result = {
        'date': today,
        'timestamp': datetime.now().isoformat(),
        'pypi': pypi,
        'npm': npm,
        'huggingface': hf,
        'openrouter': openrouter,
        'openrouter_rankings': openrouter_rankings,
        'github': github,
        'docker': docker,
        'derived': derived,
    }

    # Save dated file + latest
    dated_path = os.path.join(DATA_DIR, f'signals_{today}.json')
    latest_path = os.path.join(DATA_DIR, 'signals_latest.json')

    with open(dated_path, 'w') as f:
        json.dump(result, f, indent=2)
    with open(latest_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n✅ Saved to {dated_path}")
    print(f"✅ Updated {latest_path}")

    # Append to history
    history_path = os.path.join(DATA_DIR, 'signals_history.jsonl')
    with open(history_path, 'a') as f:
        f.write(json.dumps({'date': today, 'derived': derived}) + '\n')
    print(f"✅ Appended to {history_path}")

if __name__ == '__main__':
    main()
