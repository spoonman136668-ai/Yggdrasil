"""TGAP20: frozen, source-only, single-world witnessed training controls."""
import unittest

from tgap20_single_world_dev import (
    Experience, world_events, mechanism_bit, symbolic_beta, categorical_tree,
    exact_bayesian, brier, prove, HELD_WORLDS, TRAIN_WORLDS, PREREG_SHA,
)


class TGap20Tests(unittest.TestCase):
    def test_nonpublic_mechanism_affects_consequence(self):
        # Identical public inputs, distinct causal laws; nothing labels them
        # in the candidate learner's experience records.
        self.assertNotEqual(mechanism_bit(0, 1, 0),
                            mechanism_bit(1, 1, 0))
        self.assertNotEqual(mechanism_bit(2, 3, 1),
                            mechanism_bit(3, 3, 1))
        for k in range(4):
            for x in range(4):
                for a in (0, 1):
                    self.assertIn(mechanism_bit(k, x, a), (0, 1))

    def test_one_persistent_world_and_sequential_witnesses(self):
        for seed, op, _public_world_id in TRAIN_WORLDS:
            events = world_events(seed, op, 64)
            self.assertEqual(len(events), 64)
            self.assertEqual(tuple(row[0] for row in events), tuple(range(64)))
            self.assertEqual({(x, a) for _, x, a, _ in events},
                             {(x, a) for x in range(4) for a in (0, 1)})
            self.assertEqual(events, world_events(seed, op, 64))
            self.assertNotEqual(events,
                                world_events(seed, op, 64, evaluation=True))
        self.assertEqual(len(HELD_WORLDS), 8)
        self.assertEqual({k for _, k in HELD_WORLDS}, {0, 1, 2, 3})

    def test_true_stochastic_witnesses_are_not_binary_interpolated(self):
        learner = Experience()
        # Same public x/action genuinely supports both observed outcomes.
        learner.stage("world", (0, 0, 1, 0))
        learner.stage("world", (1, 0, 1, 1))
        self.assertEqual(learner.forecast("world", 0, 1), 0.5)
        learner.stage("world", (2, 0, 1, 1))
        self.assertEqual(learner.forecast("world", 0, 1), 3 / 5)
        self.assertEqual(learner.forecast("world", 3, 0), 0.5)

    def test_replay_forgery_bool_and_corrupt_cold_checkpoint_fail(self):
        learner = Experience()
        learner.stage("A", (0, 2, 1, 1))
        with self.assertRaisesRegex(ValueError, "REPLAY_GAP_OR_DUPLICATE"):
            learner.stage("A", (0, 2, 1, 1))
        with self.assertRaisesRegex(ValueError, "REPLAY_GAP_OR_DUPLICATE"):
            learner.stage("A", (2, 2, 1, 1))
        with self.assertRaisesRegex(ValueError, "FORGED_SOURCE"):
            learner.stage("A", (1, 2, 1, 1), source_mode="claimed_real")
        with self.assertRaisesRegex(ValueError, "TYPED_WITNESS"):
            learner.stage("A", (1, 2, True, 1))
        raw = learner.checkpoint()
        self.assertEqual(Experience.restore(raw, __import__("hashlib").sha256(
            raw).hexdigest()).checkpoint(), raw)
        with self.assertRaisesRegex(ValueError, "COLD_SOURCE_DIGEST"):
            Experience.restore(raw + b"x", __import__("hashlib").sha256(
                raw).hexdigest())

    def test_controls_fitted_with_identical_information(self):
        events = world_events(4101, 0, 64)
        learner = Experience()
        for row in events:
            learner.stage("W", row)
        symbol, tree, bayes = (symbolic_beta(events),
                               categorical_tree(events),
                               exact_bayesian(events))
        for x in range(4):
            for a in (0, 1):
                self.assertEqual(learner.forecast("W", x, a),
                                 symbol(x, a))
                self.assertEqual(learner.forecast("W", x, a),
                                 tree(x, a))
                self.assertTrue(0 <= bayes(x, a) <= 1)
        self.assertEqual(brier(0.5, 0), 0.25)
        self.assertEqual(brier(0.5, 1), 0.25)

    def test_frozen_science_receipt_and_retention(self):
        result = prove()
        self.assertEqual(result["preregistration_sha"], PREREG_SHA)
        self.assertEqual(result["source_mode"], "engineering_fixture_only")
        self.assertEqual((result["old_A_witnesses"],
                          result["new_B_witnesses"]), (64, 64))
        self.assertEqual(result["held_train_witnesses"], 192)
        self.assertEqual(result["held_scored_witnesses"], 512)
        self.assertEqual(result["retained_A_8_readouts_drift"], 0)
        self.assertTrue(result["old_A_cold_restore"])
        self.assertEqual(result["held_brier"]["source_only"], 0.25)
        self.assertEqual(result["held_brier"]["experience"],
                         result["held_brier"]["symbolic"])
        self.assertEqual(result["held_brier"]["experience"],
                         result["held_brier"]["tree"])
        self.assertEqual(result["scientific_gate"],
                         "DEV_NO_GO_SYNTHETIC_STRONG_CONTROLS")
        self.assertIn(result["engineering_gate"], ("PASS", "FAIL"))
        self.assertFalse(result["native_original_accumulator_modified"])
        self.assertFalse(result["canonical_trainer"])
        self.assertFalse(result["protected_first_use"])
        self.assertEqual(result["deployment"], "NONE")
        print("TGAP20_FROZEN_RECEIPT=" + __import__("json").dumps({
            "engineering_gate": result["engineering_gate"],
            "held_brier": result["held_brier"],
            "retained_A_8_readouts_drift":
                result["retained_A_8_readouts_drift"],
            "held_per_operator": result["held_by_operator_experience_brier"],
            "trained_witnesses": result["held_train_witnesses"],
            "scientific_gate": result["scientific_gate"],
        }, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
