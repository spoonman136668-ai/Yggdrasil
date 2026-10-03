{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-MINIMAL-EVIDENCE-CUMULATIVE-REACTIVATION-026",
  "program": "Yggdrasil external cumulative memory and cue-driven reactivation",
  "question": "After the supported twelve-packet cumulative horizon, can a previously inactive domain be reactivated from the surviving fixed 16-structure state using only the minimal cue that originally established positive evidence?",
  "hypothesis": "For each of the six supported orderings, reconstruct the exact final 025 sixteen-structure consolidated state. For each target domain, displace its active set by cue-selecting the other two domains in schedule order, without structural adaptation, then reactivate the target using only the earliest packet that met the frozen one-positive-row maturity rule. Across all 18 schedule-domain reactivation cases, the reactivated seven-active subset will retain positive heldout benefit and at least 0.50 of that domain's final-horizon active incremental benefit, with no state, record, or capacity changes.",
  "exact_parent_sha": "070074195a762fc6e630055d66b10ffb1211bb5f",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-cumulative-reactivation-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-MINIMAL-EVIDENCE-CUMULATIVE-HORIZON-025",
    "github_run_id": "37109825177",
    "classification": "supported",
    "observation": {
      "packet_event_count": 216,
      "admitted_domain_count": 18,
      "postadmission_evaluation_count": 336,
      "positive_then_nonpositive_transition_count": 0,
      "final_nonpositive_domain_count": 0,
      "minimum_active_to_independent_fraction_when_independent_positive": 0.9650711513583441
    },
    "diagnosis": "Cumulative memory is stable across six orders and twelve-packet temporal resolution. The next North-Star risk is cue-driven reactivation of dormant capability without re-adaptation."
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
    "sources": "byte-identical 025 external manifest",
    "external_split": "byte-identical first 60% cue / final 40% heldout",
    "schedules": "all six 025 permutations",
    "packetization": "byte-identical twelve cumulative prefix packets",
    "maturity_rule": "first packet with at least one strictly positive cue-side contribution row",
    "consolidation": "byte-identical 025 minimax consolidation and radius-two matching",
    "active_selector": "byte-identical seven-active cue contribution selector",
    "retained_encoding": "byte-identical nine-retained records",
    "capacity": "16 total / 7 active / 9 retained"
  },
  "reactivation_protocol": {
    "final_state": "the exact sixteen-row consolidated state at the final 025 event for each schedule",
    "target_cases": "three domains per schedule, eighteen total",
    "dormancy_displacement": "before target reactivation, select active seven for each of the other two domains using their own frozen maturity cues; this changes active membership only and does not alter the sixteen-row state",
    "reactivation_cue": "target domain's earliest cumulative packet that met the frozen one-positive-row maturity rule in that schedule",
    "reactivation_update": false,
    "evaluation": "target heldout bytes only",
    "reference": "target's final-horizon active incremental correct count from the same schedule"
  },
  "metrics_and_thresholds": [
    ["source_identity_mismatch_count","==",0],
    ["source_count","==",3],
    ["total_source_bytes","==",57272],
    ["base_training_identity_mismatch_count","==",0],
    ["schedule_count","==",6],
    ["reactivation_case_count","==",18],
    ["positive_reactivation_case_count","==",18],
    ["minimum_reactivation_to_final_active_fraction",">=",0.5],
    ["minimum_reactivation_incremental_correct_count",">=",1],
    ["reactivation_active_structure_count_min","==",7],
    ["reactivation_active_structure_count_max","==",7],
    ["reactivation_retained_structure_count_min","==",9],
    ["reactivation_retained_structure_count_max","==",9],
    ["reactivation_state_mutation_count","==",0],
    ["retained_record_integrity_mismatch_count","==",0],
    ["state_partition_mismatch_count","==",0],
    ["capacity_growth_event_count","==",0],
    ["tokenizer_use_count","==",0],
    ["external_model_call_count","==",0],
    ["invalid_evaluation_rows","==",0]
  ],
  "classification_rules": {
    "supported": "All validity criteria and all 18 reactivation thresholds pass.",
    "mixed": "Validity passes and all domains reactivate positively, but at least one reactivation/final benefit ratio falls below 0.50.",
    "negative": "Validity passes but at least one schedule-domain cannot reactivate to positive heldout benefit.",
    "invalid": "Any sealed-parent, authority, source, final-state, maturity-cue, no-update, partition, record, capacity, determinism, or host-isolation criterion fails."
  },
  "validity_criteria": [
    "Exact sealed 025 parent and North Star identities match.",
    "Fresh READY_RESEARCH is bound to this exact preregistration and manifest.",
    "The final consolidated sixteen-row state and maturity packet for each schedule-domain are reconstructed byte-for-byte from 025.",
    "Dormancy displacement and target reactivation perform active selection only; no candidate statistics, consolidation, structure replacement, or retained-record mutation occurs after the final state is frozen.",
    "Each active selection partitions exactly sixteen rows into seven active and nine retained.",
    "Heldout bytes never influence maturity cue selection, active ranking, thresholds, or stopping.",
    "Duplicate complete executions are byte-identical and all numeric outputs are finite.",
    "No tokenizer, external model, persistent corpus, capacity/radius change, LINKDEADKB execution, production authority, or post-result tuning occurs."
  ],
  "no_post_result_tuning_rule": "Do not alter sources, split, schedules, twelve-packet boundaries, maturity rule, final-state construction, dormancy displacement order, reactivation cue, no-update rule, capacity, metrics, thresholds, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-REACTIVATION-INTERFERENCE",
    "intent": "allow additional non-target consolidation during target dormancy, then test reactivation under genuine structural interference while preserving 16/7/9"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-REACTIVATION-ATTRIBUTION",
    "intent": "attribute reactivation failure to cue insufficiency versus retained-state loss before changing substrate"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-minimal-evidence-cumulative-reactivation-026.ice",
    "research/applications/plane/exp-dgr-external-minimal-evidence-cumulative-reactivation-026.py",
    ".github/workflows/external-minimal-evidence-cumulative-reactivation-026.yml"
  ]
}
