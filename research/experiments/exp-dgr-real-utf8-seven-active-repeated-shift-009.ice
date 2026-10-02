{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-SEVEN-ACTIVE-REPEATED-SHIFT-009",
  "program": "DG1 real-byte adaptive granularity",
  "question": "At the qualified seven-active capacity floor, can one fixed sixteen-motif phenotype sustain the frozen A,B,C,C,B,A demand-shift sequence and exact revisits without retraining, learned-state mutation, or benefit collapse?",
  "hypothesis": "Using the qualified seven-active floor and the unchanged first-half error-guided selector, all six cycles will preserve exactly seven active plus nine retained motifs, perform at least one wake and eviction on each cross-file transition, reproduce identical active sets on revisits, retain at least 70% of full-model incremental correct predictions, remain no worse than a seven-motif static control, and preserve positive covered-position accuracy gain with exact state integrity.",
  "exact_parent_sha": "685d7d2a48b18cae6e6c6d9052fd604f8b2a1237",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-SEVEN-ACTIVE-BOUNDARY-008",
    "classification": "supported",
    "qualification_run_id": "37037672525",
    "observation": "Seven active motifs retained at least 0.80 of full benefit across all three demand files, versus 0.60 at six; the frozen 70% useful-capacity floor is seven."
  },
  "authority": "synthetic research-only evaluation on immutable repo-owned bytes; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, retraining, production, broker, live-interface, or authority changes",
  "changed_paths": [
    "research/experiments/exp-dgr-real-utf8-seven-active-repeated-shift-009.ice",
    "research/applications/plane/exp-dgr-real-utf8-seven-active-repeated-shift-009.py",
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json"
  ],
  "inputs": {
    "training": [
      [
        "research/architecture/measurement-framework.ice",
        "6374fc3c39ee821c8f9d565bb7de0875c07d5cdc",
        10040
      ],
      [
        "research/architecture/structural-plasticity.ice",
        "d2d75b4ed60e0c112de5202ba31848b15081e0cb",
        9550
      ],
      [
        "research/architecture/developmental-substrate-v0.2.ice",
        "52d6e87e2339bdf586c33da22470e38a9ca27785",
        8448
      ],
      [
        "research/architecture/yggdrasil-north-star.ice",
        "84358ec54c0e7eba6b6f830e0b4d2755920281cb",
        8411
      ]
    ],
    "fresh_demand_files": {
      "A": [
        "research/architecture/developmental-substrate-v0.1.ice",
        "cea1d9966056f097838eb350a42795219f046fc3",
        8054
      ],
      "B": [
        "research/architecture/developmental-substrate-v0.ice",
        "03e0643a885bdbf0a40d731876659224e9c7ac43",
        8154
      ],
      "C": [
        "research/architecture/resource-pressure.ice",
        "bcfee51a0b85dbc22cc046a1437775c04e1372c3",
        6214
      ]
    },
    "cycle_order": [
      "A",
      "B",
      "C",
      "C",
      "B",
      "A"
    ],
    "encoding": "identity file bytes; no UTF decoding, normalization, tokenizer, vocabulary, separator, boundary label, or remapping",
    "split": "each demand blob is split at floor(raw_byte_length/2); raw context resets at the split",
    "contamination_rule": "Demand bytes do not contribute to training, baseline fitting, motif learning, successor learning, or frozen training utility. In each cycle only that file's first half may select activation; its second half is inaccessible until selection is frozen."
  },
  "frozen_reuse": {
    "learner": "byte-identical learner imported from EXP-DGR-REAL-UTF8-DEVELOPMENTAL-SPECIALIZATION-001: previous-byte baseline, four-byte statistics, occurrence>=12, consistency>=0.60, ranking, home hash, radius two, and sixteen fixed cells",
    "pressure": "byte-identical sixteen-record fixed-capacity substrate and six-byte retained-record format from the qualified lineage; only the active/retained partition cardinality is the separately qualified seven/nine boundary from experiment 008",
    "error_guided_policy": "byte-identical first-half per-motif incremental-correct contribution, tie breaks, and activation rule from EXP-DGR-REAL-UTF8-ERROR-GUIDED-WAKE-005",
    "metric_definitions": "byte-identical incremental-correct, covered accuracy, coverage, and greedy event-reduction definitions from the qualified lineage"
  },
  "arms_and_state": {
    "full_reference": "all sixteen frozen learned motifs; denominator/reference only",
    "static_control": "the same top seven motifs by frozen training utility in every cycle",
    "repeated_primary": "begin from the seven-motif static active partition; at each cycle rank all sixteen frozen motifs using only that cycle's first-half realized contribution, wake selected retained records, evict deselected active records, and carry the resulting seven/nine partition into the next cycle",
    "active_ceiling": 7,
    "retained_count": 9,
    "persistent_state": "six-byte records containing original cell index, four-byte motif key, and frozen successor; active and retained records together must remain an exact permutation of the original sixteen records",
    "revisit_rule": "the selected key set for the second visit to each file must be identical to its first-visit set; no accumulated learning or history-dependent rank term is allowed"
  },
  "seeds": {
    "randomness": "none",
    "seed_list": [],
    "determinism": "all rankings and transitions use fully specified deterministic tie breaks; two duplicate executions must be byte-identical"
  },
  "budgets": {
    "training_files": 4,
    "fresh_demand_files": 3,
    "demand_cycles": 6,
    "cell_count": 16,
    "active_structure_ceiling": 7,
    "retained_structure_count": 9,
    "maximum_state_transitions": 96,
    "maximum_source_processes": 1,
    "timeout_seconds": 1800,
    "primary_runs": 2,
    "network_access": false,
    "capacity_growth_events": 0
  },
  "metrics_and_thresholds": [
    [
      "training_file_identity_mismatch_count",
      "==",
      0
    ],
    [
      "evaluation_file_identity_mismatch_count",
      "==",
      0
    ],
    [
      "train_eval_blob_overlap_count",
      "==",
      0
    ],
    [
      "valid_cycle_count",
      "==",
      6
    ],
    [
      "minimum_full_incremental_correct_count",
      ">",
      0
    ],
    [
      "minimum_wake_count_per_cross_file_transition",
      ">=",
      1
    ],
    [
      "minimum_eviction_count_per_cross_file_transition",
      ">=",
      1
    ],
    [
      "maximum_same_file_transition_change_count",
      "==",
      0
    ],
    [
      "revisit_active_set_mismatch_count",
      "==",
      0
    ],
    [
      "minimum_primary_active_structure_count",
      "==",
      7
    ],
    [
      "maximum_primary_active_structure_count",
      "==",
      7
    ],
    [
      "minimum_primary_retained_structure_count",
      "==",
      9
    ],
    [
      "maximum_primary_retained_structure_count",
      "==",
      9
    ],
    [
      "minimum_primary_retained_incremental_correct_fraction",
      ">=",
      0.7
    ],
    [
      "minimum_primary_minus_static_retained_fraction",
      ">=",
      0
    ],
    [
      "minimum_eval_covered_accuracy_gain",
      ">",
      0
    ],
    [
      "retained_record_integrity_mismatch_count",
      "==",
      0
    ],
    [
      "state_partition_mismatch_count",
      "==",
      0
    ],
    [
      "future_half_selection_access_count",
      "==",
      0
    ],
    [
      "learned_state_mutation_count",
      "==",
      0
    ],
    [
      "capacity_growth_event_count",
      "==",
      0
    ],
    [
      "tokenizer_use_count",
      "==",
      0
    ],
    [
      "invalid_transition_rows",
      "==",
      0
    ]
  ],
  "controls": [
    "Every cycle compares the carried-state primary against the same frozen full reference and static seven-motif control on identical second-half bytes.",
    "All sixteen learned records remain available only through the current active partition plus exact retained records; selection cannot reconstruct from training statistics after initial state creation.",
    "The repeated C-to-C transition controls for spurious transition activity; it must perform zero wakes and evictions.",
    "The reverse C,B,A traversal tests exact revisit reproducibility after intervening demand shifts.",
    "No second-half byte is read while selecting the active set, and first-half outcomes alter activation only.",
    "Cell count remains exactly sixteen; no replicate, merge, repair, prune, retraining, or capacity growth is permitted."
  ],
  "validity_criteria": [
    "Exact parent, North Star SHA-256, prior evidence identity, source dependencies, and all seven Git blob identities match.",
    "Training and demand blob sets are disjoint, and all three demand files were absent from experiments 001-005 inputs.",
    "The reconstructed learner yields exactly sixteen motifs and the initial pressure state yields exactly seven active plus nine retained records.",
    "All six cycles execute in the frozen order from one carried partition; no cycle resets state to the initial static partition.",
    "Selection uses only the current cycle's first-half outcomes; second-half access begins after its active set is frozen.",
    "Before and after every transition the active and retained partitions are disjoint, have cardinalities seven and nine respectively, and their union is byte-identical in content to the original sixteen frozen records.",
    "Full-model second-half incremental correct count is positive in every cycle.",
    "No retraining, learned-state mutation, tokenizer, capacity growth, external model, or network access occurs.",
    "All metrics are finite and two duplicate executions from identical inputs are byte-identical."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all frozen thresholds pass across all six cycles.",
    "mixed": "Validity passes, transitions preserve exact state and revisits are reproducible, but at least one benefit, transition, or positive-gain threshold fails while retained benefit remains at least 0.50.",
    "null": "Validity passes and state transitions are exact and reproducible, but the minimum primary-minus-static retained fraction is between -0.05 and 0.05 and minimum primary retained fraction is at least 0.50.",
    "negative": "Validity passes but the primary retained fraction is below static by more than 0.05 in any cycle, below 0.50 in any cycle, or cross-file activation does not change.",
    "incomplete": "Environmental or compute interruption prevents both deterministic executions or all six frozen cycles.",
    "invalid": "Any identity, lineage reconstruction, cycle-order, split isolation, future-access, carried-state, partition-integrity, fixed-capacity, finiteness, or qualification criterion fails."
  },
  "stop_conditions": [
    "Stop invalid before scientific evaluation on any identity, lineage reconstruction, input-overlap, previously-used demand file, or dependency mismatch.",
    "Stop invalid on any future-half selection access, learned-state mutation, record or partition corruption, state reset, cycle-order drift, cell-count drift, capacity growth, non-finite metric, or nondeterministic duplicate output.",
    "Do not stop early for apparent supported, mixed, null, or negative outcomes.",
    "After any output is observed, do not repair or rerun under this experiment identifier."
  ],
  "no_post_result_tuning_rule": "After any output is observed, do not alter inputs, order, splits, learner, cue contribution, rankings, tie breaks, transition mechanics, seven-active ceiling, nine-retained format, arms, budgets, metrics, thresholds, aggregation, validity, classification, or stop conditions under this experiment identifier."
}
