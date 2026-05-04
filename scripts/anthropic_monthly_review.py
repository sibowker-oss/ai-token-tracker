#!/usr/bin/env python3
"""
anthropic_monthly_review.py — wq-079 monthly editorial cadence.

Generates `data/anthropic-monthly-<YYYY-MM>.md` summarising:
  - Latest accepted Anthropic-related claims (last 30 days)
  - Pending Anthropic-related claims still in vault-inbox
  - Engine output for collected_revenue 2025+2026
  - Override status + gap-to-engine
  - Override-retirement candidate flag (engine within ±5% of override)

Read-only against the data — does NOT auto-retire any override. The flag
is editorial signal for Simon's monthly review (wq-079 §3 #5).

Run: python3 scripts/anthropic_monthly_review.py
     python3 scripts/anthropic_monthly_review.py --year-month 2026-05  (override the report month)
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import date, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from derive_collected_revenue import (  # noqa: E402
    load_config,
    load_overrides,
    derive_collected_revenue,
)

ENTITIES_PATH = os.path.join(BASE_DIR, 'entities.json')
VAULT_INBOX_PATH = os.path.join(BASE_DIR, 'vault-inbox.json')
VAULT_DATA_PATH = os.path.join(BASE_DIR, 'vault-data.json')
REPORT_DIR = os.path.join(BASE_DIR, 'data')

ANTHROPIC_SLUG = 'anthropic'
RETIREMENT_BAND = 0.05  # ±5% per brief §3 #1


def _load_json(path, default=None):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default if default is not None else {}


def _is_anthropic(item):
    """An item is Anthropic-related if its `entity` field, claim text, or
    tags reference anthropic / claude."""
    entity = (item.get('entity') or '').lower()
    if 'anthropic' in entity or 'claude' in entity:
        return True
    claim = (item.get('claim') or '').lower()
    if 'anthropic' in claim or 'claude' in claim:
        return True
    tags = ' '.join(item.get('tags') or []).lower()
    if 'anthropic' in tags or 'claude' in tags:
        return True
    return False


def _get_anthropic_entity(entities):
    for c in entities.get('companies', []):
        if c.get('slug') == ANTHROPIC_SLUG:
            return c
    return None


def _engine_output(entity, year, config):
    """Run the consensus engine for one year. Returns a flattened
    {'value', 'confidence', 'inputs', 'stages'} dict — or None when the
    engine couldn't produce an estimate (no inputs)."""
    try:
        block = derive_collected_revenue(entity, year, config)
    except Exception as e:
        return {'value': None, 'error': str(e)}
    if not block or not block.get('claims'):
        return {'value': None, 'reason': 'no engine output'}
    claim = block['claims'][0]
    return {
        'value': claim.get('value'),
        'confidence': block.get('confidence'),
        'inputs': claim.get('inputs', {}),
        'stages': (claim.get('inputs') or {}).get('stages', {}),
    }


def _gap(engine_value, override_value):
    if engine_value is None or override_value in (None, 0):
        return None
    return (engine_value - override_value) / override_value


def _format_money(v, unit='$B'):
    if v is None:
        return '—'
    if isinstance(v, (int, float)):
        if abs(v) >= 10:
            return f'${v:.0f}B'
        return f'${v:.2f}B'
    return str(v)


def collect(year_month, today=None):
    today = today or date.today()
    cutoff = (today - timedelta(days=30)).isoformat()

    entities = _load_json(ENTITIES_PATH, {})
    inbox    = _load_json(VAULT_INBOX_PATH, {'items': []})
    vault    = _load_json(VAULT_DATA_PATH, {'dataPoints': []})
    overrides = load_overrides()
    config    = load_config()

    anthropic = _get_anthropic_entity(entities)
    if not anthropic:
        return None

    recent_accepted = [
        dp for dp in vault.get('dataPoints', [])
        if _is_anthropic(dp) and (dp.get('dateAdded') or '') >= cutoff
    ]
    pending = [
        it for it in inbox.get('items', [])
        if it.get('status') in ('pending', 'raw_pool') and _is_anthropic(it)
    ]
    pending.sort(key=lambda x: -(x.get('materiality', {}) or {}).get('score', 0)
                 if isinstance(x.get('materiality'), dict) else 0)

    engine_2025 = _engine_output(anthropic, '2025', config)
    engine_2026 = _engine_output(anthropic, '2026', config)
    override_2025 = overrides.get(f'{ANTHROPIC_SLUG}.2025.collected_revenue', {}) or {}
    override_2026 = overrides.get(f'{ANTHROPIC_SLUG}.2026.collected_revenue', {}) or {}

    state = {
        'today': today.isoformat(),
        'year_month': year_month,
        'cutoff': cutoff,
        'recent_accepted': recent_accepted,
        'pending': pending,
        'anthropic': anthropic,
        'engine_2025': engine_2025,
        'engine_2026': engine_2026,
        'override_2025': override_2025,
        'override_2026': override_2026,
    }
    return state


def render_markdown(state):
    if state is None:
        return '# Anthropic monthly review\n\nERROR: anthropic entity not found in entities.json.\n'

    today = state['today']
    ym = state['year_month']
    a = state['anthropic']
    fin = a.get('financials') or {}
    cur = a.get('current') or {}

    e25 = state['engine_2025'] or {}
    e26 = state['engine_2026'] or {}
    o25 = state['override_2025'] or {}
    o26 = state['override_2026'] or {}

    e25_val = e25.get('value') if isinstance(e25, dict) else None
    e26_val = e26.get('value') if isinstance(e26, dict) else None
    o25_val = o25.get('value')
    o26_val = o26.get('value')

    gap_2025 = _gap(e25_val, o25_val)
    gap_2026 = _gap(e26_val, o26_val)

    def retirement_status(gap):
        if gap is None:
            return 'no override'
        if abs(gap) <= RETIREMENT_BAND:
            return f'**RETIREMENT CANDIDATE** (gap {gap*100:+.1f}% within ±{RETIREMENT_BAND*100:.0f}%)'
        return f'gap {gap*100:+.1f}% (outside ±{RETIREMENT_BAND*100:.0f}% band)'

    lines = []
    lines.append(f'# Anthropic monthly review — {ym}')
    lines.append('')
    lines.append(f'Generated by `scripts/anthropic_monthly_review.py` on **{today}**.')
    lines.append('')
    lines.append('Per wq-079 — Anthropic is the central company story behind the Ledger and warrants a dedicated monthly editorial cadence. The override at $4.71B (set 2026-05-02 via §7.2 weighted consensus) is held pending fresh data; this report tracks the gap to engine output and flags retirement candidates when the two converge.')
    lines.append('')

    lines.append('## Current state (entity record)')
    lines.append('')
    lines.append('| Field | 2024 | 2025 | 2026 | current |')
    lines.append('|---|---|---|---|---|')
    fields = ['arr', 'collected_revenue', 'operating_loss', 'exit_arr']
    for f in fields:
        row = ['', '', '', '']
        for i, y in enumerate(('2024', '2025', '2026')):
            v = (fin.get(y) or {}).get(f)
            row[i] = _format_money(v) if isinstance(v, (int, float)) else (str(v) if v is not None else '—')
        cv = cur.get(f)
        row[3] = _format_money(cv) if isinstance(cv, (int, float)) else (str(cv) if cv is not None else '—')
        lines.append(f'| `{f}` | {row[0]} | {row[1]} | {row[2]} | {row[3]} |')
    lines.append('')

    lines.append('## Engine vs override')
    lines.append('')
    lines.append('| Year | Engine | Override | Gap | Status |')
    lines.append('|---|---|---|---|---|')
    lines.append(f'| 2025 collected_revenue | {_format_money(e25_val)} | {_format_money(o25_val)} | {(f"{gap_2025*100:+.1f}%" if gap_2025 is not None else "—")} | {retirement_status(gap_2025)} |')
    lines.append(f'| 2026 collected_revenue | {_format_money(e26_val)} | {_format_money(o26_val)} | {(f"{gap_2026*100:+.1f}%" if gap_2026 is not None else "—")} | {retirement_status(gap_2026)} |')
    lines.append('')

    if o25.get('reason') or o26.get('reason'):
        lines.append('### Override reasoning')
        lines.append('')
        if o25.get('reason'):
            lines.append(f'**2025**: {o25.get("reason")}')
            lines.append(f'_Set by {o25.get("set_by", "?")} on {o25.get("set_at", "?")}; expires {o25.get("expires_at", "—")}_')
            lines.append('')
        if o26.get('reason'):
            lines.append(f'**2026**: {o26.get("reason")}')
            lines.append(f'_Set by {o26.get("set_by", "?")} on {o26.get("set_at", "?")}; expires {o26.get("expires_at", "—")}_')
            lines.append('')

    lines.append('## Recent claims (last 30 days)')
    lines.append('')
    if not state['recent_accepted']:
        lines.append('_No Anthropic-related claims accepted into vault-data in the last 30 days._')
    else:
        lines.append('| Date | Claim | Value | Source |')
        lines.append('|---|---|---|---|')
        for dp in sorted(state['recent_accepted'], key=lambda x: x.get('dateAdded', ''), reverse=True)[:25]:
            claim = (dp.get('claim') or '')[:90].replace('|', '\\|')
            v = dp.get('value')
            unit = dp.get('unit', '')
            source = (dp.get('sourceAuthor') or dp.get('sourceUrl') or '')[:40].replace('|', '\\|')
            lines.append(f'| {dp.get("dateAdded", "?")} | {claim} | {_format_money(v) if isinstance(v, (int, float)) else (v or "")} {unit} | {source} |')
    lines.append('')

    lines.append('## Pending claims in inbox')
    lines.append('')
    if not state['pending']:
        lines.append('_No Anthropic-related claims currently pending review._')
    else:
        lines.append(f'**{len(state["pending"])} claim(s) pending.** Top items by materiality:')
        lines.append('')
        lines.append('| ID | Claim | Value | Status |')
        lines.append('|---|---|---|---|')
        for it in state['pending'][:15]:
            claim = (it.get('claim') or '')[:90].replace('|', '\\|')
            v = it.get('value')
            unit = it.get('unit', '')
            status = it.get('status', '?')
            lines.append(f'| `{it.get("id", "?")[:40]}` | {claim} | {_format_money(v) if isinstance(v, (int, float)) else (v or "")} {unit} | {status} |')
        if len(state['pending']) > 15:
            lines.append(f'| … | _{len(state["pending"]) - 15} more_ | | |')
    lines.append('')

    lines.append('## Gap-closing path')
    lines.append('')
    if gap_2025 is None or abs(gap_2025) <= RETIREMENT_BAND:
        lines.append('2025 override aligned with engine — eligible for retirement.')
    else:
        lines.append('To close the 2025 gap:')
        lines.append('- Need authoritative 2024 ARR ≥ $2B documented in primary source (currently editorial via wq-048 Phase C)')
        lines.append('- Need at least one 2025 collected-revenue corroborating source (Sacra estimate confirmed by independent reporting)')
        lines.append('- Need H2 2025 ARR ≥ $9B confirmed (consistent with Q3/Q4 interpolations)')
    lines.append('')

    lines.append('## Action')
    lines.append('')
    lines.append('- [ ] Review pending claims via `review.html?entity=anthropic`')
    lines.append('- [ ] Decide whether to retire override (manual edit of `data/consensus_overrides.json` if engine has converged)')
    lines.append('- [ ] Update `model-assumptions.md §1.2` if new authoritative data has landed')
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append(f'_See `anthropic-spotlight.html` for the live admin view. Override retirement criterion: |engine − override| ÷ override ≤ {RETIREMENT_BAND*100:.0f}%._')

    return '\n'.join(lines)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--year-month', help='YYYY-MM tag for the report file (default: current month)', default=None)
    p.add_argument('--out', help='Override output path', default=None)
    args = p.parse_args()

    today = date.today()
    ym = args.year_month or f'{today.year:04d}-{today.month:02d}'
    state = collect(ym, today)
    md = render_markdown(state)

    out_path = args.out or os.path.join(REPORT_DIR, f'anthropic-monthly-{ym}.md')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        f.write(md)

    print(f'Wrote {out_path}')
    if state:
        print(f'  Recent accepted: {len(state["recent_accepted"])}')
        print(f'  Pending in inbox: {len(state["pending"])}')
        e25 = (state['engine_2025'] or {}).get('value')
        o25 = (state['override_2025'] or {}).get('value')
        if e25 is not None and o25:
            print(f'  2025 engine={e25:.2f}B override={o25:.2f}B gap={(e25-o25)/o25*100:+.1f}%')


if __name__ == '__main__':
    main()
