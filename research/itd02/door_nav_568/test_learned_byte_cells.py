"""Feedback-selected feature tests with balanced nuisance positions."""
import unittest
from learned_byte_cells import LearnedByteCells
from feature_eligibility_cells import FeatureEligibilityCells

class LearnedByteTests(unittest.TestCase):
    def test_discovers_predictive_position_not_fixed_prefix(self):
        agent = LearnedByteCells(feature_positions=2)
        fixed = FeatureEligibilityCells(feature_bytes=1)
        for nuisance in (b"x", b"y"):
            for signal, correct in ((b"A", 1), (b"B", 0)):
                for action in (0, 1):
                    frame = nuisance + signal + b"-train"
                    reward = int(action == correct)
                    for learner in (agent, fixed):
                        learner.observe(frame, [0, 1])
                        learner.learn(action, b"terminal", reward, True)
        self.assertEqual(agent.feature_position, 1)
        for frame, expected in ((b"zA-unseen", 1), (b"zB-unseen", 0)):
            agent.observe(frame, [0, 1])
            self.assertEqual(agent.choose(), expected)
            fixed.observe(frame, [0, 1])
            self.assertEqual(fixed.choose(), 0)

    def test_insufficient_feedback_does_not_guarantee_transfer(self):
        agent = LearnedByteCells(feature_positions=2)
        agent.observe(b"xA-train", [0, 1])
        agent.learn(1, b"goal", 1, True)
        agent.observe(b"zA-unseen", [0, 1])
        self.assertEqual(agent.choose(), 0)

if __name__ == "__main__":
    unittest.main()
