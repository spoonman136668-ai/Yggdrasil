{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-MULTIROW-LOW-SIGNAL-COMPETITION-032",
  "program": "Yggdrasil fixed-capacity simultaneous dormant-capability preservation",
  "question": "Can fixed-capacity preservation protect two dormant target capabilities at once while the remaining domain reconsolidates, without sacrificing the non-target benefit?",
  "hypothesis": "Across all six frozen schedules and all three unordered target pairs A/B, A/C, and B/C, select each target's highest maturity-cue-positive row from the all-domain sixteen-row state using training cue only. Deduplicate identical protected keys. Rebuild the interference state from the remaining non-target full training cue only. Insert every absent requested protected row one-for-one while evicting the same number of lowest-contribution interference rows under the non-target cue, then lower utility, then lexicographically larger key. All 36 target reactivation evaluations will remain positive and non-target heldout benefit retention will remain at least 0.95 with exactly 16 total / 7 active / 9 retained structures.",
  "exact_parent_sha": "cdc34b9828daca60bc8b21b2574c9eb6b3f6f8c4",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-multirow-low-signal-competition-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-ROTATING-LOW-SIGNAL-PRESERVATION-031",
    "github_run_id": "37117887608",
    "classification": "supported",
    "observation": {
      "rotating_case_count": 18,
      "positive_target_reactivation_case_count": 18,
      "minimum_target_preserved_incremental_correct_count": 1,
      "minimum_non_target_preserved_to_unprotected_fraction": 1
    },
    "diagnosis": "One-row preservation generalized losslessly when the dormant target rotated; the next bounded capacity stress is simultaneous requests from two dormant capabilities."
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
    "sources": "byte-identical 031 external manifest",
    "external_split": "byte-identical first 60% cue / final 40% heldout",
    "schedules": "all six frozen permutations",
    "maturity_rule": "byte-identical twelve-packet maturity cue",
    "all_domain_state": "byte-identical 031 all-domain state reconstruction",
    "protected_row_rule": "for each target independently, highest strictly positive target-maturity-cue contribution, then higher utility, then lexicographically smaller key",
    "active_selector": "byte-identical seven-active cue contribution selector",
    "capacity": "16 total / 7 active / 9 retained"
  },
  "competition_protocol": {
    "target_pairs": [["A","B"],["A","C"],["B","C"]],
    "case_count": 18,
    "target_evaluation_count": 36,
    "interference_input": "the single non-target full training cue only",
    "protected_key_deduplication": "identical requested target keys consume one protected slot",
    "eviction_ranking": "on the original interference state, ascending non-target training-cue contribution, then lower utility, then lexicographically larger key",
    "preservation": "insert every absent unique protected key and evict exactly the same number of ranked non-protected interference rows",
    "heldout_updates": false
  },
  "metrics_and_thresholds": [
    ["source_identity_mismatch_count","==",0],
    ["source_count","==",3],
    ["total_source_bytes","==",57272],
    ["base_training_identity_mismatch_count","==",0],
    ["schedule_count","==",6],
    ["target_pair_count","==",3],
    ["competition_case_count","==",18],
    ["target_reactivation_evaluation_count","==",36],
    ["positive_target_reactivation_evaluation_count","==",36],
    ["minimum_target_preserved_incremental_correct_count",">=",1],
    ["minimum_non_target_preserved_to_unprotected_fraction",">=",0.95],
    ["minimum_unique_requested_protected_row_count",">=",1],
    ["maximum_unique_requested_protected_row_count","<=",2],
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
    "supported": "Validity passes, all 36 target evaluations reactivate positively, and every non-target benefit-retention ratio is at least 0.95.",
    "mixed": "Validity passes and all target evaluations reactivate positively, but at least one non-target retention ratio falls below 0.95.",
    "negative": "Validity passes but at least one target reactivation evaluation is nonpositive.",
    "invalid": "Any sealed-parent, authority, source, target-pair, protected-row, deduplication, eviction, one-for-one preservation, capacity, determinism, or heldout-isolation criterion fails."
  },
  "validity_criteria": [
    "Exact sealed 031 parent and North Star identities match.",
    "Fresh READY_RESEARCH is bound to this exact preregistration and manifest.",
    "Each target's protected row is selected independently from its training maturity cue before heldout scoring.",
    "Interference candidate statistics and minimax consolidation use only the single non-target full training cue and never either target cue.",
    "Duplicate protected keys are deduplicated deterministically before capacity accounting.",
    "Eviction ranking is frozen from the original interference state using non-target training cue only and excludes requested protected keys.",
    "Preservation is one-for-one and retains exactly sixteen structures / seven active / nine retained.",
    "No heldout result selects protected rows, eviction rows, active rows, thresholds, or stopping conditions.",
    "Duplicate complete executions are byte-identical and all numeric outputs are finite.",
    "No tokenizer, external model, persistent corpus, capacity/radius change, LINKDEADKB execution, production authority, or post-result tuning occurs."
  ],
  "no_post_result_tuning_rule": "Do not alter sources, split, schedules, target pairs, maturity cues, protected-row rule, key deduplication, eviction ranking, selectors, 0.95 floor, capacity, metrics, thresholds, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-MULTIROW-MULTIEPOCH-COMPETITION-033",
    "intent": "stress simultaneous protected capabilities across repeated reconsolidation epochs at the same fixed 16/7/9 capacity"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-MULTIROW-COMPETITION-ATTRIBUTION-033",
    "intent": "attribute target collision versus non-target eviction cost before changing fixed capacity"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-multirow-low-signal-competition-032.ice",
    "research/applications/plane/exp-dgr-external-multirow-low-signal-competition-032.py",
    ".github/workflows/external-multirow-low-signal-competition-032.yml"
  ]
}
