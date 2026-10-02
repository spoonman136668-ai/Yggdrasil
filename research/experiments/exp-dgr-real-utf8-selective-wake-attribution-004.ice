{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-SELECTIVE-WAKE-ATTRIBUTION-004",
  "program": "DG1 real-byte adaptive granularity diagnostics",
  "question": "Is the selective-wake negative caused primarily by first-half cue-to-second-half distribution mismatch, or is an eight-active motif ceiling itself insufficient to preserve the full real-byte benefit?",
  "hypothesis": "On the exact two held-out files from selective-wake 003, a counterfactual evaluation-optimal eight-motif subset chosen only for attribution from second-half incremental-correct contribution will retain at least 70% of full 16-motif benefit on both files and exceed the frozen cue-selected retained-benefit fraction by at least 0.20. If so, the negative is attributable primarily to cue ranking rather than the eight-active ceiling.",
  "exact_parent_sha": "7e5ca62c28d6744a66441a9909ed5f0d4e52657a",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-SELECTIVE-WAKE-003",
    "classification": "negative",
    "qualification_run_id": "37026853852",
    "result_sha256": "0d6ed8297b03302d93aab6ddcc1d2aa08b10a66fd40c26a9d6447fe2bc39f2a3"
  },
  "authority": "diagnostic research-only; counterfactual evaluation-optimal selection is evaluator-only and must not be promoted into policy",
  "changed_paths": [
    "research/experiments/exp-dgr-real-utf8-selective-wake-attribution-004.ice",
    "research/applications/plane/exp-dgr-real-utf8-selective-wake-attribution-004.py",
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json"
  ],
  "frozen_reuse": [
    "exact six-file corpus and blob identities",
    "exact supported 16-motif learner",
    "exact supported static eight-active pressure ranking",
    "exact selective-wake midpoint split and cue ranking",
    "exact previous-byte baseline and incremental-correct definition"
  ],
  "attribution_sets": {
    "static": "top eight by frozen training utility from resource-pressure 002",
    "cue": "top eight by frozen first-half occurrence count, then training utility, then raw key from selective-wake 003",
    "optimal": "evaluator-only top eight by second-half per-motif incremental correct contribution over previous-byte baseline; ties by frozen training utility then raw key",
    "full": "all sixteen frozen learned motifs"
  },
  "per_motif_eval_contribution": "For each learned motif independently, count second-half occurrences where motif prediction is correct minus occurrences where previous-byte baseline is correct. No interaction term exists because exact four-byte keys are mutually exclusive at a prediction position.",
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
      "valid_evaluation_file_count",
      "==",
      2
    ],
    [
      "minimum_full_incremental_correct_count",
      ">",
      0
    ],
    [
      "minimum_optimal_active_structure_count",
      "==",
      8
    ],
    [
      "maximum_optimal_active_structure_count",
      "==",
      8
    ],
    [
      "minimum_optimal_retained_incremental_correct_fraction",
      ">=",
      0.7
    ],
    [
      "minimum_optimal_minus_cue_retained_fraction",
      ">=",
      0.2
    ],
    [
      "minimum_optimal_minus_static_retained_fraction",
      ">=",
      0
    ],
    [
      "maximum_cue_optimal_jaccard",
      "<=",
      0.875
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
      "invalid_attribution_rows",
      "==",
      0
    ]
  ],
  "attribution_classification": {
    "cue_mismatch": "All validity gates pass, optimal retained fraction >=0.70 on both files, and optimal-cue advantage >=0.20.",
    "capacity_limited": "All validity gates pass but optimal retained fraction <0.70 on either file.",
    "mixed": "Optimal clears 0.70 but optimal-cue advantage is <0.20 on either file, indicating both cue mismatch and limited concentration of utility.",
    "invalid": "Any frozen identity, state reconstruction, split, or contribution accounting drifts."
  },
  "validity_criteria": [
    "Exact parent, North Star, prior negative evidence identity, and all corpus blob identities match.",
    "Static and cue sets are reconstructed byte-identically from prior qualified code.",
    "Optimal selection is used only for attribution and never for deployed/policy claims.",
    "Exactly eight motifs are selected in each static/cue/optimal set.",
    "Full incremental correct count is positive on both files and all metrics are finite.",
    "No retraining, tokenizer, capacity growth, or mutation of learned motif state occurs.",
    "Duplicate executions are byte-identical before evidence sealing."
  ],
  "no_post_result_tuning_rule": "Do not alter corpus, split, set definitions, contribution accounting, thresholds, or attribution classification after any output is observed."
}
