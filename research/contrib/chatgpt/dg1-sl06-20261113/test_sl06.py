"""Precommitted SL06 negative/custody and action-billing tests."""
import unittest
from sl06 import (ARMS,COHORTS,FREEZE,FLIPS,World,choose,learner_for,restore,
                  experiment,native_information_action,conventional_information_action)

class SL06Qualification(unittest.TestCase):
    def test_registered_physical_world(self):
        for group,seeds in COHORTS.items():
            w=World(seeds[0],group)
            s=seeds[0]%16
            for i in range(80):
                c=i%4 if i>=60 and i not in FLIPS else None
                k,a,s=w.step(s,i,c)
                self.assertIn(k,("causal","flip"))
            self.assertEqual(w.paid,80)
            with self.assertRaises(ValueError):w.step(s,79,0)
        with self.assertRaises(ValueError):World(99000,"ABCA")
    def test_no_free_action_probe_or_phase_input(self):
        for arm in ARMS:
            m=learner_for(arm)
            for state in range(16):
                action=choose(arm,m,state,60)
                self.assertIn(action,range(4))
            with self.assertRaises(TypeError):
                m.observe(0,0,0,hidden_phase=1)
            with self.assertRaises(ValueError):
                m.observe(0,0,2)
            with self.assertRaises(ValueError):
                choose(arm,m,0,59)
        with self.assertRaises(ValueError):
            World(99001,"ABCA").step(0,0,0)
    def test_cold_restore_without_learning_change(self):
        for arm in ARMS:
            m=learner_for(arm)
            for e in ((0,0,0),(1,0,1),(2,1,2)):
                m.observe(*e)
            raw=m.snapshot()
            restored=restore(arm,raw)
            self.assertEqual(raw,restored.snapshot())
            for state in range(16):
                for action in range(4):
                    self.assertEqual(m.predict(state,action),restored.predict(state,action))
            with self.assertRaises(ValueError):
                restore(arm,raw[:-1])
    def test_gated_frozen_memory_and_pure_policy(self):
        a=learner_for("native_active")
        b=learner_for("native_active_no_gate")
        c=learner_for("conventional_active")
        self.assertTrue(a.gate)
        self.assertFalse(b.gate)
        self.assertEqual(native_information_action(a,0),native_information_action(b,0))
        self.assertIn(conventional_information_action(c,0),range(4))
        self.assertEqual(a.clock,0)
        self.assertEqual(b.clock,0)
        self.assertEqual(c.clock,0)
    def test_paired_pre_cold_and_charged_post_cold(self):
        w=experiment(99001,"ABCA")
        h=w["pre_cold_trajectory_sha256"]
        self.assertEqual(set(w["arms"]),set(ARMS))
        for arm,o in w["arms"].items():
            self.assertEqual(o["charged_actions"],80)
            self.assertEqual(o["causal_observations"],70)
            self.assertEqual(o["pre_cold_trajectory_sha256"],h)
            self.assertTrue(o["cold_restored"])
            self.assertEqual(len(o["post_cold_action_sequence"]),17)
            self.assertLessEqual(o["checkpoint_bytes"]["80"],8192)
            for point in ("60","64","72","80"):
                self.assertEqual(sum(o["audits"][point][k] for k in
                                 ("correct","wrong_confident","abstained")),64)
    def test_prereg_identity(self):
        self.assertEqual(FREEZE,"2d3e530cf21e0a87596246eff648832c66737058")
        self.assertEqual(len(COHORTS),4)
        self.assertEqual(sum(len(x) for x in COHORTS.values()),32)
        self.assertEqual(len(ARMS),7)

if __name__ == "__main__":
    unittest.main()
