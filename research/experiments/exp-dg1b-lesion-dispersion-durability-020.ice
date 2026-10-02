{
  "experiment_id": "EXP-DG1B-LESION-DISPERSION-DURABILITY-020",
  "question": "At the supported fixed nine-cell lesion breadth, does four-cycle related-task regeneration remain specific when the four collateral lesions are noncontiguous rather than contiguous around the five motif-receiver cells?",
  "hypothesis": "The fixed early informative motif will retain at least 0.08 cycle-four control-corrected related-task specificity for both frozen noncontiguous collateral patterns, with no more than 0.03 attenuation from the centered contiguous control and no material unrelated-task effect, while shuffled, erased, and cold controls will not reproduce the benefit.",
  "exact_parent_sha": "73d1f948a4086cbd398b83474fc892a05d712795",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "3cd3b3d2fdbbb5b3541d433a527231b38fc441699cd0353fa86f0c3be6f0a905",
  "prior_evidence": {"experiment": "EXP-DG1B-LESION-GEOMETRY-DURABILITY-019", "result_class": "supported", "result_sha256": "cced4de068eea0167f2620a55a46745abf23724e86c2575bb2a34b28ff925012"},
  "authority": "synthetic computational research only; no wetware, living tissue, production, broker, live, CKB-plane, credential, runner, or authority-system integration",
  "changed_paths": ["research/experiments/exp-dg1b-lesion-dispersion-durability-020.ice", "research/applications/plane/exp-dg1b-lesion-dispersion-durability-020.py", ".yggdrasil/qualification-request.json", ".yggdrasil/isolated-run.json"],
  "arms": [
    "intact: apply the frozen informative 320-byte motif to receiver cells 0 through 4 after every lesion",
    "shuffled: apply a deterministic within-payload permutation after every lesion",
    "erased: apply an all-zero byte-matched payload after every lesion",
    "cold: regenerate after every lesion with the same zero payload container and no motif information"
  ],
  "inputs_and_model": {
    "model": "The frozen experiment-019 synthetic 16-cell ring, neighborhood radius 1, hidden width 8, fixed mean readout, and four local message steps per example.",
    "tasks": {"source": "label 1 iff x0+x1+x2+x3 >= 0", "related": "label 1 iff x0+x1+x2+x4 >= 0", "unrelated": "label 1 iff x8+x9+x10+x11 >= 0"},
    "motif": "The frozen serialized learned state of source cells 0 through 4 after 256 source-development updates.",
    "lesion_breadth": 9,
    "lesion_patterns": {"centered_contiguous": [14,15,0,1,2,3,4,5,6], "near_dispersed": [14,0,1,2,3,4,5,7,9], "far_dispersed": [0,1,2,3,4,7,10,12,15]},
    "lesion_rule": "At each cycle start, zero the listed nine unique cells and permitted incident edge state, then apply the arm payload once only to receiver cells 0 through 4. Each pattern contains the same receiver set and exactly four frozen collateral cells.",
    "cycles": [1,2,3,4],
    "updates_per_cycle": 128,
    "evaluations_per_cycle": [0,16,32,48,64,80,96,112,128],
    "samples": "4096 train, 1024 validation, and 2048 test observations per task from disjoint counter ranges; deterministic float64 SplitMix64/Box-Muller generation.",
    "numeric_mode": "IEEE-754 float64, deterministic single-process CPU, no accelerator"
  },
  "seeds": [27059,28069,29077,30089,31091,32099,33107,34123],
  "seed_policy": "Seeds are disjoint from experiments 014 through 019; no replacement, exclusion, or extension.",
  "budgets": {"timeout_seconds": 1800, "active_parameter_count": 128, "payload_bytes": 320, "resident_byte_count": 1344, "trial_count": 768, "matched_block_count": 192, "resource_record_count": 768, "maximum_development_updates_per_trial": 128, "fixed_resources": "All arms and patterns use identical topology, masks, payload-container bytes, resident state, breadth, updates, evaluation schedule, example order, and accounting fields; no capacity growth."},
  "controls": [
    "Each four-arm block forks from one byte-identical post-lesion checkpoint for the same seed, pattern, cycle, and relationship.",
    "Shuffled and erased controls preserve payload shape, bytes, reads, topology, masks, lesion set, and schedule.",
    "All patterns contain receiver cells 0 through 4 plus exactly four collateral cells; only frozen collateral placement changes.",
    "The centered contiguous pattern exactly reproduces experiment 019's centered lesion as an internal replication control.",
    "Related and unrelated strata use equal sample counts and frozen task definitions; all scientific outcomes are retained without tuning."
  ],
  "metrics_and_thresholds": [
    {"name":"completed_matched_block_count","comparator":"==","threshold":192},
    {"name":"completed_trial_count","comparator":"==","threshold":768},
    {"name":"valid_seed_count","comparator":"==","threshold":8},
    {"name":"resource_accounting_completeness_fraction","comparator":"==","threshold":1.0},
    {"name":"maximum_absolute_active_parameter_count_difference_across_arms_and_patterns","comparator":"==","threshold":0.0},
    {"name":"maximum_absolute_resident_byte_count_difference_across_arms_and_patterns","comparator":"==","threshold":0.0},
    {"name":"minimum_median_dispersed_cycle4_related_specific_control_corrected_cost_reduction","comparator":">=","threshold":0.08},
    {"name":"median_contiguous_minus_worst_dispersed_cycle4_specificity_attenuation","comparator":"<=","threshold":0.03},
    {"name":"minimum_dispersed_cycle4_supporting_seed_fraction","comparator":">=","threshold":0.75},
    {"name":"maximum_absolute_median_unrelated_intact_cost_reduction_across_patterns_and_cycles","comparator":"<=","threshold":0.03}
  ],
  "metric_definitions": {
    "adaptation_cost": "Arithmetic mean validation cross-entropy over nine fixed evaluations within a pattern-cycle block; lower is better.",
    "normalized_reduction": "R_arm=(C_cold-C_arm)/C_cold within seed, pattern, relationship, and cycle.",
    "specificity": "D_s,p,c=(R_intact,related-max(R_shuffled,related,R_erased,related))-(R_intact,unrelated-max(R_shuffled,unrelated,R_erased,unrelated)).",
    "support": "A seed supports a dispersed pattern iff D_s,p,4 >= 0.08 and D_s,centered_contiguous,4-D_s,p,4 <= 0.03; report the smaller fraction.",
    "attenuation": "For each seed, D_s,centered_contiguous,4 minus min(D_s,near_dispersed,4,D_s,far_dispersed,4); report the median.",
    "collateral": "For each pattern and cycle, median across seeds of R_intact,unrelated; report the maximum absolute value.",
    "aggregation": "Medians over all eight seeds; no imputation, winsorization, pooling, incomplete blocks, or post-result subgrouping."
  },
  "validity_criteria": [
    "Branch, exact parent SHA, North Star hash, and prior sealed evidence identity match this preregistration.",
    "All eight seeds, 192 matched blocks, 768 trials, and 768 complete finite resource records are present.",
    "Every block verifies byte-identical pre-arm state and exact active-parameter/resident-byte parity; every lesion has nine unique cells and receiver cells 0 through 4.",
    "The contiguous internal replication has median cycle-four specificity at least 0.08; failure is valid negative evidence.",
    "The source emits yggdrasil.research-scientific-result.v1 with this experiment and a metrics object.",
    "Two executions from identical inputs and arguments are byte-identical before qualification."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all ten thresholds pass.",
    "mixed": "Construction/accounting/determinism/completeness pass and at least one but not all four scientific thresholds pass.",
    "null": "Validity passes, both dispersed cycle-four specificity medians have absolute value below 0.03, collateral passes, and no benefit threshold passes.",
    "negative": "Validity passes but the outcome is neither supported, mixed, nor null, including material dispersion attenuation, collateral degradation, or internal-replication failure.",
    "invalid": "Any provenance, authority, determinism, cardinality, finiteness, matched-fork, lesion-construction, or resource-parity criterion fails; invalid is not scientific evidence."
  },
  "stop_conditions": [
    "Stop before execution if provenance, authority boundary, request, source, or preregistration identity differs from the sealed package.",
    "Stop and emit invalid if deterministic construction, fixed-breadth lesion construction, matched forking, finiteness, parity, or accounting fails.",
    "Stop at 1800 seconds or after all 768 trials finish; preserve incomplete records without replacing seeds or reducing dimensions.",
    "Do not stop early for benefit, futility, significance, internal-replication failure, null, mixed, or negative observations."
  ],
  "no_post_result_tuning_rule": "After any primary or diagnostic output is observed, do not change seeds, arms, tasks, lesion patterns, cycles, budgets, capacities, controls, formulas, aggregation, thresholds, classification, or stop conditions under this identifier. Duplicate runs use byte-identical source and arguments."
}
