"""T17 pre-first-use structural and negative controls; never use registered seeds."""
import importlib.util
import json
import hashlib
from pathlib import Path
import unittest

base=Path(__file__).parent
spec=importlib.util.spec_from_file_location("t17",base/"t17.py")
p=importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


class ProtocolTests(unittest.TestCase):
    def test_preregistered_seed_manifest(self):
        m={"schema":"yggdrasil.dg1-t17-seeds.v1",
           "world_seeds":list(range(410001,410017)),
           "phase_steps":[64,64,32],
           "audit_episodes_per_mark":16,"audit_marks":[128,160],
           "probe_actions_per_audit":1,"goal_actions_per_audit":1,
           "arms":list(p.ARMS)}
        self.assertEqual(p.digest(m),"eb975980ff8fae294128cd651e1d04f3b373f2263cdecce21b4fdffc7c21a8c4")
        self.assertEqual(p.digest(m),p.MANIFEST)
        self.assertEqual(p.FREEZE,"a4c0ee310f12f55535f8b5dea6ab2f0b190a6fe9")
        self.assertEqual(len(p.ARMS),5)

    def test_integer_world_physical_and_phase_private(self):
        w=p.World(11)
        x=[110,-120,55]
        self.assertNotEqual(w.step(x,0,0),w.step(x,1,0))
        self.assertEqual(w.charged,2)
        self.assertEqual(w.matrices[0],w.matrices[2])
        self.assertNotEqual(w.matrices[0][w.lesion],w.matrices[1][w.lesion])
        self.assertNotEqual(w.matrices[2],w.matrices[3])

    def test_invalid_observations_are_refused(self):
        for a in (-1,6,True,2.5):
            with self.assertRaises(ValueError):
                p.features([1,2,3],a)
        for x in ([.1,2,3],[1,2],[1,2,9*p.Q]):
            with self.assertRaises(ValueError):
                p.features(x,0)

    def test_trained_recurrent_integer_weights_are_real(self):
        m=p.IntegerRecurrent()
        before={k:json.dumps(getattr(m,k)) for k in ("wx","wh","v","b","c")}
        for t in range(160):
            x=[(t*47)%p.Q-p.Q//2,(t*77)%p.Q-p.Q//2,(t*91)%p.Q-p.Q//2]
            y=[(t*19)%p.Q-p.Q//2,(t*31)%p.Q-p.Q//2,(t*61)%p.Q-p.Q//2]
            m.observe(x,t%6,y)
        self.assertEqual(m.count,160)
        for key in ("wx","wh","v","b","c"):
            self.assertNotEqual(before[key],json.dumps(getattr(m,key)),key)
        self.assertTrue(all(isinstance(weight,int) for row in m.wx for weight in row))

    def test_cold_checkpoint_byte_identity(self):
        x=[150,-200,300]
        for arm in p.ARMS:
            m=p.learner(arm)
            for t in range(40):
                m.observe(x,t%6,[100+t,-25+t,80-t])
            raw=p.snapshot(m)
            twin=p.restore(raw)
            self.assertEqual(raw,p.snapshot(twin))
            self.assertEqual([m.predict(x,a) for a in range(6)],
                             [twin.predict(x,a) for a in range(6)])
            self.assertLessEqual(len(raw),65536)

    def test_diagnostics_are_charged_without_training_leakage(self):
        for arm in p.ARMS:
            w=p.World(17)
            m=p.learner(arm)
            before=p.snapshot(m)
            result=p.audit(m,w,17,128)
            self.assertEqual(w.charged,32)
            self.assertEqual(len(result["choices"]),16)
            self.assertEqual(p.snapshot(m),before)
            self.assertGreaterEqual(result["regret"],-1e-10)

    def test_each_training_arm_updates_observations(self):
        x=[450,-220,120]
        for arm in p.ARMS:
            m=p.learner(arm)
            before=m.predict(x,2)
            for t in range(20):
                m.observe(x,t%6,[100+t,-210+t,15-t])
            self.assertEqual(m.count,20)
            self.assertNotEqual(before,m.predict(x,2),arm)

    def test_registered_data_not_used_in_preflight(self):
        self.assertNotIn(11,p.SEEDS)
        self.assertNotIn(17,p.SEEDS)
        self.assertNotIn(19,p.SEEDS)
        w=p.World(19)
        m=p.learner("forgetting_rls")
        for t in range(10):
            y=w.step([0,0,0],t%6,0)
            m.observe([0,0,0],t%6,y)
        self.assertEqual(w.charged,10)

    def test_per_arm_paid_budget_toy_only(self):
        for arm in p.ARMS:
            record=p.one_arm(19,arm)
            self.assertEqual(record["charged_observations"],160)
            self.assertEqual(record["paid_steps"],224)
            self.assertEqual(len(record["cold_bytes"]),3)
            self.assertEqual(len(record["audits"]["128"]["choices"]),16)
            self.assertEqual(len(record["audits"]["160"]["choices"]),16)


if __name__=="__main__":
    unittest.main()
