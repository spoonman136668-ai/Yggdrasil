{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-HOOK-MARGIN-DIVERGENCE-ATTRIBUTION-075",
  "program": "DG1 real-byte adaptive granularity",
  "question": "Does experiment 073's drift of five inherited global decision hooks change the integer early/late retain margins relative to experiment 074's row-local cue-role counterfactual even though no retain/revert Boolean changed?",
  "hypothesis": "All fourteen margins on the seven aligned rows will match exactly; at least one of the ten margins on the five drifted rows will differ, while every inherited and counterfactual margin remains nonnegative.",
  "exact_parent_sha": "57589f6e68a6fcdab49ea994f22a51fad3cfcdae",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-HOOK-DECISION-DIVERGENCE-ATTRIBUTION-074",
    "classification": "supported-by-frozen-rules",
    "qualification_run_id": "38829631515",
    "result_sha256": "f84e25135c839d976052df08e8877684114419e4f04f7820ff6db1cdc43582b1",
    "observation": "All twelve inherited and row-local cue-role decisions retained with zero Boolean divergence; seven rows used intended cue hooks and five used check or model-fraction hooks.",
    "continuation_rule": "This is a non-fresh read-only diagnostic on observed Y/Z/AA and cannot establish gate performance, fresh generalization, causal benefit, or a corrected gate."
  },
  "authority": "synthetic research-only diagnostic on immutable repo-owned bytes; no wetware, deployment, external inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": ["research/experiments/exp-dgr-real-utf8-two-block-retain-revert-hook-margin-divergence-attribution-075.ice", "research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-hook-margin-divergence-attribution-075.py", ".yggdrasil/qualification-request.json", ".yggdrasil/isolated-run.json"],
  "inputs": {
    "base_training": "Byte-identical four-file set inherited through 029/043/044/074.",
    "demand": "Byte-identical observed Y/Z/AA cohort and Git identities from 044.",
    "orders": [["Y", "Z", "AA"], ["AA", "Z", "Y"]],
    "scheduled_rows": "Twelve frozen rows: each order's stage prefixes of lengths one, two, and three over every seen domain.",
    "margin_definitions": "Inherited margins are the two integer differences already emitted by unchanged 043 at its global decision hook. Counterfactual margins are the early and late cue-minimax minus cue-frozen correct-count differences recomputed exactly as frozen in 074.",
    "contamination": "Outcomes, hook roles, row offsets, and all Boolean decisions are observed; only exact row-level inherited-versus-intended integer margin divergence remains tested."
  },
  "arms": {
    "frozen_replay_control": "Run unchanged 044 gated computation and read its inherited early/late integer margins without mutation.",
    "row_local_counterfactual": "Read-only trace the frozen cue call sites and recompute the two cue-role integer margins with the unwrapped frozen model_correct_counts function."
  },
  "seeds": {"randomness": "none", "seed_list": [], "determinism": "All identities, orders, splits, fitting, tracing, call sites, margin definitions, and accounting are fixed; two executions must be byte-identical."},
  "budgets": {"base_training_files": 4, "demand_files": 3, "encounter_orders": 2, "stages_per_order": 3, "scheduled_seen_domain_rows": 12, "margins_per_row": 2, "aligned_rows": 7, "drifted_rows": 5, "cell_count": 16, "active_structure_count": 10, "retained_structure_count": 6, "primary_runs": 2, "maximum_source_processes": 1, "timeout_seconds": 1800, "network_access": false, "capacity_growth_events": 0},
  "metrics_and_thresholds": [
    ["training_file_identity_mismatch_count", "==", 0], ["evaluation_file_identity_mismatch_count", "==", 0], ["future_stage_adaptation_access_count", "==", 0], ["second_half_adaptation_access_count", "==", 0], ["valid_stage_count", "==", 6], ["valid_seen_domain_evaluation_count", "==", 12], ["matched_assignment_failure_count", "==", 0], ["capacity_growth_event_count", "==", 0], ["retained_record_integrity_mismatch_count", "==", 0], ["state_partition_mismatch_count", "==", 0],
    ["inherited_margin_count", "==", 24], ["counterfactual_margin_count", "==", 24], ["aligned_margin_mismatch_count", "==", 0], ["drifted_row_margin_difference_count", ">=", 1], ["drifted_margin_difference_count", ">=", 1], ["margin_sign_divergence_count", "==", 0], ["inherited_negative_margin_count", "==", 0], ["counterfactual_negative_margin_count", "==", 0], ["missing_counterfactual_row_count", "==", 0], ["duplicate_counterfactual_row_count", "==", 0], ["margin_accounting_mismatch_count", "==", 0], ["sealed074_decision_reproduction_mismatch_count", "==", 0], ["aligned_row_mask", "==", 127], ["drifted_row_mask", "==", 3968], ["margin_divergence_outside_drifted_count", "==", 0]
  ],
  "controls": [
    "Reuse 044 bytes, identities, orders, splits, learner, gate wrapper, matching, partition, capacity, calls, and blocks unchanged.",
    "Freeze the twelve row keys, global row indices zero through eleven, cue-frozen caller line 330, cue-minimax caller line 333, and aligned mask 127 from sealed 073/074.",
    "Use the unwrapped resource-pressure model_correct_counts solely for counterfactual scoring; split each already-permitted cue at floor length over two and reset independently for early and late blocks exactly as 043 and 074 do.",
    "Compare integer margins exactly, without tolerance, normalization, mutation, or replacement of either arm.",
    "Verify sealed 074 byte identity and reproduce both all-retain row masks and its zero decision-divergence mask; do not reinterpret benefit, comparator, retention, validity, or untouched-second-half outcomes."
  ],
  "validity_criteria": [
    "Exact parent, North Star, sealed 074, dependencies, and input identities and sizes match.",
    "Replay completes six stages with identity, access, matching, partition, and capacity controls preserved.",
    "Every scheduled row supplies exactly one inherited margin pair, one cue-frozen model, and one cue-minimax model; every counterfactual uses exactly two nonempty cue blocks.",
    "Aligned and drifted membership is exhaustive and disjoint; integer margin, sign, row, and mask accounting is complete.",
    "Two isolated executions are byte-identical; no tokenizer, external model, network, capacity growth, or cross-order state."
  ],
  "classification_rules": {
    "supported": "Validity passes, aligned margins match exactly, at least one drifted-row margin differs, and all inherited and counterfactual margins remain nonnegative.",
    "mixed": "Validity passes, aligned margins match exactly and at least one drifted-row margin differs, but at least one inherited-versus-counterfactual margin sign differs.",
    "null": "Validity passes and all twenty-four inherited margins equal their counterfactual margins exactly.",
    "negative": "Validity passes but any aligned margin differs or any numerical divergence occurs outside sealed drifted membership.",
    "incomplete": "Both executions, all six stages, all twelve rows, or all twenty-four paired margins do not complete.",
    "invalid": "Any identity, provenance, isolation, determinism, trace-site, row-key, cue-block, integer-margin, accounting, matching, partition, capacity, finiteness, or qualification criterion fails."
  },
  "stop_conditions": [
    "Stop invalid before interpretation on identity, lineage, dependency, size, source, trace-site, or schedule mismatch.",
    "Stop invalid on forbidden access, missing or duplicate row data, empty cue block, non-integer margin, accounting inconsistency, matching failure, partition corruption, capacity growth, non-finite metric, or nondeterminism.",
    "Do not stop early for supported, mixed, null, or negative outcomes.",
    "After any output is observed, do not repair or rerun this identifier."
  ],
  "no_post_result_tuning_rule": "After output, do not alter inputs, identities, orders, splits, learner, gate wrapper, tracing, sites, margin definitions, scoring, schedule, masks, accounting, budgets, metrics, thresholds, validity, classification, or stops under this identifier."
}
