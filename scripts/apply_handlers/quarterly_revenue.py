"""Quarterly revenue handler — $B quarterly revenue, $B/month, $B monthly."""

from . import _shared as S


UNITS = ("$B quarterly revenue", "$B/month", "$B monthly", "T tokens/day", "T tokens/week")


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
    if unit == "$b quarterly revenue":
        # Annualise: ×4 → $B annual, write as financials[year].revenue
        period = S.claim_period_key(claim)
        field_key = "revenue_annualised_from_q"
        value_b = float(raw) * 4
    elif unit in ("$b/month", "$b monthly"):
        period = S.claim_period_key(claim)
        field_key = "revenue_annualised_from_m"
        value_b = float(raw) * 12
    elif unit.startswith("t tokens"):
        period = "current"
        field_key = "tokens_per_day_t" if "/day" in unit else "tokens_per_week_t"
        value_b = float(raw)
    else:
        result.skip_reason = "unrecognised_quarterly_revenue_unit"
        return result

    prov_key = f"{period}.{field_key}" if period != "current" else f"current.{field_key}"
    existing = S.existing_tier(entity, prov_key)
    incoming = S.derive_tier_for_gate(claim)
    if existing and S.TIER_RANK[existing] > S.TIER_RANK[incoming]:
        result.skip_reason = f"existing_tier_higher ({existing} > {incoming})"
        return result

    write = S.FieldWrite(
        entity_slug=slug,
        year_key=period,
        field_key=field_key,
        value=round(value_b, 4),
        unit="$B" if "tokens" not in field_key else "T",
        prov_entry=S.build_prov_entry(claim, round(value_b, 4)),
        label=f"{entity.get('name', slug)} {prov_key} = {round(value_b, 4)}",
    )
    result.writes.append(write)
    result.consumer_keys.append("entityDirectory")
    result.applied = True
    return result


def _row(claim, reason):
    return {"id": claim.get("id"), "category": "quarterly_revenue", "reason": reason,
            "claim": (claim.get("claim") or "")[:120]}
