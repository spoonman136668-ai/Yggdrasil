{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-HOOK-MARGIN-BLOCK-DIRECTION-ATTRIBUTION-080",
  "program": "DG1 real-byte adaptive granularity",
  "question": "Do all four asymmetric model-fraction-hook rows from experiment 079 have a more-negative inherited-minus-cue delta in the early block than in the late block, rather than mixed within-row directions?",
  "hypothesis": "Every model-fraction-hook row will have an early delta strictly below its late delta; the four signed early-minus-late asymmetries will sum to -22, while all eight deltas remain negative, aligned and check-hook margins remain exactly equal, and every margin remains nonnegative.",
  "exact_parent_sha": "00477a0e38453b1b73e8cb7459cff1b50c45ef73",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-HOOK-MARGIN-BLOCK-SYMMETRY-ATTRIBUTION-079",
    "classification": "negative-by-frozen-rules",
    "qualification_run_id": "38863421249",
    "result_sha256": "7e7ece10041c94e46d1f134c3a9dd8d9e1b9e71ba7fd3aebee42b58dbf08fb5f",
    "observation": "All four model-fraction-hook rows were asymmetric; early and late absolute delta sums were 41 and 19, within-row absolute asymmetry summed to 22, all eight deltas were negative, aligned and check-hook margins matched, and every margin remained nonnegative. Per-row asymmetry direction was not emitted.",
    "continuation_rule": "This non-fresh read-only diagnostic on observed Y/Z/AA may localize sealed numerical drift across blocks only; it cannot establish gate performance, fresh generalization, causal benefit, or a corrected gate."
  },
  "authority": "synthetic research-only diagnostic on immutable repo-owned bytes; no wetware, deployment, external inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": ["research/experiments/exp-dgr-real-utf8-two-block-retain-revert-hook-margin-block-direction-attribution-080.ice", "research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-hook-margin-block-direction-attribution-080.py", ".yggdrasil/qualification-request.json", ".yggdrasil/isolated-run.json"],
  "inputs": {
    "base_training": "Byte-identical four-file set inherited through 029/043/044/079.",
    "demand": "Byte-identical observed Y/Z/AA cohort and Git identities from 044.",
    "orders": [["Y", "Z", "AA"], ["AA", "Z", "Y"]],
    "scheduled_rows": "Twelve frozen rows: each order's stage prefixes of lengths one, two, and three over every seen domain.",
    "direction_definition": "For each frozen model-fraction row, signed block asymmetry is the exact integer early inherited-minus-cue delta minus the late inherited-minus-cue delta; negative means early is more negative, positive means late is more negative, and zero means symmetric.",
    "contamination": "Outcomes, role masks, all four asymmetric rows, all eight negative deltas, block absolute sums 41 and 19, and total absolute asymmetry 22 are observed; only the four within-row signed directions and their signed allocation remain tested."
  },
  "arms": {
    "frozen_replay_control": "Run unchanged 044 gated computation and read inherited early/late margins.",
    "row_local_counterfactual": "Capture frozen cue-role inputs and recompute early/late cue margins exactly as frozen in 074/075/077/078/079, then compare signed paired deltas within the sealed model-fraction role."
  },
  "seeds": {"randomness": "none", "seed_list": [], "determinism": "All identities, orders, splits, fitting, tracing, call sites, role masks, margins, block pairing, signed direction definitions, and accounting are fixed; two executions must be byte-identical."},
  "budgets": {"base_training_files": 4, "demand_files": 3, "encounter_orders": 2, "stages_per_order": 3, "scheduled_seen_domain_rows": 12, "margins_per_row": 2, "aligned_rows": 7, "check_hook_rows": 1, "model_fraction_hook_rows": 4, "known_asymmetric_model_fraction_rows": 4, "known_early_absolute_delta_sum": 41, "known_late_absolute_delta_sum": 19, "known_within_row_asymmetry_absolute_sum": 22, "cell_count": 16, "active_structure_count": 10, "retained_structure_count": 6, "primary_runs": 2, "maximum_source_processes": 1, "timeout_seconds": 1800, "network_access": false, "capacity_growth_events": 0},
  "metrics_and_thresholds": [
    ["training_file_identity_mismatch_count", "==", 0], ["evaluation_file_identity_mismatch_count", "==", 0], ["future_stage_adaptation_access_count", "==", 0], ["second_half_adaptation_access_count", "==", 0], ["valid_stage_count", "==", 6], ["valid_seen_domain_evaluation_count", "==", 12], ["matched_assignment_failure_count", "==", 0], ["capacity_growth_event_count", "==", 0], ["retained_record_integrity_mismatch_count", "==", 0], ["state_partition_mismatch_count", "==", 0],
    ["aligned_margin_difference_count", "==", 0], ["check_hook_margin_difference_count", "==", 0], ["model_fraction_negative_delta_count", "==", 8], ["model_fraction_nonnegative_delta_count", "==", 0], ["model_fraction_early_more_negative_row_count", ">=", 0], ["model_fraction_late_more_negative_row_count", ">=", 0], ["model_fraction_equal_block_row_count", "==", 0], ["model_fraction_direction_accounted_count", "==", 4], ["model_fraction_signed_asymmetry_sum", ">=", -22], ["model_fraction_signed_asymmetry_sum", "<=", 22], ["model_fraction_asymmetry_absolute_sum", "==", 22], ["model_fraction_early_absolute_delta_sum", "==", 41], ["model_fraction_late_absolute_delta_sum", "==", 19], ["model_fraction_absolute_delta_sum", "==", 60], ["model_fraction_signed_delta_sum", "==", -60], ["inherited_negative_margin_count", "==", 0], ["counterfactual_negative_margin_count", "==", 0], ["margin_sign_divergence_count", "==", 0], ["missing_counterfactual_row_count", "==", 0], ["duplicate_counterfactual_row_count", "==", 0], ["role_partition_mismatch_count", "==", 0], ["block_direction_accounting_mismatch_count", "==", 0], ["sealed079_reproduction_mismatch_count", "==", 0], ["aligned_row_mask", "==", 127], ["check_hook_row_mask", "==", 128], ["model_fraction_hook_row_mask", "==", 3840], ["early_more_negative_row_mask", ">=", 0], ["late_more_negative_row_mask", ">=", 0]
  ],
  "controls": [
    "Reuse 044 bytes, identities, orders, splits, learner, gate wrapper, matching, partition, capacity, calls, and blocks unchanged.",
    "Freeze twelve row keys, indices zero through eleven, cue caller lines 330/333, aligned mask 127, check-hook mask 128, and model-fraction-hook mask 3840 from sealed 073/077/078/079.",
    "Use the unwrapped resource-pressure model_correct_counts only for counterfactual scoring; split each permitted cue at floor length over two and reset independently for early and late blocks exactly as 075/077/078/079.",
    "Compare integer margins, deltas, and signed early-minus-late asymmetries exactly within each frozen row without tolerance, normalization, mutation, replacement, aggregation-driven reassignment, or per-row thresholding.",
    "Verify sealed 079 byte identity and reproduce its role masks, four asymmetric rows, eight negative directions, early/late absolute sums 41/19, -60 signed delta sum, 60 absolute delta sum, 22 absolute asymmetry sum, zero sign divergence, and nonnegative margins; do not reinterpret benefit, retention, validity, or untouched-second-half outcomes."
  ],
  "validity_criteria": [
    "Exact parent, North Star, sealed 079, dependencies, and input identities and sizes match.",
    "Replay completes six stages with identity, access, matching, partition, and capacity controls preserved.",
    "Every scheduled row supplies exactly one inherited pair and one counterfactual pair; role masks are exhaustive and disjoint and reproduce sealed membership.",
    "All margins, deltas, and signed asymmetries are exact integers; direction counts, masks, signed and absolute sums, blockwise sums, role partition, and sealed-079 reproduction account completely for all twenty-four pairs and four model-fraction row pairs.",
    "Two isolated executions are byte-identical; no tokenizer, external model, network, capacity growth, or cross-order state."
  ],
  "classification_rules": {
    "supported": "Validity passes; all four model-fraction-hook rows have early deltas strictly below late deltas; their signed asymmetries sum to -22; all eight deltas remain negative; aligned and check-hook margins match; and all margins remain nonnegative.",
    "mixed": "Validity passes; one to three model-fraction-hook rows have early deltas below late deltas and at least one has a late delta below its early delta, while no row is equal and sealed aggregates reproduce.",
    "null": "Validity passes and all four model-fraction-hook rows have late deltas strictly below early deltas, with signed asymmetries summing to 22.",
    "negative": "Validity passes but any model-fraction row becomes block-equal, any aligned or check-hook margin differs, any model-fraction delta is nonnegative, any sealed aggregate fails to reproduce, or any inherited or counterfactual margin becomes negative.",
    "incomplete": "Both executions, all six stages, all twelve rows, all twenty-four paired margins, or all four model-fraction block directions do not complete.",
    "invalid": "Any identity, provenance, isolation, determinism, trace-site, row-key, cue-block, role-mask, integer-margin, block-direction, accounting, matching, partition, capacity, finiteness, or qualification criterion fails."
  },
  "stop_conditions": [
    "Stop invalid before interpretation on identity, lineage, dependency, size, source, trace-site, role-mask, or schedule mismatch.",
    "Stop invalid on forbidden access, missing or duplicate row data, empty cue block, non-integer margin, delta, or asymmetry, accounting inconsistency, matching failure, partition corruption, capacity growth, non-finite metric, or nondeterminism.",
    "Do not stop early for supported, mixed, null, or negative outcomes.",
    "After any output is observed, do not repair or rerun this identifier."
  ],
  "no_post_result_tuning_rule": "After output, do not alter inputs, identities, orders, splits, learner, gate wrapper, tracing, sites, roles, masks, margin, delta, block-pair, signed-direction definitions, scoring, accounting, budgets, metrics, thresholds, validity, classification, or stops under this identifier."
}
