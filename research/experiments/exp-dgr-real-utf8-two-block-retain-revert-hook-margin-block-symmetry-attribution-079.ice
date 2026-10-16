{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-HOOK-MARGIN-BLOCK-SYMMETRY-ATTRIBUTION-079",
  "program": "DG1 real-byte adaptive granularity",
  "question": "Is experiment 078's 60-point downward inherited-minus-cue margin drift block-symmetric within each of the four model-fraction-hook rows, rather than concentrated differently between early and late blocks?",
  "hypothesis": "For every model-fraction-hook row, the exact inherited-minus-cue early delta will equal its late delta; all eight deltas will remain negative, while check-hook and aligned margins remain exactly equal and every margin remains nonnegative.",
  "exact_parent_sha": "c7cdf8938e4868fe0408ef3c1ba632c3cd1c36ac",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-HOOK-MARGIN-DIRECTION-ATTRIBUTION-078",
    "classification": "mixed-by-frozen-rules",
    "qualification_run_id": "38861290262",
    "result_sha256": "d8cc08cb52b7e3260be697bde11143fac900a0936073399f8f97d77f664048ac",
    "observation": "All eight model-fraction-hook inherited-minus-cue deltas were negative, with signed and absolute sums of -60 and 60; aligned and check-hook margins matched, no sign diverged, and all margins remained nonnegative. Per-row early-versus-late delta symmetry was not emitted.",
    "continuation_rule": "This non-fresh read-only diagnostic on observed Y/Z/AA may localize the sealed numerical drift across blocks only; it cannot establish gate performance, fresh generalization, causal benefit, or a corrected gate."
  },
  "authority": "synthetic research-only diagnostic on immutable repo-owned bytes; no wetware, deployment, external inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": ["research/experiments/exp-dgr-real-utf8-two-block-retain-revert-hook-margin-block-symmetry-attribution-079.ice", "research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-hook-margin-block-symmetry-attribution-079.py", ".yggdrasil/qualification-request.json", ".yggdrasil/isolated-run.json"],
  "inputs": {
    "base_training": "Byte-identical four-file set inherited through 029/043/044/078.",
    "demand": "Byte-identical observed Y/Z/AA cohort and Git identities from 044.",
    "orders": [["Y", "Z", "AA"], ["AA", "Z", "Y"]],
    "scheduled_rows": "Twelve frozen rows: each order's stage prefixes of lengths one, two, and three over every seen domain.",
    "block_pair_definition": "Within each frozen row, pair block index zero (early) with block index one (late); block asymmetry is the exact integer early delta minus late delta, where each delta is inherited margin minus row-local cue margin.",
    "contamination": "Outcomes, role masks, differing-row membership, all eight negative directions, and aggregate magnitude 60 are observed; only within-row early/late equality and blockwise allocation remain tested."
  },
  "arms": {
    "frozen_replay_control": "Run unchanged 044 gated computation and read inherited early/late margins.",
    "row_local_counterfactual": "Capture frozen cue-role inputs and recompute early/late cue margins exactly as frozen in 074/075/077/078, then compare paired deltas within the sealed role partition."
  },
  "seeds": {"randomness": "none", "seed_list": [], "determinism": "All identities, orders, splits, fitting, tracing, call sites, role masks, margins, block pairing, symmetry definitions, and accounting are fixed; two executions must be byte-identical."},
  "budgets": {"base_training_files": 4, "demand_files": 3, "encounter_orders": 2, "stages_per_order": 3, "scheduled_seen_domain_rows": 12, "margins_per_row": 2, "aligned_rows": 7, "check_hook_rows": 1, "model_fraction_hook_rows": 4, "known_differing_margins": 8, "known_absolute_delta_sum": 60, "cell_count": 16, "active_structure_count": 10, "retained_structure_count": 6, "primary_runs": 2, "maximum_source_processes": 1, "timeout_seconds": 1800, "network_access": false, "capacity_growth_events": 0},
  "metrics_and_thresholds": [
    ["training_file_identity_mismatch_count", "==", 0], ["evaluation_file_identity_mismatch_count", "==", 0], ["future_stage_adaptation_access_count", "==", 0], ["second_half_adaptation_access_count", "==", 0], ["valid_stage_count", "==", 6], ["valid_seen_domain_evaluation_count", "==", 12], ["matched_assignment_failure_count", "==", 0], ["capacity_growth_event_count", "==", 0], ["retained_record_integrity_mismatch_count", "==", 0], ["state_partition_mismatch_count", "==", 0],
    ["aligned_margin_difference_count", "==", 0], ["check_hook_margin_difference_count", "==", 0], ["model_fraction_negative_delta_count", "==", 8], ["model_fraction_nonnegative_delta_count", "==", 0], ["model_fraction_symmetric_row_count", ">=", 0], ["model_fraction_asymmetric_row_count", ">=", 0], ["model_fraction_pair_accounted_count", "==", 4], ["model_fraction_early_absolute_delta_sum", ">=", 0], ["model_fraction_late_absolute_delta_sum", ">=", 0], ["model_fraction_block_absolute_sum_difference", ">=", 0], ["model_fraction_within_row_asymmetry_absolute_sum", ">=", 0], ["model_fraction_absolute_delta_sum", "==", 60], ["model_fraction_signed_delta_sum", "==", -60], ["inherited_negative_margin_count", "==", 0], ["counterfactual_negative_margin_count", "==", 0], ["margin_sign_divergence_count", "==", 0], ["missing_counterfactual_row_count", "==", 0], ["duplicate_counterfactual_row_count", "==", 0], ["role_partition_mismatch_count", "==", 0], ["block_pair_accounting_mismatch_count", "==", 0], ["sealed078_reproduction_mismatch_count", "==", 0], ["aligned_row_mask", "==", 127], ["check_hook_row_mask", "==", 128], ["model_fraction_hook_row_mask", "==", 3840], ["symmetric_model_fraction_row_mask", ">=", 0], ["asymmetric_model_fraction_row_mask", ">=", 0]
  ],
  "controls": [
    "Reuse 044 bytes, identities, orders, splits, learner, gate wrapper, matching, partition, capacity, calls, and blocks unchanged.",
    "Freeze twelve row keys, indices zero through eleven, cue caller lines 330/333, aligned mask 127, check-hook mask 128, and model-fraction-hook mask 3840 from sealed 073/077/078.",
    "Use the unwrapped resource-pressure model_correct_counts only for counterfactual scoring; split each permitted cue at floor length over two and reset independently for early and late blocks exactly as 075/077/078.",
    "Compare integer margins and deltas exactly; pair early and late only within the same frozen row without tolerance, normalization, mutation, replacement, aggregation-driven reassignment, or per-row thresholding.",
    "Verify sealed 078 byte identity and reproduce its role-specific difference counts, masks, eight negative directions, -60 signed sum, 60 absolute sum, zero sign divergence, and nonnegative margins; do not reinterpret benefit, retention, validity, or untouched-second-half outcomes."
  ],
  "validity_criteria": [
    "Exact parent, North Star, sealed 078, dependencies, and input identities and sizes match.",
    "Replay completes six stages with identity, access, matching, partition, and capacity controls preserved.",
    "Every scheduled row supplies exactly one inherited pair and one counterfactual pair; role masks are exhaustive and disjoint and reproduce sealed 073/077/078 membership.",
    "All margins, deltas, and within-row asymmetries are exact integers; symmetry counts, masks, blockwise sums, signed sum, absolute sum, role partition, and sealed-078 reproduction account completely for all twenty-four pairs and four model-fraction row pairs.",
    "Two isolated executions are byte-identical; no tokenizer, external model, network, capacity growth, or cross-order state."
  ],
  "classification_rules": {
    "supported": "Validity passes; all four model-fraction-hook rows have exactly equal early and late deltas; all eight deltas remain negative; aligned and check-hook margins match; and all margins remain nonnegative.",
    "mixed": "Validity passes; all eight model-fraction-hook deltas remain negative and reproduce aggregate magnitude 60, but one to three of the four rows have unequal early and late deltas.",
    "null": "Validity passes and none of the four model-fraction-hook rows has equal early and late deltas.",
    "negative": "Validity passes but any aligned or check-hook margin differs, any model-fraction delta is nonnegative, aggregate signed or absolute magnitude differs from -60/60, or any inherited or counterfactual margin becomes negative.",
    "incomplete": "Both executions, all six stages, all twelve rows, all twenty-four paired margins, or all four model-fraction block pairs do not complete.",
    "invalid": "Any identity, provenance, isolation, determinism, trace-site, row-key, cue-block, role-mask, integer-margin, block-pair, symmetry, accounting, matching, partition, capacity, finiteness, or qualification criterion fails."
  },
  "stop_conditions": [
    "Stop invalid before interpretation on identity, lineage, dependency, size, source, trace-site, role-mask, or schedule mismatch.",
    "Stop invalid on forbidden access, missing or duplicate row data, empty cue block, non-integer margin, delta, or asymmetry, accounting inconsistency, matching failure, partition corruption, capacity growth, non-finite metric, or nondeterminism.",
    "Do not stop early for supported, mixed, null, or negative outcomes.",
    "After any output is observed, do not repair or rerun this identifier."
  ],
  "no_post_result_tuning_rule": "After output, do not alter inputs, identities, orders, splits, learner, gate wrapper, tracing, sites, roles, masks, margin, delta, block-pair, or symmetry definitions, scoring, accounting, budgets, metrics, thresholds, validity, classification, or stops under this identifier."
}
