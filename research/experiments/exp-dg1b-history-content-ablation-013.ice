{
  "experiment_id": "EXP-DG1B-HISTORY-CONTENT-ABLATION-013",
  "candidate_id": "C1-history-content-ablation",
  "harness_id": "yggdrasil-isolated",
  "changed_paths": [
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json",
    "research/applications/plane/exp-dg1b-history-content-ablation-013.py",
    "research/experiments/exp-dg1b-history-content-ablation-013.ice"
  ],
  "controls": [
    "Use only the yggdrasil-isolated harness at the frozen baseline SHA.",
    "Pair all four arms by seed, task sequence, and gap.",
    "Use the baseline DG-1B task-success predicate unchanged for functional recovery.",
    "Cold-retraining is the denominator for each non-cold arm's primary adaptation-cost ratio.",
    "The equal-content-permuted arm applies one deterministic seed-keyed permutation of complete history records without changing record content or byte count.",
    "The byte-matched-erased arm replaces lineage payload values with the baseline-valid neutral encoding while preserving container shape, metadata, allocation, and resident-byte count.",
    "Run each arm in an isolated process with equivalent cache initialization; use a seed-derived balanced arm order.",
    "Record active parameters, resident bytes, communication units, development steps, and latency proxy for every arm-trial.",
    "Do not change gaps, seeds, arms, thresholds, neutral encoding, task sequence, success predicate, or analysis after observing results."
  ],
  "fixed_parameters": {
    "adaptation_cost": "Development-step count through first functional recovery; an unrecovered trial receives the unchanged benchmark ceiling plus one.",
    "analysis_policy": "Evaluate every preregistered metric after all 128 arm-trials; no substitutions, exclusions, threshold changes, or post-result tuning.",
    "arm_count": "4",
    "arm_trial_count": "8 seeds * 4 gaps * 4 arms = 128",
    "arms": "[intact_lineage,equal_content_permuted_lineage,byte_matched_erased_lineage,cold_retraining]",
    "baseline_sha": "08d1c48016ef4ba72194dc580d9d1c7b52404fb2",
    "benchmark": "DG-1B functional-regeneration benchmark exactly as encoded at baseline_sha",
    "erased_to_intact_cost_ratio": "For each seed and gap, byte_matched_erased_lineage adaptation_cost divided by paired intact_lineage adaptation_cost.",
    "evidence_sha256": "51256e4c4914cafcd5ebccff979a58908a4de77fbc614490d721b7f26c740ec3",
    "execution_order": "Seed-derived balanced order over the four arms within each seed-gap block, fixed before observations.",
    "fixed_setup_and_analysis_allowance_seconds": "392",
    "functional_recovery": "Pass/fail under the unchanged baseline DG-1B held-out task-success predicate.",
    "gap_count": "4",
    "gap_steps": "[0,32,128,256]",
    "heldout_recovery_difference": "Absolute difference between arm recovery proportions over the same eight paired seeds at each gap.",
    "matched_quadruplet_count": "8 seeds * 4 gaps = 32",
    "neutralization_rule": "Replace every lineage-history payload value with the baseline-valid neutral value; retain record count, record boundaries, container shape, metadata, and allocated bytes.",
    "north_star_sha256": "3cd3b3d2fdbbb5b3541d433a527231b38fc441699cd0353fa86f0c3be6f0a905",
    "per_arm_trial_compute_ceiling_seconds": "11",
    "permutation_rule": "Apply exactly one deterministic seed-keyed permutation to complete lineage-history records; preserve every record and byte exactly once.",
    "primary_cost_ratio": "For each seed and gap, non-cold-arm adaptation_cost divided by its paired cold_retraining adaptation_cost.",
    "reported_median": "Median of the eight paired seed-level ratios; never ratio of aggregate medians.",
    "resource_accounting": "For every arm-trial record peak active parameters, peak resident bytes, communication units, development steps, and wall-clock latency proxy.",
    "seed_count": "8",
    "total_compute_ceiling_seconds": "1408 + 392 = 1800",
    "trial_compute_ceiling_seconds": "128 arm-trials * 11 seconds = 1408"
  },
  "metrics": [
    {
      "name": "valid_seed_count",
      "comparator": "==",
      "threshold": 8
    },
    {
      "name": "completed_matched_quadruplet_count",
      "comparator": "==",
      "threshold": 32
    },
    {
      "name": "resource_accounting_completeness_fraction",
      "comparator": "==",
      "threshold": 1
    },
    {
      "name": "minimum_intact_functional_recovery_rate_across_gaps",
      "comparator": "\u003e=",
      "threshold": 0.95
    },
    {
      "name": "maximum_absolute_heldout_recovery_rate_difference_intact_vs_equal_content_permuted_across_gaps",
      "comparator": "\u003c=",
      "threshold": 0.05
    },
    {
      "name": "median_primary_cost_ratio_intact_to_cold_at_gap_0",
      "comparator": "\u003c=",
      "threshold": 0.85
    },
    {
      "name": "median_erased_to_intact_cost_ratio_at_gap_0",
      "comparator": "\u003e=",
      "threshold": 1.1
    },
    {
      "name": "absolute_median_erased_to_intact_cost_ratio_minus_one_at_gap_256",
      "comparator": "\u003c=",
      "threshold": 0.05
    },
    {
      "name": "maximum_absolute_active_parameter_count_difference_intact_vs_erased",
      "comparator": "==",
      "threshold": 0
    },
    {
      "name": "maximum_absolute_resident_byte_difference_intact_vs_erased",
      "comparator": "==",
      "threshold": 0
    }
  ],
  "seeds": [
    104729,
    130363,
    155921,
    181081,
    206369,
    231709,
    257053,
    282403
  ],
  "compute_seconds": 1800,
  "stop_conditions": [
    "Stop before trials if the baseline SHA, North-Star SHA-256, or evidence SHA-256 differs from the preregistered value.",
    "Stop before trials if any requested path, harness, credential, broker, live runtime, or authority lies outside the sealed envelope.",
    "Stop and mark incomplete if the four arms, four gaps, eight seeds, neutralization rule, permutation rule, task predicate, or resource counters cannot be instantiated exactly as preregistered.",
    "Stop when 1800 compute-seconds is reached; preserve all completed trial records and do not replace trials, alter thresholds, or tune parameters.",
    "Do not stop early because of observed metric values; metric-based early stopping is prohibited."
  ],
  "positive_meaning": "All preregistered thresholds pass: intact history reproduces the short-gap advantage, equal-content permutation remains functionally equivalent, byte-matched erasure materially raises short-gap adaptation cost, and that erasure penalty converges away by gap 256 under complete resource accounting.",
  "negative_meaning": "If the run is complete, the intact gap-0 advantage and resource controls pass, but median erased-to-intact cost ratio at gap 0 is below 1.10, preserve the result as a valid falsification of the claim that informative lineage-history content causes the short-gap advantage. A permutation effect above 0.05 separately falsifies permutation invariance.",
  "mixed_meaning": "If the intact gap-0 advantage does not reproduce, recovery falls below threshold, resource matching fails, or the erased penalty appears without convergence at gap 256, preserve the complete result as mixed: it does not isolate the proposed history-content mechanism and must not trigger parameter or threshold changes."
}
