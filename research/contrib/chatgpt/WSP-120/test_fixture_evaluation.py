"""Guarded WSP-120 comparison harness tests; no public first-use."""
from __future__ import annotations

from unittest import TestCase
from unittest.mock import patch

import fixture_evaluation as E
import structural_growth as S


class FixtureEvaluationTests(TestCase):
    def test_equal_budget_provenance_and_cold_restore(self):
        result = E.run_fixture(tier=384, family=1, exposure=4)
        self.assertEqual(result["schema"], "wsp120.fixture-evaluation.v1")
        self.assertFalse(result["scientific"])
        self.assertEqual(result["seed"], 120900)
        self.assertEqual(set(result["arms"]), set(E.ARMS))
        self.assertEqual(len(result["receipt_sha256"]), 64)
        for name, record in result["arms"].items():
            with self.subTest(arm=name):
                self.assertEqual(record["source_calls"], 4)
                self.assertEqual(len(record["observations"]), 4)
                self.assertEqual(record["held"], 24)
                self.assertEqual(
                    record["correct"] + record["wrong_confident"]
                    + record["abstained"], 24)
                self.assertEqual(len(record["source_sha256"]), 64)
                self.assertEqual(len(record["predictions"]), 24)
                if name == "SYMBOLIC_ACTIVE":
                    self.assertIsNone(record["cold_ok"])
                else:
                    self.assertTrue(record["cold_ok"])
        p = result["arms"]["NUMERIC_GROW_PASSIVE"]
        for name in ("NUMERIC_FIXED3", "NO_UPDATE"):
            record = result["arms"][name]
            self.assertEqual(record["observations"], p["observations"])
            self.assertEqual(record["source_sha256"], p["source_sha256"])
        self.assertEqual(result["arms"]["NO_UPDATE"]["abstained"], 24)

    def test_preflight_rejects_unfrozen_parameters_and_primary_seed(self):
        for kwargs in ({"tier": 256}, {"tier": True},
                       {"family": 3}, {"family": True},
                       {"exposure": 3}, {"exposure": True},
                       {"exposure": 4, "include_gru": True},
                       {"include_gru": 1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                E.run_fixture(**kwargs)
        original = S.engineering_fixture_world()
        protected = S.World(120000, original.edges, original.targets,
                            original.source_order, original.reveal_order)
        with patch.object(S, "engineering_fixture_world",
                          return_value=protected):
            with self.assertRaisesRegex(PermissionError,
                                        "PRIMARY_FIRST_USE_DENIED"):
                E.run_fixture()

    def test_zero_feedback_remains_unscored_scientifically(self):
        with patch.object(S, "source_safe_world",
                          side_effect=AssertionError("primary opened")):
            first = E.run_fixture(exposure=0, family=2)
            second = E.run_fixture(exposure=0, family=2)
        self.assertFalse(first["scientific"])
        self.assertEqual(first["receipt_sha256"], second["receipt_sha256"])
        for record in first["arms"].values():
            self.assertEqual(record["source_calls"], 0)
            self.assertEqual(record["abstained"], 24)
