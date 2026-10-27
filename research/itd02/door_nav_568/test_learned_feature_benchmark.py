"""Matched-feedback learned public feature benchmark acceptance controls."""
import unittest
from learned_feature_benchmark import run

class LearnedFeatureBenchmarkTests(unittest.TestCase):
    def test_matched_feedback_and_held_out_scores(self):
        result = run()
        self.assertEqual(result["selected_position"], 1)
        for row in result["results"].values():
            self.assertEqual(row["fit_observations"], 8)
            self.assertEqual(row["holdout_total"], 4)
        self.assertEqual(result["results"]["learned_byte"]["holdout_successes"], 4)
        self.assertEqual(result["results"]["fixed_prefix"]["holdout_successes"], 2)
        self.assertEqual(result["results"]["tabular"]["holdout_successes"], 2)

    def test_reproducible(self):
        self.assertEqual(run(), run())

if __name__ == "__main__":
    unittest.main()
