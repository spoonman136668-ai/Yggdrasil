{
  "experiment_id": "EXP-DG1B-REPEATED-REGENERATION-DURABILITY-017",
  "question": "Does the supported early critical-window motif transfer remain functionally useful through four repeated synthetic lesion/regeneration cycles without collateral degradation or additional resident capacity?",
  "hypothesis": "A fixed compact informative motif applied at the frozen early checkpoint will preserve related-task recovery through cycle four, while byte-matched shuffled, erased, and cold controls will not reproduce the effect and unrelated-task performance will remain stable.",
  "exact_parent_sha": "95fbbb8ed5a9d935031c1c1e372d828eccae8a17",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "3cd3b3d2fdbbb5b3541d433a527231b38fc441699cd0353fa86f0c3be6f0a905",
  "prior_evidence": {
    "experiment": "EXP-DG1B-CRITICAL-INTEGRATION-WINDOW-016",
    "result_class": "supported",
    "result_sha256": "14f62914dcbfadfb770b39e048a9f277284d054645d6d4cc59588798bb4a0ac4"
  },
  "authority": "synthetic computational research only; no wetware, production, broker, live, CKB-plane, or authority-system integration",
  "changed_paths": [
    "research/experiments/exp-dg1b-repeated-regeneration-durability-017.ice",
    "research/applications/plane/exp-dg1b-repeated-regeneration-durability-017.py",
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json"
  ],
  "arms": [
    "intact: apply the fixed informative source motif after every lesion",
    "shuffled: apply a deterministic within-payload permutation after every lesion",
    "erased: apply an all-zero byte-matched payload after every lesion",
    "cold: regenerate after every lesion with the same zero payload container and no motif information"
  ],
  "inputs_and_model": {
    "model": "The frozen experiment-016 synthetic 16-cell ring, neighborhood radius 1, hidden width 8, fixed mean readout, and four local message steps per example.",
    "source_task": "binary label 1 iff x0+x1+x2+x3 >= 0",
    "related_task": "binary label 1 iff x0+x1+x2+x4 >= 0",
    "unrelated_task": "binary label 1 iff x8+x9+x10+x11 >= 0",
    "motif": "The serialized learned state of source cells 0 through 4 after 256 source-development updates, including the same permitted incident edge state and lineage counters as experiment 016.",
    "lesion": "At the start of each cycle, deterministically zero receiver cells 0 through 4 and their permitted incident edge state before applying the arm payload once.",
    "cycles": [1, 2, 3, 4],
    "updates_per_cycle": 128,
    "evaluations_per_cycle": [0, 16, 32, 48, 64, 80, 96, 112, 128],
    "samples": "4096 train, 1024 validation, and 2048 test observations per task from disjoint counter ranges; deterministic float64 SplitMix64/Box-Muller generation.",
    "numeric_mode": "IEEE-754 float64, deterministic single-process CPU, no accelerator"
  },
  "seeds": [1009, 2027, 3037, 4051, 5059, 6073, 7079, 8089],
  "seed_policy": "Seeds are disjoint from experiments 014, 015, and 016. No seed replacement or exclusion is permitted.",
  "budgets": {
    "timeout_seconds": 1500,
    "active_parameter_count": 128,
    "payload_bytes": 320,
    "resident_byte_count": 1344,
    "trial_count": 256,
    "matched_block_count": 64,
    "resource_record_count": 256,
    "maximum_development_updates_per_trial": 128,
    "fixed_resources": "All arms have identical topology, trainable masks, payload-container bytes, resident state, update count, evaluation schedule, example order, and resource-accounting fields. No capacity growth is allowed."
  },
  "controls": [
    "Each four-arm block forks from one byte-identical post-lesion checkpoint.",
    "Shuffled and erased arms preserve payload shape, byte count, read operations, topology, masks, and cycle schedule.",
    "Related and unrelated strata use equal sample counts and frozen task definitions.",
    "Cycle one reproduces the early-transfer condition; cycle four is the frozen durability endpoint.",
    "All completed positive, mixed, null, and negative outcomes are retained without tuning."
  ],
  "metrics_and_thresholds": [
    {"name": "completed_matched_block_count", "comparator": "==", "threshold": 64},
    {"name": "completed_trial_count", "comparator": "==", "threshold": 256},
    {"name": "valid_seed_count", "comparator": "==", "threshold": 8},
    {"name": "resource_accounting_completeness_fraction", "comparator": "==", "threshold": 1.0},
    {"name": "maximum_absolute_active_parameter_count_difference_across_arms", "comparator": "==", "threshold": 0.0},
    {"name": "maximum_absolute_resident_byte_count_difference_across_arms", "comparator": "==", "threshold": 0.0},
    {"name": "median_cycle4_related_specific_control_corrected_cost_reduction", "comparator": ">=", "threshold": 0.10},
    {"name": "median_cycle1_minus_cycle4_specificity_decay", "comparator": "<=", "threshold": 0.03},
    {"name": "cycle4_supporting_seed_fraction", "comparator": ">=", "threshold": 0.75},
    {"name": "maximum_absolute_median_unrelated_intact_cost_reduction_across_cycles", "comparator": "<=", "threshold": 0.03}
  ],
  "metric_definitions": {
    "adaptation_cost": "Arithmetic mean validation cross-entropy over the nine fixed evaluations within a cycle; lower is better.",
    "normalized_reduction": "R_arm=(C_cold-C_arm)/C_cold within a seed, relationship, and cycle block.",
    "specificity": "D_s,c=(R_intact,related-max(R_shuffled,related,R_erased,related))-(R_intact,unrelated-max(R_shuffled,unrelated,R_erased,unrelated)).",
    "cycle4_support": "A seed supports durability iff D_s,4 >= 0.10 and D_s,1-D_s,4 <= 0.03.",
    "collateral": "For each cycle, median across seeds of R_intact,unrelated; report the maximum absolute value.",
    "aggregation": "Medians over all eight seeds; no imputation, winsorization, alternate aggregation, or incomplete-block use."
  },
  "validity_criteria": [
    "The branch, exact parent SHA, North Star hash, and prior sealed evidence identity match this preregistration.",
    "All eight seeds, 64 matched blocks, 256 trials, and 256 complete resource records are present and finite.",
    "Every matched block verifies byte-identical pre-arm state plus exact active-parameter and resident-byte parity.",
    "The source emits yggdrasil.research-scientific-result.v1 with this exact experiment identifier and a metrics object.",
    "Two duplicate executions from identical inputs must be byte-identical before qualification."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all ten metric thresholds pass.",
    "mixed": "All validity criteria pass and at least one, but not all, of the four scientific thresholds passes.",
    "null": "All validity criteria pass, cycle-four specificity has absolute median below 0.03, collateral passes, and no scientific benefit threshold passes.",
    "negative": "All validity criteria pass but the outcome is neither supported, mixed, nor null; this includes material specificity decay or collateral degradation.",
    "invalid": "Any validity, determinism, cardinality, finiteness, provenance, or resource-parity criterion fails. Invalid is not a scientific outcome."
  },
  "stop_conditions": [
    "Stop before execution if provenance, authority boundary, manifest identity, source identity, or preregistration identity differs from the sealed package.",
    "Stop and emit an invalid result if deterministic construction, matched forking, finiteness, resource parity, or required accounting fails.",
    "Stop at 1500 seconds or after all 256 trials finish, whichever occurs first; preserve incomplete records without replacing seeds or reducing dimensions.",
    "Do not stop early for benefit, futility, significance, null, mixed, or negative observations."
  ],
  "no_post_result_tuning_rule": "After any primary result is observed, do not change seeds, arms, task definitions, lesion definition, cycles, budgets, capacities, controls, formulas, aggregation, thresholds, classification, or stop conditions under this experiment identifier. Duplicate runs must use byte-identical source and arguments."
}
