{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-HOOK-MARGIN-STAGE-STABILITY-ATTRIBUTION-087",
  "program": "DG1 real-byte adaptive granularity",
  "question": "Is the exact inherited-minus-cue early/late margin-delta pair for order one's repeated Z domain stable from its stage-two row to its stage-three row?",
  "hypothesis": "The repeated Z domain will have identical exact early and late deltas at order-one stages two and three, while all sealed 082 aggregate direction, magnitude, sign, role, and control metrics reproduce.",
  "exact_parent_sha": "71515932a6180b01baa24a5ac84442806bcc6fed",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-HOOK-MARGIN-BLOCK-DIRECTION-ATTRIBUTION-082",
    "classification": "supported-by-frozen-rules",
    "qualification_run_id": "38936691799",
    "result_sha256": "40604294147eb1f76388565fb72659cc6e21ee9588640b5ac04d0c8bf254e9a6",
    "observation": "All four model-fraction-hook rows had more-negative early than late deltas; signed asymmetries summed to -22, all eight deltas were negative, aligned and check-hook margins matched, and all margins remained nonnegative. Per-row deltas were not emitted.",
    "blocked_continuation": "Experiments 083, 084, 085, and 086 preregistered this same unanswered question but were infrastructure-blocked before implementation; none ran, no output was observed, and no scientific claim was made.",
    "continuation_rule": "This non-fresh read-only diagnostic on observed Y/Z/AA may distinguish domain-linked from prefix-stage-dependent numerical drift only; it cannot establish gate performance, fresh generalization, causal benefit, or a corrected gate."
  },
  "authority": "synthetic research-only diagnostic on immutable repo-owned bytes; no wetware, deployment, external inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": ["research/experiments/exp-dgr-real-utf8-two-block-retain-revert-hook-margin-stage-stability-attribution-087.ice", "research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-hook-margin-stage-stability-attribution-087.py", ".yggdrasil/qualification-request.json", ".yggdrasil/isolated-run.json"],
  "inputs": {
    "base_training": "Byte-identical four-file set inherited through 029/043/044/082.",
    "demand": "Byte-identical observed Y/Z/AA cohort and Git identities from 044.",
    "orders": [["Y", "Z", "AA"], ["AA", "Z", "Y"]],
    "scheduled_rows": "Twelve frozen rows in 082 order; the primary comparison is frozen indices eight and ten, keys (1,2,Z) and (1,3,Z).",
    "stability_definition": "Stage-stable means exact integer equality separately for the early inherited-minus-cue delta and late inherited-minus-cue delta between the two frozen Z rows.",
    "contamination": "Aggregate role masks, directions, signs, sums, and asymmetry are observed; the two Z rows' exact deltas and equality remain unobserved."
  },
  "arms": {
    "stage_two_z": "Read the exact early and late deltas for frozen row (1,2,Z) from an unchanged 082 replay.",
    "stage_three_z": "Read the exact early and late deltas for frozen row (1,3,Z) from the same unchanged 082 replay."
  },
  "seeds": {"randomness": "none", "seed_list": [], "determinism": "All identities, orders, splits, fitting, tracing, row keys, delta definitions, and accounting are fixed; two executions must be byte-identical."},
  "budgets": {"base_training_files": 4, "demand_files": 3, "encounter_orders": 2, "stages_per_order": 3, "scheduled_seen_domain_rows": 12, "primary_compared_rows": 2, "margins_per_compared_row": 2, "cell_count": 16, "active_structure_count": 10, "retained_structure_count": 6, "primary_runs": 2, "maximum_source_processes": 1, "timeout_seconds": 1800, "network_access": false, "capacity_growth_events": 0},
  "metrics_and_thresholds": [
    ["stage_two_z_early_delta", ">=", -1000000000], ["stage_two_z_late_delta", ">=", -1000000000], ["stage_three_z_early_delta", ">=", -1000000000], ["stage_three_z_late_delta", ">=", -1000000000],
    ["z_early_delta_difference", ">=", -1000000000], ["z_early_delta_difference", "<=", 1000000000], ["z_late_delta_difference", ">=", -1000000000], ["z_late_delta_difference", "<=", 1000000000], ["z_equal_block_count", ">=", 0], ["z_equal_block_count", "<=", 2], ["z_pair_stable_count", ">=", 0], ["z_pair_stable_count", "<=", 1], ["primary_row_missing_count", "==", 0], ["primary_row_duplicate_count", "==", 0], ["stage_stability_accounting_mismatch_count", "==", 0], ["sealed082_reproduction_mismatch_count", "==", 0],
    ["training_file_identity_mismatch_count", "==", 0], ["evaluation_file_identity_mismatch_count", "==", 0], ["future_stage_adaptation_access_count", "==", 0], ["second_half_adaptation_access_count", "==", 0], ["valid_stage_count", "==", 6], ["valid_seen_domain_evaluation_count", "==", 12], ["matched_assignment_failure_count", "==", 0], ["capacity_growth_event_count", "==", 0], ["retained_record_integrity_mismatch_count", "==", 0], ["state_partition_mismatch_count", "==", 0],
    ["model_fraction_negative_delta_count", "==", 8], ["model_fraction_nonnegative_delta_count", "==", 0], ["model_fraction_early_more_negative_row_count", "==", 4], ["model_fraction_late_more_negative_row_count", "==", 0], ["model_fraction_equal_block_row_count", "==", 0], ["model_fraction_signed_asymmetry_sum", "==", -22], ["model_fraction_asymmetry_absolute_sum", "==", 22], ["model_fraction_early_absolute_delta_sum", "==", 41], ["model_fraction_late_absolute_delta_sum", "==", 19], ["model_fraction_absolute_delta_sum", "==", 60], ["model_fraction_signed_delta_sum", "==", -60], ["margin_sign_divergence_count", "==", 0], ["aligned_row_mask", "==", 127], ["check_hook_row_mask", "==", 128], ["model_fraction_hook_row_mask", "==", 3840]
  ],
  "controls": [
    "Import and run frozen source 082 with SHA-256 e98bf2654f3ff16a32dd840ee3c27f518cae0712d70a7df5a4ef70b4932e68d1; do not alter its inputs, replay, scoring, or returned metrics.",
    "Capture the already-computed exact delta mapping read-only at the frozen source transition immediately after its construction; require exactly the frozen row keys (1,2,Z) and (1,3,Z), block indices zero and one.",
    "Compute differences as stage-three minus stage-two exact integer deltas without tolerance, normalization, mutation, replacement, or thresholding.",
    "Verify sealed 082 byte identity and exact reproduction of every returned 082 metric before interpreting stability."
  ],
  "validity_criteria": [
    "Exact parent, North Star, source 082, sealed 082 result, dependencies, and input identities match.",
    "The unchanged 082 replay completes and all frozen validity/control metrics reproduce.",
    "Each primary key has exactly one exact integer early delta and one exact integer late delta; comparison and equality accounting is complete.",
    "Two isolated executions are byte-identical; no tokenizer, external model, network, capacity growth, cross-order state, or replay mutation."
  ],
  "classification_rules": {
    "supported": "Validity passes and both early and late exact deltas are equal between the two Z rows.",
    "mixed": "Validity passes and exactly one of the early or late exact deltas is equal between the two Z rows.",
    "null": "Validity passes and neither exact delta is equal between the two Z rows.",
    "negative": "Validity passes but either primary delta is nonnegative or any sealed 082 aggregate fails to reproduce.",
    "incomplete": "Both executions, the unchanged 082 replay, either primary row, or any of the four primary deltas do not complete.",
    "invalid": "Any identity, provenance, isolation, determinism, trace-site, row-key, integer-delta, accounting, matching, partition, capacity, finiteness, or qualification criterion fails."
  },
  "stop_conditions": [
    "Stop invalid before interpretation on identity, lineage, dependency, source, trace-site, row-key, or schedule mismatch.",
    "Stop invalid on forbidden access, missing or duplicate primary data, non-integer delta, accounting inconsistency, frozen metric mismatch, capacity growth, non-finite metric, or nondeterminism.",
    "Do not stop early for supported, mixed, null, or negative outcomes.",
    "After any output is observed, do not repair or rerun this identifier."
  ],
  "no_post_result_tuning_rule": "After output, do not alter inputs, identities, orders, splits, learner, gate wrapper, tracing, sites, row keys, delta or stability definitions, scoring, accounting, budgets, metrics, thresholds, validity, classification, or stops under this identifier."
}
