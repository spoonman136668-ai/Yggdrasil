{
  "experiment_id": "EXP-DG1B-LINEAGE-INFORMATION-DOSE-014",
  "candidate_id": "C1-LINEAGE-INFORMATION-DOSE",
  "harness_id": "yggdrasil-isolated",
  "changed_paths": [
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json",
    "research/applications/plane/exp-dg1b-lineage-information-dose-014.py",
    "research/experiments/exp-dg1b-lineage-information-dose-014.ice"
  ],
  "controls": [
    "Cold retraining with no retained lineage state.",
    "For each retained fraction 0.25, 0.50, 0.75, and 1.00, a resident-byte-matched state whose lineage content is deterministically erased before recovery.",
    "Identical frozen DG-1B task, functional-recovery criterion, development-step ceiling, active-parameter budget, and resource instrumentation across arms.",
    "Nested informative subsets selected by a preregistered outcome-independent hash rank.",
    "Seeded arm-order permutation within every seed-gap block.",
    "Gap 256 retained as a prespecified boundary condition but excluded from the compactness primary aggregate because verified evidence shows zero full-lineage advantage there."
  ],
  "fixed_parameters": {
    "active_parameter_budget": "4096 active parameters in every arm, matching the verified evidence.",
    "aggregation": "Use medians across the eight fixed seeds; do not exclude completed trials or alter aggregation after results.",
    "analysis_freeze": "All arms, transformations, metrics, thresholds, and interpretations are frozen before isolated execution; no post-result tuning or substitutions.",
    "arm_count": "9",
    "arms": "cold_retraining; informative_0.25; erased_0.25; informative_0.50; erased_0.50; informative_0.75; erased_0.75; informative_1.00; erased_1.00",
    "benchmark": "The same frozen DG-1B functional-regeneration task and functional-recovery criterion used by the verified evidence.",
    "boundary_gap": "256",
    "compactness_fraction_definition": "Smallest tested fraction below 1.00 whose median normalized retained advantage across seeds and primary gaps is at least 0.80; assign 1.01 if none qualifies.",
    "dose_response_definition": "At each primary gap, compute Spearman correlation across the four retained fractions between fraction and median informative-vs-erased advantage across seeds; report the minimum across primary gaps.",
    "erasure_rule": "Replace informative lineage payload bytes using a deterministic seed-derived stream while preserving serialization, byte count, and non-informative envelope fields.",
    "evidence_binding": "YRE-074fbebf0b9d641dc4b2c4489c410fbd at baseline e33a5a26dbb8c5967f465841dc8980424e544d31",
    "fraction_rounding": "For lineage record count N and fraction f, retain exactly max(1,floor(f*N)) records; erased controls use the identical serialized byte length as their paired informative arm.",
    "full_advantage_definition": "For each seed and primary gap: cold_retraining adaptation_cost minus informative_1.00 adaptation_cost.",
    "gap_count": "3",
    "gap_steps": "32,128,256",
    "informative_retained_fractions": "0.25,0.50,0.75,1.00",
    "informative_vs_erased_advantage_definition": "For each paired fraction, seed, and primary gap: (erased adaptation_cost - informative adaptation_cost)/cold_retraining adaptation_cost.",
    "matched_trial_count": "8 seeds * 3 gaps * 9 arms = 216",
    "maximum_development_steps_per_trial": "200",
    "missing_data_rule": "No imputation. Any missing arm makes its seed-gap block incomplete and prevents the completed-matched-trial validity criterion from passing.",
    "normalized_retained_advantage_definition": "For each informative fraction and each seed at primary gaps: (cold cost - informative cost)/(cold cost - informative_1.00 cost); define as 0 when the denominator is non-positive.",
    "primary_gaps": "32,128",
    "resource_fields": "active_parameter_count,resident_bytes,communication_units,development_steps,latency_proxy",
    "seed_count": "8",
    "subset_rule": "Canonicalize lineage records, rank them by SHA-256(seed || canonical_record_id), and retain the lowest-ranked nested fraction; no outcome-dependent selection."
  },
  "metrics": [
    {
      "name": "valid_seed_count",
      "comparator": "==",
      "threshold": 8
    },
    {
      "name": "completed_matched_trial_count",
      "comparator": "==",
      "threshold": 216
    },
    {
      "name": "resource_accounting_completeness_fraction",
      "comparator": "==",
      "threshold": 1
    },
    {
      "name": "minimum_informative_full_lineage_functional_recovery_rate_across_gaps",
      "comparator": "\u003e=",
      "threshold": 0.95
    },
    {
      "name": "maximum_absolute_active_parameter_count_difference_across_arms",
      "comparator": "==",
      "threshold": 0
    },
    {
      "name": "compactness_fraction_for_80_percent_full_advantage",
      "comparator": "\u003c=",
      "threshold": 0.75
    },
    {
      "name": "maximum_median_informative_vs_erased_advantage_fraction_of_cold_across_subfull_fractions_at_primary_gaps",
      "comparator": "\u003e=",
      "threshold": 0.1
    },
    {
      "name": "minimum_spearman_dose_response_across_primary_gaps",
      "comparator": "\u003e=",
      "threshold": 0.8
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
    "Stop before execution if the baseline SHA, North Star SHA-256, or evidence SHA-256 does not match the sealed envelope.",
    "Stop before execution if any requested path is outside the allowed roots or if the harness is not yggdrasil-isolated.",
    "Stop and mark the package invalid on any harness fault, nondeterministic input construction, missing arm, duplicate trial key, or incomplete required resource record; do not replace trials or seeds.",
    "Stop when all 216 preregistered trials finish or when 1800 compute seconds are consumed, whichever occurs first.",
    "Do not stop early for favorable or unfavorable scientific outcomes and do not modify parameters after any result is observed."
  ],
  "positive_meaning": "All validity and accounting criteria pass; full informative lineage recovers function; a retained fraction no greater than 0.75 preserves at least 80% of the full-lineage recovery-cost advantage; informative content beats same-size erased content by at least 0.10 of cold cost for a subfull fraction; and the advantage is monotonically dose-related at both primary gaps. This supports compact informative developmental history as a regeneration mechanism on the frozen benchmark, not a general architectural conclusion.",
  "negative_meaning": "A valid, fully accounted result is negative if no subfull informative state reaches a 0.10 median advantage over its erased control, no tested fraction at or below 0.75 retains 80% of the full advantage, or full-lineage functional recovery falls below threshold. Preserve and report the complete negative result; it weakens this developmental-history mechanism on the frozen benchmark but does not by itself reject DG-1.",
  "mixed_meaning": "After all validity and accounting criteria pass, the result is mixed if at least one but not all three scientific thresholds passes, or if the compact subfull state is beneficial without the preregistered monotone dose pattern. Report every metric and the gap-256 boundary result without changing the design."
}
