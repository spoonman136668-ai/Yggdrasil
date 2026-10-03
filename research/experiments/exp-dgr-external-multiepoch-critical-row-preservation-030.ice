{
  "schema":"yggdrasil.direct-preregistration.v1",
  "experiment_id":"EXP-DGR-EXTERNAL-MULTIEPOCH-CRITICAL-ROW-PRESERVATION-030",
  "program":"Yggdrasil cumulative-memory consolidation with repeated low-signal protection",
  "question":"Does the supported cue-side C-critical-row preservation rule remain effective across repeated A/B-only reconsolidation epochs without increasing 16/7/9 capacity or degrading A/B?",
  "hypothesis":"For each of the six frozen schedules, identify the same pre-dormancy C-critical row from the all-domain state using C maturity-cue evidence only. Run three A/B-only reconsolidation epochs using frozen increasing A/B cue exposures at packet 4, packet 8, and full packet 12. After each epoch, if the protected row is absent, insert it one-for-one and evict the epoch interference row with minimum summed A/B cue contribution, then lower utility, then lexicographically larger key. C will remain positively reactivatable after every epoch and after epoch 3, while A/B retain at least 95% of their unprotected same-epoch heldout incremental benefits. Total state remains exactly 16/7/9.",
  "exact_parent_sha":"38cf305a935144d59d71577a3a7fd852518df239",
  "north_star_path":"research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256":"57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch":"research/external-hosted-yggdrasil-multiepoch-critical-row-preservation-r1",
  "prior_evidence":{
    "experiment":"EXP-DGR-EXTERNAL-CRITICAL-ROW-PRESERVATION-029",
    "github_run_id":"37112652996",
    "classification":"supported",
    "observation":{
      "preservation_case_count":6,
      "protected_row_absent_case_count":6,
      "protected_row_insert_case_count":6,
      "c_positive_reactivation_case_count":6,
      "minimum_c_preserved_incremental_correct_count":1,
      "minimum_non_target_preserved_to_unprotected_fraction":1.0,
      "critical_row_key":[116,114,117,99]
    },
    "diagnosis":"One cue-side C-critical row can be preserved one-for-one with no observed A/B heldout cost in the single-epoch interference matrix."
  },
  "external_authority":{
    "ckb_plane_main_sha":"36d99a0257120ede57bb96638660d35014dd529e",
    "manifest_sha256":"75cdb3b97dbb7017299f573d506f07095ed89c06264b29724b78f29c909d4da4",
    "research_decision_required":"READY_RESEARCH",
    "execution_host_policy":"GitHub-hosted compute only; host distinct from LINKDEADKB",
    "persistent_corpus":false,
    "external_model_calls":false,
    "production_authority":false
  },
  "frozen_reuse":{
    "sources":"byte-identical 029 external manifest",
    "external_split":"byte-identical first 60% cue / final 40% heldout",
    "schedules":"all six frozen permutations",
    "maturity_rule":"byte-identical twelve-packet maturity cue",
    "all_domain_state":"byte-identical 029 all-domain state reconstruction",
    "critical_row_selection":"byte-identical 029 C maturity-cue rule",
    "eviction_rule":"byte-identical 029 minimum summed A/B cue contribution, lower utility, lexicographically larger key",
    "active_selector":"byte-identical seven-active cue contribution selector",
    "capacity":"16 total / 7 active / 9 retained"
  },
  "multiepoch_protocol":{
    "epoch_count":3,
    "epoch_packet_indices":[4,8,12],
    "non_target_epoch_inputs":"A and B cumulative cue prefixes at the epoch packet index; packet 12 is full cue",
    "epoch_state":"fresh A/B-only minimax reconsolidation from base training plus the two epoch cue prefixes, followed by the frozen one-for-one C critical-row preservation rule if needed",
    "protected_row_identity":"frozen from the all-domain pre-dormancy state and C maturity cue; never recomputed from heldout or epoch outcomes",
    "heldout_updates":false
  },
  "metrics_and_thresholds":[
    ["source_identity_mismatch_count","==",0],
    ["source_count","==",3],
    ["total_source_bytes","==",57272],
    ["base_training_identity_mismatch_count","==",0],
    ["schedule_count","==",6],
    ["epoch_count","==",3],
    ["preservation_epoch_case_count","==",18],
    ["c_positive_epoch_case_count","==",18],
    ["final_epoch_c_positive_case_count","==",6],
    ["minimum_c_preserved_incremental_correct_count",">=",1],
    ["minimum_non_target_preserved_to_unprotected_fraction",">=",0.95],
    ["preserved_state_structure_count_min","==",16],
    ["preserved_state_structure_count_max","==",16],
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
  "classification_rules":{
    "supported":"Validity passes, C is positive in all 18 schedule-epoch cases and all six final epochs, and A/B benefit retention is at least 0.95 in every epoch.",
    "mixed":"Validity passes and all final-epoch C cases are positive, but an intermediate C case or A/B retention threshold fails.",
    "negative":"Validity passes but at least one final-epoch C case is nonpositive.",
    "invalid":"Any sealed-parent, authority, source, epoch packetization, protected-row identity, one-for-one preservation, capacity, determinism, or heldout-isolation criterion fails."
  },
  "validity_criteria":[
    "Exact sealed 029 parent and North Star identities match.",
    "Fresh READY_RESEARCH is bound to this exact preregistration and manifest.",
    "Protected-row identity is selected once per schedule from the all-domain state using C maturity cue only.",
    "Each epoch uses only the frozen A/B cue prefixes for that epoch and no C data in interference candidate statistics or minimax consolidation.",
    "Preservation is one-for-one and retains exactly sixteen structures / seven active / nine retained.",
    "No heldout result selects epoch state, protected row, eviction row, active rows, threshold, or stopping condition.",
    "Unprotected and preserved A/B scoring within an epoch use identical heldout evaluations and selectors.",
    "Duplicate executions are byte-identical and all numeric outputs are finite.",
    "No tokenizer, external model, persistent corpus, capacity/radius change, LINKDEADKB execution, production authority, or post-result tuning occurs."
  ],
  "no_post_result_tuning_rule":"Do not alter sources, split, schedules, epoch packet indices, protected-row definition, eviction rule, selectors, 0.95 non-target floor, capacity, metrics, thresholds, classification, or authority after primary output.",
  "successor_if_supported":{
    "experiment_family":"EXP-DGR-EXTERNAL-ROTATING-LOW-SIGNAL-PRESERVATION-031",
    "intent":"generalize fixed-capacity preservation from one protected domain to rotating low-signal dormant domains"
  },
  "successor_if_mixed_or_negative":{
    "experiment_family":"EXP-DGR-EXTERNAL-MULTIEPOCH-PRESERVATION-ATTRIBUTION-031",
    "intent":"attribute which epoch or non-target cue causes preservation or non-target-retention failure before changing capacity"
  },
  "changed_paths":[
    "research/experiments/exp-dgr-external-multiepoch-critical-row-preservation-030.ice",
    "research/applications/plane/exp-dgr-external-multiepoch-critical-row-preservation-030.py",
    ".github/workflows/external-multiepoch-critical-row-preservation-030.yml"
  ]
}
