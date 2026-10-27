"""Controlled operation identification, uncertainty and information parity."""
import unittest
from operation_identification_audit import run,trial
from operation_learning_cells import OperationLearningCells

class OperationIdentificationTests(unittest.TestCase):
    def test_heldout_operation_matrix_equal_public_actions(self):
        rows=run()["experiments"]
        self.assertEqual(len(rows),24)
        for case in rows:
            self.assertEqual(case["total_actions"],22)
            self.assertEqual(case["native_observations"],22)
            self.assertEqual(case["conventional_observations"],22)
            self.assertEqual(case["pair_actions"],16)
            self.assertEqual(case["final_actions"],6)
            self.assertEqual(case["results"]["local"],case["results"]["conventional"])
            self.assertEqual(case["results"]["affine"],case["results"]["affine_control"])
            self.assertEqual(case["results"]["exact"]["abstention"],1)
            for name,scored in case["results"].items():
                self.assertEqual(sum(scored.values()),1)
                self.assertGreaterEqual(case["cpu_ns"][name],0)

    def test_unlearned_and_insufficient_composition_refuse(self):
        learner=OperationLearningCells()
        self.assertIsNone(learner.predict((False,False,True,False)))
        with self.assertRaises(ValueError):
            learner.observe_final((False,False,True,False),False)

    def test_invalid_experiment_and_completed_feedback_gate(self):
        with self.assertRaises(ValueError):
            trial((False,False),6)
        with self.assertRaises(ValueError):
            trial((1,0),0)

if __name__=="__main__":
    unittest.main()
