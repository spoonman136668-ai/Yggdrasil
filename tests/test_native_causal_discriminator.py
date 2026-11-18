"""CKAD25-X: source-only native causal discriminator focused/negative tests."""
import unittest
from fractions import Fraction
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
from test_native_causal_regime_recall import bank,rows


def independent_gini(native,slots,diagnostics,candidates):
    # Independent test-level implementation of the exact variance contract
    # from already witnessed source rows, not the new proposer code.
    likes={}
    for slot in slots:
        p=Fraction(1,1)
        for c,a,y in diagnostics:
            r=native.causal_relation_probability(slot,c,a)
            m=Fraction(*r)
            p*=m if y else 1-m
        likes[slot]=p
    other=Fraction(1,2)**len(diagnostics)
    total=sum(likes.values())+other
    weights={slot:likes[slot]/total for slot in slots}
    unknown=other/total
    ranked=[]
    for c,a in candidates:
        probs={slot:Fraction(*native.causal_relation_probability(slot,c,a)) for slot in slots}
        mu=sum(weights[slot]*probs[slot] for slot in slots)+unknown*Fraction(1,2)
        value=sum(weights[slot]*(probs[slot]-mu)**2 for slot in slots)+unknown*(Fraction(1,2)-mu)**2
        ranked.append((-value,c,a))
    return list(min(ranked)[1:])


class NativeCausalDiscriminatorTests(unittest.TestCase):
    def test_unlabeled_public_discrimination_matches_independent_fractional_control(self):
        _,m=bank()
        before=m.checkpoint()
        masks=list(range(12))
        diagnostics=[]
        for i in range(4):
            candidates=[[x&7,x>>3] for x in masks if [x&7,x>>3] not in [row[:2] for row in diagnostics]]
            proposal=m.propose_causal_discriminator((1,2),diagnostics,candidates)
            self.assertEqual(proposal,independent_gini(m,(1,2),diagnostics,candidates))
            self.assertIn(proposal,candidates)
            mask=proposal[0]|(proposal[1]<<3)
            expected=rows("A",[mask])[0]
            diagnostics.append(expected)
        self.assertEqual(len(set((r[0],r[1]) for r in diagnostics)),4)
        p,q,chosen=m.recall_causal_regime([1,2],diagnostics,13&7,13>>3)
        self.assertEqual(chosen,1)
        self.assertEqual((p,q),m.causal_relation_probability(1,13&7,13>>3))
        self.assertEqual(m.checkpoint(),before)

    def test_input_only_contract_refuses_spoofed_actions_and_overlap(self):
        _,m=bank()
        diag=rows("A",[0])
        good=[[2,0],[5,0]]
        for slots,seen,possible in (
            ((1,1),diag,good),((1,3),diag,good),
            ((1,2),[diag[0],diag[0]],good),
            ((1,2),diag,[[0,0],[2,0]]),
            ((1,2),diag,[[2,0],[2,0]]),
            ((1,2),diag,[[2,0,True]]),
            ((1,2),diag,[[2,0,1]]),
            ((1,2),diag,[]),
            ((1,2),diag[:1]+[[2,0,True]],good),
            ((1,2),diag[:1]+[[2,0,2]],good),
        ):
            with self.subTest(slots=slots,seen=seen,possible=possible),self.assertRaises(ValueError):
                m.propose_causal_discriminator(slots,seen,possible)

    def test_persistent_native_memory_survives_pressure_and_source_is_readonly(self):
        old,m=bank()
        a=m._compiled[1].checkpoint()
        b=m._compiled[2].checkpoint()
        original=m.checkpoint()
        result=m.propose_causal_discriminator([1,2],[],[[x&7,x>>3] for x in range(12)])
        self.assertEqual(m.checkpoint(),original)
        self.assertEqual((m._compiled[1].checkpoint(),m._compiled[2].checkpoint()),(a,b))
        self.assertEqual(m._properties.checkpoint(),old._properties.checkpoint())
        self.assertIsInstance(result,list)
        cold=NativeCumulativeLearner.restore(m.checkpoint(),digest(m.checkpoint()))
        self.assertEqual(cold.propose_causal_discriminator([1,2],[],[[x&7,x>>3] for x in range(12)]),result)

    def test_invalidation_fail_closed_no_future_observation_access(self):
        _,m=bank()
        addition=rows("A",[12,13,14,15])
        m=m.observe(1,addition,digest(canonical(addition)),source_ref="c"*64)
        self.assertIsNone(m._compiled[1])
        with self.assertRaises(ValueError):
            m.propose_causal_discriminator([1,2],[],[[2,0]])


if __name__=="__main__":unittest.main()
