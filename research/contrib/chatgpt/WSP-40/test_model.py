import itertools
import unittest
from model import NumericModel, IndependentIdentifier, FittedRegression, acquire, rotate
from battery import World


class Tests(unittest.TestCase):
    def test_numeric_truth_all_states(self):
        model = NumericModel(4, (3, 14))
        for action, state in itertools.product(range(2), range(16)):
            m = model.supports[action]
            self.assertEqual(model.apply(action, state), rotate(4, action, state) ^ int((state & m) == m))

    def test_active_discovers_all_four_bit_pair_triple_rules(self):
        for support in (3, 5, 6, 7, 9, 10, 11, 12, 13, 14):
            target = NumericModel(4, (support, support))
            model, transcript, remaining = acquire(4, target.apply, 12, "active", 737)
            self.assertEqual(model.supports, target.supports)
            self.assertEqual(remaining, (1, 1))
            self.assertEqual(IndependentIdentifier(4, transcript).supports, target.supports)

    def test_ambiguity_counts_as_prediction_not_certainty(self):
        target = NumericModel(8, (3, 7))
        model, transcript, remaining = acquire(8, target.apply, 4, "singleton", 741)
        self.assertTrue(all(n > 1 for n in remaining))
        self.assertEqual(len(transcript), 8)

    def test_regression_convergence_and_independent_predictions(self):
        target = NumericModel(4, (3, 14))
        transcript = tuple((a, x, target.apply(a, x) ^ rotate(4, a, x)) for a in range(2) for x in range(16))
        fitted = FittedRegression(4, transcript)
        self.assertEqual(fitted.train_errors, [0, 0])
        for a, x in itertools.product(range(2), range(16)):
            self.assertEqual(fitted.apply(a, x), target.apply(a, x))

    def test_cold_tamper_and_schema(self):
        model = NumericModel(8, (3, 7))
        self.assertEqual(NumericModel.restore(model.snapshot()).snapshot(), model.snapshot())
        for bad in (b"", model.snapshot()[:-1], model.snapshot() + b"x"):
            with self.assertRaises(ValueError): NumericModel.restore(bad)
        with self.assertRaises(ValueError): NumericModel(True, (3, 7))
        with self.assertRaises(ValueError): NumericModel(4, (15, 3))
        with self.assertRaises(ValueError): model.apply(0, -1)

    def test_ood_prior_contradiction_preserved(self):
        world = World(4, "quartic_ood", "DEV-negative")
        model, transcript, remaining = acquire(4, world.apply, 12, "active", 737)
        self.assertTrue(any(n == 0 for n in remaining))
        self.assertTrue(any(model.apply(0, x) != world.apply(0, x) for x in range(16)))

    def test_replay_and_no_hidden_oracle_state(self):
        target = NumericModel(8, (3, 7))
        first = acquire(8, target.apply, 12, "active", 741)
        second = acquire(8, target.apply, 12, "active", 741)
        self.assertEqual(first[0].snapshot(), second[0].snapshot())
        self.assertEqual(first[1:], second[1:])
        calls = []
        def probe(a, x):
            calls.append((a, x))
            return target.apply(a, x)
        acquire(8, probe, 4, "random", 741)
        self.assertEqual(len(calls), 8)


if __name__ == "__main__": unittest.main()
