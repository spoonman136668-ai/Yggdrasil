"""Protect the historical readout when validating a cumulative descendant."""

from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
import unittest

PATH = (Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/CAUSAL-AMALGAM"
        / "retention_guard.py")
SPEC = spec_from_file_location("amalgam_retention_guard_for_tests", PATH)
GUARD = module_from_spec(SPEC)
SPEC.loader.exec_module(GUARD)
EVENT = ("witness", ((0, 0), (0, 1)), 0, 1, 0, 1)


def model(transition, reward, ledger=(EVENT,)):
    def forecast(view, first, *second_stage):
        return reward if second_stage else transition
    return SimpleNamespace(native=SimpleNamespace(
        _episode_reader=lambda: SimpleNamespace(_ledger=ledger),
        experience_context_forecast=forecast,
    ))


class AmalgamRetentionGuardTests(unittest.TestCase):
    def test_each_target_is_guarded(self):
        anchor = model(Fraction(3, 4), Fraction(3, 4))
        candidate = model(Fraction(1), Fraction(1, 2))
        selected, report = GUARD.reversible_candidate(
            anchor, candidate, {"known": (0, 1)}, max_brier_drift=Fraction(1, 50),
        )
        self.assertIs(selected, anchor)
        self.assertFalse(report["pass"])
        self.assertGreater(report["windows"]["known"]["delta_brier"][1], 0)

    def test_retained_history_can_admit_candidate(self):
        anchor = model(Fraction(3, 4), Fraction(3, 4))
        candidate = model(Fraction(7, 8), Fraction(7, 8), ledger=(EVENT, ("next",)))
        selected, report = GUARD.reversible_candidate(
            anchor, candidate, {"known": (0, 1)}, max_brier_drift=Fraction(1, 50),
        )
        self.assertIs(selected, candidate)
        self.assertEqual(report["candidate_count"], 2)

    def test_rejects_rewritten_ledger_or_candidate_only_probe(self):
        anchor = model(Fraction(3, 4), Fraction(3, 4))
        changed = model(Fraction(3, 4), Fraction(3, 4), ledger=(("changed",),))
        with self.assertRaisesRegex(ValueError, "exact witness prefix"):
            GUARD.evaluate(anchor, changed, {"known": (0, 1)}, max_brier_drift=Fraction(1, 50))
        with self.assertRaisesRegex(ValueError, "within the anchor"):
            GUARD.evaluate(anchor, anchor, {"candidate_only": (1, 2)}, max_brier_drift=Fraction(1, 50))
