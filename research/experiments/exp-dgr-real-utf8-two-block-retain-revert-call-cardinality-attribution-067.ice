{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-CALL-CARDINALITY-ATTRIBUTION-067",
  "program": "DG1 real-byte adaptive granularity",
  "question": "What exact deterministic observed model_correct_counts call cardinality caused experiment 044's frozen expected-call-count predicate (len(calls) != 120) to contribute one invalid event?",
  "hypothesis": "The unchanged 044 replay will produce a finite nonnegative integer call count other than 120, and its Boolean mismatch will exactly reproduce qualified experiment 066's call_count_mismatch_event_count of one.",
  "exact_parent_sha": "0b557c2e48f1706a25bc09c4844c1c7fde10ba5c",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-INVALID-PREDICATE-ATTRIBUTION-066",
    "classification": "supported-by-frozen-rules",
    "qualification_run_id": "38781285787",
    "result_sha256": "106d3c01db06c3c2f315030b7fede72c0fa0ef7a8ece38ffa9c73b75250db556",
    "observation": "The call-count predicate alone contributed one event and exactly reproduced 044's single invalid row; the actual call cardinality was not emitted.",
    "continuation_rule": "067 is a non-fresh read-only diagnostic on observed Y/Z/AA inputs and cannot establish gate performance or fresh generalization."
  },
  "authority": "synthetic research-only diagnostic on immutable repo-owned bytes; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": ["research/experiments/exp-dgr-real-utf8-two-block-retain-revert-call-cardinality-attribution-067.ice", "research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-call-cardinality-attribution-067.py", ".yggdrasil/qualification-request.json", ".yggdrasil/isolated-run.json"],
  "inputs": {
    "base_training": "Byte-identical four-file training set inherited through 029/043/044/066.",
    "demand": "Byte-identical observed Y/Z/AA cohort and Git-blob identities from 044.",
    "orders": [["Y", "Z", "AA"], ["AA", "Z", "Y"]],
    "split": "Byte-identical 044 half split, two contiguous first-half cue blocks, and independently reset raw four-byte context.",
    "contamination": "All Y/Z/AA outcomes are observed; only observer call cardinality is attributed."
  },
  "arms": {
    "frozen_replay_control": "Run unchanged 044 gated computation with frozen Y/Z/AA constants.",
    "cardinality_attribution": "Emit len(calls), its signed and absolute difference from 120, and the unchanged Boolean mismatch."
  },
  "seeds": {"randomness": "none", "seed_list": [], "determinism": "All identities, orders, splits, fitting, observation, and accounting are fixed; two complete executions must be byte-identical."},
  "budgets": {"base_training_files": 4, "demand_files": 3, "encounter_orders": 2, "stages_per_order": 3, "seen_domain_evaluation_rows": 12, "cell_count": 16, "active_structure_count": 10, "retained_structure_count": 6, "primary_runs": 2, "maximum_source_processes": 1, "timeout_seconds": 1800, "network_access": false, "capacity_growth_events": 0},
  "metrics_and_thresholds": [
    ["training_file_identity_mismatch_count", "==", 0], ["evaluation_file_identity_mismatch_count", "==", 0], ["future_stage_adaptation_access_count", "==", 0], ["second_half_adaptation_access_count", "==", 0], ["valid_stage_count", "==", 6], ["matched_assignment_failure_count", "==", 0], ["capacity_growth_event_count", "==", 0], ["retained_record_integrity_mismatch_count", "==", 0], ["state_partition_mismatch_count", "==", 0],
    ["observed_call_count", ">=", 0], ["expected_call_count", "==", 120], ["signed_call_count_difference", "!=", 0], ["absolute_call_count_difference", ">", 0], ["call_count_mismatch_event_count", "==", 1], ["prior066_call_count_mismatch_event_count", "==", 1], ["predicate_reproduction_mismatch_count", "==", 0]
  ],
  "controls": [
    "Reuse 044's bytes, identities, orders, splits, learner, gate, matching, partition, capacity, and call observer unchanged.",
    "Derive all new metrics only from len(calls) returned by unchanged 043 gated_run under 044's frozen constants.",
    "Verify sealed 066 evidence byte identity and compare the derived Boolean predicate to its emitted value.",
    "Do not interpret or threshold observed benefit, comparator, retention, or gate-decision values."
  ],
  "validity_criteria": [
    "Exact parent, North Star, sealed 066 evidence identity, dependencies, and Y/Z/AA identities and sizes match.",
    "Unchanged replay completes six stages and preserves identity, access, matching, partition, and capacity controls.",
    "Observed cardinality is a finite nonnegative integer and signed/absolute accounting is exact.",
    "Two isolated executions are byte-identical; no tokenizer, external model, network, capacity growth, or state carry between orders."
  ],
  "classification_rules": {
    "supported": "Validity passes, observed call count differs from 120, and its Boolean mismatch exactly reproduces 066's value of one.",
    "mixed": "Validity passes and observed call count differs from 120, but the frozen signed or absolute accounting is inconsistent.",
    "null": "Validity passes and observed call count equals 120.",
    "negative": "Validity passes but observed call cardinality is nonintegral, negative, or cannot reproduce the sealed predicate.",
    "incomplete": "Compute interruption prevents both executions or all six stages.",
    "invalid": "Any identity, provenance, isolation, determinism, accounting, matching, partition, capacity, finiteness, or qualification criterion fails."
  },
  "stop_conditions": [
    "Stop invalid before interpretation on identity, lineage, dependency, size, or source mismatch.",
    "Stop invalid on forbidden access, inconsistent accounting, matching failure, partition corruption, capacity growth, non-finite metric, or nondeterministic duplicate output.",
    "Do not stop early for supported, mixed, null, or negative outcomes.",
    "After any output is observed, do not repair or rerun under this experiment identifier."
  ],
  "no_post_result_tuning_rule": "After any output is observed, do not alter inputs, identities, orders, splits, learner, gate, observation, accounting, budgets, metrics, thresholds, validity, classification, or stopping rules under this identifier."
}
