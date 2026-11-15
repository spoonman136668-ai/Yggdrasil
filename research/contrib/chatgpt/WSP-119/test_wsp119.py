"""WSP-119 source-safe microfeedback engineering tests; no protected source."""
from __future__ import annotations

import json
from pathlib import Path
import random
import sys
import unittest

import microfeedback as F


class MicrofeedbackFixture(unittest.TestCase):
    def test_fresh_public_cohorts_and_no_historical_source(self):
        self.assertEqual(len(F.PUBLIC_SEEDS),24)
        self.assertEqual(len(F.RESERVED_SCIENCE),64)
        self.assertFalse(set(F.PUBLIC_SEEDS)&set(F.RESERVED_SCIENCE))
        for invalid in (118000,119024,119800,119863,True,0.0):
            with self.subTest(seed=invalid),self.assertRaises(PermissionError):
                F.source_safe_world(invalid)
        a=F.source_safe_world(119000)
        self.assertEqual(a,F.source_safe_world(119000))
        self.assertEqual(len(a.targets),4)
        self.assertEqual(len(F.inquiry_pool(a)),40)
        self.assertEqual(len(F.held_subjects(a)),24)
        self.assertTrue(set(F.inquiry_pool(a)).isdisjoint(F.held_subjects(a)))
        self.assertEqual(F.TIERS,(64,128,192,256))
        self.assertEqual(F.EXPOSURES,(0,1,2,3,4,6,8,12))

    def test_real_source_reveals_only_requested_legal_outcome(self):
        w=F.source_safe_world(119000)
        env=F.EvidenceSource(w,w.targets[0])
        held=F.held_subjects(w)[0]
        with self.assertRaises(PermissionError):
            env.query(held)
        chosen=F.inquiry_pool(w)[0]
        first=env.query(chosen)
        self.assertEqual(first,w.actual(chosen,w.targets[0]))
        self.assertEqual(env.count,1)
        with self.assertRaises(PermissionError):
            env.query(chosen)
        with self.assertRaises(PermissionError):
            env.query(64)
        self.assertEqual(env.count,1)

    def test_internal_numeric_microfeedback_updates_only_after_observation(self):
        w=F.source_safe_world(119001)
        graph=w.public_graph(256)
        loop=F.NumericFeedback(graph,active=True)
        source=F.EvidenceSource(w,w.targets[1])
        pool=F.inquiry_pool(w)
        initial=loop.snapshot()
        subject=loop.choose(pool)
        self.assertEqual(loop.snapshot(),initial)
        self.assertIn(subject,pool)
        feedback=loop.observe(subject,source.query(subject))
        self.assertGreaterEqual(feedback,0)
        self.assertNotEqual(loop.snapshot(),initial)
        self.assertEqual(loop.count,1)
        self.assertLess(len(loop.candidates()),216)
        with self.assertRaises(ValueError):
            loop.observe(subject,0)
        self.assertNotIn(loop.choose(pool),loop.seen)

    def test_symbolic_has_identical_legal_actions_under_same_evidence(self):
        w=F.source_safe_world(119002)
        graph=w.public_graph(192)
        pool=F.inquiry_pool(w)
        a=F.NumericFeedback(graph,active=True)
        s=F.IndependentSymbolicFeedback(graph)
        env_a=F.EvidenceSource(w,w.targets[0])
        env_s=F.EvidenceSource(w,w.targets[0])
        for t in range(8):
            self.assertEqual(a.candidates(),s.candidates())
            self.assertEqual(a.law(),s.law())
            x=a.choose(pool)
            self.assertEqual(x,s.choose(pool))
            ya=env_a.query(x)
            ys=env_s.query(x)
            self.assertEqual(ya,ys)
            a.observe(x,ya)
            s.observe(x,ys)
            self.assertEqual([a.infer(v) for v in F.held_subjects(w)],
                             [s.infer(v) for v in F.held_subjects(w)])
        self.assertEqual(env_a.count,8)
        self.assertEqual(env_a.receipt.digest(),env_s.receipt.digest())

    def test_passive_receives_same_number_of_actual_outcomes_not_hidden_labels(self):
        w=F.source_safe_world(119003)
        graph=w.public_graph(256)
        pool=F.inquiry_pool(w)
        passive=F.NumericFeedback(graph,active=False)
        no_update=F.NumericFeedback(graph,active=False,updates=False)
        env_a=F.EvidenceSource(w,w.targets[2])
        env_b=F.EvidenceSource(w,w.targets[2])
        for i in range(12):
            x=passive.choose(pool)
            self.assertEqual(x,no_update.choose(pool))
            passive.observe(x,env_a.query(x))
            no_update.observe(x,env_b.query(x))
        self.assertEqual(env_a.count,12)
        self.assertEqual(env_b.count,12)
        self.assertTrue(any(v for v in passive.w))
        self.assertTrue(all(v==0 for v in no_update.w))
        self.assertIsNone(no_update.law())
        self.assertEqual(env_a.receipt.digest(),env_b.receipt.digest())
        with self.assertRaises(ValueError):
            passive.choose(())

    def test_exact_cold_numerical_restore_and_tamper_rejection(self):
        w=F.source_safe_world(119004)
        graph=w.public_graph(192)
        learner=F.NumericFeedback(graph,active=True)
        env=F.EvidenceSource(w,w.targets[0])
        for t in range(6):
            x=learner.choose(F.inquiry_pool(w))
            learner.observe(x,env.query(x))
        snap=learner.snapshot()
        restored=F.NumericFeedback.restore(graph,snap)
        self.assertEqual(restored.snapshot(),snap)
        self.assertEqual(len(learner.w)*learner.w.itemsize,1728)
        self.assertEqual([learner.infer(s) for s in F.held_subjects(w)],
                         [restored.infer(s) for s in F.held_subjects(w)])
        tampered=bytearray(snap)
        tampered[56]^=1
        with self.assertRaises(ValueError):
            F.NumericFeedback.restore(graph,bytes(tampered))
        with self.assertRaises(ValueError):
            F.NumericFeedback.restore(graph,b"W119")
        self.assertEqual(restored.count,6)

    def test_predeclared_scope_and_no_hidden_oracle_in_chooser(self):
        p=Path(__file__).parent
        spec=json.loads((p/"prereg.json").read_text(encoding="utf-8"))
        self.assertEqual(spec["experiment_id"],"WSP-119")
        self.assertFalse(spec["authority"]["scientific_first_use"])
        self.assertEqual(spec["frozen_axes"]["exposures"] if "frozen_axes" in spec else
                         spec["fresh_source"]["exposures"],F.EXPOSURES)
        self.assertEqual(F.MAX_SOURCE_CALLS,12)
        self.assertEqual(len(F.ARM_NAMES),4)
        import ast
        tree=ast.parse((p/"microfeedback.py").read_text())
        methods={node.name:node for node in ast.walk(tree)
                 if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))}
        for name in ("choose_discriminating_source","_gini_score"):
            body=ast.get_source_segment((p/"microfeedback.py").read_text(),methods[name])
            self.assertNotIn(".actual(",body)
            self.assertNotIn("._law",body)
            self.assertNotIn(".query(",body)


if __name__=="__main__":
    unittest.main()
