"""CKAD40 DEV-only tests. No campaign seed is executed by unit tests."""
import importlib.util
import json
import subprocess
import sys
import unittest
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location("ckad40_diagnostic", HERE / "diagnostic.py")
D = importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)


class Frozen:
    def __init__(self, p, q):
        self.p, self.q = float(p), float(q)

    def forecast(self, view, first, next_state=None, second=None):
        return self.p if next_state is None else self.q


class Archive:
    def __init__(self):
        self._context_start = 64
        self._context_models = (
            (0, 32, "pure-A", Frozen(.85, .8)),
            (32, 48, "pure-A", Frozen(.8, .85)),
            (48, 64, "pure-B", Frozen(.15, .2)))


def event(t, phase, s2=1, y=1):
    return (str(t), ((1, 0), (1, 1)),
            {"s1": 1, "x1": 1, "s2": s2, "x2": 1, "y": y}, phase)


class CKAD40Tests(unittest.TestCase):
    def test_frozen_identity_no_hidden_first_use(self):
        self.assertEqual(D.PREREG, "d38ba4e7c438b0a2eb89bf08cd5f54e6ff0fe2e3")
        self.assertEqual(D.DEV, (40811, 40812))
        self.assertTrue(set(D.RESERVED).isdisjoint(D.DEV))
        self.assertEqual(D.WINDOW, 16)
        for seed in (*D.RESERVED, 38911, 38912, 39181, 39182, 14181, 14182):
            with self.assertRaisesRegex(ValueError, "CKAD40_ONLY_REGISTERED_DEV"):
                D.case(seed)

    def test_regime_labels_are_evaluator_only(self):
        self.assertEqual(D.source_regime("warm"), "A")
        self.assertEqual(D.source_regime("late_return_A"), "A")
        self.assertEqual(D.source_regime("late_B"), "B")
        with self.assertRaises(ValueError):
            D.source_regime("secret")

    def test_pure_archive_eligibility_and_no_evidence_overlap(self):
        observations = [event(i, "warm" if i < 48 else "late_B")
                        for i in range(80)]
        older = D.eligible_archive(Archive(), observations)
        self.assertEqual((len(older["A"]), len(older["B"])), (2, 1))
        # A 64-stop block overlaps the newest 16 training examples at t=72.
        overlap = D.eligible_archive(Archive(), observations[:72])
        self.assertEqual((len(overlap["A"]), len(overlap["B"])), (2, 0))
        archive = Archive()
        archive._context_models = ((0, 32, "pure", Frozen(.5,.5)),
                                   (32, 64, "mixed", Frozen(.5,.5)))
        self.assertEqual(len(D.eligible_archive(archive, observations)["B"]), 0)

    def test_identifiability_uses_only_prior_observed_outcomes(self):
        recent = [event(i, "late_B") for i in range(16)]
        favorable = D.history_logevidence([Frozen(.9, .9)], recent)
        unfavorable = D.history_logevidence([Frozen(.1, .1)], recent)
        self.assertGreater(favorable, unfavorable)
        with self.assertRaises(ValueError):
            D.history_logevidence([Frozen(.9, .9)], recent[1:])
        with self.assertRaises(ValueError):
            D.history_logevidence([], recent)

    def test_oracle_ceiling_terminal_conditions_on_observed_transition(self):
        sources = [Frozen(.9,.9), Frozen(.1,.1)]
        self.assertAlmostEqual(D.source_forecast(sources,(1,0),1), .5)
        self.assertAlmostEqual(D.source_forecast(sources,(1,0),1,1,1), .82)
        self.assertAlmostEqual(D.brier(.9,.8,{"s2":1,"y":1}),.025)

    def test_outcome_categories_and_early_stop(self):
        def fixture(seed, cover=.8, acc=.8, gain=.02, conv_gain=.02):
            return {"seed":seed, "late_covered":80, "coverage":cover,
                    "evidence_accuracy":acc, "oracle_gain_vs_native":gain,
                    "oracle_gain_vs_conventional":conv_gain,
                    "worlds":[{"source_complete":True, "cold_exact":True,
                               "old_source_preserved":True,"conflict_atomic":True}]}
        a,b = (fixture(seed) for seed in D.DEV)
        self.assertEqual(D.classify([a,b]),"DIAGNOSTIC_POTENTIAL")
        self.assertEqual(D.classify([a,fixture(D.DEV[1],cover=.2)]),
                         "ARCHIVE_COVERAGE_GAP")
        self.assertEqual(D.classify([a,fixture(D.DEV[1],acc=.5)]),
                         "IDENTIFICATION_GAP")
        self.assertEqual(D.classify([a,fixture(D.DEV[1],gain=.001)]),
                         "REPRESENTATION_GAP")
        with self.assertRaises(AssertionError):
            D.classify([b,a])

    def test_unregistered_cli_never_scores_reserved_seeds(self):
        # Parser boundary test; never calls experiment source generation.
        completed = subprocess.run(
            [sys.executable, "-B", str(HERE/"diagnostic.py"),
             "--mode", "dev", "--seed", str(D.RESERVED[0])],
            capture_output=True, text=True, cwd=HERE.parents[2])
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("CKAD40_ONLY_REGISTERED_DEV", completed.stderr)


if __name__ == "__main__":
    unittest.main()
