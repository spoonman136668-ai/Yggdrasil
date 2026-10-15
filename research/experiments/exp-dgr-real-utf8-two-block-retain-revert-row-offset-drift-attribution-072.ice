{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-ROW-OFFSET-DRIFT-ATTRIBUTION-072",
  "program": "DG1 real-byte adaptive granularity",
  "question": "Does experiment 043's global len(calls) modulo ten gate remain aligned to all twelve logical rows after two zero selected_increment rows suppress their paired model_fraction calls?",
  "hypothesis": "The unchanged 044 replay will have seven aligned row starts followed by five drifted starts; the two sealed zero rows will have eight calls and the other ten rows ten calls, so the global offset-five hook will coincide with the logical cue-minimax call on exactly seven rows.",
  "exact_parent_sha": "4952dcaa885f0060eeb262935b6f88f907b18142",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-SELECTED-INCREMENT-ROW-ATTRIBUTION-071",
    "classification": "supported-by-frozen-rules",
    "qualification_run_id": "38784902260",
    "result_sha256": "abbead4be2f58facf7a0ae452a5c59b953076885bfd1867a1ae02c430c9ca1ef",
    "observation": "Ten scheduled rows have positive selected_increment; order-1 stage-1 AA and order-1 stage-2 AA are exactly zero and bypass the paired model_fraction calls.",
    "continuation_rule": "This is a non-fresh read-only diagnostic on observed Y/Z/AA and cannot establish gate performance, fresh generalization, causal benefit, or a corrected validity rule."
  },
  "authority": "synthetic research-only diagnostic on immutable repo-owned bytes; no wetware, deployment, external inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": ["research/experiments/exp-dgr-real-utf8-two-block-retain-revert-row-offset-drift-attribution-072.ice", "research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-row-offset-drift-attribution-072.py", ".yggdrasil/qualification-request.json", ".yggdrasil/isolated-run.json"],
  "inputs": {
    "base_training": "Byte-identical four-file set inherited through 029/043/044/071.",
    "demand": "Byte-identical observed Y/Z/AA cohort and Git identities from 044.",
    "orders": [["Y", "Z", "AA"], ["AA", "Z", "Y"]],
    "scheduled_rows": "Twelve frozen rows: each order's stage prefixes of lengths one, two, and three over every seen domain.",
    "call_model": "Eight unconditional model_correct_counts calls per row plus two calls iff selected_increment is positive; experiment 043 hooks by global pre-call count modulo ten.",
    "contamination": "Outcomes, signs, aggregate cardinality, and origins are observed; only row-start alignment and hook correspondence remain tested."
  },
  "arms": {
    "frozen_replay_control": "Run unchanged 044 gated computation.",
    "offset_attribution": "Read-only trace row entry, the selected_increment guard, and model_correct_counts entry; derive each row's start offset modulo ten, cardinality, logical within-row cue-minimax position five, and actual global offset-five correspondence."
  },
  "seeds": {"randomness": "none", "seed_list": [], "determinism": "All identities, orders, splits, fitting, tracing, keys, offsets, and accounting are fixed; two executions must be byte-identical."},
  "budgets": {"base_training_files": 4, "demand_files": 3, "encounter_orders": 2, "stages_per_order": 3, "scheduled_seen_domain_rows": 12, "expected_total_observed_calls": 116, "cell_count": 16, "active_structure_count": 10, "retained_structure_count": 6, "primary_runs": 2, "maximum_source_processes": 1, "timeout_seconds": 1800, "network_access": false, "capacity_growth_events": 0},
  "metrics_and_thresholds": [
    ["training_file_identity_mismatch_count", "==", 0], ["evaluation_file_identity_mismatch_count", "==", 0], ["future_stage_adaptation_access_count", "==", 0], ["second_half_adaptation_access_count", "==", 0], ["valid_stage_count", "==", 6], ["valid_seen_domain_evaluation_count", "==", 12], ["matched_assignment_failure_count", "==", 0], ["capacity_growth_event_count", "==", 0], ["retained_record_integrity_mismatch_count", "==", 0], ["state_partition_mismatch_count", "==", 0],
    ["observed_call_count", "==", 116], ["observed_row_count", "==", 12], ["unique_row_count", "==", 12], ["ten_call_row_count", "==", 10], ["eight_call_row_count", "==", 2], ["other_call_cardinality_row_count", "==", 0], ["aligned_row_start_count", "==", 7], ["drifted_row_start_count", "==", 5], ["logical_hook_aligned_row_count", "==", 7], ["logical_hook_misaligned_row_count", "==", 5], ["unknown_row_count", "==", 0], ["duplicate_row_count", "==", 0], ["missing_row_count", "==", 0], ["call_accounting_mismatch_count", "==", 0], ["sealed071_sign_reproduction_mismatch_count", "==", 0],
    ["order0_row_start_offset_mask", "==", 0], ["order1_row_start_offset_mask", "==", 6710912], ["aligned_row_mask", "==", 127], ["drifted_row_mask", "==", 3968]
  ],
  "controls": [
    "Reuse 044 bytes, identities, orders, splits, learner, gate wrapper, matching, partition, capacity, calls, and blocks unchanged.",
    "Freeze twelve row keys and global indices; aligned/drifted masks use global indices zero through eleven; each order's six offsets are packed as four-bit nibbles in local execution order.",
    "Logical cue-minimax is within-row call index five; the inherited actual hook is any pre-call global count modulo ten equal to five.",
    "Tracing reads only and cannot mutate frames, results, wrapper state, decisions, inputs, or outputs.",
    "Verify sealed 071 byte identity and reproduce sign membership; do not reinterpret benefit, comparator, retention, decision, or validity values."
  ],
  "validity_criteria": [
    "Exact parent, North Star, sealed 071, dependencies, and input identities and sizes match.",
    "Replay completes six stages with identity, access, matching, partition, and capacity controls preserved.",
    "Every call belongs to exactly one row; every scheduled row opens and closes once; row cardinalities sum to the observed total.",
    "Offsets derive only from the monotonic observed global call count and frozen hook definitions.",
    "Two isolated executions are byte-identical; no tokenizer, external model, network, capacity growth, or cross-order state."
  ],
  "classification_rules": {
    "supported": "Validity passes; seven starts/hooks align, five drift/misalign, the two sealed zero rows have eight calls, and the other ten have ten.",
    "mixed": "Validity passes and variable cardinality causes drift or hook misalignment, but counts or membership differ.",
    "null": "Validity passes and all twelve starts and hooks remain aligned.",
    "negative": "Validity passes but offsets contradict global modulo-ten accounting or cardinality contradicts sealed signs.",
    "incomplete": "Both executions or all six stages do not complete.",
    "invalid": "Any identity, provenance, isolation, determinism, trace-site, row-key, schedule, accounting, matching, partition, capacity, finiteness, or qualification criterion fails."
  },
  "stop_conditions": [
    "Stop invalid before interpretation on identity, lineage, dependency, size, source, trace-site, or schedule mismatch.",
    "Stop invalid on forbidden access, incomplete or overlapping attribution, accounting inconsistency, matching failure, partition corruption, capacity growth, non-finite metric, or nondeterminism.",
    "Do not stop early for supported, mixed, null, or negative outcomes.",
    "After any output is observed, do not repair or rerun this identifier."
  ],
  "no_post_result_tuning_rule": "After output, do not alter inputs, identities, orders, splits, learner, gate wrapper, tracing, sites, schedule, encoding, accounting, budgets, metrics, thresholds, validity, classification, or stops under this identifier."
}
