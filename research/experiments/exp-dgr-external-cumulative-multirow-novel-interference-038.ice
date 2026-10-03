{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-NOVEL-INTERFERENCE-038",
  "program": "Yggdrasil fixed-capacity reusable dormant-capability preservation under novel interference",
  "question": "Do the reusable preserved capabilities remain recoverable when the frozen 037 state is exposed to a new bounded interference episode that was not part of the original A/B/C reuse cycle?",
  "hypothesis": "Starting from each sealed 037 packet-12 preserved state, inject one deterministic novel interference cue derived only from training-prefix bytes by interleaving fixed-length segments from the two non-active domains without adding labels, rows, utilities, or capacity. Across all six schedules, three target pairs, both target orders, and three reuse cycles, every protected target will remain positively recoverable after the novel interference episode, the partner target will remain positively recoverable, and non-target safety will remain at least 0.95 under fixed 16 total / 7 active / 9 retained capacity.",
  "exact_parent_sha": "fb7e7fa43a877c0fcfb2eaf9e4e92ea714c03e95",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-cumulative-multirow-novel-interference-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-REACTIVATION-REUSE-037",
    "github_run_id": "37124619789",
    "classification": "supported",
    "observation": {
      "reuse_case_count": 36,
      "positive_target_activation_step_count": 216,
      "positive_partner_recovery_check_count": 216,
      "positive_post_hibernation_target_recovery_check_count": 216,
      "final_cycle_positive_target_activation_count": 72,
      "minimum_target_activation_incremental_correct_count": 1,
      "minimum_applicable_non_target_preserved_to_unprotected_fraction": 1,
      "row_mutation_event_count": 0
    },
    "diagnosis": "Repeated dormant-active-dormant reuse is stable with frozen rows. The next bounded stress is novel interference without changing capacity or learned state."
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
    "sources": "byte-identical 037 external manifest",
    "external_split": "byte-identical first 60% cue / final 40% heldout",
    "schedules": "all six frozen permutations",
    "target_pairs": [["A","B"],["A","C"],["B","C"]],
    "target_orders": "both permutations of each target pair",
    "reuse_cycles": 3,
    "packet12_preserved_state": "byte-identical sealed 037 construction",
    "maturity_rule": "byte-identical sealed maturity cues",
    "protected_row_rule": "byte-identical sealed rule",
    "active_selector": "byte-identical seven-active selector",
    "capacity": "16 total / 7 active / 9 retained",
    "row_learning": false,
    "utility_updates": false,
    "protected_key_updates": false
  },
  "novel_interference_protocol": {
    "episodes_per_reuse_case": 1,
    "reuse_case_count": 36,
    "novel_interference_episode_count": 36,
    "construction": "for each case, deterministically interleave 32-byte segments from the training-prefix cues of the current non-target domain and the first target domain, beginning with non-target; truncate to the shorter combined usable length",
    "selection_data": "training prefixes only",
    "insertion_point": "after completion of the third hibernation step and before final protected-target recovery checks",
    "state_effect": "recompute only active/retained partition over the same frozen sixteen rows",
    "heldout_updates": false,
    "row_learning": false
  },
  "metrics_and_thresholds": [
    ["source_identity_mismatch_count","==",0],
    ["source_count","==",3],
    ["total_source_bytes","==",57272],
    ["base_training_identity_mismatch_count","==",0],
    ["schedule_count","==",6],
    ["target_pair_count","==",3],
    ["target_order_count_per_pair","==",2],
    ["reuse_case_count","==",36],
    ["novel_interference_episode_count","==",36],
    ["post_novel_target_recovery_check_count","==",72],
    ["positive_post_novel_target_recovery_check_count","==",72],
    ["minimum_post_novel_target_incremental_correct_count",">=",1],
    ["post_novel_partner_recovery_check_count","==",72],
    ["positive_post_novel_partner_recovery_check_count","==",72],
    ["minimum_post_novel_partner_incremental_correct_count",">=",1],
    ["zero_baseline_preserved_negative_count","==",0],
    ["minimum_applicable_non_target_preserved_to_unprotected_fraction",">=",0.95],
    ["preserved_state_structure_count_min","==",16],
    ["preserved_state_structure_count_max","==",16],
    ["active_structure_count_min","==",7],
    ["active_structure_count_max","==",7],
    ["retained_structure_count_min","==",9],
    ["retained_structure_count_max","==",9],
    ["target_interference_leakage_count","==",0],
    ["heldout_selection_use_count","==",0],
    ["capacity_growth_event_count","==",0],
    ["row_mutation_event_count","==",0],
    ["tokenizer_use_count","==",0],
    ["external_model_call_count","==",0],
    ["invalid_evaluation_rows","==",0]
  ],
  "classification_rules": {
    "supported": "Validity passes; all 72 target and 72 partner post-novel recovery checks are positive; zero-baseline cases remain nonnegative; every ratio-applicable non-target retention ratio is at least 0.95.",
    "mixed": "Validity passes and all final target recoveries remain positive, but at least one partner or non-target safety threshold fails.",
    "negative": "Validity passes but at least one post-novel target recovery is nonpositive.",
    "invalid": "Any sealed-parent, authority, source, novel-cue construction, accounting, frozen-row identity, capacity, determinism, or heldout-isolation criterion fails."
  },
  "validity_criteria": [
    "Exact sealed 037 parent and North Star identities match.",
    "Fresh READY_RESEARCH is bound to this exact preregistration and external manifest.",
    "The novel cue is constructed only from training-prefix bytes by the fixed 32-byte interleave rule and is frozen before heldout scoring.",
    "The sixteen rows, utilities, protected keys, reuse cycle count, thresholds, and capacity remain unchanged.",
    "Novel interference may change only the active/retained partition over the same frozen rows.",
    "Heldout data affects scoring only and never cue construction, partition selection, stopping, thresholds, or successor choice.",
    "Duplicate complete executions are byte-identical and all numeric outputs are finite.",
    "No tokenizer, external model, persistent corpus, capacity/radius change, LINKDEADKB execution, production authority, or post-result tuning occurs."
  ],
  "no_post_result_tuning_rule": "Do not alter sources, split, schedules, target pairs, target orders, reuse cycles, novel 32-byte interleave rule, insertion point, selectors, safety semantics, 0.95 floor, capacity, metrics, thresholds, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-NOVEL-INTERFERENCE-REUSE-039",
    "intent": "repeat bounded novel interference across reuse cycles without changing capacity"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-NOVEL-INTERFERENCE-ATTRIBUTION-039",
    "intent": "attribute the first target/order/interference condition that breaks recovery before changing capacity"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-multirow-novel-interference-038.ice",
    "research/applications/plane/exp-dgr-external-cumulative-multirow-novel-interference-038.py",
    ".github/workflows/external-cumulative-multirow-novel-interference-038.yml"
  ]
}
