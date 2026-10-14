{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-RETAIN-REVERT-GATE-023",
  "program": "DG1 real-byte adaptive granularity",
  "question": "On the sealed J/K/L lineage from experiment 022, can a pre-evaluation first-half retain/revert gate prevent matched-minimax collateral regression against the frozen phenotype while preserving positive adaptation and the validated ten-active partition?",
  "hypothesis": "For every seen-domain evaluation in both frozen encounter orders, selecting the matched-minimax phenotype only when its reset-context first-half correct count is at least the frozen phenotype's, and otherwise retaining the frozen phenotype, will make gated full-phenotype improvement over frozen nonnegative, keep gated full benefit positive, preserve at least 70% of independent-adaptation benefit and first-encounter gated benefit, and retain at least 70% of the selected full phenotype's benefit with exactly ten active and six byte-exact retained records, without capacity growth.",
  "exact_parent_sha": "872095dd3f62e80d794fc39c5d100195b8a92eab",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-FRESH-DOMAIN-TEN-ACTIVE-REPLICATION-022",
    "classification": "mixed-by-frozen-rules",
    "qualification_run_id": "38551066146",
    "result_sha256": "bcb74511aa01dc21e3ac2fb99d15b94d2472cc6ed580ad367f17033bd771cba0",
    "observation": "Validity and fixed-capacity integrity passed; ten active motifs retained at least 0.8870292887029289 of full benefit, full benefit remained at least 133, independent retention was 1.0, prior-domain retention was 0.9707112970711297, and pooled parity held, but minimum full matched-minimax improvement over frozen was -6. The location and behavior of that collateral regression are now observed; this is a within-lineage mechanism test, not a fresh-domain replication."
  },
  "authority": "synthetic research-only evaluation on immutable repo-owned bytes; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": ["research/experiments/exp-dgr-real-utf8-retain-revert-gate-023.ice", "research/applications/plane/exp-dgr-real-utf8-retain-revert-gate-023.py", ".yggdrasil/qualification-request.json", ".yggdrasil/isolated-run.json"],
  "inputs": {
    "base_training": [["research/architecture/measurement-framework.ice", "6374fc3c39ee821c8f9d565bb7de0875c07d5cdc", 10040], ["research/architecture/structural-plasticity.ice", "d2d75b4ed60e0c112de5202ba31848b15081e0cb", 9550], ["research/architecture/developmental-substrate-v0.2.ice", "52d6e87e2339bdf586c33da22470e38a9ca27785", 8448], ["research/architecture/yggdrasil-north-star.ice", "84358ec54c0e7eba6b6f830e0b4d2755920281cb", 8411]],
    "demand": {"J": ["research/applications/track-a/a10-t3-developmental-prior-plasticity.ice", "0a1bf7890124b7575a02e18b08a7dcbb77c4062d", 26598], "K": ["research/applications/track-a/a11-t4-context-conditional-developmental-memory.ice", "64241601e36ad0f5b256776cc0544be64449b2d5", 25417], "L": ["research/applications/track-a/a12-t5-latent-context-inference.ice", "0bde99a15fc25e38abd9048c8a8ba35074c54782", 22454]},
    "orders": [["J", "K", "L"], ["L", "K", "J"]],
    "encoding": "identity file bytes; no UTF decoding, normalization, tokenizer, vocabulary, separator, boundary label, or remapping",
    "split": "each blob is split at floor(raw_byte_length/2); the first half is the adaptation and gate cue, and the untouched second half is evaluation-only; raw four-byte context resets independently for gate scoring and every evaluation",
    "reuse_disclosure": "J/K/L and experiment-022 outcomes have been observed. No claim of fresh replication is made.",
    "contamination_rule": "At each stage, fitting, minimax scoring, activation, and the retain/revert gate may use base blobs and only first halves encountered through that stage. No second-half or future first-half byte may enter any decision."
  },
  "frozen_reuse": {
    "source_logic": "byte-identical experiment-022 learner, controls, candidate union, pooled successor rule, minimax scoring and ranking, feasibility-preserving matching, evaluation, record encoding, ten-active selector, and underlying metric definitions",
    "only_scientific_delta": "before each second-half evaluation, compare frozen-full and matched-minimax-full raw correct counts on that domain's first half with reset context; select matched-minimax on a tie or win and frozen on a loss; apply the unchanged ten-active selector to the selected sixteen-record phenotype",
    "gate": "selected_full = matched_minimax_full iff cue_minimax_correct >= cue_frozen_correct, else frozen_full; no margin, learned parameter, threshold search, second-half access, or order-specific rule",
    "frozen_rows": "the frozen phenotype's sixteen rows are encoded with the same known-row function and current shared statistics before ten-active selection"
  },
  "arms": {
    "frozen_full_control": "unchanged architecture-only sixteen-motif phenotype",
    "ungated_matched_minimax_control": "unchanged experiment-022 full phenotype, retained to reproduce and localize the sealed collateral regression",
    "independent_adapted_full_control": "unchanged per-domain experiment-022 control",
    "pooled_cumulative_full_control": "unchanged experiment-022 comparator",
    "gated_full_primary": "deterministic first-half retain/revert selection between frozen-full and matched-minimax-full",
    "gated_ten_active_primary": "top ten records of the selected full phenotype by the unchanged cue contribution, utility, and raw-key ranking; six complementary records retained byte-exactly"
  },
  "seeds": {"randomness": "none", "seed_list": [], "determinism": "all identities, orders, splits, fitting, rankings, matching, gate comparisons, and activation are fixed; two complete executions must be byte-identical"},
  "budgets": {"base_training_files": 4, "demand_files": 3, "encounter_orders": 2, "stages_per_order": 3, "seen_domain_evaluation_rows": 12, "cell_count": 16, "active_structure_count": 10, "retained_structure_count": 6, "primary_runs": 2, "maximum_source_processes": 1, "timeout_seconds": 1800, "network_access": false, "capacity_growth_events": 0},
  "metrics_and_thresholds": [
    ["training_file_identity_mismatch_count", "==", 0], ["evaluation_file_identity_mismatch_count", "==", 0], ["future_stage_adaptation_access_count", "==", 0], ["second_half_adaptation_access_count", "==", 0],
    ["valid_stage_count", "==", 6], ["valid_seen_domain_evaluation_count", "==", 12], ["matched_assignment_failure_count", "==", 0], ["minimum_selected_motif_count", "==", 16], ["maximum_selected_motif_count", "==", 16], ["matched_ineligible_candidate_count", "==", 0],
    ["minimum_ungated_minimax_full_incremental_correct_count", ">", 0], ["minimum_ungated_minimax_minus_frozen_incremental_correct_count", "==", -6], ["minimum_gated_full_incremental_correct_count", ">", 0], ["minimum_gated_minus_frozen_incremental_correct_count", ">=", 0],
    ["minimum_gated_to_independent_incremental_correct_fraction", ">=", 0.70], ["minimum_prior_domain_gated_incremental_correct_count", ">", 0], ["minimum_prior_domain_gated_to_at_first_encounter_fraction", ">=", 0.70], ["minimum_gated_minus_pooled_incremental_correct_count", ">=", 0],
    ["gate_decision_count", "==", 12], ["gate_revert_count", ">=", 1], ["gate_decision_mismatch_count", "==", 0], ["final_order_record_mismatch_count", "==", 0],
    ["minimum_primary_active_structure_count", "==", 10], ["maximum_primary_active_structure_count", "==", 10], ["minimum_primary_retained_structure_count", "==", 6], ["maximum_primary_retained_structure_count", "==", 6],
    ["minimum_primary_retained_incremental_correct_fraction", ">=", 0.70], ["minimum_eval_covered_accuracy_gain", ">", 0.0], ["retained_record_integrity_mismatch_count", "==", 0], ["state_partition_mismatch_count", "==", 0],
    ["capacity_growth_event_count", "==", 0], ["tokenizer_use_count", "==", 0], ["invalid_evaluation_rows", "==", 0]
  ],
  "controls": [
    "All arms use the same untouched second halves, reset evaluation context, and unchanged base-trained previous-byte baseline as 022.",
    "The gate sees only the current domain's already-permitted first half, scored with independently reset context; second-half outcomes cannot affect selection.",
    "The ungated arm must reproduce the sealed -6 minimum difference, distinguishing a gate effect from learner drift.",
    "Each order starts independently; only encountered first halves accumulate, and earlier second halves remain evaluation-only.",
    "Both possible selected phenotypes contain exactly sixteen records and are partitioned into exactly ten active plus six byte-exact retained records.",
    "Cell count, radius, hashes, thresholds, matching, active ceiling, budgets, inputs, and total capacity remain frozen."
  ],
  "validity_criteria": [
    "Exact parent, North Star, experiment-022 evidence identity, source dependencies, input blobs, and sizes match.",
    "Implementation logic differs from 022 only by experiment identity, exact-parent validation if present, gate metrics, the frozen-row representation, and the frozen first-half gate plus downstream selected-phenotype evaluation.",
    "The ungated sealed minimum full benefit and minimum difference from frozen reproduce as 133 and -6 respectively.",
    "No second-half or future-stage bytes enter fitting, ranking, matching, gating, or activation.",
    "Every stage assigns sixteen minimax motifs and every selected phenotype partitions exactly ten active plus six byte-exact retained records.",
    "Every recorded gate decision equals the frozen rule applied to independently recomputed first-half correct counts.",
    "All metrics are finite and two complete executions are byte-identical.",
    "No tokenizer, external model, network access, radius widening, capacity growth, or state carry between order arms occurs."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all frozen thresholds pass.",
    "mixed": "Validity passes and gated full benefit remains positive everywhere, but at least one collateral, comparator, 0.70 retention, covered-gain, order-invariance, gate-use, or active-partition threshold fails.",
    "null": "Validity passes but gated full or ten-active benefit is zero on at least one evaluation and never negative.",
    "negative": "Validity passes but gated full or ten-active benefit is negative on any evaluation, gated full benefit is nonpositive on at least two evaluations, or prior-domain gated retention falls below 0.50.",
    "incomplete": "Compute interruption prevents both deterministic executions, all six stages, or all twelve evaluations.",
    "invalid": "Any identity, isolation, sealed-control reproduction, determinism, gate integrity, matching, fixed-capacity, finiteness, partition-integrity, or qualification criterion fails."
  },
  "stop_conditions": [
    "Stop invalid before scientific evaluation on any identity, lineage, dependency, or size mismatch.",
    "Stop invalid on forbidden byte access, sealed-control mismatch, gate mismatch, matching failure, partition corruption, capacity growth, non-finite metric, or nondeterministic duplicate output.",
    "Do not stop early for apparent supported, mixed, null, or negative outcomes.",
    "After any output is observed, do not repair or rerun under this experiment identifier."
  ],
  "no_post_result_tuning_rule": "After any primary or diagnostic output is observed, do not alter files, splits, orders, learner, controls, gate rule or tie handling, scoring, ranking, matching, active ceiling, budgets, metrics, thresholds, aggregation, validity, classification, or stopping rules under this experiment identifier."
}
