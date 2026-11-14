"""F21 source-free mathematical control invariants; source-exact run in CI."""
import unittest
from types import SimpleNamespace

from f21_jepa_linear_audit import (
    PREREG, JEPA_BLOB, JEPA_COMMIT, folded_matrix, apply_linear, fit_direct_ols,
)


class DummyPair:
    def __init__(self, obs, target):
        self.observation, self.other_view = obs, target


class F21(unittest.TestCase):
    def test_source_identity_and_preregistered_boundary(self):
        self.assertEqual(len(JEPA_COMMIT), 40)
        self.assertEqual(len(JEPA_BLOB), 40)
        self.assertEqual(len(PREREG), 40)

    def test_exact_composition_algebra_on_broad_public_probes(self):
        fake = SimpleNamespace(
            encoder=[[.7, -.3, .4], [-.2, .6, .1]],
            predictor=[[.4, .8], [-.5, .2]],
        )
        folded = folded_matrix(fake)
        for x in ((0., 0., 0.), (1., -1., .3),
                  (-2.4, 3.5, -1.), (.7, .7, .7)):
            encoded = [sum(fake.encoder[j][k] * x[k]
                           for k in range(3)) for j in range(2)]
            expected = tuple(sum(fake.predictor[i][j] * encoded[j]
                                 for j in range(2)) for i in range(2))
            for found, intended in zip(apply_linear(folded, x), expected):
                self.assertAlmostEqual(found, intended, places=12)

    def test_independent_linear_solver_recovers_exact_public_mapping(self):
        observations = [
            (1., 0., 0.), (0., 1., 0.), (0., 0., 1.),
            (1., 1., 1.), (-1., .5, 2.), (2., -1., -.5),
        ]
        truth = ((.3, .4, -.7), (-.2, .8, .1))
        rows = tuple(DummyPair(x, apply_linear(truth, x))
                     for x in observations)
        got = fit_direct_ols(rows)
        for actual, expected in zip(got, truth):
            for a, b in zip(actual, expected):
                self.assertAlmostEqual(a, b, places=11)

    def test_rank_deficient_direct_control_fails_closed(self):
        rows = tuple(DummyPair((1., 1., 1.), (.5, -.5)) for _ in range(5))
        with self.assertRaises(ValueError):
            fit_direct_ols(rows)


if __name__ == "__main__":
    unittest.main()
