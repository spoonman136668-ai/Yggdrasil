"""Three-step unfamiliar-state decisions, ablation, and fail-closed controls."""
import unittest
from three_step_feature_cells import ThreeStepFeatureCells
from public_transition_planner import PublicTransitionPlanner

def fit(native, baseline):
    # First hop: the informative public bit is at index 1, not nuisance 0.
    for nuisance in (b"x", b"y"):
        for signal in (b"A", b"B"):
            frame = nuisance + signal + b"-training"
            for action in (0, 1):
                correct = action == (1 if signal == b"A" else 0)
                nxt = b"M1-intermediate" if correct else b"D2-intermediate"
                for agent in (native, baseline):
                    agent.observe(frame, [0, 1])
                    agent.learn(action, nxt, 0, False)
    for frame, nxt in ((b"M1-intermediate", b"R3-positive"),
                       (b"D2-intermediate", b"F4-negative")):
        for agent in (native, baseline):
            agent.observe(frame, [2])
            agent.learn(2, nxt, 0, False)
    for frame, reward in ((b"R3-positive", 1), (b"F4-negative", 0)):
        for agent in (native, baseline):
            agent.observe(frame, [3])
            agent.learn(3, b"T0-terminal", reward, True)

class ThreeStepFeatureTests(unittest.TestCase):
    def test_three_step_transfer_outperforms_two_step_ablation(self):
        native = ThreeStepFeatureCells(positions=2)
        baseline = PublicTransitionPlanner()
        fit(native, baseline)
        self.assertEqual(native.model.selected_position, 1)
        for frame, expected in ((b"zA-unfamiliar", 1),
                                (b"zB-unfamiliar", 0)):
            native.observe(frame, [0, 1])
            self.assertEqual(native.choose(horizon=3), expected)
            baseline.observe(frame, [0, 1])
            self.assertEqual(baseline.choose(horizon=3), 0)
        native.observe(b"zA-unfamiliar", [0, 1])
        self.assertEqual(native.choose(horizon=2), 0)
        self.assertEqual(native.choose(horizon=3), 1)

    def test_unlearned_consequence_abstains_to_safe_tie(self):
        native = ThreeStepFeatureCells(positions=2)
        baseline = PublicTransitionPlanner()
        fit(native, baseline)
        native.observe(b"zQ-novel-family", [0, 1])
        self.assertEqual(native.choose(horizon=3), 0)
        with self.assertRaises(ValueError):
            native.choose(horizon=4)

    def test_no_fabricated_loop_value(self):
        native = ThreeStepFeatureCells(positions=2)
        for action in (0, 1):
            native.observe(b"xA-loop", [0, 1])
            native.learn(action, b"xA-loop", 0, False)
        native.observe(b"zA-unfamiliar", [0, 1])
        self.assertEqual(native.choose(horizon=3), 0)

if __name__ == "__main__":
    unittest.main()
