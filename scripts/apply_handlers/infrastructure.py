"""Infrastructure handler — GW/kW/GPUs claims.

Most claims of this shape are about market-level totals (e.g. "25 data
centres cancelled = 5GW") or hyperscaler commitments. They land on
entities.json companies[slug].current.<gw_or_gpu_field>; market-level
claims go to audit so a human routes them.
"""

from . import _shared as S


UNITS = ("GW", "kW", "GPUs", "GW at risk", "USD/GW/year",
         "$B/GW revenue", "$B/GW cost", "$/hr H100 spot")


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
        # Market-level (no entity attached) — surface in audit, not silently dropped
        result.skip_reason = "entity_unresolved" if not ambiguous else "multi_tier_ambiguous"
        result.audit_rows.append(_row(claim, result.skip_reason))
        return result

    unit = (claim.get("unit") or "").lower()
    field_key = _field_for(unit)
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
        value=float(raw),
        unit=claim.get("unit") or "",
        prov_entry=S.build_prov_entry(claim, float(raw)),
        label=f"{entity.get('name', slug)} current.{field_key} = {raw} {claim.get('unit') or ''}",
    )
    result.writes.append(write)
    result.consumer_keys.append("entityDirectory")
    result.applied = True
    return result


def _field_for(unit):
    if unit == "gw":
        return "gw_committed"
    if unit == "gw at risk":
        return "gw_at_risk"
    if unit == "kw":
        return "kw_per_rack"
    if unit == "gpus":
        return "gpu_count"
    if unit.startswith("usd/gw") or unit.startswith("$b/gw"):
        return "usd_per_gw_year"
    if "h100" in unit:
        return "h100_spot_usd_hr"
    return "infra_metric"


def _row(claim, reason):
    return {"id": claim.get("id"), "category": "infrastructure", "reason": reason,
            "claim": (claim.get("claim") or "")[:120]}
