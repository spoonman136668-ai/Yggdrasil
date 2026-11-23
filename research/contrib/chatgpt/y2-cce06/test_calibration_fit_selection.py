"""CCE06 synthetic public-fixture qualification, no registered CAL/PRIMARY seeds."""
import math
import random
import unittest

from calibration_fit_selection import (
    split_train_only, score_public_brier, select_suffix_on_train, select_hmm_on_train)
from calibration_controls import FullSuffixTable, multichannel_brier, validated


def fixture(seed=997, length=75):
    rng = random.Random(seed)
    observation = [rng.randrange(2), rng.randrange(2)]
    events = []
    for _ in range(length):
        action = rng.randrange(3)
        following = [observation[0] ^ int(action == 1 and rng.random() < .8),
                     observation[1] ^ int(action == 2 and rng.random() < .8)]
        events.append({"observation": observation[:], "action": action,
                       "next_observation": following[:]})
        observation = following
    return tuple(events)


class PublicTrainOnlySelectionFixture(unittest.TestCase):
    def setUp(self):
        self.public_train = (fixture(), fixture(998, 80))

    def test_chronological_partition_rejoins_without_leaking(self):
        p = split_train_only(self.public_train)
        self.assertEqual(p.fit_events + p.select_events, 155)
        self.assertEqual(p.fit[0] + p.select[0], self.public_train[0])
        self.assertEqual(p.fit[1] + p.select[1], self.public_train[1])
        self.assertEqual(p.select[0][0]["observation"], p.fit[0][-1]["next_observation"])
        self.assertIsNot(p.fit[0][0], self.public_train[0][0])
        validated(p.select[0])

    def test_hidden_evaluator_field_fails_closed(self):
        bad = list(fixture())
        bad[2] = dict(bad[2], true_state=[1, 0, 1])
        with self.assertRaises(ValueError):
            split_train_only((tuple(bad),))
        with self.assertRaises(ValueError):
            select_suffix_on_train((tuple(bad),))

    def test_train_only_suffix_selection_and_refit(self):
        model, receipt = select_suffix_on_train(self.public_train, depths=(1, 2, 3))
        self.assertEqual(receipt["final_train_events"], 155)
        self.assertEqual(len(receipt["grid"]), 3)
        self.assertIn(model.depth, (1, 2, 3))
        p = model.predict((), 1)
        self.assertAlmostEqual(sum(p), 1)
        self.assertTrue(math.isfinite(score_public_brier(model, (fixture(999, 12),))))

    def test_hmm_train_only_three_restarts_each_dimension(self):
        model, receipt = select_hmm_on_train(self.public_train, dimensions=(2, 3),
                                              restarts=3, max_iters=4)
        self.assertEqual(len(receipt["restarts"]), 6)
        self.assertEqual(receipt["grid_restarts"], 3)
        self.assertIn(receipt["selection"]["dimension"], (2, 3))
        self.assertEqual(receipt["full_train_events"], 155)
        self.assertEqual(receipt["status"], "HMM_CONVERGENCE_UNVERIFIED")
        self.assertFalse(receipt["final_converged"])
        self.assertTrue(all(math.isfinite(x["train_log_likelihood"])
                            for x in receipt["restarts"]))
        self.assertAlmostEqual(sum(model.predict((), 2)), 1)

    def test_invalid_grids_or_undersized_public_train_fail_closed(self):
        with self.assertRaises(ValueError):
            select_hmm_on_train(self.public_train, restarts=2)
        with self.assertRaises(ValueError):
            select_suffix_on_train(self.public_train, depths=(0,))
        with self.assertRaises(ValueError):
            split_train_only((fixture(length=20),), min_select=16)
        with self.assertRaises(ValueError):
            split_train_only((fixture(),), fraction=0.6)

    def test_bounded_suffix_history_matches_full_history(self):
        model = FullSuffixTable(3).fit(self.public_train)
        events = fixture(1001, 150)
        original = sum(
            multichannel_brier(
                model.predict(events[:t], e["action"]), e["next_observation"])
            for t, e in enumerate(events)) / len(events)
        bounded = score_public_brier(model, (events,))
        self.assertAlmostEqual(original, bounded, places=15)

    def test_predictive_holdout_scoring_prohibits_leaked_labels(self):
        model = FullSuffixTable(2).fit(self.public_train)
        valid = fixture(999, 9)
        p = score_public_brier(model, (valid,))
        self.assertTrue(0 <= p <= 1)
        bad = [dict(e) for e in valid]
        bad[-1] = dict(bad[-1], oracle_label=1)
        with self.assertRaises(ValueError):
            score_public_brier(model, (bad,))


if __name__ == "__main__":
    unittest.main()
