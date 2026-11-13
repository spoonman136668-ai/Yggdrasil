"""WSP81 synthetic unit fixtures ONLY; six frozen dev worlds are not run here."""
import json
import sys
from pathlib import Path
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from history_weights import PaidHistoryNumeric
from independent_control import IndependentHistorySymbolic
from experiment import (validate_custody, classify, CONTEXTS, PINNED, PRE_COMMIT)
import source


def synthetic_paid_rows(trigger=2, offset=3, mode_family=True):
    state = (0,) * 6
    mode = 0
    events = []
    for step in range(384):
        action = (step * 5 + step // 7) % 6
        after = list(state)
        after[action] ^= 1
        if mode_family and mode and action != trigger:
            after[(action + offset) % 6] ^= 1
        if mode_family and action == trigger:
            mode ^= 1
        after = tuple(after)
        events.append(SimpleNamespace(before=state, action=action,
                                      after=after, action_cost=1))
        state = after
    return tuple(events)


class FrozenLatentDeveloperTests(unittest.TestCase):
    def test_frozen_prereg_admission_never_calls_source(self):
        head, frozen = validate_custody()
        self.assertEqual(len(head), 40)
        self.assertEqual(frozen["state"], "FROZEN_BEFORE_SOURCE_IMPLEMENTATION_OR_RESULTS")
        self.assertEqual(len(frozen["source"]["seeds"]), 6)
        self.assertEqual(PRE_COMMIT, "a3782028045759994a5a3c3de3765a1d939ed6e3")
        self.assertEqual(len(PINNED), 7)

    def test_registered_source_and_unknown_seeds_blocked(self):
        for seed in (5601, 5608, 5616, 9001, 9400, 9407):
            with self.assertRaises(PermissionError):
                source.World.developer(seed)
        for step in (-1, 384):
            with self.assertRaises(PermissionError):
                source.fixed_action(9401, step)

    def test_numerical_symbolic_cold_parity_on_separate_synthetic_fixture(self):
        for mode_family in (False, True):
            events = synthetic_paid_rows(mode_family=mode_family)
            numeric = PaidHistoryNumeric()
            with self.assertRaises(ValueError):
                numeric.compile()
            history = []
            for event in events:
                numeric.charge(event.before, event.action, event.after,
                               event.action_cost)
                history.append(event.action)
            info = numeric.compile()
            self.assertTrue(1 <= info["surviving_mechanisms"] <= 31)
            cold = PaidHistoryNumeric.restore(numeric.snapshot())
            symbolic = IndependentHistorySymbolic(events)
            self.assertEqual(cold.snapshot(), numeric.snapshot())
            self.assertIsNone(cold._rows)
            for state in source.STATES:
                for action in source.ACTIONS:
                    for context in CONTEXTS:
                        self.assertEqual(cold.predict(state, action, context),
                                         symbolic.predict(state, action, context))
            seen = []
            for e in events:
                self.assertEqual(cold.predict(e.before, e.action, seen),
                                 e.after)
                seen.append(e.action)

    def test_paid_continuity_and_cold_snapshot_tamper_fail_closed(self):
        events = synthetic_paid_rows()
        writer = PaidHistoryNumeric()
        with self.assertRaises(ValueError):
            writer.charge((1,) * 6, 0, (0,) * 6)
        for e in events:
            writer.charge(e.before, e.action, e.after, e.action_cost)
        with self.assertRaises(ValueError):
            writer.charge(events[-1].after, 0, (0,) * 6)
        writer.compile()
        snap = writer.snapshot()
        with self.assertRaises(ValueError):
            PaidHistoryNumeric.restore(snap[:-1])
        with self.assertRaises(ValueError):
            PaidHistoryNumeric.restore(snap.replace('"charges":384', '"charges":144', 1))
        with self.assertRaises(ValueError):
            PaidHistoryNumeric.restore(snap.replace("mode_weights", "hidden_labels", 1))
        restored = PaidHistoryNumeric.restore(snap)
        with self.assertRaises(ValueError):
            restored.charge((0,) * 6, 0, (0,) * 6)

    def test_explicit_negative_developer_diagnostics_not_self_passing(self):
        frozen = json.loads(Path(__file__).with_name("prereg.json").read_text())
        results = []
        for meta in frozen["source"]["seeds"]:
            score = lambda correct: {"correct": correct, "wrong_confident": 0,
                    "abstain": 768 - correct, "unpaid_correct": 0, "unpaid_total": 0}
            results.append({
                "family": meta["family"], "paid_markov_conflicting_pairs": 0,
                "scores": {"numeric": score(448), "memoryless": score(768)},
                "numeric_symbolic_exact_parity": True,
                "numeric_cold_restored": True, "paid_actions": 384})
        outcome = classify(results, frozen)
        self.assertEqual(outcome["classification"],
                         "DEV_HIDDEN_HISTORY_DIAGNOSTICS_NEGATIVE")
        self.assertFalse(outcome["checks"]["hidden_public_markov_falsified"])
        self.assertFalse(outcome["checks"]["history_correct_over_memoryless"])

    def test_learners_never_import_private_source_or_evaluator(self):
        root = Path(__file__).parent
        for name in ("history_weights.py", "independent_control.py"):
            code = (root / name).read_text("utf8")
            for forbidden in ("from source import", "import source",
                              "_truth_for_context", "source.World",
                              "private_receipt"):
                self.assertNotIn(forbidden, code)
        code = (root / "experiment.py").read_text("utf8")
        self.assertEqual(code.count("world._truth_for_context("), 1)
        self.assertIn("evaluate_postfreeze(world, frozen)", code)


if __name__ == "__main__":
    unittest.main()
