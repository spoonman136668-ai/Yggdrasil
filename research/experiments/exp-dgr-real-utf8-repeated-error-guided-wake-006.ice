{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-REPEATED-ERROR-GUIDED-WAKE-006",
  "program": "DG1 real-byte adaptive granularity",
  "question": "Across six ordered demand-shift cycles over three previously unused immutable UTF-8 architecture files, can the qualified non-oracle error-guided policy repeatedly exchange active and retained motifs under the fixed eight-active ceiling while preserving prediction benefit, exact retained state, and identical active sets when a file is revisited?",
  "hypothesis": "Carrying one sixteen-motif phenotype through the frozen sequence A,B,C,C,B,A, first-half error-guided selection will preserve exactly eight active and eight retained motifs in every cycle, perform at least one wake and one eviction at every cross-file transition, reproduce the identical selected set on every file revisit, retain at least 70% of full-model second-half incremental correct predictions, exceed the static eight-motif control by at least 0.05 retained fraction, and maintain at least 0.01 coverage, 0.15 covered-position accuracy gain, and 0.02 effective event reduction without learned-state mutation, record corruption, or capacity growth.",
  "exact_parent_sha": "700a6ad0f21d00f2f65894736471a817cc73e8e5",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-ERROR-GUIDED-WAKE-005",
    "classification": "supported-by-frozen-thresholds",
    "qualification_run_id": "37029273633",
    "result_sha256": "01bfdd445f098c7befb1cfa696cc669660d0e8c66f5be4bb7de9cf5f02ea4792",
    "observation": "On two fresh files the first-half error-guided policy retained 100% of full-model incremental correct predictions, exceeded both controls by at least 0.3548, woke at least three retained motifs, and preserved exact fixed-capacity state. Repeated carried-state reconfiguration remains untested."
  },
  "authority": "synthetic research-only evaluation on immutable repo-owned bytes; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, retraining, production, broker, live-interface, or authority changes",
  "changed_paths": [
    "research/experiments/exp-dgr-real-utf8-repeated-error-guided-wake-006.ice",
    "research/applications/plane/exp-dgr-real-utf8-repeated-error-guided-wake-006.py",
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json"
  ],
  "inputs": {
    "training": [
      ["research/architecture/measurement-framework.ice", "6374fc3c39ee821c8f9d565bb7de0875c07d5cdc", 10040],
      ["research/architecture/structural-plasticity.ice", "d2d75b4ed60e0c112de5202ba31848b15081e0cb", 9550],
      ["research/architecture/developmental-substrate-v0.2.ice", "52d6e87e2339bdf586c33da22470e38a9ca27785", 8448],
      ["research/architecture/yggdrasil-north-star.ice", "84358ec54c0e7eba6b6f830e0b4d2755920281cb", 8411]
    ],
    "fresh_demand_files": {
      "A": ["research/architecture/developmental-substrate-v0.1.ice", "cea1d9966056f097838eb350a42795219f046fc3", 8054],
      "B": ["research/architecture/developmental-substrate-v0.ice", "03e0643a885bdbf0a40d731876659224e9c7ac43", 8154],
      "C": ["research/architecture/resource-pressure.ice", "bcfee51a0b85dbc22cc046a1437775c04e1372c3", 6214]
    },
    "cycle_order": ["A", "B", "C", "C", "B", "A"],
    "encoding": "identity file bytes; no UTF decoding, normalization, tokenizer, vocabulary, separator, boundary label, or remapping",
    "split": "each demand blob is split at floor(raw_byte_length/2); raw context resets at the split",
    "contamination_rule": "Demand bytes do not contribute to training, baseline fitting, motif learning, successor learning, or frozen training utility. In each cycle only that file's first half may select activation; its second half is inaccessible until selection is frozen."
  },
  "frozen_reuse": {
    "learner": "byte-identical learner imported from EXP-DGR-REAL-UTF8-DEVELOPMENTAL-SPECIALIZATION-001: previous-byte baseline, four-byte statistics, occurrence>=12, consistency>=0.60, ranking, home hash, radius two, and sixteen fixed cells",
    "pressure": "byte-identical utility ranking, eight-active ceiling, and six-byte retained-record format from EXP-DGR-REAL-UTF8-RESOURCE-PRESSURE-002",
    "error_guided_policy": "byte-identical first-half per-motif incremental-correct contribution, tie breaks, and activation rule from EXP-DGR-REAL-UTF8-ERROR-GUIDED-WAKE-005",
    "metric_definitions": "byte-identical incremental-correct, covered accuracy, coverage, and greedy event-reduction definitions from the qualified lineage"
  },
  "arms_and_state": {
    "full_reference": "all sixteen frozen learned motifs; denominator/reference only",
    "static_control": "the same top eight motifs by frozen training utility in every cycle",
    "repeated_primary": "begin from the static active/retained partition; at each cycle rank all sixteen frozen motifs using only that cycle's first-half realized contribution, wake selected retained records, evict deselected active records, and carry the resulting partition into the next cycle",
    "active_ceiling": 8,
    "retained_count": 8,
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
    "active_structure_ceiling": 8,
    "retained_structure_count": 8,
    "maximum_state_transitions": 96,
    "maximum_source_processes": 1,
    "timeout_seconds": 1800,
    "primary_runs": 2,
    "network_access": false,
    "capacity_growth_events": 0
  },
  "metrics_and_thresholds": [
    ["training_file_identity_mismatch_count", "==", 0],
    ["evaluation_file_identity_mismatch_count", "==", 0],
    ["train_eval_blob_overlap_count", "==", 0],
    ["valid_cycle_count", "==", 6],
    ["minimum_full_incremental_correct_count", ">", 0],
    ["minimum_wake_count_per_cross_file_transition", ">=", 1],
    ["minimum_eviction_count_per_cross_file_transition", ">=", 1],
    ["maximum_same_file_transition_change_count", "==", 0],
    ["revisit_active_set_mismatch_count", "==", 0],
    ["minimum_primary_active_structure_count", "==", 8],
    ["maximum_primary_active_structure_count", "==", 8],
    ["minimum_primary_retained_structure_count", "==", 8],
    ["maximum_primary_retained_structure_count", "==", 8],
    ["minimum_primary_retained_incremental_correct_fraction", ">=", 0.70],
    ["minimum_primary_minus_static_retained_fraction", ">=", 0.05],
    ["minimum_eval_covered_position_fraction", ">=", 0.01],
    ["minimum_eval_covered_accuracy_gain", ">=", 0.15],
    ["minimum_effective_event_reduction_fraction", ">=", 0.02],
    ["retained_record_integrity_mismatch_count", "==", 0],
    ["state_partition_mismatch_count", "==", 0],
    ["future_half_selection_access_count", "==", 0],
    ["learned_state_mutation_count", "==", 0],
    ["capacity_growth_event_count", "==", 0],
    ["tokenizer_use_count", "==", 0],
    ["invalid_transition_rows", "==", 0]
  ],
  "controls": [
    "Every cycle compares the carried-state primary against the same frozen full reference and static eight-motif control on identical second-half bytes.",
    "All sixteen learned records remain available only through the current active partition plus exact retained records; selection cannot reconstruct from training statistics after initial state creation.",
    "The repeated C-to-C transition controls for spurious transition activity; it must perform zero wakes and evictions.",
    "The reverse C,B,A traversal tests exact revisit reproducibility after intervening demand shifts.",
    "No second-half byte is read while selecting the active set, and first-half outcomes alter activation only.",
    "Cell count remains exactly sixteen; no replicate, merge, repair, prune, retraining, or capacity growth is permitted."
  ],
  "validity_criteria": [
    "Exact parent, North Star SHA-256, prior evidence identity, source dependencies, and all seven Git blob identities match.",
    "Training and demand blob sets are disjoint, and all three demand files were absent from experiments 001-005 inputs.",
    "The reconstructed learner yields exactly sixteen motifs and the initial pressure state yields exactly eight active plus eight retained records.",
    "All six cycles execute in the frozen order from one carried partition; no cycle resets state to the initial static partition.",
    "Selection uses only the current cycle's first-half outcomes; second-half access begins after its active set is frozen.",
    "Before and after every transition the active and retained partitions are disjoint, each has cardinality eight, and their union is byte-identical in content to the original sixteen frozen records.",
    "Full-model second-half incremental correct count is positive in every cycle.",
    "No retraining, learned-state mutation, tokenizer, capacity growth, external model, or network access occurs.",
    "All metrics are finite and two duplicate executions from identical inputs are byte-identical."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all twenty-five frozen thresholds pass across all six cycles.",
    "mixed": "Validity passes, every transition preserves exact state, every revisit is reproducible, and primary retained fraction is no worse than static in every cycle, but at least one benefit, transition, coverage, gain, or event threshold fails.",
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
  "no_post_result_tuning_rule": "After any primary or diagnostic output is observed, do not alter inputs, order, splits, learner, cue contribution, rankings, tie breaks, transition mechanics, active ceiling, retained format, arms, budgets, metrics, thresholds, aggregation, validity, classification, or stop conditions under this experiment identifier."
}
