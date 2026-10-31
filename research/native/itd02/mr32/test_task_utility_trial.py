"""Focused regression tests for the MR32-M task-derived utility trial."""
from __future__ import annotations

import unittest

from learned_memory_allocator import LearnedMemoryAllocator
from task_utility_trial import (
    FIT_SEEDS, TRANSFER_SEEDS, ACTIVE, TOTAL, _event, _fit,
    _fixed_sets, _metadata, _permute, _query_order, _representation,
    _bootstrap_lower, _paired_memory_utility, _score_task_action,
    _stored_guess, InteractionBayesianUtility, TaskEvent, run,
)


class TaskUtilityTrialTests(unittest.TestCase):
    def test_frozen_fit_and_transfer_cohorts_are_disjoint(self):
        self.assertEqual(len(FIT_SEEDS), 8)
        self.assertEqual(len(TRANSFER_SEEDS), 16)
        self.assertEqual(len(set(FIT_SEEDS)), 8)
        self.assertEqual(len(set(TRANSFER_SEEDS)), 16)
        self.assertFalse(set(FIT_SEEDS) & set(TRANSFER_SEEDS))

    def test_task_events_and_queries_are_reproducible(self):
        a = _event(1009, 0, 2, 4, 7)
        b = _event(1009, 0, 2, 4, 7)
        self.assertEqual(a, b)
        self.assertEqual(_query_order(1009, 0, 2),
                         _query_order(1009, 0, 2))
        self.assertIn(a.task_return, (-1.0, 1.0))

    def test_task_utility_is_paired_return_against_no_memory_abstention(self):
        event = TaskEvent(item=3, guessed_action=1, correct_action=1)
        self.assertEqual(_score_task_action(event, None), 0.0)
        self.assertEqual(_score_task_action(event, 1), 1.0)
        self.assertEqual(_score_task_action(event, 0), -1.0)
        self.assertEqual(_paired_memory_utility(event, 1), 1.0)
        self.assertEqual(_paired_memory_utility(event, 0), -1.0)

    def test_task_truth_is_conditioned_on_the_action_stored_in_memory(self):
        for seed in FIT_SEEDS[:2]:
            for regime in (0, 1):
                for item in range(TOTAL):
                    event = _event(seed, regime, 3, 7, item)
                    self.assertEqual(event.guessed_action,
                                     _stored_guess(seed, regime, item))

    def test_all_methods_use_seven_of_sixteen_memory_records(self):
        fixed = _fixed_sets(1009, 0, _permute(1009, 0))
        self.assertEqual(set(fixed), {"random", "fixed_recency", "evidence_only"})
        for active in fixed.values():
            self.assertEqual(len(active), ACTIVE)
            self.assertTrue(active.issubset(set(range(TOTAL))))

    def test_public_memory_representation_has_fixed_dimensions(self):
        for i in range(TOTAL):
            rep = _representation(i, 101, 0)
            self.assertEqual(len(rep), 16)
            self.assertTrue(all(-1.0 <= x <= 1.0 for x in rep))
            self.assertEqual(rep[0], -1.0 if rep[0] < 0 else 1.0)
            evidence, error, contradiction = _metadata(i)
            self.assertGreaterEqual(evidence, 1)
            self.assertTrue(0.0 <= error <= 1.0)
            self.assertTrue(0.0 <= contradiction <= 1.0)

    def test_allocator_cannot_learn_from_unselected_memory(self):
        model = LearnedMemoryAllocator()
        model.insert("item", [1.0] + [0.0] * 15)
        with self.assertRaisesRegex(RuntimeError, "NO_PENDING"):
            model.observe_task_outcome("item", 1.0)
        self.assertEqual(model.feedback_count, 0)

    def test_bayesian_checkpoint_cold_restore_preserves_next_prediction(self):
        model = InteractionBayesianUtility()
        model.insert_records(101, 0, _permute(101, 0))
        before = {record.item: model.predict(record) for record in model.records}
        snapshot = model.snapshot()
        restored = InteractionBayesianUtility.restore(snapshot)
        after = {record.item: restored.predict(record) for record in restored.records}
        self.assertEqual(before, after)
        self.assertEqual(model.active_items(), restored.active_items())
        self.assertEqual(snapshot, restored.snapshot())

    def test_bayesian_checkpoint_tampering_fails_closed(self):
        model = InteractionBayesianUtility()
        model.insert_records(101, 0, _permute(101, 0))
        damaged = model.snapshot().replace(b'"noise":0.25', b'"noise":0.5')
        with self.assertRaisesRegex(ValueError, "HASH_MISMATCH"):
            InteractionBayesianUtility.restore(damaged)

    def test_fit_uses_only_frozen_fit_events(self):
        weights, bayes, receipt = _fit()
        self.assertEqual(len(weights), 6)
        self.assertTrue(all(abs(w) <= 4.0 for w in weights))
        self.assertEqual(receipt["fit_seeds"], list(FIT_SEEDS))
        self.assertEqual(receipt["fit_episodes"], 48)
        self.assertEqual(receipt["fit_event_count"], 48 * 16)
        self.assertEqual(len(receipt["fit_episode_receipts"]), 48)
        self.assertEqual(len(receipt["fit_feedback_receipts"]),
                         receipt["fit_feedback_count_h"]
                         + receipt["fit_feedback_count_bayesian"])
        self.assertEqual(receipt["bayes_feedback_count"], bayes.feedback_count)
        self.assertNotIn("transfer_event_sha256", receipt)

    def test_paired_bootstrap_is_deterministic(self):
        values = [0.1, -0.1, 0.2, 0.3, -0.2, 0.4, 0.1, 0.0]
        self.assertEqual(_bootstrap_lower(values), _bootstrap_lower(values))

    def test_transfer_is_feedback_free_and_cluster_balanced(self):
        result = run()
        transfer = result["transfer"]
        self.assertEqual(transfer["feedback_events_h"], 0)
        self.assertEqual(transfer["feedback_events_bayesian"], 0)
        self.assertEqual(transfer["event_count"], 16 * 4 * 16)
        self.assertEqual(transfer["seed_cluster_count"], 16)
        self.assertEqual(len(transfer["per_seed"]), 16)
        self.assertEqual(len(transfer["per_episode_receipts"]), 64)
        self.assertTrue(all(row["task_count"] == 16
                            and row["transfer_feedback_events"] == 0
                            for row in transfer["per_episode_receipts"]))
        self.assertEqual(transfer["regime_detail"]["0"]["seed_clusters"], 8)
        self.assertEqual(transfer["regime_detail"]["1"]["seed_clusters"], 8)
        self.assertEqual(result["classification"],
                         "CONTROLLED_TASK_FIXTURE_DEVELOPMENT_NOT_SCIENTIFIC_ADMISSION")

    def test_output_reports_all_preregistered_comparators_and_resources(self):
        result = run()
        means = result["transfer"]["method_mean_task_return"]
        self.assertEqual(set(means), {
            "random", "fixed_recency", "evidence_only",
            "mr32_h_learned", "interaction_bayesian"
        })
        self.assertGreater(result["resource_diagnostics"]["process_cpu_ns"], 0)
        self.assertGreater(result["resource_diagnostics"]["tracemalloc_peak_bytes"], 0)
        self.assertIn("process_peak_rss_bytes", result["resource_diagnostics"])
        self.assertIn("process_peak_rss_method", result["resource_diagnostics"])
        self.assertEqual(set(result["resource_diagnostics"]["selector_state_bytes_mean"]), set(means))
        self.assertIn("all-in resource parity", result["resource_diagnostics"]["selector_state_scope"])
        self.assertIn("delta_at_least_0_02", result["falsifiers"])


if __name__ == "__main__":
    unittest.main()
