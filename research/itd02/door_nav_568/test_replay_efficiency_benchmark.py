"""Matched replay efficiency and false-restoration controls."""
import unittest
from replay_efficiency_benchmark import run, PROBE_A, PROBE_B

class ReplayEfficiencyTests(unittest.TestCase):
    def test_return_probe_restores_prior_regime(self):
        result = run(PROBE_A)
        self.assertEqual(result["probe_observations_per_candidate"], 2)
        self.assertEqual(result["pre_switch_scores"], {"A": 2, "B": 4})
        self.assertTrue(result["replay_restored"])
        self.assertEqual(result["replay_scores"]["A"], 4)
        self.assertLessEqual(result["replay_history"], 8)
        self.assertEqual(result["fresh_history"], 2)
        self.assertEqual(result["archive_count"], 1)

    def test_still_current_regime_must_not_restore(self):
        result = run(PROBE_B)
        self.assertFalse(result["replay_restored"])
        self.assertEqual(result["replay_scores"]["B"], 4)

    def test_matched_repetition(self):
        self.assertEqual(run(PROBE_A), run(PROBE_A))
        self.assertEqual(run(PROBE_B), run(PROBE_B))

if __name__ == "__main__":
    unittest.main()
