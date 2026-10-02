{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-MINIMAX-CONSOLIDATION-015",
  "program": "DG1 real-byte adaptive granularity",
  "question": "Can deterministic cross-domain contribution consolidation preserve the worst-domain rescue from 014 without sacrificing pooled cumulative strengths, under the same fixed sixteen-cell and seven-active ceilings?",
  "hypothesis": "Across the same A-B-C and C-B-A orders, selecting sixteen motifs from the union of pooled and independently adapted candidate sets by highest minimum first-half incremental-correct contribution across all seen domains, then highest summed contribution and raw-key tie break, will keep every seen-domain second-half incremental benefit positive, retain at least 70% of independent-adaptation benefit, rescue at least one pooled nonpositive evaluation, and never fall below the pooled full phenotype on any evaluation while retaining at least 70% benefit with seven active and nine retained structures.",
  "exact_parent_sha": "a6543900ac623aec2de4324faac1dcfcfd1b4449",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-DOMAIN-BALANCED-CONSOLIDATION-014",
    "classification": "negative-by-frozen-rules",
    "qualification_run_id": "37074732526",
    "result_sha256": "d9de15db6358488fb608e74df53c2580f5af81630fe1d959e4354079ec704f26",
    "observation": "Domain-balanced consolidation eliminated zero-benefit collapse and retained 0.8889 of independent benefit and 0.875 of benefit under seven-active pressure, but minimum balanced-minus-pooled incremental correct count was -7, so simple round-robin protection traded away pooled strengths."
  },
  "authority": "synthetic research-only evaluation on immutable repo-owned bytes; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": [
    "research/experiments/exp-dgr-real-utf8-minimax-consolidation-015.ice",
    "research/applications/plane/exp-dgr-real-utf8-minimax-consolidation-015.py",
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json"
  ],
  "inputs": {
    "base_training": "byte-identical four architecture blobs from 013-014",
    "demand": "byte-identical A/B/C Track-A blobs and first-half/second-half splits from 013-014",
    "orders": [
      [
        "A",
        "B",
        "C"
      ],
      [
        "C",
        "B",
        "A"
      ]
    ],
    "contamination_rule": "Only base blobs and first halves at or before a stage may influence candidate generation, contribution scoring, consolidation, or active selection. No second half or future first half may enter any selection decision."
  },
  "frozen_reuse": {
    "baseline": "byte-identical previous-byte baseline from 001-014",
    "candidate_statistics": "byte-identical four-byte candidate stats, occurrence>=12, consistency>=0.60",
    "independent_adaptation": "byte-identical per-domain base-plus-own-first-half development from 012-014",
    "pooled_control": "byte-identical cumulative pooled phenotype from 013-014",
    "active_selector": "byte-identical per-domain first-half contribution selector from 013-014",
    "record_format": "byte-identical six-byte retained record from 013-014"
  },
  "consolidation_primary": {
    "capacity": 16,
    "candidate_union": "unique motif keys from the current pooled sixteen-motif phenotype and each seen domain's independently adapted sixteen-motif phenotype",
    "successor_rule": "current pooled cumulative stats over base blobs plus all seen first halves; existing lowest-byte tie rule",
    "contribution_rule": "for each candidate key, compute its incremental-correct contribution on each seen domain first half against the unchanged previous-byte baseline using the pooled successor; no second-half bytes",
    "ranking": "descending minimum contribution across seen domains; then descending summed contribution across seen domains; then raw motif key",
    "cell_assignment": "visit ranked keys and assign each to the first free cell in existing radius-two local-cell order; skip locally blocked keys; exactly sixteen assignments required",
    "no_growth": true
  },
  "arms": {
    "frozen_full_control": "unchanged architecture-only sixteen-motif phenotype",
    "independent_adapted_full_control": "unchanged per-domain experiment-012 phenotype",
    "pooled_shared_full_control": "unchanged experiment-013 pooled cumulative phenotype",
    "minimax_consolidated_full_primary": "fixed-sixteen phenotype defined above",
    "minimax_consolidated_seven_primary": "per-domain seven-active selection from minimax phenotype using unchanged first-half contribution selector; retain nine byte-exact records"
  },
  "budgets": {
    "cell_count": 16,
    "active_structure_count": 7,
    "retained_structure_count": 9,
    "encounter_orders": 2,
    "stages_per_order": 3,
    "seen_domain_evaluation_rows": 12,
    "primary_runs": 2,
    "maximum_source_processes": 1,
    "timeout_seconds": 1800,
    "network_access": false,
    "capacity_growth_events": 0
  },
  "metrics_and_thresholds": [
    [
      "training_file_identity_mismatch_count",
      "==",
      0
    ],
    [
      "evaluation_file_identity_mismatch_count",
      "==",
      0
    ],
    [
      "future_stage_adaptation_access_count",
      "==",
      0
    ],
    [
      "second_half_adaptation_access_count",
      "==",
      0
    ],
    [
      "valid_stage_count",
      "==",
      6
    ],
    [
      "valid_seen_domain_evaluation_count",
      "==",
      12
    ],
    [
      "minimax_assignment_failure_count",
      "==",
      0
    ],
    [
      "minimum_minimax_full_incremental_correct_count",
      ">",
      0
    ],
    [
      "minimum_minimax_minus_frozen_incremental_correct_count",
      ">",
      0
    ],
    [
      "minimum_minimax_to_independent_incremental_correct_fraction",
      ">=",
      0.7
    ],
    [
      "minimum_prior_domain_minimax_incremental_correct_count",
      ">",
      0
    ],
    [
      "minimum_prior_domain_minimax_to_at_first_encounter_fraction",
      ">=",
      0.7
    ],
    [
      "minimum_minimax_minus_pooled_incremental_correct_count",
      ">=",
      0
    ],
    [
      "rescued_nonpositive_pooled_evaluation_count",
      ">=",
      1
    ],
    [
      "final_order_record_mismatch_count",
      "==",
      0
    ],
    [
      "minimum_primary_active_structure_count",
      "==",
      7
    ],
    [
      "maximum_primary_active_structure_count",
      "==",
      7
    ],
    [
      "minimum_primary_retained_structure_count",
      "==",
      9
    ],
    [
      "maximum_primary_retained_structure_count",
      "==",
      9
    ],
    [
      "minimum_primary_retained_incremental_correct_fraction",
      ">=",
      0.7
    ],
    [
      "minimum_eval_covered_accuracy_gain",
      ">",
      0
    ],
    [
      "retained_record_integrity_mismatch_count",
      "==",
      0
    ],
    [
      "state_partition_mismatch_count",
      "==",
      0
    ],
    [
      "capacity_growth_event_count",
      "==",
      0
    ],
    [
      "tokenizer_use_count",
      "==",
      0
    ],
    [
      "invalid_evaluation_rows",
      "==",
      0
    ]
  ],
  "validity_criteria": [
    "Exact parent, North Star, prior result identity, source blobs, sizes and lineage match.",
    "Both orders execute exactly three stages and twelve seen-domain evaluations.",
    "Candidate union includes only current pooled and seen-domain independent motifs derived without second-half access.",
    "All minimax and summed contribution scores are computed exclusively on already encountered first halves against the unchanged baseline.",
    "Pooled successor statistics use only base blobs plus already encountered first halves.",
    "Every minimax phenotype has exactly sixteen locally assigned motifs with no capacity growth.",
    "Every primary partition contains exactly seven active and nine retained byte-exact records whose union is the sixteen minimax records.",
    "Final forward and reverse minimax record sets are compared byte-for-byte.",
    "All metrics are finite and duplicate complete executions are byte-identical.",
    "No tokenizer, external model, network access, capacity growth, post-result repair, or state carry between order arms occurs."
  ],
  "classification_rules": {
    "supported": "All validity criteria and frozen thresholds pass; training-side minimax consolidation preserves pooled strengths while rescuing cumulative retention at fixed capacity.",
    "mixed": "Validity passes and minimax keeps every seen domain positive and rescues pooled failures, but at least one pooled-nondegradation, 0.70 retention, or active-partition threshold fails.",
    "negative": "Validity passes but minimax is nonpositive on any seen domain, rescues no pooled failure, or materially worsens the fixed-capacity tradeoff.",
    "null": "Validity passes but minimax and pooled differ by at most one incremental-correct prediction on every evaluation.",
    "incomplete": "Compute interruption prevents both deterministic executions, all six stages, or all twelve evaluations.",
    "invalid": "Any identity, isolation, contribution-scoring, local-assignment, fixed-capacity, finiteness, partition-integrity, or qualification criterion fails."
  },
  "no_post_result_tuning_rule": "Do not alter inputs, splits, candidate union, contribution definition, ranking, successor rule, cell assignment, active ceiling, controls, metrics, thresholds, classification, or stopping rules after any primary output."
}