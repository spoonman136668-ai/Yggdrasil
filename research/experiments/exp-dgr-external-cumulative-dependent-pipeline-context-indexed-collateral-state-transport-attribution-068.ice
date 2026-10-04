{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INDEXED-COLLATERAL-STATE-TRANSPORT-ATTRIBUTION-068",
  "program": "Yggdrasil attribution of retained-state transport versus context-gate transfer",
  "question": "When the exact retained row R from 067 is transported into the third-manifest state, does activating that row improve prose collateral independently of the old shared5 context gate?",
  "hypothesis": "Use only the immutable third manifest e46907e74ce92564bab657afc8d28b1a39b269bac88fb9b21092716c7ff53cb7 and the exact retained state materialized by 067: key=[10,32,32,32], best=32, total=112, best_count=112, consistency=1.0, utility=112.0, cell_index=12, map_best=32. Replay the four 066 schedules, 60/40 split, 12 packets, carry6 baseline, dependent/prose/partner scoring and 16 total / 7 active / 9 retained capacity. Compare three frozen training-only variants per schedule: ORIGINAL uses the new-manifest prose_guard7 unchanged; PASSIVE transports R into the 16-row state but keeps ORIGINAL active guard; ACTIVE transports R and, if R is absent from prose_guard7, replaces exactly the lowest-ranked seventh prose-guard row with R. No shared5 requirement is used. Supported attribution requires ACTIVE to produce positive prose collateral in more schedules than PASSIVE, zero partner-collateral failures, no capacity growth, and zero invalid rows. This diagnoses retained-row transport separately from the old context signature and does not promote a new gate.",
  "exact_parent_sha": "61d45c2030e278eaef0aae14ec0d58020f053a45",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-context-indexed-collateral-state-transport-attribution-r1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "materialization": {
      "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INDEXED-COLLATERAL-RETAINED-STATE-MATERIALIZATION-067",
      "github_run_id": 37164473392,
      "classification": "supported",
      "retained_state": {
        "key": [
          10,
          32,
          32,
          32
        ],
        "best": 32,
        "total": 112,
        "best_count": 112,
        "consistency": 1,
        "utility": 112,
        "cell_index": 12,
        "map_best": 32
      }
    },
    "failed_generalization": {
      "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INDEXED-COLLATERAL-GENERALIZATION-066",
      "github_run_id": 37164105991,
      "classification": "invalid",
      "observation": {
        "gate_context_incompatible_schedule_count": 4,
        "retained_memory_donor_missing_count": 1,
        "invalid_evaluation_rows": 1
      }
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
  "retained_state": {
    "schema": "yggdrasil.retained-row-state.v1",
    "key": [
      10,
      32,
      32,
      32
    ],
    "best": 32,
    "total": 112,
    "best_count": 112,
    "consistency": 1,
    "utility": 112,
    "cell_index": 12,
    "map_best": 32,
    "identity_source": "067 supported result"
  },
  "frozen_variants": {
    "original": "new-manifest training-only prose_guard7 unchanged",
    "passive": "transport retained row R into the 16-row state; active guard unchanged",
    "active": "transport R; if R absent from prose_guard7, replace only the lowest-ranked seventh guard row with R; if already present, unchanged",
    "variant_selection_from_results": false
  },
  "frozen_reuse": {
    "schedules": [
      "A-C-B",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "split": "60% training cue / 40% evaluation",
    "future_packets": 12,
    "carry6_baseline": "byte-identical 066",
    "required_union_injection": "byte-identical 066 except immutable transported R can satisfy required state",
    "success_rule": "dependent incremental correct >0 AND technical-prose collateral incremental correct >0 AND partner collateral incremental correct >0",
    "capacity": "16 total / 7 active / 9 retained"
  },
  "classification_rules": {
    "supported": "valid and ACTIVE positive-prose-collateral schedule count exceeds PASSIVE, ACTIVE partner-collateral failure count==0, exact 16/7/9 capacity holds, and invalid rows==0",
    "mixed": "valid and ACTIVE changes prose collateral or packet efficiency relative to PASSIVE but does not meet the supported rule",
    "negative": "valid and transporting/activating R gives no benefit over PASSIVE",
    "invalid": "any parent, authority, third-manifest identity, retained-state identity, variant rule, heldout-selection boundary, deterministic replay, capacity, provenance, or accounting requirement fails"
  },
  "no_post_result_tuning_rule": "Do not alter retained state, third-manifest identities, ORIGINAL/PASSIVE/ACTIVE rules, schedules, split, packets, carry baseline, scoring, 16/7/9 capacity, thresholds, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-NEUTRAL-RETAINED-ROW-GATE-069",
    "intent": "prospectively test a context-neutral training-only gate for transported retained rows before broader cumulative integration"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-RETAINED-STATE-TRANSFER-FACTORIAL-069",
    "intent": "factor whether failure is row payload, activation position, or target-context mismatch without changing capacity"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-context-indexed-collateral-state-transport-attribution-068.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-indexed-collateral-state-transport-attribution-068.py",
    ".github/workflows/external-cumulative-dependent-pipeline-context-indexed-collateral-state-transport-attribution-068.yml"
  ]
}
