"""Negative and positive controls for frozen competing causal hypotheses."""
from fractions import Fraction
import importlib.util
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ckad26_exact",HERE/"causal_evidence.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def event(i,state=0,action=0,next_state=0,second=0,reward=0):
    return {"public_state":state,"first_action":action,"next_state":next_state,
            "second_action":second,"reward":reward}


class EvidenceTests(unittest.TestCase):
    def test_exact_rational_bayes_degenerate_and_split(self):
        stable=[event(i,next_state=0) for i in range(32)]
        transition=[event(i,next_state=0 if i<16 else 1) for i in range(32)]
        self.assertLess(m.marginal_bayes_factor(stable,("public_state","first_action"),
                                                 "next_state"),1)
        self.assertGreater(m.marginal_bayes_factor(transition,
                           ("public_state","first_action"),"next_state"),16)
        self.assertEqual(m.marginal_bayes_factor(transition,
                         ("public_state","first_action"),"next_state"),
                         m.marginal_bayes_factor(transition,(),"next_state"))

    def test_action_conditioning_avoids_policy_shift_false_alarm(self):
        # Outcome remains S2 == chosen first action; only policy changes
        # from all-action-0 to all-action-1. A marginal change is not causal.
        rows=[event(i,action=0,next_state=0) for i in range(16)]
        rows += [event(i,action=1,next_state=1) for i in range(16,32)]
        causal=m.marginal_bayes_factor(rows,("public_state","first_action"),"next_state")
        marginal=m.marginal_bayes_factor(rows,(),"next_state")
        self.assertEqual(causal,1)  # disjoint action support: neutral, not evidence of stability
        self.assertGreater(marginal,16)

    def test_strong_transition_shift_fires_only_with_causal_public_evidence(self):
        model=m.ChangeEvidence("causal_bayes","unit")
        for i in range(64):
            x=event(i,next_state=int(i>=40))
            model.observe(f"{i:064x}",449+i,x)
        self.assertTrue(model.alarms)
        self.assertTrue(all(z["evidence"]=="transition" for z in model.alarms))
        self.assertTrue(all(z["evidence_count"]>=448+32 for z in model.alarms))

    def test_no_change_null_no_false_alarms(self):
        for arm in ("causal_bayes","unconditional_bayes"):
            observer=m.ChangeEvidence(arm,"null")
            for i in range(192):
                observer.observe(f"{i:064x}",449+i,event(i,next_state=i%2,reward=0))
            self.assertEqual(observer.alarms,[],arm)

    def test_reject_lookahead_hidden_data_and_count_skips(self):
        a=m.ChangeEvidence("causal_bayes","unit")
        with self.assertRaisesRegex(ValueError,"ONLY_PUBLIC"):
            a.observe("a"*64,449,{**event(1),"hidden":1})
        with self.assertRaisesRegex(ValueError,"SEQUENTIAL_COUNT"):
            a.observe("a"*64,450,event(1))
        with self.assertRaisesRegex(ValueError,"EXACT_WINDOW"):
            m.marginal_bayes_factor([event(1)],(),"reward")
        with self.assertRaisesRegex(ValueError,"MODE"):
            m.ChangeEvidence("oracle","unit")

if __name__=="__main__":
    unittest.main()
