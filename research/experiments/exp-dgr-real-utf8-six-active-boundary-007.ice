{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-SIX-ACTIVE-BOUNDARY-007",
  "program": "DG1 real-byte adaptive granularity",
  "question": "Across the three immutable demand files qualified in experiment 006, can the frozen non-oracle error-guided policy reduce the active phenotype from eight to six motifs while retaining at least 70% of the full sixteen-motif second-half prediction benefit under exact fixed-capacity state accounting?",
  "hypothesis": "For each demand file independently, selecting six of the sixteen frozen motifs solely by first-half incremental-correct contribution will retain at least 70% of the full-model second-half incremental correct predictions, remain no worse than a six-motif frozen-training-utility control, preserve positive covered-position accuracy gain, and keep exactly six active plus ten byte-exact retained records without retraining, mutation, or capacity growth.",
  "exact_parent_sha": "3d80fad3719d20faf27582a4bc5b87349bd95cb5",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-REPEATED-ERROR-GUIDED-WAKE-006",
    "classification": "mixed-by-frozen-rules",
    "qualification_run_id": "37030702834",
    "result_sha256": "c35d88609b0583e4f079657dcb9357b714dbc12b34dcb7bd4c2cdb6a0e57f5de",
    "observation": "Repeated eight-active selection preserved exact carried state and revisit sets, retained at least 0.80 of full benefit, and was never worse than static, while minimum coverage 0.00614 and event reduction 0.01266 missed their frozen thresholds. The minimum active capacity preserving predictive benefit remains unknown."
  },
  "authority": "synthetic research-only evaluation on immutable repo-owned bytes; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, retraining, production, broker, live-interface, or authority changes",
  "changed_paths": [
    "research/experiments/exp-dgr-real-utf8-six-active-boundary-007.ice",
    "research/applications/plane/exp-dgr-real-utf8-six-active-boundary-007.py",
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
    "demand": [
      ["research/architecture/developmental-substrate-v0.1.ice", "cea1d9966056f097838eb350a42795219f046fc3", 8054],
      ["research/architecture/developmental-substrate-v0.ice", "03e0643a885bdbf0a40d731876659224e9c7ac43", 8154],
      ["research/architecture/resource-pressure.ice", "bcfee51a0b85dbc22cc046a1437775c04e1372c3", 6214]
    ],
    "encoding": "identity file bytes; no UTF decoding, normalization, tokenizer, vocabulary, separator, boundary label, or remapping",
    "split": "each demand blob is split at floor(raw_byte_length/2); raw context resets at the split",
    "reuse_disclosure": "Demand files and their outcomes were used in experiment 006. This experiment is a preregistered within-lineage active-capacity boundary test, not a fresh-corpus generalization claim.",
    "contamination_rule": "Demand bytes never contribute to training, baseline fitting, motif learning, successor learning, or frozen training utility. For each file, only its first half may select activation; its second half is inaccessible until selection is frozen."
  },
  "frozen_reuse": {
    "learner": "byte-identical learner from experiment 001 through the qualified experiment-006 dependency chain: previous-byte baseline, four-byte statistics, occurrence>=12, consistency>=0.60, ranking, home hash, radius two, and sixteen fixed cells",
    "cue": "byte-identical first-half per-motif incremental-correct contribution and deterministic tie breaks from experiments 005-006",
    "records": "byte-identical six-byte record containing original cell index, four-byte motif key, and frozen successor",
    "metrics": "byte-identical incremental-correct and covered-position accuracy definitions from the qualified lineage"
  },
  "arms": {
    "full_reference": "all sixteen frozen motifs; denominator only",
    "six_static_control": "top six motifs by frozen training utility, then raw key",
    "six_error_guided_primary": "top six motifs by descending first-half incremental-correct contribution, then descending frozen training utility, then raw key"
  },
  "seeds": {
    "randomness": "none",
    "seed_list": [],
    "determinism": "all rankings use fully specified deterministic tie breaks; two duplicate executions must be byte-identical"
  },
  "budgets": {
    "training_files": 4,
    "demand_files": 3,
    "cell_count": 16,
    "active_structure_count": 6,
    "retained_structure_count": 10,
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
    ["valid_evaluation_file_count", "==", 3],
    ["minimum_full_incremental_correct_count", ">", 0],
    ["minimum_primary_active_structure_count", "==", 6],
    ["maximum_primary_active_structure_count", "==", 6],
    ["minimum_primary_retained_structure_count", "==", 10],
    ["maximum_primary_retained_structure_count", "==", 10],
    ["minimum_primary_retained_incremental_correct_fraction", ">=", 0.70],
    ["minimum_primary_minus_static_retained_fraction", ">=", 0.0],
    ["minimum_eval_covered_accuracy_gain", ">", 0.0],
    ["retained_record_integrity_mismatch_count", "==", 0],
    ["state_partition_mismatch_count", "==", 0],
    ["future_half_selection_access_count", "==", 0],
    ["learned_state_mutation_count", "==", 0],
    ["capacity_growth_event_count", "==", 0],
    ["tokenizer_use_count", "==", 0],
    ["invalid_evaluation_rows", "==", 0]
  ],
  "controls": [
    "Every file compares primary and static six-active sets against the same full reference on identical second-half bytes.",
    "All sixteen records remain represented exactly once across active and retained partitions.",
    "Each file is selected independently from the same frozen sixteen-record state; no cross-file learning or carried rank term is permitted.",
    "No second-half byte is read while selecting either active set, and first-half outcomes alter activation only.",
    "The eight-active experiment-006 outcome motivates the boundary but is not an arm and supplies no selection information.",
    "Cell count remains sixteen; no replicate, merge, repair, prune, retraining, or capacity growth is permitted."
  ],
  "validity_criteria": [
    "Exact parent, North Star SHA-256, prior evidence identity, source dependencies, and all seven Git blob identities match.",
    "Training and demand blob sets are disjoint, and the reuse disclosure remains explicit.",
    "The reconstructed learner yields exactly sixteen motifs and both arms select exactly six active records per file.",
    "Selection uses only each file's first-half outcomes; second-half access begins after both active sets are frozen.",
    "For every file, active and retained partitions are disjoint and their union is byte-identical to the original sixteen records.",
    "Full-model second-half incremental correct count is positive for every file.",
    "No retraining, learned-state mutation, tokenizer, capacity growth, external model, or network access occurs.",
    "All metrics are finite and two duplicate executions from identical inputs are byte-identical."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all nineteen frozen thresholds pass on all three files.",
    "mixed": "Validity passes and the primary retains at least 0.50 of full benefit on every file, but at least one retained-benefit, static-control, or positive-gain threshold fails.",
    "null": "Validity passes, the primary retained fraction is within 0.05 of static on every file, and at least one file retains less than 0.50 of full benefit.",
    "negative": "Validity passes but primary is below static by more than 0.05 on any file, retains less than 0.25 of full benefit on any file, or has non-positive covered-position accuracy gain on every file.",
    "incomplete": "Environmental or compute interruption prevents both deterministic executions or all three evaluations.",
    "invalid": "Any identity, lineage reconstruction, split isolation, future-access, partition-integrity, fixed-capacity, finiteness, or qualification criterion fails."
  },
  "stop_conditions": [
    "Stop invalid before scientific evaluation on any identity, lineage reconstruction, input-overlap, or dependency mismatch.",
    "Stop invalid on any future-half selection access, learned-state mutation, record or partition corruption, cell-count drift, capacity growth, non-finite metric, or nondeterministic duplicate output.",
    "Do not stop early for apparent supported, mixed, null, or negative outcomes.",
    "After any output is observed, do not repair or rerun under this experiment identifier."
  ],
  "no_post_result_tuning_rule": "After any primary or diagnostic output is observed, do not alter inputs, splits, learner, cue, rankings, tie breaks, active or retained counts, arms, budgets, metrics, thresholds, aggregation, validity, classification, or stop conditions under this experiment identifier."
}
