"""Two-hop source-free action-choice evaluation versus exact-state planner."""
import unittest
from feature_cell_lookahead import FeatureCellLookahead
from public_transition_planner import PublicTransitionPlanner

def fit(native, conventional):
    # Balanced nuisance byte and opposite transition consequences.
    for nuisance in (b"x", b"y"):
        for signal in (b"A", b"B"):
            frame = nuisance+signal+b"-fit"
            for action in (0, 1):
                nxt = b"M-next" if action == (1 if signal == b"A" else 0) else b"D-next"
                for agent in (native, conventional):
                    agent.observe(frame, [0, 1])
                    agent.learn(action, nxt, 0, False)
    for frame, reward in ((b"M-next", 1), (b"D-next", 0)):
        for agent in (native, conventional):
            agent.observe(frame, [2])
            agent.learn(2, b"T-final", reward, True)

class FeatureCellLookaheadTests(unittest.TestCase):
    def test_unfamiliar_public_frame_two_hop_action_selection(self):
        native = FeatureCellLookahead(positions=2)
        conventional = PublicTransitionPlanner()
        fit(native, conventional)
        self.assertEqual(native.model.selected_position, 1)
        for frame, expected in ((b"zA-holdout", 1), (b"zB-holdout", 0)):
            native.observe(frame, [0, 1])
            self.assertEqual(native.choose(horizon=2), expected)
            conventional.observe(frame, [0, 1])
            self.assertEqual(conventional.choose(horizon=2), 0)

    def test_ablation_depth_and_missing_outcome(self):
        native = FeatureCellLookahead(positions=2)
        conventional = PublicTransitionPlanner()
        fit(native, conventional)
        native.observe(b"zA-holdout", [0, 1])
        self.assertEqual(native.choose(horizon=1), 0)
        self.assertEqual(native.choose(horizon=2), 1)
        native.observe(b"zQ-unknown", [0, 1])
        self.assertEqual(native.choose(horizon=2), 0)

    def test_public_owned_action_and_bounded_capacity(self):
        native = FeatureCellLookahead(positions=2, capacity=4)
        native.observe(b"xA-start", [0])
        with self.assertRaises(ValueError):
            native.learn(1, b"M", 1, False)
        native.learn(0, b"M", 0, False)
        native.observe(b"M-next", [2])
        native.learn(2, b"T-final", 1, True)
        self.assertLessEqual(len(native.representatives), native.capacity)
        self.assertLessEqual(len(native.terminal), native.capacity)
        with self.assertRaises(ValueError):
            native.choose(horizon=3)

if __name__ == "__main__":
    unittest.main()
