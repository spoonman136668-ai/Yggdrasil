{
  "experiment_id": "EXP-DG1B-LINEAGE-WINDOW-003",
  "candidate_id": "YGG-A-C1-LINEAGE-WINDOW",
  "harness_id": "yggdrasil-isolated",
  "changed_paths": [
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json",
    "research/applications/plane/exp-dg1b-lineage-window-003.py",
    "research/experiments/exp-dg1b-lineage-window-003.ice"
  ],
  "controls": [
    "Full ordered history is the reproduction control for the verified lineage-regeneration result.",
    "For each retained fraction, the shuffled control contains exactly the same complete event records and bytes as its ordered pair; only record order changes via a seed-derived permutation.",
    "The no-history control receives neither lineage records nor a lineage-derived initialization.",
    "The cold-retraining control uses the same task data, initialization rule, resource accounting, and terminal capability criterion but cannot access lineage state.",
    "Each seed uses one deterministic 50-percent module-damage mask shared by all regeneration conditions; pre-damage scoring is completed before cloning conditions.",
    "All conditions have identical maximum development steps, active-parameter budget, and evaluation schedule."
  ],
  "fixed_parameters": {
    "aggregation_rule": "Use arithmetic means across all 8 seeds with no seed exclusion except a preregistered technical-invalid stop; report every per-seed value.",
    "baseline_commit": "30ca24e5563b7b9860ab17567e62e6fa98e01386",
    "condition_count": "10",
    "condition_set": "ordered suffix at four fractions; shuffled suffix at four matched fractions; no-history; cold-retrain",
    "damage_fraction": "0.50 of active modules",
    "damage_mask_rule": "Rank active module identifiers by SHA-256(seed || module_id) and remove the first ceil(0.50 * active_module_count); reuse the resulting mask across paired conditions.",
    "decision_rule": "Positive only if every preregistered metric passes. Mixed if the full ordered reproduction metrics pass but one or more timing-window or efficiency metrics fail. Negative if full ordered history reproduces recovery yet the order and bounded-window criteria fail. A technical-invalid run is not interpreted scientifically.",
    "full_history_order_advantage_definition": "Mean functional recovery for ordered fraction 1.0 minus mean functional recovery for shuffled fraction 1.0, paired by seed.",
    "functional_recovery_ratio_definition": "For each seed and condition, macro-mean across 6 tasks of min(1,recovered_task_score/pre_damage_task_score); a zero pre-damage score makes that task invalid and stops the run.",
    "global_signal_fraction_definition": "Globally addressed repair messages divided by all repair messages; define as 0 only when both counts are zero.",
    "lineage_recovery_auc_advantage_definition": "Arithmetic mean over fractions [0.125,0.25,0.5,1.0] of the paired-seed mean ordered-minus-shuffled functional recovery difference.",
    "minimal_sufficient_suffix_definition": "Smallest ordered fraction whose across-seed mean functional recovery ratio is at least 0.90; report 2.0 if no fraction qualifies.",
    "ordered_suffix_fractions": "[0.125,0.25,0.5,1.0]",
    "planned_trial_count": "80 = 8 seeds * 10 conditions",
    "post_intervention_task_evaluation_count": "480 = 80 condition-seed trials * 6 tasks",
    "regeneration_cost_definition": "Development steps through the first frozen evaluation point meeting the capability criterion; a failure consumes the full step budget.",
    "regeneration_cost_ratio_definition": "Across-seed mean regeneration cost at the minimal sufficient suffix divided by across-seed mean cold-retraining cost; report 10.0 if no suffix qualifies.",
    "resource_telemetry": "Record active parameters, resident bytes, repair-message bytes, development steps, task-compute operations, and latency-proxy steps for every condition-seed trial.",
    "result_immutability": "Persist all completed per-seed outcomes, including failures and stopped trials; do not modify conditions, thresholds, seeds, code, or aggregation after any result is observed.",
    "retained_lineage_byte_ratio_definition": "Serialized lineage bytes at the minimal sufficient suffix divided by serialized lineage bytes for full ordered history, measured before regeneration; report 2.0 if no suffix qualifies.",
    "seed_count": "8",
    "shuffle_rule": "Permute the retained complete records with a Fisher-Yates permutation driven solely by the trial seed; do not alter record contents or byte encoding.",
    "shuffled_suffix_fractions": "[0.125,0.25,0.5,1.0]",
    "suffix_record_count_rule": "For fraction f and N lineage records, retain the most recent max(1,ceil(f*N)) complete records.",
    "task_count": "6",
    "verified_evidence_id": "YRE-6698aa5ac2fc72d66798f615cd82d230"
  },
  "metrics": [
    {
      "name": "full_ordered_functional_recovery_ratio",
      "comparator": "\u003e=",
      "threshold": 0.9
    },
    {
      "name": "full_history_order_advantage",
      "comparator": "\u003e=",
      "threshold": 0.3
    },
    {
      "name": "ordered_vs_shuffled_lineage_recovery_auc_advantage",
      "comparator": "\u003e=",
      "threshold": 0.2
    },
    {
      "name": "minimal_sufficient_ordered_suffix_fraction",
      "comparator": "\u003c=",
      "threshold": 0.5
    },
    {
      "name": "regeneration_cost_ratio_vs_cold_retrain_at_minimal_suffix",
      "comparator": "\u003c=",
      "threshold": 0.75
    },
    {
      "name": "retained_lineage_byte_ratio_at_minimal_suffix",
      "comparator": "\u003c=",
      "threshold": 0.55
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
    206369,
    231701,
    257053,
    282407
  ],
  "compute_seconds": 1800,
  "stop_conditions": [
    "Stop the entire isolated run when 1800 aggregate compute seconds are reached; preserve every completed and partial trial.",
    "Stop on any attempted filesystem access outside the declared changed paths or any attempted network, credential, broker, live-runtime, or accepted-reference access.",
    "Stop if a lineage condition violates byte identity between an ordered/shuffled pair, if paired conditions receive different damage masks, or if a condition exceeds the frozen active-parameter or development-step budget.",
    "Stop if any required score or resource counter is missing, non-finite, or has an invalid denominator.",
    "Do not stop early because a scientific threshold has passed or failed; execute all 80 planned trials unless a preceding technical or safety stop applies."
  ],
  "positive_meaning": "All frozen metrics pass: full ordered history reproduces functional recovery, temporal order has the required advantage, an ordered suffix no larger than one-half is sufficient, its regeneration cost and retained bytes remain below their thresholds, and no global repair signal is used.",
  "negative_meaning": "The full ordered-history condition reproduces functional recovery, but ordered histories fail to show the preregistered advantage over byte-identical shuffled histories and no suffix at or below one-half satisfies recovery. This is retained as evidence against the bounded timing-window hypothesis, not automatically against DG-1 as a whole.",
  "mixed_meaning": "The full ordered-history condition reproduces functional recovery, but temporal order, a suffix of at most one-half, regeneration cost, retained bytes, or locality fails a frozen threshold. This preserves evidence for regeneration while withholding support for the bounded timing-window mechanism."
}
