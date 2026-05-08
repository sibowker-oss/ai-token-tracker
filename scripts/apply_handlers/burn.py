"""Burn / loss / cash position handler."""

from . import _shared as S


UNITS = (
    "$B cash burn",
    "$B operating loss",
    "$B cumulative burn",
    "$B monthly funding",
    "% of revenue burned (OpenAI)",
)


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

    slug, entity, ambiguous = S.resolve_entity(claim, ctx)
    if ambiguous or not slug:
        result.skip_reason = "entity_unresolved" if not ambiguous else "multi_tier_ambiguous"
        result.audit_rows.append(_row(claim, result.skip_reason))
        return result

    unit = (claim.get("unit") or "").lower()
    period = S.claim_period_key(claim)
    field_key = _field_for(unit)
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
        value=float(raw),
        unit="$B" if "burn" in field_key or "loss" in field_key else "%",
        prov_entry=S.build_prov_entry(claim, float(raw)),
        label=f"{entity.get('name', slug)} {prov_key} = {raw}",
    )
    result.writes.append(write)
    result.consumer_keys.append("entityDirectory")
    result.applied = True
    return result


def _field_for(unit):
    if unit == "$b cash burn":
        return "cash_burn"
    if unit == "$b operating loss":
        return "operating_loss"
    if unit == "$b cumulative burn":
        return "cumulative_burn"
    if unit == "$b monthly funding":
        return "monthly_funding_b"
    if "burned" in unit:
        return "pct_revenue_burned"
    return "burn_metric"


def _row(claim, reason):
    return {"id": claim.get("id"), "category": "burn", "reason": reason,
            "claim": (claim.get("claim") or "")[:120]}
