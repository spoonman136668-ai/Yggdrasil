"""Source-free and TRAIN-only fixtures for ST5 native recall and controls.

No held unfamiliar laws, no private source parameters passed to a model.
Unlike a hidden source-law identifier, the fingerprint must be obtained
from three actual public preaction/action/consequence transitions.
"""
import json
import unittest

from research.nci04_st5.native_memory import (
    NativeCausalRecall8,canonical,update_count,observed_rotation
)
from research.nci04_st5.matched_controls import (
    SignatureCount8,Recurrent45,brier
)
from research.nci04_st5.diagnostic_world import (
    ACTIONS,DiagnosticWorld,run_original_episode
)


def drive(model,law=3,seed=100,trial=0,train=True):
    world=DiagnosticWorld(law,seed,trial)
    last=None
    for action in ACTIONS:
        before=world.public()
        prediction=model.predict(before,action)
        after,target=world.step(action)
        returned=model.observe(before,action,target,after,train=train)
        assert returned==prediction
        last=(prediction,target)
    return last


class ST5NativeMemoryFixture(unittest.TestCase):
    def test_preaction_no_oracle_and_learning_only_from_real_probe(self):
        m=NativeCausalRecall8()
        self.assertEqual(m.accounting()["source_law_seed_trial_seen"],False)
        self.assertEqual(m.accounting()["learned_uint8_counter_capacity_bytes"],
                         16*8*2)
        world=DiagnosticWorld(3,100,0)
        for step,action in enumerate(ACTIONS):
            before=world.public()
            prediction=m.predict(before,action)
            if step==4:
                self.assertEqual(prediction,[.5]*8)
                self.assertEqual(m.learned_probes,0)
            after,target=world.step(action)
            self.assertEqual(
                m.observe(before,action,target,after,train=True),prediction
            )
            if step<4:
                self.assertEqual(m.learned_probes,0)
        self.assertEqual(m.learned_probes,1)
        self.assertEqual(sum(b is not None for b in m.banks),1)

    def test_public_interventions_index_stable_causal_profile(self):
        m=NativeCausalRecall8()
        drive(m,3,100,0)
        m.reset_episode()
        world=DiagnosticWorld(3,101,2)
        for action in ACTIONS[:3]:
            x=world.public()
            y,t=world.step(action)
            m.observe(x,action,t,y)
        self.assertIsNotNone(m.cue())
        self.assertIn(m.cue(),[tuple(b["key"]) for b in m.banks if b])
        self.assertEqual(m.step,3)

    def test_nontraining_cold_recall_preserves_integer_evidence(self):
        m=NativeCausalRecall8()
        for t in range(8):
            m.reset_episode()
            drive(m,3,100,t,train=True)
        bank_snapshot=canonical(m.banks)
        updates=m.learned_probes
        m.reset_episode()
        prediction,target=drive(m,3,100,1,train=False)
        self.assertEqual(bank_snapshot,canonical(m.banks))
        self.assertEqual(m.learned_probes,updates)
        self.assertLess(brier(prediction,target),.25)

    def test_true_cold_snapshot_and_exact_real_source_continuation(self):
        m=NativeCausalRecall8()
        drive(m,3,100,0)
        m.reset_episode()
        world=DiagnosticWorld(3,101,1)
        for action in ACTIONS[:3]:
            before=world.public()
            after,target=world.step(action)
            m.observe(before,action,target,after)
        original=m.snapshot()
        restore=NativeCausalRecall8.restore(original)
        self.assertEqual(original,restore.snapshot())
        for action in ACTIONS[3:]:
            before=world.public()
            pre=m.predict(before,action)
            self.assertEqual(pre,restore.predict(before,action))
            after,target=world.step(action)
            self.assertEqual(m.observe(before,action,target,after),
                             restore.observe(before,action,target,after))
            self.assertEqual(m.snapshot(),restore.snapshot())

    def test_equal_memory_budget_controls_have_fair_source_public_inputs(self):
        a=NativeCausalRecall8()
        b=SignatureCount8("raw")
        c=SignatureCount8("residual")
        self.assertEqual(
            a.accounting()["learned_uint8_counter_capacity_bytes"],
            b.accounting()["learned_uint8_counter_capacity_bytes"]
        )
        self.assertEqual(
            a.accounting()["learned_uint8_counter_capacity_bytes"],
            c.accounting()["learned_uint8_counter_capacity_bytes"]
        )
        for t in range(8):
            for m in (a,b,c):
                m.reset_episode()
                drive(m,3,100,t)
        # Rotation-normalized conventional count is an intentionally
        # strong algorithmic equivalence control; ties are NOT superiority.
        a.reset_episode(); c.reset_episode()
        world=DiagnosticWorld(3,101,0)
        for action in ACTIONS:
            x=world.public()
            self.assertEqual(a.predict(x,action),c.predict(x,action))
            nxt,target=world.step(action)
            a.observe(x,action,target,nxt,train=False)
            c.observe(x,action,target,nxt,train=False)

    def test_recency_without_signature_and_erasure_have_real_ablation(self):
        models={k:NativeCausalRecall8(k) for k in
                ("causal","no_cue","erase","sham_key")}
        for law in (3,5):
            for trial in range(4):
                for m in models.values():
                    m.reset_episode()
                    drive(m,law,100,trial)
        a=models["causal"]
        b=models["no_cue"]
        a.reset_episode();b.reset_episode()
        x=DiagnosticWorld(3,100,1)
        for action in ACTIONS[:4]:
            before=x.public()
            nxt,target=x.step(action)
            a.observe(before,action,target,nxt,train=False)
            b.observe(before,action,target,nxt,train=False)
        self.assertNotEqual(a.predict(x.public(),3),
                            b.predict(x.public(),3))
        models["erase"].reset_episode()
        self.assertEqual(models["erase"].banks,[None]*16)
        self.assertEqual({m.accounting()["learned_uint8_counter_capacity_bytes"]
                          for m in models.values()},{256})

    def test_cold_original_law_stored_while_eight_other_laws_are_added(self):
        m=NativeCausalRecall8()
        for law in (3,5,7,11,13,17,19,23,43,47,71,73,79,83,89,97):
            m.reset_episode()
            drive(m,law,100,0,train=True)
        self.assertEqual(sum(x is not None for x in m.banks),16)
        first=tuple(m.banks[0]["key"])
        m.reset_episode()
        world=DiagnosticWorld(3,101,0)
        for action in ACTIONS[:3]:
            x=world.public();y,t=world.step(action)
            m.observe(x,action,t,y,train=False)
        self.assertEqual(m.cue(),first)
        self.assertIsNotNone(m._find(first))

    def test_invalid_action_or_false_outcome_is_atomic(self):
        m=NativeCausalRecall8()
        world=DiagnosticWorld(3,100,0)
        before=world.public()
        snap=m.snapshot()
        for action,target,nxt,training in (
            (1,(0,)*8,before,True),
            (3,(0,)*8,(1,)*8,True),
            (3,(0,)*8,before,1),
            (3,(0,)*8,before,"yes"),
        ):
            with self.assertRaises(ValueError):
                m.observe(before,action,target,nxt,train=training)
            self.assertEqual(m.snapshot(),snap)

    def test_ambiguous_public_rotation_does_not_create_profile(self):
        m=NativeCausalRecall8()
        old=(0,)*8
        self.assertIsNone(observed_rotation(old,old))
        m.observe(old,3,old,old)
        self.assertIsNone(m.rotation)
        self.assertEqual(m.ambiguous,1)

    def test_bounded_counter_saturation(self):
        v=[255,15]
        update_count(v,1)
        self.assertEqual(v,[128,7])

    def test_invalid_native_snapshot_fail_closed(self):
        m=NativeCausalRecall8()
        m.reset_episode()
        drive(m,3,100,0)
        original=m.snapshot()
        for mutation in (
            lambda d:d.update(schema="wrong"),
            lambda d:d.update(step=6),
            lambda d:d.update(clock=True),
            lambda d:d.update(rotation=4),
            lambda d:d["banks"][0]["key"].__setitem__(0,4),
            lambda d:d["banks"][0]["counts"][0].__setitem__(0,256),
            lambda d:d["banks"][0]["counts"][0].__setitem__(1,True),
        ):
            d=json.loads(original)
            mutation(d)
            with self.assertRaises(ValueError):
                NativeCausalRecall8.restore(canonical(d))

    def test_recurrent45_fits_public_consequences_and_cold_restores(self):
        m=Recurrent45()
        before=m.snapshot()
        m.reset_episode()
        drive(m,3,100,0)
        self.assertEqual(m.train_steps,5)
        self.assertNotEqual(before,m.snapshot())
        restored=Recurrent45.restore(m.snapshot())
        self.assertEqual(restored.snapshot(),m.snapshot())
        self.assertEqual(restored.accounting()["learned_float_coefficients"],45)
        old=(canonical(restored.local),canonical(restored.shared))
        restored.reset_episode()
        drive(restored,3,100,0,train=False)
        self.assertEqual(old,
                         (canonical(restored.local),canonical(restored.shared)))

    def test_raw_count_and_residual_count_independent_cold_restore(self):
        for mode in ("raw","residual"):
            m=SignatureCount8(mode)
            m.reset_episode()
            drive(m,3,100,0)
            snap=m.snapshot()
            self.assertEqual(SignatureCount8.restore(snap).snapshot(),snap)

    def test_exhausted_native_actor_returns_controlled_failure(self):
        m=NativeCausalRecall8()
        drive(m,3,100,0)
        with self.assertRaises(ValueError):
            m.predict((0,)*8,3)

    def test_brier_protects_shape_and_finiteness(self):
        self.assertEqual(brier([.5]*8,(1,)*8),.25)
        with self.assertRaises(ValueError):
            brier([float("nan")]*8,(1,)*8)
        with self.assertRaises(ValueError):
            brier([.5]*7,(1,)*8)


if __name__=="__main__":
    unittest.main()
