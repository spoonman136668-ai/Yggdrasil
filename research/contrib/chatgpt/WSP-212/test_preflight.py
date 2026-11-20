"""Source-only WSP212 negative/preflight tests; DO NOT access calibration labels."""
import json
import math
from pathlib import Path
import unittest

from qualification import (WORLDS, FORBIDDEN, metadata, _component,
                           BlockedFullRefit, Learner, RANK, RIDGE)
from verify_parity import compare_metric, compare_receipts


class WSP212SourceFreePreflight(unittest.TestCase):
    def test_frozen_prereg_and_fresh_disjoint_world_allowlist(self):
        p = json.loads((Path(__file__).parent / "prereg.json").read_text())
        self.assertEqual("WSP-212", p["experiment_id"])
        self.assertEqual([w[0] for w in WORLDS],
                         [w["seed"] for w in p["cohort"]["worlds"]])
        self.assertFalse(FORBIDDEN.intersection({w[0] for w in WORLDS}))
        self.assertEqual(p["algorithm"]["rank"], RANK)
        self.assertEqual(p["algorithm"]["ridge"], RIDGE)
        self.assertFalse(p["permissions"]["real_data_first_use"])
        self.assertFalse(p["permissions"]["merge"])
        for w in WORLDS:
            gene, groups = metadata(w)
            self.assertTrue(gene.startswith("FABRICATED_WSP212_"))
            fit = {g for s in range(4)
                   for i, j, g in groups[("FIT", s)]}
            held = {g for i, j, g in groups[("PUBLIC_DEV", None)]}
            self.assertFalse(fit.intersection(held))
            self.assertTrue(held)
            self.assertTrue(all(groups[("FIT", s)] for s in range(4)))
        for invalid in ((21011, "hub", 64), (21101, "hub", 24),
                        (21299, "hub", 24)):
            with self.assertRaises(ValueError):
                metadata(invalid)

    def test_only_integer_digest_components_and_existing_refit(self):
        self.assertTrue(issubclass(BlockedFullRefit, Learner))
        self.assertEqual(4, RANK)
        self.assertEqual(0.2, RIDGE)
        # Component-only fixture; not a WSP212 FIT or held target.
        for position in range(1, 8):
            for k in range(RANK):
                c = _component(99999, "C", position, k)
                self.assertIsInstance(c, int)
                self.assertGreaterEqual(c, -3)
                self.assertLessEqual(c, 3)
        with self.assertRaises(ValueError):
            _component(99999, "X", 1, 0)

    def test_numeric_parity_strict_negative_controls(self):
        compare_metric("equal", 0.1234, 0.1234 + 1e-9)
        for val in (float("nan"), float("inf"), "not-a-number"):
            with self.assertRaises(ValueError):
                compare_metric("negative", 0.0, val)
        with self.assertRaises(ValueError):
            compare_metric("material OS drift", 0.01446, 0.01426)
        with self.assertRaises(ValueError):
            compare_receipts({"schema": "wrong"}, {"schema": "wrong"})
        with self.assertRaises(ValueError):
            compare_receipts({"classification": "CONTROL_UNQUALIFIED"},
                             {"classification": "CONTROL_UNQUALIFIED"})


if __name__ == "__main__":
    unittest.main()
