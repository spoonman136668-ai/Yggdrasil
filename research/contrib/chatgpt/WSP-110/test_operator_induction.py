"""WSP110 fixture-only operator qualification. No heldout answer truth is read.

These tests use generated raw facts and support labels for group 0..2999
only. They may compute unlabelled heldout *predictions* but never score them.
Original external/protected source, heldout hidden_x/hidden_y and WSP101 are
untouched. The real 22000-group evaluation is reserved to final one-shot CI.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from world import (
    N_GROUPS,N_SUPPORT,N_TEST,N_INPUT_FACTS,N_DISTRACTORS,
    original_facts,support_feedback,types_for_group,
)
from native_weights import NativeSparseWeightMemory,encode_one
from controls import SymbolicAssociationControl,ConventionalOperatorControl,L2,TOL
from experiment import _metrics


class TestMillionFactOperatorProgramming(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources,cls.relations,cls.targets=original_facts()
        cls.feedback=support_feedback()
        cls.direct=NativeSparseWeightMemory()
        cls.direct.program_million(cls.sources,cls.relations,cls.targets)
        cls.native_original_digest=cls.direct.original_digest()
        cls.direct.program_operator_weights(cls.feedback)
        cls.symbolic=SymbolicAssociationControl()
        cls.symbolic.load_facts(cls.sources,cls.relations,cls.targets)
        cls.symbolic.observe(cls.feedback)
        cls.conventional=ConventionalOperatorControl(cls.symbolic)
        cls.conventional.learn(cls.feedback)
        cls.direct.infer_first_round()
        cls.direct.infer_second_round()
        cls.symbolic.infer_first()
        cls.symbolic.infer_second()
        cls.conventional.infer_first()
        cls.conventional.infer_second()

    def test_exact_million_original_facts_and_disjoint_entity_sets(self):
        self.assertEqual(len(self.sources),N_INPUT_FACTS)
        self.assertEqual(len(self.direct.keys),N_INPUT_FACTS)
        self.assertEqual(len(self.symbolic.facts),N_INPUT_FACTS)
        self.assertEqual(N_GROUPS,N_SUPPORT+N_TEST)
        self.assertEqual(N_DISTRACTORS,925000)
        self.assertEqual(self.direct.original_storage_bytes(),12000000)
        self.assertTrue(np.all(self.direct.fact_weights==1.0))
        self.assertGreaterEqual(int(self.sources[-1]),100000)
        self.assertLess(int(self.sources[0]),100000)
        self.assertFalse(any(int(r) in (8,9) for r in self.relations))

    def test_first_second_chain_read_from_native_parameter_memory(self):
        for g in (0,1,2,50,2999,3000,17000,24999):
            a,b,c=self.direct.get_chain(g)
            self.assertEqual((a,b,c),types_for_group(g))
            self.assertEqual((a,b,c),self.symbolic.get_chain(g))
        with self.assertRaises(ValueError):
            self.direct.get_chain(25000)
        with self.assertRaises(ValueError):
            self.direct.program_million(self.sources,self.relations,self.targets)

    def test_train_label_budget_and_support_only(self):
        self.assertEqual(len(self.feedback),N_SUPPORT)
        self.assertEqual([g for g,_,_ in self.feedback],list(range(N_SUPPORT)))
        self.assertTrue(all(not y or x for _,x,y in self.feedback))
        self.assertEqual(len(self.direct.stage1_operator),16)
        self.assertEqual(len(self.direct.stage2_operator),4)
        self.assertTrue(np.all((self.direct.stage1_operator>0)&
                               (self.direct.stage1_operator<1)))
        self.assertTrue(np.all((self.direct.stage2_operator>0)&
                               (self.direct.stage2_operator<1)))
        self.assertTrue(np.all(self.direct.support_counts_1[1]>0))
        self.assertTrue(np.all(self.direct.support_counts_2[1]>0))

    def test_two_discovery_rounds_write_new_native_parameter_relations(self):
        self.assertGreater(len(self.direct.derived_x_keys),100)
        self.assertGreater(len(self.direct.derived_y_keys),100)
        self.assertEqual(len(self.direct.derived_x_keys),len(self.symbolic.derived_x))
        self.assertEqual(len(self.direct.derived_y_keys),len(self.symbolic.derived_y))
        for g in (0,1,11,100,2999,3000,17000,24999):
            self.assertEqual(self.direct.predictions(g),self.symbolic.predictions(g))
        self.assertEqual(self.direct.original_digest(),self.native_original_digest)

    def test_conventional_fully_optimized_without_heldout_labels(self):
        self.assertEqual(L2,0.01)
        self.assertEqual(TOL,1e-8)
        self.assertLessEqual(self.conventional.first.gradient_inf,TOL)
        self.assertLessEqual(self.conventional.second.gradient_inf,TOL)
        self.assertLessEqual(self.conventional.first.steps,100)
        self.assertLessEqual(self.conventional.second.steps,100)
        self.assertGreater(self.conventional.first.train_accuracy,0.90)
        self.assertGreater(self.conventional.second.train_accuracy,0.90)
        for g in (0,1,11,100,3000,17000,24999):
            self.assertEqual(len(self.conventional.predictions(g)),2)

    def test_cold_restore_after_both_induced_operator_rounds(self):
        snapshot=self.direct.checkpoint()
        restored=NativeSparseWeightMemory.cold_restore(snapshot)
        self.assertEqual(restored.original_digest(),self.native_original_digest)
        self.assertTrue(np.array_equal(self.direct.keys,restored.keys))
        self.assertTrue(np.array_equal(self.direct.fact_weights,restored.fact_weights))
        self.assertTrue(np.array_equal(self.direct.stage1_operator,restored.stage1_operator))
        self.assertTrue(np.array_equal(self.direct.stage2_operator,restored.stage2_operator))
        for g in (0,1,11,100,2999,3000,17000,24999):
            self.assertEqual(restored.predictions(g),self.direct.predictions(g))
        altered={"schema":snapshot["schema"],"sha256":snapshot["sha256"],
                 "parts":dict(snapshot["parts"])}
        blob=bytearray(altered["parts"]["derived_x"])
        blob[0]^=7
        altered["parts"]["derived_x"]=bytes(blob)
        with self.assertRaises(ValueError):
            NativeSparseWeightMemory.cold_restore(altered)

    def test_zero_operator_baseline_is_not_positive_discovery(self):
        p=[False for _ in range(12)]
        y=[True]*6+[False]*6
        score=_metrics(p,y)
        self.assertEqual(score["tp"],0)
        self.assertEqual(score["recall"],0)
        self.assertEqual(score["accuracy"],0.5)

    def test_models_do_not_import_heldout_truth(self):
        for path in ("native_weights.py","controls.py"):
            source=(HERE/path).read_text(encoding="utf-8")
            self.assertNotIn("from world import hidden_x",source)
            self.assertNotIn("from world import hidden_y",source)
            self.assertNotIn("hidden_x(",source)
            self.assertNotIn("hidden_y(",source)
        self.assertFalse((HERE/"SCIENTIFIC_PASS.json").exists())
        self.assertFalse((HERE/"PROTECTED_FIRST_USE.json").exists())


if __name__=="__main__":
    unittest.main()
