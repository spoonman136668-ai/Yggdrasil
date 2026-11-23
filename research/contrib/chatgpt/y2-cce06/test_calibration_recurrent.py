"""Public-only recurrent estimator tests: synthetic fixtures only."""
import math
import random
import unittest
from calibration_recurrent import TrainableRecurrentEstimator
from calibration_recurrent_selection import select_recurrent_on_train


def fixture(seed, length=60):
    rng = random.Random(seed)
    obs = [rng.randrange(2), rng.randrange(2)]
    out = []
    for _ in range(length):
        a = rng.randrange(3)
        new = [obs[0] ^ int(a == 1 and rng.random() < .85),
               obs[1] ^ int(a == 2 and rng.random() < .85)]
        out.append(dict(observation=obs[:], action=a, next_observation=new[:]))
        obs = new
    return tuple(out)


class RecurrentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train = (fixture(997, 75), fixture(998, 80))
        cls.model = TrainableRecurrentEstimator(4, seed=7).fit(cls.train,
                                                                epochs=6, lr=0.02,
                                                                truncate=10)

    def test_weight_training_not_random_reservoir(self):
        old = TrainableRecurrentEstimator(4, seed=7)
        self.assertNotEqual(old.wh, self.model.wh)
        self.assertNotEqual(old.wx, self.model.wx)
        self.assertNotEqual(old.wo, self.model.wo)
        self.assertEqual(self.model.train_events, 155)

    def test_recurrent_state_changes_and_probabilities_normalized(self):
        m = self.model
        h = m.new_state()
        for e in fixture(999, 20):
            h, p = m.forecast(h, e['observation'], e['action'])
            self.assertEqual(len(h), 4)
            self.assertAlmostEqual(sum(p), 1)
            self.assertTrue(all(0 < v < 1 for v in p))
            self.assertTrue(all(math.isfinite(v) for v in h))

    def test_public_stream_score_determinism(self):
        first = self.model.score((fixture(999, 15),))
        second = self.model.score((fixture(999, 15),))
        self.assertEqual(first, second)
        self.assertTrue(0 <= first <= 1)

    def test_identical_seeds_reproduce_weights(self):
        same = TrainableRecurrentEstimator(4, seed=7).fit(self.train, epochs=6,
                                                          lr=0.02, truncate=10)
        self.assertEqual(self.model.wh, same.wh)
        self.assertEqual(self.model.wo, same.wo)
        self.assertEqual(self.model.trace, same.trace)

    def test_reject_private_fields_in_train_validation_and_scoring(self):
        bad = list(self.train[0]); bad[2] = dict(bad[2], latent=[0,0,1])
        with self.assertRaises(ValueError):
            TrainableRecurrentEstimator(4).fit((tuple(bad),), epochs=2)
        with self.assertRaises(ValueError):
            TrainableRecurrentEstimator(4).fit(self.train, epochs=2,
                                             validation=(tuple(bad),))
        with self.assertRaises(ValueError):
            self.model.score((tuple(bad),))

    def test_reject_unfitted_forecasts_and_invalid_input(self):
        with self.assertRaises(ValueError):
            TrainableRecurrentEstimator(4).new_state()
        with self.assertRaises(ValueError):
            self.model.forecast(self.model.new_state(), [0, 1], 7)
        with self.assertRaises(ValueError):
            self.model.forecast((float('nan'),)*4, [0,1], 1)
        with self.assertRaises(ValueError):
            TrainableRecurrentEstimator(5)

    def test_train_only_selection_and_all_train_refit(self):
        model, receipt = select_recurrent_on_train(self.train, widths=(4,),
                        learning_rates=(0.02,), epochs=7, patience=2,
                        truncate=10)
        self.assertEqual(receipt['final_train_events'], 155)
        self.assertEqual(receipt['train_fit_events'] + receipt['train_select_events'], 155)
        self.assertFalse(receipt['includes_cal_eval'])
        self.assertGreater(receipt['final_epochs'], 0)
        self.assertLessEqual(receipt['final_epochs'], 7)
        self.assertTrue(math.isfinite(model.score((fixture(999, 17),))))

    def test_invalid_selection_grid_fails_closed(self):
        with self.assertRaises(ValueError):
            select_recurrent_on_train(self.train, widths=(3,))
        with self.assertRaises(ValueError):
            select_recurrent_on_train(self.train, learning_rates=(0.,))
        with self.assertRaises(ValueError):
            select_recurrent_on_train(self.train, widths=(4,4))


if __name__ == '__main__':
    unittest.main()
