{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-CALL-ORIGIN-ATTRIBUTION-068",
  "program": "DG1 real-byte adaptive granularity",
  "question": "Does experiment 067's observed model_correct_counts cardinality of 116 decompose into the 96 direct calls made by the twelve staged seen-domain evaluation rows in experiment 029 plus 20 inherited auxiliary calls outside that staged loop?",
  "hypothesis": "The unchanged 044 replay will attribute exactly 96 calls to direct experiment-029 staged evaluation call sites and exactly 20 calls to inherited auxiliary call sites, summing to the sealed 067 total of 116 with no unclassified calls.",
  "exact_parent_sha": "2c6d99db842cf8e61c24b5f4354db07b0919b5b2",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-CALL-CARDINALITY-ATTRIBUTION-067",
    "classification": "supported-by-frozen-rules",
    "qualification_run_id": "38781890868",
    "result_sha256": "65ccf387512df01e99b990fc8eddf1150e796db93b9a7cd1b38584785f7a7dce",
    "observation": "The unchanged 044 replay emitted 116 observed calls, four fewer than its frozen expected constant of 120; source inspection fixes eight direct staged calls per seen-domain evaluation row and sealed controls fix twelve such rows.",
    "continuation_rule": "068 is a non-fresh read-only diagnostic on observed Y/Z/AA inputs and cannot establish gate performance or fresh generalization."
  },
  "authority": "synthetic research-only diagnostic on immutable repo-owned bytes; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": ["research/experiments/exp-dgr-real-utf8-two-block-retain-revert-call-origin-attribution-068.ice", "research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-call-origin-attribution-068.py", ".yggdrasil/qualification-request.json", ".yggdrasil/isolated-run.json"],
  "inputs": {
    "base_training": "Byte-identical four-file training set inherited through 029/043/044/067.",
    "demand": "Byte-identical observed Y/Z/AA cohort and Git-blob identities from 044.",
    "orders": [["Y", "Z", "AA"], ["AA", "Z", "Y"]],
    "split": "Byte-identical 044 half split, two contiguous first-half cue blocks, and independently reset raw four-byte context.",
    "contamination": "All Y/Z/AA outcomes and total call cardinality are observed; only deterministic call origin is attributed."
  },
  "arms": {
    "frozen_replay_control": "Run unchanged 044 gated computation with frozen Y/Z/AA constants.",
    "origin_attribution": "For every observed model_correct_counts call, classify its immediate Python caller as one of the eight frozen direct staged call sites in experiment 029 or as an inherited auxiliary call site; emit category counts only."
  },
  "seeds": {"randomness": "none", "seed_list": [], "determinism": "All identities, orders, splits, fitting, observation, caller classification, and accounting are fixed; two complete executions must be byte-identical."},
  "budgets": {"base_training_files": 4, "demand_files": 3, "encounter_orders": 2, "stages_per_order": 3, "seen_domain_evaluation_rows": 12, "direct_calls_per_seen_domain_row": 8, "cell_count": 16, "active_structure_count": 10, "retained_structure_count": 6, "primary_runs": 2, "maximum_source_processes": 1, "timeout_seconds": 1800, "network_access": false, "capacity_growth_events": 0},
  "metrics_and_thresholds": [
    ["training_file_identity_mismatch_count", "==", 0], ["evaluation_file_identity_mismatch_count", "==", 0], ["future_stage_adaptation_access_count", "==", 0], ["second_half_adaptation_access_count", "==", 0], ["valid_stage_count", "==", 6], ["valid_seen_domain_evaluation_count", "==", 12], ["matched_assignment_failure_count", "==", 0], ["capacity_growth_event_count", "==", 0], ["retained_record_integrity_mismatch_count", "==", 0], ["state_partition_mismatch_count", "==", 0],
    ["observed_call_count", "==", 116], ["sealed067_observed_call_count", "==", 116], ["direct_staged_call_count", "==", 96], ["auxiliary_call_count", "==", 20], ["unclassified_call_count", "==", 0], ["expected_direct_staged_call_count", "==", 96], ["origin_accounting_mismatch_count", "==", 0], ["sealed_total_reproduction_mismatch_count", "==", 0]
  ],
  "controls": [
    "Reuse 044's bytes, identities, orders, splits, learner, gate, matching, partition, capacity, calls, and blocks unchanged.",
    "Define direct staged calls solely as immediate calls from experiment 029 source lines 303, 306, 309, 312, 330, 333, 337, and 340; all other observed calls are auxiliary.",
    "Compute the expected direct count before execution as twelve sealed seen-domain rows times eight frozen direct call sites.",
    "Verify sealed 067 evidence byte identity and reproduce its observed total; do not interpret benefit, comparator, retention, or gate-decision values."
  ],
  "validity_criteria": [
    "Exact parent, North Star, sealed 067 evidence identity, dependencies, and Y/Z/AA identities and sizes match.",
    "Unchanged replay completes six stages and preserves identity, access, matching, partition, and capacity controls.",
    "Every observed call has an immediate caller, origin categories are exhaustive and disjoint, and their integer counts sum exactly to both the live and sealed totals.",
    "Two isolated executions are byte-identical; no tokenizer, external model, network, capacity growth, or state carry between orders."
  ],
  "classification_rules": {
    "supported": "Validity passes and the 116 calls decompose exactly into 96 direct staged and 20 auxiliary calls with no unclassified calls.",
    "mixed": "Validity passes and direct staged calls equal 96, but auxiliary or total accounting differs from the frozen hypothesis.",
    "null": "Validity passes but auxiliary_call_count is zero.",
    "negative": "Validity passes but direct staged calls differ from 96 or any call is unclassified.",
    "incomplete": "Compute interruption prevents both executions or all six stages.",
    "invalid": "Any identity, provenance, isolation, determinism, caller-origin, accounting, matching, partition, capacity, finiteness, or qualification criterion fails."
  },
  "stop_conditions": [
    "Stop invalid before interpretation on identity, lineage, dependency, size, source, or frozen direct-call-site mismatch.",
    "Stop invalid on forbidden access, non-exhaustive or overlapping origin classification, inconsistent accounting, matching failure, partition corruption, capacity growth, non-finite metric, or nondeterministic duplicate output.",
    "Do not stop early for supported, mixed, null, or negative outcomes.",
    "After any output is observed, do not repair or rerun under this experiment identifier."
  ],
  "no_post_result_tuning_rule": "After any output is observed, do not alter inputs, identities, orders, splits, learner, gate, observation, caller categories, call-site definitions, accounting, budgets, metrics, thresholds, validity, classification, or stopping rules under this identifier."
}
