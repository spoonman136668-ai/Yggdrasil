{
  "experiment_id": "EXP-BRIDGE-HETEROGENEOUS-DEGRADATION-SHIFT-001",
  "program": "Wingless-Yggdrasil integrated maintenance",
  "question": "Does the already-qualified error-monitor / wrong-first / revert / correct-retain policy generalize without retuning to heterogeneous unseen higher-level degradation mechanisms under a shifted non-uniform raw-byte diagnostic distribution?",
  "hypothesis": "Across six new seeds and four sequential degradation cycles per seed, using the unchanged target monitor and 0.35 retain threshold from EXP-BRIDGE-INTERNAL-DEGRADATION-RETAIN-REVERT-001, the system will identify the affected compound key with 100% accuracy for compound removal, profile removal, compound-key corruption, and profile-bit corruption; reject every wrong same-budget repair, retain every correct repair, restore exact canonical structure identity and >=0.95 affected/unaffected/local accuracy after every cycle, and maintain selected-error-count ratio >=2 under the frozen non-uniform diagnostic pair distribution.",
  "exact_parent_sha": "4bd65021319e4158503f7edd262ee7b0e15960ea",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_policy": {
    "experiment": "EXP-BRIDGE-INTERNAL-DEGRADATION-RETAIN-REVERT-001",
    "classification_commit_sha": "4bd65021319e4158503f7edd262ee7b0e15960ea",
    "qualified_head_sha": "d889743240460d20ff830038d8cc8ea0d18dc82e",
    "result_sha256": "92ab4b8a767fb2255184a39273ce4df0d5960e7eb8270c37f18c437a250b7d27",
    "frozen_reuse": [
      "raw-error compound-key bucket monitor",
      "lexicographic tie break",
      "wrong candidate first from retained catalog id (selected+1) mod 4",
      "byte-exact revert after failed candidate",
      "correct paired compound/profile candidate second",
      "retain threshold overall long-range validation gain >=0.35 and local accuracy loss <=0"
    ]
  },
  "authority": "synthetic computational research only; no production, deployment, external-model inference, scheduler, queue, broker, accepted-ref, or runtime authority changes",
  "changed_paths": [
    "research/experiments/exp-bridge-heterogeneous-degradation-shift-001.ice",
    "research/applications/plane/exp-bridge-heterogeneous-degradation-shift-001.py",
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json"
  ],
  "canonical_state": {
    "structure_count": 16,
    "retained_catalog_bytes": 56,
    "definition": "exact bridge-004 / WBG-5 canonical 8 level-1, 4 level-2 compound, 4 profile state"
  },
  "seeds": [
    170003,
    171007,
    172001,
    173021,
    174031,
    175039
  ],
  "cycles": {
    "count_per_seed": 4,
    "total_cycles": 24,
    "target_compound": "c=(seed + 3*cycle) mod 4",
    "degradation_classes": [
      {
        "cycle_mod_4": 0,
        "name": "compound_missing",
        "operation": "remove selected level-2 compound structure; profile remains unchanged"
      },
      {
        "cycle_mod_4": 1,
        "name": "profile_missing",
        "operation": "remove selected reference-profile structure; compound remains unchanged"
      },
      {
        "cycle_mod_4": 2,
        "name": "compound_key_corruption",
        "operation": "replace first byte of selected compound key with byte XOR 1; profile remains unchanged"
      },
      {
        "cycle_mod_4": 3,
        "name": "profile_bit_corruption",
        "operation": "flip both selected profile contribution bits; compound remains unchanged"
      }
    ],
    "hidden_from_policy": "degradation class, target compound id, receiver id, evaluator affected/unaffected labels and cycle index are unavailable to monitoring, candidate construction decisions, validation and retain/revert",
    "sequential_state": "each next cycle begins from the retained recovered state of the prior cycle; no canonical reset"
  },
  "diagnostic_shift": {
    "records_per_unit_weight": 32,
    "ordered_pair_weight": "w(a,b)=1+((a+2*b) mod 3), producing 992 records total per cycle; all sixteen pairs remain present but non-uniform",
    "filler": "new deterministic SplitMix64-derived bytes mapped to 160..223, distinct from prior diagnostic/validation filler family",
    "observable": "raw compound keys, current prediction, subsequently observed target byte only",
    "monitor_rule": "unchanged from prior experiment: each misprediction increments each appearing retained-catalog compound key; repeated key increments twice; select highest count, lexicographic tie",
    "preregistered_expected_minimum_target_to_runner_up_ratio": 2.8
  },
  "candidates": {
    "construction": "unchanged from prior experiment; every candidate repairs both selected compound and corresponding profile, so candidate budget and structure shape are independent of hidden degradation class",
    "wrong_first": "payloads from catalog id (selected_id+1) mod 4 installed at selected fixed receivers",
    "correct_second": "selected key's own retained compound/profile payloads after byte-exact revert of wrong candidate",
    "read_bytes_per_candidate": 14,
    "repair_operations_per_candidate": 2
  },
  "validation": {
    "records_per_candidate": 512,
    "distribution": "all sixteen pairs balanced 32 times with filler phase disjoint from diagnostic_shift",
    "policy": "unchanged retain iff overall long-range gain >=0.35 and local level-1 accuracy loss <=0; otherwise byte-exact revert",
    "evaluator_strata_forbidden_in_decisions": true
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
      24
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
      "minimum_degradation_class_coverage",
      "==",
      4
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
      24
    ],
    [
      "minimum_correct_candidate_validation_gain",
      ">=",
      0.35
    ],
    [
      "correct_candidate_retain_count",
      "==",
      24
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
      "degradation_class_label_access_count",
      "==",
      0
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
      "policy_threshold_change_count",
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
    "Exact parent, North Star, prior-policy evidence identity, and canonical state match.",
    "The monitor, candidate order, wrong/correct candidate construction, revert semantics, validation stream size, and 0.35 retain threshold are byte/semantically unchanged from the supported prior policy except the diagnostic record schedule/filler distribution.",
    "All four degradation classes occur for every seed, but class labels are evaluator-only.",
    "Diagnostic pair weights are frozen by w(a,b)=1+((a+2*b) mod 3) and are independent of target/degradation class.",
    "Diagnostic and validation fillers/distributions are distinct and deterministic.",
    "Wrong and correct candidates use identical 14-byte/two-operation budgets.",
    "Every rejected candidate restores byte-exact pre-candidate state.",
    "Every retained result becomes the starting state of the next cycle.",
    "No capacity growth, external model, degradation label, lesion signal, evaluator stratum, or post-result threshold change occurs.",
    "Two duplicate executions are byte-identical."
  ],
  "classification_rules": {
    "supported": "All frozen thresholds and validity criteria pass across all 24 heterogeneous sequential cycles.",
    "mixed": "Monitoring and correct recovery generalize to all degradation classes but at least one confidence-margin, collateral, revert/retain, or fidelity threshold fails.",
    "negative": "Validity passes but target monitoring, wrong-candidate rejection, correct retention, or sequential recovery fails for one or more degradation classes/distribution-shift conditions.",
    "incomplete": "Environmental or compute interruption prevents full matrix.",
    "invalid": "Prior-policy identity, hidden-class isolation, shifted-distribution construction, sequential continuity, fixed capacity, deterministic execution, or qualification criteria fail."
  },
  "no_post_result_tuning_rule": "Do not alter seeds, degradation classes/schedule, diagnostic weights/filler, monitor, candidate policy, validation distribution, retain threshold, budgets, metrics, thresholds, aggregation, or classification after any output."
}
