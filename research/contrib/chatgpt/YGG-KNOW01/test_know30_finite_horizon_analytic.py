"""KNOW30 exact mathematical counterexample tests. No trials or data generation."""
import unittest
from fractions import Fraction

from know30_finite_horizon_analytic import (
    ACTIONS, TARGET, WORLDS, after_action, analytic_result, brier,
    evidence_update, greedy_action, optimal_risk, partition,
    verify_frozen_protocol,
)


def independent_one_step_risk(action):
    """Independent world-by-world enumeration, not the dynamic programmer."""
    acc = Fraction(0)
    for world in WORLDS:
        bit = ACTIONS[action][world]
        group = [w for w in WORLDS if ACTIONS[action][w] == bit]
        p = Fraction(sum(TARGET[w] for w in group), len(group))
        acc += ((1 - p) * (1 - p) if TARGET[world] else p * p) / len(WORLDS)
    return acc


class KNOW30AnalyticTests(unittest.TestCase):
    def test_prereg_source_blob_and_invariants(self):
        p = verify_frozen_protocol()
        self.assertEqual(p["frozen_expectations"]["two_step_advantage"], "1/12")
        self.assertFalse(p["execution"]["native_weights_changed"])
        self.assertFalse(p["execution"]["original_first_use_426"] if "original_first_use_426" in p["execution"] else p["execution"]["protected_original_426"])

    def test_initial_target_risk(self):
        self.assertEqual(brier(WORLDS), Fraction(2, 9))

    def test_one_step_independent_enumeration_and_greedy(self):
        expected = {"a": Fraction(2, 15), "b": Fraction(2, 15),
                    "c": Fraction(1, 9)}
        for a in ACTIONS:
            self.assertEqual(after_action(WORLDS, a, (), 0), expected[a])
            self.assertEqual(independent_one_step_risk(a), expected[a])
        self.assertEqual(greedy_action(WORLDS, tuple(ACTIONS)), "c")

    def test_two_step_conditional_bayes_risks(self):
        expected = {"a": Fraction(0), "b": Fraction(0),
                    "c": Fraction(1, 12)}
        for a in ACTIONS:
            rest = tuple(k for k in ACTIONS if k != a)
            self.assertEqual(after_action(WORLDS, a, rest, 1), expected[a])
        self.assertEqual(optimal_risk(WORLDS, tuple(ACTIONS), 2), 0)

    def test_public_observation_recovery_without_oracle(self):
        self.assertEqual(evidence_update(WORLDS, "a", 1), (0,))
        after_a_zero = evidence_update(WORLDS, "a", 0)
        self.assertEqual(evidence_update(after_a_zero, "b", 1), (1,))
        self.assertEqual(evidence_update(after_a_zero, "b", 0), (2, 3, 4, 5))
        self.assertEqual(brier(evidence_update(after_a_zero, "b", 0)), 0)

    def test_denied_hidden_or_impossible_witness(self):
        with self.assertRaisesRegex(ValueError, "KNOW30_UNKNOWN_ACTION"):
            partition(WORLDS, "private_hidden_world")
        with self.assertRaisesRegex(ValueError, "KNOW30_INVALID_WITNESS"):
            evidence_update(WORLDS, "a", 2)
        with self.assertRaisesRegex(ValueError, "KNOW30_IMPOSSIBLE_WITNESS"):
            evidence_update((0,), "a", 0)

    def test_budget_and_exact_verdict(self):
        with self.assertRaisesRegex(ValueError, "KNOW30_ACTION_BUDGET"):
            optimal_risk(WORLDS, tuple(ACTIONS), 4)
        r = analytic_result()
        self.assertEqual(r["two_step_avoidable_risk"], "1/12")
        self.assertEqual(r["greedy_first"], "c")
        self.assertEqual(r["optimal_two_step_first"], "a")
        self.assertEqual(r["scientific_result"], "NO_NATIVE_GAIN_OR_CAUSAL_ATTRIBUTION")
        self.assertFalse(r["original_world_first_use"])


if __name__ == "__main__":
    unittest.main()
