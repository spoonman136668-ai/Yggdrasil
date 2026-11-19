"""CKAD43 fixed source-only engineering fixtures; no reserved seed is run."""
import hashlib
import importlib.util
import sys
import unittest
from pathlib import Path
from yggdrasil.native_context_basis import digest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ckad43_recurrence_fixture",HERE/"campaign.py")
D=importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)


def fixture(t,variant="stable"):
    context=(t*7//3)%2
    first=(t//2)%2
    second=(t//4)%2
    shifted=(variant=="change" or (variant=="return" and 56<=t<90))
    next_state=context^first^int(shifted)
    reward=((context&first)^(next_state&second)) if not shifted else ((context&next_state)|(first&second))
    ident=hashlib.sha256(("ckad43-disjoint-unit|"+str(t)).encode()).hexdigest()
    return ident,((context,(t//5)%2),(context,(t//6)%2)),{
        "s1":context,"x1":first,"s2":next_state,"x2":second,"y":reward}


class CKAD43Unit(unittest.TestCase):
    def test_prereg_and_forbidden_cohorts(self):
        self.assertEqual(D.PREREG,"8f94cffb5e61be109038ba6f3611ee209161ce1c")
        self.assertEqual(D.DEV,(43111,43112))
        self.assertTrue(set(D.DEV).isdisjoint(D.PILOT+D.PRIMARY+D.EXCLUDED))
        for seed in (*D.PILOT,*D.PRIMARY,*D.EXCLUDED):
            with self.assertRaisesRegex(ValueError,"CKAD43_ONLY_REGISTERED_DEV"):
                D.score_seed(seed)

    def test_only_genuine_source_trains_and_no_double_observation(self):
        r=D.PersistentRuleRecall()
        for t in range(32):
            event=fixture(t)
            a_before=r.A.n
            r.observe(*event)
            self.assertEqual(r.n,t+1)
            self.assertEqual(r.A.n,a_before+1)
            self.assertIsNone(r.B)
        last=fixture(31)
        raw=r.checkpoint()
        self.assertIs(r.observe(*last),r)
        self.assertEqual(r.checkpoint(),raw)
        corrupted=dict(last[2]);corrupted["y"]^=1
        with self.assertRaisesRegex(ValueError,"CKAD43_CONFLICTING_SOURCE_ID"):
            r.observe(last[0],last[1],corrupted)
        self.assertEqual(raw,r.checkpoint())

    def test_predicted_stage_does_not_see_future_consequence(self):
        r=D.PersistentRuleRecall()
        for t in range(24):
            r.observe(*fixture(t))
        before=r.checkpoint()
        event=fixture(24)
        p=r.read("recall_two_rules",event[1][0],event[2]["x1"])
        q=r.read("recall_two_rules",event[1][0],event[2]["x1"],
                 event[2]["s2"],event[2]["x2"])
        self.assertTrue(0<p<1 and 0<q<1)
        self.assertEqual(r.checkpoint(),before)
        with self.assertRaises(ValueError):
            r.read("secret",event[1][0],event[2]["x1"])
        r.observe(*event)
        self.assertNotEqual(before,r.checkpoint())

    def test_expert_creation_and_exact_cold_state(self):
        r=D.PersistentRuleRecall()
        for t in range(120):
            mode="stable" if t<56 else "change"
            r.observe(*fixture(t,mode))
        self.assertIsNotNone(r.B)
        self.assertEqual(r.A.n+r.B.n,r.n)
        self.assertEqual(r.n,120)
        self.assertTrue(any(t["kind"]=="contradiction_created_B" for t in r.transitions))
        before=r.checkpoint()
        restored=D.PersistentRuleRecall.restore(before,digest(before))
        self.assertEqual(restored.checkpoint(),before)
        for key in ("recall_two_rules","causal_always_A","causal_never_switch_B"):
            self.assertEqual(r.read(key,(1,0),1),restored.read(key,(1,0),1))
            self.assertEqual(r.read(key,(0,0),0,1,1),restored.read(key,(0,0),0,1,1))
        self.assertEqual(before,r.checkpoint())
        with self.assertRaisesRegex(ValueError,"CKAD43_CHECKPOINT_SHA_MISMATCH"):
            D.PersistentRuleRecall.restore(before,"0"*64)

    def test_counterfactual_phase_labels_cannot_impact_training(self):
        a=D.PersistentRuleRecall();b=D.PersistentRuleRecall()
        for t in range(56):
            event=fixture(t)
            a.observe(*event)
            b.observe(*event)
        self.assertEqual(a.checkpoint(),b.checkpoint())
        self.assertEqual(a.A.checkpoint(),b.A.checkpoint())

    def test_frozen_gates_and_strongest_fitted_baseline(self):
        def item(seed,recall=.11,native=.135,other=.13,late_gain=.03):
            groups={}
            for phase in (*D.PHASES,"pooled_late_shift_and_return"):
                arms={name:.2 for name in D.ARMS}
                arms.update({"recall_two_rules":recall,"original_native":native,
                             "causal_full":other,"causal_discount93":other,
                             "causal_dual":other})
                for name in D.BASELINE:arms[name]=other
                if phase=="late_return_A":
                    arms["recall_two_rules"]=native-late_gain
                groups[phase]={"mean_brier":arms}
            return {"seed":seed,"groups":groups,"worlds":[{
                "cold_exact":True,"read_only":True,"original_source_prefix_exact":True,
                "conflict_atomic":True,"specialist_source_event_parity":True,
                "specialists_created":2}]}
        a,b=[item(s) for s in D.DEV]
        self.assertEqual(D.classify([a,b]),"DEV_FEASIBLE_NOT_SCIENTIFIC")
        self.assertEqual(D.classify([a,item(D.DEV[1],other=.113)]),"DEV_NO_GO")
        self.assertEqual(D.classify([a,item(D.DEV[1],late_gain=.015)]),"DEV_NO_GO")
        self.assertEqual(D.classify([a,item(D.DEV[1],recall=.155)]),"DEV_NO_GO")
        with self.assertRaises(AssertionError):D.classify([b,a])


if __name__=="__main__":
    unittest.main()
