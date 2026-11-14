"""MD35 fitted model-based Bellman route use; unreserved toy physics only.

The previous shared policy bypassed the fitted 40-backup planner. These
tests deliberately give planning and generic prediction contrary choices,
so regression catches silent planner substitution. No protected first use.
"""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "dg1-md34-20261114"))

from test_models import toy_block, toy_world
from public_policy import choose_route, one_public_episode, four_episode_block
from model_based_rl import ModelBasedRL
from ablations import ModelBasedWithoutRetainedBelief


class ContraryPlanner:
    """Toy action planner: generic scores favor route1, Q planner favors 0."""
    def __init__(self, choice=0):
        self.choice = choice
        self.plans = []
        self.receipts = []

    def checkpoint(self):
        return {"kind": "mechanical-test-not-trained"}

    def begin_block(self):
        self.plans = []
        self.receipts = []

    def predict_target(self, context, route):
        return ((0.25, 0.25, 0.25, 0.25) if route == 0
                else (1.0, 0.0, 0.0, 0.0))

    def plan_route(self, context):
        self.plans.append(context)
        return self.choice

    def update(self, episode):
        self.receipts.append(episode)


class MD35FittedPlannerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.toy = toy_block()
        cls.public_toy_training = (cls.toy,) * 384

    def test_fitted_q_overrides_contrary_generic_predictive_selection(self):
        p = ContraryPlanner()
        p.begin_block()
        self.assertEqual(choose_route(p, 0, arm="trained"), 0)
        self.assertEqual(p.plans, [0])
        self.assertEqual(choose_route(p, 0, arm="no_diagnostic"), 1)
        self.assertEqual(p.plans, [0])
        self.assertEqual(choose_route(p, 0, arm="route0_only"), 0)
        self.assertEqual(p.plans, [0])

    def test_real_physical_episode_uses_fitted_plan_and_charges_probe(self):
        p = ContraryPlanner()
        p.begin_block()
        ep = one_public_episode(toy_world(0), p, expected_context=0)
        self.assertEqual(p.plans, [0])
        self.assertEqual(ep.route(), 0)
        self.assertEqual(len(ep.events), 4)
        self.assertIsNotNone(ep.diagnostic())
        self.assertEqual(ep.diagnostic()[3], -0.09)
        self.assertEqual(p.receipts, [ep])
        q = ContraryPlanner()
        q.begin_block()
        no_diag = one_public_episode(toy_world(0), q,
                                     expected_context=0, arm="no_diagnostic")
        self.assertEqual(no_diag.route(), 1)
        self.assertEqual(len(no_diag.events), 3)
        self.assertIsNone(no_diag.diagnostic())
        self.assertEqual(q.plans, [])

    def test_invalid_fitted_route_cannot_reach_world_step(self):
        for invalid in (True, False, -1, 2, "1", None):
            with self.subTest(choice=invalid):
                p = ContraryPlanner(invalid)
                p.begin_block()
                with self.assertRaisesRegex(AssertionError, "NONPHYSICAL_FITTED_ROUTE"):
                    one_public_episode(toy_world(0), p, expected_context=0)
                self.assertEqual(p.receipts, [])
        with self.assertRaisesRegex(AssertionError, "INVALID_PUBLIC_CONTEXT"):
            choose_route(ContraryPlanner(), 4)
        p = ContraryPlanner()
        p.plan_route = 1
        with self.assertRaisesRegex(AssertionError, "NONCALLABLE_FITTED_PLANNER"):
            choose_route(p, 0)

    def test_real_trained_rl_and_no_memory_negative_share_q_policy(self):
        # Purely repeated handcrafted toy physical receipts, not MD35 cohorts.
        fitted = ModelBasedRL().fit(self.public_toy_training)
        baseline_checkpoint = fitted.checkpoint()
        fitted.begin_block()
        expected = fitted.plan_route(0)
        self.assertEqual(choose_route(fitted, 0), expected)
        self.assertEqual(fitted.fitted_backups, 40)
        control = ModelBasedWithoutRetainedBelief(fitted)
        control.begin_block()
        self.assertEqual(choose_route(control, 0), expected)
        first_plan = control.plan_route(0)
        self.assertEqual(first_plan, expected)
        episodes = []
        for i in range(4):
            ep = one_public_episode(toy_world(i), control,
                                    expected_context=i, arm="trained")
            episodes.append(ep)
            self.assertEqual(fitted._block_episodes, 0)
            self.assertEqual(fitted._local_success.sum(), 0)
            self.assertEqual(fitted._local_failure.sum(), 0)
        self.assertEqual(len(episodes), 4)
        self.assertEqual(fitted.checkpoint(), baseline_checkpoint)
        with self.assertRaisesRegex(AssertionError, "NEGATIVE_PUBLIC_CONTEXT_ORDER"):
            control.plan_route(0)

    def test_full_four_episode_fitted_rl_charges_physical_actions(self):
        fitted = ModelBasedRL().fit(self.public_toy_training)
        checkpoint = fitted.checkpoint()
        cohort = four_episode_block([toy_world(i) for i in range(4)], fitted)
        self.assertEqual(len(cohort), 4)
        self.assertEqual([x.context for x in cohort], list(range(4)))
        self.assertEqual(fitted.checkpoint(), checkpoint)
        self.assertEqual(fitted._block_episodes, 4)
        self.assertTrue(all(len(ep.events) in (3, 4) for ep in cohort))


if __name__ == "__main__":
    unittest.main()
