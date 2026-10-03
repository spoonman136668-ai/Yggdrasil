{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-HORIZON-035",
  "program": "Yggdrasil fixed-capacity simultaneous dormant-capability preservation across the full cumulative cue horizon",
  "question": "Does supported two-target preservation remain stable at every cumulative non-target cue packet rather than only the sampled packet-4/8/12 checkpoints?",
  "hypothesis": "Reuse the exact supported 034 mechanism, zero-baseline scoring contract, all six schedules, and all three target pairs, but evaluate every cumulative non-target packet 1 through 12. All 432 target reactivation evaluations and all 36 packet-12 target evaluations will remain positive, every zero-baseline case will remain nonnegative, and every ratio-applicable non-target case will retain at least 0.95 of unprotected benefit under fixed 16 total / 7 active / 9 retained capacity.",
  "exact_parent_sha": "6fdce5420ffe461e08f356be737c50d81772d1c2",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-cumulative-multirow-horizon-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-MULTIROW-MULTIEPOCH-ZEROBASELINE-034",
    "github_run_id": "37119733513",
    "classification": "supported",
    "observation": {
      "competition_epoch_case_count": 54,
      "target_reactivation_evaluation_count": 108,
      "positive_target_reactivation_evaluation_count": 108,
      "final_epoch_positive_target_evaluation_count": 36,
      "minimum_target_preserved_incremental_correct_count": 1,
      "zero_baseline_non_target_case_count": 12,
      "ratio_applicable_non_target_case_count": 42,
      "zero_baseline_preserved_negative_count": 0,
      "minimum_applicable_non_target_preserved_to_unprotected_fraction": 1
    },
    "diagnosis": "The two-target preservation mechanism is valid across sampled early/mid/final reconsolidation checkpoints once zero-baseline retention semantics are explicit. The next bounded stress is the entire twelve-packet cumulative horizon."
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
    "sources": "byte-identical 034 external manifest",
    "external_split": "byte-identical first 60% cue / final 40% heldout",
    "schedules": "all six frozen permutations",
    "target_pairs": [["A","B"],["A","C"],["B","C"]],
    "maturity_rule": "byte-identical twelve-packet maturity cue",
    "all_domain_state": "byte-identical 034 all-domain reconstruction",
    "protected_row_rule": "byte-identical 034 per-target rule",
    "protected_key_deduplication": "byte-identical 034",
    "eviction_ranking": "byte-identical 034 non-target cue contribution, lower utility, lexicographically larger key",
    "active_selector": "byte-identical seven-active cue contribution selector",
    "zero_baseline_contract": "byte-identical 034 ratio-domain and safety semantics",
    "capacity": "16 total / 7 active / 9 retained"
  },
  "full_horizon_protocol": {
    "epoch_packet_indices": [1,2,3,4,5,6,7,8,9,10,11,12],
    "epoch_count": 12,
    "competition_epoch_case_count": 216,
    "target_reactivation_evaluation_count": 432,
    "final_epoch_target_evaluation_count": 36,
    "interference_input": "only the single non-target cumulative training prefix through the current packet",
    "preservation": "recompute the same frozen 034 one-for-one preservation independently at every packet",
    "heldout_updates": false
  },
  "metrics_and_thresholds": [
    ["source_identity_mismatch_count","==",0],
    ["source_count","==",3],
    ["total_source_bytes","==",57272],
    ["base_training_identity_mismatch_count","==",0],
    ["schedule_count","==",6],
    ["target_pair_count","==",3],
    ["epoch_count","==",12],
    ["competition_epoch_case_count","==",216],
    ["target_reactivation_evaluation_count","==",432],
    ["positive_target_reactivation_evaluation_count","==",432],
    ["final_epoch_positive_target_evaluation_count","==",36],
    ["minimum_target_preserved_incremental_correct_count",">=",1],
    ["zero_baseline_non_target_case_count",">",0],
    ["ratio_applicable_non_target_case_count",">",0],
    ["zero_baseline_non_target_case_count_plus_ratio_applicable","==",216],
    ["zero_baseline_preserved_negative_count","==",0],
    ["minimum_applicable_non_target_preserved_to_unprotected_fraction",">=",0.95],
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
    "supported": "Validity passes, all 432 target evaluations and all 36 final-packet target evaluations are positive, all zero-baseline cases remain nonnegative, and every ratio-applicable retention ratio is at least 0.95.",
    "mixed": "Validity passes and all final-packet target evaluations are positive, but an intermediate target, zero-baseline safety, or applicable retention threshold fails.",
    "negative": "Validity passes but at least one final-packet target evaluation is nonpositive.",
    "invalid": "Any sealed-parent, authority, source, horizon accounting, zero-baseline partition, preservation, capacity, determinism, or heldout-isolation criterion fails."
  },
  "validity_criteria": [
    "Exact sealed 034 parent and North Star identities match.",
    "Fresh READY_RESEARCH is bound to this exact preregistration and external manifest.",
    "The only scientific delta from 034 is evaluating all cumulative non-target packets 1..12 instead of only packets 4, 8, and 12.",
    "Protected rows remain training-selected and frozen for each schedule-target-pair case.",
    "Each non-target state uses only the cumulative training prefix through the current packet.",
    "Every one of 216 non-target cases is assigned exactly once to zero-baseline or ratio-applicable scoring, and the two counts sum to 216.",
    "Heldout increments affect scoring/classification only and never row selection, eviction, active selection, epoch choice, or stopping.",
    "Every packet retains exactly sixteen structures / seven active / nine retained.",
    "Duplicate complete executions are byte-identical and all numeric outputs are finite.",
    "No tokenizer, external model, persistent corpus, capacity/radius change, LINKDEADKB execution, production authority, or post-result tuning occurs."
  ],
  "no_post_result_tuning_rule": "Do not alter sources, split, schedules, target pairs, packet horizon, maturity cues, protected-row rule, deduplication, eviction ranking, selectors, zero-baseline semantics, 0.95 floor, capacity, metrics, thresholds, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-REACTIVATION-036",
    "intent": "carry full-horizon simultaneous preservation into an explicit dormant-to-active reactivation cycle without changing fixed capacity"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-HORIZON-ATTRIBUTION-036",
    "intent": "attribute the first packet/target/non-target condition that breaks target persistence or non-target safety before changing fixed capacity"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-multirow-horizon-035.ice",
    "research/applications/plane/exp-dgr-external-cumulative-multirow-horizon-035.py",
    ".github/workflows/external-cumulative-multirow-horizon-035.yml"
  ]
}
