{
  "experiment_id": "EXP-DG1B-LINEAGE-STATE-CAUSALITY-007",
  "candidate_id": "YGG-A-DG1B-LINEAGE-STATE-CAUSALITY-007",
  "harness_id": "yggdrasil-isolated",
  "changed_paths": [
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json",
    "research/applications/plane/exp-dg1b-lineage-state-causality-007.py",
    "research/experiments/exp-dg1b-lineage-state-causality-007.ice"
  ],
  "controls": [
    "Intact lineage state at each of 64, 256, and 1024 persistent bytes.",
    "Within-budget lineage-order permutation preserving byte count and value multiset.",
    "Within-budget deterministic random state preserving byte count and decoder format.",
    "Zero-byte no-state regeneration.",
    "Archived full-phenotype reload positive control, accounted at its complete resident-byte size.",
    "Cold retraining from the same initialization and task data, charged with the same development-step and latency accounting.",
    "Identical current task context, evaluation set, local transition radius, structural-operation budget, initialization family, and scoring procedure across applicable conditions."
  ],
  "fixed_parameters": {
    "aggregation": "Compute per-seed values first and report medians across the eight frozen seeds; no seed exclusion except a preregistered harness-integrity failure.",
    "analysis_policy": "All thresholds, transformations, and sentinel values are fixed here; no post-result parameter, task, seed, condition, or metric changes are allowed.",
    "budgeted_interventions": "intact_lineage,within_lineage_order_permutation,deterministic_random_state",
    "causal_advantage": "At a byte budget, intact functional_recovery_ratio minus max(permuted functional_recovery_ratio, random functional_recovery_ratio).",
    "causally_sufficient_budget": "The smallest tested budget whose intact median functional_recovery_ratio is \u003e=0.80 and causal_advantage is \u003e=0.20; assign sentinel 2048 bytes if none qualifies.",
    "evidence_anchor": "YRE-7c60900fd124f80e88b9f80be7c8d92d reported full_ordered_functional_recovery_ratio=1.0, full_order_advantage=0.0, distributed_order_synergy=0.0, leave_one_sensitive_window_count=0.0, regeneration_cost_ratio=0.5, condition_resident_byte_spread=0.0, and global_signal_fraction=0.0.",
    "functional_recovery_ratio": "Mean post-regeneration task score across all four tasks divided by the corresponding pre-destruction score, clipped only to [0,1], then aggregated as the median across eight seeds.",
    "missing_or_invalid_run_policy": "Any scientifically valid failed run scores zero recovery and remains in the aggregate; harness-integrity failures invalidate qualification and permit only an unchanged rerun.",
    "permutation_rule": "For each seed and byte budget, deterministically permute lineage-record order using SHA-256(seed,budget,'permute') while preserving serialized length and the multiset of serialized record values.",
    "persistent_budgets_bytes": "64,256,1024",
    "persistent_byte_ratio": "Bytes retained at the causally sufficient budget divided by complete serialized bytes of the archived full phenotype; assign 1.0 if no budget is causally sufficient.",
    "phenotype_destruction": "Before regeneration scoring, discard all active learned phenotype parameters, optimizer state, caches, and task-specific active modules; retain only the condition-authorized state and frozen current context.",
    "random_control_rule": "Generate decoder-valid size-matched bytes from SHA-256(seed,budget,'random'); no resampling is permitted.",
    "regeneration_cost_ratio": "At the causally sufficient budget, median regeneration development steps divided by median cold-retraining development steps for the same seed and target score; assign 1.0 if no budget is causally sufficient or the target score is not reached.",
    "resource_accounting": "Record active parameters, resident bytes, communication bytes, development steps, and deterministic latency-proxy operation counts for every run.",
    "run_cardinality": "8 seeds * 3 byte budgets * 3 budgeted interventions + 8 seeds * 3 unbudgeted controls = 96 isolated runs.",
    "task_count": "4",
    "task_evaluation_cardinality": "96 runs * 4 tasks = 384 task-level evaluations.",
    "task_sequence": "Four deterministic task fixtures in one frozen order; the same sequence is used in every condition and seed.",
    "transition_scope": "Local or bounded-neighborhood transitions only; neighborhood radius=1; no global developmental or repair signal.",
    "unbudgeted_control_conditions": "zero_state,archived_full_phenotype_reload,cold_retraining"
  },
  "metrics": [
    {
      "name": "fixture_resolution_success_rate",
      "comparator": "==",
      "threshold": 1
    },
    {
      "name": "scorer_resolution_success_rate",
      "comparator": "==",
      "threshold": 1
    },
    {
      "name": "minimum_causally_sufficient_budget_bytes",
      "comparator": "\u003c=",
      "threshold": 1024
    },
    {
      "name": "functional_recovery_ratio_at_minimum_sufficient_budget",
      "comparator": "\u003e=",
      "threshold": 0.8
    },
    {
      "name": "causal_advantage_at_minimum_sufficient_budget",
      "comparator": "\u003e=",
      "threshold": 0.2
    },
    {
      "name": "regeneration_cost_ratio_at_minimum_sufficient_budget",
      "comparator": "\u003c=",
      "threshold": 0.75
    },
    {
      "name": "persistent_byte_ratio_at_minimum_sufficient_budget",
      "comparator": "\u003c=",
      "threshold": 0.25
    },
    {
      "name": "condition_resident_byte_spread_within_budget",
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
    230003,
    254713,
    279481
  ],
  "compute_seconds": 1800,
  "stop_conditions": [
    "Stop and mark invalid if the baseline SHA, North-Star SHA-256, evidence SHA-256, harness identity, fixture identity, or scorer identity does not match the sealed request.",
    "Stop and mark invalid if any condition exceeds its authorized persistent-byte budget, uses a global developmental signal, or retains phenotype state not authorized for that condition.",
    "Stop and preserve all completed outputs if aggregate compute reaches 1800 seconds; do not replace seeds, reduce conditions, or alter thresholds.",
    "Stop and mark invalid on nondeterministic fixture or scorer resolution; only an unchanged rerun is permitted after infrastructure repair.",
    "Do not stop early for favorable, unfavorable, or apparently conclusive scientific outcomes; execute all 96 runs unless an integrity or compute stop condition occurs.",
    "After first result observation, do not tune tasks, budgets, seeds, transitions, controls, scoring, aggregation, thresholds, or sentinel rules."
  ],
  "positive_meaning": "A positive result requires every registered metric to pass: correct bounded lineage state must causally recover function at a tested budget no larger than 1024 bytes, achieve at least 0.80 recovery and 0.20 advantage over both size-matched history-destroying controls, cost no more than 0.75 of cold retraining, occupy no more than 0.25 of the archived phenotype bytes, and use no global signal.",
  "negative_meaning": "A valid negative result occurs if no tested budget meets both the frozen recovery and causal-advantage criteria, or if intact lineage state does not outperform both size-matched controls by 0.20. The result must be retained unchanged and interpreted as evidence against this lineage-state mechanism, not automatically against the entire developmental thesis.",
  "mixed_meaning": "Mixed evidence means a causally sufficient budget is found and the recovery and causal-advantage gates pass, but one or both efficiency gates fail; this supports a role for developmental history without supporting compact, cheaper regeneration. Harness-resolution or locality failures are invalid rather than mixed."
}
