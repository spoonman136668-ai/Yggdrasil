{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-MINIMAX-MATCHED-CONSOLIDATION-016",
  "program": "DG1 real-byte adaptive granularity",
  "question": "Can the unchanged minimax consolidation ranking from 015 be realized as a valid fixed-sixteen phenotype by replacing greedy first-free local placement with deterministic feasibility-preserving local matching, without changing motif scores, capacity, radius, or evaluation rules?",
  "hypothesis": "Across the same A-B-C and C-B-A orders, selecting candidates in the unchanged 015 minimax rank order while admitting a candidate only when the selected set remains matchable to the existing radius-two sixteen-cell geometry will produce exactly sixteen motifs at every stage with seven active and nine retained, while preserving positive second-half benefit on every seen domain, at least 70% of independent-adaptation benefit, at least one rescue of pooled nonpositive performance, and no degradation below pooled full performance.",
  "exact_parent_sha": "c884846cd79dc05153a77d1ee8a7ad8474dcdcf3",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-MINIMAX-CONSOLIDATION-015",
    "classification": "invalid-by-frozen-rules",
    "qualification_run_id": "37075188067",
    "result_sha256": "7ba16816469fe87b8632faf562f8d5f665ecf4b3fbb7c4cc2f3ece8b58c78d3b",
    "validity_failure": "Two stages failed greedy local assignment to sixteen motifs, causing minimax_assignment_failure_count=2, minimum retained count=8, state_partition_mismatch_count=2, invalid_evaluation_rows=2. No scientific performance claim is adopted from 015."
  },
  "authority": "synthetic research-only evaluation on immutable repo-owned bytes; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": [
    "research/experiments/exp-dgr-real-utf8-minimax-matched-consolidation-016.ice",
    "research/applications/plane/exp-dgr-real-utf8-minimax-matched-consolidation-016.py",
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json"
  ],
  "frozen_reuse": {
    "inputs": "byte-identical base and A/B/C bytes/splits/orders from 013-015",
    "baseline": "byte-identical previous-byte baseline",
    "candidate_union": "byte-identical pooled plus seen-domain independent motif union from 015",
    "successor_rule": "byte-identical pooled cumulative successor rule from 015",
    "contribution_rule": "byte-identical per-seen-domain first-half contribution scores from 015",
    "ranking": "byte-identical descending minimum contribution, descending summed contribution, raw-key ranking from 015",
    "active_selector": "byte-identical seven-active first-half contribution selector",
    "record_format": "byte-identical six-byte retained record"
  },
  "assignment_repair": {
    "capacity": 16,
    "local_geometry": "unchanged sixteen-cell ring, existing home hash, radius two, existing local-cell order",
    "independence_rule": "visit candidates in frozen minimax rank order; tentatively add each candidate; keep it only if the entire tentative selected set admits a one-to-one matching to allowed local cells",
    "feasibility_test": "deterministic augmenting-path bipartite matching using selected-key rank order and existing local-cell order",
    "stopping_rule": "stop after sixteen feasible motifs are admitted; failure to reach sixteen is invalid",
    "final_assignment": "run the same deterministic matching on the frozen sixteen selected motifs and write each motif to its matched existing cell",
    "no_growth": true,
    "no_radius_change": true
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
      "matched_assignment_failure_count",
      "==",
      0
    ],
    [
      "minimum_selected_motif_count",
      "==",
      16
    ],
    [
      "maximum_selected_motif_count",
      "==",
      16
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
    "Exact parent, North Star, prior invalid-result identity, source blobs, sizes and lineage match.",
    "015 candidate union, pooled successors, first-half contribution scores and minimax ranking are reproduced byte-for-byte before assignment.",
    "No second-half or future first-half data enters selection, matching, or activation.",
    "Matching changes only placement feasibility; cell count, home hash, radius and local-cell order remain unchanged.",
    "Every stage selects and assigns exactly sixteen motifs and every primary partition contains exactly seven active plus nine retained byte-exact records.",
    "Final forward and reverse record sets are compared byte-for-byte.",
    "All metrics are finite and duplicate complete executions are byte-identical.",
    "No tokenizer, external model, network access, capacity growth, radius widening, post-result repair, or state carry between order arms occurs."
  ],
  "classification_rules": {
    "supported": "All validity criteria and frozen thresholds pass; feasibility-preserving local matching validates the minimax consolidation mechanism at fixed capacity.",
    "mixed": "Validity passes and every seen domain remains positive with at least one pooled rescue, but at least one pooled-nondegradation, 0.70 retention, or active-partition threshold fails.",
    "negative": "Validity passes but minimax matched consolidation is nonpositive on any seen domain, rescues no pooled failure, or materially worsens the fixed-capacity tradeoff.",
    "incomplete": "Compute interruption prevents both deterministic executions, all six stages, or all twelve evaluations.",
    "invalid": "Any identity, rank drift, isolation, matching, fixed-capacity, finiteness, partition-integrity, or qualification criterion fails."
  },
  "no_post_result_tuning_rule": "Do not alter inputs, candidate union, contribution scores, minimax ranking, matching algorithm, cell geometry, active ceiling, controls, metrics, thresholds, classification, or stopping rules after any primary output."
}