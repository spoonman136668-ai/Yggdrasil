{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-GATE-032",
  "program": "DG1 real-byte adaptive granularity",
  "question": "On the sealed fresh M/N/O lineage from experiments 029-030, does a frozen two-block unanimity gate over the already-permitted first half prevent every negative untouched-second-half matched-minimax choice while preserving fixed-capacity benefit?",
  "hypothesis": "Selecting matched-minimax only when its reset-context correct-count difference from frozen is nonnegative in both contiguous blocks of the permitted first half will produce no false retains across the twelve seen-domain evaluations, will revert at least once, and will leave every selected untouched-second-half incremental benefit positive and noninferior to frozen, without capacity growth.",
  "exact_parent_sha": "a300f4b4c0a3b6a25057ddfe5c89039fff089214",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-RETAIN-REVERT-CUE-CONCORDANCE-030",
    "classification": "negative-by-frozen-rules",
    "qualification_run_id": "38554836389",
    "result_sha256": "a8646b60575e49640b26fa5f16c6ba8311960a5dcbc824df9d281bf6ba4589df",
    "observation": "All validity controls passed and first-half versus untouched-second-half sign concordance was 11/12, but one positive cue was a false retain against a negative evaluation difference. The within-first-half stability of that cue is unobserved."
  },
  "blocked_predecessor": {
    "experiment": "EXP-DGR-REAL-UTF8-TWO-BLOCK-RETAIN-REVERT-GATE-031",
    "preregistration_commit": "29091b6afc3cf889628a1bc6e8a6721da82e82f7",
    "blocker_record_commit": "a300f4b4c0a3b6a25057ddfe5c89039fff089214",
    "status": "preregistered-blocked; no implementation, run, scientific output, or scientific claim",
    "continuation_rule": "032 preserves the 031 scientific design and changes only experiment identity, exact parent, and provenance needed to resume after the infrastructure-only block."
  },
  "authority": "synthetic research-only diagnostic on immutable repo-owned bytes; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": ["research/experiments/exp-dgr-real-utf8-two-block-retain-revert-gate-032.ice", "research/applications/plane/exp-dgr-real-utf8-two-block-retain-revert-gate-032.py", ".yggdrasil/qualification-request.json", ".yggdrasil/isolated-run.json"],
  "inputs": {
    "base_training": [["research/architecture/measurement-framework.ice", "6374fc3c39ee821c8f9d565bb7de0875c07d5cdc", 10040], ["research/architecture/structural-plasticity.ice", "d2d75b4ed60e0c112de5202ba31848b15081e0cb", 9550], ["research/architecture/developmental-substrate-v0.2.ice", "52d6e87e2339bdf586c33da22470e38a9ca27785", 8448], ["research/architecture/yggdrasil-north-star.ice", "84358ec54c0e7eba6b6f830e0b4d2755920281cb", 8411]],
    "demand": {"M": ["research/applications/track-a/a13-t6-bounded-novel-context-discovery.ice", "c48fe4c06b50e5dc18b0013967d8074b33a17bad", 22805], "N": ["research/applications/track-a/a14-t6-strict-bounded-novel-context-creation.ice", "597a641af867f3f4f4e73b9df14289846516e68b", 32552], "O": ["research/applications/track-a/a15-t7-versioned-context-revision.ice", "113bc2bc8b436555d586655561e92235b5b2f333", 40412]},
    "orders": [["M", "N", "O"], ["O", "N", "M"]],
    "split": "byte-identical experiment-029 floor(raw_byte_length/2) adaptation/evaluation split; split the permitted first half again at floor(first_half_length/2) into contiguous early and late cue blocks; every block and untouched second half uses independently reset raw four-byte context",
    "reuse_disclosure": "M/N/O and aggregate experiments 029-030 outcomes are observed. No block-specific cue output has been observed. This is a preregistered within-lineage gate diagnostic, not fresh-domain generalization.",
    "contamination_rule": "Fitting, minimax scoring, and activation may use base blobs and encountered complete first halves exactly as in 029. Gate scoring may use only the evaluated domain's two first-half blocks. Untouched second halves are accessed only after phenotype construction and both block decisions are frozen."
  },
  "arms": {"frozen_full_control": "unchanged architecture-only sixteen-motif phenotype from 029", "matched_minimax_full_control": "unchanged sixteen-motif matched-minimax phenotype from 029", "sealed_single_cue_control": "reproduce experiment-030 aggregate cue/evaluation results exactly", "two_block_gate_primary": "select matched-minimax iff both early-block and late-block differences (matched-minimax correct minus frozen correct) are nonnegative; otherwise select frozen; ties remain nonnegative"},
  "seeds": {"randomness": "none", "seed_list": [], "determinism": "all identities, orders, splits, fitting, rankings, matching, block comparisons, and selection rules are fixed; two complete executions must be byte-identical"},
  "budgets": {"base_training_files": 4, "demand_files": 3, "encounter_orders": 2, "stages_per_order": 3, "seen_domain_evaluation_rows": 12, "cue_blocks_per_row": 2, "cell_count": 16, "active_structure_count": 10, "retained_structure_count": 6, "primary_runs": 2, "maximum_source_processes": 1, "timeout_seconds": 1800, "network_access": false, "capacity_growth_events": 0},
  "metrics_and_thresholds": [
    ["training_file_identity_mismatch_count", "==", 0], ["evaluation_file_identity_mismatch_count", "==", 0], ["future_stage_adaptation_access_count", "==", 0], ["second_half_adaptation_access_count", "==", 0],
    ["valid_stage_count", "==", 6], ["valid_evaluation_row_count", "==", 12], ["valid_cue_block_count", "==", 24], ["matched_assignment_failure_count", "==", 0], ["minimum_selected_motif_count", "==", 16], ["maximum_selected_motif_count", "==", 16], ["matched_ineligible_candidate_count", "==", 0],
    ["sealed_minimum_ungated_incremental_correct_count", "==", 64], ["sealed_minimum_ungated_minus_frozen_count", "==", -12], ["sealed_single_cue_concordance_fraction", "==", 0.9166666666666666], ["sealed_single_cue_false_retain_count", "==", 1],
    ["two_block_gate_decision_count", "==", 12], ["two_block_gate_revert_count", ">=", 1], ["two_block_false_retain_count", "==", 0], ["two_block_false_revert_count", "==", 0],
    ["minimum_selected_incremental_correct_count", ">", 0], ["minimum_selected_minus_frozen_count", ">=", 0], ["minimum_selected_to_independent_fraction", ">=", 0.70], ["minimum_selected_minus_pooled_count", ">=", 0],
    ["minimum_active_retained_incremental_fraction", ">=", 0.70], ["minimum_eval_covered_accuracy_gain", ">", 0.0], ["retained_record_integrity_mismatch_count", "==", 0], ["state_partition_mismatch_count", "==", 0], ["capacity_growth_event_count", "==", 0], ["invalid_evaluation_rows", "==", 0]
  ],
  "controls": [
    "Import and execute the sealed experiment-029 learner chain without altering its learner, candidate union, pooled successor rule, minimax ranking, matching, splits, orders, capacity, or ten-active partition.",
    "Reproduce the sealed experiment-029 aggregate controls and experiment-030 single-cue aggregate diagnostic before interpreting the two-block gate.",
    "The only scientific delta is the gate input partition and fixed unanimity rule; the first-half bytes available to the gate do not increase.",
    "Split each first half by integer floor once, with no dropped or duplicated byte, and independently reset raw context for each block and arm.",
    "Record false retain when the two-block gate selects matched-minimax and its untouched-second-half difference is negative; record false revert when it selects frozen and the difference is nonnegative.",
    "Every selected phenotype contains sixteen records partitioned into exactly ten active plus six byte-exact retained records using the unchanged 029 cue-contribution ranking on the complete first half.",
    "Cell count, radius, hashes, active ceiling, retained count, budgets, total capacity, and all collateral thresholds remain frozen."
  ],
  "validity_criteria": [
    "Exact parent, North Star, experiments 029-030 evidence identities, source dependencies, input blobs, and sizes match.",
    "All sealed controls reproduce exactly, including minimum ungated benefit 64, minimum ungated-minus-frozen -12, single-cue concordance 11/12, and one single-cue false retain.",
    "Exactly twelve evaluation rows and twenty-four nonempty cue blocks are scored under the frozen unanimity and tie rules.",
    "No untouched-second-half or future-stage bytes enter fitting, ranking, matching, block scoring, selection, or activation.",
    "Every stage assigns sixteen matched-minimax motifs and every selected phenotype partitions exactly ten active plus six byte-exact retained records.",
    "All metrics are finite and two complete executions are byte-identical.",
    "No tokenizer, external model, network access, radius widening, capacity growth, or state carry between order arms occurs."
  ],
  "classification_rules": {
    "supported": "Validity passes, at least one revert occurs, no false retain or false revert occurs, and every frozen benefit, comparator, 0.70 retention, covered-gain, integrity, and fixed-capacity threshold passes.",
    "mixed": "Validity passes and the two-block gate has no false retain, but at least one false revert or collateral/comparator/retention threshold fails.",
    "null": "Validity passes, the two-block gate makes no different selection from the sealed single-cue gate, and the false-retain count remains one.",
    "negative": "Validity passes but any false retain remains, selected benefit is negative on any row, or selected benefit is nonpositive on at least two rows.",
    "incomplete": "Compute interruption prevents both deterministic executions, all six stages, twelve evaluation rows, or twenty-four block scores.",
    "invalid": "Any identity, isolation, sealed-control reproduction, determinism, matching, block-partition, gate-integrity, fixed-capacity, finiteness, partition-integrity, or qualification criterion fails."
  },
  "stop_conditions": ["Stop invalid before scientific evaluation on any identity, lineage, dependency, size, or sealed-control mismatch.", "Stop invalid on forbidden byte access, empty/malformed block, gate mismatch, matching failure, partition corruption, capacity growth, non-finite metric, or nondeterministic duplicate output.", "Do not stop early for apparent supported, mixed, null, or negative outcomes.", "After any output is observed, do not repair or rerun under this experiment identifier."],
  "no_post_result_tuning_rule": "After any primary or diagnostic output is observed, do not alter inputs, splits, orders, learner, controls, block definition, gate or tie rule, scoring, ranking, matching, active ceiling, budgets, metrics, thresholds, aggregation, validity, classification, or stopping rules under this experiment identifier."
}
