{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-RESIDUAL-BRIDGE-073",
  "program": "Yggdrasil corrective RSI tranche: role-preserving context translation of retained state",
  "question": "Can the retained source state's operative role be translated into the target context by mapping a local trigger to its strongest training-only successor that differs from the target baseline, while keeping the accepted source state itself immutable?",
  "hypothesis": "Y72 established that key-only translation with source best=32 is behaviorally inert. The active inference path uses only key->best; other retained-row fields do not affect prediction. Therefore 073 preserves the accepted source state byte-for-byte outside the bridge and translates only its functional role. First verify from training-only state that the source retained row is an OVERRIDE role: source best differs from the fixed base baseline prediction for source key terminal byte. For each of the exact two frozen Y71 target keys, compute the fixed base baseline prediction for that key's terminal byte and the complete target-prose training successor histogram. Eligible target triggers must have at least one observed successor different from baseline. For each eligible trigger choose ALT_BEST as the highest-count successor excluding the baseline prediction, with lowest-byte tie break; compatibility score = ALT_BEST_COUNT / key_occurrence_count. Freeze the highest-score trigger before evaluation, lexicographic key tie-break. Build an ephemeral bridge map entry local_key -> ALT_BEST. The accepted source state is not rewritten or persisted. Evaluate selected and alternate eligible triggers as preregistered arms under byte-identical 068 schedules/scoring/capacity. No held-out labels may influence trigger or successor selection.",
  "exact_parent_sha": "1d6f270f829240b2a361d5482b209587a65cc95d",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-context-residual-bridge-r1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "predecessor": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-BRIDGE-TRANSLATION-072",
    "github_run_id": 37167925315,
    "classification": "negative",
    "validity_pass": true,
    "decision": "BRIDGE",
    "exact_predecessor_sha": "1d6f270f829240b2a361d5482b209587a65cc95d",
    "observation": {
      "selected_trigger_rank": 1,
      "selected_key": [
        32,
        116,
        104,
        101
      ],
      "selected_compatibility_score": 6.117647058823529,
      "alternate_trigger_rank": 2,
      "alternate_key": [
        32,
        97,
        110,
        100
      ],
      "alternate_compatibility_score": 1.972972972972973,
      "selected_bridge_behavior_change_count": 0,
      "alternate_bridge_behavior_change_count": 0,
      "selected_positive_prose_collateral_schedule_count": 0,
      "alternate_positive_prose_collateral_schedule_count": 0,
      "invalid_evaluation_rows": 0
    },
    "causal_update": "active_map maps only row.key to row.best; source count/consistency/utility/cell-index fields are not inference-active. Key-only Y72 retained best=32, so it failed to create a context-specific predictive intervention."
  },
  "cause_effect_trace": {
    "observed_failure": "Y72 source-payload bridge was valid but behaviorally identical to original/passive across all packets and schedules",
    "internal_diagnostic": "active_map and model_correct_counts show that only key and best participate in active prediction",
    "attributed_cause": "the translated target key inherited source best=32, which does not encode a target-specific residual prediction and can collapse to the target baseline/local mapping",
    "candidate_corrective_mechanisms": [
      "role-preserving baseline-residual successor translation",
      "compatibility-based reject/fallback"
    ],
    "frozen_candidate_selection_rule": "among the same two Y71 keys, choose highest training-only nonbaseline alternative-successor fraction; lexicographic tie-break",
    "exact_bounded_delta": "ephemeral local_key->ALT_BEST adapter only; accepted source state untouched; same 16/7/9 capacity and schedules",
    "qualification": "exact third-manifest identity, deterministic double replay, exact source-state identity, one-shot READY_RESEARCH",
    "held_out_result": "evaluation opened only after baseline, successor histograms, ALT_BEST values and selected trigger are frozen",
    "retain_revert": "adapter discarded after run; source retained state unchanged; unsuccessful translation cannot persist",
    "next_hypothesis": "if successful, verify retain/revert and then repeat on disjoint context; if not, test multi-key/context-width bridge rather than arbitrary payload reweighting"
  },
  "source_state": {
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
  "frozen_target_keys": [
    {
      "rank": 1,
      "key": [
        32,
        116,
        104,
        101
      ]
    },
    {
      "rank": 2,
      "key": [
        32,
        97,
        110,
        100
      ]
    }
  ],
  "translation_contract": {
    "source_role_requirement": "source best != base baseline prediction for source key terminal byte",
    "target_baseline": "byte-identical learner.baseline_predict(base, local_key[3]) using base training only",
    "successor_histogram": "technical-prose training cue only; count byte immediately after each exact local key occurrence",
    "alternative_successor": "highest-count observed successor != target baseline; lowest byte tie-break",
    "eligibility": "key occurrence >=1 and alternative successor count >=1",
    "compatibility_score": "alternative_successor_count / key_occurrence_count",
    "selection": "highest compatibility score, lexicographic key tie-break",
    "selected_arm_count": 1,
    "alternate_falsification_arm": "the other eligible frozen key, if present",
    "heldout_selection_count": 0,
    "post_result_adapter_choice_count": 0
  },
  "bridge_contract": {
    "persistent_source_state_mutation": false,
    "persistent_adapter_write": false,
    "adapter_entry_count": 1,
    "inference_active_fields": [
      "key",
      "best"
    ],
    "capacity": "16 total / 7 active / 9 retained",
    "activation_position": 7,
    "schedules": [
      "A-C-B",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "future_packets": 12,
    "success_rule": "dependent incremental correct >0 AND technical-prose collateral incremental correct >0 AND partner collateral incremental correct >0"
  },
  "classification_rules": {
    "supported": "valid, selected residual bridge changes behavior and improves positive prose collateral over ORIGINAL on at least one schedule with zero selected partner collateral failures and no source/capacity/persistence violation",
    "mixed": "valid and alternate residual bridge rescues or selected bridge changes behavior without prose-collateral rescue",
    "negative": "valid and neither eligible residual bridge produces useful behavior change/prose-collateral improvement",
    "invalid": "any parent, authority, manifest identity, source-state identity, active-map causal premise, baseline/successor histogram, selection isolation, adapter restriction, deterministic replay, capacity, provenance or accounting requirement fails"
  },
  "no_post_result_tuning_rule": "Do not alter source state, target keys, base baseline definition, successor histogram, nonbaseline exclusion, tie-break, compatibility score, selection rule, activation rank, schedules, scoring, capacity, thresholds, classification or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-RESIDUAL-BRIDGE-RETAIN-REVERT-074",
    "intent": "verify exact adapter retain/revert semantics while source state remains unchanged, then replicate on disjoint context"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-WIDTH-BRIDGE-ATTRIBUTION-074",
    "intent": "test whether a broader/multi-key target context is required, without arbitrary persistent-state synthesis"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-context-residual-bridge-073.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-residual-bridge-073.py",
    ".github/workflows/external-cumulative-dependent-pipeline-context-residual-bridge-073.yml"
  ]
}
