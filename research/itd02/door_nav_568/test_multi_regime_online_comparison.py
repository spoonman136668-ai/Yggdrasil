"""Matched native-adapter/tabular online regime-switch controls."""
import unittest
from multi_regime_online_comparison import run, score, deep_bytes

class MultiRegimeComparisonTests(unittest.TestCase):
    def test_matched_action_and_observation_budgets(self):
        report = run()
        for label, per_stage in (("matched_two_sample", 4),
                                 ("single_sample_negative", 2)):
            result = report[label]
            self.assertEqual(len(result["stages"]), 6)
            self.assertEqual(result["total_actions"], 6 * per_stage)
            self.assertEqual(result["native_examples"], result["tabular_examples"])
            self.assertEqual(result["native_examples"], result["total_actions"])
            self.assertTrue(all(stage["actions"] == per_stage
                                for stage in result["stages"]))
            self.assertTrue(result["frozen_source_unchanged"])
            self.assertLessEqual(result["native_records"], 128)
            self.assertLessEqual(result["tabular_records"], 128)

    def test_switching_and_forgetting_outcomes_are_reported_not_filtered(self):
        result = run()["matched_two_sample"]
        names = [r["regime"] for r in result["stages"]]
        self.assertEqual(names, ["A_initial", "B_switch", "C_unfamiliar",
                                 "A_return", "C_return", "B_return"])
        for stage in result["stages"]:
            for timing in ("native_cpu_ns", "tabular_cpu_ns"):
                self.assertGreaterEqual(stage[timing], 0)
            for memory in ("native_bytes", "tabular_bytes"):
                self.assertGreater(stage[memory], 0)
            for phase in ("before", "after"):
                for policy in ("native", "tabular"):
                    values = stage[phase][policy]
                    self.assertEqual(values["correct"] + values["wrong"] +
                                     values["abstentions"], 2)

    def test_memory_accounting_and_no_imputed_success(self):
        self.assertEqual(score([None, b"wrong"], (b"right", b"correct")),
                         {"correct": 0, "wrong": 1, "abstentions": 1})
        self.assertGreater(deep_bytes({b"x": {b"y": 1}}), 0)
        result = run()
        self.assertEqual(result["matched_two_sample"]["total_actions"], 24)
        self.assertEqual(result["single_sample_negative"]["total_actions"], 12)
        self.assertGreaterEqual(result["matched_two_sample"]["native_revisions"], 1)

if __name__ == "__main__":
    unittest.main()
