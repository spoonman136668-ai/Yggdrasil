"""F19 source-free gradient/negative controls before pinned package execution."""
import unittest
import numpy as np

from f19_temporal_challenge import (
    HIDDEN, SEEDS, ADAM_UPDATES, symbolic_design, symbolic_ols,
    rnn_loss_grad, rnn_predict, rnn_forward,
)


class F19(unittest.TestCase):
    def test_frozen_capacity_and_seeds(self):
        self.assertEqual(HIDDEN, 16)
        self.assertEqual(ADAM_UPDATES, 240)
        self.assertEqual(SEEDS, (2011, 2012, 2013, 2014))

    def test_symbolic_basis_covers_relu_tanh_and_abs(self):
        x = np.asarray([
            [-2., 0., -.5, 2.], [-1., 2., -.25, 1.],
            [0., -1., .5, 0.], [1., 1., .8, -1.],
            [2., -2., -.9, 0.], [.5, 0., 1., 1.],
            [-.5, -1.5, .4, 2.], [1.5, .5, -1.2, -2.],
        ])
        basis = symbolic_design(x)
        self.assertEqual(basis.shape, (8, 12))
        self.assertTrue(np.isfinite(basis).all())
        self.assertTrue((basis[:, 0] == 1.).all())

    def test_rnn_bptt_gradient_agrees_with_central_difference(self):
        rng = np.random.default_rng(19)
        x = rng.normal(size=(6, 4))
        target = rng.normal(size=6)
        params = [
            rng.normal(0, .1, size=(4, HIDDEN)),
            rng.normal(0, .04, size=(HIDDEN, HIDDEN)),
            np.zeros(HIDDEN),
            rng.normal(0, .1, size=HIDDEN),
            np.zeros(1),
        ]
        loss, grads = rnn_loss_grad(x, target, params)
        self.assertTrue(np.isfinite(loss))
        for index, coordinate in ((0, (1, 2)), (1, (1, 2)), (2, (3,)),
                                  (3, (4,)), (4, (0,))):
            param = params[index]
            old = float(param[coordinate])
            param[coordinate] = old + 1e-5
            upper = rnn_loss_grad(x, target, params)[0]
            param[coordinate] = old - 1e-5
            lower = rnn_loss_grad(x, target, params)[0]
            param[coordinate] = old
            numerical = (upper - lower) / (2e-5)
            self.assertAlmostEqual(float(grads[index][coordinate]), numerical,
                                   places=5)

    def test_fully_trained_rnn_deterministic_and_nontrivial(self):
        rng = np.random.default_rng(170)
        x = rng.normal(size=(48, 4))
        y = .75*np.tanh(x[:, 0]) + .1*x[:, 3]
        a, _ = rnn_predict(x, y, x, seed=32, updates=120)
        b, _ = rnn_predict(x, y, x, seed=32, updates=120)
        np.testing.assert_array_equal(a, b)
        self.assertLess(float(np.mean((a-y)**2)), .10)

    def test_public_symbolic_regression_learns_nonlinearity(self):
        rng = np.random.default_rng(57)
        x = rng.normal(size=(200, 4))
        y = .8*np.maximum(x[:, 0], 0) - .4*np.abs(x[:, 1]) + .3*np.tanh(x[:, 2])
        test_x = rng.normal(size=(90, 4))
        expected = .8*np.maximum(test_x[:, 0], 0) - .4*np.abs(test_x[:, 1]) + .3*np.tanh(test_x[:, 2])
        got = symbolic_ols(x, y, test_x)
        np.testing.assert_allclose(got, expected, atol=1e-7)


if __name__ == "__main__":
    unittest.main()
