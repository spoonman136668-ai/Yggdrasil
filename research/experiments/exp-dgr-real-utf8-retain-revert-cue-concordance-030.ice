{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-REAL-UTF8-RETAIN-REVERT-CUE-CONCORDANCE-030",
  "program": "DG1 real-byte adaptive granularity",
  "question": "On the sealed fresh M/N/O lineage from experiment 029, does the frozen reset-context first-half retain/revert cue direction agree with the untouched second-half matched-minimax-versus-frozen collateral direction across all twelve seen-domain evaluations?",
  "hypothesis": "The frozen first-half signed correct-count difference will have the same negative/zero/positive sign as the untouched second-half signed correct-count difference on at least 75% of the twelve evaluations, with no false-retain decisions (nonnegative cue when the second-half difference is negative), while reproducing experiment 029 exactly and preserving all fixed-capacity controls.",
  "exact_parent_sha": "05e936d51065ac513b874c4c5740b29e1d929365",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-RETAIN-REVERT-FRESH-REPLICATION-029",
    "classification": "mixed-by-frozen-rules",
    "qualification_run_id": "38554488872",
    "result_sha256": "ba1eee58766f296bd6d37ca671208ab1976069a143d96248f5af6c0c4eecd048",
    "observation": "Validity and fixed-capacity integrity passed, gated full benefit remained positive, independent retention was 1.0, prior-domain retention exceeded 1.0, ten-active retention was 0.7670807453416149, and pooled parity held; however, zero of twelve gate decisions reverted and minimum gated-minus-frozen second-half benefit was -12. Whether first-half cue direction is a reliable collateral-direction proxy is unresolved."
  },
  "authority": "synthetic research-only diagnostic on immutable repo-owned bytes; no wetware, deployment, external-model inference, scheduler, queue, accepted-ref, credential, production, broker, live-interface, or authority changes",
  "changed_paths": [
    "research/experiments/exp-dgr-real-utf8-retain-revert-cue-concordance-030.ice",
    "research/applications/plane/exp-dgr-real-utf8-retain-revert-cue-concordance-030.py",
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json"
  ],
  "inputs": {
    "base_training": [["research/architecture/measurement-framework.ice", "6374fc3c39ee821c8f9d565bb7de0875c07d5cdc", 10040], ["research/architecture/structural-plasticity.ice", "d2d75b4ed60e0c112de5202ba31848b15081e0cb", 9550], ["research/architecture/developmental-substrate-v0.2.ice", "52d6e87e2339bdf586c33da22470e38a9ca27785", 8448], ["research/architecture/yggdrasil-north-star.ice", "84358ec54c0e7eba6b6f830e0b4d2755920281cb", 8411]],
    "demand": {"M": ["research/applications/track-a/a13-t6-bounded-novel-context-discovery.ice", "c48fe4c06b50e5dc18b0013967d8074b33a17bad", 22805], "N": ["research/applications/track-a/a14-t6-strict-bounded-novel-context-creation.ice", "597a641af867f3f4f4e73b9df14289846516e68b", 32552], "O": ["research/applications/track-a/a15-t7-versioned-context-revision.ice", "113bc2bc8b436555d586655561e92235b5b2f333", 40412]},
    "orders": [["M", "N", "O"], ["O", "N", "M"]],
    "split": "byte-identical experiment-029 floor(raw_byte_length/2) split; first half is adaptation and cue data and untouched second half is evaluation-only; raw four-byte context resets independently",
    "reuse_disclosure": "M/N/O and aggregate experiment-029 outcomes are observed. This is a preregistered within-lineage attribution diagnostic, not a fresh-domain generalization claim.",
    "contamination_rule": "At each stage, fitting, minimax scoring, activation, and cue scoring may use base blobs and only first halves encountered through that stage. Second-half signed differences are computed only after both phenotypes and the cue decision are frozen."
  },
  "arms": {
    "frozen_full_control": "unchanged architecture-only sixteen-motif phenotype from 029",
    "matched_minimax_full_control": "unchanged sixteen-motif matched-minimax phenotype from 029",
    "cue_diagnostic": "for each of the twelve evaluations, compare sign(cue_minimax_correct-cue_frozen_correct) on the reset first half with sign(eval_minimax_correct-eval_frozen_correct) on the untouched reset second half"
  },
  "seeds": {"randomness": "none", "seed_list": [], "determinism": "all identities, orders, splits, fitting, rankings, matching, comparisons, and sign rules are fixed; two complete executions must be byte-identical"},
  "budgets": {"base_training_files": 4, "demand_files": 3, "encounter_orders": 2, "stages_per_order": 3, "diagnostic_rows": 12, "cell_count": 16, "active_structure_count": 10, "retained_structure_count": 6, "primary_runs": 2, "maximum_source_processes": 1, "timeout_seconds": 1800, "network_access": false, "capacity_growth_events": 0},
  "metrics_and_thresholds": [
    ["training_file_identity_mismatch_count", "==", 0], ["evaluation_file_identity_mismatch_count", "==", 0], ["future_stage_adaptation_access_count", "==", 0], ["second_half_adaptation_access_count", "==", 0],
    ["valid_stage_count", "==", 6], ["valid_diagnostic_row_count", "==", 12], ["matched_assignment_failure_count", "==", 0], ["minimum_selected_motif_count", "==", 16], ["maximum_selected_motif_count", "==", 16], ["matched_ineligible_candidate_count", "==", 0],
    ["sealed_minimum_ungated_incremental_correct_count", "==", 64], ["sealed_minimum_ungated_minus_frozen_count", "==", -12], ["sealed_gate_decision_count", "==", 12], ["sealed_gate_revert_count", "==", 0],
    ["cue_eval_sign_concordance_fraction", ">=", 0.75], ["false_retain_count", "==", 0], ["false_revert_count", "==", 0],
    ["zero_cue_negative_eval_count", "==", 0], ["positive_cue_negative_eval_count", "==", 0], ["capacity_growth_event_count", "==", 0], ["invalid_evaluation_rows", "==", 0]
  ],
  "controls": [
    "Import and execute the experiment-029 learner chain without altering its learner, candidate union, pooled successor rule, minimax ranking, matching, gate, splits, orders, or capacity.",
    "Reproduce the sealed 029 aggregate controls before interpreting concordance.",
    "Use a three-way sign function fixed as negative below zero, zero at zero, and positive above zero; no margin, calibration, threshold search, or post-result regrouping is permitted.",
    "Record false retain when cue difference is nonnegative and evaluation difference is negative; record false revert when cue difference is negative and evaluation difference is nonnegative.",
    "Every comparison uses identical bytes and independently reset raw context for frozen and matched-minimax phenotypes.",
    "Cell count, radius, hashes, active ceiling, retained count, budgets, and total capacity remain frozen."
  ],
  "validity_criteria": [
    "Exact parent, North Star, experiment-029 evidence identity, source dependencies, input blobs, and sizes match.",
    "All sealed experiment-029 aggregate controls reproduce exactly, including minimum ungated benefit 64, minimum ungated-minus-frozen -12, twelve decisions, and zero reverts.",
    "Exactly twelve diagnostic rows are evaluated with the frozen three-way sign and false-decision definitions.",
    "No second-half or future-stage bytes enter fitting, ranking, matching, or cue decisions.",
    "Every stage assigns sixteen matched-minimax motifs; no learner, gate, partition, capacity, or corpus change occurs.",
    "All metrics are finite and two complete executions are byte-identical.",
    "No tokenizer, external model, network access, radius widening, capacity growth, or state carry between order arms occurs."
  ],
  "classification_rules": {
    "supported": "Validity passes, sign concordance is at least 0.75, and both false-retain and false-revert counts are zero.",
    "mixed": "Validity passes and sign concordance is at least 0.75, but at least one false retain or false revert occurs.",
    "null": "Validity passes and sign concordance is exactly chance-level 0.50 with both concordant and discordant rows present.",
    "negative": "Validity passes and sign concordance is below 0.75, or any false-retain decision occurs; this is negative evidence for the frozen cue as a collateral-direction proxy.",
    "incomplete": "Compute interruption prevents both deterministic executions, all six stages, or all twelve diagnostic rows.",
    "invalid": "Any identity, isolation, sealed-control reproduction, determinism, matching, fixed-capacity, finiteness, or qualification criterion fails."
  },
  "stop_conditions": [
    "Stop invalid before scientific evaluation on any identity, lineage, dependency, size, or sealed-control mismatch.",
    "Stop invalid on forbidden byte access, matching failure, capacity growth, non-finite metric, or nondeterministic duplicate output.",
    "Do not stop early for apparent supported, mixed, null, or negative outcomes.",
    "After any output is observed, do not repair or rerun under this experiment identifier."
  ],
  "no_post_result_tuning_rule": "After any primary or diagnostic output is observed, do not alter inputs, splits, orders, learner, controls, cue or sign rule, row definitions, budgets, metrics, thresholds, aggregation, validity, classification, or stopping rules under this experiment identifier."
}
