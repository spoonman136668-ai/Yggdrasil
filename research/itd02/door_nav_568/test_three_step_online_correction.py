"""Bounded online correction measured without assuming it succeeds."""
import unittest
from three_step_online_correction import run

class ThreeStepOnlineCorrectionTests(unittest.TestCase):
    def test_reversal_falsification_and_retention_are_reported(self):
        result = run()
        self.assertEqual(result["before"], 1)
        self.assertEqual(result["intervention_actions"], 24)
        self.assertLessEqual(result["retained_fit_examples"], result["max_examples"])
        self.assertIn(result["after"], (0, 1))
        self.assertIn(result["other_family_action"], (0, 1))
        self.assertIn(result["feature_position"], (0, 1))
        self.assertEqual(result, run())

if __name__ == "__main__":
    unittest.main()
