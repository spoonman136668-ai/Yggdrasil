import unittest
from sl03 import ARMS, Learner, PhysicalWorld, candidate_for, fitted_mask, one_world, run

class SL03Qualification(unittest.TestCase):
    def test_frozen_independent_physical_schedule(self):
        w=PhysicalWorld(95001,"ABA")
        s=1
        seen=[]
        for i in range(48):
            kind,a,nxt=w.step(s,i)
            seen.append(kind)
            s=nxt
        self.assertEqual(seen.count("flip"),6)
        self.assertEqual(w.paid_actions,48)
        with self.assertRaises(ValueError): w.step(s,47)
    def test_no_oracle_input_to_learner(self):
        m=Learner("selective_sleep")
        self.assertIsNone(m.predict(0,0))
        with self.assertRaises(TypeError):m.observe(0,0,0,hidden_phase=1)
        with self.assertRaises(ValueError):m.observe(0,0,2)
        self.assertEqual(len(m.events),0)
    def test_cold_restore_and_tamper(self):
        for arm in ARMS:
            m=Learner(arm)
            m.observe(0,0,0)
            m.rest()
            data=m.snapshot()
            self.assertEqual(Learner.restore(data).snapshot(),data)
            self.assertLessEqual(len(data),8192)
            for bad in (data[:-1],data+b"x",bytearray(data),bytes([data[0]^1])+data[1:]):
                with self.assertRaises(ValueError):Learner.restore(bad)
    def test_offline_uses_only_real_observations(self):
        m=Learner("selective_sleep")
        for event in ((0,0,0),(1,0,1),(3,1,3),(5,2,5)):
            m.observe(*event)
        old=list(m.events)
        m.rest()
        self.assertEqual(m.events,old)
        self.assertEqual(m.model.observations,4)
        self.assertIsNotNone(candidate_for([tuple(e) for e in old],"native"))
    def test_one_world_matched_and_source_bound(self):
        w=one_world(95001,"ABA")
        self.assertEqual(w["charged_actions"],48)
        self.assertEqual(w["mechanism_observations"],42)
        self.assertTrue(w["cold_restore_identical"])
        self.assertEqual(set(w["audits"]),set(ARMS))
        self.assertEqual(w["audits"]["selective_sleep"]["48"],w["audits"]["online_same_compute"]["48"])
        for arm in ARMS:
            self.assertEqual(sum(w["audits"][arm]["48"][k] for k in
                             ("correct","wrong_confident","abstained")),64)
    def test_result_custody(self):
        res=run()
        self.assertEqual(res["freeze_sha"],"93f91491b6235945b16ab5928c06c64f8ca84581")
        self.assertEqual(len(res["worlds"]),24)
        self.assertEqual(res["charged_actions_total"],1152)
        self.assertFalse(res["same_total_compute"])
        self.assertEqual(res["scientific_acceptance"],"UNVERIFIED")

if __name__=="__main__":
    unittest.main()
