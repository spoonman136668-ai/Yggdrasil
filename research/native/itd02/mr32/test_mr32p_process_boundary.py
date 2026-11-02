"""Hand-built MR32-P evaluator/policy process isolation tests; no cohort seeds."""
from __future__ import annotations

from dataclasses import replace
import json
import os
from unittest.mock import patch
import unittest

from counterfactual_shapley import shapley_q16_credits
from mr32p_evaluator import (
    ACTIVE, EVENTS, TOTAL, evaluate_all_coalitions, make_private_task,
    public_memory_records, public_policy_message, terminal_return, transition,
)
from mr32p_policy import initial_state
from mr32p_process import invoke_policy, PolicyProcessError


def run_policy(message: dict) -> dict:
    return invoke_policy(message)


class PolicyProcessBoundaryTests(unittest.TestCase):
    def setUp(self):
        # These are hand-built static fixtures, not preregistered cohort seeds.
        self.spec = make_private_task(37, 0, 2)
        self.message = public_policy_message(
            self.spec, "shapley", initial_state()
        )

    def test_policy_message_contains_only_public_allowlisted_fields(self):
        self.assertEqual(set(self.message), {
            "schema", "operation", "method", "public_items", "records", "state"
        })
        encoded = json.dumps(self.message, sort_keys=True)
        for forbidden in (
            "target_position", "initial_position", "role_weights",
            "coalition_values", "hidden_task_spec", "terminal_return",
        ):
            self.assertNotIn(forbidden, encoded)

    def test_policy_process_output_does_not_change_when_private_target_changes(self):
        altered_private = replace(
            self.spec,
            target_position=(self.spec.target_position + 1) % 11,
        )
        self.assertNotEqual(self.spec.target_position,
                            altered_private.target_position)
        left_message = public_policy_message(
            self.spec, "shapley", initial_state()
        )
        right_message = public_policy_message(
            altered_private, "shapley", initial_state()
        )
        self.assertEqual(left_message, right_message)
        left = run_policy(left_message)
        with patch.dict(os.environ, {"MR32P_HIDDEN_TARGET": "9"}):
            right = run_policy(right_message)
        left.pop("policy_cpu_ns")
        right.pop("policy_cpu_ns")
        self.assertEqual(left, right)

    def test_policy_rejects_hidden_target_injection(self):
        malicious = dict(self.message)
        malicious["target_position"] = self.spec.target_position
        with self.assertRaisesRegex(PolicyProcessError, "POLICY_MESSAGE_FIELDS"):
            run_policy(malicious)

    def test_policy_output_contains_only_public_action_and_use_receipts(self):
        output = run_policy(self.message)
        self.assertEqual(set(output), {
            "schema", "method", "selected_items", "actions",
            "public_trace", "use_receipts", "state_after_episode", "policy_cpu_ns", "policy_peak_rss_bytes",
        })
        self.assertEqual(len(output["actions"]), EVENTS)
        self.assertEqual(len(output["selected_items"]), ACTIVE)
        self.assertEqual(len(output["use_receipts"]), ACTIVE)
        self.assertEqual(output["state_after_episode"]["clock"], EVENTS)
        self.assertGreaterEqual(output["policy_cpu_ns"], 0)
        self.assertTrue(output["policy_peak_rss_bytes"] is None
                        or output["policy_peak_rss_bytes"] > 0)
        serialized = json.dumps(output, sort_keys=True)
        self.assertNotIn("target_position", serialized)
        self.assertNotIn("coalition_values", serialized)
        self.assertNotIn("terminal_return", serialized)

    def test_policy_update_rejects_preterminal_credit(self):
        result = run_policy(self.message)
        update = {
            "schema": "yggdrasil.mr32p.policy-message.v1",
            "operation": "update",
            "method": "shapley",
            "episode_terminal": False,
            "state": result["state_after_episode"],
            "use_receipts": result["use_receipts"],
            "credits_q16": [0] * ACTIVE,
        }
        with self.assertRaisesRegex(PolicyProcessError, "FEEDBACK_BEFORE_TERMINAL"):
            run_policy(update)

    def test_policy_update_rejects_coalition_table_or_hidden_target(self):
        result = run_policy(self.message)
        update = {
            "schema": "yggdrasil.mr32p.policy-message.v1",
            "operation": "update",
            "method": "shapley",
            "episode_terminal": True,
            "state": result["state_after_episode"],
            "use_receipts": result["use_receipts"],
            "credits_q16": [0] * ACTIVE,
            "coalition_values": {0: 0},
        }
        with self.assertRaisesRegex(PolicyProcessError, "LEARNER_MESSAGE_FIELDS"):
            run_policy(update)


class EvaluatorCoalitionTests(unittest.TestCase):
    def setUp(self):
        self.spec = make_private_task(41, 1, 3)
        self.records = {row["item_id"]: row for row in public_memory_records()}
        self.players = (0, 2, 4, 6, 8, 10, 12)

    def test_public_query_is_full_permutation_but_private_state_is_separate(self):
        self.assertEqual(len(self.spec.public_items), EVENTS)
        self.assertEqual(set(self.spec.public_items), set(range(TOTAL)))
        self.assertTrue(0 <= self.spec.initial_position < 11)
        self.assertTrue(0 <= self.spec.target_position < 11)
        public = public_policy_message(
            self.spec, "uniform_mc", initial_state()
        )
        self.assertNotIn("seed", public)
        self.assertNotIn("regime", public)
        self.assertNotIn("initial_position", public)
        self.assertNotIn("target_position", public)

    def test_exact_128_coalitions_repeat_from_same_initial_state(self):
        first = evaluate_all_coalitions(self.spec, self.players)
        second = evaluate_all_coalitions(self.spec, self.players)
        self.assertEqual(set(first), set(range(1 << ACTIVE)))
        self.assertEqual(first, second)
        self.assertEqual(len(first), 128)

    def test_empty_and_full_coalitions_match_explicit_rollouts(self):
        values = evaluate_all_coalitions(self.spec, self.players)
        fallback = {item: 0 for item in range(TOTAL)}
        full = dict(fallback)
        for item in self.players:
            full[item] = self.records[item]["proposed_action"]
        self.assertEqual(values[0], terminal_return(fallback, self.spec))
        self.assertEqual(values[(1 << ACTIVE) - 1],
                         terminal_return(full, self.spec))

    def test_all_coalition_replays_are_binary_and_shapley_efficient(self):
        values = evaluate_all_coalitions(self.spec, self.players)
        self.assertTrue(all(value in (0, 1) for value in values.values()))
        credits, _, delta = shapley_q16_credits(self.players, values)
        self.assertEqual(sum(credits),
                         (values[(1 << ACTIVE) - 1] - values[0]) * 65536)
        self.assertEqual(delta,
                         values[(1 << ACTIVE) - 1] - values[0])

    def test_noncohort_hand_fixtures_have_both_success_and_failure_coalitions(self):
        players = (0, 2, 4, 6, 8, 10, 12)
        hand_seeds = (37, 41, 43, 47, 53, 59, 61, 67)
        for index, seed in enumerate(hand_seeds):
            regime = index % 2
            spec = make_private_task(seed, regime, index % 3)
            values = evaluate_all_coalitions(spec, players)
            self.assertEqual(set(values.values()), {0, 1},
                             msg=f"degenerate hand fixture seed={seed} regime={regime}")

    def test_evaluator_rejects_unordered_or_duplicate_players(self):
        with self.assertRaisesRegex(ValueError, "COALITION_PLAYERS_NOT_SORTED"):
            evaluate_all_coalitions(self.spec, tuple(reversed(self.players)))
        with self.assertRaisesRegex(ValueError, "COALITION_PLAYERS_NOT_UNIQUE"):
            evaluate_all_coalitions(self.spec, (0, 2, 4, 6, 8, 10, 10))

    def test_transition_rejects_invalid_action_and_state(self):
        with self.assertRaisesRegex(ValueError, "WORLD_ACTION_RANGE"):
            transition(0, 0, 2, 0)
        with self.assertRaisesRegex(ValueError, "WORLD_POSITION_RANGE"):
            transition(11, 0, 1, 0)


if __name__ == "__main__":
    unittest.main()
