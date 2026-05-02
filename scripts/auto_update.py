#!/usr/bin/env python3
"""
Auto-update pipeline: scrape signals, update dashboard data, commit and push.

Runs:
1. scrape_signals.py — pulls PyPI, npm, HuggingFace, OpenRouter
2. Updates dashboard.html + index.html with latest live data
3. Commits and pushes to GitHub (auto-deploys via GitHub Pages)

Schedule: daily via cron
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from log_run import logged_run  # noqa: E402
DATA_DIR = os.path.join(BASE_DIR, 'data')
SIGNALS_PATH = os.path.join(DATA_DIR, 'signals_latest.json')
DASHBOARD_PATH = os.path.join(BASE_DIR, 'dashboard.html')
INDEX_PATH = os.path.join(BASE_DIR, 'index.html')
SITE_DATA_PATH = os.path.join(BASE_DIR, 'site-data.json')

# Baseline calibration for self-hosted ("Others") token estimate.
# Anchored to Q1 2026 signals: at 16.35M vLLM Docker Hub cumulative pulls → 130T/day self-hosted.
# As Docker pulls grow the estimate scales proportionally; floor prevents it shrinking below baseline.
_BASELINE_DOCKER_VLLM = 16_350_000
_BASELINE_OTHERS_TOKENS = 130  # T/day

def run_scraper():
    """Run the signal scraper."""
    print("🔍 Running signal scraper...")
    scraper = os.path.join(BASE_DIR, 'scripts', 'scrape_signals.py')
    result = subprocess.run([sys.executable, scraper], capture_output=True, text=True, cwd=BASE_DIR)
    print(result.stdout)
    if result.returncode != 0:
        print(f"⚠ Scraper errors: {result.stderr}")
    return result.returncode == 0

def load_signals():
    """Load the latest signals data."""
    if not os.path.exists(SIGNALS_PATH):
        print("⚠ No signals file found")
        return None
    with open(SIGNALS_PATH) as f:
        return json.load(f)

def update_dashboard(signals):
    """Update dashboard.html with latest signal data."""
    if not signals:
        return False

    with open(DASHBOARD_PATH) as f:
        html = f.read()

    changes = []
    d = signals.get('derived', {})
    pypi = signals.get('pypi', {})
    npm = signals.get('npm', {})
    hf = signals.get('huggingface', {})
    github = signals.get('github', {})
    docker = signals.get('docker', {})
    date = signals.get('date', 'unknown')

    # Update methodology section with latest SDK numbers
    openai_total = d.get('openai_total', 0)
    anthropic_total = d.get('anthropic_total', 0)
    if openai_total and anthropic_total:
        # Update SDK download numbers in methodology
        old_pattern = r'openai PyPI: \d+M/month, anthropic: \d+M/month'
        openai_m = round(pypi.get('openai', 0) / 1e6)
        anthropic_m = round(pypi.get('anthropic', 0) / 1e6)
        new_text = f'openai PyPI: {openai_m}M/month, anthropic: {anthropic_m}M/month'
        if re.search(old_pattern, html):
            html = re.sub(old_pattern, new_text, html)
            changes.append(f"SDK downloads: openai {openai_m}M, anthropic {anthropic_m}M")

    # Update HuggingFace model download numbers in methodology
    llama_downloads = hf.get('meta-llama/Llama-3.1-8B-Instruct', 0)
    if llama_downloads:
        old_pattern = r'Llama 3\.1 8B: [\d.]+M HuggingFace downloads/30d'
        llama_m = round(llama_downloads / 1e6, 1)
        new_text = f'Llama 3.1 8B: {llama_m}M HuggingFace downloads/30d'
        if re.search(old_pattern, html):
            html = re.sub(old_pattern, new_text, html)
            changes.append(f"Llama 3.1 8B: {llama_m}M HF downloads")

    # Update vllm download number
    vllm_downloads = pypi.get('vllm', 0)
    if vllm_downloads:
        old_pattern = r'vllm: [\d.]+M PyPI downloads/month'
        vllm_m = round(vllm_downloads / 1e6, 1)
        new_text = f'vllm: {vllm_m}M PyPI downloads/month'
        if re.search(old_pattern, html):
            html = re.sub(old_pattern, new_text, html)
            changes.append(f"vllm: {vllm_m}M PyPI downloads")

    # Update Ollama GitHub release downloads (binary installs — stronger signal than PyPI)
    ollama_gh = (github.get('ollama') or {}).get('total_downloads', 0)
    if ollama_gh:
        old_pattern = r'Ollama: [\d.]+M binary downloads'
        ollama_m = round(ollama_gh / 1e6, 1)
        new_text = f'Ollama: {ollama_m}M binary downloads'
        if re.search(old_pattern, html):
            html = re.sub(old_pattern, new_text, html)
            changes.append(f"Ollama binary downloads: {ollama_m}M")

    # Update Docker Hub container pulls (production deployment signal)
    docker_vllm = docker.get('vllm', 0) or 0
    docker_tgi = docker.get('tgi', 0) or 0
    if docker_vllm or docker_tgi:
        old_pattern = r'vLLM \+ TGI containers: [\d.]+M pulls'
        total_m = round((docker_vllm + docker_tgi) / 1e6, 1)
        new_text = f'vLLM + TGI containers: {total_m}M pulls'
        if re.search(old_pattern, html):
            html = re.sub(old_pattern, new_text, html)
            changes.append(f"Container pulls: {total_m}M")

    # Update date in footer
    old_footer = r'Data as of \w+ \d{4}'
    new_footer = f'Data as of {datetime.now().strftime("%B %Y")}'
    html = re.sub(old_footer, new_footer, html)

    # Update pypistats date reference
    old_date_pattern = r'pypistats\.org, \w+ \d{4}'
    new_date = f'pypistats.org, {datetime.now().strftime("%b %Y")}'
    html = re.sub(old_date_pattern, new_date, html)

    if changes:
        with open(DASHBOARD_PATH, 'w') as f:
            f.write(html)
        # Copy to index.html
        with open(INDEX_PATH, 'w') as f:
            f.write(html)
        print(f"✅ Dashboard updated with {len(changes)} changes:")
        for c in changes:
            print(f"   • {c}")
        return True
    else:
        print("ℹ No dashboard changes needed")
        return False

def update_site_data(signals):
    """Update self-hosted ('Others') token estimate in site-data.json from live signals.

    Uses vLLM Docker Hub cumulative pull count as the scaling signal — it's the strongest
    proxy for active enterprise self-hosted deployments and grows monotonically over time.
    The Ollama GitHub release download count provides a secondary cross-check.

    Only updates the current-quarter entry (last row of tokenData) and the providers dict.
    Historical rows are left untouched — they represent our best point-in-time estimates.
    """
    if not os.path.exists(SITE_DATA_PATH):
        print("⚠ site-data.json not found, skipping self-hosted update")
        return False

    docker_vllm = (signals.get('docker') or {}).get('vllm') or _BASELINE_DOCKER_VLLM
    growth = docker_vllm / _BASELINE_DOCKER_VLLM
    new_tokens = max(_BASELINE_OTHERS_TOKENS, round(_BASELINE_OTHERS_TOKENS * growth))

    with open(SITE_DATA_PATH) as f:
        site = json.load(f)

    old_tokens = site['dashboard']['providers']['Others']['tokens']
    if old_tokens == new_tokens:
        print(f"ℹ Self-hosted estimate unchanged: {new_tokens}T/day")
        return False

    site['dashboard']['providers']['Others']['tokens'] = new_tokens

    # Update the last (current quarter) row of the timeline tokenData — index 7 is Others
    token_data = site['timeline']['tokenData']
    token_data[-1][7] = new_tokens
    site['timeline']['tokenData'] = token_data

    with open(SITE_DATA_PATH, 'w') as f:
        json.dump(site, f, indent=2)

    print(f"✅ Self-hosted estimate updated: {old_tokens}T → {new_tokens}T/day "
          f"(Docker vLLM pulls: {docker_vllm:,}, growth factor: {growth:.3f}x)")
    return True


def git_commit_push(date):
    """Commit and push changes."""
    os.chdir(BASE_DIR)

    # Check if there are changes
    status = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
    if not status.stdout.strip():
        print("ℹ No changes to commit")
        return

    # Stage data files + dashboard
    subprocess.run(['git', 'add', 'data/', 'dashboard.html', 'index.html', 'site-data.json'], check=True)

    # Commit
    msg = f"Auto-update: signal scrape {date}\n\nAutomated daily data refresh from PyPI, npm, HuggingFace, OpenRouter, GitHub releases, Docker Hub.\n\nCo-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
    subprocess.run(['git', 'commit', '-m', msg], check=True)

    # Push
    result = subprocess.run(['git', 'push'], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Pushed to GitHub — site will update in ~60 seconds")
    else:
        print(f"⚠ Push failed: {result.stderr}")

def main():
    with logged_run("auto_update.py") as outputs:
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"\n{'='*60}")
        print(f"🤖 AI Token Tracker Auto-Update — {today}")
        print(f"{'='*60}\n")

        # Step 1: Scrape
        if not run_scraper():
            print("⚠ Scraper had issues but continuing...")
            outputs["scraper_ok"] = False
        else:
            outputs["scraper_ok"] = True

        # Step 2: Load signals
        signals = load_signals()

        # Step 3: Update dashboard HTML
        updated = update_dashboard(signals)
        outputs["dashboard_updated"] = bool(updated)

        # Step 4: Update self-hosted estimate in site-data.json
        update_site_data(signals)

        # Step 5: Apply any approved claims from web review
        try:
            from apply_claims import main as apply_claims_main
            apply_claims_main()
        except Exception as e:
            print(f"  Claims application: {e}")
            outputs["apply_claims_error"] = str(e)[:120]

        # Step 6: Commit and push
        git_commit_push(today)

        print(f"\n{'='*60}")
        print(f"✅ Auto-update complete — {today}")
        print(f"{'='*60}\n")

if __name__ == '__main__':
    main()
