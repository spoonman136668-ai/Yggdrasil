{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-SEVEN-ACTIVE-CROSS-DOMAIN-SHIFT-011",
  "program": "DG1 real-byte adaptive granularity",
  "question": "Across six ordered demand-shift cycles over three previously unused immutable Track-A UTF-8 research documents, does the qualified seven-active non-oracle error-guided policy transfer unchanged from architecture prose while preserving prediction benefit, exact retained state, and identical active sets on revisits?",
  "hypothesis": "Carrying one frozen sixteen-motif phenotype through A,B,C,C,B,A on a fresh prose domain, first-half error-guided selection will preserve exactly seven active and nine retained motifs in every cycle, perform at least one wake and eviction at every cross-file transition, reproduce each file's selected set on revisit, retain at least 70% of full-model second-half incremental correct predictions, remain no worse than the static seven-motif control, and maintain positive covered-position accuracy gain without learned-state mutation, record corruption, or capacity growth.",
  "exact_parent_sha": "099a5c9e5ae044c54ad4c175c2acdc889be779f1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-SEVEN-ACTIVE-REPEATED-SHIFT-010",
    "classification": "supported-by-frozen-thresholds",
    "qualification_run_id": "37038824697",
    "result_sha256": "6b3c7d23f7692e62ca4b0389f9357f4bd3df2101fd7130af2df38343513f993d",
    "observation": "On the three within-lineage architecture demand files, all frozen 010 thresholds passed: the carried seven/nine partition was exact, cross-file transitions exchanged at least two motifs, revisits were identical, retained benefit was at least 0.80 and never below static, and covered-position gain remained positive. Cross-domain portability remains untested."
  },
  "authority": "synthetic research-only evaluation on immutable repo-owned bytes; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, retraining, production, broker, live-interface, or authority changes",
  "changed_paths": [
    "research/experiments/exp-dgr-real-utf8-seven-active-cross-domain-shift-011.ice",
    "research/applications/plane/exp-dgr-real-utf8-seven-active-cross-domain-shift-011.py",
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
      "A": ["research/applications/track-a/a02-adaptive-transform-service-organism.ice", "2770482f2bd0fcffab8b00d206c54ae81f3ae7a1", 21855],
      "B": ["research/applications/track-a/a03-fixa-dynamic-partition-remerge-alignment.ice", "ea322d9b33044d9c0442df460fc2b354b2d4830b", 11293],
      "C": ["research/applications/track-a/a03-heldout-adaptive-generalization.ice", "fdb9b8c908ed45e075fdb39ac578c0e3c79edce5", 28605]
    },
    "cycle_order": ["A", "B", "C", "C", "B", "A"],
    "encoding": "identity file bytes; no UTF decoding, normalization, tokenizer, vocabulary, separator, boundary label, or remapping",
    "split": "each demand blob is split at floor(raw_byte_length/2); raw context resets at the split",
    "freshness": "The three demand Git blobs do not appear in experiments 001-010 inputs and no outcome from them has been observed for this lineage before this preregistration.",
    "contamination_rule": "Demand bytes do not contribute to training, baseline fitting, motif learning, successor learning, or frozen training utility. In each cycle only that file's first half may select activation; its second half is inaccessible until selection is frozen."
  },
  "frozen_reuse": {
    "learner": "byte-identical qualified learner: previous-byte baseline, four-byte statistics, occurrence>=12, consistency>=0.60, ranking, home hash, radius two, and sixteen fixed cells",
    "state": "byte-identical sixteen-record substrate and six-byte retained-record encoding from the qualified lineage with the seven-active/nine-retained boundary qualified in 008",
    "selector": "byte-identical first-half per-motif incremental-correct contribution and deterministic tie breaks qualified in 005 and reused through 010",
    "metrics": "byte-identical incremental-correct, covered-position accuracy, coverage, and greedy event-reduction definitions from 010"
  },
  "arms_and_state": {
    "full_reference": "all sixteen frozen motifs; denominator/reference only",
    "static_control": "the same top seven motifs by frozen training utility in every cycle",
    "repeated_primary": "begin from the seven-motif static partition; at each cycle rank all sixteen frozen records using only that cycle's first-half realized contribution, wake selected retained records, evict deselected active records, and carry the resulting partition",
    "active_ceiling": 7,
    "retained_count": 9,
    "persistent_state": "six-byte records containing original cell index, four-byte motif key, and frozen successor; active plus retained records must remain an exact permutation of the original sixteen records",
    "revisit_rule": "the second selected set for each file must equal its first selected set; no accumulated learning or history-dependent ranking is allowed"
  },
  "seeds": {
    "randomness": "none",
    "seed_list": [],
    "determinism": "fully specified deterministic rankings and transitions; two complete executions must be byte-identical"
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
    ["training_file_identity_mismatch_count", "==", 0],
    ["evaluation_file_identity_mismatch_count", "==", 0],
    ["train_eval_blob_overlap_count", "==", 0],
    ["valid_cycle_count", "==", 6],
    ["minimum_full_incremental_correct_count", ">", 0],
    ["minimum_wake_count_per_cross_file_transition", ">=", 1],
    ["minimum_eviction_count_per_cross_file_transition", ">=", 1],
    ["maximum_same_file_transition_change_count", "==", 0],
    ["revisit_active_set_mismatch_count", "==", 0],
    ["minimum_primary_active_structure_count", "==", 7],
    ["maximum_primary_active_structure_count", "==", 7],
    ["minimum_primary_retained_structure_count", "==", 9],
    ["maximum_primary_retained_structure_count", "==", 9],
    ["minimum_primary_retained_incremental_correct_fraction", ">=", 0.70],
    ["minimum_primary_minus_static_retained_fraction", ">=", 0.0],
    ["minimum_eval_covered_accuracy_gain", ">", 0.0],
    ["retained_record_integrity_mismatch_count", "==", 0],
    ["state_partition_mismatch_count", "==", 0],
    ["future_half_selection_access_count", "==", 0],
    ["learned_state_mutation_count", "==", 0],
    ["capacity_growth_event_count", "==", 0],
    ["tokenizer_use_count", "==", 0],
    ["invalid_transition_rows", "==", 0]
  ],
  "controls": [
    "Every cycle compares carried-state primary against the same frozen full reference and static seven-motif control on identical second-half bytes.",
    "All sixteen records remain available only through the current active partition plus exact retained records; selection cannot reconstruct them after initial state creation.",
    "The repeated C-to-C transition must produce zero wakes and evictions.",
    "The reverse C,B,A traversal tests exact revisit reproducibility after intervening cross-domain demand shifts.",
    "No second-half byte is read while selecting; first-half outcomes alter activation only.",
    "Cell count remains sixteen; no replicate, merge, repair, prune, retraining, learned-state mutation, or capacity growth is permitted."
  ],
  "validity_criteria": [
    "Exact parent, North Star SHA-256, prior evidence identity, source dependencies, and all seven Git blob identities match.",
    "Training and demand blob sets are disjoint, all fresh demand blobs are absent from experiments 001-010 inputs, and their exact sizes match.",
    "The learner yields exactly sixteen motifs and the initial pressure state yields seven active plus nine retained records.",
    "All six cycles execute in the frozen order from one carried partition without state reset.",
    "Selection uses only current first-half outcomes; second-half access begins after the active set is frozen.",
    "Before and after every transition the partitions are disjoint, have cardinalities seven and nine, and their union is byte-identical to the original sixteen records.",
    "No retraining, learned-state mutation, tokenizer, capacity growth, external model, or network access occurs.",
    "All metrics are finite and two duplicate complete executions are byte-identical."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all frozen thresholds pass across all six fresh-domain cycles.",
    "mixed": "Validity passes, transitions preserve exact state and revisits are reproducible, but at least one benefit, transition, or positive-gain threshold fails while minimum retained benefit is at least 0.50.",
    "null": "Validity passes and transitions are exact and reproducible, but minimum primary-minus-static retained fraction is between -0.05 and 0.05 while minimum retained benefit is at least 0.50.",
    "negative": "Validity passes but retained benefit is below static by more than 0.05 in any cycle, below 0.50 in any cycle, full-reference incremental benefit is non-positive on any fresh file, or cross-file activation does not change.",
    "incomplete": "Environmental or compute interruption prevents both deterministic executions or all six cycles.",
    "invalid": "Any identity, lineage, freshness, split isolation, future-access, carried-state, partition-integrity, fixed-capacity, finiteness, or qualification criterion fails."
  },
  "stop_conditions": [
    "Stop invalid before scientific evaluation on any identity, lineage, input-overlap, freshness, size, or dependency mismatch.",
    "Stop invalid on future-half selection access, learned-state mutation, record or partition corruption, state reset, cycle-order drift, cell-count drift, capacity growth, non-finite metric, or nondeterministic duplicate output.",
    "Do not stop early for apparent supported, mixed, null, or negative outcomes.",
    "After any output is observed, do not repair or rerun under this experiment identifier."
  ],
  "no_post_result_tuning_rule": "After any primary or diagnostic output is observed, do not alter inputs, order, splits, learner, selector, rankings, tie breaks, transition mechanics, seven-active ceiling, nine-retained format, arms, budgets, metrics, thresholds, aggregation, validity, classification, or stop conditions under this experiment identifier."
}
