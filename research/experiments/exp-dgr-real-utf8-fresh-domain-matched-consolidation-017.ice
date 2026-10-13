{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-FRESH-DOMAIN-MATCHED-CONSOLIDATION-017",
  "program": "DG1 real-byte adaptive granularity",
  "question": "Does the frozen fixed-capacity minimax-matched consolidation mechanism from experiment 016 preserve positive predictive benefit and seven-active/nine-retained state when cumulatively adapted across three previously unevaluated immutable Track-A files?",
  "hypothesis": "Across forward D-E-F and reverse F-E-D orders on three fresh files, the unchanged 016 mechanism will assign exactly sixteen motifs at every stage, retain positive second-half incremental-correct benefit on every seen domain, preserve at least 70% of independent first-half adaptation benefit and prior-domain first-encounter benefit, and maintain exactly seven active plus nine retained records without capacity growth.",
  "exact_parent_sha": "650cafdfae07dfc5ce3f3d23c59810b80b6eb8aa",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-MINIMAX-MATCHED-CONSOLIDATION-016",
    "classification": "supported-by-frozen-rules",
    "qualification_run_id": "37075511579",
    "result_sha256": "138d21335abc10e0eb7bddbbe5dd2a4e4b2ba5ea902d2319dc80eff637df2b29",
    "observation": "On reused A/B/C files, matched minimax consolidation produced sixteen motifs at all six stages, positive benefit on all twelve seen-domain evaluations, full independent-adaptation retention, two pooled-failure rescues, exact seven-active/nine-retained partitions, and no invalid rows. Generalization to files not used in experiments 011-016 is unknown."
  },
  "authority": "synthetic research-only evaluation on immutable repo-owned bytes; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": [
    "research/experiments/exp-dgr-real-utf8-fresh-domain-matched-consolidation-017.ice",
    "research/applications/plane/exp-dgr-real-utf8-fresh-domain-matched-consolidation-017.py",
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json"
  ],
  "inputs": {
    "base_training": "byte-identical four architecture files and identities from experiments 001-016",
    "fresh_demand": {
      "D": ["research/applications/track-a/a04-fixa-resource-qualified-fault-recovery.ice", "e146e2ce5e3000fc452d9bcc12b626208ef89c99", 14185],
      "E": ["research/applications/track-a/a05-post-freeze-task-semantic-transfer.ice", "caf48f688cc9670c98cef7173ad0952e6964f052", 22994],
      "F": ["research/applications/track-a/a06-lineage-qualified-online-program-inheritance.ice", "50f6d93fb1c5e7e3f0811b4d456b7a750bec2a9e", 27670]
    },
    "orders": [["D", "E", "F"], ["F", "E", "D"]],
    "encoding": "identity file bytes; no UTF decoding, normalization, tokenizer, vocabulary, separator, boundary label, or remapping",
    "split": "each fresh blob is split at floor(raw_byte_length/2), with raw four-byte context reset at every second-half evaluation",
    "freshness": "D/E/F were not inputs to experiments 001-016 and no algorithmic output on these files was observed before this preregistration",
    "contamination_rule": "At each stage, fitting and minimax scoring may use base blobs and only first halves encountered through that stage. No second-half or future first-half byte may enter fitting, selection, matching, or activation."
  },
  "frozen_reuse": {
    "learner": "byte-identical baseline, four-byte statistics, occurrence and consistency filters, utility, home hash, radius-two geometry, and sixteen-cell development from 016",
    "consolidation": "byte-identical pooled-plus-independent candidate union, pooled successor rule, descending minimum contribution then summed contribution then raw-key minimax ranking, feasibility-preserving matching, and local-cell order from 016",
    "activation": "byte-identical domain-first-half seven-active contribution selector and six-byte retained records from 016",
    "controls_and_metrics": "byte-identical frozen-full, independent-adaptation, pooled-full controls and metric definitions from 016"
  },
  "seeds": {"randomness": "none", "seed_list": [], "determinism": "all file identities, orders, splits, rankings, tie breaks, and matching are fixed; two complete executions must be byte-identical"},
  "budgets": {"base_training_files": 4, "fresh_demand_files": 3, "encounter_orders": 2, "stages_per_order": 3, "seen_domain_evaluation_rows": 12, "cell_count": 16, "active_structure_count": 7, "retained_structure_count": 9, "primary_runs": 2, "maximum_source_processes": 1, "timeout_seconds": 1800, "network_access": false, "capacity_growth_events": 0},
  "metrics_and_thresholds": [
    ["training_file_identity_mismatch_count", "==", 0], ["evaluation_file_identity_mismatch_count", "==", 0],
    ["future_stage_adaptation_access_count", "==", 0], ["second_half_adaptation_access_count", "==", 0],
    ["valid_stage_count", "==", 6], ["valid_seen_domain_evaluation_count", "==", 12],
    ["matched_assignment_failure_count", "==", 0], ["minimum_selected_motif_count", "==", 16], ["maximum_selected_motif_count", "==", 16],
    ["minimum_minimax_full_incremental_correct_count", ">", 0], ["minimum_minimax_minus_frozen_incremental_correct_count", ">", 0],
    ["minimum_minimax_to_independent_incremental_correct_fraction", ">=", 0.70],
    ["minimum_prior_domain_minimax_incremental_correct_count", ">", 0], ["minimum_prior_domain_minimax_to_at_first_encounter_fraction", ">=", 0.70],
    ["final_order_record_mismatch_count", "==", 0],
    ["minimum_primary_active_structure_count", "==", 7], ["maximum_primary_active_structure_count", "==", 7],
    ["minimum_primary_retained_structure_count", "==", 9], ["maximum_primary_retained_structure_count", "==", 9],
    ["minimum_primary_retained_incremental_correct_fraction", ">=", 0.70], ["minimum_eval_covered_accuracy_gain", ">", 0.0],
    ["retained_record_integrity_mismatch_count", "==", 0], ["state_partition_mismatch_count", "==", 0],
    ["capacity_growth_event_count", "==", 0], ["tokenizer_use_count", "==", 0], ["invalid_evaluation_rows", "==", 0]
  ],
  "controls": [
    "Every arm for a domain is evaluated on its untouched second half with a reset context and unchanged base-trained previous-byte baseline.",
    "Each order starts independently; only encountered first halves accumulate.",
    "Frozen-full receives no fresh demand bytes; independent controls receive only their own first half; pooled and minimax arms receive identical stage data.",
    "All earlier-domain second halves remain evaluation-only and cannot feed subsequent stages.",
    "Forward and reverse final learners receive the same multiset, providing an order-invariance control.",
    "Cell count, active ceiling, radius, hashes, candidate thresholds, matching, budgets, and capacity remain frozen."
  ],
  "validity_criteria": [
    "Exact parent, North Star, prior evidence identity, source dependencies, input blobs, and sizes match.",
    "No D/E/F scientific output predates this preregistration commit.",
    "016 logic differs only in the preregistered fresh demand identities, labels, and forward/reverse orders.",
    "No second-half or future-stage bytes enter adaptation, ranking, matching, or activation.",
    "Every stage assigns sixteen motifs and every evaluation partitions seven active plus nine byte-exact retained records.",
    "All metrics are finite and two complete executions are byte-identical.",
    "No tokenizer, external model, network access, radius widening, capacity growth, or state carry between order arms occurs."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all frozen thresholds pass on the fresh domains.",
    "mixed": "Validity passes and every full minimax evaluation remains positive, but at least one improvement, 0.70 retention, covered-gain, or active-partition threshold fails.",
    "null": "Validity passes but fresh-domain minimax benefit is zero on at least one evaluation and never negative.",
    "negative": "Validity passes but minimax benefit is negative on any evaluation, is nonpositive on at least two evaluations, or prior-domain retention falls below 0.50.",
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
