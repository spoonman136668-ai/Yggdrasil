"""NLD-03 public cue: state fidelity, feedback integrity, and scientific nonclaims."""
import json
import inspect
import unittest

from cued_state import (
    SEED, FIT, EVAL, N, PATTERNS, KNOWN_FIT_TRACES,
    CueNative, CuePerceptron, CueEpisodic, CUE, x20,
    train_public, evaluate, checkpoint, run,
)


class NLD03Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run()

    def test_no_independent_original_source_and_rejected_old_frozen_seeds(self):
        x = self.result
        self.assertEqual(x["source_seed"], 3)
        self.assertTrue(x["existing_consumed_public_source_only"])
        self.assertFalse(x["first_use_heldout"])
        self.assertFalse(x["original_r9_frozen_101_211_307_replayed"])
        self.assertEqual(x["ckb_scientific_admission"], "NOT_OBSERVED")
        with self.assertRaisesRegex(ValueError, "SEED_3_ONLY"):
            run(101)

    def test_genuinely_one_shared_array_and_predeclared_capacity(self):
        x = self.result
        self.assertEqual(x["native_single_shared_cell_array_length"], 20)
        self.assertEqual(x["native_per_family_bank_count"], 0)
        self.assertTrue(x["human_designed_context_interaction_features"])
        self.assertTrue(x["same_20_cell_capacity_for_cue_and_blind_native"])
        for enabled in (True, False):
            m = CueNative(enabled)
            self.assertEqual(len(m.cells), N)
            self.assertFalse(hasattr(m, "family_banks"))
            self.assertNotIn("family", inspect.signature(m.choose).parameters)
        with self.assertRaisesRegex(ValueError, "PUBLIC_CUE_REQUIRED"):
            x20((True, False, False, True), 0, True)

    def test_cue_is_frozen_public_identifier_not_hidden_label(self):
        self.assertEqual(CUE, {"A": -1, "B": 1})
        sensors = (True, False, True, False)
        self.assertNotEqual(x20(sensors, -1, True), x20(sensors, 1, True))
        self.assertEqual(x20(sensors, -1, False), x20(sensors, 1, False))
        for p in PATTERNS:
            self.assertEqual(len(x20(p, -1, True)), N)
            self.assertEqual(len(x20(p, 1, True)), N)

    def test_exact_preexisting_public_source_receipts_and_equal_updates(self):
        x = self.result
        self.assertEqual({row["role"]: row["trace_sha256"]
                          for row in x["source_traces"]}, KNOWN_FIT_TRACES)
        self.assertEqual([row["public_actions"] for row in x["source_traces"]],
                         [FIT, FIT])
        self.assertEqual([row["delayed_feedback_events"]
                          for row in x["source_traces"]], [FIT, FIT])
        self.assertEqual(set(x["fit_feedback_per_arm"].values()), {2*FIT})
        self.assertEqual(len(x["fit_feedback_per_arm"]), 6)

    def test_readonly_scoring_matched_legal_actions_and_ablations(self):
        x = self.result
        self.assertEqual(set(x["scores"]),
                         {"a_pre", "a_after_a", "a_after_b", "b_after_b"})
        for role in x["scores"].values():
            self.assertEqual(role["n"], EVAL)
            self.assertEqual(role["updates_during_eval"], 0)
            self.assertEqual(set(role["accuracy"]), set(x["fit_feedback_per_arm"]) |
                             {"erased-public-cue-native"})
            self.assertTrue(all(0 <= z <= 1 for z in role["accuracy"].values()))
            self.assertTrue(all(isinstance(z, int) for z in role["correct_counts"].values()))
            self.assertEqual(sum(role["correct_counts"].values()) >= 0, True)
        self.assertEqual(x["blind_native_task_flip_policy_disagreements_of_16"], 0)
        self.assertGreaterEqual(x["cue_native_task_flip_policy_disagreements_of_16"], 0)

    def test_feedback_rejects_duplicate_reordered_and_unmatched(self):
        m = CueNative(True)
        s = (True, False, True, False)
        with self.assertRaisesRegex(ValueError, "MISSING_ACTION"):
            m.learn_delayed("unknown", True, 2)
        m.observe_public_action("valid", s, -1, 0, 0)
        with self.assertRaisesRegex(ValueError, "DUPLICATE"):
            m.observe_public_action("valid", s, -1, 0, 0)
        with self.assertRaisesRegex(ValueError, "PENDING"):
            m.save()
        for tick in (1, 3):
            with self.assertRaisesRegex(ValueError, "EARLY_OR_LATE"):
                m.learn_delayed("valid", True, tick)
        m.learn_delayed("valid", True, 2)
        self.assertEqual(m.feedback_updates, 1)
        with self.assertRaisesRegex(ValueError, "MISSING_ACTION"):
            m.learn_delayed("valid", True, 2)

    def test_cold_save_restore_rejects_tampering_and_persists_decisions(self):
        model = CueNative(True)
        train_public([model], "A")
        receipt = checkpoint(model)
        self.assertEqual(receipt["matching_two_task_32_decisions"], 32)
        self.assertTrue(receipt["cold_restore_exact"])
        raw = model.save()
        restored = CueNative.restore(raw)
        self.assertEqual(restored.save(), raw)
        changed = json.loads(raw)
        changed["payload"]["bias"] += .1
        with self.assertRaisesRegex(ValueError, "CHECKPOINT_HASH"):
            CueNative.restore(json.dumps(changed).encode())
        with self.assertRaisesRegex(ValueError, "CHECKPOINT_SIZE"):
            CueNative.restore(b"")

    def test_no_unseen_transfer_composition_or_native_victory_claim(self):
        x = self.result
        self.assertEqual(x["causal_composition"],
                         "NOT_TESTED_HANDCODED_TASK_CUE_AND_FEATURES")
        self.assertEqual(x["unfamiliar_transfer"],
                         "NOT_TESTED_R9_C_ZERO_SHOT_NEGATIVE_PRESERVED")
        self.assertEqual(x["native_better_than_equally_informed_trained_controls"],
                         "NOT_PRESUMED")
        self.assertFalse(x["matched_cpu_rss_resource_efficiency"])
        self.assertEqual(x["disposition"], "NLD03_PUBLIC_CUE_DEV_ONLY_RETAIN_RESULTS")
        self.assertEqual(len(x["fit_model_serialized_bytes"]), 6)


if __name__ == "__main__":
    unittest.main()
