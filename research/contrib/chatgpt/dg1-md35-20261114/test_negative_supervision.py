"""MD35 action/outcome-shuffle control, verified using ONLY handbuilt toy physics.

Never reads the reserved synthetic cohort or creates a purported physical
receipt for a shuffled label. A real 384-block trainer must later be separately
authorized and the source/family-blind custody ledger checked.
"""
import random
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from test_models import toy_block
from public_actions import PublicEpisode, require_public_blocks
from negative_supervision import (REAL, SHUFFLED, SEED, TrainingOnlyTarget,
                                  training_targets)
from bayesian_control import BayesianControl
from model_based_rl import ModelBasedRL
from gated_recurrent import training_arrays, GatedRecurrentControl
from ablations import ModelBasedWithoutRetainedBelief


class NegativeSupervisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.block = toy_block()
        # Repeated handcrafted *toy* physical receipts, NOT MD35 research
        # cohort data, used solely to test the contract's full input shape.
        cls.source = (cls.block,) * 384

    def test_shuffle_is_reproducible_derangement_and_preserves_marginals(self):
        before = tuple((ep.trace_sha256, ep.events, ep.net_utility)
                       for ep in self.block)
        real = training_targets(self.source, mode=REAL)
        shuffled = training_targets(self.source, mode=SHUFFLED)
        self.assertEqual(shuffled, training_targets(self.source, mode=SHUFFLED))
        self.assertEqual(len(shuffled), 384)
        self.assertEqual(SEED, 35047)
        self.assertTrue(all(type(v) is TrainingOnlyTarget
                            for block in shuffled for v in block))
        shift_rng = random.Random(SEED)
        for i, block in enumerate(shuffled):
            shift = shift_rng.randrange(1, 4)
            self.assertEqual(
                [v.donor_index for v in block],
                [(slot + shift) % 4 for slot in range(4)])
            self.assertEqual(sorted((v.terminal_reward, v.diagnostic_bit)
                                    for v in block),
                             sorted((v.terminal_reward, v.diagnostic_bit)
                                    for v in real[i]))
            for slot, label in enumerate(block):
                self.assertNotEqual(label.donor_index, slot)
                self.assertEqual(label.donor_trace_sha256,
                                 self.block[label.donor_index].trace_sha256)
        self.assertEqual(before, tuple((ep.trace_sha256, ep.events, ep.net_utility)
                                       for ep in self.block))
        self.assertTrue(all(type(ep) is PublicEpisode for ep in self.block))
        with self.assertRaisesRegex(AssertionError, "PRIVATE_METADATA"):
            require_public_blocks((shuffled[0],))

    def test_shuffled_supervision_cannot_be_silently_passed_as_validation(self):
        for bad in ("shuffled", None, True, False, "source"):
            with self.subTest(mode=bad):
                with self.assertRaisesRegex(
                        AssertionError, "UNREGISTERED_TRAIN_SUPERVISION"):
                    training_targets(self.source, mode=bad)
        with self.assertRaisesRegex(AssertionError, "UNQUALIFIED_TRAIN"):
            training_targets(self.source[:96], mode=SHUFFLED)
        with self.assertRaisesRegex(AssertionError, "UNQUALIFIED_TRAIN"):
            training_arrays(self.source, 96, shuffled_training=True)
        with self.assertRaisesRegex(AssertionError, "INVALID_SHUFFLE_SELECTOR"):
            training_arrays(self.source, 384, shuffled_training="true")

    def test_train_only_sham_updates_recurrent_tensors_not_public_receipts(self):
        pure = training_arrays(self.source, 384)
        sham = training_arrays(self.source, 384, shuffled_training=True)
        self.assertTrue(np.array_equal(pure[0], sham[0]))  # actions same
        self.assertTrue(np.array_equal(pure[3], sham[3]))  # masks same
        self.assertFalse(np.array_equal(pure[2], sham[2]))  # labels broken
        self.assertFalse(np.array_equal(pure[1], sham[1]))  # history labels broken
        self.assertEqual(pure[2].sum(axis=(0, 1)).tolist(),
                         sham[2].sum(axis=(0, 1)).tolist())
        self.assertTrue(all(ep.terminal()[3] in (0.98, -0.52)
                            for ep in self.block))
        self.assertEqual(GatedRecurrentControl().fitted, False)

    def test_bayes_and_rl_negative_labels_reach_fitted_statistics(self):
        # Train *only* on repeated public toy receipts for wiring inspection.
        # These are deliberately NOT substantive scientific model scores.
        real_b = BayesianControl().fit(self.source)
        sham_b = BayesianControl().fit(self.source, shuffled_training=True)
        self.assertEqual(real_b.checkpoint()["training_target_mode"], REAL)
        self.assertEqual(sham_b.checkpoint()["training_target_mode"], SHUFFLED)
        self.assertEqual(sham_b.fitted_episodes, 1536)
        self.assertTrue(np.isfinite(sham_b.prior_success).all())
        real_rl = ModelBasedRL().fit(self.source)
        sham_rl = ModelBasedRL().fit(self.source, shuffled_training=True)
        self.assertEqual(real_rl.checkpoint()["training_target_mode"], REAL)
        self.assertEqual(sham_rl.checkpoint()["training_target_mode"], SHUFFLED)
        self.assertEqual(sham_rl.fitted_backups, 40)
        self.assertEqual(real_rl.success.sum() + real_rl.failure.sum(), 5 * 1536)
        self.assertEqual(sham_rl.success.sum() + sham_rl.failure.sum(), 5 * 1536)
        self.assertEqual(sham_rl.diagnostic.sum(), 5 * 1536)
        self.assertEqual(BayesianControl.restore(sham_b.checkpoint())
                         .checkpoint(), sham_b.checkpoint())
        self.assertEqual(ModelBasedRL.restore(sham_rl.checkpoint())
                         .checkpoint(), sham_rl.checkpoint())

    def test_model_based_no_retained_belief_is_explicit_frozen_negative(self):
        with self.assertRaisesRegex(
                AssertionError, "RL_ABLATION_REQUIRES_FITTED_MODEL_BASED"):
            ModelBasedWithoutRetainedBelief(BayesianControl())
        trained = ModelBasedRL().fit(self.source)
        arm = ModelBasedWithoutRetainedBelief(trained)
        arm.begin_block()
        for ep in self.block:
            arm.update(ep)
            self.assertEqual(trained._local_success.sum(), 0)
            self.assertEqual(trained._local_failure.sum(), 0)
            self.assertEqual(trained._local_probe.sum(), 0)
        self.assertEqual(arm._position, 4)
        self.assertEqual(arm.checkpoint()["schema"],
                         "md35.rl-no-retained-law-belief-negative.v1")
        self.assertEqual(trained.fitted_episodes, 1536)


if __name__ == "__main__":
    unittest.main()
