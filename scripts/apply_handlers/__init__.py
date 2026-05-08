"""apply_handlers — typed handlers for vault claim application.

Each module exposes:
    UNITS: tuple[str, ...]              # vault `unit` values handled
    handle(claim, ctx) -> HandlerResult  # apply logic

The dispatcher (`apply_pipeline.HandlerRegistry`) imports each module and
registers its `UNITS` against `handle`. Adding a new claim category means
adding a new module and listing it in `_REGISTERED` below.

Per wq-098 D3: every distinct `unit` value in vault-data.json must map to a
registered handler (or be explicitly listed in `_default.UNHANDLED_UNITS`)
or `release-check.mjs` fails.
"""

from . import (
    arr,
    valuation,
    acv,
    pricing,
    user_count,
    employee_count,
    infrastructure,
    quarterly_revenue,
    burn,
    growth,
    telemetry,
    _default,
)

_REGISTERED = (
    arr,
    valuation,
    acv,
    pricing,
    user_count,
    employee_count,
    infrastructure,
    quarterly_revenue,
    burn,
    growth,
    telemetry,
)


def all_handlers():
    """Yield (unit, handler_module, handler_fn) for every registered unit."""
    for module in _REGISTERED:
        for unit in module.UNITS:
            yield unit, module, module.handle


def default_handler():
    return _default
