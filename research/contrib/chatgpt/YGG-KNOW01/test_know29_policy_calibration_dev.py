"""KNOW29 structural tests intentionally never run HELD source or proof()."""
import random
import unittest
from know29_policy_calibration_dev import (
    PROTO,PREREG,PREREG_BLOB,MODE,MATCH,SHIFT,COHORTS,ARMS,N,
    protocol,bits_shift,source_identity,witnessed,model_for,
    public_choice,myopic_identity)
from unknown_action_affordance_dev import JointHypothesis,digest

class KNOW29PreFirstUse(unittest.TestCase):
    def test_frozen_prereg_and_disjoint_cohorts(self):
        p=protocol()
        self.assertEqual(p["schema"],PROTO)
        self.assertEqual(PREREG,"a0b3c666cb9573aa62cbf32a66e960f7ad342d5c")
        self.assertEqual(PREREG_BLOB,"4dc40db53b7f2e8a4db38fd58912b7df7c47000d")
        self.assertEqual(MODE,"engineering_fixture_only")
        self.assertEqual(len(MATCH),8)
        self.assertEqual(len(SHIFT),8)
        self.assertEqual(len(set(MATCH+SHIFT)),16)
        self.assertEqual((len(COHORTS),len(ARMS),N),(2,7,32))
        self.assertEqual(p["worlds"]["score_queries_per_policy_per_cohort"],96)
        self.assertFalse(p["authority"]["original_first_use"])
    def test_private_injection_denied(self):
        m=JointHypothesis([1/6.]*6)
        for arm in ARMS:
            if arm=="privileged_known_map_entropy":
                continue
            with self.assertRaises(ValueError):
                model_for(arm,[1/6.]*6,(0,0))
            self.assertIn(public_choice(arm,m,0,0,random.Random(7)),range(4))
        with self.assertRaises(ValueError):
            model_for("privileged_known_map_entropy",[1/6.]*6)
        with self.assertRaises(ValueError):
            source_identity("original_owner",0,MATCH[0])
        with self.assertRaises(ValueError):
            witnessed("original_owner",0,MATCH[0],0,0,(0,0))
        with self.assertRaises(ValueError):
            witnessed(COHORTS[0],0,MATCH[0],0,0,(0,0),mode="protected")
    def test_structured_truths_no_held_source(self):
        for c in range(8):
            for k in range(4):
                self.assertIn(bits_shift(k,c),(0,1))
        for bad in (-1,4,True):
            with self.assertRaises(ValueError):
                bits_shift(bad,0)
        self.assertEqual(bits_shift(3,0),0)
    def test_analytic_evi_two_outcome_identity_no_held(self):
        x=myopic_identity([1/6.]*6)
        self.assertEqual(x["action_cases"],8)
        self.assertLessEqual(x["max_abs_error"],1e-10)
    def test_checkpoint_negative_without_held(self):
        m=JointHypothesis([1/6.]*6)
        m.observe(0,0,0,1)
        raw=m.checkpoint()
        self.assertEqual(JointHypothesis.restore(raw,digest(raw)).checkpoint(),raw)
        with self.assertRaises(ValueError):
            JointHypothesis.restore(raw,"0"*64)
        with self.assertRaises(ValueError):
            m.observe(0,0,0,1)
        with self.assertRaises(ValueError):
            m.observe(1,1,0,1,source_mode="owner_original")
if __name__=="__main__":
    unittest.main()
