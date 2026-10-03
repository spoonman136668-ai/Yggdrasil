{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INDEXED-COLLATERAL-RETAIN-REVERT-065",
  "program": "Yggdrasil bounded retain/revert verification for context-indexed collateral memory",
  "question": "Can the context-indexed retained row supported by 064 be admitted into a bounded research candidate state only when it reproduces the frozen 064 success contract, while a causally insufficient same-budget alternate is deterministically rejected and byte-exactly reverted?",
  "hypothesis": "Replay the exact 064 experiment twice from the same frozen research-state snapshot and same c79f09... transfer manifest. WRONG candidate replaces retained key R=[10,32,32,32] with the already-tested other BC-specific row W=[97,116,105,111], preserving one retained-row slot, gate rules, donor source, 16/7/9 capacity, schedules, packets, scoring, thresholds and all other budgets. CORRECT candidate uses R exactly. Evaluate WRONG first using only the frozen 064 supported-contract metrics; it must fail and trigger byte-exact rollback to the pre-candidate snapshot. Only after rollback evaluate CORRECT; it must reproduce the 064 supported contract and be retained as a research-only candidate state. No filesystem persistence, accepted-ref mutation, production state, runtime activation, or later-manifest generalization is authorized.",
  "exact_parent_sha": "b662b6321be15fe965f694092d637350201fd750",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-context-indexed-collateral-retain-revert-r1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INDEXED-COLLATERAL-COALITION-064",
    "github_run_id": 37163029186,
    "classification": "supported",
    "validity_pass": true,
    "observation": {
      "gate_use_schedule_count": 2,
      "gate_noop_schedule_count": 2,
      "candidate_mean_packet_reduction": 2,
      "candidate_positive_reduction_schedule_count": 2,
      "candidate_schedule_slower_than_baseline_count": 0,
      "candidate_positive_prose_collateral_schedule_count": 4,
      "candidate_partner_collateral_failure_count": 0,
      "invalid_evaluation_rows": 0
    },
    "causal_attribution": {
      "source_experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-STATE-COMPATIBILITY-ATTRIBUTION-063",
      "correct_retained_key": [
        10,
        32,
        32,
        32
      ],
      "wrong_same_budget_key": [
        97,
        116,
        105,
        111
      ],
      "basis": "063 showed all rescuing variants contained R and tested variants lacking R failed; W is the other BC-specific row and is insufficient without R"
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
  "frozen_candidates": {
    "pre_candidate_state": {
      "retained_key": [
        10,
        32,
        32,
        32
      ],
      "state_scope": "ephemeral research descriptor only"
    },
    "wrong": {
      "retained_key": [
        97,
        116,
        105,
        111
      ],
      "retained_row_slots": 1,
      "source": "063 preregistered context-specific pool"
    },
    "correct": {
      "retained_key": [
        10,
        32,
        32,
        32
      ],
      "retained_row_slots": 1,
      "source": "064 frozen retained memory key"
    },
    "order": "wrong first; correct only after verified rollback",
    "rollback": "restore byte-exact serialized pre-candidate research descriptor before correct trial"
  },
  "frozen_reuse": {
    "implementation": "import and replay 064 with only RETAINED_KEY substituted per candidate",
    "sources": "byte-identical 064 transfer manifest",
    "schedules": [
      "A-C-B",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "packets": 12,
    "gate_rules": "byte-identical 064",
    "donor_source": "byte-identical 064 B+C training-only donor",
    "success_rule": "byte-identical 064",
    "capacity": "16 total / 7 active / 9 retained"
  },
  "retain_policy": {
    "observables": "064 frozen aggregate validity and success-contract metrics only",
    "supported_contract": [
      "gate_use_schedule_count==2",
      "gate_noop_schedule_count==2",
      "retained_memory_donor_missing_count==0",
      "candidate_reserved_key_missing_count==0",
      "candidate_positive_prose_collateral_schedule_count==4",
      "candidate_partner_collateral_failure_count==0",
      "candidate_schedule_slower_than_baseline_count==0",
      "candidate_mean_packet_reduction>=1",
      "preserved_state_structure_count_min==16",
      "active_structure_count_min==7",
      "retained_structure_count_min==9",
      "capacity_growth_event_count==0",
      "invalid_evaluation_rows==0"
    ],
    "retain_if": "all frozen 064 supported-contract predicates pass",
    "revert_otherwise": "restore byte-exact pre-candidate research descriptor"
  },
  "metrics_and_thresholds": [
    [
      "wrong_candidate_retain_count",
      "==",
      0
    ],
    [
      "wrong_candidate_revert_count",
      "==",
      1
    ],
    [
      "rollback_snapshot_mismatch_count",
      "==",
      0
    ],
    [
      "correct_candidate_retain_count",
      "==",
      1
    ],
    [
      "correct_candidate_revert_count",
      "==",
      0
    ],
    [
      "correct_result_mismatch_vs_064_contract_count",
      "==",
      0
    ],
    [
      "wrong_and_correct_retained_slot_count",
      "==",
      1
    ],
    [
      "capacity_growth_event_count",
      "==",
      0
    ],
    [
      "persistent_state_write_count",
      "==",
      0
    ],
    [
      "accepted_ref_mutation_count",
      "==",
      0
    ],
    [
      "production_authority_count",
      "==",
      0
    ],
    [
      "invalid_evaluation_rows",
      "==",
      0
    ]
  ],
  "classification_rules": {
    "supported": "valid and wrong candidate is reverted, rollback is byte-exact, correct candidate is retained, and all frozen thresholds pass",
    "mixed": "valid and rollback works but the correct candidate fails at least one 064 supported-contract predicate or wrong candidate unexpectedly ties a boundary without being retained",
    "negative": "valid but wrong candidate is retained, rollback is not exact, or correct candidate cannot reproduce the 064 supported contract",
    "invalid": "any parent, authority, source, candidate identity, candidate order, decision-observable isolation, deterministic replay, capacity, rollback accounting, or provenance requirement fails"
  },
  "no_post_result_tuning_rule": "Do not alter R, W, candidate order, 064 code path, transfer sources, gate rules, donor source, 16/7/9 capacity, supported-contract predicates, rollback definition, thresholds, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INDEXED-COLLATERAL-GENERALIZATION-066",
    "intent": "test the retained research candidate on a newly preregistered disjoint manifest; retain/revert success on the current manifest is not a generalization claim"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INDEXED-COLLATERAL-RETAIN-REVERT-ATTRIBUTION-066",
    "intent": "attribute rollback or validation failure before changing the retained row or gate"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-context-indexed-collateral-retain-revert-065.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-indexed-collateral-retain-revert-065.py",
    ".github/workflows/external-cumulative-dependent-pipeline-context-indexed-collateral-retain-revert-065.yml"
  ]
}
