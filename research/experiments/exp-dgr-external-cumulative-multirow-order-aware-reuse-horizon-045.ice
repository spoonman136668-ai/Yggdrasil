{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-ORDER-AWARE-REUSE-HORIZON-045",
  "program": "Yggdrasil fixed-capacity orientation-complete guard reuse horizon",
  "question": "Does the supported orientation-complete 044 guard remain safe across a doubled six-cycle reuse horizon without any learned-state or capacity change?",
  "hypothesis": "Replay the exact 36 frozen 044 cases with the identical orientation-complete guard, rows, cues, selectors, and 0.95 safety floor, but double the preregistered reuse horizon from three to six cycles. This yields 432 frozen interference episodes. Exactly 216 episodes will receive the unchanged guard: 144 existing order-1 episodes and 72 diagnosed order-0 second-step episodes. Every non-target safety check will remain at or above 0.95 and all 432 target and 432 partner recovery checks will remain positive under fixed 16 total / 7 active / 9 retained capacity.",
  "exact_parent_sha": "9203fccf6ff504a0c59fc008be67f178259ef8d2",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-cumulative-multirow-order-aware-reuse-horizon-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-ORDER-AWARE-SECOND-STEP-SAFETY-REPAIR-044",
    "github_run_id": "37133787802",
    "classification": "supported",
    "observation": {
      "novel_interference_episode_count": 216,
      "guard_applied_episode_count": 108,
      "additional_second_step_guard_episode_count": 36,
      "non_target_safety_failure_count": 0,
      "minimum_applicable_non_target_preserved_to_unprotected_fraction": 0.9862600536193029,
      "positive_post_episode_target_recovery_check_count": 216,
      "positive_post_episode_partner_recovery_check_count": 216
    },
    "diagnosis": "Orientation-complete guard applicability closes the repeated-use safety hole at three cycles. The next bounded test is a doubled fixed horizon before introducing any new stateful mechanism."
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
    "sources": "byte-identical 044 external manifest",
    "base_case_count": 36,
    "reuse_cycles": 6,
    "novel_steps_per_cycle": 2,
    "episode_count": 432,
    "novel_interference_construction": "byte-identical 044",
    "guard_rule": "byte-identical 044 orientation-complete guard",
    "existing_order1_guarded_episodes": 144,
    "order0_second_step_guarded_episodes": 72,
    "total_guarded_episodes": 216,
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
    ["reuse_cycle_count_per_case","==",6],
    ["novel_steps_per_cycle","==",2],
    ["novel_interference_episode_count","==",432],
    ["guard_applied_episode_count","==",216],
    ["additional_second_step_guard_episode_count","==",72],
    ["non_target_safety_failure_count","==",0],
    ["minimum_applicable_non_target_preserved_to_unprotected_fraction",">=",0.95],
    ["post_episode_target_recovery_check_count","==",432],
    ["positive_post_episode_target_recovery_check_count","==",432],
    ["post_episode_partner_recovery_check_count","==",432],
    ["positive_post_episode_partner_recovery_check_count","==",432],
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
    "supported": "Validity passes; all 432 safety checks meet the 0.95 floor and all 432 target and 432 partner recovery checks are positive.",
    "mixed": "Validity passes and protected recovery remains complete, but one or more non-target safety checks fail.",
    "negative": "Validity passes but any target or partner recovery becomes nonpositive.",
    "invalid": "Any sealed-parent, authority, source, horizon accounting, guard identity/applicability, frozen-state, capacity, determinism, or heldout-isolation criterion fails."
  },
  "validity_criteria": [
    "Exact qualified supported 044 parent and North Star identities match.",
    "Fresh READY_RESEARCH is bound to this exact preregistration and external manifest.",
    "Rows, maps, maturity cues, target orders, novel cue construction, guard rule, guard applicability, and capacity reproduce 044 exactly.",
    "Only the cycle count changes from three to six; all six cycles are frozen before heldout scoring.",
    "Exactly 216 of 432 episodes receive the unchanged guard, including exactly 72 order-0 second-step episodes.",
    "Only active/retained partition membership may change; no row, utility, protected key, threshold, or capacity change.",
    "Heldout data affects scoring only and never guard selection, cycle count, cue construction, thresholds, or stopping.",
    "Duplicate complete executions are byte-identical.",
    "No tokenizer, external model, persistent corpus, LINKDEADKB execution, production authority, or post-result tuning occurs."
  ],
  "no_post_result_tuning_rule": "Do not alter sources, six-cycle horizon, episode order, novel cue, guard rule/applicability, seven-active selector, 0.95 floor, capacity, metrics, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-ORDER-AWARE-STATE-CARRY-046",
    "intent": "introduce one preregistered inter-cycle state-carry stress while keeping rows and capacity frozen, moving from repeated replay toward cumulative retained-state dynamics"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-REUSE-HORIZON-ATTRIBUTION-046",
    "intent": "attribute the first failing cycle and orientation before changing the guard"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-multirow-order-aware-reuse-horizon-045.ice",
    "research/applications/plane/exp-dgr-external-cumulative-multirow-order-aware-reuse-horizon-045.py",
    ".github/workflows/external-cumulative-multirow-order-aware-reuse-horizon-045.yml"
  ]
}
