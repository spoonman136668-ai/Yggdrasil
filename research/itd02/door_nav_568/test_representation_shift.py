"""Out-of-distribution falsification of supplied-prefix transfer.

These trials hold reward semantics fixed while changing nuisance bytes, and
invert reward semantics within a fixed prefix. Neither is included in FIT.
"""
import unittest
from adaptive_feature_cells import AdaptiveFeatureCells
from feature_eligibility_cells import FeatureEligibilityCells
from eligibility_local_cells import EligibilityLocalCells

class RepresentationShiftTests(unittest.TestCase):
    def test_shifted_prefix_breaks_unseen_same_semantics(self):
        # XY has the same desired action as trained AB, but no shared bytes.
        for cls in (AdaptiveFeatureCells, FeatureEligibilityCells):
            candidate = cls(feature_bytes=2)
            for _ in range(4):
                candidate.observe(b"AB-train", [0, 1])
                candidate.learn(1, b"success", 1, True)
            candidate.observe(b"XY-unseen", [0, 1])
            self.assertEqual(candidate.choose(), 0)

    def test_collision_misgeneralizes_unseen_opposite_semantics(self):
        # Both AB frames share a prefix, but the held-out frame needs 0.
        for cls in (AdaptiveFeatureCells, FeatureEligibilityCells):
            candidate = cls(feature_bytes=2)
            for _ in range(4):
                candidate.observe(b"AB-train", [0, 1])
                candidate.learn(1, b"success", 1, True)
            candidate.observe(b"AB-heldout-opposite", [0, 1])
            self.assertEqual(candidate.choose(), 1)

    def test_exact_state_control_is_uninformed_on_holdout(self):
        candidate = EligibilityLocalCells()
        candidate.observe(b"AB-train", [0, 1])
        candidate.learn(1, b"success", 1, True)
        candidate.observe(b"AB-heldout-opposite", [0, 1])
        self.assertEqual(candidate.choose(), 0)

if __name__ == "__main__":
    unittest.main()
