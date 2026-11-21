"""Source-free exact checks of a conventional planning control; no trials."""
import unittest
from fractions import Fraction as F

from know42_predictive_cost_planner_dev import plan, analytical_example


class Know42PredictiveCostPlanner(unittest.TestCase):
    def test_expected_reward_and_cost_can_justify_exploration(self):
        rows = analytical_example()
        self.assertEqual([r["optimal_action"] for r in rows], [0, 1, 1, 1, 1])
        self.assertEqual([r["greedy_action"] for r in rows], [0] * 5)
        self.assertEqual([F(r["gain"]) for r in rows],
                         [F(0), F(1, 50), F(9, 100), F(1663, 10000),
                          F(1213, 5000)])

    def test_independent_two_step_expansion(self):
        # First a1 reward .35; posterior after success favors H1 7/8;
        # predictive a1 net .575. After failure use a0 net .4.
        # P(success)=.4, P(failure)=.6: total .35+.4*.575+.6*.4=.82.
        step = ((400, 100), (400, 700))
        r = plan((F(1, 2), F(1, 2)), (step, step))
        self.assertEqual(r["conditional_values"], (F(4, 5), F(41, 50)))
        self.assertEqual(r["expected_net_utility"], F(41, 50))
        self.assertEqual(r["action"], 1)

    def test_negative_no_information_or_excessive_cost(self):
        w = (F(1, 2), F(1, 2))
        same = ((400, 400), (400, 400))
        for h in range(1, 6):
            r = plan(w, (same,) * h)
            self.assertEqual(r["action"], 0)
            self.assertEqual(r["expected_net_utility"], h * F(2, 5))
        uncertain = ((400, 100), (400, 700))
        self.assertEqual(plan(w, (uncertain,) * 5, (0, 1000))["action"], 0)

    def test_degenerate_and_context_dependent_predictions(self):
        w = (F(1), F(0))
        first, second = ((0, 1000), (1000, 0)), ((1000, 0), (0, 1000))
        r = plan(w, (first, second), (0, 50))
        self.assertEqual(r["action"], 1)
        self.assertEqual(r["expected_net_utility"], F(39, 20))
        self.assertLessEqual(r["states_evaluated"], 21)

    def test_reject_invalid_parameters_and_bound_compute(self):
        w = (F(1, 2), F(1, 2))
        step = ((400, 100), (400, 700))
        for invalid in ((), (step,) * 6):
            with self.assertRaisesRegex(ValueError, "HORIZON"):
                plan(w, invalid)
        with self.assertRaisesRegex(ValueError, "WEIGHTS"):
            plan((F(2), F(0)), (step,))
        with self.assertRaisesRegex(ValueError, "FORECAST_VALUES"):
            plan(w, (((400, True), (400, 700)),))
        with self.assertRaisesRegex(ValueError, "COSTS"):
            plan(w, (step,), (0, -1))
        with self.assertRaisesRegex(ValueError, "POLICY"):
            plan(w, (step,), policy="oracle")
        self.assertLessEqual(plan(w, (step,) * 5)["states_evaluated"],
                             1 + 4 + 16 + 64 + 256)


if __name__ == "__main__":
    unittest.main()
