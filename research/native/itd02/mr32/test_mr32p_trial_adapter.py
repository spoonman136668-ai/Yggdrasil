"""Hand-fixture integration tests for MR32-P runner adapters; no frozen cohorts."""
from __future__ import annotations

import unittest

from mr32p_evaluator import make_private_task
from mr32p_policy import initial_state
from mr32p_trial import (
    COMPARATORS, DELTA_THRESHOLD_Q16, LEARNED, METHODS, _episode_step,
    _frozen_margin_pass, restore_state, snapshot_state,
)


class TrialAdapterTests(unittest.TestCase):
    def setUp(self):
        self.spec = make_private_task(73, 0, 2)  # not a FIT/TRANSFER seed
        self.policy_cpu = {method: 0 for method in METHODS}
        self.policy_peak_rss = {method: 0 for method in METHODS}
        self.evaluator_cpu = {method: 0 for method in METHODS}
        self.credit_cpu = {method: 0 for method in METHODS}
        self.learner_update_calls = {method: 0 for method in METHODS}

    def test_frozen_margin_gate_checks_every_comparator(self):
        passing = {method: DELTA_THRESHOLD_Q16 for method in COMPARATORS}
        self.assertTrue(_frozen_margin_pass(passing))
        one_below = dict(passing)
        one_below[COMPARATORS[-1]] = DELTA_THRESHOLD_Q16 - 1
        self.assertFalse(_frozen_margin_pass(one_below))
        with self.assertRaisesRegex(ValueError, "COMPARATOR_DELTA_SET"):
            _frozen_margin_pass({COMPARATORS[0]: DELTA_THRESHOLD_Q16})

    def test_all_six_methods_complete_one_hand_fixture_episode(self):
        for method in METHODS:
            with self.subTest(method=method):
                next_state, receipt = _episode_step(
                    method, self.spec, initial_state(), True,
                    self.policy_cpu, self.policy_peak_rss,
                    self.evaluator_cpu, self.credit_cpu,
                    self.learner_update_calls
                )
                self.assertEqual(len(receipt["coalition_values"]), 128)
                self.assertEqual(len(receipt["selected_items"]), 7)
                self.assertEqual(len(receipt["use_receipts_by_item_id"]), 7)
                self.assertIn(receipt["terminal_return"], (0, 1))
                self.assertEqual(receipt["coalition_values"][0],
                                 receipt["no_memory_return"])
                self.assertEqual(receipt["coalition_values"][127],
                                 receipt["terminal_return"])
                self.assertFalse(receipt["transfer_feedback_applied"])
        self.assertEqual(self.learner_update_calls[method], 1)
        self.assertEqual(transfer_calls, {name: 0 for name in METHODS})
        self.assertEqual(self.learner_update_calls[method], 1)
        self.assertEqual(transfer_calls, {name: 0 for name in METHODS})
                if method in LEARNED:
                    self.assertEqual(receipt["credit_method"], method)
                    self.assertEqual(len(receipt["credits_q16_by_item_id"]), 7)
                    if method == "shapley":
                        self.assertEqual(len(receipt["shapley_exact_numerators_by_item_id"]), 7)
                        self.assertEqual(receipt["shapley_common_denominator"], 5040)
                        self.assertEqual(
                            sum(receipt["shapley_exact_numerators_by_item_id"]),
                            5040 * receipt["terminal_delta"]
                        )
                    else:
                        self.assertIsNone(receipt["shapley_exact_numerators_by_item_id"])
                    self.assertGreaterEqual(self.policy_cpu[method], 0)
                    self.assertGreaterEqual(self.credit_cpu[method], 0)
                    self.assertGreaterEqual(self.policy_peak_rss[method], 0)
                else:
                    self.assertIsNone(receipt["credit_method"])
                    self.assertEqual(receipt["credits_q16_by_item_id"], [])

    def test_shapley_and_uniform_episode_updates_conserve_terminal_delta(self):
        for method in ("uniform_mc", "shapley"):
            with self.subTest(method=method):
                _, receipt = _episode_step(
                    method, self.spec, initial_state(), True,
                    self.policy_cpu, self.policy_peak_rss,
                    self.evaluator_cpu, self.credit_cpu,
                    self.learner_update_calls
                )
                expected = (
                    receipt["terminal_return"] - receipt["no_memory_return"]
                ) * 65_536
                self.assertEqual(sum(receipt["credits_q16_by_item_id"]), expected)
                if method == "shapley":
                    self.assertEqual(sum(receipt["shapley_exact_numerators_by_item_id"]),
                                     5040 * (receipt["terminal_return"] - receipt["no_memory_return"]))

    def test_fit_checkpoint_round_trip_and_tamper_rejection(self):
        for method in METHODS:
            with self.subTest(method=method):
                raw = snapshot_state(initial_state())
                restored = restore_state(raw)
                self.assertEqual(snapshot_state(restored), raw)
                bad = raw.replace(b'"clock":0', b'"clock":1')
                with self.assertRaisesRegex(ValueError, "STATE_SNAPSHOT_HASH"):
                    restore_state(bad)

    def test_transfer_mode_never_updates_learned_weights(self):
        method = "shapley"
        state, _ = _episode_step(
            method, self.spec, initial_state(), True,
            self.policy_cpu, self.policy_peak_rss,
            self.evaluator_cpu, self.credit_cpu,
            self.learner_update_calls
        )
        fit_weights = list(state["weights"])
        transfer_calls = {name: 0 for name in METHODS}
        transfer_state, receipt = _episode_step(
            method, self.spec, restore_state(snapshot_state(state)), False,
            self.policy_cpu, self.policy_peak_rss,
            self.evaluator_cpu, self.credit_cpu, transfer_calls
        )
        self.assertEqual(transfer_state["weights"], fit_weights)
        self.assertIsNone(receipt["credit_method"])
        self.assertEqual(receipt["credits_q16_by_item_id"], [])
        self.assertFalse(receipt["transfer_feedback_applied"])


if __name__ == "__main__":
    unittest.main()
