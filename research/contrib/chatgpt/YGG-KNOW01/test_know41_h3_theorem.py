"""Source-free proof tests: no synthetic FIT/HELD first use."""
import unittest
from fractions import Fraction

from know41_active_evaluator_dev import create_tape, v3
from know41_h3_theorem import certificate, mean_regret, OLD_H3, NEW_H3
from know41_active_identifiability_dev import expected_milli


class Know41PreprimaryImpossibility(unittest.TestCase):
    def test_exact_analytic_h3_v1_was_impossible_without_outcomes(self):
        doc = v3()
        self.assertTrue(doc["no_held_source_first_use"])
        self.assertEqual(doc["prospective_change"]["only_superseded_rule"],
                         "v1 H3, inherited unchanged by v2")
        self.assertEqual(Fraction(str(doc["prospective_change"]["new_H3_margin"])),
                         NEW_H3)
        a = certificate()
        for theta in (0, 1):
            r = a[str(theta)]
            self.assertEqual(r["passive_regret"], Fraction(3, 80))
            self.assertEqual(r["oracle_regret"], 0)
            self.assertGreater(OLD_H3, r["maximum_improvement_over_passive"])
        self.assertEqual(a["0"]["no_memory_regret"], Fraction(3, 40))
        self.assertEqual(a["1"]["no_memory_regret"], Fraction(1, 40))
        self.assertGreater(a["1"]["no_memory_regret"], NEW_H3)

    def test_no_regret_can_go_below_zero(self):
        for theta in (0, 1):
            for mask in range(256):
                r = mean_regret(theta, lambda c, mask=mask: (mask >> c) & 1)
                self.assertGreaterEqual(r, Fraction(0))
        self.assertEqual(expected_milli("FORK", 0, 0, 0), 350)

    def test_frozen_first_use_blocked_even_with_injected_provider(self):
        p = v3()
        self.assertEqual(p["governance"]["synthetic_first_use"],
                         "NOT_AUTHORIZED_BY_THIS_DOCUMENT")
        # Fail *before* invoking a callback; never see frozen-source seeds.
        calls = []
        def spy(seed, t, c):
            calls.append((seed, t, c))
            raise AssertionError("frozen source was called")
        for seed in (41003, 41101, 41201):
            with self.assertRaisesRegex(ValueError, "FROZEN_FIRST_USE_DENIED"):
                create_tape(seed, spy)
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
