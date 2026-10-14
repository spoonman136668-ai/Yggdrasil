{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-RETAIN-REVERT-FRESH-REPLICATION-028",
  "program": "DG1 real-byte adaptive granularity",
  "question": "Does the frozen first-half retain/revert gate and ten-active matched-minimax partition from experiment 027 replicate without collateral regression or capacity growth on three previously unevaluated Track-A text domains?",
  "hypothesis": "Across both frozen encounter orders on fresh domains M/N/O, the unchanged first-half gate will select between frozen and matched-minimax phenotypes such that every gated full evaluation remains positive and noninferior to frozen, retains at least 70% of independent-adaptation and first-encounter benefit, is noninferior to pooled cumulative adaptation, and its unchanged ten-active partition retains at least 70% of selected-full benefit with six byte-exact retained records and no capacity growth.",
  "exact_parent_sha": "f9f60a184505a3574c2c737facd6c89bc9a69974",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-RETAIN-REVERT-GATE-027",
    "classification": "supported-by-frozen-rules",
    "qualification_run_id": "38553269372",
    "result_sha256": "3d97e0e91b0d4f3113b920a2f47171cb28acf3a36f96e8fe80bb824a624145a0",
    "observation": "On reused J/K/L, the gate reverted once across twelve decisions, changed the sealed minimum matched-minimax minus frozen result from -6 to 0, retained minimum gated-full benefit 133, independent fraction 1.0, prior-domain fraction 0.9707112970711297, ten-active selected-full fraction 0.8870292887029289, exact state integrity, and zero capacity growth. Fresh-domain gate generalization remains unknown."
  },
  "authority": "synthetic research-only evaluation on immutable repo-owned bytes; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": ["research/experiments/exp-dgr-real-utf8-retain-revert-fresh-replication-028.ice", "research/applications/plane/exp-dgr-real-utf8-retain-revert-fresh-replication-028.py", ".yggdrasil/qualification-request.json", ".yggdrasil/isolated-run.json"],
  "inputs": {
    "base_training": [["research/architecture/measurement-framework.ice", "6374fc3c39ee821c8f9d565bb7de0875c07d5cdc", 10040], ["research/architecture/structural-plasticity.ice", "d2d75b4ed60e0c112de5202ba31848b15081e0cb", 9550], ["research/architecture/developmental-substrate-v0.2.ice", "52d6e87e2339bdf586c33da22470e38a9ca27785", 8448], ["research/architecture/yggdrasil-north-star.ice", "84358ec54c0e7eba6b6f830e0b4d2755920281cb", 8411]],
    "demand": {"M": ["research/applications/track-a/a13-t6-bounded-novel-context-discovery.ice", "c48fe4c06b50e5dc18b0013967d8074b33a17bad", 22805], "N": ["research/applications/track-a/a14-t6-strict-bounded-novel-context-creation.ice", "597a641af867f3f4f4e73b9df14289846516e68b", 32552], "O": ["research/applications/track-a/a15-t7-versioned-context-revision.ice", "113bc2bc8b436555d586655561e92235b5b2f333", 40412]},
    "orders": [["M", "N", "O"], ["O", "N", "M"]],
    "encoding": "identity file bytes; no UTF decoding, normalization, tokenizer, vocabulary, separator, boundary label, or remapping",
    "split": "each blob is split at floor(raw_byte_length/2); first half is adaptation and gate cue, untouched second half is evaluation-only; raw four-byte context resets independently for gate scoring and every evaluation",
    "freshness": "M/N/O are immutable repository prose not evaluated by experiments 001-027 in this real-byte lineage; their existence in other Track-A research is disclosed and no corpus-independence claim is made",
    "contamination_rule": "At each stage, fitting, minimax scoring, activation, and gating may use base blobs and only first halves encountered through that stage. No second-half or future first-half byte may enter any decision."
  },
  "frozen_reuse": {
    "source_logic": "byte-identical experiment-027 learner chain, controls, candidate union, pooled successor rule, minimax scoring/ranking, feasibility-preserving matching, evaluation, record encoding, gate, and ten-active selector",
    "only_scientific_delta": "replace J/K/L with fresh M/N/O and corresponding two encounter orders; no mechanism, threshold, capacity, or aggregation change",
    "gate": "selected_full = matched_minimax_full iff reset-context first-half cue_minimax_correct >= cue_frozen_correct, else frozen_full; no margin, learned parameter, search, second-half access, or order-specific rule"
  },
  "arms": {
    "frozen_full_control": "unchanged architecture-only sixteen-motif phenotype",
    "ungated_matched_minimax_control": "unchanged full matched-minimax phenotype",
    "independent_adapted_full_control": "per-domain phenotype fitted from base blobs plus only that domain's first half",
    "pooled_cumulative_full_control": "unchanged pooled cumulative comparator",
    "gated_full_primary": "frozen first-half selection between frozen-full and matched-minimax-full",
    "gated_ten_active_primary": "top ten records of selected full phenotype by unchanged cue contribution, utility, and raw-key ranking; six complementary records retained byte-exactly"
  },
  "seeds": {"randomness": "none", "seed_list": [], "determinism": "all identities, orders, splits, fitting, rankings, matching, gate comparisons, and activation are fixed; two complete executions must be byte-identical"},
  "budgets": {"base_training_files": 4, "demand_files": 3, "encounter_orders": 2, "stages_per_order": 3, "seen_domain_evaluation_rows": 12, "cell_count": 16, "active_structure_count": 10, "retained_structure_count": 6, "primary_runs": 2, "maximum_source_processes": 1, "timeout_seconds": 1800, "network_access": false, "capacity_growth_events": 0},
  "metrics_and_thresholds": [
    ["training_file_identity_mismatch_count", "==", 0], ["evaluation_file_identity_mismatch_count", "==", 0], ["future_stage_adaptation_access_count", "==", 0], ["second_half_adaptation_access_count", "==", 0],
    ["valid_stage_count", "==", 6], ["valid_seen_domain_evaluation_count", "==", 12], ["matched_assignment_failure_count", "==", 0], ["minimum_selected_motif_count", "==", 16], ["maximum_selected_motif_count", "==", 16], ["matched_ineligible_candidate_count", "==", 0],
    ["minimum_gated_full_incremental_correct_count", ">", 0], ["minimum_gated_minus_frozen_incremental_correct_count", ">=", 0], ["minimum_gated_to_independent_incremental_correct_fraction", ">=", 0.70],
    ["minimum_prior_domain_gated_incremental_correct_count", ">", 0], ["minimum_prior_domain_gated_to_at_first_encounter_fraction", ">=", 0.70], ["minimum_gated_minus_pooled_incremental_correct_count", ">=", 0],
    ["gate_decision_count", "==", 12], ["gate_decision_mismatch_count", "==", 0], ["final_order_record_mismatch_count", "==", 0],
    ["minimum_primary_active_structure_count", "==", 10], ["maximum_primary_active_structure_count", "==", 10], ["minimum_primary_retained_structure_count", "==", 6], ["maximum_primary_retained_structure_count", "==", 6],
    ["minimum_primary_retained_incremental_correct_fraction", ">=", 0.70], ["minimum_eval_covered_accuracy_gain", ">", 0.0], ["retained_record_integrity_mismatch_count", "==", 0], ["state_partition_mismatch_count", "==", 0],
    ["capacity_growth_event_count", "==", 0], ["tokenizer_use_count", "==", 0], ["invalid_evaluation_rows", "==", 0]
  ],
  "controls": [
    "All arms use identical untouched second halves, reset evaluation context, and the unchanged base-trained previous-byte baseline.",
    "The gate sees only the current domain's permitted first half with independently reset context; second-half outcomes cannot affect selection.",
    "Ungated outcomes and gate reverts are reported without requiring a revert, because forcing gate use on fresh domains would change the mechanism.",
    "Each order starts independently; only encountered first halves accumulate, and earlier second halves remain evaluation-only.",
    "Every selected phenotype contains sixteen records partitioned into exactly ten active plus six byte-exact retained records.",
    "Cell count, radius, hashes, learner thresholds, matching, active ceiling, budgets, inputs, and total capacity remain frozen."
  ],
  "validity_criteria": [
    "Exact parent, North Star, experiment-027 evidence identity, source dependencies, input blobs, and sizes match.",
    "Implementation logic differs from 027 only by experiment identity, exact-parent provenance, demand identities, order labels, and removal of J/K/L sealed-outcome reproduction thresholds.",
    "No second-half or future-stage bytes enter fitting, ranking, matching, gating, or activation.",
    "Every stage assigns sixteen minimax motifs and every selected phenotype partitions exactly ten active plus six byte-exact retained records.",
    "Every gate decision equals the frozen rule applied to independently recomputed first-half correct counts.",
    "All metrics are finite and two complete executions are byte-identical.",
    "No tokenizer, external model, network access, radius widening, capacity growth, or state carry between order arms occurs."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all frozen thresholds pass.",
    "mixed": "Validity passes and gated full benefit remains positive everywhere, but at least one collateral, comparator, 0.70 retention, covered-gain, order-invariance, or active-partition threshold fails.",
    "null": "Validity passes but gated full or ten-active benefit is zero on at least one evaluation and never negative.",
    "negative": "Validity passes but gated full or ten-active benefit is negative on any evaluation, gated full benefit is nonpositive on at least two evaluations, or prior-domain gated retention falls below 0.50.",
    "incomplete": "Compute interruption prevents both deterministic executions, all six stages, or all twelve evaluations.",
    "invalid": "Any identity, isolation, determinism, gate integrity, matching, fixed-capacity, finiteness, partition-integrity, or qualification criterion fails."
  },
  "stop_conditions": [
    "Stop invalid before scientific evaluation on any identity, lineage, dependency, or size mismatch.",
    "Stop invalid on forbidden byte access, gate mismatch, matching failure, partition corruption, capacity growth, non-finite metric, or nondeterministic duplicate output.",
    "Do not stop early for apparent supported, mixed, null, or negative outcomes.",
    "After any output is observed, do not repair or rerun under this experiment identifier."
  ],
  "no_post_result_tuning_rule": "After any primary or diagnostic output is observed, do not alter files, splits, orders, learner, controls, gate rule or tie handling, scoring, ranking, matching, active ceiling, budgets, metrics, thresholds, aggregation, validity, classification, or stopping rules under this experiment identifier."
}
