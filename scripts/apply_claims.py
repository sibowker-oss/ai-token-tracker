#!/usr/bin/env python3
"""
Apply approved claims to site-data.json.

Reads data-updates/approved-claims.json (written by claims.html Submit),
applies changes to site-data.json, moves processed claims to vault-data.json,
and archives the approved file.

Run: python3 scripts/apply_claims.py
Called by: auto_update.py (daily 7am)

Safety rules:
  - Only applies claims with review_decision='accepted'
  - Claims flagged 'major_change' (>15% diff) must have confirm=true
  - Updates provider ARR, topConsumer ARR/tokens, and vault data points
  - Logs every change for audit trail
"""

import json
import os
import shutil
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_DATA = os.path.join(BASE_DIR, 'site-data.json')
VAULT_DATA = os.path.join(BASE_DIR, 'vault-data.json')
APPROVED_FILE = os.path.join(BASE_DIR, 'data-updates', 'approved-claims.json')
ARCHIVE_DIR = os.path.join(BASE_DIR, 'data-updates', 'archive')
LOG_FILE = os.path.join(BASE_DIR, 'data', 'apply_claims.log')

# COGS ratios for token recalculation
COGS_RATIOS = {
    'ai-application': 0.30, 'ai-infrastructure': 0.65, 'vertical-ai': 0.25,
    'digital-native': 0.12, 'enterprise-saas': 0.05, 'foundation-model': 0.50,
}
BLENDED_TOKEN_PRICE = 2.5  # $/M tokens


def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')


def apply_provider_arr(site, claim):
    """Update a provider's ARR in dashboard.providers."""
    entity = claim.get('entity', '')
    value = claim.get('value')
    if not entity or not value:
        return False

    providers = site['dashboard']['providers']
    # Match provider by name
    matched = None
    for name in providers:
        if entity.lower() in name.lower() or name.lower() in entity.lower():
            matched = name
            break

    if not matched:
        return False

    old_val = providers[matched].get('rev', 0)
    new_val = value / 1e9  # Convert to $B

    if old_val == new_val:
        log(f"  SKIP {matched} ARR: already ${new_val}B")
        return False

    providers[matched]['rev'] = new_val
    log(f"  UPDATE {matched} ARR: ${old_val}B → ${new_val}B")

    # Also update timeline last quarter
    timeline = site['timeline']
    prov_names = timeline['providerNames']
    if matched in prov_names:
        idx = prov_names.index(matched)
        last_q = len(timeline['revData']) - 1
        timeline['revData'][last_q][idx] = new_val
        log(f"  UPDATE timeline {matched} Q{last_q}: ${new_val}B")

    return True


def apply_consumer_arr(site, claim):
    """Update a topConsumer's ARR and recalculate tokens."""
    entity = claim.get('entity', '')
    value = claim.get('value')
    if not entity or not value:
        return False

    consumers = site['dashboard']['topConsumers']
    matched = None
    for c in consumers:
        if entity.lower() in c['co'].lower() or c['co'].lower() in entity.lower():
            matched = c
            break

    if not matched:
        return False

    old_arr = matched.get('arrNumeric', 0)
    new_arr = value
    matched['arrNumeric'] = new_arr

    # Human-readable ARR
    if new_arr >= 1e9:
        matched['arr'] = f"${new_arr/1e9:.1f}B"
    else:
        matched['arr'] = f"${new_arr/1e6:.0f}M"

    log(f"  UPDATE {matched['co']} ARR: ${old_arr/1e6:.0f}M → ${new_arr/1e6:.0f}M")

    # Recalculate tokens using COGS method
    category = matched.get('category', 'ai-application')
    cogs_ratio = COGS_RATIOS.get(category, 0.25)
    daily_rev = new_arr / 365
    daily_api_spend = daily_rev * cogs_ratio
    new_tokens = int(daily_api_spend / BLENDED_TOKEN_PRICE * 1e6)

    old_tokens = matched.get('tokensNumeric', 0)
    if new_tokens > 0 and old_tokens > 0:
        change_pct = abs(new_tokens - old_tokens) / old_tokens * 100
        if change_pct > 20:
            matched['tokensNumeric'] = new_tokens
            if new_tokens >= 1e12:
                matched['tokens'] = f"~{new_tokens/1e12:.1f}T/day"
            else:
                matched['tokens'] = f"~{new_tokens/1e9:.0f}B/day"
            log(f"  RECALC {matched['co']} tokens: {old_tokens/1e9:.0f}B → {new_tokens/1e9:.0f}B/day (COGS {cogs_ratio:.0%})")

    matched['lastUpdated'] = datetime.now().strftime('%Y-%m-%d')
    return True


def add_to_vault(vault, claim):
    """Add accepted claim as a vault data point."""
    dp_id = f"dp-{len(vault['dataPoints']) + 1:03d}"
    vault['dataPoints'].append({
        'id': dp_id,
        'claim': claim.get('claim', ''),
        'value': claim.get('value'),
        'unit': claim.get('unit', 'USD'),
        'sourceUrl': claim.get('source_url', ''),
        'sourceType': 'reporting',
        'sourceAuthor': f"{claim.get('source_podcast', '')} ({claim.get('speaker', '')})",
        'confidence': claim.get('confidence', 'estimated'),
        'dateOfClaim': claim.get('source_date', ''),
        'dateAdded': datetime.now().strftime('%Y-%m-%d'),
        'usedOn': ['dashboard'],
        'notes': f"Auto-applied from claims review. Weight: {claim.get('weight', '?')}. Dedup: {claim.get('dedup_status', '?')}.",
        'tags': [claim.get('entity', '').lower(), claim.get('category', '')],
        'metricKey': f"{claim.get('entity', '').lower().replace(' ', '-')}-{claim.get('metric', '').lower().replace(' ', '-')}",
        'status': 'accepted',
    })
    return dp_id


def main():
    # Check both data-updates/ and ~/Downloads/ for approved file
    downloads_file = os.path.expanduser('~/Downloads/approved-claims.json')
    if os.path.exists(downloads_file) and not os.path.exists(APPROVED_FILE):
        import shutil as _sh
        os.makedirs(os.path.dirname(APPROVED_FILE), exist_ok=True)
        _sh.move(downloads_file, APPROVED_FILE)
        print(f"  Moved approved-claims.json from Downloads to data-updates/")

    if not os.path.exists(APPROVED_FILE):
        return  # Nothing to apply — normal state

    log("=" * 50)
    log("APPLY CLAIMS — processing approved-claims.json")

    with open(APPROVED_FILE) as f:
        approved = json.load(f)

    if not approved:
        log("  No claims to apply")
        os.remove(APPROVED_FILE)
        return

    with open(SITE_DATA) as f:
        site = json.load(f)
    with open(VAULT_DATA) as f:
        vault = json.load(f)

    applied = 0
    skipped = 0

    for claim in approved:
        decision = claim.get('review_decision', '')
        if decision != 'accepted':
            skipped += 1
            continue

        # Safety gate: major changes need explicit confirm
        if claim.get('major_change') and not claim.get('confirmed'):
            log(f"  BLOCKED {claim.get('entity', '?')}: major change not confirmed")
            skipped += 1
            continue

        metric = (claim.get('metric') or '').lower()
        entity = claim.get('entity', '')

        changed = False
        if 'arr' in metric or 'revenue' in metric:
            # Try provider-level first
            if apply_provider_arr(site, claim):
                changed = True
            # Then consumer-level
            if apply_consumer_arr(site, claim):
                changed = True

        if changed:
            add_to_vault(vault, claim)
            applied += 1
        else:
            # Still add to vault as reference even if no dashboard field to update
            add_to_vault(vault, claim)
            applied += 1
            log(f"  VAULT-ONLY {entity}: {claim.get('claim', '')[:60]}")

    # Update timestamps
    site['meta']['generatedAt'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    site['meta']['acceptedPoints'] = len(vault['dataPoints'])
    vault['meta']['lastUpdated'] = datetime.now().strftime('%Y-%m-%d')

    # Save
    with open(SITE_DATA, 'w') as f:
        json.dump(site, f, indent=2)
    with open(VAULT_DATA, 'w') as f:
        json.dump(vault, f, indent=2)

    # Archive the approved file
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    archive_name = f"approved-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}.json"
    shutil.move(APPROVED_FILE, os.path.join(ARCHIVE_DIR, archive_name))

    log(f"DONE: {applied} applied, {skipped} skipped, archived as {archive_name}")


if __name__ == '__main__':
    main()
