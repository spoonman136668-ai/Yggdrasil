{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-HOOK-MARGIN-DIRECTION-ATTRIBUTION-078",
  "program": "DG1 real-byte adaptive granularity",
  "question": "Do experiment 077's eight model-fraction-hook margin differences include both upward and downward inherited-minus-cue shifts, rather than a uniform directional bias?",
  "hypothesis": "Among the eight differing model-fraction-hook margins, at least one inherited margin will exceed its row-local cue margin and at least one will be lower; the check-hook and aligned margins will remain exactly equal and every margin will remain nonnegative.",
  "exact_parent_sha": "b6ef7f37e7bfe47c0a4e50fa4ba9637207625927",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-HOOK-MARGIN-ROLE-ATTRIBUTION-077",
    "classification": "supported-by-frozen-rules",
    "qualification_run_id": "38833999147",
    "result_sha256": "71eff907b74cbec49ab20ef06374303f9b0f29237f6dde9243628233167ab127",
    "observation": "Exactly eight margins on four model-fraction-hook rows differed; all aligned and check-hook margins matched, no sign diverged, and every margin remained nonnegative. Difference direction and magnitude were not emitted.",
    "continuation_rule": "This non-fresh read-only diagnostic on observed Y/Z/AA may attribute numerical drift direction only; it cannot establish gate performance, fresh generalization, causal benefit, or a corrected gate."
  },
  "authority": "synthetic research-only diagnostic on immutable repo-owned bytes; no wetware, deployment, external inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": ["research/experiments/exp-dgr-real-utf8-two-block-retain-revert-hook-margin-direction-attribution-078.ice", "research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-hook-margin-direction-attribution-078.py", ".yggdrasil/qualification-request.json", ".yggdrasil/isolated-run.json"],
  "inputs": {
    "base_training": "Byte-identical four-file set inherited through 029/043/044/077.",
    "demand": "Byte-identical observed Y/Z/AA cohort and Git identities from 044.",
    "orders": [["Y", "Z", "AA"], ["AA", "Z", "Y"]],
    "scheduled_rows": "Twelve frozen rows: each order's stage prefixes of lengths one, two, and three over every seen domain.",
    "direction_definition": "For each early and late paired margin, direction is the exact integer sign of inherited margin minus row-local cue margin; positive means inherited is higher and negative means inherited is lower.",
    "contamination": "Outcomes, role masks, differing-row membership, difference count, and nonnegative signs are observed; only exact difference direction and aggregate magnitude remain tested."
  },
  "arms": {
    "frozen_replay_control": "Run unchanged 044 gated computation and read inherited early/late margins.",
    "row_local_counterfactual": "Capture frozen cue-role inputs and recompute early/late cue margins exactly as frozen in 074/075/077, then compare exact integer direction within the sealed role partition."
  },
  "seeds": {"randomness": "none", "seed_list": [], "determinism": "All identities, orders, splits, fitting, tracing, call sites, role masks, margins, direction definitions, and accounting are fixed; two executions must be byte-identical."},
  "budgets": {"base_training_files": 4, "demand_files": 3, "encounter_orders": 2, "stages_per_order": 3, "scheduled_seen_domain_rows": 12, "margins_per_row": 2, "aligned_rows": 7, "check_hook_rows": 1, "model_fraction_hook_rows": 4, "known_differing_margins": 8, "cell_count": 16, "active_structure_count": 10, "retained_structure_count": 6, "primary_runs": 2, "maximum_source_processes": 1, "timeout_seconds": 1800, "network_access": false, "capacity_growth_events": 0},
  "metrics_and_thresholds": [
    ["training_file_identity_mismatch_count", "==", 0], ["evaluation_file_identity_mismatch_count", "==", 0], ["future_stage_adaptation_access_count", "==", 0], ["second_half_adaptation_access_count", "==", 0], ["valid_stage_count", "==", 6], ["valid_seen_domain_evaluation_count", "==", 12], ["matched_assignment_failure_count", "==", 0], ["capacity_growth_event_count", "==", 0], ["retained_record_integrity_mismatch_count", "==", 0], ["state_partition_mismatch_count", "==", 0],
    ["aligned_margin_difference_count", "==", 0], ["check_hook_margin_difference_count", "==", 0], ["model_fraction_higher_inherited_count", ">=", 1], ["model_fraction_lower_inherited_count", ">=", 1], ["model_fraction_equal_margin_count", "==", 0], ["model_fraction_direction_accounted_count", "==", 8], ["model_fraction_absolute_delta_sum", ">=", 8], ["model_fraction_signed_delta_sum", ">=", -1000000000], ["inherited_negative_margin_count", "==", 0], ["counterfactual_negative_margin_count", "==", 0], ["margin_sign_divergence_count", "==", 0], ["missing_counterfactual_row_count", "==", 0], ["duplicate_counterfactual_row_count", "==", 0], ["role_partition_mismatch_count", "==", 0], ["direction_accounting_mismatch_count", "==", 0], ["sealed077_reproduction_mismatch_count", "==", 0], ["aligned_row_mask", "==", 127], ["check_hook_row_mask", "==", 128], ["model_fraction_hook_row_mask", "==", 3840], ["higher_inherited_row_mask", ">=", 0], ["lower_inherited_row_mask", ">=", 0]
  ],
  "controls": [
    "Reuse 044 bytes, identities, orders, splits, learner, gate wrapper, matching, partition, capacity, calls, and blocks unchanged.",
    "Freeze twelve row keys, indices zero through eleven, cue caller lines 330/333, aligned mask 127, check-hook mask 128, and model-fraction-hook mask 3840 from sealed 073/077.",
    "Use the unwrapped resource-pressure model_correct_counts only for counterfactual scoring; split each permitted cue at floor length over two and reset independently for early and late blocks exactly as 075/077.",
    "Compare integer margins exactly; compute delta as inherited minus counterfactual without tolerance, normalization, mutation, replacement, or per-row thresholding.",
    "Verify sealed 077 byte identity and reproduce its role-specific difference counts, masks, zero sign divergence, and nonnegative margins; do not reinterpret benefit, retention, validity, or untouched-second-half outcomes."
  ],
  "validity_criteria": [
    "Exact parent, North Star, sealed 077, dependencies, and input identities and sizes match.",
    "Replay completes six stages with identity, access, matching, partition, and capacity controls preserved.",
    "Every scheduled row supplies exactly one inherited pair and one counterfactual pair; role masks are exhaustive and disjoint and reproduce sealed 073/077 membership.",
    "All margins and deltas are exact integers; direction counts, masks, signed sum, absolute sum, role partition, and sealed-077 reproduction account completely for all twenty-four pairs.",
    "Two isolated executions are byte-identical; no tokenizer, external model, network, capacity growth, or cross-order state."
  ],
  "classification_rules": {
    "supported": "Validity passes; at least one of the eight model-fraction-hook deltas is positive and at least one is negative; aligned and check-hook margins match; and all margins remain nonnegative.",
    "mixed": "Validity passes; all eight model-fraction-hook margins differ and remain nonnegative, but every delta has the same direction.",
    "null": "Validity passes and all twenty-four inherited margins equal their counterfactual margins.",
    "negative": "Validity passes but any aligned or check-hook margin differs, any model-fraction margin unexpectedly equals, or any inherited or counterfactual margin becomes negative.",
    "incomplete": "Both executions, all six stages, all twelve rows, or all twenty-four paired margins do not complete.",
    "invalid": "Any identity, provenance, isolation, determinism, trace-site, row-key, cue-block, role-mask, integer-margin, direction, accounting, matching, partition, capacity, finiteness, or qualification criterion fails."
  },
  "stop_conditions": [
    "Stop invalid before interpretation on identity, lineage, dependency, size, source, trace-site, role-mask, or schedule mismatch.",
    "Stop invalid on forbidden access, missing or duplicate row data, empty cue block, non-integer margin or delta, accounting inconsistency, matching failure, partition corruption, capacity growth, non-finite metric, or nondeterminism.",
    "Do not stop early for supported, mixed, null, or negative outcomes.",
    "After any output is observed, do not repair or rerun this identifier."
  ],
  "no_post_result_tuning_rule": "After output, do not alter inputs, identities, orders, splits, learner, gate wrapper, tracing, sites, roles, masks, margin or direction definitions, scoring, accounting, budgets, metrics, thresholds, validity, classification, or stops under this identifier."
}
