{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-FRESH-DOMAIN-TEN-ACTIVE-REPLICATION-022",
  "program": "DG1 real-byte adaptive granularity",
  "question": "Does the frozen ten-active matched-minimax boundary from experiment 021 replicate without capacity growth on three previously unevaluated Track-A text domains?",
  "hypothesis": "Across both forward and reverse encounters of fresh domains J/K/L, the unchanged matched-minimax mechanism will retain at least 70% of full second-half incremental-correct benefit on every seen-domain evaluation with exactly ten active and six byte-exact retained records, while maintaining positive full-phenotype benefit, improvement over the frozen architecture-only phenotype, at least 70% of independent-adaptation and first-encounter benefit, parity with or improvement over the pooled cumulative comparator, positive covered-position accuracy gain, order-invariant final records, and fixed sixteen-cell capacity.",
  "exact_parent_sha": "28236c121d04198ad2d3911ba9a7f078c62d1195",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-FRESH-DOMAIN-TEN-ACTIVE-BOUNDARY-021",
    "classification": "supported-by-frozen-rules",
    "qualification_run_id": "38516999507",
    "result_sha256": "42a9a6a93e42d39f6a57563ffd0ae47c9ed1e5ed97d24a224e9a872452a00651",
    "observation": "On reused G/H/I domains, ten active motifs retained a minimum 0.8113207547169812 of full benefit and crossed the frozen 0.70 boundary, with minimum full benefit 59, frozen-control improvement 37, independent retention 1.0, prior-domain retention 0.9605911330049262, positive covered accuracy gain, exact state integrity, and no capacity growth. Replication on fresh domains remains unknown."
  },
  "authority": "synthetic research-only evaluation on immutable repo-owned bytes; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": ["research/experiments/exp-dgr-real-utf8-fresh-domain-ten-active-replication-022.ice", "research/applications/plane/exp-dgr-real-utf8-fresh-domain-ten-active-replication-022.py", ".yggdrasil/qualification-request.json", ".yggdrasil/isolated-run.json"],
  "inputs": {
    "base_training": [["research/architecture/measurement-framework.ice", "6374fc3c39ee821c8f9d565bb7de0875c07d5cdc", 10040], ["research/architecture/structural-plasticity.ice", "d2d75b4ed60e0c112de5202ba31848b15081e0cb", 9550], ["research/architecture/developmental-substrate-v0.2.ice", "52d6e87e2339bdf586c33da22470e38a9ca27785", 8448], ["research/architecture/yggdrasil-north-star.ice", "84358ec54c0e7eba6b6f830e0b4d2755920281cb", 8411]],
    "fresh_demand": {"J": ["research/applications/track-a/a10-t3-developmental-prior-plasticity.ice", "0a1bf7890124b7575a02e18b08a7dcbb77c4062d", 26598], "K": ["research/applications/track-a/a11-t4-context-conditional-developmental-memory.ice", "64241601e36ad0f5b256776cc0544be64449b2d5", 25417], "L": ["research/applications/track-a/a12-t5-latent-context-inference.ice", "0bde99a15fc25e38abd9048c8a8ba35074c54782", 22454]},
    "orders": [["J", "K", "L"], ["L", "K", "J"]],
    "encoding": "identity file bytes; no UTF decoding, normalization, tokenizer, vocabulary, separator, boundary label, or remapping",
    "split": "each fresh blob is split at floor(raw_byte_length/2), with raw four-byte context reset at every second-half evaluation",
    "freshness": "J/K/L were not scientific inputs to experiments 001-021 and no algorithmic output on them was observed before this preregistration",
    "contamination_rule": "At each stage, fitting and minimax scoring may use base blobs and only first halves encountered through that stage. No second-half or future first-half byte may enter fitting, selection, matching, or activation."
  },
  "frozen_reuse": {
    "source_logic": "byte-identical experiment-021 learner, controls, candidate union, pooled successor rule, minimax scoring and ranking, feasibility-preserving matching, evaluation, record encoding, selector, and metric definitions",
    "only_scientific_delta": "replace sealed G/H/I inputs and labels with fresh J/K/L inputs and labels; ACTIVE_CEILING remains 10 and retained count remains 6",
    "full_phenotype": "sixteen matched-minimax records at every stage",
    "selector": "unchanged domain-first-half incremental-correct contribution, training utility, and raw-key tie breaks from 021"
  },
  "arms": {
    "frozen_full_control": "unchanged architecture-only sixteen-motif phenotype",
    "independent_adapted_full_control": "per-domain sixteen-motif phenotype fitted to base blobs plus only that domain's first half",
    "pooled_cumulative_full_control": "sixteen-motif phenotype fitted to base blobs plus all encountered first halves without minimax selection",
    "matched_minimax_full_reference": "sixteen motifs chosen by the frozen minimax ranking and feasibility-preserving matching",
    "matched_minimax_ten_primary": "top ten matched-minimax motifs selected from the evaluated domain's first half; other six records retained byte-exactly",
    "sealed_021_historical_control": "sealed G/H/I minimum retained-benefit fraction 0.8113207547169812; not recomputed or used for selection"
  },
  "seeds": {"randomness": "none", "seed_list": [], "determinism": "all identities, orders, splits, rankings, tie breaks, matching, and activation are fixed; two complete executions must be byte-identical"},
  "budgets": {"base_training_files": 4, "fresh_demand_files": 3, "encounter_orders": 2, "stages_per_order": 3, "seen_domain_evaluation_rows": 12, "cell_count": 16, "active_structure_count": 10, "retained_structure_count": 6, "primary_runs": 2, "maximum_source_processes": 1, "timeout_seconds": 1800, "network_access": false, "capacity_growth_events": 0},
  "metrics_and_thresholds": [
    ["training_file_identity_mismatch_count", "==", 0], ["evaluation_file_identity_mismatch_count", "==", 0], ["future_stage_adaptation_access_count", "==", 0], ["second_half_adaptation_access_count", "==", 0],
    ["valid_stage_count", "==", 6], ["valid_seen_domain_evaluation_count", "==", 12], ["matched_assignment_failure_count", "==", 0], ["minimum_selected_motif_count", "==", 16], ["maximum_selected_motif_count", "==", 16], ["matched_ineligible_candidate_count", "==", 0],
    ["minimum_minimax_full_incremental_correct_count", ">", 0], ["minimum_minimax_minus_frozen_incremental_correct_count", ">", 0], ["minimum_minimax_to_independent_incremental_correct_fraction", ">=", 0.70],
    ["minimum_prior_domain_minimax_incremental_correct_count", ">", 0], ["minimum_prior_domain_minimax_to_at_first_encounter_fraction", ">=", 0.70], ["minimum_minimax_minus_pooled_incremental_correct_count", ">=", 0], ["final_order_record_mismatch_count", "==", 0],
    ["minimum_primary_active_structure_count", "==", 10], ["maximum_primary_active_structure_count", "==", 10], ["minimum_primary_retained_structure_count", "==", 6], ["maximum_primary_retained_structure_count", "==", 6],
    ["minimum_primary_retained_incremental_correct_fraction", ">=", 0.70], ["minimum_eval_covered_accuracy_gain", ">", 0.0], ["retained_record_integrity_mismatch_count", "==", 0], ["state_partition_mismatch_count", "==", 0],
    ["capacity_growth_event_count", "==", 0], ["tokenizer_use_count", "==", 0], ["invalid_evaluation_rows", "==", 0]
  ],
  "controls": [
    "Every arm for a domain is evaluated on identical untouched second-half bytes with reset context and the unchanged base-trained previous-byte baseline.",
    "Each order starts independently; only encountered first halves accumulate, and earlier second halves remain evaluation-only.",
    "Frozen-full receives no fresh demand bytes; independent controls receive only their own first half; pooled and minimax arms receive identical stage data.",
    "Forward and reverse final learners receive the same multiset, providing an order-invariance control.",
    "Every evaluation partitions all sixteen records into exactly ten active plus six byte-exact retained records.",
    "Cell count, active ceiling, radius, hashes, candidate thresholds, matching, budgets, and capacity remain frozen."
  ],
  "validity_criteria": [
    "Exact parent, North Star, experiment-021 evidence identity, source dependencies, all input blob identities, and sizes match.",
    "No scientific output for J/K/L predates this preregistration commit.",
    "Implementation logic differs from 021 only in experiment identity, exact-parent validation if present, fresh demand identities, labels, and orders.",
    "No second-half or future-stage bytes enter adaptation, ranking, matching, or activation.",
    "Every stage assigns sixteen motifs and every evaluation partitions ten active plus six byte-exact retained records.",
    "All metrics are finite and two complete executions are byte-identical.",
    "No tokenizer, external model, network access, radius widening, capacity growth, or state carry between order arms occurs."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all frozen thresholds pass on J/K/L.",
    "mixed": "Validity passes and every full minimax evaluation remains positive, but at least one improvement, comparator, 0.70 retention, covered-gain, order-invariance, or active-partition threshold fails.",
    "null": "Validity passes but minimax full benefit or ten-active retained benefit is zero on at least one evaluation and never negative.",
    "negative": "Validity passes but minimax full benefit or ten-active retained benefit is negative on any evaluation, full minimax benefit is nonpositive on at least two evaluations, or prior-domain retention falls below 0.50.",
    "incomplete": "Compute interruption prevents both deterministic executions, all six stages, or all twelve evaluations.",
    "invalid": "Any identity, freshness, isolation, determinism, matching, fixed-capacity, finiteness, partition-integrity, or qualification criterion fails."
  },
  "stop_conditions": [
    "Stop invalid before scientific evaluation on any identity, lineage, dependency, freshness, or size mismatch.",
    "Stop invalid on forbidden byte access, matching failure, partition corruption, capacity growth, non-finite metric, or nondeterministic duplicate output.",
    "Do not stop early for apparent supported, mixed, null, or negative outcomes.",
    "After any output is observed, do not repair or rerun under this experiment identifier."
  ],
  "no_post_result_tuning_rule": "After any primary or diagnostic output is observed, do not alter files, splits, orders, learner, controls, candidate union, scoring, ranking, matching, active ceiling, budgets, metrics, thresholds, aggregation, validity, classification, or stopping rules under this experiment identifier."
}
