"""KNOW28 analytic source/privacy/metric tests. No simulation or held first-use."""
from fractions import Fraction
import unittest

from know28_phase_ambiguity_falsifier import (
    SCHEMA, PROTO, PREREG, PREREG_BLOB, Q_A, Q_B,
    protocol, causal_bit, expected_brier, phase_blind_fork_brier,
    exact_certificate, two_indistinguishable_forks,
    common_pre_return_forecast, proof,
)


class KNOW28AnalyticTests(unittest.TestCase):
    def test_frozen_before_code_and_blob(self):
        p = protocol()
        self.assertEqual(p["schema"], PROTO)
        self.assertEqual(PREREG, "41fbc89a22aa915234454dbf1d41e9a0ad559d8d")
        self.assertEqual(PREREG_BLOB, "34bc59c3fdcf05d1613eb386aa5dd456a4941e71")
        self.assertEqual(p["custody"]["new_held_trials"], 0)
        self.assertFalse(p["custody"]["original_first_use"])

    def test_frozen_rules_disagree_on_unseen_high_context(self):
        self.assertEqual(causal_bit("H0", 4), 0)
        self.assertEqual(causal_bit("H2", 4), 1)
        self.assertEqual((Q_A, Q_B), (Fraction(3, 20), Fraction(17, 20)))
        with self.assertRaises(ValueError):
            causal_bit("H0", True)
        with self.assertRaises(ValueError):
            causal_bit("privileged", 4)

    def test_identical_public_prefix_cannot_reveal_fork(self):
        history = ((0, 0, 0, 1), (1, 1, 2, 0))
        view = (24, 4, 0)
        a, b = two_indistinguishable_forks(history, view)
        self.assertEqual(a, b)
        forecasts = common_pre_return_forecast(
            history, view, lambda observed, nxt: Fraction(3, 5))
        self.assertEqual(forecasts, (Fraction(3, 5), Fraction(3, 5)))
        with self.assertRaises(ValueError):
            two_indistinguishable_forks([], view)

    def test_exact_uniform_branch_lower_bound(self):
        for k in range(101):
            p = Fraction(k, 100)
            loss, cert = exact_certificate(p)
            self.assertEqual(loss, cert)
            self.assertGreaterEqual(loss, Fraction(1, 4))
        self.assertEqual(phase_blind_fork_brier(Fraction(1, 2)),
                         Fraction(1, 4))
        self.assertGreater(phase_blind_fork_brier(Q_A), Fraction(1, 4))
        self.assertGreater(phase_blind_fork_brier(Q_B), Fraction(1, 4))

    def test_privileged_phase_oracle_is_not_fair_control(self):
        oracle = (expected_brier(Q_A, Q_A) + expected_brier(Q_B, Q_B)) / 2
        self.assertEqual(oracle, Fraction(51, 400))
        self.assertEqual(Fraction(1, 4) - oracle, Fraction(49, 400))
        self.assertLess(oracle, phase_blind_fork_brier(Fraction(1, 2)))

    def test_probability_and_policy_negatives(self):
        for invalid in [Fraction(-1, 10), Fraction(11, 10), .5]:
            with self.assertRaises(ValueError):
                expected_brier(invalid, Q_A)
        with self.assertRaises(ValueError):
            common_pre_return_forecast((), (24, 4, 0),
                lambda observed, nxt: .5)

    def test_complete_proof_no_spurious_science_claim(self):
        r = proof()
        self.assertEqual(r["schema"], SCHEMA)
        self.assertEqual(r["result"], "IDENTIFIABILITY_LIMIT_CONFIRMED")
        self.assertEqual(r["phase_blind_min_brier"], .25)
        self.assertEqual(r["privileged_phase_oracle_brier"], .1275)
        self.assertEqual(r["irreducible_preobservation_gap"], .1225)
        self.assertEqual(r["new_held_trials"], 0)
        self.assertEqual(r["new_action_witnesses"], 0)
        self.assertFalse(r["native_modified"])
        self.assertFalse(r["scientific_gain_verified"])
        self.assertEqual(r["deployment"], "NONE")


if __name__ == "__main__":
    unittest.main()
