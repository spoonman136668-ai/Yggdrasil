{
  "experiment_id": "EXP-DG1B-MOTIF-COMPRESSION-DURABILITY-028",
  "question": "After supported four-cycle regeneration through a total sixteen-cell synthetic lesion with a 192-byte informative motif, does reducing informative restored motif state to two cells (128 informative bytes) preserve related-task regeneration when the physical transfer container remains fixed at 320 bytes?",
  "hypothesis": "On new disjoint seeds, compressed192 will internally replicate its prior cycle-four specificity and compressed128 will retain at least 0.04 cycle-four control-corrected related-task specificity with no more than 0.015 median attenuation from compressed192, at least 0.75 supporting-seed fraction, and no material unrelated-task effect; shuffled, erased, and cold controls will not reproduce the benefit.",
  "exact_parent_sha": "77507c277d7ed84afb054fcf5e721f53dc2beaf7",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DG1B-MOTIF-COMPRESSION-DURABILITY-026",
    "classification": "supported",
    "result_sha256": "2f244c524f4eb1fe7928963f73d368d8b7b1a4824b886a59e5d8724d347c21da",
    "scientific_claim": "192 informative bytes preserved the preregistered four-cycle total-lesion regeneration criteria with a fixed 320-byte physical transfer container."
  },
  "authority": "synthetic computational research only; no wetware, living tissue, production, broker, live, accepted-ref, credential, runner-configuration, scheduler, queue-consumer, or authority-system integration",
  "changed_paths": [
    "research/experiments/exp-dg1b-motif-compression-durability-028.ice",
    "research/applications/plane/exp-dg1b-motif-compression-durability-028.py",
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json"
  ],
  "conditions": [
    "compressed192: restore the first 24 float64 motif values for receiver cells 0 through 2; remaining sixteen values are zero padding",
    "compressed128: restore the first 16 float64 motif values for receiver cells 0 through 1; remaining twenty-four values are zero padding"
  ],
  "arms": [
    "intact: apply the condition-specific informative motif after every total lesion",
    "shuffled: deterministically permute only the condition's informative values and preserve zero padding",
    "erased: transfer an all-zero 320-byte container",
    "cold: regenerate with the same all-zero 320-byte container and no motif information"
  ],
  "inputs_and_model": {
    "model": "Frozen experiment-026 synthetic 16-cell ring, neighborhood radius 1, hidden width 8, fixed mean readout, and four local message steps per example.",
    "tasks": {
      "source": "label 1 iff x0+x1+x2+x3 >= 0",
      "related": "label 1 iff x0+x1+x2+x4 >= 0",
      "unrelated": "label 1 iff x8+x9+x10+x11 >= 0"
    },
    "source_motif": "Frozen learned-state construction from the 026 lineage after 256 source-development updates; 40 float64 values total.",
    "lesion": "At each cycle start zero all sixteen cells and permitted incident edge state, then apply exactly one condition/arm payload.",
    "informative_value_counts": {
      "compressed192": 24,
      "compressed128": 16
    },
    "informative_byte_counts": {
      "compressed192": 192,
      "compressed128": 128
    },
    "transfer_container_bytes": 320,
    "cycles": [
      1,
      2,
      3,
      4
    ],
    "updates_per_cycle": 128,
    "evaluations_per_cycle": [
      0,
      16,
      32,
      48,
      64,
      80,
      96,
      112,
      128
    ],
    "samples": "4096 train, 1024 validation, and 2048 test observations per task from disjoint counter ranges; deterministic float64 SplitMix64/Box-Muller generation.",
    "numeric_mode": "IEEE-754 float64, deterministic single-process CPU, no accelerator"
  },
  "seeds": [
    77213,
    78229,
    79231,
    80233,
    81239,
    82249,
    83257,
    84263
  ],
  "seed_policy": "Eight new seeds are frozen before implementation and are disjoint from experiments 025 and 026. No seed replacement, exclusion, or extension is permitted.",
  "budgets": {
    "timeout_seconds": 1800,
    "active_parameter_count": 128,
    "transfer_container_bytes": 320,
    "resident_byte_count": 1344,
    "trial_count": 512,
    "matched_block_count": 128,
    "resource_record_count": 512,
    "maximum_development_updates_per_trial": 128,
    "fixed_resources": "Both conditions and all arms use identical topology, masks, physical transfer-container bytes, resident state, updates, evaluation schedule, example order, lesion breadth, and accounting. Compression changes only informative motif cardinality."
  },
  "controls": [
    "Every four-arm comparison forks from one byte-identical total-lesion checkpoint.",
    "compressed192 is an internal replication on new seeds; compressed128 is the only new informative-state dose.",
    "Both conditions use the same 320-byte physical transfer container; zero padding carries no informative state.",
    "The shuffled arm permutes only informative values within its condition; zero padding remains zero.",
    "Erased and cold preserve container bytes, topology, masks, cycle schedule, and accounting.",
    "Related and unrelated strata use equal sample counts and frozen task definitions.",
    "All valid supported, mixed, null, and negative outcomes are retained without tuning."
  ],
  "metrics_and_thresholds": [
    {
      "name": "completed_matched_block_count",
      "comparator": "==",
      "threshold": 128
    },
    {
      "name": "completed_trial_count",
      "comparator": "==",
      "threshold": 512
    },
    {
      "name": "valid_seed_count",
      "comparator": "==",
      "threshold": 8
    },
    {
      "name": "resource_accounting_completeness_fraction",
      "comparator": "==",
      "threshold": 1
    },
    {
      "name": "maximum_absolute_active_parameter_count_difference_across_arms_and_conditions",
      "comparator": "==",
      "threshold": 0
    },
    {
      "name": "maximum_absolute_resident_byte_count_difference_across_arms_and_conditions",
      "comparator": "==",
      "threshold": 0
    },
    {
      "name": "maximum_absolute_transfer_container_byte_count_difference_across_arms_and_conditions",
      "comparator": "==",
      "threshold": 0
    },
    {
      "name": "median_compressed192_cycle4_related_specific_control_corrected_cost_reduction",
      "comparator": ">=",
      "threshold": 0.045
    },
    {
      "name": "median_compressed128_cycle4_related_specific_control_corrected_cost_reduction",
      "comparator": ">=",
      "threshold": 0.04
    },
    {
      "name": "median_compressed192_minus_compressed128_cycle4_specificity_attenuation",
      "comparator": "<=",
      "threshold": 0.015
    },
    {
      "name": "compressed128_cycle4_supporting_seed_fraction",
      "comparator": ">=",
      "threshold": 0.75
    },
    {
      "name": "maximum_absolute_median_unrelated_intact_cost_reduction_across_conditions_and_cycles",
      "comparator": "<=",
      "threshold": 0.03
    }
  ],
  "metric_definitions": {
    "adaptation_cost": "Arithmetic mean validation cross-entropy over the nine fixed evaluations within a condition-cycle block; lower is better.",
    "normalized_reduction": "R_arm=(C_cold-C_arm)/C_cold within a seed, condition, relationship, and cycle block.",
    "specificity": "D_s,k,c=(R_intact,related-max(R_shuffled,related,R_erased,related))-(R_intact,unrelated-max(R_shuffled,unrelated,R_erased,unrelated)).",
    "compressed128_support": "A seed supports 128-byte compression iff D_s,compressed128,4 >= 0.04 and D_s,compressed192,4-D_s,compressed128,4 <= 0.015.",
    "attenuation": "For each seed subtract compressed128 cycle-four specificity from compressed192 cycle-four specificity, then take the median across all eight seeds.",
    "collateral": "For every condition and cycle take the median across seeds of R_intact,unrelated; report the maximum absolute value.",
    "aggregation": "Medians over all eight seeds; no imputation, winsorization, alternate aggregation, incomplete-block use, or post-result subgrouping."
  },
  "validity_criteria": [
    "The branch, exact parent SHA, updated North Star hash, and prior sealed evidence identity match this preregistration.",
    "All eight seeds, 128 matched blocks, 512 trials, and 512 finite resource records are present.",
    "Every matched block verifies identical pre-arm state plus exact active-parameter, resident-byte, and transfer-container-byte parity.",
    "compressed192 carries exactly 24 informative float64 values plus sixteen zeros; compressed128 carries exactly 16 informative values plus twenty-four zeros; both physical containers contain exactly 40 float64 values.",
    "All conditions use total sixteen-cell lesion and no pre-lesion cell state survives.",
    "The compressed192 internal replication meets its frozen cycle-four specificity floor; failure is a valid scientific internal-replication failure.",
    "The source emits yggdrasil.research-scientific-result.v1 with this exact experiment identifier and a metrics object.",
    "Two duplicate executions from identical inputs must be byte-identical before qualification."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all twelve metric thresholds pass.",
    "mixed": "Construction, accounting, determinism, completeness, and compressed192 internal replication pass and at least one but not all compressed128 scientific thresholds pass.",
    "null": "Validity passes, compressed128 cycle-four specificity has absolute median below 0.03, collateral passes, and no 128-byte benefit threshold passes.",
    "negative": "Validity passes but the outcome is neither supported, mixed, nor null, including material compression attenuation, low supporting-seed fraction, collateral degradation, or internal-replication failure.",
    "incomplete": "An environmental or compute stop prevents full cardinality; preserve diagnostics and make no scientific claim.",
    "invalid": "Any provenance, authority, determinism, construction, cardinality, finiteness, matched-fork, or resource-parity criterion fails; invalid is not scientific evidence."
  },
  "stop_conditions": [
    "Stop before execution if provenance, authority boundary, source identity, updated North Star identity, or preregistration identity differs from the sealed package.",
    "Stop and classify invalid if deterministic construction, matched forking, total-lesion construction, informative-value cardinality, finiteness, resource parity, or required accounting fails.",
    "Stop at 1800 seconds or after all 512 trials finish, whichever occurs first; preserve incomplete records without replacing seeds or reducing dimensions.",
    "Do not stop early for benefit, futility, internal-replication failure, null, mixed, or negative observations."
  ],
  "no_post_result_tuning_rule": "After any primary or diagnostic output is observed, do not change seeds, conditions, arms, tasks, motif construction, lesion definition, cycles, budgets, capacities, controls, formulas, aggregation, thresholds, classification, or stop conditions under this experiment identifier. Duplicate runs must use byte-identical source and arguments.",
  "supersedes_invalid_attempt": {
    "experiment": "EXP-DG1B-MOTIF-COMPRESSION-DURABILITY-027",
    "disposition": "invalid-infrastructure",
    "scientific_claim": false,
    "primary_probe_executed": false
  }
}
