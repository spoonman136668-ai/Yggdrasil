{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-FRESH-DOMAIN-REPLICATION-018",
  "program": "DG1 real-byte adaptive granularity",
  "question": "Does the frozen experiment-016 minimax-matched consolidation mechanism replicate without capacity growth on three previously unevaluated Track-A text domains?",
  "hypothesis": "Across both forward and reverse encounters of fresh domains G/H/I, the frozen matched minimax mechanism will maintain positive full-phenotype benefit on every seen-domain second half, improve over the frozen architecture-only phenotype, retain at least 70% of independent-adaptation benefit and first-encounter benefit, match or exceed the pooled cumulative comparator, rescue at least one nonpositive pooled evaluation, and retain at least 70% of full benefit with exactly seven active and nine byte-exact retained records.",
  "exact_parent_sha": "7db8f3bd4a1df532a64990ec7c0c22844a30abd3",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "scientific_predecessor": {"experiment": "EXP-DGR-REAL-UTF8-MINIMAX-MATCHED-CONSOLIDATION-016", "classification": "supported-by-frozen-rules", "qualification_run_id": "37075511579", "result_sha256": "138d21335abc10e0eb7bddbbe5dd2a4e4b2ba5ea902d2319dc80eff637df2b29", "observation": "On reused A/B/C domains the feasibility-preserving matched minimax mechanism assigned sixteen motifs at all stages, preserved seven-active/nine-retained integrity, remained positive, matched or exceeded pooled benefit, and rescued two nonpositive pooled evaluations."},
    "procedural_predecessor": {"experiment": "EXP-DGR-REAL-UTF8-FRESH-DOMAIN-MATCHED-CONSOLIDATION-017", "classification": "preregistered-blocked", "blocker_run_id": "38369913117", "scientific_claim": false, "observation": "D/E/F output was exposed after a preregistration omission was detected; those domains and outputs are excluded from 018."}
  },
  "authority": "synthetic research-only evaluation on immutable repo-owned bytes; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": ["research/experiments/exp-dgr-real-utf8-fresh-domain-replication-018.ice", "research/applications/plane/exp-dgr-real-utf8-fresh-domain-replication-018.py", ".yggdrasil/qualification-request.json", ".yggdrasil/isolated-run.json"],
  "inputs": {
    "base_training": [["research/architecture/measurement-framework.ice", "6374fc3c39ee821c8f9d565bb7de0875c07d5cdc", 10040], ["research/architecture/structural-plasticity.ice", "d2d75b4ed60e0c112de5202ba31848b15081e0cb", 9550], ["research/architecture/developmental-substrate-v0.2.ice", "52d6e87e2339bdf586c33da22470e38a9ca27785", 8448], ["research/architecture/yggdrasil-north-star.ice", "84358ec54c0e7eba6b6f830e0b4d2755920281cb", 8411]],
    "fresh_demand": {"G": ["research/applications/track-a/a07-t1-experience-dependent-hereditary-learning.ice", "482bd1f5e28598f9e8d0155dd6112b2f8ab046d0", 27665], "H": ["research/applications/track-a/a08-t2-provenance-aware-noisy-training.ice", "d628806aa9513c827ea76d3032901b810b5b79b1", 37585], "I": ["research/applications/track-a/a09-t2b-distributed-cellular-training-memory.ice", "28284bebf5febaaa7724315908e73acf80be991e", 34169]},
    "orders": [["G", "H", "I"], ["I", "H", "G"]],
    "encoding": "identity file bytes; no UTF decoding, normalization, tokenizer, vocabulary, separator, boundary label, or remapping",
    "split": "each fresh blob is split at floor(raw_byte_length/2), with raw four-byte context reset at every second-half evaluation",
    "freshness": "G/H/I were not scientific inputs to experiments 001-017 and no algorithmic output on them was observed before this preregistration",
    "contamination_rule": "At each stage, fitting and minimax scoring may use base blobs and only first halves encountered through that stage. No second-half or future first-half byte may enter fitting, selection, matching, or activation."
  },
  "frozen_reuse": {
    "learner": "byte-identical previous-byte baseline, four-byte statistics, occurrence>=12, consistency>=0.60, utility, home hash, radius-two geometry, and sixteen-cell development from 016",
    "consolidation": "byte-identical pooled-plus-independent candidate union, pooled successor rule, descending minimum contribution then summed contribution then raw-key minimax ranking, feasibility-preserving matching, and local-cell order from 016",
    "activation": "byte-identical domain-first-half seven-active contribution selector and six-byte retained records from 016",
    "controls_and_metrics": "byte-identical frozen-full, independent-adaptation, pooled-full controls and all metric definitions from 016"
  },
  "arms": {
    "frozen_full_control": "unchanged architecture-only sixteen-motif phenotype",
    "independent_adapted_full_control": "per-domain sixteen-motif phenotype fitted to base blobs plus only that domain's first half",
    "pooled_cumulative_full_control": "sixteen-motif phenotype fitted to base blobs plus all encountered first halves without minimax selection",
    "matched_minimax_full_reference": "sixteen motifs chosen from pooled and independent candidates by frozen minimax ranking and feasibility-preserving radius-two matching",
    "matched_minimax_seven_primary": "top seven matched-minimax motifs selected from the evaluated domain's first half; other nine records retained byte-exactly"
  },
  "seeds": {"randomness": "none", "seed_list": [], "determinism": "all identities, orders, splits, rankings, tie breaks, and matching are fixed; two complete executions must be byte-identical"},
  "budgets": {"base_training_files": 4, "fresh_demand_files": 3, "encounter_orders": 2, "stages_per_order": 3, "seen_domain_evaluation_rows": 12, "cell_count": 16, "active_structure_count": 7, "retained_structure_count": 9, "primary_runs": 2, "maximum_source_processes": 1, "timeout_seconds": 1800, "network_access": false, "capacity_growth_events": 0},
  "metrics_and_thresholds": [
    ["training_file_identity_mismatch_count", "==", 0], ["evaluation_file_identity_mismatch_count", "==", 0], ["future_stage_adaptation_access_count", "==", 0], ["second_half_adaptation_access_count", "==", 0],
    ["valid_stage_count", "==", 6], ["valid_seen_domain_evaluation_count", "==", 12], ["matched_assignment_failure_count", "==", 0], ["minimum_selected_motif_count", "==", 16], ["maximum_selected_motif_count", "==", 16],
    ["matched_ineligible_candidate_count", "==", 0], ["matched_feasibility_skip_count", ">=", 0],
    ["minimum_minimax_full_incremental_correct_count", ">", 0], ["minimum_minimax_minus_frozen_incremental_correct_count", ">", 0], ["minimum_minimax_to_independent_incremental_correct_fraction", ">=", 0.70],
    ["minimum_prior_domain_minimax_incremental_correct_count", ">", 0], ["minimum_prior_domain_minimax_to_at_first_encounter_fraction", ">=", 0.70],
    ["minimum_minimax_minus_pooled_incremental_correct_count", ">=", 0], ["rescued_nonpositive_pooled_evaluation_count", ">=", 1], ["final_order_record_mismatch_count", "==", 0],
    ["minimum_primary_active_structure_count", "==", 7], ["maximum_primary_active_structure_count", "==", 7], ["minimum_primary_retained_structure_count", "==", 9], ["maximum_primary_retained_structure_count", "==", 9],
    ["minimum_primary_retained_incremental_correct_fraction", ">=", 0.70], ["minimum_eval_covered_accuracy_gain", ">", 0.0], ["retained_record_integrity_mismatch_count", "==", 0], ["state_partition_mismatch_count", "==", 0],
    ["capacity_growth_event_count", "==", 0], ["tokenizer_use_count", "==", 0], ["invalid_evaluation_rows", "==", 0]
  ],
  "controls": [
    "Every arm for a domain is evaluated on identical untouched second-half bytes with reset context and the unchanged base-trained previous-byte baseline.",
    "Each order starts independently; only encountered first halves accumulate, and earlier second halves remain evaluation-only.",
    "Frozen-full receives no fresh demand bytes; independent controls receive only their own first half; pooled and minimax arms receive identical stage data.",
    "Forward and reverse final learners receive the same multiset, providing an order-invariance control.",
    "Every evaluation partitions all sixteen records into exactly seven active plus nine byte-exact retained records.",
    "Cell count, active ceiling, radius, hashes, candidate thresholds, matching, budgets, and capacity remain frozen."
  ],
  "validity_criteria": [
    "Exact parent, North Star, 016 evidence identity, source dependencies, all input blob identities, and sizes match.",
    "No scientific output for G/H/I predates this preregistration commit.",
    "Implementation logic differs from 016 only in experiment identity, exact-parent validation, fresh demand identities, labels, and orders.",
    "No second-half or future-stage bytes enter adaptation, ranking, matching, or activation.",
    "Every stage assigns sixteen motifs and every evaluation partitions seven active plus nine byte-exact retained records.",
    "All metrics are finite and two complete executions are byte-identical.",
    "No tokenizer, external model, network access, radius widening, capacity growth, or state carry between order arms occurs."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all frozen thresholds pass on G/H/I.",
    "mixed": "Validity passes and every full minimax evaluation remains positive, but at least one improvement, comparator, 0.70 retention, covered-gain, rescue, or active-partition threshold fails.",
    "null": "Validity passes but minimax benefit is zero on at least one evaluation and never negative.",
    "negative": "Validity passes but minimax benefit is negative on any evaluation, is nonpositive on at least two evaluations, or prior-domain retention falls below 0.50.",
    "incomplete": "Compute interruption prevents both deterministic executions, all six stages, or all twelve evaluations.",
    "invalid": "Any identity, freshness, isolation, determinism, matching, fixed-capacity, finiteness, partition-integrity, or qualification criterion fails."
  },
  "stop_conditions": ["Stop invalid before scientific evaluation on any identity, lineage, dependency, freshness, or size mismatch.", "Stop invalid on forbidden byte access, matching failure, partition corruption, capacity growth, non-finite metric, or nondeterministic duplicate output.", "Do not stop early for apparent supported, mixed, null, or negative outcomes.", "After any output is observed, do not repair or rerun under this experiment identifier."],
  "no_post_result_tuning_rule": "After any primary or diagnostic output is observed, do not alter files, splits, orders, learner, controls, candidate union, scoring, ranking, matching, active ceiling, budgets, metrics, thresholds, aggregation, validity, classification, or stopping rules under this experiment identifier."
}
