"""WSP-213 source-only preflight. No seed213xx target or learner run here."""
from __future__ import annotations
import json
from pathlib import Path
import unittest
from study import (WORLDS, FORBIDDEN, MODES, RANK, RIDGE, PREREG_SHA,
                   metadata, _factor, BlockedFullRefit, Learner)
from verify_parity import compare_metric, compare_receipts


class WSP213Preflight(unittest.TestCase):
    def test_prereg_freeze_and_source_fences(self):
        p = json.loads((Path(__file__).parent / "prereg.json").read_text())
        self.assertEqual(p["experiment_id"], "WSP-213")
        self.assertEqual(PREREG_SHA, "8b8f8deaf14ea256a311690e4ca59d4cc4110caa")
        self.assertEqual([x["seed"] for x in p["cohort"]["primary_worlds"]],
                         [w[0] for w in WORLDS])
        self.assertFalse(FORBIDDEN.intersection(w[0] for w in WORLDS))
        self.assertFalse(p["permissions"]["original_GFP_first_use"])
        self.assertFalse(p["permissions"]["merge"])
        self.assertFalse(p["permissions"]["native_training"])
        self.assertEqual(4, RANK)
        self.assertEqual(0.2, RIDGE)
        self.assertTrue(issubclass(BlockedFullRefit, Learner))
        self.assertEqual(set(MODES), {"full_refit", "contradiction",
                         "surprise", "random", "always", "no_update"})
        for world in WORLDS:
            gene, groups = metadata(world)
            self.assertTrue(gene.startswith("FABRICATED_WSP213_"))
            fit = {g for s in range(4)
                   for _, _, g in groups[("FIT", s)]}
            held = {g for _, _, g in groups[("PUBLIC_DEV", None)]}
            self.assertTrue(held)
            self.assertFalse(fit.intersection(held))
            self.assertTrue(all(groups[("FIT", s)] for s in range(4)))
        for forbidden in ((21011, "hub", 64),
                          (21101, "hub", 24),
                          (21201, "hub", 24),
                          (21399, "hub", 24)):
            with self.assertRaises(ValueError):
                metadata(forbidden)

    def test_deny_foreign_generator_without_primary_read(self):
        # The negative guard must not evaluate any actual 213xx target.
        for bad in (21011, 21101, 21201, 90001):
            with self.assertRaises(ValueError):
                _factor(bad, "C", 1, 0)
        with self.assertRaises(ValueError):
            _factor(21301, "E", 1, 0)
        with self.assertRaises(ValueError):
            _factor(21301, "C", -1, 0)
        with self.assertRaises(ValueError):
            _factor(21301, "C", 1, 4)

    def test_cross_os_comparator_negative_fences(self):
        compare_metric("close", .12345678, .123456781)
        for metric in (float("nan"), float("inf"), "not numeric"):
            with self.assertRaises(ValueError):
                compare_metric("bad", 0, metric)
        with self.assertRaises(ValueError):
            compare_metric("material drift", .14, .17)
        for bad in ({"classification": "DIRECT_GAIN"},
                    {"schema": "wrong"},
                    {"original_gfp_labels_accessed": True}):
            with self.assertRaises(ValueError):
                compare_receipts(bad, bad)


if __name__ == "__main__":
    unittest.main()
