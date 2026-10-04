{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-EXPLICIT-APPLICABILITY-CONDITION-ATTRIBUTION-085",
  "program": "Yggdrasil RSI corrective tranche: explicit target-time applicability attribution",
  "question": "After Y084 changed relational class selection without producing a rescue, is the missing mechanism an explicit target-time condition that rejects ambiguous relational memory application rather than always activating the best-ranked retained class?",
  "hypothesis": "Y084 showed that the fixed context-minimax relation can change the selected retained class while still producing zero clean rescues. Freeze one categorical applicability condition over the byte-identical Y084 relational scores. UNCONDITIONAL_RELATIONAL_ACTIVATION reproduces Y084 and always activates the class selected by the full (maximum per-context minimum Hamming, sum per-context minimum Hamming, lexical class key) ordering. STRICT_MINIMAX_DOMINANCE_GATE activates that same selected class only when its primary minimax distance is strictly smaller than the primary minimax distance of every other candidate class. If the best primary minimax distance is tied and the choice would require the secondary sum or lexical tie-break, reject activation and retain original fifth-context behavior. No numeric threshold, fitted margin, held-out tuning, new representation, or capacity change is allowed.",
  "exact_parent_sha": "346666d73136c94d71e5d0ff00c2fc38a37d1103",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-explicit-applicability-condition-attribution-r1",
  "predecessor": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-RELATIONAL-REPRESENTATION-ATTRIBUTION-084",
    "github_run_id": 37225196728,
    "classification": "negative",
    "validity_pass": true,
    "observation": {
      "historical_full_pool_row_count": 17,
      "class_group_count": 2,
      "multi_context_class_group_count": 2,
      "relational_candidate_class_count": 2,
      "relational_selected_class_change_count": 1,
      "control_clean_rescue_count": 0,
      "relational_clean_rescue_count": 0,
      "relational_behavior_change_count": 1,
      "relational_partner_collateral_failure_count": 0,
      "lost_control_clean_rescue_count": 0,
      "relational_support": 0,
      "mixed_signal": 0,
      "invalid_evaluation_rows": 0
    },
    "eliminated_hypothesis": "selecting retained state by fixed context-minimax relational compatibility is sufficient to make retained state useful in the fifth context",
    "strengthened_hypothesis": "retained state may require an explicit target-time applicability condition that distinguishes uniquely supported relational matches from ambiguous matches before activation"
  },
  "cause_effect_trace": {
    "observed_failure": "Y084 changed one selected class under relational retrieval but produced zero clean rescues and no favorable mixed signal; SOURCE_CONDITIONED activation still changed behavior without improving positive-prose collateral.",
    "residual_cause_under_test": "AMBIGUOUS_RELATIONAL_MATCH_APPLIED_WITHOUT_EXPLICIT_TARGET_TIME_CONDITION",
    "exact_bounded_delta": "change only whether the byte-identical Y084 relationally selected class is activated; historical pool, class groups, per-context member keys, relation score, selected class, payload, target keys, schedules, scoring and capacity remain unchanged",
    "control_rule": "UNCONDITIONAL_RELATIONAL_ACTIVATION is byte-identical Y084 CONTEXT_MINIMAX_RELATION selection and activation",
    "gated_rule": "STRICT_MINIMAX_DOMINANCE_GATE computes the same Y084 score for every candidate class and activates the full-tuple winner only if its primary maximum per-context minimum Hamming is strictly smaller than every runner-up primary maximum; any primary tie causes safe rejection and original behavior",
    "no_threshold_rule": "no fitted distance threshold, ratio, learned margin, quantile, context parameter, held-out tuning, or post-result applicability choice",
    "useful_rejection_rule": "a gate rejection is useful only when the same-key unconditional relational activation changes behavior without increasing positive-prose collateral and the rejection introduces no partner collateral",
    "retain_revert": "Y085 is shadow attribution only; support authorizes only separately preregistered prospective applicability validation/correction, not accepted-state mutation."
  },
  "manifests": {
    "transfer": {
      "sha256": "c79f09eb3841309b38827ceffee6a14eb87973c8aa2cf817908ed05f10e5c250"
    },
    "third": {
      "sha256": "e46907e74ce92564bab657afc8d28b1a39b269bac88fb9b21092716c7ff53cb7"
    },
    "fourth": {
      "sha256": "974ecf332c019ac094ecb7098f371001fa7e37fd4b476ac7513341fff6f812e5"
    },
    "fifth_target": {
      "sha256": "7077d2b72d8954afc24f36b2971393acc11e3b345f7c3521102c20347b9c6171"
    }
  },
  "frozen_reuse": {
    "historical_pool_builder": "byte-identical Y079/Y080-Y084 17-row full eligible pool",
    "grouping": "byte-identical Y080 multi-context class-key grouping",
    "payload": "byte-identical Y080 uniform class aggregate",
    "target_keys": [
      "SOURCE_CONDITIONED",
      "LOCAL_ONLY"
    ],
    "relational_selection": "byte-identical Y084 exact 4-byte Hamming per-context minima and (max,sum,lexical class) ordering",
    "control": "UNCONDITIONAL_RELATIONAL_ACTIVATION",
    "new_mechanism": "STRICT_MINIMAX_DOMINANCE_GATE",
    "candidate_requirement": "at least two candidate classes; otherwise gate rejects because comparative dominance is undefined",
    "schedules": [
      "A-C-B",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "split": "60% training cue / 40% evaluation",
    "future_packets": 12,
    "activation_position": 7,
    "scoring": "byte-identical Y080-Y084 clean-rescue, behavior-change, partner-collateral and first-success accounting",
    "capacity": "16 total / 7 active / 9 retained",
    "heldout_applicability_choice_count": 0,
    "post_result_applicability_change_count": 0
  },
  "representation_cells": [
    "SOURCE_CONDITIONED_KEY × UNCONDITIONAL_RELATIONAL_ACTIVATION",
    "SOURCE_CONDITIONED_KEY × STRICT_MINIMAX_DOMINANCE_GATE",
    "LOCAL_ONLY_KEY × UNCONDITIONAL_RELATIONAL_ACTIVATION",
    "LOCAL_ONLY_KEY × STRICT_MINIMAX_DOMINANCE_GATE"
  ],
  "outcome_definition": {
    "clean_rescue": "active_positive_prose_collateral_schedule_count > original_positive_prose_collateral_schedule_count AND active_partner_collateral_failure_count == 0",
    "useful_rejection": "gate rejects while same-key unconditional relational activation changes behavior without increasing positive-prose collateral, and original behavior has no partner collateral failure",
    "applicability_support": "at least one useful rejection or at least one gated clean rescue absent in the same-key unconditional control, with zero missed same-key control clean rescues and zero gated partner collateral",
    "mixed_signal": "support is false, but the gate rejects/accepts in the preregistered direction and weakly improves positive-prose collateral or mean first-success timing versus same-key unconditional control without partner harm"
  },
  "metrics": [
    "variant_count",
    "historical_full_pool_row_count",
    "class_group_count",
    "multi_context_class_group_count",
    "relational_candidate_class_count",
    "primary_minimax_tie_count",
    "dominance_approved_count",
    "dominance_rejected_count",
    "control_clean_rescue_count",
    "gated_clean_rescue_count",
    "control_behavior_change_count",
    "gated_behavior_change_count",
    "gated_partner_collateral_failure_count",
    "useful_rejection_count",
    "missed_control_clean_rescue_count",
    "applicability_support",
    "mixed_signal",
    "heldout_applicability_choice_count",
    "post_result_applicability_change_count",
    "source_state_mutation_count",
    "persistent_state_write_count",
    "capacity_growth_event_count",
    "all_child_source_identity_mismatch_count",
    "all_child_transport_identity_mismatch_count",
    "invalid_evaluation_rows"
  ],
  "classification_rules": {
    "supported": "valid AND applicability_support is true AND missed_control_clean_rescue_count==0 AND gated_partner_collateral_failure_count==0",
    "mixed": "valid AND supported is false AND mixed_signal is true AND missed_control_clean_rescue_count==0",
    "negative": "valid AND supported is false AND mixed_signal is false",
    "invalid": "any parent, manifest identity, 17-row historical-pool identity, class grouping/uniform-payload identity, exact Y084 relation scores/selection, strict primary-minimax dominance rule, target-key identity, heldout ordering, deterministic replay, 16/7/9 capacity, provenance, persistence or accounting requirement fails"
  },
  "rsi_success": false,
  "rsi_success_note": "Y085 is independent Yggdrasil target-time applicability attribution on studied contexts. Support still requires disjoint prospective validation before any RSI claim.",
  "no_post_result_tuning_rule": "Do not alter manifests, historical pool, class groups, per-context member keys, 4-byte Hamming, Y084 score ordering, strict-primary dominance rule, payloads, target keys, four cells, schedules, split, packet count, activation/scoring, capacity, classification or authority after primary output.",
  "successors": {
    "supported": {
      "contract_id": "yggdrasil-086-explicit-applicability-prospective-validation",
      "experiment_family": "prospective-explicit-applicability-validation-086"
    },
    "mixed": {
      "contract_id": "yggdrasil-086-explicit-applicability-disambiguation",
      "experiment_family": "explicit-applicability-disambiguation-086"
    },
    "negative": {
      "contract_id": "yggdrasil-086-explicit-context-key-representation-attribution",
      "experiment_family": "explicit-context-key-representation-attribution-086"
    }
  },
  "required_authority": {
    "disposition": "READY_RESEARCH",
    "manifest_sha256": "7077d2b72d8954afc24f36b2971393acc11e3b345f7c3521102c20347b9c6171",
    "hosted_compute": true,
    "research_only": true,
    "one_shot": true,
    "external_model_calls": false,
    "persistent_corpus": false,
    "production_authority": false
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-explicit-applicability-condition-attribution-085.ice"
  ]
}
