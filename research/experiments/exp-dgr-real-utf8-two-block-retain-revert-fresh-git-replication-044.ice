{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-FRESH-GIT-REPLICATION-044",
  "program": "DG1 real-byte adaptive granularity",
  "question": "Does the frozen Git-identity two-block retain/revert gate generalize from the qualified V/W/X cohort to the previously unevaluated Y/Z/AA cohort while preserving fixed-capacity benefit without false retains and remaining noninferior to the pooled comparator on every row?",
  "hypothesis": "Across both frozen encounter orders on Y/Z/AA, the unchanged gate will produce no false retains, every selected untouched-second-half incremental benefit will be positive and noninferior to frozen and pooled controls, independent and active benefit retention will remain at least 0.70, and capacity will remain fixed.",
  "exact_parent_sha": "985e8476820e3c273656eceec16c52affd06ba78",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "qualified_experiment": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-GIT-IDENTITY-REPLICATION-043",
    "classification": "supported-by-frozen-rules",
    "qualification_run_id": "38694154102",
    "result_sha256": "1dbaff7a5ef0414a29c4fdb10a1f35d4641c9429822a14a8deceab32f7374c09",
    "observation": "On V/W/X, duplicate output was byte-identical, all validity metrics passed, all twelve decisions retained matched-minimax, no false decision occurred, selected-minus-frozen and selected-minus-pooled minima were zero, independent and active retention were 1.0, and capacity remained fixed. Generalization to Y/Z/AA is unknown.",
    "lineage_context": "Valid experiment 034 included one correct reversion; valid fresh experiment 037 had no false decision but missed the pooled comparator by two. Invalid experiment 038 makes no scientific claim; 039 through 042 were blocked without output."
  },
  "authority": "synthetic research-only evaluation on immutable repo-owned bytes; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": ["research/experiments/exp-dgr-real-utf8-two-block-retain-revert-fresh-git-replication-044.ice", "research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-fresh-git-replication-044.py", ".yggdrasil/qualification-request.json", ".yggdrasil/isolated-run.json"],
  "inputs": {
    "base_training": "Byte-identical lineage-native four-file training set and Git-blob verifier inherited from experiments 029 and 043; identity mismatch must remain zero.",
    "demand": {
      "Y": ["research/applications/track-a/a25-t8i-temporal-low-pass-persistence-calibration.ice", "af5a14691830a487f81a202c9880bc03c5591283", 20253],
      "Z": ["research/applications/track-a/a26-t8j-threshold-ultrasensitivity-calibration.ice", "18cec23aa4d8b6a62020904f19066c9f9ea957d2", 18258],
      "AA": ["research/applications/track-a/a27-t8k-negative-feedback-homeostatic-authority-correction.ice", "4451649de0edf3fe16de362b5b266ed9437db01b", 22531]
    },
    "orders": [["Y", "Z", "AA"], ["AA", "Z", "Y"]],
    "split": "Split each raw demand blob at floor(length/2) into permitted first half and untouched second half; split the first half at floor(first_half_length/2) into contiguous early and late cue blocks; reset raw four-byte context independently for every block and second half.",
    "freshness": "Y/Z/AA paths have zero references in preregistrations present at the exact parent; their scientific outcomes and block scores have not been observed in this lineage.",
    "contamination_rule": "Fitting, minimax scoring, and activation may use base blobs and encountered complete first halves only. Gate scoring may use only the evaluated domain's two first-half blocks. Untouched second halves are accessed only after phenotype construction and both block decisions are frozen."
  },
  "frozen_reuse": {
    "learner": "byte-identical 029/034/037/043 previous-byte baseline, four-byte candidate statistics, occurrence>=12, consistency>=0.60, utility ranking, home hash, radius two, sixteen-cell development, candidate union, pooled successor rule, minimax ranking, deterministic matching, and Git-blob identity verifier",
    "gate": "byte-identical 034/037/043 two-block rule: select matched-minimax iff early-block and late-block correct-count differences from frozen are both nonnegative; ties remain nonnegative",
    "activation": "byte-identical complete-first-half cue-contribution ranking selecting ten active records and retaining six complementary records byte-exactly",
    "metrics": "byte-identical 043 incremental-correct, covered-position accuracy, comparator, gate-error, and integrity definitions"
  },
  "arms": {
    "frozen_full_control": "unchanged architecture-only sixteen-motif phenotype",
    "matched_minimax_full_control": "unchanged sixteen-motif matched-minimax adaptation",
    "independent_adapted_full_control": "per-domain phenotype fitted from base blobs plus only that domain's first half",
    "pooled_cumulative_full_control": "unchanged pooled cumulative comparator",
    "two_block_gate_primary": "frozen selection between frozen-full and matched-minimax-full",
    "gated_ten_active_primary": "top ten selected-full records by unchanged complete-first-half ranking; retain six complementary records byte-exactly"
  },
  "seeds": {"randomness": "none", "seed_list": [], "determinism": "all identities, orders, splits, fitting, rankings, matching, block comparisons, and selections are fixed; two complete executions must be byte-identical"},
  "budgets": {"base_training_files": 4, "demand_files": 3, "encounter_orders": 2, "stages_per_order": 3, "seen_domain_evaluation_rows": 12, "cue_blocks_per_row": 2, "cell_count": 16, "active_structure_count": 10, "retained_structure_count": 6, "primary_runs": 2, "maximum_source_processes": 1, "timeout_seconds": 1800, "network_access": false, "capacity_growth_events": 0},
  "metrics_and_thresholds": [
    ["training_file_identity_mismatch_count", "==", 0], ["evaluation_file_identity_mismatch_count", "==", 0], ["fresh_demand_preregistration_reference_count", "==", 0], ["future_stage_adaptation_access_count", "==", 0], ["second_half_adaptation_access_count", "==", 0],
    ["valid_stage_count", "==", 6], ["valid_evaluation_row_count", "==", 12], ["valid_cue_block_count", "==", 24], ["matched_assignment_failure_count", "==", 0], ["minimum_selected_motif_count", "==", 16], ["maximum_selected_motif_count", "==", 16], ["matched_ineligible_candidate_count", "==", 0],
    ["two_block_gate_decision_count", "==", 12], ["two_block_false_retain_count", "==", 0], ["minimum_selected_incremental_correct_count", ">", 0], ["minimum_selected_minus_frozen_count", ">=", 0], ["minimum_selected_to_independent_fraction", ">=", 0.70], ["minimum_selected_minus_pooled_count", ">=", 0],
    ["minimum_active_retained_incremental_fraction", ">=", 0.70], ["minimum_eval_covered_accuracy_gain", ">", 0.0], ["retained_record_integrity_mismatch_count", "==", 0], ["state_partition_mismatch_count", "==", 0], ["capacity_growth_event_count", "==", 0], ["tokenizer_use_count", "==", 0], ["invalid_evaluation_rows", "==", 0]
  ],
  "controls": [
    "Reuse the sealed learner chain without changing learner, verifier algorithm, candidate union, pooled rule, minimax ranking, matching, splits, capacity, or partition.",
    "The only scientific delta from qualified 043 is the previously unevaluated Y/Z/AA cohort and its two frozen encounter orders.",
    "False retain means selecting matched-minimax when its untouched-second-half difference is negative; false revert means selecting frozen when that difference is nonnegative.",
    "Each selected phenotype has sixteen records partitioned into ten active plus six byte-exact retained records.",
    "Cell count, radius, active ceiling, retained count, total capacity, and all scientific thresholds remain frozen; gate reversion is measured but not required."
  ],
  "validity_criteria": [
    "Exact parent, North Star, 043 evidence identity, dependencies, current Y/Z/AA Git-blob identities, sizes, and preregistration freshness match.",
    "Exactly twelve evaluation rows and twenty-four nonempty cue blocks are scored under the frozen gate.",
    "No untouched-second-half or future-stage bytes enter fitting, ranking, matching, block scoring, selection, or activation.",
    "Every stage assigns sixteen matched-minimax motifs and every selected phenotype partitions ten active plus six retained records.",
    "All metrics are finite and two executions are byte-identical.",
    "No tokenizer, external model, network, radius widening, capacity growth, or state carry between orders occurs."
  ],
  "classification_rules": {
    "supported": "Validity passes, no false retain occurs, and every benefit, comparator, 0.70 retention, covered-gain, integrity, and capacity threshold passes.",
    "mixed": "Validity passes and no false retain occurs, but at least one false revert or collateral/comparator/retention threshold fails.",
    "null": "Validity passes, every matched-minimax versus frozen evaluation difference is zero, and selected benefit is never negative.",
    "negative": "Validity passes but any false retain occurs, selected benefit is negative on any row, selected benefit is nonpositive on at least two rows, or active retained benefit falls below 0.50 on any row.",
    "incomplete": "Compute interruption prevents both deterministic executions, six stages, twelve evaluation rows, or twenty-four block scores.",
    "invalid": "Any identity, freshness, isolation, determinism, matching, block-partition, gate-integrity, fixed-capacity, finiteness, partition-integrity, or qualification criterion fails."
  },
  "stop_conditions": [
    "Stop invalid before scientific evaluation on any identity, lineage, dependency, freshness, size, or source mismatch.",
    "Stop invalid on forbidden byte access, malformed block, gate mismatch, matching failure, partition corruption, capacity growth, non-finite metric, or nondeterministic duplicate output.",
    "Do not stop early for apparent supported, mixed, null, or negative outcomes.",
    "After any output is observed, do not repair or rerun under this experiment identifier."
  ],
  "no_post_result_tuning_rule": "After any primary or diagnostic output is observed, do not alter inputs, identities, splits, orders, learner, controls, gate, tie rule, scoring, ranking, matching, active ceiling, budgets, metrics, thresholds, aggregation, validity, classification, or stopping rules under this experiment identifier."
}
