"""ARR handler — annualised run-rate revenue claims.

Writes to entities.json:
  companies[slug].financials[<year>].arr   (in $B)
  companies[slug].current.arr              (when scope is point_in_time)

Conflict resolution per D6: highest tier wins; ties broken by latest
dateOfClaim then latest dateAdded. The handler queues a write only when
the incoming tier is >= the existing field's strongest tier.
"""

from . import _shared as S


UNITS = (
    "$B",
    "$B ARR",
    "USD billions",
    "USD_billions",
    "USD billions (annualized)",
    "USD",
    "USD millions",
    "$M ARR",
    "$B ARR (peak-4wk)",
)


def handle(claim, ctx):
    result = S.HandlerResult()

    if S.is_do_not_apply(claim):
        result.skip_reason = "do_not_apply"
        return result

    # Heuristic gate: this handler only fires for claims that talk about
    # ARR/revenue. Lots of vault claims have unit "USD" but describe
    # valuation, capex, burn, etc. Hand off to other handlers via the
    # tag/text gate.
    if not _looks_like_arr(claim):
        result.skip_reason = "unit_matches_but_not_arr_claim"
        return result

    value_b = S.coerce_value_to_billions(claim.get("value"), claim.get("unit"))
    if value_b is None:
        result.skip_reason = "value_uncoercible"
        result.audit_rows.append({
            "id": claim.get("id"),
            "category": "arr",
            "reason": "value not numeric / unit not recognised",
            "claim": (claim.get("claim") or "")[:120],
        })
        return result

    slug, entity, ambiguous = S.resolve_entity(claim, ctx)
    if ambiguous:
        result.skip_reason = "multi_tier_ambiguous"
        result.audit_rows.append({
            "id": claim.get("id"),
            "category": "arr",
            "reason": "multi-tier company; need tier-record entity slug",
            "claim": (claim.get("claim") or "")[:120],
        })
        return result
    if not slug:
        result.skip_reason = "entity_unresolved"
        result.audit_rows.append({
            "id": claim.get("id"),
            "category": "arr",
            "reason": "entity not in entities.json",
            "claim": (claim.get("claim") or "")[:120],
        })
        return result

    # Period: ARR claims usually carry a year; if missing, route to current.
    period = S.claim_period_key(claim)
    field_key = "arr"
    prov_key = f"{period}.{field_key}" if period != "current" else f"current.{field_key}"

    # Conflict resolution
    existing_tier = S.existing_tier(entity, prov_key)
    incoming_tier = S.derive_tier(claim)
    if existing_tier and S.TIER_RANK[existing_tier] > S.TIER_RANK[incoming_tier]:
        result.skip_reason = f"existing_tier_higher ({existing_tier} > {incoming_tier})"
        result.audit_rows.append({
            "id": claim.get("id"),
            "category": "arr",
            "reason": f"existing {existing_tier} > incoming {incoming_tier} on {entity['name']} {prov_key}",
            "claim": (claim.get("claim") or "")[:120],
        })
        return result

    write = S.FieldWrite(
        entity_slug=slug,
        year_key=period,
        field_key=field_key,
        value=round(value_b, 4),
        unit="$B",
        prov_entry=S.build_prov_entry(claim, round(value_b, 4)),
        label=f"{entity.get('name', slug)} {prov_key} = ${round(value_b, 4)}B",
    )
    result.writes.append(write)
    result.consumer_keys.append("entityDirectory")
    # ai_app entities also flow through to dashboard.topConsumers + arrModel
    if "ai_app" in (entity.get("roles") or []):
        result.consumer_keys.append("dashboard.topConsumers")
        result.consumer_keys.append("arrModel.apps.aiNative")
    if "model_provider" in (entity.get("roles") or []):
        result.consumer_keys.append("dashboard.providers")
        result.consumer_keys.append("arrModel.apps.frontier")
    result.applied = True
    return result


def _looks_like_arr(claim):
    """Filter for unit='USD' / 'USD billions' / '$B' claims that are
    actually ARR/revenue (not valuation/capex/burn/pricing)."""
    text = " ".join([
        claim.get("claim", "") or "",
        claim.get("metricKey", "") or "",
        " ".join(str(t) for t in (claim.get("tags") or [])),
        claim.get("unit", "") or "",
    ]).lower()

    # Strong-positive tokens
    arr_tokens = (
        "arr", "annualized revenue", "annualised revenue", "run rate", "run-rate",
        "revenue run", "revenue run-rate", "revenue (annualised)",
        "revenue (annualized)", "annual revenue run rate", "annualized run rate",
    )
    if any(t in text for t in arr_tokens):
        # Negative — exclude valuation/burn/capex/funding even if "revenue" appears
        if any(neg in text for neg in (
            "valuation", "valued at", "investor offer", "implied ipo",
            "cash burn", "operating loss", "cumulative burn", "burn rate",
            "capex", "monthly funding", "% of revenue burned",
        )):
            return False
        return True

    # If unit is $B ARR / $M ARR / $B/month explicitly → it's ARR-shaped
    unit = (claim.get("unit") or "").lower()
    if unit in ("$b arr", "$m arr", "$b arr (peak-4wk)"):
        return True

    return False
