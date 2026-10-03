{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-DORMANT-AUTHORITY-ISOLATION-019",
  "program": "Yggdrasil external fixed-capacity cumulative consolidation",
  "question": "Does treating the nine retained structures as dormant storage with zero predictive authority until cue-selected reactivation remove the external cumulative interference isolated by 018 while preserving the fixed sixteen-cell, seven-active, nine-retained memory state?",
  "hypothesis": "On the exact 017 external sources, splits, encounter orders, consolidated sixteen-structure states, and 018 cue-side selector, restricting prediction to exactly seven cue-selected active structures will keep every seen-domain heldout arm positive, rescue both technical-prose nonpositive full-cumulative arms, retain at least 0.50 of independent-adaptation benefit and at least 0.50 of first-encounter prior-domain benefit, while the other nine structures remain byte-exact retained records and at least two distinct active sets are observed after all three domains have been consolidated.",
  "exact_parent_sha": "139eb131d5c86c60c305c727af027142393bb1b1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-dormant-authority-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-INTERFERENCE-ATTRIBUTION-018",
    "qualification_run_id": "37083333508",
    "classification": "supported",
    "observation": "All independent external arms were positive. Exactly two full-cumulative arms were nonpositive, both technical-prose C. The seven-active cue-selected predictor remained positive in both failing arms, with no active-partition-loss arm."
  },
  "external_authority": {
    "ckb_plane_main_sha": "36d99a0257120ede57bb96638660d35014dd529e",
    "manifest_sha256": "75cdb3b97dbb7017299f573d506f07095ed89c06264b29724b78f29c909d4da4",
    "research_decision_required": "READY_RESEARCH",
    "execution_host_policy": "GitHub-hosted compute only; host must be distinct from LINKDEADKB",
    "persistent_corpus": false,
    "external_model_calls": false,
    "production_authority": false
  },
  "frozen_reuse": {
    "sources": "byte-identical external source manifest from 017-018",
    "external_split": "byte-identical 60% cue / 40% heldout split from 017-018",
    "orders": [["A","B","C"],["C","B","A"]],
    "base_training": "byte-identical repo-owned baseline initialization from 016-018",
    "candidate_statistics": "byte-identical 017-018 candidate statistics",
    "independent_adaptation": "byte-identical 017-018 independent adaptation",
    "cumulative_consolidation": "byte-identical 017-018 minimax ranking and radius-two feasibility-preserving matching",
    "active_selector": "byte-identical 018 cue-side contribution selector and tie breaks",
    "retained_encoding": "byte-identical six-byte retained records from 016-018"
  },
  "mechanism_delta": {
    "predictive_authority": "Only the seven cue-selected active structures may contribute predictions. The nine retained structures remain stored but have zero predictive authority until selected active by a later cue.",
    "reactivation": "Each evaluation cue may select a different seven-active set from the same current sixteen-structure consolidated state; previous active membership grants no authority.",
    "storage": "All non-active structures are encoded as byte-exact retained records and must pass record-integrity and partition checks.",
    "capacity_change": false,
    "ranking_change": false,
    "matching_change": false,
    "selector_change": false,
    "threshold_change": false
  },
  "capacity": {
    "total_structures": 16,
    "active_structures": 7,
    "retained_structures": 9,
    "capacity_growth": false,
    "radius": 2
  },
  "metrics_and_thresholds": [
    ["source_identity_mismatch_count","==",0],
    ["source_count","==",3],
    ["total_source_bytes","==",57272],
    ["base_training_identity_mismatch_count","==",0],
    ["valid_stage_count","==",6],
    ["valid_seen_domain_evaluation_count","==",12],
    ["matched_assignment_failure_count","==",0],
    ["minimum_selected_motif_count","==",16],
    ["maximum_selected_motif_count","==",16],
    ["minimum_active_incremental_correct_count",">",0],
    ["minimum_active_to_independent_incremental_correct_fraction",">=",0.5],
    ["minimum_prior_domain_active_incremental_correct_count",">",0],
    ["minimum_prior_domain_active_to_first_encounter_fraction",">=",0.5],
    ["technical_prose_full_nonpositive_arm_count","==",2],
    ["technical_prose_active_positive_rescue_count","==",2],
    ["minimum_final_stage_distinct_active_set_count",">=",2],
    ["minimum_primary_active_structure_count","==",7],
    ["maximum_primary_active_structure_count","==",7],
    ["minimum_primary_retained_structure_count","==",9],
    ["maximum_primary_retained_structure_count","==",9],
    ["retained_record_integrity_mismatch_count","==",0],
    ["state_partition_mismatch_count","==",0],
    ["capacity_growth_event_count","==",0],
    ["tokenizer_use_count","==",0],
    ["external_model_call_count","==",0],
    ["invalid_evaluation_rows","==",0]
  ],
  "validity_criteria": [
    "The exact sealed 018 head is the parent and prior 017-018 scientific evidence remains unchanged.",
    "A fresh CKB-plane READY_RESEARCH receipt is bound to this exact preregistration commit and frozen external manifest.",
    "Execution occurs only on GitHub-hosted compute; verified external bytes are deleted before completion.",
    "No heldout byte enters adaptation, consolidation, active selection, or threshold selection.",
    "The sixteen consolidated structures, minimax ranking, radius-two matching, seven-active selector, and nine-retained record format are unchanged from 017-018.",
    "The only mechanism delta is predictive authority: retained structures are dormant until cue-selected active.",
    "Every evaluation has exactly seven active and nine retained structures, and every retained record is byte-exact.",
    "Duplicate executions are byte-identical and all numeric metrics are finite.",
    "No tokenizer, external model, persistent corpus, capacity growth, radius widening, production authority, LINKDEADKB execution, or post-result tuning occurs."
  ],
  "classification_rules": {
    "supported": "All validity criteria and frozen thresholds pass; dormant retained-authority isolation removes the observed external interference at fixed capacity.",
    "mixed": "Validity passes and both technical-prose failures are rescued, but at least one 0.50 retention/reactivation threshold or distinct-active-set criterion fails.",
    "negative": "Validity passes but any seen-domain active arm is nonpositive or either technical-prose interference arm is not rescued.",
    "invalid": "Any authority, identity, contamination, mechanism-drift, capacity, partition, record-integrity, determinism, or host-isolation criterion fails.",
    "incomplete": "Authority, source retrieval, or hosted compute interruption prevents the frozen matrix."
  },
  "no_post_result_tuning_rule": "Do not alter sources, splits, orders, consolidated state construction, active selector, retained encoding, predictive-authority rule, capacity, metrics, thresholds, or classification after any primary output.",
  "changed_paths": [
    "research/experiments/exp-dgr-external-dormant-authority-isolation-019.ice",
    "research/applications/plane/exp-dgr-external-dormant-authority-isolation-019.py",
    ".github/workflows/external-dormant-authority-isolation-019.yml"
  ]
}
