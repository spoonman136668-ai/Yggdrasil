{
  "experiment_id": "EXP-DG1B-WINDOW-CAUSALITY-006",
  "candidate_id": "CAND-DG1B-WINDOW-QUALIFIED-006",
  "harness_id": "yggdrasil-isolated",
  "changed_paths": [
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json",
    "research/applications/plane/exp-dg1b-window-causality-006.py",
    "research/experiments/exp-dg1b-window-causality-006.ice"
  ],
  "controls": [
    "Harness qualification must resolve the sealed DG-1B fixture and frozen scorer before any scientific trial; failure is retained as an invalid result and is not interpreted as a negative scientific result.",
    "Ordered, shuffled, reversed, and leave-one-window-out conditions receive exactly 32 development steps and identical active-parameter, resident-byte, lesion, and communication budgets.",
    "The cold-retraining control receives the same task data and functional scorer but is measured independently for regeneration_cost_ratio.",
    "Condition order is fixed before execution by deterministic seed-indexed cyclic counterbalancing; observed results cannot alter ordering.",
    "Repair transitions are restricted to a von Neumann neighborhood of at most four adjacent cells; all nonlocal signal use is counted in global_signal_fraction.",
    "Functional recovery is scored by the harness-resolved frozen scorer; the scientific source may not modify scorer thresholds or fixture contents.",
    "Resident-byte accounting includes genome, retained lineage state, active phenotype state, routing state, and serialization metadata.",
    "All valid negative and mixed results are retained and reported with the same metric set as positive results."
  ],
  "fixed_parameters": {
    "aggregate_compute_ceiling": "1600 + 200 = 1800 seconds",
    "baseline_commit": "6689ae29cceb4e5e0e64566228c4765e6e26b5c0",
    "cell_count": "64",
    "cell_grid": "8x8",
    "condition_count": "8",
    "conditions": "ordered_full; shuffled_2-1-4-3; reversed_4-3-2-1; leave_out_1; leave_out_2; leave_out_3; leave_out_4; cold_retraining",
    "derived_trial_compute_ceiling": "64 trials * 25 seconds = 1600 seconds",
    "derived_trial_count": "8 conditions * 8 seeds * 1 replicate = 64 trials",
    "development_steps_per_non_cold_condition": "32",
    "evidence_result_id": "YRE-edf591c4f46059c0067293f07534de04",
    "evidence_status": "invalid",
    "fixture": "harness-resolved sealed DG-1B fixture; immutable during qualification and execution",
    "lesion_cell_count": "16",
    "lesion_fraction": "16/64 = 0.25",
    "maximum_seconds_per_trial": "25",
    "neighborhood": "von Neumann radius 1, maximum 4 neighbors",
    "post_result_tuning": "prohibited",
    "qualification_and_aggregation_budget": "200 seconds",
    "qualification_gate": "sealed fixture and frozen scorer both resolve through yggdrasil-isolated",
    "replicates_per_seed_condition": "1",
    "scorer": "harness-resolved frozen DG-1B scorer; immutable during qualification and execution",
    "seeds_per_condition": "8",
    "steps_per_window": "8",
    "window_boundaries": "[0,8),[8,16),[16,24),[24,32)",
    "window_count": "4"
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
      "name": "full_ordered_functional_recovery_ratio",
      "comparator": "\u003e=",
      "threshold": 0.8
    },
    {
      "name": "full_order_advantage",
      "comparator": "\u003e=",
      "threshold": 0.15
    },
    {
      "name": "distributed_order_synergy",
      "comparator": "\u003e=",
      "threshold": 0.05
    },
    {
      "name": "leave_one_sensitive_window_count",
      "comparator": "\u003e=",
      "threshold": 2
    },
    {
      "name": "regeneration_cost_ratio",
      "comparator": "\u003c=",
      "threshold": 0.5
    },
    {
      "name": "condition_resident_byte_spread",
      "comparator": "\u003c=",
      "threshold": 0
    },
    {
      "name": "global_signal_fraction",
      "comparator": "\u003c=",
      "threshold": 0.05
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
    282821
  ],
  "compute_seconds": 1800,
  "stop_conditions": [
    "Before scientific execution, stop and retain an invalid result if the sealed DG-1B fixture or frozen scorer cannot be resolved by yggdrasil-isolated.",
    "Stop and retain an invalid result if the checked baseline commit differs from 6689ae29cceb4e5e0e64566228c4765e6e26b5c0.",
    "Stop and retain an invalid result if any non-cold condition does not receive exactly 32 development steps or if active-parameter, resident-byte, lesion, or communication budgets differ across those conditions.",
    "Stop and retain an invalid result if any requested nonlocal access is unaccounted for or the bounded-neighborhood restriction is violated.",
    "Stop when aggregate compute reaches 1800 seconds; retain completed trials and mark the experiment incomplete and invalid for threshold interpretation.",
    "Stop and retain an invalid result if any required metric is missing or non-finite.",
    "Do not alter seeds, conditions, window boundaries, budgets, scorer, thresholds, or analysis after any result is observed."
  ],
  "positive_meaning": "Both qualification metrics equal 1.0 and all seven scientific thresholds are met without any stop condition, demonstrating preregistered evidence that ordered bounded-neighborhood developmental timing contributes to functional regeneration under matched resource budgets.",
  "negative_meaning": "Qualification succeeds, scoring is valid, and at least one core causal criterion—full_ordered_functional_recovery_ratio, full_order_advantage, distributed_order_synergy, or leave_one_sensitive_window_count—fails. Preserve and report the result unchanged as evidence against this four-window timing mechanism. Failure of fixture or scorer resolution is instead an invalid result, retained as an operational failure and not converted into scientific evidence.",
  "mixed_meaning": "Qualification succeeds and the result is valid, but only a strict subset of the seven scientific thresholds is met. Report every metric and condition without changing thresholds; interpret this as evidence about the specific timing mechanism, not as confirmation or rejection of the overall developmental thesis."
}
