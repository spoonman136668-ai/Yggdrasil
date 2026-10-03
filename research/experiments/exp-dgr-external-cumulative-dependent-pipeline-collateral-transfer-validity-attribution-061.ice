{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-TRANSFER-VALIDITY-ATTRIBUTION-061",
  "program": "Yggdrasil transfer-validity attribution after frozen 060 invalid result",
  "question": "Which exact frozen evaluator subsystem accounts for the 26 invalid_evaluation_rows observed in disjoint transfer run 060, without changing the 060 mechanism, data, schedules, capacity, thresholds, or authority?",
  "hypothesis": "Replay the exact 060 computation over the exact c79f09 transfer manifest and add accounting-only counters at every existing invalid_evaluation_rows increment site. The original aggregate invalid_evaluation_rows counter must remain byte-for-byte semantically unchanged and equal the sealed 060 value 26. Attribution counters must sum exactly to the aggregate. A dominant category (>50% of invalid rows) supports a localized transfer-validity boundary; otherwise the invalidity is distributed. This experiment may diagnose but may not repair, suppress, reinterpret, or exclude invalid rows.",
  "exact_parent_sha": "6365ce14268382a2ff757f69d52435ffdaf96302",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-collateral-transfer-validity-attribution-r1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-COALITION-TRANSFER-060",
    "github_run_id": 37161214719,
    "classification": "invalid",
    "validity_pass": false,
    "sealed_metrics": {
      "invalid_evaluation_rows": 26,
      "source_identity_mismatch_count": 0,
      "transfer_manifest_identity_mismatch_count": 0,
      "candidate_k": 7,
      "preserved_state_structure_count_min": 16,
      "preserved_state_structure_count_max": 16,
      "active_structure_count_min": 7,
      "active_structure_count_max": 7,
      "retained_structure_count_min": 9,
      "retained_structure_count_max": 9,
      "candidate_positive_prose_collateral_schedule_count": 4,
      "candidate_mean_packet_reduction": 0
    }
  },
  "external_transfer_manifest_sha256": "c79f09eb3841309b38827ceffee6a14eb87973c8aa2cf817908ed05f10e5c250",
  "external_authority": {
    "ckb_plane_main_sha": "06c3cb723820407bc2db1bd3ec9e46f462059e41",
    "research_decision_required": "READY_RESEARCH",
    "execution_host_policy": "GitHub-hosted compute only; host distinct from LINKDEADKB",
    "external_model_calls": false,
    "persistent_corpus": false,
    "production_authority": false
  },
  "frozen_reuse": {
    "source_prefixes": "byte-identical 060 transfer sources",
    "schedules": "byte-identical 060 four affected schedules",
    "packet_budget_per_schedule": 12,
    "candidate_k": 7,
    "capacity": "16 total / 7 active / 9 retained",
    "mechanism": "byte-identical 060 baseline/candidate construction and scoring",
    "scientific_output_changes": "none; instrumentation/accounting only"
  },
  "attribution_categories": [
    "candidate_stats_overflow",
    "candidate_stats_invalid",
    "develop_radius_violation",
    "state_shape",
    "selection_or_rebuild",
    "derived_or_guard",
    "final_coverage"
  ],
  "classification_rules": {
    "supported": "all identity/capacity/determinism checks pass, aggregate invalid_evaluation_rows exactly equals sealed 060 value 26, attribution counters sum exactly to 26, and one preregistered attribution category accounts for at least 14 rows (>50%)",
    "mixed": "all validity checks pass, attribution counters sum exactly to 26, but no category reaches 14 rows",
    "negative": "instrumented replay does not reproduce the sealed 060 invalid count despite exact identities",
    "invalid": "any authority, source, parent, capacity, deterministic replay, accounting-sum, or instrumentation-only boundary fails"
  },
  "no_post_result_tuning_rule": "Do not alter transfer data, schedules, packets, k=7, capacity, model logic, scoring, success rule, aggregate invalid counter semantics, attribution categories, 14-row dominance threshold, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-TRANSFER-VALIDITY-BOUNDARY-062",
    "intent": "test the localized validity boundary with one preregistered causal perturbation while preserving all scientific controls"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-TRANSFER-VALIDITY-FACTORIAL-062",
    "intent": "factor the distributed or non-reproducing validity sources before any mechanism repair"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-collateral-transfer-validity-attribution-061.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-collateral-transfer-validity-attribution-061.py",
    ".github/workflows/external-cumulative-dependent-pipeline-collateral-transfer-validity-attribution-061.yml"
  ]
}
