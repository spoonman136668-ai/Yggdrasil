{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONSOLIDATION-DYNAMICS-ATTRIBUTION-080",
  "program": "Yggdrasil RSI tranche: cumulative consolidation dynamics attribution",
  "question": "After Y079 showed that retaining every eligible historical row still fails, is the missing mechanism cumulative evidence integration across recurring historical states rather than static row storage and nearest-row retrieval?",
  "hypothesis": "Y078 compression and Y079 full-pool storage both failed: the exact historical information was present, but retrieval still selected a single transfer row and produced zero clean rescues. Freeze two new shadow consolidation mechanisms over the same transfer/third/fourth training-only pools. EXACT_KEY_ACCUMULATION groups rows with byte-identical four-byte keys across contexts and aggregates successor evidence before target retrieval. CLASS_KEY_ACCUMULATION groups rows by the unchanged Y075 four-position byte-class signature and aggregates successor evidence within each class group. The Y079 FULL_ELIGIBLE_POOL nearest-row arm remains the control. Aggregation is deterministic, uses no fifth-context outcomes, does not add retained capacity, and projects only the frozen aggregate payload onto the already-frozen fifth-context target keys.",
  "exact_parent_sha": "562e24cde73c479e820d576410ad75d86645fd64",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-consolidation-dynamics-attribution-r1",
  "predecessor": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONSOLIDATION-MECHANISM-ATTRIBUTION-079",
    "github_run_id": 37200042062,
    "classification": "negative",
    "validity_pass": true,
    "observation": {
      "historical_context_count": 3,
      "historical_full_pool_row_count": 17,
      "full_pool_retrieval_count": 2,
      "full_pool_selected_transfer_count": 2,
      "full_pool_selected_third_count": 0,
      "full_pool_selected_fourth_count": 0,
      "compressed_clean_rescue_count": 0,
      "full_pool_clean_rescue_count": 0,
      "full_pool_behavior_change_count": 1,
      "compression_support": 0,
      "mixed_signal": 0
    },
    "eliminated_hypothesis": "one-row-per-context compression is the reason cumulative retrieval fails on the fifth context",
    "strengthened_hypothesis": "static storage/retrieval may be insufficient; useful cumulative memory may require evidence integration across repeated or structurally equivalent historical states"
  },
  "cause_effect_trace": {
    "observed_failure": "Y079 preserved all 17 eligible historical rows but both frozen target keys still retrieved transfer and neither arm rescued.",
    "residual_cause_under_test": "MISSING_CUMULATIVE_EVIDENCE_INTEGRATION",
    "exact_bounded_delta": "replace only the historical representation in two new shadow arms: deterministic evidence accumulation by exact key or byte-class key; reproduce Y079 full-pool control unchanged",
    "exact_key_accumulation": "for each exact four-byte key appearing in >=2 historical contexts, sum total across member rows and accumulate each row's exposed best_count under that row's best successor byte; winner is the byte with highest summed best_count with lowest-byte tie-break; consistency=winner_best_count/summed_total; utility=winner_best_count*consistency, matching the donor utility form; no unavailable non-best successor histogram is reconstructed and no fifth-context data is used",
    "class_key_accumulation": "same exposed-best-count aggregation after mapping every key byte through the unchanged Y075 byte_class; retain the lexicographically smallest exact member key as deterministic representative anchor; payload winner derives only from summed historical best_count evidence",
    "target_retrieval": "for each frozen fifth-context key, choose nearest aggregate by raw four-byte Hamming for EXACT_KEY_ACCUMULATION and class-Hamming for CLASS_KEY_ACCUMULATION; deterministic lexical tie-break",
    "nonredundancy": "Y067-Y079 transported, projected, compressed, expanded, and retrieved static rows. None accumulated repeated historical evidence into a consolidated state before target retrieval.",
    "retain_revert": "Y080 is shadow attribution only; support authorizes a separately preregistered consolidation update rule, not accepted-state mutation."
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
    "historical_pool_builder": "byte-identical Y079 full eligible pool",
    "target_keys": [
      "SOURCE_CONDITIONED",
      "LOCAL_ONLY"
    ],
    "controls": [
      "FULL_ELIGIBLE_POOL"
    ],
    "new_mechanisms": [
      "EXACT_KEY_ACCUMULATION",
      "CLASS_KEY_ACCUMULATION"
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
    "scoring": "byte-identical Y079/Y078 clean-rescue and behavior-change accounting",
    "capacity": "16 total / 7 active / 9 retained",
    "heldout_consolidation_choice_count": 0,
    "post_result_consolidation_change_count": 0
  },
  "representation_cells": [
    "SOURCE_CONDITIONED_KEY × FULL_ELIGIBLE_POOL",
    "SOURCE_CONDITIONED_KEY × EXACT_KEY_ACCUMULATION",
    "SOURCE_CONDITIONED_KEY × CLASS_KEY_ACCUMULATION",
    "LOCAL_ONLY_KEY × FULL_ELIGIBLE_POOL",
    "LOCAL_ONLY_KEY × EXACT_KEY_ACCUMULATION",
    "LOCAL_ONLY_KEY × CLASS_KEY_ACCUMULATION"
  ],
  "outcome_definition": {
    "clean_rescue": "active_positive_prose_collateral_schedule_count > original_positive_prose_collateral_schedule_count AND active_partner_collateral_failure_count == 0",
    "consolidation_support": "at least one accumulation mechanism yields a clean rescue for a target key while the corresponding FULL_ELIGIBLE_POOL control is a non-rescue",
    "mixed_signal": "no clean rescue, but an accumulation mechanism improves positive-prose collateral schedule count or mean first-success packet versus its corresponding control without partner-collateral harm"
  },
  "metrics": [
    "variant_count",
    "historical_full_pool_row_count",
    "exact_key_group_count",
    "class_key_group_count",
    "multi_context_exact_group_count",
    "multi_context_class_group_count",
    "full_pool_clean_rescue_count",
    "exact_key_accumulation_clean_rescue_count",
    "class_key_accumulation_clean_rescue_count",
    "accumulation_behavior_change_count",
    "accumulation_partner_collateral_failure_count",
    "consolidation_support",
    "mixed_signal",
    "heldout_consolidation_choice_count",
    "post_result_consolidation_change_count",
    "source_state_mutation_count",
    "persistent_state_write_count",
    "capacity_growth_event_count",
    "invalid_evaluation_rows"
  ],
  "classification_rules": {
    "supported": "valid AND consolidation_support is true AND accumulation_partner_collateral_failure_count==0",
    "mixed": "valid AND supported is false AND mixed_signal is true",
    "negative": "valid AND both accumulation clean-rescue counts are zero AND mixed_signal is false",
    "invalid": "any parent, manifest identity, Y079 pool identity, accumulation formula, target-key identity, retrieval/tie-break, heldout ordering, deterministic replay, 16/7/9 capacity, provenance, persistence or accounting requirement fails"
  },
  "rsi_success": false,
  "rsi_success_note": "Y080 remains shadow attribution on studied contexts; a supported accumulation mechanism still requires separately frozen prospective disjoint-context validation.",
  "no_post_result_tuning_rule": "Do not alter manifests, historical pool, key/class grouping, exposed-best-count aggregation formulas, target keys, retrieval, six cells, schedules, split, packet count, activation/scoring, 16/7/9 capacity, classification or authority after primary output.",
  "successors": {
    "supported": {
      "contract_id": "yggdrasil-081-cumulative-evidence-consolidation-correction",
      "experiment_family": "bounded-consolidation-correction-081"
    },
    "mixed": {
      "contract_id": "yggdrasil-081-consolidation-dynamics-disambiguation",
      "experiment_family": "consolidation-dynamics-disambiguation-081"
    },
    "negative": {
      "contract_id": "yggdrasil-081-cumulative-state-transition-attribution",
      "experiment_family": "cumulative-state-transition-attribution-081"
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
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-consolidation-dynamics-attribution-080.ice"
  ]
}
