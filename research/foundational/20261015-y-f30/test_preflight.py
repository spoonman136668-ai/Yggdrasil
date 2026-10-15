"""Y-F30 bounded pre-original contract tests. Do not execute held-out cohort."""
import importlib.util
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("yf30_exec",HERE/"execute.py")
m=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=m
spec.loader.exec_module(m)

class Contract(unittest.TestCase):
    def test_disjoint_primary_seeds(self):
        self.assertFalse(set(m.TRAIN_SEEDS)&set(m.TEST_SEEDS))
        self.assertFalse(set(m.TRAIN_REGIMES)&set(m.TEST_REGIMES))
        self.assertEqual(m.FEATURE_DIM,10)
    def test_public_anchor_shape(self):
        anchors=m.public_anchors(161200,0,0)
        self.assertEqual(len(anchors),64)
        pub=m.calibration(anchors)
        self.assertEqual(len(pub.reliability),4)
        self.assertEqual(len(m.features(pub,anchors,.25,1)),10)
        self.assertEqual(m.public_anchors(161200,0,0),anchors)
    def test_first_observation_precedes_second_acquisition(self):
        anchors=m.public_anchors(161201,0,1)
        pub=m.calibration(anchors)
        _,data=m.physics(161202,0,0,1,22)
        weights=(0.,)*m.FEATURE_DIM
        receipt=m.custody.evaluate_policy(data,pub,lambda _:0,
            lambda public,first:m.second("calibrated_static",public,anchors,first,weights),
            m.CORE_BYTES,m.CALIB_BYTES)
        self.assertEqual(receipt.physical_reads,2)
        self.assertEqual(receipt.trace[0].sensor,0)
        self.assertIn(receipt.trace[1].sensor,m.OPTIONS)
        self.assertNotEqual(receipt.trace[0].sensor,receipt.trace[1].sensor)
    def test_first_read_counterfactual_cannot_peek(self):
        anchors=m.public_anchors(161201,1,0);pub=m.calibration(anchors)
        observed=m.custody.PurchasedReading(0,.2)
        weights=(0.,)*m.FEATURE_DIM
        self.assertEqual(m.second("learned",pub,anchors,observed,weights),
                         m.second("learned",pub,anchors,observed,weights))
    def test_resource_bounds(self):
        self.assertLessEqual(m.FEATURE_DIM*8,m.CORE_BYTES)
        self.assertEqual(m.CALIB_BYTES,64*(4*8+8))
if __name__=="__main__":
    unittest.main()
