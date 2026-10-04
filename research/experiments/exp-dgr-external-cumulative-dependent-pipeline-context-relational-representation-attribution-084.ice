{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-RELATIONAL-REPRESENTATION-ATTRIBUTION-084",
  "program": "Yggdrasil RSI corrective tranche: context-relational applicability attribution",
  "question": "After Y083 showed that categorical historical write gating can reject a disagreeing class without changing target-selected retained state or producing a rescue, is the missing applicability signal the relation between the new target and the distribution of context-specific historical keys inside each retained class?",
  "hypothesis": "Y083 weakened write-time unanimity as a sufficient mechanism. Freeze a relational representation while leaving retained payload content unchanged. REPRESENTATIVE_CLASS_HAMMING reproduces Y080/Y083 retrieval using each class aggregate's lexicographically smallest representative key. CONTEXT_MINIMAX_RELATION retains the same multi-context class groups and uniform aggregate payloads, but represents each group by its historical per-context exact member keys. For a frozen fifth-context target key, compute for each candidate class the minimum exact 4-byte Hamming distance to any member key within each contributing historical context; score the class by the maximum of those per-context minima, then their sum, then lexical class key. Choose the lexicographically first exact tie. This asks whether applicability requires a state-to-context relation that is simultaneously compatible across historical contexts rather than proximity to one representative key.",
  "exact_parent_sha": "f5e7a2b20e911153b08f0b548c40025485d2a684",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-context-relational-representation-attribution-r1",
  "predecessor": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-CONDITIONED-WRITE-GATE-ATTRIBUTION-083",
    "github_run_id": 37223975264,
    "classification": "negative",
    "validity_pass": true,
    "observation": {
      "historical_full_pool_row_count": 17,
      "class_group_count": 2,
      "multi_context_class_group_count": 2,
      "writable_class_group_count": 1,
      "rejected_class_group_count": 1,
      "gate_context_disagreement_count": 1,
      "ungated_clean_rescue_count": 0,
      "gated_clean_rescue_count": 0,
      "gated_rejection_count": 0,
      "gate_selected_payload_change_count": 0,
      "useful_rejection_count": 0,
      "write_gate_support": 0,
      "mixed_signal": 0,
      "invalid_evaluation_rows": 0
    },
    "eliminated_hypothesis": "categorical cross-context successor unanimity at write time is sufficient to make retained state applicable in the fifth context",
    "strengthened_hypothesis": "applicability may depend on an explicit relation between a new target state and the distribution of context-specific historical states represented within retained memory"
  },
  "cause_effect_trace": {
    "observed_failure": "Y083 identified a historically disagreeing class but the categorical gate did not alter either target-selected payload and produced no rescue or favorable mixed signal.",
    "residual_cause_under_test": "REPRESENTATIVE_KEY_COLLAPSES_CONTEXT_RELATIONAL_COMPATIBILITY",
    "exact_bounded_delta": "change only class retrieval representation from one representative exact key to the frozen set of historical per-context exact member keys; uniform payload aggregation, target keys, schedules, scoring and capacity remain unchanged",
    "control_rule": "REPRESENTATIVE_CLASS_HAMMING is byte-identical Y080/Y083 class retrieval by representative key",
    "relational_rule": "for each multi-context class and each contributing historical context, compute target-to-context distance as the minimum exact 4-byte Hamming distance between the target key and any historical member key from that context; class score=(maximum per-context distance, sum per-context distances, lexical class key); choose lowest tuple",
    "no_threshold_rule": "no fitted threshold, weighting, learned embedding, context ID parameter, or held-out tuning is permitted",
    "payload_rule": "after class selection, activate the byte-identical Y080 uniform aggregate payload for that class projected through the same Y079 payload projection",
    "retain_revert": "Y084 is shadow attribution only; support authorizes only separately preregistered prospective applicability validation/correction, not accepted-state mutation"
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
    "historical_pool_builder": "byte-identical Y079/Y080-Y083 17-row full eligible pool",
    "grouping": "byte-identical Y080 class-key grouping over multi-context groups",
    "payload": "byte-identical Y080 uniform class aggregate",
    "target_keys": [
      "SOURCE_CONDITIONED",
      "LOCAL_ONLY"
    ],
    "control": "REPRESENTATIVE_CLASS_HAMMING",
    "new_mechanism": "CONTEXT_MINIMAX_RELATION",
    "exact_hamming_bytes": 4,
    "relational_tie_break": [
      "maximum per-context minimum Hamming",
      "sum per-context minimum Hamming",
      "lexical class key"
    ],
    "schedules": [
      "A-C-B",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "split": "60% training cue / 40% evaluation",
    "future_packets": 12,
    "activation_position": 7,
    "scoring": "byte-identical Y080-Y083 clean-rescue, behavior-change, partner-collateral and first-success accounting",
    "capacity": "16 total / 7 active / 9 retained",
    "heldout_relation_choice_count": 0,
    "post_result_relation_change_count": 0
  },
  "representation_cells": [
    "SOURCE_CONDITIONED_KEY × REPRESENTATIVE_CLASS_HAMMING",
    "SOURCE_CONDITIONED_KEY × CONTEXT_MINIMAX_RELATION",
    "LOCAL_ONLY_KEY × REPRESENTATIVE_CLASS_HAMMING",
    "LOCAL_ONLY_KEY × CONTEXT_MINIMAX_RELATION"
  ],
  "outcome_definition": {
    "clean_rescue": "active_positive_prose_collateral_schedule_count > original_positive_prose_collateral_schedule_count AND active_partner_collateral_failure_count == 0",
    "relational_support": "at least one CONTEXT_MINIMAX_RELATION cell selects a different class than its same-key control and yields a clean rescue while the control does not, with zero partner collateral and no lost same-key control clean rescue",
    "mixed_signal": "supported is false, but relational retrieval changes class selection and improves positive-prose collateral or mean first-success timing versus same-key control without partner harm"
  },
  "metrics": [
    "variant_count",
    "historical_full_pool_row_count",
    "class_group_count",
    "multi_context_class_group_count",
    "relational_candidate_class_count",
    "relational_selected_class_change_count",
    "control_clean_rescue_count",
    "relational_clean_rescue_count",
    "relational_behavior_change_count",
    "relational_partner_collateral_failure_count",
    "lost_control_clean_rescue_count",
    "relational_support",
    "mixed_signal",
    "heldout_relation_choice_count",
    "post_result_relation_change_count",
    "source_state_mutation_count",
    "persistent_state_write_count",
    "capacity_growth_event_count",
    "all_child_source_identity_mismatch_count",
    "all_child_transport_identity_mismatch_count",
    "invalid_evaluation_rows"
  ],
  "classification_rules": {
    "supported": "valid AND relational_support is true AND lost_control_clean_rescue_count==0 AND relational_partner_collateral_failure_count==0",
    "mixed": "valid AND supported is false AND mixed_signal is true AND lost_control_clean_rescue_count==0",
    "negative": "valid AND supported is false AND mixed_signal is false",
    "invalid": "any parent, manifest identity, 17-row historical-pool identity, class grouping/uniform-payload identity, exact 4-byte Hamming relation, minimax/sum/lexical ordering, target-key identity, heldout ordering, deterministic replay, 16/7/9 capacity, provenance, persistence or accounting requirement fails"
  },
  "rsi_success": false,
  "rsi_success_note": "Y084 is independent Yggdrasil relational-applicability attribution on studied contexts. Support still requires disjoint prospective validation before any RSI claim.",
  "no_post_result_tuning_rule": "Do not alter manifests, historical pool, class groups, per-context member keys, 4-byte Hamming, minimax/sum/lexical ordering, payloads, target keys, four cells, schedules, split, packet count, activation/scoring, capacity, classification or authority after primary output.",
  "successors": {
    "supported": {
      "contract_id": "yggdrasil-085-relational-applicability-prospective-validation",
      "experiment_family": "prospective-relational-applicability-validation-085"
    },
    "mixed": {
      "contract_id": "yggdrasil-085-relational-applicability-disambiguation",
      "experiment_family": "relational-applicability-disambiguation-085"
    },
    "negative": {
      "contract_id": "yggdrasil-085-explicit-applicability-condition-attribution",
      "experiment_family": "explicit-applicability-condition-attribution-085"
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
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-context-relational-representation-attribution-084.ice"
  ]
}
