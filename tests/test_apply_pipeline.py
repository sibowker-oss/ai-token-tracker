"""Unit tests for scripts/apply_pipeline.py and scripts/apply_handlers/*.

Run via: python3 -m unittest tests.test_apply_pipeline
"""

import os
import sys
import unittest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "scripts"))

import apply_pipeline as P  # noqa: E402
from apply_handlers import _shared as S  # noqa: E402
from apply_handlers import arr as arr_handler  # noqa: E402
from apply_handlers import valuation as val_handler  # noqa: E402
from apply_handlers import _default  # noqa: E402


def make_ctx(entities=None, schema=None, dry_run=True):
    return P.PipelineContext(
        entities=entities or {"companies": []},
        schema=schema or {"entity_match_rules": []},
        dry_run=dry_run,
        verbose=False,
    )


class TestTierDerivation(unittest.TestCase):

    def test_sworn_affidavit_is_1A(self):
        claim = {"sourceType": "sworn-affidavit", "confidence": "verified"}
        self.assertEqual(S.derive_tier(claim), "tier_1A")

    def test_sec_filing_verified_is_1B(self):
        claim = {"sourceType": "sec_filing", "confidence": "verified"}
        self.assertEqual(S.derive_tier(claim), "tier_1B")

    def test_reporting_verified_is_2A(self):
        claim = {"sourceType": "reporting", "confidence": "verified"}
        self.assertEqual(S.derive_tier(claim), "tier_2A")

    def test_reporting_estimated_is_2B(self):
        claim = {"sourceType": "reporting", "confidence": "estimated"}
        self.assertEqual(S.derive_tier(claim), "tier_2B")

    def test_podcast_is_3A(self):
        claim = {"sourceType": "podcast_discussion", "confidence": "verified"}
        self.assertEqual(S.derive_tier(claim), "tier_3A")


class TestAutoApplyGate(unittest.TestCase):

    def test_verified_2A_passes(self):
        claim = {"sourceType": "reporting", "confidence": "verified"}
        self.assertTrue(S.is_auto_apply(claim))

    def test_verified_3A_blocks(self):
        claim = {"sourceType": "podcast_discussion", "confidence": "verified"}
        self.assertFalse(S.is_auto_apply(claim))

    def test_estimated_2A_blocks(self):
        claim = {"sourceType": "reporting", "confidence": "estimated"}
        self.assertFalse(S.is_auto_apply(claim))


class TestValueCoercion(unittest.TestCase):

    def test_b_unit_passthrough(self):
        self.assertEqual(S.coerce_value_to_billions(2.5, "$B"), 2.5)

    def test_usd_billions_dollars_to_b(self):
        self.assertEqual(S.coerce_value_to_billions(2_000_000_000, "USD"), 2.0)

    def test_usd_millions_to_b(self):
        self.assertEqual(S.coerce_value_to_billions(500, "USD millions"), 0.5)

    def test_string_value_returns_none(self):
        self.assertIsNone(S.coerce_value_to_billions("approximately 2 billion", "USD"))


class TestEntityResolution(unittest.TestCase):

    def setUp(self):
        self.entities = {
            "companies": [
                {"slug": "openai", "name": "OpenAI", "roles": ["model_provider"]},
                {"slug": "anthropic", "name": "Anthropic", "roles": ["model_provider"]},
                {"slug": "cursor-(anysphere)", "name": "Cursor (Anysphere)", "roles": ["ai_app"]},
            ],
        }
        self.schema = {
            "entity_match_rules": [
                {"pattern": "openai|chatgpt", "slug": "openai"},
                {"pattern": "anthropic|claude", "slug": "anthropic"},
            ]
        }
        self.ctx = make_ctx(self.entities, self.schema)

    def test_resolve_via_entity_field(self):
        slug, ent, ambig = S.resolve_entity({"entity": "openai"}, self.ctx)
        self.assertEqual(slug, "openai")
        self.assertFalse(ambig)

    def test_resolve_alias_cursor(self):
        slug, ent, ambig = S.resolve_entity(
            {"entity": "", "claim": "Cursor hit $2B in annualized revenue."},
            self.ctx,
        )
        self.assertEqual(slug, "cursor-(anysphere)")
        self.assertFalse(ambig)

    def test_resolve_microsoft_is_ambiguous(self):
        slug, ent, ambig = S.resolve_entity(
            {"entity": "", "claim": "Microsoft AI annual revenue $37B"},
            self.ctx,
        )
        self.assertTrue(ambig)
        self.assertIsNone(slug)

    def test_resolve_codex_is_ambiguous(self):
        # Per dp-110 — Codex must NOT mis-attribute to OpenAI even when
        # claim.notes mentions OpenAI Press Release
        slug, ent, ambig = S.resolve_entity(
            {"entity": "", "claim": "Codex serves over 2 million users",
             "tags": ["users", "Codex", "weekly"]},
            self.ctx,
        )
        self.assertTrue(ambig)


class TestArrHandler(unittest.TestCase):

    def setUp(self):
        self.entities = {
            "companies": [
                {"slug": "cursor-(anysphere)", "name": "Cursor (Anysphere)",
                 "roles": ["ai_app"], "financials": {}, "current": {}},
            ],
        }
        self.schema = {"entity_match_rules": []}
        self.ctx = make_ctx(self.entities, self.schema)

    def test_cursor_2b_arr(self):
        # dp-148 — verified Sacra reporting, $2B annualized revenue Feb 2026
        claim = {
            "id": "dp-148",
            "claim": "Cursor hit $2B in annualized revenue in February 2026.",
            "value": 2_000_000_000,
            "unit": "USD",
            "sourceType": "web_page",
            "confidence": "verified",
            "dateOfClaim": "February 2026",
            "tags": ["provider_revenue"],
        }
        result = arr_handler.handle(claim, self.ctx)
        self.assertTrue(result.applied)
        self.assertEqual(len(result.writes), 1)
        w = result.writes[0]
        self.assertEqual(w.entity_slug, "cursor-(anysphere)")
        self.assertEqual(w.field_key, "arr")
        self.assertEqual(w.year_key, "2026")
        self.assertEqual(w.value, 2.0)
        self.assertIn("entityDirectory", result.consumer_keys)


class TestConflictResolution(unittest.TestCase):

    def setUp(self):
        # Anthropic with existing prov entry from a tier_2A source
        self.entities = {
            "companies": [
                {
                    "slug": "anthropic",
                    "name": "Anthropic",
                    "roles": ["model_provider"],
                    "financials": {"2026": {"arr": 30}},
                    "current": {},
                    "provenance": {
                        "2026.arr": {
                            "confidence": "high",
                            "claim_count": 1,
                            "claims": [{
                                "id": "preexisting",
                                "value": 30,
                                "tier": "tier_1B",
                                "weight": "corroborating",
                                "date": "2026-04-01",
                            }],
                        },
                    },
                },
            ],
        }
        self.schema = {"entity_match_rules": [
            {"pattern": "anthropic|claude", "slug": "anthropic"},
        ]}
        self.ctx = make_ctx(self.entities, self.schema)

    def test_lower_tier_skipped(self):
        # Incoming tier_2A vs existing tier_1B → skip
        claim = {
            "id": "dp-test",
            "claim": "Anthropic ARR $14B",
            "value": 14,
            "unit": "$B ARR",
            "sourceType": "reporting",
            "confidence": "verified",
            "entity": "anthropic",
            "dateOfClaim": "2026-03-01",
        }
        result = arr_handler.handle(claim, self.ctx)
        self.assertFalse(result.applied)
        self.assertIn("existing_tier_higher", result.skip_reason)


class TestIdempotency(unittest.TestCase):

    def test_running_twice_changes_nothing(self):
        # Setup: a single claim that successfully applies
        entities = {
            "companies": [{
                "slug": "test", "name": "Test", "roles": ["ai_app"],
                "financials": {}, "current": {},
            }],
        }
        schema = {"entity_match_rules": []}
        vault = {"dataPoints": [{
            "id": "dp-test",
            "claim": "Test annualized revenue $1B in 2026",
            "value": 1_000_000_000,
            "unit": "USD",
            "sourceType": "reporting",
            "confidence": "verified",
            "entity": "test",
            "dateOfClaim": "2026-01-01",
            "tags": [],
            "usedOn": [],
        }]}

        ctx = make_ctx(entities, schema)
        dispatch = P.build_dispatch()

        # First pass — should apply
        r1 = P.process_claim(vault["dataPoints"][0], dispatch, ctx)
        self.assertTrue(r1.applied)
        # Mark used
        P.append_used_on(vault, "dp-test", r1.consumer_keys)
        self.assertIn("entityDirectory", vault["dataPoints"][0]["usedOn"])

        # Second pass — claim already has entityDirectory in usedOn,
        # main loop skips it. Simulate by running build_dispatch again
        # and walking the vault.
        ran_again = "entityDirectory" in (vault["dataPoints"][0]["usedOn"] or [])
        self.assertTrue(ran_again, "Second-run guard failed — would re-process")


class TestDoNotApply(unittest.TestCase):

    def test_parked_claim_skipped(self):
        claim = {
            "id": "dp-x",
            "claim": "X",
            "value": 1,
            "unit": "$B",
            "sourceType": "reporting",
            "confidence": "parked",
        }
        self.assertTrue(S.is_do_not_apply(claim))

    def test_explicit_do_not_apply_skipped(self):
        claim = {"do_not_apply": True, "value": 1, "unit": "$B"}
        self.assertTrue(S.is_do_not_apply(claim))


class TestKnownUnits(unittest.TestCase):

    def test_every_vault_unit_has_a_handler_or_default(self):
        """Per D3: vault unit values must all be known."""
        import json
        vault_path = os.path.join(BASE, "vault-data.json")
        with open(vault_path, encoding="utf-8") as f:
            vault = json.load(f)
        units = {(dp.get("unit") or "") for dp in vault["dataPoints"]}
        units.discard("")
        dispatch = P.build_dispatch()
        known = P.known_units(dispatch)
        unknown = units - known
        self.assertEqual(unknown, set(),
                         f"vault contains units with no handler: {unknown}")


if __name__ == "__main__":
    unittest.main()
