{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONSOLIDATION-REPRESENTATION-ATTRIBUTION-078",
  "program": "Yggdrasil RSI tranche: cumulative consolidation representation attribution",
  "question": "After Y077 found no clean rescue from either target-key choice or single-source payload origin, does representing prior experience as a frozen multi-context retained set recover target-compatible information that a single retained row loses?",
  "hypothesis": "Y077 eliminated a pure target-key, payload-origin, or key×payload explanation on the fifth context: all four cells failed clean rescue. The remaining failure may be representational: one source-retained row is too context-specific, while target-local payload discards cumulative prior information. Rebuild one immutable training-only representative row from each of the three earlier sealed contexts using the byte-identical canonical donor and LOCAL_ONLY selector, freeze the resulting three-row cumulative set, and for each of the two already-frozen fifth-context keys retrieve exactly one historical row by minimum four-byte key Hamming distance with fixed transfer→third→fourth tie-break. Project only that selected immutable payload onto the frozen target key. Compare this cumulative-retrieval representation against the exact Y077 TARGET_LOCAL and SINGLE_SOURCE_RETAINED controls under the same schedules and shadow evaluator.",
  "exact_parent_sha": "d1562b6ab98b729df96c6e3ea219b1bc58658e40",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-consolidation-representation-attribution-r1",
  "predecessor": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COMPATIBILITY-FACTORIAL-077",
    "github_run_id": 37194872211,
    "classification": "negative",
    "validity_pass": true,
    "observation": {
      "variant_count": 4,
      "clean_rescue_count": 0,
      "key_main_effect": 0,
      "payload_main_effect": 0,
      "interaction_effect": 0,
      "behavior_change_count": 2,
      "source_payload_projection_count": 2,
      "source_state_mutation_count": 0,
      "persistent_state_write_count": 0,
      "capacity_growth_event_count": 0,
      "invalid_evaluation_rows": 0
    },
    "eliminated_hypothesis": "target-key selection, single-source payload origin, or their interaction is sufficient to recover clean rescue on the fifth context",
    "strengthened_hypothesis": "the missing variable may be how cumulative prior contexts are represented before target-compatible retrieval"
  },
  "cause_effect_trace": {
    "observed_failure": "Y077's two source-retained projections changed behavior but still produced zero clean rescues, while both target-local payload cells also failed. The failure therefore survived key choice and one-row payload origin.",
    "residual_cause_under_test": "SINGLE_CONTEXT_REPRESENTATION_LOSS",
    "exact_bounded_delta": "add one cumulative representation arm per frozen Y077 target key; reproduce the four Y077 control cells unchanged; no accepted-state mutation, persistent write, capacity growth, operational gate change, or post-result arm selection",
    "cumulative_representation": {
      "historical_contexts": [
        "transfer",
        "third",
        "fourth"
      ],
      "representative_builder": "byte-identical Y075/Y076 canonical B+C donor generalized only to each sealed historical manifest",
      "representative_selector": "byte-identical Y075 LOCAL_ONLY training-only selector; exactly one row per historical context",
      "retained_set_size": 3,
      "target_retrieval": "minimum Hamming distance across the four key bytes from frozen target key to historical representative key",
      "tie_break": [
        "transfer",
        "third",
        "fourth"
      ],
      "projection": "project selected immutable historical payload fields best,total,best_count,consistency,utility,cell_index,map_best onto the already-frozen target key; do not synthesize or average payload fields"
    },
    "nonredundancy": "Y067-Y069 transported one retained row; Y073/Y077 rebound one source payload onto target keys. No prior experiment retained a frozen set of multiple prior-context representatives and performed training-only target-compatible retrieval from that set on the fifth context.",
    "retain_revert": "Y078 is shadow-only attribution. A supported result may justify a separately preregistered cumulative-memory retention/retrieval correction; mixed/negative does not."
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
  "source_retained_state": {
    "key": [
      10,
      32,
      32,
      32
    ],
    "best": 32,
    "total": 112,
    "best_count": 112,
    "consistency": 1,
    "utility": 112,
    "cell_index": 12,
    "map_best": 32,
    "immutable": true
  },
  "frozen_reuse": {
    "fifth_donor": "byte-identical Y075/Y076/Y077 fifth-context donor",
    "target_keys": [
      "SOURCE_CONDITIONED",
      "LOCAL_ONLY"
    ],
    "controls": [
      "TARGET_LOCAL",
      "SINGLE_SOURCE_RETAINED"
    ],
    "new_representation": "MULTI_CONTEXT_RETRIEVED_PROJECTION",
    "schedules": [
      "A-C-B",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "split": "60% training cue / 40% evaluation",
    "future_packets": 12,
    "activation_position": 7,
    "scoring": "byte-identical Y077 clean-rescue and behavior-change accounting",
    "capacity": "16 total / 7 active / 9 retained",
    "heldout_representation_choice_count": 0,
    "post_result_representation_change_count": 0
  },
  "representation_cells": [
    "SOURCE_CONDITIONED_KEY × TARGET_LOCAL",
    "SOURCE_CONDITIONED_KEY × SINGLE_SOURCE_RETAINED",
    "SOURCE_CONDITIONED_KEY × MULTI_CONTEXT_RETRIEVED_PROJECTION",
    "LOCAL_ONLY_KEY × TARGET_LOCAL",
    "LOCAL_ONLY_KEY × SINGLE_SOURCE_RETAINED",
    "LOCAL_ONLY_KEY × MULTI_CONTEXT_RETRIEVED_PROJECTION"
  ],
  "outcome_definition": {
    "clean_rescue": "active_positive_prose_collateral_schedule_count > original_positive_prose_collateral_schedule_count AND active_partner_collateral_failure_count == 0",
    "representation_support": "at least one MULTI_CONTEXT_RETRIEVED_PROJECTION cell is a clean rescue while both corresponding Y077 control representations for that key are non-rescues",
    "mixed_signal": "no clean rescue, but a cumulative cell changes behavior and improves positive-prose collateral schedule count or mean first-success packet versus both corresponding controls without partner-collateral harm"
  },
  "metrics": [
    "variant_count",
    "historical_representative_count",
    "historical_representative_identity_mismatch_count",
    "multi_context_retrieval_count",
    "multi_context_selected_transfer_count",
    "multi_context_selected_third_count",
    "multi_context_selected_fourth_count",
    "target_local_clean_rescue_count",
    "single_source_clean_rescue_count",
    "multi_context_clean_rescue_count",
    "multi_context_behavior_change_count",
    "multi_context_partner_collateral_failure_count",
    "heldout_representation_choice_count",
    "post_result_representation_change_count",
    "source_state_mutation_count",
    "persistent_state_write_count",
    "capacity_growth_event_count",
    "invalid_evaluation_rows"
  ],
  "classification_rules": {
    "supported": "valid AND multi_context_clean_rescue_count>=1 AND representation_support is true AND multi_context_partner_collateral_failure_count==0",
    "mixed": "valid AND supported is false AND mixed_signal is true",
    "negative": "valid AND multi_context_clean_rescue_count==0 AND mixed_signal is false",
    "invalid": "any parent, four-manifest identity, historical representative builder/selector, retained-set size, target-key identity, Hamming retrieval/tie-break, control reproduction, heldout ordering, deterministic replay, 16/7/9 capacity, provenance, persistence or accounting requirement fails"
  },
  "rsi_success": false,
  "rsi_success_note": "Y078 remains shadow attribution on previously studied contexts; even a supported cumulative representation requires a separately preregistered prospective disjoint-context replication before RSI transfer success.",
  "no_post_result_tuning_rule": "Do not alter historical manifests, representative builder/selector, three-row set, target keys, Hamming metric, tie-break, payload projection, six cells, schedules, split, packet count, activation/scoring, 16/7/9 capacity, outcome definition, classification, or authority after primary output.",
  "successors": {
    "supported": {
      "contract_id": "yggdrasil-079-cumulative-representation-retrieval-correction",
      "experiment_family": "bounded-cumulative-retrieval-correction-079"
    },
    "mixed": {
      "contract_id": "yggdrasil-079-consolidation-representation-disambiguation",
      "experiment_family": "consolidation-representation-disambiguation-079"
    },
    "negative": {
      "contract_id": "yggdrasil-079-consolidation-mechanism-attribution",
      "experiment_family": "consolidation-mechanism-attribution-079"
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
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-consolidation-representation-attribution-078.ice"
  ]
}
