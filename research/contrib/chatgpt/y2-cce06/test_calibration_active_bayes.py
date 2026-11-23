"""Active Bayesian fixture only; no calibrated or protected causal source."""
import math
import unittest
from calibration_active_bayes import (
    ActiveBayesianPolicy, posterior_information_gain, COST)
from test_calibration_psr import fixture


class ActiveBayesianFixtures(unittest.TestCase):
    def setUp(self):
        self.train = (fixture(997, 160), fixture(998, 160))

    def test_dirichlet_exact_information_gain_decreases_with_evidence(self):
        weak = posterior_information_gain([0.5] * 4)
        strong = posterior_information_gain([50.] * 4)
        self.assertGreater(weak, strong)
        self.assertGreater(strong, 0)
        self.assertTrue(math.isfinite(weak))

    def test_posterior_normalization_and_public_only_fit(self):
        m = ActiveBayesianPolicy().fit(self.train)
        self.assertEqual(m.fit_events, 320)
        self.assertAlmostEqual(sum(m.posterior([0,0], 1)), 1)
        self.assertNotIn('hidden_world', vars(m))

    def test_action_budget_enforced_even_after_repeated_steps(self):
        m = ActiveBayesianPolicy(probe_penalty=0).fit(self.train)
        m.start([0, 0], paid_budget=2)
        for i in range(24):
            act = m.choose()
            before = m.current[:]
            m.update({'observation':before,'action':act,'next_observation':before[:]})
        self.assertLessEqual(m.spent, 2)
        self.assertEqual(m.actions_taken, 24)
        self.assertIn(act, COST)

    def test_pending_outcome_and_wrong_action_rejected(self):
        m = ActiveBayesianPolicy().fit(self.train)
        m.start([0,1], paid_budget=2)
        act = m.choose()
        with self.assertRaises(ValueError):
            m.choose()
        with self.assertRaises(ValueError):
            m.update({'observation':[0,1], 'action':(act+1)%3,
                      'next_observation':[0,0]})
        with self.assertRaises(ValueError):
            m.update({'observation':[0,1], 'action':act,
                      'next_observation':[0,0], 'oracle':1})
        m.update({'observation':[0,1], 'action':act,'next_observation':[1,0]})
        self.assertEqual(m.current, [1,0])

    def test_no_budget_chooses_only_no_action(self):
        m = ActiveBayesianPolicy(probe_penalty=0).fit(self.train)
        m.start([1,1], paid_budget=0)
        self.assertEqual(m.choose(), 0)
        self.assertEqual(m.spent, 0)

    def test_posterior_update_changes_only_selected_public_context(self):
        m = ActiveBayesianPolicy(probe_penalty=0).fit(self.train)
        before = m.posterior([0,0], 2)
        other = m.posterior([1,1], 2)
        m.start([0,0], paid_budget=1)
        act = m.choose()
        chosen_before = m.posterior([0,0], act)
        m.update({'observation':[0,0], 'action':act,'next_observation':[1,1]})
        self.assertNotEqual(chosen_before, m.posterior([0,0], act))
        self.assertEqual(other, m.posterior([1,1], 2))
        if act != 2:
            self.assertEqual(before, m.posterior([0,0], 2))

    def test_frozen_fit_and_invalid_private_field_rejected(self):
        m = ActiveBayesianPolicy().fit(self.train)
        with self.assertRaises(ValueError):
            m.fit(self.train)
        bad = list(self.train[0]); bad[0] = dict(bad[0], true_latent=[0,0,1])
        with self.assertRaises(ValueError):
            ActiveBayesianPolicy().fit((tuple(bad),))
        for vec in ([0.,0.,0.,0.], [0.5,0.5,0.5,float('nan')]):
            with self.assertRaises(ValueError):
                posterior_information_gain(vec)

    def test_reproducible_policies_and_cold_state_values(self):
        m = ActiveBayesianPolicy(probe_penalty=.1).fit(self.train)
        n = ActiveBayesianPolicy(probe_penalty=.1).fit(self.train)
        self.assertEqual(m.snapshot(), n.snapshot())
        m.start([1,0], paid_budget=1)
        n.start([1,0], paid_budget=1)
        self.assertEqual(m.choose(), n.choose())
        self.assertEqual(m.snapshot(), n.snapshot())


if __name__ == '__main__':
    unittest.main()
