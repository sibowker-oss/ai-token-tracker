#!/usr/bin/env python3
"""Unit tests for the safe_str + load_json + save_json encoding contract in
scripts/apply_decisions.py.

Reproduces the wq-021 bug:
  - vault-inbox sourceAuthor "Sacra — Cursor Deep Dive" (clean U+2014)
    must produce a vault-data dataPoint with the same byte sequence — never
    the "â" mojibake triple.
  - A pre-mojibaked input must be cleaned by safe_str on the way INTO
    vault-data, not propagated as-is.

See briefs/active/2026-04-26-mojibake-roundtrip-fix.md §4.3.

Run: python3 tests/test_apply_decisions_encoding.py
"""
import json
import os
import sys
import tempfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "scripts"))

from apply_decisions import safe_str, load_json, save_json, apply_accepted  # noqa: E402

EM_DASH = "—"
CLEAN_AUTHOR = f"Sacra {EM_DASH} Cursor Deep Dive"
MOJIBAKE_AUTHOR = "Sacra â Cursor Deep Dive"
CURLY_APOSTROPHE_MOJIBAKE = "MSFTâOAI"  # U+2019 mojibake
CURLY_APOSTROPHE_CLEAN = "MSFT’OAI"


def _empty_schema():
    return {"entity_match_rules": [], "field_match_rules": [], "roles": {}}


def _empty_entities():
    return {"companies": []}


def _empty_vault_data():
    return {"dataPoints": []}


def _make_claim(source_author, claim_text="Cursor hit $2B ARR.", notes=""):
    return {
        "id": "test-1",
        "claim": claim_text,
        "value": 2,
        "unit": "$B",
        "sourceUrl": "https://example.com",
        "sourceType": "reporting",
        "sourceAuthor": source_author,
        "confidence": "verified",
        "dateOfClaim": "2026-02",
        "notes": notes,
        "tags": [],
        "metricKey": "annualized_revenue",
        "source_id": "src-035",
    }


def test_safe_str_passes_through_clean():
    assert safe_str(CLEAN_AUTHOR) == CLEAN_AUTHOR, "clean em-dash must not be touched"
    assert safe_str("plain ASCII text") == "plain ASCII text"
    assert safe_str("Anthropic — $19B ARR") == "Anthropic — $19B ARR"
    assert safe_str("") == ""


def test_safe_str_passes_through_non_strings():
    assert safe_str(None) is None
    assert safe_str(42) == 42
    assert safe_str([1, 2, 3]) == [1, 2, 3]


def test_safe_str_cleans_em_dash_mojibake():
    cleaned = safe_str(MOJIBAKE_AUTHOR)
    assert cleaned == CLEAN_AUTHOR, (
        f"mojibake must be cleaned: got {cleaned!r}, want {CLEAN_AUTHOR!r}"
    )


def test_safe_str_cleans_curly_apostrophe_mojibake():
    cleaned = safe_str(CURLY_APOSTROPHE_MOJIBAKE)
    assert cleaned == CURLY_APOSTROPHE_CLEAN, (
        f"curly apostrophe mojibake must be cleaned: "
        f"got {cleaned!r}, want {CURLY_APOSTROPHE_CLEAN!r}"
    )


def test_safe_str_no_op_on_partial_marker():
    # U+00E2 alone (no U+0080) is legitimate (e.g. plain "â" in a French name).
    # safe_str must not corrupt these.
    assert safe_str("Citroën") == "Citroën"
    assert safe_str("Café — name") == "Café — name"


def test_safe_str_no_op_on_undecodable():
    # Ensure round-trip failure is caught and string passes through unchanged.
    weird = "âÿ"  # not a valid utf-8 sequence after re-encoding
    out = safe_str(weird)
    # Either cleaned (if it happens to decode) or passed through. Must NOT raise.
    assert isinstance(out, str)


def test_apply_accepted_clean_input_stays_clean():
    """Positive path: clean em-dash in inbox -> clean em-dash in vault-data."""
    claim = _make_claim(CLEAN_AUTHOR, notes=f"From {CLEAN_AUTHOR}")
    vault = _empty_vault_data()
    apply_accepted(claim, vault, _empty_entities(), _empty_schema())

    dp = vault["dataPoints"][0]
    assert dp["sourceAuthor"] == CLEAN_AUTHOR, (
        f"clean -> clean expected, got {dp['sourceAuthor']!r}"
    )
    assert dp["notes"] == f"From {CLEAN_AUTHOR}"
    assert dp["claim"] == claim["claim"]


def test_apply_accepted_mojibake_input_is_cleaned():
    """Negative path: mojibaked inbox -> safe_str cleans on the way in.

    This is the wq-021 contract: even when upstream feeds us a corrupt
    string, vault-data.json must end up with the canonical em-dash.
    """
    claim = _make_claim(MOJIBAKE_AUTHOR, notes=f"From {MOJIBAKE_AUTHOR}")
    vault = _empty_vault_data()
    apply_accepted(claim, vault, _empty_entities(), _empty_schema())

    dp = vault["dataPoints"][0]
    assert dp["sourceAuthor"] == CLEAN_AUTHOR, (
        f"safe_str must clean sourceAuthor: got {dp['sourceAuthor']!r}, "
        f"want {CLEAN_AUTHOR!r}"
    )
    assert dp["notes"] == f"From {CLEAN_AUTHOR}", (
        f"safe_str must clean notes: got {dp['notes']!r}"
    )


def test_load_save_roundtrip_preserves_em_dash():
    """End-to-end: save_json -> load_json on a struct with em-dash returns
    the same Python string. Default ensure_ascii=True is fine — what matters
    is that the round-trip is byte-stable through Python."""
    payload = {"sourceAuthor": CLEAN_AUTHOR, "notes": f"From {CLEAN_AUTHOR}"}

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        path = f.name
    try:
        save_json(path, payload)
        # Verify on-disk format: ensure_ascii=True writes —, not raw —.
        on_disk = open(path, "rb").read()
        assert b"\\u2014" in on_disk, "save_json should escape U+2014 (ensure_ascii=True)"
        assert b"\\u00e2\\u0080\\u0094" not in on_disk, "no mojibake on disk"

        loaded = load_json(path)
        assert loaded["sourceAuthor"] == CLEAN_AUTHOR
        assert loaded["notes"] == f"From {CLEAN_AUTHOR}"
    finally:
        os.unlink(path)


def main():
    tests = [
        test_safe_str_passes_through_clean,
        test_safe_str_passes_through_non_strings,
        test_safe_str_cleans_em_dash_mojibake,
        test_safe_str_cleans_curly_apostrophe_mojibake,
        test_safe_str_no_op_on_partial_marker,
        test_safe_str_no_op_on_undecodable,
        test_apply_accepted_clean_input_stays_clean,
        test_apply_accepted_mojibake_input_is_cleaned,
        test_load_save_roundtrip_preserves_em_dash,
    ]
    failures = []
    for t in tests:
        try:
            t()
        except AssertionError as e:
            failures.append(f"  {t.__name__}: {e}")
        except Exception as e:
            failures.append(f"  {t.__name__}: {type(e).__name__}: {e}")

    if failures:
        print(f"FAIL — {len(failures)} of {len(tests)} cases:")
        for line in failures:
            print(line)
        return 1
    print(f"OK — {len(tests)} cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
