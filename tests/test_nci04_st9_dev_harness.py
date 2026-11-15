"""ST9 original training-only custody and fabricated frozen stop tests.

Classifier score fixtures are synthetic unit values, NOT held outcomes.
Only eight original source TRAIN interventions are executed by real
model tests. All held, negative and protected data remain unopened.
"""
from pathlib import Path
import tempfile
import unittest

from research.nci04_st9.dev_compare import (
    guard,train_once,load_training,classify,NAMES,
    original_episode,ACTOR_GROUPS,PROBES
)
from research.nci04_st9.matched_controls import (
    make_models,restore_all,active_plan
)


def fake_frozen_dev():
    names=NAMES
    probes={n:.25 for n in names}
    probes.update(candidate=.0001,adaptive_conventional=.0001,
                  full_active=.0001,no_replay=.16,no_growth=.31,
                  erase=.25,blind_dispersed=.20,blind_repeat=.35)
    rows=[]
    for law in (29,31,37,41):
        for seed in (201,202,203,204):
            rows.append({
                "law_evaluator_only":law,"seed_evaluator_only":seed,
                "real_source_steps":32,"probe_brier":dict(probes),
                "all_model_cold_restores":len(names),
                "model_cpu_wall_ns":{
                    n:{"wall_ns":100,"cpu_ns":90} for n in names
                },
                "source_actor_wall_ns":1000,
                "shared_worker_peak_rss":4000
            })
    negatives=[]
    for law in (43,47):
        negatives.append({
            "law_evaluator_only":law,"seed_evaluator_only":205,
            "real_source_steps":32,
            "probe_brier":{n:.25 for n in names},
            "all_model_cold_restores":len(names),
            "model_cpu_wall_ns":{
                n:{"wall_ns":100,"cpu_ns":90} for n in names
            },
            "source_actor_wall_ns":1000,
            "shared_worker_peak_rss":4000
        })
    ret={
        "real_interference_source_actions":16,
        "native_retained_chance_adjusted_gain":1.,
        "native_cold_original_probe_Brier_change":0.,
        "interference_model_cpu_wall_ns":{
            n:{"wall_ns":100,"cpu_ns":90} for n in names
        },
        "interference_source_actor_wall_ns":1000,
        "before":{"model_cpu_wall_ns":{
            n:{"wall_ns":100,"cpu_ns":90} for n in names
        },"source_actor_wall_ns":1000},
        "after":{"model_cpu_wall_ns":{
            n:{"wall_ns":100,"cpu_ns":90} for n in names
        },"source_actor_wall_ns":1000},
    }
    train={
        "native_original_contradictions":1,
        "native_actual_growth_events":1,
        "native_trigger_on_original_intervention":3,
        "native_learned_quadratic_rank":8,
        "native_post_growth_conflicts":0,
        "native_replayed_pre_growth_experiences":2,
        "original_train_source_actions_per_arm":{n:16 for n in names},
        "capacity_receipts":{
            "candidate":{"learned_GF2_evidence_bits_max":128},
            "adaptive_conventional":{"max_GF2_learned_augmented_bits":128}
        },
        "model_training_cpu_wall_ns":{
            n:{"wall_ns":100,"cpu_ns":90} for n in names
        },
        "source_train_wall_ns":1000,
        "actor_train_wall_ns":100,
    }
    return (
        {"actual_original_source_actions":512,
         "records":rows,"pooled_brier":probes},
        {"actual_original_source_actions":64,
         "records":negatives,
         "pooled_brier":{n:.25 for n in names}},
        ret,train
    )


class ST9PublicOnlyDevGate(unittest.TestCase):
    def test_exhaustive_frozen_source_protocol_custody(self):
        d=guard()
        self.assertEqual(
            d["status"],"FROZEN_BEFORE_ST9_ORIGINAL_SOURCE_OR_MODEL_OR_OUTCOME"
        )
        self.assertFalse(d["authority"]["merge"])
        self.assertFalse(d["authority"]["protected_first_use"])
        self.assertEqual(active_plan(),PROBES["active"])

    def test_exact_one_train_checkpoint_on_only_16_real_actions_per_arm(self):
        with tempfile.TemporaryDirectory() as folder:
            out=Path(folder)/"train.json"
            d=train_once(out)
            reread,sha=load_training(out)
            self.assertEqual(d,reread)
            self.assertEqual(len(sha),64)
            self.assertEqual(d["original_train_source_actions_per_arm"],
                             {n:16 for n in NAMES})
            self.assertEqual(d["native_actual_growth_events"],1)
            self.assertEqual(d["native_learned_quadratic_rank"],8)
            self.assertLess(d["no_replay_control_rank"],8)
            self.assertEqual(d["adaptive_conventional_rank"],8)
            self.assertEqual(d["full_active_conventional_rank"],8)
            self.assertTrue(d["held_worlds_not_opened"])
            self.assertTrue(d["alternative_rule_not_opened"])
            self.assertFalse(d["protected_scientific_first_use"])
            clones=restore_all(d["model_states"])
            self.assertTrue(all(
                clones[n].snapshot()==d["model_states"][n] for n in NAMES
            ))

    def test_all_arms_public_only_source_and_correct_action_count(self):
        m=make_models()
        for name,model in m.items():
            active=ACTOR_GROUPS[name]
            probe=PROBES["active" if active=="active" else active][0]
            rec=original_episode(3,100,0,probe,{name:model},True,
                                 cold=True)
            self.assertEqual(rec["genuine_source_steps"],2)
            self.assertEqual(rec["original_cold_model_restores"],1)
            self.assertFalse(rec["private_source_law_or_coefficients_given_to_models"])
            self.assertEqual(len(bytes.fromhex(
                rec["real_source_action_bytes_hex"])),2*(8+1+8+8))

    def test_fabricated_positive_does_not_grant_independent_science(self):
        result=classify(*fake_frozen_dev())
        self.assertTrue(all(result["checks"].values()))
        self.assertEqual(result["development_disposition"],
            "BUDGETED_MEMORY_REPAIR_DEV_SIGNAL_NOT_SCIENTIFIC_PASS")
        self.assertFalse(result[
            "native_unique_advantage_over_conventional_adaptive"])

    def test_equal_no_replay_is_frozen_no_go(self):
        held,neg,ret,train=fake_frozen_dev()
        held["pooled_brier"]["no_replay"]=.0001
        result=classify(held,neg,ret,train)
        self.assertFalse(result["checks"][
            "replay_improves_matched_no_replay_ge_0_06"])
        self.assertEqual(result["development_disposition"],"DEV_NO_GO")

    def test_blind_information_advantage_and_causal_repair_must_be_real(self):
        held,neg,ret,train=fake_frozen_dev()
        held["pooled_brier"]["blind_dispersed"]=.03
        self.assertFalse(classify(held,neg,ret,train)["checks"][
            "active_improves_strong_blind_dispersed_ge_0_06"])
        held,neg,ret,train=fake_frozen_dev()
        train["native_actual_growth_events"]=0
        self.assertFalse(classify(held,neg,ret,train)["checks"][
            "true_linear_contradiction_triggers_one_repair"])

    def test_genuine_eight_action_budget_and_full_cost_nonwaivable(self):
        held,neg,ret,train=fake_frozen_dev()
        train["original_train_source_actions_per_arm"]["candidate"]=18
        self.assertEqual(classify(held,neg,ret,train)[
            "development_disposition"],"DEV_NO_GO")
        held,neg,ret,train=fake_frozen_dev()
        train["model_training_cpu_wall_ns"]["candidate"]["wall_ns"]=10**9
        self.assertFalse(classify(held,neg,ret,train)["checks"][
            "end_to_end_source_actor_training_evaluation_ratio_le_1_5"])

    def test_new_mechanism_negative_and_retention_cannot_be_waived(self):
        held,neg,ret,train=fake_frozen_dev()
        neg["pooled_brier"]["candidate"]=.02
        self.assertFalse(classify(held,neg,ret,train)["checks"][
            "unseen_different_rule_negative_Brier_ge_0_10"])
        held,neg,ret,train=fake_frozen_dev()
        ret["native_retained_chance_adjusted_gain"]=.94
        self.assertFalse(classify(held,neg,ret,train)["checks"][
            "after_eight_interferences_retained_gain_ge_0_95"])

    def test_incomplete_original_held_data_cannot_be_scored(self):
        held,neg,ret,train=fake_frozen_dev()
        held["records"]=held["records"][:-1]
        with self.assertRaisesRegex(
            ValueError,"FROZEN_SOURCE_AND_ACTION_BUDGET_MISMATCH"
        ):
            classify(held,neg,ret,train)


if __name__=="__main__":
    unittest.main()
