{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-AUXILIARY-CALLSITE-ATTRIBUTION-069",
  "program": "DG1 real-byte adaptive granularity",
  "question": "Do experiment 068's 20 auxiliary model_correct_counts calls consist exactly of ten paired calls from error_guided.model_fraction, with one call at each of its frozen full-model and active-model call sites for every qualifying row?",
  "hypothesis": "The unchanged 044 replay will attribute exactly 10 auxiliary calls to error-guided-wake-005.py line 39 and exactly 10 to line 40, with zero auxiliary calls at any other call site, implying 10 model_fraction invocations among the twelve staged seen-domain evaluation rows.",
  "exact_parent_sha": "b4cad8ccdf012ffdbc6f6eae6b4f78a6d2099184",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-CALL-ORIGIN-ATTRIBUTION-068",
    "classification": "supported-by-frozen-rules",
    "qualification_run_id": "38782544088",
    "result_sha256": "8712b9f2ff3bb24d98aed64c58c1679a385c3cd51df824ba1a36ba12b70e772f",
    "observation": "The unchanged replay emitted 96 direct staged calls and 20 auxiliary calls with exhaustive accounting; static source inspection fixes model_fraction as a paired two-call auxiliary mechanism guarded by selected_increment > 0.",
    "continuation_rule": "069 is a non-fresh read-only diagnostic on observed Y/Z/AA inputs and cannot establish gate performance, fresh generalization, or causal benefit."
  },
  "authority": "synthetic research-only diagnostic on immutable repo-owned bytes; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": ["research/experiments/exp-dgr-real-utf8-two-block-retain-revert-auxiliary-callsite-attribution-069.ice", "research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-auxiliary-callsite-attribution-069.py", ".yggdrasil/qualification-request.json", ".yggdrasil/isolated-run.json"],
  "inputs": {
    "base_training": "Byte-identical four-file training set inherited through 029/043/044/068.",
    "demand": "Byte-identical observed Y/Z/AA cohort and Git-blob identities from 044.",
    "orders": [["Y", "Z", "AA"], ["AA", "Z", "Y"]],
    "split": "Byte-identical 044 half split, two contiguous first-half cue blocks, and independently reset raw four-byte context.",
    "contamination": "All Y/Z/AA outcomes and aggregate origin counts are observed; only deterministic auxiliary call-site attribution is tested."
  },
  "arms": {
    "frozen_replay_control": "Run unchanged 044 gated computation with frozen Y/Z/AA constants.",
    "auxiliary_callsite_attribution": "For each call classified as auxiliary by 068's frozen rule, count immediate caller occurrences at error-guided-wake-005.py lines 39 and 40 and at all other call sites."
  },
  "seeds": {"randomness": "none", "seed_list": [], "determinism": "All identities, orders, splits, fitting, observation, caller classification, and accounting are fixed; two complete executions must be byte-identical."},
  "budgets": {"base_training_files": 4, "demand_files": 3, "encounter_orders": 2, "stages_per_order": 3, "seen_domain_evaluation_rows": 12, "direct_calls_per_seen_domain_row": 8, "cell_count": 16, "active_structure_count": 10, "retained_structure_count": 6, "primary_runs": 2, "maximum_source_processes": 1, "timeout_seconds": 1800, "network_access": false, "capacity_growth_events": 0},
  "metrics_and_thresholds": [
    ["training_file_identity_mismatch_count", "==", 0], ["evaluation_file_identity_mismatch_count", "==", 0], ["future_stage_adaptation_access_count", "==", 0], ["second_half_adaptation_access_count", "==", 0], ["valid_stage_count", "==", 6], ["valid_seen_domain_evaluation_count", "==", 12], ["matched_assignment_failure_count", "==", 0], ["capacity_growth_event_count", "==", 0], ["retained_record_integrity_mismatch_count", "==", 0], ["state_partition_mismatch_count", "==", 0],
    ["observed_call_count", "==", 116], ["direct_staged_call_count", "==", 96], ["auxiliary_call_count", "==", 20], ["model_fraction_full_call_count", "==", 10], ["model_fraction_active_call_count", "==", 10], ["other_auxiliary_call_count", "==", 0], ["inferred_model_fraction_invocation_count", "==", 10], ["paired_call_count_mismatch", "==", 0], ["auxiliary_accounting_mismatch_count", "==", 0], ["sealed068_reproduction_mismatch_count", "==", 0]
  ],
  "controls": [
    "Reuse 044's bytes, identities, orders, splits, learner, gate, matching, partition, capacity, calls, and blocks unchanged.",
    "Reuse 068's direct classification as experiment-029.py lines 303, 306, 309, 312, 330, 333, 337, and 340; every remaining classified call is auxiliary.",
    "Define the two hypothesized auxiliary sites before execution as error-guided-wake-005.py lines 39 and 40; retain an exhaustive other-auxiliary category.",
    "Verify sealed 068 evidence byte identity and reproduce its observed, direct, and auxiliary totals; do not interpret benefit, comparator, retention, or gate-decision values."
  ],
  "validity_criteria": [
    "Exact parent, North Star, sealed 068 evidence identity, dependencies, and Y/Z/AA identities and sizes match.",
    "Unchanged replay completes six stages and preserves identity, access, matching, partition, and capacity controls.",
    "Every observed call has an immediate caller; direct and auxiliary categories are exhaustive and disjoint; auxiliary site categories are exhaustive and disjoint.",
    "Two isolated executions are byte-identical; no tokenizer, external model, network, capacity growth, or state carry between orders."
  ],
  "classification_rules": {
    "supported": "Validity passes and the 20 auxiliary calls decompose exactly into 10 full-site plus 10 active-site model_fraction calls, with zero other auxiliary calls and exact pairing.",
    "mixed": "Validity passes and all auxiliary calls arise from the two model_fraction sites, but the two site counts are unequal or differ from 10.",
    "null": "Validity passes but neither model_fraction site is observed.",
    "negative": "Validity passes but any auxiliary call arises outside the two frozen model_fraction sites.",
    "incomplete": "Compute interruption prevents both executions or all six stages.",
    "invalid": "Any identity, provenance, isolation, determinism, caller-site, accounting, matching, partition, capacity, finiteness, or qualification criterion fails."
  },
  "stop_conditions": [
    "Stop invalid before interpretation on identity, lineage, dependency, size, source, or frozen call-site mismatch.",
    "Stop invalid on forbidden access, non-exhaustive or overlapping classification, inconsistent accounting, matching failure, partition corruption, capacity growth, non-finite metric, or nondeterministic duplicate output.",
    "Do not stop early for supported, mixed, null, or negative outcomes.",
    "After any output is observed, do not repair or rerun under this experiment identifier."
  ],
  "no_post_result_tuning_rule": "After any output is observed, do not alter inputs, identities, orders, splits, learner, gate, observation, caller sites, classifications, accounting, budgets, metrics, thresholds, validity, classification, or stopping rules under this identifier."
}
