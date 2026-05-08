"""Pricing handler — list-price claims (subscription, per-token).

Writes to entities.json companies[slug].current.pricing[<sku>] = <value>.
Pricing claims rarely move headline figures; treated as informational
provenance unless the claim's tags explicitly target a published field.
"""

from . import _shared as S


UNITS = (
    "USD/month",
    "USD/user/month",
    "$/user/month",
    "USD/million tokens",
    "$/M tokens (2026 equivalent)",
    "$/M input tokens (Opus 4.6)",
)


def handle(claim, ctx):
    result = S.HandlerResult()
    if S.is_do_not_apply(claim):
        result.skip_reason = "do_not_apply"
        return result

    val = claim.get("value")
    if not isinstance(val, (int, float)):
        result.skip_reason = "value_uncoercible"
        result.audit_rows.append(_row(claim, "value not numeric"))
        return result

    slug, entity, ambiguous = S.resolve_entity(claim, ctx)
    if ambiguous or not slug:
        result.skip_reason = "entity_unresolved" if not ambiguous else "multi_tier_ambiguous"
        result.audit_rows.append(_row(claim, result.skip_reason))
        return result

    field_key = _pricing_field_for_unit(claim.get("unit") or "")
    prov_key = f"current.{field_key}"

    existing = S.existing_tier(entity, prov_key)
    incoming = S.derive_tier_for_gate(claim)
    if existing and S.TIER_RANK[existing] > S.TIER_RANK[incoming]:
        result.skip_reason = f"existing_tier_higher ({existing} > {incoming})"
        return result

    write = S.FieldWrite(
        entity_slug=slug,
        year_key="current",
        field_key=field_key,
        value=float(val),
        unit=claim.get("unit") or "",
        prov_entry=S.build_prov_entry(claim, float(val)),
        label=f"{entity.get('name', slug)} current.{field_key} = {val} {claim.get('unit') or ''}",
    )
    result.writes.append(write)
    result.consumer_keys.append("entityDirectory")
    result.applied = True
    return result


def _pricing_field_for_unit(unit):
    u = unit.lower()
    if "user/month" in u or "/user/month" in u:
        return "price_per_user_month_usd"
    if "/month" in u:
        return "price_per_month_usd"
    if "tokens" in u and ("input" in u or "opus" in u):
        return "input_token_price_usd_per_m"
    if "tokens" in u:
        return "token_price_usd_per_m"
    return "price"


def _row(claim, reason):
    return {"id": claim.get("id"), "category": "pricing", "reason": reason,
            "claim": (claim.get("claim") or "")[:120]}
