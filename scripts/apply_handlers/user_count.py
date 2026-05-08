"""User-count handler — WAU/MAU/seat counts.

Writes companies[slug].current.user_count or .seat_count (in millions, to
match the existing entities.json convention).
"""

from . import _shared as S


UNITS = ("users", "M users", "M monthly users", "M seats", "seats", "business customers", "customers", "teams", "subscriber_count")


def handle(claim, ctx):
    result = S.HandlerResult()
    if S.is_do_not_apply(claim):
        result.skip_reason = "do_not_apply"
        return result

    raw = claim.get("value")
    if not isinstance(raw, (int, float)):
        result.skip_reason = "value_uncoercible"
        result.audit_rows.append(_row(claim, "value not numeric"))
        return result

    unit = (claim.get("unit") or "").lower()
    # Normalise to whole-number count
    count = float(raw)
    if unit in ("m users", "m monthly users", "m seats"):
        count *= 1_000_000

    slug, entity, ambiguous = S.resolve_entity(claim, ctx)
    if ambiguous or not slug:
        result.skip_reason = "entity_unresolved" if not ambiguous else "multi_tier_ambiguous"
        result.audit_rows.append(_row(claim, result.skip_reason))
        return result

    field_key = _field_for(unit, claim)
    prov_key = f"current.{field_key}"
    existing = S.existing_tier(entity, prov_key)
    incoming = S.derive_tier(claim)
    if existing and S.TIER_RANK[existing] > S.TIER_RANK[incoming]:
        result.skip_reason = f"existing_tier_higher ({existing} > {incoming})"
        return result

    write = S.FieldWrite(
        entity_slug=slug,
        year_key="current",
        field_key=field_key,
        value=int(count),
        unit="count",
        prov_entry=S.build_prov_entry(claim, int(count)),
        label=f"{entity.get('name', slug)} current.{field_key} = {int(count):,}",
    )
    result.writes.append(write)
    result.consumer_keys.append("entityDirectory")
    result.applied = True
    return result


def _field_for(unit, claim):
    text = (claim.get("claim") or "").lower()
    if "seat" in unit or "seat" in text:
        return "seat_count"
    if "team" in unit:
        return "team_count"
    if "subscriber" in text:
        return "subscriber_count"
    if "business customer" in text or "enterprise customer" in text or unit == "business customers":
        return "business_customer_count"
    return "user_count"


def _row(claim, reason):
    return {"id": claim.get("id"), "category": "user_count", "reason": reason,
            "claim": (claim.get("claim") or "")[:120]}
