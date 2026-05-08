"""Shared helpers for apply_handlers — entity resolution, tier/conflict logic.

The handler `ctx` is a `PipelineContext` (see `scripts/apply_pipeline.py`)
exposing:
    ctx.entities          dict — entities.json
    ctx.schema            dict — metric-schema.json
    ctx.dry_run           bool
    ctx.tier(claim)       -> "tier_1A" | ... | "tier_3B"
    ctx.log(level, msg)
    ctx.skip(claim, reason)
    ctx.audit(category, row)

Handler functions return a `HandlerResult` dataclass — apply_pipeline applies
the diff (or, if dry_run, accumulates it for reporting).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


# Tier rank: higher number = stronger source. Mirrors the apply_decisions
# WEIGHT_RANK ladder but extended to the tier_1A..tier_3B ladder used on
# rendered pages (compute_disclosures, computeProviders, etc).
TIER_RANK = {
    "tier_1A": 6,
    "tier_1B": 5,
    "tier_2A": 4,
    "tier_2B": 3,
    "tier_3A": 2,
    "tier_3B": 1,
    None: 0,
}


# Multi-tier companies that REQUIRE a tier-record entity slug per D12.
# A claim whose `entity` field resolves to one of these (without specifying
# the tier) is sent to the audit doc with reason "multi-tier ambiguous".
MULTI_TIER_AMBIGUOUS = {
    "google": ("google_workspace_ai", "google_cloud", "gcp"),
    "microsoft": ("m365_copilot", "github_copilot", "azure", "msft_ai"),
    "oracle": ("oracle_fusion_ai", "oci"),
    "amazon": ("aws", "alexa"),
}


# Aliases for entity slugs whose canonical entities.json slug differs from
# how vault claims reference them. Keyed by lowercase short name; value is
# the entities.json slug.
SLUG_ALIASES = {
    "cursor": "cursor-(anysphere)",
    "anysphere": "cursor-(anysphere)",
    "openai": "openai",
    "anthropic": "anthropic",
    "perplexity": "perplexity",
    "chatgpt": "openai",
    "claude": "anthropic",
    "gemini": "google",
    "github copilot": "github-copilot",
    "copilot": "github-copilot",
    "midjourney": "midjourney",
    "character.ai": "character-ai",
    "character ai": "character-ai",
    "harvey": "harvey",
    "replit": "replit",
    "notion": "notion",
    "figma": "figma",
    "canva": "canva",
}


@dataclass
class FieldWrite:
    """One scalar write into entities.json — current.<field> or financials[year].<field>."""

    entity_slug: str
    year_key: str  # "current" or "2026" or "2026_q1" etc.
    field_key: str
    value: Any
    unit: str
    prov_entry: dict
    label: str  # human-readable for logs


@dataclass
class HandlerResult:
    """What a handler decided to do for a claim.

    `applied` — True if at least one write was queued; False = skipped.
    `writes` — list of FieldWrite. Idempotent-deduped before commit.
    `consumer_keys` — usedOn keys to append to vault dataPoint.usedOn.
    `audit_rows` — rows to add to data/audits/wq-098-skipped-claims.md.
    `skip_reason` — if applied=False, short string for log + audit.
    """

    applied: bool = False
    writes: list = field(default_factory=list)
    consumer_keys: list = field(default_factory=list)
    audit_rows: list = field(default_factory=list)
    skip_reason: str = ""


def derive_tier(claim) -> str:
    """Map (sourceType, confidence) to a tier_1A..tier_3B label.

    Vault doesn't carry an explicit tier; we derive it from sourceType +
    confidence per the wq-098 D2 ladder. Aligns with the editorial tier
    naming used by wq-096 emit (`tier_1b`, `tier_2a`, etc.) but UPPERCASE
    in code so we can compare numerically via TIER_RANK.
    """
    st = (claim.get("sourceType") or "").lower()
    conf = (claim.get("confidence") or "").lower()

    if st == "sworn-affidavit":
        return "tier_1A"
    if st in ("official", "sec_filing"):
        return "tier_1B"
    if st in ("leaked-internal", "earnings-aggregation"):
        return "tier_1B" if conf == "verified" else "tier_2A"
    if st in ("reporting", "newsletter"):
        return "tier_2A" if conf == "verified" else "tier_2B"
    if st == "platform-data":
        return "tier_2A" if conf == "verified" else "tier_2B"
    if st == "ats_api":
        return "tier_2B"
    if st == "web_page":
        return "tier_2A" if conf == "verified" else "tier_3A"
    if st in ("podcast", "podcast_discussion"):
        return "tier_3A"
    if st in ("calculation", "observation", "estimate"):
        return "tier_2B" if conf == "verified" else "tier_3A"
    return "tier_3B"


def is_auto_apply(claim) -> bool:
    """D2: verified confidence AND tier_1A/1B/2A auto-apply."""
    if (claim.get("confidence") or "").lower() != "verified":
        return False
    return derive_tier(claim) in ("tier_1A", "tier_1B", "tier_2A")


def normalise_year(claim) -> str | None:
    """Best-effort year string from claim.dateOfClaim or claim text.

    Returns 4-digit year as string (e.g. "2026") or None.
    """
    for key in ("dateOfClaim", "claim", "notes", "tags"):
        v = claim.get(key)
        if not v:
            continue
        if isinstance(v, list):
            text = " ".join(str(x) for x in v)
        else:
            text = str(v)
        m = re.findall(r"\b(20[2-3]\d)\b", text)
        if m:
            return m[-1]  # most-recent year mentioned
    return None


def claim_period_key(claim) -> str:
    """Return the entities.json period key for this claim.

    Annual scope → "<year>"; quarterly/half scope → "<year>_<scope>";
    point-in-time → "current".
    """
    year = normalise_year(claim)
    scope = (claim.get("timePeriodScope") or claim.get("time_period_scope") or "").lower()
    if not scope:
        scope = "annual"
    if scope == "annual":
        return year or "current"
    if scope in ("h1", "h2", "q1", "q2", "q3", "q4"):
        return f"{year}_{scope}" if year else "current"
    if scope == "point_in_time":
        return "current"
    if scope == "exit_snapshot":
        return year or "current"
    if scope == "monthly_peak":
        return year or "current"
    return year or "current"


def resolve_entity(claim, ctx, *, allow_text_fallback: bool = True):
    """Resolve a vault claim → (entity_slug, entity_record, ambiguous).

    Resolution order:
      1. claim['entity'] field (lowercased) directly matches a companies[].slug
      2. SLUG_ALIASES short-name lookup
      3. tags pass: each tag tested against schema entity_match_rules. The
         first non-multi-tier-ambiguous match wins, but a tag that names
         a non-canonical product (e.g. "Codex") aborts the resolve so the
         claim routes to audit — better to ask a human than misattribute.
      4. claim text + tags joined → entity_match_rules (only when no
         product-level signal exists in tags)
      5. fall back to None — unresolved

    Returns:
      ("slug", entity_dict, False)  — match
      (None, None, True)            — multi-tier ambiguous (caller routes to audit)
      (None, None, False)           — no match
    """
    companies = ctx.entities.get("companies", [])
    by_slug = {c["slug"].lower(): c for c in companies}
    by_name = {c.get("name", "").lower(): c for c in companies}

    # Direct entity field
    raw = (claim.get("entity") or "").strip().lower()
    if raw:
        # multi-tier guard
        if raw in MULTI_TIER_AMBIGUOUS:
            return None, None, True
        if raw in by_slug:
            return raw, by_slug[raw], False
        if raw in SLUG_ALIASES:
            slug = SLUG_ALIASES[raw]
            if slug in by_slug:
                return slug, by_slug[slug], False
        if raw in by_name:
            ent = by_name[raw]
            return ent["slug"].lower(), ent, False

    # Tags pass — strict. If a tag names a known non-canonical product
    # (e.g. "Codex" — not in entities.json), refuse the resolve. Tag
    # signals are usually the most reliable; an unknown product tag means
    # the ARR/users/etc. attribution would be wrong.
    rules = ctx.schema.get("entity_match_rules", []) or []
    PRODUCT_TAGS_NEEDING_DISAMBIG = {
        "codex", "claude code", "claude-code", "gemini cli",
        "azure openai", "github copilot",  # multi-attribution products
    }

    def _try_rules(text):
        for rule in rules:
            try:
                if re.search(rule["pattern"], text, re.I):
                    slug = rule.get("slug")
                    if slug and slug.lower() in by_slug:
                        return slug.lower(), by_slug[slug.lower()]
            except re.error:
                continue
        return None, None

    tag_matches = []
    for tag in claim.get("tags") or []:
        tag_str = str(tag).strip().lower()
        if not tag_str:
            continue
        if tag_str in PRODUCT_TAGS_NEEDING_DISAMBIG:
            return None, None, True  # route to audit; humans pick the host entity
        if tag_str in MULTI_TIER_AMBIGUOUS:
            return None, None, True
        if tag_str in by_slug:
            tag_matches.append((tag_str, by_slug[tag_str]))
            continue
        if tag_str in SLUG_ALIASES:
            slug = SLUG_ALIASES[tag_str]
            if slug in by_slug:
                tag_matches.append((slug, by_slug[slug]))
                continue
        slug, ent = _try_rules(tag_str)
        if slug:
            tag_matches.append((slug, ent))

    if tag_matches:
        # If multiple distinct entities match across tags, that's ambiguous.
        unique = {s for s, _ in tag_matches}
        if len(unique) > 1:
            return None, None, True
        return tag_matches[0][0], tag_matches[0][1], False

    if allow_text_fallback:
        # Restrict text fallback to claim text + metricKey — NOT notes /
        # sourceAuthor, which often name the publisher rather than the
        # subject (e.g. "OpenAI Press Release" routing every claim to
        # OpenAI). This narrows false positives like dp-110.
        haystack = " ".join(
            [
                claim.get("claim", "") or "",
                claim.get("metricKey", "") or "",
                " ".join(str(t) for t in (claim.get("tags") or [])),
            ]
        ).lower()
        # Multi-tier guard on text
        for ambiguous, tier_records in MULTI_TIER_AMBIGUOUS.items():
            if any(tr in haystack for tr in tier_records):
                continue
            if re.search(rf"\b{re.escape(ambiguous)}\b", haystack):
                return None, None, True
        # Refuse text-fallback matches when the claim mentions a known
        # ambiguous product label
        for product in PRODUCT_TAGS_NEEDING_DISAMBIG:
            if re.search(rf"\b{re.escape(product)}\b", haystack):
                return None, None, True

        slug, ent = _try_rules(haystack)
        if slug:
            return slug, ent, False

        # SLUG_ALIASES fallback — match short names against the haystack,
        # only return if the resulting slug is unambiguous (one match).
        alias_hits = set()
        for alias, slug in SLUG_ALIASES.items():
            if slug not in by_slug:
                continue
            if re.search(rf"\b{re.escape(alias)}\b", haystack):
                alias_hits.add(slug)
        if len(alias_hits) == 1:
            slug = alias_hits.pop()
            return slug, by_slug[slug], False
        if len(alias_hits) > 1:
            return None, None, True  # ambiguous

        # Final pass: full-name token match against entities.json
        # companies[].name. Stricter than rules — must be a whole-word
        # match. Only fires for unambiguous (single) matches.
        name_hits = set()
        for ent in companies:
            name = (ent.get("name") or "").lower().strip()
            if not name or len(name) < 4:
                continue
            if re.search(rf"\b{re.escape(name)}\b", haystack):
                name_hits.add(ent["slug"].lower())
        if len(name_hits) == 1:
            slug = name_hits.pop()
            return slug, by_slug[slug], False
        if len(name_hits) > 1:
            return None, None, True

    return None, None, False


def existing_tier(entity, prov_key) -> str | None:
    """Strongest tier currently recorded on entity.provenance[prov_key].

    Returns None if no provenance exists yet. Mirrors the WEIGHT_RANK guard
    in apply_decisions.check_provenance_guard but in the tier_1A..tier_3B
    namespace used by wq-098.
    """
    prov = (entity or {}).get("provenance", {}).get(prov_key)
    if not prov or not prov.get("claims"):
        return None
    best = None
    for c in prov["claims"]:
        t = c.get("tier") or _legacy_weight_to_tier(c.get("weight"))
        if not t:
            continue
        if best is None or TIER_RANK.get(t, 0) > TIER_RANK.get(best, 0):
            best = t
    return best


def _legacy_weight_to_tier(weight):
    """Best-effort backfill for pre-098 provenance entries that carry only
    `weight` (authoritative/corroborating/indicative)."""
    return {
        "authoritative": "tier_1A",
        "corroborating": "tier_2A",
        "indicative": "tier_3A",
    }.get((weight or "").lower())


def build_prov_entry(claim, value, *, role="supports", origin="wq-098-apply"):
    """Standard provenance entry shape. Mirrors apply_decisions.apply_accepted
    so audit/UI code that already parses entity provenance keeps working."""
    return {
        "id": claim.get("id"),
        "claim": (claim.get("claim") or "")[:160],
        "value": value,
        "unit": claim.get("unit") or "",
        "weight": _tier_to_weight(derive_tier(claim)),
        "tier": derive_tier(claim),
        "confidence": claim.get("confidence") or "estimated",
        "source": claim.get("sourceAuthor") or "",
        "source_url": claim.get("sourceUrl") or "",
        "date": claim.get("dateOfClaim") or "",
        "origin": origin,
        "role": role,
    }


def _tier_to_weight(tier):
    if tier in ("tier_1A", "tier_1B"):
        return "authoritative" if tier == "tier_1A" else "corroborating"
    if tier in ("tier_2A", "tier_2B"):
        return "corroborating"
    return "indicative"


def coerce_value_to_billions(value, unit) -> float | None:
    """Normalise a vault claim value to $B scalar.

    Recognised units: $B, USD billions, USD_billions, $B ARR, $B valuation,
    USD millions, $M ARR, $M ACV, USD (raw dollars), $B/month, $B monthly,
    USD/month treated as raw dollars-per-month (caller decides whether to
    annualise).

    Returns None if `value` can't be coerced (e.g. string "approximately 2
    billion") — caller routes to audit instead of silently coercing.
    """
    if value is None:
        return None
    if not isinstance(value, (int, float)):
        return None

    u = (unit or "").lower().strip()

    # already in $B
    if u in ("$b", "$b arr", "$b valuation", "usd billions", "usd_billions",
             "usd billions (annualized)", "$b range", "$b investment",
             "$b capex", "$b quarterly revenue", "$b/month", "$b monthly",
             "$b cash burn", "$b operating loss", "$b cumulative burn",
             "$b ar(peak-4wk)", "$b arr (peak-4wk)", "$b monthly funding",
             "$b (investor offer valuation)", "$b (implied ipo valuation)",
             "$b/gw revenue", "$b/gw cost"):
        return float(value)

    # $M → divide by 1000
    if u in ("usd millions", "$m arr", "$m acv"):
        return float(value) / 1000.0

    # raw USD → divide by 1e9
    if u in ("usd", "usd ", "us$", "us$ "):
        if abs(value) >= 1e6:  # likely raw dollars, not "$2 billion"
            return float(value) / 1e9
        # already in $B-style scalar (e.g. "$2 billion" = value=2)
        return float(value)

    return None


def now_iso() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d")


def is_do_not_apply(claim) -> bool:
    """D7: parked claims and explicit do_not_apply=True skip."""
    if claim.get("do_not_apply") is True:
        return True
    if (claim.get("confidence") or "").lower() == "parked":
        return True
    if (claim.get("status") or "").lower() == "parked":
        return True
    return False
