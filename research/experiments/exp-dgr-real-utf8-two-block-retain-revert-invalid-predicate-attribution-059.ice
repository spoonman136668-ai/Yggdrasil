{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-INVALID-PREDICATE-ATTRIBUTION-059",
  "program": "DG1 real-byte adaptive granularity",
  "question": "Which frozen validity predicate produced experiment 044's invalid_evaluation_rows value of one: the inherited core count, experiment-identity mismatch, call-count mismatch, block-count mismatch, malformed block shape, or inherited gate-decision mismatch?",
  "hypothesis": "Exactly one frozen predicate will contribute one invalid event, and the six predicate contributions will reproduce experiment 044's invalid_evaluation_rows value of one.",
  "exact_parent_sha": "272351ac7f65df836020827f69700cebe086b7a1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-FRESH-GIT-REPLICATION-044",
    "classification": "invalid-by-frozen-rules",
    "qualification_run_id": "38694585500",
    "result_sha256": "5d896e07e9ea1bab17a27a1ea3e822e7b4d8869f2e35ccb23a984442ed078f9f",
    "observation": "Duplicate output was byte-identical and invalid_evaluation_rows was one; its aggregate does not identify which of six frozen predicates failed.",
    "blocked_predecessors": "Experiments 045 through 058 were preregistered then infrastructure-blocked before implementation or output; none makes a scientific claim.",
    "continuation_rule": "059 is a non-fresh read-only attribution replay on observed Y/Z/AA inputs and cannot establish gate performance or fresh generalization."
  },
  "authority": "synthetic research-only diagnostic on immutable repo-owned bytes; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": ["research/experiments/exp-dgr-real-utf8-two-block-retain-revert-invalid-predicate-attribution-059.ice", "research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-invalid-predicate-attribution-059.py", ".yggdrasil/qualification-request.json", ".yggdrasil/isolated-run.json"],
  "inputs": {
    "base_training": "Byte-identical four-file training set inherited through 029/043/044.",
    "demand": "Byte-identical observed Y/Z/AA cohort and Git-blob identities from 044.",
    "orders": [["Y", "Z", "AA"], ["AA", "Z", "Y"]],
    "split": "Byte-identical 044 half split, two contiguous first-half cue blocks, and independently reset raw four-byte context.",
    "contamination": "All Y/Z/AA outcomes are observed; only validity failure is attributed."
  },
  "arms": {
    "frozen_replay_control": "Run unchanged 044 gated computation with frozen Y/Z/AA constants.",
    "predicate_attribution": "Report inherited core count and five outer Boolean predicates separately, then reproduce unchanged Boolean-OR aggregation."
  },
  "seeds": {"randomness": "none", "seed_list": [], "determinism": "All identities, orders, splits, fitting, hooks, predicates, and accounting are fixed; two complete executions must be byte-identical."},
  "budgets": {"base_training_files": 4, "demand_files": 3, "encounter_orders": 2, "stages_per_order": 3, "seen_domain_evaluation_rows": 12, "cell_count": 16, "active_structure_count": 10, "retained_structure_count": 6, "primary_runs": 2, "maximum_source_processes": 1, "timeout_seconds": 1800, "network_access": false, "capacity_growth_events": 0},
  "metrics_and_thresholds": [
    ["training_file_identity_mismatch_count", "==", 0], ["evaluation_file_identity_mismatch_count", "==", 0], ["future_stage_adaptation_access_count", "==", 0], ["second_half_adaptation_access_count", "==", 0], ["valid_stage_count", "==", 6], ["matched_assignment_failure_count", "==", 0], ["capacity_growth_event_count", "==", 0], ["retained_record_integrity_mismatch_count", "==", 0], ["state_partition_mismatch_count", "==", 0],
    ["inherited_core_invalid_event_count", ">=", 0], ["experiment_identity_mismatch_event_count", ">=", 0], ["call_count_mismatch_event_count", ">=", 0], ["block_count_mismatch_event_count", ">=", 0], ["malformed_block_event_count", ">=", 0], ["gate_decision_mismatch_event_count", ">=", 0], ["reproduced_invalid_evaluation_rows", "==", 1], ["predicate_accounting_mismatch_count", "==", 0], ["nonzero_predicate_count", "==", 1]
  ],
  "controls": [
    "Reuse 044's bytes, identities, orders, splits, learner, gate, matching, partition, capacity, calls, blocks, and inherited core metrics unchanged.",
    "Compute each outer predicate with the exact 044 expression and expected constant; preserve Boolean-OR aggregation.",
    "Account inherited core count plus Boolean OR of five outer predicates against the reproduced invalid metric.",
    "Do not interpret or threshold observed benefit, comparator, retention, or gate-decision values."
  ],
  "validity_criteria": [
    "Exact parent, North Star, 044 evidence identity, blocked-no-output provenance through 058, dependencies, and Y/Z/AA identities and sizes match.",
    "Unchanged replay completes six stages and preserves identity, access, matching, partition, and capacity controls.",
    "Six attribution values are finite nonnegative integers, five outer values are Boolean, and accounting reproduces 044's invalid metric.",
    "Two isolated executions are byte-identical; no tokenizer, external model, network, capacity growth, or state carry between orders."
  ],
  "classification_rules": {
    "supported": "Validity passes, reproduced invalid value is one, accounting is exact, and exactly one predicate is nonzero.",
    "mixed": "Validity passes and accounting is exact, but more than one predicate is nonzero.",
    "null": "Validity passes but reproduced invalid value is zero.",
    "negative": "Validity passes but reproduced invalid value exceeds one or cannot be localized to nonnegative frozen predicate values.",
    "incomplete": "Compute interruption prevents both executions or all six stages.",
    "invalid": "Any identity, provenance, isolation, determinism, accounting, matching, partition, capacity, finiteness, or qualification criterion fails."
  },
  "stop_conditions": [
    "Stop invalid before interpretation on identity, lineage, dependency, size, or source mismatch.",
    "Stop invalid on forbidden access, inconsistent accounting, matching failure, partition corruption, capacity growth, non-finite metric, or nondeterministic duplicate output.",
    "Do not stop early for supported, mixed, null, or negative outcomes.",
    "After any output is observed, do not repair or rerun under this experiment identifier."
  ],
  "no_post_result_tuning_rule": "After any output is observed, do not alter inputs, identities, orders, splits, learner, gate, hooks, predicate definitions, accounting, budgets, metrics, thresholds, validity, classification, or stopping rules under this identifier."
}
