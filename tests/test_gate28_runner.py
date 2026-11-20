"""Gate28 3-process A/B/R evaluator tests; reserved scientific seeds barred."""
import sys
import unittest
from pathlib import Path

HERE = (Path(__file__).resolve().parents[1] /
        "research/contrib/chatgpt/self-assembling-topologies/gate28")
sys.path.insert(0, str(HERE))
import runner
import world


class TestGate28Runner(unittest.TestCase):
    def test_public_preaction_context_and_intervention_independence(self):
        w = world.HiddenWorld(900011, diagnostic=True)
        for phase in ("B", "R"):
            for step in range(4):
                peek = w.public_context(phase, step)
                self.assertEqual(len(peek), 8)
                for action in world.ACTIONS:
                    self.assertEqual(w.feedback(phase, step, action).context, peek)

    def test_guard_rejects_primary_and_unapproved_seeds(self):
        for seed in (501000, 501047, 502001, 503023, -1, 999999, True):
            with self.assertRaisesRegex(ValueError, "PRIMARY_SEEDS_RESERVED"):
                runner.require_diagnostic(seed)
        runner.require_diagnostic(900011)

    def test_true_cold_and_identical_forced_exposure(self):
        result = runner.diagnostic(900011)
        self.assertEqual(result["stages"], ["A", "B", "R"])
        self.assertEqual(result["distinct_processes"], 3)
        self.assertFalse(result["primary_scored"])
        self.assertEqual(result["status"], "G28_DIAGNOSTIC_COLD_PROCESS_PASS")
        self.assertEqual(result["science"], "NOT_RUN_NO_EXHAUSTIVE_BAYESIAN_OR_MATCHED_CAUSAL_CONTROL")
        self.assertLessEqual(result["max_rule_work"], 8192)
        self.assertLessEqual(result["max_checkpoint_bytes"], 16384)
        self.assertNotEqual(result["forced_B_exposure_hash"],
                            result["forced_R_exposure_hash"])
