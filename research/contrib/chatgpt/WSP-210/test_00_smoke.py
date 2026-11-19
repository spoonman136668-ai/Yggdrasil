"""WSP-210 smoke only: disjoint seed21001, NEVER primary seeds."""
import math
import unittest

from study import (SMOKE, LAMBDAS, ridge_scope, metadata,
                   run_world, _factor, _classification)
import learner as core


class WSP210Preflight(unittest.TestCase):
    def test_frozen_smoke_world_and_lambda_restoration(self):
        gene,groups=metadata(SMOKE)
        self.assertTrue(gene.startswith("FABRICATED_WSP210_"))
        self.assertTrue(all(groups[("FIT",s)] for s in range(4)))
        self.assertTrue(groups[("PUBLIC_DEV",None)])
        self.assertEqual(core.LAMBDA,10.0)
        with self.assertRaises(RuntimeError):
            with ridge_scope(.2):
                self.assertEqual(core.LAMBDA,.2)
                raise RuntimeError("guard restoration test")
        self.assertEqual(core.LAMBDA,10.0)
        with self.assertRaises(ValueError):
            ridge_scope(0.0001).__enter__()
        with self.assertRaises(ValueError):
            metadata((21011,"hub",63))

    def test_smoke_all_controls_and_cold_restore(self):
        result=run_world(SMOKE)
        self.assertFalse(result["reserved_labels_generated"])
        self.assertEqual(set(result["arms"]),{str(x) for x in LAMBDAS})
        self.assertGreater(result["held_groups"],0)
        for values in result["arms"].values():
            for name in ("direct","refit","adam"):
                arm=values[name]
                self.assertEqual(4,len(arm["b0_mse"]))
                self.assertTrue(all(math.isfinite(x) for x in arm["b0_mse"]))
                self.assertTrue(math.isfinite(arm["held_rmse"]))
                self.assertTrue(all(len(x)==64 for x in arm["checkpoint_sha256"]))
        self.assertEqual(core.LAMBDA,10.0)
        self.assertTrue(result["valid_conventional"],
                        "Frozen Adam baseline did not plateau on the smoke world")
        self.assertEqual("INVALID",_classification([result]))


if __name__=="__main__":
    unittest.main()
