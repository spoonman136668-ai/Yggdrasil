{
  "experiment_id": "EXP-DG1B-HISTORY-COMPRESSION-008",
  "candidate_id": "YGG-A-C1-HISTORY-COMPRESSION",
  "harness_id": "yggdrasil-isolated",
  "changed_paths": [
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json",
    "research/applications/plane/exp-dg1b-history-compression-008.py",
    "research/experiments/exp-dg1b-history-compression-008.ice"
  ],
  "controls": [
    "adaptive_lineage: update the matched 256-byte lineage state only after each completed successful exposure and use it for the next exposure",
    "frozen_lineage: retain the matched state produced after exposure 1 but prohibit all subsequent lineage updates",
    "shuffled_lineage: use a deterministic within-family derangement of another training task's same-exposure lineage state, with no self-matches",
    "cold_retraining: reset developmental state before every episode and provide a zero-filled 256-byte accounted allocation",
    "All four conditions use identical task instances, task order, 1024-active-parameter ceiling, 4096-byte active-phenotype ceiling, 256-byte persistent allocation, local-transition rules, evaluation code, and 512-step episode ceiling.",
    "Condition labels remain hidden from scoring and aggregation until every episode has completed and the result artifact has been sealed."
  ],
  "fixed_parameters": {
    "active_parameter_ceiling": "1024 scalar parameters",
    "active_phenotype_byte_ceiling": "4096 = 1024 parameters * 4 bytes per parameter",
    "adaptive_heldout_cost_ratio_vs_cold_definition": "For each seed-family heldout task, adaptive_lineage cost divided by cold_retraining cost; report the median over 32 values.",
    "adaptive_heldout_recovery_definition": "Mean functional recovery ratio across all 32 adaptive_lineage heldout episodes.",
    "adaptive_repeat_cost_ratio_definition": "For each seed-family-training-task, adaptive_lineage exposure-4 cost divided by exposure-1 cost; report the median over 64 values.",
    "adaptive_repeated_recovery_definition": "Mean functional recovery ratio across all 256 adaptive_lineage repeated-task episodes.",
    "aggregation_rule": "Use only the preregistered per-pair ratios and stated medians or means; do not remove outliers, substitute seeds, reweight tasks, or add post hoc subgroups.",
    "condition_count": "4",
    "condition_resident_byte_spread_definition": "Maximum minus minimum charged persistent resident bytes across the four conditions.",
    "conditions": "adaptive_lineage,frozen_lineage,shuffled_lineage,cold_retraining",
    "development_cost_definition": "Count every bounded-neighborhood transition from episode start through the first successful evaluation; evaluation calls do not count as transitions but their latency is reported separately.",
    "episode_step_ceiling": "512 bounded-neighborhood developmental transitions",
    "evidence_anchor": "YRE-99e22d3f9881c5c88ca7f5fde892904c: recovery_ratio=1.0, minimum_causally_sufficient_budget_bytes=256, persistent_byte_ratio=0.0625, regeneration_cost_ratio=1.0, global_signal_fraction=0.0",
    "failed_episode_cost": "Assign 512 steps to an episode that does not meet the success criterion by the ceiling.",
    "functional_recovery_ratio_definition": "Episode functional score divided by its seed-matched intact phenotype score, clipped to [0,1].",
    "global_signal_fraction_target": "0.0",
    "heldout_episode_count": "128 = 8 seeds * 4 conditions * 4 families * 1 heldout task",
    "heldout_rule": "Heldout tasks never update or contribute to lineage state before their sole scored evaluation.",
    "heldout_tasks_per_family": "1",
    "implementation_freeze": "Freeze source, task generator, fixtures, scorer, condition assignment, thresholds, and hashes before requesting isolated execution.",
    "lineage_budget_bytes": "256",
    "lineage_specific_compression_advantage_definition": "shuffled_repeat_cost_ratio minus adaptive_repeat_cost_ratio.",
    "locality_rule": "Developmental state transitions and communication are restricted to radius-one neighbors; no global task, gradient, population, or summary signal is available.",
    "missing_data_rule": "Treat any missing, invalid, timed-out, or non-finite episode as failed with cost 512 and recovery ratio 0; do not rerun selectively.",
    "persistent_byte_ratio": "0.0625 = 256 persistent bytes / 4096 active-phenotype bytes",
    "post_result_policy": "No parameter, threshold, seed, task, ordering, metric, or stopping-rule changes after any result is observed.",
    "primary_decision_rule": "Positive only if every preregistered metric threshold is met; otherwise retain the complete result and classify it using negative_meaning or mixed_meaning without tuning.",
    "primary_question": "Whether matched adaptive lineage history converts prior causal sufficiency into lower repeated and held-out regeneration cost at fixed storage and recovery",
    "repeated_exposures_per_training_task": "4",
    "repeated_task_episode_count": "1024 = 8 seeds * 4 conditions * 4 families * 2 training tasks * 4 exposures",
    "resident_accounting_rule": "Charge every condition exactly 256 persistent resident bytes; unused control bytes are zero-filled and remain inaccessible.",
    "seed_count": "8",
    "shuffled_repeat_cost_ratio_definition": "For each seed-family-training-task, shuffled_lineage exposure-4 cost divided by exposure-1 cost; report the median over 64 values.",
    "shuffling_rule": "Within each seed, family, and exposure, map each training task to the other training task's lineage state; this two-element derangement is frozen and has no self-match.",
    "success_criterion": "Functional score at least 0.95 of the seed-matched intact phenotype score on the frozen evaluation set.",
    "task_family_count": "4",
    "task_order": "For each seed and family, run both training tasks for exposures 1 through 4 in a frozen round-robin order, then run the heldout task once; apply the same order to every condition.",
    "total_scored_episode_count": "1152 = 1024 repeated-task episodes + 128 heldout episodes",
    "training_tasks_per_family": "2",
    "unique_heldout_task_count": "4 = 4 families * 1 heldout task per family",
    "unique_task_count": "12 = 8 training tasks + 4 heldout tasks",
    "unique_training_task_count": "8 = 4 families * 2 training tasks per family"
  },
  "metrics": [
    {
      "name": "adaptive_repeat_cost_ratio",
      "comparator": "\u003c=",
      "threshold": 0.75
    },
    {
      "name": "lineage_specific_compression_advantage",
      "comparator": "\u003e=",
      "threshold": 0.2
    },
    {
      "name": "adaptive_heldout_cost_ratio_vs_cold",
      "comparator": "\u003c=",
      "threshold": 0.85
    },
    {
      "name": "adaptive_repeated_functional_recovery_ratio",
      "comparator": "\u003e=",
      "threshold": 0.95
    },
    {
      "name": "adaptive_heldout_functional_recovery_ratio",
      "comparator": "\u003e=",
      "threshold": 0.9
    },
    {
      "name": "persistent_byte_ratio",
      "comparator": "==",
      "threshold": 0.0625
    },
    {
      "name": "condition_resident_byte_spread_bytes",
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
    1103,
    2207,
    3301,
    4409,
    5519,
    6619,
    7723,
    8837
  ],
  "compute_seconds": 1800,
  "stop_conditions": [
    "Stop the complete run if wall-clock compute reaches 1800 seconds; score all unexecuted episodes as missing under the frozen missing-data rule.",
    "Stop and seal a negative invalid-run result if locality instrumentation reports any global signal fraction greater than 0.",
    "Stop and seal a negative invalid-run result if any condition exceeds 256 charged persistent bytes, 4096 active phenotype bytes, or 1024 active scalar parameters.",
    "Stop and seal an invalid-run result if fixture or scorer resolution fails; do not replace fixtures, scorers, tasks, or seeds.",
    "Do not stop early for apparent success, apparent failure, effect size, variance, or threshold crossing."
  ],
  "positive_meaning": "Meeting every threshold shows that matched adaptive developmental history reduces both late repeated-task and held-out family-task regeneration cost, preserves functional recovery, uses no global signal, and does so with the same 256-byte persistent allocation and 4096-byte active-phenotype ceiling.",
  "negative_meaning": "Failure of either repeated-cost threshold rejects the proposed history-compression mechanism at the frozen 256-byte budget. Failure only on held-out cost rejects reusable family-level transfer. All negative and partial results remain valid evidence against this mechanism under the preregistered dimensions and must be sealed without tuning; they do not by themselves reject the overall developmental thesis.",
  "mixed_meaning": "If repeated-task compression and lineage specificity pass but held-out cost or recovery fails, the 256-byte state supports task-specific trajectory reuse but not reusable family-level motifs. If held-out improvement passes while lineage specificity fails, attribute the apparent benefit to a shared control or task-order effect rather than matched developmental history. Any recovery failure prevents a claim of useful regeneration even if costs fall."
}
