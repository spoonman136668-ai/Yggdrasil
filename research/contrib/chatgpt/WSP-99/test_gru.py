"""WSP99 GRU baseline gradient and guard tests, fixture source only."""
from __future__ import annotations
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from controls import _training_arrays
from gru_control import GradientGRU16
from test_controls import fixture_episodes
from task import bits


class GRUTests(unittest.TestCase):
    def test_capacity_and_determinism(self):
        rows = fixture_episodes(0, 4)
        a, b = GradientGRU16(11), GradientGRU16(11)
        self.assertEqual(sum(w.size for w in a.weights.values()), 1398)
        self.assertEqual(a.train(rows, epochs=12, development=True),
                         b.train(rows, epochs=12, development=True))
        self.assertEqual(a.rollout(bits(2), (0, 1, 3)),
                         b.rollout(bits(2), (0, 1, 3)))
        self.assertTrue(0 <= a.source_fit(rows) <= 1)

    def test_gradient_matches_independent_numeric_difference(self):
        model = GradientGRU16(17)
        _, xs, ys = _training_arrays(fixture_episodes(1, 2))
        _, gradients = model._grad(xs, ys)
        for name, coord in (
            ("Wo", (0, 0)), ("Wn", (0, 0)), ("Un", (0, 0)),
            ("Wr", (0, 0)), ("Ur", (0, 0)),
            ("Wz", (0, 0)), ("Uz", (0, 0)),
            ("bn", (0,)), ("br", (0,)), ("bz", (0,))
        ):
            arr = model.weights[name]
            original = arr[coord]
            epsilon = 1e-5
            arr[coord] = original + epsilon
            positive = model._grad(xs, ys)[0]
            arr[coord] = original - epsilon
            negative = model._grad(xs, ys)[0]
            arr[coord] = original
            approx = (positive - negative) / (2 * epsilon)
            self.assertAlmostEqual(gradients[name][coord], approx, delta=1e-7)

    def test_loss_decreases_under_fixture_training(self):
        rows = fixture_episodes(2, 5)
        model = GradientGRU16(23)
        _, xs, ys = _training_arrays(rows)
        before = model._grad(xs, ys)[0]
        after = model.train(rows, epochs=24, development=True)
        self.assertLess(after, before)

    def test_disallow_budget_change_and_unregistered_seeds(self):
        rows = fixture_episodes(0, 2)
        with self.assertRaises(ValueError):
            GradientGRU16(99)
        with self.assertRaises(ValueError):
            GradientGRU16(True)
        model = GradientGRU16(11)
        for epochs in (0, 24, 1799, 1801):
            with self.assertRaises(ValueError):
                model.train(rows, epochs=epochs)
        with self.assertRaises(ValueError):
            model.train(rows, epochs=25, development=True)
        with self.assertRaises(ValueError):
            model.rollout(bits(0), (0, 1, 2, 3, 0))


if __name__ == "__main__":
    unittest.main()
