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
TRIANGULATIONS_PENDING = os.path.join(ROOT_DIR, "data", "triangulations-pending.json")

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


# wq-054 — sub-period attribution. Extractors emit time_period_scope on every
# claim; we use it to decide which sub-field to write to instead of the annual
# default. Schema documented in metric-schema.json:field_patterns.
SUB_PERIOD_SCOPES = {"h1", "h2", "q1", "q2", "q3", "q4"}
EXIT_SCOPES = {"exit_snapshot"}
PEAK_SCOPES = {"monthly_peak"}
POINT_IN_TIME_SCOPES = {"point_in_time"}
ANNUAL_SCOPES = {"annual", "", None}

# Heuristic fallback when extractor didn't tag scope but the claim text
# contains an obvious period qualifier. Conservative — only fires for clear
# cases. Used in legacy claims via audit_period_attribution.py.
_PERIOD_QUALIFIER_PATTERNS = {
    "h1": [r"\bH1\b", r"first\s+half", r"jan(?:uary)?\s*[-–to]+\s*jun", r"上半年"],
    "h2": [r"\bH2\b", r"second\s+half", r"jul(?:y)?\s*[-–to]+\s*dec", r"下半年"],
    "q1": [r"\bQ1\b", r"first\s+quarter", r"jan-?mar"],
    "q2": [r"\bQ2\b", r"second\s+quarter", r"apr-?jun"],
    "q3": [r"\bQ3\b", r"third\s+quarter", r"jul-?sep"],
    "q4": [r"\bQ4\b", r"fourth\s+quarter", r"oct-?dec"],
    "exit_snapshot": [
        r"exit\s+arr", r"year[\-\s]?end\s+(?:run[\-\s]?rate|arr)",
        r"as\s+of\s+(?:dec|december)", r"best[\-\s]?(?:4|four)[\-\s]?week",
        r"december\s+annualis(?:ed|zed)",
    ],
    "monthly_peak": [
        r"monthly\s+peak", r"per\s+month\b", r"single\s+month\s+(?:peak|run[\-\s]?rate)",
        r"\$\d+(?:\.\d+)?[MB]?\s*\/\s*month",
    ],
    "point_in_time": [r"\bcurrent\b", r"as\s+of\s+today", r"as\s+of\s+now", r"this\s+week"],
}

_QUALIFIER_REGEXES = {
    scope: re.compile("|".join(patterns), re.IGNORECASE)
    for scope, patterns in _PERIOD_QUALIFIER_PATTERNS.items()
}


def detect_period_scope(text):
    """Best-effort scope detection from raw claim text.

    Returns (scope, qualifier_substring). Used as a fallback when an extractor
    didn't set time_period_scope, and by the audit backfill (wq-054 §4.4) to
    flag legacy claims that were silently routed to annual fields.

    Order of precedence: exit_snapshot / monthly_peak / quarterly / half-year
    / point_in_time. Matches more-specific qualifiers first.
    """
    if not text:
        return None, None
    # Order matters — match more specific scopes before generic ones
    for scope in ("exit_snapshot", "monthly_peak", "q1", "q2", "q3", "q4", "h1", "h2", "point_in_time"):
        m = _QUALIFIER_REGEXES[scope].search(text)
        if m:
            return scope, m.group(0)
    return None, None


def resolve_field_path(entity_slug, year, field_id, scope):
    """Pick the right entity-record path for a value, given the scope.

    Returns the dotted path components (financial_year_key, field_key) suitable
    for writing to entity['financials'][financial_year_key][field_key], OR
    ('current', field_key) for point-in-time scopes.

    Returns (None, None) when scope is unknown — caller should refuse routing.

    Examples (wq-054 §4.3):
      ('annual',        2025, 'collected_revenue') → ('2025', 'collected_revenue')
      ('h1',            2025, 'collected_revenue') → ('2025_h1', 'collected_revenue')
      ('q3',            2025, 'arr')               → ('2025_q3', 'arr')
      ('exit_snapshot', 2024, 'arr')               → ('2024', 'exit_arr')
      ('monthly_peak',  2026, 'arr')               → ('2026', 'monthly_peak_arr')
      ('point_in_time', None, 'employees')         → ('current', 'employees')
    """
    s = (scope or "").lower()
    if s in ANNUAL_SCOPES:
        if year:
            return str(year), field_id
        return "current", field_id
    if s in SUB_PERIOD_SCOPES:
        if not year:
            return None, None  # sub-period without a year is unroutable
        return f"{year}_{s}", field_id
    if s in EXIT_SCOPES:
        if not year:
            return None, None
        return str(year), f"exit_{field_id}"
    if s in PEAK_SCOPES:
        if not year:
            return None, None
        return str(year), f"monthly_peak_{field_id}"
    if s in POINT_IN_TIME_SCOPES:
        return "current", field_id
    return None, None  # unknown scope — refuse

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
    # wq-039 follow-on: include the inbox item's structured `entity` field
    # so claims like "databricks — 130 AI roles..." anchor on the entity
    # name even when the claim text is bare. Catches ~10–15 prior misses.
    search_text = (claim.get("claim", "") + " " + claim.get("entity", "") + " " + " ".join(claim.get("tags", []))).lower()
    metric_key_text = (claim.get("metricKey") or "").lower()
    entity_slug = match_entity(search_text, schema.get("entity_match_rules", []))
    field_id = match_field(search_text, schema.get("field_match_rules", []))
    if not field_id and metric_key_text:
        field_id = match_field(metric_key_text, schema.get("field_match_rules", []))
    year = match_year(search_text) or match_year(claim.get("dateOfClaim", ""))

    if entity_slug and field_id and claim.get("value") is not None:
        # wq-054 — pick scope from extractor; fall back to text heuristic, then
        # to "annual" so legacy callers without scope still route somewhere.
        scope = (claim.get("timePeriodScope") or claim.get("time_period_scope") or "").lower()
        period_qualifier = claim.get("periodQualifier") or claim.get("period_qualifier_detected")
        if not scope:
            inferred_scope, inferred_qual = detect_period_scope(
                (claim.get("claim") or "") + " " + (claim.get("notes") or "")
            )
            if inferred_scope:
                scope = inferred_scope
                period_qualifier = period_qualifier or inferred_qual
                log(f"  PERIOD: inferred scope={scope} from text qualifier '{inferred_qual}' (extractor didn't tag)")
            else:
                scope = "annual"

        # Annualise monthly/quarterly values before storing — but ONLY when the
        # claim is meant to represent an annual figure. Sub-period claims keep
        # their raw value (H1 stays half-year, monthly_peak stays one month).
        value = claim["value"]
        unit = (claim.get("unit") or "").lower()
        claim_text = (claim.get("claim") or "").lower()

        annualised = False
        if scope == "annual" and isinstance(value, (int, float)):
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
            # wq-054 — resolve final field path per scope. If unroutable
            # (sub-period claim with no year), refuse and log so audit can
            # surface it instead of silently dropping.
            year_key, field_key = resolve_field_path(entity_slug, year, field_id, scope)
            if year_key is None:
                log(f"  REFUSE: {entity['name']} → cannot route scope={scope} field={field_id} (year missing or scope unknown). Vault entry kept but entity not updated.")
                # Vault entry was already added above — return that id; entity record stays unchanged.
                return dp_id
            prov_key = f"{year_key}.{field_key}" if year_key != "current" else f"current.{field_key}"

            # 3. Update entity financials — with provenance guard
            new_weight = infer_weight(claim)
            allowed, guard_reason = check_provenance_guard(entity, prov_key, new_weight)

            if allowed:
                if year_key == "current":
                    if "current" not in entity:
                        entity["current"] = {}
                    entity["current"][field_key] = value
                    log(f"  ENTITY: {entity['name']} → current.{field_key} = {claim['value']} (scope={scope})")
                else:
                    if "financials" not in entity:
                        entity["financials"] = {}
                    if year_key not in entity["financials"]:
                        entity["financials"][year_key] = {}
                    entity["financials"][year_key][field_key] = value
                    log(f"  ENTITY: {entity['name']} → {year_key}.{field_key} = {value}"
                        + (" (annualised)" if annualised else "")
                        + f" (scope={scope}"
                        + (f", qual='{period_qualifier}'" if period_qualifier else "")
                        + ")")
            else:
                log(f"  GUARD: {entity['name']} → {prov_key}: {guard_reason}")

            # 4. Add provenance
            if "provenance" not in entity:
                entity["provenance"] = {}
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
                "role": "supports",
                # wq-054 — period scope on the trail so audit and downstream
                # consumers can tell H1 from full-year. Defaults to "annual".
                "time_period_scope": scope,
                "period_qualifier": period_qualifier,
            })
            prov["claim_count"] = len(prov["claims"])
            prov["needs_source"] = False

            # Recalculate confidence (wq-086 commit 4 — shared helper now
            # accounts for triangulation entries with fractional weights and
            # enforces the medium-tier cap on triangulation-only promotions).
            prov["confidence"] = compute_provenance_tier(prov["claims"])
            if compute_needs_review(prov["claims"]):
                prov["needs_review"] = True
            elif prov.get("needs_review") and not compute_needs_review(prov["claims"]):
                # Direct claim accepted on a previously needs_review field —
                # leave the flag (a reviewer should clear it intentionally).
                pass

            log(f"  PROVENANCE: {entity['name']} → {prov_key}: {prov['confidence']} ({prov['claim_count']} sources)")

            # wq-048 §3.5: when an `arr` field updates, re-derive
            # collected_revenue for that entity-year. Per brief §5 edge case:
            # only re-derive if the source claim's dateOfClaim is in Q4 of
            # the year being derived — earlier-quarter ARR snapshots are
            # mid-year leaks that would inflate the engine if treated as
            # year-end ARR.
            if field_id == "arr" and year:
                date_of_claim = (claim.get("dateOfClaim") or "").strip()
                in_q4 = (
                    date_of_claim.startswith(f"{year}-10")
                    or date_of_claim.startswith(f"{year}-11")
                    or date_of_claim.startswith(f"{year}-12")
                )
                if in_q4:
                    try:
                        # Lazy import — derive engine + config; no cost when
                        # field_id != arr or claim is not Q4.
                        sys.path.insert(0, SCRIPT_DIR)
                        from derive_collected_revenue import (
                            derive_collected_revenue,
                            load_config,
                            load_overrides,
                            resolve_with_override,
                        )
                        cfg = load_config()
                        overrides = load_overrides()
                        engine_block = derive_collected_revenue(entity, year, cfg)
                        if engine_block is not None:
                            resolved = resolve_with_override(
                                entity_slug, year, engine_block, overrides
                            )
                            new_cr = resolved["value"]
                            old_cr = (entity.get("financials") or {}).get(year, {}).get("collected_revenue")
                            entity.setdefault("financials", {}).setdefault(year, {})
                            entity["financials"][year]["collected_revenue"] = new_cr
                            cr_prov_key = f"{year}.collected_revenue"
                            prior_cr_prov = entity.get("provenance", {}).get(cr_prov_key)
                            if resolved["origin"] == "editorial_override":
                                from derive_collected_revenue import _override_provenance_block
                                cr_block = _override_provenance_block(resolved, engine_block)
                            else:
                                cr_block = engine_block
                            # Preserve prior provenance as superseded — same
                            # logic as backfill (--apply) so the trail is
                            # consistent however the field gets written.
                            if prior_cr_prov and prior_cr_prov.get("claims"):
                                today_str = datetime.now().strftime("%Y-%m-%d")
                                for prior in prior_cr_prov["claims"]:
                                    sup = dict(prior)
                                    sup["role"] = "superseded"
                                    sup["superseded_at"] = today_str
                                    sup["superseded_by"] = cr_block["claims"][0]["id"]
                                    cr_block["claims"].append(sup)
                            entity["provenance"][cr_prov_key] = cr_block
                            log(
                                f"  CONSENSUS: arr update triggered re-derivation "
                                f"of {entity['name']} {year}.collected_revenue: "
                                f"{old_cr} → {new_cr} (origin={resolved['origin']}, "
                                f"trigger_claim={dp_id})"
                            )
                    except Exception as exc:
                        log(f"  CONSENSUS: re-derivation failed for {entity['name']} {year}: {exc}")
                else:
                    log(
                        f"  CONSENSUS: arr update for {entity['name']} {year} skipped re-derivation "
                        f"(dateOfClaim={date_of_claim!r} not in Q4 of {year} per wq-048 §5 edge case)"
                    )

    return dp_id


# ─────────────────────────── triangulation routing ─────────────────────────
#
# Triangulations are claims that don't move a published number but contribute
# indirect evidence to one or more nodes in the flow model. Per
# dec-2026-05-05-triangulation-apply-semantics.md and wq-086 §3, they route
# via target_nodes paths (NOT entity_match_rules). The path strings follow the
# flow-model conventions emitted by curated_intake.py (build_revenue_flow /
# build_capex_flow):
#
#   market.<year>.<field>        → entities.market_aggregates[year][field]
#   sankey.buyers.<Segment>      → entities.market_aggregates[year].total_segment_<seg>
#   sankey.providers.<slug>      → entities.companies[slug].financials[year].arr
#   <slug>.<year>.<field>        → entities.companies[slug].financials[year][field]
#   <slug>.current.<field>       → entities.companies[slug].current[field]
#   capex.<bucket>.<key>         → entities.market_aggregates[year].<bucket>_capex
#
# Unknown paths (e.g. sankey.channels.*, sankey.outcomes.*) skip cleanly with
# a logged counter so audit can surface coverage gaps.

_BUYER_SEGMENT_NORMALISE = {
    "enterprise": "enterprise",
    "sme": "sme",
    "consumer": "consumer",
    "smb": "sme",  # tolerated alias
}

_CAPEX_BUCKET_TO_FIELD = {
    "mag7": "mag7_capex",
    "neocloud": "neocloud_capex",
    "neoclouds": "neocloud_capex",
    "sovereign": "sovereign_capex",
    "enterprise": "enterprise_capex",
}


def _claim_primary_year(claim):
    """Best-effort year for a triangulation claim.

    Reads claim.time_period first ("2025" or "2024-2025" → "2025"); falls
    back to dateOfClaim. Returns None if neither yields a 4-digit year. Used
    to fill the year slot for sankey.* paths that don't encode year directly.
    """
    for key in ("time_period", "timePeriod", "dateOfClaim"):
        v = claim.get(key)
        if not v:
            continue
        m = re.findall(r"\b(20[2-3]\d)\b", str(v))
        if m:
            return m[-1]
    return None


def resolve_target_node(path, claim_year=None):
    """Map a flow-model path to a (kind, slug, year, field) target.

    Returns a dict {kind, slug, year, field} or None if the path doesn't
    match a known shape. `kind` is "market" (entities.market_aggregates) or
    "entity" (entities.companies[slug]). Caller is responsible for the actual
    write — this helper only parses paths.
    """
    if not path or not isinstance(path, str):
        return None

    parts = path.split(".")

    # Bare slug — non-canonical path the LLM sometimes emits in place of
    # "<slug>.<year>.arr". Tolerated because the slug alone is unambiguous
    # and dropping these would lose ~half the Menlo 8 target attachments.
    if len(parts) == 1:
        slug = parts[0].lower()
        if not claim_year or not slug:
            return None
        return {"kind": "entity", "slug": slug, "year": claim_year, "field": "arr"}

    head = parts[0].lower()

    # market.<year>.<field>
    if head == "market" and len(parts) >= 3:
        year = parts[1]
        field = ".".join(parts[2:])
        return {"kind": "market", "slug": None, "year": year, "field": field}

    # sankey.buyers.<Segment>
    if head == "sankey" and len(parts) >= 3 and parts[1].lower() == "buyers":
        raw = ".".join(parts[2:]).strip()
        seg = _BUYER_SEGMENT_NORMALISE.get(raw.lower())
        if not seg or not claim_year:
            return None
        return {"kind": "market", "slug": None, "year": claim_year,
                "field": f"total_segment_{seg}"}

    # sankey.providers.<slug>
    if head == "sankey" and len(parts) >= 3 and parts[1].lower() == "providers":
        slug = ".".join(parts[2:]).lower()
        if not claim_year:
            return None
        return {"kind": "entity", "slug": slug, "year": claim_year, "field": "arr"}

    # sankey.channels.<label>, sankey.outcomes.<label>, sankey.totalVCSubsidy
    # are aggregate computed values without a stable provenance home.
    if head == "sankey":
        return None

    # capex.<bucket>.<key>
    if head == "capex" and len(parts) >= 2:
        bucket = parts[1].lower()
        field = _CAPEX_BUCKET_TO_FIELD.get(bucket)
        if not field or not claim_year:
            return None
        return {"kind": "market", "slug": None, "year": claim_year, "field": field}

    # <slug>.current.<field>
    if len(parts) >= 3 and parts[1].lower() == "current":
        return {"kind": "entity", "slug": parts[0].lower(), "year": "current",
                "field": ".".join(parts[2:])}

    # <slug>.<year>.<field>
    if len(parts) >= 3 and re.match(r"^\d{4}$", parts[1]):
        return {"kind": "entity", "slug": parts[0].lower(), "year": parts[1],
                "field": ".".join(parts[2:])}

    return None


def is_triangulation(claim):
    """Detect triangulation claims by comparison_type or dedup_status.

    Per dec-2026-05-05-triangulation-apply-semantics.md §3 and wq-086 §3.1,
    these route to the parallel apply_triangulation branch (target_nodes
    paths, not entity_match_rules) instead of falling through to apply_accepted.
    """
    return (
        claim.get("comparison_type") == "triangulates"
        or claim.get("dedup_status") == "triangulates"
    )


def apply_triangulation_softpark(claim, decision_id):
    """Park a triangulation accept until the full apply path lands.

    wq-086 commit 1. Writes the full claim payload + decision metadata to
    data/triangulations-pending.json so the full apply branch (commits 2-7)
    can drain and replay it with no signal loss. See resolution doc §4.
    """
    pending = []
    if os.path.exists(TRIANGULATIONS_PENDING):
        try:
            with open(TRIANGULATIONS_PENDING, encoding="utf-8") as f:
                pending = json.load(f)
        except (json.JSONDecodeError, OSError):
            pending = []
    if not isinstance(pending, list):
        pending = []

    target_nodes = (claim.get("triangulation") or {}).get("target_nodes", []) or []
    confidence_impact = (claim.get("triangulation") or {}).get("confidence_impact")
    accepted_impact = claim.get("accepted_confidence_impact") or confidence_impact

    pending.append({
        "decision_id": decision_id,
        "soft_parked_at": datetime.now().isoformat(),
        "claim": claim,
        "target_nodes": target_nodes,
        "confidence_impact": confidence_impact,
        "accepted_confidence_impact": accepted_impact,
    })

    os.makedirs(os.path.dirname(TRIANGULATIONS_PENDING), exist_ok=True)
    with open(TRIANGULATIONS_PENDING, "w", encoding="utf-8") as f:
        json.dump(pending, f, indent=2)

    log(
        f"  TRIANGULATION-SOFTPARK: parked decision={decision_id} "
        f"target_nodes={target_nodes} impact={accepted_impact}"
    )


# Per resolution doc §2 — fractional weights for triangulation contributions
# to the confidence-tier calc. Exposed at module scope so commit 4 (which
# updates _provenance_confidence in both apply_decisions.py AND
# curated_intake.py) can import the same constants and they stay in sync.
TRIANGULATION_WEIGHTS = {
    "strengthens": 0.5,
    "widens_range": 0.25,
    "weakens": -0.25,
}

# Triangulation-only tier promotion cap (resolution doc §2). Indirect
# evidence may lift low → medium but never medium → high.
TRIANGULATION_TIER_CAP = "medium"

# At least this many weakening triangulations against the same field set
# the needs_review flag (resolution doc §2 — does not downgrade tier).
WEAKENS_NEEDS_REVIEW_THRESHOLD = 2

# Triangulation contributions ≥ this score promote low → medium. 0.5 = one
# strengthens, two widens_range, or any equivalent combination.
TRIANGULATION_PROMOTION_THRESHOLD = 0.5


def compute_provenance_tier(claims):
    """Compute the confidence tier for a list of provenance entries.

    Direct (role == "supports") claims set the base tier:
      - any "authoritative" or ≥2 "corroborating" → "high"
      - 1 "corroborating" or ≥2 entries → "medium"
      - 1 "indicative"                  → "low"
      - none                            → "unsourced"

    Triangulation (role == "triangulates") claims contribute fractional
    weights (resolution doc §2):
      strengthens=+0.5, widens_range=+0.25, weakens=-0.25.
    A triangulation_score >= TRIANGULATION_PROMOTION_THRESHOLD on a "low"
    base tier promotes to "medium". Triangulations alone NEVER promote
    past TRIANGULATION_TIER_CAP — direct evidence is required for "high".

    Mirrored in scripts/curated_intake.py:_provenance_confidence so the
    flow-model context the curated intake builds reflects the same tiers
    apply_decisions.py writes.
    """
    if not claims:
        return "unsourced"

    direct_weights = [
        (c.get("weight") or "indicative")
        for c in claims if c.get("role") in (None, "supports")
    ]
    n_direct = len(direct_weights)
    n_strong = sum(1 for w in direct_weights if w in ("authoritative", "corroborating"))
    has_authoritative = any(w == "authoritative" for w in direct_weights)

    if has_authoritative or n_strong >= 2:
        base = "high"
    elif n_strong == 1 or n_direct >= 2:
        base = "medium"
    elif n_direct == 1:
        base = "low"
    else:
        base = "unsourced"

    triangulation_score = 0.0
    for c in claims:
        if c.get("role") != "triangulates":
            continue
        impact = c.get("confidence_impact")
        triangulation_score += TRIANGULATION_WEIGHTS.get(impact, 0.0)

    # Promotion via triangulations — capped at "medium".
    if base == "unsourced" and triangulation_score >= TRIANGULATION_PROMOTION_THRESHOLD:
        return TRIANGULATION_TIER_CAP
    if base == "low" and triangulation_score >= TRIANGULATION_PROMOTION_THRESHOLD:
        return TRIANGULATION_TIER_CAP

    return base


def compute_needs_review(claims):
    """≥2 weakening triangulations against the same field flag for review.

    Per resolution doc §2: weakening triangulations don't move tier on
    their own (asymmetric weights), but a *pattern* of weakens against
    the same field is editorially meaningful and should be surfaced in
    vault.html. This helper returns just the boolean — caller writes it
    onto the prov block as needs_review.
    """
    weakens = sum(
        1 for c in claims
        if c.get("role") == "triangulates"
        and c.get("confidence_impact") == "weakens"
    )
    return weakens >= WEAKENS_NEEDS_REVIEW_THRESHOLD


def _triangulation_prov_id(decision_id, target_node):
    """Idempotency key for a triangulation provenance entry.

    decision_id + target_node uniquely identifies one (claim, target) pair.
    Used by apply_triangulation to dedupe replays (soft-park then full
    apply, or duplicate decision file submissions). See edge cases §5.
    """
    safe_target = re.sub(r"[^A-Za-z0-9_.-]", "_", target_node)
    return f"tri:{decision_id}:{safe_target}"


def _ensure_market_field(entities, year, field):
    """Make sure entities.market_aggregates[year][field] exists.

    Per edge cases §5: if a target_node resolves to a field that doesn't
    exist yet, create it with null so the field exists for future direct
    claims to land on. Returns the prior value (or None if newly created).
    """
    market = entities.setdefault("market_aggregates", {})
    year_block = market.setdefault(year, {})
    existed = field in year_block
    if not existed:
        year_block[field] = None
    return existed


def _ensure_entity_field(entity, year, field):
    """Same as _ensure_market_field but for a company entity.

    For year == "current", writes to entity.current[field]. Otherwise
    entity.financials[year][field]. Returns whether the field already existed.
    """
    if year == "current":
        cur = entity.setdefault("current", {})
        existed = field in cur
        if not existed:
            cur[field] = None
        return existed
    fin = entity.setdefault("financials", {}).setdefault(year, {})
    existed = field in fin
    if not existed:
        fin[field] = None
    return existed


def apply_triangulation(claim, entities, decision_id=None):
    """Write triangulation provenance entries to entities.json.

    For each target_node in claim.triangulation.target_nodes:
      1. Resolve to (kind, slug, year, field) via resolve_target_node
      2. Ensure the field exists (create with null if missing — edge case §5)
      3. Append a role="triangulates" provenance entry
      4. Idempotent on (decision_id, target_node) — replays are safe

    Numbers are NEVER updated from triangulations (Option B per resolution
    doc §1). implied_value is preserved on the entry for future Option C
    work but ignored at apply time.

    Returns (written, skipped_unresolvable, skipped_no_target, skipped_duplicate,
             created_empty_fields).
    """
    decision_id = decision_id or claim.get("id") or "unknown"
    tri = claim.get("triangulation") or {}
    target_nodes = tri.get("target_nodes") or []
    if not target_nodes:
        log(f"  TRIANGULATION: decision={decision_id} has empty target_nodes — skipped")
        return 0, 0, 1, 0, 0

    # Reviewer override > model classification (per resolution doc §2 / brief §3.5)
    model_impact = tri.get("confidence_impact")
    accepted_impact = claim.get("accepted_confidence_impact") or model_impact
    if accepted_impact and accepted_impact not in TRIANGULATION_WEIGHTS:
        log(f"  TRIANGULATION: decision={decision_id} unknown confidence_impact "
            f"{accepted_impact!r} — defaulting to widens_range")
        accepted_impact = "widens_range"
    overrode = (
        model_impact is not None
        and accepted_impact is not None
        and accepted_impact != model_impact
    )

    derivation = tri.get("derivation", "")
    implied_value = tri.get("implied_value")
    claim_year = _claim_primary_year(claim)

    written = 0
    skipped_unresolvable = 0
    skipped_duplicate = 0
    created_fields = 0

    for target_node in target_nodes:
        resolved = resolve_target_node(target_node, claim_year=claim_year)
        if not resolved:
            log(f"  TRIANGULATION-SKIP: decision={decision_id} target={target_node!r} "
                f"(unresolved path — see resolve_target_node)")
            skipped_unresolvable += 1
            continue

        kind = resolved["kind"]
        year = resolved["year"]
        field = resolved["field"]
        slug = resolved.get("slug")

        if kind == "market":
            existed = _ensure_market_field(entities, year, field)
            entity_label = "market_aggregates"
            host = entities.setdefault("market_aggregates", {}).setdefault(year, {})
            prov_root = entities["market_aggregates"]
        else:
            entity = next(
                (c for c in entities.get("companies", []) if c.get("slug") == slug),
                None,
            )
            if not entity:
                log(f"  TRIANGULATION-SKIP: decision={decision_id} target={target_node!r} "
                    f"slug={slug!r} not in entities.companies")
                skipped_unresolvable += 1
                continue
            existed = _ensure_entity_field(entity, year, field)
            entity_label = entity.get("name") or slug
            host = entity
            prov_root = entity

        prov_root.setdefault("provenance", {})
        prov_key = (
            f"current.{field}" if year == "current" else f"{year}.{field}"
        )
        prov_block = prov_root["provenance"].setdefault(
            prov_key,
            {"confidence": "unsourced", "claim_count": 0, "claims": []},
        )

        prov_id = _triangulation_prov_id(decision_id, target_node)
        if any(c.get("id") == prov_id for c in prov_block["claims"]):
            log(f"  TRIANGULATION-DUP: {entity_label} {prov_key} already has {prov_id}")
            skipped_duplicate += 1
            continue

        entry = {
            "id": prov_id,
            "claim": safe_str(claim.get("claim", ""))[:160],
            "value": None,  # triangulations don't move numbers
            "unit": claim.get("unit", ""),
            "weight": "indicative",
            "confidence": claim.get("confidence", "estimated"),
            "source": safe_str(claim.get("speaker") or claim.get("sourceAuthor") or ""),
            "source_url": claim.get("source_url") or claim.get("sourceUrl", ""),
            "date": claim.get("dateOfClaim") or claim.get("extracted_at", ""),
            "origin": "triangulation",
            "role": "triangulates",
            "confidence_impact": accepted_impact,
            "derivation": safe_str(derivation),
            "target_node": target_node,
            "implied_value": implied_value,
            "decision_id": decision_id,
        }
        if overrode:
            entry["model_classified_as"] = model_impact
        prov_block["claims"].append(entry)
        prov_block["claim_count"] = len(prov_block["claims"])

        # Recalculate tier + needs_review with the shared helper. Per
        # resolution doc §2 — single weakens never moves tier on its own,
        # but ≥2 weakens against the same field flag for review.
        prior_tier = prov_block.get("confidence")
        new_tier = compute_provenance_tier(prov_block["claims"])
        prov_block["confidence"] = new_tier
        if compute_needs_review(prov_block["claims"]):
            prov_block["needs_review"] = True
        if prior_tier and prior_tier != new_tier:
            log(f"  TIER-MOVE: {entity_label} {prov_key} {prior_tier} → {new_tier}")

        if not existed:
            created_fields += 1
            log(f"  TRIANGULATION-CREATED-EMPTY-FIELD: {entity_label} {prov_key} (was absent)")
        log(f"  TRIANGULATION: {entity_label} → {prov_key} role=triangulates "
            f"impact={accepted_impact}{' (overrode model='+model_impact+')' if overrode else ''}"
            f" target={target_node}")
        written += 1

    return written, skipped_unresolvable, 1 if not target_nodes else 0, skipped_duplicate, created_fields


def replay_triangulations_pending(entities):
    """Drain data/triangulations-pending.json through apply_triangulation.

    Called on every apply_decisions.py run so that any soft-parked entry
    (commit 1) gets applied as soon as the apply path is available. After a
    successful drain (zero failures) the pending file is renamed to
    .replayed-<ts>.bak. If any entries fail (e.g. unresolvable target_node),
    those entries remain in a residual data/triangulations-pending.json so
    the next run can retry them — successful entries are still removed from
    the residual file.

    Returns (drained, residual_kept, total_provs_written) for the run summary.
    """
    if not os.path.exists(TRIANGULATIONS_PENDING):
        return 0, 0, 0

    try:
        with open(TRIANGULATIONS_PENDING, encoding="utf-8") as f:
            pending = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        log(f"  TRIANGULATION-REPLAY: cannot read {TRIANGULATIONS_PENDING}: {exc}")
        return 0, 0, 0

    if not isinstance(pending, list) or not pending:
        # Empty list or wrong shape — clean up the empty file.
        try:
            os.remove(TRIANGULATIONS_PENDING)
        except OSError:
            pass
        return 0, 0, 0

    log(f"  TRIANGULATION-REPLAY: draining {len(pending)} pending entr(ies) "
        f"from {os.path.basename(TRIANGULATIONS_PENDING)}")

    drained = 0
    residual = []
    total_written = 0
    for entry in pending:
        claim = entry.get("claim") or {}
        decision_id = entry.get("decision_id") or claim.get("id") or "unknown"
        # Carry the reviewer's accepted impact (if recorded at soft-park time)
        # back into the claim payload so apply_triangulation reads it first.
        if entry.get("accepted_confidence_impact") and not claim.get("accepted_confidence_impact"):
            claim["accepted_confidence_impact"] = entry["accepted_confidence_impact"]
        written, skip_unres, skip_no_t, skip_dup, _created = apply_triangulation(
            claim, entities, decision_id=decision_id
        )
        total_written += written
        # Drain rule: if every target_node either wrote or was a duplicate
        # (i.e. nothing unresolvable AND there were targets), the entry is
        # complete. Unresolvable targets should be retried on the next run
        # — they may correspond to new entity slugs added since soft-park.
        if skip_no_t == 0 and skip_unres == 0:
            drained += 1
        else:
            residual.append(entry)

    if residual:
        # Some entries had unresolvable paths — keep them for next run.
        with open(TRIANGULATIONS_PENDING, "w", encoding="utf-8") as f:
            json.dump(residual, f, indent=2)
        log(f"  TRIANGULATION-REPLAY: {drained} drained, {len(residual)} kept "
            f"in residual pending file (unresolvable target_nodes)")
    else:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        bak_path = f"{TRIANGULATIONS_PENDING}.replayed-{ts}.bak"
        try:
            shutil.move(TRIANGULATIONS_PENDING, bak_path)
            log(f"  TRIANGULATION-REPLAY: drained all {drained} entr(ies); "
                f"moved pending file → {os.path.basename(bak_path)}")
        except OSError as exc:
            log(f"  TRIANGULATION-REPLAY: drained {drained} but failed to "
                f"archive pending file: {exc}")

    return drained, len(residual), total_written


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
        # wq-039 follow-on: include the inbox item's structured `entity` field
        search_text = (item.get("claim", "") + " " + item.get("entity", "") + " " + " ".join(item.get("tags", []))).lower()
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
            prov["confidence"] = compute_provenance_tier(prov["claims"])
            if compute_needs_review(prov["claims"]):
                prov["needs_review"] = True
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

    # wq-086 commit 7 — even with no decisions file, drain any soft-parked
    # triangulations. This makes scripts/apply_decisions.py the single drain
    # point for triangulations-pending.json regardless of whether there's a
    # fresh review batch.
    if not decisions_path or not os.path.exists(decisions_path):
        if os.path.exists(TRIANGULATIONS_PENDING):
            log("apply_decisions.py — no decisions file; draining triangulations-pending only")
            entities_only = load_json(ENTITIES)
            drained, residual, prov_writes = replay_triangulations_pending(entities_only)
            if drained > 0 or prov_writes > 0:
                save_json(ENTITIES, entities_only)
                log(f"  Saved entities.json ({drained} triangulations drained, "
                    f"{prov_writes} provenance entries written)")
                from generate_site_data import generate
                generate(ENTITIES, os.path.join(SITE_DIR, "site-data.json"),
                         os.path.join(SITE_DIR, "site-data.json"))
                log("  Regenerated: site-data.json")
            outputs["items_accepted"] = 0
            outputs["items_declined"] = 0
            outputs["items_parked"] = 0
            outputs["triangulations_drained"] = drained
            outputs["triangulation_prov_entries"] = prov_writes
            return

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
    softparked = 0
    for claim in accepted:
        # wq-086 commit 1 — triangulations route to a separate pending file.
        # The existing entity_match_rules pipeline silently drops them
        # (entity = "Enterprise Generative AI Market" never matches a slug),
        # so we intercept BEFORE apply_accepted to preserve the accept signal.
        if is_triangulation(claim):
            apply_triangulation_softpark(claim, claim.get("id"))
            softparked += 1
            for item in vault_inbox.get("items", []):
                if item.get("id") == claim.get("id"):
                    item["status"] = "triangulation_pending"
                    item["soft_parked_at"] = datetime.now().strftime("%Y-%m-%d")
                    break
            continue

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

    # wq-086 commit 7 — drain triangulations-pending.json. Includes any
    # entries soft-parked above in this same run, plus any older pending
    # entries from prior runs. Successful drains move the file to a .bak;
    # entries with unresolvable target_nodes stay in residual for retry.
    drained, residual, prov_writes = replay_triangulations_pending(entities)

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

    log(
        f"  Done. {len(accepted) - softparked} accepted "
        f"({softparked} softparked as triangulations, "
        f"{drained} drained → {prov_writes} prov entries), "
        f"{len(declined)} declined, {len(parked)} parked, "
        f"{len(new_fields)} new fields."
    )

    outputs["items_accepted"] = len(accepted) - softparked
    outputs["items_declined"] = len(declined)
    outputs["items_parked"] = len(parked)
    outputs["new_fields_approved"] = len(new_fields)
    outputs["triangulations_softparked"] = softparked
    outputs["triangulations_drained"] = drained
    outputs["triangulation_prov_entries"] = prov_writes
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
