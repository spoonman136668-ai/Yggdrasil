{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-CUMULATIVE-FIRST-HALF-ADAPTATION-013",
  "program": "DG1 real-byte adaptive granularity",
  "question": "Across the three immutable Track-A domains from experiment 012, can one fixed sixteen-cell phenotype cumulatively adapt from each encountered first half while retaining positive second-half benefit on every previously encountered domain, independent of forward or reverse encounter order, with only seven motifs active per evaluation?",
  "hypothesis": "In both A-B-C and C-B-A orders, rebuilding one shared phenotype from the four frozen architecture blobs plus all first halves encountered so far will preserve positive incremental-correct benefit and improve over the frozen architecture-only phenotype on every seen domain; domain-specific first-half activation will retain at least 70% of the shared full phenotype's benefit with exactly seven active and nine byte-exact retained records; and the final sixteen-record phenotype will be byte-identical across orders without capacity growth.",
  "exact_parent_sha": "38a051573b5ce11fb72e718652f8fa5802944f85",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-CROSS-DOMAIN-FIRST-HALF-ADAPTATION-012",
    "classification": "supported-by-frozen-rules",
    "qualification_run_id": "37054910449",
    "result_sha256": "0b7941f5e5e3bf3286965cd94e738fd39c18c3f9d2de843dc53ef63f60a34a16",
    "observation": "Independent per-file first-half adaptation produced a minimum adapted-full incremental-correct count of 7, improved over the frozen full phenotype by at least 8, retained at least 0.875 of adapted benefit with seven active motifs, and preserved exact fixed-capacity state. Whether a single cumulatively adapted phenotype preserves earlier domains is unknown."
  },
  "authority": "synthetic research-only evaluation on immutable repo-owned bytes; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": [
    "research/experiments/exp-dgr-real-utf8-cumulative-first-half-adaptation-013.ice",
    "research/applications/plane/exp-dgr-real-utf8-cumulative-first-half-adaptation-013.py",
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
    "orders": [["A", "B", "C"], ["C", "B", "A"]],
    "encoding": "identity file bytes; no UTF decoding, normalization, tokenizer, vocabulary, separator, boundary label, or remapping",
    "split": "each demand blob is split at floor(raw_byte_length/2), with raw four-byte context reset at every second-half evaluation",
    "reuse_disclosure": "All three demand files and their independent-adaptation outcomes were observed in experiments 011-012. This is a preregistered within-lineage cumulative-retention test, not a fresh-corpus generalization claim.",
    "contamination_rule": "At each order stage, fitting may use the four base blobs and only first halves at or before that stage. No second-half byte ever enters fitting or activation selection. A seen domain's own first half may select its active partition; unseen first halves and all unseen second halves remain inaccessible until their stage."
  },
  "frozen_reuse": {
    "learner": "byte-identical previous-byte baseline, four-byte candidate statistics, occurrence>=12, consistency>=0.60, utility ranking, home hash, radius two, and sixteen-cell development from experiments 001-012",
    "selector": "byte-identical per-domain first-half incremental-correct contribution with descending current shared-phenotype training utility then raw-key tie breaks",
    "records": "byte-identical six-byte record containing original cell index, four-byte motif key, and frozen successor",
    "metrics": "byte-identical incremental-correct, covered-position accuracy, and retained-benefit definitions from experiments 005-012"
  },
  "arms": {
    "frozen_full_control": "the unchanged sixteen-motif architecture-trained phenotype from experiments 011-012",
    "independent_adapted_full_control": "for each evaluated domain, the experiment-012 phenotype rebuilt from the four base blobs plus only that domain's first half",
    "cumulative_shared_full_reference": "at each stage, one sixteen-motif phenotype rebuilt from the four base blobs plus every first half encountered in that order through the current stage",
    "cumulative_shared_seven_primary": "for each seen domain, top seven current shared motifs selected only by that domain's first-half contribution, current shared training utility, and raw key; the other nine current records are retained exactly"
  },
  "seeds": {
    "randomness": "none",
    "seed_list": [],
    "determinism": "both encounter orders, fitting, rankings, splits, and tie breaks are fully specified; two complete executions must be byte-identical"
  },
  "budgets": {
    "base_training_files": 4,
    "demand_files": 3,
    "encounter_orders": 2,
    "cumulative_stages_per_order": 3,
    "seen_domain_evaluation_rows": 12,
    "cell_count_per_stage": 16,
    "active_structure_count_per_evaluation": 7,
    "retained_structure_count_per_evaluation": 9,
    "maximum_source_processes": 1,
    "timeout_seconds": 1800,
    "primary_runs": 2,
    "network_access": false,
    "capacity_growth_events": 0
  },
  "metrics_and_thresholds": [
    ["training_file_identity_mismatch_count", "==", 0],
    ["evaluation_file_identity_mismatch_count", "==", 0],
    ["future_stage_adaptation_access_count", "==", 0],
    ["second_half_adaptation_access_count", "==", 0],
    ["valid_stage_count", "==", 6],
    ["valid_seen_domain_evaluation_count", "==", 12],
    ["minimum_shared_full_incremental_correct_count", ">", 0],
    ["minimum_shared_minus_frozen_incremental_correct_count", ">", 0],
    ["minimum_shared_to_independent_incremental_correct_fraction", ">=", 0.70],
    ["minimum_prior_domain_shared_incremental_correct_count", ">", 0],
    ["minimum_prior_domain_shared_to_at_first_encounter_fraction", ">=", 0.70],
    ["final_order_record_mismatch_count", "==", 0],
    ["minimum_primary_active_structure_count", "==", 7],
    ["maximum_primary_active_structure_count", "==", 7],
    ["minimum_primary_retained_structure_count", "==", 9],
    ["maximum_primary_retained_structure_count", "==", 9],
    ["minimum_primary_retained_incremental_correct_fraction", ">=", 0.70],
    ["minimum_eval_covered_accuracy_gain", ">", 0.0],
    ["retained_record_integrity_mismatch_count", "==", 0],
    ["state_partition_mismatch_count", "==", 0],
    ["capacity_growth_event_count", "==", 0],
    ["tokenizer_use_count", "==", 0],
    ["invalid_evaluation_rows", "==", 0]
  ],
  "controls": [
    "Every shared, independent, and frozen arm for a domain is evaluated on identical second-half bytes with a raw-context reset and the unchanged base-trained previous-byte baseline.",
    "Each order begins independently from the same four base blobs; only encountered first halves accumulate in the shared learner.",
    "At every stage, all previously seen domains are reevaluated to measure collateral retention; their second halves never feed back into fitting or selection.",
    "Independent experiment-012 controls are reconstructed per domain and never contribute state to the cumulative arm.",
    "Forward and reverse final learners receive the identical multiset of base blobs and three first halves, making final record equality an order-invariance control.",
    "All sixteen current shared records remain represented exactly once across each seven-active and nine-retained partition.",
    "Cell count remains sixteen; no replicate, merge, repair, prune, external model, tokenizer, network access, or capacity growth is permitted."
  ],
  "validity_criteria": [
    "Exact parent, North Star SHA-256, prior evidence identity, source dependencies, and all seven Git blob identities and sizes match.",
    "Both frozen orders execute exactly three stages and yield exactly twelve seen-domain evaluation rows.",
    "At every stage the shared learner receives exactly the base blobs plus the prefix of first halves for that order, with no future-stage or second-half access.",
    "The frozen, independent, and every cumulative learner yield exactly sixteen motifs.",
    "Every primary partition contains exactly seven active and nine retained byte-exact records whose disjoint union equals that stage's sixteen shared records.",
    "The previous-byte baseline is unchanged across all comparisons; only motif candidate statistics and development receive first-half adaptation data.",
    "The final forward and reverse shared record sets are compared byte-for-byte before scientific classification.",
    "No tokenizer, external model, network access, capacity growth, or state carry between encounter-order arms occurs.",
    "All metrics are finite and two duplicate complete executions are byte-identical."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all twenty-three frozen thresholds pass across both orders and all twelve seen-domain evaluations.",
    "mixed": "Validity passes; shared benefit remains positive on every seen domain and final order records match, but at least one improvement, independent-retention, prior-domain-retention, seven-active-retention, or covered-gain threshold fails.",
    "null": "Validity passes but shared adaptation is within one incremental-correct prediction of the frozen control on every evaluation while never worse than frozen.",
    "negative": "Validity passes but shared benefit is non-positive on any seen domain, shared adaptation is worse than frozen on any evaluation, prior-domain benefit falls below 50% of its first-encounter value, or final phenotype records depend on encounter order.",
    "incomplete": "Environmental or compute interruption prevents both deterministic executions, all six stages, or all twelve seen-domain evaluations.",
    "invalid": "Any identity, lineage, stage isolation, second-half access, order execution, partition-integrity, fixed-capacity, finiteness, or qualification criterion fails."
  },
  "stop_conditions": [
    "Stop invalid before scientific evaluation on any identity, lineage, size, dependency, or prior-evidence mismatch.",
    "Stop invalid on future-stage or second-half adaptation access, partition corruption, cell-count drift, capacity growth, order drift, non-finite metric, or nondeterministic duplicate output.",
    "Do not stop early for apparent supported, mixed, null, or negative outcomes.",
    "After any output is observed, do not repair or rerun under this experiment identifier."
  ],
  "no_post_result_tuning_rule": "After any primary or diagnostic output is observed, do not alter inputs, orders, splits, adaptation prefixes, baseline isolation, learner, selector, tie breaks, record format, seven-active ceiling, arms, budgets, metrics, thresholds, aggregation, validity, classification, or stop conditions under this experiment identifier."
}
