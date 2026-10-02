{
  "experiment_id": "EXP-DG1B-MOTIF-COMPRESSION-DURABILITY-025",
  "question": "After supported four-cycle regeneration through a total sixteen-cell synthetic lesion, does reducing informative restored motif state from five cells (320 informative bytes) to four cells (256 informative bytes) preserve related-task regeneration when the physical transfer container remains byte-matched at 320 bytes?",
  "hypothesis": "The frozen four-cell informative motif will preserve at least 0.05 cycle-four control-corrected related-task specificity after total lesion, with no more than 0.02 median attenuation from the full five-cell motif, at least 0.75 supporting-seed fraction, and no material unrelated-task effect, while shuffled, erased, and cold controls will not reproduce the benefit.",
  "exact_parent_sha": "db3a1750a71c18f0d26f02bec4c4edb099423be2",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "3cd3b3d2fdbbb5b3541d433a527231b38fc441699cd0353fa86f0c3be6f0a905",
  "prior_evidence": {
    "experiment": "EXP-DG1B-TOTAL-LESION-DURABILITY-023",
    "result_class": "supported",
    "result_sha256": "ca32b6c78baeaa01f6fb07cb35f4dc1efc30244be7318b176d3a232420ba5f2a"
  },
  "supersedes_invalid_attempt": {
    "experiment": "EXP-DG1B-MOTIF-COMPRESSION-DURABILITY-024",
    "disposition": "invalid-infrastructure",
    "scientific_claim": false
  },
  "authority": "synthetic computational research only; no wetware, living tissue, production, broker, live, CKB-plane execution, credential, runner-configuration, or authority-system integration",
  "changed_paths": [
    "research/experiments/exp-dg1b-motif-compression-durability-025.ice",
    "research/applications/plane/exp-dg1b-motif-compression-durability-025.py",
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json"
  ],
  "conditions": [
    "full320: restore all 40 float64 motif values for receiver cells 0 through 4",
    "compressed256: restore only the first 32 float64 motif values for receiver cells 0 through 3; cell 4 receives eight zero float64 padding values so the physical container remains 320 bytes"
  ],
  "arms": [
    "intact: apply the condition-specific informative motif after every total lesion",
    "shuffled: deterministically permute only the condition's informative values and preserve zero padding",
    "erased: transfer an all-zero 320-byte container",
    "cold: regenerate with the same all-zero 320-byte container and no motif information"
  ],
  "inputs_and_model": {
    "model": "The frozen experiment-023 synthetic 16-cell ring, neighborhood radius 1, hidden width 8, fixed mean readout, and four local message steps per example.",
    "tasks": {
      "source": "label 1 iff x0+x1+x2+x3 >= 0",
      "related": "label 1 iff x0+x1+x2+x4 >= 0",
      "unrelated": "label 1 iff x8+x9+x10+x11 >= 0"
    },
    "source_motif": "The frozen learned state representation of source cells 0 through 4 after 256 source-development updates; 40 float64 values total.",
    "lesion": "At each cycle start zero all sixteen cells and permitted incident edge state, then apply exactly one condition/arm payload.",
    "informative_value_counts": {
      "full320": 40,
      "compressed256": 32
    },
    "informative_byte_counts": {
      "full320": 320,
      "compressed256": 256
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
    61091,
    62119,
    63127,
    64151,
    65167,
    66179,
    67189,
    68209
  ],
  "seed_policy": "All eight seeds were checked against the repository before preregistration and had no matches; no seed replacement, exclusion, or extension is permitted.",
  "budgets": {
    "timeout_seconds": 1800,
    "active_parameter_count": 128,
    "transfer_container_bytes": 320,
    "resident_byte_count": 1344,
    "trial_count": 512,
    "matched_block_count": 128,
    "resource_record_count": 512,
    "maximum_development_updates_per_trial": 128,
    "fixed_resources": "Both conditions and all arms use identical topology, masks, physical transfer-container bytes, resident state, updates, evaluation schedule, example order, lesion breadth, and accounting fields. Compression changes informative motif values only; it adds no capacity."
  },
  "controls": [
    "Every four-arm comparison forks from one byte-identical total-lesion checkpoint.",
    "full320 is an internal replication of the experiment-023 full five-cell motif condition under new disjoint seeds.",
    "compressed256 differs from full320 only by replacing the eight cell-4 motif values with zeros while retaining the same 320-byte physical container.",
    "The shuffled arm permutes only informative values within its condition; zero padding remains zero.",
    "Erased and cold arms preserve container bytes, topology, masks, cycle schedule, and accounting.",
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
      "name": "median_full320_cycle4_related_specific_control_corrected_cost_reduction",
      "comparator": ">=",
      "threshold": 0.06
    },
    {
      "name": "median_compressed256_cycle4_related_specific_control_corrected_cost_reduction",
      "comparator": ">=",
      "threshold": 0.05
    },
    {
      "name": "median_full320_minus_compressed256_cycle4_specificity_attenuation",
      "comparator": "<=",
      "threshold": 0.02
    },
    {
      "name": "compressed256_cycle4_supporting_seed_fraction",
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
    "compressed_support": "A seed supports compression iff D_s,compressed256,4 >= 0.05 and D_s,full320,4-D_s,compressed256,4 <= 0.02.",
    "attenuation": "For each seed subtract compressed256 cycle-four specificity from full320 cycle-four specificity, then take the median across all eight seeds.",
    "collateral": "For every condition and cycle take the median across seeds of R_intact,unrelated; report the maximum absolute value.",
    "aggregation": "Medians over all eight seeds; no imputation, winsorization, alternate aggregation, incomplete-block use, or post-result subgrouping."
  },
  "validity_criteria": [
    "The branch, exact parent SHA, North Star hash, and prior sealed evidence identity match this preregistration.",
    "All eight seeds, 128 matched blocks, 512 trials, and 512 finite resource records are present.",
    "Every matched block verifies identical pre-arm state plus exact active-parameter, resident-byte, and transfer-container-byte parity.",
    "full320 carries exactly 40 informative float64 values; compressed256 carries exactly 32 informative values followed by eight zeros; both physical containers contain exactly 40 float64 values.",
    "All conditions use total sixteen-cell lesion and no pre-lesion cell state survives.",
    "The full320 internal replication has cycle-four specificity median at least 0.06; failure is a valid scientific internal-replication failure.",
    "The source emits yggdrasil.research-scientific-result.v1 with this exact experiment identifier and a metrics object.",
    "Two duplicate executions from identical inputs must be byte-identical before qualification."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all twelve metric thresholds pass.",
    "mixed": "Construction, accounting, determinism, completeness, and internal replication pass and at least one but not all compression scientific thresholds pass.",
    "null": "Validity passes, compressed256 cycle-four specificity has absolute median below 0.03, collateral passes, and no compression benefit threshold passes.",
    "negative": "Validity passes but the outcome is neither supported, mixed, nor null, including material compression attenuation, low supporting-seed fraction, collateral degradation, or internal-replication failure.",
    "incomplete": "An environmental or compute stop prevents full cardinality; preserve diagnostics and make no scientific claim.",
    "invalid": "Any provenance, authority, determinism, construction, cardinality, finiteness, matched-fork, or resource-parity criterion fails; invalid is not scientific evidence."
  },
  "stop_conditions": [
    "Stop before execution if provenance, authority boundary, manifest identity, source identity, North Star identity, or preregistration identity differs from the sealed package.",
    "Stop and classify invalid if deterministic construction, matched forking, total-lesion construction, informative-value cardinality, finiteness, resource parity, or required accounting fails.",
    "Stop at 1800 seconds or after all 512 trials finish, whichever occurs first; preserve incomplete records without replacing seeds or reducing dimensions.",
    "Do not stop early for benefit, futility, significance, internal-replication failure, null, mixed, or negative observations."
  ],
  "no_post_result_tuning_rule": "After any primary or diagnostic output is observed, do not change seeds, conditions, arms, tasks, motif construction, lesion definition, cycles, budgets, capacities, controls, formulas, aggregation, thresholds, classification, or stop conditions under this experiment identifier. Duplicate runs must use byte-identical source and arguments."
}
