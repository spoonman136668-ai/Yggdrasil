"""WSP-211: disjoint comparator preflight; no WSP-210 primary runs."""
import math
import unittest
from calibration import CALIBRATION, FORBIDDEN, BlockedFullRefit, metadata, run_calibration


class WSP211ComparatorCalibration(unittest.TestCase):
    def test_strict_world_allowlist_and_original_primary_exclusion(self):
        self.assertEqual({21101, 21102}, {w[0] for w in CALIBRATION})
        self.assertTrue(FORBIDDEN.isdisjoint(w[0] for w in CALIBRATION))
        for w in CALIBRATION:
            gene, groups = metadata(w)
            self.assertTrue(gene.startswith("FABRICATED_WSP211_"))
            self.assertTrue(all(groups[("FIT", s)] for s in range(4)))
            self.assertTrue(groups[("PUBLIC_DEV", None)])
        for w in ((21011, "hub", 64), (21012, "hub", 64),
                  (21013, "complete", 16), (21014, "complete", 16),
                  (21121, "hub", 24)):
            with self.assertRaises(ValueError):
                metadata(w)

    def test_only_fresh_calibration_and_fail_closed_controls(self):
        output = run_calibration()
        self.assertEqual("wsp211.convergence-calibration.source-free.v1",
                         output["schema"])
        self.assertEqual(2, len(output["worlds"]))
        self.assertFalse(output["wsp210_primary_reused"])
        self.assertFalse(output["original_gfp_labels_accessed"])
        self.assertFalse(output["reserved_labels_accessed"])
        self.assertIn(output["classification"],
                      ("CONTROL_QUALIFIED", "CONTROL_UNQUALIFIED"))
        for w, expected in zip(output["worlds"], CALIBRATION):
            self.assertEqual(expected, w["world"])
            self.assertFalse(w["original_source_accessed"])
            self.assertFalse(w["reserved_labels_generated"])
            for step in w["trace"]:
                self.assertEqual(0, step["refit_actual_sweeps"] % 8)
                self.assertLessEqual(step["refit_actual_sweeps"], 800)
                self.assertTrue(math.isfinite(step["refit_objective"]))
                self.assertEqual(64, len(step["refit_checkpoint_sha256"]))
                self.assertEqual(64, len(step["adam_checkpoint_sha256"]))
            if w["status"] == "CONTROL_QUALIFIED":
                self.assertEqual(4, w["stages_completed"])
                self.assertEqual(4, len(w["trace"]))
                for key in ("refit_held_rmse", "adam_held_rmse",
                            "zero_held_rmse"):
                    self.assertTrue(math.isfinite(w[key]))
            else:
                self.assertIn("reason", w)
        print("WSP211_CALIBRATION_RESULT=" +
              __import__("json").dumps(output, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
