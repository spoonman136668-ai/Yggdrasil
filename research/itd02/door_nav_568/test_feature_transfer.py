"""Source-free positive transfer and negative aliasing controls."""
import unittest
from feature_eligibility_cells import FeatureEligibilityCells
from eligibility_local_cells import EligibilityLocalCells

class FeatureTransferTests(unittest.TestCase):
    def test_shared_feature_transfers_rewarded_action(self):
        shared = FeatureEligibilityCells(feature_bytes=2)
        exact = EligibilityLocalCells()
        for agent in (shared, exact):
            agent.observe(b"AB-training", [0, 1])
            agent.learn(1, b"goal", 1, True)
            agent.observe(b"AB-unfamiliar", [0, 1])
        self.assertEqual(shared.choose(), 1)
        self.assertEqual(exact.choose(), 0)

    def test_feature_collision_causes_wrong_action(self):
        shared = FeatureEligibilityCells(feature_bytes=2)
        exact = EligibilityLocalCells()
        for agent in (shared, exact):
            agent.observe(b"AB-left", [0, 1])
            agent.learn(1, b"goal", 1, True)
            agent.observe(b"AB-right", [0, 1])
            agent.learn(0, b"goal", 1, True)
            agent.observe(b"AB-left", [0, 1])
        self.assertEqual(exact.choose(), 1)
        # Both states alias to AB, so local cells cannot choose distinct
        # actions. This is a failure of the fixed feature projection.
        left = shared.choose()
        shared.observe(b"AB-right", [0, 1])
        right = shared.choose()
        self.assertEqual(left, right)
        self.assertNotEqual((left, right), (1, 0))

if __name__ == "__main__":
    unittest.main()
