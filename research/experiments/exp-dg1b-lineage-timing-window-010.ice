{
  "experiment_id": "EXP-DG1B-LINEAGE-TIMING-WINDOW-010",
  "candidate_id": "C2-EQUAL-CONTENT-TIMING-PERMUTATION",
  "harness_id": "yggdrasil-isolated",
  "changed_paths": [
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json",
    "research/applications/plane/exp-dg1b-lineage-timing-window-010.py",
    "research/experiments/exp-dg1b-lineage-timing-window-010.ice"
  ],
  "controls": [
    "intact_history: eight authentic lineage records in chronological order",
    "age_shift_4: the identical eight-record multiset cyclically reindexed by four positions using frozen permutation [4,5,6,7,0,1,2,3]",
    "reverse_order: the identical eight-record multiset reindexed using frozen permutation [7,6,5,4,3,2,1,0]",
    "deranged_task_assignment: eight authentic records retained while record-to-task associations are rotated by one position across the acquisition sequence",
    "cold_history: 256 checksum-valid zero-payload lineage bytes with no acquired developmental information",
    "All five conditions use eight 32-byte records, 256 resident lineage bytes, identical active parameters, identical task inputs, a 120-step development cap, and no global-signal access.",
    "Condition evaluation order is deterministically permuted from the seed before outcomes are generated; analysis pools only after all preregistered episodes complete.",
    "Functional recovery uses the frozen benchmark success predicate implemented before execution; failed or timed-out regeneration is recorded as recovery=false and development_cost=120.",
    "Report every seed and episode, including failures, timeouts, and integrity failures; do not exclude outliers or rerun individual seeds."
  ],
  "fixed_parameters": {
    "acquisition_episodes_per_seed": "8",
    "analysis_rule": "Evaluate only the preregistered aggregate metrics and thresholds; no subgroup substitution, seed removal, threshold revision, or post-result parameter change",
    "benchmark_protocol": "Frozen DG-1B acquisition and probe generator at baseline fe597b25e79f1c647d2b79b9a0e63b4b81989b0a",
    "confidence_interpretation": "This experiment tests timing-sensitive lineage specifically; failure does not by itself falsify all developmental-history mechanisms or DG-1",
    "cost_ratio_definition": "Median intact repeat development cost over the lower of the two separately computed 16-episode medians for age_shift_4 and reverse_order",
    "development_cost_definition": "Count of bounded developmental controller-state accesses through functional recovery; unrecovered or timed-out episodes receive cost 120",
    "development_step_cap_per_regeneration_episode": "120",
    "equal_content_permutations": "age_shift_4 and reverse_order preserve the exact authentic record multiset and alter only temporal indices/order",
    "evidence_anchor": "YRE-f3fb59e4ed2257e8b260e9fcf69e8d06",
    "functional_recovery_definition": "Frozen benchmark success predicate evaluated after phenotype regeneration",
    "heldout_pair_count_per_condition": "16 = 8 seeds * 2 heldout tasks",
    "heldout_probe_tasks": "8,9",
    "heldout_specificity_definition": "Maximum absolute recovery-rate difference between intact and either equal-content permutation over the two 16-episode condition samples",
    "history_condition_count": "5",
    "history_conditions": "intact_history,age_shift_4,reverse_order,deranged_task_assignment,cold_history",
    "latency_proxy": "Development steps through recovery, capped at 120",
    "lineage_bytes_per_condition": "256 = 8 records * 32 bytes",
    "lineage_bytes_per_record": "32",
    "lineage_records_per_condition": "8",
    "pairwise_cost_fraction_definition": "Fraction of 16 repeat seed-task pairs for which intact cost is strictly lower than both equal-content permutation costs",
    "primary_pair_count": "16 repeat seed-task pairs = 8 seeds * 2 repeat tasks",
    "probe_classes": "repeat,heldout",
    "probe_tasks_per_class": "2",
    "regeneration_episodes_per_seed": "20 = 2 probe classes * 2 tasks per class * 5 history conditions",
    "repeat_probe_tasks": "1,6",
    "resource_accounting": "Record active parameters, total resident bytes, lineage bytes, local communication accesses, global-signal accesses, development steps, controller-state accesses, and deterministic latency proxy for every episode",
    "seed_count": "8",
    "total_acquisition_episodes": "64 = 8 seeds * 8 acquisition episodes",
    "total_regeneration_episodes": "160 = 8 seeds * 20 regeneration episodes per seed",
    "total_task_episodes": "224 = 64 acquisition episodes + 160 regeneration episodes"
  },
  "metrics": [
    {
      "name": "valid_seed_count",
      "comparator": "==",
      "threshold": 8
    },
    {
      "name": "lineage_resident_byte_spread_bytes",
      "comparator": "==",
      "threshold": 0
    },
    {
      "name": "active_parameter_count_spread",
      "comparator": "==",
      "threshold": 0
    },
    {
      "name": "global_signal_access_fraction",
      "comparator": "==",
      "threshold": 0
    },
    {
      "name": "intact_repeat_functional_recovery_rate",
      "comparator": "\u003e=",
      "threshold": 0.875
    },
    {
      "name": "fraction_of_repeat_seed_task_pairs_with_lower_intact_cost_than_both_equal_content_permutations",
      "comparator": "\u003e=",
      "threshold": 0.75
    },
    {
      "name": "median_repeat_regeneration_cost_ratio_intact_vs_best_equal_content_permutation",
      "comparator": "\u003c=",
      "threshold": 0.8
    },
    {
      "name": "max_absolute_heldout_recovery_rate_difference_intact_vs_equal_content_permutations",
      "comparator": "\u003c=",
      "threshold": 0.125
    }
  ],
  "seeds": [
    1103,
    2137,
    3251,
    4271,
    5393,
    6421,
    7547,
    8677
  ],
  "compute_seconds": 1500,
  "stop_conditions": [
    "Do not start unless the qualification request, isolated-run request, scientific source, and preregistration document agree exactly on seeds, dimensions, permutations, metrics, thresholds, and baseline SHA.",
    "Stop before scientific execution if the baseline SHA, North-Star SHA-256, evidence ID, harness identity, or allowed-root checks fail.",
    "Stop and mark the run invalid if any condition has a lineage size other than 256 bytes, a record count other than 8, or an active-parameter count differing from another condition.",
    "Stop and mark the run invalid on any global-signal access or access outside the isolated harness.",
    "Stop at 1500 compute seconds; preserve completed episodes and record all uncompleted preregistered episodes as timeout failures without replacement seeds.",
    "Do not stop early for efficacy or futility, do not rerun failed seeds, and do not modify any parameter after observing an outcome."
  ],
  "positive_meaning": "Positive evidence requires every preregistered metric to satisfy its comparator: intact chronology retains functional repeat recovery, beats both exact-content temporal permutations in at least 12 of 16 repeat seed-task pairs, achieves a pooled median cost ratio no greater than 0.8 against the better permutation, remains heldout-specific, and does so with equal lineage bytes, equal active parameters, and zero global-signal access. This supports a causal timing-sensitive lineage mechanism but does not authorize activation or architectural change.",
  "negative_meaning": "Negative evidence means integrity and resource controls pass but either both preregistered repeat-cost criteria fail or intact repeat recovery is below threshold without a compensating timing-specific cost result. This falsifies the selected timing-sensitive explanation of the verified repeat advantage under the frozen benchmark; it does not erase the prior result or establish that all developmental-history mechanisms fail. Preserve all negative episodes and do not tune or rerun.",
  "mixed_meaning": "Mixed evidence means all integrity and resource controls pass but exactly one repeat-cost criterion passes, or both repeat-cost criteria pass while intact recovery or heldout specificity fails. This supports some sensitivity to record ordering but does not isolate a useful repeat-specific timing mechanism. Preserve and report the complete result without changing permutations, thresholds, seeds, or caps."
}
