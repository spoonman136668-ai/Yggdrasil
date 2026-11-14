"""Pre-first-use structural, provenance, negative, and checkpoint tests only."""
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location("cr16",Path(__file__).with_name("cr16.py"))
p=importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


class FrozenRepairTests(unittest.TestCase):
    def test_seed_manifest_identity_without_primary_use(self):
        manifest={"schema":"yggdrasil.dg1-cr16-seeds.v1",
                  "world_seeds":list(range(310001,310017)),
                  "training_steps_per_world":192,
                  "audit_cases_per_checkpoint":12,
                  "checkpoints":[72,144,168,192]}
        self.assertEqual(p.digest(manifest),p.MANIFEST)
        self.assertEqual(p.FREEZE,"cd2823483a9d984915e887cd6a076a15c0a59b68")
        self.assertEqual(len(p.ARMS),5)
        self.assertEqual(len(p.SEEDS),16)

    def test_no_invalid_motor_or_nonphysical_values(self):
        for value in (-1,6,1.5,True):
            with self.assertRaises(ValueError):
                p.features([.1,.2,.3],value)
        with self.assertRaises(ValueError):
            p.features([float("nan"),.2,.3],0)
        with self.assertRaises(ValueError):
            p.World(7).next([0.,0.,0.],0,4)

    def test_rls_fits_actual_outcomes_without_rule_labels(self):
        m=p.RLS()
        f=p.features([.2,.1,-.3],2)
        for _ in range(30):
            m.fit(f,.7)
        self.assertLess(abs(m.predict(f)-.7),.001)
        self.assertEqual(m.n,30)

    def test_prospective_world_interventions_are_physical(self):
        w=p.World(7)  # never a registered first-use seed
        x=[.2,-.3,.4]
        y0=w.step(x,0,0)
        y1=w.step(x,1,0)
        self.assertNotEqual(y0,y1)
        self.assertEqual(w.charged,2)
        self.assertEqual(w.lesion,1)
        self.assertIs(w.matrices[0],w.matrices[2])
        self.assertNotEqual(w.matrices[0][1],w.matrices[1][1])

    def test_all_five_learners_update_only_from_outcomes(self):
        x=[.2,-.1,.4]
        for arm in p.ARMS:
            m=p.learner(arm)
            before=m.predict(x,2)
            for step in range(20):
                m.observe(x,2,[.1+step*.0001,-.2,.3])
            self.assertEqual(m.count,20)
            self.assertNotEqual(before,m.predict(x,2))
            self.assertLess(len(p.snapshot(m)),65536)

    def test_cold_round_trip_and_same_action_predictions(self):
        x=[.2,-.1,.4]
        for arm in p.ARMS:
            m=p.learner(arm)
            for i in range(35):
                m.observe(x,i%6,[.12,-.21,.3])
            original=p.snapshot(m)
            twin=p.restore(original)
            self.assertEqual(original,p.snapshot(twin))
            self.assertEqual([m.predict(x,a) for a in range(6)],
                             [twin.predict(x,a) for a in range(6)])

    def test_cold_does_not_uncharge_physical_actions(self):
        w=p.World(19)
        for arm in p.ARMS:
            learner=p.learner(arm)
            x=[.1,.2,-.1]
            y=w.step(x,1,0)
            learner.observe(x,1,y)
            rebuilt=p.restore(p.snapshot(learner))
            self.assertEqual(rebuilt.count,1)
        self.assertEqual(w.charged,5)

    def test_predict_is_side_effect_free_and_evaluator_hidden(self):
        x=[.3,-.1,.2]
        for arm in p.ARMS:
            m=p.learner(arm)
            raw=p.snapshot(m)
            for a in range(6): m.predict(x,a)
            self.assertEqual(p.snapshot(m),raw)
            self.assertNotIn("lesion",vars(m))
            self.assertNotIn("matrices",vars(m))

    def test_audit_charges_exactly_twelve_action_consequences(self):
        w=p.World(7)
        m=p.learner("forgetting_rls")
        result=p.audit(m,w,7,72)
        self.assertEqual(w.charged,12)
        self.assertEqual(len(result["choices"]),12)
        self.assertGreaterEqual(result["regret"],-.000000001)


if __name__=="__main__":
    unittest.main()
