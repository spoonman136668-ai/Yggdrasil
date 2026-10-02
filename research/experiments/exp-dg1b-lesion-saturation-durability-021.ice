{
  "experiment_id": "EXP-DG1B-LESION-SATURATION-DURABILITY-021",
  "question": "At the supported dispersed nine-cell lesion, does four-cycle related-task regeneration remain specific as nonreceiver collateral loss increases from four cells to six and eight cells without additional resident or active capacity?",
  "hypothesis": "The frozen early informative motif will retain at least 0.08 cycle-four control-corrected related-task specificity at the severe thirteen-cell lesion breadth, with no more than 0.04 attenuation from the nine-cell dispersed control and no material unrelated-task effect, while shuffled, erased, and cold controls will not reproduce the benefit.",
  "exact_parent_sha": "7d8b3b8df754937b0f59fb75f13d9295fe0c0c83",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "3cd3b3d2fdbbb5b3541d433a527231b38fc441699cd0353fa86f0c3be6f0a905",
  "prior_evidence": {
    "experiment": "EXP-DG1B-LESION-DISPERSION-DURABILITY-020",
    "result_class": "supported",
    "result_sha256": "c214a9504a2983a0ea0eca61b6d9bbe6f48d431c06a199ef60091015e2c9da7b"
  },
  "authority": "synthetic computational research only; no wetware, living tissue, production, broker, live, CKB-plane, credential, runner, or authority-system integration",
  "changed_paths": [
    "research/experiments/exp-dg1b-lesion-saturation-durability-021.ice",
    "research/applications/plane/exp-dg1b-lesion-saturation-durability-021.py",
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json"
  ],
  "arms": [
    "intact: apply the frozen informative 320-byte motif to receiver cells 0 through 4 after every lesion",
    "shuffled: apply a deterministic within-payload permutation after every lesion",
    "erased: apply an all-zero byte-matched payload after every lesion",
    "cold: regenerate after every lesion with the same zero payload container and no motif information"
  ],
  "inputs_and_model": {
    "model": "The frozen experiment-020 synthetic 16-cell ring, neighborhood radius 1, hidden width 8, fixed mean readout, and four local message steps per example.",
    "tasks": {
      "source": "label 1 iff x0+x1+x2+x3 >= 0",
      "related": "label 1 iff x0+x1+x2+x4 >= 0",
      "unrelated": "label 1 iff x8+x9+x10+x11 >= 0"
    },
    "motif": "The frozen 320-byte serialized learned state of source cells 0 through 4 after 256 source-development updates.",
    "lesion_breadths": [9, 11, 13],
    "lesion_sets": {
      "9": [0, 1, 2, 3, 4, 7, 10, 12, 15],
      "11": [0, 1, 2, 3, 4, 6, 7, 10, 12, 13, 15],
      "13": [0, 1, 2, 3, 4, 6, 7, 8, 10, 12, 13, 14, 15]
    },
    "lesion_rule": "At each cycle start, zero the listed unique cells and permitted incident edge state, then apply the arm payload once only to receiver cells 0 through 4. Sets are nested, include the experiment-020 far-dispersed nine-cell control, and add exactly two frozen nonreceiver collateral cells per breadth step.",
    "cycles": [1, 2, 3, 4],
    "updates_per_cycle": 128,
    "evaluations_per_cycle": [0, 16, 32, 48, 64, 80, 96, 112, 128],
    "samples": "4096 train, 1024 validation, and 2048 test observations per task from disjoint counter ranges; deterministic float64 SplitMix64/Box-Muller generation.",
    "numeric_mode": "IEEE-754 float64, deterministic single-process CPU, no accelerator"
  },
  "seeds": [35023, 36037, 37049, 38053, 39079, 40087, 41093, 42101],
  "seed_policy": "Seeds are disjoint from experiments 014 through 020. No replacement, exclusion, or extension is permitted.",
  "budgets": {
    "timeout_seconds": 1800,
    "active_parameter_count": 128,
    "payload_bytes": 320,
    "resident_byte_count": 1344,
    "trial_count": 768,
    "matched_block_count": 192,
    "resource_record_count": 768,
    "maximum_development_updates_per_trial": 128,
    "fixed_resources": "All arms and breadths use identical topology, masks, payload-container bytes, resident state, updates, evaluation schedule, example order, and accounting fields. Zeroing additional existing cells allocates no capacity; no capacity growth is allowed."
  },
  "controls": [
    "Every four-arm comparison forks from one byte-identical post-lesion checkpoint.",
    "The breadth-nine arm is the exact frozen far-dispersed lesion set from experiment 020 and is an internal replication control.",
    "The breadth-eleven and breadth-thirteen sets are nested additions to breadth nine; receiver cells and payload application are identical.",
    "Shuffled and erased controls preserve payload shape, byte count, read operations, topology, masks, lesion schedule, and cycle schedule.",
    "Related and unrelated strata use equal sample counts and frozen task definitions.",
    "All valid supported, mixed, null, and negative outcomes are retained without tuning."
  ],
  "metrics_and_thresholds": [
    {"name": "completed_matched_block_count", "comparator": "==", "threshold": 192},
    {"name": "completed_trial_count", "comparator": "==", "threshold": 768},
    {"name": "valid_seed_count", "comparator": "==", "threshold": 8},
    {"name": "resource_accounting_completeness_fraction", "comparator": "==", "threshold": 1.0},
    {"name": "maximum_absolute_active_parameter_count_difference_across_arms_and_breadths", "comparator": "==", "threshold": 0.0},
    {"name": "maximum_absolute_resident_byte_count_difference_across_arms_and_breadths", "comparator": "==", "threshold": 0.0},
    {"name": "median_breadth13_cycle4_related_specific_control_corrected_cost_reduction", "comparator": ">=", "threshold": 0.08},
    {"name": "median_breadth9_minus_breadth13_cycle4_specificity_attenuation", "comparator": "<=", "threshold": 0.04},
    {"name": "breadth13_cycle4_supporting_seed_fraction", "comparator": ">=", "threshold": 0.75},
    {"name": "maximum_absolute_median_unrelated_intact_cost_reduction_across_breadths_and_cycles", "comparator": "<=", "threshold": 0.03}
  ],
  "metric_definitions": {
    "adaptation_cost": "Arithmetic mean validation cross-entropy over the nine frozen evaluations within a cycle; lower is better.",
    "normalized_reduction": "R_arm=(C_cold-C_arm)/C_cold within a seed, breadth, relationship, and cycle block.",
    "specificity": "D_s,b,c=(R_intact,related-max(R_shuffled,related,R_erased,related))-(R_intact,unrelated-max(R_shuffled,unrelated,R_erased,unrelated)).",
    "breadth13_support": "A seed supports severe-lesion durability iff D_s,13,4 >= 0.08 and D_s,9,4-D_s,13,4 <= 0.04.",
    "collateral": "For each breadth and cycle, median across seeds of R_intact,unrelated; report the maximum absolute value.",
    "aggregation": "Medians over all eight seeds; no imputation, winsorization, alternate aggregation, or incomplete-block use."
  },
  "validity_criteria": [
    "The branch, exact parent SHA, North Star hash, and prior sealed evidence identity match this preregistration.",
    "All eight seeds, 192 matched blocks, 768 trials, and 768 complete resource records are present and finite.",
    "Every matched block verifies byte-identical pre-arm state plus exact active-parameter and resident-byte parity.",
    "Each lesion set has its preregistered unique cardinality, contains receiver cells 0 through 4, and is nested in the next breadth.",
    "The breadth-nine result reproduces a cycle-four specificity median of at least 0.08; failure is a valid scientific internal-replication failure.",
    "The source emits yggdrasil.research-scientific-result.v1 with this exact experiment identifier and a metrics object.",
    "Two duplicate executions from identical inputs must be byte-identical before qualification."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all ten metric thresholds pass.",
    "mixed": "Construction, accounting, determinism, and completeness pass and at least one but not all four scientific thresholds passes, including an internal-replication failure with another scientific threshold passing.",
    "null": "Validity passes, breadth-thirteen cycle-four specificity has absolute median below 0.03, collateral passes, and no benefit threshold passes.",
    "negative": "Validity passes but the outcome is neither supported, mixed, nor null, including material breadth attenuation, collateral degradation, or breadth-nine internal-replication failure.",
    "invalid": "Any provenance, authority, determinism, cardinality, finiteness, matched-fork, lesion-construction, or resource-parity criterion fails; invalid is not scientific evidence."
  },
  "stop_conditions": [
    "Stop before execution if provenance, authority boundary, manifest identity, source identity, or preregistration identity differs from the sealed package.",
    "Stop and emit an invalid result if deterministic construction, matched forking, lesion construction, finiteness, resource parity, or required accounting fails.",
    "Stop at 1800 seconds or after all 768 trials finish, whichever occurs first; preserve incomplete records without replacing seeds or reducing dimensions.",
    "Do not stop early for benefit, futility, significance, null, mixed, or negative observations."
  ],
  "no_post_result_tuning_rule": "After any primary result is observed, do not change seeds, arms, tasks, motif, lesion sets, cycles, budgets, capacities, controls, formulas, aggregation, thresholds, classification, or stop conditions under this experiment identifier. Duplicate runs must use byte-identical source and arguments."
}
