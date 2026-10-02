{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-CROSS-DOMAIN-FIRST-HALF-ADAPTATION-012",
  "program": "DG1 real-byte adaptive granularity",
  "question": "On the three immutable Track-A files where the frozen architecture-trained phenotype failed cross-domain transfer in experiment 011, does bounded adaptation using only each file's first half restore positive second-half prediction benefit while retaining the qualified seven-active/nine-retained fixed-capacity partition?",
  "hypothesis": "For each file independently, rebuilding the unchanged sixteen-cell learner from the four frozen architecture training blobs plus only that file's first half will make the adapted full phenotype's second-half incremental-correct count positive and greater than the frozen full control, while first-half error-guided selection retains at least 70% of adapted-full benefit with exactly seven active and nine byte-exact retained records, positive covered-position accuracy gain, no second-half access, and no capacity growth.",
  "exact_parent_sha": "54966e69021acfd3eeac09a65756cacbaedbfdff",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-SEVEN-ACTIVE-CROSS-DOMAIN-SHIFT-011",
    "classification": "negative-by-frozen-rules",
    "qualification_run_id": "37053573819",
    "result_sha256": "fdd73ae47364338cf11fa2410033be2e8f438ed0c71314ff2870c04ddc15283b",
    "observation": "The six-cycle fresh Track-A evaluation preserved exact seven-active/nine-retained state, deterministic revisits, and cross-file activation changes, but the full frozen phenotype had a minimum incremental-correct count of -2 and minimum covered-position accuracy gain of 0.0. Under the frozen 011 classification rules, non-positive full-reference benefit on any fresh file is negative evidence. Whether bounded in-domain adaptation can restore benefit is unknown."
  },
  "authority": "synthetic research-only evaluation on immutable repo-owned bytes; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": [
    "research/experiments/exp-dgr-real-utf8-cross-domain-first-half-adaptation-012.ice",
    "research/applications/plane/exp-dgr-real-utf8-cross-domain-first-half-adaptation-012.py",
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json"
  ],
  "inputs": {
    "base_training": [
      ["research/architecture/measurement-framework.ice", "6374fc3c39ee821c8f9d565bb7de0875c07d5cdc", 10040],
      ["research/architecture/structural-plasticity.ice", "d2d75b4ed60e0c112de5202ba31848b15081e0cb", 9550],
      ["research/architecture/developmental-substrate-v0.2.ice", "52d6e87e2339bdf586c33da22470e38a9ca27785", 8448],
      ["research/architecture/yggdrasil-north-star.ice", "84358ec54c0e7eba6b6f830e0b4d2755920281cb", 8411]
    ],
    "demand": {
      "A": ["research/applications/track-a/a02-adaptive-transform-service-organism.ice", "2770482f2bd0fcffab8b00d206c54ae81f3ae7a1", 21855],
      "B": ["research/applications/track-a/a03-fixa-dynamic-partition-remerge-alignment.ice", "ea322d9b33044d9c0442df460fc2b354b2d4830b", 11293],
      "C": ["research/applications/track-a/a03-heldout-adaptive-generalization.ice", "fdb9b8c908ed45e075fdb39ac578c0e3c79edce5", 28605]
    },
    "encoding": "identity file bytes; no UTF decoding, normalization, tokenizer, vocabulary, separator, boundary label, or remapping",
    "split": "each demand blob is split at floor(raw_byte_length/2), with the raw four-byte context reset at the split",
    "reuse_disclosure": "All three demand files and their frozen-phenotype outcomes were observed in experiment 011. This is a preregistered within-lineage adaptation diagnostic, not a fresh-corpus generalization claim.",
    "contamination_rule": "For each independent file arm, only that file's first half may augment learner fitting and select activation. Its second half remains inaccessible until the adapted learner and active set are frozen. No bytes from either half of either other demand file may enter that file's arm."
  },
  "frozen_reuse": {
    "learner": "byte-identical previous-byte baseline, four-byte candidate statistics, occurrence>=12, consistency>=0.60, utility ranking, home hash, radius two, and sixteen-cell development from the qualified lineage",
    "selector": "byte-identical first-half per-motif incremental-correct contribution with descending adapted training utility then raw-key tie breaks",
    "records": "byte-identical six-byte record containing original cell index, four-byte motif key, and frozen successor",
    "metrics": "byte-identical incremental-correct, covered-position accuracy, and retained-benefit definitions from experiments 005-011"
  },
  "arms": {
    "frozen_full_control": "the unchanged sixteen-motif architecture-trained phenotype from experiment 011, evaluated on the same second-half bytes",
    "adapted_full_reference": "an independently rebuilt sixteen-motif phenotype trained on the four base blobs plus only the current file's first half",
    "adapted_seven_primary": "top seven adapted motifs selected by current-file first-half incremental-correct contribution, then adapted training utility, then raw key; the other nine adapted records are retained exactly"
  },
  "seeds": {
    "randomness": "none",
    "seed_list": [],
    "determinism": "all fitting, rankings, splits, and tie breaks are fully specified; two complete executions must be byte-identical"
  },
  "budgets": {
    "base_training_files": 4,
    "demand_files": 3,
    "independent_adaptation_arms": 3,
    "cell_count_per_arm": 16,
    "active_structure_count": 7,
    "retained_structure_count": 9,
    "maximum_source_processes": 1,
    "timeout_seconds": 1800,
    "primary_runs": 2,
    "network_access": false,
    "capacity_growth_events": 0
  },
  "metrics_and_thresholds": [
    ["training_file_identity_mismatch_count", "==", 0],
    ["evaluation_file_identity_mismatch_count", "==", 0],
    ["cross_file_adaptation_access_count", "==", 0],
    ["valid_evaluation_file_count", "==", 3],
    ["minimum_adapted_full_incremental_correct_count", ">", 0],
    ["minimum_adapted_minus_frozen_full_incremental_correct_count", ">", 0],
    ["minimum_primary_active_structure_count", "==", 7],
    ["maximum_primary_active_structure_count", "==", 7],
    ["minimum_primary_retained_structure_count", "==", 9],
    ["maximum_primary_retained_structure_count", "==", 9],
    ["minimum_primary_retained_incremental_correct_fraction", ">=", 0.70],
    ["minimum_eval_covered_accuracy_gain", ">", 0.0],
    ["retained_record_integrity_mismatch_count", "==", 0],
    ["state_partition_mismatch_count", "==", 0],
    ["future_half_selection_access_count", "==", 0],
    ["capacity_growth_event_count", "==", 0],
    ["tokenizer_use_count", "==", 0],
    ["invalid_evaluation_rows", "==", 0]
  ],
  "controls": [
    "Each file's adapted and frozen arms are evaluated on identical second-half bytes with a raw-context reset.",
    "The frozen full control is reconstructed byte-identically to experiment 011 and receives no demand bytes during fitting.",
    "Each adapted arm starts independently from the same four base blobs; no adapted state is carried between files.",
    "The previous-byte baseline remains fitted only on the four base blobs, isolating adaptation to developmental motif state rather than changing the baseline.",
    "The first half is deliberately reused for both bounded motif adaptation and non-oracle activation selection; no claim of independent selection data is made.",
    "All sixteen adapted records remain represented exactly once across the seven active and nine retained partitions.",
    "Cell count remains sixteen; no replicate, merge, repair, prune, external model, tokenizer, network access, or capacity growth is permitted."
  ],
  "validity_criteria": [
    "Exact parent, North Star SHA-256, prior evidence identity, source dependencies, and all seven Git blob identities and sizes match.",
    "Every file is split exactly once before adaptation, and no second-half or cross-file demand byte is accessed while fitting or selecting its arm.",
    "The frozen learner yields exactly sixteen motifs, and every independently adapted learner yields exactly sixteen motifs.",
    "Every adapted primary partition contains exactly seven active and nine retained byte-exact records whose disjoint union equals that arm's sixteen original records.",
    "The baseline is unchanged between frozen and adapted comparisons; only motif candidate statistics and development receive the current first half.",
    "No tokenizer, external model, network access, capacity growth, or state carry between file arms occurs.",
    "All metrics are finite and two duplicate complete executions are byte-identical."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all frozen thresholds pass on all three files.",
    "mixed": "Validity passes and adaptation improves over the frozen full control on every file, but at least one positive-benefit, seven-active retention, or covered-gain threshold fails.",
    "null": "Validity passes but the minimum adapted-minus-frozen improvement is zero while neither arm is worse on any file.",
    "negative": "Validity passes but adaptation is worse than the frozen full control on any file, adapted full benefit is non-positive on at least two files, or seven-active retained benefit is below 0.50 on any file.",
    "incomplete": "Environmental or compute interruption prevents both deterministic executions or all three file arms.",
    "invalid": "Any identity, lineage, split isolation, future-access, cross-file access, partition-integrity, fixed-capacity, finiteness, or qualification criterion fails."
  },
  "stop_conditions": [
    "Stop invalid before scientific evaluation on any identity, lineage, size, dependency, or prior-evidence mismatch.",
    "Stop invalid on second-half or cross-file adaptation access, partition corruption, cell-count drift, capacity growth, non-finite metric, or nondeterministic duplicate output.",
    "Do not stop early for apparent supported, mixed, null, or negative outcomes.",
    "After any output is observed, do not repair or rerun under this experiment identifier."
  ],
  "no_post_result_tuning_rule": "After any primary or diagnostic output is observed, do not alter inputs, splits, adaptation data, baseline isolation, learner, selector, tie breaks, record format, seven-active ceiling, arms, budgets, metrics, thresholds, aggregation, validity, classification, or stop conditions under this experiment identifier."
}
