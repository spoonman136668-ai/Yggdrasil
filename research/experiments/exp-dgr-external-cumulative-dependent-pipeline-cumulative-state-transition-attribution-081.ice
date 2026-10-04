{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CUMULATIVE-STATE-TRANSITION-ATTRIBUTION-081",
  "program": "Yggdrasil RSI tranche: cumulative state-transition attribution",
  "question": "After Y080 showed that static historical rows and deterministic evidence accumulation both fail, does transferable cumulative information live in how retained states change across successive contexts rather than in any single or aggregated state?",
  "hypothesis": "Y079 preserved all eligible historical rows and Y080 consolidated repeated exact/class keys, yet neither static storage nor summed evidence yielded a clean fifth-context rescue. Freeze a transition representation over the same transfer→third→fourth historical order. For each exact or byte-class key group that appears in at least two successive historical contexts, derive only training-visible transition fields: best-byte changed/stable, best-count delta normalized by prior total, consistency delta, utility delta, and context recurrence count. For each frozen fifth-context target key, compare three shadow payload sources: LAST_STATE uses the latest matching historical state unchanged; EXACT_TRANSITION selects the latest exact-key transition whose prior→current direction most closely matches the target-local training row's direction from source-conditioned to local-only diagnostics; CLASS_TRANSITION applies the same rule at the unchanged Y075 byte-class signature level. No fifth-context outcome may select a transition or alter the rule.",
  "exact_parent_sha": "3560ad1ce4d6f72cd2a0e168ca10cd3968c51318",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-cumulative-state-transition-attribution-r1",
  "predecessor": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONSOLIDATION-DYNAMICS-ATTRIBUTION-080",
    "github_run_id": 37207649561,
    "classification": "negative",
    "validity_pass": true,
    "observation": {
      "historical_full_pool_row_count": 17,
      "exact_key_group_count": 2,
      "class_key_group_count": 2,
      "multi_context_exact_group_count": 2,
      "multi_context_class_group_count": 2,
      "full_pool_clean_rescue_count": 0,
      "exact_key_accumulation_clean_rescue_count": 0,
      "class_key_accumulation_clean_rescue_count": 0,
      "accumulation_behavior_change_count": 2,
      "accumulation_partner_collateral_failure_count": 0,
      "consolidation_support": 0,
      "mixed_signal": 0
    },
    "eliminated_hypothesis": "static full-pool storage or simple exact/class cumulative evidence aggregation is sufficient to produce useful fifth-context transfer",
    "strengthened_hypothesis": "the missing cumulative signal may be temporal or relational—how a retained state changes across contexts—not the marginal state itself"
  },
  "cause_effect_trace": {
    "observed_failure": "Both exact-key and class-key accumulation changed behavior in some arms but never improved the already-positive prose-collateral baseline and produced zero clean rescues.",
    "residual_cause_under_test": "MISSING_STATE_TRANSITION_REPRESENTATION",
    "historical_order": [
      "transfer",
      "third",
      "fourth"
    ],
    "transition_fields": [
      "best_byte_changed",
      "normalized_best_count_delta",
      "consistency_delta",
      "utility_delta",
      "recurrence_count"
    ],
    "target_direction_proxy": "training-only difference between the frozen fifth-context SOURCE_CONDITIONED and LOCAL_ONLY candidate rows on best byte class, normalized best_count/total, consistency and utility; no evaluation bytes or outcomes",
    "exact_transition_rule": "among exact-key transitions, rank minimum L1 distance to the target direction proxy across the numeric transition fields, then newest destination context, then lexical key",
    "class_transition_rule": "same ranking after grouping keys by the unchanged Y075 four-position byte_class signature",
    "payload_projection": "project only the destination state's immutable exposed payload onto the already-frozen target key; transition fields choose a historical destination but do not synthesize a new payload",
    "exact_bounded_delta": "transition selection only; reproduce LAST_STATE control; no extra retained capacity, payload averaging, accepted-state mutation, persistence, operational gate change, or post-result selection",
    "nonredundancy": "Y067-Y080 tested materialization, transport, activation position, payload rebinding, target-local induction, compatibility gates, static multi-context storage, full-pool retrieval and cumulative count aggregation. None represented ordered historical state change as the retrieval signal.",
    "retain_revert": "Y081 is shadow attribution only; support authorizes only a separately preregistered transition-aware correction and prospective disjoint-context test."
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
    "historical_pool_builder": "byte-identical Y079/Y080 full eligible historical pool",
    "target_keys": [
      "SOURCE_CONDITIONED",
      "LOCAL_ONLY"
    ],
    "target_direction_proxy": "training-only; frozen before any fifth evaluation opens",
    "controls": [
      "LAST_STATE"
    ],
    "mechanisms": [
      "EXACT_TRANSITION",
      "CLASS_TRANSITION"
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
    "scoring": "byte-identical Y080 clean-rescue and behavior-change accounting",
    "capacity": "16 total / 7 active / 9 retained",
    "heldout_transition_choice_count": 0,
    "post_result_transition_change_count": 0
  },
  "representation_cells": [
    "SOURCE_CONDITIONED_KEY × LAST_STATE",
    "SOURCE_CONDITIONED_KEY × EXACT_TRANSITION",
    "SOURCE_CONDITIONED_KEY × CLASS_TRANSITION",
    "LOCAL_ONLY_KEY × LAST_STATE",
    "LOCAL_ONLY_KEY × EXACT_TRANSITION",
    "LOCAL_ONLY_KEY × CLASS_TRANSITION"
  ],
  "metrics": [
    "variant_count",
    "historical_full_pool_row_count",
    "exact_transition_count",
    "class_transition_count",
    "target_direction_proxy_count",
    "transition_context_change_count",
    "last_state_clean_rescue_count",
    "exact_transition_clean_rescue_count",
    "class_transition_clean_rescue_count",
    "transition_behavior_change_count",
    "transition_partner_collateral_failure_count",
    "transition_support",
    "mixed_signal",
    "heldout_transition_choice_count",
    "post_result_transition_change_count",
    "source_state_mutation_count",
    "persistent_state_write_count",
    "capacity_growth_event_count",
    "invalid_evaluation_rows"
  ],
  "classification_rules": {
    "supported": "valid AND at least one transition mechanism chooses a different destination state than LAST_STATE for >=1 target key AND that mechanism yields >=1 clean rescue while the corresponding LAST_STATE cell is a non-rescue AND transition_partner_collateral_failure_count==0",
    "mixed": "valid AND a transition mechanism changes destination state and favorably changes prose collateral or first-success timing versus LAST_STATE without clean rescue or partner harm",
    "negative": "valid AND neither transition mechanism yields a clean rescue or favorable mixed signal",
    "invalid": "any parent, four-manifest identity, Y079/Y080 historical-pool identity, historical ordering, transition-field formula, target-direction proxy, transition ranking/tie-break, heldout ordering, deterministic replay, 16/7/9 capacity, provenance, persistence or accounting requirement fails"
  },
  "rsi_success": false,
  "rsi_success_note": "Y081 remains shadow attribution on studied contexts; support still requires a separately frozen prospective disjoint-context replication before RSI transfer success.",
  "no_post_result_tuning_rule": "Do not alter manifests, historical order, pool, transition fields, target-direction proxy, ranking/tie-breaks, target keys, payload projection, six cells, schedules, split, packet count, activation/scoring, 16/7/9 capacity, classification or authority after primary output.",
  "successors": {
    "supported": {
      "contract_id": "yggdrasil-082-transition-aware-consolidation-correction",
      "experiment_family": "bounded-transition-correction-082"
    },
    "mixed": {
      "contract_id": "yggdrasil-082-transition-attribution-disambiguation",
      "experiment_family": "transition-disambiguation-082"
    },
    "negative": {
      "contract_id": "yggdrasil-082-memory-update-rule-attribution",
      "experiment_family": "memory-update-rule-attribution-082"
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
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-cumulative-state-transition-attribution-081.ice"
  ]
}
