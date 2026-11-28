"""Adversarial adaptive-feature split and delayed-credit tests."""
import unittest
from adaptive_feature_cells import AdaptiveFeatureCells

class AdaptiveFeatureTests(unittest.TestCase):
    def test_conflict_split_preserves_previous_reward(self):
        agent = AdaptiveFeatureCells(feature_bytes=2)
        agent.observe(b"AB-left", [0, 1])
        agent.learn(1, b"goal", 1, True)
        agent.observe(b"AB-right", [0, 1])
        agent.learn(0, b"goal", 1, True)
        self.assertIn(b"AB", agent.split)
        agent.observe(b"AB-left", [0, 1])
        self.assertEqual(agent.choose(), 1, "split lost learned left action")
        agent.observe(b"AB-right", [0, 1])
        self.assertEqual(agent.choose(), 0)

    def test_delayed_reward_does_not_attribute_to_final_only(self):
        agent = AdaptiveFeatureCells(feature_bytes=2)
        agent.observe(b"AB-left", [0, 1])
        agent.learn(1, b"middle", 0, False)
        agent.observe(b"CD-middle", [2])
        agent.learn(2, b"goal", 1, True)
        agent.observe(b"AB-left", [0, 1])
        self.assertEqual(agent.choose(), 1)

    def test_same_public_frame_different_rewarded_actions_not_split(self):
        agent = AdaptiveFeatureCells(feature_bytes=2)
        for action in (0, 1):
            agent.observe(b"AB-same", [0, 1])
            agent.learn(action, b"goal", 1, True)
        self.assertNotIn(b"AB", agent.split)

if __name__ == "__main__":
    unittest.main()
