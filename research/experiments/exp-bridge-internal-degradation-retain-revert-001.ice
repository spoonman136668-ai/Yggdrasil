{
  "experiment_id": "EXP-BRIDGE-INTERNAL-DEGRADATION-RETAIN-REVERT-001",
  "program": "Wingless-Yggdrasil integrated maintenance",
  "question": "Can the integrated Wingless/Yggdrasil substrate detect an unknown higher-level degradation from its own raw-byte prediction errors, select the damaged structure without lesion labels, reject and revert a wrong bounded repair after held-out validation, retain the correct repair after recovery, and repeat the cycle on a second unseen degradation?",
  "hypothesis": "Across six new seeds and two sequential degradation cycles per seed, an error-only monitor will identify the lesioned Wingless compound key with 100% accuracy, a deliberately wrong same-budget repair candidate will produce <0.05 validation gain and be reverted every time, the correct retained candidate will improve held-out long-range accuracy by >=0.35 and be retained every time, exact canonical structure identity will be restored after each cycle, local level-1 accuracy and unaffected long-range accuracy will remain >=0.95, and no capacity growth or lesion-label access will occur.",
  "exact_parent_sha": "65c92d5c6bdefe6a28046911ac5a867eb1ade6a8",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_bridge": {
    "experiment": "EXP-BRIDGE-WINGLESS-YGGDRASIL-HIERARCHY-MAINTENANCE-004",
    "classification_commit_sha": "65c92d5c6bdefe6a28046911ac5a867eb1ade6a8",
    "qualified_head_sha": "765b7f909678ac5e69ce06c91dca805b5676a61b",
    "result_sha256": "489ed03df4246634b9dcbeef43013c99807c001c1c7afd1549040747b5ecf0a9",
    "classification": "supported"
  },
  "wingless_source": {
    "classification_commit_sha": "fa272d061773003720afc3cd74e3a954246b062a",
    "experiment": "WLM-LM-MULTISCALE-NATIVE-LANGUAGE-PRECURSOR-R2",
    "classification": "supported"
  },
  "authority": "synthetic computational research only; no production, deployment, external-model inference, broker, accepted-ref, scheduler, queue, runtime, or autonomous execution authority changes",
  "changed_paths": [
    "research/experiments/exp-bridge-internal-degradation-retain-revert-001.ice",
    "research/applications/plane/exp-bridge-internal-degradation-retain-revert-001.py",
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json"
  ],
  "canonical_state": {
    "structure_count": 16,
    "definition": "byte-identical 8 level-1 motifs, 4 level-2 compounds, and 4 reference profiles from the sealed bridge-004/WBG-5 canonical state",
    "retained_higher_level_catalog": "four 10-byte compound records plus four 4-byte profile records = 56 logical bytes; catalog contains no lesion labels or current-state health flags"
  },
  "seeds": [
    160001,
    161009,
    162017,
    163019,
    164021,
    165029
  ],
  "seed_policy": "All six seeds were checked against both Wingless and Yggdrasil repositories before preregistration and had no matches. No replacement, exclusion, or extension is permitted.",
  "cycles": {
    "count": 2,
    "lesion_cycle0": "compound id L0=(seed//2) mod 4 plus its corresponding reference profile",
    "lesion_cycle1": "compound id L1=(L0+1) mod 4 plus its corresponding reference profile",
    "hidden_from_monitor": "lesion ID, lesioned receiver index, cycle target, and evaluator affected/unaffected labels are unavailable to monitoring, candidate selection, validation, retain/revert, and repair",
    "prerequisite": "cycle 1 begins only from the retained/recovered state produced by cycle 0; no reset to canonical fixture between cycles"
  },
  "diagnostic_monitor": {
    "records_per_cycle": 512,
    "record_schedule": "all sixteen ordered compound pairs balanced exactly 32 times; raw 32-byte grammar records as in bridge-004",
    "observable": "for each raw record, current model prediction and subsequently observed true reference byte",
    "error_bucket_rule": "for every mispredicted record, increment an error counter for each of the two raw eight-byte compound keys appearing in the record if that key exists in the retained higher-level catalog; a repeated key in both positions increments twice",
    "selection": "choose the retained compound key with highest error count; ties choose lexicographically lowest eight-byte key",
    "lesion_labels": false
  },
  "repair_candidates": {
    "wrong_first": "using selected key S with catalog compound id c inferred only by exact retained-key lookup, construct a two-record candidate for receiver c using the compound-key payload and profile payload from retained catalog id (c+1) mod 4. Receiver/type bytes remain c's fixed receivers. Candidate reads 14 retained bytes and uses two repair operations.",
    "correct_second": "if wrong candidate is reverted, construct the two-record candidate from the selected key's own retained compound/profile records. Candidate reads 14 retained bytes and uses two repair operations.",
    "candidate_order": "wrong candidate is always evaluated first, then correct candidate only after wrong candidate is reverted"
  },
  "validation_policy": {
    "records_per_candidate": 512,
    "stream": "separate deterministic held-out raw grammar stream balanced over all sixteen ordered compound pairs; filler phase disjoint from diagnostic stream",
    "decision_observables": [
      "overall long-range reference accuracy",
      "level-1 local successor accuracy"
    ],
    "retain_if": "candidate overall long-range accuracy minus pre-candidate damaged-state accuracy >=0.35 AND local level-1 accuracy loss <=0.0",
    "revert_otherwise": "restore byte-exact pre-candidate state snapshot",
    "no_affected_labels": "validation policy cannot use evaluator affected/unaffected strata or lesion identity"
  },
  "evaluator_only_metrics": {
    "affected_record_definition": "record contains actual injected lesion compound in either position",
    "unaffected_record_definition": "record contains no injected lesion compound",
    "purpose": "scientific scoring only; unavailable to monitor/validation decisions"
  },
  "budgets": {
    "seed_count": 6,
    "cycles_per_seed": 2,
    "total_cycles": 12,
    "physical_structure_count": 16,
    "retained_catalog_bytes": 56,
    "retained_bytes_read_per_candidate": 14,
    "repair_operations_per_candidate": 2,
    "maximum_candidates_per_cycle": 2,
    "capacity_growth": false
  },
  "metrics_and_thresholds": [
    [
      "valid_seed_count",
      "==",
      6
    ],
    [
      "completed_cycle_count",
      "==",
      12
    ],
    [
      "minimum_monitor_target_selection_accuracy",
      "==",
      1
    ],
    [
      "minimum_selected_error_count_ratio_vs_runner_up",
      ">=",
      2
    ],
    [
      "maximum_wrong_candidate_validation_gain",
      "<",
      0.05
    ],
    [
      "wrong_candidate_retain_count",
      "==",
      0
    ],
    [
      "wrong_candidate_revert_count",
      "==",
      12
    ],
    [
      "minimum_correct_candidate_validation_gain",
      ">=",
      0.35
    ],
    [
      "correct_candidate_retain_count",
      "==",
      12
    ],
    [
      "correct_candidate_revert_count",
      "==",
      0
    ],
    [
      "minimum_post_retain_affected_long_range_accuracy",
      ">=",
      0.95
    ],
    [
      "minimum_post_retain_unaffected_long_range_accuracy",
      ">=",
      0.95
    ],
    [
      "minimum_post_retain_local_accuracy",
      ">=",
      0.95
    ],
    [
      "minimum_structure_jaccard_after_each_cycle",
      "==",
      1
    ],
    [
      "maximum_unlesioned_structure_mutation_count",
      "==",
      0
    ],
    [
      "maximum_candidate_read_bytes",
      "<=",
      14
    ],
    [
      "maximum_candidate_repair_operations",
      "<=",
      2
    ],
    [
      "maximum_final_structure_count",
      "==",
      16
    ],
    [
      "minimum_final_structure_count",
      "==",
      16
    ],
    [
      "lesion_label_access_count",
      "==",
      0
    ],
    [
      "evaluator_strata_access_in_decision_count",
      "==",
      0
    ],
    [
      "capacity_growth_event_count",
      "==",
      0
    ],
    [
      "invalid_cycle_rows",
      "==",
      0
    ]
  ],
  "validity_criteria": [
    "Exact parent/North-Star identity and sealed bridge-004/WBG-5 evidence identities match.",
    "All six seeds complete two sequential cycles without canonical-state reset between cycles.",
    "Monitor receives only raw keys, current predictions, observed post-prediction targets, and the retained key catalog; injected lesion identity is never exposed.",
    "Diagnostic and validation raw streams are disjoint by deterministic filler phase.",
    "Wrong and correct candidates have identical receiver count, record lengths, retained-byte read budget, and repair-operation budget.",
    "Validation decisions use only overall held-out long-range accuracy gain and level-1 local accuracy loss; evaluator affected/unaffected labels are inaccessible.",
    "A reverted candidate restores byte-exact pre-candidate state before the next candidate.",
    "A retained correct candidate becomes the starting state for the next cycle.",
    "Unlesioned structures are byte-identical across both cycles.",
    "No capacity growth, external model, oracle lesion signal, or post-result threshold change occurs.",
    "Two duplicate executions from identical inputs must be byte-identical."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all twenty-three frozen thresholds pass.",
    "mixed": "Monitoring and correct repair work across both cycles, but at least one revert/retain, collateral, fidelity, or efficiency threshold fails.",
    "negative": "Validity passes but the monitor cannot identify unseen damage, wrong candidates are retained, correct candidates fail validation/recovery, or repeated cycles lose prior capability.",
    "incomplete": "Environmental or compute interruption prevents full twelve-cycle matrix.",
    "invalid": "Source identity, hidden-lesion isolation, decision-policy isolation, deterministic construction, sequential-state continuity, fixed capacity, or qualification criteria fail."
  },
  "no_post_result_tuning_rule": "After any diagnostic, candidate, or validation output is observed, do not alter seeds, cycle lesion schedule, monitoring rule, error buckets, candidate order/construction, validation streams, retain threshold, budgets, metrics, thresholds, aggregation, or classification."
}
