{
  "experiment_id": "EXP-DG1B-LINEAGE-TIMING-GAP-012",
  "candidate_id": "C-DG1B-TIMING-GAP-012",
  "harness_id": "yggdrasil-isolated",
  "changed_paths": [
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json",
    "research/applications/plane/exp-dg1b-lineage-timing-gap-012.py",
    "research/experiments/exp-dg1b-lineage-timing-gap-012.ice"
  ],
  "controls": [
    "Use only the yggdrasil-isolated harness; prohibit network, broker, credential, live-runtime, cross-lane, and accepted-reference access.",
    "Use the unchanged baseline commit and supplied verified result only; the prior result fixes the replication target but supplies no additional unreported observations.",
    "For each seed and task, compare intact lineage with exactly two deterministic equal-content permutations: one cyclic rotation and one reversal.",
    "Require each lineage condition to contain the identical serialized record multiset, identical serialized byte count, identical parser path, and identical number of record reads; only record order may differ.",
    "During every gap, run the same frozen bounded-neighborhood transition rule. Gap length is the only timing intervention; no task examples, labels, gradients, or global signals are available during gaps.",
    "Measure regeneration cost as the number of development steps until the frozen functional-recovery criterion is first met; assign the fixed censoring value of 513 when recovery is not reached within 512 steps.",
    "Evaluate recovery with a frozen held-out set that is never exposed during development, gap transitions, or regeneration.",
    "Record active parameters, resident lineage bytes, local-message count, development steps, and latency proxy for every run.",
    "Run all 384 cells even if an early pattern is apparent, except for preregistered safety or integrity stop conditions; preserve incomplete and negative cells.",
    "Compute all metrics once from the frozen analysis code after all valid cells finish; make no threshold, task, gap, seed, or analysis changes after results are observed."
  ],
  "fixed_parameters": {
    "analysis_policy": "single frozen analysis after all cells; no exclusions except preregistered integrity failures; integrity failures remain reported",
    "cell_count_formula": "8 seeds * 4 tasks * 3 lineage conditions * 4 gaps = 384 cells",
    "developmental_neighborhood_radius": "1",
    "evidence_anchor": "YRE-789836de275a40a1b021096d90730bdb: valid_seed_count=8; zero-gap reference ratio=0.75; intact recovery=1.0; heldout recovery difference=0.0; active-parameter spread=0; lineage-byte spread=0; global-signal fraction=0",
    "execution_order": "deterministic seed-major order with task, gap, and lineage condition order independently permuted by a preregistered hash of seed and cell identifiers",
    "functional_recovery_criterion": "heldout task accuracy at least 0.90 of the pre-discard phenotype accuracy",
    "gap_count": "4",
    "gap_steps": "0,16,64,256",
    "global_signal_access_allowed": "false",
    "lineage_condition_count": "3",
    "lineage_conditions": "intact,cyclic_rotation_by_one,reversal",
    "long_gap_timing_window_threshold": "median primary ratio at gap 256 must be \u003e=0.95",
    "maximum_regeneration_steps_per_cell": "512",
    "paired_gap_stratum_count_formula": "8 seeds * 4 tasks * 4 gaps = 128 intact-versus-best-permutation strata",
    "pairwise_ratio_count_formula": "8 seeds * 4 tasks * 4 gaps * 2 permutations = 256 pairwise ratios",
    "primary_ratio_definition": "within each seed-task-gap stratum, intact censored regeneration cost divided by the lower censored regeneration cost of the two equal-content permutations; report the median across 32 seed-task strata at each gap",
    "recovery_difference_definition": "maximum across gaps and permutations of the absolute difference in heldout functional-recovery rate from intact lineage",
    "resource_spread_definition": "maximum minus minimum across lineage conditions within each seed-task-gap stratum",
    "seed_count": "8",
    "seeds": "1103,2207,3301,4409,5501,6607,7703,8807",
    "task_count": "4",
    "task_ids": "T0,T1,T2,T3",
    "task_order": "T0,T1,T2,T3",
    "time_budget_seconds": "1800",
    "trajectory_definition": "a seed-task primary-ratio sequence ordered by gaps 0,16,64,256 is nondecreasing when each successive value is greater than or equal to the preceding value",
    "unrecovered_cost_censor_value": "513",
    "zero_gap_replication_threshold": "median primary ratio at gap 0 must be \u003c=0.80"
  },
  "metrics": [
    {
      "name": "valid_seed_count",
      "comparator": "==",
      "threshold": 8
    },
    {
      "name": "median_primary_cost_ratio_at_gap_0",
      "comparator": "\u003c=",
      "threshold": 0.8
    },
    {
      "name": "median_primary_cost_ratio_at_gap_256",
      "comparator": "\u003e=",
      "threshold": 0.95
    },
    {
      "name": "fraction_of_32_seed_task_ratio_trajectories_that_are_nondecreasing",
      "comparator": "\u003e=",
      "threshold": 0.75
    },
    {
      "name": "intact_functional_recovery_rate_across_all_gaps",
      "comparator": "\u003e=",
      "threshold": 0.95
    },
    {
      "name": "max_absolute_heldout_recovery_rate_difference_intact_vs_equal_content_permutations",
      "comparator": "\u003c=",
      "threshold": 0.05
    },
    {
      "name": "active_parameter_count_spread",
      "comparator": "==",
      "threshold": 0
    },
    {
      "name": "lineage_resident_byte_spread_bytes",
      "comparator": "==",
      "threshold": 0
    },
    {
      "name": "global_signal_access_fraction",
      "comparator": "==",
      "threshold": 0
    }
  ],
  "seeds": [
    1103,
    2207,
    3301,
    4409,
    5501,
    6607,
    7703,
    8807
  ],
  "compute_seconds": 1800,
  "stop_conditions": [
    "Stop before scientific execution if the baseline SHA, North-Star SHA-256, or evidence SHA-256 does not exactly match the envelope.",
    "Stop before scientific execution if any requested path is outside the allowed roots or if the harness is not yggdrasil-isolated.",
    "Stop and preserve all produced artifacts if any run accesses a global signal, network, broker, credential, live runtime, accepted reference, or cross-lane resource.",
    "Stop and preserve partial results if serialized lineage record multisets or byte counts differ between the three lineage conditions.",
    "Stop and preserve partial results if total wall-clock compute reaches 1800 seconds; mark all unrun cells missing and do not replace seeds or reduce dimensions.",
    "Stop and preserve partial results on non-finite metrics, source-integrity failure, or inability to account for active parameters, resident bytes, messages, development steps, and latency.",
    "Do not stop for futility, apparent confirmation, apparent refutation, or an unfavorable result."
  ],
  "positive_meaning": "Support for the timing-window hypothesis requires all preregistered metrics to pass: replication of the zero-gap advantage, disappearance of that advantage by 256 local transitions, predominantly nondecreasing cost-ratio trajectories, maintained functional recovery, matched resource accounting, and zero global-signal access. This localizes the verified order effect to a bounded temporal mechanism; it does not by itself establish reusable developmental motifs.",
  "negative_meaning": "A negative result for the selected timing-window hypothesis occurs if the zero-gap effect fails to replicate or, more discriminatingly, if the intact-lineage ratio remains at or below 0.80 at 256 gap steps while recovery and resource controls remain matched. Preserve and report it without tuning; persistence at the long gap favors durable developmental-history compression over the proposed transient trace but does not establish the overall developmental thesis.",
  "mixed_meaning": "A mixed result is any preregistered valid outcome in which the zero-gap advantage replicates but the long-gap ratio lies between 0.80 and 0.95, trajectories are materially nonmonotonic, or recovery/resource controls diverge. It is preserved as evidence that timing and lineage order interact but does not establish either a bounded timing trace or durable compression."
}
