{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-RESOURCE-PRESSURE-002",
  "program": "DG1 real-byte adaptive granularity",
  "question": "After supported real-byte developmental specialization fills all 16 cells, can the fixed Yggdrasil substrate satisfy a hard eight-active-structure ceiling by hibernating the lower-utility eight learned motifs while preserving most held-out predictive benefit and event efficiency without retraining or capacity growth?",
  "hypothesis": "Using the exact supported six-file real-byte split and byte-identical 16-motif learner, deterministic utility ranking will keep exactly eight motifs active and encode exactly eight hibernated motif records in 48 logical bytes. On both held-out files, the pressured eight-active model will retain at least 55% of the full 16-motif model's incremental correct predictions over the previous-byte baseline, maintain at least 0.15 covered-position accuracy gain, cover at least 1% of next-byte positions, and reduce effective event count by at least 2%, with no cell-count growth or active/hibernated state corruption.",
  "exact_parent_sha": "2dac12b534ddd41a8f95499b984b0fa61187dfea",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-DEVELOPMENTAL-SPECIALIZATION-001",
    "classification": "supported",
    "qualification_run_id": "37025892945",
    "result_sha256": "e5c4ec95883d4d42f351d3fe28f657a556ef86213cd73c132232ce80f220ac74"
  },
  "authority": "research-only immutable real-byte resource-pressure test; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, or capacity authority changes",
  "changed_paths": [
    "research/experiments/exp-dgr-real-utf8-resource-pressure-002.ice",
    "research/applications/plane/exp-dgr-real-utf8-resource-pressure-002.py",
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json"
  ],
  "frozen_reuse": {
    "corpus": "exact six files and blob identities from EXP-DGR-REAL-UTF8-DEVELOPMENTAL-SPECIALIZATION-001",
    "learner": "same previous-byte baseline, four-byte candidate statistics, occurrence>=12, consistency>=0.60, candidate ranking, home hash, local radius two, and 16-cell differentiation",
    "evaluation": "same held-out prediction, coverage, transferred-motif, and event-accounting definitions"
  },
  "resource_pressure": {
    "active_structure_ceiling": 8,
    "utility_score": "best_successor_count * consistency",
    "ranking": "descending utility score, then descending total occurrence, then lexicographic four-byte key",
    "keep_active": "first eight ranked differentiated motifs",
    "hibernate": "remaining eight differentiated motifs",
    "hibernated_record": "[original_cell_index, key_byte0, key_byte1, key_byte2, key_byte3, learned_best_successor], exactly 6 bytes",
    "expected_hibernated_record_count": 8,
    "expected_hibernated_logical_bytes": 48,
    "physical_cells": "remain exactly 16; hibernated cells become generic but are not deleted",
    "retraining": false
  },
  "evaluation_additions": {
    "full_model": "supported 16-motif model reconstructed from the exact frozen learner",
    "pressured_model": "same baseline plus only the eight active motifs",
    "incremental_correct_predictions": "number of positions where model is correct minus number where baseline is correct across all eligible next-byte positions",
    "retained_incremental_correct_fraction": "pressured incremental correct predictions divided by full-model incremental correct predictions; if full increment <=0, experiment is invalid",
    "hibernated_integrity": "decode all eight 6-byte records and require exact key/successor/cell identity match to pre-pressure state"
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
      "train_eval_blob_overlap_count",
      "==",
      0
    ],
    [
      "pre_pressure_differentiated_cell_count",
      "==",
      16
    ],
    [
      "post_pressure_active_structure_count",
      "==",
      8
    ],
    [
      "hibernated_structure_count",
      "==",
      8
    ],
    [
      "retained_hibernated_logical_bytes",
      "==",
      48
    ],
    [
      "minimum_active_transferred_motif_count_per_eval_file",
      ">=",
      6
    ],
    [
      "minimum_eval_covered_position_fraction",
      ">=",
      0.01
    ],
    [
      "minimum_eval_covered_accuracy_gain",
      ">=",
      0.15
    ],
    [
      "minimum_retained_incremental_correct_fraction",
      ">=",
      0.55
    ],
    [
      "minimum_effective_event_reduction_fraction",
      ">=",
      0.02
    ],
    [
      "hibernated_record_integrity_mismatch_count",
      "==",
      0
    ],
    [
      "maximum_final_cell_count",
      "==",
      16
    ],
    [
      "minimum_final_cell_count",
      "==",
      16
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
      "invalid_pressure_rows",
      "==",
      0
    ]
  ],
  "validity_criteria": [
    "Exact parent, North Star identity, supported real-byte specialization evidence identity, and six blob identities match.",
    "The 16-motif pre-pressure model exactly follows the prior frozen learner and contains exactly sixteen differentiated structures.",
    "Pressure ordering is computed only from training evidence and never from held-out files.",
    "Exactly eight motifs remain active and exactly eight are hibernated into exact six-byte records.",
    "No hibernated structure participates in pressured prediction or event accounting.",
    "Held-out files remain read-only; no wake, repair, retraining, or adaptation occurs.",
    "Cell count stays exactly sixteen and all metrics are finite.",
    "Two duplicate executions are byte-identical before evidence sealing."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all eighteen frozen thresholds pass.",
    "mixed": "Validity passes and pressured model retains positive predictive gain on both files, but at least one benefit-retention, coverage, transfer, event, or resource threshold fails.",
    "negative": "Validity passes but minimum retained incremental-correct fraction is below 0.25 or pressured covered accuracy gain is non-positive on either file.",
    "incomplete": "Environmental or compute interruption prevents complete evaluation.",
    "invalid": "Blob identity, prior-learner identity, pressure ranking, record construction, active ceiling, fixed-cell capacity, held-out isolation, finiteness, or qualification criteria fail."
  },
  "no_post_result_tuning_rule": "Do not alter files, learner, pressure score/order, active ceiling, hibernated record format, metrics, thresholds, aggregation, or classification after observing any output."
}
