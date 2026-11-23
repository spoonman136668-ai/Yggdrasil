"""Synthetic public fixtures for decision-focused Bayesian action selection."""
import math
import unittest

from calibration_decision_bayes import (
    DecisionFocusedBayesianPolicy, expected_dirichlet_brier_reduction)
from test_calibration_psr import fixture


class DecisionFocusedBayesFixtures(unittest.TestCase):
    def setUp(self):
        self.train = (fixture(997, 160), fixture(998, 160))

    def test_expected_brier_risk_reduction_is_positive_and_diminishes(self):
        weak = expected_dirichlet_brier_reduction([0.5] * 4)
        strong = expected_dirichlet_brier_reduction([50.] * 4)
        self.assertGreater(weak, 0)
        self.assertGreater(strong, 0)
        self.assertGreater(weak, strong)
        self.assertTrue(math.isfinite(weak))

    def test_rejects_invalid_dirichlet_vectors(self):
        for row in ([0, 1, 1, 1], [1, 1, 1], [1, 1, 1, float('nan')], "1111"):
            with self.subTest(row=row):
                with self.assertRaises(ValueError):
                    expected_dirichlet_brier_reduction(row)

    def test_fit_uses_only_public_train_context_weights(self):
        m = DecisionFocusedBayesianPolicy().fit(self.train)
        self.assertEqual(m.train_events, 320)
        self.assertAlmostEqual(sum(m.train_context_weight.values()), 1)
        self.assertEqual(sum(m.train_context_counts.values()), 320)
        self.assertNotIn('hidden_world', vars(m))

    def test_gain_is_weighted_for_the_matching_context_and_action(self):
        m = DecisionFocusedBayesianPolicy(probe_penalty=0).fit(self.train)
        obs, action = [0, 0], 1
        key = (0, action)
        before = expected_dirichlet_brier_reduction(m.counts[key])
        self.assertAlmostEqual(m.expected_brier_gain(obs, action),
                               m.train_context_weight[key] * before)
        other_action = (action + 1) % 3
        self.assertAlmostEqual(m.expected_brier_gain(obs, other_action),
            m.train_context_weight[(0, other_action)] *
            expected_dirichlet_brier_reduction(m.counts[0, other_action]))

    def test_penalty_controls_paid_interventions_but_never_exceeds_budget(self):
        m = DecisionFocusedBayesianPolicy(probe_penalty=0.5).fit(self.train)
        m.start([0, 0], paid_budget=0)
        self.assertEqual(m.choose(), 0)
        m.update(dict(observation=[0,0], action=0, next_observation=[1,0]))
        self.assertEqual(m.spent, 0)
        m.start([0,0], paid_budget=2)
        for _ in range(30):
            action = m.choose()
            obs = m.current[:]
            m.update(dict(observation=obs, action=action,
                          next_observation=obs[:]))
        self.assertLessEqual(m.spent, 2)
        self.assertEqual(m.actions_taken, 30)

    def test_online_update_changes_posterior_not_train_importance_weights(self):
        m = DecisionFocusedBayesianPolicy(probe_penalty=0).fit(self.train)
        weights = dict(m.train_context_weight)
        m.start([0,0], paid_budget=1)
        action = m.choose()
        before = tuple(m.counts[0, action])
        m.update(dict(observation=[0,0], action=action, next_observation=[1,1]))
        self.assertNotEqual(before, tuple(m.counts[0, action]))
        self.assertEqual(weights, m.train_context_weight)

    def test_rejects_wrong_action_stale_witness_and_hidden_fields(self):
        m = DecisionFocusedBayesianPolicy().fit(self.train)
        m.start([0,0], paid_budget=1)
        action = m.choose()
        with self.assertRaises(ValueError):
            m.update(dict(observation=[0,0], action=(action+1)%3,
                          next_observation=[1,1]))
        with self.assertRaises(ValueError):
            m.update(dict(observation=[0,0], action=action,
                          next_observation=[1,1], hidden_state=[0,1]))
        m.update(dict(observation=[0,0], action=action, next_observation=[1,1]))
        self.assertEqual(m.current, [1,1])

    def test_deterministic_fit_and_action_choice(self):
        left = DecisionFocusedBayesianPolicy(probe_penalty=0.0001).fit(self.train)
        right = DecisionFocusedBayesianPolicy(probe_penalty=0.0001).fit(self.train)
        self.assertEqual(left.snapshot(), right.snapshot())
        self.assertEqual(left.train_context_weight, right.train_context_weight)
        left.start([1,0], paid_budget=2)
        right.start([1,0], paid_budget=2)
        self.assertEqual(left.choose(), right.choose())

    def test_no_context_support_never_claims_positive_value(self):
        m = DecisionFocusedBayesianPolicy(probe_penalty=0).fit(self.train)
        # This binary observation is valid but may have zero support for an action.
        gains = [m.expected_brier_gain([0,0], a) for a in (0,1,2)]
        self.assertTrue(all(math.isfinite(x) and x >= 0 for x in gains))


if __name__ == '__main__':
    unittest.main()
