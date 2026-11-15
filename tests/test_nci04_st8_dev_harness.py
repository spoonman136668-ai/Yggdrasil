"""ST8 original-source TRAIN-ONLY model custody and fake frozen gates.

No ST8 held law, different-rule negative, interference experiment or
protected scientific first-use is executed. Hand-authored numeric score
fixtures are classifier tests, NEVER science observations.
"""
import unittest

from research.nci04_st8.dev_compare import (
    guard,episode,NAMES,classify,learned_data
)
from research.nci04_st8.matched_controls import models,restored_models


def fake_comparison():
    names=NAMES
    heldrows=[]
    for law in (29,31,37,41):
        for seed in range(201,209):
            metrics={n:.25 for n in names}
            metrics.update(candidate=.0001,full_cubic=.0001,
                           adaptive_conventional=.0001,
                           st7_quadratic=.30,no_growth=.31,
                           no_replay=.25,erase=.25)
            heldrows.append({
                "law_evaluator_only":law,
                "seed_evaluator_only":seed,
                "original_source_actions":80,
                "preaction_probe_Brier":metrics,
                "all_model_cold_restores":len(names),
                "model_cpu_wall_ns":{
                    n:{"wall_ns":100,"cpu_ns":90} for n in names
                },
                "source_actor_wall_ns":1000,
                "shared_peak_rss_bytes":123456
            })
    neg=[
        {"law_evaluator_only":law,"original_source_actions":80,
         "preaction_probe_Brier":{n:.25 for n in names},
         "all_model_cold_restores":len(names),
         "model_cpu_wall_ns":{
             n:{"wall_ns":100,"cpu_ns":90} for n in names
         },
         "source_actor_wall_ns":1000,
         "shared_peak_rss_bytes":123456}
        for law in (43,47)
    ]
    return (
        {"actual_original_source_actions":2560,
         "receipts":heldrows,
         "pooled_Brier":heldrows[0]["preaction_probe_Brier"]},
        {"actual_original_source_actions":160,
         "receipts":neg,
         "pooled_Brier":{n:.25 for n in names}},
        {"real_interference_actions":640,
         "candidate_retained_gain_fraction":1.0,
         "candidate_cold_Brier_increase":0.,
         "interference_model_cpu_wall_ns":{
             n:{"wall_ns":100,"cpu_ns":90} for n in names
         },"interference_source_actor_wall_ns":1000,
         "before":{
             "model_cpu_wall_ns":{
                 n:{"wall_ns":100,"cpu_ns":90} for n in names
             },"source_actor_wall_ns":1000
         },
         "after":{
             "model_cpu_wall_ns":{
                 n:{"wall_ns":100,"cpu_ns":90} for n in names
             },"source_actor_wall_ns":1000
         }},
        {"candidate_actual_original_genuine_contradictions":1,
         "candidate_growth_events":1,
         "candidate_growth_on_original_step":42,
         "candidate_post_growth_conflicts":0,
         "candidate_train_public_feature_rank":92,
         "capacity":{
             "candidate":{"learned_GF2_augmented_bits_max":9200},
             "adaptive_conventional":{"learned_augmented_bits_max":9200}
         },
         "model_training_cpu_wall_ns":{
             n:{"wall_ns":100,"cpu_ns":90} for n in names
         },
         "source_training_wall_ns":1000,
         "actor_training_wall_ns":100}
    )


class ST8OriginalTrainingBoundary(unittest.TestCase):
    def test_all_frozen_precustody_is_verified_before_held(self):
        p=guard()
        self.assertEqual(p["status"],
            "FROZEN_BEFORE_ST8_SOURCE_CODE_MODEL_IMPLEMENTATION_OR_OUTCOME")
        self.assertFalse(p["authority"]["merge"])
        self.assertFalse(p["authority"]["protected_scientific_first_use"])

    def test_authentic_original_source_public_action_custody(self):
        m=models()
        result=episode(3,100,0,m,"train",True,cold=True)
        self.assertEqual(result["actual_original_source_actions"],5)
        self.assertEqual(result["all_model_true_cold_restores"],len(NAMES))
        self.assertFalse(result["private_source_rule_or_future_seen_by_model"])
        self.assertFalse(result["scientific_first_use_protected"])
        self.assertEqual(len(bytes.fromhex(result[
            "original_public_action_bytes_hex"])),5*(8+1+8+8))
        self.assertEqual(m["candidate"].updates,1)
        self.assertEqual(m["full_cubic"].examples,1)
        self.assertEqual(m["adaptive_conventional"].examples,1)
        self.assertEqual(m["st7_quadratic"].updates,1)

    def test_public_nonfit_cold_restores_all_seven(self):
        m=models()
        episode(3,100,0,m,"train",True)
        states={n:v.snapshot() for n,v in m.items()}
        recovered=restored_models(states)
        self.assertTrue(all(recovered[n].snapshot()==states[n]
                            for n in NAMES))
        frozen={n:learned_data(v) for n,v in m.items()}
        data=episode(5,101,2,m,"recall",False)
        self.assertEqual(data["actual_original_source_actions"],5)
        self.assertTrue(all(learned_data(m[n])==frozen[n]
                            for n in NAMES if n!="erase"))

    def test_fake_success_is_dev_not_unique_science(self):
        result=classify(*fake_comparison())
        self.assertTrue(all(result["frozen_checks"].values()))
        self.assertEqual(result["development_disposition"],
            "STRUCTURAL_GROWTH_DEV_SIGNAL_NOT_INDEPENDENT_SCIENCE")
        self.assertFalse(result[
            "native_unique_performance_advantage_over_adaptive"])

    def test_equal_no_replay_held_score_fails_frozen_efficacy(self):
        held,neg,ret,train=fake_comparison()
        held["pooled_Brier"]["no_replay"]=.0001
        result=classify(held,neg,ret,train)
        self.assertEqual(result["development_disposition"],"DEV_NO_GO")
        self.assertFalse(result["frozen_checks"][
            "candidate_beats_no_replay_by_0_10"
        ])

    def test_no_genuine_trigger_and_rank_fails_closed(self):
        held,neg,ret,train=fake_comparison()
        train["candidate_growth_events"]=0
        self.assertFalse(classify(held,neg,ret,train)["frozen_checks"][
            "genuine_original_quadratic_contradiction_triggered_growth"
        ])
        held,neg,ret,train=fake_comparison()
        train["candidate_train_public_feature_rank"]=91
        self.assertFalse(classify(held,neg,ret,train)["frozen_checks"][
            "candidate_full_cubic_rank92_no_postgrowth_conflicts"
        ])

    def test_held_source_and_cost_limits_are_not_waived(self):
        held,neg,ret,train=fake_comparison()
        held["receipts"]=held["receipts"][:-1]
        with self.assertRaisesRegex(
            ValueError,"FROZEN_EXPERIMENT_SOURCE_INCOMPLETE"
        ):
            classify(held,neg,ret,train)
        held,neg,ret,train=fake_comparison()
        train["model_training_cpu_wall_ns"]["candidate"]["wall_ns"]=10**9
        self.assertFalse(classify(held,neg,ret,train)["frozen_checks"][
            "measured_total_original_process_ratio_le_1_5"
        ])

    def test_other_rule_and_retention_fail_closed(self):
        held,neg,ret,train=fake_comparison()
        neg["pooled_Brier"]["candidate"]=.01
        self.assertFalse(classify(held,neg,ret,train)["frozen_checks"][
            "new_rule_negative_Brier_ge_0_10"
        ])
        held,neg,ret,train=fake_comparison()
        ret["candidate_retained_gain_fraction"]=.90
        self.assertFalse(classify(held,neg,ret,train)["frozen_checks"][
            "cold_same_rule_retention_gain_ge_0_95"
        ])


if __name__=="__main__":
    unittest.main()
