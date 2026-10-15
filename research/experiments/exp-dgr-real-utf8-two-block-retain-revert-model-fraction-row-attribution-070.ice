{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-MODEL-FRACTION-ROW-ATTRIBUTION-070",
  "program": "DG1 real-byte adaptive granularity",
  "question": "Which exact order, stage, and seen-domain rows account for experiment 069's ten model_fraction invocations, and which two of the twelve scheduled rows bypass the selected_increment > 0 branch?",
  "hypothesis": "The unchanged 044 replay will map the ten paired model_fraction invocations one-to-one onto ten distinct scheduled seen-domain rows, leaving exactly two distinct scheduled rows uninvoked and no duplicate, unknown, or out-of-schedule attribution.",
  "exact_parent_sha": "b75b002c3d29be7bc801388fc540605c82a8833f",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-AUXILIARY-CALLSITE-ATTRIBUTION-069",
    "classification": "supported-by-frozen-rules",
    "qualification_run_id": "38783347305",
    "result_sha256": "a5f85d72526e90cef62c43453501f03e023719f4e4b50523dd5311e9a0cf35da",
    "observation": "The unchanged replay emitted ten calls at each of model_fraction's paired call sites and zero other auxiliary calls, proving ten invocations among twelve scheduled seen-domain rows without identifying their row coordinates.",
    "continuation_rule": "070 is a non-fresh read-only diagnostic on observed Y/Z/AA inputs and cannot establish gate performance, fresh generalization, or causal benefit."
  },
  "authority": "synthetic research-only diagnostic on immutable repo-owned bytes; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": ["research/experiments/exp-dgr-real-utf8-two-block-retain-revert-model-fraction-row-attribution-070.ice", "research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-model-fraction-row-attribution-070.py", ".yggdrasil/qualification-request.json", ".yggdrasil/isolated-run.json"],
  "inputs": {
    "base_training": "Byte-identical four-file training set inherited through 029/043/044/069.",
    "demand": "Byte-identical observed Y/Z/AA cohort and Git-blob identities from 044.",
    "orders": [["Y", "Z", "AA"], ["AA", "Z", "Y"]],
    "scheduled_rows": "For each order, stage prefixes of lengths one, two, and three are evaluated over every seen domain, yielding twelve unique (order_index, stage_index, domain) rows.",
    "split": "Byte-identical 044 half split, two contiguous first-half cue blocks, and independently reset raw four-byte context.",
    "contamination": "All Y/Z/AA outcomes and aggregate invocation counts are observed; only deterministic row attribution is tested."
  },
  "arms": {
    "frozen_replay_control": "Run unchanged 044 gated computation with frozen Y/Z/AA constants.",
    "row_attribution": "Observe each model_fraction entry without changing execution, attribute it from its caller's frozen order, stage-prefix, domain, and selected_increment locals, and compare the observed set with the preregistered twelve-row schedule."
  },
  "seeds": {"randomness": "none", "seed_list": [], "determinism": "All identities, orders, splits, fitting, observation, row keys, and accounting are fixed; two complete executions must be byte-identical."},
  "budgets": {"base_training_files": 4, "demand_files": 3, "encounter_orders": 2, "stages_per_order": 3, "scheduled_seen_domain_rows": 12, "expected_model_fraction_invocations": 10, "cell_count": 16, "active_structure_count": 10, "retained_structure_count": 6, "primary_runs": 2, "maximum_source_processes": 1, "timeout_seconds": 1800, "network_access": false, "capacity_growth_events": 0},
  "metrics_and_thresholds": [
    ["training_file_identity_mismatch_count", "==", 0], ["evaluation_file_identity_mismatch_count", "==", 0], ["future_stage_adaptation_access_count", "==", 0], ["second_half_adaptation_access_count", "==", 0], ["valid_stage_count", "==", 6], ["valid_seen_domain_evaluation_count", "==", 12], ["matched_assignment_failure_count", "==", 0], ["capacity_growth_event_count", "==", 0], ["retained_record_integrity_mismatch_count", "==", 0], ["state_partition_mismatch_count", "==", 0],
    ["scheduled_row_count", "==", 12], ["observed_model_fraction_invocation_count", "==", 10], ["unique_invoked_row_count", "==", 10], ["uninvoked_row_count", "==", 2], ["positive_selected_increment_invoked_row_count", "==", 10], ["nonpositive_selected_increment_invoked_row_count", "==", 0], ["duplicate_invoked_row_count", "==", 0], ["unknown_invoked_row_count", "==", 0], ["row_accounting_mismatch_count", "==", 0], ["sealed069_invocation_reproduction_mismatch_count", "==", 0],
    ["order0_invoked_row_mask", ">=", 0], ["order1_invoked_row_mask", ">=", 0], ["order0_uninvoked_row_mask", ">=", 0], ["order1_uninvoked_row_mask", ">=", 0], ["domain_y_invoked_row_count", ">=", 0], ["domain_z_invoked_row_count", ">=", 0], ["domain_aa_invoked_row_count", ">=", 0]
  ],
  "controls": [
    "Reuse 044's bytes, identities, orders, splits, learner, gate, matching, partition, capacity, calls, and blocks unchanged.",
    "Define the twelve scheduled row keys before execution in deterministic order: order 0 then order 1; within each, stage 1 through 3; within each stage, the order prefix's domain order.",
    "Observe only entries to error_guided.model_fraction called from experiment 029 line 440 and read the caller's order, seen, name, and selected_increment locals without mutation.",
    "Encode each order's invoked and uninvoked membership as a six-bit integer mask over its frozen six-row schedule and emit per-domain invocation totals.",
    "Verify sealed 069 evidence byte identity and reproduce its inferred invocation total; do not interpret benefit, comparator, retention, or gate-decision values."
  ],
  "validity_criteria": [
    "Exact parent, North Star, sealed 069 evidence identity, dependencies, and Y/Z/AA identities and sizes match.",
    "Unchanged replay completes six stages and preserves identity, access, matching, partition, and capacity controls.",
    "Every observed model_fraction invocation has the frozen immediate caller and a complete scheduled row key; row categories are exhaustive and disjoint.",
    "All invoked rows have selected_increment > 0 as required by the frozen line-439 guard, and schedule-complement accounting is exact.",
    "Two isolated executions are byte-identical; no tokenizer, external model, network, capacity growth, or state carry between orders."
  ],
  "classification_rules": {
    "supported": "Validity passes; ten invocations map to ten unique scheduled rows with positive selected_increment; exactly two distinct scheduled rows are uninvoked; and all accounting is exact.",
    "mixed": "Validity passes and exactly ten invocations are observed, but they do not map one-to-one onto ten distinct scheduled rows.",
    "null": "Validity passes but no model_fraction invocation is observed.",
    "negative": "Validity passes but the invocation count differs from ten or any invocation has nonpositive selected_increment.",
    "incomplete": "Compute interruption prevents both executions or all six stages.",
    "invalid": "Any identity, provenance, isolation, determinism, caller, row-key, schedule, accounting, matching, partition, capacity, finiteness, or qualification criterion fails."
  },
  "stop_conditions": [
    "Stop invalid before interpretation on identity, lineage, dependency, size, source, frozen caller-site, or schedule mismatch.",
    "Stop invalid on forbidden access, missing caller locals, unknown or overlapping row classification, inconsistent accounting, matching failure, partition corruption, capacity growth, non-finite metric, or nondeterministic duplicate output.",
    "Do not stop early for supported, mixed, null, or negative outcomes.",
    "After any output is observed, do not repair or rerun under this experiment identifier."
  ],
  "no_post_result_tuning_rule": "After any output is observed, do not alter inputs, identities, orders, splits, learner, gate, observation, caller definition, row schedule, mask encoding, accounting, budgets, metrics, thresholds, validity, classification, or stopping rules under this identifier."
}
