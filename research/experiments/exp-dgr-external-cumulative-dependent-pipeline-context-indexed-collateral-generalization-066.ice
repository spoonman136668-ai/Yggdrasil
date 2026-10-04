{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INDEXED-COLLATERAL-GENERALIZATION-066",
  "program": "Yggdrasil disjoint-manifest generalization of retained context-indexed collateral memory",
  "question": "Does the research-only retained row R and training-only context gate supported through 064-065 preserve dependent-pipeline success and collateral capability on a newly admitted third manifest without changing capacity, retained identity, or gate policy?",
  "hypothesis": "Use only the immutable third manifest e46907e74ce92564bab657afc8d28b1a39b269bac88fb9b21092716c7ff53cb7. Replay the exact 064 mechanism: retained row R=[10,32,32,32], shared5, training-only present/absent context gate, B+C training-only retained-row donor, 60/40 source split, four schedules, 12 future packets, carry6 baseline, required-union injection, dependent/prose/partner success rule, and 16 total / 7 active / 9 retained capacity. Gate application is determined only from each new-manifest training history. If R is present in the current prose_guard7, use the guard unchanged; if R is absent and shared5 plus two context-specific rows are present, substitute R for the lower-ranked context-specific row exactly as 064. If that structural precondition is absent on the new manifest, count a gate_context_incompatible_schedule rather than retuning the gate. No evaluation labels, packet outcomes, or 066 results may alter R, shared5, donor policy, or the gate.",
  "exact_parent_sha": "bf572db74dac4b3c76ba845e3e2b0ac3057ac00f",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-context-indexed-collateral-generalization-r1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INDEXED-COLLATERAL-RETAIN-REVERT-065",
    "github_run_id": 37163694364,
    "classification": "supported",
    "validity_pass": true,
    "observation": {
      "wrong_candidate_retain_count": 0,
      "wrong_candidate_revert_count": 1,
      "rollback_snapshot_mismatch_count": 0,
      "correct_candidate_retain_count": 1,
      "correct_candidate_revert_count": 0,
      "capacity_growth_event_count": 0,
      "persistent_state_write_count": 0,
      "invalid_evaluation_rows": 0
    },
    "retained_candidate": {
      "retained_key": [
        10,
        32,
        32,
        32
      ],
      "scope": "research-only ephemeral candidate; no persistence or production authority"
    }
  },
  "external_manifest": {
    "path": "research/experiments/external-future-data-third-manifest-066.json",
    "sha256": "e46907e74ce92564bab657afc8d28b1a39b269bac88fb9b21092716c7ff53cb7",
    "source_count": 3,
    "effective_total_bytes": 57272
  },
  "external_authority": {
    "ckb_plane_main_sha": "2518306c74ff426278f31b1199f8ad9891299d14",
    "manifest_sha256": "e46907e74ce92564bab657afc8d28b1a39b269bac88fb9b21092716c7ff53cb7",
    "research_decision_required": "READY_RESEARCH",
    "execution_host_policy": "GitHub-hosted compute only; host distinct from LINKDEADKB",
    "external_model_calls": false,
    "persistent_corpus": false,
    "production_authority": false
  },
  "frozen_gate": {
    "retained_memory_key": [
      10,
      32,
      32,
      32
    ],
    "shared5": [
      [
        118,
        101,
        108,
        111
      ],
      [
        101,
        118,
        101,
        108
      ],
      [
        100,
        101,
        118,
        101
      ],
      [
        111,
        112,
        109,
        101
      ],
      [
        32,
        32,
        32,
        32
      ]
    ],
    "present_rule": "if R present in training-only prose_guard7, use original guard unchanged",
    "absent_compatible_rule": "if R absent and guard contains shared5 plus exactly two context-specific rows, keep shared5 + highest-ranked context-specific row + R",
    "absent_incompatible_rule": "do not tune or synthesize a new guard; use original guard for measurement and increment gate_context_incompatible_schedule_count",
    "retained_row_source": "training-only B+C donor state on the third manifest",
    "heldout_selection": false
  },
  "frozen_reuse": {
    "schedules": [
      "A-C-B",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "split": "60% training cue / 40% evaluation per source, byte-identical 064 construction",
    "future_packets": 12,
    "carry6_baseline": "byte-identical 064",
    "required_union_injection": "byte-identical 064",
    "success_rule": "dependent incremental correct >0 AND technical-prose collateral incremental correct >0 AND partner collateral incremental correct >0",
    "capacity": "16 total / 7 active / 9 retained"
  },
  "classification_rules": {
    "supported": "valid, gate_context_incompatible_schedule_count==0, all four schedules preserve prose and partner collateral, no schedule is slower than baseline, candidate mean packet reduction >=1, and exact 16/7/9 capacity holds",
    "mixed": "valid and gate structure is compatible with all schedules and full collateral holds, but mean/no-regression packet-efficiency thresholds are not all met",
    "negative": "valid but at least one schedule is gate-context-incompatible or the retained gate loses prose/partner collateral on the third manifest",
    "invalid": "any parent, authority, manifest/source identity, retained-row identity, heldout-selection boundary, deterministic replay, fixed capacity, provenance, or accounting requirement fails"
  },
  "no_post_result_tuning_rule": "Do not alter third-manifest identities, R, shared5, present/absent gate rules, incompatible-context handling, donor source, schedules, 60/40 split, packets, carry baseline, injection, success rule, 16/7/9 capacity, thresholds, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INDEXED-COLLATERAL-MULTIMANIFEST-RETAIN-REVERT-067",
    "intent": "verify bounded retain/revert across both independently supported manifests before integrating the retained context gate into broader cumulative-pipeline experiments"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-GENERALIZATION-ATTRIBUTION-067",
    "intent": "attribute whether failure is gate-context incompatibility, retained-row donor absence, or collateral non-transfer before changing memory or capacity"
  },
  "changed_paths": [
    "research/experiments/external-future-data-third-manifest-066.json",
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-context-indexed-collateral-generalization-066.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-indexed-collateral-generalization-066.py",
    ".github/workflows/external-cumulative-dependent-pipeline-context-indexed-collateral-generalization-066.yml"
  ]
}
