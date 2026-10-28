"""Adversarial repeated-conflict and capacity controls for adaptive features."""
import unittest
from adaptive_feature_cells import AdaptiveFeatureCells

class AdaptiveStressTests(unittest.TestCase):
    def test_repeated_conflict_does_not_erase_split_memory(self):
        p = AdaptiveFeatureCells(feature_bytes=2)
        for _ in range(4):
            for frame, action in ((b"AB-left", 1), (b"AB-right", 0)):
                p.observe(frame, [0, 1])
                p.learn(action, b"goal", 1, True)
        for frame, action in ((b"AB-left", 1), (b"AB-right", 0)):
            p.observe(frame, [0, 1])
            self.assertEqual(p.choose(), action)

    def test_split_respects_state_capacity(self):
        p = AdaptiveFeatureCells(max_states=2, feature_bytes=2)
        p.observe(b"AB-left", [0, 1])
        p.learn(1, b"goal", 1, True)
        p.observe(b"AB-right", [0, 1])
        with self.assertRaises(ValueError):
            p.learn(0, b"goal", 1, True)

    def test_unseen_collision_after_split_not_inherited(self):
        p = AdaptiveFeatureCells(feature_bytes=2)
        for frame, action in ((b"AB-left", 1), (b"AB-right", 0)):
            p.observe(frame, [0, 1])
            p.learn(action, b"goal", 1, True)
        p.observe(b"AB-third", [0, 1])
        self.assertEqual(p.choose(), 0)

if __name__ == "__main__":
    unittest.main()
