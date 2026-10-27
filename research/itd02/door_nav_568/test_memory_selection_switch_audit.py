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

    def test_preserves_wrong_answers_and_abstentions(self):
        result = run()
        for case in result["cases"]:
            self.assertEqual(case["admitted"], case["selected"] is not None)
            if case["abstained"]:
                self.assertIsNone(case["decision"])
        self.assertEqual(result, run())

if __name__ == "__main__":
    unittest.main()
