{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INDEXED-COLLATERAL-RETAINED-STATE-MATERIALIZATION-067",
  "program": "Yggdrasil deterministic materialization of the retained context-indexed row",
  "question": "Can the exact retained row R supported by 064-065 be deterministically serialized from its original training-only B+C donor state so later third-manifest tests can carry the retained research state without re-deriving it from the new manifest?",
  "hypothesis": "Use only the original immutable transfer manifest c79f09eb3841309b38827ceffee6a14eb87973c8aa2cf817908ed05f10e5c250 and the byte-identical 064 B+C rebalanced training-only donor construction. Locate retained key R=[10,32,32,32] in the resulting 16-row matched-minimax state and serialize exactly its row fields required by later injection: key, best successor, total, best_count, consistency, utility, cell_index, plus the specialized-map best value. Run twice and require byte-identical serialized state. This is state materialization only: no new evaluation, gate selection, policy choice, persistence, capacity change, or production authority.",
  "exact_parent_sha": "e5b3d88ba4b1a5a27341109681e59ff6d7054e6e",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-context-indexed-collateral-retained-state-materialization-r1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "supported_source": {
      "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INDEXED-COLLATERAL-RETAIN-REVERT-065",
      "github_run_id": 37163694364,
      "classification": "supported",
      "retained_key": [
        10,
        32,
        32,
        32
      ]
    },
    "failed_generalization": {
      "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INDEXED-COLLATERAL-GENERALIZATION-066",
      "github_run_id": 37164105991,
      "classification": "invalid",
      "observation": {
        "retained_memory_donor_missing_count": 1,
        "gate_context_incompatible_schedule_count": 4,
        "invalid_evaluation_rows": 1
      },
      "interpretation": "066 cannot test transported retained state because it re-derived the retained row from the new manifest and failed before a valid generalization measurement."
    }
  },
  "external_authority": {
    "ckb_plane_main_sha": "2518306c74ff426278f31b1199f8ad9891299d14",
    "manifest_sha256": "c79f09eb3841309b38827ceffee6a14eb87973c8aa2cf817908ed05f10e5c250",
    "research_decision_required": "READY_RESEARCH",
    "execution_host_policy": "GitHub-hosted compute only; host distinct from LINKDEADKB",
    "external_model_calls": false,
    "persistent_corpus": false,
    "production_authority": false
  },
  "frozen_reuse": {
    "source_manifest": "byte-identical 064 original transfer manifest",
    "retained_key": [
      10,
      32,
      32,
      32
    ],
    "donor_domains": [
      "B",
      "C"
    ],
    "split": "60% training cue / 40% evaluation per source",
    "donor_history_rebalancing": "byte-identical 064 rebalanced(B,C)",
    "donor_state_builder": "byte-identical 064 matched-minimax 16-row build",
    "output_fields": [
      "key",
      "best",
      "total",
      "best_count",
      "consistency",
      "utility",
      "cell_index",
      "map_best"
    ],
    "evaluation_use_count": 0,
    "policy_selection_count": 0,
    "capacity": "16 structures unchanged"
  },
  "classification_rules": {
    "supported": "valid, R exists exactly once in donor rows and map, serialized key/map_best/best agree, two executions are byte-identical, and zero persistence/capacity/authority violations occur",
    "negative": "valid but R is absent or serialization cannot reproduce a single exact retained row",
    "invalid": "any parent, authority, source identity, donor construction, output-field contract, deterministic replay, provenance, or accounting requirement fails"
  },
  "no_post_result_tuning_rule": "Do not alter source identities, R, B+C donor construction, split, rebalancing, matched-minimax builder, serialized fields, classification, or authority after output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INDEXED-COLLATERAL-STATE-TRANSPORT-ATTRIBUTION-068",
    "intent": "inject the immutable serialized retained row into the third-manifest state and separately test retained-state usefulness versus old shared5 gate-context transfer"
  },
  "successor_if_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INDEXED-COLLATERAL-STATE-MATERIALIZATION-ATTRIBUTION-068",
    "intent": "attribute why the supported retained candidate cannot be serialized before any new-manifest test"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-context-indexed-collateral-retained-state-materialization-067.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-indexed-collateral-retained-state-materialization-067.py",
    ".github/workflows/external-cumulative-dependent-pipeline-context-indexed-collateral-retained-state-materialization-067.yml"
  ]
}
