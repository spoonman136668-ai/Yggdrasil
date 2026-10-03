{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-INTERFERENCE-ATTRIBUTION-018",
  "program": "Yggdrasil external fixed-capacity cumulative consolidation",
  "question": "Did the valid negative in external cumulative consolidation 017 arise from cross-domain cumulative interference between otherwise learnable external domains, from the seven-active/nine-retained partition, or from a domain that is already nonpositive under independent adaptation?",
  "hypothesis": "The primary 017 failure is cumulative interference: at least one heldout arm that is positive under independent adaptation becomes nonpositive after cumulative minimax-matched consolidation, while the fixed sixteen-cell geometry remains valid. The experiment is diagnostic only and does not change selection, matching, capacity, activation, thresholds, source bytes, or encounter orders.",
  "exact_parent_sha": "7c87c9e810265eb7b991220141b2cf4b08ebb468",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-attribution-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-RAW-CUMULATIVE-CONSOLIDATION-017",
    "qualification_run_id": "37081722164",
    "classification": "negative",
    "validity_pass": true,
    "observed_metrics": {
      "minimum_cumulative_incremental_correct_count": -1,
      "minimum_cumulative_to_independent_incremental_correct_fraction": -1,
      "minimum_prior_domain_incremental_correct_count": -1,
      "minimum_prior_domain_to_first_encounter_fraction": -1,
      "minimum_active_retained_incremental_correct_fraction": 0,
      "minimum_selected_motif_count": 16,
      "maximum_selected_motif_count": 16,
      "minimum_primary_active_structure_count": 7,
      "maximum_primary_active_structure_count": 7,
      "minimum_primary_retained_structure_count": 9,
      "maximum_primary_retained_structure_count": 9
    }
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
    "source_manifest": "byte-identical three-source manifest from 017",
    "external_split": "byte-identical 60% cue / 40% heldout split from 017",
    "orders": [["A","B","C"],["C","B","A"]],
    "base_training": "byte-identical repo-owned baseline initialization from 016/017",
    "candidate_statistics": "byte-identical 017 candidate statistics",
    "independent_adaptation": "byte-identical 017 independent adaptation",
    "pooled_control": "byte-identical 017 cumulative pooled construction",
    "minimax_ranking": "byte-identical 017 minimax ranking",
    "local_assignment": "byte-identical 016/017 deterministic radius-two feasibility-preserving matching",
    "active_selector": "byte-identical 017 cue-side seven-active selector",
    "record_format": "byte-identical six-byte retained record"
  },
  "capacity": {
    "total_structures": 16,
    "active_structures": 7,
    "retained_structures": 9,
    "capacity_growth": false,
    "radius": 2
  },
  "diagnostic_outputs": [
    "For each of the twelve seen-domain evaluation arms: encounter order, stage, evaluated domain, baseline correct count, independent correct count, full cumulative correct count, seven-active correct count, and corresponding increments.",
    "Count independently nonpositive arms.",
    "Count positive-independent/nonpositive-cumulative interference arms.",
    "Count prior-domain flips from positive at first encounter to nonpositive after a later domain is admitted.",
    "Count full-cumulative-positive/seven-active-nonpositive partition-loss arms.",
    "Reproduce the five aggregate failure minima from 017 exactly before interpreting attribution."
  ],
  "metrics_and_thresholds": [
    ["source_identity_mismatch_count","==",0],
    ["source_count","==",3],
    ["total_source_bytes","==",57272],
    ["base_training_identity_mismatch_count","==",0],
    ["valid_stage_count","==",6],
    ["valid_seen_domain_evaluation_count","==",12],
    ["diagnostic_arm_count","==",12],
    ["matched_assignment_failure_count","==",0],
    ["minimum_selected_motif_count","==",16],
    ["maximum_selected_motif_count","==",16],
    ["minimum_primary_active_structure_count","==",7],
    ["maximum_primary_active_structure_count","==",7],
    ["minimum_primary_retained_structure_count","==",9],
    ["maximum_primary_retained_structure_count","==",9],
    ["retained_record_integrity_mismatch_count","==",0],
    ["state_partition_mismatch_count","==",0],
    ["capacity_growth_event_count","==",0],
    ["tokenizer_use_count","==",0],
    ["external_model_call_count","==",0],
    ["invalid_evaluation_rows","==",0],
    ["replayed_minimum_cumulative_incremental_correct_count","==",-1],
    ["replayed_minimum_cumulative_to_independent_incremental_correct_fraction","==",-1],
    ["replayed_minimum_prior_domain_incremental_correct_count","==",-1],
    ["replayed_minimum_prior_domain_to_first_encounter_fraction","==",-1],
    ["replayed_minimum_active_retained_incremental_correct_fraction","==",0]
  ],
  "attribution_rules": {
    "supported": "All validity/replay criteria pass, independently_nonpositive_arm_count is zero, and cumulative_interference_arm_count is at least one.",
    "mixed": "All validity/replay criteria pass and cumulative_interference_arm_count is at least one, but independent nonpositive or seven-active partition-loss arms also occur.",
    "negative": "All validity/replay criteria pass but no positive-independent/nonpositive-cumulative interference arm occurs; the 017 failure is attributable to independent learnability and/or the active partition rather than cumulative interference.",
    "invalid": "Any source/authority/replay/identity/fixed-capacity/partition/determinism criterion fails.",
    "incomplete": "Authority, source retrieval, or hosted compute interruption prevents the frozen diagnostic matrix."
  },
  "validity_criteria": [
    "The exact sealed 017 head is the parent and 017 remains unmodified.",
    "A fresh ckb-plane READY_RESEARCH receipt is bound to this exact preregistration commit and the frozen external manifest.",
    "Execution occurs only on GitHub-hosted compute; external bytes are verified before use and deleted before completion.",
    "No heldout byte enters adaptation, consolidation, activation, or threshold selection.",
    "The 017 mechanism is replayed without scientific changes; only diagnostic measurement is added.",
    "The five aggregate 017 failure minima reproduce exactly.",
    "Every stage remains exactly sixteen structures with seven active and nine retained; no capacity/radius change occurs.",
    "Duplicate executions are byte-identical and all numeric outputs are finite.",
    "No tokenizer, external model, persistent corpus, production authority, LINKDEADKB execution, or post-result tuning occurs."
  ],
  "no_post_result_tuning_rule": "Do not alter sources, split, orders, mechanism, capacity, active/retained partition, diagnostic definitions, replay values, attribution rules, authority requirements, or thresholds after any primary output.",
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-interference-attribution-018.ice",
    "research/applications/plane/exp-dgr-external-cumulative-interference-attribution-018.py",
    ".github/workflows/external-cumulative-interference-attribution-018.yml"
  ]
}
