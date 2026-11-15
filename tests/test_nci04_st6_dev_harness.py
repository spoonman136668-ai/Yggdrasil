"""ST6 genuine original training-only harness, fake held classifier negatives.

Held law IDs, negative mechanism source, scientific first use are NOT run
or imported as data here. Numeric classifier fixtures are invented ONLY
to test strict stop criteria, not observations or scientific results.
"""
import unittest

from research.nci04_st6.dev_compare import (
    guard,run_original,MODELS,load_checkpoint,classify
)
from research.nci04_st6.matched_controls import (
    create_models,restored_models
)


def fake_dev():
    models=MODELS
    held_rows=[]
    for law in (29,31,37,41):
        for seed in range(201,209):
            v={n:.25 for n in models}
            v.update(candidate=.003,symbolic8=.003,st5_exact_key=.25,
                     recurrent45=.22,no_b=.23,shuffle=.20,erase=.25)
            held_rows.append({
                "law_evaluator_only":law,"seed_evaluator_only":seed,
                "source_actions":80,"preaction_probe_brier":v,
                "all_model_cold_restarts":len(models),
                "model_cpu_wall_ns":{
                    n:{"wall_ns":100,"cpu_ns":90} for n in models
                },
                "source_actor_wall_ns":1000,
                "peak_shared_process_rss_bytes":10000
            })
    neg=[
        {"law_evaluator_only":law,"source_actions":80,
         "preaction_probe_brier":{
             n:.24 for n in models
         },"all_model_cold_restarts":len(models),
         "model_cpu_wall_ns":{
             n:{"wall_ns":100,"cpu_ns":90} for n in models
         },"source_actor_wall_ns":1000,
         "peak_shared_process_rss_bytes":10000}
        for law in (43,47)
    ]
    return (
        {"original_source_steps":2560,"source_receipts":held_rows,
         "pooled_probe_brier":{
             n:held_rows[0]["preaction_probe_brier"][n] for n in models
         }},
        {"original_source_steps":160,"source_receipts":neg,
         "pooled_probe_brier":{n:.24 for n in models}},
        {"interference_real_original_actions":640,
         "candidate_retained_gain_fraction":1.,
         "candidate_absolute_brier_change":0.,
         "interference_model_cost":{
             n:{"wall_ns":100,"cpu_ns":90} for n in models
         },
         "interference_source_actor_wall_ns":1000,
         "before":{"model_cost":{
             n:{"wall_ns":100,"cpu_ns":90} for n in models
         },"source_actor_wall_ns":1000},
         "after":{"model_cost":{
             n:{"wall_ns":100,"cpu_ns":90} for n in models
         },"source_actor_wall_ns":1000}},
        {"model_training_cpu_wall_ns":{
            n:{"wall_ns":100,"cpu_ns":90} for n in models
         },
         "training_source_wall_ns":1000,
         "training_actor_wall_ns":100,
         "model_capacity_receipts":{
            "candidate":{"learned_uint32_error_support_bytes":64},
            "symbolic8":{"learned_uint32_error_support_bytes":64}
         }}
    )


class ST6FrozenTrainingFixture(unittest.TestCase):
    def test_immutable_source_model_and_frozen_gate_before_held(self):
        data=guard()
        self.assertEqual(
            data["status"],
            "PREREG_FROZEN_BEFORE_ST6_SOURCE_CODE_OR_OUTCOMES"
        )
        self.assertFalse(data["authority"]["merge"])
        self.assertFalse(data["authority"][
            "independent_scientific_first_use"
        ])

    def test_training_original_action_sequence_identical_all_variants(self):
        models=create_models()
        report=run_original(3,100,0,models,"train",True,cold=True)
        self.assertEqual(report["original_source_steps"],5)
        self.assertEqual(report["all_model_cold_restores"],len(MODELS))
        self.assertFalse(report["source_private_law_or_rule_passed_to_learner"])
        self.assertEqual(models["candidate"].training_probes,1)
        self.assertEqual(models["symbolic8"].fitted,1)
        self.assertEqual(models["st5_exact_key"].learned_probes,1)
        self.assertEqual(models["recurrent45"].train_steps,5)
        self.assertEqual(len(bytes.fromhex(
            report["original_event_bytes_hex"])),5*(8+1+8+8)
        )

    def test_all_seven_model_checkpoints_restore_byte_exact(self):
        models=create_models()
        run_original(3,100,0,models,"train",True)
        blobs={n:models[n].snapshot() for n in models}
        restored=restored_models(blobs)
        self.assertTrue(all(
            restored[n].snapshot()==blobs[n] for n in restored
        ))

    def test_training_only_recall_never_updates_fitted_operator(self):
        models=create_models()
        for trial in range(8):
            run_original(3,100,trial,models,"train",True)
        state={n:models[n].snapshot() for n in MODELS}
        rec=run_original(5,100,0,models,"recall",False)
        self.assertLess(rec["preaction_probe_brier"]["candidate"],.05)
        self.assertEqual(models["candidate"].training_probes,8)
        self.assertEqual(models["symbolic8"].fitted,8)
        self.assertTrue(rec["protected_scientific_first_use"] is False)
        self.assertNotEqual(state["candidate"],models["candidate"].snapshot())
        # The only changes during inference are episodic or retrieval
        # metadata: learned mismatches/support remain byte-identical.
        self.assertEqual(models["candidate"].mismatches,
                         restored_models({n:(
                             state[n] if n=="candidate" else models[n].snapshot()
                         ) for n in MODELS})["candidate"].mismatches)

    def test_fabricated_scoring_fixture_positive_is_only_dev(self):
        held,neg,rec,ck=fake_dev()
        scored=classify(held,neg,rec,ck)
        self.assertTrue(all(scored["frozen_checks"].values()))
        self.assertFalse(scored["native_unique_advantage_over_strong_symbolic"])
        self.assertEqual(scored["development_disposition"],
                         "COMPOSITIONAL_DEV_SIGNAL_NOT_SCIENTIFIC_PASS")

    def test_no_B_cue_and_unfamiliar_operator_cannot_be_waived(self):
        held,neg,rec,ck=fake_dev()
        held["pooled_probe_brier"]["no_b"]=.02
        self.assertEqual(classify(held,neg,rec,ck)[
            "development_disposition"],"DEV_NO_GO")
        held,neg,rec,ck=fake_dev()
        neg["pooled_probe_brier"]["candidate"]=.03
        self.assertFalse(classify(held,neg,rec,ck)["frozen_checks"][
            "different_operator_negative_Brier_ge_0_10"
        ])

    def test_retention_and_full_process_cost_are_strict(self):
        held,neg,rec,ck=fake_dev()
        rec["candidate_retained_gain_fraction"]=.94
        self.assertEqual(classify(held,neg,rec,ck)[
            "development_disposition"],"DEV_NO_GO")
        held,neg,rec,ck=fake_dev()
        ck["model_training_cpu_wall_ns"]["candidate"][
            "wall_ns"]=10**9
        self.assertFalse(classify(held,neg,rec,ck)["frozen_checks"][
            "whole_source_actor_model_wall_ratio_le_1_5"
        ])

    def test_incomplete_original_held_data_rejected(self):
        held,neg,rec,ck=fake_dev()
        held["source_receipts"]=held["source_receipts"][:-1]
        with self.assertRaisesRegex(ValueError,"FROZEN_SOURCE_SCOPES_MISSING"):
            classify(held,neg,rec,ck)


if __name__=="__main__":unittest.main()
