{
  "experiment_id": "EXP-DG1B-LINEAGE-DERANGEMENT-009",
  "candidate_id": "C1-LINEAGE-DERANGEMENT",
  "harness_id": "yggdrasil-isolated",
  "changed_paths": [
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json",
    "research/applications/plane/exp-dg1b-lineage-derangement-009.py",
    "research/experiments/exp-dg1b-lineage-derangement-009.ice"
  ],
  "controls": [
    "Cold-history control uses the same genome, task fixtures, phenotype-discard operation, resource ceilings, and initialization policy but no acquired lineage records.",
    "Deranged-history control uses exactly the intact serialized lineage bytes and record count, with task-affinity associations changed by a seed-frozen no-fixed-point permutation.",
    "Restore one immutable post-acquisition snapshot before every probe-condition episode to eliminate probe-order learning and carryover.",
    "Use identical local-transition, active-parameter, resident-byte, communication, development-step, and latency-proxy accounting in all conditions.",
    "Score all conditions with frozen task-specific functional criteria; neither task fixtures nor thresholds may change after any result is observed.",
    "Log any attempted global read or write as a locality violation; no global signal is permitted in the developmental controller.",
    "Report every seed, failed episode, timeout, and partial result; exclusions are limited to preregistered harness-integrity failures and must remain visible."
  ],
  "fixed_parameters": {
    "acquisition_episode_count": "64 = 8 seeds * 8 acquisition tasks",
    "acquisition_task_count": "8",
    "aggregation_policy": "Compute episode values first, seed-level paired summaries second, and the frozen across-seed median or rate last; do not pool transitions across seeds.",
    "analysis_population": "All 96 scheduled regeneration episodes, including failures and timeouts.",
    "byte_matching_policy": "Intact and deranged lineage serializations must have identical byte length and record count within each seed.",
    "condition_count": "3: intact_history, deranged_history, cold_history",
    "decision_policy": "Evaluate the preregistered primary cost metrics and recovery, byte-equality, and locality guardrails once after all scheduled episodes or a safety stop; perform no threshold, task, seed, permutation, or analysis changes.",
    "derangement_policy": "For each seed, apply one preregistered deterministic no-fixed-point permutation across all 8 acquired task-affinity associations; reuse that permutation for every probe.",
    "development_cost_definition": "Count executed local developmental state transitions through the first frozen functional evaluation; failed recovery is assigned the full episode transition budget.",
    "evidence_anchor_adaptive_heldout_cost_ratio_vs_cold": "0.7524752475247525",
    "evidence_anchor_adaptive_repeat_cost_ratio": "0.5522388059701493",
    "evidence_anchor_experiment": "EXP-DG1B-HISTORY-COMPRESSION-008",
    "evidence_anchor_heldout_functional_recovery_ratio": "1.0",
    "evidence_anchor_lineage_specific_compression_advantage": "0.29850746268656714",
    "evidence_anchor_persistent_byte_ratio": "0.0625",
    "evidence_anchor_repeat_functional_recovery_ratio": "1.0",
    "functional_recovery_definition": "An episode recovers function iff its first post-development evaluation meets the preregistered task-specific score criterion.",
    "global_signal_fraction_definition": "Global-signal accesses divided by all developmental-controller state accesses.",
    "heldout_cost_ratio_definition": "For each seed, mean intact-history cost over its 2 held-out probes divided by mean deranged-history cost over the same probes; aggregate by the median across 8 seeds.",
    "heldout_probe_count": "2",
    "locality_definition": "A developmental transition may read or write only the focal module, its permitted bounded neighbors, and immutable task input; any other access is a violation.",
    "measured_regeneration_episode_count": "96 = 8 seeds * 4 probes * 3 conditions",
    "missing_data_policy": "Do not impute or silently exclude. Treat a scientific failure or timeout as non-recovery with full budget cost; separately flag harness-integrity failures while retaining their records.",
    "phenotype_policy": "Discard all active phenotype before every measured regeneration episode.",
    "probe_count": "4 = 2 repeated + 2 heldout",
    "recovery_difference_definition": "Intact-history recovery rate minus deranged-history recovery rate over the indicated probe class.",
    "repeat_cost_ratio_definition": "For each seed, mean intact-history cost over its 2 repeated probes divided by mean deranged-history cost over the same probes; aggregate by the median across 8 seeds.",
    "repeated_probe_count": "2",
    "seed_count": "8",
    "seed_improvement_definition": "A seed improves when its intact-history mean repeated-probe cost is strictly lower than its deranged-history mean repeated-probe cost.",
    "snapshot_policy": "Restore the same seed-specific post-acquisition snapshot before each of the 12 probe-condition episodes.",
    "total_task_episode_count": "160 = 64 acquisition + 96 regeneration"
  },
  "metrics": [
    {
      "name": "median_repeat_regeneration_cost_ratio_intact_vs_deranged",
      "comparator": "\u003c=",
      "threshold": 0.75
    },
    {
      "name": "fraction_of_seeds_with_lower_repeat_cost_intact_vs_deranged",
      "comparator": "\u003e=",
      "threshold": 0.75
    },
    {
      "name": "median_heldout_regeneration_cost_ratio_intact_vs_deranged",
      "comparator": "\u003c=",
      "threshold": 0.9
    },
    {
      "name": "intact_repeat_functional_recovery_rate",
      "comparator": "\u003e=",
      "threshold": 0.95
    },
    {
      "name": "intact_heldout_functional_recovery_rate",
      "comparator": "\u003e=",
      "threshold": 0.9
    },
    {
      "name": "repeat_recovery_rate_difference_intact_minus_deranged",
      "comparator": "\u003e=",
      "threshold": -0.05
    },
    {
      "name": "heldout_recovery_rate_difference_intact_minus_deranged",
      "comparator": "\u003e=",
      "threshold": -0.05
    },
    {
      "name": "intact_deranged_lineage_byte_spread_bytes",
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
    2137,
    3251,
    4271,
    5393,
    6421,
    7547,
    8677
  ],
  "compute_seconds": 1800,
  "stop_conditions": [
    "Complete exactly 64 acquisition episodes and 96 measured regeneration episodes, then stop.",
    "Do not stop early for efficacy, futility, or an emerging trend.",
    "Stop the isolated run if wall-clock compute reaches 1800 seconds; preserve all completed and partial records and classify unfinished scientific episodes according to the frozen missing-data policy.",
    "Stop on a harness-integrity failure that prevents trustworthy isolation or accounting; preserve diagnostics and all prior records, and do not substitute seeds or rerun with changed parameters.",
    "Stop immediately on any attempted path access outside the declared changed paths or any request for broker, credential, live-runtime, activation, or accepted-reference mutation authority."
  ],
  "positive_meaning": "Both repeated-task primary criteria pass, the held-out cost criterion passes, and every functional-recovery, byte-equality, and locality guardrail passes. This supports the bounded claim that task-affinity-preserving developmental history causally reduces regeneration cost and carries reusable information under the frozen benchmark; it does not establish the overall developmental thesis.",
  "negative_meaning": "Either repeated-task primary cost criterion fails while recovery equivalence, byte equality, and locality remain valid, falsifying the proposed causal compression effect under this mechanism, or a guardrail failure makes the causal interpretation invalid. Negative and invalidating results remain reportable and must not trigger post-result tuning.",
  "mixed_meaning": "The primary repeated-task cost criteria pass but a held-out-transfer criterion or a recovery, byte-equality, or locality guardrail fails; or repeated-task results improve in some seeds without meeting both frozen primary thresholds. This supports only a narrower or inconclusive mechanism claim, and every result must be preserved without tuning."
}
