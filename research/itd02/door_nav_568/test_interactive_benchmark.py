"""Reproducible measured transfer with matched conventional control."""
import unittest
from interactive_benchmark import run

class InteractiveBenchmarkTests(unittest.TestCase):
    def test_matched_fit_counts_and_unfamiliar_transfer(self):
        report = run(16)
        self.assertEqual(report["episodes"], 16)
        self.assertEqual(set(report["results"]),
                         {"adaptive", "exact", "fixed_feature", "conventional_tabular"})
        for counts in report["results"].values():
            self.assertEqual(counts["train_actions"], 16)
            self.assertEqual(counts["transfer_actions"], 16)
            self.assertEqual(counts["train_success"], 8)
        self.assertEqual(report["results"]["conventional_tabular"]["transfer_success"], 8)
        self.assertEqual(report["results"]["exact"]["transfer_success"], 8)
        self.assertEqual(report["results"]["fixed_feature"]["transfer_success"], 16)
        self.assertEqual(report["results"]["adaptive"]["transfer_success"], 16)

    def test_deterministic_repetition(self):
        self.assertEqual(run(16), run(16))

if __name__ == "__main__":
    unittest.main()
