"""WSP-210 one frozen primary look; newly preregistered synthetic worlds only.

No original data, no further seed/hyperparameter selection after this result.
"""
import json
import math
import unittest

from study import WORLDS, LAMBDAS, run_primary


class WSP210FrozenPrimary(unittest.TestCase):
    def test_10_fixed_four_world_primary_evaluation(self):
        result = run_primary()
        self.assertEqual("FABRICATED_ONLY_NO_ORIGINAL_GFP", result["source"])
        self.assertEqual(4, len(result["worlds"]))
        self.assertFalse(result["reserved_outcomes_accessed"])
        self.assertIn(result["classification"], (
            "INVALID", "REGULARIZATION_RECOVERS_ALL",
            "REGULARIZATION_RECOVERS_CONTROLS_ONLY",
            "LOW_LAMBDA_MEMORIZATION_ONLY",
            "PERSISTENT_LOW_LAMBDA_FAILURE", "MIXED"
        ))
        for expected, world in zip(WORLDS, result["worlds"]):
            self.assertEqual(tuple(world["world"]), expected)
            self.assertFalse(world["oracle_equal_information"])
            self.assertFalse(world["reserved_labels_generated"])
            self.assertEqual(0.0, world["privileged_oracle_rmse"])
            self.assertEqual(set(world["arms"]), {str(x) for x in LAMBDAS})
            self.assertGreater(world["held_groups"], 0)
            for arms in world["arms"].values():
                for arm in arms.values():
                    self.assertEqual(4, len(arm["b0_mse"]))
                    self.assertTrue(all(math.isfinite(x) for x in arm["b0_mse"]))
                    self.assertTrue(math.isfinite(arm["held_rmse"]))
                    self.assertEqual(4, len(arm["checkpoint_sha256"]))
        print("WSP210_PRIMARY_RESULT="+json.dumps(result,sort_keys=True,
                                                separators=(",",":")))


if __name__ == "__main__":
    unittest.main()
