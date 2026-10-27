"""Strict local corroboration against negative and conventional baselines."""
import unittest
from corroborated_local_selector import CorroboratedLocalSelector
from corroborated_local_audit import run
from specialization_scaling_audit import families

class CorroborationTests(unittest.TestCase):
    def test_bounded_and_fail_closed_before_evidence(self):
        candidate=CorroboratedLocalSelector()
        bits,label=families(3)[0]
        self.assertIsNone(candidate.predict(bits))
        candidate.observe(bits,label)
        self.assertIsNone(candidate.predict(bits))
        candidate.observe(bits,label)
        self.assertEqual(candidate.predict(bits),label)
        with self.assertRaises(ValueError):
            CorroboratedLocalSelector(min_support=1)

    def test_all_samples_and_abstentions_are_scored(self):
        report=run()
        self.assertEqual(len(report["experiments"]),18)
        for row in report["experiments"]:
            self.assertEqual(row["actions"],row["count"]*2)
            self.assertEqual(set(row["updates"].values()),{row["actions"]})
            for arm in ("original","corroborated","linear","tabular"):
                self.assertEqual(sum(row["training"][arm].values()),row["count"])
                self.assertEqual(sum(row["heldout"][arm].values()),16-row["count"])
                self.assertGreaterEqual(row["cpu_ns"][arm],0)
            self.assertEqual(row["records"]["original"],
                             row["records"]["corroborated"])
            self.assertLessEqual(row["records"]["corroborated"],32)

    def test_corroboration_never_adds_unbacked_predictions(self):
        for row in run()["experiments"]:
            strict=row["heldout"]["corroborated"]
            self.assertLessEqual(strict["correct"]+strict["wrong"],
                                 16-row["count"])
            self.assertEqual(strict["correct"]+strict["wrong"]+
                             strict["abstentions"],16-row["count"])
