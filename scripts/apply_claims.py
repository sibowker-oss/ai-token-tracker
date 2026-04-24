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
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coerce_date import coerce_or_keep  # noqa: E402
SITE_DATA = os.path.join(BASE_DIR, 'site-data.json')
VAULT_DATA = os.path.join(BASE_DIR, 'vault-data.json')
COMPANIES_FILE = os.path.join(BASE_DIR, 'companies.json')
APPROVED_FILE = os.path.join(BASE_DIR, 'data-updates', 'approved-claims.json')
ARCHIVE_DIR = os.path.join(BASE_DIR, 'data-updates', 'archive')
LOG_FILE = os.path.join(BASE_DIR, 'data', 'apply_claims.log')
SOURCES_LOG_MD = os.path.join(BASE_DIR, 'data', 'sources.log.md')
COMPANY_SURFACED_LOG = os.path.join(BASE_DIR, 'data', 'company-surfaced.log.json')

# Structured claim types handled by this module (wq-014). Dispatch table wired
# at the bottom of the file, after the per-type apply_* functions are defined.
STRUCTURED_TYPES = ('power_project', 'hiring_snapshot', 'patent_snapshot', 'company_surfaced')

# Publish-ready confidence casing per GUIDELINES §4.4 / §5.6.
CONFIDENCE_DISPLAY = {'high': 'High', 'medium': 'Med', 'low': 'Low'}

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
        'dateOfClaim': coerce_or_keep(claim.get('source_date') or '', datetime.now().strftime('%Y-%m-%d')),
        'dateAdded': datetime.now().strftime('%Y-%m-%d'),
        'usedOn': ['dashboard'],
        'notes': f"Auto-applied from claims review. Weight: {claim.get('weight', '?')}. Dedup: {claim.get('dedup_status', '?')}.",
        'tags': [claim.get('entity', '').lower(), claim.get('category', '')],
        'metricKey': f"{claim.get('entity', '').lower().replace(' ', '-')}-{claim.get('metric', '').lower().replace(' ', '-')}",
        'status': 'accepted',
    })
    return dp_id


# ---------------------------------------------------------------------------
# Structured claim routing (wq-014)
#
# Each apply_<type> function accepts one accepted claim and mutates
# `site` / `companies` / a log file in place. Returns True on change.
#
# Provenance translation: claim payloads carry a nested `source` block
# (brief wq-014 §2). GUIDELINES §4.2 requires flat sourceUrl/retrievedAt/
# nextReview/confidence on stored entries. We flatten on write.
# ---------------------------------------------------------------------------

def _flatten_source(block, include_next_review=True):
    out = {
        'sourceUrl': block.get('url', ''),
        'retrievedAt': block.get('retrievedAt', ''),
        'confidence': CONFIDENCE_DISPLAY.get((block.get('confidence') or '').lower(),
                                             block.get('confidence') or ''),
    }
    if include_next_review and block.get('nextReview'):
        out['nextReview'] = block['nextReview']
    # Preserve source sub-type (ATS identifier, patent fetch method) alongside the flat envelope
    if block.get('type'):
        out['sourceType'] = block['type']
    if block.get('token'):
        out['sourceToken'] = block['token']
    return out


def _ensure_path(site, *keys):
    """Navigate into site[key1][key2]..., creating empty dicts along the way.
    Returns the node at the final key. `_ensure_path(site, 'a', 'b')` returns
    site['a']['b'], creating both intermediate and terminal keys if absent."""
    node = site
    for k in keys:
        if k not in node or node[k] is None:
            node[k] = {}
        node = node[k]
    return node


def _append_sources_log_row(row):
    """Append one row to data/sources.log.md (Markdown table)."""
    if not os.path.exists(SOURCES_LOG_MD):
        return  # File not present; silently skip. Phase 2 of wq-015 wires this file up.
    with open(SOURCES_LOG_MD, 'a') as f:
        f.write('| ' + ' | '.join(str(row.get(c, '')) for c in
                ('date', 'field', 'priorValue', 'newValue', 'reason',
                 'sourceId', 'operator', 'reviewer', 'commit')) + ' |\n')


def apply_power_project(site, claim):
    """Upsert a power project by (queue_market, queue_id) into site.power.projects."""
    power = _ensure_path(site, 'power')
    projects = power.setdefault('projects', [])
    merge_key = (claim.get('queue_market'), claim.get('queue_id'))
    if not all(merge_key):
        log(f"  SKIP power_project: missing queue_market or queue_id")
        return False

    entry = {
        'id': f"{merge_key[0].lower()}-{merge_key[1].lower()}",
        'queue_market': claim['queue_market'],
        'queue_id': claim['queue_id'],
        'stage': claim.get('stage'),
    }
    for field in ('company_slug', 'attribution_confidence', 'attribution_sources',
                  'poi', 'county', 'mw_requested', 'mw_approved', 'mw_in_service',
                  'requested_cod', 'llc_of_record'):
        if field in claim:
            entry[field] = claim[field]
    entry.update(_flatten_source(claim.get('source', {})))
    entry['label'] = f"{entry['queue_market']} {entry['queue_id']}" + (
        f" ({entry.get('mw_requested')} MW)" if entry.get('mw_requested') else ''
    )
    entry['year'] = int((claim.get('source', {}).get('retrievedAt') or '0000')[:4]) or None
    entry['unit'] = 'MW'

    existing_idx = next((i for i, p in enumerate(projects)
                         if (p.get('queue_market'), p.get('queue_id')) == merge_key), None)
    if existing_idx is None:
        projects.append(entry)
        log(f"  ADD power_project: {entry['label']}")
    else:
        projects[existing_idx] = entry
        log(f"  UPDATE power_project: {entry['label']}")

    _append_sources_log_row({
        'date': datetime.utcnow().strftime('%Y-%m-%d'),
        'field': f"power.projects[{entry['id']}]",
        'priorValue': 'null' if existing_idx is None else 'prior',
        'newValue': entry['label'],
        'reason': 'apply_claims — accepted power_project claim',
        'sourceId': claim.get('source', {}).get('url', ''),
        'operator': 'agent:apply_claims@1.1',
        'reviewer': 'human via claims.html',
        'commit': '(pending)',
    })
    return True


def apply_hiring_snapshot(site, claim):
    company = claim.get('company_slug')
    window = claim.get('window')
    if not company or not window:
        log("  SKIP hiring_snapshot: missing company_slug or window")
        return False

    snapshots = _ensure_path(site, 'hiring', 'snapshots')
    per_company = snapshots.setdefault(company, {})
    entry = {
        'company_slug': company,
        'window': window,
        'metrics': dict(claim.get('metrics', {})),
        'label': f"{company} hiring — {window}",
        'unit': 'count',
        'year': int(window[:4]) if window[:4].isdigit() else None,
    }
    if 'by_function' in claim:
        entry['by_function'] = dict(claim['by_function'])
    entry.update(_flatten_source(claim.get('source', {})))

    prior = window in per_company
    per_company[window] = entry
    log(f"  {'UPDATE' if prior else 'ADD'} hiring_snapshot: {entry['label']}")

    _append_sources_log_row({
        'date': datetime.utcnow().strftime('%Y-%m-%d'),
        'field': f"hiring.snapshots.{company}.{window}",
        'priorValue': 'prior' if prior else 'null',
        'newValue': f"{entry['metrics'].get('open_roles_ai_titled', '?')} AI-titled / {entry['metrics'].get('open_roles_total', '?')} total",
        'reason': 'apply_claims — accepted hiring_snapshot claim',
        'sourceId': claim.get('source', {}).get('url', ''),
        'operator': 'agent:apply_claims@1.1',
        'reviewer': 'human via claims.html',
        'commit': '(pending)',
    })
    return True


def apply_patent_snapshot(site, claim):
    company = claim.get('company_slug')
    window = claim.get('window')
    if not company or not window:
        log("  SKIP patent_snapshot: missing company_slug or window")
        return False

    snapshots = _ensure_path(site, 'patents', 'snapshots')
    per_company = snapshots.setdefault(company, {})
    entry = {
        'company_slug': company,
        'assignee_ids': list(claim.get('assignee_ids', [])),
        'window': window,
        'metrics': dict(claim.get('metrics', {})),
        'label': f"{company} patents — {window}",
        'unit': 'count',
        'year': int(window[:4]) if window[:4].isdigit() else None,
    }
    if 'top_cpc_subclasses' in claim:
        entry['top_cpc_subclasses'] = [dict(x) for x in claim['top_cpc_subclasses']]
    entry.update(_flatten_source(claim.get('source', {})))

    prior = window in per_company
    per_company[window] = entry
    log(f"  {'UPDATE' if prior else 'ADD'} patent_snapshot: {entry['label']}")

    _append_sources_log_row({
        'date': datetime.utcnow().strftime('%Y-%m-%d'),
        'field': f"patents.snapshots.{company}.{window}",
        'priorValue': 'prior' if prior else 'null',
        'newValue': f"{entry['metrics'].get('applications_published_trailing_12m', '?')} apps 12m",
        'reason': 'apply_claims — accepted patent_snapshot claim',
        'sourceId': claim.get('source', {}).get('url', ''),
        'operator': 'agent:apply_claims@1.1',
        'reviewer': 'human via claims.html',
        'commit': '(pending)',
    })
    return True


def apply_company_surfaced(claim):
    """Append a surfaced candidate to companies.json candidates list + dedicated log.

    Does NOT promote to the main companies list — that requires enrichment
    (outreach_status, providers, volume estimate) and stays a manual step.
    """
    name = claim.get('candidate_name')
    if not name:
        log("  SKIP company_surfaced: missing candidate_name")
        return False

    with open(COMPANIES_FILE) as f:
        companies = json.load(f)
    candidates = companies.setdefault('candidates', [])

    already = next((c for c in candidates
                    if c.get('candidate_name', '').lower() == name.lower()), None)
    if already:
        log(f"  SKIP company_surfaced: {name} already in candidates list")
        return False

    entry = {
        'candidate_name': name,
        'candidate_aliases': list(claim.get('candidate_aliases', [])),
        'first_seen_signal': dict(claim.get('first_seen_signal', {})),
        'density_score_estimate': claim.get('density_score_estimate'),
        'surfaced_at': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'status': 'candidate',
    }
    entry.update(_flatten_source(claim.get('source', {}), include_next_review=False))
    candidates.append(entry)

    with open(COMPANIES_FILE, 'w') as f:
        json.dump(companies, f, indent=2)

    # Separate append-only log for provenance/audit
    log_rows = []
    if os.path.exists(COMPANY_SURFACED_LOG):
        with open(COMPANY_SURFACED_LOG) as f:
            log_rows = json.load(f)
    log_rows.append(entry)
    with open(COMPANY_SURFACED_LOG, 'w') as f:
        json.dump(log_rows, f, indent=2)

    log(f"  ADD company_surfaced: {name}")
    _append_sources_log_row({
        'date': datetime.utcnow().strftime('%Y-%m-%d'),
        'field': f"companies.candidates[{name}]",
        'priorValue': 'null',
        'newValue': name,
        'reason': 'apply_claims — accepted company_surfaced claim',
        'sourceId': claim.get('source', {}).get('url', ''),
        'operator': 'agent:apply_claims@1.1',
        'reviewer': 'human via claims.html',
        'commit': '(pending)',
    })
    return True


STRUCTURED_APPLIERS = {
    'power_project': lambda site, vault, claim: apply_power_project(site, claim),
    'hiring_snapshot': lambda site, vault, claim: apply_hiring_snapshot(site, claim),
    'patent_snapshot': lambda site, vault, claim: apply_patent_snapshot(site, claim),
    'company_surfaced': lambda site, vault, claim: apply_company_surfaced(claim),
}


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

        # Structured claim types (wq-014) — dispatch by type before the
        # legacy entity/metric heuristics.
        claim_type = claim.get('type')
        if claim_type in STRUCTURED_TYPES:
            applier = STRUCTURED_APPLIERS[claim_type]
            if applier(site, vault, claim):
                add_to_vault(vault, claim)
                applied += 1
            else:
                skipped += 1
            continue

        metric = (claim.get('metric') or '').lower()
        entity = claim.get('entity', '')

        changed = False

        # Handle new company additions and updates
        if metric in ('new_company', 'update_company') and claim.get('company_data'):
            company = claim['company_data']
            existing_idx = None
            for i, c in enumerate(site['dashboard']['topConsumers']):
                if c['co'].lower() == company['co'].lower():
                    existing_idx = i
                    break

            if metric == 'update_company' and existing_idx is not None:
                old = site['dashboard']['topConsumers'][existing_idx]
                for k, v in company.items():
                    if v is not None and v != '' and v != 0:
                        old[k] = v
                old['lastUpdated'] = datetime.now().strftime('%Y-%m-%d')
                site['dashboard']['topConsumers'].sort(key=lambda c: c.get('tokensNumeric') or 0, reverse=True)
                log(f"  UPDATE COMPANY {company['co']} (source: {claim.get('source_url', '?')})")
                changed = True
            elif existing_idx is None:
                site['dashboard']['topConsumers'].append(company)
                site['dashboard']['topConsumers'].sort(key=lambda c: c.get('tokensNumeric') or 0, reverse=True)
                log(f"  ADD COMPANY {company['co']} ({company.get('tokens', '?')})")
                changed = True
            else:
                log(f"  SKIP {company['co']}: already exists (use update_company to edit)")

        elif 'arr' in metric or 'revenue' in metric:
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
