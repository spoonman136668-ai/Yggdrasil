{
  "experiment_id": "EXP-DG1B-NEAR-TOTAL-LESION-DURABILITY-022",
  "question": "Does the supported four-cycle related-task regeneration benefit remain specific under a near-total fifteen-cell lesion when only one of the three nonreceiver cells surviving the supported thirteen-cell lesion remains intact?",
  "hypothesis": "The frozen early informative motif will retain at least 0.07 cycle-four control-corrected related-task specificity for each of the three fifteen-cell singleton-survivor patterns, with no more than 0.04 attenuation from the thirteen-cell control and no material unrelated-task effect, while shuffled, erased, and cold controls will not reproduce the benefit.",
  "exact_parent_sha": "bb95904e5441c1947e53047cb3216c5ec84ee3e7",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "3cd3b3d2fdbbb5b3541d433a527231b38fc441699cd0353fa86f0c3be6f0a905",
  "prior_evidence": {
    "experiment": "EXP-DG1B-LESION-SATURATION-DURABILITY-021",
    "result_class": "supported",
    "result_sha256": "58bd6dabe7b0d85c37874cf7d51d8f1105bf2688014e5c5307235f85cc7b2718"
  },
  "authority": "synthetic computational research only; no wetware, living tissue, production, broker, live, CKB-plane, credential, runner, or authority-system integration",
  "changed_paths": [
    "research/experiments/exp-dg1b-near-total-lesion-durability-022.ice",
    "research/applications/plane/exp-dg1b-near-total-lesion-durability-022.py",
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
    "model": "The frozen experiment-021 synthetic 16-cell ring, neighborhood radius 1, hidden width 8, fixed mean readout, and four local message steps per example.",
    "tasks": {
      "source": "label 1 iff x0+x1+x2+x3 >= 0",
      "related": "label 1 iff x0+x1+x2+x4 >= 0",
      "unrelated": "label 1 iff x8+x9+x10+x11 >= 0"
    },
    "motif": "The frozen 320-byte serialized learned state of source cells 0 through 4 after 256 source-development updates.",
    "lesion_patterns": {
      "breadth13_control": [0,1,2,3,4,6,7,8,10,12,13,14,15],
      "breadth15_survivor5": [0,1,2,3,4,6,7,8,9,10,11,12,13,14,15],
      "breadth15_survivor9": [0,1,2,3,4,5,6,7,8,10,11,12,13,14,15],
      "breadth15_survivor11": [0,1,2,3,4,5,6,7,8,9,10,12,13,14,15]
    },
    "lesion_rule": "At each cycle start, zero the listed unique cells and permitted incident edge state, then apply the arm payload once only to receiver cells 0 through 4. Each breadth-fifteen pattern contains the breadth-thirteen control and adds the other two frozen survivor cells, leaving exactly one of cells 5, 9, or 11 intact.",
    "cycles": [1,2,3,4],
    "updates_per_cycle": 128,
    "evaluations_per_cycle": [0,16,32,48,64,80,96,112,128],
    "samples": "4096 train, 1024 validation, and 2048 test observations per task from disjoint counter ranges; deterministic float64 SplitMix64/Box-Muller generation.",
    "numeric_mode": "IEEE-754 float64, deterministic single-process CPU, no accelerator"
  },
  "seeds": [45007,46021,47051,48073,49081,50087,51109,52127],
  "seed_policy": "Seeds are disjoint from experiments 014 through 021. No seed replacement, exclusion, or extension is permitted.",
  "budgets": {
    "timeout_seconds": 1800,
    "active_parameter_count": 128,
    "payload_bytes": 320,
    "resident_byte_count": 1344,
    "trial_count": 1024,
    "matched_block_count": 256,
    "resource_record_count": 1024,
    "maximum_development_updates_per_trial": 128,
    "fixed_resources": "All arms and patterns use identical topology, masks, payload-container bytes, resident state, updates, evaluation schedule, example order, and accounting fields. Zeroing additional existing cells allocates no capacity; no capacity growth is allowed."
  },
  "controls": [
    "Every four-arm comparison forks from one byte-identical post-lesion checkpoint.",
    "The breadth-thirteen pattern is the exact frozen severe lesion from experiment 021 and is an internal replication control.",
    "The three breadth-fifteen patterns differ only in which one of the same three nonreceiver survivor cells remains intact.",
    "Shuffled and erased controls preserve payload shape, byte count, read operations, topology, masks, lesion schedule, and cycle schedule.",
    "Related and unrelated strata use equal sample counts and frozen task definitions.",
    "All valid supported, mixed, null, and negative outcomes are retained without tuning."
  ],
  "metrics_and_thresholds": [
    {"name":"completed_matched_block_count","comparator":"==","threshold":256},
    {"name":"completed_trial_count","comparator":"==","threshold":1024},
    {"name":"valid_seed_count","comparator":"==","threshold":8},
    {"name":"resource_accounting_completeness_fraction","comparator":"==","threshold":1.0},
    {"name":"maximum_absolute_active_parameter_count_difference_across_arms_and_patterns","comparator":"==","threshold":0.0},
    {"name":"maximum_absolute_resident_byte_count_difference_across_arms_and_patterns","comparator":"==","threshold":0.0},
    {"name":"minimum_median_breadth15_cycle4_related_specific_control_corrected_cost_reduction","comparator":">=","threshold":0.07},
    {"name":"median_breadth13_minus_worst_breadth15_cycle4_specificity_attenuation","comparator":"<=","threshold":0.04},
    {"name":"minimum_breadth15_cycle4_supporting_seed_fraction","comparator":">=","threshold":0.75},
    {"name":"maximum_absolute_median_unrelated_intact_cost_reduction_across_patterns_and_cycles","comparator":"<=","threshold":0.03}
  ],
  "metric_definitions": {
    "adaptation_cost": "Arithmetic mean validation cross-entropy over the nine fixed evaluations within a pattern-cycle block; lower is better.",
    "normalized_reduction": "R_arm=(C_cold-C_arm)/C_cold within a seed, pattern, relationship, and cycle block.",
    "specificity": "D_s,p,c=(R_intact,related-max(R_shuffled,related,R_erased,related))-(R_intact,unrelated-max(R_shuffled,unrelated,R_erased,unrelated)).",
    "breadth15_support": "A seed supports a singleton-survivor pattern iff D_s,p,4 >= 0.07 and D_s,control,4-D_s,p,4 <= 0.04.",
    "attenuation": "For each seed subtract the minimum breadth-fifteen cycle-four specificity from breadth-thirteen control specificity, then take the median across seeds.",
    "collateral": "For every pattern and cycle, take the median across seeds of R_intact,unrelated; report the maximum absolute value.",
    "aggregation": "Medians over all eight seeds; minimum across the three preregistered breadth-fifteen patterns; no imputation, winsorization, alternate aggregation, incomplete-block use, or post-result subgrouping."
  },
  "validity_criteria": [
    "The branch, exact parent SHA, North Star hash, and prior sealed evidence identity match this preregistration.",
    "All eight seeds, 256 matched blocks, 1024 trials, and 1024 complete finite resource records are present.",
    "Every matched block verifies byte-identical pre-arm state plus exact active-parameter and resident-byte parity.",
    "The control has cardinality thirteen; every near-total pattern has cardinality fifteen, includes receiver cells 0 through 4, contains the control, and leaves exactly its named survivor among cells 5, 9, and 11.",
    "The breadth-thirteen control reproduces a cycle-four specificity median of at least 0.08; failure is a valid scientific internal-replication failure.",
    "The source emits yggdrasil.research-scientific-result.v1 with this exact experiment identifier and a metrics object.",
    "Two duplicate executions from identical inputs must be byte-identical before qualification."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all ten metric thresholds pass.",
    "mixed": "Construction, accounting, determinism, and completeness pass and at least one but not all four scientific thresholds passes, including an internal-replication failure with another scientific threshold passing.",
    "null": "Validity passes, every breadth-fifteen cycle-four specificity median has absolute value below 0.03, collateral passes, and no benefit threshold passes.",
    "negative": "Validity passes but the outcome is neither supported, mixed, nor null, including material attenuation, survivor-dependent failure, collateral degradation, or breadth-thirteen internal-replication failure.",
    "invalid": "Any provenance, authority, determinism, cardinality, finiteness, matched-fork, lesion-construction, or resource-parity criterion fails; invalid is not scientific evidence."
  },
  "stop_conditions": [
    "Stop before execution if provenance, authority boundary, manifest identity, source identity, or preregistration identity differs from the sealed package.",
    "Stop and emit an invalid result if deterministic construction, matched forking, lesion construction, finiteness, resource parity, or required accounting fails.",
    "Stop at 1800 seconds or after all 1024 trials finish, whichever occurs first; preserve incomplete records without replacing seeds or reducing dimensions.",
    "Do not stop early for benefit, futility, significance, null, mixed, or negative observations."
  ],
  "no_post_result_tuning_rule": "After any primary or diagnostic output is observed, do not change seeds, arms, tasks, motif, lesion patterns, cycles, budgets, capacities, controls, formulas, aggregation, thresholds, classification, or stop conditions under this experiment identifier. Duplicate runs must use byte-identical source and arguments."
}
