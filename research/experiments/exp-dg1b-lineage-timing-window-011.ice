{
  "experiment_id": "EXP-DG1B-LINEAGE-TIMING-WINDOW-011",
  "candidate_id": "YGG-A-C1-TIMING-REPRODUCTION",
  "harness_id": "yggdrasil-isolated",
  "changed_paths": [
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json",
    "research/applications/plane/exp-dg1b-lineage-timing-window-011.py",
    "research/experiments/exp-dg1b-lineage-timing-window-011.ice"
  ],
  "controls": [
    "For every seed-task pair, compare intact lineage order with exactly two preregistered permutations of the identical lineage-event multiset.",
    "Keep model initialization, task data, evaluation examples, event content, active-parameter budget, and lineage-resident-byte budget identical across the three timing conditions.",
    "Evaluate all conditions on the same heldout examples and require recovery-rate parity so reduced cost cannot be credited to reduced function.",
    "Reject a seed completely if any of its twelve condition-task trials is missing or invalid; do not replace rejected seeds.",
    "Record global signal access and require zero access in every valid trial.",
    "Compute every metric only after all sealed trials finish; perform no interim selection, threshold changes, seed substitution, or post-result tuning."
  ],
  "fixed_parameters": {
    "active_parameter_count_spread_definition": "Maximum minus minimum active parameter count across the three conditions over all valid trials.",
    "analysis_rule": "Evaluate only the preregistered metrics and thresholds after all trials; no alternative aggregation or subgroup analysis determines the outcome.",
    "functional_recovery_rate_definition": "Fraction of the 64 frozen heldout examples meeting the task-correctness rule after regeneration.",
    "global_signal_access_fraction_definition": "Global-signal reads divided by all recorded signal reads across valid trials; zero reads yields zero.",
    "heldout_examples_per_trial": "64",
    "heldout_prediction_count": "6144",
    "lineage_event_multiset_rule": "Exactly identical within each seed-task triplet; only event order differs.",
    "lineage_resident_byte_spread_definition": "Maximum minus minimum lineage-resident bytes across the three conditions over all valid trials.",
    "median_cost_ratio_definition": "For each repeat seed-task pair, intact cost divided by the lower cost of the two equal-content permutations; report the median over 32 pairs.",
    "pairwise_cost_fraction_denominator": "32 repeat seed-task pairs.",
    "permutation_a_rule": "Reverse the frozen lineage timing windows.",
    "permutation_b_rule": "Apply a seed-keyed cyclic rotation fixed before execution.",
    "regeneration_cost_definition": "Count of observable developmental state-transition applications from discarded phenotype to completed heldout evaluation.",
    "regeneration_trial_count": "96",
    "repeat_seed_task_pair_count": "32",
    "seed_count": "8",
    "task_count": "4",
    "timing_condition_count": "3",
    "timing_conditions": "intact_order,equal_content_permutation_a,equal_content_permutation_b"
  },
  "metrics": [
    {
      "name": "valid_seed_count",
      "comparator": "==",
      "threshold": 8
    },
    {
      "name": "fraction_of_repeat_seed_task_pairs_with_lower_intact_cost_than_both_equal_content_permutations",
      "comparator": "\u003e=",
      "threshold": 0.75
    },
    {
      "name": "median_repeat_regeneration_cost_ratio_intact_vs_best_equal_content_permutation",
      "comparator": "\u003c=",
      "threshold": 0.5
    },
    {
      "name": "intact_repeat_functional_recovery_rate",
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
    104729,
    130363,
    155921,
    181081,
    205759,
    232003,
    257053,
    282089
  ],
  "compute_seconds": 1500,
  "stop_conditions": [
    "Stop and mark the package invalid if execution would exceed 1500 compute seconds; retain all completed partial records without interpreting outcome metrics.",
    "Stop and mark the package invalid if the harness, baseline SHA, North-Star SHA-256, evidence binding, candidate binding, or any frozen dimension differs from this preregistration.",
    "Stop and mark the package invalid if any condition changes the lineage-event multiset, active-parameter budget, resident-byte budget, task data, or heldout examples within a seed-task triplet.",
    "Stop and mark the package invalid if global-signal access is unavailable for measurement or if regeneration cost and functional recovery cannot be computed exactly as preregistered.",
    "Do not stop for favorable or unfavorable scientific results, and do not rerun, replace, or tune any seed after results are observed."
  ],
  "positive_meaning": "Positive support requires all eight preregistered metric comparisons to pass jointly: all seeds valid, intact timing cheaper in at least 75% of repeat seed-task pairs, median cost ratio at most 0.5, intact recovery at least 0.95, recovery difference at most 0.05, zero resource spread, and zero global-signal access.",
  "negative_meaning": "A valid negative result occurs when valid_seed_count is eight but the joint positive criteria are not all met. Preserve and publish the sealed result as evidence that this reproduction did not support the timing-cost mechanism; do not substitute seeds, tune permutations, or reinterpret failed endpoints.",
  "mixed_meaning": "A valid mixed result occurs when all resource, locality, and recovery controls pass but one or both timing-cost criteria fail, or when the timing-cost criteria pass but a recovery or resource-control criterion fails. Preserve every metric and classify the timing mechanism as unresolved; do not change thresholds or add analyses after observation."
}
