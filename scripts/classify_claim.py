#!/usr/bin/env python3
"""
classify_claim.py — Classify a claim to entity + field + year.

Uses regex rules from metric-schema.json first. If entity matches but
field doesn't, calls Claude to propose a new field definition.

Can be used standalone (CLI) or imported by other scripts.

Usage:
  python3 scripts/classify_claim.py "OpenAI burn rate hit $25B in 2026"
  python3 scripts/classify_claim.py --batch vault-inbox.json
"""

import json, re, sys, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
BETA_DIR = os.path.join(ROOT_DIR, "beta")

def load_json(path):
    with open(path) as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

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

def classify_with_rules(claim_text, tags, schema):
    """Try regex rules first. Returns (entity_slug, field_id, year) or partial match."""
    search_text = (claim_text + " " + " ".join(tags)).lower()

    entity_slug = match_entity(search_text, schema.get("entity_match_rules", []))
    field_id = match_field(search_text, schema.get("field_match_rules", []))
    year = match_year(search_text)

    return entity_slug, field_id, year

def classify_with_claude(claim_text, entity_slug, existing_fields, api_key):
    """Call Claude to propose a field classification for an unmatched claim."""
    import urllib.request

    field_list = "\n".join(f"  - {fid}: {fdef.get('label', fid)} ({fdef.get('unit', '?')}) — {fdef.get('description', '')}"
                          for fid, fdef in existing_fields.items())

    prompt = f"""You are a data schema classifier for an AI industry intelligence platform.

A claim has been matched to entity "{entity_slug}" but no existing field matches it.

CLAIM: "{claim_text}"

EXISTING FIELDS for this entity type:
{field_list}

Your job:
1. If this claim DOES match one of the existing fields above (just worded differently), return the existing field ID.
2. If this is genuinely a NEW metric we don't track, propose a new field.

Return ONLY valid JSON (no markdown, no explanation):

If existing field matches:
{{"match": "existing", "field_id": "<existing_field_id>"}}

If new field needed:
{{"match": "new", "field_id": "<snake_case_id>", "label": "<Human Label>", "unit": "<$B|%|count|string|ratio|months|etc>", "yearly": true, "description": "<one line description>", "regex_pattern": "<regex to match similar claims in future>"}}
"""

    body = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 300,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }
    )

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            text = result["content"][0]["text"].strip()
            # Parse JSON from response (handle markdown wrapping)
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text.strip())
    except Exception as e:
        print(f"  Claude API error: {e}", file=sys.stderr)
        return None

def get_fields_for_entity(entity_slug, entities, schema):
    """Get the field definitions applicable to an entity."""
    entity = None
    for c in entities.get("companies", []):
        if c["slug"] == entity_slug:
            entity = c
            break
    if not entity:
        return {}

    all_fields = {}
    for role in entity.get("roles", []):
        role_def = schema.get("roles", {}).get(role, {})
        all_fields.update(role_def.get("fields", {}))
    return all_fields

def classify_claim(claim, entities, schema, api_key=None):
    """
    Full classification pipeline for a single claim.

    Returns dict:
      entity_slug, field_id, year, is_new_field, proposed_field (if new)
    """
    text = claim.get("claim", "")
    tags = claim.get("tags", [])

    entity_slug, field_id, year = classify_with_rules(text, tags, schema)

    result = {
        "entity_slug": entity_slug,
        "field_id": field_id,
        "year": year or match_year(claim.get("dateOfClaim", "")),
        "is_new_field": False,
        "proposed_field": None,
        "classification": "full" if (entity_slug and field_id) else ("entity_only" if entity_slug else "unmatched")
    }

    # If entity matched but field didn't, try Claude
    if entity_slug and not field_id and api_key:
        existing_fields = get_fields_for_entity(entity_slug, entities, schema)
        claude_result = classify_with_claude(text, entity_slug, existing_fields, api_key)

        if claude_result:
            if claude_result.get("match") == "existing":
                result["field_id"] = claude_result["field_id"]
                result["classification"] = "full"
            elif claude_result.get("match") == "new":
                result["field_id"] = claude_result["field_id"]
                result["is_new_field"] = True
                result["classification"] = "new_field"
                result["proposed_field"] = {
                    "field_id": claude_result["field_id"],
                    "label": claude_result.get("label", claude_result["field_id"]),
                    "unit": claude_result.get("unit", ""),
                    "type": "primary",
                    "yearly": claude_result.get("yearly", True),
                    "description": claude_result.get("description", ""),
                    "regex_pattern": claude_result.get("regex_pattern", ""),
                    "status": "proposed",
                    "proposed_from_claim": claim.get("id", ""),
                    "proposed_for_entity": entity_slug
                }

    return result

def process_batch(inbox_path, entities_path, schema_path, api_key=None):
    """Classify all pending claims in vault-inbox.json."""
    inbox = load_json(inbox_path)
    entities = load_json(entities_path)
    schema = load_json(schema_path)

    results = {"full": 0, "entity_only": 0, "new_field": 0, "unmatched": 0}
    new_fields = []

    for item in inbox.get("items", []):
        if item.get("status") != "pending":
            continue

        r = classify_claim(item, entities, schema, api_key)
        results[r["classification"]] += 1

        if r["is_new_field"] and r["proposed_field"]:
            new_fields.append(r["proposed_field"])
            print(f"  NEW FIELD: {r['proposed_field']['field_id']} ({r['proposed_field']['label']}) — from: {item['claim'][:60]}")
        elif r["classification"] == "entity_only":
            print(f"  NO FIELD:  {r['entity_slug']} — {item['claim'][:60]}")

    # Save proposed fields to schema
    if new_fields:
        # Deduplicate by field_id
        existing_proposed = {f["field_id"] for f in schema.get("proposed_fields", [])}
        new_unique = [f for f in new_fields if f["field_id"] not in existing_proposed]
        schema.setdefault("proposed_fields", []).extend(new_unique)
        save_json(schema_path, schema)
        print(f"\n  {len(new_unique)} new field(s) proposed and saved to metric-schema.json")

    return results, new_fields

# ── CLI ──
if __name__ == "__main__":
    entities_path = os.path.join(BETA_DIR, "entities.json")
    schema_path = os.path.join(BETA_DIR, "metric-schema.json")

    # Get API key
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        # Try to read from common locations
        for key_file in [os.path.expanduser("~/.anthropic_api_key"), os.path.join(ROOT_DIR, ".env")]:
            if os.path.exists(key_file):
                with open(key_file) as f:
                    content = f.read().strip()
                    if content.startswith("sk-ant-"):
                        api_key = content
                    elif "ANTHROPIC_API_KEY" in content:
                        for line in content.split("\n"):
                            if line.startswith("ANTHROPIC_API_KEY="):
                                api_key = line.split("=", 1)[1].strip().strip('"\'')
                break

    if len(sys.argv) > 1 and sys.argv[1] == "--batch":
        inbox_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(BETA_DIR, "vault-inbox.json")
        print(f"classify_claim.py — batch mode")
        print(f"  Inbox: {inbox_path}")
        print(f"  API key: {'set' if api_key else 'NOT SET (field discovery disabled)'}")
        results, new_fields = process_batch(inbox_path, entities_path, schema_path, api_key)
        print(f"\nResults: {results}")

    elif len(sys.argv) > 1:
        claim_text = " ".join(sys.argv[1:])
        entities = load_json(entities_path)
        schema = load_json(schema_path)

        claim = {"claim": claim_text, "tags": [], "id": "cli-test"}
        result = classify_claim(claim, entities, schema, api_key)

        print(json.dumps(result, indent=2))

    else:
        print("Usage:")
        print("  python3 scripts/classify_claim.py 'OpenAI burn rate hit $25B'")
        print("  python3 scripts/classify_claim.py --batch beta/vault-inbox.json")
        print("")
        print("Set ANTHROPIC_API_KEY env var for field discovery via Claude.")
