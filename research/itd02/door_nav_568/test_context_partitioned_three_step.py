"""Prospective public-context retention after wrong-action correction."""
import unittest
from context_partitioned_three_step import ContextPartitionedThreeStep
from test_three_step_feature_cells import fit
from public_transition_planner import PublicTransitionPlanner

class ContextPartitionTests(unittest.TestCase):
    def test_correction_preserves_old_context_at_memory_cost(self):
        learner = ContextPartitionedThreeStep(positions=2, capacity=128)
        baseline = PublicTransitionPlanner()
        fit(learner, baseline)
        learner.freeze_boundary()
        learner.observe(b"zA-reversed", [0, 1])
        self.assertEqual(learner.choose(3), 1)
        for _ in range(12):
            for action, successor in ((1, b"D2-intermediate"),
                                      (0, b"M1-intermediate")):
                learner.observe(b"zA-reversed", [0, 1])
                learner.learn(action, successor, 0, False)
        learner.observe(b"zA-reversed", [0, 1])
        self.assertEqual(learner.choose(3), 0)
        learner.observe(b"xA-retention", [0, 1])
        self.assertEqual(learner.choose(3), 1)
        self.assertEqual(len(learner.prior_contexts), 6)
        self.assertLessEqual(learner.stored_examples(), 2*learner.capacity)
        self.assertEqual(learner.active.model.selected_position, 0)
        self.assertEqual(learner.snapshot.model.selected_position, 1)

    def test_one_snapshot_and_no_unfounded_retention_guarantee(self):
        learner = ContextPartitionedThreeStep(positions=2, capacity=16)
        with self.assertRaises(ValueError):
            learner.freeze_boundary()
        learner.observe(b"xA-first", [0])
        learner.learn(0, b"M-next", 0, False)
        learner.freeze_boundary()
        with self.assertRaises(ValueError):
            learner.freeze_boundary()
        learner.observe(b"qQ-unknown", [0, 1])
        self.assertEqual(learner.choose(3), 0)

if __name__ == "__main__":
    unittest.main()
