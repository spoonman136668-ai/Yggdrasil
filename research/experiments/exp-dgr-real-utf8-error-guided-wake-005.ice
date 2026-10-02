{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-ERROR-GUIDED-WAKE-005",
  "program": "DG1 real-byte adaptive granularity",
  "question": "On two fresh immutable held-out UTF-8 architecture files, can a non-oracle cue based only on first-half realized prediction outcomes select eight active motifs that recover at least 70% of the frozen full model's second-half benefit without future-half access, retraining, or capacity growth?",
  "hypothesis": "For each fresh held-out file, ranking the sixteen frozen learned motifs by their first-half incremental correct contribution over the frozen previous-byte baseline will preserve exactly eight active and eight retained structures, wake at least one formerly hibernated motif, and on the untouched second half retain at least 70% of full-model incremental correct predictions while exceeding both the frozen static-pressure and occurrence-only cue retained fractions by at least 0.05, with at least 0.01 motif coverage, 0.15 covered-position accuracy gain, and 0.02 effective event reduction.",
  "exact_parent_sha": "2f108e4d540a0e9c2a37c0c980cba7b86544b16d",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-SELECTIVE-WAKE-ATTRIBUTION-004",
    "classification": "supported-attribution-cue-mismatch",
    "qualification_run_id": "37027249686",
    "result_sha256": "cec83728b4482539b5bcc3aed4c0ca32f24afb357855b0c0591aed0b0a6b701c",
    "implication": "Eight active motifs were sufficient on the prior files under evaluator-optimal selection, but occurrence-only first-half cues were poorly aligned with future utility."
  },
  "authority": "synthetic research-only evaluation on immutable repo-owned bytes; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, retraining, or capacity authority changes",
  "changed_paths": [
    "research/experiments/exp-dgr-real-utf8-error-guided-wake-005.ice",
    "research/applications/plane/exp-dgr-real-utf8-error-guided-wake-005.py",
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
    "fresh_evaluation": [
      ["research/architecture/cell-model.ice", "db9d3c06e0cc0ddd780c7e51685d7dcdfdd32673", 5889],
      ["research/architecture/developmental-genome.ice", "d7791d7971ebcc82999cb90219cb71387ba3005e", 6203]
    ],
    "encoding": "identity file bytes; no UTF decoding, normalization, tokenizer, vocabulary, separator, boundary label, or remapping",
    "split": "each fresh evaluation blob is split at floor(raw_byte_length/2); raw context resets at the split",
    "contamination_rule": "Fresh evaluation bytes do not contribute to training, baseline fitting, motif learning, or frozen training utility. First-half bytes may only determine cue ranking; second-half bytes are inaccessible until evaluation."
  },
  "frozen_reuse": {
    "learner": "byte-identical learner imported from EXP-DGR-REAL-UTF8-DEVELOPMENTAL-SPECIALIZATION-001: previous-byte baseline, four-byte statistics, occurrence>=12, consistency>=0.60, ranking, home hash, radius two, and sixteen fixed cells",
    "pressure": "byte-identical utility ranking, eight-active ceiling, and six-byte retained-record format from EXP-DGR-REAL-UTF8-RESOURCE-PRESSURE-002",
    "occurrence_control": "byte-identical first-half occurrence ranking from EXP-DGR-REAL-UTF8-SELECTIVE-WAKE-003",
    "metric_definitions": "byte-identical incremental-correct, covered accuracy, coverage, and greedy event-reduction definitions from the qualified lineage"
  },
  "arms": {
    "full_reference": "all sixteen frozen motifs; denominator/reference only",
    "static_control": "top eight motifs by frozen training utility",
    "occurrence_control": "top eight by first-half motif occurrence count, then frozen training utility, then raw key",
    "error_guided_primary": "top eight by descending first-half per-motif incremental correct contribution over the frozen previous-byte baseline, then descending frozen training utility, then raw key"
  },
  "cue_and_state_rules": {
    "per_motif_contribution": "For each known four-byte motif independently, count first-half positions where its frozen successor prediction is correct minus positions where the frozen previous-byte baseline is correct.",
    "allowed_outcomes": "The cue reads first-half target bytes solely to score already-frozen motif predictions; it performs no parameter, successor, baseline, or motif update.",
    "wake": "A primary-selected motif absent from the static set is restored from its exact six-byte retained record.",
    "eviction": "A static-active motif absent from the primary set becomes its exact frozen six-byte retained record.",
    "active_ceiling": 8,
    "retained_count": 8,
    "retraining": false,
    "future_half_access_during_selection": false
  },
  "seeds": {
    "randomness": "none",
    "seed_list": [],
    "determinism": "all rankings use fully specified deterministic tie breaks; two duplicate executions must be byte-identical"
  },
  "budgets": {
    "training_files": 4,
    "fresh_evaluation_files": 2,
    "cell_count": 16,
    "active_structure_ceiling": 8,
    "retained_structure_count": 8,
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
    ["valid_evaluation_file_count", "==", 2],
    ["minimum_full_incremental_correct_count", ">", 0],
    ["minimum_woken_hibernated_motif_count_per_file", ">=", 1],
    ["minimum_primary_active_structure_count", "==", 8],
    ["maximum_primary_active_structure_count", "==", 8],
    ["minimum_primary_retained_structure_count", "==", 8],
    ["maximum_primary_retained_structure_count", "==", 8],
    ["minimum_primary_retained_incremental_correct_fraction", ">=", 0.70],
    ["minimum_primary_minus_static_retained_fraction", ">=", 0.05],
    ["minimum_primary_minus_occurrence_retained_fraction", ">=", 0.05],
    ["minimum_eval_covered_position_fraction", ">=", 0.01],
    ["minimum_eval_covered_accuracy_gain", ">=", 0.15],
    ["minimum_effective_event_reduction_fraction", ">=", 0.02],
    ["retained_record_integrity_mismatch_count", "==", 0],
    ["future_half_selection_access_count", "==", 0],
    ["learned_state_mutation_count", "==", 0],
    ["capacity_growth_event_count", "==", 0],
    ["tokenizer_use_count", "==", 0],
    ["invalid_wake_rows", "==", 0]
  ],
  "controls": [
    "Static and occurrence arms are reconstructed from frozen qualified policies.",
    "All arms use the same frozen baseline, motifs, second-half bytes, and eight-active budget.",
    "No second-half byte is read while selecting the primary active set.",
    "First-half outcomes change activation only and never alter learned motif state.",
    "Cell count remains exactly sixteen; no replicate, merge, repair, prune, or capacity growth is permitted.",
    "Each file is evaluated independently; state and context reset between files."
  ],
  "validity_criteria": [
    "Exact parent, North Star SHA-256, prior evidence identity, source dependencies, and all six Git blob identities match.",
    "Training and fresh evaluation blob sets are disjoint, and neither fresh file appeared in experiments 001-004.",
    "The learner yields exactly sixteen motifs and pressure yields exactly eight active plus eight exact retained records.",
    "Selection uses first-half outcomes only; second-half access begins after the active set is frozen.",
    "Exactly eight structures remain active and eight retained for every arm and file.",
    "Full-model second-half incremental correct count is positive for both files.",
    "No retraining, learned-state mutation, tokenizer, capacity growth, external model, or network access occurs.",
    "All metrics are finite and two duplicate executions from identical inputs are byte-identical."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all twenty-two frozen thresholds pass on both fresh files.",
    "mixed": "Validity passes and primary retained fraction is no worse than both controls on both files, but at least one benefit, wake, coverage, gain, or event threshold fails.",
    "negative": "Validity passes but the primary retained fraction is below either control on either file, below 0.50 on either file, or no hibernated motif is woken on either file.",
    "incomplete": "Environmental or compute interruption prevents both deterministic executions or both-file evaluation.",
    "invalid": "Any identity, lineage reconstruction, split isolation, future-access, state-integrity, fixed-capacity, finiteness, or qualification criterion fails."
  },
  "stop_conditions": [
    "Stop invalid before scientific evaluation on any identity, lineage reconstruction, input-overlap, or dependency mismatch.",
    "Stop invalid on any future-half selection access, learned-state mutation, retained-record corruption, cell-count drift, capacity growth, non-finite metric, or nondeterministic duplicate output.",
    "After any output is observed, do not repair or rerun under this experiment identifier."
  ],
  "no_post_result_tuning_rule": "After any primary or diagnostic output is observed, do not alter inputs, splits, learner, cue contribution, rankings, tie breaks, active ceiling, retained format, arms, budgets, metrics, thresholds, aggregation, validity, or classification under this experiment identifier."
}
