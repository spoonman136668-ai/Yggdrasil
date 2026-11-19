"""WSP-208 synthetic-only full protocol integration; no original GFP outcomes."""
import json
import math
import unittest

from learner import group_bucket
from source_free_comparison import ARMS, evaluate_fabricated
from source_free_partition import SYNTHETIC_DIGEST
from test_targets import fixture


class FullSourceFreeComparison(unittest.TestCase):
    def test_all_frozen_arms_retention_and_grouped_transfer(self):
        manifest, labels = fixture()
        result = evaluate_fabricated(manifest, labels, "wt",
                                    source_digest=SYNTHETIC_DIGEST)
        self.assertEqual(8, len(result["arms"]))
        self.assertEqual(8, len(ARMS))
        self.assertEqual(1, result["held_public_dev_reads"])
        self.assertFalse(result["reserved_outcomes_accessed"])
        self.assertEqual(2, result["held_groups"])
        self.assertEqual(8, result["fit_observation_receipts"])
        self.assertEqual("SOURCE_FREE_DIAGNOSTIC_NOT_SCIENTIFIC_RESULT",
                         result["classification"])
        for name, item in result["arms"].items():
            self.assertEqual(4, len(item["stage_costs"]))
            self.assertEqual([0,1,2,3],
                             [s["stage"] for s in item["stage_costs"]])
            self.assertGreater(item["all_stage_wall_ms"],0)
            self.assertGreater(item["factor_coordinates"],0)
            self.assertTrue(math.isfinite(item["dev_group_weighted_rmse"]))
            self.assertEqual(64, len(item["checkpoint_sha256"]))
        for arm in ("full_refit_r4","full_refit_r8"):
            self.assertTrue(all(s["converged"] for s in
                                result["arms"][arm]["stage_costs"]))
        for stage in range(1,4):
            cand = result["arms"]["contradiction_r4"]["stage_costs"][stage]
            self.assertEqual(cand["changed_addresses"],
                result["arms"]["surprise_r4"]["stage_costs"][stage]["changed_addresses"])
            self.assertEqual(cand["changed_addresses"],
                result["arms"]["random_r4"]["stage_costs"][stage]["changed_addresses"])
        self.assertEqual(2000,result["bootstrap"]["resamples"])
        self.assertEqual("site_pair_group",result["bootstrap"]["unit"])
        self.assertFalse("SCIENTIFIC_PASS" in json.dumps(result))
        self.assertGreater(result["paired_comparison"]["cost_ratio"],0)
        print("WSP208_FABRICATED_COMPARISON=" + json.dumps(
            result["paired_comparison"], sort_keys=True))

    def test_reserved_outcomes_not_read_even_with_poison(self):
        manifest, labels = fixture()
        protected = {r.row_id for r in manifest.eligible
                     if group_bucket(r.group)=="RESERVED_UNTOUCHED"}
        class OutcomeTrap(dict):
            def __getitem__(self, key):
                if key in protected:
                    raise AssertionError("RESERVED double target was accessed")
                return super().__getitem__(key)
        result = evaluate_fabricated(manifest, OutcomeTrap(labels), "wt",
                                    source_digest=SYNTHETIC_DIGEST)
        self.assertFalse(result["reserved_outcomes_accessed"])

    def test_deterministic_checkpoint_hashes_under_repeat(self):
        manifest, labels = fixture()
        a = evaluate_fabricated(manifest,labels,"wt",source_digest=SYNTHETIC_DIGEST)
        b = evaluate_fabricated(manifest,labels,"wt",source_digest=SYNTHETIC_DIGEST)
        for name in a["arms"]:
            self.assertEqual(a["arms"][name]["checkpoint_sha256"],
                             b["arms"][name]["checkpoint_sha256"])
            self.assertEqual(a["arms"][name]["dev_group_weighted_rmse"],
                             b["arms"][name]["dev_group_weighted_rmse"])

    def test_invalid_source_or_measured_value_fails_closed(self):
        manifest, labels = fixture()
        with self.assertRaises(ValueError):
            evaluate_fabricated(manifest,labels,"wt",source_digest="0"*64)
        bad = dict(labels)
        b0id = next(r.row_id for r in manifest.eligible
                    if r.bucket=="FIT" and r.stage==0)
        bad[b0id] = float("nan")
        with self.assertRaises(ValueError):
            evaluate_fabricated(manifest,bad,"wt",source_digest=SYNTHETIC_DIGEST)


if __name__=="__main__":
    unittest.main()
