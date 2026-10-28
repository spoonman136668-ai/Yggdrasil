"""Guarded learning-feedback policy and matched source-free accounting."""
import unittest
from feedback_public_loop_audit import run
from feedback_public_loop import FeedbackPublicLoop
from native_public_loop import PublicWorld

class FeedbackLoopTests(unittest.TestCase):
    def test_policy_comparison_accounts_for_every_case(self):
        report = run()
        for key in ("frozen_selector_control", "online_feedback",
                    "feedback_with_qualified_fallback"):
            arm = report[key]
            self.assertEqual(len(arm["rounds"]), 4)
            self.assertEqual(arm["correct"] + arm["abstentions"] + arm["wrong"], 4)
            self.assertTrue(arm["archive_unchanged"])
            self.assertLessEqual(arm["actions"], 24)
            self.assertLessEqual(arm["online_records"], 128)
            self.assertTrue(all(item["actions"] <= 6 for item in arm["rounds"]))

    def test_online_feedback_regression_is_retained(self):
        report = run()
        baseline = report["frozen_selector_control"]
        feedback = report["online_feedback"]
        self.assertEqual((baseline["correct"], baseline["abstentions"],
                          baseline["wrong"]), (4, 0, 0))
        self.assertEqual((feedback["correct"], feedback["abstentions"],
                          feedback["wrong"]), (3, 1, 0))
        self.assertEqual(feedback["rounds"][-1]["actions"], 0)
        self.assertIsNone(feedback["rounds"][-1]["selected"])
        self.assertEqual((baseline["actions"], feedback["actions"]), (18, 14))

    def test_recovered_probe_must_still_pass_physical_evidence(self):
        report = run()
        frozen = report["frozen_selector_control"]
        failed = report["online_feedback"]
        repaired = report["feedback_with_qualified_fallback"]
        self.assertEqual((frozen["correct"], failed["correct"]), (4, 3))
        self.assertEqual((failed["abstentions"], failed["wrong"]), (1, 0))
        self.assertEqual(repaired["correct"], 4)
        self.assertEqual(repaired["wrong"], 0)
        self.assertEqual(repaired["abstentions"], 0)
        self.assertTrue(repaired["rounds"][-1]["fallback_used"])
        self.assertGreaterEqual(repaired["rounds"][-1]["actions"], 4)
        self.assertLessEqual(repaired["rounds"][-1]["actions"], 6)
        self.assertTrue(repaired["archive_unchanged"])
        self.assertEqual(repaired["rounds"][-1]["online_changes"], 2)

    def test_recovery_does_not_fake_disagreement_without_a_frozen_candidate(self):
        learner = FeedbackPublicLoop(enabled=True, recovery=True)
        learner.model.active_links = dict(learner.model.archived_links)
        learner.learned.links = dict(learner.model.archived_links)
        outcome = learner.episode(PublicWorld("A"), budget=4)
        self.assertIsNone(outcome["selected"])
        self.assertEqual(outcome["actions"], 0)

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
