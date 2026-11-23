"""CCE06 public TRAIN-only PSR selection; fixture seeds only."""
import math
import unittest
from calibration_psr_selection import select_psr_on_train
from test_calibration_psr import fixture


class PSRSelectionFixtures(unittest.TestCase):
    def setUp(self):
        self.train = (fixture(997, 100), fixture(998, 100))

    def test_selects_capacity_and_refits_only_from_train(self):
        model, receipt = select_psr_on_train(self.train, test_grid=(3, 6),
                                             depth_grid=(1, 2), ridge_grid=(0.1,))
        self.assertEqual(receipt['status'], 'TRAIN_ONLY_PSR_SELECTED')
        self.assertEqual(receipt['fit_events'] + receipt['selection_events'], 200)
        self.assertEqual(receipt['final_train_events'], 200)
        self.assertEqual(receipt['learned_operators'], 12)
        self.assertEqual(len(receipt['grid']), 4)
        self.assertIn(receipt['selected']['tests'], (3, 6))
        self.assertFalse(receipt['includes_cal_eval'])
        self.assertTrue(all(math.isfinite(s['validation_brier'])
                            for s in receipt['grid']))
        self.assertAlmostEqual(sum(model.forecast(model.new_state(), 1)), 1)

    def test_rejects_hidden_fields_and_invalid_capacity(self):
        bad = list(self.train[0]); bad[0] = dict(bad[0], latent_graph=[1,0])
        with self.assertRaises(ValueError):
            select_psr_on_train((tuple(bad), self.train[1]), test_grid=(3,))
        with self.assertRaises(ValueError):
            select_psr_on_train(self.train, test_grid=(2,))
        with self.assertRaises(ValueError):
            select_psr_on_train(self.train, ridge_grid=(-1,))
        with self.assertRaises(ValueError):
            select_psr_on_train(self.train, depth_grid=(0,))

    def test_determinism_and_no_label_selection(self):
        left, l = select_psr_on_train(self.train, test_grid=(3, 6),
                                      depth_grid=(2,), ridge_grid=(0.05,))
        right, r = select_psr_on_train(self.train, test_grid=(3, 6),
                                       depth_grid=(2,), ridge_grid=(0.05,))
        self.assertEqual(l, r)
        self.assertEqual(left.operators, right.operators)


if __name__ == '__main__':
    unittest.main()
