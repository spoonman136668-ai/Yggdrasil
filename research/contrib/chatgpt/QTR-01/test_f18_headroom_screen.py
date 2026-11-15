"""F18 source-free invariants; actual upstream run is in CI."""
import unittest
import numpy as np
from f18_headroom_screen import (
    N_TRAIN, N_TEST, SEEDS, polynomial_features, ols_predict,
    knn_predict, exact_event_coverage, mlp_predict,
)


class F18(unittest.TestCase):
    def test_frozen_size_and_seeds(self):
        self.assertEqual((N_TRAIN, N_TEST, SEEDS), (480, 240, (1911, 1912, 1913, 1914)))

    def test_quadratic_recovers_known_causal_law_with_no_leakage(self):
        x = np.asarray([[-2., .1], [-1., 1.], [0., -.5],
                        [1., .3], [2., -1.], [3., .7]])
        y = .8 * x[:, 0]**2 - .3 * x[:, 1] + .5
        query = np.asarray([[-1.5, 1.], [1.5, -1.]])
        answer = ols_predict(x, y, query, True)
        expected = .8 * query[:, 0]**2 - .3 * query[:, 1] + .5
        np.testing.assert_allclose(answer, expected, atol=1e-9)
        linear = ols_predict(x, y, query, False)
        self.assertGreater(float(np.mean((linear - expected)**2)), 0.001)

    def test_exact_event_lookup_reports_abstention(self):
        train = np.asarray([[1., 2.], [3., 4.]])
        test = np.asarray([[3., 4.], [5., 6.]])
        self.assertEqual(exact_event_coverage(train, test), 1)

    def test_mlp_fixed_optimization_deterministic_and_nontrivial(self):
        x = np.linspace(-2, 2, 40)[:, None]
        y = x[:, 0]**2
        a = mlp_predict(x, y, x, 55, updates=300)
        b = mlp_predict(x, y, x, 55, updates=300)
        np.testing.assert_array_equal(a, b)
        self.assertLess(float(np.mean((a - y)**2)), .15)

    def test_knn_and_wrong_shapes(self):
        x = np.asarray([[0.], [1.], [2.], [3.], [4.],
                        [5.], [6.], [7.]])
        y = x[:, 0]
        pred = knn_predict(x, y, np.asarray([[.5]]))
        self.assertEqual(pred.shape, (1,))
        with self.assertRaises(ValueError):
            polynomial_features(np.asarray([1., 2.]), True)


if __name__ == "__main__":
    unittest.main()
