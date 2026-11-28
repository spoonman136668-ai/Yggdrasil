"""Unfamiliar public-state transfer falsification fixture.

A novel frame has a distinct hash. No unseen source-world episodes are used.
"""
import unittest
from eligibility_local_cells import EligibilityLocalCells
from state_local_cells import StateLocalActionCells

class UnfamiliarStateTests(unittest.TestCase):
    def test_exact_state_local_eligibility_fails_zero_shot_transfer(self):
        for cls in (EligibilityLocalCells, StateLocalActionCells):
            learner = cls()
            for _ in range(3):
                learner.observe(b"training-room", [0, 1])
                learner.learn(1, b"goal", 1, True)
            learner.observe(b"training-room", [0, 1])
            self.assertEqual(learner.choose(), 1)
            learner.observe(b"unfamiliar-room", [0, 1])
            self.assertEqual(learner.choose(), 0)

    def test_delayed_credit_does_not_generalize_to_new_frame(self):
        learner = EligibilityLocalCells()
        learner.observe(b"train-start", [0, 1])
        learner.learn(1, b"train-middle", 0, False)
        learner.observe(b"train-middle", [2])
        learner.learn(2, b"train-goal", 1, True)
        learner.observe(b"train-start", [0, 1])
        self.assertEqual(learner.choose(), 1)
        learner.observe(b"unseen-start", [0, 1])
        self.assertEqual(learner.choose(), 0)

if __name__ == "__main__":
    unittest.main()
