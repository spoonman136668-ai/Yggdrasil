"""ST7 source-real TRAIN-only native induction and conventional controls.

No held, negative-rule or first-use outcome. Any positive estimates
here use ONLY original frozen training-law 3 public action experiences.
"""
import json
import unittest

from research.nci04_st7.private_world import PrivateQuadraticWorld,ACTIONS
from research.nci04_st7.native_induction import (
    NativeInductive8,quadratic_features,canonical
)
from research.nci04_st7.matched_controls import (
    GF2Conventional,Logistic36,models,restored_models,brier
)


def drive(models,law=3,seed=100,trial=0,train=True):
    w=PrivateQuadraticWorld(law,seed,trial)
    for m in models.values():m.reset_episode()
    score=None
    for step,action in enumerate(ACTIONS):
        public=w.public()
        before={n:m.predict(public,action) for n,m in models.items()}
        if step==4:
            score={}
        after,target=w.step(action)
        for n,m in models.items():
            self_prediction=m.observe(public,action,target,after,train=train)
            assert self_prediction==before[n]
            if step==4:
                score[n]=brier(before[n],target)
    return score


class ST7NativeInductionTests(unittest.TestCase):
    def test_native_learned_evidence_only_after_genuine_final_action(self):
        m=NativeInductive8()
        w=PrivateQuadraticWorld(3,100,0)
        for i,action in enumerate(ACTIONS):
            x=w.public();pred=m.predict(x,action)
            if i==4:
                self.assertEqual(pred,[.5]*8)
                self.assertEqual(m.updates,0)
            y,delta=w.step(action)
            self.assertEqual(pred,m.observe(x,action,delta,y))
        self.assertEqual(m.updates,1)
        self.assertEqual(m.rank,1)
        self.assertEqual(m.conflicts,0)
        receipt=m.accounting()
        self.assertEqual(receipt["learned_bit_budget"],36*44)
        self.assertEqual(receipt["number_fixed_correct_hypothesis_menu_entries"],0)
        self.assertFalse(receipt["source_private_law_or_coefficient_seen"])

    def test_basis_is_quadratic_not_named_operator_menu(self):
        self.assertEqual(quadratic_features(0),0)
        self.assertEqual(quadratic_features(1),1)
        self.assertEqual(quadratic_features(3)&255,3)
        self.assertNotEqual(quadratic_features(3)>>8,0)
        self.assertEqual(quadratic_features(255).bit_count(),36)
        self.assertEqual(len(NativeInductive8().basis),36)

    def test_native_vs_independent_symbolic_predicts_same_after_fitting(self):
        a=NativeInductive8();b=GF2Conventional()
        for seed in range(100,105):
            for trial in range(16):
                drive({"candidate":a,"gf2":b},3,seed,trial)
        self.assertEqual(a.rank,36)
        self.assertEqual(b.rank,36)
        self.assertEqual(a.conflicts,0)
        self.assertEqual(b.conflicts,0)
        self.assertEqual(a.accounting()["learned_bit_budget"],
                         b.accounting()["learned_bit_budget"])
        for trial in range(16):
            res=drive({"candidate":a,"gf2":b},5,105,trial,False)
            self.assertEqual(res["candidate"],res["gf2"])
            self.assertLess(res["candidate"],.02)
        self.assertEqual(a.updates,80)

    def test_ablations_do_not_get_free_future_labels(self):
        ms={v:NativeInductive8(v) for v in
            ("causal","linear_only","no_b","erase")}
        for trial in range(16):
            drive(ms,3,100,trial)
        self.assertEqual(ms["causal"].updates,16)
        self.assertLessEqual(ms["linear_only"].rank,8)
        self.assertEqual(ms["no_b"].rank,0)
        ms["erase"].reset_episode()
        self.assertEqual(ms["erase"].rank,0)
        self.assertTrue(all(m.accounting()[
            "source_private_law_or_coefficient_seen"] is False
            for m in ms.values()))

    def test_cold_restore_mid_episode_exact_integer_state(self):
        m=NativeInductive8()
        drive({"candidate":m},3,100,0)
        m.reset_episode()
        world=PrivateQuadraticWorld(3,102,1)
        for act in ACTIONS[:3]:
            x=world.public();y,delta=world.step(act)
            m.observe(x,act,delta,y)
        cold=m.snapshot()
        restored=NativeInductive8.restore(cold)
        self.assertEqual(restored.snapshot(),cold)
        for action in ACTIONS[3:]:
            x=world.public()
            self.assertEqual(restored.predict(x,action),m.predict(x,action))
            y,d=world.step(action)
            self.assertEqual(restored.observe(x,action,d,y),
                             m.observe(x,action,d,y))
            self.assertEqual(restored.snapshot(),m.snapshot())

    def test_saturation_bounds_and_invalid_checkpoint_fail_closed(self):
        m=NativeInductive8()
        drive({"candidate":m},3,100,0)
        for edit in (
            {"schema":"other"},{"step":6},{"rank":37},
            {"updates":True},{"basis":[True]*36},
            {"basis":[1<<44]*36},{"conflicts":-1},
        ):
            bad=json.loads(m.snapshot());bad.update(edit)
            with self.assertRaises(ValueError):
                NativeInductive8.restore(canonical(bad))

    def test_invalid_transition_does_not_mutate_model(self):
        m=NativeInductive8()
        w=PrivateQuadraticWorld(3,100,0)
        x=w.public()
        snap=m.snapshot()
        for action,target,after,train in (
            (2,(0,)*8,x,True),(3,(1,)*8,x,True),
            (3,(0,)*8,x,1),(3,(0,)*8,x,"train")
        ):
            with self.assertRaises(ValueError):
                m.observe(x,action,target,after,train=train)
            self.assertEqual(snap,m.snapshot())

    def test_fully_trained_logistic_has_eight_outputs_and_288_weights(self):
        m=Logistic36()
        baseline=m.snapshot()
        drive({"logistic":m},3,100,0)
        self.assertEqual(m.fitted,1)
        self.assertNotEqual(m.snapshot(),baseline)
        self.assertEqual(m.accounting()["trained_float_parameters"],288)
        restored=Logistic36.restore(m.snapshot())
        self.assertEqual(restored.snapshot(),m.snapshot())
        m.reset_episode()
        prev=json.loads(m.snapshot())["weights"]
        drive({"logistic":m},3,101,0,False)
        self.assertEqual(prev,m.weights)

    def test_seven_shared_public_source_interfaces_and_snapshots(self):
        m=models()
        self.assertEqual(set(m),{
            "candidate","gf2_conventional","logistic36","st6_menu",
            "linear_only","no_b","erase"
        })
        drive(m,3,100,0)
        blobs={n:x.snapshot() for n,x in m.items()}
        recovered=restored_models(blobs)
        self.assertTrue(all(recovered[n].snapshot()==blobs[n]
                            for n in m))

    def test_conventional_solver_cold_checkpoint_corruption(self):
        a=GF2Conventional()
        drive({"gf2":a},3,100,0)
        snap=a.snapshot()
        self.assertEqual(GF2Conventional.restore(snap).snapshot(),snap)
        d=json.loads(snap);d["rows"]=[True]*36
        with self.assertRaises(ValueError):
            GF2Conventional.restore(canonical(d))

    def test_brier_missing_and_nonfinite_predictions_fail(self):
        self.assertEqual(brier([.5]*8,(1,)*8),.25)
        with self.assertRaises(ValueError):
            brier([float("nan")]*8,(1,)*8)
        with self.assertRaises(ValueError):
            brier([.5]*7,(1,)*8)


if __name__=="__main__":unittest.main()
