"""Synthetic source-free learned action-successor generalization controls."""
import unittest
from learned_successor_features import LearnedSuccessorFeatures
from public_transition_planner import PublicTransitionPlanner

def train(candidate, baseline):
    for nuisance in (b"x", b"y"):
        for signal, correct in ((b"A", 1), (b"B", 0)):
            for action in (0, 1):
                frame = nuisance + signal + b"-train"
                nxt = b"G-terminal" if action == correct else b"F-terminal"
                candidate.observe(frame, [0, 1])
                candidate.learn(action, nxt, int(action == correct), True)
                baseline.observe(frame, [0, 1])
                baseline.learn(action, nxt, int(action == correct), True)

class LearnedSuccessorTests(unittest.TestCase):
    def test_predicts_unseen_action_consequences_from_learned_feature(self):
        learner = LearnedSuccessorFeatures(positions=2)
        baseline = PublicTransitionPlanner()
        train(learner, baseline)
        self.assertEqual(learner.selected_position, 1)
        for frame, correct in ((b"zA-unseen", 1), (b"zB-unseen", 0)):
            learner.observe(frame, [0, 1])
            self.assertEqual(learner.predict_successor_label(correct), ord("G"))
            self.assertEqual(learner.predict_successor_label(1-correct), ord("F"))
            baseline.observe(frame, [0, 1])
            self.assertEqual(baseline.choose(horizon=1), 0)

    def test_unknown_or_conflicting_outcomes_abstain(self):
        learner = LearnedSuccessorFeatures(positions=1)
        learner.observe(b"A-first", [0])
        self.assertIsNone(learner.predict_successor_label(0))
        learner.learn(0, b"X-next", 0, True)
        learner.observe(b"A-second", [0])
        learner.learn(0, b"Y-next", 0, True)
        learner.observe(b"A-heldout", [0])
        self.assertIsNone(learner.predict_successor_label(0))
        with self.assertRaises(ValueError):
            learner.predict_successor_label(1)

    def test_bounded_examples_and_action_ownership(self):
        learner = LearnedSuccessorFeatures(positions=2, capacity=4)
        for i in range(16):
            learner.observe(b"xA-"+bytes([i]), [0])
            with self.assertRaises(ValueError):
                learner.learn(1, b"G", 1, True)
            learner.learn(0, b"G", 1, True)
            self.assertLessEqual(len(learner.examples), 4)
        with self.assertRaises(ValueError):
            LearnedSuccessorFeatures(capacity=3)

    def test_unseen_feature_refuses_prediction(self):
        learner = LearnedSuccessorFeatures(positions=2)
        baseline = PublicTransitionPlanner()
        train(learner, baseline)
        learner.observe(b"zQ-unseen", [0, 1])
        self.assertIsNone(learner.predict_successor_label(0))

if __name__ == "__main__":
    unittest.main()
