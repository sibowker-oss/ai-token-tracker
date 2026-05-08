"""Default handler — claims with units that have no specific handler.

Per D3: every distinct unit value in vault-data.json must map to a
registered handler OR be explicitly listed in `UNHANDLED_UNITS` here.
release-check.mjs walks vault-data.json units against the union of
{handler-registered units, UNHANDLED_UNITS} and fails if any unit is
present in vault but in neither set.

Adding to UNHANDLED_UNITS is a deliberate "we know about this and won't
auto-apply it" — typically because the claim is editorial (qualitative
percent, narrative timeline) or the routing requires a human call.
"""

from . import _shared as S


# Units we consciously don't auto-apply. The release-check enforces that
# every unit in vault appears either here or in a registered handler.
UNHANDLED_UNITS = frozenset({
    "T tokens/day",   # OpenRouter aggregate — handled by quarterly_revenue but
                      # listed here as fallback for legacy spellings
    "$B range",       # editorial — narrative range, not a single value
    "% range",        # editorial — narrative range
    "$B investment",  # one-shot capital deployment claims; routing varies
    "$B capex",       # market-level — routes to market_aggregates manually
    "T tokens (MiniMax M2.5)",
    "T tokens (Anthropic, OpenRouter)",
    "millions",       # legacy spelling — covered by user_count.M users
    "year",           # editorial timeline (e.g. break-even projection)
})


UNITS = ()  # not registered to dispatcher; called only as fallback


def handle(claim, ctx):
    result = S.HandlerResult()
    if S.is_do_not_apply(claim):
        result.skip_reason = "do_not_apply"
        return result

    unit = claim.get("unit") or ""
    if unit in UNHANDLED_UNITS:
        result.skip_reason = "intentionally_unhandled"
        result.audit_rows.append({
            "id": claim.get("id"),
            "category": "default",
            "reason": f"unit '{unit}' intentionally_unhandled — see _default.UNHANDLED_UNITS",
            "claim": (claim.get("claim") or "")[:120],
        })
        return result

    # Unknown unit — surface loudly. release-check.mjs will fail until a
    # handler is registered or unit added to UNHANDLED_UNITS.
    result.skip_reason = f"no_handler_for_unit:{unit}"
    result.audit_rows.append({
        "id": claim.get("id"),
        "category": "default",
        "reason": f"NO HANDLER for unit '{unit}'. Register one in scripts/apply_handlers/ or add to UNHANDLED_UNITS.",
        "claim": (claim.get("claim") or "")[:120],
    })
    return result
