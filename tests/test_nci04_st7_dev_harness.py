"""ST7 original TRAIN-only comparator/evaluator and strict fake score tests.

Every positive/negative metric below is a HANDWRITTEN CLASSIFIER FIXTURE,
not held or protected scientific data. Only actual training law3/seed100
source actions execute. No private law/correct coefficient in model API.
"""
import unittest

from research.nci04_st7.dev_compare import (
    exact_guard,run_episode,MODEL_NAMES,classify,
    restored_models,fixed_evidence
)
from research.nci04_st7.matched_controls import models
from research.nci04_st7.private_world import original_episode


def fake_all():
    names=MODEL_NAMES
    heldrows=[]
    for law in (29,31,37,41):
        for seed in range(201,209):
            metrics={n:.25 for n in names}
            metrics.update(candidate=.0001,gf2_conventional=.0001,
                           logistic36=.18,st6_menu=.30,
                           linear_only=.28,no_b=.25,erase=.25)
            heldrows.append({
                "law_evaluator_only":law,"seed_evaluator_only":seed,
                "original_source_actions":80,"probe_brier":metrics,
                "all_model_cold_restarts":len(names),
                "model_cpu_wall_ns":{
                    n:{"wall_ns":100,"cpu_ns":90} for n in names
                },
                "source_actor_wall_ns":1000,"shared_peak_rss_bytes":98765
            })
    negative=[
        {"law_evaluator_only":law,"original_source_actions":80,
         "probe_brier":{n:.25 for n in names},
         "all_model_cold_restarts":len(names),
         "model_cpu_wall_ns":{
             n:{"wall_ns":100,"cpu_ns":90} for n in names
         },
         "source_actor_wall_ns":1000,"shared_peak_rss_bytes":98765}
        for law in (43,47)
    ]
    return (
        {"actual_original_source_actions":2560,
         "source_receipts":heldrows,
         "pooled_probe_brier":heldrows[0]["probe_brier"]},
        {"actual_original_source_actions":160,
         "source_receipts":negative,
         "pooled_probe_brier":{n:.25 for n in names}},
        {"interference_original_source_actions":640,
         "candidate_chance_adjusted_retention":1.,
         "original_probe_brier_absolute_deterioration":0.,
         "interference_model_cost":{
             n:{"wall_ns":100,"cpu_ns":90} for n in names
         },
         "interference_source_actor_wall_ns":1000,
         "original_before":{
             "model_cost":{
                 n:{"wall_ns":100,"cpu_ns":90} for n in names
             },"source_actor_wall_ns":1000
         },
         "original_after":{
             "model_cost":{
                 n:{"wall_ns":100,"cpu_ns":90} for n in names
             },"source_actor_wall_ns":1000
         }},
        {"capacity":{
             "candidate":{"learned_bit_budget":1584},
             "gf2_conventional":{"learned_bit_budget":1584}
         },"model_training_cpu_wall_ns":{
             n:{"wall_ns":100,"cpu_ns":90} for n in names
         },
         "source_training_wall_ns":1000,
         "actor_training_wall_ns":100}
    )


class ST7RealTrainingBoundary(unittest.TestCase):
    def test_frozen_source_model_controls_before_any_held_rule(self):
        p=exact_guard()
        self.assertEqual(
            p["status"],
            "PREREGISTERED_BEFORE_SOURCE_CODE_OR_ANY_ST7_OUTCOME"
        )
        self.assertFalse(p["authority"]["merge"])
        self.assertFalse(p["authority"]["protected_scientific_first_use"])

    def test_all_seven_on_same_genuine_source_and_cold_restore(self):
        cohort=models()
        rec=run_episode(3,100,0,cohort,"train",True,cold=True)
        self.assertEqual(rec["original_actions"],5)
        self.assertEqual(rec["all_model_cold_restarts"],len(MODEL_NAMES))
        self.assertFalse(rec["private_law_coefficient_or_future_given_to_model"])
        self.assertFalse(rec["protected_scientific_first_use"])
        self.assertEqual(cohort["candidate"].updates,1)
        self.assertEqual(cohort["gf2_conventional"].examples,1)
        self.assertEqual(cohort["logistic36"].fitted,1)
        self.assertEqual(cohort["st6_menu"].training_probes,1)
        self.assertEqual(
            len(bytes.fromhex(rec["authentic_source_bytes_hex"])),5*25
        )
        from hashlib import sha256
        trace,_=original_episode(3,100,0)
        source_bytes=b"".join(
            bytes((*x,action,*y,*delta))
            for x,action,y,delta in trace
        )
        self.assertEqual(sha256(source_bytes).hexdigest(),
                         rec["authentic_source_sha256"])

    def test_same_source_candidate_gaussian_learn_and_hold(self):
        cohort=models()
        for t in range(16):
            run_episode(3,100,t,cohort,"train",True)
        self.assertGreater(cohort["candidate"].rank,0)
        self.assertEqual(cohort["candidate"].rank,
                         cohort["gf2_conventional"].rank)
        snapshots={n:m.snapshot() for n,m in cohort.items()}
        copied=restored_models(snapshots)
        self.assertEqual(set(copied),set(MODEL_NAMES))
        self.assertTrue(all(copied[n].snapshot()==snapshots[n]
                            for n in MODEL_NAMES))
        persistent={n:fixed_evidence(m) for n,m in cohort.items()}
        rec=run_episode(5,101,2,cohort,"recall",False)
        self.assertEqual(rec["original_actions"],5)
        self.assertTrue(all(fixed_evidence(cohort[n])==persistent[n]
                            for n in MODEL_NAMES if n!="erase"))

    def test_fabricated_frozen_gate_positive_is_dev_only(self):
        out=classify(*fake_all())
        self.assertTrue(all(out["frozen_checks"].values()))
        self.assertEqual(out["development_disposition"],
                         "QUADRATIC_RULE_DISCOVERY_DEV_SIGNAL_NOT_INDEPENDENT_SCIENCE")
        self.assertFalse(out["native_unique_advantage_over_GF2_conventional"])

    def test_frozen_nonlinearity_ablations_are_not_waived(self):
        held,neg,ret,c=fake_all()
        held["pooled_probe_brier"]["linear_only"]=.03
        result=classify(held,neg,ret,c)
        self.assertEqual(result["development_disposition"],"DEV_NO_GO")
        self.assertFalse(result["frozen_checks"][
            "causal_quadratic_vs_linear_gain_ge_0_10"
        ])

    def test_negative_new_rule_and_retention_are_strict(self):
        held,neg,ret,c=fake_all()
        neg["pooled_probe_brier"]["candidate"]=.01
        scored=classify(held,neg,ret,c)
        self.assertFalse(scored["frozen_checks"][
            "unknown_different_rule_negative_Brier_ge_0_10"
        ])
        held,neg,ret,c=fake_all()
        ret["candidate_chance_adjusted_retention"]=.94
        self.assertFalse(classify(held,neg,ret,c)["frozen_checks"][
            "eight_interfering_laws_retained_chance_gain_ge_0_95"
        ])

    def test_persistent_byte_budget_and_wall_limit_cannot_be_ignored(self):
        held,neg,ret,c=fake_all()
        c["capacity"]["gf2_conventional"]["learned_bit_budget"]=1600
        self.assertEqual(classify(held,neg,ret,c)[
            "development_disposition"],"DEV_NO_GO")
        held,neg,ret,c=fake_all()
        c["model_training_cpu_wall_ns"]["candidate"]["wall_ns"]=10**9
        self.assertFalse(classify(held,neg,ret,c)["frozen_checks"][
            "charged_whole_process_wall_ratio_le_1_5"
        ])

    def test_mismatched_held_cohort_refused(self):
        held,neg,ret,c=fake_all()
        held["source_receipts"]=held["source_receipts"][:-1]
        with self.assertRaisesRegex(ValueError,"FROZEN_ORIGINAL_SOURCE_COHORT_MISSING"):
            classify(held,neg,ret,c)


if __name__=="__main__":unittest.main()
