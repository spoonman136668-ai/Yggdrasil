{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-EXPLICIT-CONTEXT-KEY-REPRESENTATION-ATTRIBUTION-086",
  "program": "Yggdrasil RSI corrective tranche: explicit observable-context key attribution",
  "question": "After Y085 showed that a target-time ambiguity gate can reject one relational match without improving transfer, is the retained-state key missing an explicit observable description of the context in which that state was learned?",
  "hypothesis": "Y085 weakened another activation-gate explanation: one primary-minimax tie was rejected, but the rejection was not useful, while the approved SOURCE_CONDITIONED activation still changed behavior without improving positive-prose collateral. Freeze a representation attribution that changes no payload, capacity, schedules, or outcomes. EXACT_KEY_ONLY retrieves from the byte-identical Y079 17-row historical full pool by exact 4-byte key Hamming with the same fixed context-order/lexical tie-break. EXPLICIT_CONTEXT_KEY augments every historical row's 4-byte state key with a 3-component observable context signature computed before target evaluation from that context's 60% training cues: for code, structured, and technical-prose separately, map every byte through the unchanged Y075 byte_class function and record the most frequent class (exact ties choose the lowest class 0<1<2<3). Compute the fifth target's same 3-component signature from its own 60% training cues. Retrieve by minimum total Hamming over the concatenated 7-component (state key + context signature), then minimum 4-byte state-key Hamming, then fixed context order transfer→third→fourth, then lexical exact key. This tests whether applicability needs an explicit generalizable context descriptor in the key rather than another target-time gate.",
  "exact_parent_sha": "ff1ff289d875af9154e4a7a9fcac22691c687a16",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-explicit-context-key-representation-attribution-r1",
  "predecessor": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-EXPLICIT-APPLICABILITY-CONDITION-ATTRIBUTION-085",
    "github_run_id": 37226562513,
    "classification": "negative",
    "validity_pass": true,
    "observation": {
      "historical_full_pool_row_count": 17,
      "class_group_count": 2,
      "relational_candidate_class_count": 2,
      "primary_minimax_tie_count": 1,
      "dominance_approved_count": 1,
      "dominance_rejected_count": 1,
      "control_behavior_change_count": 1,
      "gated_behavior_change_count": 1,
      "useful_rejection_count": 0,
      "control_clean_rescue_count": 0,
      "gated_clean_rescue_count": 0,
      "applicability_support": 0,
      "mixed_signal": 0,
      "invalid_evaluation_rows": 0
    },
    "eliminated_hypothesis": "a strict target-time primary-minimax dominance gate is sufficient to identify when relationally selected retained state should be applied",
    "strengthened_hypothesis": "the retained-state key itself may need an explicit observable context descriptor so applicability is represented before activation rather than inferred by a downstream gate"
  },
  "cause_effect_trace": {
    "observed_failure": "Y085 rejected one ambiguous relational match but the rejection was not useful; the uniquely approved SOURCE_CONDITIONED match still changed behavior without improving the outcome.",
    "residual_cause_under_test": "STATE_KEY_OMITS_OBSERVABLE_CONTEXT_DESCRIPTOR",
    "exact_bounded_delta": "change only retrieval representation from exact 4-byte state key to a fixed concatenated 4-byte state key + 3-component cue-derived context signature; historical rows, payloads, target selectors, activation, schedules, scoring, and 16/7/9 capacity remain unchanged",
    "control_rule": "EXACT_KEY_ONLY is byte-identical Y079 full-pool retrieval by minimum exact 4-byte Hamming, then context order transfer→third→fourth, then lexical key",
    "context_signature_rule": "for each context and each of its code/structured/technical-prose 60% training cues, classify every byte with Y075 byte_class and record the modal class; exact class-count ties choose the numerically lowest class; concatenate the three modal classes in code, structured, technical_prose order",
    "treatment_rule": "EXPLICIT_CONTEXT_KEY scores each historical row by total Hamming across target exact key vs historical exact key (4 components) plus target context signature vs historical context signature (3 components); tie-break by lower 4-byte key Hamming, then context order transfer→third→fourth, then lexical exact key",
    "no_threshold_rule": "no fitted embedding, learned weight, distance threshold, ratio, held-out tuning, label use, or post-result representation choice",
    "retain_revert": "Y086 is shadow attribution only; support authorizes only separately preregistered prospective validation/correction, not accepted-state mutation."
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
    "historical_pool_builder": "byte-identical Y079/Y080-Y085 17-row full eligible pool with origin context retained",
    "payload": "byte-identical original historical-row retained-state payload",
    "target_keys": [
      "SOURCE_CONDITIONED",
      "LOCAL_ONLY"
    ],
    "control": "EXACT_KEY_ONLY",
    "new_mechanism": "EXPLICIT_CONTEXT_KEY",
    "byte_class": "byte-identical Y075 byte_class: whitespace=0, letters=1, digits=2, other=3",
    "context_signature_sources": [
      "code",
      "structured",
      "technical_prose"
    ],
    "context_signature_split": "60% training cue only",
    "context_signature_tie_break": "lowest class id",
    "treatment_distance": "unweighted 7-component Hamming; tie by 4-byte state-key Hamming, fixed historical context order, lexical exact key",
    "historical_context_order": [
      "transfer",
      "third",
      "fourth"
    ],
    "schedules": [
      "A-C-B",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "future_packets": 12,
    "activation_position": 7,
    "scoring": "byte-identical Y079-Y085 clean-rescue, behavior-change, partner-collateral and first-success accounting",
    "capacity": "16 total / 7 active / 9 retained; shadow candidate search does not authorize persistent-state growth",
    "heldout_context_signature_choice_count": 0,
    "post_result_context_representation_change_count": 0
  },
  "representation_cells": [
    "SOURCE_CONDITIONED_KEY × EXACT_KEY_ONLY",
    "SOURCE_CONDITIONED_KEY × EXPLICIT_CONTEXT_KEY",
    "LOCAL_ONLY_KEY × EXACT_KEY_ONLY",
    "LOCAL_ONLY_KEY × EXPLICIT_CONTEXT_KEY"
  ],
  "outcome_definition": {
    "clean_rescue": "active_positive_prose_collateral_schedule_count > original_positive_prose_collateral_schedule_count AND active_partner_collateral_failure_count == 0",
    "context_key_support": "at least one EXPLICIT_CONTEXT_KEY cell selects a different historical row than its same-key EXACT_KEY_ONLY control and yields a clean rescue while the control does not, with zero partner collateral and no lost same-key control clean rescue",
    "mixed_signal": "supported is false, but explicit-context retrieval changes selection and improves positive-prose collateral or mean first-success timing versus same-key control without partner harm"
  },
  "metrics": [
    "variant_count",
    "historical_full_pool_row_count",
    "historical_context_count",
    "distinct_context_signature_count",
    "context_signature_identity_mismatch_count",
    "explicit_context_selected_row_change_count",
    "control_clean_rescue_count",
    "explicit_context_clean_rescue_count",
    "explicit_context_behavior_change_count",
    "explicit_context_partner_collateral_failure_count",
    "lost_control_clean_rescue_count",
    "context_key_support",
    "mixed_signal",
    "heldout_context_signature_choice_count",
    "post_result_context_representation_change_count",
    "source_state_mutation_count",
    "persistent_state_write_count",
    "capacity_growth_event_count",
    "all_child_source_identity_mismatch_count",
    "all_child_transport_identity_mismatch_count",
    "invalid_evaluation_rows"
  ],
  "classification_rules": {
    "supported": "valid AND context_key_support is true AND lost_control_clean_rescue_count==0 AND explicit_context_partner_collateral_failure_count==0",
    "mixed": "valid AND supported is false AND mixed_signal is true AND lost_control_clean_rescue_count==0",
    "negative": "valid AND supported is false AND mixed_signal is false",
    "invalid": "any parent, manifest identity, 17-row full-pool identity, context-origin identity, Y075 byte_class identity, 60% cue split, three-component modal signature/tie-break, exact-key control retrieval, 7-component Hamming/tie-break, target-key identity, heldout ordering, deterministic replay, 16/7/9 capacity, provenance, persistence or accounting requirement fails"
  },
  "rsi_success": false,
  "rsi_success_note": "Y086 is independent Yggdrasil context-key representation attribution on studied contexts. Support still requires disjoint prospective validation before any RSI claim.",
  "no_post_result_tuning_rule": "Do not alter manifests, pool, context origins, byte_class, cue split, context-signature rule, seven-component distance, tie-breaks, target keys, four cells, schedules, packet count, activation/scoring, capacity, classification or authority after primary output.",
  "successors": {
    "supported": {
      "contract_id": "yggdrasil-087-explicit-context-key-prospective-validation",
      "experiment_family": "prospective-explicit-context-key-validation-087"
    },
    "mixed": {
      "contract_id": "yggdrasil-087-explicit-context-key-disambiguation",
      "experiment_family": "explicit-context-key-disambiguation-087"
    },
    "negative": {
      "contract_id": "yggdrasil-087-context-invariant-specific-factorization-attribution",
      "experiment_family": "context-invariant-specific-factorization-attribution-087"
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
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-explicit-context-key-representation-attribution-086.ice"
  ]
}
