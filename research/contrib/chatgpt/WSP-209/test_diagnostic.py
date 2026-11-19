"""WSP-209 source-free frozen four-world update-suppression study checks."""
import math
import unittest

from diagnostic import WORLDS, metadata, run_world, evaluate, classify


class WSP209Qualification(unittest.TestCase):
    def test_source_free_worlds_and_splits_are_disjoint(self):
        all_genes=set()
        for seed,kind in WORLDS:
            gene,buckets=metadata(seed,kind)
            self.assertTrue(gene.startswith("FABRICATED_WSP209_"))
            self.assertNotIn(gene,all_genes)
            all_genes.add(gene)
            groups={}
            for (bucket,stage),items in buckets.items():
                for i,j,key in items:
                    self.assertNotIn(key,groups)
                    groups[key]=(bucket,stage)
            self.assertGreater(len(buckets[("PUBLIC_DEV",None)]),0)
            self.assertTrue(all(buckets[("FIT",k)] for k in range(4)))
            self.assertFalse(any("amacGFP" in key or "cgreGFP" in key or
                                 "ppluGFP" in key for key in groups))

    def test_complete_frozen_program_and_classification(self):
        result=evaluate()
        self.assertFalse(result["original_source_labels_accessed"])
        self.assertFalse(result["reserved_labels_accessed"])
        self.assertEqual(len(result["worlds"]),4)
        self.assertIn(result["classification"],
                      {"UPDATE_SUPPRESSION","INFORMATION_LIMIT",
                       "CANDIDATE_SUPPORTED_DEV","MIXED"})
        for world in result["worlds"]:
            self.assertFalse(world["reserved_labels_computed"])
            self.assertEqual(world["world_model_count"],4)
            self.assertGreater(world["fit_groups"],0)
            self.assertGreater(world["public_dev_groups"],0)
            for name,metrics in world["trace"].items():
                self.assertEqual(len(metrics["b0_mse"]),4)
                self.assertEqual(len(metrics["checkpoint_sha256"]),4)
                self.assertTrue(all(math.isfinite(v) for v in metrics["b0_mse"]))
                self.assertTrue(all(len(d)==64 for d in metrics["checkpoint_sha256"]))
                self.assertTrue(math.isfinite(metrics["dev_group_rmse"]))
                self.assertTrue(math.isfinite(metrics["cost_wall_ms"]))
        self.assertEqual(result["classification"],classify(result["worlds"]))
        import json
        print("WSP209_FABRICATED_SUMMARY="+json.dumps({
            "classification":result["classification"],
            "worlds":[{
                "seed":w["seed"],"topology":w["topology"],
                "candidate_gain":w["candidate_gain"],
                "refit_gain":w["refit_gain"],
                "write_ratio":w["candidate_to_always_write_ratio"],
                "candidate_b0":w["trace"]["contradiction"]["b0_mse"],
                "refit_b0":w["trace"]["full_refit"]["b0_mse"],
                "held_candidate":w["trace"]["contradiction"]["dev_group_rmse"],
                "held_refit":w["trace"]["full_refit"]["dev_group_rmse"],
                "held_zero":w["zero_rmse"]
            } for w in result["worlds"]]
        },sort_keys=True))

    def test_nonfrozen_world_fails_closed(self):
        with self.assertRaises(ValueError):
            metadata(20915,"hub")
        with self.assertRaises(ValueError):
            metadata(20911,"other")


if __name__=="__main__":
    unittest.main()
