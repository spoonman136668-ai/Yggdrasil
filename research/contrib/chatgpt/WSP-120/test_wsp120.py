"""WSP-120 engineering tests only: disjoint 120900 fixture, NO primary cohort."""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import unittest

import structural_growth as S


class StructuralGrowthEngineering(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.w = S.engineering_fixture_world()
        cls.graph = cls.w.public_graph(384)

    def test_guarded_cohorts_and_source_custody(self):
        self.assertEqual(len(S.PUBLIC_SEEDS), 24)
        self.assertTrue(set(S.PUBLIC_SEEDS).isdisjoint(S.RESERVED_SEEDS))
        self.assertNotIn(S.ENGINEERING_SEED, S.PUBLIC_SEEDS)
        for seed in (120900, 119000, 120024, 120800, 120863, True, 120000.0):
            with self.subTest(seed=seed), self.assertRaises(PermissionError):
                S.source_safe_world(seed)
        self.assertEqual(len(S.inquiry_pool(self.w)), 40)
        self.assertEqual(len(S.held_subjects(self.w)), 24)
        self.assertTrue(set(S.inquiry_pool(self.w)).isdisjoint(S.held_subjects(self.w)))
        self.assertEqual(sum(map(len, self.graph)), 384)

    def test_new_relations_not_old_three_hop_functions(self):
        self.assertEqual([len(law[1]) if law[0] == "c" else 2
                          for law in self.w.targets], [4, 5, 2])
        older = {tuple(S.walk(self.graph, s, p) for s in range(S.N))
                 for p in S._chain_programs((1, 2, 3))}
        new = [tuple(S.walk(self.graph, s, law) for s in range(S.N))
               for law in self.w.targets]
        self.assertTrue(all(x not in older for x in new))
        self.assertEqual(len(set(new)), 3)
        self.assertLessEqual(len(S.GRAMMAR), S.MAX_PROGRAMS)
        self.assertLessEqual(len(S.GRAMMAR)*8, S.MAX_NUMERIC_BYTES)

    def test_guarded_external_feedback_and_replay_rejection(self):
        source = S.EvidenceSource(self.w, self.w.targets[0])
        subject = S.inquiry_pool(self.w)[0]
        actual = source.query(subject)
        self.assertEqual(actual, S.walk(self.graph, subject, self.w.targets[0]))
        self.assertEqual(source.count, 1)
        for s in (subject, S.held_subjects(self.w)[0], -1, 64):
            with self.subTest(s=s), self.assertRaises(PermissionError):
                source.query(s)
        self.assertEqual(source.count, 1)

    def test_numeric_growth_and_checkpoint(self):
        source = S.EvidenceSource(self.w, self.w.targets[1])
        m = S.NumericGrow(self.graph, active=False)
        no_growth = S.NumericGrow(self.graph, active=False, grow=False)
        no_update = S.NumericGrow(self.graph, active=False, updates=False)
        for _ in range(8):
            subject = m.choose(S.inquiry_pool(self.w))
            truth = source.query(subject)
            for learner in (m, no_growth, no_update):
                learner.observe(subject, truth)
        self.assertEqual(len(m.observed), 8)
        self.assertTrue(m.grown, "new five-hop law must exhaust old three-hop rules")
        self.assertFalse(no_growth.grown)
        self.assertFalse(no_update.grown)
        self.assertTrue(all(v == 0 for v in no_update.weights))
        self.assertLessEqual(len(m.weights)*4, S.MAX_NUMERIC_BYTES)
        snap = m.snapshot()
        restored = S.NumericGrow.restore(self.graph, snap)
        self.assertEqual(snap, restored.snapshot())
        self.assertEqual(restored.seen, m.seen)
        self.assertEqual([restored.infer(s) for s in S.held_subjects(self.w)],
                         [m.infer(s) for s in S.held_subjects(self.w)])
        bad = bytearray(snap)
        bad[20] ^= 1
        with self.assertRaises(ValueError):
            S.NumericGrow.restore(self.graph, bytes(bad))
        data = json.loads(snap.rpartition(b"\\n")[0])
        data["weights"][0] += 1
        content = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
        forged = content + b"\\n" + sha256(content).hexdigest().encode()
        with self.assertRaises(ValueError):
            S.NumericGrow.restore(self.graph, forged)

    def test_symbolic_strong_control_and_source_budget(self):
        source = S.EvidenceSource(self.w, self.w.targets[2])
        control = S.SymbolicGrow(self.graph)
        for subject in S.inquiry_pool(self.w)[:8]:
            control.observe(subject, source.query(subject))
        self.assertEqual(source.count, 8)
        self.assertIn(self.w.targets[2], control.hypotheses)
        held = S.held_subjects(self.w)
        if control.law() is not None:
            self.assertEqual([control.infer(s) for s in held],
                             [S.walk(self.graph, s, self.w.targets[2]) for s in held])
        with self.assertRaises(ValueError):
            control.observe(S.inquiry_pool(self.w)[0], 1)

    def test_preimplementation_prereg_and_no_primary_execution(self):
        spec = json.loads((Path(__file__).parent/"prereg.json").read_text())
        self.assertEqual(spec["experiment_id"], "WSP-120")
        self.assertFalse(spec["authority"]["scientific_first_use"])
        self.assertEqual(spec["fresh_source"]["background_edge_tiers"], list(S.TIERS))
        self.assertEqual(spec["fresh_source"]["max_source_calls"], S.MAX_QUERIES)
        self.assertEqual(spec["fresh_source"]["exposure_checkpoints"], list(S.EXPOSURES))
        self.assertNotIn(S.ENGINEERING_SEED, S.PUBLIC_SEEDS)


if __name__ == "__main__":
    unittest.main()
