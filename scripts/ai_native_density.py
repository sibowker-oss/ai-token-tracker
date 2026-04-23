#!/usr/bin/env python3
"""
AI Native Density — ranking score for the Stream 3 discovery review queue.

Per wq-013 §5: four normalised sub-scores combined with weights
0.30 / 0.20 / 0.20 / 0.30 (to be validated against the §6 31-company set).

Sub-scores:
  hiring     = ai_lca_filings_trailing_4q / log(employer_size_proxy)
  patents    = ai_cpc_applications_trailing_12m z-scored within funding tier
  capital    = total_funding_trailing_24m / months_since_last_round
  revenue    = ln(ARR_estimate) if known, else HF downloads / GH stars proxy

Output 0-100. Per brief: NOT tracked as a metric in its own right; used
as a ranking filter for the discovery review queue (claims.html sorts
candidate_surfaced by this). Never rendered publicly.

Run:
  python3 scripts/ai_native_density.py --slug anthropic
  python3 scripts/ai_native_density.py --all           (whole alias map)
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from dataclasses import dataclass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALIAS_MAP = os.path.join(BASE_DIR, 'data', 'company-alias-map.json')
SITE_DATA = os.path.join(BASE_DIR, 'site-data.json')

# Weights per wq-013 §5 — pre-validation defaults.
W_HIRING, W_PATENTS, W_CAPITAL, W_REVENUE = 0.30, 0.20, 0.20, 0.30


@dataclass
class Inputs:
    """Inputs per company. Any field may be None — the scorer routes
    around missing data rather than imputing."""
    ai_lca_filings_4q: int | None = None
    employer_size_proxy: int | None = None   # total headcount or open-role count
    ai_cpc_applications_12m: int | None = None
    funding_tier_peers: list[int] | None = None
    total_funding_24m_usd: float | None = None
    months_since_last_round: float | None = None
    arr_estimate_usd: float | None = None
    hf_downloads_month: int | None = None
    github_stars: int | None = None


def _safe_log(x: float, base: float = math.e) -> float:
    return math.log(max(x, 1), base)


def _zscore_in_tier(x: float, peers: list[float]) -> float:
    """Z-score x within its funding-tier peer list. Returns 0 if peers is
    empty or has no variance."""
    if not peers:
        return 0.0
    mean = sum(peers) / len(peers)
    var = sum((p - mean) ** 2 for p in peers) / len(peers)
    if var == 0:
        return 0.0
    return (x - mean) / math.sqrt(var)


def _normalise(x: float, min_ref: float = 0.0, max_ref: float = 10.0) -> float:
    """Clamp to [0, 1] given known reference bounds."""
    if max_ref == min_ref:
        return 0.0
    v = (x - min_ref) / (max_ref - min_ref)
    return max(0.0, min(1.0, v))


def score_hiring(inp: Inputs) -> float | None:
    if inp.ai_lca_filings_4q is None or inp.employer_size_proxy is None:
        return None
    raw = inp.ai_lca_filings_4q / _safe_log(inp.employer_size_proxy + 1)
    return _normalise(raw, 0.0, 50.0)


def score_patents(inp: Inputs) -> float | None:
    if inp.ai_cpc_applications_12m is None:
        return None
    z = _zscore_in_tier(inp.ai_cpc_applications_12m, inp.funding_tier_peers or [])
    # Map z-score range [-2, +2] to [0, 1]
    return _normalise(z + 2.0, 0.0, 4.0)


def score_capital(inp: Inputs) -> float | None:
    if inp.total_funding_24m_usd is None or inp.months_since_last_round is None:
        return None
    if inp.months_since_last_round <= 0:
        return None
    raw = inp.total_funding_24m_usd / (inp.months_since_last_round * 1e6)  # $M/month
    return _normalise(raw, 0.0, 200.0)


def score_revenue(inp: Inputs) -> float | None:
    if inp.arr_estimate_usd is not None and inp.arr_estimate_usd > 0:
        return _normalise(math.log(inp.arr_estimate_usd, 10) - 6, 0.0, 4.0)  # $1M → 0, $10B → 1
    if inp.hf_downloads_month is not None:
        return _normalise(math.log(inp.hf_downloads_month + 1, 10), 0.0, 8.0)
    if inp.github_stars is not None:
        return _normalise(math.log(inp.github_stars + 1, 10), 0.0, 6.0)
    return None


def density_score(inp: Inputs) -> tuple[int, dict]:
    """Returns (score_0_to_100, breakdown). Weight is redistributed across
    available sub-scores when some are missing, so a company with only
    hiring data gets a score based on just hiring."""
    components = [
        ('hiring', W_HIRING, score_hiring(inp)),
        ('patents', W_PATENTS, score_patents(inp)),
        ('capital', W_CAPITAL, score_capital(inp)),
        ('revenue', W_REVENUE, score_revenue(inp)),
    ]
    present = [(n, w, s) for n, w, s in components if s is not None]
    if not present:
        return 0, {'note': 'no sub-score data', 'components': {}}

    total_weight = sum(w for _, w, _ in present)
    score = sum(s * w for _, w, s in present) / total_weight
    breakdown = {
        'score': round(score * 100, 1),
        'components': {n: round(s, 3) for n, _, s in present},
        'missing': [n for n, _, s in components if s is None],
        'weights_redistributed_over': sum(w for _, w, _ in present),
    }
    return int(round(score * 100)), breakdown


def from_alias_entry(slug: str) -> Inputs:
    """Build Inputs from whatever signals are available for this slug in the
    repo's current state. v1 reads hiring/patent snapshots from
    site-data.json if present; otherwise returns an empty Inputs."""
    inp = Inputs()
    if not os.path.exists(SITE_DATA):
        return inp
    with open(SITE_DATA) as f:
        site = json.load(f)

    # Hiring — most recent snapshot
    hiring = site.get('hiring', {}).get('snapshots', {}).get(slug, {})
    if hiring:
        latest = max(hiring.values(), key=lambda s: s.get('retrievedAt', ''))
        m = latest.get('metrics', {}) if isinstance(latest, dict) else {}
        inp.employer_size_proxy = m.get('open_roles_total')
        # Use AI-titled as a proxy for LCA when LCA isn't wired yet
        if m.get('open_roles_ai_titled') is not None:
            inp.ai_lca_filings_4q = m['open_roles_ai_titled']

    # Patents — most recent snapshot
    patents = site.get('patents', {}).get('snapshots', {}).get(slug, {})
    if patents:
        latest = max(patents.values(), key=lambda s: s.get('retrievedAt', ''))
        m = latest.get('metrics', {}) if isinstance(latest, dict) else {}
        inp.ai_cpc_applications_12m = m.get('applications_published_trailing_12m')

    return inp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--slug', help='Score one company.')
    ap.add_argument('--all', action='store_true', help='Score every company in the alias map.')
    args = ap.parse_args()

    with open(ALIAS_MAP) as f:
        alias = json.load(f)
    companies = alias.get('companies', {})

    if args.slug:
        if args.slug not in companies:
            print(f"Unknown slug: {args.slug}")
            return 1
        score, breakdown = density_score(from_alias_entry(args.slug))
        print(json.dumps({'slug': args.slug, 'density': score, **breakdown}, indent=2))
        return 0

    if args.all:
        rows = []
        for slug in companies:
            s, _ = density_score(from_alias_entry(slug))
            rows.append((s, slug))
        rows.sort(reverse=True)
        for s, slug in rows:
            print(f"  {s:3d}  {slug}")
        return 0

    ap.print_help()
    return 1


if __name__ == '__main__':
    sys.exit(main())
