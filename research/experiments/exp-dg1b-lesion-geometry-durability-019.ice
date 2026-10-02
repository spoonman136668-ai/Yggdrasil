{
  "experiment_id": "EXP-DG1B-LESION-GEOMETRY-DURABILITY-019",
  "question": "At the supported fixed nine-cell lesion breadth, does the four-cycle related-task regeneration benefit remain specific when the four collateral lesions are placed asymmetrically to either side of the five motif-receiver cells?",
  "hypothesis": "The fixed early informative motif will retain at least 0.08 control-corrected related-task specificity through cycle four for centered, left-heavy, and right-heavy nine-cell lesions, with no more than 0.03 attenuation from centered to the worst asymmetric geometry and no material unrelated-task benefit or degradation, while shuffled, erased, and cold controls will not reproduce the effect.",
  "exact_parent_sha": "378de6ace010f41e38abca56c5af5a94214c7be1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "3cd3b3d2fdbbb5b3541d433a527231b38fc441699cd0353fa86f0c3be6f0a905",
  "prior_evidence": {
    "experiment": "EXP-DG1B-LESION-BREADTH-DURABILITY-018",
    "result_class": "supported",
    "result_sha256": "98469cf218d7d61ffa9ceb48575e8dc58cd5d926f792ee5504774619f0bd3a96"
  },
  "authority": "synthetic computational research only; no wetware, living tissue, production, broker, live, CKB-plane, credential, runner, or authority-system integration",
  "changed_paths": [
    "research/experiments/exp-dg1b-lesion-geometry-durability-019.ice",
    "research/applications/plane/exp-dg1b-lesion-geometry-durability-019.py",
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
    "model": "The frozen experiment-018 synthetic 16-cell ring, neighborhood radius 1, hidden width 8, fixed mean readout, and four local message steps per example.",
    "source_task": "binary label 1 iff x0+x1+x2+x3 >= 0",
    "related_task": "binary label 1 iff x0+x1+x2+x4 >= 0",
    "unrelated_task": "binary label 1 iff x8+x9+x10+x11 >= 0",
    "motif": "The frozen 320-byte serialized learned state of source cells 0 through 4 after 256 source-development updates.",
    "lesion_breadth": 9,
    "lesion_geometries": {
      "centered": [14, 15, 0, 1, 2, 3, 4, 5, 6],
      "left_heavy": [12, 13, 14, 15, 0, 1, 2, 3, 4],
      "right_heavy": [0, 1, 2, 3, 4, 5, 6, 7, 8]
    },
    "lesion_rule": "At every cycle start, zero the listed nine cells and their permitted incident edge state, then apply the arm payload once only to receiver cells 0 through 4. Each geometry contains the identical receiver set and exactly four contiguous collateral cells; geometry labels and sets are frozen.",
    "cycles": [1, 2, 3, 4],
    "updates_per_cycle": 128,
    "evaluations_per_cycle": [0, 16, 32, 48, 64, 80, 96, 112, 128],
    "samples": "4096 train, 1024 validation, and 2048 test observations per task from disjoint counter ranges; deterministic float64 SplitMix64/Box-Muller generation.",
    "numeric_mode": "IEEE-754 float64, deterministic single-process CPU, no accelerator"
  },
  "seeds": [19001, 20011, 21013, 22027, 23029, 24043, 25057, 26063],
  "seed_policy": "Seeds are disjoint from experiments 014 through 018. No seed replacement, exclusion, or extension is permitted.",
  "budgets": {
    "timeout_seconds": 1800,
    "active_parameter_count": 128,
    "payload_bytes": 320,
    "resident_byte_count": 1344,
    "trial_count": 768,
    "matched_block_count": 192,
    "resource_record_count": 768,
    "maximum_development_updates_per_trial": 128,
    "fixed_resources": "All arms and lesion geometries have identical topology, trainable masks, payload-container bytes, resident state, lesion breadth, update count, evaluation schedule, example order, and resource-accounting fields. Moving which existing collateral cells are zeroed does not allocate capacity. No capacity growth is allowed."
  },
  "controls": [
    "Each four-arm block forks from one byte-identical post-lesion checkpoint at the same seed, geometry, cycle, and relationship.",
    "The shuffled and erased controls preserve payload shape, byte count, reads, topology, masks, lesion set, and cycle schedule.",
    "All three lesion sets contain the same five receiver cells and four collateral cells, isolating collateral placement at fixed breadth.",
    "Related and unrelated strata use equal sample counts and frozen task definitions.",
    "The centered geometry exactly reproduces experiment 018's primary nine-cell lesion and serves as the internal replication control; the asymmetric geometries are the primary robustness endpoints.",
    "All completed supported, mixed, null, and negative outcomes are retained without tuning."
  ],
  "metrics_and_thresholds": [
    {"name": "completed_matched_block_count", "comparator": "==", "threshold": 192},
    {"name": "completed_trial_count", "comparator": "==", "threshold": 768},
    {"name": "valid_seed_count", "comparator": "==", "threshold": 8},
    {"name": "resource_accounting_completeness_fraction", "comparator": "==", "threshold": 1.0},
    {"name": "maximum_absolute_active_parameter_count_difference_across_arms_and_geometries", "comparator": "==", "threshold": 0.0},
    {"name": "maximum_absolute_resident_byte_count_difference_across_arms_and_geometries", "comparator": "==", "threshold": 0.0},
    {"name": "minimum_median_asymmetric_cycle4_related_specific_control_corrected_cost_reduction", "comparator": ">=", "threshold": 0.08},
    {"name": "median_centered_minus_worst_asymmetric_cycle4_specificity_attenuation", "comparator": "<=", "threshold": 0.03},
    {"name": "minimum_asymmetric_cycle4_supporting_seed_fraction", "comparator": ">=", "threshold": 0.75},
    {"name": "maximum_absolute_median_unrelated_intact_cost_reduction_across_geometries_and_cycles", "comparator": "<=", "threshold": 0.03}
  ],
  "metric_definitions": {
    "adaptation_cost": "Arithmetic mean validation cross-entropy over the nine fixed evaluations within a geometry-cycle block; lower is better.",
    "normalized_reduction": "R_arm=(C_cold-C_arm)/C_cold within a seed, geometry, relationship, and cycle block.",
    "specificity": "D_s,g,c=(R_intact,related-max(R_shuffled,related,R_erased,related))-(R_intact,unrelated-max(R_shuffled,unrelated,R_erased,unrelated)).",
    "asymmetric_cycle4_support": "A seed supports a given asymmetric geometry iff D_s,g,4 >= 0.08 and D_s,centered,4-D_s,g,4 <= 0.03; report the smaller support fraction across left-heavy and right-heavy geometries.",
    "geometry_attenuation": "For each seed, D_s,centered,4 minus min(D_s,left-heavy,4,D_s,right-heavy,4); report the median across seeds.",
    "collateral": "For every geometry and cycle, take the median across seeds of R_intact,unrelated; report the maximum absolute value.",
    "aggregation": "Medians over all eight seeds; no imputation, winsorization, alternate aggregation, incomplete-block use, geometry pooling, or post-result subgrouping."
  },
  "validity_criteria": [
    "The branch, exact parent SHA, North Star hash, and prior sealed evidence identity match this preregistration.",
    "All eight seeds, 192 matched blocks, 768 trials, and 768 complete finite resource records are present.",
    "Every matched block verifies byte-identical pre-arm state and exact active-parameter and resident-byte parity; every geometry contains exactly nine unique cells including receiver cells 0 through 4.",
    "The centered internal replication has median cycle-four specificity at least 0.08; failure is a valid negative outcome, not grounds to tune or rerun.",
    "The source emits yggdrasil.research-scientific-result.v1 with this exact experiment identifier and a metrics object.",
    "Two duplicate executions from identical inputs and arguments must be byte-identical before qualification."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all ten metric thresholds pass.",
    "mixed": "All construction, accounting, determinism, and completeness criteria pass and at least one, but not all, of the four scientific thresholds passes, including an internal-replication failure with another scientific threshold passing.",
    "null": "All construction, accounting, determinism, and completeness criteria pass, both asymmetric cycle-four specificity medians have absolute value below 0.03, collateral passes, and no benefit threshold passes.",
    "negative": "All construction, accounting, determinism, and completeness criteria pass but the outcome is neither supported, mixed, nor null; this includes material geometry attenuation, collateral degradation, or failure of the centered internal replication.",
    "invalid": "Any provenance, authority, determinism, cardinality, finiteness, matched-fork, lesion-construction, or resource-parity criterion fails. Invalid is not a scientific outcome."
  },
  "stop_conditions": [
    "Stop before execution if provenance, authority boundary, request identity, source identity, or preregistration identity differs from the sealed package.",
    "Stop and emit an invalid result if deterministic construction, fixed-breadth lesion construction, matched forking, finiteness, resource parity, or required accounting fails.",
    "Stop at 1800 seconds or after all 768 trials finish, whichever occurs first; preserve incomplete records without replacing seeds or reducing dimensions.",
    "Do not stop early for benefit, futility, significance, internal-replication failure, null, mixed, or negative observations."
  ],
  "no_post_result_tuning_rule": "After any primary or diagnostic output is observed, do not change seeds, arms, tasks, lesion geometries, cycles, budgets, capacities, controls, formulas, aggregation, thresholds, classification, or stop conditions under this experiment identifier. Duplicate runs must use byte-identical source and arguments."
}
