{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-DEVELOPMENTAL-SPECIALIZATION-001",
  "program": "DG1 real-byte developmental specialization",
  "question": "Can the existing fixed 16-cell Yggdrasil developmental substrate differentiate a bounded set of predictive four-byte structures directly from immutable real UTF-8 project prose and improve next-byte prediction on two held-out files without tokenization, supplied boundaries, or capacity growth?",
  "hypothesis": "Across four immutable training architecture documents and two disjoint held-out architecture documents, a fixed 16-cell ring using only local home-plus/minus-two DIFFERENTIATE operations will learn at least 8 predictive raw-byte motifs, transfer at least 6 of them to each held-out file, cover at least 1% of held-out next-byte positions, improve top-1 accuracy by at least 0.10 over a previous-byte baseline on motif-covered positions, reduce effective event count by at least 0.005, and maintain exact 16-cell capacity with zero tokenizer use or local-radius violations.",
  "exact_parent_sha": "7cb56dc08db62e77512c4b3b2deb8ab75d94c67d",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-BRIDGE-HETEROGENEOUS-DEGRADATION-SHIFT-001",
    "classification": "supported",
    "qualification_run_id": "37001241966",
    "scientific_claim": "Frozen monitor/repair policy recovered all 24 synthetic heterogeneous degradations under distribution shift with exact retain/revert behavior."
  },
  "authority": "synthetic/software research on immutable repo-owned UTF-8 bytes only; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, or capacity authority changes",
  "changed_paths": [
    "research/experiments/exp-dgr-real-utf8-developmental-specialization-001.ice",
    "research/applications/plane/exp-dgr-real-utf8-developmental-specialization-001.py",
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json"
  ],
  "corpus": {
    "encoding": "identity file bytes; no UTF decoding, normalization, tokenizer, vocabulary, inserted separator, boundary label, or remapping",
    "training": [
      {
        "path": "research/architecture/measurement-framework.ice",
        "sha": "6374fc3c39ee821c8f9d565bb7de0875c07d5cdc",
        "size_bytes": 10040
      },
      {
        "path": "research/architecture/structural-plasticity.ice",
        "sha": "d2d75b4ed60e0c112de5202ba31848b15081e0cb",
        "size_bytes": 9550
      },
      {
        "path": "research/architecture/developmental-substrate-v0.2.ice",
        "sha": "52d6e87e2339bdf586c33da22470e38a9ca27785",
        "size_bytes": 8448
      },
      {
        "path": "research/architecture/yggdrasil-north-star.ice",
        "sha": "84358ec54c0e7eba6b6f830e0b4d2755920281cb",
        "size_bytes": 8411
      }
    ],
    "evaluation": [
      {
        "path": "research/architecture/functional-regeneration.ice",
        "sha": "21e01507a9d93e4bfb92b2f79109c2cd94bf8216",
        "size_bytes": 8090
      },
      {
        "path": "research/architecture/ancestor-inheritance.ice",
        "sha": "0603b3ed2cb8e67f95f8596883594d3deb37aa8f",
        "size_bytes": 6565
      }
    ],
    "file_boundary_policy": "raw context resets at each file boundary; no boundary byte is inserted",
    "contamination_rule": "evaluation bytes do not contribute to baseline counts, motif candidate statistics, differentiation, candidate ranking, or thresholds"
  },
  "substrate": {
    "cell_count": 16,
    "topology": "fixed ring",
    "operation": "DIFFERENTIATE only",
    "local_assignment_radius": 2,
    "home_hash": "h=(3*b0+5*b1+7*b2+11*b3) mod 16",
    "candidate_evidence": "occurrence count and 256-way immediate-successor counts for every four-byte window in training files",
    "candidate_filter": "occurrence >=12 and best-successor fraction >=0.60",
    "ranking": "descending best-successor count, then descending consistency, then descending total occurrence, then lexicographic four-byte key",
    "differentiation": "scan ranked candidates; for each unassigned key, choose nearest generic cell within ring distance <=2 of its home, tie by lower distance then lower index; stop when no generic cells remain or candidates are exhausted",
    "learned_cell_state": "one four-byte key + learned best successor + frozen successor count histogram metadata",
    "capacity_growth": false
  },
  "baseline": {
    "model": "256x256 previous-byte successor count table learned only from training files",
    "prediction": "argmax successor for previous byte, lowest-byte tie break",
    "purpose": "matched raw-byte generic prediction baseline"
  },
  "evaluation": {
    "specialized_prediction": "when current four-byte context exactly matches a differentiated cell reachable within home±2, use that cell's learned best successor; otherwise use previous-byte baseline",
    "covered_position": "next-byte position whose preceding four bytes match a differentiated cell",
    "covered_accuracy_gain": "specialized top-1 accuracy minus baseline top-1 accuracy restricted to covered positions",
    "transferred_motif_count": "number of distinct differentiated keys observed at least once in the held-out file",
    "effective_event_reduction": "greedily replace each non-overlapping occurrence of a differentiated four-byte key by one internal event; reduction=(raw byte events - specialized events)/raw byte events",
    "per_file_reporting": true
  },
  "controls": [
    "No evaluator file identity or outcome enters differentiation.",
    "No tokenizer, symbolic motif label, record boundary, external embedding, or external model is used.",
    "Cell count remains exactly sixteen and no replication/merge/hibernation/wake/repair operation is permitted.",
    "All differentiated cell assignments must lie within ring distance two of deterministic home.",
    "Held-out evaluation is read-only; no adaptation or repair occurs."
  ],
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
      "differentiated_cell_count",
      ">=",
      8
    ],
    [
      "maximum_differentiated_cell_count",
      "<=",
      16
    ],
    [
      "minimum_transferred_motif_count_per_eval_file",
      ">=",
      6
    ],
    [
      "minimum_eval_covered_position_fraction",
      ">=",
      0.01
    ],
    [
      "minimum_eval_covered_accuracy_gain",
      ">=",
      0.1
    ],
    [
      "minimum_effective_event_reduction_fraction",
      ">=",
      0.005
    ],
    [
      "maximum_final_cell_count",
      "==",
      16
    ],
    [
      "minimum_final_cell_count",
      "==",
      16
    ],
    [
      "local_assignment_radius_violation_count",
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
      "invalid_byte_rows",
      "==",
      0
    ],
    [
      "counter_overflow_rows",
      "==",
      0
    ]
  ],
  "validity_criteria": [
    "Exact parent, North Star SHA-256, prior evidence identity, and six Git blob identities match.",
    "Training/evaluation blob sets are disjoint and all bytes are consumed exactly as stored.",
    "Evaluation blobs do not contribute to baseline, candidate statistics, ranking, or differentiation.",
    "Every differentiated key satisfies the frozen occurrence/consistency filter and local assignment rule.",
    "Cell count remains exactly sixteen; no capacity growth or other developmental operation occurs.",
    "All metrics are finite and source emits yggdrasil.research-scientific-result.v1 with exact experiment identity.",
    "Two duplicate executions from identical inputs must be byte-identical before evidence sealing."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all sixteen frozen metric thresholds pass.",
    "mixed": "Validity passes and motif specialization improves covered held-out prediction on both files, but at least one transfer-count, coverage, event-reduction, or capacity threshold fails.",
    "negative": "Validity passes but minimum held-out covered accuracy gain is <=0 or fewer than four learned motifs transfer to either held-out file.",
    "incomplete": "Environmental or compute interruption prevents complete six-file execution.",
    "invalid": "Blob identity, train/eval isolation, raw-byte identity, deterministic differentiation, local-radius, fixed-capacity, finiteness, or qualification criteria fail."
  },
  "no_post_result_tuning_rule": "After any primary or diagnostic output is observed, do not alter files, blob identities, candidate thresholds, ranking, home hash, local radius, cell count, baseline, prediction rule, metrics, thresholds, aggregation, or classification under this experiment identifier."
}
