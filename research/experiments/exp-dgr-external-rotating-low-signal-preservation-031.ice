{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-ROTATING-LOW-SIGNAL-PRESERVATION-031",
  "program": "Yggdrasil fixed-capacity rotating dormant-domain preservation",
  "question": "Does the cue-side one-row preservation rule generalize when each domain in turn is treated as the dormant target while the other two reconsolidate?",
  "hypothesis": "Across all six frozen schedules and each target domain A/B/C, identify that target's highest maturity-cue-positive row from the all-domain sixteen-row state using training cue only. Rebuild the fixed-capacity interference state from the other two full training cues. If the protected row is absent, insert it one-for-one and evict the interference row with minimum summed contribution under the two non-target full training cues, then lower utility, then lexicographically larger key. All 18 schedule-target cases will reactivate positively and non-target heldout benefit retention will remain at least 0.95 without changing 16/7/9 capacity.",
  "exact_parent_sha": "073f351226c1ba7ecd481347eb3d93943f2e1d20",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-rotating-low-signal-preservation-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-MULTIEPOCH-CRITICAL-ROW-PRESERVATION-030",
    "github_run_id": "37113574777",
    "classification": "supported",
    "observation": {
      "preservation_epoch_case_count": 18,
      "c_positive_epoch_case_count": 18,
      "final_epoch_c_positive_case_count": 6,
      "minimum_c_preserved_incremental_correct_count": 1,
      "minimum_non_target_preserved_to_unprotected_fraction": 1
    },
    "diagnosis": "The one-row protection rule remains lossless for C across three A/B reconsolidation epochs; next test is whether the same cue-side rule generalizes when the dormant target rotates."
  },
  "external_authority": {
    "ckb_plane_main_sha": "36d99a0257120ede57bb96638660d35014dd529e",
    "manifest_sha256": "75cdb3b97dbb7017299f573d506f07095ed89c06264b29724b78f29c909d4da4",
    "research_decision_required": "READY_RESEARCH",
    "execution_host_policy": "GitHub-hosted compute only; host distinct from LINKDEADKB",
    "persistent_corpus": false,
    "external_model_calls": false,
    "production_authority": false
  },
  "frozen_reuse": {
    "sources": "byte-identical 030 external manifest",
    "external_split": "byte-identical first 60% cue / final 40% heldout",
    "schedules": "all six frozen permutations",
    "maturity_rule": "byte-identical twelve-packet maturity cue",
    "all_domain_state": "byte-identical 030 all-domain state reconstruction",
    "protected_row_rule": "highest strictly positive target-maturity-cue contribution, then higher utility, then lexicographically smaller key",
    "eviction_rule": "minimum summed contribution under the two non-target full training cues, then lower utility, then lexicographically larger key",
    "active_selector": "byte-identical seven-active cue contribution selector",
    "capacity": "16 total / 7 active / 9 retained"
  },
  "rotating_protocol": {
    "target_domains": [
      "A",
      "B",
      "C"
    ],
    "case_count": 18,
    "target_reactivation_cue": "target maturity cue",
    "interference_inputs": "the two non-target full training cues only",
    "target_leakage": false,
    "preservation": "one-for-one only if protected row absent",
    "heldout_updates": false
  },
  "metrics_and_thresholds": [
    [
      "source_identity_mismatch_count",
      "==",
      0
    ],
    [
      "source_count",
      "==",
      3
    ],
    [
      "total_source_bytes",
      "==",
      57272
    ],
    [
      "base_training_identity_mismatch_count",
      "==",
      0
    ],
    [
      "schedule_count",
      "==",
      6
    ],
    [
      "target_domain_count",
      "==",
      3
    ],
    [
      "rotating_case_count",
      "==",
      18
    ],
    [
      "positive_target_reactivation_case_count",
      "==",
      18
    ],
    [
      "minimum_target_preserved_incremental_correct_count",
      ">=",
      1
    ],
    [
      "minimum_non_target_preserved_to_unprotected_fraction",
      ">=",
      0.95
    ],
    [
      "preserved_state_structure_count_min",
      "==",
      16
    ],
    [
      "preserved_state_structure_count_max",
      "==",
      16
    ],
    [
      "active_structure_count_min",
      "==",
      7
    ],
    [
      "active_structure_count_max",
      "==",
      7
    ],
    [
      "retained_structure_count_min",
      "==",
      9
    ],
    [
      "retained_structure_count_max",
      "==",
      9
    ],
    [
      "target_interference_leakage_count",
      "==",
      0
    ],
    [
      "heldout_selection_use_count",
      "==",
      0
    ],
    [
      "capacity_growth_event_count",
      "==",
      0
    ],
    [
      "tokenizer_use_count",
      "==",
      0
    ],
    [
      "external_model_call_count",
      "==",
      0
    ],
    [
      "invalid_evaluation_rows",
      "==",
      0
    ]
  ],
  "classification_rules": {
    "supported": "Validity passes, all 18 rotating target cases reactivate positively, and every non-target benefit-retention ratio is at least 0.95.",
    "mixed": "Validity passes and all target cases reactivate positively, but at least one non-target retention ratio falls below 0.95.",
    "negative": "Validity passes but at least one target fails to reactivate positively.",
    "invalid": "Any sealed-parent, authority, source, target-omission, protected-row, one-for-one preservation, capacity, determinism, or heldout-isolation criterion fails."
  },
  "validity_criteria": [
    "Exact sealed 030 parent and North Star identities match.",
    "Fresh READY_RESEARCH is bound to this exact preregistration and manifest.",
    "Protected-row identity is computed independently for each schedule-target case using target training maturity cue only.",
    "Interference candidate statistics and minimax consolidation use exactly the two non-target full training cues and no target cue.",
    "Eviction uses only non-target training-cue contributions, utility, and key tie-breaks.",
    "Preservation is one-for-one and retains exactly sixteen structures / seven active / nine retained.",
    "No heldout result selects protected row, eviction row, active rows, threshold, or stopping condition.",
    "Duplicate executions are byte-identical and all numeric outputs are finite.",
    "No tokenizer, external model, persistent corpus, capacity/radius change, LINKDEADKB execution, production authority, or post-result tuning occurs."
  ],
  "no_post_result_tuning_rule": "Do not alter sources, split, schedules, target rotation, protected-row definition, eviction rule, selectors, 0.95 floor, capacity, metrics, thresholds, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-MULTIROW-LOW-SIGNAL-COMPETITION-032",
    "intent": "stress fixed-capacity preservation when multiple dormant low-signal capabilities request protection simultaneously"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-ROTATING-PRESERVATION-ATTRIBUTION-032",
    "intent": "attribute domain-specific preservation failure or non-target cost before changing capacity"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-rotating-low-signal-preservation-031.ice",
    "research/applications/plane/exp-dgr-external-rotating-low-signal-preservation-031.py",
    ".github/workflows/external-rotating-low-signal-preservation-031.yml"
  ]
}
