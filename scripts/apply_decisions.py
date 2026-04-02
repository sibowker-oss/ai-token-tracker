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
BETA_DIR = os.path.join(ROOT_DIR, "beta")

VAULT_DATA = os.path.join(BETA_DIR, "vault-data.json")
VAULT_INBOX = os.path.join(BETA_DIR, "vault-inbox.json")
ENTITIES = os.path.join(BETA_DIR, "entities.json")
SCHEMA = os.path.join(BETA_DIR, "metric-schema.json")
ARCHIVE_DIR = os.path.join(BETA_DIR, "data-updates", "archive")
LOG_FILE = os.path.join(ROOT_DIR, "data", "apply_decisions.log")

def load_json(path):
    with open(path) as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def match_entity(text, rules):
    for rule in rules:
        if re.search(rule["pattern"], text, re.I):
            return rule["slug"]
    return None

def match_field(text, rules):
    for rule in rules:
        if re.search(rule["pattern"], text, re.I):
            return rule["field"]
    return None

def match_year(text):
    m = re.search(r'\b(20[2-3]\d)\b', text)
    return m.group(1) if m else None

def infer_weight(claim):
    st = (claim.get("sourceType") or "").lower()
    if st in ("sworn-affidavit", "official", "leaked-internal"):
        return "authoritative"
    if st in ("reporting", "platform-data", "earnings-aggregation"):
        return "corroborating"
    return "indicative"


def apply_accepted(claim, vault_data, entities, schema):
    """Process an accepted claim: vault-data + entities + provenance."""

    # 1. Add to vault-data.json
    dp_id = "dp-" + str(len(vault_data["dataPoints"]) + 1).zfill(3)
    data_point = {
        "id": dp_id,
        "claim": claim.get("claim", ""),
        "value": claim.get("value"),
        "unit": claim.get("unit", ""),
        "sourceUrl": claim.get("sourceUrl", ""),
        "sourceType": claim.get("sourceType", ""),
        "sourceAuthor": claim.get("sourceAuthor", ""),
        "confidence": claim.get("confidence", "estimated"),
        "dateOfClaim": claim.get("dateOfClaim", ""),
        "dateAdded": datetime.now().strftime("%Y-%m-%d"),
        "usedOn": claim.get("usedOn", []),
        "notes": claim.get("notes", ""),
        "tags": claim.get("tags", []),
        "metricKey": claim.get("metricKey", ""),
        "status": "accepted",
        "source_id": claim.get("source_id"),
    }
    vault_data["dataPoints"].append(data_point)
    log(f"  VAULT: Added {dp_id}: {claim['claim'][:60]}")

    # 2. Classify to entity + field + year
    search_text = (claim.get("claim", "") + " " + " ".join(claim.get("tags", []))).lower()
    entity_slug = match_entity(search_text, schema.get("entity_match_rules", []))
    field_id = match_field(search_text, schema.get("field_match_rules", []))
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
            # 3. Update entity financials
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

            # 4. Add provenance
            if "provenance" not in entity:
                entity["provenance"] = {}
            prov_key = f"{year}.{field_id}" if year else f"current.{field_id}"
            if prov_key not in entity["provenance"]:
                entity["provenance"][prov_key] = {"confidence": "medium", "claim_count": 0, "claims": []}

            prov = entity["provenance"][prov_key]
            prov["claims"].append({
                "id": dp_id,
                "claim": claim["claim"][:120] + (f" [annualised: {value}]" if annualised else ""),
                "value": value,
                "unit": "$B" if annualised else claim.get("unit", ""),
                "weight": infer_weight(claim),
                "confidence": claim.get("confidence", "estimated"),
                "source": claim.get("sourceAuthor", ""),
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


def main(decisions_path=None):
    # Find decisions file
    if not decisions_path:
        # Look for latest review-decisions-*.json in data-updates/
        updates_dir = os.path.join(BETA_DIR, "data-updates")
        if os.path.isdir(updates_dir):
            files = sorted([f for f in os.listdir(updates_dir) if f.startswith("review-decisions-")], reverse=True)
            if files:
                decisions_path = os.path.join(updates_dir, files[0])

    if not decisions_path or not os.path.exists(decisions_path):
        print("No decisions file found. Save review-decisions-*.json to beta/data-updates/")
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
    generate(ENTITIES, os.path.join(BETA_DIR, "site-data.json"), os.path.join(BETA_DIR, "site-data.json"))

    log(f"  Done. {len(accepted)} accepted, {len(declined)} declined, {len(parked)} parked, {len(new_fields)} new fields.")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    main(path)
