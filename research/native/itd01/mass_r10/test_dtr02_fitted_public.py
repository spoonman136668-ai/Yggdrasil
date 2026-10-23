"""Frozen non-sampling smoke guards for DTR-02 policy fitting."""
import pathlib
import sys
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from run_dtr02_fitted_public import (
    LogisticCandidate, TabularModel, EpisodicK3, Planner,
    reward_features, next_features, freeze_state, bit, ARMS, TRAIN_PAIRS
)

def fit_rows():
    rows=[]
    for k in range(256):
        s1=(k>>1)&1;x1=TRAIN_PAIRS[k%4][0];x2=TRAIN_PAIRS[k%4][1]
        s2=(s1^x1)&1;y=(s1^s2^x2)&1
        rows.append({"seed":1100000+k,"s1":s1,"x1":x1,"s2":s2,"x2":x2,"y":y})
    return rows

class Boundaries(unittest.TestCase):
    def test_feature_basis_fixed(self):
        self.assertEqual(len(next_features(0,1)),4)
        self.assertEqual(len(reward_features(1,0,1,1)),16)
        with self.assertRaises(RuntimeError):bit(2)

    def test_three_models_really_fit_public_rows(self):
        rows=fit_rows()
        for cls in [LogisticCandidate,TabularModel,EpisodicK3]:
            obj=cls()
            before=freeze_state(obj)
            obj.train(rows)
            self.assertNotEqual(before,freeze_state(obj))
            self.assertIn(Planner(obj).choose_first(1),(0,1))
            self.assertIn(Planner(obj).choose_second(1,0,1),(0,1))
        self.assertEqual(LogisticCandidate().erased().export()["updates"],0)

    def test_no_proxy_for_native_yggdrasil(self):
        self.assertEqual(len(ARMS),5)
        self.assertEqual(TRAIN_PAIRS,((0,0),(0,1),(1,0),(1,1)))
        self.assertEqual(len(set(TRAIN_PAIRS)),4)

if __name__=="__main__":
    unittest.main()
