"""CKAD28 frozen development-gate and evidence-rejection tests."""
import json
from fractions import Fraction
from pathlib import Path
import unittest

import audit


class AuditControls(unittest.TestCase):
    def test_source_protocol_is_frozen_and_has_distinct_holdout(self):
        p=audit.campaign.source_protocol()
        self.assertEqual(p["schema"],"yggdrasil.ckad28.decision-relevance.prereg.v1")
        self.assertEqual(list(p["scenarios"]),list(audit.SCENARIOS))
        self.assertEqual(p["source_episodes_per_arm"],128)
        self.assertEqual(p["held_evaluations"]["episodes_per_checkpoint"],96)
        self.assertNotEqual(p["source_cohort"],p["held_cohort"])
        self.assertEqual(p["scientific_pass"],False)
        self.assertEqual(p["deployment"],"NONE")

    def test_missing_replicates_or_hidden_metrics_rejected(self):
        with self.assertRaisesRegex(ValueError,"SIX_SOURCE_CASES"):
            audit.metrics([])
        with self.assertRaisesRegex(ValueError,"RATIONAL_METRIC"):
            audit.fraction([1,0])
        self.assertEqual(audit.fraction([1,2]),Fraction(1,2))
        self.assertFalse(audit.sha64("short"))
        self.assertTrue(audit.sha64("a"*64))

    def test_stable_hash_and_model_readback_drift_detection(self):
        a={"x":[0,1],"wall_seconds":2.0,"scientific_pass":False}
        self.assertEqual(audit.campaign.stable(a),
                         audit.campaign.stable({**a,"wall_seconds":9.0}))
        self.assertNotEqual(audit.campaign.stable(a),
                            audit.campaign.stable({**a,"x":[1,0]}))


if __name__=="__main__":
    unittest.main()
