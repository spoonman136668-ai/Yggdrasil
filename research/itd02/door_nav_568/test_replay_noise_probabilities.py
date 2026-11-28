"""Analytical noise weights must preserve mass and scientific negatives."""
import unittest
from replay_noise_probabilities import run, probability

class ReplayNoiseProbabilityTests(unittest.TestCase):
    def test_each_regime_probability_mass_is_one(self):
        for row in run()["records"]:
            self.assertAlmostEqual(row["probability_mass_A"], 1)
            self.assertAlmostEqual(row["probability_mass_B"], 1)
            self.assertAlmostEqual(row["correct_restore_probability_given_A"] +
                                   row["false_refusal_probability_given_A"], 1)
            self.assertEqual(row["probe_interactions_per_decision"], row["probe_count"])

    def test_independent_noise_benefit_and_cost(self):
        rows = {r["probe_count"]: r for r in run()["records"]
                if r["scenario"] == "independent_10pct"}
        self.assertAlmostEqual(rows[2]["false_restore_probability_given_B"], 0.01)
        self.assertAlmostEqual(rows[3]["false_restore_probability_given_B"], 0.001)
        self.assertAlmostEqual(rows[2]["correct_restore_probability_given_A"], 0.81)
        self.assertAlmostEqual(rows[3]["correct_restore_probability_given_A"], 0.729)
        self.assertEqual(rows[3]["probe_interactions_per_decision"] -
                         rows[2]["probe_interactions_per_decision"], 1)

    def test_correlated_noise_does_not_disappear(self):
        rows = {r["probe_count"]: r for r in run()["records"]
                if r["scenario"] == "correlated_10pct"}
        self.assertAlmostEqual(rows[2]["false_restore_probability_given_B"], 0.09)
        self.assertAlmostEqual(rows[3]["false_restore_probability_given_B"], 0.0738)
        self.assertGreater(rows[3]["false_restore_probability_given_B"], 0.07)

    def test_mass_and_repeatability(self):
        self.assertAlmostEqual(sum(probability(mask, 3, .25, .25)
                                   for mask in range(8)), 1)
        self.assertEqual(run(), run())

if __name__ == "__main__":
    unittest.main()
