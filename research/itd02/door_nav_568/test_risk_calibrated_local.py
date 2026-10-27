"""Prequential local-risk policy is safe to test, not yet scientific acceptance."""
import unittest
from risk_calibrated_local import RiskCalibratedLocal
from risk_calibrated_local_audit import run,trial
from specialization_scaling_audit import families

class RiskCalibratedTests(unittest.TestCase):
    def test_no_public_evidence_no_claim(self):
        model=RiskCalibratedLocal()
        bits,outcome=families(3)[0]
        self.assertIsNone(model.predict(bits))
        model.observe(bits,outcome)
        self.assertIsNone(model.predict(bits))
        self.assertIsNone(model.cutoff())
        with self.assertRaises(ValueError):
            RiskCalibratedLocal(min_support=1)

    def test_action_and_calibration_custody(self):
        rows=run()["experiments"]
        self.assertEqual(len(rows),18)
        for r in rows:
            self.assertEqual(set(r["updates"].values()),{r["actions"]})
            self.assertEqual(r["calibration_actions"],r["count"])
            for arm in ("calibrated","raw","linear"):
                self.assertEqual(sum(r["train"][arm].values()),r["count"])
                self.assertEqual(sum(r["heldout"][arm].values()),16-r["count"])
                self.assertGreaterEqual(r["cpu_ns"][arm],0)
            self.assertIn(r["chosen_cutoff"],(None,0.5,0.75,1.0))

    def test_no_heldout_label_changes_threshold(self):
        a=trial(3,8,"parity")
        b=trial(3,8,"first_bit")
        self.assertEqual(a["calibration_actions"],b["calibration_actions"])
        self.assertEqual(a["actions"],b["actions"])

if __name__=="__main__":
    unittest.main()
