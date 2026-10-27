"""Frozen-versus-online unseen public transition transfer accounting."""
import unittest
from unfamiliar_transition_transfer_audit import run

class UnfamiliarTransferTests(unittest.TestCase):
    def test_matched_source_free_calibration_and_resource_limits(self):
        report = run()
        frozen, online = report["frozen_control"], report["online_feedback"]
        self.assertEqual(frozen["calibration_actions"], online["calibration_actions"])
        self.assertEqual(frozen["calibration_actions"], 8)
        for arm in (frozen, online, report["one_sample_negative"]):
            self.assertTrue(arm["archive_unchanged"])
            self.assertTrue(arm["first_hop_unchanged"])
            self.assertLessEqual(arm["online_records"], 128)
            self.assertEqual(arm["total_actions"],
                arm["calibration_actions"] + arm["novel_actions"] +
                arm["retention_actions"])
            self.assertLessEqual(arm["novel_actions"], 6)
            self.assertLessEqual(arm["retention_actions"], 6)

    def test_unfamiliar_transfer_must_improve_over_frozen_control(self):
        report = run()
        frozen, online = report["frozen_control"], report["online_feedback"]
        self.assertTrue(frozen["novel_abstained"])
        self.assertFalse(frozen["novel_wrong"])
        self.assertTrue(online["novel_correct"])
        self.assertFalse(online["novel_wrong"])
        self.assertTrue(online["retention_correct"])

    def test_single_sample_not_enough_to_admit_novel_transition(self):
        outcome = run()["one_sample_negative"]
        self.assertFalse(outcome["novel_correct"])
        self.assertTrue(outcome["novel_abstained"])

if __name__ == "__main__":
    unittest.main()
