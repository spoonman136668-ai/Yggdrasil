{
  "experiment_id": "EXP-DG1B-LINEAGE-ORDER-WINDOW-004",
  "candidate_id": "C1-LINEAGE-ORDER-ECONOMIC-WINDOW",
  "harness_id": "yggdrasil-isolated",
  "changed_paths": [
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json",
    "research/applications/plane/exp-dg1b-lineage-order-window-004.py",
    "research/experiments/exp-dg1b-lineage-order-window-004.ice"
  ],
  "controls": [
    "Genome-only regeneration with zero retained lineage events.",
    "Byte-identical shuffled-lineage control: permute retained records without replacement while preserving every record and serialized byte.",
    "Byte-identical reversed-lineage control: reverse the exact retained record sequence without changing records or bytes.",
    "Cold retraining from the same initial genome and seed, with no lineage or phenotype retained.",
    "Common-source control: all interventions for a seed branch from one frozen pre-destruction phenotype and lineage.",
    "Locality audit requiring zero global-control reads or messages during regeneration."
  ],
  "fixed_parameters": {
    "analysis_population": "Include every started cell. A failed or timed-out cell receives zero functional recovery and retains its measured resource consumption through termination.",
    "benchmark": "The sole Python scientific source deterministically defines six tasks with IDs 0 through 5; each task uses all 256 eight-bit binary inputs and a fixed 128/64/64 train/validation/test partition keyed only by seed.",
    "cardinality": "Per seed: 4 fractions * 3 lineage conditions = 12 regeneration cells, plus 1 genome-only cell and 1 cold-retraining cell, for 14 evaluation cells; with 8 seeds this is 112 evaluation cells. Adding one common source-training cell per seed gives 120 total bounded cells.",
    "cost_accounting": "Regeneration and cold-retraining cost count development steps, parameter updates, multiply-adds, local messages, and latency proxy ticks using one frozen accounting implementation. Compare costs at the same recovered-function target; cold retraining must reach that target within its frozen budget for an uncensored economic comparison.",
    "decision_rule": "Positive requires every preregistered metric threshold to pass. Negative applies if either causal order-advantage threshold fails or no sufficient ordered suffix exists. All other combinations are mixed.",
    "evidence_anchor": "YRE-b1c3f03e26fad1da0c83299346b04cf5 reports full_ordered_functional_recovery_ratio=0.7291666666666666, full_history_order_advantage=0.5208333333333333, ordered_vs_shuffled_lineage_recovery_auc_advantage=0.33203124999999994, minimal_sufficient_ordered_suffix_fraction=2.0, regeneration_cost_ratio_vs_cold_retrain_at_minimal_suffix=10.0, retained_lineage_byte_ratio_at_minimal_suffix=2.0, and global_signal_fraction=0.0; no unreported interpretation is assumed.",
    "functional_recovery_ratio": "For each cell, compute the unweighted mean across six tasks of min(1, post-regeneration test accuracy / max(pre-destruction test accuracy,1e-12)). Aggregate by arithmetic mean across the eight seeds.",
    "lineage_conditions": "At each positive retention fraction run ordered, shuffled, and reversed conditions using the same selected records and identical canonical serialization length.",
    "locality_constraint": "Developmental transitions may read only a cell's state and radius-one neighbor state; any global-control read or message sets global_signal_fraction above zero and fails the locality gate.",
    "multiple_testing": "No alternative thresholds, subsets, seed exclusions, fraction grids, aggregations, or post-result mechanism variants are permitted.",
    "phenotype_intervention": "After source training, delete all active phenotype parameters and transient optimizer state before every regeneration condition; retain only the common genome plus the condition-authorized lineage bytes.",
    "randomness": "Only the eight declared seeds may influence initialization, partitions, task order, and the frozen shuffle permutation; no retries, seed replacement, or result-conditioned branching are permitted.",
    "recovery_auc": "For each ordering condition, use the shared genome-only recovery at fraction 0 and that condition's recovery at fractions 0.25,0.50,0.75,1.00; compute trapezoidal AUC over the fixed fraction axis, then take the arithmetic mean of paired seed-level AUC differences.",
    "regeneration_cost_ratio": "At the minimal sufficient suffix, divide regeneration accounted cost by cold-retraining accounted cost to the same aggregate functional target. If no sufficient suffix exists or cold retraining is censored, report 2.0 and classify the economic comparison as mixed unless the no-suffix rule already makes it negative.",
    "resource_accounting": "Record active parameter count, peak resident bytes, persistent bytes, local-message count and bytes, development steps, multiply-adds, and latency proxy ticks for every cell.",
    "retained_byte_ratio": "At the minimal sufficient suffix, divide canonical serialized genome-plus-lineage bytes by canonical serialized genome-plus-discarded-phenotype bytes from the same source cell. If no sufficient suffix exists, report 2.0.",
    "retention_fractions": "Positive suffix fractions are [0.25,0.50,0.75,1.00], corresponding exactly to [12,24,36,48] of the 48 lineage events; genome-only supplies the shared zero-fraction point.",
    "shuffle_rule": "Use a deterministic Fisher-Yates permutation keyed by SHA-256(experiment_id || seed || retention_event_count || 'shuffle'); resample is forbidden.",
    "source_training": "Each of the six tasks receives exactly eight developmental epochs, producing exactly 48 lineage events per seed before phenotype destruction.",
    "sufficient_suffix_rule": "The minimal sufficient ordered suffix is the smallest preregistered positive fraction whose aggregate functional recovery ratio is at least 0.75. If none qualifies, report minimal_sufficient_ordered_suffix_fraction as 1.25 and classify the economic-window claim as negative.",
    "task_sequence": "For each seed, one deterministic permutation of the six task IDs is generated before training and reused unchanged by every intervention and control for that seed."
  },
  "metrics": [
    {
      "name": "full_ordered_functional_recovery_ratio",
      "comparator": "\u003e=",
      "threshold": 0.75
    },
    {
      "name": "ordered_vs_shuffled_lineage_recovery_auc_advantage",
      "comparator": "\u003e",
      "threshold": 0.1
    },
    {
      "name": "ordered_vs_reversed_lineage_recovery_auc_advantage",
      "comparator": "\u003e",
      "threshold": 0.1
    },
    {
      "name": "minimal_sufficient_ordered_suffix_fraction",
      "comparator": "\u003c=",
      "threshold": 0.75
    },
    {
      "name": "regeneration_cost_ratio_vs_cold_retrain_at_minimal_suffix",
      "comparator": "\u003c",
      "threshold": 1
    },
    {
      "name": "retained_lineage_byte_ratio_at_minimal_suffix",
      "comparator": "\u003c",
      "threshold": 1
    },
    {
      "name": "cold_retrain_target_reach_fraction",
      "comparator": "==",
      "threshold": 1
    },
    {
      "name": "global_signal_fraction",
      "comparator": "==",
      "threshold": 0
    }
  ],
  "seeds": [
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7
  ],
  "compute_seconds": 1800,
  "stop_conditions": [
    "Stop the complete isolated run at 1800 aggregate compute-seconds and preserve all completed and partial cells.",
    "Stop a cell at 64 regeneration development steps or 640 cold-retraining steps; score a regeneration timeout as zero recovery and retain consumed resources.",
    "Abort and preserve a qualification failure if any requested path is outside the declared allowed roots or if the package contains more than one Python scientific source or more than one preregistration document.",
    "Abort and preserve the run if network, broker, credential, accepted-reference mutation, live-runtime activation, cross-lane access, or undeclared file access is attempted.",
    "Abort and preserve the run if canonical serialization differs between ordered and either byte-matched ordering control at the same seed and retention fraction.",
    "Abort and preserve the run on NaN, infinity, missing cell output, undeclared randomness, seed replacement, result-conditioned branching, or any post-result parameter change.",
    "Stop a cell and score zero recovery if its active-parameter, resident-byte, local-message, development-step, or latency counter exceeds the frozen limits encoded by the scientific source."
  ],
  "positive_meaning": "Across all eight preregistered seeds, chronological order beats both byte-identical ordering controls, an ordered suffix no larger than 0.75 restores at least 0.75 of pre-destruction function, regeneration is cheaper than cold retraining to matched function, retained genome-plus-lineage bytes are fewer than genome-plus-discarded-phenotype bytes, cold retraining provides an uncensored comparator, and regeneration uses no global signal.",
  "negative_meaning": "A causal order gate fails or no preregistered sufficient suffix exists. Preserve and report the sealed result without tuning. This weakens the tested chronological-lineage mechanism under the frozen benchmark but is not evidence against every developmental mechanism or the entire DG-1 thesis.",
  "mixed_meaning": "Temporal order appears causal but does not satisfy all functional, economic, byte, locality, or uncensored-comparison gates, or the shuffled and reversed controls disagree. Preserve the sealed result without tuning; it supports only the passing component and does not establish the North-Star claim."
}
