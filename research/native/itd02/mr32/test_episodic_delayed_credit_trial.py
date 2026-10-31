"""Focused MR32-O tests: hidden multi-step returns, delayed credit and custody."""
from __future__ import annotations

import json
import unittest

from episodic_delayed_credit_trial import (
    ACTIVE, EVENTS, FIT_SEEDS, GOALS, LEARNED, METHODS, Q, RETAINED,
    TOTAL, TRANSFER_SEEDS, UseReceipt, PolicyState, _canonical_sha,
    base_features, correct_probability_bp, make_episode_spec,
    no_memory_return, proposal_action, run, terminal_return,
)


class EpisodicTaskTests(unittest.TestCase):
    def test_frozen_cohorts_are_disjoint_and_balanced(self):
        self.assertEqual(len(FIT_SEEDS), 16)
        self.assertEqual(len(TRANSFER_SEEDS), 32)
        self.assertEqual(len(set(FIT_SEEDS)), 16)
        self.assertEqual(len(set(TRANSFER_SEEDS)), 32)
        self.assertFalse(set(FIT_SEEDS) & set(TRANSFER_SEEDS))
        self.assertEqual(len(FIT_SEEDS) // 2, 8)
        self.assertEqual(len(TRANSFER_SEEDS) // 2, 16)

    def test_task_generator_is_deterministic_and_public_stream_has_no_repeats(self):
        left = make_episode_spec(1009, 0, 3)
        right = make_episode_spec(1009, 0, 3)
        self.assertEqual(left, right)
        self.assertEqual(len(left.public_items), EVENTS)
        self.assertEqual(len(set(left.public_items)), EVENTS)
        self.assertEqual(len(left.goal_positions), GOALS)
        self.assertEqual(len(set(left.goal_positions)), GOALS)
        self.assertEqual(left.hidden_sha256, right.hidden_sha256)

    def test_regime_reliability_is_bounded_and_nonidentical(self):
        for item in range(TOTAL):
            p0 = correct_probability_bp(item, 0)
            p1 = correct_probability_bp(item, 1)
            self.assertTrue(2000 <= p0 <= 9500)
            self.assertTrue(2000 <= p1 <= 9500)
        self.assertTrue(any(correct_probability_bp(i, 0) !=
                            correct_probability_bp(i, 1)
                            for i in range(TOTAL)))

    def test_terminal_success_requires_every_hidden_goal_action(self):
        spec = make_episode_spec(1013, 1, 2)
        actions = [0] * EVENTS
        for position in spec.goal_positions:
            actions[position] = spec.required_actions[position]
        self.assertEqual(terminal_return(actions, spec), 1)
        self.assertEqual(no_memory_return(spec),
                         terminal_return([0] * EVENTS, spec))
        broken = list(actions)
        goal_position = spec.goal_positions[0]
        broken[goal_position] = 1 - broken[goal_position]
        self.assertEqual(terminal_return(broken, spec), 0)

    def test_invalid_action_stream_rejected(self):
        spec = make_episode_spec(1013, 0, 0)
        with self.assertRaisesRegex(ValueError, "ACTION_STREAM_INVALID"):
            terminal_return([0] * (EVENTS - 1), spec)
        bad = [0] * EVENTS
        bad[0] = 2
        with self.assertRaisesRegex(ValueError, "ACTION_STREAM_INVALID"):
            terminal_return(bad, spec)


class DelayedCreditTests(unittest.TestCase):
    def test_use_time_features_are_immutable_before_episode_terminal(self):
        state = PolicyState.create("deca_q16")
        spec = make_episode_spec(1031, 0, 4)
        actions, uses, events = state.act_episode(
            spec.public_items, spec.seed, spec.regime, spec.episode
        )
        self.assertEqual(state.feedback_events, 0)
        self.assertEqual(state.weights, [0] * 6)
        self.assertEqual(len(events), EVENTS)
        self.assertTrue(all(len(use.features) == 6 for use in uses))
        for use in uses:
            self.assertEqual(use.features[0], Q)
            self.assertEqual(use.action, proposal_action(use.item))
            self.assertEqual(use.step, next(e["step"] for e in events
                                           if e["item"] == use.item))
        result = terminal_return(actions, spec)
        delta = result - no_memory_return(spec)
        feedback = state.apply_terminal_feedback(uses, delta)
        self.assertEqual(state.feedback_events, len(uses))
        self.assertEqual(len(feedback), len(uses))
        self.assertTrue(any(state.weights))

    def test_no_memory_or_unselected_record_receives_episodic_credit(self):
        state = PolicyState.create("uniform_mc")
        uses = [
            UseReceipt(2, 3, proposal_action(3), base_features(3, 0, -1, 0)),
            UseReceipt(9, 11, proposal_action(11), base_features(11, 0, -1, 0)),
        ]
        credits = state.allocate_terminal_credit(uses, Q)
        self.assertEqual(sum(credits), Q)
        receipts = state.apply_terminal_feedback(uses, 1)
        self.assertEqual(len(receipts), 2)
        self.assertEqual(state.feedback_events, 2)
        self.assertEqual(sum(state.uses), 0)  # only retrieval changes use counters

    def test_uniform_credit_is_conserved_even_with_integer_remainder(self):
        state = PolicyState.create("uniform_mc")
        uses = [
            UseReceipt(0, 0, proposal_action(0), base_features(0, 0, -1, 0)),
            UseReceipt(4, 4, proposal_action(4), base_features(4, 0, -1, 4)),
            UseReceipt(11, 11, proposal_action(11), base_features(11, 0, -1, 11)),
        ]
        credits = state.allocate_terminal_credit(uses, Q)
        self.assertEqual(sum(credits), Q)
        self.assertEqual(credits[-1], credits[0] + 1)
        self.assertLessEqual(max(credits) - min(credits), 1)

    def test_deca_trace_conserves_terminal_delta_and_prefers_recent_use(self):
        state = PolicyState.create("deca_q16")
        uses = [
            UseReceipt(0, 0, proposal_action(0), base_features(0, 0, -1, 0)),
            UseReceipt(5, 5, proposal_action(5), base_features(5, 0, -1, 5)),
            UseReceipt(11, 11, proposal_action(11), base_features(11, 0, -1, 11)),
        ]
        credits = state.allocate_terminal_credit(uses, Q)
        self.assertEqual(sum(credits), Q)
        self.assertGreater(credits[-1], credits[1])
        self.assertGreater(credits[1], credits[0])
        self.assertGreater(sum(credits), 0)

    def test_negative_terminal_delta_is_conserved(self):
        state = PolicyState.create("deca_q16")
        uses = [
            UseReceipt(1, 1, proposal_action(1), base_features(1, 0, -1, 1)),
            UseReceipt(10, 10, proposal_action(10), base_features(10, 0, -1, 10)),
        ]
        credits = state.allocate_terminal_credit(uses, -Q)
        self.assertEqual(sum(credits), -Q)
        self.assertLess(credits[-1], credits[0])

    def test_no_use_episode_produces_no_credit_receipt(self):
        state = PolicyState.create("deca_q16")
        self.assertEqual(state.allocate_terminal_credit([], Q), [])
        self.assertEqual(state.apply_terminal_feedback([], 1), [])
        self.assertEqual(state.feedback_events, 0)
        self.assertEqual(state.weights, [0] * 6)

    def test_checkpoint_restore_preserves_exact_state_for_learned_methods(self):
        for method in sorted(LEARNED):
            with self.subTest(method=method):
                state = PolicyState.create(method)
                spec = make_episode_spec(1051, 1, 1)
                actions, uses, _ = state.act_episode(
                    spec.public_items, spec.seed, spec.regime, spec.episode
                )
                state.apply_terminal_feedback(
                    uses, terminal_return(actions, spec) - no_memory_return(spec)
                )
                snapshot = state.snapshot()
                restored = PolicyState.restore(snapshot)
                self.assertEqual(restored.snapshot(), snapshot)
                self.assertEqual(restored.weights, state.weights)
                self.assertEqual(restored.uses, state.uses)
                self.assertEqual(restored.last_used, state.last_used)
                self.assertEqual(restored.clock, state.clock)
                self.assertEqual(restored.feedback_events, state.feedback_events)

    def test_checkpoint_tamper_is_rejected(self):
        state = PolicyState.create("deca_q16")
        raw = state.snapshot()
        damaged = raw.replace(b'"clock":0', b'"clock":1')
        with self.assertRaisesRegex(ValueError, "HASH_MISMATCH"):
            PolicyState.restore(damaged)

    def test_checkpoint_with_recency_beyond_clock_is_rejected_even_with_valid_hash(self):
        state = PolicyState.create("deca_q16")
        envelope = json.loads(state.snapshot().decode("utf-8"))
        payload = envelope["payload"]
        payload["last_used"][0] = 0
        envelope["sha256"] = _canonical_sha(payload)
        raw = json.dumps(envelope, sort_keys=True, separators=(",", ":")).encode()
        with self.assertRaisesRegex(ValueError, "RECENCY_RANGE"):
            PolicyState.restore(raw)

    def test_all_selectors_keep_exact_seven_of_sixteen_partition(self):
        spec = make_episode_spec(1061, 0, 0)
        for method in METHODS:
            with self.subTest(method=method):
                state = PolicyState.create(method)
                active = state.active_items(spec.seed, spec.regime, spec.episode)
                self.assertEqual(len(active), ACTIVE)
                self.assertEqual(active | (set(range(TOTAL)) - active),
                                 set(range(TOTAL)))
                self.assertEqual(len(set(range(TOTAL)) - active), RETAINED)


class FullTrialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run()

    def test_fit_and_transfer_receipt_counts_and_cohort_isolation(self):
        result = self.result
        self.assertEqual(result["fit"]["event_receipt_count"], 16 * 8 * 6)
        self.assertEqual(len(result["fit"]["episode_receipts"]), 16 * 8)
        self.assertEqual(result["transfer"]["event_receipt_count"], 32 * 8 * 6)
        self.assertEqual(len(result["transfer"]["episode_receipts"]), 32 * 8)
        self.assertEqual(len(result["transfer"]["cluster_receipts"]), 32)
        self.assertEqual(result["protocol"]["fit_seeds"], list(FIT_SEEDS))
        self.assertEqual(result["protocol"]["transfer_seeds"], list(TRANSFER_SEEDS))
        self.assertFalse(set(FIT_SEEDS) & set(TRANSFER_SEEDS))

    def test_no_transfer_feedback_and_terminal_use_receipts_reconcile(self):
        transfer = self.result["transfer"]
        self.assertEqual(transfer["feedback_events_applied"],
                         {method: 0 for method in METHODS})
        self.assertTrue(all(not episode["transfer_feedback_applied"]
                            for episode in transfer["episode_receipts"]))
        self.assertEqual(set(self.result["fit"]["feedback_counts"]), set(METHODS))
        for method in ("uniform_mc", "interaction", "deca_q16"):
            self.assertEqual(
                self.result["fit"]["feedback_counts"][method],
                sum(row["method"] == method
                    for row in self.result["fit"]["feedback_receipts"])
            )
        for episode in transfer["episode_receipts"]:
            for method in METHODS:
                self.assertEqual(len(episode["terminal_return"]), len(METHODS))
                self.assertEqual(
                    episode["delta_return"][method],
                    episode["terminal_return"][method] - episode["no_memory_return"]
                )

    def test_each_transfer_seed_cluster_cold_restores_fit_terminal_checkpoint(self):
        fit_sha = self.result["fit"]["checkpoint_sha256"]
        fit_weights = self.result["fit"]["checkpoint_sha256"]
        transfer = self.result["transfer"]
        self.assertEqual(transfer["cold_restore_cluster_count_by_method"],
                         {method: 32 for method in METHODS})
        self.assertTrue(all(value == 0
                            for value in transfer["feedback_events_applied"].values()))
        for cluster in transfer["cluster_receipts"]:
            self.assertEqual(cluster["episode_count"], 8)
            self.assertEqual(cluster["episodes_executed_after_restore"],
                             {method: 8 for method in METHODS})
            self.assertEqual(cluster["feedback_events_applied"],
                             {method: 0 for method in METHODS})
            self.assertEqual(cluster["cold_restore_checkpoint_sha256"], fit_sha)
            self.assertEqual(cluster["terminal_weights_sha256"],
                             cluster["fit_weights_sha256"])
        self.assertEqual(len(transfer["cluster_receipts"]), 32)

    def test_receipts_contain_only_sealed_hidden_spec_digests(self):
        for row in self.result["fit"]["episode_receipts"]:
            self.assertEqual(len(row["terminal_return"]), len(METHODS))
        # Each per-method FIT event binds the same hidden spec with a SHA, not
        # the hidden goal locations or required actions themselves.
        self.assertEqual(len(self.result["fit"]["event_sha256"]), 64)
        self.assertEqual(len(self.result["transfer"]["event_sha256"]), 64)

    def test_every_method_has_checkpoint_and_resource_accounting(self):
        result = self.result
        self.assertEqual(set(result["fit"]["checkpoint_sha256"]), set(METHODS))
        self.assertEqual(set(result["resource_diagnostics"]["checkpoint_bytes"]), set(METHODS))
        self.assertEqual(set(result["resource_diagnostics"]["per_method_cpu_ns_fit_plus_transfer"]),
                         set(METHODS))
        self.assertGreater(result["resource_diagnostics"]["process_cpu_ns"], 0)
        self.assertGreater(result["resource_diagnostics"]["process_wall_ns"], 0)
        self.assertGreater(result["resource_diagnostics"]["process_peak_rss_bytes"], 0)

    def test_frozen_signal_is_boolean_and_development_only(self):
        result = self.result
        self.assertIsInstance(result["development_signal"], bool)
        self.assertEqual(
            result["classification"],
            "CONTROLLED_MULTI_STEP_TASK_FIXTURE_DEVELOPMENT_ONLY"
        )
        self.assertTrue(all(isinstance(value, bool)
                            for value in result["falsifiers"].values()))
        self.assertEqual(set(result["transfer"]["method_mean_terminal_success"]), set(METHODS))


if __name__ == "__main__":
    unittest.main()
