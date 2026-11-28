"""Source-free falsification of unconditioned R7 action cells against a planner."""
import unittest
from local_action_cells import LocalActionConsequences
from public_transition_planner import PublicTransitionPlanner

class LocalCellComparison(unittest.TestCase):
    def test_action_cells_cannot_disambiguate_public_states(self):
        local = LocalActionConsequences()
        planner = PublicTransitionPlanner()
        # Two distinct public states require opposite rewarded actions.
        for frame, rewarded in ((b"left", 0), (b"right", 1)):
            for action in (0, 1):
                local.observe(frame, [0, 1])
                local.learn(action, b"next", int(action == rewarded), True)
                planner.observe(frame, [0, 1])
                planner.learn(action, b"next", int(action == rewarded), True)
        local.observe(b"left", [0, 1])
        local_left = local.choose()
        local.observe(b"right", [0, 1])
        local_right = local.choose()
        planner.observe(b"left", [0, 1])
        planner_left = planner.choose(horizon=1)
        planner.observe(b"right", [0, 1])
        planner_right = planner.choose(horizon=1)
        self.assertEqual((planner_left, planner_right), (0, 1))
        self.assertEqual(local_left, local_right)
        self.assertNotEqual((local_left, local_right), (planner_left, planner_right))

if __name__ == "__main__":
    unittest.main()
