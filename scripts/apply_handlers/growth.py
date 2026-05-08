"""Growth-rate / share / multiplier handler.

Most growth claims are editorial colour rather than load-bearing numerics —
this handler records them as provenance entries on entities.json without
overwriting structured data fields. The audit doc lists what was captured
so future briefs can promote specific shapes.
"""

from . import _shared as S


UNITS = (
    "%",
    "percent",
    "% range",
    "% growth/quarter",
    "% drawdown",
    "% YoY decline",
    "% API revenue",
    "% of revenue burned",
    "% of GitHub commits",
    "% of AI compute (inference)",
    "x",
    "x YoY",
    "x per quarter",
    "x spend ratio",
    "ratio",
    "pp vs prior forecast",
)


def handle(claim, ctx):
    result = S.HandlerResult()
    if S.is_do_not_apply(claim):
        result.skip_reason = "do_not_apply"
        return result

    raw = claim.get("value")
    if not isinstance(raw, (int, float)):
        result.skip_reason = "value_uncoercible"
        return result

    slug, entity, ambiguous = S.resolve_entity(claim, ctx)
    if ambiguous or not slug:
        # Most growth claims have no entity (market-level). Audit, don't fail.
        result.skip_reason = "entity_unresolved" if not ambiguous else "multi_tier_ambiguous"
        result.audit_rows.append({
            "id": claim.get("id"),
            "category": "growth",
            "reason": result.skip_reason,
            "claim": (claim.get("claim") or "")[:120],
        })
        return result

    unit = (claim.get("unit") or "").lower()
    period = S.claim_period_key(claim)
    field_key = _field_for(unit, claim)
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
        unit=claim.get("unit") or "",
        prov_entry=S.build_prov_entry(claim, float(raw)),
        label=f"{entity.get('name', slug)} {prov_key} = {raw} {claim.get('unit') or ''}",
    )
    result.writes.append(write)
    result.consumer_keys.append("entityDirectory")
    result.applied = True
    return result


def _field_for(unit, claim):
    text = (claim.get("claim") or "").lower()
    if "drawdown" in unit or "drawdown" in text:
        return "stock_drawdown_pct"
    if "yoy decline" in unit:
        return "yoy_decline_pct"
    if "growth/quarter" in unit:
        return "qoq_growth_pct"
    if "yoy" in unit and "x" in unit:
        return "yoy_multiple"
    if "api revenue" in unit:
        return "pct_api_revenue"
    if "github commits" in unit:
        return "pct_github_commits"
    if "spend ratio" in unit:
        return "spend_ratio_x"
    if unit == "x" or "x per quarter" in unit:
        return "growth_multiple"
    if "pp vs" in unit:
        return "pp_vs_prior_forecast"
    if "compute" in unit and "inference" in unit:
        return "pct_compute_inference"
    return "growth_pct"
