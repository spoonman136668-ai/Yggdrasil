"""ST4 actual-source training harness: source-only and fabricated negatives.

One predeclared already-used training law/seed is allowed for interface
dry-run. ALL 'held' numerical data in score fixtures is handwritten, NOT
produced from predeclared held law source or independent science.
"""
import copy
import unittest

from research.nci04_st4.dev_compare import (
    MODELS, create_models, run_law_seed, classify,restore_models,
    guard_source, cold_retention
)
from research.nci04_st4.native_credit import NativeCausal8


def fake_receipt(law,seed,candidate=.08,control=.18):
    n={name:control for name in MODELS}
    n["candidate"]=candidate
    n["erase"]=.2
    return {
        "law_evaluator_only":law,"seed_evaluator_only":seed,
        "source_real_actions":64,"cold_restarts":2*len(MODELS),
        "paired_true_opposing_bits":90,
        "paired_candidate_directionally_correct_bits":85,
        "paired_mean_candidate_probability_separation":.6,
        "shared_process_peak_rss_bytes":100000,
        "source_wall_ns":1500,
        "blind_actor_wall_ns":150,
        "model_cost_ns":{
            k:{"wall_ns":1000,"cpu_ns":850} for k in MODELS
        },
        "preaction_brier":{
            k:{"all":v,"probe":v,"treat_probe":v,
               "control_probe":v}
            for k,v in n.items()
        },
    }


def fabricated_source_results():
    return [
        fake_receipt(law,seed) for law in (29,31,37,41)
        for seed in (201,202,203,204,205,206,207,208)
    ]


def capacity():
    return {
        "candidate":{"learned_uint8_counter_bytes":3456},
        "lag_count":{"learned_uint8_counter_bytes":3456}
    }


class ST4FrozenDevelopmentHarnessTest(unittest.TestCase):
    def test_frozen_immutable_original_stage0_parent(self):
        p=guard_source()
        self.assertEqual(p["scientific_status"],"PREREG_ONLY")
        self.assertFalse(p["authority"]["protected_first_use"])

    def test_one_training_seed_real_original_source_model_interface(self):
        models=create_models()
        report=run_law_seed(
            3,100,models,"train",True,state_sha=True
        )
        self.assertEqual(report["source_real_actions"],64)
        self.assertEqual(report["cold_restarts"],2*len(MODELS))
        self.assertEqual(len(report["original_pair_sha256"]),16)
        self.assertEqual(len(report["candidate_per_actual_action_state_hash"]),64)
        self.assertTrue(report["model_received_private_source_fields"] is False)
        self.assertFalse(report["protected_scientific_first_use"])
        self.assertIsNone(report["preaction_brier"])
        self.assertEqual(models["candidate"].updates,64)
        self.assertEqual(models["recurrent45"].train_steps,64)
        self.assertEqual(models["lag_count"].updates,64)

    def test_cold_snapshot_exact_same_training_data_and_capacities(self):
        models=create_models()
        self.assertEqual(set(models),set(MODELS))
        frozen={n:m.snapshot() for n,m in models.items()}
        recovered=restore_models(frozen)
        for n in MODELS:
            self.assertEqual(recovered[n].snapshot(),frozen[n])
            self.assertEqual(recovered[n].predict((0,)*8,3),
                             models[n].predict((0,)*8,3))
        self.assertEqual(
            recovered["candidate"].accounting()["learned_uint8_counter_bytes"],
            recovered["lag_count"].accounting()["learned_uint8_counter_bytes"]
        )
        self.assertEqual(recovered["recurrent45"].accounting()[
            "trained_coefficients"],45)

    def test_fabricated_positive_only_means_development_pending_portability(self):
        result=classify(
            fabricated_source_results(),
            {"passed":True},capacity()
        )
        self.assertEqual(result["development_disposition"],
                         "DEV_SIGNAL_PENDING_CROSS_OS_NOT_SCIENTIFIC")
        self.assertTrue(all(result["frozen_checks"].values()))
        self.assertEqual(result["true_pair_opposed_outcome_bits"],2880)

    def test_no_delay_margin_fails_frozen_hypothesis_even_when_fast(self):
        fake=fabricated_source_results()
        for row in fake:
            row["preaction_brier"]["no_delay"]["treat_probe"]=.08
        result=classify(fake,{"passed":True},capacity())
        self.assertEqual(result["development_disposition"],"DEV_NO_GO")
        self.assertFalse(result["frozen_checks"][
            "causal_credit_beats_both_frozen_ablations_by_0_02"
        ])

    def test_retention_ablation_and_cost_cannot_be_waived(self):
        fake=fabricated_source_results()
        result=classify(fake,{"passed":False},capacity())
        self.assertEqual(result["development_disposition"],"DEV_NO_GO")
        self.assertFalse(result["frozen_checks"][
            "cold_interference_retained_95pct_chance_corrected_gain"
        ])
        fake[0]["model_cost_ns"]["candidate"]["wall_ns"]=999999999
        result=classify(fake,{"passed":True},capacity())
        self.assertFalse(result["frozen_checks"][
            "whole_source_actor_model_wall_ratio_under_1_5"
        ])

    def test_interference_probe_executes_only_predeclared_training_laws(self):
        # Runs on SOURCE training + a declared negative control, not held
        # development, not protected scientific first-use. DO NOT demand
        # positive retention here: that would tune the experiment.
        r=cold_retention()
        self.assertEqual(r["original_law_evaluator_only"],3)
        self.assertEqual(len(r["unrelated_interfering_training_laws"]),8)
        self.assertFalse(r["cold_recall_fitted_original_law"])
        self.assertFalse(r["protected_scientific_first_use"])
        self.assertEqual(r["frozen_minimum_retained_ratio"],.95)
        self.assertTrue(
            0<=r["chance_corrected_gain_retained_ratio"]<=1
        )

    def test_capacity_missing_or_nonmatching_counter_budget_fails(self):
        fake=fabricated_source_results()
        bad=capacity()
        bad["lag_count"]["learned_uint8_counter_bytes"]=100
        result=classify(fake,{"passed":True},bad)
        self.assertEqual(result["development_disposition"],"DEV_NO_GO")
        self.assertFalse(result["frozen_checks"][
            "candidate_and_lag_count_counter_byte_budget_equal"
        ])

    def test_incomplete_development_cohort_refused(self):
        with self.assertRaisesRegex(ValueError,"UNQUALIFIED_HELD_COHORT"):
            classify(fabricated_source_results()[:-1],
                     {"passed":True},capacity())


if __name__=="__main__":
    unittest.main()
