"""Focused physical billing, contradiction specificity and cold-custody tests."""
import unittest
from sl07 import (
    ARMS,COHORTS,FLIPS,FREEZE,Agent,World,contradiction,one_world,run
)

class SL07Tests(unittest.TestCase):
    def test_registered_world_charged_actions(self):
        for group,seeds in COHORTS.items():
            w=World(seeds[0],group)
            s=seeds[0]%16
            for step in range(80):
                k,a,s=w.step(s,step,step%4 if step>=60 and step not in FLIPS else None)
                self.assertIn(k,("causal","flip"))
            self.assertEqual(w.paid,80)
            with self.assertRaises(ValueError):w.step(s,79,0)
        with self.assertRaises(ValueError):World(99001,"ABCA")

    def test_contradiction_is_not_surprise(self):
        a=Agent("native_witness")
        a.model.banks=[[1]*4,[2]*4]
        a.model.hits=[3,3]
        a.model.last_used=[0,0]
        self.assertTrue(contradiction(a.model,0,0,1,a.family))
        self.assertFalse(contradiction(a.model,0,0,0,a.family))
        self.assertFalse(contradiction(a.model,0,1,0,a.family))
        a.observe(0,0,1,60)
        self.assertEqual(a.armings,0)
        a.observe(1,1,1,61)
        self.assertEqual(a.armings,1)
        self.assertEqual(a.armed,4)
        self.assertIn(a.choose(0,63),range(4))
        a.observe(0,0,1,63)
        self.assertEqual(a.armed,3)

    def test_no_oracle_or_unpaid_probe(self):
        for arm in ARMS:
            a=Agent(arm)
            with self.assertRaises(ValueError):a.choose(0,59)
            with self.assertRaises(ValueError):a.choose(0,62)
            with self.assertRaises(TypeError):a.observe(0,0,0,60,hidden_phase="A")
            with self.assertRaises(ValueError):a.observe(0,0,2,60)
            with self.assertRaises(ValueError):a.observe(0,0,0,62)
            self.assertEqual(a.causal_events,0)

    def test_checkpoint_restores_policy_and_rejects_tamper(self):
        for arm in ARMS:
            a=Agent(arm)
            a.observe(0,0,0,0)
            a.observe(1,1,1,1)
            a.rest()
            raw=a.snapshot()
            restored=Agent.restore(raw)
            self.assertEqual(restored.snapshot(),raw)
            self.assertLessEqual(len(raw),8192)
            for state in range(16):
                for action in range(4):
                    self.assertEqual(a.predict(state,action),
                                     restored.predict(state,action))
            for invalid in (raw[:-1],raw+b" ",bytearray(raw),
                            bytes([raw[0]^1])+raw[1:]):
                with self.assertRaises(ValueError):Agent.restore(invalid)

    def test_single_world_paid_fairness_and_frozen_cold(self):
        w=one_world(100101,"ABCA")
        self.assertEqual(set(w["arms"]),set(ARMS))
        for arm,o in w["arms"].items():
            self.assertEqual(o["charged_physical_actions"],80)
            self.assertEqual(o["causal_observations"],70)
            self.assertTrue(o["cold_restore_pass"])
            self.assertEqual(o["pre_cold_trajectory_sha256"],
                             w["shared_pre_cold_trace_sha256"])
            self.assertEqual(len(o["post_cold_actions"]),17)
            self.assertLessEqual(max(o["checkpoint_bytes"].values()),8192)
            for stage in ("60","64","72","80"):
                v=o["stage_audits"][stage]
                self.assertEqual(v["correct"]+v["wrong_confident"]+v["abstained"],64)

    def test_prereg_seal(self):
        self.assertEqual(FREEZE,"27d0ad88fdb64dda815cfb248cf47faf8b2f8e5a")
        self.assertEqual(len(COHORTS),4)
        self.assertEqual(sum(map(len,COHORTS.values())),32)
        self.assertEqual(len(ARMS),7)

if __name__=="__main__":
    unittest.main()
