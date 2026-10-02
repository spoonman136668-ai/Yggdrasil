{
  "experiment_id": "EXP-DG1B-TOTAL-LESION-DURABILITY-023",
  "question": "Does the supported four-cycle related-task regeneration benefit remain specific after a total sixteen-cell synthetic lesion, when no pre-lesion phenotype survives and only the fixed compact motif is restored to receiver cells 0 through 4?",
  "hypothesis": "The frozen early informative motif will retain at least 0.06 cycle-four control-corrected related-task specificity after the total lesion, with no more than 0.03 attenuation from the supported breadth-fifteen control and no material unrelated-task effect, while shuffled, erased, and cold controls will not reproduce the benefit.",
  "exact_parent_sha": "a2e9278a4f145957a22071a19315ca16e658228f",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "3cd3b3d2fdbbb5b3541d433a527231b38fc441699cd0353fa86f0c3be6f0a905",
  "prior_evidence": {
    "experiment": "EXP-DG1B-NEAR-TOTAL-LESION-DURABILITY-022",
    "result_class": "supported",
    "result_sha256": "d94b6bcd1af33fed4a22dae5593b90e673e86c4c3342449c2ee7fff08b9a3ad5"
  },
  "authority": "synthetic computational research only; no wetware, living tissue, production, broker, live, CKB-plane, credential, runner, or authority-system integration",
  "changed_paths": [
    "research/experiments/exp-dg1b-total-lesion-durability-023.ice",
    "research/applications/plane/exp-dg1b-total-lesion-durability-023.py",
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
    "model": "The frozen experiment-022 synthetic 16-cell ring, neighborhood radius 1, hidden width 8, fixed mean readout, and four local message steps per example.",
    "tasks": {
      "source": "label 1 iff x0+x1+x2+x3 >= 0",
      "related": "label 1 iff x0+x1+x2+x4 >= 0",
      "unrelated": "label 1 iff x8+x9+x10+x11 >= 0"
    },
    "motif": "The frozen 320-byte serialized learned state of source cells 0 through 4 after 256 source-development updates.",
    "lesion_patterns": {
      "breadth15_control": [0,1,2,3,4,5,6,7,8,9,10,12,13,14,15],
      "breadth16_total": [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
    },
    "lesion_rule": "At each cycle start, zero every listed cell and its permitted incident edge state, then apply the arm payload once only to receiver cells 0 through 4. The total-lesion pattern adds cell 11 to the exact breadth15_survivor11 pattern from experiment 022, leaving no pre-lesion cell state intact.",
    "cycles": [1,2,3,4],
    "updates_per_cycle": 128,
    "evaluations_per_cycle": [0,16,32,48,64,80,96,112,128],
    "samples": "4096 train, 1024 validation, and 2048 test observations per task from disjoint counter ranges; deterministic float64 SplitMix64/Box-Muller generation.",
    "numeric_mode": "IEEE-754 float64, deterministic single-process CPU, no accelerator"
  },
  "seeds": [53047,54049,55051,56053,57059,58061,59063,60077],
  "seed_policy": "Seeds are disjoint from experiments 014 through 022. No seed replacement, exclusion, or extension is permitted.",
  "budgets": {
    "timeout_seconds": 1800,
    "active_parameter_count": 128,
    "payload_bytes": 320,
    "resident_byte_count": 1344,
    "trial_count": 512,
    "matched_block_count": 128,
    "resource_record_count": 512,
    "maximum_development_updates_per_trial": 128,
    "fixed_resources": "Both lesion patterns and all arms use identical topology, masks, payload-container bytes, resident state, updates, evaluation schedule, example order, and accounting fields. Zeroing the final surviving cell allocates no capacity; no capacity growth is allowed."
  },
  "controls": [
    "Every four-arm comparison forks from one byte-identical post-lesion checkpoint.",
    "The breadth-fifteen control is the exact breadth15_survivor11 lesion from experiment 022 and is an internal replication control.",
    "The total lesion differs from the control only by zeroing its sole surviving nonreceiver cell 11.",
    "Shuffled and erased controls preserve payload shape, byte count, read operations, topology, masks, lesion schedule, and cycle schedule.",
    "Related and unrelated strata use equal sample counts and frozen task definitions.",
    "All valid supported, mixed, null, and negative outcomes are retained without tuning."
  ],
  "metrics_and_thresholds": [
    {"name":"completed_matched_block_count","comparator":"==","threshold":128},
    {"name":"completed_trial_count","comparator":"==","threshold":512},
    {"name":"valid_seed_count","comparator":"==","threshold":8},
    {"name":"resource_accounting_completeness_fraction","comparator":"==","threshold":1.0},
    {"name":"maximum_absolute_active_parameter_count_difference_across_arms_and_patterns","comparator":"==","threshold":0.0},
    {"name":"maximum_absolute_resident_byte_count_difference_across_arms_and_patterns","comparator":"==","threshold":0.0},
    {"name":"median_breadth16_cycle4_related_specific_control_corrected_cost_reduction","comparator":">=","threshold":0.06},
    {"name":"median_breadth15_minus_breadth16_cycle4_specificity_attenuation","comparator":"<=","threshold":0.03},
    {"name":"breadth16_cycle4_supporting_seed_fraction","comparator":">=","threshold":0.75},
    {"name":"maximum_absolute_median_unrelated_intact_cost_reduction_across_patterns_and_cycles","comparator":"<=","threshold":0.03}
  ],
  "metric_definitions": {
    "adaptation_cost": "Arithmetic mean validation cross-entropy over the nine fixed evaluations within a pattern-cycle block; lower is better.",
    "normalized_reduction": "R_arm=(C_cold-C_arm)/C_cold within a seed, pattern, relationship, and cycle block.",
    "specificity": "D_s,p,c=(R_intact,related-max(R_shuffled,related,R_erased,related))-(R_intact,unrelated-max(R_shuffled,unrelated,R_erased,unrelated)).",
    "breadth16_support": "A seed supports total-lesion regeneration iff D_s,total,4 >= 0.06 and D_s,control,4-D_s,total,4 <= 0.03.",
    "attenuation": "For each seed subtract total-lesion cycle-four specificity from breadth-fifteen-control cycle-four specificity, then take the median across seeds.",
    "collateral": "For every pattern and cycle, take the median across seeds of R_intact,unrelated; report the maximum absolute value.",
    "aggregation": "Medians over all eight seeds; no imputation, winsorization, alternate aggregation, incomplete-block use, or post-result subgrouping."
  },
  "validity_criteria": [
    "The branch, exact parent SHA, North Star hash, and prior sealed evidence identity match this preregistration.",
    "All eight seeds, 128 matched blocks, 512 trials, and 512 complete finite resource records are present.",
    "Every matched block verifies byte-identical pre-arm state plus exact active-parameter and resident-byte parity.",
    "The control has cardinality fifteen and leaves only cell 11 intact; the total lesion has cardinality sixteen, contains the control, and leaves no cell intact.",
    "The breadth-fifteen control reproduces a cycle-four specificity median of at least 0.07; failure is a valid scientific internal-replication failure.",
    "The source emits yggdrasil.research-scientific-result.v1 with this exact experiment identifier and a metrics object.",
    "Two duplicate executions from identical inputs must be byte-identical before qualification."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all ten metric thresholds pass.",
    "mixed": "Construction, accounting, determinism, and completeness pass and at least one but not all four scientific thresholds passes, including an internal-replication failure with another scientific threshold passing.",
    "null": "Validity passes, total-lesion cycle-four specificity has absolute median below 0.03, collateral passes, and no benefit threshold passes.",
    "negative": "Validity passes but the outcome is neither supported, mixed, nor null, including material attenuation, collateral degradation, or breadth-fifteen internal-replication failure.",
    "invalid": "Any provenance, authority, determinism, cardinality, finiteness, matched-fork, lesion-construction, or resource-parity criterion fails; invalid is not scientific evidence."
  },
  "stop_conditions": [
    "Stop before execution if provenance, authority boundary, manifest identity, source identity, or preregistration identity differs from the sealed package.",
    "Stop and emit an invalid result if deterministic construction, matched forking, lesion construction, finiteness, resource parity, or required accounting fails.",
    "Stop at 1800 seconds or after all 512 trials finish, whichever occurs first; preserve incomplete records without replacing seeds or reducing dimensions.",
    "Do not stop early for benefit, futility, significance, internal-replication failure, null, mixed, or negative observations."
  ],
  "no_post_result_tuning_rule": "After any primary or diagnostic output is observed, do not change seeds, arms, tasks, motif, lesion patterns, cycles, budgets, capacities, controls, formulas, aggregation, thresholds, classification, or stop conditions under this experiment identifier. Duplicate runs must use byte-identical source and arguments."
}
