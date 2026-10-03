{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CRITICAL-ROW-PRESERVATION-029",
  "program": "Yggdrasil cumulative-memory consolidation with low-signal protection",
  "question": "Can a cue-side critical-row preservation rule prevent C memory loss during A/B-only reconsolidation without increasing 16/7/9 capacity or materially degrading A/B?",
  "hypothesis": "Before C dormancy, identify the highest C-maturity-cue-positive row in the all-domain sixteen-row state using training-cue evidence only. Build the frozen A/B-only interference state exactly as in 027. If the protected row is absent, insert it one-for-one and evict the A/B interference row with the minimum summed contribution under full A and full B training cues, then lower utility, then lexicographically larger key. With this preserved sixteen-row state, C maturity-cue reactivation will be positive in all six schedules while A and B retain at least 95% of their corresponding unprotected interference-state heldout incremental benefits.",
  "exact_parent_sha": "83d16efec53c2e704f5715be7547ef2d0b0b2968",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-critical-row-preservation-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-INTERFERENCE-ATTRIBUTION-028",
    "github_run_id": "37112088525",
    "classification": "supported",
    "observation": {
      "c_failure_reproduction_count": 6,
      "full_cue_positive_case_count": 0,
      "c_absent_critical_row_case_count": 6,
      "single_row_restore_positive_case_count": 6,
      "minimum_single_row_restore_incremental_correct_count": 1,
      "critical_row_key": [116,114,117,99]
    },
    "diagnosis": "C loss is caused by displacement of one cue-relevant structure rather than insufficient reactivation cue."
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
    "sources": "byte-identical 028 external manifest",
    "external_split": "byte-identical first 60% cue / final 40% heldout",
    "schedules": "all six frozen permutations",
    "maturity_rule": "byte-identical twelve-packet maturity cue",
    "all_domain_state": "byte-identical 028 all-domain state reconstruction",
    "unprotected_interference_state": "byte-identical A/B-only state reconstruction",
    "active_selector": "byte-identical seven-active cue contribution selector",
    "capacity": "16 total / 7 active / 9 retained"
  },
  "preservation_rule": {
    "protected_row": "highest strictly positive C-maturity-cue contribution row in the pre-dormancy all-domain state; then higher utility; then lexicographically smaller key",
    "activation_condition": "only if the protected key is absent from the A/B-only interference state",
    "eviction_score": "sum of each interference row's contribution under full A training cue plus full B training cue",
    "eviction_tie_break": "lower summed contribution, then lower utility, then lexicographically larger key",
    "replacement": "one-for-one protected-row insertion; no other row or map changes",
    "heldout_selection": false
  },
  "evaluation": {
    "C": "select seven active rows with C maturity cue and score C heldout",
    "A": "select seven active rows with full A training cue and score A heldout",
    "B": "select seven active rows with full B training cue and score B heldout",
    "non_target_reference": "same-domain heldout incremental benefit on the unprotected A/B interference state"
  },
  "metrics_and_thresholds": [
    ["source_identity_mismatch_count","==",0],
    ["source_count","==",3],
    ["total_source_bytes","==",57272],
    ["base_training_identity_mismatch_count","==",0],
    ["schedule_count","==",6],
    ["preservation_case_count","==",6],
    ["protected_row_absent_case_count","==",6],
    ["protected_row_insert_case_count","==",6],
    ["c_positive_reactivation_case_count","==",6],
    ["minimum_c_preserved_incremental_correct_count",">=",1],
    ["minimum_non_target_preserved_to_unprotected_fraction",">=",0.95],
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
    "supported": "Validity passes, C is positive in all six preserved states, and A/B benefit retention is at least 0.95 in every case.",
    "mixed": "Validity passes and C is positive in all six cases, but at least one A/B benefit-retention ratio falls below 0.95.",
    "negative": "Validity passes but C remains nonpositive in at least one preserved state.",
    "invalid": "Any sealed-parent, authority, source, cue-only selection, one-for-one preservation, capacity, determinism, or heldout-isolation criterion fails."
  },
  "validity_criteria": [
    "Exact sealed 028 parent and North Star identities match.",
    "Fresh READY_RESEARCH is bound to this exact preregistration and manifest.",
    "Protected-row identity is computed independently in each schedule using C training maturity cue only, even if the resulting key is the same.",
    "Eviction uses only A/B training-cue contribution scores, utility, and key tie-breaks.",
    "No heldout result selects the protected row, eviction row, active rows, threshold, or stopping condition.",
    "Preservation is one-for-one and retains exactly sixteen structures / seven active / nine retained.",
    "Unprotected A/B reference and preserved A/B scoring use identical heldout evaluations and selectors.",
    "Duplicate executions are byte-identical and all numeric outputs are finite.",
    "No tokenizer, external model, persistent corpus, capacity/radius change, LINKDEADKB execution, production authority, or post-result tuning occurs."
  ],
  "no_post_result_tuning_rule": "Do not alter sources, split, schedules, protected-row definition, eviction score/tie-break, C/A/B selectors, 0.95 non-target floor, capacity, metrics, thresholds, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-MULTIEPOCH-CRITICAL-ROW-PRESERVATION-030",
    "intent": "stress the cue-side preservation rule across repeated dormant reconsolidation epochs"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-PRESERVATION-COST-ATTRIBUTION-030",
    "intent": "attribute preservation failure or non-target cost before changing capacity"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-critical-row-preservation-029.ice",
    "research/applications/plane/exp-dgr-external-critical-row-preservation-029.py",
    ".github/workflows/external-critical-row-preservation-029.yml"
  ]
}
