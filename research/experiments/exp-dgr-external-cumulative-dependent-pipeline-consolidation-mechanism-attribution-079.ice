{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONSOLIDATION-MECHANISM-ATTRIBUTION-079",
  "program": "Yggdrasil RSI tranche: cumulative consolidation mechanism attribution",
  "question": "Did Y078's one-row-per-context consolidation discard target-compatible historical rows before retrieval on the fifth context?",
  "hypothesis": "Y078 retained three historical representatives and deterministically retrieved the transfer representative for both frozen fifth-context keys, yet produced zero clean rescues. The failure may therefore be caused by consolidation compression rather than retrieval distance itself. Rebuild the exact training-only eligible candidate pool for each of the transfer, third, and fourth sealed contexts using the byte-identical canonical donor and Y075 LOCAL_ONLY eligibility machinery. Freeze their exact union before fifth-context evaluation. For each already-frozen Y078 target key, retrieve one immutable historical row from the union by minimum four-byte key Hamming distance with fixed transfer→third→fourth context tie-break and then the unchanged LOCAL_ONLY ranking/lexical order. Project only that row's immutable payload onto the frozen target key. Compare FULL_ELIGIBLE_POOL retrieval against the exact Y078 COMPRESSED_REPRESENTATIVE_SET and its TARGET_LOCAL/SINGLE_SOURCE controls under the same schedules and shadow evaluator.",
  "exact_parent_sha": "fad7140b3d9ffa172d5b5ef8965ae557b15c528c",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-consolidation-mechanism-attribution-r1",
  "predecessor": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONSOLIDATION-REPRESENTATION-ATTRIBUTION-078",
    "github_run_id": 37198259189,
    "classification": "negative",
    "validity_pass": true,
    "observation": {
      "variant_count": 6,
      "historical_representative_count": 3,
      "multi_context_retrieval_count": 2,
      "multi_context_selected_transfer_count": 2,
      "multi_context_selected_third_count": 0,
      "multi_context_selected_fourth_count": 0,
      "target_local_clean_rescue_count": 0,
      "single_source_clean_rescue_count": 0,
      "multi_context_clean_rescue_count": 0,
      "multi_context_behavior_change_count": 1,
      "multi_context_partner_collateral_failure_count": 0,
      "source_state_mutation_count": 0,
      "persistent_state_write_count": 0,
      "capacity_growth_event_count": 0,
      "invalid_evaluation_rows": 0
    },
    "eliminated_hypothesis": "one locally selected representative per historical context plus nearest-key retrieval is sufficient to recover target-compatible cumulative information on the fifth context",
    "strengthened_hypothesis": "single-row consolidation may discard useful within-context alternatives before retrieval"
  },
  "cause_effect_trace": {
    "observed_failure": "Both Y078 cumulative retrievals selected the transfer representative and neither rescued, despite the retained set containing three exact historical representatives.",
    "residual_cause_under_test": "CONSOLIDATION_COMPRESSION_LOSS",
    "exact_bounded_delta": "replace only the historical candidate source for one new shadow arm per frozen target key: all exact eligible historical rows instead of one representative per context; reproduce Y078 controls unchanged",
    "full_pool_definition": "for each transfer/third/fourth manifest, rebuild the byte-identical canonical B+C donor and include every row passing the unchanged Y075 build_pool eligibility rule; no outcome labels from the fifth context and no row synthesis",
    "retrieval": "minimum Hamming distance across four key bytes; context tie-break transfer, third, fourth; within-context tie-break unchanged LOCAL_ONLY rank then lexical key order",
    "projection": "rebind only the selected exact immutable row payload fields best,total,best_count,consistency,utility,cell_index,map_best to the already-frozen target key",
    "nonredundancy": "Y078 compressed each historical context to one LOCAL_ONLY representative before retrieval. Y079 tests whether that compression itself caused information loss while leaving target keys, distance metric, projection, evaluator, schedules and capacity unchanged.",
    "retain_revert": "Y079 is shadow-only attribution. Supported compression loss authorizes only a separately preregistered bounded retention/retrieval correction."
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
    "historical_contexts": [
      "transfer",
      "third",
      "fourth"
    ],
    "pool_builder": "byte-identical Y075 build_pool generalized only to each exact historical source identity",
    "target_keys": [
      "SOURCE_CONDITIONED",
      "LOCAL_ONLY"
    ],
    "controls": [
      "TARGET_LOCAL",
      "SINGLE_SOURCE_RETAINED",
      "COMPRESSED_REPRESENTATIVE_SET"
    ],
    "new_mechanism": "FULL_ELIGIBLE_POOL",
    "schedules": [
      "A-C-B",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "split": "60% training cue / 40% evaluation",
    "future_packets": 12,
    "activation_position": 7,
    "scoring": "byte-identical Y078/Y077 clean-rescue and behavior-change accounting",
    "capacity": "16 total / 7 active / 9 retained",
    "heldout_pool_choice_count": 0,
    "post_result_pool_change_count": 0
  },
  "representation_cells": [
    "SOURCE_CONDITIONED_KEY × TARGET_LOCAL",
    "SOURCE_CONDITIONED_KEY × SINGLE_SOURCE_RETAINED",
    "SOURCE_CONDITIONED_KEY × COMPRESSED_REPRESENTATIVE_SET",
    "SOURCE_CONDITIONED_KEY × FULL_ELIGIBLE_POOL",
    "LOCAL_ONLY_KEY × TARGET_LOCAL",
    "LOCAL_ONLY_KEY × SINGLE_SOURCE_RETAINED",
    "LOCAL_ONLY_KEY × COMPRESSED_REPRESENTATIVE_SET",
    "LOCAL_ONLY_KEY × FULL_ELIGIBLE_POOL"
  ],
  "outcome_definition": {
    "clean_rescue": "active_positive_prose_collateral_schedule_count > original_positive_prose_collateral_schedule_count AND active_partner_collateral_failure_count == 0",
    "compression_support": "at least one FULL_ELIGIBLE_POOL cell is a clean rescue while the corresponding COMPRESSED_REPRESENTATIVE_SET, TARGET_LOCAL and SINGLE_SOURCE_RETAINED cells are all non-rescues",
    "mixed_signal": "no clean rescue, but a FULL_ELIGIBLE_POOL cell changes behavior and improves positive-prose collateral schedule count or mean first-success packet versus its corresponding compressed cell without partner-collateral harm"
  },
  "metrics": [
    "variant_count",
    "historical_context_count",
    "historical_full_pool_row_count",
    "historical_empty_pool_count",
    "full_pool_retrieval_count",
    "full_pool_selected_transfer_count",
    "full_pool_selected_third_count",
    "full_pool_selected_fourth_count",
    "compressed_clean_rescue_count",
    "full_pool_clean_rescue_count",
    "full_pool_behavior_change_count",
    "full_pool_partner_collateral_failure_count",
    "compression_support",
    "mixed_signal",
    "heldout_pool_choice_count",
    "post_result_pool_change_count",
    "source_state_mutation_count",
    "persistent_state_write_count",
    "capacity_growth_event_count",
    "invalid_evaluation_rows"
  ],
  "classification_rules": {
    "supported": "valid AND compression_support is true AND full_pool_partner_collateral_failure_count==0",
    "mixed": "valid AND supported is false AND mixed_signal is true",
    "negative": "valid AND full_pool_clean_rescue_count==0 AND mixed_signal is false",
    "invalid": "any parent, four-manifest identity, historical pool builder/eligibility, target-key identity, Hamming/tie-break retrieval, control reproduction, heldout ordering, deterministic replay, 16/7/9 capacity, provenance, persistence or accounting requirement fails"
  },
  "rsi_success": false,
  "rsi_success_note": "Y079 remains shadow attribution on previously studied contexts; even supported compression loss requires prospective disjoint-context validation after a separately frozen correction.",
  "no_post_result_tuning_rule": "Do not alter manifests, historical eligibility, pool membership, target keys, distance metric, tie-breaks, payload projection, eight cells, schedules, split, packet count, activation/scoring, 16/7/9 capacity, outcome definition, classification, or authority after primary output.",
  "successors": {
    "supported": {
      "contract_id": "yggdrasil-080-compression-aware-retention-correction",
      "experiment_family": "bounded-consolidation-correction-080"
    },
    "mixed": {
      "contract_id": "yggdrasil-080-retrieval-mechanism-disambiguation",
      "experiment_family": "retrieval-mechanism-disambiguation-080"
    },
    "negative": {
      "contract_id": "yggdrasil-080-consolidation-dynamics-attribution",
      "experiment_family": "consolidation-dynamics-attribution-080"
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
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-consolidation-mechanism-attribution-079.ice"
  ]
}
