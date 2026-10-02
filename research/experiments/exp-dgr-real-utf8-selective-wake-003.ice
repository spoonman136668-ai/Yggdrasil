{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-SELECTIVE-WAKE-003",
  "program": "DG1 real-byte adaptive granularity",
  "question": "Under the supported eight-active resource ceiling, can raw-byte cue occurrence evidence selectively wake useful hibernated motifs and evict less-relevant active motifs so that the same fixed-capacity substrate recovers more of the full 16-motif held-out benefit without retraining?",
  "hypothesis": "For each of the two immutable held-out files, using only motif-key occurrence counts from the first half as a cue will reconfigure the eight-active set under an unchanged ceiling, wake at least one hibernated motif, preserve exactly eight active and eight retained structures, and on the untouched second half retain at least 70% of the full 16-motif incremental correct predictions while improving retained-benefit fraction by at least 0.05 over the static pressured set, maintaining >=0.15 covered-position accuracy gain and >=0.02 event reduction.",
  "exact_parent_sha": "2ad973d0d410615a7ed9b08194e542286d8c4754",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-RESOURCE-PRESSURE-002",
    "classification": "supported",
    "qualification_run_id": "37026364355",
    "result_sha256": "aa49047f9c33d1fbbb9c078274ef7bd72b995a60c3e9ef53e97ec6bdff66b23d"
  },
  "authority": "research-only immutable real-byte selective-wake test; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, retraining, or capacity authority changes",
  "changed_paths": [
    "research/experiments/exp-dgr-real-utf8-selective-wake-003.ice",
    "research/applications/plane/exp-dgr-real-utf8-selective-wake-003.py",
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json"
  ],
  "frozen_reuse": {
    "corpus": "exact six-file split and blob identities from prior supported real-byte tests",
    "learner": "byte-identical supported 16-motif developmental specialization",
    "pressure": "byte-identical supported utility ranking, eight-active ceiling, and six-byte hibernated record format",
    "baseline": "same training-only previous-byte predictor"
  },
  "cue_policy": {
    "split": "each held-out file split at raw byte midpoint into cue half and evaluation half; raw context resets at midpoint",
    "visible_state": "eight active motif keys plus eight retained six-byte records",
    "cue_signal": "count exact occurrences of each of the sixteen known motif keys in cue half; target successor bytes are not read by policy",
    "selection": "rank all sixteen known motifs by descending cue occurrence count, then descending frozen training utility score, then lexicographic four-byte key; choose first eight as active",
    "wake": "selected motif previously hibernated is restored from its six-byte retained record",
    "eviction": "previously active motif not selected becomes a six-byte retained record using its frozen pre-pressure cell/key/successor identity",
    "active_ceiling": 8,
    "retained_count": 8,
    "retraining": false,
    "target_outcome_access": false
  },
  "evaluation": {
    "segment": "second half only, with raw context reset",
    "full_model": "frozen 16-motif model",
    "static_pressure_model": "supported original eight-active pressure set",
    "cue_adapted_model": "cue-selected eight-active set",
    "retained_incremental_correct_fraction": "cue-adapted incremental correct predictions over baseline divided by full-model incremental correct predictions",
    "improvement_over_static_fraction": "cue-adapted retained fraction minus static pressured retained fraction",
    "covered_accuracy_gain": "cue-adapted top1 accuracy minus baseline accuracy on cue-adapted motif-covered positions",
    "event_reduction": "greedy non-overlapping replacement of cue-adapted four-byte motifs by one event"
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
      "valid_evaluation_file_count",
      "==",
      2
    ],
    [
      "minimum_woken_hibernated_motif_count_per_file",
      ">=",
      1
    ],
    [
      "maximum_woken_hibernated_motif_count_per_file",
      "<=",
      8
    ],
    [
      "minimum_post_wake_active_structure_count",
      "==",
      8
    ],
    [
      "maximum_post_wake_active_structure_count",
      "==",
      8
    ],
    [
      "minimum_post_wake_retained_structure_count",
      "==",
      8
    ],
    [
      "maximum_post_wake_retained_structure_count",
      "==",
      8
    ],
    [
      "minimum_retained_incremental_correct_fraction",
      ">=",
      0.7
    ],
    [
      "minimum_improvement_over_static_fraction",
      ">=",
      0.05
    ],
    [
      "minimum_eval_covered_position_fraction",
      ">=",
      0.01
    ],
    [
      "minimum_eval_covered_accuracy_gain",
      ">=",
      0.15
    ],
    [
      "minimum_effective_event_reduction_fraction",
      ">=",
      0.02
    ],
    [
      "retained_record_integrity_mismatch_count",
      "==",
      0
    ],
    [
      "cue_target_byte_access_count",
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
      "invalid_wake_rows",
      "==",
      0
    ]
  ],
  "validity_criteria": [
    "Exact parent, North Star, prior supported pressure evidence identity, and all blob identities match.",
    "The full and static-pressure states are reconstructed byte-identically from prior qualified logic.",
    "Cue ranking uses only key occurrence counts, frozen training utility, and raw keys; it does not read cue successor targets or evaluation-half bytes.",
    "Exactly eight structures are active and eight retained after every reconfiguration.",
    "All wakes decode exact six-byte retained records; evictions encode the same exact record format.",
    "Evaluation half is read-only and no retraining, repair, capacity growth, or post-result adaptation occurs.",
    "All metrics are finite and duplicate executions are byte-identical."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all twenty frozen thresholds pass on both files.",
    "mixed": "Validity passes and cue-adapted retained fraction is >= static pressure on both files, but at least one wake-count, improvement, retained-benefit, coverage, gain, or event threshold fails.",
    "negative": "Validity passes but cue adaptation reduces retained-benefit fraction on either file or fails to wake any hibernated motif on either file.",
    "incomplete": "Environmental or compute interruption prevents complete two-file execution.",
    "invalid": "Blob identity, prior-state reconstruction, cue isolation, retained-record integrity, active ceiling, held-out isolation, finiteness, or qualification criteria fail."
  },
  "no_post_result_tuning_rule": "Do not alter corpus, midpoint split, cue ranking, utility tie-break, active ceiling, record format, metrics, thresholds, aggregation, or classification after any output is observed."
}
