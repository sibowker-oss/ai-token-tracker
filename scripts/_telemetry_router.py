"""
_telemetry_router.py — shared telemetry detection + bucket-append helper.

Owned by wq-047. Single source of truth for what counts as
"operational telemetry" vs a human-extractable claim.

Telemetry items (hiring scrapes, package downloads, GitHub stats,
SEC filings monitoring) are written to data/telemetry-feed.json
instead of vault-inbox.json so they don't pollute the review queue.

Importers: scripts/monitor_sources.py, scripts/scan_sources.py.
Schema: data/telemetry-schema.md.
"""

import json
import os
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TELEMETRY_PATH = os.path.join(BASE_DIR, 'data', 'telemetry-feed.json')

TELEMETRY_SOURCE_TYPES = {
    'ats_api',
    'package_index',
    'github_repo',
    'sec_filing',
    'patent_index',
    'permit_db',
}

TELEMETRY_METRIC_KEYS = {
    'X-hiring_snapshot',
    'X-patent_snapshot',
    'X-power_project',
    'pypi_downloads',
    'npm_downloads',
    'docker_pulls',
    'github_stars',
    'recent_filings',
}

# Vault-item `type` values that originate from automated structured scrapers
# (monitor_sources.py:_STRUCTURED_TYPES_SET). These carry telemetry payloads
# even when no explicit metric_key is set.
TELEMETRY_STRUCTURED_TYPES = {
    'hiring_snapshot',
    'patent_snapshot',
    'power_project',
}


def _metric_key(claim_or_item):
    return (
        claim_or_item.get('metric_key')
        or claim_or_item.get('metricKey')
        or claim_or_item.get('metric')
        or ''
    )


def _source_type(claim_or_item, source):
    return (
        claim_or_item.get('sourceType')
        or claim_or_item.get('source_type')
        or (source or {}).get('type')
        or ''
    )


def is_telemetry(claim_or_item, source=None):
    """Return True if this claim/item should route to telemetry-feed.json
    instead of vault-inbox.json.

    Accepts either a raw extractor claim dict or a vault-item-shaped dict.
    `source` is the matching sources-registry entry (optional — falls back
    to fields on the item itself)."""
    if (claim_or_item.get('type') or '') in TELEMETRY_STRUCTURED_TYPES:
        return True

    stype = _source_type(claim_or_item, source)
    if stype in TELEMETRY_SOURCE_TYPES:
        return True

    metric = _metric_key(claim_or_item)
    if metric in TELEMETRY_METRIC_KEYS:
        return True
    if metric.startswith('X-') or metric.endswith('_downloads'):
        return True

    return False


def _vault_item_to_telemetry_payload(item):
    """Project a vault-item-shaped dict into a telemetry-feed `data` payload.

    Preserves the structured payload verbatim where present
    (monitor_sources.py:_structured_claim_to_vault sets `structured_payload`),
    falls back to a flat value/unit projection otherwise."""
    if 'structured_payload' in item:
        sp = item['structured_payload']
        # Strip transport-only fields; keep the metric content.
        return {k: v for k, v in sp.items() if k != 'source'}
    return {
        'value': item.get('value'),
        'unit': item.get('unit', ''),
        'claim': item.get('claim', ''),
    }


def _telemetry_type(item):
    """Pick a `type` for the telemetry-feed record."""
    if item.get('type') in TELEMETRY_STRUCTURED_TYPES:
        return item['type']
    metric = _metric_key(item)
    if metric.startswith('X-'):
        return metric[2:]  # strip X- prefix for cleaner type tag
    if metric.endswith('_downloads'):
        return 'package_downloads'
    if metric:
        return metric
    return item.get('sourceType') or 'unknown'


def _load_feed():
    if os.path.exists(TELEMETRY_PATH):
        with open(TELEMETRY_PATH) as f:
            return json.load(f)
    return {'items': [], 'lastWritten': None}


def _save_feed(feed):
    with open(TELEMETRY_PATH, 'w') as f:
        json.dump(feed, f, indent=2)


def append_to_telemetry_feed(item, source, today):
    """Append a single telemetry record to data/telemetry-feed.json.

    `item` is a vault-item-shaped dict (post-conversion from extractor output).
    `source` is the sources-registry entry. `today` is YYYY-MM-DD."""
    feed = _load_feed()
    src_id = (source or {}).get('id') or item.get('source_id') or 'unknown'
    seq = len(feed['items']) + 1
    entry_id = f"tel-{today.replace('-', '')}-{src_id}-{seq:03d}"
    entry = {
        'id': entry_id,
        'type': _telemetry_type(item),
        'entity': item.get('entity') or '',
        'source_id': src_id,
        'source_url': item.get('sourceUrl') or item.get('source_url') or (source or {}).get('url', ''),
        'scraped_at': datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'),
        'data': _vault_item_to_telemetry_payload(item),
        'metric_key': _metric_key(item),
    }
    feed['items'].append(entry)
    feed['lastWritten'] = entry['scraped_at']
    _save_feed(feed)
    return entry


def split_telemetry(items, source=None):
    """Split a list of vault-item-shaped dicts into (telemetry, inbox).

    Convenience for callers that already convert claims to vault-item shape
    before deciding the destination."""
    telemetry, inbox = [], []
    for it in items:
        (telemetry if is_telemetry(it, source) else inbox).append(it)
    return telemetry, inbox
