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
DATA_DIR = os.path.join(BASE_DIR, 'data')
SIGNALS_PATH = os.path.join(DATA_DIR, 'signals_latest.json')
DASHBOARD_PATH = os.path.join(BASE_DIR, 'dashboard.html')
INDEX_PATH = os.path.join(BASE_DIR, 'index.html')

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

def git_commit_push(date):
    """Commit and push changes."""
    os.chdir(BASE_DIR)

    # Check if there are changes
    status = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
    if not status.stdout.strip():
        print("ℹ No changes to commit")
        return

    # Stage data files + dashboard
    subprocess.run(['git', 'add', 'data/', 'dashboard.html', 'index.html'], check=True)

    # Commit
    msg = f"Auto-update: signal scrape {date}\n\nAutomated daily data refresh from PyPI, npm, HuggingFace, OpenRouter.\n\nCo-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
    subprocess.run(['git', 'commit', '-m', msg], check=True)

    # Push
    result = subprocess.run(['git', 'push'], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Pushed to GitHub — site will update in ~60 seconds")
    else:
        print(f"⚠ Push failed: {result.stderr}")

def main():
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"\n{'='*60}")
    print(f"🤖 AI Token Tracker Auto-Update — {today}")
    print(f"{'='*60}\n")

    # Step 1: Scrape
    if not run_scraper():
        print("⚠ Scraper had issues but continuing...")

    # Step 2: Load signals
    signals = load_signals()

    # Step 3: Update dashboard
    updated = update_dashboard(signals)

    # Step 4: Commit and push
    git_commit_push(today)

    print(f"\n{'='*60}")
    print(f"✅ Auto-update complete — {today}")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()
