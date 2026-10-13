{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-FRESH-DOMAIN-NINE-ACTIVE-BOUNDARY-020",
  "program": "DG1 real-byte adaptive granularity",
  "question": "On the sealed G/H/I domains from experiments 018-019, does increasing only the matched-minimax active partition from eight to nine motifs cross the frozen 70% full-benefit retention boundary under the same fixed sixteen-cell capacity?",
  "hypothesis": "Across both frozen G-H-I and I-H-G encounter orders, nine active matched-minimax motifs will retain at least 70% of full second-half incremental-correct benefit on every seen-domain evaluation, with exactly nine active and seven byte-exact retained records, while all full-phenotype, frozen-control, independent-adaptation, prior-domain, covered-accuracy, order-invariance, and fixed-capacity controls remain valid.",
  "exact_parent_sha": "12fc8fa6fb2c84fd90d8826de361f26e2a90ead7",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-FRESH-DOMAIN-EIGHT-ACTIVE-BOUNDARY-019",
    "classification": "mixed-by-frozen-rules",
    "qualification_run_id": "38431578055",
    "result_sha256": "6fd08c03f2fac82e27578733121af89e5c79e5efc56414625ac0882f9fffd59a",
    "observation": "Eight active motifs preserved exact state and increased minimum retained-benefit fraction from the sealed seven-active 0.4968553459119497 to 0.5660377358490566, but remained below 0.70. Full-phenotype minimum benefit was 59, frozen-control improvement 37, independent retention 1.0, prior-domain retention 0.9605911330049262, and covered accuracy gain 0.2883435582822086."
  },
  "authority": "synthetic research-only evaluation on immutable repo-owned bytes; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": ["research/experiments/exp-dgr-real-utf8-fresh-domain-nine-active-boundary-020.ice", "research/applications/plane/exp-dgr-real-utf8-fresh-domain-nine-active-boundary-020.py", ".yggdrasil/qualification-request.json", ".yggdrasil/isolated-run.json"],
  "inputs": {
    "base_training": [["research/architecture/measurement-framework.ice", "6374fc3c39ee821c8f9d565bb7de0875c07d5cdc", 10040], ["research/architecture/structural-plasticity.ice", "d2d75b4ed60e0c112de5202ba31848b15081e0cb", 9550], ["research/architecture/developmental-substrate-v0.2.ice", "52d6e87e2339bdf586c33da22470e38a9ca27785", 8448], ["research/architecture/yggdrasil-north-star.ice", "84358ec54c0e7eba6b6f830e0b4d2755920281cb", 8411]],
    "demand": {"G": ["research/applications/track-a/a07-t1-experience-dependent-hereditary-learning.ice", "482bd1f5e28598f9e8d0155dd6112b2f8ab046d0", 27665], "H": ["research/applications/track-a/a08-t2-provenance-aware-noisy-training.ice", "d628806aa9513c827ea76d3032901b810b5b79b1", 37585], "I": ["research/applications/track-a/a09-t2b-distributed-cellular-training-memory.ice", "28284bebf5febaaa7724315908e73acf80be991e", 34169]},
    "orders": [["G", "H", "I"], ["I", "H", "G"]],
    "encoding": "identity file bytes; no UTF decoding, normalization, tokenizer, vocabulary, separator, boundary label, or remapping",
    "split": "each blob is split at floor(raw_byte_length/2), with raw four-byte context reset at every second-half evaluation",
    "reuse_disclosure": "G/H/I and their 018-019 outcomes have been observed. This is a within-lineage active-capacity boundary test, not a fresh-domain replication claim.",
    "contamination_rule": "At each stage, fitting and minimax scoring may use base blobs and only first halves encountered through that stage. No second-half or future first-half byte may enter fitting, selection, matching, or activation."
  },
  "frozen_reuse": {
    "source_logic": "byte-identical experiment-019 learner, controls, candidate union, pooled successor rule, minimax scoring and ranking, feasibility-preserving matching, evaluation, record encoding, and metric definitions",
    "only_scientific_delta": "ACTIVE_CEILING changes from 8 to 9 and the complementary retained count changes from 8 to 7",
    "full_phenotype": "all sixteen matched-minimax rows remain unchanged",
    "selector": "unchanged domain-first-half incremental-correct contribution, training utility, and raw-key tie breaks from 019"
  },
  "arms": {
    "frozen_full_control": "unchanged architecture-only sixteen-motif phenotype",
    "independent_adapted_full_control": "unchanged per-domain experiment-019 control",
    "pooled_cumulative_full_control": "unchanged experiment-019 pooled comparator",
    "matched_minimax_full_reference": "unchanged sixteen-motif experiment-019 reference",
    "matched_minimax_nine_primary": "top nine matched-minimax motifs selected from the evaluated domain's first half; other seven records retained byte-exactly",
    "eight_active_historical_control": "sealed experiment-019 minimum retained-benefit fraction 0.5660377358490566; not recomputed or used for selection"
  },
  "seeds": {"randomness": "none", "seed_list": [], "determinism": "all identities, orders, splits, rankings, tie breaks, matching, and activation are fixed; two complete executions must be byte-identical"},
  "budgets": {"base_training_files": 4, "demand_files": 3, "encounter_orders": 2, "stages_per_order": 3, "seen_domain_evaluation_rows": 12, "cell_count": 16, "active_structure_count": 9, "retained_structure_count": 7, "primary_runs": 2, "maximum_source_processes": 1, "timeout_seconds": 1800, "network_access": false, "capacity_growth_events": 0},
  "metrics_and_thresholds": [
    ["training_file_identity_mismatch_count", "==", 0], ["evaluation_file_identity_mismatch_count", "==", 0], ["future_stage_adaptation_access_count", "==", 0], ["second_half_adaptation_access_count", "==", 0],
    ["valid_stage_count", "==", 6], ["valid_seen_domain_evaluation_count", "==", 12], ["matched_assignment_failure_count", "==", 0], ["minimum_selected_motif_count", "==", 16], ["maximum_selected_motif_count", "==", 16], ["matched_ineligible_candidate_count", "==", 0],
    ["minimum_minimax_full_incremental_correct_count", ">", 0], ["minimum_minimax_minus_frozen_incremental_correct_count", ">", 0], ["minimum_minimax_to_independent_incremental_correct_fraction", ">=", 0.70],
    ["minimum_prior_domain_minimax_incremental_correct_count", ">", 0], ["minimum_prior_domain_minimax_to_at_first_encounter_fraction", ">=", 0.70], ["minimum_minimax_minus_pooled_incremental_correct_count", ">=", 0], ["final_order_record_mismatch_count", "==", 0],
    ["minimum_primary_active_structure_count", "==", 9], ["maximum_primary_active_structure_count", "==", 9], ["minimum_primary_retained_structure_count", "==", 7], ["maximum_primary_retained_structure_count", "==", 7],
    ["minimum_primary_retained_incremental_correct_fraction", ">=", 0.70], ["minimum_eval_covered_accuracy_gain", ">", 0.0], ["retained_record_integrity_mismatch_count", "==", 0], ["state_partition_mismatch_count", "==", 0],
    ["capacity_growth_event_count", "==", 0], ["tokenizer_use_count", "==", 0], ["invalid_evaluation_rows", "==", 0]
  ],
  "controls": [
    "Every arm is evaluated on the same untouched second halves, reset context, and unchanged base-trained previous-byte baseline as 019.",
    "Each order starts independently; only encountered first halves accumulate and earlier second halves remain evaluation-only.",
    "Frozen, independent, pooled, and full matched-minimax arms are byte-identical in definition to 019.",
    "The primary selector is unchanged; only one additional ranked motif is activated and the complementary retained record count decreases by one.",
    "All sixteen records remain represented exactly once across the nine active and seven retained partitions.",
    "Cell count, radius, hashes, thresholds, matching, inputs, and total capacity remain frozen."
  ],
  "validity_criteria": [
    "Exact parent, North Star, experiment-019 evidence identity, source dependencies, input blobs, and sizes match.",
    "Implementation logic differs from 019 only in experiment identity, exact-parent validation if present, ACTIVE_CEILING 9, and complementary partition expectations.",
    "No second-half or future-stage bytes enter adaptation, ranking, matching, or activation.",
    "Every stage assigns sixteen motifs and every evaluation partitions exactly nine active plus seven byte-exact retained records.",
    "Full-reference metrics equal the corresponding 019 metrics except metrics directly describing the active/retained partition.",
    "All metrics are finite and two complete executions are byte-identical.",
    "No tokenizer, external model, network access, radius widening, capacity growth, or state carry between order arms occurs."
  ],
  "classification_rules": {
    "supported": "All validity criteria and frozen thresholds pass; nine active motifs cross the 0.70 retained-benefit boundary on every evaluation.",
    "mixed": "Validity passes and the nine-active minimum retained-benefit fraction exceeds 0.5660377358490566 but remains below 0.70, or another non-partition scientific threshold fails while full benefit remains positive.",
    "null": "Validity passes but the nine-active minimum retained-benefit fraction equals 0.5660377358490566 within exact floating-point output and is never lower.",
    "negative": "Validity passes but nine-active retained benefit is lower than 0.5660377358490566, falls below 0.50, full matched-minimax benefit is nonpositive on any evaluation, or prior-domain retention falls below 0.50.",
    "incomplete": "Compute interruption prevents both deterministic executions, all six stages, or all twelve evaluations.",
    "invalid": "Any identity, isolation, determinism, matching, fixed-capacity, full-reference equivalence, finiteness, partition-integrity, or qualification criterion fails."
  },
  "stop_conditions": [
    "Stop invalid before scientific evaluation on any identity, lineage, dependency, or size mismatch.",
    "Stop invalid on forbidden byte access, matching failure, partition corruption, unexpected full-reference drift, capacity growth, non-finite metric, or nondeterministic duplicate output.",
    "Do not stop early for apparent supported, mixed, null, or negative outcomes.",
    "After any output is observed, do not repair or rerun under this experiment identifier."
  ],
  "no_post_result_tuning_rule": "After any primary or diagnostic output is observed, do not alter inputs, splits, orders, learner, controls, selector, active ceiling, retained count, budgets, metrics, thresholds, aggregation, validity, classification, or stopping rules under this experiment identifier."
}
