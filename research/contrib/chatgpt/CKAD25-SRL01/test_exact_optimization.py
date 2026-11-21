"""SRL01 exact-risk optimization contract: immutable science, source-only math.

Independently reconstructs the *original* fraction-based finite model; every
possible 3-world sequence of two source-witnessed action consequences is tested.
Does not read target outcomes, original world data, native checkpoints or runners.
"""
from fractions import Fraction as F
from itertools import combinations, product
import unittest

from yggdrasil.native_shared_fault_risk import NativeSharedFaultRisk, Q_GRID
from dev_trial import STATIONARY_SEEDS, NEGATIVE_SEEDS, training_history

PUBLIC_MASKS = (0,1,2,3)
Q_REFERENCE = (F(1,4),F(1,2),F(3,4),F(9,10))


def independent_fraction_posterior(masks, source_worlds):
    """Mathematical control; no import of candidate likelihood table."""
    states=[]
    for hot,q in product(masks,Q_REFERENCE):
        weight=F(1,16)
        for witnesses in source_worlds:
            detected=[mask for mask,y in witnesses if y]
            if len(detected)>1:raise ValueError('multiple defect observations')
            if detected:
                likelihood = q if detected[0]==hot else (1-q)/3
            else:
                likelihood = 1 - sum((q if address==hot else (1-q)/3
                                      for address,y in witnesses),F(0))
            weight*=likelihood
        states.append((hot,q,weight))
    evidence=sum((w for _,_,w in states),F(0))
    if evidence<=0:raise ValueError('invalid likelihood')
    posterior=tuple((hot,q,w/evidence) for hot,q,w in states)
    risks=tuple(sum((mass*(q if hot==address else (1-q)/3)
                     for hot,q,mass in posterior),F(0))
                for address in masks)
    actions=tuple(sorted(masks,key=lambda a:(-risks[masks.index(a)],a))[:2])
    return evidence,posterior,risks,actions


def valid_public_worlds(masks):
    return tuple(tuple((a,int(a==fault)) for a in pair)
                 for pair in combinations(masks,2)
                 for fault in (None,*pair))


class ExactOptimizedSourceContracts(unittest.TestCase):
    def test_all_5832_possible_three_world_witness_sequences(self):
        cases=valid_public_worlds(PUBLIC_MASKS)
        self.assertEqual(len(cases),18)
        for worlds in product(cases,repeat=3):
            fitted=NativeSharedFaultRisk(PUBLIC_MASKS,worlds)
            ref=independent_fraction_posterior(PUBLIC_MASKS,worlds)
            self.assertEqual((fitted.evidence,fitted.posterior,fitted.risks,fitted.select()),ref)
            self.assertEqual(fitted.checkpoint_fingerprint(),
                             (fitted.masks,fitted.worlds,fitted.posterior,fitted.risks))
    def test_72_previous_public_history_readouts_only(self):
        cases=[(s,False) for s in STATIONARY_SEEDS]+[(s,True) for s in NEGATIVE_SEEDS]
        self.assertEqual(len(cases),72)
        for seed,negative in cases:
            history=training_history(seed,negative=negative)
            model=NativeSharedFaultRisk(PUBLIC_MASKS,history)
            exact=independent_fraction_posterior(PUBLIC_MASKS,history)
            self.assertEqual((model.evidence,model.posterior,model.risks,model.select()),exact)
    def test_nonsequential_action_id_relabeling(self):
        ids=(0,2,7,15)
        for index,worlds in enumerate(product(valid_public_worlds(ids),repeat=3)):
            if index%11:continue
            fitted=NativeSharedFaultRisk(ids,worlds)
            ref=independent_fraction_posterior(ids,worlds)
            self.assertEqual((fitted.evidence,fitted.posterior,fitted.risks,fitted.select()),ref)
    def test_reject_invalid_public_witnesses(self):
        valid=(((0,0),(1,0)),)*3
        for masks,worlds in [((0,0,2,3),valid),
                             (PUBLIC_MASKS,valid[:2]),
                             (PUBLIC_MASKS,(((0,True),(1,0)),)*3),
                             (PUBLIC_MASKS,(((0,1),(1,1)),)*3),
                             (PUBLIC_MASKS,(((0,0),(0,0)),)*3)]:
            with self.subTest(masks=masks,worlds=worlds):
                with self.assertRaises(ValueError):
                    NativeSharedFaultRisk(masks,worlds)
    def test_source_inputs_unmodified(self):
        worlds=[[[0,0],[1,0]],[[0,1],[3,0]],[[2,0],[3,0]]]
        old=repr(worlds)
        model=NativeSharedFaultRisk(list(reversed(PUBLIC_MASKS)),worlds)
        model.select()
        self.assertEqual(repr(worlds),old)
        self.assertEqual(sum(model.risks,F(0)),F(1))
    def test_source_class_not_changed(self):
        self.assertEqual(Q_GRID,Q_REFERENCE)
        self.assertEqual(len(NativeSharedFaultRisk(PUBLIC_MASKS,(((0,0),(1,0)),)*3).posterior),16)
    def test_fast_actions_equal_fraction_rank_on_all_cases(self):
        for seed,negative in [(STATIONARY_SEEDS[0],False),(NEGATIVE_SEEDS[0],True)]:
            m=NativeSharedFaultRisk(PUBLIC_MASKS,training_history(seed,negative=negative))
            actions=m.select()
            expected=tuple(sorted(PUBLIC_MASKS,key=lambda a:(-m.risk(a),a))[:2])
            self.assertEqual(actions,expected)

if __name__=='__main__':unittest.main(verbosity=2)
