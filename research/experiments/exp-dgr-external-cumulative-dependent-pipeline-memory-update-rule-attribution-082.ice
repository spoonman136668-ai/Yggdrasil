{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-MEMORY-UPDATE-RULE-ATTRIBUTION-082",
  "program": "Yggdrasil RSI tranche: cumulative memory update-rule attribution",
  "question": "After Y080 uniform evidence accumulation and Y081 historical transition selection both failed, is the missing cumulative-memory mechanism an online recency-sensitive write rule rather than static aggregation or transition retrieval?",
  "hypothesis": "Y080 showed that uniformly accumulating repeated historical evidence into a consolidated state did not rescue the fifth context, while Y081 showed that selecting historically observed state transitions changed context choice without producing a clean rescue. Freeze one new shadow update rule while holding representation and retrieval fixed: CLASS_UNIFORM_ACCUMULATION reproduces Y080 class-key accumulation exactly; CLASS_RECENCY_HALF_UPDATE processes transfer→third→fourth online, decays all previously retained exposed evidence in a class group by exactly 1/2 at each historical context transition, then adds that context's exposed total and best_count evidence. The winner, consistency, utility, representative key, target retrieval, fifth-context target keys, capacity and scoring remain byte-identical to Y080. This tests whether stale evidence overweighting—not representation, storage size, or transition selection—prevents cumulative memory from adapting.",
  "exact_parent_sha": "a9be0f85c76bc2ca7fc5ad9aac6feada082646a9",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-memory-update-rule-attribution-r1",
  "predecessor": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CUMULATIVE-STATE-TRANSITION-ATTRIBUTION-081",
    "github_run_id": 37209974945,
    "classification": "negative",
    "validity_pass": true,
    "observation": {
      "historical_full_pool_row_count": 17,
      "exact_transition_count": 4,
      "class_transition_count": 10,
      "transition_context_change_count": 4,
      "last_state_clean_rescue_count": 0,
      "exact_transition_clean_rescue_count": 0,
      "class_transition_clean_rescue_count": 0,
      "transition_behavior_change_count": 2,
      "transition_partner_collateral_failure_count": 0,
      "mixed_signal": 0,
      "invalid_evaluation_rows": 0
    },
    "eliminated_hypothesis": "retrieving ordered exact-key or class-key historical state transitions is sufficient to rescue cumulative transfer",
    "strengthened_hypothesis": "useful cumulative memory may require a bounded online write/update rule that discounts stale historical evidence while integrating newer compatible evidence"
  },
  "cause_effect_trace": {
    "observed_failure": "Y081 changed historical context selection in all four transition-vs-last-state comparisons and changed behavior twice, yet produced zero clean rescues and no favorable mixed signal.",
    "residual_cause_under_test": "STALE_EVIDENCE_OVERWEIGHTING_IN_CUMULATIVE_MEMORY_UPDATE",
    "exact_bounded_delta": "change only the update weighting applied to the byte-identical Y080 class-key accumulator; representation, grouping, target keys, retrieval, schedules, capacity and scoring remain unchanged",
    "control_rule": "CLASS_UNIFORM_ACCUMULATION is byte-identical Y080 CLASS_KEY_ACCUMULATION: exposed best_count and total evidence are summed uniformly across transfer, third and fourth",
    "recency_rule": "CLASS_RECENCY_HALF_UPDATE processes contexts in fixed transfer→third→fourth order; before adding evidence from each context after transfer, multiply every retained class accumulator total and each successor-byte exposed-best-count accumulator by exactly 0.5; then add that context's rows; no tuning or fifth-context data",
    "winner_rule": "winner is successor byte with highest retained weighted exposed-best-count; lowest byte wins exact ties; consistency=winner_weighted_best_count/weighted_total; utility=winner_weighted_best_count*consistency",
    "representative_key_rule": "retain lexicographically smallest exact member key in the class group, byte-identical to Y080 class accumulation",
    "target_retrieval": "for each frozen fifth-context target key, choose nearest class aggregate by unchanged class-Hamming and lexical tie-break",
    "nonredundancy": "Y080 tested equal-weight static accumulation; Y081 tested transition selection. Neither tested a fixed recency-decayed online update while holding representation/retrieval constant.",
    "retain_revert": "Y082 is shadow attribution only; support authorizes only a separately preregistered bounded update-rule correction, not accepted-state mutation."
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
    "historical_pool_builder": "byte-identical Y079/Y080 17-row full eligible pool",
    "grouping": "byte-identical Y080 class-key grouping using unchanged Y075 byte_class",
    "target_keys": [
      "SOURCE_CONDITIONED",
      "LOCAL_ONLY"
    ],
    "control": "CLASS_UNIFORM_ACCUMULATION",
    "new_mechanism": "CLASS_RECENCY_HALF_UPDATE",
    "historical_context_order": [
      "transfer",
      "third",
      "fourth"
    ],
    "decay_factor": 0.5,
    "decay_application": "once before adding each context after transfer, to all retained class-group total and successor exposed-best-count evidence",
    "schedules": [
      "A-C-B",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "split": "60% training cue / 40% evaluation",
    "future_packets": 12,
    "activation_position": 7,
    "scoring": "byte-identical Y080/Y081 clean-rescue, behavior-change, partner-collateral and first-success accounting",
    "capacity": "16 total / 7 active / 9 retained",
    "heldout_update_choice_count": 0,
    "post_result_update_change_count": 0
  },
  "representation_cells": [
    "SOURCE_CONDITIONED_KEY × CLASS_UNIFORM_ACCUMULATION",
    "SOURCE_CONDITIONED_KEY × CLASS_RECENCY_HALF_UPDATE",
    "LOCAL_ONLY_KEY × CLASS_UNIFORM_ACCUMULATION",
    "LOCAL_ONLY_KEY × CLASS_RECENCY_HALF_UPDATE"
  ],
  "outcome_definition": {
    "clean_rescue": "active_positive_prose_collateral_schedule_count > original_positive_prose_collateral_schedule_count AND active_partner_collateral_failure_count == 0",
    "update_support": "at least one CLASS_RECENCY_HALF_UPDATE cell yields a clean rescue while its same-key CLASS_UNIFORM_ACCUMULATION control is a non-rescue, with zero partner collateral",
    "mixed_signal": "no clean rescue, but recency update improves positive-prose collateral schedule count or mean first-success packet versus its same-key uniform control without partner-collateral harm"
  },
  "metrics": [
    "variant_count",
    "historical_full_pool_row_count",
    "class_group_count",
    "multi_context_class_group_count",
    "uniform_clean_rescue_count",
    "recency_half_clean_rescue_count",
    "recency_half_behavior_change_count",
    "recency_half_partner_collateral_failure_count",
    "recency_half_selected_payload_change_count",
    "update_support",
    "mixed_signal",
    "heldout_update_choice_count",
    "post_result_update_change_count",
    "source_state_mutation_count",
    "persistent_state_write_count",
    "capacity_growth_event_count",
    "all_child_source_identity_mismatch_count",
    "all_child_transport_identity_mismatch_count",
    "invalid_evaluation_rows"
  ],
  "classification_rules": {
    "supported": "valid AND update_support is true AND recency_half_partner_collateral_failure_count==0",
    "mixed": "valid AND supported is false AND mixed_signal is true",
    "negative": "valid AND recency_half_clean_rescue_count==0 AND mixed_signal is false",
    "invalid": "any parent, manifest identity, historical-pool identity/order, Y080 class grouping/control identity, 0.5 update rule, winner/utility formula, target-key identity, retrieval/tie-break, heldout ordering, deterministic replay, 16/7/9 capacity, provenance, persistence or accounting requirement fails"
  },
  "rsi_success": false,
  "rsi_success_note": "Y082 remains shadow update-rule attribution on studied contexts; any support still requires separately frozen prospective disjoint-context validation.",
  "no_post_result_tuning_rule": "Do not alter manifests, pool, class grouping, context order, 0.5 decay, accumulation/winner formulas, target keys, retrieval, four cells, schedules, split, packet count, activation/scoring, 16/7/9 capacity, classification or authority after primary output.",
  "successors": {
    "supported": {
      "contract_id": "yggdrasil-083-recency-update-consolidation-correction",
      "experiment_family": "bounded-memory-update-correction-083"
    },
    "mixed": {
      "contract_id": "yggdrasil-083-memory-update-rule-disambiguation",
      "experiment_family": "memory-update-rule-disambiguation-083"
    },
    "negative": {
      "contract_id": "yggdrasil-083-context-conditioned-write-gate-attribution",
      "experiment_family": "context-conditioned-write-gate-attribution-083"
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
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-memory-update-rule-attribution-082.ice"
  ]
}
