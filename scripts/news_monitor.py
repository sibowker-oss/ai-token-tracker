#!/usr/bin/env python3
"""
News monitor: checks RSS feeds and flags when dashboard assumptions may be outdated.

Monitors for:
- Provider earnings (OpenAI, Anthropic, Google, Microsoft, Salesforce, ServiceNow)
- Funding rounds (AI startups)
- Pricing changes (model price cuts/increases)
- Major launches (new models, products)

Output: data/news_alerts.json — items that may require dashboard updates
"""

import json
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from urllib.request import urlopen, Request
from urllib.error import URLError

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
ALERTS_PATH = os.path.join(DATA_DIR, 'news_alerts.json')

import sys  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from log_run import logged_run  # noqa: E402

# Keywords that suggest dashboard numbers need updating
TRIGGER_KEYWORDS = [
    # Revenue / earnings
    'openai revenue', 'openai arr', 'anthropic revenue', 'anthropic arr',
    'google cloud ai revenue', 'azure openai revenue',
    # Enterprise SaaS AI
    'agentforce revenue', 'agentforce arr', 'now assist',
    'm365 copilot seats', 'copilot adoption', 'github copilot subscribers',
    # Pricing
    'token pricing', 'price cut', 'price reduction', 'new pricing',
    'gpt-5 pricing', 'claude pricing', 'gemini pricing',
    # Funding
    'series a', 'series b', 'series c', 'valuation', 'raises',
    # Models
    'gpt-5', 'gpt-6', 'claude 4', 'claude 5', 'gemini 3', 'llama 5',
    'deepseek', 'new model launch',
    # Market data
    'token consumption', 'ai spending', 'ai market size',
    'gpu shipments', 'nvidia earnings', 'ai capex',
]

# RSS feeds to monitor
RSS_FEEDS = [
    ('https://techcrunch.com/category/artificial-intelligence/feed/', 'TechCrunch AI'),
    ('https://www.theinformation.com/feed', 'The Information'),
    ('https://aibusiness.com/rss.xml', 'AI Business'),
    ('https://www.cnbc.com/id/19854910/device/rss/rss.html', 'CNBC Tech'),
    ('https://feeds.feedburner.com/venturebeat/SZYF', 'VentureBeat'),
]

def fetch_rss(url, source_name, days_back=7):
    """Fetch and parse an RSS feed."""
    items = []
    try:
        req = Request(url, headers={'User-Agent': 'AI-Token-Tracker/1.0'})
        with urlopen(req, timeout=15) as resp:
            content = resp.read().decode('utf-8', errors='replace')

        root = ET.fromstring(content)
        cutoff = datetime.now() - timedelta(days=days_back)

        # Handle both RSS 2.0 and Atom
        for item in root.iter('item'):
            title = item.findtext('title', '')
            link = item.findtext('link', '')
            desc = item.findtext('description', '')
            pub_date = item.findtext('pubDate', '')

            items.append({
                'title': title,
                'link': link,
                'description': desc[:300],
                'source': source_name,
                'pub_date': pub_date,
            })

    except Exception as e:
        print(f"  ⚠ Failed to fetch {source_name}: {e}")

    return items

def check_triggers(items):
    """Check items against trigger keywords."""
    alerts = []
    for item in items:
        text = (item['title'] + ' ' + item['description']).lower()
        matched = [kw for kw in TRIGGER_KEYWORDS if kw in text]
        if matched:
            alerts.append({
                **item,
                'matched_keywords': matched,
                'priority': 'high' if len(matched) >= 2 else 'medium',
            })
    return alerts

def main():
    with logged_run("news_monitor.py") as outputs:
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"📰 News Monitor — {today}\n{'='*50}")

        all_items = []
        for url, name in RSS_FEEDS:
            print(f"  Checking {name}...")
            items = fetch_rss(url, name)
            all_items.extend(items)
            print(f"    Found {len(items)} items")

        print(f"\n📊 Total items: {len(all_items)}")

        # Check for triggers
        alerts = check_triggers(all_items)
        alerts.sort(key=lambda a: len(a['matched_keywords']), reverse=True)

        print(f"🚨 Alerts (items matching dashboard keywords): {len(alerts)}")
        for a in alerts[:10]:
            priority_icon = '🔴' if a['priority'] == 'high' else '🟡'
            print(f"  {priority_icon} [{a['source']}] {a['title'][:80]}")
            print(f"     Keywords: {', '.join(a['matched_keywords'])}")

        # Save
        result = {
            'date': today,
            'total_items_scanned': len(all_items),
            'alerts': alerts[:30],  # Top 30
        }

        os.makedirs(DATA_DIR, exist_ok=True)
        with open(ALERTS_PATH, 'w') as f:
            json.dump(result, f, indent=2)

        print(f"\n✅ Saved {len(alerts)} alerts to {ALERTS_PATH}")

        high = [a for a in alerts if a['priority'] == 'high']
        if high:
            print(f"\n⚠️  {len(high)} HIGH PRIORITY alerts — dashboard may need manual update!")
            for h in high[:5]:
                print(f"   → {h['title'][:100]}")

        outputs["items_scanned"] = len(all_items)
        outputs["alerts_total"] = len(alerts)
        outputs["alerts_high_priority"] = len(high)
        outputs["feeds_checked"] = len(RSS_FEEDS)

if __name__ == '__main__':
    main()
