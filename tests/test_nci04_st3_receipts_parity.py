"""ST3 receipt-only fake regression controls. No held sources are opened."""
import copy
import unittest

from research.nci04_st3.receipts_parity import (
    compare_receipts,RESULT_SCHEMA,COST_KEY
)


def fixture(cost_pass=False):
    models=("candidate","recurrent45","action_count","no_delay",
            "sham","episode_erase")
    brier={name:.1 for name in models}
    sample={
        "law_id_evaluator_only":29,
        "seed_evaluator_only":201,
        "phase":"held",
        "actual_source_steps":64,
        "source_action_outcome_sha256":"a"*64,
        "delayed_action2_followed_by_action3_steps":16,
        "cold_model_restarts":6,
        "learner_received_private_law_or_mask":False,
        "independent_science_first_use":False,
        "candidate_trained_observed_actions":100,
        "candidate_forks":4,
        "candidate_retrievals":2,
        "candidate_per_action_state_sha_chain":"b"*64,
        "preaction_brier":brier,
        "delayed_action2_to_action3_brier":brier
    }
    checks={
        "frozen_delay_margin":False,
        "frozen_retention":False,
        COST_KEY:cost_pass
    }
    return {
        "schema":RESULT_SCHEMA,
        "original_source_kind":"IN_HOUSE_SYNTHETIC_DEV_ONLY",
        "frozen_protocol_blob":"ce51862f6b5af6a130b6ad93c30f019131bfeb16",
        "training_checkpoint_sha256":"c"*64,
        "training_source_trace_sha256":"d"*64,
        "source_stage0":{"disposition":"SOURCE_TASK_IDENTIFIABLE_DEV_ONLY"},
        "held_development_opened":True,
        "protected_scientific_first_use":False,
        "scientific_pass":False,
        "original_frozen_hypothesis_changed_after_observation":False,
        "held_source_receipts":[copy.deepcopy(sample) for _ in range(32)],
        "retention_probe":{"pass":False,
                           "retained_chance_corrected_brier_gain_ratio":0.0},
        "metrics":{
            "checks":checks,
            "pooled_brier":brier,
            "held_law_brier":{"29":brier},
            "delayed_after_action2_to_action3_brier":brier,
            "whole_process_modelled_wall_ratio":(
                1.8 if cost_pass is False else 1.1
            ),
            "pre_cross_os_disposition":"DEV_NO_GO"
        }
    }


class ReceiptOnlyParityFixtures(unittest.TestCase):
    def test_cost_threshold_disagreement_is_frozen_negative_not_infra(self):
        a=fixture(False)
        b=fixture(True)
        r=compare_receipts(a,b)
        self.assertFalse(r["cost_threshold_same_across_os"])
        self.assertEqual(r["disposition"],"DEV_NO_GO")
        self.assertTrue(r["candidate_native_integer_checkpoint_sha_exact_cross_os"])
        self.assertTrue(r["all_preaction_scores_equal_to_1e_12"])
        self.assertTrue(r["no_model_or_source_reexecuted_during_receipt_analysis"])

    def test_actual_source_trace_mismatch_fails_closed(self):
        a,b=fixture(False),fixture(False)
        b["held_source_receipts"][2]["source_action_outcome_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"ORIGINAL_EVENT"):
            compare_receipts(a,b)

    def test_checkpoint_sha_mismatch_is_scientific_negative(self):
        a,b=fixture(False),fixture(False)
        b["held_source_receipts"][1][
            "candidate_per_action_state_sha_chain"]="0"*64
        r=compare_receipts(a,b)
        self.assertFalse(r["candidate_native_integer_checkpoint_sha_exact_cross_os"])
        self.assertEqual(r["disposition"],"DEV_NO_GO")

    def test_frozen_non_cost_check_difference_fails_closed(self):
        a,b=fixture(False),fixture(False)
        b["metrics"]["checks"]["frozen_delay_margin"]=True
        with self.assertRaisesRegex(ValueError,"NONCOST_CLASSIFIER_DRIFT"):
            compare_receipts(a,b)


if __name__=="__main__":
    unittest.main()
