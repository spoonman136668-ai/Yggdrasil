"""ST4 public-only native and equally-budgeted conventional controls.

Hand-authored public transitions, not frozen held DEV or protected first-use.
Test return value before mutation, cold exactness, lag-credit ablation,
contradiction-driven fork, equality of learned counter bytes, and invalid
source outcomes. All actual source trials remain separate CI stage0.
"""
import json
import unittest

from research.nci04_st4.native_credit import (
    NativeCausal8, make_bank, increment, shifted,canonical,rotate_candidates
)
from research.nci04_st4.matched_controls import (
    Recurrent45,LagAwareCount,brier,RECUR_UPDATES
)


def bits(n):
    return tuple((n >> i)&1 for i in range(8))


def after(x,r=1,mask=0):
    return tuple(shifted(x,r,i)^((mask>>i)&1) for i in range(8))


def update(m,x,a,nxt,train=True):
    target=tuple(i^j for i,j in zip(x,nxt))
    return m.observe(x,a,target,nxt,train=train)


def artificial_arm(m,first,mask):
    # Public-only fixture. Both arms have SAME x1 & announced action 3.
    m.reset_episode()
    x0=bits(75)
    x1=after(x0,1)
    assert len(m.predict(x0,first))==8
    update(m,x0,first,x1)
    x2=after(x1,1,mask if first==2 else 0)
    pred=m.predict(x1,3)
    update(m,x1,3,x2)
    return pred


class ST4NativeDevelopmentFixtures(unittest.TestCase):
    def test_public_shift_inference_is_observed_not_private_source(self):
        x=bits(75)
        y=after(x,1)
        found=rotate_candidates(x,y)
        self.assertIn(1,found)
        self.assertEqual(rotate_candidates(x,after(x,2))[0],2)

    def test_episodic_hypothesis_persists_but_not_observation_state(self):
        m=NativeCausal8()
        initial=m.snapshot()
        x=bits(75)
        y=after(x)
        self.assertEqual(m.predict(x,2),[.5]*8)
        self.assertEqual(m.snapshot(),initial)
        p=update(m,x,2,y)
        self.assertEqual(p,[.5]*8)
        self.assertEqual(m.clock,1)
        self.assertEqual(m.rotation,1)
        self.assertIsNotNone(m.active)
        memory=m.banks[m.active]
        m.reset_episode()
        self.assertIsNone(m.rotation)
        self.assertIsNone(m.prior)
        self.assertIs(memory,m.banks[m.active])
        self.assertEqual(m.accounting()["learned_uint8_counter_bytes"],3456)
        self.assertEqual(m.accounting()["extra_neural_coefficients"],0)

    def test_delayed_intervention_has_distinct_learned_public_predictions(self):
        m=NativeCausal8()
        for t in range(28):
            artificial_arm(m,2,170)
            artificial_arm(m,3,0)
        a=artificial_arm(m,2,170)
        b=artificial_arm(m,3,0)
        self.assertNotEqual(a,b)
        x1=after(bits(75),1)
        treatment_after=after(x1,1,170)
        actual_treatment_change=tuple(u^v for u,v in zip(x1,treatment_after))
        self.assertLess(
            brier(a,actual_treatment_change),
            brier(b,actual_treatment_change)
        )
        self.assertGreater(m.updates,0)

    def test_delay_credit_ablation_and_fixed_sham_do_not_gain_free_memory(self):
        models={k:NativeCausal8(k) for k in
                ("causal","no_delay","sham","erase","label_shuffle")}
        for _ in range(5):
            for first in (2,3):
                for m in models.values():
                    artificial_arm(m,first,170)
        caps={m.accounting()["learned_uint8_counter_bytes"]
              for m in models.values()}
        self.assertEqual(caps,{3456})
        for m in models.values():
            self.assertFalse(m.accounting()["privileged_source_access"])
        models["erase"].reset_episode()
        self.assertEqual(models["erase"].banks,[None]*9)

    def test_cold_checkpoint_roundtrip_and_byte_exact_continuation(self):
        m=NativeCausal8()
        for _ in range(3):
            artificial_arm(m,2,91)
        m.reset_episode()
        x=bits(75)
        x1=after(x)
        update(m,x,2,x1)
        frozen=m.snapshot()
        restored=NativeCausal8.restore(frozen)
        self.assertEqual(restored.snapshot(),frozen)
        next_public=after(x1,1,91)
        self.assertEqual(update(m,x1,3,next_public),
                         update(restored,x1,3,next_public))
        self.assertEqual(m.snapshot(),restored.snapshot())

    def test_observation_only_recall_does_not_fit_evidence(self):
        m=NativeCausal8()
        for _ in range(8):
            artificial_arm(m,2,91)
        m.reset_episode()
        public=bits(75)
        nxt=after(public)
        old_banks=canonical(m.banks)
        prev_updates=m.updates
        update(m,public,2,nxt,train=False)
        self.assertEqual(m.updates,prev_updates)
        self.assertEqual(canonical(m.banks),old_banks)
        self.assertEqual(m.rotation,1)

    def test_violations_fail_before_any_mutation(self):
        m=NativeCausal8()
        x=bits(75)
        before=m.snapshot()
        for action,target,nxt,mode in (
            (4,bits(0),x,True),
            (0,bits(0),after(x),True),
            (0,bits(0),x,1),
            (0,bits(0),x,"train"),
        ):
            with self.assertRaises(ValueError):
                m.observe(x,action,target,nxt,train=mode)
            self.assertEqual(before,m.snapshot())

    def test_corrupt_cold_checkpoint_rejected(self):
        m=NativeCausal8()
        artificial_arm(m,2,91)
        initial=m.snapshot()
        for fn in (
            lambda d:d.update(schema="other"),
            lambda d:d.update(active=12),
            lambda d:d.update(clock=True),
            lambda d:d.update(rotation=4),
            lambda d:d["banks"][0]["counts"][0][0][0][0].__setitem__(0,256),
            lambda d:d["banks"][0]["counts"][0][0][0][0].__setitem__(0,True),
        ):
            d=json.loads(initial)
            fn(d)
            with self.assertRaises(ValueError):
                NativeCausal8.restore(canonical(d))

    def test_uint8_saturation_is_bounded(self):
        a=[255,7]
        increment(a,1)
        self.assertEqual(a,[128,3])

    def test_recurrent_is_trained_and_observation_freeze_preserves_weights(self):
        m=Recurrent45()
        x=bits(75);nxt=after(x)
        old=m.snapshot()
        p=m.predict(x,2)
        self.assertEqual(p,[.5]*8)
        observed=update(m,x,2,nxt)
        self.assertEqual(len(observed),8)
        self.assertEqual(m.train_steps,1)
        self.assertNotEqual(old,m.snapshot())
        self.assertEqual(m.accounting()["trained_coefficients"],45)
        self.assertEqual(m.accounting()["optimizer_steps_per_training_action"],
                         RECUR_UPDATES)
        restored=Recurrent45.restore(m.snapshot())
        self.assertEqual(restored.snapshot(),m.snapshot())
        restored.reset_episode()
        fixed=(restored.local[:],restored.shared[:])
        target=after(x)
        update(restored,x,2,target,train=False)
        self.assertEqual(fixed,(restored.local,restored.shared))

    def test_count_matches_native_evidence_budget_and_cold_restore(self):
        m=LagAwareCount()
        n=NativeCausal8()
        self.assertEqual(m.accounting()["learned_uint8_counter_bytes"],
                         n.accounting()["learned_uint8_counter_bytes"])
        artificial_arm(m,2,91)
        snap=m.snapshot()
        self.assertEqual(LagAwareCount.restore(snap).snapshot(),snap)

    def test_all_matched_interfaces_receive_same_public_outcome(self):
        models=[NativeCausal8(),LagAwareCount(),Recurrent45()]
        x=bits(75);x1=after(x)
        for m in models:
            m.reset_episode()
            before=m.predict(x,2)
            returned=update(m,x,2,x1)
            self.assertEqual(before,returned)
            self.assertEqual(len(m.predict(x1,3)),8)

    def test_brier_negative_finite_and_shape(self):
        self.assertAlmostEqual(brier([.5]*8,bits(255)),.25)
        with self.assertRaises(ValueError):
            brier([float("nan")]*8,bits(255))
        with self.assertRaises(ValueError):
            brier([.2]*7,bits(255))


if __name__=="__main__":
    unittest.main()
