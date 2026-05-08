"""Employee-count handler."""

from . import _shared as S


UNITS = ("employees", "AI roles")


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
    field_key = "ai_roles_open" if unit == "ai roles" else "employee_count"
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
        value=int(raw),
        unit="count",
        prov_entry=S.build_prov_entry(claim, int(raw)),
        label=f"{entity.get('name', slug)} current.{field_key} = {int(raw):,}",
    )
    result.writes.append(write)
    result.consumer_keys.append("entityDirectory")
    if unit == "ai roles":
        # ATS-derived hiring counts also flow through to the hiring snapshot block
        result.consumer_keys.append("hiring.snapshots")
    result.applied = True
    return result


def _row(claim, reason):
    return {"id": claim.get("id"), "category": "employee_count", "reason": reason,
            "claim": (claim.get("claim") or "")[:120]}
