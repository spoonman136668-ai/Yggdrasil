{
  "experiment_id": "EXP-DG1B-WINDOW-CAUSALITY-005",
  "candidate_id": "C1-DG1B-WINDOW-CAUSALITY",
  "harness_id": "yggdrasil-isolated",
  "changed_paths": [
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json",
    "research/applications/plane/exp-dg1b-window-causality-005.py",
    "research/experiments/exp-dg1b-window-causality-005.ice"
  ],
  "controls": [
    "Use only the sealed DG-1B lineage fixture associated with evidence YRE-6d86a276f91c96d948bc26e6e4ba0e14; qualification fails closed if the harness cannot resolve and verify that association.",
    "Hold the complete event multiset, event count, recovery target, functional scorer, developmental budget, and cold-retraining procedure fixed across conditions.",
    "Partition N lineage events into eight contiguous windows using boundaries floor(i*N/8) for i=0..8; window sizes therefore differ by at most one event.",
    "Remove ordinal and timestamp leakage from model inputs or deterministically reindex those fields after permutation; the qualification test must reject any remaining recoverability of original positions from metadata.",
    "Encode every experimental history with the same fixed-width record format and pad to the same resident-byte length; reject the run if condition resident-byte spread is nonzero.",
    "Use one deterministic within-window permutation per seed and window, reused across all paired conditions for that seed.",
    "Pair every condition by seed and reuse identical initialization, lesion state, task data, evaluation checkpoints, and stochastic streams except for the preregistered lineage-order intervention.",
    "Include full ordered history as the positive control, fully within-window-shuffled history as the order-destruction control, and one cold-retraining trajectory per seed as the cost and target-reach control.",
    "Instrument and persist active parameters, resident bytes, communication bytes, development steps, latency proxy, functional score, and global-signal fraction for every trajectory.",
    "Compute all aggregate metrics only after all valid trajectories finish; do not alter windows, thresholds, seeds, scoring, or conditions after observing results."
  ],
  "fixed_parameters": {
    "baseline_commit": "fda0900037583749eb7fee7ff856be108743e0df",
    "cold_retraining_trajectory_count": "8 = 1 cold-retraining control * 8 seeds",
    "condition_resident_byte_spread": "Maximum minus minimum resident lineage bytes across the 18 experimental conditions; fixed-width encoding and padding require zero.",
    "decision_rule": "Positive only if every preregistered metric threshold passes. Negative if any causal-order metric fails. Resource, qualification, or completeness failure is invalid rather than negative.",
    "distributed_order_synergy": "Across-seed median recovery_auc(full-ordered) minus the maximum across the eight single-window-preserved conditions of their across-seed median recovery_auc.",
    "evaluation_checkpoint_count_per_trajectory": "101, including step fractions 0.00 through 1.00 in increments of 0.01 over the fixture's frozen development or retraining budget",
    "experimental_condition_count": "18",
    "experimental_conditions": "1 full-ordered; 1 fully-within-window-shuffled; 8 single-window-preserved with that window ordered and the other seven shuffled; 8 leave-one-window-shuffled with that window shuffled and the other seven ordered.",
    "full_order_advantage": "Across-seed median of paired recovery_auc(full-ordered) minus recovery_auc(fully-within-window-shuffled).",
    "full_ordered_functional_recovery_ratio": "Across-seed median final functional score for full-ordered regeneration divided by the frozen cold-retraining target.",
    "functional_score": "Use the exact frozen functional scorer and target resolved from the qualified evidence-associated DG-1B fixture; substitution or redefinition invalidates the run.",
    "global_signal_fraction": "Global or non-neighborhood developmental signal bytes divided by all developmental communication bytes; any uninstrumented communication invalidates the run.",
    "leave_one_sensitive_window_count": "Count of the eight windows whose leave_one_window_drop_i is at least 0.005.",
    "leave_one_window_drop_i": "Across-seed median of paired recovery_auc(full-ordered) minus recovery_auc(leave-window-i-shuffled).",
    "missing_or_invalid_run_rule": "No imputation and no replacement seeds; report the package as invalid with all partial measurements preserved.",
    "multiple_comparison_rule": "No post-hoc window selection or significance testing; the maximum single-window statistic and fixed sensitive-window count are the only window aggregates.",
    "permutation_rule": "Fisher-Yates within each window using a domain-separated PRNG stream keyed by experiment_id, seed, and window index; no cross-window movement.",
    "recovery_auc": "Trapezoidal area under functional_score divided by the cold-retraining target, over normalized development fraction [0,1], clipped only for reporting to [0,1]; statistical comparisons use the unclipped value.",
    "regeneration_cost_ratio": "Across-seed median full-ordered development steps required to first reach 80% of the frozen target divided by the paired cold-retraining steps required to first reach the same level; failure to reach maps to 1.0.",
    "regeneration_trajectory_count": "144 = 18 experimental conditions * 8 seeds",
    "result_preservation": "Persist positive, negative, mixed, invalid, and timeout outcomes with raw per-seed metrics and intervention labels.",
    "seed_count": "8",
    "total_checkpoint_vectors": "15352 = 152 trajectories * 101 checkpoints",
    "total_trajectory_count": "152 = 144 regeneration trajectories + 8 cold-retraining trajectories",
    "verified_evidence_id": "YRE-6d86a276f91c96d948bc26e6e4ba0e14",
    "verified_evidence_sha256": "5e6d716288ad484a56a923631bf95c2e1c1ff9f7a0dfbe516a3fa52343836086",
    "window_boundary_rule": "For N ordered lineage events, window i is [floor(i*N/8), floor((i+1)*N/8)) for i=0..7.",
    "window_count": "8"
  },
  "metrics": [
    {
      "name": "full_order_advantage",
      "comparator": "\u003e=",
      "threshold": 0.04
    },
    {
      "name": "distributed_order_synergy",
      "comparator": "\u003e=",
      "threshold": 0.03
    },
    {
      "name": "leave_one_sensitive_window_count",
      "comparator": "\u003e=",
      "threshold": 4
    },
    {
      "name": "full_ordered_functional_recovery_ratio",
      "comparator": "\u003e=",
      "threshold": 0.8
    },
    {
      "name": "regeneration_cost_ratio",
      "comparator": "\u003c=",
      "threshold": 0.2
    },
    {
      "name": "condition_resident_byte_spread",
      "comparator": "==",
      "threshold": 0
    },
    {
      "name": "global_signal_fraction",
      "comparator": "==",
      "threshold": 0
    }
  ],
  "seeds": [
    104729,
    130363,
    155921,
    181081,
    205759,
    231481,
    257053,
    282869
  ],
  "compute_seconds": 1800,
  "stop_conditions": [
    "Stop before scientific execution if the evidence-associated fixture, frozen scorer, target, lineage, or cold-retraining control cannot be resolved and qualified without substitution.",
    "Stop and mark invalid if any experimental condition has a different event multiset, event count, resident-byte length, development budget, or evaluation schedule.",
    "Stop and mark invalid if timestamp or ordinal leakage, nonlocal developmental signaling, uninstrumented communication, nonfinite metrics, or nondeterministic condition generation is detected.",
    "Stop when the aggregate wall-clock compute reaches 1800 seconds; preserve every completed and partial trajectory and report timeout without adding seeds or reducing conditions.",
    "Stop after the single preregistered run; do not tune parameters, thresholds, window count, permutations, or analysis in response to observed results."
  ],
  "positive_meaning": "All thresholds pass: full order causally improves recovery, no single preserved window accounts for the effect, at least four windows make detectable contributions, functional recovery remains useful, regeneration stays cheaper than cold retraining, and neither bytes nor global signaling confound the comparison.",
  "negative_meaning": "Failure of any causal-order threshold means this distributed-window mechanism is not supported under the frozen protocol. The result weakens the interpretation that the verified full-history requirement reflects broadly distributed temporal information, but it does not by itself reject DG-1 or the overall developmental thesis.",
  "mixed_meaning": "A mixed result occurs when full order beats full shuffling but distributed-order synergy or the sensitive-window count fails, indicating a real order effect concentrated in one or a few windows; or when causal thresholds pass but functional recovery or regeneration-cost thresholds fail, indicating mechanistic dependence without North-Star-useful regeneration."
}
