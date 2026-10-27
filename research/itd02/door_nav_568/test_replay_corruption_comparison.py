"""Corruption comparison retains failures and accounts for added probes."""
import unittest
from replay_corruption_comparison import run

class CorruptionComparisonTests(unittest.TestCase):
    def test_complete_enumeration_and_resource_accounting(self):
        data = run()["policies"]
        for count, expected_cases in (("2", 8), ("3", 16)):
            policy = data[count]
            n = int(count)
            self.assertEqual(policy["total_cases"], expected_cases)
            self.assertEqual(policy["probe_interactions_per_case"], n)
            self.assertEqual(policy["archive_snapshots_per_case"], 1)
            self.assertEqual(policy["archived_feedback_examples_per_case"], 8)
            self.assertTrue(all(x["probe_closed"] for x in policy["cases"]))
            self.assertEqual(policy["continuing_regime_cases"], 1 << n)

    def test_third_independent_probe_defeats_two_corruptions(self):
        policies = run()["policies"]
        b2 = {x["flip_mask"]: x for x in policies["2"]["cases"] if x["regime"] == "B"}
        b3 = {x["flip_mask"]: x for x in policies["3"]["cases"] if x["regime"] == "B"}
        self.assertTrue(b2[3]["false_restore"])
        self.assertFalse(b3[3]["false_restore"])
        self.assertTrue(b3[7]["false_restore"])
        self.assertEqual(policies["2"]["false_restorations"], 1)
        self.assertEqual(policies["3"]["false_restorations"], 1)

    def test_clean_change_restores_and_clean_continuation_refuses(self):
        for policy in run()["policies"].values():
            for case in policy["cases"]:
                if case["flip_mask"] == 0:
                    self.assertEqual(case["restored"], case["regime"] == "A")

    def test_determinism(self):
        self.assertEqual(run(), run())

if __name__ == "__main__":
    unittest.main()
