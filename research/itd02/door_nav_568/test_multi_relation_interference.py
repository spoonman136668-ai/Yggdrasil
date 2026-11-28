"""Multi-relation native cell retention and unfamiliar public features."""
import unittest
from multi_relation_interference_audit import measure, PATTERNS, UNSEEN

class MultiRelationInterferenceTests(unittest.TestCase):
    def test_strict_matched_public_feedback_and_restart(self):
        r = measure()
        self.assertEqual(r["actions"], 4)
        self.assertEqual(r["native_feedback_updates"], 4)
        self.assertEqual(r["tabular_examples"], 4)
        self.assertEqual([p["phase"] for p in r["phases"]],
                         ["untrained", "relationship_1", "relationship_2"])
        self.assertTrue(r["cold_restore_equal"])
        self.assertLessEqual(r["native_checkpoint_bytes"], 32768)
        self.assertGreater(r["tabular_state_bytes"], 0)
        for phase in r["phases"]:
            for key in ("native_trained", "tabular_trained", "native_heldout", "tabular_heldout"):
                self.assertEqual(sum(phase[key].values()), 2)
        for arm in ("native", "tabular"):
            self.assertGreaterEqual(r["cpu_ns"][arm], 0)

    def test_distinct_relationships_have_no_target_overlap(self):
        self.assertNotEqual(PATTERNS[0][0], PATTERNS[1][0])
        self.assertNotEqual(PATTERNS[0][1], PATTERNS[1][1])
        self.assertTrue(all(bits not in {p for p, _ in PATTERNS}
                            for bits, _ in UNSEEN))
        self.assertEqual(measure()["phases"][0]["tabular_heldout"]["abstentions"], 2)

    def test_conventional_can_retain_both_public_relationships(self):
        last = measure()["phases"][-1]
        self.assertEqual(last["tabular_trained"]["correct"], 2)
        self.assertEqual(last["tabular_trained"]["wrong"], 0)
        self.assertEqual(last["tabular_heldout"]["abstentions"], 2)

    def test_documented_interference_regression(self):
        end = measure()["phases"][-1]
        self.assertEqual(end["native_trained"]["correct"], 1)
        self.assertEqual(end["native_trained"]["abstentions"], 1)
        self.assertEqual(end["tabular_trained"]["correct"], 2)
        self.assertEqual(end["native_heldout"]["correct"], 1)
        self.assertEqual(end["tabular_heldout"]["abstentions"], 2)
