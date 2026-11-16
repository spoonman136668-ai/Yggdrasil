"""WSP-121 allowed engineering-only assertions. No primary first-use."""
from __future__ import annotations
from unittest import TestCase
import json
from hashlib import sha256

import meta_operator as M


class SourceSafeOperatorTests(TestCase):
    def test_direct_numeric_programming_and_optimized_symbolic_parity(self):
        report = M.engineering_fixture()
        self.assertEqual(report['schema'], 'wsp121.source-safe-fixture.v1')
        self.assertFalse(report['scientific'])
        self.assertFalse(report['source_first_use'])
        self.assertTrue(report['strong_symbolic_identical'])
        self.assertTrue(report['cold_ok'])
        self.assertEqual(report['numeric_learned_bytes'], 64)
        self.assertEqual(report['retained_contexts'], 8)
        self.assertEqual([a['budget'] for a in report['worlds']], [8, 8, 4, 4])
        for row in report['worlds']:
            self.assertEqual(len({x['source_sha256'] for x in row['arms'].values()}), 1)
            for record in row['arms'].values():
                self.assertEqual(record['source_calls'], row['budget'])
                self.assertEqual(sum(record[k] for k in
                    ('correct','wrong_confident','abstained')), 24)
        self.assertEqual(report['worlds'][-1]['arms']['NO_UPDATE']['correct'], 0)

    def test_primary_protected_and_replay_denied(self):
        for seed in (121000,121047,121800,121863,120800,120863,120019,122001,True):
            with self.subTest(seed=seed), self.assertRaises(PermissionError):
                M.engineering_world(seed)
            with self.subTest(primary=seed), self.assertRaises(PermissionError):
                M.original_world(seed)
            with self.subTest(hidden_generator=seed), self.assertRaises(PermissionError):
                M._public_world(seed,0)
        w = M.engineering_world(121900)
        self.assertEqual(set(w.legal) & set(w.held), set())
        self.assertEqual((len(w.legal),len(w.held)),(40,24))
        source = M.EvidenceSource(w,budget=4)
        for s in w.held:
            with self.assertRaises(PermissionError):
                source.query(s)
        self.assertEqual(source.count,0)
        first=w.legal[0]
        source.query(first)
        with self.assertRaises(PermissionError):
            source.query(first)
        for s in w.legal[1:4]:
            source.query(s)
        with self.assertRaises(PermissionError):
            source.query(w.legal[4])

    def test_cold_tamper_and_valid_digest_counter_forgery_denied(self):
        w=M.engineering_world(121900)
        n=M.NumericFastWeights()
        source=M.EvidenceSource(w,budget=4)
        for s in w.legal[:4]:
            n.observe(w,s,source.query(s))
        state=n.snapshot()
        self.assertEqual(M.NumericFastWeights.restore(state).snapshot(),state)
        changed=json.loads(state)
        changed['payload']['weights'][0]+=1
        with self.assertRaisesRegex(ValueError,'WSP121_COLD_DIGEST_INVALID'):
            M.NumericFastWeights.restore(json.dumps(changed))
        forged=json.loads(state)
        forged['payload']['weights'][0]+=1
        canonical=json.dumps(forged['payload'],sort_keys=True,separators=(',',':'))
        forged['sha256']=sha256(canonical.encode()).hexdigest()
        with self.assertRaisesRegex(ValueError,'WSP121_COLD_COUNTER_PROVENANCE'):
            M.NumericFastWeights.restore(json.dumps(forged))

    def test_unobserved_context_abstention_and_gate_shift_detection(self):
        w=M.engineering_world(121900)
        n=M.NumericFastWeights()
        sym=M.SymbolicMemo()
        en=M.SymbolicEnumerative()
        source=M.EvidenceSource(w,budget=4)
        s=w.legal[0];outcome=source.query(s)
        for model in (n,sym,en): model.observe(w,s,outcome)
        self.assertEqual(n.infer(w,s),sym.infer(w,s))
        seen_context=w.feature(s)
        for held in w.held:
            if w.feature(held)!=seen_context:
                self.assertIsNone(n.infer(w,held))
                self.assertIsNone(sym.infer(w,held))
                self.assertIsNone(en.infer(w,held))
        other=w.routes(s)[1-M._fixture_gate(w.feature(s))]
        for model in (n,sym,en):
            with self.assertRaisesRegex(ValueError,'WSP121_OPERATOR_CONTRADICTION'):
                model.observe(w,s,other)

    def test_graph_transfer_and_independent_strong_controls(self):
        first=M.engineering_world(121900)
        next_world=M.engineering_world(121903)
        self.assertNotEqual(first.graph,next_world.graph)
        numeric=M.NumericFastWeights();symbolic=M.SymbolicMemo()
        source=M.EvidenceSource(first,budget=8)
        for s in first.legal[:8]:
            answer=source.query(s)
            numeric.observe(first,s,answer)
            symbolic.observe(first,s,answer)
        self.assertEqual(source.count,8)
        self.assertEqual(len(numeric.history),8)
        self.assertEqual(sum(numeric.infer_route(c) is not None for c in range(8)),8)
        self.assertEqual([numeric.infer(next_world,s) for s in next_world.held],
                         [symbolic.infer(next_world,s) for s in next_world.held])
        self.assertTrue(all(v is None for v in
           [M.NumericFastWeights().infer(next_world,s) for s in next_world.held]))
