"""Shared helper for the decided-claims fingerprint index.

claims.html and review.html re-load their candidate pools from static files on
every page load. Without a server-side record of "this claim was already
decided," items resurface after each submit because browser localStorage is the
only thing tracking decisions client-side, and it gets cleared on success.

This module owns:
  - claim_signature(c): the canonical fingerprint (mirrored in claims.html)
  - load_index() / save_index(): on-disk format at data-updates/decided-signatures.json
  - record_decisions(payload): append signatures from a decision payload

The index format is a flat dict { signature: {decision, decided_at} } so the
file is human-readable and easy to inspect during incidents.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Iterable

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(ROOT_DIR, "data-updates", "decided-signatures.json")


def _norm(v) -> str:
    return str("" if v is None else v).strip().lower()


def claim_signature(c: dict) -> str:
    """Stable per-claim fingerprint. Must match claimSignature() in claims.html."""
    if not c:
        return ""
    parts = [
        _norm(c.get("entity")),
        _norm(c.get("metric")),
        _norm(c.get("value_display") or c.get("value")),
        _norm(c.get("source_url")),
        _norm(c.get("time_period")),
    ]
    sig = "|".join(parts)
    if sig.replace("|", "").strip() == "":
        sig = "claim:" + _norm(c.get("claim"))[:200]
    return sig


def claim_signature_fallback(c: dict) -> str:
    """Claim-text-only fallback. Emitted alongside the structured signature so
    historical decisions (which only carried claim text) still match items
    loaded with full structured fields."""
    if not c:
        return ""
    return "claim:" + _norm(c.get("claim"))[:200]


def load_index() -> dict:
    if not os.path.exists(INDEX_PATH):
        return {}
    try:
        with open(INDEX_PATH) as f:
            return json.load(f) or {}
    except Exception:
        return {}


def save_index(index: dict) -> None:
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    with open(INDEX_PATH, "w") as f:
        json.dump(index, f, indent=2, sort_keys=True)


def record_decisions(decisions: dict, decided_at: str | None = None) -> int:
    """Append signatures for every accepted/declined/parked/raw_pool item in
    `decisions`. Idempotent — re-recording the same payload is a no-op.

    Returns the number of NEW signatures added.
    """
    if not decisions:
        return 0
    decided_at = decided_at or datetime.now().isoformat(timespec="seconds")
    index = load_index()
    added = 0
    for bucket in ("accepted", "declined", "parked", "raw_pool"):
        for item in decisions.get(bucket) or []:
            if not isinstance(item, dict):
                continue
            for sig in (claim_signature(item), claim_signature_fallback(item)):
                if not sig or sig in index:
                    continue
                index[sig] = {"decision": bucket, "decided_at": decided_at}
                added += 1
    if added:
        save_index(index)
    return added


def record_signatures(sigs: Iterable[str], decision: str, decided_at: str | None = None) -> int:
    """Lower-level: record raw signature strings (used by the backfill)."""
    decided_at = decided_at or datetime.now().isoformat(timespec="seconds")
    index = load_index()
    added = 0
    for sig in sigs:
        if not sig or sig in index:
            continue
        index[sig] = {"decision": decision, "decided_at": decided_at}
        added += 1
    if added:
        save_index(index)
    return added
