"""ST5 frozen source-bound model-harness tests, no held DEV opened.

Only original training law 3 is executed; all scored unfamiliar-law
results in decision-fixture tests are HANDWRITTEN, not source outcomes.
No private law/seed/trial passes to model method and no scientific pass.
"""
import copy
import unittest

from research.nci04_st5.dev_compare import (
    NAMES,make_models,actual_episode,original_recall,
    restored_suite,model_counters,classify
)
from research.nci04_st5.diagnostic_world import run_original_episode
from research.nci04_st5.native_memory import canonical
from research.nci04_st5.matched_controls import brier


def fake_retention():
    pre={n:.01 for n in NAMES}
    post={n:.30 for n in NAMES}
    post["candidate"]=.012
    post["residual_count"]=.012
    post["raw_count"]=.23
    post["recurrent45"]=.24
    post["no_cue"]=.25
    post["erase"]=.25
    return {
        "original_before":{"preaction_delayed_probe_brier":pre},
        "original_after":{"preaction_delayed_probe_brier":post},
        "candidate_retained_chance_corrected_gain":.991,
        "post_interference_causal_bank_count":16,
        "same_16_profile_uint8_counter_budget":True
    }


def fake_unfamiliar():
    return {
        "held_development_source_receipts":[{
            "actual_source_steps":80,
            "all_models_cold_restarts":len(NAMES),
            "source_actor_wall_ns":1000,
            "model_cpu_wall_ns":{
                n:{"cpu_ns":100,"wall_ns":150} for n in NAMES
            },
            "peak_shared_worker_rss_bytes":123456
        } for _ in range(32)],
        "original_held_source_actions":2560,
        "model_never_fitted_unfamiliar_laws":True,
        "held_development_probe_brier":{
            n:.25 for n in NAMES
        }
    }


class ST5PreheldEvaluatorFixture(unittest.TestCase):
    def test_original_five_step_actor_and_true_source_hash_match(self):
        m=make_models()
        result=actual_episode(3,100,0,m,"train",True,cold_check=True)
        self.assertEqual(result["genuine_original_source_steps"],5)
        self.assertEqual(result["cold_restarts"],len(NAMES))
        self.assertFalse(result["private_source_fields_given_to_model"])
        self.assertFalse(result["protected_first_use"])
        self.assertIsNone(result["preaction_delayed_probe_brier"])
        import hashlib
        actual=hashlib.sha256()
        history,cue=run_original_episode(3,100,0)
        for x,action,y,delta in history:
            actual.update(bytes((*x,action,*y,*delta)))
        self.assertEqual(actual.hexdigest(),result["source_sha256"])
        original_bytes=b"".join(
            bytes((*x,action,*y,*delta))
            for x,action,y,delta in history
        )
        self.assertEqual(
            bytes.fromhex(result["original_public_event_bytes_hex"]),
            original_bytes
        )
        for name in NAMES:
            self.assertGreater(result["model_cost_ns"][name]["wall_ns"],0)

    def test_exact_same_source_actions_for_conventional_and_native(self):
        models=make_models()
        for trial in range(4):
            actual_episode(3,100,trial,models,"train",True)
        self.assertEqual(models["candidate"].learned_probes,4)
        self.assertEqual(models["recurrent45"].train_steps,20)
        self.assertEqual(models["raw_count"].updates,4)
        self.assertEqual(models["residual_count"].updates,4)
        self.assertEqual(
            models["candidate"].accounting()[
                "learned_uint8_counter_capacity_bytes"],
            models["residual_count"].accounting()[
                "learned_uint8_counter_capacity_bytes"]
        )

    def test_retention_probe_is_source_real_and_cannot_fit_any_model(self):
        models=make_models()
        for trial in range(16):
            actual_episode(3,100,trial,models,"train",True)
        state={n:model_counters(models[n]) for n in NAMES}
        receipt=original_recall(models)
        self.assertEqual(receipt["actual_original_source_actions"],80)
        self.assertFalse(receipt["learned_bank_write_during_recall"])
        self.assertEqual(receipt["cold_model_restarts"],len(NAMES))
        for n in NAMES:
            if n!="erase":
                self.assertEqual(model_counters(models[n]),state[n])
        self.assertLess(
            receipt["preaction_delayed_probe_brier"]["candidate"],.25
        )

    def test_exact_frozen_single_checkpoint_restore_of_all_seven_models(self):
        models=make_models()
        for trial in range(3):
            actual_episode(3,100,trial,models,"train",True)
        snap={n:models[n].snapshot() for n in NAMES}
        recovered=restored_suite(snap)
        self.assertEqual(set(recovered),set(NAMES))
        self.assertTrue(all(recovered[n].snapshot()==snap[n]
                            for n in NAMES))

    def test_fabricated_success_never_claims_independent_science(self):
        out=classify(fake_retention(),fake_unfamiliar())
        self.assertTrue(all(out["frozen_checks"].values()))
        self.assertEqual(out["development_disposition"],
                         "MEMORY_DEV_SIGNAL_NOT_INDEPENDENT_SCIENCE")
        self.assertFalse(out["native_method_unique_vs_equal_info_residual_count"])
        self.assertEqual(
            out["original_post_candidate_vs_exact_residual_count_abs_gap"],0
        )
        self.assertEqual(out["full_final_regression"],"UNVERIFIED")

    def test_frozen_retention_failure_never_hidden_by_zero_shot(self):
        r=fake_retention()
        r["candidate_retained_chance_corrected_gain"]=0.
        out=classify(r,fake_unfamiliar())
        self.assertEqual(out["development_disposition"],"DEV_NO_GO")
        self.assertFalse(out["frozen_checks"][
            "cold_original_retains_95pct_chance_corrected_gain"
        ])

    def test_frozen_memory_and_cost_negative_fail_closed(self):
        retention=fake_retention()
        retention["original_after"]["preaction_delayed_probe_brier"][
            "candidate"]=.245
        weird=classify(retention,fake_unfamiliar())
        self.assertFalse(weird["frozen_checks"][
            "original_cold_candidate_beats_no_cue_by_0_02"
        ])
        held=fake_unfamiliar()
        held["held_development_source_receipts"][0][
            "model_cpu_wall_ns"]["candidate"]["wall_ns"]=10**9
        out=classify(fake_retention(),held)
        self.assertFalse(out["frozen_checks"][
            "whole_source_actor_model_wall_ratio_le_1_5"
        ])
        self.assertEqual(out["development_disposition"],"DEV_NO_GO")

    def test_brier_probability_and_real_public_consequence_only(self):
        self.assertEqual(brier([.5]*8,(0,)*8),.25)
        with self.assertRaises(ValueError):
            brier([float("nan")]*8,(0,)*8)
        with self.assertRaises(ValueError):
            brier([.5]*7,(0,)*8)


if __name__=="__main__":
    unittest.main()
