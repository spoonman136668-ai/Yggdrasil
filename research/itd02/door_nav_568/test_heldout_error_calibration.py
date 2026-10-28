import unittest
from heldout_error_calibration_audit import run,trial,episode
from public_error_calibrator import PublicErrorCalibrator
from empirical_local_probe import EmpiricalLocalProbe

class HeldoutErrorCalibrationTests(unittest.TestCase):
    def test_leave_one_world_out_evidence_and_matched_control(self):
        folds=run()["folds"]
        self.assertEqual(len(folds),16)
        for fold in folds:
            local=fold["arms"]["local"]
            control=fold["arms"]["conventional"]
            for item in (local,control):
                self.assertEqual(item["training_world_count"],15)
                self.assertTrue(item["heldout_not_in_training"])
                self.assertGreater(item["calibration_predictions"],0)
                self.assertEqual(len(item["scores"]),2)
                for s in item["scores"]:
                    for treatment in ("raw","calibrated"):
                        self.assertEqual(sum(s[treatment].values()),s["unseen"])
                    self.assertEqual(s["actions"],s["unseen"]*-1+4)
            self.assertEqual(local["scores"],control["scores"])
            self.assertEqual(local["calibration_predictions"],control["calibration_predictions"])
            self.assertEqual(local["calibration_bucket_counts"],control["calibration_bucket_counts"])

    def test_no_heldout_outcome_before_gate(self):
        cal=PublicErrorCalibrator(min_predictions=5,max_upper_error=0.2)
        self.assertIsNone(cal.accept((2,1),True))
        for i in range(5):
            cal.record_completed((2,1),True,True)
        self.assertEqual(cal.total(),5)
        self.assertLessEqual(cal.upper_error((2,1)),1)
        with self.assertRaises(ValueError):
            cal.record_completed((2,1),True,1)
        with self.assertRaises(ValueError):
            trial(16)

    def test_calibration_never_invents_predictions(self):
        c=PublicErrorCalibrator()
        self.assertIsNone(c.accept((1,0),None))
        for i in range(30):
            c.record_completed((1,0),True,True)
        self.assertIsNone(c.accept((1,0),None))
        self.assertIs(c.accept((1,0),True),True)

    def test_source_custody_training_is_bounded(self):
        self.assertEqual(len(episode(EmpiricalLocalProbe,3)),2)
