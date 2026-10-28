"""Native colony receives real completed public action feedback, not labels."""
import unittest
from native_cell_recency_bridge_audit import measure, run, public_context, public_features
from native_cells_r7 import Colony

class NativeCellRecencyBridgeTests(unittest.TestCase):
    def test_actual_native_cell_updates_are_action_accounted(self):
        report = run()
        for key, expected in (("two_observation", 24),
                              ("single_observation", 12)):
            arm = report[key]
            self.assertEqual(arm["actions"], expected)
            self.assertEqual(arm["colony_feedback_updates"], expected)
            self.assertEqual(arm["control_examples"], expected)
            self.assertEqual(arm["colony_neighbor_messages"], expected * 8)
            self.assertTrue(arm["cold_restore_equal"])
            self.assertTrue(arm["archive_unchanged"])
            self.assertLessEqual(arm["native_checkpoint_bytes"], 32768)
            self.assertEqual(len(arm["stages"]), 6)
            for row in arm["stages"]:
                for policy in ("native", "control"):
                    metrics = row[policy]
                    self.assertEqual(sum(metrics.values()), 2)

    def test_public_only_mapping(self):
        self.assertEqual(public_context((b"M1-intermediate", 2)), "A")
        self.assertEqual(public_context((b"D2-intermediate", 2)), "B")
        self.assertEqual(len(public_features((b"M1-intermediate", 2))), 4)
        self.assertTrue(all(type(b) is bool for b in public_features(
            (b"D2-intermediate", 2))))
        with self.assertRaises(ValueError):
            public_features((b"", 2))

    def test_only_completed_feedback_is_admissible(self):
        colony = Colony()
        key = (b"M1-intermediate", 2)
        with self.assertRaises(ValueError):
            colony.learn_completed_public_feedback(
                public_context(key), public_features(key), True, 1)
        self.assertEqual(colony.feedback_updates, 0)

if __name__ == "__main__":
    unittest.main()
