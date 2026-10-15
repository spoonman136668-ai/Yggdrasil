{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-SELECTED-INCREMENT-ROW-ATTRIBUTION-071",
  "program": "DG1 real-byte adaptive granularity",
  "question": "Are experiment 070's two uninvoked order-1 AA rows bypassed because selected_increment is exactly zero rather than negative, and what are the exact deterministic selected_increment values for all twelve scheduled rows?",
  "hypothesis": "The unchanged 044 replay will expose exactly twelve finite selected_increment values: the order-1 AA rows at stages one and two will equal zero, the other ten rows will be positive, and no row will be negative, duplicated, unknown, or missing.",
  "exact_parent_sha": "eb84b4ba17809ff7efde5d41fe26bf9f9dccda62",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-MODEL-FRACTION-ROW-ATTRIBUTION-070",
    "classification": "supported-by-frozen-rules",
    "qualification_run_id": "38784134132",
    "result_sha256": "54c45ab449bbf3f7cf2e7423cfac85310ba9bc390f6d11b8850a936b0d9a1fb6",
    "observation": "Ten unique scheduled rows invoked model_fraction with positive selected_increment; the order-1 AA rows at stages one and two were the two uninvoked rows, but their unobserved selected_increment values and signs remain unknown.",
    "continuation_rule": "071 is a non-fresh read-only diagnostic on observed Y/Z/AA inputs and cannot establish gate performance, fresh generalization, or causal benefit."
  },
  "authority": "synthetic research-only diagnostic on immutable repo-owned bytes; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": ["research/experiments/exp-dgr-real-utf8-two-block-retain-revert-selected-increment-row-attribution-071.ice", "research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-selected-increment-row-attribution-071.py", ".yggdrasil/qualification-request.json", ".yggdrasil/isolated-run.json"],
  "inputs": {
    "base_training": "Byte-identical four-file training set inherited through 029/043/044/070.",
    "demand": "Byte-identical observed Y/Z/AA cohort and Git-blob identities from 044.",
    "orders": [["Y", "Z", "AA"], ["AA", "Z", "Y"]],
    "scheduled_rows": "For each order, stage prefixes of lengths one, two, and three are evaluated over every seen domain, yielding twelve unique (order_index, stage_index, domain) rows.",
    "split": "Byte-identical 044 half split, two contiguous first-half cue blocks, and independently reset raw four-byte context.",
    "contamination": "All Y/Z/AA outcomes and invoked-row membership are observed; only deterministic selected_increment row values and signs are tested."
  },
  "arms": {
    "frozen_replay_control": "Run unchanged 044 gated computation with frozen Y/Z/AA constants.",
    "increment_attribution": "Observe experiment 029 line 439 without mutation, record the frozen order, stage-prefix, domain, and selected_increment locals once per scheduled row, and compare sign masks with sealed experiment 070."
  },
  "seeds": {"randomness": "none", "seed_list": [], "determinism": "All identities, orders, splits, fitting, observation, row keys, and accounting are fixed; two complete executions must be byte-identical."},
  "budgets": {"base_training_files": 4, "demand_files": 3, "encounter_orders": 2, "stages_per_order": 3, "scheduled_seen_domain_rows": 12, "cell_count": 16, "active_structure_count": 10, "retained_structure_count": 6, "primary_runs": 2, "maximum_source_processes": 1, "timeout_seconds": 1800, "network_access": false, "capacity_growth_events": 0},
  "metrics_and_thresholds": [
    ["training_file_identity_mismatch_count", "==", 0], ["evaluation_file_identity_mismatch_count", "==", 0], ["future_stage_adaptation_access_count", "==", 0], ["second_half_adaptation_access_count", "==", 0], ["valid_stage_count", "==", 6], ["valid_seen_domain_evaluation_count", "==", 12], ["matched_assignment_failure_count", "==", 0], ["capacity_growth_event_count", "==", 0], ["retained_record_integrity_mismatch_count", "==", 0], ["state_partition_mismatch_count", "==", 0],
    ["observed_increment_row_count", "==", 12], ["unique_increment_row_count", "==", 12], ["positive_increment_row_count", "==", 10], ["zero_increment_row_count", "==", 2], ["negative_increment_row_count", "==", 0], ["duplicate_increment_row_count", "==", 0], ["unknown_increment_row_count", "==", 0], ["missing_increment_row_count", "==", 0], ["order0_positive_row_mask", "==", 63], ["order1_positive_row_mask", "==", 60], ["order0_zero_row_mask", "==", 0], ["order1_zero_row_mask", "==", 3], ["order0_negative_row_mask", "==", 0], ["order1_negative_row_mask", "==", 0], ["sign_accounting_mismatch_count", "==", 0], ["sealed070_membership_reproduction_mismatch_count", "==", 0],
    ["order0_stage1_y_selected_increment", ">", 0], ["order0_stage2_y_selected_increment", ">", 0], ["order0_stage2_z_selected_increment", ">", 0], ["order0_stage3_y_selected_increment", ">", 0], ["order0_stage3_z_selected_increment", ">", 0], ["order0_stage3_aa_selected_increment", ">", 0], ["order1_stage1_aa_selected_increment", "==", 0], ["order1_stage2_aa_selected_increment", "==", 0], ["order1_stage2_z_selected_increment", ">", 0], ["order1_stage3_aa_selected_increment", ">", 0], ["order1_stage3_z_selected_increment", ">", 0], ["order1_stage3_y_selected_increment", ">", 0]
  ],
  "controls": [
    "Reuse 044's bytes, identities, orders, splits, learner, gate, matching, partition, capacity, calls, and blocks unchanged.",
    "Define the twelve scheduled row keys and six-bit per-order mask encoding exactly as experiment 070.",
    "Observe only line events at experiment 029 line 439 and read order, seen, name, and selected_increment locals without mutation.",
    "Verify sealed 070 evidence byte identity and reproduce its positive/invoked and complement membership masks; do not interpret benefit, comparator, retention, or gate-decision values."
  ],
  "validity_criteria": [
    "Exact parent, North Star, sealed 070 evidence identity, dependencies, and Y/Z/AA identities and sizes match.",
    "Unchanged replay completes six stages and preserves identity, access, matching, partition, and capacity controls.",
    "Every scheduled row is observed exactly once at the frozen guard; row keys are exhaustive and disjoint; every selected_increment is finite numeric.",
    "Positive-value membership exactly reproduces 070's invoked masks and its complement exactly reproduces 070's uninvoked masks.",
    "Two isolated executions are byte-identical; no tokenizer, external model, network, capacity growth, or state carry between orders."
  ],
  "classification_rules": {
    "supported": "Validity passes; the two order-1 AA values at stages one and two are exactly zero; all other ten values are positive; and no value is negative.",
    "mixed": "Validity passes and exactly ten values are positive with two nonpositive values, but either nonpositive value is negative or row membership differs from the hypothesis.",
    "null": "Validity passes but all twelve selected_increment values are positive.",
    "negative": "Validity passes but fewer than ten values are positive, more than two are nonpositive, or positive membership fails to reproduce sealed 070.",
    "incomplete": "Compute interruption prevents both executions or all six stages.",
    "invalid": "Any identity, provenance, isolation, determinism, trace-site, row-key, schedule, accounting, matching, partition, capacity, finiteness, or qualification criterion fails."
  },
  "stop_conditions": [
    "Stop invalid before interpretation on identity, lineage, dependency, size, source, frozen trace-site, or schedule mismatch.",
    "Stop invalid on forbidden access, missing caller locals, unknown, duplicated, or missing row classification, inconsistent accounting, matching failure, partition corruption, capacity growth, non-finite metric, or nondeterministic duplicate output.",
    "Do not stop early for supported, mixed, null, or negative outcomes.",
    "After any output is observed, do not repair or rerun under this experiment identifier."
  ],
  "no_post_result_tuning_rule": "After any output is observed, do not alter inputs, identities, orders, splits, learner, gate, observation, trace site, row schedule, mask encoding, accounting, budgets, metrics, thresholds, validity, classification, or stopping rules under this identifier."
}
