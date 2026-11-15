"""ST6 authentic TRAIN-only native composition and strong control fixtures.

No frozen held IDs 29/31/37/41, negative 43/47, or protected science.
All learner APIs receive current public action/state and past observed
changes only. Frozen original source is evaluator-side, not an input.
"""
import json
import unittest

from research.nci04_st6.original_world import (
    OriginalWorld,ACTIONS,source_episode,hypothesis_outputs
)
from research.nci04_st6.native_operator import (
    NativeOperator8,menu,canonical
)
from research.nci04_st6.matched_controls import (
    SymbolicSelector,create_models,restored_models,restore_one,brier
)


def run_episode(models,law=3,seed=100,trial=0,train=True):
    world=OriginalWorld(law,seed,trial)
    for m in models.values():m.reset_episode()
    last={}
    for action in ACTIONS:
        public=world.public()
        predictions={n:m.predict(public,action) for n,m in models.items()}
        after,target=world.step(action)
        for n,m in models.items():
            response=m.observe(public,action,target,after,train=train)
            assert response==predictions[n]
        if action==3 and len(last)==0 and any(m.step==5 for m in models.values()):
            last={n:brier(predictions[n],target) for n in models}
    return last


class ST6NativeCompositionFixture(unittest.TestCase):
    def test_direct_operator_hypothesis_matches_public_math(self):
        for a,b in ((4,128),(171,99),(0,255)):
            self.assertEqual(menu(a,b),hypothesis_outputs(a,b))
        self.assertEqual(len(menu(17,31)),8)

    def test_no_oracle_prediction_before_real_source_final_action(self):
        m=NativeOperator8()
        w=OriginalWorld(3,100,0)
        for step,act in enumerate(ACTIONS):
            public=w.public()
            pred=m.predict(public,act)
            self.assertEqual(pred,[.5]*8)
            after,target=w.step(act)
            self.assertEqual(m.observe(public,act,target,after),pred)
            self.assertEqual(m.training_probes,int(step==4))
        self.assertEqual(m.support,[8]*8)
        self.assertEqual(m.mismatches[0],0)
        self.assertEqual(m.accounting()["learned_uint32_error_support_bytes"],64)

    def test_same_public_source_stable_exact_symbolic_equivalence(self):
        models={"candidate":NativeOperator8(),"symbolic8":SymbolicSelector()}
        for law in (3,5):
            for trial in range(8):
                w=OriginalWorld(law,100,trial)
                for model in models.values():model.reset_episode()
                for act in ACTIONS:
                    public=w.public()
                    self.assertEqual(
                        models["candidate"].predict(public,act),
                        models["symbolic8"].predict(public,act)
                    )
                    after,target=w.step(act)
                    for model in models.values():
                        model.observe(public,act,target,after)
        self.assertEqual(
            models["candidate"].accounting()[
                "learned_uint32_error_support_bytes"],
            models["symbolic8"].accounting()[
                "learned_uint32_error_support_bytes"]
        )

    def test_one_familiar_operator_transfers_to_unseen_training_pair(self):
        m=NativeOperator8()
        for trial in range(8):
            run_episode({"candidate":m},3,100,trial,train=True)
        scores=[]
        for trial in range(6):
            scores.append(run_episode({"candidate":m},5,101,trial,
                                      train=False)["candidate"])
        self.assertLess(sum(scores)/len(scores),.05)
        self.assertEqual(m.training_probes,8)

    def test_erasure_and_ignored_component_ablation(self):
        models={v:NativeOperator8(v) for v in
                ("causal","no_b","erase","shuffle")}
        for t in range(6):
            run_episode(models,3,100,t)
        scores=run_episode(models,5,101,1,train=False)
        self.assertLess(scores["causal"],.05)
        self.assertGreaterEqual(scores["erase"],.20)
        self.assertTrue(all(m.accounting()["private_source_or_law_access"] is False
                            for m in models.values()))

    def test_public-only_frozen_st5_memory_and_recurrent_compatibility(self):
        models=create_models()
        self.assertEqual(set(models),{
            "candidate","symbolic8","st5_exact_key","recurrent45",
            "no_b","shuffle","erase"
        })
        for t in range(3):run_episode(models,3,100,t)
        self.assertEqual(models["st5_exact_key"].learned_probes,3)
        self.assertEqual(models["recurrent45"].train_steps,15)

    def test_all_seven_exact_source_trained_cold_checkpoints(self):
        models=create_models()
        run_episode(models,3,100,0)
        snapshots={n:m.snapshot() for n,m in models.items()}
        restored=restored_models(snapshots)
        self.assertTrue(all(restored[n].snapshot()==snapshots[n]
                            for n in restored))

    def test_native_mid_source_exact_integer_cold_continuation(self):
        m=NativeOperator8()
        w=OriginalWorld(3,100,0)
        for act in ACTIONS[:3]:
            before=w.public();after,target=w.step(act)
            m.observe(before,act,target,after)
        snapshot=m.snapshot()
        restore=NativeOperator8.restore(snapshot)
        self.assertEqual(restore.snapshot(),snapshot)
        for act in ACTIONS[3:]:
            before=w.public()
            self.assertEqual(m.predict(before,act),restore.predict(before,act))
            after,target=w.step(act)
            self.assertEqual(
                m.observe(before,act,target,after),
                restore.observe(before,act,target,after)
            )
            self.assertEqual(m.snapshot(),restore.snapshot())

    def test_invalid_source_action_transition_is_atomic(self):
        m=NativeOperator8();w=OriginalWorld(3,100,0)
        old=m.snapshot();x=w.public()
        for action,target,after,train in (
            (2,(0,)*8,x,True),(3,(0,)*8,(1,)*8,True),
            (3,(0,)*8,x,1),(3,(0,)*8,x,"train")
        ):
            with self.assertRaises(ValueError):
                m.observe(x,action,target,after,train=train)
            self.assertEqual(m.snapshot(),old)

    def test_corrupted_cold_native_checkpoint_rejected(self):
        m=NativeOperator8();run_episode({"candidate":m},3,100,0)
        for patch in (
            {"schema":"wrong"},{"step":6},{"mismatches":[2]*8},
            {"support":[True]*8},{"r":4},{"training_probes":True}
        ):
            d=json.loads(m.snapshot());d.update(patch)
            with self.assertRaises(ValueError):
                NativeOperator8.restore(canonical(d))

    def test_symbolic_checkpoint_independent_weak_cases(self):
        m=SymbolicSelector()
        run_episode({"symbolic":m},3,100,0)
        checkpoint=m.snapshot()
        self.assertEqual(SymbolicSelector.restore(checkpoint).snapshot(),checkpoint)
        d=json.loads(checkpoint);d["samples"]=[True]*8
        with self.assertRaises(ValueError):
            SymbolicSelector.restore(canonical(d))

    def test_prediction_shape_valid_and_brier_cannot_accept_nans(self):
        self.assertAlmostEqual(brier([.5]*8,(1,)*8),.25)
        with self.assertRaises(ValueError):
            brier([float("nan")]*8,(1,)*8)


if __name__=="__main__":unittest.main()
