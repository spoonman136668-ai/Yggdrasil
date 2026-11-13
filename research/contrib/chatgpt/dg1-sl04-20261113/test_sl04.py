import unittest
from sl04 import (ARMS,SEEDS,SEAL,PhysicalWorld,BayesianTwoBank,RecentWindow,
                  restore_control,new_learner,one_world,run)
class SL04Tests(unittest.TestCase):
    def test_physical_custody(self):
        for group,seeds in SEEDS.items():
            world=PhysicalWorld(next(iter(seeds)),group)
            s=next(iter(seeds))%16
            flips=0
            for step in range(64):
                kind,a,s=world.step(s,step)
                flips+=int(kind=="flip")
            self.assertEqual(flips,8)
            self.assertEqual(world.paid,64)
            with self.assertRaises(ValueError):world.step(s,63)
            with self.assertRaises(ValueError):world.audit_truth(0,0,37)
    def test_no_oracle_in_the_learner(self):
        for arm in ARMS:
            m=new_learner(arm)
            with self.assertRaises(TypeError):m.observe(0,0,0,hidden_phase="A")
            with self.assertRaises(ValueError):m.observe(0,0,2)
            self.assertIsNone(m.predict(0,0))
    def test_cold_checkpoint_canonical_and_tamper(self):
        for cls in (BayesianTwoBank,RecentWindow):
            agent=cls()
            agent.observe(0,0,0)
            snap=agent.snapshot()
            self.assertEqual(restore_control(snap).snapshot(),snap)
            for bad in (snap[:-1],snap+b" ",bytearray(snap),
                        bytes([snap[0]^1])+snap[1:]):
                with self.assertRaises(ValueError):restore_control(bad)
    def test_context_transfer_and_equal_paid_experience(self):
        for group in SEEDS:
            w=one_world(next(iter(SEEDS[group])),group)
            self.assertEqual(w["physical_actions"],64)
            self.assertEqual(w["mechanism_observations"],56)
            self.assertTrue(w["cold_restore_identical"])
            self.assertLessEqual(max(w["snapshot_bytes"].values()),8192)
            for arm in ARMS:
                self.assertEqual(sum(w["audits"][arm]["64"][k] for k in
                               ("correct","wrong_confident","abstained")),64)
    def test_exact_cohorts_and_prereg(self):
        r=run()
        self.assertEqual(r["prereg_sha"],SEAL)
        self.assertEqual(len(r["worlds"]),24)
        self.assertEqual(r["charged_physical_actions"],24*64)
        self.assertFalse(r["same_total_compute"])
        self.assertEqual(r["scientific_acceptance"],"UNVERIFIED")
        self.assertTrue(r["same_physical_actions"])
if __name__=="__main__":
    unittest.main()
