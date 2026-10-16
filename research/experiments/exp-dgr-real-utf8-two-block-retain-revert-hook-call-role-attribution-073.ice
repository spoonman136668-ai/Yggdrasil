{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-HOOK-CALL-ROLE-ATTRIBUTION-073",
  "program": "DG1 real-byte adaptive granularity",
  "question": "Which logical call roles receive experiment 043's global offset-four capture and offset-five decision hooks across the five drifted rows established by experiment 072?",
  "hypothesis": "The unchanged 044 replay will assign both hooks to cue_frozen/cue_minimax on seven aligned rows, to check_frozen/check_minimax on the single start-offset-eight row, and to model_fraction_full/model_fraction_active on the four start-offset-six rows, with no other hook roles.",
  "exact_parent_sha": "ab494dd6a41c1082899161bbab5a2d039b9e4348",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-ROW-OFFSET-DRIFT-ATTRIBUTION-072",
    "classification": "supported-by-frozen-rules",
    "qualification_run_id": "38822951064",
    "result_sha256": "446a5b293997f0c6f201bc6ff106a83246b0abd94847e434081df41126048ecb",
    "observation": "Seven row starts are aligned and five drift; order 1's six start offsets are 0, 8, 6, 6, 6, 6, while ten rows have ten calls and two have eight.",
    "continuation_rule": "This is a non-fresh read-only diagnostic on observed Y/Z/AA and cannot establish gate performance, fresh generalization, causal benefit, or a corrected gate."
  },
  "authority": "synthetic research-only diagnostic on immutable repo-owned bytes; no wetware, deployment, external inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": ["research/experiments/exp-dgr-real-utf8-two-block-retain-revert-hook-call-role-attribution-073.ice", "research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-hook-call-role-attribution-073.py", ".yggdrasil/qualification-request.json", ".yggdrasil/isolated-run.json"],
  "inputs": {
    "base_training": "Byte-identical four-file set inherited through 029/043/044/072.",
    "demand": "Byte-identical observed Y/Z/AA cohort and Git identities from 044.",
    "orders": [["Y", "Z", "AA"], ["AA", "Z", "Y"]],
    "scheduled_rows": "Twelve frozen rows: each order's stage prefixes of lengths one, two, and three over every seen domain.",
    "logical_roles": "Eight direct roles in frozen source order: evaluation_frozen, evaluation_independent, evaluation_pooled, evaluation_minimax, cue_frozen, cue_minimax, check_frozen, check_minimax; positive-increment rows then have model_fraction_full and model_fraction_active.",
    "contamination": "Outcomes, row cardinalities, signs, offsets, and aligned membership are observed; only exact hook-to-logical-role attribution remains tested."
  },
  "arms": {
    "frozen_replay_control": "Run unchanged 044 gated computation.",
    "hook_role_attribution": "Read-only trace each model_correct_counts entry, attribute its logical role from the immediate frozen call site, and record roles at global pre-call offsets four and five modulo ten for each frozen row."
  },
  "seeds": {"randomness": "none", "seed_list": [], "determinism": "All identities, orders, splits, fitting, tracing, call sites, keys, offsets, and accounting are fixed; two executions must be byte-identical."},
  "budgets": {"base_training_files": 4, "demand_files": 3, "encounter_orders": 2, "stages_per_order": 3, "scheduled_seen_domain_rows": 12, "expected_total_observed_calls": 116, "expected_capture_hooks": 12, "expected_decision_hooks": 12, "cell_count": 16, "active_structure_count": 10, "retained_structure_count": 6, "primary_runs": 2, "maximum_source_processes": 1, "timeout_seconds": 1800, "network_access": false, "capacity_growth_events": 0},
  "metrics_and_thresholds": [
    ["training_file_identity_mismatch_count", "==", 0], ["evaluation_file_identity_mismatch_count", "==", 0], ["future_stage_adaptation_access_count", "==", 0], ["second_half_adaptation_access_count", "==", 0], ["valid_stage_count", "==", 6], ["valid_seen_domain_evaluation_count", "==", 12], ["matched_assignment_failure_count", "==", 0], ["capacity_growth_event_count", "==", 0], ["retained_record_integrity_mismatch_count", "==", 0], ["state_partition_mismatch_count", "==", 0],
    ["observed_call_count", "==", 116], ["capture_hook_count", "==", 12], ["decision_hook_count", "==", 12], ["capture_cue_frozen_count", "==", 7], ["decision_cue_minimax_count", "==", 7], ["capture_check_frozen_count", "==", 1], ["decision_check_minimax_count", "==", 1], ["capture_model_fraction_full_count", "==", 4], ["decision_model_fraction_active_count", "==", 4], ["other_capture_role_count", "==", 0], ["other_decision_role_count", "==", 0], ["unknown_call_role_count", "==", 0], ["duplicate_hook_row_count", "==", 0], ["missing_capture_row_count", "==", 0], ["missing_decision_row_count", "==", 0], ["hook_accounting_mismatch_count", "==", 0], ["sealed072_offset_reproduction_mismatch_count", "==", 0],
    ["aligned_decision_row_mask", "==", 127], ["check_decision_row_mask", "==", 128], ["model_fraction_decision_row_mask", "==", 3840]
  ],
  "controls": [
    "Reuse 044 bytes, identities, orders, splits, learner, gate wrapper, matching, partition, capacity, calls, and blocks unchanged.",
    "Freeze the twelve row keys, global indices zero through eleven, role labels, direct caller lines 303/306/309/312/330/333/337/340 in experiment 029, and paired caller lines 39/40 in error-guided-wake-005.",
    "Capture means global pre-call count modulo ten equals four; decision means it equals five; each hook is attributed to exactly one logical role and row.",
    "Verify sealed 072 byte identity and reproduce its call total, row start offsets, and aligned/drifted masks; do not reinterpret benefit, comparator, retention, decision, or validity values."
  ],
  "validity_criteria": [
    "Exact parent, North Star, sealed 072, dependencies, and input identities and sizes match.",
    "Replay completes six stages with identity, access, matching, partition, and capacity controls preserved.",
    "Every observed call maps to exactly one frozen row and logical role; every row receives exactly one capture and one decision hook; hook and role categories are exhaustive and disjoint.",
    "Offsets derive only from monotonic observed global call count and exactly reproduce sealed 072.",
    "Two isolated executions are byte-identical; no tokenizer, external model, network, capacity growth, or cross-order state."
  ],
  "classification_rules": {
    "supported": "Validity passes; hooks map 7/1/4 respectively to cue, check, and model_fraction role pairs exactly as hypothesized.",
    "mixed": "Validity passes and all hooks map to known roles, but the role counts or row membership differ.",
    "null": "Validity passes and all twelve hooks map to the intended cue role pair.",
    "negative": "Validity passes but any hook maps outside the three hypothesized role pairs or capture/decision pairing is inconsistent.",
    "incomplete": "Both executions or all six stages do not complete.",
    "invalid": "Any identity, provenance, isolation, determinism, trace-site, caller-role, row-key, schedule, accounting, matching, partition, capacity, finiteness, or qualification criterion fails."
  },
  "stop_conditions": [
    "Stop invalid before interpretation on identity, lineage, dependency, size, source, trace-site, caller-role, or schedule mismatch.",
    "Stop invalid on forbidden access, incomplete or overlapping attribution, accounting inconsistency, matching failure, partition corruption, capacity growth, non-finite metric, or nondeterminism.",
    "Do not stop early for supported, mixed, null, or negative outcomes.",
    "After any output is observed, do not repair or rerun this identifier."
  ],
  "no_post_result_tuning_rule": "After output, do not alter inputs, identities, orders, splits, learner, gate wrapper, tracing, sites, roles, schedule, encoding, accounting, budgets, metrics, thresholds, validity, classification, or stops under this identifier."
}
