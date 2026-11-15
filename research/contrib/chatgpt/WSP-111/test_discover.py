"""WSP111 fixture-only native class invention tests.

The source consists of the real million ORIGINAL factual observations, which
carry no WSP111 hidden effect labels. All 3000 feedback effect responses in
these tests are fabricated from a completely separate, manually specified
toy relation function. NO import or call to oracle.py is permitted here.
Original 22000 heldout consequences stay unconsumed until qualified CI.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from world import original_facts,source_types_for_group,N_GROUPS,N_SUPPORT
from native import NativeRelationInventor,effect_signature
from controls import IndependentSymbolicInventor,ConventionalInventor
from experiment import adjusted_rand_index,accuracy_metrics


def fake_training_effects():
    support=[]
    mapping=(1,2,4,7)
    for group in range(N_SUPPORT):
        a,b,c=source_types_for_group(group)
        kind=4*a+b-4
        e1=mapping[kind%4]
        e2=(e1+c-10)%4
        support.append((group,e1,e2))
    return tuple(support)


class TestNativeUnlabeledRelationInvention(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source,rels,target=original_facts()
        cls.native=NativeRelationInventor()
        cls.native.program_original(source,rels,target)
        cls.original_digest=cls.native.original_sha256()
        cls.symbolic=IndependentSymbolicInventor()
        cls.symbolic.load_facts(source,rels,target)
        cls.support=fake_training_effects()
        cls.native.program_first_operator(cls.support)
        cls.native.infer_first()
        cls.symbolic.learn_first(cls.support)
        cls.symbolic.infer_first()
        cls.conventional=ConventionalInventor(cls.symbolic)
        cls.conventional.learn_first(cls.support)
        cls.conventional.infer_first()
        cls.native.program_second_operator(cls.support)
        cls.native.infer_second()
        cls.symbolic.learn_second(cls.support)
        cls.symbolic.infer_second()
        cls.conventional.learn_second(cls.support)
        cls.conventional.infer_second()

    def test_exact_million_facts_and_source_weight_fence(self):
        self.assertEqual(len(self.native.original_keys),1_000_000)
        self.assertEqual(len(self.native.original_weights),1_000_000)
        self.assertEqual(len(self.symbolic.facts),1_000_000)
        self.assertEqual(self.native.original_keys.nbytes+self.native.original_weights.nbytes,12_000_000)
        self.assertEqual(self.native.original_sha256(),self.original_digest)
        self.assertTrue(np.all(self.native.original_weights==1.0))
        with self.assertRaises(ValueError):
            self.native.program_original(*original_facts())

    def test_anonymous_first_categories_invented_only_from_observed_consequences(self):
        self.assertEqual(len(self.support),N_SUPPORT)
        self.assertEqual(self.native.first_signatures,(1,2,4,7))
        self.assertEqual(self.native.first_signatures,self.symbolic.first_signatures)
        self.assertEqual(self.native.first_signatures,self.conventional.first_signatures)
        self.assertEqual(self.native.operator1.shape,(16,3))
        self.assertEqual(len(self.native.derived1),N_GROUPS)
        self.assertEqual(len(self.symbolic.derived1),N_GROUPS)
        self.assertEqual(len(self.conventional.derived1),N_GROUPS)
        for g in (0,1,73,2999,3000,10000,24999):
            a,b,c=self.native.chain(g)
            self.assertEqual((a,b,c),source_types_for_group(g))
            rel,sig=self.native.first_relation(g)
            self.assertEqual(sig,(1,2,4,7)[(4*a+b-4)%4])
            self.assertTrue(32<=rel<=35)

    def test_second_class_uses_persisted_new_first_relationship(self):
        self.assertEqual(self.native.operator2.shape,(4,4,2))
        self.assertEqual(self.native.second_signatures,self.symbolic.second_signatures)
        self.assertEqual(self.native.second_signatures,self.conventional.second_signatures)
        self.assertEqual(self.native.second_signatures,(0,1,2,3))
        self.assertEqual(len(self.native.derived2),N_GROUPS)
        for group in (0,1,57,2999,3000,10000,24999):
            n=self.native.predictions(group)
            self.assertEqual(n,self.symbolic.predictions(group))
            self.assertEqual(n,self.conventional.predictions(group))
            _,_,c=self.native.chain(group)
            self.assertEqual(n[1],(n[0]+c-10)%4)

    def test_independent_symbolic_numerical_predicted_partition_parity(self):
        self.assertEqual(
            [(self.native.predictions(g)) for g in (0,1,200,3000,15000,24999)],
            [(self.symbolic.predictions(g)) for g in (0,1,200,3000,15000,24999)])
        self.assertEqual(self.native.original_sha256(),self.original_digest)

    def test_fitted_conventional_stationary_and_identical_information(self):
        self.assertEqual(len(self.conventional.head1),3)
        self.assertEqual(len(self.conventional.head2),2)
        for head in (*self.conventional.head1,*self.conventional.head2):
            self.assertLessEqual(head.gradient_inf,1e-8)
            self.assertLessEqual(head.steps,100)
            self.assertGreater(head.train_accuracy,0.95)

    def test_cold_full_million_weight_and_two_derived_generation_custody(self):
        state=self.native.checkpoint()
        r=NativeRelationInventor.cold_restore(state)
        self.assertEqual(r.original_sha256(),self.original_digest)
        self.assertTrue(np.array_equal(r.operator1,self.native.operator1))
        self.assertTrue(np.array_equal(r.operator2,self.native.operator2))
        self.assertTrue(np.array_equal(r.derived1,self.native.derived1))
        self.assertTrue(np.array_equal(r.derived2,self.native.derived2))
        for g in (0,2,15,3000,12000,24999):
            self.assertEqual(r.predictions(g),self.native.predictions(g))
        tampered={"schema":state["schema"],"maps":state["maps"],
                  "parts":dict(state["parts"]),"sha256":state["sha256"]}
        bits=bytearray(tampered["parts"]["derived2"])
        bits[0]^=1
        tampered["parts"]["derived2"]=bytes(bits)
        with self.assertRaises(ValueError):
            NativeRelationInventor.cold_restore(tampered)

    def test_wrong_pair_binding_degrades_fabricated_effect_task(self):
        correct=[]
        wrong=[]
        for g in range(N_SUPPORT,4000):
            a,b,c=self.native.chain(g)
            kind=4*a+b-4
            correct.append(effect_signature(self.native.operator1[kind]))
            wrong.append(effect_signature(self.native.operator1[(kind+1)%16]))
        self.assertGreater(sum(x==y for x,y in zip(correct,correct)),
                           sum(x==y for x,y in zip(correct,wrong)))

    def test_metrics_and_permutation_invariant_invented_type_scores(self):
        self.assertAlmostEqual(adjusted_rand_index([0,0,1,1],[6,6,4,4]),1.0)
        self.assertLess(adjusted_rand_index([0,0,1,1],[0,1,0,1]),1.0)
        s=accuracy_metrics([1,2,4,7],[1,2,4,7],3)
        self.assertEqual(s["exact_correct"],4)
        self.assertEqual(s["exact_accuracy"],1.0)
        self.assertEqual(len(s["bit_metrics"]),3)

    def test_learners_never_import_original_hidden_effect_oracle(self):
        for name in ("native.py","controls.py"):
            source=(HERE/name).read_text(encoding="utf-8")
            self.assertNotIn("import oracle",source)
            self.assertNotIn("from oracle",source)
            self.assertNotIn("hidden_signature(",source)
            self.assertNotIn("effect_one(",source)
            self.assertNotIn("effect_two(",source)
        self.assertFalse((HERE/"SCIENTIFIC_PASS.json").exists())
        self.assertFalse((HERE/"PROTECTED_FIRST_USE.json").exists())


if __name__=="__main__":
    unittest.main()
