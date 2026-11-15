"""Source-free hand-authored ST3 native causal substrate and controls tests.

These use synthetic public byte-shaped stimuli, NOT frozen held law IDs.
They do not call the original source generator, consume scientific data,
change any protected owner runner or claim beneficial learning.
"""
import json
import unittest

from research.nci04_st3.native_credit import (
    NativeInterventionCredit8, row_mode, residual, blank_profile,
    update_profile, predict_profile, match_cost, canonical
)
from research.nci04_st3.matched_controls import (
    ConventionalRecurrent45, ActionCount8, brier
)


def public(seed):
    return tuple((seed >> i) & 1 for i in range(8))


def event(model, raw, action, target_byte, learn=True):
    target=public(target_byte)
    after=tuple(a^b for a,b in zip(raw,target))
    return model.observe(raw,action,target,after,learn=learn)


class NativeCausalSourceFree(unittest.TestCase):
    def test_explicit_intervention_credit_and_no_delay_ablation(self):
        self.assertEqual(row_mode(3,2,"causal",update=False),7)
        self.assertEqual(row_mode(3,2,"no_delay",update=False),3)
        self.assertEqual(row_mode(3,2,"sham",update=False),7)
        self.assertEqual(row_mode(3,2,"sham",update=True),3)
        self.assertEqual(row_mode(3,1,"sham",update=True),7)
        self.assertEqual(residual(public(0),public(1),0,1),1)

    def test_evidence_is_written_only_after_a_public_consequence(self):
        m=NativeInterventionCredit8()
        x=public(12)
        snap=m.snapshot()
        self.assertEqual(m.predict(x,0),[0.5]*8)
        self.assertEqual(snap,m.snapshot())
        event(m,x,0,42)
        self.assertEqual(m.updates,1)
        self.assertEqual(m.clock,1)
        self.assertIsNone(m.active)
        self.assertEqual(len(m.preamble),1)

    def test_four_public_actions_activate_integer_causal_register(self):
        m=NativeInterventionCredit8()
        x=public(37)
        for action in range(4):
            event(m,x,action,42)
        self.assertIsNotNone(m.active)
        state=m.profiles[m.active]
        self.assertEqual(state["observations"],4)
        self.assertEqual(state["last_used"],4)
        self.assertEqual(state["evidence"][0][0][0][0]+
                         state["evidence"][0][0][0][1],1)
        self.assertEqual(m.accounting()["native_cells"],8)
        self.assertEqual(
            m.accounting()["binary_residual_uint8_counter_capacity_bytes"],
            9*3*8*8*2
        )
        self.assertEqual(m.accounting()["extra_neural_weights"],0)

    def test_public_temporal_same_action_yields_different_predictions(self):
        m=NativeInterventionCredit8()
        x=public(0)
        # Contrasting events are both truthful public changes; no hidden ID.
        for t in range(40):
            event(m,x,(2,3,2,3)[t%4],255 if t%4==1 else 0)
        self.assertIsNotNone(m.active)
        m.prior_action=2
        a=m.predict(x,3)
        m.prior_action=1
        b=m.predict(x,3)
        self.assertNotEqual(a,b)

    def test_candidate_and_sham_credit_differ_on_same_observations(self):
        a=NativeInterventionCredit8("causal")
        b=NativeInterventionCredit8("sham")
        x=public(0)
        for t in range(44):
            action=(0,2,3,1)[t%4]
            target=255 if t%4==2 else 0
            event(a,x,action,target)
            event(b,x,action,target)
        self.assertEqual(a.updates,b.updates)
        self.assertNotEqual(a.snapshot(),b.snapshot())
        self.assertEqual(a.accounting()["binary_residual_uint8_counter_capacity_bytes"],
                         b.accounting()["binary_residual_uint8_counter_capacity_bytes"])

    def test_snapshot_canonical_and_true_cold_continuation(self):
        m=NativeInterventionCredit8()
        x=public(131)
        for t in range(11):
            event(m,x,t%4,(5*t)%256)
        snap=m.snapshot()
        other=NativeInterventionCredit8.restore(snap)
        self.assertEqual(other.snapshot(),snap)
        for t in range(11,25):
            self.assertEqual(event(m,x,t%4,(5*t)%256),
                             event(other,x,t%4,(5*t)%256))
            self.assertEqual(m.snapshot(),other.snapshot())
        self.assertIsNotNone(m.active)
        m.reset_episode()
        self.assertIsNone(m.active)
        self.assertIsNone(m.prior_action)
        self.assertGreater(sum(p is not None for p in m.profiles),0)

    def test_episode_erasure_is_actual_negative_control(self):
        m=NativeInterventionCredit8("episode_erase")
        x=public(11)
        for i in range(5):
            event(m,x,i%4,1)
        self.assertGreater(sum(p is not None for p in m.profiles),0)
        m.reset_episode()
        self.assertEqual(m.profiles,[None]*9)

    def test_fail_closed_no_target_leakage_or_training_mutation(self):
        m=NativeInterventionCredit8()
        raw=public(0)
        before=m.snapshot()
        with self.assertRaises(ValueError):
            m.observe(raw,0,public(0),public(1),learn=True)
        with self.assertRaises(ValueError):
            m.observe(raw,4,public(0),public(0),learn=True)
        with self.assertRaises(ValueError):
            m.observe(raw,0,public(0),public(0),learn=1)
        self.assertEqual(before,m.snapshot())
        event(m,raw,2,0,learn=False)
        self.assertEqual(m.updates,0)
        self.assertEqual(m.clock,0)
        self.assertEqual(m.episode_steps,1)

    def test_counter_saturation_bounded_and_invalid_cold_state_rejected(self):
        p=blank_profile()
        p["evidence"][0][0][0]=[255,8]
        update_profile(p,public(0),0,None,public(1),"causal",1)
        self.assertEqual(p["evidence"][0][0][0],[128,4])
        m=NativeInterventionCredit8()
        for action in range(4):
            event(m,public(0),action,42)
        snap=m.snapshot()
        for mutate in (
            lambda d:d.update(schema="wrong"),
            lambda d:d["profiles"][0]["evidence"][0][0][0].__setitem__(0,256),
            lambda d:d["profiles"][0]["evidence"][0][0][0].__setitem__(1,True),
            lambda d:d["profiles"][0]["contradictions"].__setitem__(0,-1),
            lambda d:d.update(active=8),
            lambda d:d.update(prior_action=5),
            lambda d:d.update(clock=-1),
        ):
            d=json.loads(snap)
            mutate(d)
            with self.assertRaises(ValueError):
                NativeInterventionCredit8.restore(canonical(d))

    def test_trained_recurrent_updates_only_from_real_public_labels(self):
        r=ConventionalRecurrent45()
        x=public(11)
        frozen=r.weights_snapshot()
        self.assertEqual(len(r.predict(x,0)),8)
        event(r,x,0,255) if False else None
        target=public(255)
        nxt=tuple(a^b for a,b in zip(x,target))
        pred=r.observe(x,0,target,nxt,train=True)
        self.assertEqual(len(pred),8)
        self.assertNotEqual(frozen,r.weights_snapshot())
        stored=r.snapshot()
        restored=ConventionalRecurrent45.restore(stored)
        self.assertEqual(restored.snapshot(),stored)
        frozen=restored.weights_snapshot()
        restored.observe(x,0,target,nxt,train=False)
        self.assertEqual(restored.weights_snapshot(),frozen)
        self.assertEqual(restored.accounting()["trained_coefficients"],45)

    def test_action_count_has_real_bounded_learned_history(self):
        x=public(0)
        m=ActionCount8()
        for i in range(16):
            event(m,x,i%4,255)
        self.assertEqual(m.updates,16)
        self.assertGreater(sum(b is not None for b in m.banks),0)
        restored=ActionCount8.restore(m.snapshot())
        self.assertEqual(restored.snapshot(),m.snapshot())
        self.assertEqual(restored.accounting()["nine_profile_uint8_evidence_bytes"],
                         9*8*4*2)
        self.assertFalse(restored.accounting()["allocated_information_capacity_equal"])

    def test_preaction_brier_and_invalid_forecast_negative(self):
        self.assertAlmostEqual(brier([.5]*8,public(255)),.25)
        with self.assertRaises(ValueError):
            brier([float("nan")]*8,public(255))
        with self.assertRaises(ValueError):
            brier([.5]*7,public(255))


if __name__=="__main__":
    unittest.main()
