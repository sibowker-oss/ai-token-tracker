"""Valuation handler — equity / pre-money / IPO valuation claims.

Writes to companies[slug].financials[<year>].valuation OR current.valuation.
Stored in $B per existing entities.json convention.
"""

from . import _shared as S


UNITS = (
    "$B valuation",
    "$B (investor offer valuation)",
    "$B (implied IPO valuation)",
)


def handle(claim, ctx):
    result = S.HandlerResult()
    if S.is_do_not_apply(claim):
        result.skip_reason = "do_not_apply"
        return result

    value_b = S.coerce_value_to_billions(claim.get("value"), claim.get("unit"))
    if value_b is None:
        result.skip_reason = "value_uncoercible"
        result.audit_rows.append(_audit_row(claim, "value not numeric"))
        return result

    slug, entity, ambiguous = S.resolve_entity(claim, ctx)
    if ambiguous or not slug:
        result.skip_reason = "entity_unresolved" if not ambiguous else "multi_tier_ambiguous"
        result.audit_rows.append(_audit_row(claim, result.skip_reason))
        return result

    period = S.claim_period_key(claim)
    field_key = "valuation"
    prov_key = f"{period}.{field_key}" if period != "current" else f"current.{field_key}"

    existing = S.existing_tier(entity, prov_key)
    incoming = S.derive_tier(claim)
    if existing and S.TIER_RANK[existing] > S.TIER_RANK[incoming]:
        result.skip_reason = f"existing_tier_higher ({existing} > {incoming})"
        return result

    write = S.FieldWrite(
        entity_slug=slug,
        year_key=period,
        field_key=field_key,
        value=round(value_b, 4),
        unit="$B",
        prov_entry=S.build_prov_entry(claim, round(value_b, 4)),
        label=f"{entity.get('name', slug)} {prov_key} = ${round(value_b, 4)}B valuation",
    )
    result.writes.append(write)
    result.consumer_keys.append("entityDirectory")
    result.applied = True
    return result


def _audit_row(claim, reason):
    return {
        "id": claim.get("id"),
        "category": "valuation",
        "reason": reason,
        "claim": (claim.get("claim") or "")[:120],
    }
