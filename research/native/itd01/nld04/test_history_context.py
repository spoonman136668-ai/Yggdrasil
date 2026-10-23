"""NLD04 delayed-history context inference and source-bound negatives."""
import copy
import unittest

from history_context import (PROBES, SCORED, SEED, infer_from_public_history, run)


class NativeHistoryContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run()

    def test_only_old_public_development_first_use(self):
        r = self.result
        self.assertEqual(r["source_first_use"], "REUSED_ALREADY_PUBLIC_R9_DEVELOPMENT_SEED_3")
        self.assertFalse(r["protected_first_use_consumed"])
        self.assertFalse(r["original_r9_101_211_307_replayed"])
        self.assertEqual(r["ckb_scientific_admission"], "NOT_OBSERVED")
        with self.assertRaisesRegex(ValueError, "ONLY_PREVIOUSLY_EXPOSED"):
            run(101)

    def test_delayed_public_information_budget_and_frozen_models(self):
        r = self.result
        self.assertEqual(r["public_probe_count_per_family"], PROBES)
        self.assertEqual(r["scored_steps_per_family"], SCORED)
        self.assertEqual(set(r["equal_public_delayed_fit_feedback"].values()), {256})
        self.assertEqual(len(r["equal_public_delayed_fit_feedback"]), 6)
        self.assertEqual(r["native_cold_restart"]["matching_two_task_32_decisions"], 32)
        self.assertTrue(r["native_cold_restart"]["cold_restore_exact"])

    def test_two_original_public_roles_and_no_scoring_updates(self):
        for row, expected in ((self.result["eval_a"], "DEV_A_RETAINED"),
                              (self.result["eval_b"], "VALID_B")):
            self.assertEqual(row["source_role_for_private_audit_only"], expected)
            self.assertEqual(row["public_role_steps"], 64)
            self.assertEqual(row["unscored_public_probe_cost"], 8)
            self.assertEqual(row["public_feedback_delay"], 2)
            self.assertEqual(row["scored_steps"], 56)
            self.assertEqual(row["score_updates"], 0)
            self.assertEqual(len(row["probe_public_history_sha256"]), 64)
            self.assertEqual(len(row["context_selection"]), 6)
            for key, num in row["correct_counts_over_56"].items():
                self.assertIs(type(num), int, key)
                self.assertTrue(0 <= num <= SCORED, key)
            self.assertEqual(len(row["selection_correctness_evaluator_only"]), 6)

    def test_public_history_only_no_task_id_in_selector_signature(self):
        import inspect
        p = inspect.signature(infer_from_public_history)
        self.assertEqual(list(p.parameters), ["model", "transcript"])
        r = self.result
        self.assertEqual(r["context_mechanism"],
                         "INTEGER_MISMATCH_SELECTOR_USING_FROZEN_LEARNED_CONTEXT_POLICIES")
        self.assertFalse(r["learned_context_representation"])

    def test_probe_count_fail_closed_and_delayed_results_never_replayed(self):
        class NeutralModel:
            def choose(self, sensors, cue):
                return 0
        probe = {"token": "p0", "sensors": [True, False, False, True],
                 "action": 0, "success": True, "action_tick": 0,
                 "feedback_tick": 2}
        with self.assertRaisesRegex(ValueError, "EXACT_EIGHT"):
            infer_from_public_history(NeutralModel(), [probe])
        events = []
        for i in range(8):
            v = dict(probe, token="p" + str(i), action_tick=i, feedback_tick=i+2)
            events.append(v)
        x = infer_from_public_history(NeutralModel(), events)
        self.assertTrue(x["ambiguous_tie"])
        self.assertEqual(x["chosen_public_context"], -1)
        self.assertEqual(x["diagnostic_disagreements"], 0)
        early = copy.deepcopy(events)
        early[0]["feedback_tick"] = 1
        with self.assertRaisesRegex(ValueError, "TOKEN_OR_DELAY"):
            infer_from_public_history(NeutralModel(), early)
        duplicate = copy.deepcopy(events)
        duplicate[1]["token"] = duplicate[0]["token"]
        with self.assertRaisesRegex(ValueError, "TOKEN_OR_DELAY"):
            infer_from_public_history(NeutralModel(), duplicate)

    def test_explicit_oracle_and_equal_information_conventional_challengers(self):
        for row in (self.result["eval_a"], self.result["eval_b"]):
            counts = row["correct_counts_over_56"]
            self.assertIn("supplied_context_native_ORACLE", counts)
            self.assertIn("erased_context_native", counts)
            self.assertIn("always_A_context_native", counts)
            self.assertIn("trained-cue-perceptron", counts)
            self.assertIn("trained-cue-episodic", counts)
            self.assertIn("native-shared-cue-blind", counts)
            for hypothesis in row["context_selection"].values():
                self.assertEqual(hypothesis["diagnostic_delayed_outcomes"], 8)
                self.assertIn(hypothesis["chosen_public_context"], (-1, 1))
                self.assertEqual(len(hypothesis["mismatch_scores_A_B"]), 2)

    def test_scientific_boundary_not_unfamiliar_transfer(self):
        r = self.result
        self.assertEqual(r["unfamiliar_transfer"],
                         "NOT_TESTED_ORIGINAL_R9_C_NEGATIVE_PRESERVED")
        self.assertEqual(r["causal_composition"],
                         "NOT_TESTED_TWO_PREDECLARED_TASK_HYPOTHESES")
        self.assertFalse(r["per_model_cpu_rss_parity"])
        self.assertFalse(r["new_family_generation"])
        self.assertEqual(r["disposition"],
                         "NLD04_PUBLIC_HISTORY_DEV_OBSERVATION_RETAIN_POSITIVE_AND_NEGATIVE")


if __name__ == "__main__":
    unittest.main()
