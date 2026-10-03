{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-ORDER-AWARE-NONTARGET-SAFETY-REPAIR-041",
  "program": "Yggdrasil fixed-capacity order-aware non-target safety repair",
  "question": "Can one frozen training-only guard-slot partition rule restore non-target safety in the two diagnosed order-1 failure strata without harming protected capability recovery?",
  "hypothesis": "Replay the exact 36 frozen 040 cases. Only for target-order index 1 in pair AB/non-target C and pair BC/non-target A, reserve one of the seven active slots for the row with maximum non-target training-cue contribution, then fill the remaining active slots in the original novel-cue ranking order while keeping all sixteen rows unchanged. The rule will be applied in exactly 12 cases, eliminate all 12 non-target safety failures so the minimum ratio-applicable preserved-to-unprotected fraction is at least 0.95, and preserve all 72 target and 72 partner recoveries.",
  "exact_parent_sha": "1530dd23e2d0731c375807f61bb0b0c05246a41b",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-cumulative-multirow-order-aware-nontarget-safety-repair-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-NOVEL-INTERFERENCE-FACTORIAL-ATTRIBUTION-040",
    "github_run_id": "37130928927",
    "classification": "supported",
    "observation": {
      "non_target_safety_failure_count": 12,
      "failure_order0_count": 0,
      "failure_order1_count": 12,
      "failure_pair_AB_count": 6,
      "failure_pair_AC_count": 0,
      "failure_pair_BC_count": 6,
      "minimum_failures_per_schedule": 2,
      "maximum_failures_per_schedule": 2,
      "positive_post_novel_target_recovery_check_count": 72,
      "positive_post_novel_partner_recovery_check_count": 72
    },
    "diagnosis": "The failure is schedule-invariant and confined to order-1 for AB/C and BC/A. A bounded order-aware training-only partition guard can now be tested without changing rows or capacity."
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
    "sources": "byte-identical 040 external manifest",
    "external_split": "byte-identical first 60% cue / final 40% heldout",
    "schedules": "all six frozen permutations",
    "target_pairs": [["A","B"],["A","C"],["B","C"]],
    "target_orders": "both permutations of each target pair",
    "safety_case_count": 36,
    "novel_interference_construction": "byte-identical 040 32-byte training-prefix interleave",
    "preserved_state": "byte-identical effective 040 construction",
    "capacity": "16 total / 7 active / 9 retained",
    "row_learning": false,
    "utility_updates": false,
    "protected_key_updates": false
  },
  "repair_protocol": {
    "applicability": "only target-order index 1 for pair AB/non-target C and pair BC/non-target A",
    "guard_cue": "the frozen non-target packet-12 training cue only",
    "guard_row": "highest non-target-cue contribution row under the frozen sixteen-row map; deterministic utility/key tie-break",
    "novel_ranking": "byte-identical original novel-cue contribution ranking",
    "active_set": "guard row first, then novel-ranking rows not already selected until exactly seven active rows",
    "unaffected_cases": "byte-identical original 040 active selector",
    "heldout_selection": false,
    "capacity_change": false,
    "row_change": false
  },
  "metrics_and_thresholds": [
    ["safety_case_count","==",36],
    ["guard_applied_case_count","==",12],
    ["repaired_non_target_safety_failure_count","==",0],
    ["minimum_applicable_non_target_preserved_to_unprotected_fraction",">=",0.95],
    ["positive_post_novel_target_recovery_check_count","==",72],
    ["positive_post_novel_partner_recovery_check_count","==",72],
    ["preserved_state_structure_count_min","==",16],
    ["preserved_state_structure_count_max","==",16],
    ["active_structure_count_min","==",7],
    ["active_structure_count_max","==",7],
    ["retained_structure_count_min","==",9],
    ["retained_structure_count_max","==",9],
    ["repair_accounting_error_count","==",0],
    ["heldout_selection_use_count","==",0],
    ["capacity_growth_event_count","==",0],
    ["row_mutation_event_count","==",0],
    ["tokenizer_use_count","==",0],
    ["external_model_call_count","==",0],
    ["invalid_evaluation_rows","==",0]
  ],
  "classification_rules": {
    "supported": "Validity passes, the guard is applied to exactly 12 preregistered cases, all non-target safety failures are eliminated at the frozen 0.95 floor, and protected recovery remains 72/72 plus 72/72.",
    "mixed": "Validity passes and protected recovery remains intact, but at least one non-target safety failure remains.",
    "negative": "Validity passes but the repair causes any protected target or partner recovery to become nonpositive.",
    "invalid": "Any sealed-parent, authority, source, applicability, guard construction, accounting, frozen-state, capacity, determinism, or heldout-isolation criterion fails."
  },
  "validity_criteria": [
    "Exact qualified supported 040 parent and North Star identities match.",
    "Fresh READY_RESEARCH is bound to this exact preregistration and external manifest.",
    "The original 36 cases reproduce before the guard is evaluated.",
    "The guard uses training-prefix contribution only and is applied only to the frozen 12 diagnosed strata.",
    "Exactly sixteen rows remain present, exactly seven are active, and no row, utility, protected key, threshold, or capacity changes.",
    "Heldout data is used only for scoring after the active set is frozen.",
    "Duplicate complete executions are byte-identical.",
    "No tokenizer, external model, persistent corpus, LINKDEADKB execution, production authority, or post-result tuning occurs."
  ],
  "no_post_result_tuning_rule": "Do not alter sources, split, cases, diagnosed applicability, guard cue, guard-row rule, novel ranking, seven-active construction, 0.95 floor, capacity, metrics, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-ORDER-AWARE-NOVEL-INTERFERENCE-REUSE-042",
    "intent": "stress the fixed guard across repeated novel-interference reuse without changing capacity"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-GUARD-SLOT-ATTRIBUTION-042",
    "intent": "attribute residual guard failures before changing the rule or capacity"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-multirow-order-aware-nontarget-safety-repair-041.ice",
    "research/applications/plane/exp-dgr-external-cumulative-multirow-order-aware-nontarget-safety-repair-041.py",
    ".github/workflows/external-cumulative-multirow-order-aware-nontarget-safety-repair-041.yml"
  ]
}
