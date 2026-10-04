{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-GENERALIZATION-ATTRIBUTION-067",
  "program": "Yggdrasil attribution of 066 third-manifest generalization invalidity",
  "question": "Is the 066 invalid result fully explained by failure of the literal retained row/context contract to exist on the third manifest—specifically one missing retained-row donor and four structurally incompatible gate contexts—rather than source, authority, capacity, or execution defects?",
  "hypothesis": "Replay 066 byte-identically on the same third manifest and preserve its original invalid classification inputs. Add attribution-only interpretation: supported if source/manifest/base identities, schedules, packet budget, history accounting, heldout-selection boundary, 16/7/9 capacity, deterministic replay and execution authority all remain clean; original retained_memory_donor_missing_count==1; original gate_context_incompatible_schedule_count==4; original invalid_evaluation_rows==1; and no candidate reserved-key, required-union, state-capacity, matching, capacity-growth, row-mutation, tokenizer or external-model violations occur. This experiment does not repair or reinterpret 066; it identifies the bounded cause of its invalidity.",
  "exact_parent_sha": "e5b3d88ba4b1a5a27341109681e59ff6d7054e6e",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-context-generalization-attribution-r1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INDEXED-COLLATERAL-GENERALIZATION-066",
    "github_run_id": 37164105991,
    "classification": "invalid",
    "validity_pass": false,
    "observation": {
      "source_identity_mismatch_count": 0,
      "transfer_manifest_identity_mismatch_count": 0,
      "base_training_identity_mismatch_count": 0,
      "gate_use_schedule_count": 0,
      "gate_noop_schedule_count": 4,
      "gate_context_incompatible_schedule_count": 4,
      "retained_memory_donor_missing_count": 1,
      "candidate_reserved_key_missing_count": 0,
      "candidate_required_union_over_capacity_count": 0,
      "candidate_state_capacity_failure_count": 0,
      "preserved_state_structure_count_min": 16,
      "active_structure_count_min": 7,
      "retained_structure_count_min": 9,
      "capacity_growth_event_count": 0,
      "invalid_evaluation_rows": 1
    }
  },
  "external_manifest": {
    "sha256": "e46907e74ce92564bab657afc8d28b1a39b269bac88fb9b21092716c7ff53cb7",
    "source_count": 3,
    "effective_total_bytes": 57272
  },
  "external_authority": {
    "ckb_plane_main_sha": "2518306c74ff426278f31b1199f8ad9891299d14",
    "manifest_sha256": "e46907e74ce92564bab657afc8d28b1a39b269bac88fb9b21092716c7ff53cb7",
    "research_decision_required": "READY_RESEARCH",
    "external_model_calls": false,
    "persistent_corpus": false,
    "production_authority": false
  },
  "frozen_reuse": {
    "implementation_behavior": "byte-identical 066 replay; attribution wrapper only",
    "retained_memory_key": [
      10,
      32,
      32,
      32
    ],
    "gate_policy": "byte-identical 066",
    "source_manifest": "byte-identical 066 third manifest",
    "schedules": [
      "A-C-B",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "packets": 12,
    "capacity": "16 total / 7 active / 9 retained"
  },
  "classification_rules": {
    "supported": "replay is deterministic; source/authority/capacity invariants are clean; donor_missing==1; gate_context_incompatible==4; original invalid rows==1; all other structural invalid-source counters are zero",
    "mixed": "replay is deterministic and donor/context incompatibility contributes, but at least one additional structural invalid-source counter is nonzero",
    "negative": "replay is deterministic and donor/context incompatibility does not account for the 066 invalidity",
    "invalid": "replay diverges from 066, source/authority identities fail, or attribution changes 066 behavior"
  },
  "no_post_result_tuning_rule": "Do not alter 066 sources, retained key, gate, donor policy, schedules, packets, capacity, original invalid counters, attribution predicates, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-ROLE-TRANSFER-068",
    "intent": "test whether a training-only content/role-derived retained row can replace literal byte-key identity across manifests without increasing capacity or using heldout labels"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-GENERALIZATION-ATTRIBUTION-068",
    "intent": "isolate any remaining validity source before changing retained-memory semantics"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-context-generalization-attribution-067.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-generalization-attribution-067.py",
    ".github/workflows/external-cumulative-dependent-pipeline-context-generalization-attribution-067.yml"
  ]
}
