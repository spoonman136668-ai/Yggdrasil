{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-ORDER-AWARE-STATE-CARRY-046",
  "program": "Yggdrasil fixed-capacity orientation-complete guard with bounded inter-cycle active-state carry",
  "question": "Does the supported six-cycle 045 regime remain safe when one deterministic active-state key is carried from each completed cycle into the next cycle's first novel-interference step?",
  "hypothesis": "Replay the exact 36 frozen 045 cases, six cycles, two steps per cycle, orientation-complete guard, rows, cues, selectors, and 0.95 safety floor. Beginning with cycle 1, carry exactly one key from the immediately preceding cycle's final active partition: the active key with greatest contribution to that preceding final novel cue, tie-broken by utility then key. On the next cycle's first step, reserve that carried key in the seven-active set and fill the remaining six slots using the unchanged 045 guarded or unguarded ranking as applicable. The second step remains byte-identical 045 selection and produces the next carry key. Exactly 180 first-step episodes will receive carry state. All 432 non-target safety checks will remain at or above 0.95 and all 432 target and 432 partner recovery checks will remain positive under fixed 16 total / 7 active / 9 retained capacity.",
  "exact_parent_sha": "41c07ce42cc4e337c12b1e4623a367a59bd3a616",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-cumulative-multirow-order-aware-state-carry-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-ORDER-AWARE-REUSE-HORIZON-045",
    "github_run_id": "37134293706",
    "classification": "supported",
    "observation": {
      "novel_interference_episode_count": 432,
      "guard_applied_episode_count": 216,
      "additional_second_step_guard_episode_count": 72,
      "non_target_safety_failure_count": 0,
      "minimum_applicable_non_target_preserved_to_unprotected_fraction": 0.9862600536193029,
      "positive_post_episode_target_recovery_check_count": 432,
      "positive_post_episode_partner_recovery_check_count": 432
    },
    "diagnosis": "Six-cycle replay is stable but each episode still selects from the same frozen state independently. The next bounded North-Star step is one-key inter-cycle state carry without row learning or capacity growth."
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
    "sources": "byte-identical 045 external manifest",
    "base_case_count": 36,
    "reuse_cycles": 6,
    "novel_steps_per_cycle": 2,
    "episode_count": 432,
    "novel_interference_construction": "byte-identical 045",
    "guard_rule": "byte-identical 045 orientation-complete guard",
    "capacity": "16 total / 7 active / 9 retained",
    "row_learning": false,
    "utility_updates": false,
    "protected_key_updates": false
  },
  "state_carry_protocol": {
    "carry_start_cycle": 1,
    "carry_application": "first step only of cycles 1 through 5",
    "carry_application_count": 180,
    "carry_source": "immediately preceding cycle's second-step active partition",
    "carry_key_rule": "highest contribution to the preceding second-step novel cue among its seven active rows; tie-break by higher utility then key",
    "next_first_step_rule": "reserve the carried key, then fill the remaining active slots by the unchanged 045 selector/guard ranking without duplicates",
    "second_step_rule": "byte-identical 045 selection; its resulting active partition determines the next carry key",
    "carried_state_width": 1,
    "learned_state": false
  },
  "metrics_and_thresholds": [
    ["source_identity_mismatch_count","==",0],
    ["source_count","==",3],
    ["total_source_bytes","==",57272],
    ["base_case_count","==",36],
    ["reuse_cycle_count_per_case","==",6],
    ["novel_interference_episode_count","==",432],
    ["state_carry_application_count","==",180],
    ["state_carry_width_min","==",1],
    ["state_carry_width_max","==",1],
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
    ["state_carry_accounting_error_count","==",0],
    ["heldout_selection_use_count","==",0],
    ["capacity_growth_event_count","==",0],
    ["row_mutation_event_count","==",0],
    ["tokenizer_use_count","==",0],
    ["external_model_call_count","==",0],
    ["invalid_evaluation_rows","==",0]
  ],
  "classification_rules": {
    "supported": "Validity passes; all 180 carry applications are accounted, all 432 safety checks meet the 0.95 floor, and all 432 target and 432 partner recoveries are positive.",
    "mixed": "Validity passes and protected recovery remains complete, but one or more non-target safety checks fail under state carry.",
    "negative": "Validity passes but any target or partner recovery becomes nonpositive.",
    "invalid": "Any sealed-parent, authority, source, carry accounting, carry width/rule, guard identity, frozen-state, capacity, determinism, or heldout-isolation criterion fails."
  },
  "validity_criteria": [
    "Exact qualified supported 045 parent and North Star identities match.",
    "Fresh READY_RESEARCH is bound to this exact preregistration and manifest.",
    "Rows, maps, cues, target orders, guard rule/applicability, six-cycle horizon, and capacity reproduce 045 exactly.",
    "The only new state is one deterministic carried row key between consecutive cycles; it never changes row contents, utilities, protected keys, thresholds, or capacity.",
    "Carry is applied only to the first step of cycles 1 through 5, exactly 180 times total.",
    "Heldout data affects scoring only and never carry-key selection, guard selection, cue construction, thresholds, or stopping.",
    "Duplicate complete executions are byte-identical.",
    "No tokenizer, external model, persistent corpus, LINKDEADKB execution, production authority, or post-result tuning occurs."
  ],
  "no_post_result_tuning_rule": "Do not alter sources, six-cycle horizon, carry width, carry source/ranking/reservation rule, episode order, novel cue, guard rule/applicability, 0.95 floor, capacity, metrics, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-STATE-CARRY-DEPTH-047",
    "intent": "increase bounded carried state from one row to a preregistered small multirow carry while keeping total capacity frozen"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-STATE-CARRY-ATTRIBUTION-047",
    "intent": "attribute the first carry-induced safety or recovery failure before changing carry width or guard"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-multirow-order-aware-state-carry-046.ice",
    "research/applications/plane/exp-dgr-external-cumulative-multirow-order-aware-state-carry-046.py",
    ".github/workflows/external-cumulative-multirow-order-aware-state-carry-046.yml"
  ]
}
