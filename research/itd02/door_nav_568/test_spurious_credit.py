"""Source-free counterexample: eligibility alone can reward an irrelevant action.

This is a falsification fixture, not an original DoorKey result.
"""
import unittest
from eligibility_local_cells import EligibilityLocalCells
from public_transition_planner import PublicTransitionPlanner

class SpuriousCreditTests(unittest.TestCase):
    def test_unrelated_earlier_action_receives_terminal_reward(self):
        native = EligibilityLocalCells()
        planner = PublicTransitionPlanner()
        # Action 1 is an irrelevant detour. The next state has the same reward
        # regardless of the previous action; local traces cannot identify that.
        for agent in (native, planner):
            agent.observe(b"start", [0, 1])
            agent.learn(1, b"middle", 0, False)
            agent.observe(b"middle", [2])
            agent.learn(2, b"goal", 1, True)
        native.observe(b"start", [0, 1])
        planner.observe(b"start", [0, 1])
        self.assertEqual(native.choose(), 1)
        self.assertEqual(planner.choose(horizon=2), 1)
        # Neither mechanism has counterfactual evidence that action 1 caused
        # the reward. These decisions must not be labeled causal learning.

    def test_trace_window_prevents_unbounded_old_credit(self):
        native = EligibilityLocalCells(trace_limit=2)
        for frame, action, nxt, reward, done in (
            (b"first", 1, b"middle1", 0, False),
            (b"middle1", 2, b"middle2", 0, False),
            (b"middle2", 3, b"goal", 1, True),
        ):
            native.observe(frame, [action])
            native.learn(action, nxt, reward, done)
        native.observe(b"first", [0, 1])
        self.assertEqual(native.choose(), 0)
        native.observe(b"middle1", [0, 2])
        self.assertEqual(native.choose(), 2)

if __name__ == "__main__":
    unittest.main()
