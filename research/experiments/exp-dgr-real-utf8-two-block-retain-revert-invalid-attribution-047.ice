{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-INVALID-ATTRIBUTION-047",
  "program": "DG1 real-byte adaptive granularity",
  "question": "Which frozen core validity class produced the single invalid_evaluation_rows event in experiment 044 on Y/Z/AA: candidate-statistics overflow/invalidity, developmental radius violation, or a residual structural check?",
  "hypothesis": "Exactly one frozen core event will account for experiment 044's invalid_evaluation_rows value of one, and candidate events plus radius events plus residual structural events will equal the unchanged core invalid total.",
  "exact_parent_sha": "e50f07276cadef43d1fe13d1dcf1a269b1123cca",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-FRESH-GIT-REPLICATION-044",
    "classification": "invalid-by-frozen-rules",
    "qualification_run_id": "38694585500",
    "result_sha256": "5d896e07e9ea1bab17a27a1ea3e822e7b4d8869f2e35ccb23a984442ed078f9f",
    "observation": "Duplicate output was byte-identical and identity, access, matching, partition, capacity, gate-error, and reported benefit metrics were otherwise favorable, but invalid_evaluation_rows equaled one. Therefore 044 makes no gate-performance claim and Y/Z/AA outcomes are observed.",
    "blocked_predecessors": "Experiments 045 and 046 were each preregistered then infrastructure-blocked before implementation or output; neither makes a scientific claim.",
    "continuation_rule": "047 is a non-fresh diagnostic on the same immutable inputs. It preserves all computation and adds read-only counters around already-frozen candidate_stats and develop calls; it cannot establish fresh generalization."
  },
  "authority": "synthetic research-only diagnostic on immutable repo-owned bytes; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": ["research/experiments/exp-dgr-real-utf8-two-block-retain-revert-invalid-attribution-047.ice", "research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-invalid-attribution-047.py", ".yggdrasil/qualification-request.json", ".yggdrasil/isolated-run.json"],
  "inputs": {
    "base_training": "Byte-identical four-file training set inherited from 029/043/044.",
    "demand": "Byte-identical observed Y/Z/AA cohort and Git-blob identities from 044.",
    "orders": [["Y", "Z", "AA"], ["AA", "Z", "Y"]],
    "split": "Byte-identical 044 half split, two contiguous first-half cue blocks, and independently reset raw four-byte context.",
    "contamination": "All Y/Z/AA scientific outputs are observed. This experiment attributes validity failure only and makes no fresh-cohort or gate-performance claim."
  },
  "arms": {
    "frozen_replay_control": "Unchanged 044 computation through the 043 gated runner with Y/Z/AA constants.",
    "candidate_diagnostic": "Count every nonzero overflow plus invalid return from unchanged candidate_stats calls without changing returns.",
    "radius_diagnostic": "Count every nonzero radius-violation return from unchanged develop calls without changing returns.",
    "residual_diagnostic": "Subtract candidate and radius event totals from the unchanged core invalid_evaluation_rows total."
  },
  "seeds": {"randomness": "none", "seed_list": [], "determinism": "All identities, orders, splits, fitting, hooks, and accounting are fixed; two complete executions must be byte-identical."},
  "budgets": {"base_training_files": 4, "demand_files": 3, "encounter_orders": 2, "stages_per_order": 3, "seen_domain_evaluation_rows": 12, "cell_count": 16, "active_structure_count": 10, "retained_structure_count": 6, "primary_runs": 2, "maximum_source_processes": 1, "timeout_seconds": 1800, "network_access": false, "capacity_growth_events": 0},
  "metrics_and_thresholds": [
    ["training_file_identity_mismatch_count", "==", 0], ["evaluation_file_identity_mismatch_count", "==", 0], ["future_stage_adaptation_access_count", "==", 0], ["second_half_adaptation_access_count", "==", 0],
    ["valid_stage_count", "==", 6], ["matched_assignment_failure_count", "==", 0], ["capacity_growth_event_count", "==", 0], ["retained_record_integrity_mismatch_count", "==", 0], ["state_partition_mismatch_count", "==", 0],
    ["core_invalid_event_count", "==", 1], ["candidate_invalid_event_count", ">=", 0], ["radius_violation_event_count", ">=", 0], ["residual_structural_invalid_event_count", ">=", 0], ["attribution_accounting_mismatch_count", "==", 0], ["attributed_class_count", "==", 1], ["instrumentation_return_mismatch_count", "==", 0]
  ],
  "controls": [
    "Reuse 044's Y/Z/AA bytes, identities, orders, splits, learner, gate, matching, partition, capacity, and core metrics unchanged.",
    "Instrumentation wrappers must return the original candidate_stats and develop objects identity/equality-identically and may only accumulate integer counters.",
    "The core invalid total is read before any outer 044 aggregation; the three attribution buckets must sum exactly to it.",
    "An attribution class is nonzero candidate, nonzero radius, or nonzero residual; exactly one class must be nonzero for supported attribution.",
    "Do not interpret or threshold the already-observed benefit, comparator, or gate-decision values."
  ],
  "validity_criteria": [
    "Exact parent, North Star, 044 evidence identity, 045/046 blocked-no-output provenance, source dependencies, Y/Z/AA Git identities, and sizes match.",
    "The unchanged core run completes six stages and preserves identity, access, matching, partition, and capacity controls.",
    "Every wrapper returns its original value unchanged, counters are finite nonnegative integers, and attribution accounting is exact.",
    "Two complete isolated executions are byte-identical and no tokenizer, external model, network, capacity growth, or state carry between orders occurs."
  ],
  "classification_rules": {
    "supported": "Validity passes, the unchanged core invalid total is exactly one, accounting is exact, and exactly one of candidate, radius, or residual structural classes is nonzero.",
    "mixed": "Validity passes and accounting is exact, but more than one attribution class is nonzero.",
    "null": "Validity passes but the unchanged core invalid total is zero, so the 044 invalid event does not reproduce.",
    "negative": "Validity passes but the unchanged core invalid total exceeds one or cannot be localized to a nonnegative attribution bucket.",
    "incomplete": "Compute interruption prevents both deterministic executions or all six stages.",
    "invalid": "Any identity, provenance, isolation, determinism, instrumentation-integrity, accounting, matching, partition, capacity, finiteness, or qualification criterion fails."
  },
  "stop_conditions": [
    "Stop invalid before diagnostic interpretation on any identity, lineage, dependency, size, or source mismatch.",
    "Stop invalid on mutated wrapper returns, negative/residual-inconsistent accounting, forbidden access, matching failure, partition corruption, capacity growth, non-finite metric, or nondeterministic duplicate output.",
    "Do not stop early for apparent supported, mixed, null, or negative outcomes.",
    "After any output is observed, do not repair or rerun under this experiment identifier."
  ],
  "no_post_result_tuning_rule": "After any primary or diagnostic output is observed, do not alter inputs, identities, orders, splits, learner, gate, hooks, counters, accounting, budgets, metrics, thresholds, validity, classification, or stopping rules under this experiment identifier."
}
