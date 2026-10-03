{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-NOVEL-INTERFERENCE-ATTRIBUTION-039",
  "program": "Yggdrasil fixed-capacity novel-interference non-target safety attribution",
  "question": "Which frozen schedule, target order, and non-target domain conditions account for the non-target safety collapse observed in valid mixed result 038?",
  "hypothesis": "Replay the exact 36 valid 038 novel-interference cases with identical preserved rows, cues, selectors, capacity, and scoring. The target and partner recoveries will remain positive, while the non-target safety failures will be materially localized: at least 0.75 of all failing cases will share one non-target domain. This would identify a bounded domain-conditioned interference failure without changing capacity, learned rows, utilities, or thresholds.",
  "exact_parent_sha": "543c157709eaff2c0ffbb8c9120ee7c7cb0b5b05",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-cumulative-multirow-novel-interference-attribution-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-NOVEL-INTERFERENCE-038",
    "github_run_id": "37128728125",
    "classification": "mixed",
    "observation": {
      "reuse_case_count": 36,
      "novel_interference_episode_count": 36,
      "positive_post_novel_target_recovery_check_count": 72,
      "positive_post_novel_partner_recovery_check_count": 72,
      "minimum_post_novel_target_incremental_correct_count": 1,
      "minimum_post_novel_partner_incremental_correct_count": 1,
      "zero_baseline_preserved_negative_count": 0,
      "minimum_applicable_non_target_preserved_to_unprotected_fraction": 0.0,
      "invalid_evaluation_rows": 0
    },
    "diagnosis": "Novel interference did not break either protected capability, but non-target preservation violated the frozen 0.95 floor. The next bounded step is attribution of the failing condition, not capacity growth."
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
    "sources": "byte-identical 038 external manifest",
    "external_split": "byte-identical first 60% cue / final 40% heldout",
    "schedules": "all six frozen permutations",
    "target_pairs": [["A", "B"], ["A", "C"], ["B", "C"]],
    "target_orders": "both permutations of each target pair",
    "reuse_case_count": 36,
    "novel_interference_episode_count": 36,
    "novel_interference_construction": "byte-identical 038 32-byte training-prefix interleave",
    "packet12_preserved_state": "byte-identical effective 038 construction including sealed 037 protected-key deduplication semantics",
    "active_selector": "byte-identical seven-active selector",
    "capacity": "16 total / 7 active / 9 retained",
    "row_learning": false,
    "utility_updates": false,
    "protected_key_updates": false
  },
  "attribution_protocol": {
    "safety_failure": "ratio-applicable case with preserved/non-target-unprotected fraction below 0.95, or zero-baseline case with preserved increment below zero",
    "case_order": "schedule index, target-pair index, target-order index",
    "categories": [
      "non-target domain",
      "schedule index",
      "target pair",
      "target order",
      "unprotected non-target increment",
      "preserved non-target increment",
      "preserved-to-unprotected fraction"
    ],
    "selection_data": "none; attribution is post hoc over the exact frozen 36 cases",
    "adaptive_changes": false
  },
  "metrics_and_thresholds": [
    ["source_identity_mismatch_count", "==", 0],
    ["source_count", "==", 3],
    ["total_source_bytes", "==", 57272],
    ["base_training_identity_mismatch_count", "==", 0],
    ["schedule_count", "==", 6],
    ["target_pair_count", "==", 3],
    ["target_order_count_per_pair", "==", 2],
    ["safety_case_count", "==", 36],
    ["post_novel_target_recovery_check_count", "==", 72],
    ["positive_post_novel_target_recovery_check_count", "==", 72],
    ["post_novel_partner_recovery_check_count", "==", 72],
    ["positive_post_novel_partner_recovery_check_count", "==", 72],
    ["non_target_safety_failure_count", ">", 0],
    ["failure_attribution_accounting_error_count", "==", 0],
    ["dominant_failure_domain_fraction", ">=", 0.75],
    ["preserved_state_structure_count_min", "==", 16],
    ["preserved_state_structure_count_max", "==", 16],
    ["active_structure_count_min", "==", 7],
    ["active_structure_count_max", "==", 7],
    ["retained_structure_count_min", "==", 9],
    ["retained_structure_count_max", "==", 9],
    ["target_interference_leakage_count", "==", 0],
    ["heldout_selection_use_count", "==", 0],
    ["capacity_growth_event_count", "==", 0],
    ["row_mutation_event_count", "==", 0],
    ["tokenizer_use_count", "==", 0],
    ["external_model_call_count", "==", 0],
    ["invalid_evaluation_rows", "==", 0]
  ],
  "classification_rules": {
    "supported": "Validity passes, protected recoveries remain 72/72 and at least 0.75 of non-target safety failures share one non-target domain.",
    "mixed": "Validity passes, protected recoveries remain intact, and the dominant failure domain fraction is at least 0.50 but below 0.75.",
    "negative": "Validity passes but failures are diffuse across domains with dominant failure domain fraction below 0.50, or a protected recovery becomes nonpositive.",
    "invalid": "Any sealed-parent, authority, source, case-accounting, frozen-row identity, capacity, determinism, or heldout-isolation criterion fails."
  },
  "validity_criteria": [
    "Exact qualified mixed 038 parent and North Star identities match.",
    "Fresh READY_RESEARCH is bound to this exact preregistration and external manifest.",
    "The effective 038 shared-row/protected-key deduplication semantics are reproduced exactly before attribution.",
    "The same 36 cases, 32-byte novel cue construction, rows, utilities, protected keys, selectors, safety floor, and capacity are unchanged.",
    "Attribution changes no learned state and uses heldout data only for scoring already-frozen cases.",
    "Duplicate complete executions are byte-identical and every case is attributed exactly once.",
    "No tokenizer, external model, persistent corpus, capacity/radius change, LINKDEADKB execution, production authority, or post-result tuning occurs."
  ],
  "no_post_result_tuning_rule": "Do not alter sources, split, schedules, target pairs, target orders, novel cue, preserved-state construction, active selector, 0.95 safety floor, 0.75/0.50 localization thresholds, capacity, metrics, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-DOMAIN-CONDITIONAL-INTERFERENCE-REPAIR-040",
    "intent": "test one bounded preregistered domain-conditioned partition rule without changing capacity or learned rows"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-NOVEL-INTERFERENCE-FACTORIAL-ATTRIBUTION-040",
    "intent": "factor schedule, target order, and non-target domain interactions before any repair or capacity change"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-multirow-novel-interference-attribution-039.ice",
    "research/applications/plane/exp-dgr-external-cumulative-multirow-novel-interference-attribution-039.py",
    ".github/workflows/external-cumulative-multirow-novel-interference-attribution-039.yml"
  ]
}
