"""NLD01 smoke tests preserve research distinction between engineering and science."""
from __future__ import annotations
import pathlib
import unittest
from learning_cycle import (
    SCHEMA, SMOKE_SEED, FIT_PER_FAMILY, EVAL_PER_ROLE,
    smoke_cycle, cold_restart_and_decisions, paired_state_ablation, parameter_hash
)
import sys

R9 = pathlib.Path(__file__).resolve().parents[1] / "r9"
sys.path.insert(0, str(R9))
from action_cells import LocalActionColony, train_equal_public_interventions


class NativeLearningCycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.x = smoke_cycle()

    def test_existing_smoke_only_and_no_source_first_use(self):
        x = self.x
        self.assertEqual(x["schema"], SCHEMA)
        self.assertEqual(x["public_smoke_seed"], SMOKE_SEED)
        self.assertEqual(x["fit_per_public_family"], FIT_PER_FAMILY)
        self.assertEqual(x["eval_per_public_role"], EVAL_PER_ROLE)
        self.assertFalse(x["independent_source_first_use"])
        self.assertFalse(x["original_r9_seeds_101_211_307_replayed"])
        self.assertFalse(x["original_H1_H2_accessed"])
        self.assertEqual(x["ckb_admission"], "NOT_OBSERVED")
        with self.assertRaisesRegex(ValueError, "ONLY_EXISTING_PUBLIC"):
            smoke_cycle(101)

    def test_all_fitted_arms_equal_public_delayed_events(self):
        x = self.x
        self.assertTrue(x["fitted_arms_equal_public_delayed_feedback"])
        self.assertEqual(set(x["fitted_arm_update_counts"].values()),
                         {FIT_PER_FAMILY * 2})
        self.assertEqual(len(x["fit_public_traces"]), 2)
        for receipt in x["fit_public_traces"]:
            self.assertEqual(receipt["public_fit_interactions"], FIT_PER_FAMILY)
            self.assertEqual(receipt["public_delayed_feedback"], FIT_PER_FAMILY)
            self.assertEqual(len(receipt["public_intervention_trace_sha256"]), 64)

    def test_decision_relevant_native_state_and_cold_persistence(self):
        x = self.x
        self.assertTrue(x["native_state_changed_vs_initial"])
        self.assertTrue(x["native_state_changed_during_b_fit"])
        self.assertGreater(x["native_weight_changes"], 0)
        self.assertTrue(x["cold_after_a"]["cold_restore_exact"])
        self.assertTrue(x["cold_after_b"]["cold_restore_exact"])
        self.assertEqual(x["cold_after_a"]["matching_public_decisions"], 32)
        self.assertEqual(x["cold_after_b"]["matching_public_decisions"], 32)
        self.assertLess(x["cold_after_b"]["checkpoint_bytes"], 32768)

    def test_all_evaluations_are_readonly_legal_and_controlled(self):
        x = self.x
        self.assertEqual(set(x["role_scores"]),
                         {"a_untrained", "a_trained", "a_after_b", "b_trained"})
        for role in x["role_scores"].values():
            self.assertEqual(role["evaluation_episodes"], EVAL_PER_ROLE)
            self.assertEqual(role["feedback_parameter_updates"], 0)
            self.assertTrue(role["all_actions_legal"])
            self.assertEqual(len(role["evaluation_role_sha256"]), 64)
            for k in ("native_accuracy", "pairwise_accuracy",
                      "episodic_accuracy", "current_only_accuracy",
                      "erased_native_accuracy"):
                self.assertGreaterEqual(role[k], 0)
                self.assertLessEqual(role[k], 1)

    def test_separate_axes_and_no_premature_transfer_victory(self):
        x = self.x
        self.assertEqual(x["causal_composition"],
                         "NOT_TESTED_KNOWN_FAMILY_ID_AND_PAIR_FEATURES")
        self.assertEqual(x["unfamiliar_transfer"],
                         "NOT_TESTED_ORIGINAL_R9_ZERO_SHOT_NO_GO")
        self.assertEqual(x["native_better_than_trained_conventional_baselines"],
                         "NOT_CLAIMED")
        self.assertFalse(x["isolated_per_model_cpu_rss_parity"])
        self.assertIn(x["disposition"],
                      {"NLD01_NATIVE_SMOKE_POSITIVE_NARROW",
                       "NLD01_NATIVE_SMOKE_NO_GO_RETAIN_NEGATIVE"})
        # No hidden target, label or source-family rule imported by this runner.
        code = (pathlib.Path(__file__).parent / "learning_cycle.py").read_text()
        self.assertNotIn("from action_cells import hidden_target", code)
        self.assertNotIn("FIT_C", code)

    def test_cold_restoration_refuses_tampering_without_relearning(self):
        model = LocalActionColony()
        train_equal_public_interventions([model], SMOKE_SEED, "FIT_A", "A", 12)
        snap = model.save()
        restored = LocalActionColony.restore(snap)
        self.assertEqual(parameter_hash(model), parameter_hash(restored))
        report = cold_restart_and_decisions(model)
        self.assertTrue(report["cold_restore_exact"])
        self.assertEqual(sum(paired_state_ablation(model).values()) >= 0, True)
        bad = bytearray(snap)
        bad[-5] ^= 1
        with self.assertRaises(ValueError):
            LocalActionColony.restore(bytes(bad))


if __name__ == "__main__":
    unittest.main()
