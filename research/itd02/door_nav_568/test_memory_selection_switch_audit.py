"""Pinned accounting and diagnostic negatives for repeated-memory selection."""
import unittest
from memory_selection_switch_audit import run

class MemorySelectionSwitchTests(unittest.TestCase):
    def test_complete_sequential_switches_and_budget(self):
        data = run()
        self.assertEqual(len(data["cases"]), 7)
        self.assertEqual([c["case"] for c in data["cases"]],
                         ["A_prior", "B_changed", "A_return", "B_return",
                          "B_reward_corrupted", "B_public_collision", "unknown_family"])
        self.assertEqual(data["extra_probe_actions"], 14)
        self.assertTrue(all(c["probe_actions"] == 2 for c in data["cases"]))
        self.assertTrue(all(c["stored_examples"] <= data["memory_cap"] for c in data["cases"]))
        self.assertEqual(data["correct"] + data["abstentions"] + data["wrong_decisions"], 7)

    def test_experimentally_observed_return_and_aliasing_failures(self):
        result = run()
        cases = {case["case"]: case for case in result["cases"]}
        for label, decision, memory in (
            ("A_prior", 1, "snapshot"),
            ("B_changed", 0, "active"),
            ("B_return", 0, "active"),
            ("B_reward_corrupted", 0, "active"),
            ("A_return", None, None),
            ("B_public_collision", None, None),
            ("unknown_family", None, None),
        ):
            self.assertEqual(cases[label]["decision"], decision)
            self.assertEqual(cases[label]["selected"], memory)
        self.assertEqual(result["correct"], 4)
        self.assertEqual(result["abstentions"], 3)
        self.assertEqual(result["wrong_decisions"], 0)

    def test_probe_prediction_provenance_and_score_accounting(self):
        report = run()
        for case in report["cases"]:
            evidence = case["diagnostics"]
            self.assertEqual(len(evidence["observed_successor"]), 2)
            for key, score in (("active_prediction", "active_matches"),
                               ("archive_prediction", "archive_matches")):
                self.assertEqual(evidence[score], sum(
                    predicted == observed for predicted, observed in zip(
                        evidence[key], evidence["observed_successor"]
                    )))
            if case["admitted"]:
                self.assertEqual(max(evidence["active_matches"],
                                     evidence["archive_matches"]), 2)
                self.assertNotEqual(evidence["active_matches"],
                                    evidence["archive_matches"])

    def test_preserves_wrong_answers_and_abstentions(self):
        result = run()
        for case in result["cases"]:
            self.assertEqual(case["admitted"], case["selected"] is not None)
            if case["abstained"]:
                self.assertIsNone(case["decision"])
        self.assertEqual(result, run())

if __name__ == "__main__":
    unittest.main()
