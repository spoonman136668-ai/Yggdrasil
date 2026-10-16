{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-HOOK-DECISION-DIVERGENCE-ATTRIBUTION-074",
  "program": "DG1 real-byte adaptive granularity",
  "question": "Does experiment 073's drift of the inherited global capture and decision hooks away from the intended cue roles change any retain/revert Boolean relative to a row-local two-block cue-role counterfactual on the twelve frozen rows?",
  "hypothesis": "The unchanged 044 replay will retain on all twelve rows under both the inherited global hook and the row-local cue-role counterfactual, producing zero decision divergences despite five role-drifted rows.",
  "exact_parent_sha": "cd6e3a681ed3fe73f610b176996b79ab3b56d52a",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-HOOK-CALL-ROLE-ATTRIBUTION-073",
    "classification": "supported-by-frozen-rules",
    "qualification_run_id": "38827378772",
    "result_sha256": "30d382889990d80dce17069aece3141a9fba23b09a962e15b979938c98f6d45a",
    "observation": "Seven rows receive the intended cue hooks, one receives check hooks, and four receive model-fraction hooks; all twelve capture and decision hooks were exhaustively attributed.",
    "continuation_rule": "This is a non-fresh read-only diagnostic on observed Y/Z/AA and cannot establish gate performance, fresh generalization, causal benefit, or a corrected gate."
  },
  "authority": "synthetic research-only diagnostic on immutable repo-owned bytes; no wetware, deployment, external inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": ["research/experiments/exp-dgr-real-utf8-two-block-retain-revert-hook-decision-divergence-attribution-074.ice", "research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-hook-decision-divergence-attribution-074.py", ".yggdrasil/qualification-request.json", ".yggdrasil/isolated-run.json"],
  "inputs": {
    "base_training": "Byte-identical four-file set inherited through 029/043/044/073.",
    "demand": "Byte-identical observed Y/Z/AA cohort and Git identities from 044.",
    "orders": [["Y", "Z", "AA"], ["AA", "Z", "Y"]],
    "scheduled_rows": "Twelve frozen rows: each order's stage prefixes of lengths one, two, and three over every seen domain.",
    "decision_definitions": "Inherited decision is the unchanged 043 global offset-five block Boolean. Counterfactual decision applies the same nonnegative early-and-late rule to each row's cue, frozen model, and minimax model captured at the frozen cue call sites.",
    "contamination": "Outcomes, hook roles, row offsets, and aggregate 044 decisions are observed; only row-level inherited-versus-intended Boolean divergence remains tested."
  },
  "arms": {
    "frozen_replay_control": "Run unchanged 044 gated computation and observe its inherited global-hook decisions without mutation.",
    "row_local_counterfactual": "Read-only trace the frozen cue call sites, then recompute only the two cue-block correct-count differences with the unwrapped frozen model_correct_counts function and apply the unchanged nonnegative conjunction."
  },
  "seeds": {"randomness": "none", "seed_list": [], "determinism": "All identities, orders, splits, fitting, tracing, call sites, counterfactual scoring, and accounting are fixed; two executions must be byte-identical."},
  "budgets": {"base_training_files": 4, "demand_files": 3, "encounter_orders": 2, "stages_per_order": 3, "scheduled_seen_domain_rows": 12, "cue_blocks_per_row": 2, "cell_count": 16, "active_structure_count": 10, "retained_structure_count": 6, "primary_runs": 2, "maximum_source_processes": 1, "timeout_seconds": 1800, "network_access": false, "capacity_growth_events": 0},
  "metrics_and_thresholds": [
    ["training_file_identity_mismatch_count", "==", 0], ["evaluation_file_identity_mismatch_count", "==", 0], ["future_stage_adaptation_access_count", "==", 0], ["second_half_adaptation_access_count", "==", 0], ["valid_stage_count", "==", 6], ["valid_seen_domain_evaluation_count", "==", 12], ["matched_assignment_failure_count", "==", 0], ["capacity_growth_event_count", "==", 0], ["retained_record_integrity_mismatch_count", "==", 0], ["state_partition_mismatch_count", "==", 0],
    ["inherited_decision_count", "==", 12], ["counterfactual_decision_count", "==", 12], ["inherited_retain_count", "==", 12], ["counterfactual_retain_count", "==", 12], ["decision_divergence_count", "==", 0], ["aligned_row_divergence_count", "==", 0], ["drifted_row_divergence_count", "==", 0], ["missing_counterfactual_row_count", "==", 0], ["duplicate_counterfactual_row_count", "==", 0], ["decision_accounting_mismatch_count", "==", 0], ["sealed073_role_reproduction_mismatch_count", "==", 0], ["inherited_retain_row_mask", "==", 4095], ["counterfactual_retain_row_mask", "==", 4095], ["decision_divergence_row_mask", "==", 0]
  ],
  "controls": [
    "Reuse 044 bytes, identities, orders, splits, learner, gate wrapper, matching, partition, capacity, calls, and blocks unchanged.",
    "Freeze the twelve row keys, global row indices zero through eleven, cue_frozen caller line 330, cue_minimax caller line 333, and aligned mask 127 from sealed 073.",
    "Use the unwrapped resource-pressure model_correct_counts solely for counterfactual scoring; split each already-permitted cue at floor length over two and reset the function independently for early and late blocks exactly as 043 does.",
    "Counterfactual scoring may not modify replay frames, models, results, decisions, inputs, or outputs.",
    "Verify sealed 073 byte identity and reproduce its aligned/check/model-fraction decision-row masks; do not reinterpret benefit, comparator, retention, validity, or untouched-second-half outcomes."
  ],
  "validity_criteria": [
    "Exact parent, North Star, sealed 073, dependencies, and input identities and sizes match.",
    "Replay completes six stages with identity, access, matching, partition, and capacity controls preserved.",
    "Every scheduled row supplies exactly one cue-frozen model, one cue-minimax model, and one inherited decision; each counterfactual uses exactly two nonempty cue blocks.",
    "Inherited and counterfactual row categories are exhaustive and disjoint and reproduce sealed 073 role membership.",
    "Two isolated executions are byte-identical; no tokenizer, external model, network, capacity growth, or cross-order state."
  ],
  "classification_rules": {
    "supported": "Validity passes and all twelve inherited and counterfactual decisions retain, with zero divergence.",
    "mixed": "Validity passes and at least one row diverges, but all aligned rows agree and divergences are confined to the five sealed drifted rows.",
    "null": "Validity passes, no row diverges, and both decision systems revert on all twelve rows.",
    "negative": "Validity passes but any aligned row diverges or a divergence occurs outside sealed drifted membership.",
    "incomplete": "Both executions, all six stages, or all twelve row comparisons do not complete.",
    "invalid": "Any identity, provenance, isolation, determinism, trace-site, row-key, cue-block, accounting, matching, partition, capacity, finiteness, or qualification criterion fails."
  },
  "stop_conditions": [
    "Stop invalid before interpretation on identity, lineage, dependency, size, source, trace-site, or schedule mismatch.",
    "Stop invalid on forbidden access, missing or duplicate row data, empty cue block, accounting inconsistency, matching failure, partition corruption, capacity growth, non-finite metric, or nondeterminism.",
    "Do not stop early for supported, mixed, null, or negative outcomes.",
    "After any output is observed, do not repair or rerun this identifier."
  ],
  "no_post_result_tuning_rule": "After output, do not alter inputs, identities, orders, splits, learner, gate wrapper, tracing, sites, decision definitions, scoring, schedule, masks, accounting, budgets, metrics, thresholds, validity, classification, or stops under this identifier."
}
