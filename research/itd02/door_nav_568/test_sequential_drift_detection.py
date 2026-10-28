"""Scientific custody gates for staged environment drift evidence."""
import unittest
from sequential_drift_detection_audit import run,trial

class SequentialDriftTests(unittest.TestCase):
    def test_all_worlds_equal_public_observations(self):
        rows=run()["runs"]
        self.assertEqual(len(rows),256)
        for row in rows:
            self.assertEqual(row["source_observations"],8)
            self.assertEqual(row["target_observations"],3)
            self.assertEqual(row["updates"],(3,3,3))
            self.assertEqual(len(row["stages"]),3)
            for index,stage in enumerate(row["stages"],1):
                self.assertEqual(stage["target_observations"],index)
                self.assertEqual(stage["unseen_inputs"],4-index)
                self.assertTrue(stage["cold_restore_exact"])
                self.assertLessEqual(stage["checkpoint_bytes"],4096)
                self.assertEqual(stage["scores"]["local"],stage["scores"]["table"])
                self.assertEqual(stage["scores"]["scratch"]["abstentions"],4-index)
                for scores in stage["scores"].values():
                    self.assertEqual(sum(scores.values()),4-index)

    def test_related_worlds_never_trigger_false_drift(self):
        for row in run()["runs"]:
            if row["relationship"] in ("same","complement"):
                for stage in row["stages"]:
                    self.assertFalse(stage["drift_detected"])
                    self.assertEqual(stage["scores"]["local"]["wrong"],0)
                    self.assertEqual(stage["scores"]["local"]["correct"],stage["unseen_inputs"])

    def test_unrelated_drift_detected_but_not_guaranteed_at_first_probe(self):
        negatives=[r for r in run()["runs"] if r["relationship"]=="unrelated"]
        self.assertEqual(len(negatives),224)
        self.assertTrue(any(r["stages"][0]["scores"]["local"]["wrong"]>0 for r in negatives))
        self.assertTrue(any(r["stages"][1]["drift_detected"] for r in negatives))

        self.assertTrue(any(not r["stages"][2]["drift_detected"] for r in negatives))
        self.assertGreater(sum(r["stages"][2]["scores"]["local"]["wrong"] for r in negatives),0)