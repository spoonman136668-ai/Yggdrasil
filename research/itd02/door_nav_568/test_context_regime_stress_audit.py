"""Retain repeated-environment and public-context collision negatives."""
import unittest
from context_regime_stress_audit import run

class ContextRegimeStressTests(unittest.TestCase):
    def test_both_agents_get_matched_interventions(self):
        report = run()
        self.assertEqual(set(report["agents"]), {"single", "snapshot"})
        for candidate in report["agents"].values():
            self.assertEqual(candidate["A_initial"], 1)
            self.assertLessEqual(candidate["examples"], 256)
            for key, target in report["expected"].items():
                self.assertIn(candidate[key], (0, 1))
                self.assertIn(target, (0, 1))
        self.assertEqual(report["per_arm_new_context_interventions"], 48)
        self.assertEqual(report["per_arm_collision_interventions"], 4)
        self.assertEqual(report, run())

    def test_explicit_capacity_and_snapshot_memory_cost(self):
        report = run(capacity=64)
        single = report["agents"]["single"]["examples"]
        snap = report["agents"]["snapshot"]["examples"]
        self.assertLessEqual(single, 64)
        self.assertLessEqual(snap, 128)
        self.assertGreaterEqual(snap, single)

    def test_observed_failure_modes_remain_explicit(self):
        report = run()
        single = report["agents"]["single"]
        snapshot = report["agents"]["snapshot"]
        self.assertEqual(single["A_old_retention"], 0)
        self.assertEqual(single["A_return"], 0)
        self.assertEqual(snapshot["A_old_retention"], 1)
        self.assertEqual(snapshot["B_colliding_context"], 1)
        self.assertEqual(snapshot["A_return"], 0)
        self.assertEqual((single["examples"], snapshot["examples"]), (64, 76))

    def test_collision_and_return_are_reported_not_silently_accepted(self):
        report = run()
        for candidate in report["agents"].values():
            self.assertIn("B_colliding_context", candidate)
            self.assertIn("A_return", candidate)
            self.assertIn("A_old_retention", candidate)

if __name__ == "__main__":
    unittest.main()
