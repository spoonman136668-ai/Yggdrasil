{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-ORDER-AWARE-REUSE-ATTRIBUTION-043",
  "program": "Yggdrasil fixed-capacity repeated order-aware interference failure attribution",
  "question": "Are the repeated-use safety failures from 042 confined to one frozen target-order/step orientation rather than indicating guard decay across cycles?",
  "hypothesis": "Replay the exact 216 frozen 042 episodes without changing any row, cue, guard, selector, threshold, or capacity. All 36 non-target safety failures will reproduce exactly and every failure will occur in target-order index 0 at step index 1 with the guard not applied; the failures will repeat uniformly across all three cycles and only in the frozen AB/C and BC/A strata. Protected target and partner recovery will remain 216/216 positive. This would localize 042 to an orientation-specific guard-applicability hole rather than cumulative guard degradation.",
  "exact_parent_sha": "0cbaf9b1c3b53d83de18376e40f2c313dc82df66",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-cumulative-multirow-order-aware-reuse-attribution-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-ORDER-AWARE-NOVEL-INTERFERENCE-REUSE-042",
    "github_run_id": "37132325619",
    "classification": "mixed",
    "observation": {
      "novel_interference_episode_count": 216,
      "positive_post_episode_target_recovery_check_count": 216,
      "positive_post_episode_partner_recovery_check_count": 216,
      "non_target_safety_failure_count": 36,
      "guard_applied_episode_count": 72,
      "minimum_applicable_non_target_preserved_to_unprotected_fraction": 0.0,
      "invalid_evaluation_rows": 0
    },
    "diagnosis": "All protected recoveries survived, but repeated use reintroduced 36 non-target failures. The observed failure rows are all unguarded order-0 second-target steps; 043 freezes that as an attribution hypothesis before any repair."
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
    "source_experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-ORDER-AWARE-NOVEL-INTERFERENCE-REUSE-042",
    "sources": "byte-identical 042 external manifest",
    "base_case_count": 36,
    "reuse_cycles": 3,
    "novel_steps_per_cycle": 2,
    "episode_count": 216,
    "guard_rule": "byte-identical 042 guard",
    "guard_applicability": "byte-identical 042 applicability",
    "capacity": "16 total / 7 active / 9 retained",
    "row_learning": false,
    "utility_updates": false,
    "protected_key_updates": false
  },
  "attribution_protocol": {
    "method": "run the exact 042 probe and categorize only its already-produced diagnostics",
    "failure_categories": [
      "target_order_index",
      "step_index",
      "cycle_index",
      "target_pair_index",
      "target",
      "non_target",
      "guard_applied"
    ],
    "selection_data": "none; post hoc attribution only",
    "adaptive_changes": false
  },
  "metrics_and_thresholds": [
    ["source_identity_mismatch_count","==",0],
    ["source_count","==",3],
    ["total_source_bytes","==",57272],
    ["episode_count","==",216],
    ["base_failure_count","==",36],
    ["failure_order0_count","==",36],
    ["failure_step1_count","==",36],
    ["failure_unguarded_count","==",36],
    ["failure_pair0_count","==",18],
    ["failure_pair2_count","==",18],
    ["failure_pair1_count","==",0],
    ["failure_cycle0_count","==",12],
    ["failure_cycle1_count","==",12],
    ["failure_cycle2_count","==",12],
    ["orientation_match_fraction","==",1.0],
    ["positive_post_episode_target_recovery_check_count","==",216],
    ["positive_post_episode_partner_recovery_check_count","==",216],
    ["attribution_accounting_error_count","==",0],
    ["heldout_selection_use_count","==",0],
    ["capacity_growth_event_count","==",0],
    ["row_mutation_event_count","==",0],
    ["tokenizer_use_count","==",0],
    ["external_model_call_count","==",0],
    ["invalid_evaluation_rows","==",0]
  ],
  "classification_rules": {
    "supported": "Validity passes; all 36 failures reproduce and all 36 match the preregistered unguarded order-0 step-1 orientation, with 18 failures in pair 0, 18 in pair 2, none in pair 1, and 12 in each cycle.",
    "mixed": "Validity passes and protected recovery remains complete, but fewer than all failures match the frozen orientation or cycle/pair distribution differs.",
    "negative": "Validity passes but protected recovery degrades or the failure population no longer reproduces.",
    "invalid": "Any sealed-parent, authority, source, 042 replay, accounting, determinism, capacity, or heldout-isolation criterion fails."
  },
  "validity_criteria": [
    "Exact qualified mixed 042 parent and North Star identities match.",
    "Fresh READY_RESEARCH is bound to this exact preregistration and manifest.",
    "043 executes the exact 042 scientific probe and performs attribution only over returned diagnostics.",
    "No cue, row, map, utility, protected key, guard rule, guard applicability, selector, threshold, cycle count, or capacity changes.",
    "All 216 diagnostics are present exactly once and the 36 failures are accounted exactly once.",
    "Heldout data affects only the frozen 042 scoring and post hoc attribution.",
    "Duplicate complete executions are byte-identical.",
    "No tokenizer, external model, persistent corpus, LINKDEADKB execution, production authority, or post-result tuning occurs."
  ],
  "no_post_result_tuning_rule": "Do not alter the 042 replay, categories, 36-failure expectation, order/step hypothesis, pair/cycle accounting, safety floor, capacity, metrics, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-ORDER-AWARE-SECOND-STEP-SAFETY-REPAIR-044",
    "intent": "extend the frozen 041 guard only to the diagnosed order-0 second-target steps in the two failing strata, without changing capacity"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-ORDER-AWARE-REUSE-FACTORIAL-ATTRIBUTION-044",
    "intent": "factor cycle, order, pair, and guard interactions before any repair"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-multirow-order-aware-reuse-attribution-043.ice",
    "research/applications/plane/exp-dgr-external-cumulative-multirow-order-aware-reuse-attribution-043.py",
    ".github/workflows/external-cumulative-multirow-order-aware-reuse-attribution-043.yml"
  ]
}
