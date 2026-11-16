"""Public first-use runner tests: fixture seed only, no science consumption."""
from __future__ import annotations
from unittest import TestCase
from unittest.mock import patch
import os

import original_public as P
import structural_growth as S

class OriginalRunnerSourceSafeTests(TestCase):
    def test_gated_fixture_and_no_hidden_world_generation(self):
        fixture = S.engineering_fixture_world()
        with patch.object(S, "source_safe_world",
                          side_effect=AssertionError("primary source read")):
            rows = P.run_world(fixture, tier=384, family=0,
                               max_calls=4, include_gru=False)
        self.assertEqual([r["exposure"] for r in rows], [0, 4])
        for row in rows:
            self.assertEqual(set(row["arms"]), set(P.ARM_NAMES))
            for name, arm in row["arms"].items():
                self.assertEqual(arm["source_calls"], row["exposure"])
                self.assertEqual(
                    arm["correct"] + arm["wrong_confident"] + arm["abstained"], 24)
                self.assertEqual(len(arm["predictions"]), 24)
                self.assertTrue(arm["cold_ok"] if name != "SYMBOLIC_ACTIVE"
                                else arm["cold_ok"] is None)
            for n in ("NUMERIC_FIXED3", "NO_UPDATE"):
                self.assertEqual(
                    row["arms"][n]["source_sha256"],
                    row["arms"]["NUMERIC_GROW_PASSIVE"]["source_sha256"])

    def test_original_first_use_requires_exact_owner_gate(self):
        with patch.dict(os.environ, {"WSP120_FIRST_USE_ALLOWED": "",
                                    "GITHUB_RUN_ATTEMPT": "2"}):
            with patch.object(S, "source_safe_world",
                              side_effect=AssertionError("opened primary")):
                with self.assertRaises(PermissionError):
                    P.run_original_shard(0, "Linux")

    def test_invalid_seed_and_gru_budget_rejected(self):
        fixture = S.engineering_fixture_world()
        for kwargs in ({"tier": 256, "family": 0},
                       {"tier": 384, "family": 3},
                       {"tier": 384, "family": 0, "max_calls": 9},
                       {"tier": 384, "family": 0, "max_calls": 4,
                        "include_gru": True}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                P.run_world(fixture, **kwargs)
