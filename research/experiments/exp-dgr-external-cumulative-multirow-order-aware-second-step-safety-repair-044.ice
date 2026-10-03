{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-ORDER-AWARE-SECOND-STEP-SAFETY-REPAIR-044",
  "program": "Yggdrasil fixed-capacity orientation-complete order-aware interference safety repair",
  "question": "Does extending the unchanged 041 guard only to the diagnosed order-0 second-target steps eliminate the 36 repeated-use safety failures without harming protected recovery?",
  "hypothesis": "Replay the exact 216 frozen 042 episodes and unchanged 041 guard. Preserve the existing 72 guarded order-1 episodes. Additionally apply the identical guard to only the 36 order-0 step-1 episodes in AB/C and BC/A diagnosed by supported 043, yielding exactly 108 guarded episodes. All 216 non-target safety checks will meet the frozen 0.95 floor and all 216 target and 216 partner recovery checks will remain positive under unchanged 16 total / 7 active / 9 retained capacity.",
  "exact_parent_sha": "ad9f969117f21e9a27441d93a6a336892c680c4c",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-cumulative-multirow-order-aware-second-step-safety-repair-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-ORDER-AWARE-REUSE-ATTRIBUTION-043",
    "github_run_id": "37133156490",
    "classification": "supported",
    "observation": {
      "episode_count": 216,
      "base_failure_count": 36,
      "failure_order0_count": 36,
      "failure_step1_count": 36,
      "failure_unguarded_count": 36,
      "failure_pair0_count": 18,
      "failure_pair2_count": 18,
      "failure_cycle0_count": 12,
      "failure_cycle1_count": 12,
      "failure_cycle2_count": 12,
      "orientation_match_fraction": 1.0
    },
    "diagnosis": "Repeated-use safety failure is an exact guard-applicability hole: order-0 second-target steps in AB/C and BC/A. There is no evidence of guard decay across cycles."
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
    "sources": "byte-identical 042 external manifest",
    "base_case_count": 36,
    "reuse_cycles": 3,
    "novel_steps_per_cycle": 2,
    "episode_count": 216,
    "novel_interference_construction": "byte-identical 042",
    "existing_guard_rule": "byte-identical 041 highest non-target training-cue contribution row reserve",
    "existing_guarded_episodes": 72,
    "new_guard_applicability": "only order-index 0, step-index 1, pair-index 0 or 2",
    "additional_guarded_episodes": 36,
    "total_guarded_episodes": 108,
    "capacity": "16 total / 7 active / 9 retained",
    "row_learning": false,
    "utility_updates": false,
    "protected_key_updates": false
  },
  "metrics_and_thresholds": [
    ["source_identity_mismatch_count","==",0],
    ["source_count","==",3],
    ["total_source_bytes","==",57272],
    ["base_case_count","==",36],
    ["reuse_cycle_count_per_case","==",3],
    ["novel_steps_per_cycle","==",2],
    ["novel_interference_episode_count","==",216],
    ["guard_applied_episode_count","==",108],
    ["additional_second_step_guard_episode_count","==",36],
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
    ["repair_accounting_error_count","==",0],
    ["heldout_selection_use_count","==",0],
    ["capacity_growth_event_count","==",0],
    ["row_mutation_event_count","==",0],
    ["tokenizer_use_count","==",0],
    ["external_model_call_count","==",0],
    ["invalid_evaluation_rows","==",0]
  ],
  "classification_rules": {
    "supported": "Validity passes; all 216 safety checks pass the 0.95 floor, all protected recovery remains positive, and exactly 36 additional diagnosed second-step episodes receive the unchanged guard.",
    "mixed": "Validity passes and protected recovery remains complete, but one or more non-target safety checks still fail.",
    "negative": "Validity passes but any target or partner recovery becomes nonpositive.",
    "invalid": "Any sealed-parent, authority, source, repair accounting, guard identity/applicability, frozen-state, capacity, determinism, or heldout-isolation criterion fails."
  },
  "validity_criteria": [
    "Exact qualified supported 043 parent and North Star identities match.",
    "Fresh READY_RESEARCH is bound to this exact preregistration and external manifest.",
    "The 216 episode sequence, rows, maps, cues, target orders, existing guard rule, and capacity reproduce 042 exactly.",
    "Existing order-1 guard applicability remains unchanged at 72 episodes.",
    "The identical guard is added only to the 36 supported-043 order-0 step-1 episodes in pair indices 0 and 2.",
    "Only active/retained partition membership may change; no row, utility, protected key, threshold, or capacity change.",
    "Heldout data affects scoring only and never guard selection, cue construction, cycle count, thresholds, or stopping.",
    "Duplicate complete executions are byte-identical.",
    "No tokenizer, external model, persistent corpus, LINKDEADKB execution, production authority, or post-result tuning occurs."
  ],
  "no_post_result_tuning_rule": "Do not alter sources, episode order, cycle count, novel cue, guard rule, existing 72 guarded episodes, diagnosed 36 additional episodes, seven-active selector, 0.95 floor, capacity, metrics, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-ORDER-AWARE-REUSE-HORIZON-045",
    "intent": "extend the orientation-complete fixed guard to a longer preregistered reuse horizon without changing capacity"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-SECOND-STEP-REPAIR-ATTRIBUTION-045",
    "intent": "attribute remaining failures or protected regressions before changing the guard"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-multirow-order-aware-second-step-safety-repair-044.ice",
    "research/applications/plane/exp-dgr-external-cumulative-multirow-order-aware-second-step-safety-repair-044.py",
    ".github/workflows/external-cumulative-multirow-order-aware-second-step-safety-repair-044.yml"
  ]
}
