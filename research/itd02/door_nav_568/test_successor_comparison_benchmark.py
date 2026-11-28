"""Matched public transition corroboration benchmark checks and negatives."""
import unittest
from successor_comparison_benchmark import run

class SuccessorComparisonTests(unittest.TestCase):
    def test_reward_successor_crossed_conditions(self):
        report = run()
        self.assertEqual(len(report["cases"]), 4)
        cases = {(x["reward_channel"], x["successor_channel"]): x
                 for x in report["cases"]}
        self.assertTrue(cases["A", "A"]["reward_only_restored"])
        self.assertTrue(cases["A", "A"]["corroborated_restored"])
        self.assertTrue(cases["A", "B"]["reward_only_restored"])
        self.assertFalse(cases["A", "B"]["corroborated_restored"])
        self.assertFalse(cases["B", "A"]["reward_only_restored"])
        self.assertFalse(cases["B", "A"]["corroborated_restored"])
        self.assertFalse(cases["B", "B"]["reward_only_restored"])
        self.assertFalse(cases["B", "B"]["corroborated_restored"])

    def test_matched_feedback_and_explicit_memory_cost(self):
        report = run()
        self.assertEqual({x["probe_actions_per_arm"] for x in report["cases"]}, {2})
        self.assertEqual({x["historical_reward_examples_per_arm"] for x in report["cases"]}, {16})
        self.assertEqual({x["additional_successor_transition_examples"] for x in report["cases"]}, {16})
        self.assertTrue(all(x["public_successor_key_count"] > 0 for x in report["cases"]))
        self.assertEqual(report, run())

if __name__ == "__main__":
    unittest.main()
