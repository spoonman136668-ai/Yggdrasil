"""Delayed reward credit and misleading reward controls, source-free."""
import unittest
from eligibility_local_cells import EligibilityLocalCells
from state_local_cells import StateLocalActionCells
from public_transition_planner import PublicTransitionPlanner

class EligibilityTests(unittest.TestCase):
    def test_delayed_reward_changes_earlier_action(self):
        native = EligibilityLocalCells()
        baseline = StateLocalActionCells()
        planner = PublicTransitionPlanner()
        for agent in (native, baseline, planner):
            agent.observe(b"start", [0, 1])
            agent.learn(1, b"middle", 0, False)
            agent.observe(b"middle", [2])
            agent.learn(2, b"goal", 1, True)
        native.observe(b"start", [0, 1])
        baseline.observe(b"start", [0, 1])
        planner.observe(b"start", [0, 1])
        self.assertEqual(native.choose(), 1)
        self.assertEqual(baseline.choose(), 0)
        self.assertEqual(planner.choose(horizon=2), 1)

    def test_terminal_negative_reward_does_not_promote_trace(self):
        native = EligibilityLocalCells()
        native.observe(b"start", [0, 1])
        native.learn(1, b"middle", 0, False)
        native.observe(b"middle", [2])
        native.learn(2, b"bad", -1, True)
        native.observe(b"start", [0, 1])
        self.assertEqual(native.choose(), 0)

    def test_no_credit_across_episode_boundary(self):
        native = EligibilityLocalCells()
        native.observe(b"first", [1])
        native.learn(1, b"terminal", 0, True)
        native.observe(b"second", [2])
        native.learn(2, b"goal", 1, True)
        native.observe(b"first", [0, 1])
        self.assertEqual(native.choose(), 0)

if __name__ == "__main__":
    unittest.main()
