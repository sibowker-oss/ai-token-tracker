#!/usr/bin/env python3
"""
apply_decisions.py — Process review decisions end-to-end.

Reads review-decisions-*.json (from review.html Submit),
then for each decision:

  ACCEPTED:
    1. Moves claim from vault-inbox → vault-data (with full provenance)
    2. Updates entities.json (entity + field + year)
    3. Adds provenance link
    4. Runs generate_site_data.py to rebuild site-data.json

  DECLINED:
    1. Marks claim as 'declined' in vault-inbox.json
    2. Moves to archive with reason

  PARKED:
    1. Marks claim as 'parked' in vault-inbox.json (stays for next review)

  NEW FIELDS APPROVED:
    1. Moves from proposed_fields → role fields in metric-schema.json
    2. Adds field_match_rule for auto-matching future claims

Run: python3 scripts/apply_decisions.py [decisions-file]
"""

import json, os, re, shutil, sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
SITE_DIR = ROOT_DIR

sys.path.insert(0, SCRIPT_DIR)
from log_run import logged_run  # noqa: E402

VAULT_DATA = os.path.join(SITE_DIR, "vault-data.json")
VAULT_INBOX = os.path.join(SITE_DIR, "vault-inbox.json")
ENTITIES = os.path.join(SITE_DIR, "entities.json")
SCHEMA = os.path.join(SITE_DIR, "metric-schema.json")
ARCHIVE_DIR = os.path.join(SITE_DIR, "data-updates", "archive")
LOG_FILE = os.path.join(ROOT_DIR, "data", "apply_decisions.log")

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# Single-pass mojibake markers: U+00E2 (the latin-1 reading of UTF-8 byte 0xE2,
# the leading byte of the U+2014 / U+2018 / U+2019 / U+201C / U+201D / U+2026
# punctuation block) plus U+0080 (the Latin-1 reading of UTF-8 byte 0x80, which
# follows 0xE2 in those sequences). Both must be present for safe_str to fire.
_MOJI_HIGH = "â"  # â — leading byte of mis-decoded U+201X punctuation
_MOJI_CTRL = ""  # invisible control — second byte of those sequences


def safe_str(s):
    """Defensive cleanup of single-pass mojibake on string fields.

    Catches the canonical U+00E2 + U+0080 pairing — UTF-8 punctuation bytes
    (E2 80 94 em-dash, E2 80 99 curly apostrophe, E2 80 93 en-dash, ...)
    decoded as Latin-1 — and undoes one pass of latin-1 -> utf-8. No-op for
    already-clean strings. Multi-pass / deep mojibake is left intact; the
    Phase 2 cleanup script iterates for those.

    See briefs/active/2026-04-26-mojibake-roundtrip-fix.md §4.2.
    """
    if not isinstance(s, str):
        return s
    if _MOJI_HIGH not in s or _MOJI_CTRL not in s:
        return s
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

# wq-039 matcher resolution order: overrides → generated → legacy.
# Caches loaded once per process; rebuild via scripts/build_matcher_rules.py.
_GENERATED_PATH = os.path.join(ROOT_DIR, "data", "matcher_rules.generated.json")
_OVERRIDES_PATH = os.path.join(ROOT_DIR, "data", "matcher_overrides.json")
_RULE_CACHE = None


def _load_rule_layers():
    global _RULE_CACHE
    if _RULE_CACHE is not None:
        return _RULE_CACHE
    layers = {"overrides_entity": [], "overrides_field": [],
              "generated_entity": [], "generated_field": []}
    if os.path.exists(_OVERRIDES_PATH):
        try:
            with open(_OVERRIDES_PATH) as f:
                ov = json.load(f)
            layers["overrides_entity"] = ov.get("entity_overrides", []) or []
            layers["overrides_field"] = ov.get("field_overrides", []) or []
        except (json.JSONDecodeError, OSError):
            pass
    if os.path.exists(_GENERATED_PATH):
        try:
            with open(_GENERATED_PATH) as f:
                gen = json.load(f)
            layers["generated_entity"] = gen.get("entity_match_rules", []) or []
            layers["generated_field"] = gen.get("field_match_rules", []) or []
        except (json.JSONDecodeError, OSError):
            pass
    _RULE_CACHE = layers
    return _RULE_CACHE


def match_entity(text, rules):
    """Resolution order: overrides → generated → legacy (the `rules` arg).

    `rules` is the legacy hand-maintained list from metric-schema.json,
    preserved as the lowest-priority fallback so existing rules still
    catch what the canonical-derived rules miss.
    """
    layers = _load_rule_layers()
    for source in (layers["overrides_entity"], layers["generated_entity"], rules):
        for rule in source:
            try:
                if re.search(rule["pattern"], text, re.I):
                    return rule["slug"]
            except re.error:
                continue
    return None


def match_field(text, rules):
    layers = _load_rule_layers()
    for source in (layers["overrides_field"], layers["generated_field"], rules):
        for rule in source:
            try:
                if re.search(rule["pattern"], text, re.I):
                    return rule["field"]
            except re.error:
                continue
    return None

def match_year(text):
    """Extract the most relevant year from claim text.
    Grabs the LAST year mentioned, since claims like
    '$1B in 2024 to $9B in 2025' should key to 2025, not 2024.
    """
    matches = re.findall(r'\b(20[2-3]\d)\b', text)
    return matches[-1] if matches else None

def infer_weight(claim):
    st = (claim.get("sourceType") or "").lower()
    if st in ("sworn-affidavit", "official", "leaked-internal"):
        return "authoritative"
    if st in ("reporting", "platform-data", "earnings-aggregation"):
        return "corroborating"
    return "indicative"


# Provenance tier ranks — higher number = stronger source, cannot be overwritten by lower
WEIGHT_RANK = {
    "authoritative": 3,  # sworn affidavit, official filing, CEO on own company
    "corroborating": 2,  # named primary source (Bloomberg, earnings call, The Information)
    "indicative": 1,     # podcast discussion, market colour, estimates
}


def check_provenance_guard(entity, prov_key, new_weight):
    """Check if existing provenance for this field has a stronger source.

    Returns (allowed, reason):
      - (True, None) if overwrite is allowed
      - (False, reason_str) if a higher-tier source already exists
    """
    prov = entity.get("provenance", {}).get(prov_key)
    if not prov or not prov.get("claims"):
        return True, None  # No existing data, safe to write

    new_rank = WEIGHT_RANK.get(new_weight, 0)

    # Find the strongest existing source
    best_existing_weight = None
    best_existing_source = None
    for existing in prov["claims"]:
        w = existing.get("weight", "indicative")
        if WEIGHT_RANK.get(w, 0) > WEIGHT_RANK.get(best_existing_weight, 0):
            best_existing_weight = w
            best_existing_source = existing.get("source", "unknown")

    best_rank = WEIGHT_RANK.get(best_existing_weight, 0)

    if new_rank < best_rank:
        return False, (
            f"BLOCKED: new source is '{new_weight}' (rank {new_rank}) "
            f"but existing has '{best_existing_weight}' (rank {best_rank}) "
            f"from {best_existing_source}. "
            f"Lower-tier source cannot overwrite higher-tier. "
            f"Claim added to provenance trail but value NOT updated."
        )

    return True, None


def apply_accepted(claim, vault_data, entities, schema):
    """Process an accepted claim: vault-data + entities + provenance."""

    # wq-043 §3.6: refuse to insert a duplicate of an existing dp-N whose
    # claim text is identical and was added in the last 7 days. Catches
    # re-submitted decisions files (e.g. dp-001 Cursor $2B ARR was added 4×
    # in 30min on 2026-04-29). Verbose log line so the audit trail shows
    # every guard fire — drop into apply_decisions.log to debug if needed.
    incoming_claim = (claim.get("claim") or "").strip()
    if incoming_claim:
        from datetime import timedelta
        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        for existing in vault_data.get("dataPoints", []):
            if (existing.get("claim") or "").strip() != incoming_claim:
                continue
            if (existing.get("dateAdded") or "") < seven_days_ago:
                continue
            log(
                f"  GUARD-DUP: refusing duplicate of {existing.get('id')} "
                f"(same claim text added {existing.get('dateAdded')}, "
                f"<7d ago); incoming={claim.get('id')!r} claim={incoming_claim[:80]!r}"
            )
            return existing.get("id")

    # 1. Add to vault-data.json — safe_str on every text field guards against
    #    mojibake leaking through from upstream (vault-inbox or decisions
    #    payload). See briefs/active/2026-04-26-mojibake-roundtrip-fix.md.
    dp_id = "dp-" + str(len(vault_data["dataPoints"]) + 1).zfill(3)
    data_point = {
        "id": dp_id,
        "claim": safe_str(claim.get("claim", "")),
        "value": claim.get("value"),
        "unit": claim.get("unit", ""),
        "sourceUrl": claim.get("sourceUrl", ""),
        "sourceType": claim.get("sourceType", ""),
        "sourceAuthor": safe_str(claim.get("sourceAuthor", "")),
        "confidence": claim.get("confidence", "estimated"),
        "dateOfClaim": claim.get("dateOfClaim", ""),
        "dateAdded": datetime.now().strftime("%Y-%m-%d"),
        "usedOn": claim.get("usedOn", []),
        "notes": safe_str(claim.get("notes", "")),
        "tags": claim.get("tags", []),
        "metricKey": claim.get("metricKey", ""),
        "status": "accepted",
        "source_id": claim.get("source_id"),
    }
    vault_data["dataPoints"].append(data_point)
    log(f"  VAULT: Added {dp_id}: {claim['claim'][:60]}")

    # 2. Classify to entity + field + year
    # wq-028 P1: try claim+tags first (legacy behavior). If no field rule
    # matches, fall back to metricKey alone. Concatenating metricKey into
    # the same search_text lets patterns like `infrastructure.*spend`
    # bridge across tag/metricKey boundaries (gpu_infrastructure + spend
    # = false-positive capex). Two-pass keeps multi-word rules intact for
    # claim text while still catching ~140 metricKey-only routings.
    search_text = (claim.get("claim", "") + " " + " ".join(claim.get("tags", []))).lower()
    metric_key_text = (claim.get("metricKey") or "").lower()
    entity_slug = match_entity(search_text, schema.get("entity_match_rules", []))
    field_id = match_field(search_text, schema.get("field_match_rules", []))
    if not field_id and metric_key_text:
        field_id = match_field(metric_key_text, schema.get("field_match_rules", []))
    year = match_year(search_text) or match_year(claim.get("dateOfClaim", ""))

    if entity_slug and field_id and claim.get("value") is not None:
        # Annualise monthly/quarterly values before storing
        value = claim["value"]
        unit = (claim.get("unit") or "").lower()
        claim_text = (claim.get("claim") or "").lower()

        annualised = False
        if isinstance(value, (int, float)):
            if "/month" in unit or "per month" in unit or "per month" in claim_text or "/month" in claim_text:
                value = value * 12
                annualised = True
                log(f"  ANNUALISE: {claim['value']} /month × 12 = {value} (annual)")
            elif "/quarter" in unit or "per quarter" in unit or "per quarter" in claim_text or "/quarter" in claim_text:
                value = value * 4
                annualised = True
                log(f"  ANNUALISE: {claim['value']} /quarter × 4 = {value} (annual)")

        # Find entity in entities.json
        entity = None
        for c in entities["companies"]:
            if c["slug"] == entity_slug:
                entity = c
                break

        if entity:
            # 3. Update entity financials — with provenance guard
            new_weight = infer_weight(claim)
            prov_key = f"{year}.{field_id}" if year else f"current.{field_id}"
            allowed, guard_reason = check_provenance_guard(entity, prov_key, new_weight)

            if allowed:
                if year:
                    if "financials" not in entity:
                        entity["financials"] = {}
                    if year not in entity["financials"]:
                        entity["financials"][year] = {}
                    entity["financials"][year][field_id] = value
                    log(f"  ENTITY: {entity['name']} → {year}.{field_id} = {value}" + (" (annualised)" if annualised else ""))
                else:
                    if "current" not in entity:
                        entity["current"] = {}
                    entity["current"][field_id] = value
                    log(f"  ENTITY: {entity['name']} → current.{field_id} = {claim['value']}")
            else:
                log(f"  GUARD: {entity['name']} → {prov_key}: {guard_reason}")

            # 4. Add provenance
            if "provenance" not in entity:
                entity["provenance"] = {}
            prov_key = f"{year}.{field_id}" if year else f"current.{field_id}"
            if prov_key not in entity["provenance"]:
                entity["provenance"][prov_key] = {"confidence": "medium", "claim_count": 0, "claims": []}

            prov = entity["provenance"][prov_key]
            prov["claims"].append({
                "id": dp_id,
                "claim": safe_str(claim["claim"][:120]) + (f" [annualised: {value}]" if annualised else ""),
                "value": value,
                "unit": "$B" if annualised else claim.get("unit", ""),
                "weight": infer_weight(claim),
                "confidence": claim.get("confidence", "estimated"),
                "source": safe_str(claim.get("sourceAuthor", "")),
                "source_url": claim.get("sourceUrl", ""),
                "date": claim.get("dateOfClaim", ""),
                "origin": "accepted",
                "role": "supports"
            })
            prov["claim_count"] = len(prov["claims"])
            prov["needs_source"] = False

            # Recalculate confidence
            weights = [c["weight"] for c in prov["claims"]]
            if "authoritative" in weights:
                prov["confidence"] = "high"
            elif weights.count("corroborating") >= 2:
                prov["confidence"] = "high"
            elif "corroborating" in weights:
                prov["confidence"] = "medium"
            else:
                prov["confidence"] = "low"

            log(f"  PROVENANCE: {entity['name']} → {prov_key}: {prov['confidence']} ({prov['claim_count']} sources)")

    return dp_id


def apply_declined(claim, vault_inbox):
    """Mark claim as declined in vault-inbox."""
    for item in vault_inbox.get("items", []):
        if item.get("id") == claim.get("id"):
            item["status"] = "declined"
            item["declined_at"] = datetime.now().strftime("%Y-%m-%d")
            item["declined_note"] = claim.get("note", "")
            log(f"  DECLINED: {claim['id']}: {claim.get('claim', '')[:60]}")
            return True
    return False


def apply_parked(claim, vault_inbox):
    """Mark claim as parked in vault-inbox."""
    for item in vault_inbox.get("items", []):
        if item.get("id") == claim.get("id"):
            item["status"] = "parked"
            item["parked_at"] = datetime.now().strftime("%Y-%m-%d")
            item["parked_note"] = claim.get("note", "")
            log(f"  PARKED: {claim['id']}: {claim.get('claim', '')[:60]}")
            return True
    return False


def apply_new_fields(approved_fields, schema):
    """Move approved proposed fields into the schema as real fields."""
    for field in approved_fields:
        field_id = field["field_id"]
        target_entity = field.get("proposed_for_entity", "")

        # Find which role this entity has
        target_role = None
        for role_name, role_def in schema.get("roles", {}).items():
            # Check if field_id makes sense for this role
            # Simple heuristic: add to all roles for now, can refine later
            if not target_role:
                target_role = role_name

        # For now, add to model_provider since most new fields come from there
        # In future, classify_claim.py could specify the role
        role_name = "model_provider"

        role_def = schema.get("roles", {}).get(role_name, {})
        if "fields" not in role_def:
            role_def["fields"] = {}

        role_def["fields"][field_id] = {
            "label": field.get("label", field_id),
            "unit": field.get("unit", ""),
            "type": "primary",
            "yearly": field.get("yearly", True),
            "description": field.get("description", ""),
        }
        log(f"  NEW FIELD: Added {field_id} to {role_name}: {field.get('label', '')}")

        # Add field_match_rule if regex provided
        if field.get("regex_pattern"):
            rules = schema.get("field_match_rules", [])
            # Check not already present
            if not any(r["field"] == field_id for r in rules):
                rules.append({
                    "pattern": field["regex_pattern"],
                    "field": field_id
                })
                log(f"  MATCH RULE: Added regex for {field_id}")

    # Remove approved/rejected from proposed_fields
    approved_ids = {f["field_id"] for f in approved_fields}
    schema["proposed_fields"] = [
        f for f in schema.get("proposed_fields", [])
        if f["field_id"] not in approved_ids
    ]


def replay_accepted(vault_inbox, vault_data, entities, schema, dry_run=False, only_ids=None):
    """wq-028 P1 replay: walk status=accepted inbox items, run the new
    matcher, and gap-fill entity fields that are currently empty.

    Skips items where the field is already populated to avoid duplicate
    provenance. Honours the provenance guard. Annotates new provenance
    entries with origin='wq-028-p1-replay' for traceability.

    If `only_ids` is provided (set/list of inbox IDs), processes only
    those items — used to whitelist a hand-picked subset after a dry-run
    review (e.g., to skip entity-misroute false positives surfaced by
    the dry-run).

    Does NOT touch vault-data.json — accepted items already have their
    dataPoints from prior apply_decisions runs. This only fills the
    entity-record gap that was silently missed under the old matcher.

    Returns (rescued, skipped_already_populated, skipped_no_match,
             skipped_no_value, skipped_no_entity, blocked_by_guard).
    """
    rescued = 0
    skipped_already = 0
    skipped_no_match = 0
    skipped_no_value = 0
    skipped_no_entity = 0
    blocked = 0

    only_ids_set = set(only_ids) if only_ids else None

    for item in vault_inbox.get("items", []):
        if item.get("status") != "accepted":
            continue
        if only_ids_set is not None and item.get("id") not in only_ids_set:
            continue

        # Two-pass match (mirrors apply_accepted §2)
        search_text = (item.get("claim", "") + " " + " ".join(item.get("tags", []))).lower()
        metric_key_text = (item.get("metricKey") or "").lower()
        entity_slug = match_entity(search_text, schema.get("entity_match_rules", []))
        field_id = match_field(search_text, schema.get("field_match_rules", []))
        if not field_id and metric_key_text:
            field_id = match_field(metric_key_text, schema.get("field_match_rules", []))
        year = match_year(search_text) or match_year(item.get("dateOfClaim", ""))

        if not (entity_slug and field_id):
            skipped_no_match += 1
            continue
        if item.get("value") is None:
            skipped_no_value += 1
            continue

        entity = next((c for c in entities.get("companies", []) if c.get("slug") == entity_slug), None)
        if not entity:
            skipped_no_entity += 1
            continue

        # Annualise (same logic as apply_accepted)
        value = item["value"]
        unit = (item.get("unit") or "").lower()
        claim_text = (item.get("claim") or "").lower()
        annualised = False
        if isinstance(value, (int, float)):
            if "/month" in unit or "per month" in unit or "per month" in claim_text or "/month" in claim_text:
                value = value * 12
                annualised = True
            elif "/quarter" in unit or "per quarter" in unit or "per quarter" in claim_text or "/quarter" in claim_text:
                value = value * 4
                annualised = True

        # Determine target path
        if year:
            existing = entity.get("financials", {}).get(year, {}).get(field_id)
            target_path = f"{year}.{field_id}"
        else:
            existing = entity.get("current", {}).get(field_id)
            target_path = f"current.{field_id}"

        # Gap-fill only — don't overwrite
        if existing is not None:
            skipped_already += 1
            continue

        # Provenance guard (defence-in-depth — should always pass for empty fields)
        new_weight = infer_weight(item)
        prov_key = f"{year}.{field_id}" if year else f"current.{field_id}"
        allowed, guard_reason = check_provenance_guard(entity, prov_key, new_weight)
        if not allowed:
            blocked += 1
            log(f"  GUARD: {entity['name']} → {prov_key}: {guard_reason}")
            continue

        # Populate
        if dry_run:
            log(f"  [DRY-RUN] REPLAY: {entity['name']} → {target_path} = {value}{' (annualised)' if annualised else ''} [from inbox.{item['id']}]")
        else:
            if year:
                entity.setdefault("financials", {}).setdefault(year, {})[field_id] = value
            else:
                entity.setdefault("current", {})[field_id] = value

            # Provenance trail
            if "provenance" not in entity:
                entity["provenance"] = {}
            if prov_key not in entity["provenance"]:
                entity["provenance"][prov_key] = {"confidence": "medium", "claim_count": 0, "claims": []}
            prov = entity["provenance"][prov_key]
            prov["claims"].append({
                "id": item.get("id"),
                "claim": safe_str(item.get("claim", ""))[:120] + (f" [annualised: {value}]" if annualised else ""),
                "value": value,
                "unit": "$B" if annualised else item.get("unit", ""),
                "weight": new_weight,
                "confidence": item.get("confidence", "estimated"),
                "source": safe_str(item.get("sourceAuthor", "")),
                "source_url": item.get("sourceUrl", ""),
                "date": item.get("dateOfClaim", ""),
                "origin": "wq-028-p1-replay",
                "role": "supports",
            })
            prov["claim_count"] = len(prov["claims"])
            weights = [c["weight"] for c in prov["claims"]]
            if "authoritative" in weights:
                prov["confidence"] = "high"
            elif weights.count("corroborating") >= 2:
                prov["confidence"] = "high"
            elif "corroborating" in weights:
                prov["confidence"] = "medium"
            else:
                prov["confidence"] = "low"
            log(f"  REPLAY: {entity['name']} → {target_path} = {value}{' (annualised)' if annualised else ''} [from inbox.{item['id']}]")

        rescued += 1

    return rescued, skipped_already, skipped_no_match, skipped_no_value, skipped_no_entity, blocked


def run_replay(dry_run=False, only_ids=None):
    """Top-level entry for --replay-accepted mode."""
    log(f"apply_decisions.py --replay-accepted (dry-run={dry_run}, only_ids={only_ids})")
    vault_data = load_json(VAULT_DATA)
    vault_inbox = load_json(VAULT_INBOX)
    entities = load_json(ENTITIES)
    schema = load_json(SCHEMA)

    rescued, skip_already, skip_no_match, skip_no_value, skip_no_entity, blocked = replay_accepted(
        vault_inbox, vault_data, entities, schema, dry_run=dry_run, only_ids=only_ids
    )

    log("")
    log(f"  Replay summary:")
    log(f"    Rescued (gap-filled):              {rescued}")
    log(f"    Skipped (field already populated): {skip_already}")
    log(f"    Skipped (no entity+field match):   {skip_no_match}")
    log(f"    Skipped (no value):                {skip_no_value}")
    log(f"    Skipped (entity not in entities):  {skip_no_entity}")
    log(f"    Blocked by provenance guard:       {blocked}")

    if not dry_run and rescued > 0:
        save_json(ENTITIES, entities)
        log(f"  Saved: entities.json")
        # Regenerate site-data.json from updated entities
        from generate_site_data import generate
        generate(ENTITIES, os.path.join(SITE_DIR, "site-data.json"), os.path.join(SITE_DIR, "site-data.json"))
        log(f"  Regenerated: site-data.json")
    elif dry_run:
        log(f"  [DRY-RUN] No files written.")


def main(decisions_path=None):
    with logged_run("apply_decisions.py") as outputs:
        _main_impl(decisions_path, outputs)


def _main_impl(decisions_path, outputs):
    # Find decisions file
    if not decisions_path:
        # Look for latest review-decisions-*.json in data-updates/
        updates_dir = os.path.join(SITE_DIR, "data-updates")
        if os.path.isdir(updates_dir):
            files = sorted([f for f in os.listdir(updates_dir) if f.startswith("review-decisions-")], reverse=True)
            if files:
                decisions_path = os.path.join(updates_dir, files[0])

    if not decisions_path or not os.path.exists(decisions_path):
        print("No decisions file found. Save review-decisions-*.json to beta/data-updates/")
        outputs["items_accepted"] = 0
        outputs["items_declined"] = 0
        outputs["items_parked"] = 0
        return

    log(f"apply_decisions.py — Processing {decisions_path}")

    decisions = load_json(decisions_path)
    vault_data = load_json(VAULT_DATA)
    vault_inbox = load_json(VAULT_INBOX)
    entities = load_json(ENTITIES)
    schema = load_json(SCHEMA)

    # Process accepted claims
    accepted = decisions.get("accepted", [])
    declined = decisions.get("declined", [])
    parked = decisions.get("parked", [])
    new_fields = decisions.get("new_fields_approved", [])
    rejected_fields = decisions.get("new_fields_rejected", [])

    log(f"  Accepted: {len(accepted)}, Declined: {len(declined)}, Parked: {len(parked)}, New fields: {len(new_fields)}")

    # Apply accepted
    for claim in accepted:
        dp_id = apply_accepted(claim, vault_data, entities, schema)
        # Also mark as accepted in inbox
        for item in vault_inbox.get("items", []):
            if item.get("id") == claim.get("id"):
                item["status"] = "accepted"
                item["accepted_as"] = dp_id
                break

    # Apply declined
    for claim in declined:
        apply_declined(claim, vault_inbox)

    # Apply parked
    for claim in parked:
        apply_parked(claim, vault_inbox)

    # Apply new fields
    if new_fields:
        apply_new_fields(new_fields, schema)

    # Remove rejected proposed fields
    if rejected_fields:
        schema["proposed_fields"] = [
            f for f in schema.get("proposed_fields", [])
            if f["field_id"] not in set(rejected_fields)
        ]
        log(f"  Removed {len(rejected_fields)} rejected field proposal(s)")

    # Save everything
    save_json(VAULT_DATA, vault_data)
    save_json(VAULT_INBOX, vault_inbox)
    save_json(ENTITIES, entities)
    save_json(SCHEMA, schema)
    log(f"  Saved: vault-data, vault-inbox, entities, metric-schema")

    # Archive the decisions file
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    archive_name = os.path.basename(decisions_path)
    shutil.move(decisions_path, os.path.join(ARCHIVE_DIR, archive_name))
    log(f"  Archived: {archive_name}")

    # Regenerate site-data.json
    log(f"  Regenerating site-data.json from entities.json...")
    from generate_site_data import generate
    generate(ENTITIES, os.path.join(SITE_DIR, "site-data.json"), os.path.join(SITE_DIR, "site-data.json"))

    log(f"  Done. {len(accepted)} accepted, {len(declined)} declined, {len(parked)} parked, {len(new_fields)} new fields.")

    outputs["items_accepted"] = len(accepted)
    outputs["items_declined"] = len(declined)
    outputs["items_parked"] = len(parked)
    outputs["new_fields_approved"] = len(new_fields)
    outputs["decisions_file"] = os.path.basename(decisions_path)


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--replay-accepted" in args:
        dry = "--dry-run" in args
        only_ids = None
        # --ids id1,id2,id3
        if "--ids" in args:
            i = args.index("--ids")
            if i + 1 < len(args):
                only_ids = [s.strip() for s in args[i + 1].split(",") if s.strip()]
        run_replay(dry_run=dry, only_ids=only_ids)
    else:
        path = args[0] if args and not args[0].startswith("--") else None
        main(path)
