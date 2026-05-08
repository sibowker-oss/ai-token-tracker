"""Unit tests for scripts/apply_handlers/_variance_gate.py (wq-100).

Covers each branch of D3 / D4 / D5 plus the §5 edge case 3
absolute-magnitude floor. Run via:

    python3 -m unittest tests.test_variance_gate
"""

import os
import sys
import unittest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "scripts"))

from apply_handlers import _shared as S  # noqa: E402
from apply_handlers import _variance_gate as VG  # noqa: E402


def make_write(*, slug="cursor-(anysphere)", year_key="2026", field_key="arr",
               value=2.0, unit="$B", tier="tier_2A", claim_id="dp-test"):
    prov = {"id": claim_id, "tier": tier}
    return S.FieldWrite(
        entity_slug=slug,
        year_key=year_key,
        field_key=field_key,
        value=value,
        unit=unit,
        prov_entry=prov,
        label=f"{slug}.{field_key}@{year_key}={value}{unit}",
    )


def make_entity(*, slug="cursor-(anysphere)", current=None, financials=None,
                provenance=None):
    return {
        "slug": slug,
        "name": slug,
        "current": current or {},
        "financials": financials or {},
        "provenance": provenance or {},
    }


class TestVarianceBands(unittest.TestCase):
    """D5 — variance bands."""

    def test_under_15pct_auto_applies(self):
        # Prior $2B, incoming $2.2B = +10% → auto
        ent = make_entity(financials={"2026": {"arr": 2.0}})
        w = make_write(value=2.2)
        d = VG.evaluate(w, ent)
        self.assertEqual(d.bucket, "auto_apply")
        self.assertAlmostEqual(d.variance, 0.10, places=4)

    def test_just_over_15pct_routes_to_review(self):
        # Prior $2B, incoming $2.4B = +20% → review (variance band ≥15%)
        ent = make_entity(financials={"2026": {"arr": 2.0}})
        w = make_write(value=2.4)
        d = VG.evaluate(w, ent)
        self.assertEqual(d.bucket, "review")

    def test_30pct_routes_to_review(self):
        ent = make_entity(financials={"2026": {"arr": 2.0}})
        w = make_write(value=2.6)  # +30%
        d = VG.evaluate(w, ent)
        self.assertEqual(d.bucket, "review")

    def test_over_50pct_anomaly(self):
        ent = make_entity(financials={"2026": {"arr": 2.0}})
        w = make_write(value=4.0)  # +100%
        d = VG.evaluate(w, ent)
        self.assertEqual(d.bucket, "anomaly")
        self.assertGreater(d.variance, 0.50)


class TestFirstTimeEntity(unittest.TestCase):
    """D4 — first-time entity values ALWAYS go to review even if D3 conditions
    would otherwise pass."""

    def test_no_prior_routes_to_review(self):
        ent = make_entity(financials={})
        w = make_write(value=2.0)
        d = VG.evaluate(w, ent)
        self.assertEqual(d.bucket, "review")
        self.assertTrue(d.is_first_time)

    def test_other_year_present_but_target_year_missing_routes_to_review(self):
        ent = make_entity(financials={"2024": {"arr": 1.0}})  # not 2026
        w = make_write(year_key="2026", value=2.0)
        d = VG.evaluate(w, ent)
        self.assertEqual(d.bucket, "review")
        self.assertTrue(d.is_first_time)

    def test_prior_zero_treated_as_first_time(self):
        ent = make_entity(financials={"2026": {"arr": 0}})
        w = make_write(value=1.0)
        d = VG.evaluate(w, ent)
        self.assertEqual(d.bucket, "review")
        self.assertTrue(d.is_first_time)


class TestAbsoluteMagnitudeFloor(unittest.TestCase):
    """§5 edge case 3 — when both prior and incoming are <$50M, gate
    routes to review regardless of percentage delta."""

    def test_both_below_floor_routes_to_review(self):
        # Prior $10M ($0.01B), incoming $40M ($0.04B) → 300% but immaterial
        ent = make_entity(financials={"2026": {"arr": 0.01}})
        w = make_write(value=0.04)
        d = VG.evaluate(w, ent)
        self.assertEqual(d.bucket, "review")
        self.assertTrue(d.floor_breached)

    def test_one_above_floor_uses_variance_band(self):
        # Prior $40M ($0.04B), incoming $200M ($0.20B) → 400% anomaly
        ent = make_entity(financials={"2026": {"arr": 0.04}})
        w = make_write(value=0.20)
        d = VG.evaluate(w, ent)
        self.assertIn(d.bucket, ("anomaly", "review"))
        self.assertFalse(d.floor_breached)

    def test_floor_does_not_apply_to_non_dollar_field(self):
        # employee_count is not in DOLLAR_FIELDS — variance band should fire
        ent = make_entity(financials={"2026": {"employee_count": 10}})
        w = make_write(field_key="employee_count", value=11, unit="count")
        d = VG.evaluate(w, ent)
        self.assertEqual(d.bucket, "auto_apply")  # 10% delta


class TestProvenanceRank(unittest.TestCase):
    """D3-d — incoming tier must be ≥ existing tier."""

    def test_weaker_provenance_routes_to_review(self):
        # Existing entry with tier_1B; incoming tier_2A — even with small
        # variance, gate routes to review.
        ent = make_entity(
            financials={"2026": {"arr": 2.0}},
            provenance={
                "2026.arr": {
                    "claim_count": 1,
                    "claims": [{"id": "dp-001", "tier": "tier_1B"}],
                },
            },
        )
        w = make_write(value=2.05, tier="tier_2A")  # 2.5% variance
        d = VG.evaluate(w, ent)
        self.assertEqual(d.bucket, "review")
        self.assertEqual(d.existing_tier, "tier_1B")
        self.assertEqual(d.incoming_tier, "tier_2A")

    def test_same_or_higher_provenance_auto_applies(self):
        ent = make_entity(
            financials={"2026": {"arr": 2.0}},
            provenance={
                "2026.arr": {
                    "claim_count": 1,
                    "claims": [{"id": "dp-001", "tier": "tier_2A"}],
                },
            },
        )
        w = make_write(value=2.05, tier="tier_1B")
        d = VG.evaluate(w, ent)
        self.assertEqual(d.bucket, "auto_apply")


class TestEdgeCases(unittest.TestCase):

    def test_unresolved_entity_routes_to_review(self):
        w = make_write()
        d = VG.evaluate(w, None)
        self.assertEqual(d.bucket, "review")
        self.assertIn("entity_unresolved", d.reason)

    def test_non_numeric_prior_routes_to_review(self):
        ent = make_entity(financials={"2026": {"arr": "approximately 2"}})
        w = make_write(value=2.0)
        d = VG.evaluate(w, ent)
        self.assertEqual(d.bucket, "review")
        self.assertIn("non_numeric", d.reason)


class TestBriefAcceptance(unittest.TestCase):
    """§3 acceptance criteria #2 — brief states explicit examples."""

    def test_acceptance_2_verified_tier1B_5pct_auto_applies(self):
        ent = make_entity(financials={"2026": {"arr": 2.0}})
        w = make_write(value=2.1, tier="tier_1B")  # +5%
        d = VG.evaluate(w, ent)
        self.assertEqual(d.bucket, "auto_apply")

    def test_acceptance_2_verified_tier1B_20pct_routes_to_review(self):
        ent = make_entity(financials={"2026": {"arr": 2.0}})
        w = make_write(value=2.4, tier="tier_1B")  # +20%
        d = VG.evaluate(w, ent)
        self.assertEqual(d.bucket, "review")

    def test_acceptance_2_tier3A_handled_at_apply_layer(self):
        # Tier 3A claims never reach the variance gate — they fail the
        # wq-098 D2 gate (is_auto_apply) at handler dispatch. We assert
        # that here for completeness.
        claim = {"sourceType": "podcast_discussion", "confidence": "verified"}
        self.assertEqual(S.derive_tier(claim), "tier_3A")
        self.assertFalse(S.is_auto_apply(claim))


if __name__ == "__main__":
    unittest.main()
