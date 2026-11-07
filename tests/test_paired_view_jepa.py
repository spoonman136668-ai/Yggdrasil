"""Development parity and falsification only; never scientific first use."""
import unittest

from yggdrasil.paired_view_jepa import Pair, PairedViewJEPA, DirectLinearControl, development_pairs, mispaired


class PairedViewJEPATests(unittest.TestCase):
    def test_learns_predictive_latents_from_genuine_pairs(self):
        train = development_pairs(0, 180)
        cold = development_pairs(5000, 90)
        learner = PairedViewJEPA()
        before = learner.mse(cold)
        learner.fit(train, epochs=170)
        after = learner.mse(cold)
        self.assertLess(after, before)
        self.assertTrue(all(abs(v) < 10 for row in learner.encoder for v in row))

    def test_bad_views_are_separately_falsifiable(self):
        train = development_pairs(0, 180)
        cold = development_pairs(5000, 90)
        good = PairedViewJEPA()
        bad = PairedViewJEPA()
        good.fit(train, epochs=170)
        bad.fit(mispaired(train), epochs=170)
        self.assertLess(good.mse(cold), bad.mse(cold))

    def test_fully_trained_conventional_control_is_not_omitted(self):
        train = development_pairs(0, 180)
        heldout = development_pairs(5000, 90)
        conventional = DirectLinearControl()
        before = conventional.mse(heldout)
        conventional.fit(train, epochs=170)
        self.assertLess(conventional.mse(heldout), before)
        self.assertEqual(len(conventional.weights), 2)

    def test_train_does_not_mutate_dataset_or_frozen_target(self):
        train = development_pairs(0, 80)
        before = tuple(train)
        model = PairedViewJEPA()
        model.fit(train, epochs=3)
        self.assertEqual(train, before)
        self.assertEqual(model.predictor != [[.8, .02], [-.02, .8]], True)

    def test_invalid_pairs_and_budget_fail_closed(self):
        model = PairedViewJEPA()
        for rows in ((Pair((0., 0., 0.), (1., 1.)),) * 8,
                     (Pair((0., 0., 0.), (float('nan'), 1.)),) * 8):
            with self.assertRaises(ValueError):
                model.fit(rows)
        with self.assertRaises(ValueError):
            model.fit(development_pairs(0, 20), epochs=201)
        with self.assertRaises(ValueError):
            model.predict((float('inf'), 0., 0.))
        with self.assertRaises(ValueError):
            development_pairs(-1, 10)

    def test_no_hidden_state_or_autonomy_authority(self):
        learner = PairedViewJEPA()
        self.assertEqual(len(learner.encoder), 2)
        self.assertEqual(len(learner.predictor), 2)
        self.assertFalse(hasattr(learner, 'dispatch'))
        self.assertFalse(hasattr(learner, 'grant_scientific_first_use'))


if __name__ == '__main__':
    unittest.main()
