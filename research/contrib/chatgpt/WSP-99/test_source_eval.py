"""Fixture-only WSP99 source/evaluation custody checks: NO original worlds."""
from __future__ import annotations
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from task import bits
from source_eval import (
    make_fixture_sources, verify_sources, make_fixture_heldout_plan,
    make_predictions, score_fixture_predictions, HELDOUT_TARGETS,
    PASSIVE_EPISODES, INVESTIGATIVE_EPISODES
)
from controls import SymbolicFiniteState


class SourceEvaluationTests(unittest.TestCase):
    def test_exact_budgets_and_no_initial_state_overlap(self):
        for fixture_id in range(8):
            b = make_fixture_sources(fixture_id)
            self.assertTrue(verify_sources(b))
            self.assertEqual(len(b["passive"]), PASSIVE_EPISODES)
            self.assertEqual(len(b["active"]), INVESTIGATIVE_EPISODES)
            self.assertEqual(len(b["random"]), INVESTIGATIVE_EPISODES)
            self.assertEqual(b["active_action_count"], 32)
            self.assertEqual(b["random_action_count"], 32)
            self.assertTrue(all(
                a[0][0] == r[0][0] for a, r in zip(b["active"], b["random"])
            ))
            plan = make_fixture_heldout_plan(b)
            self.assertEqual(len(plan["targets"]), HELDOUT_TARGETS)
            seen = {e[0][0] for arm in ("passive","active","random") for e in b[arm]}
            self.assertEqual(len({t[0] for t in plan["targets"]}), HELDOUT_TARGETS)
            self.assertFalse(any(t[0] in seen for t in plan["targets"]))
            for initial, a, r in plan["targets"]:
                self.assertNotEqual(a[0], r[0])
                self.assertEqual(a[1:], r[1:])
                self.assertEqual(len(initial), 6)

    def test_fixture_replay_is_identical(self):
        for fixture_id in range(8):
            first, second = make_fixture_sources(fixture_id), make_fixture_sources(fixture_id)
            self.assertEqual(first, second)
            self.assertEqual(make_fixture_heldout_plan(first),
                             make_fixture_heldout_plan(second))

    def test_source_hash_and_action_budget_tamper_fails(self):
        b = make_fixture_sources(0)
        changes = []
        alt = copy.deepcopy(b)
        alt["active_action_count"] += 1
        changes.append(alt)
        alt = copy.deepcopy(b)
        alt["passive_sha256"] = "0" * 64
        changes.append(alt)
        alt = copy.deepcopy(b)
        alt["active"] = alt["random"]
        changes.append(alt)
        alt = copy.deepcopy(b)
        alt["source_sha256"] = "f" * 64
        changes.append(alt)
        for damaged in changes:
            with self.assertRaises(ValueError):
                verify_sources(damaged)

    def test_prediction_precommit_and_fixture_only_scoring(self):
        b = make_fixture_sources(1)
        plan = make_fixture_heldout_plan(b)
        fake = make_predictions(
            plan, lambda initial, actions: tuple((0,)*6 for _ in actions)
        )
        result = score_fixture_predictions(b, plan, fake)
        self.assertEqual(result["classification"], "FIXTURE_DEVELOPMENT_ONLY")
        self.assertFalse(result["scientific_superiority"])
        self.assertEqual(result["per_step_total"], 288)
        self.assertEqual(len(result["per_step_correct"]), 3)
        self.assertEqual(result["delayed_pair_total"], 24)
        self.assertEqual(len(result["pre_score_sha256"]), 64)
        self.assertTrue(result["predictions_frozen_before_truth"])
        self.assertGreaterEqual(result["evaluator_cpu_ns"], 0)
        for score in result["per_step_correct"]:
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 288)

    def test_prediction_or_plan_tamper_rejected(self):
        b = make_fixture_sources(0)
        plan = make_fixture_heldout_plan(b)
        predictions = make_predictions(
            plan, lambda initial, actions: tuple((1,)*6 for _ in actions)
        )
        with self.assertRaises(ValueError):
            score_fixture_predictions(b, plan, predictions[:-1])
        wrong_plan = copy.deepcopy(plan)
        wrong_plan["targets"] = wrong_plan["targets"][:-1]
        with self.assertRaises(ValueError):
            score_fixture_predictions(b, wrong_plan, predictions)
        corrupt_prediction = list(predictions)
        corrupt_prediction[0] = (((False, 0, 0, 0, 0, 0),)*3, predictions[0][1])
        with self.assertRaises(ValueError):
            score_fixture_predictions(b, plan, corrupt_prediction)

    def test_learners_only_receive_episodes_and_actions(self):
        b = make_fixture_sources(2)
        model = SymbolicFiniteState(b["passive"] + b["active"])
        self.assertEqual(model.source_accuracy, 1.0)
        plan = make_fixture_heldout_plan(b)
        prediction = make_predictions(plan, model.rollout)
        result = score_fixture_predictions(b, plan, prediction)
        self.assertEqual(result["classification"], "FIXTURE_DEVELOPMENT_ONLY")
        self.assertGreater(result["terminal_accuracy"], 0.45)
        self.assertEqual(result["per_step_total"], 288)

    def test_original_fixtures_rejected(self):
        for value in (99011, 99042, 99101, 99164, -1, True):
            with self.assertRaises(PermissionError):
                make_fixture_sources(value)


if __name__ == "__main__":
    unittest.main()
