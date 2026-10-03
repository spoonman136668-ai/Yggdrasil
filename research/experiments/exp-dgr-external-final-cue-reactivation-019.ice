{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-FINAL-CUE-REACTIVATION-019",
  "program": "Yggdrasil external pipelined cumulative consolidation",
  "question": "After all three external domains have been cumulatively consolidated at fixed sixteen-cell capacity, can domain-specific cue activation reliably reactivate useful memory on two disjoint heldout windows per domain even when the full sixteen-structure store contains cross-domain interference?",
  "hypothesis": "The final cumulative sixteen-cell store remains a usable memory substrate when read through the unchanged seven-active cue selector: every one of the twelve order-by-domain-by-window reactivation evaluations will remain positive over the frozen baseline, while the seven-active/nine-retained partition, local geometry, and stored records remain intact. Full-store evaluations are measured only to quantify interference and are not used to select or tune the active set.",
  "exact_parent_sha": "139eb131d5c86c60c305c727af027142393bb1b1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-reactivation-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-INTERFERENCE-ATTRIBUTION-018",
    "qualification_run_id": "37083333508",
    "classification": "supported",
    "observation": "All independent external arms were positive. Exactly two full-cumulative arms were nonpositive, both on technical-prose C. In both failing full-store arms, the unchanged cue-selected seven-active subset remained positive. No active-partition-loss arm was observed."
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
  "frozen_input_protocol": {
    "sources": "byte-identical three-source manifest used by 017 and 018",
    "adaptation_split": "first floor(0.60*N) bytes per source, identical to 017/018",
    "heldout_split": "the existing 40% heldout region is divided once at its midpoint into H1 and H2; neither window is used for adaptation, consolidation, activation, threshold selection, or model choice",
    "encounter_orders": [["A","B","C"],["C","B","A"]],
    "final_state": "for each order, build the final cumulative state after all three complete adaptation cues using the byte-identical 017 minimax-matched mechanism"
  },
  "frozen_reuse": {
    "base_training": "byte-identical 016/017 baseline initialization",
    "candidate_statistics": "byte-identical 017 four-byte candidate statistics and eligibility",
    "minimax_ranking": "byte-identical 017 minimax ranking",
    "local_assignment": "byte-identical radius-two deterministic feasibility-preserving matching from 016/017",
    "active_selector": "byte-identical cue-side contribution selector from 017/018",
    "record_format": "byte-identical six-byte retained record",
    "capacity": "exactly sixteen total structures, seven active and nine retained"
  },
  "capacity": {
    "total_structures": 16,
    "active_structures": 7,
    "retained_structures": 9,
    "capacity_growth": false,
    "radius": 2
  },
  "primary_evaluation": {
    "rows": 12,
    "definition": "2 encounter orders x 3 domains x 2 disjoint heldout windows, all evaluated from the final cumulative store using the unchanged domain cue to select seven active structures",
    "controls": [
      "frozen baseline on the same heldout window",
      "independent adaptation on the same domain cue",
      "full sixteen-structure cumulative store on the same heldout window"
    ]
  },
  "metrics_and_thresholds": [
    ["source_identity_mismatch_count","==",0],
    ["source_count","==",3],
    ["total_source_bytes","==",57272],
    ["base_training_identity_mismatch_count","==",0],
    ["valid_final_state_count","==",2],
    ["reactivation_evaluation_count","==",12],
    ["matched_assignment_failure_count","==",0],
    ["minimum_selected_motif_count","==",16],
    ["maximum_selected_motif_count","==",16],
    ["minimum_active_structure_count","==",7],
    ["maximum_active_structure_count","==",7],
    ["minimum_retained_structure_count","==",9],
    ["maximum_retained_structure_count","==",9],
    ["retained_record_integrity_mismatch_count","==",0],
    ["state_partition_mismatch_count","==",0],
    ["active_reactivation_nonpositive_window_count","==",0],
    ["minimum_active_reactivation_incremental_correct_count",">",0],
    ["minimum_domain_order_active_aggregate_incremental_correct_count",">",0],
    ["capacity_growth_event_count","==",0],
    ["tokenizer_use_count","==",0],
    ["external_model_call_count","==",0],
    ["invalid_evaluation_rows","==",0]
  ],
  "diagnostic_metrics": [
    "independent_nonpositive_window_count",
    "full_store_nonpositive_window_count",
    "active_reactivation_rescue_window_count",
    "minimum_active_to_independent_fraction_when_independent_positive",
    "per-row baseline, independent, full-store, and active correct counts"
  ],
  "classification_rules": {
    "supported": "All validity criteria pass and all twelve active reactivation windows are positive over baseline.",
    "mixed": "Validity passes and each order-by-domain aggregate active benefit is positive, but at least one individual heldout window is nonpositive.",
    "negative": "Validity passes but at least one order-by-domain aggregate active reactivation benefit is nonpositive.",
    "invalid": "Any authority, identity, contamination, determinism, fixed-capacity, partition-integrity, or source-verification criterion fails.",
    "incomplete": "Authority, source retrieval, or hosted compute interruption prevents the frozen matrix."
  },
  "validity_criteria": [
    "The exact sealed 018 evidence head is the parent and all 017/018 files remain unchanged.",
    "A fresh ckb-plane READY_RESEARCH receipt is bound to this exact preregistration commit and the frozen external manifest.",
    "Execution occurs only on GitHub-hosted compute; source bytes are SHA-256 verified and deleted before completion.",
    "The full 60% cue for each domain is the only domain-specific information used to choose its seven active structures; H1 and H2 remain sealed until evaluation.",
    "Final cumulative state construction is unchanged from 017; the experiment changes only the read/evaluation surface.",
    "Every final state contains exactly sixteen matched structures and every cue read partitions them into exactly seven active and nine retained byte-exact records.",
    "Duplicate complete executions are byte-identical and all numeric outputs are finite.",
    "No tokenizer, external model, persistent corpus, capacity/radius change, LINKDEADKB execution, production authority, or post-result tuning occurs."
  ],
  "no_post_result_tuning_rule": "Do not alter source bytes, split points, heldout-window boundary, encounter orders, final-state construction, cue selector, capacity, metrics, thresholds, classification, or authority requirements after any primary output.",
  "changed_paths": [
    "research/experiments/exp-dgr-external-final-cue-reactivation-019.ice",
    "research/applications/plane/exp-dgr-external-final-cue-reactivation-019.py",
    ".github/workflows/external-final-cue-reactivation-019.yml"
  ]
}
