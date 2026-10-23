"""P0F-C1 focused source-free checks; never substitute these for original engine runs."""
import copy
import math
import unittest

from research.p0fc1.original_history import (
    cluster_review, contract, probs, score, train, validate_row,
)

C = bytes([12])*32 + bytes([1])
H0 = C + bytes([22])*66
H1 = C + bytes([33])*66
Y0 = bytes([44])*32
Y1 = bytes([55])*32


def event(seed, hist, outcome):
    return {"seed": seed, "step": 0, "current_key": C,
            "history_key": hist, "next_key": outcome}


class P0FC1SourceFree(unittest.TestCase):
    def test_frozen_original_source_dev_roles(self):
        p = contract()
        self.assertEqual(len(p["train_seeds"]), 30)
        self.assertEqual(len(p["development_seeds"]), 12)
        self.assertTrue(set(p["train_seeds"]).isdisjoint(p["development_seeds"]))
        self.assertIs(p["protected_first_use"], False)
        self.assertIs(p["no_native_model_training"], True)

    def test_invalid_or_privileged_schema_rejected(self):
        with self.assertRaisesRegex(ValueError, "SCHEMA"):
            validate_row({**event(1, H0, Y0), "hidden_game_state": 5})
        with self.assertRaisesRegex(ValueError, "BYTES"):
            validate_row({**event(1, H0, Y0), "history_key": b"a"})

    def test_true_lawful_history_raises_full_outcome_probability(self):
        t = [event(i, H0, Y0) for i in range(20)]
        t += [event(i+20, H1, Y1) for i in range(20)]
        model = train(t)
        p0, p1, seen_current, seen_hist = probs(model, event(100, H0, Y0))
        self.assertGreater(p1, p0)
        self.assertTrue(seen_current)
        self.assertTrue(seen_hist)
        self.assertTrue(0 < p0 <= 1)
        self.assertTrue(0 < p1 <= 1)

    def test_unknown_history_backoff_is_exact_current_prediction(self):
        model = train([event(i, H0, Y0) for i in range(5)])
        third = C + bytes([66])*66
        p0, p1, _, seen_hist = probs(model, event(200, third, Y0))
        self.assertFalse(seen_hist)
        self.assertAlmostEqual(p0, p1, places=14)

    def test_held_outcome_does_not_train_model(self):
        t = [event(i, H0, Y0) for i in range(5)]
        m = train(t)
        before = copy.deepcopy(m)
        _ = score(m, [event(1000, H0, Y1)])
        self.assertEqual(m, before)

    def test_never_collapse_distinct_categorical_next_public_frames(self):
        m = train([event(i, H0, Y0) for i in range(12)])
        good = probs(m, event(100, H0, Y0))[0]
        bad = probs(m, event(100, H0, Y1))[0]
        self.assertGreater(good, bad)
        self.assertTrue(math.isfinite(-math.log(bad)))

    def test_replicate_unit_is_reset_seed_not_timestep(self):
        m = train([event(i, H0, Y0) for i in range(12)] +
                  [event(i+12, H1, Y1) for i in range(12)])
        held = [event(100+j, H0, Y0) for j in range(12)]
        obs = score(m, held)
        s = cluster_review(obs)
        self.assertEqual(s["independent_source_reset_clusters"], 12)
        self.assertEqual(s["original_held_events"], 12)
        self.assertGreater(s["paired_seed_95_percentile_bootstrap_interval"][0], 0)


if __name__ == "__main__":
    unittest.main()
