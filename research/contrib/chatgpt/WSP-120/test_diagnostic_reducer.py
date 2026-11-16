"""WSP120 scorer tests use fabricated summaries, not generated worlds."""
from copy import deepcopy
from hashlib import sha256
from unittest import TestCase
from unittest.mock import patch

import diagnostic_reducer as D


def summaries(active=17, fixed=10, errors=0):
    rows = []
    for seed in range(130000, 130024):  # labels only; never source access
        for family in D.FAMILIES:
            arms = {}
            for name, count in (("NUMERIC_GROW_ACTIVE", active),
                                ("NUMERIC_GROW_PASSIVE", 11),
                                ("NUMERIC_FIXED3", fixed),
                                ("SYMBOLIC_ACTIVE", 19),
                                ("NO_UPDATE", 0)):
                err = errors if name == "NUMERIC_GROW_ACTIVE" else 0
                basis = ("PASSIVE" if name in
                         ("NUMERIC_GROW_PASSIVE", "NUMERIC_FIXED3", "NO_UPDATE")
                         else name)
                arms[name] = {
                    "correct": count, "wrong_confident": err,
                    "abstained": 24 - count - err, "held": 24,
                    "source_calls": 16,
                    "source_sha256": sha256(
                        f"{seed}/{family}/{basis}".encode()).hexdigest(),
                    "cold_ok": None if name == "SYMBOLIC_ACTIVE" else True,
                }
            rows.append({"seed": seed, "family": family, "tier": 384,
                         "exposure": 16, "arms": arms})
    return rows


class DiagnosticReducerTests(TestCase):
    def test_24_world_pairing_and_controls(self):
        import structural_growth as S
        with patch.object(S, "source_safe_world",
                          side_effect=AssertionError("first-use violation")):
            result = D.reduce_frozen_16_call_diagnostic(summaries())
        self.assertFalse(result["source_accessed"])
        self.assertEqual(result["scientific_status"], "UNVERIFIED")
        self.assertEqual(result["mechanism_signal"], "DEVELOPMENT_SIGNAL")
        self.assertAlmostEqual(result["active_accuracy"], 17 / 24)
        fixed = result["comparisons"]["ACTIVE_MINUS_NUMERIC_FIXED3"]
        self.assertAlmostEqual(fixed["mean_difference"], 7 / 24)
        self.assertGreater(fixed["ci95_lower"], 0)
        self.assertEqual((fixed["resamples"], fixed["seed"]),
                         (10000, 1200))
        self.assertLess(
            result["comparisons"]["ACTIVE_MINUS_SYMBOLIC_ACTIVE"][
                "mean_difference"], 0)
        self.assertEqual(result["comparisons"],
                         D.reduce_frozen_16_call_diagnostic(
                             summaries())["comparisons"])

    def test_errors_and_small_gain_prevent_signal(self):
        self.assertEqual(
            D.reduce_frozen_16_call_diagnostic(
                summaries(errors=1))["mechanism_signal"],
            "NO_DEVELOPMENT_SIGNAL")
        self.assertEqual(
            D.reduce_frozen_16_call_diagnostic(
                summaries(fixed=16))["mechanism_signal"],
            "NO_DEVELOPMENT_SIGNAL")

    def test_fail_closed_on_missing_pairs_receipts_cold_and_budget(self):
        original = summaries()
        cases = [original[:-1]]
        duplicate = deepcopy(original)
        duplicate[-1] = deepcopy(duplicate[0])
        cases.append(duplicate)
        for arm, key, value in (
            ("NUMERIC_FIXED3", "source_calls", 15),
            ("NUMERIC_FIXED3", "source_sha256", "0" * 64),
            ("NUMERIC_GROW_ACTIVE", "source_sha256", ""),
            ("NUMERIC_GROW_ACTIVE", "cold_ok", False),
            ("NUMERIC_GROW_ACTIVE", "correct", 23),
        ):
            c = deepcopy(original)
            c[0]["arms"][arm][key] = value
            cases.append(c)
        bad_config = deepcopy(original)
        bad_config[0]["tier"] = 256
        cases.append(bad_config)
        for i, case in enumerate(cases):
            with self.subTest(i=i), self.assertRaisesRegex(
                    ValueError, "WSP120_DIAGNOSTIC_"):
                D.reduce_frozen_16_call_diagnostic(case)
