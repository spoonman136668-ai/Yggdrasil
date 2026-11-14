"""Pre-first-use IV18 structural and negative tests. All seeds are unregistered."""
import importlib.util
import json
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location("iv18",Path(__file__).with_name("iv18.py"))
p=importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


class BoundedInterventionTests(unittest.TestCase):
    def test_frozen_preregistration_seed_identity(self):
        manifest={"schema":"yggdrasil.dg1-iv18-seeds.v1",
                  "world_seeds":list(range(520001,520017)),
                  "phase_steps":[64,64,32],
                  "audit_episodes_per_mark":12,
                  "audit_marks":[128,160],
                  "probe_actions_per_audit":2,
                  "goal_actions_per_audit":2,
                  "arms":list(p.ARMS)}
        self.assertEqual(p.MANIFEST,p.digest(manifest))
        self.assertEqual(p.MANIFEST,"37b70a87720bfbc26a7fe05f6460cbf6c1607a7f07cdb2b04eb85c452f2a10fb")
        self.assertEqual(p.FREEZE,"20b0af804ffbd04d7e3d22cdf39b3c82a14d7093")
        self.assertEqual(len(p.ARMS),6)

    def test_physical_world_novel_nonlinear_C(self):
        w=p.World(11)
        x=[p.Q//2,p.Q//3,p.Q//4]
        self.assertNotEqual(w.step(x,0,0),w.step(x,1,0))
        self.assertEqual(w.charged,2)
        self.assertEqual(w.matrices[0],w.matrices[2])
        self.assertNotEqual(w.matrices[2],w.matrices[3])
        novel=(w.lesion+2)%3
        integer_linear=p.divr(sum(w.matrices[3][novel][k]*x[k] for k in range(3)),p.Q)
        actual=w.next(x,0,3)[novel]
        self.assertNotEqual(actual,integer_linear)
        self.assertEqual(w.charged,2)  # evaluator-only next does not charge

    def test_invalid_actions_and_nonphysical_features_rejected(self):
        for action in (6,-1,True,1.5):
            with self.assertRaises(ValueError):
                p.features([0,1,2],action)
        for x in ([.1,1,2],[1,2],[9*p.Q,0,0]):
            with self.assertRaises(ValueError):
                p.features(x,0)

    def test_all_six_learners_cold_start_and_update(self):
        x=[410,-220,230]
        for arm in p.ARMS:
            m=p.learner(arm)
            before=m.predict(x,2)
            for t in range(28):
                m.observe(x,t%6,[100+t,-110+t,15-t])
            self.assertEqual(m.count,28)
            self.assertNotEqual(before,m.predict(x,2),arm)
            self.assertLessEqual(len(p.snapshot(m)),65536)

    def test_equal_training_for_gate_and_sham_ablation(self):
        models=[p.learner(a) for a in ("certified_gate","ungated_route","sham_route")]
        for t in range(40):
            x=[t*13-100,t*7-60,t*9-90]
            y=[30+t,-60+t,90-t]
            for m in models:
                m.observe(x,t%6,y)
        self.assertEqual(models[0].dump()["rows"],models[1].dump()["rows"])
        self.assertEqual(models[0].dump()["rows"],models[2].dump()["rows"])
        self.assertEqual(models[0].switches,models[2].switches)

    def test_two_probes_can_veto_implausible_archive(self):
        arms={a:p.learner(a) for a in ("certified_gate","ungated_route","sham_route")}
        x=[120,-190,210]
        for t in range(30):
            for m in arms.values():
                m.observe(x,t%6,[100,-70,90])
        probes=((x,0,[6*p.Q,7*p.Q,8*p.Q]),
                ([300,-200,250],3,[-6*p.Q,-7*p.Q,-8*p.Q]))
        veto=p.probe_routes(arms["certified_gate"],probes,11,160,2)
        ungated=p.probe_routes(arms["ungated_route"],probes,11,160,2)
        self.assertEqual(veto,[None,None,None])
        self.assertTrue(all(k is not None for k in ungated))
        self.assertEqual(p.snapshot(arms["certified_gate"]),p.snapshot(arms["certified_gate"]))

    def test_recurrent_all_weight_groups_train_in_fixed_point(self):
        m=p.IntegerRecurrent()
        before={k:json.dumps(getattr(m,k)) for k in ("wx","wh","v","b","c")}
        for t in range(160):
            x=[(t*47)%p.Q-p.Q//2,(t*77)%p.Q-p.Q//2,(t*91)%p.Q-p.Q//2]
            y=[(t*19)%p.Q-p.Q//2,(t*31)%p.Q-p.Q//2,(t*61)%p.Q-p.Q//2]
            m.observe(x,t%6,y)
        for key in before:
            self.assertNotEqual(before[key],json.dumps(getattr(m,key)),key)
        self.assertTrue(all(type(v) is int for row in m.wx for v in row))

    def test_cold_checkpoint_byte_exact_and_read_only_audits(self):
        x=[200,-100,150]
        for arm in p.ARMS:
            m=p.learner(arm)
            for t in range(35):
                m.observe(x,t%6,[100+t,-70+t,80-t])
            raw=p.snapshot(m)
            twin=p.restore(raw)
            self.assertEqual(raw,p.snapshot(twin))
            self.assertEqual([m.predict(x,a) for a in range(6)],
                             [twin.predict(x,a) for a in range(6)])
            w=p.World(19)
            result=p.audit(twin,w,19,160)
            self.assertEqual(w.charged,48)
            self.assertEqual(len(result["choices"]),12)
            self.assertEqual(raw,p.snapshot(twin))
            self.assertGreaterEqual(result["regret"],-1e-10)

    def test_toy_full_budget_no_registered_first_use(self):
        self.assertTrue(all(s not in p.SEEDS for s in (11,19)))
        for arm in p.ARMS:
            data=p.one_arm(19,arm)
            self.assertEqual(data["paid_steps"],256)
            self.assertEqual(data["charged_observations"],160)
            self.assertEqual(len(data["cold_bytes"]),3)
            self.assertEqual(len(data["audits"]["128"]["choices"]),12)
            self.assertEqual(len(data["audits"]["160"]["choices"]),12)


if __name__=="__main__":
    unittest.main()
