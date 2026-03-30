#!/usr/bin/env python3
"""
Reconcile signals against topConsumers — detect stale ARR/token estimates.

Scans:
  1. vault-data.json — accepted claims with ARR/revenue data
  2. data-updates/*-candidates.json — pending claim candidates
  3. data/signals_latest.json — OpenRouter app rankings (measured tokens)

Matches entities to topConsumers entries, recalculates implied token
volumes using COGS triangulation, and flags conflicts.

Output: data-updates/reconciliation-{date}.json + console summary

Run: python3 scripts/reconcile.py
"""

import json
import os
import re
import glob
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_DATA = os.path.join(BASE_DIR, 'site-data.json')
VAULT_DATA = os.path.join(BASE_DIR, 'vault-data.json')
SIGNALS = os.path.join(BASE_DIR, 'data', 'signals_latest.json')
CANDIDATES_DIR = os.path.join(BASE_DIR, 'data-updates')
OUTPUT_DIR = os.path.join(BASE_DIR, 'data-updates')

# COGS assumptions by category
COGS_RATIOS = {
    'ai-application': {'low': 0.20, 'mid': 0.30, 'high': 0.40},
    'ai-infrastructure': {'low': 0.50, 'mid': 0.65, 'high': 0.80},
    'vertical-ai': {'low': 0.15, 'mid': 0.25, 'high': 0.35},
    'digital-native': {'low': 0.05, 'mid': 0.12, 'high': 0.20},
    'enterprise-saas': {'low': 0.02, 'mid': 0.05, 'high': 0.10},
    'foundation-model': {'low': 0.30, 'mid': 0.50, 'high': 0.70},
}
DEFAULT_COGS = {'low': 0.15, 'mid': 0.25, 'high': 0.35}

# Blended token price assumptions ($/M tokens)
BLENDED_PRICE = {'cheap': 1.0, 'mid': 2.5, 'expensive': 5.0}


def normalize_name(name):
    """Normalize company name for fuzzy matching."""
    name = name.lower().strip()
    # Remove common suffixes/prefixes
    for remove in [' ai', ' inc', ' labs', ' technologies', ' (anysphere)',
                   'the ', '.ai', '.com', ' corp']:
        name = name.replace(remove, '')
    return name.strip()


def load_consumers():
    """Load topConsumers from site-data.json."""
    with open(SITE_DATA) as f:
        s = json.load(f)
    consumers = {}
    for c in s['dashboard']['topConsumers']:
        key = normalize_name(c['co'])
        consumers[key] = c
        # Also index by exact name
        consumers[c['co'].lower()] = c
    return consumers


def load_arr_signals():
    """Collect all ARR/revenue signals from vault + candidates."""
    signals = []

    # From vault-data.json
    if os.path.exists(VAULT_DATA):
        with open(VAULT_DATA) as f:
            vault = json.load(f)
        for dp in vault.get('dataPoints', []):
            if dp.get('status') != 'accepted':
                continue
            metric = (dp.get('metricKey') or '').lower()
            claim = (dp.get('claim') or '').lower()
            if 'arr' in metric or 'revenue' in metric or 'arr' in claim:
                signals.append({
                    'entity': dp.get('claim', '').split('$')[0].strip().rstrip(' —-–'),
                    'value': dp.get('value'),
                    'unit': dp.get('unit', ''),
                    'metric': dp.get('metricKey', ''),
                    'date': dp.get('dateOfClaim', ''),
                    'source': 'vault',
                    'source_detail': dp.get('sourceAuthor', ''),
                    'confidence': dp.get('confidence', ''),
                })

    # From candidate files
    for fpath in sorted(glob.glob(os.path.join(CANDIDATES_DIR, '*-candidates.json'))):
        try:
            with open(fpath) as f:
                candidates = json.load(f)
            for c in candidates:
                if c.get('category') in ('provider_revenue', 'valuation_funding'):
                    if c.get('metric') and 'arr' in c.get('metric', '').lower():
                        signals.append({
                            'entity': c.get('entity', ''),
                            'value': c.get('value'),
                            'unit': c.get('unit', 'USD'),
                            'metric': c.get('metric', ''),
                            'date': c.get('source_date', ''),
                            'source': 'podcast',
                            'source_detail': f"{c.get('source_podcast', '')} ({c.get('speaker', '')})",
                            'confidence': c.get('confidence', ''),
                            'weight': c.get('weight', 'indicative'),
                        })
        except (json.JSONDecodeError, KeyError):
            continue

    return signals


def load_openrouter_app_signals():
    """Load per-app token volumes from OpenRouter rankings."""
    if not os.path.exists(SIGNALS):
        return {}
    with open(SIGNALS) as f:
        sig = json.load(f)

    # The openrouter_rankings has weekly provider-level data
    # Per-app data would come from the rankMap — but we don't scrape that yet
    # For now, return the weekly total as a reference point
    or_data = sig.get('openrouter_rankings', {})
    return {
        'weekly_total': or_data.get('weekly_tokens_total', 0),
        'week_date': or_data.get('week_date', ''),
    }


def calculate_implied_tokens(arr_numeric, category):
    """Calculate implied daily tokens from ARR using COGS triangulation."""
    if not arr_numeric or arr_numeric <= 0:
        return None

    cogs = COGS_RATIOS.get(category, DEFAULT_COGS)
    daily_rev = arr_numeric / 365

    results = {}
    for scenario, cogs_ratio in cogs.items():
        daily_api_spend = daily_rev * cogs_ratio
        # Use mid-range token price
        daily_tokens = daily_api_spend / BLENDED_PRICE['mid'] * 1e6
        results[scenario] = int(daily_tokens)

    return results


def match_signal_to_consumer(signal, consumers):
    """Try to match a signal entity to a topConsumers entry."""
    entity = signal.get('entity', '')
    if not entity:
        return None

    # Try exact match
    key = entity.lower()
    if key in consumers:
        return consumers[key]

    # Try normalized match
    norm = normalize_name(entity)
    if norm in consumers:
        return consumers[norm]

    # Try substring match
    for ckey, consumer in consumers.items():
        if norm in ckey or ckey in norm:
            return consumer

    return None


def reconcile():
    """Main reconciliation logic."""
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"🔄 Reconciliation — {today}\n{'='*60}")

    consumers = load_consumers()
    arr_signals = load_arr_signals()
    or_signals = load_openrouter_app_signals()

    print(f"  Consumers loaded: {len(set(id(v) for v in consumers.values()))}")
    print(f"  ARR signals found: {len(arr_signals)}")
    print(f"  OpenRouter data: {or_signals.get('week_date', 'N/A')}")

    updates = []
    unmatched = []

    # Match ARR signals to consumers
    for signal in arr_signals:
        consumer = match_signal_to_consumer(signal, consumers)
        if not consumer:
            unmatched.append(signal)
            continue

        signal_arr = signal.get('value')
        if not signal_arr or not isinstance(signal_arr, (int, float)):
            continue

        current_arr = consumer.get('arrNumeric')
        current_tokens = consumer.get('tokensNumeric', 0)
        category = consumer.get('category', 'ai-application')

        # Calculate implied tokens from signal ARR
        implied = calculate_implied_tokens(signal_arr, category)
        if not implied:
            continue

        # Check for conflict
        arr_changed = current_arr and abs(signal_arr - current_arr) / max(current_arr, 1) > 0.15
        token_stale = current_tokens and implied['mid'] and abs(implied['mid'] - current_tokens) / max(current_tokens, 1) > 0.20

        if arr_changed or token_stale or not current_arr:
            update = {
                'company': consumer['co'],
                'current_arr': current_arr,
                'signal_arr': signal_arr,
                'arr_change_pct': round((signal_arr - (current_arr or 0)) / max(current_arr or 1, 1) * 100, 1),
                'current_tokens': current_tokens,
                'implied_tokens_low': implied['low'],
                'implied_tokens_mid': implied['mid'],
                'implied_tokens_high': implied['high'],
                'token_change_pct': round((implied['mid'] - (current_tokens or 0)) / max(current_tokens or 1, 1) * 100, 1) if current_tokens else None,
                'signal_source': signal.get('source', ''),
                'signal_detail': signal.get('source_detail', ''),
                'signal_date': signal.get('date', ''),
                'signal_confidence': signal.get('confidence', ''),
                'signal_weight': signal.get('weight', ''),
                'category': category,
                'action': 'update_arr' if arr_changed else ('new_arr' if not current_arr else 'token_recalc'),
            }
            updates.append(update)

    # COGS sanity check on ALL consumers (even without new signals)
    seen_companies = {u['company'] for u in updates}
    seen_ids = set()
    for consumer in consumers.values():
        if id(consumer) in seen_ids:
            continue
        seen_ids.add(id(consumer))
        if consumer['co'] in seen_companies:
            continue
        arr = consumer.get('arrNumeric')
        tokens = consumer.get('tokensNumeric')
        if not arr or not tokens:
            continue

        category = consumer.get('category', 'ai-application')
        implied = calculate_implied_tokens(arr, category)
        if not implied:
            continue

        ratio = tokens / max(implied['mid'], 1) if implied['mid'] else 0
        if ratio < 0.3 or ratio > 3.0:
            updates.append({
                'company': consumer['co'],
                'current_arr': arr,
                'signal_arr': arr,
                'arr_change_pct': 0,
                'current_tokens': tokens,
                'implied_tokens_low': implied['low'],
                'implied_tokens_mid': implied['mid'],
                'implied_tokens_high': implied['high'],
                'token_change_pct': round((implied['mid'] - tokens) / max(tokens, 1) * 100, 1),
                'signal_source': 'cogs_check',
                'signal_detail': f'Current tokens vs implied: ratio={ratio:.1f}x (expected 0.3-3.0x)',
                'signal_date': today,
                'signal_confidence': '',
                'signal_weight': '',
                'category': category,
                'action': 'token_mismatch',
            })

    # Sort: biggest changes first
    updates.sort(key=lambda u: abs(u.get('token_change_pct') or 0), reverse=True)

    # Output
    output = {
        'date': today,
        'total_consumers': len(set(id(v) for v in consumers.values())),
        'signals_processed': len(arr_signals),
        'updates_flagged': len(updates),
        'unmatched_signals': len(unmatched),
        'updates': updates,
        'unmatched': [{'entity': s['entity'], 'value': s['value'], 'source': s['source']} for s in unmatched],
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, f'reconciliation-{today}.json')
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    # Console summary
    print(f"\n{'='*60}")
    print(f"  Updates flagged: {len(updates)}")
    print(f"  Unmatched signals: {len(unmatched)}")

    if updates:
        print(f"\n📋 FLAGGED UPDATES:")
        for u in updates:
            icon = '🆕' if u['action'] == 'new_arr' else '⚠️' if u['action'] == 'update_arr' else '🔄' if u['action'] == 'token_recalc' else '❓'
            arr_str = f"${u['current_arr']/1e6:.0f}M → ${u['signal_arr']/1e6:.0f}M" if u['current_arr'] else f"NEW ${u['signal_arr']/1e6:.0f}M"
            tok_str = f"{(u['current_tokens'] or 0)/1e9:.0f}B → {u['implied_tokens_mid']/1e9:.0f}B ({u['token_change_pct']:+.0f}%)" if u['token_change_pct'] is not None else 'N/A'
            print(f"  {icon} {u['company']:25s} | ARR: {arr_str:25s} | Tokens: {tok_str}")
            print(f"     Source: {u['signal_source']} — {u['signal_detail']}")

    if unmatched:
        print(f"\n❓ UNMATCHED SIGNALS (no matching consumer):")
        for s in unmatched[:10]:
            print(f"  - {s['entity']}: ${s['value']}")

    print(f"\n✅ Saved to {output_path}")
    return output


if __name__ == '__main__':
    reconcile()
