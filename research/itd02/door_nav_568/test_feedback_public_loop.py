"""Guarded learning-feedback policy and matched source-free accounting."""
import unittest
from feedback_public_loop_audit import run
from feedback_public_loop import FeedbackPublicLoop
from native_public_loop import PublicWorld

class FeedbackLoopTests(unittest.TestCase):
    def test_policy_comparison_accounts_for_every_case(self):
        report = run()
        for key in ("frozen_selector_control", "online_feedback"):
            arm = report[key]
            self.assertEqual(len(arm["rounds"]), 4)
            self.assertEqual(arm["correct"] + arm["abstentions"] + arm["wrong"], 4)
            self.assertTrue(arm["archive_unchanged"])
            self.assertLessEqual(arm["actions"], 24)
            self.assertLessEqual(arm["online_records"], 128)
            self.assertTrue(all(item["actions"] <= 6 for item in arm["rounds"]))

    def test_prior_evidence_not_current_or_future_outcome(self):
        learner = FeedbackPublicLoop(enabled=True)
        before = dict(learner.learned.links)
        outcome = learner.episode(PublicWorld("A", surprise=True))
        self.assertEqual(outcome["selected"], "snapshot")
        self.assertEqual(outcome["actions"], 5)
        self.assertGreater(outcome["online_examples"], 0)
        self.assertEqual(learner.model.archived_links[(b"M1-intermediate", 2)],
                         b"R3-positive")
        self.assertEqual(before[(b"M1-intermediate", 2)], b"X5-shift")

    def test_insufficient_evidence_abstains(self):
        learner = FeedbackPublicLoop(enabled=True)
        row = learner.episode(PublicWorld("A", surprise=True), budget=4)
        self.assertIsNone(row["selected"])
        self.assertEqual(row["actions"], 4)

if __name__ == "__main__":
    unittest.main()
