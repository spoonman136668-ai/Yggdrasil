{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-DOMAIN-BALANCED-CONSOLIDATION-014",
  "program": "DG1 real-byte adaptive granularity",
  "question": "Is the cumulative-retention collapse in experiment 013 primarily caused by globally pooled motif-selection competition, and can deterministic domain-balanced consolidation preserve all seen domains under the same fixed sixteen-cell and seven-active ceilings?",
  "hypothesis": "Across the same A-B-C and C-B-A cumulative orders, interleaving the independently adapted per-domain motif rankings into one fixed sixteen-cell consolidated phenotype will preserve positive second-half incremental benefit on every seen domain, retain at least 70% of independent-adaptation benefit, rescue at least one evaluation where the pooled-shared control is non-positive, remain order-invariant at the final stage, and preserve at least 70% of consolidated benefit with exactly seven active and nine retained structures.",
  "exact_parent_sha": "de83379d7b936b24c42c82460ab48571f978cf9f",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-CUMULATIVE-FIRST-HALF-ADAPTATION-013",
    "classification": "negative-by-frozen-rules",
    "qualification_run_id": "37056173540",
    "result_sha256": "5e3216b680dddaad006f55cdcdc48bbc10bb4a041e22e6416807aee2b3c8c76a",
    "observation": "Pooled cumulative adaptation preserved identity, order invariance, seven-active/nine-retained partition integrity, zero capacity growth and zero future/second-half access, but minimum shared full benefit, independent-retention fraction, prior-domain benefit, retained fraction, and covered accuracy gain reached zero."
  },
  "authority": "synthetic research-only evaluation on immutable repo-owned bytes; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": [
    "research/experiments/exp-dgr-real-utf8-domain-balanced-consolidation-014.ice",
    "research/applications/plane/exp-dgr-real-utf8-domain-balanced-consolidation-014.py",
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json"
  ],
  "inputs": {
    "base_training": "byte-identical four architecture blobs from 013",
    "demand": "byte-identical A/B/C Track-A blobs and first-half/second-half splits from 013",
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
    "contamination_rule": "Only base blobs and first halves at or before a stage may influence consolidation or active selection. No second half or future first half may enter fitting, ranking, consolidation, or activation."
  },
  "frozen_reuse": {
    "baseline": "byte-identical previous-byte baseline from 001-013",
    "candidate_statistics": "byte-identical four-byte candidate stats, occurrence>=12, consistency>=0.60",
    "independent_adaptation": "byte-identical per-domain base-plus-own-first-half development from 012-013",
    "pooled_control": "byte-identical cumulative pooled shared phenotype from 013",
    "active_selector": "byte-identical per-domain first-half contribution selector from 013",
    "record_format": "byte-identical six-byte retained record from 013"
  },
  "consolidation_primary": {
    "capacity": 16,
    "per_domain_source": "Each seen domain contributes its independently adapted sixteen specialized rows built from base blobs plus only that domain's first half.",
    "per_domain_order": "Rows are sorted by descending independent training utility then raw motif key.",
    "merge_order": "At each depth 0..15, visit seen domains in lexical label order A,B,C and admit the row key if not already selected; continue until sixteen keys have been successfully assigned.",
    "successor_rule": "For every admitted key, use the best successor from the current pooled cumulative stats over base blobs plus all seen first halves; ties use the existing lowest-byte rule.",
    "cell_assignment": "For each admitted key in merge order, compute the existing home cell and assign to the first free cell in existing radius-two local-cell order. If a candidate cannot be assigned, continue to the next candidate. Exactly sixteen assignments are required.",
    "no_growth": true
  },
  "arms": {
    "frozen_full_control": "unchanged architecture-only sixteen-motif phenotype",
    "independent_adapted_full_control": "unchanged per-domain experiment-012 phenotype",
    "pooled_shared_full_control": "unchanged experiment-013 cumulative pooled sixteen-motif phenotype",
    "balanced_consolidated_full_primary": "fixed-sixteen domain-balanced phenotype defined above",
    "balanced_consolidated_seven_primary": "for each seen domain select seven active rows from the balanced phenotype by its own first-half contribution then current pooled utility/raw-key ties; retain the other nine byte-exact records"
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
      "balanced_assignment_failure_count",
      "==",
      0
    ],
    [
      "minimum_balanced_full_incremental_correct_count",
      ">",
      0
    ],
    [
      "minimum_balanced_minus_frozen_incremental_correct_count",
      ">",
      0
    ],
    [
      "minimum_balanced_to_independent_incremental_correct_fraction",
      ">=",
      0.7
    ],
    [
      "minimum_prior_domain_balanced_incremental_correct_count",
      ">",
      0
    ],
    [
      "minimum_prior_domain_balanced_to_at_first_encounter_fraction",
      ">=",
      0.7
    ],
    [
      "minimum_balanced_minus_pooled_incremental_correct_count",
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
    "Independent per-domain candidate sources use only base blobs plus that domain's own first half.",
    "Balanced consolidation uses lexical domain order and frozen per-domain row rankings; no second-half metric enters selection.",
    "Pooled shared successor statistics use only base blobs plus already encountered first halves.",
    "Every balanced phenotype has exactly sixteen locally assigned motifs with no radius violation or capacity growth.",
    "Every primary partition contains exactly seven active and nine retained byte-exact records whose union is the sixteen balanced records.",
    "Final forward and reverse balanced record sets are compared byte-for-byte.",
    "All metrics are finite and duplicate complete executions are byte-identical.",
    "No tokenizer, external model, network access, capacity growth, post-result repair, or state carry between order arms occurs."
  ],
  "classification_rules": {
    "supported": "All validity criteria and frozen thresholds pass; domain-balanced fixed-capacity consolidation rescues the pooled cumulative failure.",
    "mixed": "Validity passes and balanced consolidation rescues at least one pooled failure with positive benefit on every seen domain, but at least one 0.70 retention or active-partition threshold fails.",
    "negative": "Validity passes but balanced consolidation remains non-positive on any seen domain, is worse than pooled on any evaluation, or rescues no pooled failure.",
    "null": "Validity passes but balanced and pooled differ by at most one incremental-correct prediction on every evaluation.",
    "incomplete": "Compute interruption prevents both deterministic executions, all six stages, or all twelve evaluations.",
    "invalid": "Any identity, isolation, selection, local-assignment, fixed-capacity, finiteness, partition-integrity, or qualification criterion fails."
  },
  "stop_conditions": [
    "Stop invalid before evaluation on identity, lineage, size, dependency or prior-evidence mismatch.",
    "Stop invalid on future-stage/second-half access, local-assignment failure, partition corruption, capacity growth, order drift, non-finite metric, or nondeterministic duplicate output.",
    "Do not stop early for apparent supported, mixed, negative, or null outcomes.",
    "Do not alter the experiment after any primary output is observed."
  ],
  "no_post_result_tuning_rule": "Do not alter inputs, splits, independent sources, lexical merge order, per-domain row order, successor rule, cell assignment, seven-active ceiling, controls, metrics, thresholds, classification, or stopping rules after any primary output."
}