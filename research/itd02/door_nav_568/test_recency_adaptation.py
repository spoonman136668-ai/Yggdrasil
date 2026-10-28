"""Bounded recency plasticity and matched conventional controls."""
import unittest
from recency_adaptation_audit import run
from recency_transition_candidate import RecencyTransitionCandidate
from sliding_tabular_control import SlidingTabularControl

class RecencyAdaptationTests(unittest.TestCase):
    def test_matched_six_regime_reacquisition(self):
        report = run()["two_sample"]
        self.assertEqual(report["actions"], 24)
        self.assertEqual(report["native_examples"], report["control_examples"])
        self.assertEqual(report["native_examples"], 24)
        self.assertEqual(len(report["stages"]), 6)
        self.assertTrue(report["archive_unchanged"])
        for row in report["stages"]:
            for arm in ("native", "control"):
                self.assertEqual(row["after"][arm],
                                 {"correct": 2, "wrong": 0, "abstentions": 0})
            self.assertEqual(row["actions"], 4)
        self.assertEqual(report["native_records"], 4)
        self.assertEqual(report["control_records"], 4)
        self.assertGreater(report["native_bytes"], 0)
        self.assertGreater(report["control_bytes"], 0)

    def test_one_observation_switch_abstains_without_unsafe_claim(self):
        report = run()["single_sample"]
        self.assertEqual(report["actions"], 12)
        for row in report["stages"]:
            for arm in ("native", "control"):
                result = row["after"][arm]
                self.assertEqual(result["correct"] + result["wrong"] +
                                 result["abstentions"], 2)
        # Once a coherent previous regime exists, the first new observation
        # cannot immediately certify a new regime.
        self.assertEqual(report["stages"][2]["after"]["native"]["abstentions"], 2)

    def test_capacity_and_immutability(self):
        original = {(b"state", 0): b"history"}
        native = RecencyTransitionCandidate(original, capacity=1)
        tabular = SlidingTabularControl(capacity=1)
        for instance in (native, tabular):
            instance.observe((b"state", 0), b"new")
            self.assertIsNone(instance.predict((b"state", 0)))
            instance.observe((b"state", 0), b"new")
            self.assertEqual(instance.predict((b"state", 0)), b"new")
            with self.assertRaises(ValueError):
                instance.observe((b"other", 0), b"new")
        self.assertEqual(native.archive[(b"state", 0)], b"history")
        self.assertEqual(original[(b"state", 0)], b"history")

if __name__ == "__main__":
    unittest.main()
