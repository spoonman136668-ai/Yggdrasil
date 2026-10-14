{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-FRESH-REPLICATION-036",
  "program": "DG1 real-byte adaptive granularity",
  "question": "Does the frozen two-block unanimity retain/revert gate and ten-active matched-minimax partition supported on M/N/O in experiment 034 replicate without collateral regression or capacity growth on three previously unevaluated and previously unpreregistered Track-A text domains?",
  "hypothesis": "Across both frozen encounter orders on fresh domains S/T/U, selecting matched-minimax only when its reset-context correct-count difference from frozen is nonnegative in both contiguous blocks of the permitted first half will produce no false retains, will leave every selected untouched-second-half incremental benefit positive and noninferior to frozen, will preserve at least 70% of independent-adaptation and selected-full benefit, and will preserve the fixed sixteen-cell, ten-active/six-retained capacity.",
  "exact_parent_sha": "8c044b21f128dad9a7b8349887b12680674808d1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-GATE-034",
    "classification": "supported-by-frozen-rules",
    "qualification_run_id": "38626257890",
    "result_sha256": "17f2f8fc15f200ae190d3c6da8bb5390d45970798211cd11ea561243551018cf",
    "observation": "On reused M/N/O, the frozen two-block gate made twelve decisions, reverted once, eliminated the sealed single-cue false retain without false reverts, kept minimum selected-minus-frozen benefit at zero, retained independent benefit at 1.0 and active benefit at 0.7670807453416149, preserved exact state integrity, and used no capacity growth. Experiment 035 produced no implementation or output; fresh-domain replication remains unknown."
  },
  "authority": "synthetic research-only replication on immutable repo-owned bytes; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": ["research/experiments/exp-dgr-real-utf8-two-block-retain-revert-fresh-replication-036.ice", "research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-fresh-replication-036.py", ".yggdrasil/qualification-request.json", ".yggdrasil/isolated-run.json"],
  "inputs": {
    "base_training": [["research/architecture/measurement-framework.ice", "6374fc3c39ee821c8f9d565bb7de0875c07d5cdc", 10040], ["research/architecture/structural-plasticity.ice", "d2d75b4ed60e0c112de5202ba31848b15081e0cb", 9550], ["research/architecture/developmental-substrate-v0.2.ice", "52d6e87e2339bdf586c33da22470e38a9ca27785", 8448], ["research/architecture/yggdrasil-north-star.ice", "84358ec54c0e7eba6b6f830e0b4d2755920281cb", 8411]],
    "demand": {"S": ["research/applications/track-a/a19-t8c-distributed-shadow-gated-patch-activation.ice", "e0e0c2c3d6a6197ea37a4a3761451c292de3704c", 24876], "T": ["research/applications/track-a/a20-t8d-provisional-canary-patch-activation.ice", "746cd0518bf7c6fff27d0579b03ca0d89b3f6bd5", 22763], "U": ["research/applications/track-a/a21-t8e-out-of-sample-canary-replication.ice", "551f957a9b256ff5648c04364e5a4eb2af126e1c", 18315]},
    "orders": [["S", "T", "U"], ["U", "T", "S"]],
    "split": "Split each raw demand blob at floor(raw_byte_length/2) into permitted first half and untouched second half; split the permitted first half again at floor(first_half_length/2) into contiguous early and late cue blocks; every block and untouched second half uses independently reset raw four-byte context.",
    "freshness": "S/T/U have zero references in all preregistrations present at the exact parent; neither their scientific outcomes nor block scores have been observed in this lineage.",
    "contamination_rule": "Fitting, minimax scoring, and activation may use base blobs and encountered complete first halves only. Gate scoring may use only the evaluated domain's two first-half blocks. Untouched second halves are accessed only after phenotype construction and both block decisions are frozen."
  },
  "frozen_reuse": {
    "learner": "byte-identical experiment-029/034 previous-byte baseline, four-byte candidate statistics, occurrence>=12, consistency>=0.60, utility ranking, home hash, radius two, sixteen-cell development, candidate union, pooled successor rule, minimax ranking, and deterministic matching",
    "gate": "byte-identical experiment-034 two-block rule: select matched-minimax iff early-block and late-block correct-count differences from frozen are both nonnegative; ties remain nonnegative",
    "activation": "byte-identical experiment-029/034 complete-first-half cue-contribution ranking selecting ten active records and retaining the complementary six records byte-exactly",
    "metrics": "byte-identical experiment-034 incremental-correct, covered-position accuracy, comparator, gate error, and integrity definitions"
  },
  "arms": {"frozen_full_control": "unchanged architecture-only sixteen-motif phenotype", "matched_minimax_full_control": "unchanged sixteen-motif matched-minimax adaptation mechanism applied to S/T/U", "independent_adapted_full_control": "per-domain phenotype fitted from base blobs plus only that domain's first half", "pooled_cumulative_full_control": "unchanged pooled cumulative comparator", "two_block_gate_primary": "frozen experiment-034 two-block selection between frozen-full and matched-minimax-full", "gated_ten_active_primary": "top ten selected-full records by unchanged complete-first-half ranking; six complementary records retained byte-exactly"},
  "seeds": {"randomness": "none", "seed_list": [], "determinism": "all identities, orders, splits, fitting, rankings, matching, block comparisons, and selection rules are fixed; two complete executions must be byte-identical"},
  "budgets": {"base_training_files": 4, "demand_files": 3, "encounter_orders": 2, "stages_per_order": 3, "seen_domain_evaluation_rows": 12, "cue_blocks_per_row": 2, "cell_count": 16, "active_structure_count": 10, "retained_structure_count": 6, "primary_runs": 2, "maximum_source_processes": 1, "timeout_seconds": 1800, "network_access": false, "capacity_growth_events": 0},
  "metrics_and_thresholds": [
    ["training_file_identity_mismatch_count", "==", 0], ["evaluation_file_identity_mismatch_count", "==", 0], ["fresh_demand_preregistration_reference_count", "==", 0], ["future_stage_adaptation_access_count", "==", 0], ["second_half_adaptation_access_count", "==", 0],
    ["valid_stage_count", "==", 6], ["valid_evaluation_row_count", "==", 12], ["valid_cue_block_count", "==", 24], ["matched_assignment_failure_count", "==", 0], ["minimum_selected_motif_count", "==", 16], ["maximum_selected_motif_count", "==", 16], ["matched_ineligible_candidate_count", "==", 0],
    ["two_block_gate_decision_count", "==", 12], ["two_block_false_retain_count", "==", 0],
    ["minimum_selected_incremental_correct_count", ">", 0], ["minimum_selected_minus_frozen_count", ">=", 0], ["minimum_selected_to_independent_fraction", ">=", 0.70], ["minimum_selected_minus_pooled_count", ">=", 0],
    ["minimum_active_retained_incremental_fraction", ">=", 0.70], ["minimum_eval_covered_accuracy_gain", ">", 0.0], ["retained_record_integrity_mismatch_count", "==", 0], ["state_partition_mismatch_count", "==", 0], ["capacity_growth_event_count", "==", 0], ["tokenizer_use_count", "==", 0], ["invalid_evaluation_rows", "==", 0]
  ],
  "controls": [
    "Reuse the sealed learner chain without altering its learner, candidate union, pooled successor rule, minimax ranking, matching, splits, capacity, or ten-active partition.",
    "The only scientific delta from 034 is replacement of M/N/O with fresh S/T/U; the two-block gate, tie rule, and all scientific thresholds remain unchanged.",
    "Split each first half by integer floor once, with no dropped or duplicated byte, and independently reset raw context for each block and arm.",
    "Record false retain when the gate selects matched-minimax and its untouched-second-half difference is negative; record false revert when it selects frozen and the difference is nonnegative.",
    "Every selected phenotype contains sixteen records partitioned into exactly ten active plus six byte-exact retained records using the unchanged complete-first-half ranking.",
    "Cell count, radius, hashes, active ceiling, retained count, budgets, total capacity, and collateral thresholds remain frozen. Gate reversion is measured but not required because absence of a harmful candidate on fresh data is scientifically valid."
  ],
  "validity_criteria": [
    "Exact parent, North Star, experiment-034 evidence identity, source dependencies, input blobs, sizes, and zero prior preregistration references for S/T/U match.",
    "Exactly twelve evaluation rows and twenty-four nonempty cue blocks are scored under the frozen unanimity and tie rules.",
    "No untouched-second-half or future-stage bytes enter fitting, ranking, matching, block scoring, selection, or activation.",
    "Every stage assigns sixteen matched-minimax motifs and every selected phenotype partitions exactly ten active plus six byte-exact retained records.",
    "All metrics are finite and two complete executions are byte-identical.",
    "No tokenizer, external model, network access, radius widening, capacity growth, or state carry between order arms occurs."
  ],
  "classification_rules": {
    "supported": "Validity passes, no false retain occurs, and every frozen-benefit, comparator, 0.70 retention, covered-gain, integrity, and fixed-capacity threshold passes.",
    "mixed": "Validity passes and the two-block gate has no false retain, but at least one false revert or collateral/comparator/retention threshold fails.",
    "null": "Validity passes, every matched-minimax versus frozen evaluation difference is zero, and selected benefit is never negative.",
    "negative": "Validity passes but any false retain occurs, selected benefit is negative on any row, selected benefit is nonpositive on at least two rows, or active retained benefit falls below 0.50 on any row.",
    "incomplete": "Compute interruption prevents both deterministic executions, all six stages, twelve evaluation rows, or twenty-four block scores.",
    "invalid": "Any identity, freshness, isolation, determinism, matching, block-partition, gate-integrity, fixed-capacity, finiteness, partition-integrity, or qualification criterion fails."
  },
  "stop_conditions": ["Stop invalid before scientific evaluation on any identity, lineage, dependency, freshness, size, or source mismatch.", "Stop invalid on forbidden byte access, empty/malformed block, gate mismatch, matching failure, partition corruption, capacity growth, non-finite metric, or nondeterministic duplicate output.", "Do not stop early for apparent supported, mixed, null, or negative outcomes.", "After any output is observed, do not repair or rerun under this experiment identifier."],
  "no_post_result_tuning_rule": "After any primary or diagnostic output is observed, do not alter inputs, splits, orders, learner, controls, block definition, gate or tie rule, scoring, ranking, matching, active ceiling, budgets, metrics, thresholds, aggregation, validity, classification, or stopping rules under this experiment identifier."
}
