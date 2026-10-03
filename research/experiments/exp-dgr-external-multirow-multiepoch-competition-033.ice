{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-MULTIROW-MULTIEPOCH-COMPETITION-033",
  "program": "Yggdrasil fixed-capacity simultaneous dormant-capability preservation across repeated reconsolidation",
  "question": "Do the supported multirow preservation rules remain stable when the same two dormant target capabilities must survive repeated reconsolidation epochs of the remaining domain?",
  "hypothesis": "Across all six frozen schedules, all three unordered target pairs A/B, A/C, B/C, and non-target packet epochs 4, 8, and 12, reuse the exact 032 protected-row selection, deduplication, one-for-one insertion, eviction ranking, and 16/7/9 active-retained selector. All 108 target reactivation evaluations will remain positive and every non-target heldout benefit-retention ratio will remain at least 0.95 without capacity growth.",
  "exact_parent_sha": "13d34716f9e5523d2df8f4bf88419690880d2649",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-multirow-multiepoch-competition-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-MULTIROW-LOW-SIGNAL-COMPETITION-032",
    "github_run_id": "37118557871",
    "classification": "supported",
    "observation": {
      "competition_case_count": 18,
      "target_reactivation_evaluation_count": 36,
      "positive_target_reactivation_evaluation_count": 36,
      "minimum_target_preserved_incremental_correct_count": 1,
      "minimum_non_target_preserved_to_unprotected_fraction": 1,
      "minimum_unique_requested_protected_row_count": 1,
      "maximum_unique_requested_protected_row_count": 2
    },
    "diagnosis": "Two simultaneous dormant target requests fit losslessly under fixed capacity in every schedule; temporal persistence across repeated non-target reconsolidation is the next bounded stress."
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
    "sources": "byte-identical 032 external manifest",
    "external_split": "byte-identical first 60% cue / final 40% heldout",
    "schedules": "all six frozen permutations",
    "target_pairs": [["A","B"],["A","C"],["B","C"]],
    "maturity_rule": "byte-identical twelve-packet maturity cue",
    "all_domain_state": "byte-identical 032 all-domain reconstruction",
    "protected_row_rule": "byte-identical 032 per-target rule",
    "protected_key_deduplication": "byte-identical 032 key deduplication",
    "eviction_ranking": "byte-identical 032 non-target cue contribution, lower utility, lexicographically larger key",
    "active_selector": "byte-identical seven-active cue contribution selector",
    "capacity": "16 total / 7 active / 9 retained"
  },
  "multiepoch_protocol": {
    "epoch_packet_indices": [4,8,12],
    "epoch_count": 3,
    "competition_epoch_case_count": 54,
    "target_reactivation_evaluation_count": 108,
    "interference_input": "only the single non-target cumulative prefix through the current epoch",
    "preservation": "recompute the same frozen 032 one-for-one preservation independently at each epoch",
    "heldout_updates": false
  },
  "metrics_and_thresholds": [
    ["source_identity_mismatch_count","==",0],
    ["source_count","==",3],
    ["total_source_bytes","==",57272],
    ["base_training_identity_mismatch_count","==",0],
    ["schedule_count","==",6],
    ["target_pair_count","==",3],
    ["epoch_count","==",3],
    ["competition_epoch_case_count","==",54],
    ["target_reactivation_evaluation_count","==",108],
    ["positive_target_reactivation_evaluation_count","==",108],
    ["minimum_target_preserved_incremental_correct_count",">=",1],
    ["minimum_non_target_preserved_to_unprotected_fraction",">=",0.95],
    ["final_epoch_positive_target_evaluation_count","==",36],
    ["preserved_state_structure_count_min","==",16],
    ["preserved_state_structure_count_max","==",16],
    ["active_structure_count_min","==",7],
    ["active_structure_count_max","==",7],
    ["retained_structure_count_min","==",9],
    ["retained_structure_count_max","==",9],
    ["target_interference_leakage_count","==",0],
    ["heldout_selection_use_count","==",0],
    ["capacity_growth_event_count","==",0],
    ["tokenizer_use_count","==",0],
    ["external_model_call_count","==",0],
    ["invalid_evaluation_rows","==",0]
  ],
  "classification_rules": {
    "supported": "Validity passes, all 108 target evaluations remain positive, all 36 final-epoch target evaluations are positive, and every non-target retention ratio is at least 0.95.",
    "mixed": "Validity passes and all final-epoch target evaluations are positive, but an intermediate target evaluation or non-target retention threshold fails.",
    "negative": "Validity passes but at least one final-epoch target evaluation is nonpositive.",
    "invalid": "Any sealed-parent, authority, source, epoch, target-pair, preservation, capacity, determinism, or heldout-isolation criterion fails."
  },
  "validity_criteria": [
    "Exact sealed 032 parent and North Star identities match.",
    "Fresh READY_RESEARCH is bound to this exact preregistration and manifest.",
    "Protected rows are selected only from training maturity cues and remain frozen across the three non-target epochs within each schedule-target-pair case.",
    "Each interference state uses only the single non-target cumulative training prefix for that epoch.",
    "032 key deduplication and one-for-one eviction rules are unchanged.",
    "Each epoch retains exactly sixteen structures / seven active / nine retained.",
    "No heldout result selects rows, thresholds, epochs, or stopping conditions.",
    "Duplicate complete executions are byte-identical and all numeric outputs are finite.",
    "No tokenizer, external model, persistent corpus, capacity/radius change, LINKDEADKB execution, production authority, or post-result tuning occurs."
  ],
  "no_post_result_tuning_rule": "Do not alter sources, split, schedules, target pairs, epochs, maturity cues, protected-row rule, deduplication, eviction ranking, selectors, 0.95 floor, capacity, metrics, thresholds, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-HORIZON-034",
    "intent": "extend simultaneous fixed-capacity preservation across a longer preregistered cumulative horizon while retaining the same substrate"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-MULTIROW-MULTIEPOCH-ATTRIBUTION-034",
    "intent": "attribute temporal target loss versus non-target eviction cost before changing fixed capacity"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-multirow-multiepoch-competition-033.ice",
    "research/applications/plane/exp-dgr-external-multirow-multiepoch-competition-033.py",
    ".github/workflows/external-multirow-multiepoch-competition-033.yml"
  ]
}
