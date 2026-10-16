{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-HOOK-MARGIN-ROLE-ATTRIBUTION-077",
  "program": "DG1 real-byte adaptive granularity",
  "question": "Are experiment 075's four drifted rows with inherited-versus-cue margin differences exactly the four model-fraction-hook rows from experiment 073, with the single check-hook row matching both cue margins?",
  "hypothesis": "All eight margins on the four model-fraction-hook rows will differ, while both margins on the single check-hook row will match exactly; no aligned-row margin will differ.",
  "exact_parent_sha": "f3502675a60905a7301dc28e09cfc4e81c7b1bc5",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-HOOK-MARGIN-DIVERGENCE-ATTRIBUTION-075",
    "classification": "supported-by-frozen-rules",
    "qualification_run_id": "38831771803",
    "result_sha256": "3a0da77df49c6cd8c5c9a8677cab625216a064148e44de832216ec66b494cd00",
    "observation": "Four of five drifted rows and eight drifted margins differed; seven aligned rows matched, no sign changed, and every margin remained nonnegative.",
    "blocked_predecessor": "Experiment 076 froze the same question but produced no output and no scientific claim because its implementation edit was blocked.",
    "continuation_rule": "This non-fresh read-only diagnostic on observed Y/Z/AA may attribute numerical drift only; it cannot establish gate performance, fresh generalization, causal benefit, or a corrected gate."
  },
  "authority": "synthetic research-only diagnostic on immutable repo-owned bytes; no wetware, deployment, external inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": ["research/experiments/exp-dgr-real-utf8-two-block-retain-revert-hook-margin-role-attribution-077.ice", "research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-hook-margin-role-attribution-077.py", ".yggdrasil/qualification-request.json", ".yggdrasil/isolated-run.json"],
  "inputs": {
    "base_training": "Byte-identical four-file set inherited through 029/043/044/075.",
    "demand": "Byte-identical observed Y/Z/AA cohort and Git identities from 044.",
    "orders": [["Y", "Z", "AA"], ["AA", "Z", "Y"]],
    "scheduled_rows": "Twelve frozen rows: each order's stage prefixes of lengths one, two, and three over every seen domain.",
    "role_masks": "Aligned mask 127, check-hook mask 128, and model-fraction-hook mask 3840 are frozen from sealed 073 and reproduced by unchanged tracing.",
    "contamination": "Outcomes, role masks, aggregate margin-difference counts, and signs are observed; only exact row-level association between role and margin difference remains tested."
  },
  "arms": {
    "frozen_replay_control": "Run unchanged 044 gated computation and read inherited early/late margins.",
    "row_local_counterfactual": "Capture frozen cue-role inputs and recompute early/late cue margins exactly as frozen in 074/075, then partition exact differences by sealed hook-role membership."
  },
  "seeds": {"randomness": "none", "seed_list": [], "determinism": "All identities, orders, splits, fitting, tracing, call sites, role masks, margins, and accounting are fixed; two executions must be byte-identical."},
  "budgets": {"base_training_files": 4, "demand_files": 3, "encounter_orders": 2, "stages_per_order": 3, "scheduled_seen_domain_rows": 12, "margins_per_row": 2, "aligned_rows": 7, "check_hook_rows": 1, "model_fraction_hook_rows": 4, "cell_count": 16, "active_structure_count": 10, "retained_structure_count": 6, "primary_runs": 2, "maximum_source_processes": 1, "timeout_seconds": 1800, "network_access": false, "capacity_growth_events": 0},
  "metrics_and_thresholds": [
    ["training_file_identity_mismatch_count", "==", 0], ["evaluation_file_identity_mismatch_count", "==", 0], ["future_stage_adaptation_access_count", "==", 0], ["second_half_adaptation_access_count", "==", 0], ["valid_stage_count", "==", 6], ["valid_seen_domain_evaluation_count", "==", 12], ["matched_assignment_failure_count", "==", 0], ["capacity_growth_event_count", "==", 0], ["retained_record_integrity_mismatch_count", "==", 0], ["state_partition_mismatch_count", "==", 0],
    ["aligned_margin_difference_count", "==", 0], ["check_hook_margin_difference_count", "==", 0], ["model_fraction_hook_margin_difference_count", "==", 8], ["model_fraction_hook_row_difference_count", "==", 4], ["difference_outside_model_fraction_count", "==", 0], ["model_fraction_unchanged_margin_count", "==", 0], ["margin_sign_divergence_count", "==", 0], ["missing_counterfactual_row_count", "==", 0], ["duplicate_counterfactual_row_count", "==", 0], ["role_partition_mismatch_count", "==", 0], ["margin_accounting_mismatch_count", "==", 0], ["sealed075_aggregate_reproduction_mismatch_count", "==", 0], ["aligned_row_mask", "==", 127], ["check_hook_row_mask", "==", 128], ["model_fraction_hook_row_mask", "==", 3840], ["margin_difference_row_mask", "==", 3840]
  ],
  "controls": [
    "Reuse 044 bytes, identities, orders, splits, learner, gate wrapper, matching, partition, capacity, calls, and blocks unchanged.",
    "Freeze twelve row keys, indices zero through eleven, cue caller lines 330/333, aligned mask 127, check mask 128, and model-fraction mask 3840 from sealed 073/075.",
    "Use the unwrapped resource-pressure model_correct_counts only for counterfactual scoring; split each permitted cue at floor length over two and reset independently for early and late blocks exactly as 075.",
    "Compare integer margins exactly and partition differences by the frozen disjoint role masks without tolerance, mutation, or replacement.",
    "Verify sealed 075 byte identity and reproduce its aggregate counts, masks, all-retain decisions, and zero sign divergence; do not reinterpret benefit, retention, validity, or untouched-second-half outcomes."
  ],
  "validity_criteria": [
    "Exact parent, North Star, sealed 075, dependencies, and input identities and sizes match.",
    "Replay completes six stages with identity, access, matching, partition, and capacity controls preserved.",
    "Every scheduled row supplies exactly one inherited pair and one counterfactual pair; role masks are exhaustive and disjoint and reproduce sealed 073 membership.",
    "Integer margin, sign, difference, row-mask, and role-partition accounting is complete and reproduces sealed 075 aggregates.",
    "Two isolated executions are byte-identical; no tokenizer, external model, network, capacity growth, or cross-order state."
  ],
  "classification_rules": {
    "supported": "Validity passes; all eight model-fraction-hook margins differ, the check-hook and aligned margins match, and no sign differs.",
    "mixed": "Validity passes and differences are confined to model-fraction-hook rows, but fewer than all eight model-fraction margins differ.",
    "null": "Validity passes and all twenty-four inherited margins equal their counterfactual margins.",
    "negative": "Validity passes but any check-hook or aligned margin differs, or any difference occurs outside model-fraction-hook membership.",
    "incomplete": "Both executions, all six stages, all twelve rows, or all twenty-four paired margins do not complete.",
    "invalid": "Any identity, provenance, isolation, determinism, trace-site, row-key, cue-block, role-mask, integer-margin, accounting, matching, partition, capacity, finiteness, or qualification criterion fails."
  },
  "stop_conditions": [
    "Stop invalid before interpretation on identity, lineage, dependency, size, source, trace-site, role-mask, or schedule mismatch.",
    "Stop invalid on forbidden access, missing or duplicate row data, empty cue block, non-integer margin, accounting inconsistency, matching failure, partition corruption, capacity growth, non-finite metric, or nondeterminism.",
    "Do not stop early for supported, mixed, null, or negative outcomes.",
    "After any output is observed, do not repair or rerun this identifier."
  ],
  "no_post_result_tuning_rule": "After output, do not alter inputs, identities, orders, splits, learner, gate wrapper, tracing, sites, roles, masks, margin definitions, scoring, accounting, budgets, metrics, thresholds, validity, classification, or stops under this identifier."
}
