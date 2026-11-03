"""G41 score/custody assertions; negative development outcomes must not fail CI."""
import json
import unittest
from g40_adaptation import CONDITIONS, ROUNDS, FRAMES, GRADIENT_CALLS, CUES
from g41_score_report import SCHEMA, build_report, serialize_report

class G41DevelopmentReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_report()

    def test_complete_paired_condition_scores(self):
        rows = self.report["rows"]
        self.assertEqual(len(rows), 2 * len(CONDITIONS))
        self.assertEqual({(r["pretrained"], r["condition"]) for r in rows},
                         {(warm, condition) for warm in (False, True)
                          for condition in CONDITIONS})
        for row in rows:
            with self.subTest(warm=row["pretrained"], condition=row["condition"]):
                for key in ("source_before", "target_before", "target_after"):
                    self.assertIn(row[key], (0.0, 0.5, 1.0))
                self.assertAlmostEqual(row["target_delta"],
                                       row["target_after"] - row["target_before"])
                self.assertEqual(row["interactions"], ROUNDS * len(CUES))
                self.assertEqual(row["frames"], row["interactions"] * FRAMES)
                self.assertEqual(row["gradient_calls"],
                                 row["interactions"] * GRADIENT_CALLS)

    def test_report_fails_closed_on_scientific_scope(self):
        report = self.report
        self.assertEqual(report["schema"], SCHEMA)
        self.assertFalse(report["primary_execution_allowed"])
        self.assertEqual(report["scientific_acceptance"], "NO_GO")
        self.assertEqual(report["genuine_transfer"], "UNVERIFIED")
        self.assertTrue(report["warm_start_has_unmatched_source_pretraining"])
        self.assertIn(report["diagnostic_signal"],
                      ("WARM_MAPPED_GAIN_EXCEEDS_COLD_AND_WARM_CONTROLS",
                       "NO_DISTINCT_WARM_MAPPED_GAIN"))

    def test_deterministic_machine_readable_receipt(self):
        payload = serialize_report(self.report)
        self.assertEqual(json.loads(payload), self.report)
        self.assertEqual(serialize_report(json.loads(payload)), payload)
        print("YGG_G41_DEV_REPORT_JSON=" + payload, flush=True)

if __name__ == "__main__":
    unittest.main()
