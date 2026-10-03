{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-NOVEL-INTERFERENCE-FACTORIAL-ATTRIBUTION-040",
  "program": "Yggdrasil fixed-capacity novel-interference factorial attribution",
  "question": "Are the 039 non-target safety failures explained by target-order and pair/domain interaction while remaining invariant to schedule permutation?",
  "hypothesis": "Replay the exact 36 frozen 039 cases without changing rows, cues, selectors, safety semantics, or capacity. All 12 safety failures will remain confined to target-order index 1; target-order index 0 will have zero failures; pair AB/non-target C and pair BC/non-target A will each fail in all six schedules; pair AC/non-target B will remain failure-free; and every schedule will contain exactly two failures. Protected target and partner recoveries will remain 72/72.",
  "exact_parent_sha": "3290a16be49086d630beedacb48fe163160348ef",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-cumulative-multirow-novel-interference-factorial-attribution-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-NOVEL-INTERFERENCE-ATTRIBUTION-039",
    "github_run_id": "37130365001",
    "classification": "mixed",
    "observation": {
      "safety_case_count": 36,
      "non_target_safety_failure_count": 12,
      "failure_domain_A_count": 6,
      "failure_domain_B_count": 0,
      "failure_domain_C_count": 6,
      "dominant_failure_domain_fraction": 0.5,
      "positive_post_novel_target_recovery_check_count": 72,
      "positive_post_novel_partner_recovery_check_count": 72
    },
    "diagnosis": "Failures are split across non-target A and C rather than localized to one domain. The 039 case diagnostics indicate a repeated target-order interaction that must be confirmed factorally before any repair."
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
    "sources": "byte-identical 039 external manifest",
    "external_split": "byte-identical first 60% cue / final 40% heldout",
    "schedules": "all six frozen permutations",
    "target_pairs": [["A","B"],["A","C"],["B","C"]],
    "target_orders": "both permutations of each target pair",
    "safety_case_count": 36,
    "novel_interference_construction": "byte-identical 039 32-byte training-prefix interleave",
    "preserved_state": "byte-identical effective 039 construction",
    "active_selector": "byte-identical seven-active selector",
    "capacity": "16 total / 7 active / 9 retained",
    "row_learning": false,
    "utility_updates": false,
    "protected_key_updates": false
  },
  "factorial_protocol": {
    "factors": ["schedule_index","target_pair_index","target_order_index","non_target_domain"],
    "primary_failure_definition": "byte-identical 039 non-target safety failure definition",
    "selection_data": "none; post hoc attribution over the exact frozen 36 cases",
    "adaptive_changes": false
  },
  "metrics_and_thresholds": [
    ["safety_case_count","==",36],
    ["non_target_safety_failure_count","==",12],
    ["failure_order0_count","==",0],
    ["failure_order1_count","==",12],
    ["failure_pair_AB_count","==",6],
    ["failure_pair_AC_count","==",0],
    ["failure_pair_BC_count","==",6],
    ["minimum_failures_per_schedule","==",2],
    ["maximum_failures_per_schedule","==",2],
    ["positive_post_novel_target_recovery_check_count","==",72],
    ["positive_post_novel_partner_recovery_check_count","==",72],
    ["factorial_accounting_error_count","==",0],
    ["heldout_selection_use_count","==",0],
    ["capacity_growth_event_count","==",0],
    ["row_mutation_event_count","==",0],
    ["tokenizer_use_count","==",0],
    ["external_model_call_count","==",0],
    ["invalid_evaluation_rows","==",0]
  ],
  "classification_rules": {
    "supported": "Validity passes and every preregistered factorial count matches, confirming schedule-invariant order/pair interaction.",
    "mixed": "Validity passes and order-1 remains dominant but one or more pair/schedule invariance counts differ.",
    "negative": "Validity passes but failures are not primarily target-order-1 conditioned.",
    "invalid": "Any sealed-parent, authority, source, accounting, frozen-state, capacity, determinism, or heldout-isolation criterion fails."
  },
  "validity_criteria": [
    "Exact qualified mixed 039 parent and North Star identities match.",
    "Fresh READY_RESEARCH is bound to this exact preregistration and external manifest.",
    "The exact 36 039 cases and failure definition are reproduced before factorial counts are accepted.",
    "No repair rule, threshold, learned state, row, utility, selector, or capacity changes.",
    "Duplicate complete executions are byte-identical and every case is assigned exactly once.",
    "No tokenizer, external model, persistent corpus, LINKDEADKB execution, production authority, or post-result tuning occurs."
  ],
  "no_post_result_tuning_rule": "Do not alter sources, split, schedules, target pairs, orders, cue construction, preserved state, safety definition, capacity, factorial thresholds, metrics, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-ORDER-AWARE-NONTARGET-SAFETY-REPAIR-041",
    "intent": "test one bounded preregistered order-aware partition rule without changing capacity or learned rows"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-PAIRWISE-INTERFERENCE-ATTRIBUTION-041",
    "intent": "decompose the remaining pair/order interaction before any repair"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-multirow-novel-interference-factorial-attribution-040.ice",
    "research/applications/plane/exp-dgr-external-cumulative-multirow-novel-interference-factorial-attribution-040.py",
    ".github/workflows/external-cumulative-multirow-novel-interference-factorial-attribution-040.yml"
  ]
}
