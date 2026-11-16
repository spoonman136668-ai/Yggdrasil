"""WSP-120 conventional GRU source-safe fixture; NEVER the primary cohort."""
from __future__ import annotations

import unittest

import structural_growth as S
import trained_gru as G


class TrainedGRUFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.world = S.engineering_fixture_world()
        cls.graph = cls.world.public_graph(384)
        cls.source = S.EvidenceSource(cls.world, cls.world.targets[0])
        cls.observations = tuple(
            (s, cls.source.query(s)) for s in S.inquiry_pool(cls.world)[:8])

    def test_full_three_seed_training_and_reproducibility(self):
        result = G.train_conventional_gru(self.graph, self.observations)
        self.assertTrue(result.converged, "fixture must fully converge")
        self.assertEqual(set(result.epochs_by_seed), set(G.SEEDS))
        self.assertEqual(result.training_accuracy, 1.0)
        self.assertLessEqual(result.training_loss, G.TRAIN_LOSS_CEILING)
        self.assertLessEqual(max(x["epochs"] for x in result.epochs_by_seed.values()),
                             G.MAX_EPOCHS)
        self.assertEqual(
            result.infer([s for s, _ in self.observations]),
            tuple(y for _, y in self.observations))
        self.assertEqual(len(result.infer(S.held_subjects(self.world))), 24)
        self.assertEqual(result.parameter_count, 42560)
        rerun = G.train_conventional_gru(self.graph, self.observations)
        self.assertTrue(rerun.converged)
        self.assertEqual(result.winning_seed, rerun.winning_seed)
        self.assertEqual(
            result.infer(S.held_subjects(self.world)),
            rerun.infer(S.held_subjects(self.world)))

    def test_evidence_guard_no_update_and_missing_convergence(self):
        for observations in (
            [(0, 1), (0, 2)], [(0, 0)] * 33, [(0, 64)],
            [(True, 4)], [(64, 1)], [(0, 0, 1)]):
            with self.subTest(observations=str(observations)[:20]):
                with self.assertRaises(ValueError):
                    G.train_conventional_gru(self.graph, observations)
        empty = G.train_conventional_gru(self.graph, [])
        self.assertFalse(empty.converged)
        self.assertEqual(empty.infer([0, 1]), (None, None))
        self.assertNotIn(S.ENGINEERING_SEED, S.PUBLIC_SEEDS)
        self.assertTrue(set(S.PUBLIC_SEEDS).isdisjoint(S.RESERVED_SEEDS))


if __name__ == "__main__":
    unittest.main()
