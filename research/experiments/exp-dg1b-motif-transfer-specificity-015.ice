{
  "experiment_id": "EXP-DG1B-MOTIF-TRANSFER-SPECIFICITY-015",
  "candidate_id": "CAND-DG1B-MOTIF-TRANSFER-SPECIFICITY-015",
  "harness_id": "yggdrasil-isolated",
  "changed_paths": [
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json",
    "research/applications/plane/exp-dg1b-motif-transfer-specificity-015.py",
    "research/experiments/exp-dg1b-motif-transfer-specificity-015.ice"
  ],
  "controls": [
    "Cold erased-lineage control is run for every seed, motif family, source-target relation, and timing gap.",
    "Byte-matched shuffled-lineage control preserves retained-byte count while destroying lineage-to-development correspondence.",
    "Unrelated-source informative-lineage control separates motif-specific transfer from generic warm-start effects.",
    "All arms use identical active-parameter limits, resident-memory limits, development-step caps, local transition radius, initialization distribution, evaluation threshold, and target observations.",
    "Trial ordering is deterministically permuted from the preregistered seed and does not alter arm assignment.",
    "Analysis includes every valid preregistered trial; negative and null results are retained without parameter or threshold changes."
  ],
  "fixed_parameters": {
    "active_capacity_rule": "identical fixed active-parameter ceiling across all arms",
    "adaptation_cost_definition": "first development step reaching the fixed functional threshold; assign 201 if the threshold is not reached by step 200",
    "analysis_rule": "compute only preregistered aggregate metrics after all valid trials complete; no interim analysis or post-result tuning",
    "benchmark_kind": "deterministic synthetic compositional task benchmark with bounded-neighborhood developmental transitions",
    "control_advantage_definition": "maximum absolute median normalized reduction among shuffled-lineage and erased-lineage controls relative to their matched cold arm",
    "derived_matched_trial_count": "8 seeds * 2 motif families * 2 source-target relations * 4 lineage arms * 3 timing gaps = 384",
    "dose_retention_definition": "median 0.75-dose related-target reduction divided by median full-informative related-target reduction; defined as 0 when the denominator is non-positive",
    "evidence_anchor": "YRE-495c26c5183805d15c19863f63e6031c",
    "functional_threshold": "0.90 of the matched cold arm's terminal functional score, computed within each seed-family-relation-gap block",
    "lineage_arm_count": "4: full-informative, 0.75-dose-informative, byte-matched-shuffled, erased-cold",
    "lineage_dose_fraction": "0.75, frozen from the verified evidence value compactness_fraction_for_80_percent_full_advantage=0.75",
    "lineage_subset_rule": "deterministic hash-ranked selection fixed before execution",
    "locality_rule": "developmental state transitions may read only the module and its fixed-radius neighborhood",
    "maximum_development_steps_per_trial": "200",
    "motif_family_count": "2",
    "normalized_adaptation_cost_reduction": "(cold adaptation cost - tested-arm adaptation cost) / cold adaptation cost within each matched block",
    "relatedness_contrast_definition": "median full-informative normalized reduction on related targets minus median full-informative normalized reduction on unrelated targets",
    "seed_count": "8",
    "source_target_relation_count": "2: motif-related and motif-unrelated",
    "timing_gap_count": "3",
    "timing_gaps_development_steps": "0,32,128"
  },
  "metrics": [
    {
      "name": "valid_seed_count",
      "comparator": "\u003e=",
      "threshold": 8
    },
    {
      "name": "completed_matched_trial_count",
      "comparator": "==",
      "threshold": 384
    },
    {
      "name": "resource_accounting_completeness_fraction",
      "comparator": "==",
      "threshold": 1
    },
    {
      "name": "maximum_absolute_active_parameter_count_difference_across_arms",
      "comparator": "==",
      "threshold": 0
    },
    {
      "name": "median_related_minus_unrelated_normalized_adaptation_cost_reduction",
      "comparator": "\u003e=",
      "threshold": 0.1
    },
    {
      "name": "median_related_75_percent_dose_advantage_retention_fraction",
      "comparator": "\u003e=",
      "threshold": 0.8
    },
    {
      "name": "maximum_absolute_median_shuffled_or_erased_control_advantage_fraction_of_cold",
      "comparator": "\u003c=",
      "threshold": 0.05
    }
  ],
  "seeds": [
    1103,
    2081,
    3253,
    4421,
    5591,
    6763,
    7933,
    9109
  ],
  "compute_seconds": 1800,
  "stop_conditions": [
    "Stop and mark the package invalid if the baseline SHA, North-Star SHA-256, evidence SHA-256, harness identity, or authority generation does not match the sealed request.",
    "Stop before scientific execution if any requested path is outside the allowed roots or if the package contains anything other than one qualification request, one isolated-run request, exactly one Python scientific source, and exactly one preregistration document.",
    "Stop and report an invalid run if the harness cannot enforce identical active-capacity, resident-memory, local-transition, or development-step budgets across arms.",
    "Stop and report an invalid run if deterministic construction cannot produce every preregistered motif-family and relation block for a seed.",
    "Stop when 1800 compute seconds are consumed; preserve all completed and incomplete trial records and do not replace seeds or reduce dimensions.",
    "Do not stop early for favorable, unfavorable, or null scientific results, and do not inspect interim aggregates for decision-making.",
    "Do not alter doses, timing gaps, task families, thresholds, seeds, formulas, or controls after any result is observed."
  ],
  "positive_meaning": "A positive result requires all preregistered metrics to pass jointly: all 384 matched trials across eight seeds complete with full accounting and exact active-capacity parity; informative full lineage yields at least a 0.10 larger median normalized adaptation-cost reduction for motif-related than unrelated targets; the frozen 0.75 lineage dose retains at least 0.80 of the full related-target advantage; and shuffled or erased controls remain within 0.05 of cold. This supports reusable, compact developmental-history motifs under the frozen benchmark but does not establish open-ended growth or superiority to every mandatory architecture baseline.",
  "negative_meaning": "A valid negative result means all validity, trial-completion, accounting, and active-capacity-parity metrics pass but one or more of the three mechanism criteria fail. It weakens this reusable-motif mechanism at the frozen benchmark and dimensions, including the generic-warm-start alternative where applicable, but does not by itself refute the overall developmental thesis. The result remains reportable and must not be rerun with tuned doses, gaps, thresholds, tasks, or seeds under this experiment ID.",
  "mixed_meaning": "A mixed result occurs if validity and resource-parity metrics pass but only some mechanism metrics pass. A relatedness contrast without 0.75-dose retention supports motif specificity but not compact retention; dose retention without a relatedness contrast supports generic retained-state benefit but not reusable motifs; informative and shuffled lineage performing similarly attributes the effect to retained quantity or warm start rather than lineage semantics. Every mixed result is preserved as observed and triggers no threshold or parameter revision within this experiment."
}
