{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-REACTIVATION-INTERFERENCE-027",
  "program": "Yggdrasil external cumulative memory under structural interference",
  "question": "Can a dormant domain reactivate after the fixed 16-structure state is structurally reconsolidated using only the other two domains?",
  "hypothesis": "For each of the six schedules and each target domain, reconstruct the sealed 026 all-domain final state and its final active benefit. Then omit the target entirely and perform one frozen minimax consolidation using only the two non-target full cues, producing a genuine changed sixteen-row interference state. Without target adaptation or reconsolidation, use only the target's frozen maturity cue to select seven active structures from that interference state and evaluate target heldout. All 18 cases will reactivate positively and retain at least 0.50 of the target's pre-interference final active incremental benefit.",
  "exact_parent_sha": "8ac20bd73227d7cb5268e6815516d196ceb7ff92",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-reactivation-interference-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-MINIMAL-EVIDENCE-CUMULATIVE-REACTIVATION-026",
    "github_run_id": "37110752549",
    "classification": "supported",
    "observation": {
      "reactivation_case_count": 18,
      "positive_reactivation_case_count": 18,
      "minimum_reactivation_to_final_active_fraction": 0.989946380697051,
      "reactivation_state_mutation_count": 0
    },
    "diagnosis": "Cue-only reactivation works almost losslessly when the sixteen-row memory state is frozen. The next risk is true structural interference while the target is dormant."
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
    "sources": "byte-identical 026 external manifest",
    "external_split": "byte-identical first 60% cue / final 40% heldout",
    "schedules": "all six frozen permutations",
    "maturity_rule": "byte-identical frozen twelve-packet maturity cue from 026",
    "all_domain_final_state": "byte-identical 026 final-state reconstruction",
    "consolidation": "byte-identical minimax ranking and radius-two matching",
    "active_selector": "byte-identical seven-active cue contribution selector",
    "retained_encoding": "byte-identical nine-retained records",
    "capacity": "16 total / 7 active / 9 retained"
  },
  "interference_protocol": {
    "case_count": 18,
    "target_omission": "target cue is absent from all interference candidate statistics and consolidation inputs",
    "non_target_inputs": "the two non-target full cues, ordered by their appearance in the frozen schedule",
    "interference_state": "a new sixteen-row minimax consolidated state built from base training plus only the two non-target cues",
    "required_state_change": "interference-state record set must differ from the all-domain final-state record set in every case",
    "reactivation": "target maturity cue selects seven active structures from the interference state; no target candidate-statistics update or reconsolidation occurs",
    "evaluation": "target heldout bytes only",
    "reference": "target final active incremental correct count in the all-domain final state"
  },
  "metrics_and_thresholds": [
    ["source_identity_mismatch_count","==",0],
    ["source_count","==",3],
    ["total_source_bytes","==",57272],
    ["base_training_identity_mismatch_count","==",0],
    ["schedule_count","==",6],
    ["interference_case_count","==",18],
    ["interference_changed_case_count","==",18],
    ["target_interference_leakage_count","==",0],
    ["positive_reactivation_case_count","==",18],
    ["minimum_reactivation_to_preinterference_fraction",">=",0.5],
    ["minimum_reactivation_incremental_correct_count",">=",1],
    ["active_structure_count_min","==",7],
    ["active_structure_count_max","==",7],
    ["retained_structure_count_min","==",9],
    ["retained_structure_count_max","==",9],
    ["retained_record_integrity_mismatch_count","==",0],
    ["state_partition_mismatch_count","==",0],
    ["capacity_growth_event_count","==",0],
    ["tokenizer_use_count","==",0],
    ["external_model_call_count","==",0],
    ["invalid_evaluation_rows","==",0]
  ],
  "classification_rules": {
    "supported": "All validity criteria pass, every interference state genuinely changes, all 18 targets reactivate positively, and minimum benefit retention is >=0.50.",
    "mixed": "Validity passes and all targets reactivate positively, but at least one benefit-retention ratio is below 0.50.",
    "negative": "Validity passes but at least one target fails to reactivate to positive benefit after structural interference.",
    "invalid": "Any sealed-parent, authority, source, target-omission, state-change, maturity-cue, capacity, partition, record, determinism, or host-isolation criterion fails."
  },
  "validity_criteria": [
    "Exact sealed 026 parent and North Star identities match.",
    "Fresh READY_RESEARCH is bound to this exact preregistration and manifest.",
    "All-domain reference states and maturity cues are reconstructed using sealed 026 mechanics.",
    "Each interference state uses exactly the two non-target full cues and excludes the target from candidate statistics, independent rows, current demands, and minimax inputs.",
    "The interference state must differ structurally from the all-domain state before target reactivation is scored.",
    "Target reactivation performs active selection only; no target structural update occurs.",
    "Every active selection partitions exactly sixteen structures into seven active and nine retained.",
    "Heldout bytes never influence consolidation, maturity cue, active ranking, thresholds, or stopping.",
    "Duplicate complete executions are byte-identical and all numeric outputs are finite.",
    "No tokenizer, external model, persistent corpus, capacity/radius change, LINKDEADKB execution, production authority, or post-result tuning occurs."
  ],
  "no_post_result_tuning_rule": "Do not alter sources, split, schedules, maturity cues, target-omission rule, interference inputs, consolidation, active selector, capacity, metrics, thresholds, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIEPOCH-INTERFERENCE",
    "intent": "repeat non-target consolidation across multiple dormant epochs before reactivation while keeping 16/7/9 fixed"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-INTERFERENCE-ATTRIBUTION",
    "intent": "identify which retained structures or domains are lost during non-target reconsolidation before changing substrate"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-reactivation-interference-027.ice",
    "research/applications/plane/exp-dgr-external-cumulative-reactivation-interference-027.py",
    ".github/workflows/external-cumulative-reactivation-interference-027.yml"
  ]
}
