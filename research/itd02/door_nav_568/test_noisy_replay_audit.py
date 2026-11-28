"""Noisy replay audit is deterministic and preserves negative findings."""
import unittest
from noisy_replay_audit import run

class NoisyReplayAuditTests(unittest.TestCase):
    def test_enumerates_all_feedback_masks(self):
        report = run()
        self.assertEqual(report["total_cases"], 8)
        self.assertEqual({(x["actual"], x["flip_mask"]) for x in report["cases"]},
                         {(regime, mask) for regime in ("A", "B") for mask in range(4)})
        self.assertTrue(all(x["probe_closed"] for x in report["cases"]))

    def test_clean_feedback_restores_only_when_regime_returns(self):
        cases = {x["actual"]: x for x in run()["cases"] if x["flip_mask"] == 0}
        self.assertTrue(cases["A"]["restored"])
        self.assertFalse(cases["B"]["restored"])

    def test_false_restoration_is_reported_not_hidden(self):
        report = run()
        self.assertEqual(report["false_restorations"],
                         sum(x["false_restoration"] for x in report["cases"]))
        self.assertEqual(report, run())

if __name__ == "__main__":
    unittest.main()
