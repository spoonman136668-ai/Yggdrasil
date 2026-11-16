"""Three-seed conventional MLP, disjoint source-safe engineering-only tests."""
from unittest import TestCase

import trained_mlp as G
import control_fixture as C


class TestConventionalMLP(TestCase):
    def test_converges_on_complete_boolean_table_and_repeatable(self):
        evidence = tuple((c, c.bit_count() & 1) for c in range(8))
        one = G.train_conventional_mlp(evidence)
        two = G.train_conventional_mlp(evidence)
        self.assertTrue(one.converged and two.converged)
        self.assertEqual(set(one.epochs_by_seed), set(G.SEEDS))
        self.assertEqual(one.parameter_count, 1250)
        self.assertEqual(one.evidence_count, 8)
        self.assertEqual(one.winning_seed, two.winning_seed)
        self.assertLessEqual(one.training_loss, G.LOSS_CEILING)
        self.assertEqual(one.infer_routes(range(8)), two.infer_routes(range(8)))
        self.assertEqual(one.infer_routes(range(8)), tuple(y for _, y in evidence))

    def test_control_rejects_invalid_evidence_and_bad_context(self):
        examples = [[], [(0, 0), (0, 1)], [(8, 1)], [(True, 1)],
                    [(1, 2)], [(0, False)], [(0, 0)] * 289]
        for bad in examples:
            with self.subTest(bad=repr(bad)[:50]), self.assertRaisesRegex(
                    ValueError, 'WSP121_MLP_'):
                G.train_conventional_mlp(bad)
        trained = G.train_conventional_mlp(tuple((i, i % 2) for i in range(8)))
        with self.assertRaisesRegex(ValueError, 'WSP121_MLP_INVALID_CONTEXT'):
            trained.infer_routes((8,))

    def test_matched_source_budget_and_full_cross_world_fixture(self):
        r = C.engineering_control_fixture()
        self.assertFalse(r['scientific'])
        self.assertFalse(r['source_first_use'])
        self.assertFalse(r['native_admission'])
        self.assertFalse(r['primary_seed_accessed'])
        self.assertEqual([x['budget'] for x in r['rows']], [8, 8, 4, 4])
        self.assertEqual(r['final_verified_evidence'], 24)
        self.assertEqual(len(r['rows']), 4)
        for row in r['rows']:
            self.assertTrue(row['numeric_cold_ok'])
            self.assertTrue(row['mlp_control']['converged'])
            self.assertEqual(row['mlp_control']['training_accuracy'], 1.0)
            self.assertEqual(row['mlp_control']['parameter_count'], 1250)
            self.assertEqual(row['mlp_control']['parameter_bytes'], 10000)
            for arm in ('numeric', 'symbolic', 'mlp'):
                self.assertEqual(sum(row[arm][k] for k in
                                     ('correct', 'wrong_confident', 'abstained')), 24)
            self.assertEqual(row['numeric'], row['symbolic'])
        self.assertTrue(all(x['mlp']['correct'] == 24 for x in r['rows']))
