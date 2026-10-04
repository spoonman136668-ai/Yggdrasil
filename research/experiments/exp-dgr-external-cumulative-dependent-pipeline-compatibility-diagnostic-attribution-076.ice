{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COMPATIBILITY-DIAGNOSTIC-ATTRIBUTION-076",
  "program": "Yggdrasil RSI tranche: target-local support attribution for retained-state compatibility false positives",
  "question": "Was the Y075 false ALLOW primarily caused by the source-conditioned row having too little target-local support, a locally disagreeing successor, or insufficient target-local precision despite source-class similarity?",
  "hypothesis": "On a disjoint fifth target context, pre-outcome candidate diagnostics derived only from the 60% training cue will identify rows likely to fail clean rescue. The primary candidate mechanism is LOW_TARGET_SUPPORT: a source-compatible row with target-local occurrence support below 25% of the maximum eligible-row support is more likely to produce no clean rescue. Two secondary preregistered mechanisms are SUCCESSOR_MISMATCH (target-local train argmax differs from candidate best) and LOW_TARGET_PRECISION (target-local argmax_count/occurrence_count <0.90). All flags for all eligible rows freeze before any 40% evaluation or shadow outcome is opened. This experiment is attribution only and does not alter the operational gate.",
  "exact_parent_sha": "a1e582e2b4c8855ba5cd7564fd114bdf78939077",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-compatibility-diagnostic-attribution-r1",
  "predecessor": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-RETAINED-STATE-INCOMPATIBILITY-GATE-075",
    "github_run_id": 37169535389,
    "classification": "mixed",
    "validity_pass": true,
    "exact_predecessor_sha": "a1e582e2b4c8855ba5cd7564fd114bdf78939077",
    "observation": {
      "decision": "ALLOW_SOURCE_PRIOR",
      "source_behavior_change_count": 1,
      "source_positive_prose_collateral_schedule_count": 4,
      "original_positive_prose_collateral_schedule_count": 4,
      "source_partner_collateral_failure_count": 0,
      "source_selected_train_occurrence_count": 1,
      "source_selected_train_argmax_count": 1,
      "local_selected_train_occurrence_count": 68,
      "local_selected_train_argmax_count": 66,
      "source_specificity_gain": 4
    },
    "eliminated_hypothesis": "source-class specificity gain alone is sufficient to justify retained-state-guided ALLOW",
    "strengthened_hypothesis": "source compatibility must be conditioned on enough target-local evidence before source priors are allowed to override locally supported alternatives"
  },
  "cause_effect_trace": {
    "observed_failure": "Y075 allowed the source prior; the selected row changed behavior but did not improve positive prose collateral over ORIGINAL and therefore was not a clean rescue.",
    "internal_diagnostic": "source-selected target-local support was 1 occurrence / 1 argmax versus 68 occurrences / 66 argmax for the local-only row.",
    "attributed_causes_under_test": [
      "low target-local support",
      "target-local successor disagreement",
      "low target-local precision"
    ],
    "candidate_corrective_mechanisms": "none in Y076; attribution only",
    "frozen_candidate_selection_rule": "evaluate every eligible candidate row; do not choose a post-result diagnostic",
    "exact_bounded_delta": "add training-only diagnostic flags and shadow-evaluate the already-defined bounded candidate rows; accepted source state remains immutable",
    "qualification": "exact fifth-manifest identity, deterministic double replay, one-shot READY_RESEARCH, all flags frozen before held-out evaluation",
    "held_out_result": "candidate clean-rescue outcome opened only after all candidate diagnostics freeze",
    "retain_revert": "no retained-state mutation or gate change in Y076",
    "next_hypothesis": "if one diagnostic is supported, add only that bounded diagnostic to the compatibility gate and validate prospectively on another disjoint context; otherwise test preregistered diagnostic interactions without forcing retained-state reuse"
  },
  "target_manifest": {
    "path": "research/experiments/external-future-data-fifth-context-manifest-076.json",
    "sha256": "7077d2b72d8954afc24f36b2971393acc11e3b345f7c3521102c20347b9c6171",
    "source_count": 3,
    "effective_total_bytes": 57272
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
    "donor_builder": "byte-identical Y075 canonical B+C donor generalized only to exact fifth-target source identities",
    "split": "60% training cue / 40% evaluation",
    "schedules": [
      "A-C-B",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "future_packets": 12,
    "activation_position": 7,
    "guard_injection_scoring": "byte-identical Y075/Y068 shadow variant",
    "capacity": "16 total / 7 active / 9 retained",
    "candidate_pool": "all Y075-eligible target rows; max 16"
  },
  "diagnostic_definitions": {
    "LOW_TARGET_SUPPORT": "train_occurrence_count / max eligible train_occurrence_count < 0.25",
    "SUCCESSOR_MISMATCH": "target-local train_argmax != candidate best",
    "LOW_TARGET_PRECISION": "train_argmax_count / train_occurrence_count < 0.90"
  },
  "outcome_definition": {
    "clean_rescue": "active_positive_prose_collateral_schedule_count > original_positive_prose_collateral_schedule_count AND active_partner_collateral_failure_count == 0",
    "non_rescue": "not clean_rescue"
  },
  "metrics": [
    "eligible_candidate_count",
    "diagnostic_coverage",
    "flagged_non_rescue_rate",
    "unflagged_non_rescue_rate",
    "non_rescue_rate_delta",
    "source_state_mutation_count",
    "persistent_state_write_count",
    "heldout_diagnostic_input_count",
    "post_result_diagnostic_change_count",
    "capacity_growth_event_count"
  ],
  "classification_rules": {
    "supported": "valid and at least one preregistered diagnostic has flagged_count>=2, unflagged_count>=2, coverage between 0.20 and 0.80 inclusive, and flagged non-rescue rate >= unflagged non-rescue rate + 0.30",
    "mixed": "valid and at least one diagnostic has flagged_count>=1, unflagged_count>=1, and flagged non-rescue rate > unflagged non-rescue rate but no diagnostic meets supported thresholds",
    "negative": "valid and no diagnostic has higher flagged non-rescue rate than unflagged",
    "invalid": "any parent, target-manifest identity, source-state identity, donor/candidate identity, diagnostic definition, heldout ordering, deterministic replay, capacity, provenance, persistence or accounting requirement fails"
  },
  "rsi_success": false,
  "rsi_success_note": "Y076 is attribution only; even supported diagnostics do not establish useful retained-state transfer.",
  "no_post_result_tuning_rule": "Do not alter target sources, source state, donor construction, candidate eligibility, split, diagnostic definitions or thresholds, shadow activation/scoring, schedules, packet count, 16/7/9 capacity, outcome definition, classification, or authority after primary output.",
  "successors": {
    "supported": {
      "contract_id": "yggdrasil-077-support-aware-compatibility-gate",
      "experiment_family": "support-aware-compatibility-gate-077"
    },
    "mixed": {
      "contract_id": "yggdrasil-077-compatibility-factorial",
      "experiment_family": "compatibility-factorial-attribution-077"
    },
    "negative": {
      "contract_id": "yggdrasil-077-compatibility-factorial",
      "experiment_family": "compatibility-factorial-attribution-077"
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
    "research/experiments/external-future-data-fifth-context-manifest-076.json",
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-compatibility-diagnostic-attribution-076.ice"
  ]
}
