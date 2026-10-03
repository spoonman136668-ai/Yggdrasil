{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-ORDER-AWARE-NOVEL-INTERFERENCE-REUSE-042",
  "program": "Yggdrasil fixed-capacity order-aware novel-interference reuse stress",
  "question": "Does the supported 041 order-aware guard remain safe when both ordered target-derived novel interference cues are reused across three complete cycles?",
  "hypothesis": "Replay the exact 36 frozen 041 cases with the same sixteen rows, seven-active selector, diagnosed guard applicability, and 0.95 non-target safety floor. For each case, run three cycles; within every cycle apply one novel-interference episode derived from the first target and one from the second target, preserving the case target order. This yields 216 frozen interference episodes. In the 12 diagnosed order-1 AB/C and BC/A cases, apply the unchanged 041 guard to all six episodes per case (72 guarded episodes total). Every one of the 216 episodes will preserve non-target safety at or above 0.95, and every post-episode target and partner recovery check will remain positive.",
  "exact_parent_sha": "581391ef44477023d96cbd1544e94378b3b4f319",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-cumulative-multirow-order-aware-novel-interference-reuse-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-ORDER-AWARE-NONTARGET-SAFETY-REPAIR-041",
    "github_run_id": "37131695453",
    "classification": "supported",
    "observation": {
      "baseline_non_target_safety_failure_count": 12,
      "guard_applied_case_count": 12,
      "guard_noop_case_count": 0,
      "repaired_non_target_safety_failure_count": 0,
      "minimum_applicable_non_target_preserved_to_unprotected_fraction": 0.9862600536193029,
      "positive_post_novel_target_recovery_check_count": 72,
      "positive_post_novel_partner_recovery_check_count": 72
    },
    "diagnosis": "The single-episode order-aware guard fully repaired the 12 diagnosed failures without protected-capability loss. The next bounded stress is repeated use across both ordered target-derived novel cues."
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
    "sources": "byte-identical 041 external manifest",
    "external_split": "byte-identical first 60% cue / final 40% heldout",
    "schedules": "all six frozen permutations",
    "target_pairs": [["A","B"],["A","C"],["B","C"]],
    "target_orders": "both permutations of each target pair",
    "base_case_count": 36,
    "reuse_cycles": 3,
    "novel_steps_per_cycle": 2,
    "novel_interference_episode_count": 216,
    "novel_interference_construction": "byte-identical 32-byte interleave of non-target packet-12 training cue and current target frozen maturity cue",
    "guard_applicability": "byte-identical 041 diagnosed order-1 AB/C and BC/A strata",
    "guard_rule": "byte-identical 041 highest non-target training-cue contribution row reserved before novel-cue ranking",
    "capacity": "16 total / 7 active / 9 retained",
    "row_learning": false,
    "utility_updates": false,
    "protected_key_updates": false
  },
  "reuse_protocol": {
    "cycles_per_case": 3,
    "within_cycle_target_sequence": "first target then second target under the frozen case order",
    "state_transition": "recompute active/retained partition only; rows, map, utilities, and protected keys remain frozen",
    "guarded_episode_count": 72,
    "unguarded_episode_count": 144,
    "heldout_selection": false
  },
  "metrics_and_thresholds": [
    ["base_case_count","==",36],
    ["reuse_cycle_count_per_case","==",3],
    ["novel_steps_per_cycle","==",2],
    ["novel_interference_episode_count","==",216],
    ["guard_applied_episode_count","==",72],
    ["non_target_safety_failure_count","==",0],
    ["minimum_applicable_non_target_preserved_to_unprotected_fraction",">=",0.95],
    ["post_episode_target_recovery_check_count","==",216],
    ["positive_post_episode_target_recovery_check_count","==",216],
    ["post_episode_partner_recovery_check_count","==",216],
    ["positive_post_episode_partner_recovery_check_count","==",216],
    ["preserved_state_structure_count_min","==",16],
    ["preserved_state_structure_count_max","==",16],
    ["active_structure_count_min","==",7],
    ["active_structure_count_max","==",7],
    ["retained_structure_count_min","==",9],
    ["retained_structure_count_max","==",9],
    ["reuse_accounting_error_count","==",0],
    ["heldout_selection_use_count","==",0],
    ["capacity_growth_event_count","==",0],
    ["row_mutation_event_count","==",0],
    ["tokenizer_use_count","==",0],
    ["external_model_call_count","==",0],
    ["invalid_evaluation_rows","==",0]
  ],
  "classification_rules": {
    "supported": "Validity passes; all 216 non-target safety episodes pass the frozen 0.95 floor; all 216 target and 216 partner recovery checks are positive.",
    "mixed": "Validity passes and protected recovery remains complete, but one or more non-target safety episodes fail.",
    "negative": "Validity passes but any target or partner recovery becomes nonpositive.",
    "invalid": "Any sealed-parent, authority, source, reuse accounting, guard identity, frozen-state, capacity, determinism, or heldout-isolation criterion fails."
  },
  "validity_criteria": [
    "Exact qualified supported 041 parent and North Star identities match.",
    "Fresh READY_RESEARCH is bound to this exact preregistration and external manifest.",
    "The 36 base cases, preserved rows/maps, maturity cues, target orders, guard rule, and capacity reproduce 041 exactly.",
    "All three cycles and both target-derived novel steps are frozen before heldout scoring.",
    "The guard is applied to exactly 72 episodes and nowhere outside the preregistered 12-case strata.",
    "Only active/retained partition membership may change; no row, utility, protected key, threshold, or capacity change.",
    "Heldout data affects scoring only and never cue construction, guard selection, cycle count, thresholds, or stopping.",
    "Duplicate complete executions are byte-identical.",
    "No tokenizer, external model, persistent corpus, LINKDEADKB execution, production authority, or post-result tuning occurs."
  ],
  "no_post_result_tuning_rule": "Do not alter sources, split, base cases, cycle count, target sequence, novel cue construction, guard applicability/rule, seven-active construction, 0.95 floor, capacity, metrics, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-ORDER-AWARE-NOVEL-INTERFERENCE-HORIZON-043",
    "intent": "extend the fixed guard to a longer preregistered reuse horizon without changing capacity"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-ORDER-AWARE-REUSE-ATTRIBUTION-043",
    "intent": "attribute the first cycle/target step that breaks safety or recovery before changing the guard"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-multirow-order-aware-novel-interference-reuse-042.ice",
    "research/applications/plane/exp-dgr-external-cumulative-multirow-order-aware-novel-interference-reuse-042.py",
    ".github/workflows/external-cumulative-multirow-order-aware-novel-interference-reuse-042.yml"
  ]
}
