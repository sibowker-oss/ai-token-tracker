#!/usr/bin/env python3
"""wq-039 — derive matcher rules from canonical sources.

Reads:
  - entities.json            (92 companies, slugs + names)
  - metric-schema.json       (8 roles × ~56 unique fields, with labels)
  - data/matcher_overrides.json   (hand-maintained overrides + extra synonyms)

Writes:
  - data/matcher_rules.generated.json   (entity_match_rules + field_match_rules)
  - data/matcher_coverage.md            (human-readable report)

Idempotent: same inputs produce identical outputs (sets are sorted; rule lists
are stable-sorted so the generated file diff stays clean across runs).

Resolution order in apply_decisions.py is: overrides → generated → legacy
(see brief §3.2). This script never touches metric-schema.json — the
hand-maintained rules there are preserved as the lowest-priority fallback.

Run:
  python3 scripts/build_matcher_rules.py
  python3 scripts/build_matcher_rules.py --dry-run     # diff vs existing output
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from log_run import logged_run  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ENTITIES_PATH = ROOT / "entities.json"
SCHEMA_PATH = ROOT / "metric-schema.json"
OVERRIDES_PATH = ROOT / "data" / "matcher_overrides.json"
GENERATED_PATH = ROOT / "data" / "matcher_rules.generated.json"
COVERAGE_PATH = ROOT / "data" / "matcher_coverage.md"

# Slugs at or below this length get \b word boundaries to avoid false
# positives (e.g. "xai" matching "xain", "amd" matching "amazed").
SHORT_SLUG_THRESHOLD = 4

# Hand-curated synonym hints — used when a field's label is too short to
# generate useful regex on its own. Keep this list narrow; per-field overrides
# belong in matcher_overrides.json.
DEFAULT_FIELD_SYNONYMS = {
    "arr": ["arr", "annualised revenue", "annualized revenue", "revenue run rate", "run rate"],
    "exit_arr": ["exit arr", "year end arr", "end of year arr", "exit run rate"],
    "ai_arr": ["ai arr", "ai revenue", "ai-specific arr"],
    "valuation": ["valuation", "valued at", "post-money", "post money"],
    "total_funding": ["total funding", "total raised", "raised to date", "funding raised"],
    "capex": ["capex", "capital expenditure", "capital spend"],
    "gpu_capex": ["gpu capex", "ai capex", "gpu spend"],
    "data_center_revenue": ["data center revenue", "datacenter revenue", "dc revenue"],
    "data_center_capacity": ["data center capacity", "datacenter capacity", "dc capacity"],
    "gpu_capacity": ["gpu capacity", "gpu count", "h100", "h200", "blackwell", "gb200"],
    "gpu_rental_revenue": ["gpu rental revenue", "gpu rental", "compute rental"],
    "tokens_per_day": ["tokens per day", "tokens/day", "daily tokens", "token volume"],
    "requests_per_day": ["requests per day", "requests/day", "daily requests", "api calls per day"],
    "user_count": ["user count", "active users", "monthly active users", "mau", "weekly active users", "wau"],
    "employees": ["employees", "headcount", "employee count", "staff count"],
    "employee_count": ["employees", "headcount", "employee count", "staff count"],
    "customer_count": ["customers", "customer count", "paying customers", "enterprise customers"],
    "paid_seats": ["paid seats", "paying seats", "licenses sold"],
    "subscription_revenue": ["subscription revenue", "subscriptions", "subscription income"],
    "operating_income": ["operating income", "operating profit", "op income"],
    "operating_loss": ["operating loss", "op loss"],
    "gross_profit": ["gross profit", "gross income"],
    "gross_margin_pct": ["gross margin", "gm%", "gross margin %"],
    "growth_rate": ["growth rate", "yoy growth", "year over year growth"],
    "market_share_pct": ["market share", "share of market", "market share %"],
    "cash_burn": ["cash burn", "burn rate", "monthly burn"],
    "blended_price_per_m": ["blended price", "average price per million", "blended cost"],
    "purchase_commitments": ["purchase commitments", "contractual commitments"],
    "contract_value": ["contract value", "tcv", "total contract value"],
    "enterprise_revenue": ["enterprise revenue", "enterprise arr", "enterprise sales"],
    "api_revenue": ["api revenue", "api business", "api arr"],
    "managed_api_revenue": ["managed api revenue", "managed api"],
    "consumer_pct": ["consumer percentage", "consumer share", "consumer revenue %"],
    "biz_pct": ["business percentage", "business share", "enterprise share"],
    "ai_cloud_revenue": ["ai cloud revenue", "azure ai revenue", "google cloud ai revenue"],
    "iaas_connected": ["iaas connected", "infrastructure connected"],
    "model_count": ["model count", "models hosted", "number of models"],
    "models_hosted": ["models hosted", "hosted models", "model catalog"],
    "model_providers_hosted": ["model providers hosted", "providers hosted"],
    "model_providers_resold": ["model providers resold", "providers resold"],
    "providers": ["model providers", "provider list"],
    "providers_connected": ["providers connected", "connected providers"],
    "primary_provider": ["primary provider", "main provider"],
    "key_products": ["key products", "main products", "product line"],
    "pricing_model": ["pricing model", "pricing tier", "price tier"],
    "seat_price": ["seat price", "price per seat", "per-seat pricing"],
    "total_addressable_seats": ["addressable seats", "tam seats", "total seats"],
    "active_rate": ["active rate", "activation rate", "active user %"],
    "people_sga": ["people sga", "sga people", "personnel sga"],
    "cogs_ratio": ["cogs ratio", "cogs %", "cost of goods sold %"],
    "margin_on_resale_pct": ["margin on resale", "resale margin"],
    "daily_spend": ["daily spend", "daily revenue", "spend per day"],
    "capex_from_customers": ["capex from customers", "customer-funded capex", "prepaid capex"],
    "rack_power_density_kw": ["rack power density", "rack density", "power per rack"],
    "dc_power_capacity_gw": ["dc power capacity", "data center power", "datacenter capacity gw"],
    "inference_cost": ["inference cost", "cost per inference", "inference unit cost"],
    "total_revenue": ["total revenue", "annual revenue"],
    "gpu_count": ["gpu count", "number of gpus", "gpu fleet"],
    "gpu_types": ["gpu types", "gpu mix", "h100/h200"],
    "arr_date": ["arr date", "arr as of", "arr measurement date"],
    "confidence": [],  # too generic — leave unmatched intentionally
}


def _esc(s: str) -> str:
    """Regex-escape but preserve the input for human-readable diffs."""
    return re.escape(s)


def _word_bounded(pattern: str) -> str:
    return rf"\b{pattern}\b"


def _label_to_synonyms(field_id: str, label: str) -> list[str]:
    """Derive obvious synonyms from a snake_case field_id and human label.

    Always includes the field_id itself (with underscores → spaces and hyphens),
    the label, and any DEFAULT_FIELD_SYNONYMS hardcoded above.
    """
    cands = set()
    cands.add(field_id.lower())
    cands.add(field_id.replace("_", " ").lower())
    cands.add(field_id.replace("_", "-").lower())
    if label:
        cands.add(label.lower())
        # Also try without parentheticals e.g. "Current ARR" → "current arr"
        cleaned = re.sub(r"\(.*?\)", "", label).strip().lower()
        if cleaned:
            cands.add(cleaned)
    for syn in DEFAULT_FIELD_SYNONYMS.get(field_id, []):
        cands.add(syn.lower())
    # Drop empty / trivially short
    return sorted({c for c in cands if c and len(c) >= 2})


def _entity_pattern(slug: str, name: str, aliases: list[str]) -> str:
    """Build a regex pattern for an entity.

    Short slugs (≤4 chars) get \\b word boundaries to prevent false positives
    like "amd" matching "amazed". Longer slugs / names are anchored loosely.
    """
    parts = []
    seen = set()
    forms = [slug, name] + list(aliases or [])
    for form in forms:
        if not form:
            continue
        f = form.strip()
        key = f.lower()
        if key in seen:
            continue
        seen.add(key)
        escaped = _esc(f.lower())
        if len(f) <= SHORT_SLUG_THRESHOLD:
            parts.append(_word_bounded(escaped))
        else:
            parts.append(escaped)
    return "|".join(parts)


def _field_pattern(synonyms: list[str]) -> str:
    """Order longest-first so 'exit arr' beats 'arr' when both match."""
    if not synonyms:
        return ""
    sorted_syns = sorted(synonyms, key=lambda s: (-len(s), s))
    return "|".join(_esc(s) for s in sorted_syns)


def _load_overrides() -> dict:
    if not OVERRIDES_PATH.exists():
        return {"entity_overrides": [], "field_overrides": [], "entity_aliases": {}, "field_synonyms": {}}
    with open(OVERRIDES_PATH) as f:
        data = json.load(f)
    data.setdefault("entity_overrides", [])
    data.setdefault("field_overrides", [])
    data.setdefault("entity_aliases", {})
    data.setdefault("field_synonyms", {})
    return data


def _ensure_overrides_file():
    """Create matcher_overrides.json if missing — initially empty arrays."""
    if OVERRIDES_PATH.exists():
        return
    OVERRIDES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OVERRIDES_PATH, "w") as f:
        json.dump({
            "_doc": "Hand-maintained overrides for the matcher. See brief wq-039 §2.4.",
            "entity_overrides": [],
            "field_overrides": [],
            "entity_aliases": {
                "_doc": "{ slug: [extra alias strings] } — appended to the generated entity rule",
            },
            "field_synonyms": {
                "_doc": "{ field_id: [extra synonym strings] } — appended to the generated field rule",
            },
        }, f, indent=2)
    print(f"  Created {OVERRIDES_PATH} (empty scaffold)")


def build_rules() -> tuple[dict, dict]:
    """Return (generated_dict, coverage_dict).

    coverage_dict has shape:
      {
        "entities_total": int, "entities_covered": int,
        "fields_total": int, "fields_covered": int,
        "uncovered_entities": [slug, ...],
        "uncovered_fields": [(field_id, role_id), ...],
      }
    """
    with open(ENTITIES_PATH) as f:
        ents = json.load(f)
    with open(SCHEMA_PATH) as f:
        schema = json.load(f)
    overrides = _load_overrides()

    extra_aliases = overrides.get("entity_aliases", {})
    extra_synonyms = overrides.get("field_synonyms", {})

    # ── Entity rules ────────────────────────────────────────────────────────
    entity_rules = []
    uncovered_entities = []
    for company in ents.get("companies", []):
        slug = company.get("slug", "")
        name = company.get("name", "")
        aliases = company.get("aliases", []) or []
        # Merge overrides aliases
        extras = extra_aliases.get(slug, [])
        if isinstance(extras, list):
            aliases = list(aliases) + extras
        pattern = _entity_pattern(slug, name, aliases)
        if not pattern:
            uncovered_entities.append(slug)
            continue
        entity_rules.append({
            "slug": slug,
            "pattern": pattern,
            "_source": "generated",
        })

    # ── Field rules ─────────────────────────────────────────────────────────
    field_rules = []
    uncovered_fields = []
    seen_fields = set()
    for role_id, role in schema.get("roles", {}).items():
        for field_id, fdef in role.get("fields", {}).items():
            if field_id in seen_fields:
                continue
            seen_fields.add(field_id)
            label = fdef.get("label", "")
            synonyms = _label_to_synonyms(field_id, label)
            # Append override synonyms
            extra = extra_synonyms.get(field_id, [])
            if isinstance(extra, list):
                synonyms = sorted(set(list(synonyms) + [s.lower() for s in extra if s]))
            pattern = _field_pattern(synonyms)
            if not pattern:
                uncovered_fields.append((field_id, role_id))
                continue
            field_rules.append({
                "field": field_id,
                "pattern": pattern,
                "_source": "generated",
                "_role": role_id,
            })

    # Stable sort for reproducible output
    entity_rules.sort(key=lambda r: r["slug"])
    # Field rules: keep rules with longer-pattern (more specific) first so
    # exit_arr beats arr. Within ties, sort by field_id alphabetically.
    field_rules.sort(key=lambda r: (-len(r["pattern"]), r["field"]))

    generated = {
        "_meta": {
            "_doc": "AUTO-GENERATED by scripts/build_matcher_rules.py — do not hand-edit. wq-039.",
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "entity_count": len(entity_rules),
            "field_count": len(field_rules),
            "source_files": ["entities.json", "metric-schema.json", "data/matcher_overrides.json"],
        },
        "entity_match_rules": entity_rules,
        "field_match_rules": field_rules,
    }

    all_field_ids = set(seen_fields)
    coverage = {
        "entities_total": len(ents.get("companies", [])),
        "entities_covered": len(entity_rules),
        "fields_total": len(all_field_ids),
        "fields_covered": len(field_rules),
        "uncovered_entities": sorted(uncovered_entities),
        "uncovered_fields": sorted(uncovered_fields),
    }
    return generated, coverage


def write_coverage_report(coverage: dict) -> str:
    ent_pct = 100 * coverage["entities_covered"] / max(1, coverage["entities_total"])
    fld_pct = 100 * coverage["fields_covered"] / max(1, coverage["fields_total"])
    lines = [
        "# Matcher coverage report",
        "",
        f"_Generated {datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')} — wq-039_",
        "",
        "## Summary",
        "",
        f"- **Entities**: {coverage['entities_covered']}/{coverage['entities_total']} = {ent_pct:.1f}%",
        f"- **Fields**:   {coverage['fields_covered']}/{coverage['fields_total']} = {fld_pct:.1f}%",
        "",
    ]
    if coverage["uncovered_entities"]:
        lines.append("## Uncovered entities")
        lines.append("")
        for slug in coverage["uncovered_entities"]:
            lines.append(f"- `{slug}` — consider adding alias for: …")
        lines.append("")
    if coverage["uncovered_fields"]:
        lines.append("## Uncovered fields")
        lines.append("")
        for field_id, role_id in coverage["uncovered_fields"]:
            lines.append(f"- `{field_id}` (role `{role_id}`)")
        lines.append("")
    lines.append("## How to add coverage")
    lines.append("")
    lines.append("Add an entry to `data/matcher_overrides.json`:")
    lines.append("")
    lines.append("```json")
    lines.append('{ "entity_aliases": { "openai": ["chatgpt enterprise", "gpt"] },')
    lines.append('  "field_synonyms": { "arr": ["annualized recurring revenue"] } }')
    lines.append("```")
    lines.append("")
    lines.append("Then re-run `python3 scripts/build_matcher_rules.py`.")
    return "\n".join(lines)


def diff_summary(old: dict, new: dict) -> str:
    if not old:
        return "First-run generation — no prior file to diff against."
    old_meta = old.get("_meta", {})
    new_meta = new.get("_meta", {})
    return (
        f"Entity rules: {old_meta.get('entity_count', '?')} → {new_meta['entity_count']} "
        f"({new_meta['entity_count'] - old_meta.get('entity_count', 0):+d})\n"
        f"Field rules:  {old_meta.get('field_count', '?')} → {new_meta['field_count']} "
        f"({new_meta['field_count'] - old_meta.get('field_count', 0):+d})"
    )


def main() -> None:
    with logged_run("build_matcher_rules.py") as outputs:
        parser = argparse.ArgumentParser(description="Build matcher rules from canonical data (wq-039).")
        parser.add_argument("--dry-run", action="store_true",
                            help="Do not write files; print diff vs existing output.")
        args = parser.parse_args()

        _ensure_overrides_file()
        generated, coverage = build_rules()

        old = {}
        if GENERATED_PATH.exists():
            try:
                with open(GENERATED_PATH) as f:
                    old = json.load(f)
            except json.JSONDecodeError:
                pass

        diff = diff_summary(old, generated)
        print(f"Coverage:  entity {coverage['entities_covered']}/{coverage['entities_total']} "
              f"({100*coverage['entities_covered']/coverage['entities_total']:.1f}%) | "
              f"field {coverage['fields_covered']}/{coverage['fields_total']} "
              f"({100*coverage['fields_covered']/coverage['fields_total']:.1f}%)")
        print(diff)

        outputs["entities_covered"] = coverage["entities_covered"]
        outputs["entities_total"] = coverage["entities_total"]
        outputs["fields_covered"] = coverage["fields_covered"]
        outputs["fields_total"] = coverage["fields_total"]
        outputs["dry_run"] = args.dry_run

        if args.dry_run:
            print("\n[DRY-RUN] No files written.")
            return

        GENERATED_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(GENERATED_PATH, "w") as f:
            json.dump(generated, f, indent=2)
        with open(COVERAGE_PATH, "w") as f:
            f.write(write_coverage_report(coverage))
        print(f"Wrote {GENERATED_PATH}")
        print(f"Wrote {COVERAGE_PATH}")


if __name__ == "__main__":
    main()
