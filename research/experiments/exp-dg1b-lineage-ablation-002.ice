{
  "experiment_id": "EXP-DG1B-LINEAGE-ABLATION-002",
  "candidate_id": "C-DG1B-LINEAGE-ABLATION",
  "harness_id": "yggdrasil-isolated",
  "changed_paths": [
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json",
    "research/applications/plane/exp-dg1b-lineage-ablation-002.py",
    "research/experiments/exp-dg1b-lineage-ablation-002.ice"
  ],
  "controls": [
    "Byte-matched shuffled-lineage control: permute complete fixed-width lineage records using the condition seed while preserving record count, serialization length, and all non-lineage parameters.",
    "No-retained-state cold-retraining control: rebuild from the common initialization with the same data and count all update-equivalent operations in the cost denominator.",
    "Fixed-routed control: use a static routing table with the same maximum active-parameter budget and task data, without developmental structural transitions.",
    "Determinism control: every condition within a seed uses the identical task sequence, samples, initialization values, discard point, evaluation set, and resource caps.",
    "Leakage control: destroy active phenotype arrays before regeneration and prohibit access to pre-discard parameters, optimizer state, or evaluation labels."
  ],
  "fixed_parameters": {
    "active_parameter_growth_ratio_definition": "Fractional increase from the first-task active-parameter count to the final active-parameter count divided by the fractional increase in mastered-task count; mastery means evaluation accuracy at least 0.80. A zero capability-growth denominator is invalid and negative.",
    "aggregation_and_uncertainty": "Report all seed-level values and the macro mean across the eight seeds; additionally report a paired seed bootstrap 95% interval with exactly 10000 resamples generated from seed 1701. Threshold decisions use the preregistered point estimates, not the interval.",
    "derived_experiment_cardinalities": "8 seeds*4 conditions*12 tasks=384 condition-task cells; two accuracy measurements per cell give 768 accuracy measurements; 8*12*1024=98304 unique seed-task examples and 98304*4=393216 condition-example exposures.",
    "derived_task_cardinalities": "Per seed: 12*1024=12288 unique generated examples, comprising 12*768=9216 learning examples and 12*256=3072 evaluation examples.",
    "design": "Paired deterministic 4-condition experiment: ordered_lineage, byte_matched_shuffled_lineage, no_state_cold_retrain, and fixed_routed.",
    "development_budget": "At most 256 local development steps per task and at most 4096 local messages per task; a local message may address only the sender or its two radius-1 neighbors.",
    "discard_protocol": "After each task's pre-discard evaluation, delete all active cell parameters, activations, routing state, and optimizer state; retain only the condition-authorized lineage bytes and the common task context.",
    "evidence_anchor": "YRE-9953675ce43d138070615391910cfe1b reports regeneration_cost_ratio_vs_retrain=0.25, functional_recovery_ratio=0.85, active_parameter_growth_ratio=0.2, resident_byte_growth_ratio=0.15, and global_signal_fraction=0.02; these values are used only to preregister reproduction gates.",
    "failure_handling": "Non-finite values, denominator failures, resource-cap breaches, prohibited state access, or incomplete condition cells are recorded and make the experiment negative; all partial outputs and diagnostics remain preserved.",
    "functional_recovery_ratio_definition": "For each ordered-lineage seed-task cell, post-regeneration evaluation accuracy divided by its pre-discard evaluation accuracy; values are macro-averaged across all 8*12=96 cells. A zero pre-discard accuracy makes the run invalid and negative.",
    "global_signal_fraction_definition": "Messages whose source-to-destination ring distance exceeds 1 divided by all developmental messages; attempted prohibited messages count in the numerator.",
    "implementation_scope": "The single Python scientific source must contain task generation, all four conditions, accounting, metric calculation, and machine-readable result emission; it may use only the Python standard library.",
    "lineage_recovery_advantage_definition": "Macro mean functional_recovery_ratio for ordered_lineage minus the paired macro mean for byte_matched_shuffled_lineage over the same 96 seed-task cells.",
    "model_dimensions": "64 cells arranged in a ring; 16 scalar trainable parameters per cell; neighborhood radius 1; at most 32 active cells; maximum active trainable parameters=32*16=512.",
    "persistent_state_budget": "Exactly one 16-byte fixed-width lineage record per cell, so the lineage budget is 64*16=1024 bytes; ordered and shuffled conditions must serialize to exactly 1024 bytes.",
    "regeneration_cost_ratio_definition": "Total update-equivalent operations used by ordered-lineage regeneration divided by total update-equivalent operations used by no-state cold retraining to reach its frozen stopping rule, aggregated before division across all seeds and tasks.",
    "regeneration_protocol": "Run the frozen radius-1 developmental rule until the 256-step cap or its deterministic convergence predicate; no evaluation labels or pre-discard phenotype values may be read.",
    "resident_byte_growth_ratio_definition": "Fractional increase from first-task to final-task resident bytes divided by the same mastered-task fractional increase used for active_parameter_growth_ratio; resident bytes include active phenotype, retained lineage, routing, and optimizer state. A zero denominator is invalid and negative.",
    "success_rule": "Positive requires every registered metric threshold to pass. No metric may be removed, redefined, or reweighted after results are observed.",
    "task_dimensions": "12 procedural tasks per seed, task IDs 0 through 11; each task has exactly 1024 examples partitioned as the first 768 generated examples for learning and the remaining 256 for evaluation.",
    "task_order": "Task IDs are presented in ascending order 0..11 in every condition; generated examples are determined solely by the listed seed and task ID."
  },
  "metrics": [
    {
      "name": "functional_recovery_ratio",
      "comparator": "\u003e=",
      "threshold": 0.8
    },
    {
      "name": "regeneration_cost_ratio_vs_retrain",
      "comparator": "\u003c=",
      "threshold": 0.35
    },
    {
      "name": "active_parameter_growth_ratio",
      "comparator": "\u003c=",
      "threshold": 0.25
    },
    {
      "name": "resident_byte_growth_ratio",
      "comparator": "\u003c=",
      "threshold": 0.2
    },
    {
      "name": "global_signal_fraction",
      "comparator": "\u003c=",
      "threshold": 0.05
    },
    {
      "name": "ordered_vs_shuffled_lineage_recovery_advantage",
      "comparator": "\u003e=",
      "threshold": 0.1
    }
  ],
  "seeds": [
    1103,
    1229,
    1361,
    1499,
    1613,
    1759,
    1877,
    1999
  ],
  "compute_seconds": 1800,
  "stop_conditions": [
    "Stop and record a negative result if wall-clock compute reaches 1800 seconds.",
    "Stop and record a negative result if any condition exceeds 256 development steps for a task, 4096 developmental messages for a task, 64 total cells, 32 active cells, 512 active trainable parameters, or its authorized retained-state budget.",
    "Stop and record a negative result on any non-finite metric, zero required denominator, prohibited state access, malformed output, or missing condition-task cell.",
    "Do not stop early because a success or failure threshold appears inevitable; absent a safety or resource stop, execute all 384 preregistered condition-task cells."
  ],
  "positive_meaning": "Passing every threshold reproduces the supplied bounded functional-regeneration profile and shows that ordered developmental history provides at least 0.10 more functional recovery than an equal-byte shuffled artifact while remaining cheaper than cold retraining and within active, resident, and locality bounds.",
  "negative_meaning": "A negative result rejects this bounded ordered-lineage mechanism under the frozen task, state, and resource definitions. It does not by itself reject the overall developmental thesis; failures and partial outputs must be retained unchanged.",
  "mixed_meaning": "If all reproduction gates pass but the ordered-versus-shuffled advantage fails, the supplied regeneration observation is reproduced without evidence that lineage ordering is causally important. If the lineage advantage passes while a reproduction gate fails, the lineage mechanism may carry signal but does not meet the North-Star resource or recovery requirements. Either outcome remains preserved and motivates a separately preregistered follow-up, not post-result tuning."
}
