"""CKAD41-49 read-only original archive qualification checks.

No import of any experimental campaign and no new source / science first-use.
"""
from __future__ import annotations
import importlib.util, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ckad41_49_verified_archives",HERE/"run_audit.py")
A=importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)

class CrossStudyArchiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record=A.analyze()
        cls.results={v["study"]:v for v in cls.record["study_results"]}

    def test_exact_nine_original_archives_and_different_world_metrics(self):
        self.assertEqual(self.record["studies"],9)
        self.assertEqual(set(self.results),{f"CKAD{n}" for n in range(41,50)})
        self.assertTrue(all(v["same_metric_across_studies"] is False for v in self.results.values()))
        self.assertEqual(self.record["scientific_seeds_consumed_here"],[])
        self.assertEqual(self.record["accepted_main_verified_at_audit"],
                         "5e74f8db85b2f5839c42148c0dfba69a88b1a2c9")

    def test_nine_scientific_original_no_go_not_ci_success_promotion(self):
        self.assertEqual(self.record["scientific_dev_no_go"],9)
        self.assertEqual(self.record["scientific_dev_passes"],0)
        self.assertTrue(all(v["scientific"]=="DEV_NO_GO" for v in self.results.values()))
        self.assertTrue(all(not all(row["gain_threshold_met"] for row in v["dev_rows"])
                            for v in self.results.values()))
        self.assertFalse(self.record["promotion_authorized"])
        self.assertTrue(self.record["audit_only"])

    def test_ckad42_engineering_unqualified_despite_successful_CI(self):
        self.assertEqual(self.record["engineering_dev_passes"],8)
        self.assertEqual(self.record["engineering_dev_unqualified"],1)
        self.assertEqual(self.results["CKAD42"]["engineering"],
                         "NOT_QUALIFIED_CROSS_PLATFORM_CHECKPOINT_DRIFT")
        report=A.load_archive(42)
        self.assertFalse(report["ci"]["exact_learned_checkpoint_sha256_equal"])
        self.assertTrue(report["ci"]["deterministic_scoring_metrics_equal"])
        self.assertEqual(len(report["ci"]["learned_checkpoint_drifts"]),1)

    def test_native_microanchors_worse_than_original_cumulative_stream(self):
        for row in self.results["CKAD41"]["dev_rows"]:
            self.assertLess(row["absolute_gain"],0)
        self.assertEqual(self.results["CKAD41"]["original_ci_run"],44442044268)

    def test_partial_causal_evidence_and_active_intervention_not_decisive(self):
        improved=self.results["CKAD44"]["dev_rows"]
        self.assertTrue(all(row["absolute_gain"]>0 for row in improved))
        self.assertTrue(all(not row["gain_threshold_met"] for row in improved))
        active=self.results["CKAD45"]["dev_rows"]
        self.assertLess(active[0]["absolute_gain"],0)
        self.assertGreater(active[1]["absolute_gain"],0)
        self.assertTrue(all(not row["gain_threshold_met"] for row in active))

    def test_unseen_symbols_lost_to_exact_balanced_inference(self):
        rows=self.results["CKAD46"]["dev_rows"]
        self.assertTrue(all(row["absolute_gain"]<0 for row in rows))
        report=A.load_archive(46)
        self.assertTrue(all(x["primary_pool"]["best_nonprivileged_control_name"]=="exact_balanced_mapping"
                            for x in report["results"]))

    def test_new_fourway_models_not_decisive_against_tabular(self):
        for n in (47,48,49):
            rows=self.results[f"CKAD{n}"]["dev_rows"]
            self.assertTrue(all(0<row["absolute_gain"]<.010 for row in rows))
            self.assertTrue(all("tabular" in row["specified_comparator"] for row in rows))
        q=A.load_archive(48)
        self.assertTrue(all(x["pooled_late_return"]["candidate"]==
                            x["pooled_late_return"]["exact_structure_BMA"] for x in q["cases"]))
        p=A.load_archive(49)
        self.assertTrue(all(x["frozen_checks"]["hidden_exception_and_operator_recovered_by_last_scored_probe"]
                            for x in p["original_seed_outcomes"]))

    def test_original_ci_source_sha_receipts_not_mixed_between_studies(self):
        all_source=set()
        for n in range(41,50):
            x=self.results[f"CKAD{n}"]
            self.assertEqual(x["original_source_sha"],A.SOURCE[n])
            self.assertEqual(x["original_ci_run"],A.RUNS[n])
            self.assertEqual(len(x["dev_rows"]),2)
            self.assertNotIn(x["original_source_sha"],all_source)
            all_source.add(x["original_source_sha"])
        self.assertEqual(len(all_source),9)

if __name__=="__main__":
    unittest.main()
