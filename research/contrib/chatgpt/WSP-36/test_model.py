import unittest
from model import (
    NumericCircuit, GATES, MASKS, THREE, TWO, FOUR, table,
    signature, learned_weights, numeric_acquire, teacher_view
)
from run_dev import generate, novel_rule, independent_oracle, TARGETS, run

class PartialKnowledgeTests(unittest.TestCase):
    def test_three_rows_identify_known_masks_two_rows_do_not(self):
        self.assertEqual(len({signature(m, THREE) for m in MASKS}), 8)
        self.assertLess(len({signature(m, TWO) for m in MASKS}), 8)

    def test_actual_probe_count_and_no_full_source_to_numeric_learner(self):
        spec = generate("DEV", 5)
        fn, seen = teacher_view(spec)
        topo = tuple((a,b) for a,b,_ in spec)
        model, recovered, trace = numeric_acquire(topo, fn, THREE)
        self.assertEqual(recovered, spec)
        self.assertEqual(tuple(seen), trace)
        self.assertEqual(len(seen), 3*GATES)
        self.assertTrue(all(k in THREE for _,k,_ in seen))
        for x in TARGETS:
            self.assertEqual(model.predict(x), independent_oracle(spec,x))

    def test_unseen_row_two_is_never_queried_in_three_probe_arm(self):
        spec = generate("DEV", 9)
        _, recovered, audit = learned_weights(spec, THREE)
        self.assertEqual(len(audit), 3*GATES)
        self.assertFalse(any(row == 2 for _,row,_ in audit))
        self.assertEqual(recovered, spec)

    def test_two_row_ambiguity_and_weight_identity(self):
        spec = generate("DEV", 4)
        a, ra, t = learned_weights(spec, TWO)
        b, rb, _ = learned_weights(spec, TWO)
        self.assertEqual(a.snapshot(),b.snapshot())
        self.assertEqual(ra,rb)
        self.assertEqual(len(t),2*GATES)
        self.assertNotEqual(set(signature(m,TWO) for m in MASKS),set(signature(m,THREE) for m in MASKS))

    def test_out_of_family_flip_is_unobservable_until_fourth_query(self):
        spec = novel_rule(generate("DEV", 3))
        m3, inferred, audit = learned_weights(spec, THREE)
        m4, full, _ = learned_weights(spec, FOUR)
        self.assertEqual(len(audit),3*GATES)
        self.assertEqual(sum(a==b for a,b in zip(inferred[-1][2],spec[-1][2])),3)
        self.assertEqual(full,spec)
        self.assertNotEqual(m3.snapshot(),m4.snapshot())

    def test_atomic_invalid_queries_and_checkpoint_guard(self):
        spec = generate("DEV", 1)
        topology = tuple((a,b) for a,b,_ in spec)
        bad = list(topology)
        bad[0] = (3,1)
        with self.assertRaises(ValueError):
            numeric_acquire(tuple(bad),lambda g,k: 0,THREE)
        with self.assertRaises(ValueError):
            numeric_acquire(topology,lambda g,k: True,THREE)
        with self.assertRaises(ValueError):
            numeric_acquire(topology,lambda g,k: 0,(0,2,3))
        raw = learned_weights(spec,THREE)[0].snapshot()
        with self.assertRaises(ValueError):
            NumericCircuit.restore(raw[:-1]+bytes([raw[-1]^1]))

    def test_dev_cohort_complete_and_science_bounded(self):
        result = run("DEV")
        self.assertEqual(result["engineering"],"PASS")
        self.assertEqual(result["scientific_status"],"DEV_SUPPORTED")
        self.assertEqual(result["scores_gate_rows"]["direct_3"],64*8*4)
        self.assertEqual(result["scores_composed"]["direct_3"],64*8)
        self.assertEqual(result["scores_composed"]["trained_3"],64*8)
        self.assertEqual(result["ood"]["three_gate7_correct"],64*3)
        self.assertEqual(result["ood"]["four_gate7_correct"],64*4)

if __name__=="__main__":
    unittest.main()
