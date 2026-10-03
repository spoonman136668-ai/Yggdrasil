{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-INTERFERENCE-ATTRIBUTION-028",
  "program": "Yggdrasil cumulative-memory structural-interference attribution",
  "question": "Why does low-signal domain C lose reactivation after A/B-only structural reconsolidation while A and B survive?",
  "hypothesis": "Reproduce the six sealed C failures from experiment 027. Using only C cue-side evidence, distinguish cue insufficiency from structural loss with two preregistered diagnostic arms. First, apply C's full training cue to the unchanged A/B interference state; if heldout benefit remains nonpositive, extra cue alone does not rescue. Second, restore exactly one absent C-critical row: the absent all-domain row with maximum positive contribution under C's frozen maturity cue, replacing the interference row with minimum maturity-cue contribution (deterministic utility/key tie-break), while keeping exactly 16 total structures. If this single cue-selected restoration makes C heldout benefit positive in all six schedules, the failure is attributed to structural displacement of C-critical memory.",
  "exact_parent_sha": "de9d94ee311aa5441509babedea439ad345aa0b5",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-interference-attribution-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-REACTIVATION-INTERFERENCE-027",
    "github_run_id": "37111322497",
    "classification": "negative",
    "observation": {
      "interference_case_count": 18,
      "interference_changed_case_count": 18,
      "positive_reactivation_case_count": 12,
      "domain_A_reactivation_fraction": 0.9065013404825737,
      "domain_B_reactivation_fraction": 0.891218872870249,
      "domain_C_reactivation_incremental_correct": 0,
      "domain_C_preinterference_incremental_correct": 1
    },
    "diagnosis": "The failure is selective to low-signal C across all six schedules after genuine non-target reconsolidation."
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
    "sources": "byte-identical 027 external manifest",
    "external_split": "byte-identical first 60% cue / final 40% heldout",
    "schedules": "all six frozen permutations",
    "maturity_rule": "byte-identical twelve-packet maturity cue",
    "all_domain_state": "byte-identical 027 all-domain final-state reconstruction",
    "interference_state": "byte-identical A/B-only state reconstruction for target C",
    "active_selector": "byte-identical seven-active cue contribution selector",
    "capacity": "16 total / 7 active / 9 retained"
  },
  "attribution_protocol": {
    "target": "C only",
    "case_count": 6,
    "critical_row_definition": "row in all-domain state with strictly positive contribution under C maturity cue",
    "critical_row_selection": "among critical rows absent from the A/B interference state, choose maximum maturity-cue contribution, then higher utility, then lexicographically smaller key",
    "full_cue_arm": "unchanged A/B interference state; select seven active rows using full C training cue; no structural update",
    "single_row_restore_arm": "replace the A/B interference row having minimum C-maturity-cue contribution (then lower utility, then lexicographically larger key) with the selected absent C-critical all-domain row; keep 16 rows; rebuild map from the corresponding sealed row records only; select active seven using C maturity cue",
    "heldout_use": "heldout C bytes are scoring-only and never select the critical row, replacement row, active rows, threshold, or stopping condition"
  },
  "metrics_and_thresholds": [
    ["source_identity_mismatch_count","==",0],
    ["source_count","==",3],
    ["total_source_bytes","==",57272],
    ["base_training_identity_mismatch_count","==",0],
    ["schedule_count","==",6],
    ["c_failure_reproduction_count","==",6],
    ["c_case_count","==",6],
    ["c_absent_critical_row_case_count","==",6],
    ["full_cue_positive_case_count","==",0],
    ["single_row_restore_case_count","==",6],
    ["single_row_restore_positive_case_count","==",6],
    ["minimum_single_row_restore_incremental_correct_count",">=",1],
    ["restored_state_structure_count_min","==",16],
    ["restored_state_structure_count_max","==",16],
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
    "supported": "Validity passes, all six C failures reproduce, full C cue alone rescues none, each case loses at least one C-critical row, and one cue-selected fixed-capacity row restoration rescues positive C benefit in all six cases.",
    "mixed": "Validity passes and structural loss is implicated, but full-cue or single-row-restoration outcomes are not uniform across all six schedules.",
    "negative": "Validity passes but the predicted structural-displacement attribution is not supported.",
    "invalid": "Any sealed-parent, authority, source, target-isolation, cue-only selection, fixed-capacity, determinism, or heldout-isolation criterion fails."
  },
  "validity_criteria": [
    "Exact sealed 027 parent and North Star identities match.",
    "Fresh READY_RESEARCH is bound to this exact preregistration and manifest.",
    "Only target C is analyzed because A and B already passed the sealed interference test in every schedule.",
    "All critical/replacement row choices use C training cue contributions and frozen row utility/key tie-breaks only.",
    "The full-cue arm makes no structural change.",
    "The restore arm performs exactly one-for-one replacement and remains at 16 total structures / 7 active / 9 retained.",
    "Heldout C bytes are scoring-only and cannot alter any choice.",
    "Duplicate executions are byte-identical and all numeric outputs are finite.",
    "No tokenizer, external model, persistent corpus, capacity/radius change, LINKDEADKB execution, production authority, or post-result tuning occurs."
  ],
  "no_post_result_tuning_rule": "Do not alter sources, split, schedules, C target selection, maturity cue, critical-row definition/tie-break, full-cue arm, one-row restoration rule, capacity, metrics, thresholds, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CRITICAL-ROW-PRESERVATION-029",
    "intent": "preregister a cue-side consolidation rule that preserves one low-signal critical row during non-target reconsolidation without increasing 16/7/9 capacity"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-INTERFERENCE-MECHANISM-029",
    "intent": "separate cue-ranking failure from representational incompatibility before changing substrate"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-interference-attribution-028.ice",
    "research/applications/plane/exp-dgr-external-interference-attribution-028.py",
    ".github/workflows/external-interference-attribution-028.yml"
  ]
}
