#!/usr/bin/env python3
"""wq-040 — materiality scoring for review-queue triage.

Public API:
    score(claim, entities, schema) -> dict

Returns the materiality block per brief §3 #1:
    {
      "lane":               "material" | "context",
      "sublane":            "would_change" | "field_expansion" | None,
      "reason":             "...",
      "current_value":      number | None,
      "proposed_value":     number,
      "pct_delta":          float | None,
      "weight_vs_existing": "stronger" | "equal" | "weaker" | "no_existing",
      "age_days":           int,
      "scored_at":          ISO timestamp,
    }

Reuses apply_decisions.match_entity / match_field / match_year / infer_weight
so the lane assignment is consistent with the matcher and weight rules used at
accept time. wq-039's matcher rule layers are honoured automatically.

Decisions baked in (Simon 2026-05-02):
- BROAD threshold: entity match alone qualifies for material (sublane splits
  would_change vs field_expansion).
- No SLA on context lane — the age_days field powers the visual badge in
  review.html (≤7d none, 8-14d yellow, 15-30d orange, >30d red).

Usage:
    python3 scripts/score_materiality.py --backfill-inbox            # rewrite vault-inbox.json
    python3 scripts/score_materiality.py --backfill-inbox --dry-run  # histogram only, no write
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import apply_decisions as ad  # noqa: E402
from log_run import logged_run  # noqa: E402

ENTITIES_PATH = ROOT / "entities.json"
SCHEMA_PATH = ROOT / "metric-schema.json"
INBOX_PATH = ROOT / "vault-inbox.json"

# Threshold for would_change — a delta this large vs existing tracked value
# flips the sublane to would_change even when the source weight is equal/weaker.
DELTA_THRESHOLD = 0.10


def _claim_search_text(claim: dict) -> tuple[str, str]:
    """Mirror apply_decisions.apply_accepted — claim + entity + tags, plus
    metricKey for field fallback. Returns (search_text, metric_key_text)."""
    claim_t = claim.get("claim", "") or ""
    entity_t = claim.get("entity", "") or ""
    tags = claim.get("tags", []) or []
    search_text = (claim_t + " " + entity_t + " " + " ".join(tags)).lower()
    metric_key_text = (claim.get("metricKey") or "").lower()
    return search_text, metric_key_text


def _annualised_value(claim: dict):
    """Mirror apply_decisions annualisation — returns the annual-equivalent
    of a per-month / per-quarter claim so deltas vs existing arr are sane."""
    value = claim.get("value")
    if not isinstance(value, (int, float)):
        return value
    unit = (claim.get("unit") or "").lower()
    claim_text = (claim.get("claim") or "").lower()
    if "/month" in unit or "per month" in unit or "/month" in claim_text or "per month" in claim_text:
        return value * 12
    if "/quarter" in unit or "per quarter" in unit or "/quarter" in claim_text or "per quarter" in claim_text:
        return value * 4
    return value


def _resolve_existing(entity: dict, field_id: str, year):
    """Return the currently-tracked value for entity.field at year (or current
    block if no year). Returns None if no tracked value exists."""
    if not entity:
        return None
    if year:
        return ((entity.get("financials") or {}).get(year) or {}).get(field_id)
    return (entity.get("current") or {}).get(field_id)


def _existing_best_weight(entity: dict, field_id: str, year) -> str | None:
    """Return the weight tier of the strongest existing claim on that
    field/year. None if no provenance entry."""
    if not entity:
        return None
    prov_key = f"{year}.{field_id}" if year else f"current.{field_id}"
    prov = (entity.get("provenance") or {}).get(prov_key)
    if not prov or not prov.get("claims"):
        return None
    best_rank = -1
    best_weight = None
    for c in prov["claims"]:
        w = c.get("weight", "indicative")
        rank = ad.WEIGHT_RANK.get(w, 0)
        if rank > best_rank:
            best_rank = rank
            best_weight = w
    return best_weight


def _compare_weight(new_weight: str, existing_weight: str | None) -> str:
    if existing_weight is None:
        return "no_existing"
    nr = ad.WEIGHT_RANK.get(new_weight, 0)
    er = ad.WEIGHT_RANK.get(existing_weight, 0)
    if nr > er:
        return "stronger"
    if nr < er:
        return "weaker"
    return "equal"


def _is_proposed_field(field_id: str | None, schema: dict) -> bool:
    if not field_id:
        return False
    return any(f.get("field_id") == field_id for f in schema.get("proposed_fields", []) or [])


def _age_days(claim: dict, today: datetime | None = None) -> int:
    today = today or datetime.now(timezone.utc)
    date_added = claim.get("dateAdded") or ""
    if not date_added:
        return 0
    try:
        d = datetime.strptime(date_added, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return max(0, (today - d).days)
    except ValueError:
        return 0


def score(claim: dict, entities: dict, schema: dict, today: datetime | None = None) -> dict:
    """Return the materiality block for one claim. Pure function — no I/O."""
    today = today or datetime.now(timezone.utc)
    proposed_value = _annualised_value(claim)
    age_days = _age_days(claim, today)

    base = {
        "lane": "context",
        "sublane": None,
        "reason": "",
        "current_value": None,
        "proposed_value": proposed_value,
        "pct_delta": None,
        "weight_vs_existing": "no_existing",
        "age_days": age_days,
        "scored_at": today.isoformat(timespec="seconds").replace("+00:00", "Z"),
    }

    if proposed_value is None:
        base["reason"] = "no_value"
        return base

    search_text, metric_key_text = _claim_search_text(claim)
    legacy_entity_rules = schema.get("entity_match_rules", []) or []
    legacy_field_rules = schema.get("field_match_rules", []) or []
    entity_slug = ad.match_entity(search_text, legacy_entity_rules)
    field_id = ad.match_field(search_text, legacy_field_rules)
    if not field_id and metric_key_text:
        field_id = ad.match_field(metric_key_text, legacy_field_rules)

    if not entity_slug:
        base["reason"] = "no_entity_match"
        return base

    # BROAD threshold: entity match qualifies for material lane.
    entity = next((c for c in entities.get("companies", []) if c.get("slug") == entity_slug), None)
    if not entity:
        # Rule matched a slug but entity record absent — treat as no_entity_match.
        base["reason"] = "no_entity_match"
        return base

    # Proposed-field edge case (brief §5).
    if _is_proposed_field(field_id, schema):
        base["lane"] = "material"
        base["sublane"] = "would_change"
        base["reason"] = "proposed_field_evidence"
        return base

    if not field_id:
        base["lane"] = "material"
        base["sublane"] = "field_expansion"
        base["reason"] = "matches_entity_no_field"
        return base

    year = ad.match_year(search_text) or ad.match_year(claim.get("dateOfClaim", "") or "")
    existing = _resolve_existing(entity, field_id, year)
    existing_best_weight = _existing_best_weight(entity, field_id, year)
    new_weight = ad.infer_weight(claim)
    weight_cmp = _compare_weight(new_weight, existing_best_weight)
    base["weight_vs_existing"] = weight_cmp
    base["current_value"] = existing

    if existing is None:
        base["lane"] = "material"
        base["sublane"] = "would_change"
        base["reason"] = "new_value_for_known_field"
        return base

    if isinstance(existing, (int, float)) and isinstance(proposed_value, (int, float)) and existing != 0:
        pct_delta = abs(proposed_value - existing) / abs(existing)
        base["pct_delta"] = pct_delta
        if pct_delta >= DELTA_THRESHOLD:
            base["lane"] = "material"
            base["sublane"] = "would_change"
            base["reason"] = "would_change_existing_value"
            return base

    if weight_cmp == "stronger":
        base["lane"] = "material"
        base["sublane"] = "would_change"
        base["reason"] = "stronger_provenance_for_existing"
        return base

    base["reason"] = "confirms_existing_within_tolerance"
    return base


def _histogram(items_with_scores: list[dict]) -> str:
    """Return a text histogram. Used for the dry-run report."""
    total = len(items_with_scores)
    by_lane = {}
    by_sublane = {}
    by_reason = {}
    by_age = {"<=7d": 0, "8-14d": 0, "15-30d": 0, ">30d": 0}
    for it in items_with_scores:
        m = it["materiality"]
        by_lane[m["lane"]] = by_lane.get(m["lane"], 0) + 1
        sub = m.get("sublane") or "—"
        by_sublane[sub] = by_sublane.get(sub, 0) + 1
        by_reason[m["reason"]] = by_reason.get(m["reason"], 0) + 1
        a = m["age_days"]
        if a <= 7:
            by_age["<=7d"] += 1
        elif a <= 14:
            by_age["8-14d"] += 1
        elif a <= 30:
            by_age["15-30d"] += 1
        else:
            by_age[">30d"] += 1

    lines = [
        f"# wq-040 materiality histogram",
        f"_Generated {datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')}_",
        "",
        f"## Total scored: {total}",
        "",
        "## Lane split",
    ]
    for lane in ("material", "context"):
        n = by_lane.get(lane, 0)
        pct = 100 * n / max(1, total)
        lines.append(f"  {lane:10}  {n:5}  ({pct:5.1f}%)")
    lines.append("")
    lines.append("## Sublane split (material only)")
    for sub in ("would_change", "field_expansion", "—"):
        n = by_sublane.get(sub, 0)
        if n:
            lines.append(f"  {sub:18}  {n:5}")
    lines.append("")
    lines.append("## Reason breakdown")
    for reason, n in sorted(by_reason.items(), key=lambda x: -x[1]):
        pct = 100 * n / max(1, total)
        lines.append(f"  {reason:42}  {n:5}  ({pct:5.1f}%)")
    lines.append("")
    lines.append("## Age distribution")
    for bucket in ("<=7d", "8-14d", "15-30d", ">30d"):
        n = by_age[bucket]
        pct = 100 * n / max(1, total)
        lines.append(f"  {bucket:8}  {n:5}  ({pct:5.1f}%)")
    return "\n".join(lines) + "\n"


def backfill_inbox(dry_run: bool, today: datetime | None = None) -> tuple[int, int, str]:
    """Score every item in vault-inbox.json. Returns (scored_count,
    skipped_count, histogram_text). When dry_run=False, persists the
    materiality block on each item and saves the inbox."""
    today = today or datetime.now(timezone.utc)
    with open(ENTITIES_PATH) as f:
        entities = json.load(f)
    with open(SCHEMA_PATH) as f:
        schema = json.load(f)
    with open(INBOX_PATH) as f:
        inbox = json.load(f)

    # Force matcher cache reload so the latest generated rules get used.
    ad._RULE_CACHE = None
    ad._load_rule_layers()

    scored = 0
    skipped = 0
    items_with_scores = []
    for item in inbox.get("items", []):
        try:
            m = score(item, entities, schema, today=today)
        except Exception as e:
            skipped += 1
            continue
        item["materiality"] = m
        items_with_scores.append(item)
        scored += 1

    histogram_text = _histogram(items_with_scores)

    if not dry_run:
        with open(INBOX_PATH, "w") as f:
            json.dump(inbox, f, indent=2)
    return scored, skipped, histogram_text


def main() -> None:
    with logged_run("score_materiality.py") as outputs:
        parser = argparse.ArgumentParser(description="Score claim materiality (wq-040).")
        parser.add_argument("--backfill-inbox", action="store_true",
                            help="Score every item in vault-inbox.json.")
        parser.add_argument("--dry-run", action="store_true",
                            help="Print histogram; do not modify inbox.")
        parser.add_argument("--out", default=str(ROOT / "data" / "wq-040-lane-histogram.txt"),
                            help="Where to write the histogram report.")
        args = parser.parse_args()

        if not args.backfill_inbox:
            print("Use --backfill-inbox to score the existing inbox.")
            outputs["scored"] = 0
            return

        scored, skipped, histogram_text = backfill_inbox(args.dry_run)
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        with open(args.out, "w") as f:
            f.write(histogram_text)
        print(histogram_text)
        print(f"Scored: {scored}, skipped: {skipped}, wrote {args.out}")
        outputs["scored"] = scored
        outputs["skipped"] = skipped
        outputs["dry_run"] = args.dry_run


if __name__ == "__main__":
    main()
