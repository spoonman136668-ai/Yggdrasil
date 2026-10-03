{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-MULTIEPOCH-CRITICAL-ROW-PRESERVATION-030",
  "program": "Yggdrasil cumulative-memory multiepoch dormant consolidation",
  "question": "Does the supported cue-side critical-row preservation rule keep low-signal C reactivatable while A/B consolidation strengthens across multiple dormant epochs?",
  "hypothesis": "Freeze the C-critical row from the pre-dormancy all-domain state using the same maturity-cue rule as 029. For each of six schedules, perform four A/B-only consolidation epochs using cumulative A/B cue prefixes at packet indices 3, 6, 9, and 12. At each epoch, construct the A/B state from that epoch's cumulative cues, apply the frozen one-for-one preservation rule if the C-critical row is absent, then score C reactivation with the frozen C maturity cue and A/B with their current epoch cues. Across all 24 schedule-epoch cases, C will remain positive with at least +1 incremental correct, and A/B will retain at least 95% of their corresponding unprotected epoch-state incremental benefit.",
  "exact_parent_sha": "38cf305a935144d59d71577a3a7fd852518df239",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-multiepoch-preservation-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CRITICAL-ROW-PRESERVATION-029",
    "github_run_id": "37112652996",
    "classification": "supported",
    "observation": {
      "preservation_case_count": 6,
      "protected_row_insert_case_count": 6,
      "c_positive_reactivation_case_count": 6,
      "minimum_c_preserved_incremental_correct_count": 1,
      "minimum_non_target_preserved_to_unprotected_fraction": 1.0,
      "protected_row_key": [116,114,117,99]
    },
    "diagnosis": "A single cue-selected protected row closes the one-epoch C interference hole at zero measured A/B cost."
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
    "sources": "byte-identical 029 external manifest",
    "external_split": "byte-identical first 60% cue / final 40% heldout",
    "schedules": "all six frozen permutations",
    "packet_count": 12,
    "maturity_rule": "byte-identical one-positive-row maturity cue",
    "protected_row_rule": "byte-identical 029 highest C-maturity-cue-positive row rule",
    "eviction_rule": "byte-identical 029 minimum summed current A/B cue contribution, then lower utility, then lexicographically larger key",
    "active_selector": "byte-identical seven-active cue contribution selector",
    "capacity": "16 total / 7 active / 9 retained"
  },
  "multiepoch_protocol": {
    "epoch_packet_indices": [3,6,9,12],
    "epoch_count": 4,
    "case_count": 24,
    "A_B_epoch_cues": "cumulative prefixes ending at the epoch packet index; no C cue is included in A/B candidate statistics or consolidation",
    "protected_row_identity": "computed once per schedule from the pre-dormancy all-domain full-cue state and C maturity cue, then held fixed across all four epochs",
    "preservation": "at each epoch, if the protected key is absent from the A/B state, insert it one-for-one using the frozen eviction rule",
    "C_reactivation": "frozen C maturity cue only; no C structural update",
    "A_B_reference": "unprotected A/B epoch state scored with the same A/B epoch cue selector and heldout evaluation"
  },
  "metrics_and_thresholds": [
    ["source_identity_mismatch_count","==",0],
    ["source_count","==",3],
    ["total_source_bytes","==",57272],
    ["base_training_identity_mismatch_count","==",0],
    ["schedule_count","==",6],
    ["epoch_count","==",4],
    ["multiepoch_case_count","==",24],
    ["c_positive_reactivation_case_count","==",24],
    ["minimum_c_preserved_incremental_correct_count",">=",1],
    ["minimum_non_target_preserved_to_unprotected_fraction",">=",0.95],
    ["protected_row_missing_after_preservation_count","==",0],
    ["preservation_insert_count",">",0],
    ["preserved_state_structure_count_min","==",16],
    ["preserved_state_structure_count_max","==",16],
    ["active_structure_count_min","==",7],
    ["active_structure_count_max","==",7],
    ["retained_structure_count_min","==",9],
    ["retained_structure_count_max","==",9],
    ["heldout_selection_use_count","==",0],
    ["capacity_growth_event_count","==",0],
    ["tokenizer_use_count","==",0],
    ["external_model_call_count","==",0],
    ["invalid_evaluation_rows","==",0]
  ],
  "classification_rules": {
    "supported": "Validity passes, C remains positive in all 24 schedule-epoch cases, and every A/B preserved/unprotected benefit ratio is at least 0.95.",
    "mixed": "Validity passes and C remains positive in all 24 cases, but at least one A/B benefit-retention ratio falls below 0.95.",
    "negative": "Validity passes but C becomes nonpositive in at least one preserved schedule-epoch case.",
    "invalid": "Any sealed-parent, authority, source, epoch-prefix, protected-row identity, cue-only preservation, capacity, determinism, or heldout-isolation criterion fails."
  },
  "validity_criteria": [
    "Exact sealed 029 parent and North Star identities match.",
    "Fresh READY_RESEARCH is bound to this exact preregistration and manifest.",
    "The protected C row is selected before dormancy from C training maturity cue only and remains fixed within a schedule.",
    "C is excluded from every A/B epoch candidate-statistics and minimax consolidation input.",
    "Each epoch uses only the preregistered cumulative A/B packet prefix.",
    "Eviction choices use only current A/B training-cue contributions, utility, and key tie-breaks.",
    "Preservation remains one-for-one at exactly 16 total / 7 active / 9 retained.",
    "Heldout bytes are scoring-only and never affect epoch construction, preservation, eviction, active selection, thresholds, or stopping.",
    "Duplicate executions are byte-identical and all numeric outputs are finite.",
    "No tokenizer, external model, persistent corpus, capacity/radius change, LINKDEADKB execution, production authority, or post-result tuning occurs."
  ],
  "no_post_result_tuning_rule": "Do not alter epoch indices, sources, split, schedules, protected-row rule, eviction rule, selectors, 0.95 non-target floor, capacity, metrics, thresholds, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-PRESERVATION-GENERALIZATION-031",
    "intent": "generalize cue-side critical-row preservation beyond the current three-source matrix and single low-signal domain"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-MULTIEPOCH-PRESERVATION-ATTRIBUTION-031",
    "intent": "attribute the first failing epoch or non-target cost before changing capacity"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-multiepoch-critical-row-preservation-030.ice",
    "research/applications/plane/exp-dgr-external-multiepoch-critical-row-preservation-030.py",
    ".github/workflows/external-multiepoch-critical-row-preservation-030.yml"
  ]
}
