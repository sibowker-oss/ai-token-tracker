"""wq-100 variance gate.

Sits between handler-produced FieldWrites and the entities.json commit.
Partitions writes into:
  - auto_apply: incoming variance from prior is small AND provenance is
    same-or-better AND prior exists.
  - review:    must be human-reviewed (variance ≥15%, first-time entity
    value, lower-tier-than-existing, or absolute-magnitude floor breach).
  - anomaly:   variance >50% — also written to a daily anomalies markdown
    so Simon's morning glance surfaces them.

The wq-098 D2 gate (verified + tier_2A+) already filters at handler time;
by the time a write arrives here, the claim is auto-apply-eligible. The
wq-100 gate adds the variance / first-time / magnitude / provenance
guards from §Decisions D3, D4, D5.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import _shared as S


# §Decisions D5 — variance bands (fraction, not percent).
VARIANCE_AUTO_APPLY = 0.15
VARIANCE_ANOMALY = 0.50

# §5 Edge case 3 — absolute-magnitude floor for dollar-denominated fields.
# When BOTH prior and incoming are below this, the variance gate routes to
# review regardless of the percentage delta. Avoids the "$10M → $40M is
# 300%, but immaterial" trap. Expressed in $B because that's the unit
# coerce_value_to_billions returns.
ABS_FLOOR_B = 0.05  # $50M

# Field keys whose values are dollar-denominated and therefore subject to
# the absolute-magnitude floor. Anything not in this set is gated only by
# the percentage variance.
DOLLAR_FIELDS = {
    "arr",
    "revenue",
    "revenue_annualised",
    "revenue_annualised_from_m",
    "valuation",
    "acv",
    "burn",
    "cash_burn",
    "operating_loss",
    "cumulative_burn",
    "capex",
    "investment",
    "quarterly_revenue",
}


@dataclass
class GateDecision:
    bucket: str        # "auto_apply" | "review" | "anomaly"
    reason: str        # human-readable explanation for log + audit
    variance: float | None = None  # fractional delta from prior, when both numeric
    is_first_time: bool = False
    floor_breached: bool = False
    incoming_tier: str | None = None
    existing_tier: str | None = None


def _resolve_prior(entity, year_key, field_key):
    """Look up the existing scalar value for (entity, period, field)."""
    if entity is None:
        return None
    if year_key == "current":
        return (entity.get("current") or {}).get(field_key)
    return ((entity.get("financials") or {}).get(year_key) or {}).get(field_key)


def _both_below_floor(prior, incoming, field_key):
    """True when the field is dollar-denominated and both values are below
    the $50M absolute floor. Non-dollar fields never trip the floor."""
    if field_key not in DOLLAR_FIELDS:
        return False
    if not isinstance(prior, (int, float)) or not isinstance(incoming, (int, float)):
        return False
    return abs(prior) < ABS_FLOOR_B and abs(incoming) < ABS_FLOOR_B


def evaluate(write, entity) -> GateDecision:
    """Decide whether `write` may auto-apply, must go to review, or is an
    anomaly. Mirrors §Decisions D3 / D4 / D5 of the wq-100 brief.

    `write` is a FieldWrite. `entity` is the entities.json companies[] dict
    for the target slug (or None — surfaces as ENTITY_UNRESOLVED, route to
    review).
    """
    if entity is None:
        return GateDecision(
            bucket="review",
            reason="entity_unresolved — apply_pipeline could not match the claim "
                   "to an entities.json record",
        )

    prior = _resolve_prior(entity, write.year_key, write.field_key)
    incoming_tier = (write.prov_entry or {}).get("tier")
    prov_key = (f"current.{write.field_key}" if write.year_key == "current"
                else f"{write.year_key}.{write.field_key}")
    existing_tier = S.existing_tier(entity, prov_key)

    # D4: first-time entity value → ALWAYS review.
    if prior is None:
        return GateDecision(
            bucket="review",
            reason="first_time — no existing value for this entity+period+field; "
                   "humans set the baseline",
            is_first_time=True,
            incoming_tier=incoming_tier,
            existing_tier=existing_tier,
        )

    # If prior is non-numeric we can't compute a variance — defer to review
    # rather than guess.
    if not isinstance(prior, (int, float)) or not isinstance(write.value, (int, float)):
        return GateDecision(
            bucket="review",
            reason=f"non_numeric — prior={prior!r}, incoming={write.value!r}; "
                   f"variance gate needs numeric inputs",
            incoming_tier=incoming_tier,
            existing_tier=existing_tier,
        )

    # Absolute-magnitude floor (§5 edge case 3).
    if _both_below_floor(prior, write.value, write.field_key):
        return GateDecision(
            bucket="review",
            reason=f"below_abs_floor — both prior (${prior * 1000:.0f}M) and "
                   f"incoming (${write.value * 1000:.0f}M) under $50M; gate "
                   f"defaults to human review",
            floor_breached=True,
            incoming_tier=incoming_tier,
            existing_tier=existing_tier,
        )

    # Variance computation. Prior == 0 is treated as "first-time-ish" because
    # any positive incoming is +∞%; defer to review.
    if prior == 0:
        return GateDecision(
            bucket="review",
            reason="prior_zero — variance undefined when prior is zero",
            is_first_time=True,
            incoming_tier=incoming_tier,
            existing_tier=existing_tier,
        )

    variance = abs(write.value - prior) / abs(prior)

    # D5: anomaly band — >50% always triggers anomaly + review.
    if variance > VARIANCE_ANOMALY:
        return GateDecision(
            bucket="anomaly",
            reason=f"variance {variance * 100:.1f}% exceeds 50% anomaly band",
            variance=variance,
            incoming_tier=incoming_tier,
            existing_tier=existing_tier,
        )

    # D5: review band — 15-50%.
    if variance >= VARIANCE_AUTO_APPLY:
        return GateDecision(
            bucket="review",
            reason=f"variance {variance * 100:.1f}% in 15–50% review band",
            variance=variance,
            incoming_tier=incoming_tier,
            existing_tier=existing_tier,
        )

    # D3d: provenance must be ≥ existing. If existing tier is stronger
    # than incoming, even a small-variance write gets reviewed.
    if existing_tier and incoming_tier:
        if S.TIER_RANK.get(incoming_tier, 0) < S.TIER_RANK.get(existing_tier, 0):
            return GateDecision(
                bucket="review",
                reason=f"weaker_provenance — incoming {incoming_tier} below "
                       f"existing {existing_tier}; variance {variance * 100:.1f}%",
                variance=variance,
                incoming_tier=incoming_tier,
                existing_tier=existing_tier,
            )

    # All four D3 conditions met — auto-apply.
    return GateDecision(
        bucket="auto_apply",
        reason=f"variance {variance * 100:.1f}% — all D3 conditions met",
        variance=variance,
        incoming_tier=incoming_tier,
        existing_tier=existing_tier,
    )
