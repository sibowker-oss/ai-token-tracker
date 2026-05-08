"""Telemetry handler — downloads, version numbers, completions.

These are operational signals (PyPI/npm/HF download counters, package
versions, GitHub completion stats). Per wq-047 they should NOT live in
vault-data.json long-term — wq-098 backfill marks them used so the orphan
count drops, but the right home is `data/signals_latest.json` (the
auto_update.py output).

This handler queues NO writes — it only records the consumer key
"telemetry-signals" so the orphan validator can stop pinging on these.
The audit doc captures every telemetry claim so wq-099 can sort them.
"""

from . import _shared as S


UNITS = (
    "downloads",
    "B downloads",
    "M downloads",
    "M downloads (Qwen)",
    "completions/month",
    "version number",
    "version",
    "T tokens (MiniMax M2.5)",
    "T tokens (Anthropic, OpenRouter)",
    "filings",
    "examples",
    "qualitative",
    "timeline",
    "months",
    "years",
    "years payback",
)


def handle(claim, ctx):
    result = S.HandlerResult()
    if S.is_do_not_apply(claim):
        result.skip_reason = "do_not_apply"
        return result

    # Always consume telemetry claims — even if confidence is verified, they
    # do not move headline figures. Audit row records what was collected.
    result.consumer_keys.append("telemetry-signals")
    result.applied = True
    result.audit_rows.append({
        "id": claim.get("id"),
        "category": "telemetry",
        "reason": "telemetry signal — recorded but not propagated to entityDirectory (wq-099 reroutes)",
        "claim": (claim.get("claim") or "")[:120],
    })
    return result
