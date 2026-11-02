"""Hand-built MR32-P streaming policy/evaluator isolation tests; no cohort seeds."""
from __future__ import annotations

from dataclasses import replace
import json
import os
from unittest.mock import patch
import unittest

from counterfactual_shapley import shapley_q16_credits
from mr32p_evaluator import (
    ACTIVE, EVENTS, TOTAL, evaluate_all_coalitions, make_private_task,
    public_memory_records, public_policy_begin_message,
    public_policy_step_message, terminal_return, transition,
)
from mr32p_policy import initial_state
from mr32p_process import PolicyProcessError, PolicySession, invoke_policy


def run_policy_episode(spec, method="shapley", policy_nonce=991):
    """Send only one cue per request to a persistent policy process."""
    actions = []
    selected = None
    use_receipts = []
    step_trace = []
    with PolicySession(timeout_seconds=30) as session:
        begin = session.request(public_policy_begin_message(
            method, initial_state(), policy_nonce
        ))
        selected = begin["selected_items"]
        state = begin["state"]
        for step, item in enumerate(spec.public_items):
            message = public_policy_step_message(
                method, step, item, selected, state
            )
            response = session.request(message)
            actions.append(response["action"])
            state = response["state"]
            step_trace.append({
                "step": response["step"], "item_id": response["item_id"],
                "selected": response["selected"], "action": response["action"],
            })
            if response["use_receipt"] is not None:
                use_receipts.append(response["use_receipt"])
    return {
        "selected_items": selected,
        "actions": actions,
        "step_trace": step_trace,
        "use_receipts": use_receipts,
        "state": state,
    }


def deterministic_policy_view(result: dict) -> dict:
    """Remove explicitly nondeterministic timing/RSS measurements."""
    return json.loads(json.dumps(result, sort_keys=True))


class PolicyProcessBoundaryTests(unittest.TestCase):
    def setUp(self):
        # Static hand fixture only; not in the frozen MR32-P cohorts.
        self.spec = make_private_task(37, 0, 2)

    def test_begin_message_has_no_future_query_or_evaluator_fields(self):
        message = public_policy_begin_message("shapley", initial_state(), 991)
        self.assertEqual(set(message), {
            "schema", "operation", "method", "records", "state", "policy_nonce"
        })
        encoded = json.dumps(message, sort_keys=True)
        for forbidden in (
            "public_items", "target_position", "initial_position",
            "role_weights", "coalition_values", "terminal_return",
            "seed", "regime",
        ):
            self.assertNotIn(forbidden, encoded)

    def test_step_message_contains_only_the_current_public_cue(self):
        message = public_policy_step_message(
            "shapley", 4, self.spec.public_items[4],
            [0, 1, 2, 3, 4, 5, 6], initial_state()
        )
        self.assertEqual(set(message), {
            "schema", "operation", "method", "step", "item_id",
            "selected_items", "record", "state",
        })
        self.assertEqual(message["step"], 4)
        self.assertEqual(message["item_id"], self.spec.public_items[4])
        self.assertNotIn("public_items", message)
        self.assertNotIn("future_items", message)
        self.assertNotIn("target_position", message)

    def test_policy_trace_is_invariant_to_private_target_change(self):
        altered_private = replace(
            self.spec,
            target_position=(self.spec.target_position + 1) % 11,
        )
        self.assertNotEqual(self.spec.target_position,
                            altered_private.target_position)
        left = run_policy_episode(self.spec, "shapley", 991)
        right = run_policy_episode(altered_private, "shapley", 991)
        self.assertEqual(deterministic_policy_view(left),
                         deterministic_policy_view(right))

    def test_sanitized_process_environment_does_not_inherit_hidden_target(self):
        with patch.dict(os.environ, {"MR32P_HIDDEN_TARGET": "9"}):
            result = run_policy_episode(self.spec, "shapley", 992)
        self.assertEqual(len(result["actions"]), EVENTS)
        self.assertEqual(len(result["use_receipts"]), ACTIVE)

    def test_policy_rejects_hidden_target_injection_at_episode_begin(self):
        message = public_policy_begin_message("shapley", initial_state(), 991)
        message["target_position"] = self.spec.target_position
        with PolicySession(timeout_seconds=30) as session:
            with self.assertRaisesRegex(PolicyProcessError, "POLICY_BEGIN_FIELDS"):
                session.request(message)

    def test_policy_rejects_future_query_injection_at_step(self):
        begin = public_policy_begin_message("shapley", initial_state(), 993)
        with PolicySession(timeout_seconds=30) as session:
            begun = session.request(begin)
            state = begun["state"]
            message = public_policy_step_message(
                "shapley", 0, self.spec.public_items[0],
                begun["selected_items"], state
            )
            message["future_items"] = list(self.spec.public_items[1:])
            with self.assertRaisesRegex(PolicyProcessError, "POLICY_STEP_FIELDS"):
                session.request(message)

    def test_policy_outputs_only_current_actions_and_use_receipts(self):
        result = run_policy_episode(self.spec, "shapley", 994)
        self.assertEqual(len(result["actions"]), EVENTS)
        self.assertEqual(len(result["selected_items"]), ACTIVE)
        self.assertEqual(len(result["use_receipts"]), ACTIVE)
        self.assertEqual(result["state"]["clock"], EVENTS)
        for trace in result["step_trace"]:
            self.assertEqual(set(trace), {"step", "item_id", "selected", "action"})

    def test_policy_update_rejects_preterminal_credit(self):
        result = run_policy_episode(self.spec, "shapley", 995)
        update = {
            "schema": "yggdrasil.mr32p.policy-message.v1",
            "operation": "update",
            "method": "shapley",
            "episode_terminal": False,
            "state": result["state"],
            "use_receipts": sorted(
                result["use_receipts"], key=lambda row: row["item_id"]
            ),
            "credits_q16": [0] * ACTIVE,
        }
        with self.assertRaisesRegex(PolicyProcessError, "FEEDBACK_BEFORE_TERMINAL"):
            invoke_policy(update)

    def test_policy_update_rejects_coalition_table_or_hidden_target(self):
        result = run_policy_episode(self.spec, "shapley", 996)
        update = {
            "schema": "yggdrasil.mr32p.policy-message.v1",
            "operation": "update",
            "method": "shapley",
            "episode_terminal": True,
            "state": result["state"],
            "use_receipts": sorted(
                result["use_receipts"], key=lambda row: row["item_id"]
            ),
            "credits_q16": [0] * ACTIVE,
            "coalition_values": {0: 0},
        }
        with self.assertRaisesRegex(PolicyProcessError, "LEARNER_MESSAGE_FIELDS"):
            invoke_policy(update)


class EvaluatorCoalitionTests(unittest.TestCase):
    def setUp(self):
        self.spec = make_private_task(41, 1, 3)
        self.records = {row["item_id"]: row for row in public_memory_records()}
        self.players = (0, 2, 4, 6, 8, 10, 12)

    def test_task_stream_is_full_permutation_but_not_passed_at_begin(self):
        self.assertEqual(len(self.spec.public_items), EVENTS)
        self.assertEqual(set(self.spec.public_items), set(range(TOTAL)))
        begin = public_policy_begin_message("uniform_mc", initial_state(), 997)
        self.assertNotIn("seed", begin)
        self.assertNotIn("regime", begin)
        self.assertNotIn("public_items", begin)
        self.assertNotIn("initial_position", begin)
        self.assertNotIn("target_position", begin)

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
                         (values[(1 << ACTIVE) - 1] - values[0]) * 65_536)
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
