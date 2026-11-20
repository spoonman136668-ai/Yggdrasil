"""Frozen source-only negatives; historical original-object test requires pinned ZIP.

Never execute original source actor or create fresh world episodes in root CI.
"""
from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
import os
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research/contrib/chatgpt/CAUSAL-AMALGAM/ckad22_native_zero_probe.py"
SPEC = spec_from_file_location("ckad22_native_zero_probe_test", SOURCE)
a = module_from_spec(SPEC)
SPEC.loader.exec_module(a)
ZIP = Path(os.environ.get("CKAD22_ORIGINAL_ZIP",
                           "/mnt/data/ckad22-linux-original.zip"))


class _Member:
    def __init__(self, transition, terminal):
        self.transition = transition
        self.terminal = terminal

    def forecast(self, view, first, state=None, second=None):
        return self.transition if state is None else (
            self.terminal if second == 1 else 1 - self.terminal)


def _reader(*, change_prior=False, start=384):
    members = []
    for i in range(13):
        transition = Fraction(1, 4) if i < 6 else Fraction(3, 4)
        terminal = Fraction(1, 4) if i < 6 else Fraction(3, 4)
        if i == 12:
            transition = terminal = Fraction(1, 2)
        begin = i * 32 if i < 12 else 384
        stop = (i + 1) * 32 if i < 12 else 384
        members.append((begin, stop, "0" * 64, _Member(transition, terminal)))
    prior = list(a.PRIOR)
    if change_prior:
        prior[0] += Fraction(1, 96)
    return SimpleNamespace(_ledger=(None,) * 384, _context_start=start,
                           _context_novel=True, _context_models=tuple(members),
                           _context_weights=tuple(prior))


class ArchiveIndependentContracts(unittest.TestCase):
    def test_original_pinned_source_blobs(self):
        a.verify_sources()

    def test_exact_original_sha_seed_set_and_frozen_plans(self):
        self.assertEqual(sorted(a.HISTORICAL), [101, 202, 303])
        self.assertEqual(a.FROZEN_FIRST, {101: (0, 0), 202: (0, 0), 303: (0, 1)})
        self.assertEqual(sum(a.PRIOR), 1)
        self.assertEqual(a.PRIOR, (Fraction(7, 96),) * 12 + (Fraction(1, 8),))

    def test_source_blob_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises((FileNotFoundError, ValueError)):
                a.verify_sources(tmp)
        self.assertNotEqual(a.git_blob(b"x"), a.git_blob(b"y"))

    def test_no_fabricated_fraction_or_bad_probability(self):
        self.assertEqual(a.ratio(Fraction(1, 4)), [1, 4])
        with self.assertRaisesRegex(ValueError, "EXACT_FRACTION"):
            a.ratio(0.5)
        with self.assertRaisesRegex(ValueError, "PROBABILITY_BOUNDS"):
            a.ratio(Fraction(5, 4))

    def test_prior_mismatch_and_old_context_refused(self):
        a.check_prior(_reader())
        with self.assertRaisesRegex(ValueError, "PRIOR_OR_CONTEXT"):
            a.check_prior(_reader(change_prior=True))
        with self.assertRaisesRegex(ValueError, "PRIOR_OR_CONTEXT"):
            a.check_prior(_reader(start=352))

    def test_conditional_transition_is_bayesian_not_unweighted(self):
        r = _reader()
        unconditional = a.mixture(r, (0, 0), 0)
        self.assertEqual(unconditional, Fraction(1, 2))
        terminal_on_one = a.mixture(r, (0, 0), 0, 1, 1)
        terminal_on_zero = a.mixture(r, (0, 0), 0, 0, 1)
        self.assertGreater(terminal_on_one, Fraction(1, 2))
        self.assertLess(terminal_on_zero, Fraction(1, 2))
        self.assertEqual((terminal_on_one + terminal_on_zero) / 2, Fraction(1, 2))

    def test_two_stage_contract_and_ties(self):
        with self.assertRaisesRegex(ValueError, "TWO_STAGE_HISTORY"):
            a.mixture(_reader(), (0, 0), 0, 1)
        p = a.plan_from_mixture(_reader(), (0, 0))
        self.assertEqual(p["first_action"], 0)
        self.assertEqual(p["second_actions"], ((1, 1), (1, 1)))
        self.assertEqual(len(p["first_values"]), 2)

    def test_no_original_archive_is_successfully_claimed(self):
        self.assertEqual(a.SCHEMA, "ckad22.historical-native-cold-zero-probe.v1")
        self.assertFalse("source" in a.SCHEMA and "first_use_go" in a.SCHEMA)


@unittest.skipUnless(ZIP.exists(), "original pinned historical ZIP absent: authentic native cold UNVERIFIED")
class HistoricalNativeNoNewSource(unittest.TestCase):
    def test_actual_pinned_historical_native_class_zero_probe(self):
        result = a.audit(ZIP)
        self.assertEqual(result["schema"], a.SCHEMA)
        self.assertEqual(len(result["results"]), 3)
        self.assertEqual(result["original_world_source_actions"], 0)
        self.assertEqual(result["new_observations"], 0)
        self.assertFalse(result["scientific_gain_verified"])
        self.assertFalse(result["source_first_use"])
        self.assertEqual(result["deployment"], "NONE")
        for one in result["results"]:
            self.assertEqual(one["retained_witnesses"], 384)
            self.assertEqual(one["new_context_start"], 384)
            self.assertEqual(one["end_b_context_start"], 352)
            self.assertEqual(one["prior_old"], [7, 96])
            self.assertEqual(one["prior_novel"], [1, 8])
            self.assertTrue(one["cold_restore_equal"])
            self.assertEqual(len(one["public_readouts"]), 2)
            self.assertEqual([s["planner_first"] for s in one["public_readouts"]],
                             list(a.FROZEN_FIRST[one["seed"]]))


if __name__ == "__main__":
    unittest.main()
