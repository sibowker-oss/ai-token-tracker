#!/usr/bin/env python3
"""
Add a company to topConsumers in site-data.json.

Three modes:
  1. Interactive: python3 scripts/add_company.py
  2. Quick:       python3 scripts/add_company.py --name "Acme AI" --url "https://acme.ai"
  3. From URL:    python3 scripts/add_company.py --from-url "https://acme.ai"
                  (fetches the page and uses Claude to extract company data)

The script auto-fills what it can (category, providers, founded year)
and uses Claude API to research the company if --from-url is used.
"""

import json
import os
import re
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_DATA = os.path.join(BASE_DIR, 'site-data.json')

COGS_RATIOS = {
    'ai-application': 0.30, 'ai-infrastructure': 0.65, 'vertical-ai': 0.25,
    'digital-native': 0.12, 'enterprise-saas': 0.05,
}
BLENDED_PRICE = 2.5  # $/M tokens


def estimate_tokens(arr_numeric, category):
    """Estimate daily tokens from ARR using COGS method."""
    if not arr_numeric:
        return None
    cogs = COGS_RATIOS.get(category, 0.25)
    daily_rev = arr_numeric / 365
    daily_tokens = int(daily_rev * cogs / BLENDED_PRICE * 1e6)
    return daily_tokens


def format_tokens(n):
    if not n:
        return 'Unknown'
    if n >= 1e12:
        return f'~{n/1e12:.1f}T/day'
    return f'~{n/1e9:.0f}B/day'


def format_money(n):
    if not n:
        return None
    if n >= 1e9:
        return f'${n/1e9:.1f}B'
    return f'${n/1e6:.0f}M'


def research_company(url):
    """Use Claude to research a company from its website."""
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("  No ANTHROPIC_API_KEY — skipping auto-research")
        return {}

    from urllib.request import urlopen, Request
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='replace')
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text)[:15000]
    except Exception as e:
        print(f"  Could not fetch {url}: {e}")
        return {}

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model='claude-sonnet-4-6',
            max_tokens=1024,
            messages=[{'role': 'user', 'content': f"""From this company's website text, extract:
- company_name: official name
- hq: headquarters country/city
- type: what they do (e.g. "AI Dev Tool", "Legal AI", "Voice AI")
- category: one of: ai-application, ai-infrastructure, vertical-ai, digital-native, enterprise-saas
- subcategory: freeform (e.g. coding, search, legal, voice, content)
- providers: which AI providers they use (e.g. ["openai", "anthropic"]) — infer from product description
- founded: year founded (number or null)
- arr: estimated ARR if mentioned, or null
- arr_numeric: ARR as number in USD, or null
- valuation: last known valuation string, or null
- funding: total funding string, or null
- description: one-sentence summary of what they do

Return ONLY a JSON object. No explanation.

Website text:
{text}"""}]
        )
        raw = response.content[0].text.strip()
        raw = re.sub(r'^```(?:json)?\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        return json.loads(raw)
    except Exception as e:
        print(f"  Claude research error: {e}")
        return {}


def add_company(data):
    """Add company to site-data.json topConsumers."""
    with open(SITE_DATA) as f:
        site = json.load(f)

    consumers = site['dashboard']['topConsumers']

    # Check for duplicates
    name_lower = data['co'].lower()
    for c in consumers:
        if c['co'].lower() == name_lower:
            print(f"  Already exists: {c['co']}")
            return False

    # Estimate tokens if ARR is known
    tokens_numeric = data.get('tokensNumeric')
    if not tokens_numeric and data.get('arrNumeric'):
        tokens_numeric = estimate_tokens(data['arrNumeric'], data.get('category', 'ai-application'))
        data['tokensNumeric'] = tokens_numeric
        data['tokens'] = format_tokens(tokens_numeric)

    # Set defaults
    data.setdefault('conf', 'Low')
    data.setdefault('lastUpdated', datetime.now().strftime('%Y-%m-%d'))
    data.setdefault('status', 'private')
    data.setdefault('employeeCount', None)

    consumers.append(data)
    # Re-sort by tokens descending
    consumers.sort(key=lambda c: c.get('tokensNumeric') or 0, reverse=True)

    with open(SITE_DATA, 'w') as f:
        json.dump(site, f, indent=2)

    print(f"  ✅ Added {data['co']} ({data.get('tokens', '?')}) — total: {len(consumers)} companies")
    return True


def interactive_add():
    """Interactive CLI for adding a company."""
    print("\n🏢 Add Company to Top Token Consumers\n")

    name = input("  Company name: ").strip()
    if not name:
        return

    url = input("  Website URL (or blank): ").strip()

    # Try auto-research if URL provided
    research = {}
    if url:
        print("  Researching...")
        research = research_company(url)
        if research:
            print(f"  Found: {research.get('company_name', '?')} — {research.get('description', '?')}")

    hq = input(f"  HQ [{research.get('hq', 'US')}]: ").strip() or research.get('hq', 'US')
    type_str = input(f"  Type [{research.get('type', 'AI Application')}]: ").strip() or research.get('type', 'AI Application')
    category = input(f"  Category [{research.get('category', 'ai-application')}]: ").strip() or research.get('category', 'ai-application')

    providers_str = input(f"  Providers (comma-sep) [{','.join(research.get('providers', ['openai']))}]: ").strip()
    providers = [p.strip().lower() for p in (providers_str or ','.join(research.get('providers', ['openai']))).split(',')]

    founded = input(f"  Founded year [{research.get('founded', '')}]: ").strip()
    founded = int(founded) if founded else research.get('founded')

    arr_str = input(f"  ARR (e.g. 50000000) [{research.get('arr_numeric', '')}]: ").strip()
    arr_numeric = int(float(arr_str)) if arr_str else research.get('arr_numeric')

    evidence = input("  Evidence / source: ").strip()

    data = {
        'co': name,
        'hq': hq,
        'type': type_str,
        'tokens': 'Unknown',
        'prov': ', '.join(p.title() for p in providers),
        'ev': evidence or research.get('description', ''),
        'conf': 'Low',
        'founded': founded,
        'category': category,
        'subcategory': research.get('subcategory', ''),
        'providers': providers,
        'tokensNumeric': None,
        'arr': format_money(arr_numeric) if arr_numeric else research.get('arr'),
        'arrNumeric': arr_numeric,
        'valuation': research.get('valuation'),
        'valuationNumeric': None,
        'totalFunding': research.get('funding'),
        'status': 'private',
        'website': url,
        'employeeCount': None,
        'lastUpdated': datetime.now().strftime('%Y-%m-%d'),
    }

    add_company(data)


def quick_add(name, url, arr=None, category='ai-application'):
    """Quick CLI add with minimal inputs."""
    research = research_company(url) if url else {}

    data = {
        'co': name,
        'hq': research.get('hq', 'US'),
        'type': research.get('type', 'AI Application'),
        'tokens': 'Unknown',
        'prov': ', '.join(p.title() for p in research.get('providers', ['openai'])),
        'ev': research.get('description', ''),
        'conf': 'Low',
        'founded': research.get('founded'),
        'category': research.get('category', category),
        'subcategory': research.get('subcategory', ''),
        'providers': research.get('providers', ['openai']),
        'tokensNumeric': None,
        'arr': format_money(arr) if arr else research.get('arr'),
        'arrNumeric': arr or research.get('arr_numeric'),
        'valuation': research.get('valuation'),
        'valuationNumeric': None,
        'totalFunding': research.get('funding'),
        'status': 'private',
        'website': url,
        'employeeCount': None,
        'lastUpdated': datetime.now().strftime('%Y-%m-%d'),
    }

    add_company(data)


def main():
    if '--from-url' in sys.argv:
        url = sys.argv[sys.argv.index('--from-url') + 1]
        print(f"\n🔍 Researching {url}...")
        research = research_company(url)
        name = research.get('company_name', url.split('//')[1].split('/')[0].replace('www.', ''))
        quick_add(name, url, category=research.get('category', 'ai-application'))
    elif '--name' in sys.argv:
        idx = sys.argv.index('--name')
        name = sys.argv[idx + 1]
        url = sys.argv[sys.argv.index('--url') + 1] if '--url' in sys.argv else ''
        arr = int(sys.argv[sys.argv.index('--arr') + 1]) if '--arr' in sys.argv else None
        quick_add(name, url, arr)
    else:
        interactive_add()


if __name__ == '__main__':
    main()
