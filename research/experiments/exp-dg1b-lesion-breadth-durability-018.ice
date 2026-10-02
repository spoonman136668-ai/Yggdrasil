{
  "experiment_id": "EXP-DG1B-LESION-BREADTH-DURABILITY-018",
  "question": "Does the supported four-cycle related-task regeneration benefit remain specific and useful when each cycle's synthetic lesion expands from the five motif-receiver cells to include two or four adjacent collateral cells, without additional resident or active capacity?",
  "hypothesis": "The fixed early informative motif will retain at least 0.08 control-corrected related-task specificity at the nine-cell lesion breadth through cycle four, with no more than 0.05 attenuation from the five-cell breadth and no material unrelated-task benefit or degradation, while shuffled, erased, and cold controls will not reproduce the effect.",
  "exact_parent_sha": "77434d755a4619644fd267edce36181f721bb378",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "3cd3b3d2fdbbb5b3541d433a527231b38fc441699cd0353fa86f0c3be6f0a905",
  "prior_evidence": {
    "experiment": "EXP-DG1B-REPEATED-REGENERATION-DURABILITY-017",
    "result_class": "supported",
    "result_sha256": "52326e8bb0b3b6b91f97ff4d4bfea211abb2a14435036bd41f5eed0065fe0055"
  },
  "authority": "synthetic computational research only; no wetware, living tissue, production, broker, live, CKB-plane, credential, runner, or authority-system integration",
  "changed_paths": [
    "research/experiments/exp-dg1b-lesion-breadth-durability-018.ice",
    "research/applications/plane/exp-dg1b-lesion-breadth-durability-018.py",
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json"
  ],
  "arms": [
    "intact: apply the fixed informative source motif to receiver cells 0 through 4 after every lesion",
    "shuffled: apply a deterministic within-payload permutation after every lesion",
    "erased: apply an all-zero byte-matched payload after every lesion",
    "cold: regenerate after every lesion with the same zero payload container and no motif information"
  ],
  "inputs_and_model": {
    "model": "The frozen experiment-017 synthetic 16-cell ring, neighborhood radius 1, hidden width 8, fixed mean readout, and four local message steps per example.",
    "source_task": "binary label 1 iff x0+x1+x2+x3 >= 0",
    "related_task": "binary label 1 iff x0+x1+x2+x4 >= 0",
    "unrelated_task": "binary label 1 iff x8+x9+x10+x11 >= 0",
    "motif": "The frozen 320-byte serialized learned state of source cells 0 through 4 after 256 source-development updates.",
    "lesion_breadths": [5, 7, 9],
    "lesion_sets": {
      "5": [0, 1, 2, 3, 4],
      "7": [15, 0, 1, 2, 3, 4, 5],
      "9": [14, 15, 0, 1, 2, 3, 4, 5, 6]
    },
    "lesion_rule": "At every cycle start, zero the listed cells and their permitted incident edge state, then apply the arm payload once only to receiver cells 0 through 4. Lesion sets are nested and frozen.",
    "cycles": [1, 2, 3, 4],
    "updates_per_cycle": 128,
    "evaluations_per_cycle": [0, 16, 32, 48, 64, 80, 96, 112, 128],
    "samples": "4096 train, 1024 validation, and 2048 test observations per task from disjoint counter ranges; deterministic float64 SplitMix64/Box-Muller generation.",
    "numeric_mode": "IEEE-754 float64, deterministic single-process CPU, no accelerator"
  },
  "seeds": [11027, 12037, 13049, 14057, 15061, 16063, 17077, 18089],
  "seed_policy": "Seeds are disjoint from experiments 014 through 017. No seed replacement, exclusion, or extension is permitted.",
  "budgets": {
    "timeout_seconds": 1800,
    "active_parameter_count": 128,
    "payload_bytes": 320,
    "resident_byte_count": 1344,
    "trial_count": 768,
    "matched_block_count": 192,
    "resource_record_count": 768,
    "maximum_development_updates_per_trial": 128,
    "fixed_resources": "All arms and lesion breadths have identical topology, trainable masks, payload-container bytes, resident state, update count, evaluation schedule, example order, and resource-accounting fields. Zeroing more existing cells does not allocate capacity. No capacity growth is allowed."
  },
  "controls": [
    "Each four-arm block forks from one byte-identical post-lesion checkpoint at the same seed, breadth, cycle, and relationship.",
    "The shuffled and erased controls preserve payload shape, byte count, reads, topology, masks, lesion set, and cycle schedule.",
    "Nested lesion sets isolate adjacent lesion breadth while preserving the original receiver cells and ring geometry.",
    "Related and unrelated strata use equal sample counts and frozen task definitions.",
    "The five-cell breadth is the frozen experiment-017 lesion and serves as the internal replication control; the nine-cell breadth is the primary robustness endpoint.",
    "All completed supported, mixed, null, and negative outcomes are retained without tuning."
  ],
  "metrics_and_thresholds": [
    {"name": "completed_matched_block_count", "comparator": "==", "threshold": 192},
    {"name": "completed_trial_count", "comparator": "==", "threshold": 768},
    {"name": "valid_seed_count", "comparator": "==", "threshold": 8},
    {"name": "resource_accounting_completeness_fraction", "comparator": "==", "threshold": 1.0},
    {"name": "maximum_absolute_active_parameter_count_difference_across_arms_and_breadths", "comparator": "==", "threshold": 0.0},
    {"name": "maximum_absolute_resident_byte_count_difference_across_arms_and_breadths", "comparator": "==", "threshold": 0.0},
    {"name": "median_breadth9_cycle4_related_specific_control_corrected_cost_reduction", "comparator": ">=", "threshold": 0.08},
    {"name": "median_breadth5_minus_breadth9_cycle4_specificity_attenuation", "comparator": "<=", "threshold": 0.05},
    {"name": "breadth9_cycle4_supporting_seed_fraction", "comparator": ">=", "threshold": 0.75},
    {"name": "maximum_absolute_median_unrelated_intact_cost_reduction_across_breadths_and_cycles", "comparator": "<=", "threshold": 0.03}
  ],
  "metric_definitions": {
    "adaptation_cost": "Arithmetic mean validation cross-entropy over the nine fixed evaluations within a breadth-cycle block; lower is better.",
    "normalized_reduction": "R_arm=(C_cold-C_arm)/C_cold within a seed, breadth, relationship, and cycle block.",
    "specificity": "D_s,b,c=(R_intact,related-max(R_shuffled,related,R_erased,related))-(R_intact,unrelated-max(R_shuffled,unrelated,R_erased,unrelated)).",
    "breadth9_cycle4_support": "A seed supports breadth robustness iff D_s,9,4 >= 0.08 and D_s,5,4-D_s,9,4 <= 0.05.",
    "collateral": "For every breadth and cycle, take the median across seeds of R_intact,unrelated; report the maximum absolute value.",
    "aggregation": "Medians over all eight seeds; no imputation, winsorization, alternate aggregation, incomplete-block use, or post-result subgrouping."
  },
  "validity_criteria": [
    "The branch, exact parent SHA, North Star hash, and prior sealed evidence identity match this preregistration.",
    "All eight seeds, 192 matched blocks, 768 trials, and 768 complete finite resource records are present.",
    "Every matched block verifies byte-identical pre-arm state and exact active-parameter and resident-byte parity; all breadths retain the same fixed capacity.",
    "The five-cell internal replication has median cycle-four specificity at least 0.10; failure is a valid negative outcome, not grounds to tune or rerun.",
    "The source emits yggdrasil.research-scientific-result.v1 with this exact experiment identifier and a metrics object.",
    "Two duplicate executions from identical inputs and arguments must be byte-identical before qualification."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all ten metric thresholds pass.",
    "mixed": "All construction, accounting, determinism, and completeness criteria pass and at least one, but not all, of the four scientific thresholds passes, including an internal-replication failure with another scientific threshold passing.",
    "null": "All construction, accounting, determinism, and completeness criteria pass, breadth-nine cycle-four specificity has absolute median below 0.03, collateral passes, and no benefit threshold passes.",
    "negative": "All construction, accounting, determinism, and completeness criteria pass but the outcome is neither supported, mixed, nor null; this includes material lesion-breadth attenuation, collateral degradation, or failure of the five-cell internal replication.",
    "invalid": "Any provenance, authority, determinism, cardinality, finiteness, matched-fork, or resource-parity criterion fails. Invalid is not a scientific outcome."
  },
  "stop_conditions": [
    "Stop before execution if provenance, authority boundary, request identity, source identity, or preregistration identity differs from the sealed package.",
    "Stop and emit an invalid result if deterministic construction, nested lesion construction, matched forking, finiteness, resource parity, or required accounting fails.",
    "Stop at 1800 seconds or after all 768 trials finish, whichever occurs first; preserve incomplete records without replacing seeds or reducing dimensions.",
    "Do not stop early for benefit, futility, significance, internal-replication failure, null, mixed, or negative observations."
  ],
  "no_post_result_tuning_rule": "After any primary or diagnostic output is observed, do not change seeds, arms, tasks, lesion sets or breadths, cycles, budgets, capacities, controls, formulas, aggregation, thresholds, classification, or stop conditions under this experiment identifier. Duplicate runs must use byte-identical source and arguments."
}
