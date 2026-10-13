"""Synthetic mechanical-only tests. No R015/016 project data or primary outputs."""
import unittest
try:
    from .probe import paired_placement, deterministic_matching, greedy_first_free
except ImportError:
    from probe import paired_placement, deterministic_matching, greedy_first_free

class ToyLearner:
    def __init__(self, cells): self.cells=cells
    def home_cell(self, key): return key
    def local_cells(self, home): return self.cells[home]

class PlacementTests(unittest.TestCase):
    def test_augmenting_reassignment_recovers_greedy_failure(self):
        # A can use 0 or 1, B can use only 0.
        learner=ToyLearner({"A":(0,1),"B":(0,)})
        self.assertIsNone(greedy_first_free(learner,("A","B")))
        self.assertEqual(deterministic_matching(learner,("A","B")),{"A":1,"B":0})
    def test_both_valid_with_no_collision(self):
        learner=ToyLearner({"A":(0,),"B":(1,)})
        result=paired_placement(learner,("A","B"))
        self.assertEqual(result["matched"],result["greedy"])
    def test_infeasible_does_not_mutate_capacity(self):
        learner=ToyLearner({"A":(0,),"B":(0,)})
        self.assertIsNone(deterministic_matching(learner,("A","B")))
    def test_duplicate_selected_key_fails_closed(self):
        learner=ToyLearner({"A":(0,1)})
        with self.assertRaises(ValueError): paired_placement(learner,("A","A"))
    def test_out_of_capacity_cell_fails_closed(self):
        learner=ToyLearner({"A":(16,)})
        with self.assertRaises(ValueError): paired_placement(learner,("A",))
    def test_deterministic_order_and_no_source_mutation(self):
        learner=ToyLearner({"A":(0,1),"B":(0,)})
        keys=["A","B"]
        self.assertEqual(paired_placement(learner,keys),paired_placement(learner,keys))
        self.assertEqual(keys,["A","B"])

if __name__ == "__main__": unittest.main()
