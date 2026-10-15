"""Pre-original tests restricted to public calibration and TRAIN source."""
import importlib.util
import pathlib
import sys
import unittest
P=pathlib.Path(__file__).with_name("execute.py")
spec=importlib.util.spec_from_file_location("yf29",P)
mod=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=mod
spec.loader.exec_module(mod)
class Preflight(unittest.TestCase):
    def test_separate_seeds_and_regimes(self):
        self.assertFalse(set(mod.TRAIN_SEEDS)&set(mod.TEST_SEEDS))
        self.assertFalse(set(mod.TRAIN_REGIMES)&set(mod.TEST_REGIMES))
    def test_train_only_source_reproducibility(self):
        self.assertEqual(mod.measurements(151000,1,0,0,42),
                         mod.measurements(151000,1,0,0,42))
    def test_same_public_evidence_for_fair_arms(self):
        pub,anchors=mod.calibrate(151000,0,0)
        self.assertEqual(len(anchors),48)
        self.assertEqual(len(pub.reliability),4)
        self.assertEqual(len(pub.missingness),4)
        self.assertEqual(mod.first_choice(pub),mod.first_choice(pub))
    def test_disjoint_purchased_channels(self):
        pub,anchors=mod.calibrate(151000,0,0)
        _,data=mod.measurements(151001,1,0,0,42)
        rec=mod.custody.evaluate_policy(data,pub,mod.first_choice,
            lambda p,first:mod.second_choice("static",p,first,anchors,(0.,)*8,(0.,)*4),
            576,mod.CALIBRATION_EXTERNAL_BYTES)
        self.assertEqual(rec.physical_reads,2)
        self.assertNotEqual(rec.trace[0].sensor,rec.trace[1].sensor)
if __name__=="__main__":unittest.main()
