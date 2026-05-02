#!/usr/bin/env python3
"""wq-048 — consensus engine: derive collected_revenue from ARR + assumptions.

Implements assumptions-audit.md §2 conversion pipeline:

    Step 0: adjustedEndingARR = endingARR × ARR_METHOD.factor    [vanity stage]
    Step 1: baseRevenue       = growth_method(starting, ending) × ARR_METHOD.factor
    Step 2: segmentAdjusted   = baseRevenue × blendedSegmentFactor
    Step 3: finalEstimate     = segmentAdjusted × nrrBoost
    Step 4: confidenceBand    = finalEstimate × [0.85, 1.15]

Two methodology decisions confirmed in Phase A (see Phase A report on the
feat/wq-048-consensus-engine branch):

1. NRR application uses audit §2.5 formula: `nrrBoost = 1.0 + (NRR - 1.0) × 0.25`
   The brief example (§2 acceptance criteria #3) showed the raw NRR as the
   multiplier, but the audit unambiguously documents the dampened formula
   with a worked example (NRR 1.50 → 1.125). The audit wins.

2. ARR_METHOD.factor is applied to the *growth_method output*, NOT to
   endingARR before growth math. The brief's example provenance only makes
   arithmetic sense this way: log_mean(20, 5) × 0.88 = 9.52, which matches
   the brief example's baseRevenue. Multiplying endingARR by 0.88 first
   would give a different (and lower) baseRevenue. The "adjustedEndingARR"
   stage is recorded for transparency but doesn't actually feed the calc.

CLI:
    python3 scripts/derive_collected_revenue.py --validate
    python3 scripts/derive_collected_revenue.py --backfill --dry-run
    python3 scripts/derive_collected_revenue.py --backfill --apply       # MUTATES entities.json
    python3 scripts/derive_collected_revenue.py --entity openai --year 2025
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from log_run import logged_run  # noqa: E402

ENTITIES_PATH = ROOT / "entities.json"
CONFIG_PATH = ROOT / "data" / "consensus_config.json"
OVERRIDES_PATH = ROOT / "data" / "consensus_overrides.json"
LOG_PATH = ROOT / "data" / "consensus_log.md"
VALIDATION_REPORT_PATH = ROOT / "data" / "wq-048-validation-report.txt"


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return json.load(f)


def load_overrides() -> dict:
    if not OVERRIDES_PATH.exists():
        return {}
    with open(OVERRIDES_PATH) as f:
        d = json.load(f)
    # Strip _doc / _schema_example keys so override key lookups are clean
    return {k: v for k, v in d.items() if not k.startswith("_")}


def load_entities() -> dict:
    with open(ENTITIES_PATH) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Engine — pure functions
# ---------------------------------------------------------------------------

def _resolve_profile(slug: str, config: dict) -> dict:
    profiles = config["company_profiles"]
    return profiles.get(slug) or profiles["_default"]


def _blended_segment_factor(profile: dict, segment_factors: dict) -> float:
    return sum(
        share * segment_factors[segment]
        for segment, share in profile["segments"].items()
    )


def _quarterly_arrs(entity: dict, year: str) -> Optional[list[float]]:
    """Return [Q1, Q2, Q3, Q4] ARR snapshots for the year, or None if any missing.

    Looks for fields named {year}_q{1..4}.arr in financials, OR Q{1..4}.arr
    keys nested under financials[year]. The audit doesn't pin a schema; we
    accept either shape so future quarterly-claim ingest doesn't need a
    converter.
    """
    fin_year = (entity.get("financials") or {}).get(year) or {}
    for key_pattern in (
        ["Q1", "Q2", "Q3", "Q4"],
        ["q1", "q2", "q3", "q4"],
    ):
        nested = [fin_year.get(k, {}).get("arr") if isinstance(fin_year.get(k), dict)
                  else fin_year.get(f"{k}.arr") for k in key_pattern]
        if all(isinstance(v, (int, float)) for v in nested):
            return list(nested)
    # Top-level financials.{year}_q1.arr style
    top = entity.get("financials") or {}
    nested = [(top.get(f"{year}_Q{q}") or {}).get("arr") for q in (1, 2, 3, 4)]
    if all(isinstance(v, (int, float)) for v in nested):
        return list(nested)
    return None


def _starting_arr(entity: dict, year: str) -> Optional[float]:
    """Prior-year ending ARR, used as startingARR for the growth method.

    Falls back to None if not present, in which case growth_method becomes
    'ending_x_0.60' (60% haircut) per audit §2.4.
    """
    try:
        prior = str(int(year) - 1)
    except ValueError:
        return None
    prior_block = (entity.get("financials") or {}).get(prior) or {}
    v = prior_block.get("arr")
    return v if isinstance(v, (int, float)) else None


def _growth_calc(starting_arr: Optional[float], ending_arr: float,
                 quarterly: Optional[list[float]]) -> tuple[float, str]:
    """Return (baseRevenue_pre_method_haircut, growth_method_name).

    Per audit §2.4, selection precedence:
      1. quarterly data available → SUM(qARR × 0.25)  [haircut still applied later by caller]
      2. starting unknown          → ending × 0.60
      3. ratio > 1.5               → log_mean
      4. else                       → simple_average
    """
    if quarterly is not None and len(quarterly) == 4:
        return (sum(q * 0.25 for q in quarterly), "sum_quarterly_x_0.25")
    if starting_arr is None or starting_arr <= 0:
        return (ending_arr * 0.60, "ending_x_0.60")
    ratio = ending_arr / starting_arr
    if ratio > 1.5:
        # log mean = (E - S) / ln(E / S). For E < S (ratio < 1) this still
        # returns a sensible positive value, but we only fire this branch
        # when growth is hyper, so the input is always E > S × 1.5.
        return ((ending_arr - starting_arr) / math.log(ratio), "logarithmic_mean")
    return ((starting_arr + ending_arr) / 2, "simple_average")


def _apply_method_haircut(base_rev_pre: float, growth_method: str,
                          arr_method_factor: float) -> float:
    """Apply ARR_METHOD.factor to growth-method output.

    Per Phase A confirmation: factor applies to growth output, not to
    endingARR before growth math. Skip the haircut for sum_quarterly because
    quarterly snapshots don't suffer the best-period inflation that the
    haircut is meant to correct (per brief §5 edge case).
    """
    if growth_method == "sum_quarterly_x_0.25":
        return base_rev_pre  # no haircut — quarterly data already calendar-bound
    return base_rev_pre * arr_method_factor


def _nrr_boost(profile: dict, config: dict) -> float:
    """Audit §2.5: nrrBoost = 1.0 + (NRR - 1.0) × multiplier (when NRR > 1.0)."""
    nrr = profile.get("nrr", 1.0)
    if nrr <= 1.0:
        return 1.0
    multiplier = config.get("nrr_formula", {}).get("multiplier", 0.25)
    return 1.0 + (nrr - 1.0) * multiplier


def derive_collected_revenue(entity: dict, year: str, config: dict) -> Optional[dict]:
    """Run the §2 conversion pipeline for one entity-year.

    Returns the provenance block (matches §2 acceptance criteria #3 schema)
    or None if endingARR is not populated for this year.
    """
    fin_year = (entity.get("financials") or {}).get(year) or {}
    ending_arr = fin_year.get("arr")
    if not isinstance(ending_arr, (int, float)):
        return None

    slug = entity.get("slug", "")
    profile = _resolve_profile(slug, config)
    profile_used = slug if slug in config["company_profiles"] else "_default"

    method_name = profile["arr_method"]
    arr_method = config["arr_methods"][method_name]
    arr_method_factor = arr_method["factor"]

    starting_arr = _starting_arr(entity, year)
    quarterly = _quarterly_arrs(entity, year)

    base_rev_pre, growth_method = _growth_calc(starting_arr, ending_arr, quarterly)
    base_revenue = _apply_method_haircut(base_rev_pre, growth_method, arr_method_factor)

    blended = _blended_segment_factor(profile, config["segment_factors"])
    segment_adjusted = base_revenue * blended

    nrr_boost = _nrr_boost(profile, config)
    final_estimate = segment_adjusted * nrr_boost

    band_lo, band_hi = config["confidence_band"]
    confidence_band = [round(final_estimate * band_lo, 4), round(final_estimate * band_hi, 4)]

    adjusted_ending_arr = ending_arr * arr_method_factor  # vanity stage; see module docstring

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return {
        "confidence": "medium",
        "claim_count": 1,
        "claims": [{
            "id": f"derived-{year}-collected_revenue",
            "claim": f"Derived via consensus engine from {year} ARR + segment mix + ARR method haircut + growth method + NRR",
            "value": round(final_estimate, 4),
            "unit": "$B",
            "weight": "corroborating",
            "confidence": "estimated",
            "source": "scripts/derive_collected_revenue.py",
            "source_url": "",
            "date": today,
            "origin": "consensus_engine_derived",
            "inputs": {
                "endingARR": ending_arr,
                "startingARR": starting_arr,
                "quarterly_arrs": quarterly,
                "arrMethod": method_name,
                "arrMethodFactor": arr_method_factor,
                "blendedSegmentFactor": round(blended, 4),
                "nrrRaw": profile.get("nrr"),
                "nrrBoost": round(nrr_boost, 4),
                "growthMethod": growth_method,
                "profileUsed": profile_used,
                "stages": {
                    "adjustedEndingARR": round(adjusted_ending_arr, 4),
                    "baseRevenuePreHaircut": round(base_rev_pre, 4),
                    "baseRevenue": round(base_revenue, 4),
                    "segmentAdjusted": round(segment_adjusted, 4),
                    "finalEstimate": round(final_estimate, 4),
                    "confidenceBand": confidence_band,
                },
            },
        }],
    }


# ---------------------------------------------------------------------------
# Override resolution
# ---------------------------------------------------------------------------

def _override_active(ov: dict) -> bool:
    """Override is active if no expires_at, or expires_at > today."""
    expires = ov.get("expires_at")
    if not expires:
        return True
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return today < expires


def resolve_with_override(slug: str, year: str, engine_block: Optional[dict],
                          overrides: dict) -> dict:
    """Returns the resolved block: either engine-only, override-only, or
    override-wins-with-engine-recorded-as-context.

    Output shape:
      {
        "value": float,
        "origin": "consensus_engine_derived" | "editorial_override" | "no_inputs",
        "engine_block": <engine_block or None>,
        "override": <override metadata or None>,
      }
    """
    key = f"{slug}.{year}.collected_revenue"
    ov = overrides.get(key)
    if ov and _override_active(ov):
        return {
            "value": ov["value"],
            "origin": "editorial_override",
            "engine_block": engine_block,
            "override": ov,
        }
    if engine_block is None:
        return {"value": None, "origin": "no_inputs", "engine_block": None, "override": None}
    return {
        "value": engine_block["claims"][0]["value"],
        "origin": "consensus_engine_derived",
        "engine_block": engine_block,
        "override": None,
    }


# ---------------------------------------------------------------------------
# Validation gate (§3.4 + §4)
# ---------------------------------------------------------------------------

def _is_within_band(engine_value: Optional[float], target: float,
                    band: tuple[float, float] = (0.85, 1.15)) -> bool:
    if engine_value is None:
        return False
    lo, hi = target * band[0], target * band[1]
    return lo <= engine_value <= hi


def run_validate(entities: dict, config: dict, overrides: dict) -> list[dict]:
    """Compare engine output to assumptions-audit.md §4.4 hand-curated values.

    Returns a list of result dicts (one per validation target) for the report.
    """
    results = []
    targets = config.get("validation_targets", {})
    for slug, year_map in targets.items():
        if slug.startswith("_") or not isinstance(year_map, dict):
            continue  # skip _doc and other meta keys
        entity = next((c for c in entities.get("companies", []) if c.get("slug") == slug), None)
        if entity is None:
            for year, target in year_map.items():
                results.append({
                    "slug": slug, "year": year, "target": target,
                    "engine_value": None, "delta_pct": None, "within_band": False,
                    "note": "entity not in entities.json",
                })
            continue
        for year, target in year_map.items():
            engine_block = derive_collected_revenue(entity, year, config)
            resolved = resolve_with_override(slug, year, engine_block, overrides)
            engine_value = resolved["value"]
            within = _is_within_band(engine_value, target)
            delta_pct = ((engine_value - target) / target * 100) if engine_value is not None else None
            results.append({
                "slug": slug, "year": year, "target": target,
                "engine_value": engine_value,
                "delta_pct": delta_pct,
                "within_band": within,
                "origin": resolved["origin"],
                "engine_block": engine_block,
                "override": resolved["override"],
            })
    return results


def format_validation_table(results: list[dict]) -> str:
    lines = [
        "## Validation gate vs assumptions-audit.md §4.4 (±15% band)",
        "",
        f"{'Provider':12}  {'Year':6}  {'Hand-curated':>13}  {'Engine output':>15}  {'Delta':>10}  {'Within band?':>14}  Origin",
        f"{'-'*12}  {'-'*6}  {'-'*13}  {'-'*15}  {'-'*10}  {'-'*14}  {'-'*30}",
    ]
    for r in results:
        ev = r.get("engine_value")
        ev_str = f"${ev:.2f}B" if isinstance(ev, (int, float)) else "—"
        delta_str = f"{r['delta_pct']:+.1f}%" if r.get("delta_pct") is not None else "—"
        in_band = "✓ yes" if r["within_band"] else "✗ NO"
        origin = r.get("origin") or r.get("note") or ""
        lines.append(
            f"{r['slug']:12}  {r['year']:6}  ${r['target']:>11.2f}B  {ev_str:>15}  {delta_str:>10}  {in_band:>14}  {origin}"
        )
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Backfill (§2 acceptance criteria #6)
# ---------------------------------------------------------------------------

def run_backfill(entities: dict, config: dict, overrides: dict,
                 dry_run: bool = True) -> list[dict]:
    """Walk every entity × every populated year; derive collected_revenue.

    Returns a list of dicts describing each derivation (or skip reason).
    Default dry_run=True does NOT mutate entities.

    Brief §5 edge cases handled:
      - Missing prior-year ARR → 60% haircut growth method (in _growth_calc)
      - Quarterly data → quarterly interpolation (in _growth_calc)
      - Entity not in profile → _default (in _resolve_profile)
      - Mid-year ARR claim → engine derives whatever ARR snapshot is in
        entities.json. Brief §5's "only re-derive if Q4 dateOfClaim" rule
        is enforced in apply_decisions.py post-write hook (Phase C), not
        here — the backfill operates on whatever's in financials.<year>.arr.
    """
    results = []
    for entity in entities.get("companies", []):
        slug = entity.get("slug", "")
        years = (entity.get("financials") or {}).keys()
        for year in sorted(years):
            if "_projected" in year:
                continue
            fin_year = entity["financials"][year]
            existing = fin_year.get("collected_revenue")
            engine_block = derive_collected_revenue(entity, year, config)
            if engine_block is None:
                continue  # no ARR for this year → engine has no input
            resolved = resolve_with_override(slug, year, engine_block, overrides)
            engine_value = engine_block["claims"][0]["value"]
            resolved_value = resolved["value"]
            inputs = engine_block["claims"][0]["inputs"]
            delta_pct = (
                (resolved_value - existing) / existing * 100
                if isinstance(existing, (int, float)) and existing != 0 and resolved_value is not None
                else None
            )
            within_band = (
                _is_within_band(resolved_value, existing)
                if isinstance(existing, (int, float))
                else None
            )
            results.append({
                "slug": slug,
                "year": year,
                "existing": existing,
                "engine_output": engine_value,
                "resolved_value": resolved_value,
                "delta_pct_vs_existing": delta_pct,
                "within_band_vs_existing": within_band,
                "origin": resolved["origin"],
                "growth_method": inputs["growthMethod"],
                "profile_used": inputs["profileUsed"],
                "starting_arr": inputs["startingARR"],
                "ending_arr": inputs["endingARR"],
                "would_write": (resolved_value is not None and not dry_run),
            })
            if not dry_run and resolved_value is not None:
                fin_year["collected_revenue"] = resolved_value
                entity.setdefault("provenance", {})[f"{year}.collected_revenue"] = (
                    _override_provenance_block(resolved, engine_block)
                    if resolved["origin"] == "editorial_override"
                    else engine_block
                )
    return results


def _override_provenance_block(resolved: dict, engine_block: dict) -> dict:
    """Provenance block when an editorial override wins. Records both the
    override metadata AND the engine output as context (per brief §3.3)."""
    ov = resolved["override"]
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return {
        "confidence": "medium",
        "claim_count": 1,
        "claims": [{
            "id": f"override-{today}",
            "claim": f"Editorial override (engine output: ${engine_block['claims'][0]['value']}B): {ov.get('reason', '')}",
            "value": ov["value"],
            "unit": "$B",
            "weight": "authoritative",
            "confidence": "verified",
            "source": "data/consensus_overrides.json",
            "source_url": "",
            "date": today,
            "origin": "editorial_override",
            "override_set_by": ov.get("set_by"),
            "override_set_at": ov.get("set_at"),
            "override_expires_at": ov.get("expires_at"),
            "engine_value": engine_block["claims"][0]["value"],
            "engine_inputs": engine_block["claims"][0]["inputs"],
        }],
    }


def format_backfill_report(results: list[dict], dry_run: bool) -> str:
    lines = [
        "## Backfill diff — every entity × year with populated ARR",
        f"_{'DRY-RUN — no writes' if dry_run else 'APPLY MODE — entities.json mutated'}_",
        "",
        f"{'Slug':22}  {'Year':6}  {'Existing':>10}  {'Engine':>10}  {'Resolved':>10}  {'Δ%':>8}  {'Method':22}  {'Profile':12}  Origin",
        f"{'-'*22}  {'-'*6}  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*8}  {'-'*22}  {'-'*12}  {'-'*30}",
    ]
    for r in results:
        ex = r.get("existing")
        ev = r.get("engine_output")
        rv = r.get("resolved_value")
        dp = r.get("delta_pct_vs_existing")
        ex_s = f"${ex:.2f}B" if isinstance(ex, (int, float)) else "—"
        ev_s = f"${ev:.2f}B" if isinstance(ev, (int, float)) else "—"
        rv_s = f"${rv:.2f}B" if isinstance(rv, (int, float)) else "—"
        dp_s = f"{dp:+6.1f}%" if dp is not None else "—"
        method = r.get("growth_method") or ""
        profile = r.get("profile_used") or ""
        origin = r.get("origin") or ""
        lines.append(
            f"{r['slug']:22}  {r['year']:6}  {ex_s:>10}  {ev_s:>10}  {rv_s:>10}  {dp_s:>8}  {method:22}  {profile:12}  {origin}"
        )

    # Summary
    total = len(results)
    with_existing = sum(1 for r in results if isinstance(r.get("existing"), (int, float)))
    in_band = sum(1 for r in results if r.get("within_band_vs_existing") is True)
    overrides_in = sum(1 for r in results if r.get("origin") == "editorial_override")
    lines += [
        "",
        "## Summary",
        f"  Total entity-years derived:                    {total}",
        f"  With existing collected_revenue value:         {with_existing}",
        f"  Engine output within ±15% of existing:         {in_band}",
        f"  Editorial overrides applied:                   {overrides_in}",
    ]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    with logged_run("derive_collected_revenue.py") as outputs:
        parser = argparse.ArgumentParser(description="Consensus engine for ARR-to-collected-revenue (wq-048).")
        parser.add_argument("--validate", action="store_true",
                            help="Run validation gate against assumptions-audit.md §4.4 hand-curated values.")
        parser.add_argument("--backfill", action="store_true",
                            help="Walk every entity × year and derive collected_revenue.")
        parser.add_argument("--dry-run", action="store_true",
                            help="With --backfill: report only, do not write to entities.json. Default = on.")
        parser.add_argument("--apply", action="store_true",
                            help="With --backfill: WRITE derived values to entities.json. Otherwise dry-run.")
        parser.add_argument("--entity", help="Inspect a single entity slug.")
        parser.add_argument("--year", help="With --entity: single year to derive.")
        parser.add_argument("--out", default=str(VALIDATION_REPORT_PATH),
                            help="Path for the validation/backfill report.")
        args = parser.parse_args()

        config = load_config()
        overrides = load_overrides()
        entities = load_entities()
        outputs["validation_targets"] = len(config.get("validation_targets", {}))
        outputs["overrides_loaded"] = len(overrides)

        if args.entity:
            ent = next((c for c in entities.get("companies", []) if c.get("slug") == args.entity), None)
            if not ent:
                print(f"No entity with slug={args.entity!r}")
                outputs["error"] = "entity_not_found"
                return
            year = args.year
            if not year:
                # Default to most recent non-projected year with ARR
                yrs = sorted(
                    y for y, d in (ent.get("financials") or {}).items()
                    if "_projected" not in y and isinstance(d, dict) and isinstance(d.get("arr"), (int, float))
                )
                if not yrs:
                    print(f"No populated ARR years for {args.entity}")
                    return
                year = yrs[-1]
            block = derive_collected_revenue(ent, year, config)
            if block is None:
                print(f"No ARR for {args.entity}.{year}")
                return
            print(json.dumps(block, indent=2))
            outputs["derived_value"] = block["claims"][0]["value"]
            return

        if args.validate:
            results = run_validate(entities, config, overrides)
            txt = (
                f"# wq-048 validation report\n"
                f"_Generated {datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')}_\n\n"
                + format_validation_table(results)
            )
            print(txt)
            VALIDATION_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
            VALIDATION_REPORT_PATH.write_text(txt)
            outputs["targets_validated"] = len(results)
            outputs["targets_in_band"] = sum(1 for r in results if r["within_band"])

        if args.backfill:
            dry_run = not args.apply
            results = run_backfill(entities, config, overrides, dry_run=dry_run)
            report = format_backfill_report(results, dry_run=dry_run)
            print(report)
            # Append backfill to validation report file
            existing_content = VALIDATION_REPORT_PATH.read_text() if VALIDATION_REPORT_PATH.exists() else ""
            if not args.validate:
                existing_content = (
                    f"# wq-048 backfill report\n"
                    f"_Generated {datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')}_\n\n"
                )
            VALIDATION_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
            VALIDATION_REPORT_PATH.write_text(existing_content + "\n" + report)

            if not dry_run:
                with open(ENTITIES_PATH, "w") as f:
                    json.dump(entities, f, indent=2)
                # Append to consensus_log.md
                today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                summary = (
                    f"\n## {today} — backfill --apply\n"
                    f"- Entity-years derived: {len(results)}\n"
                    f"- Editorial overrides applied: "
                    f"{sum(1 for r in results if r['origin'] == 'editorial_override')}\n"
                    f"- Trigger: manual CLI (--backfill --apply)\n"
                )
                with open(LOG_PATH, "a") as f:
                    f.write(summary)
                outputs["entities_written"] = sum(1 for r in results if r["would_write"])
            outputs["backfill_records"] = len(results)
            outputs["dry_run"] = dry_run


if __name__ == "__main__":
    main()
