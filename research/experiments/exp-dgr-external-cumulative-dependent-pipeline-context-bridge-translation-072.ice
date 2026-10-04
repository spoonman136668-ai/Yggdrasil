{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-BRIDGE-TRANSLATION-072",
  "program": "Yggdrasil corrective RSI tranche: training-only compatibility diagnosis and reversible context bridge",
  "corrective_tranche_path": "research/experiments/yggdrasil-rsi-corrective-tranche-2026-10-04.ice",
  "question": "Can an accepted retained source row become useful in the third-manifest target context when its payload is preserved exactly but activation is mediated by a training-only selected local trigger key through an ephemeral reversible bridge?",
  "hypothesis": "Keep the accepted source retained state from 067 byte-identical: source key [10,32,32,32], best=32,total=112,best_count=112,consistency=1.0,utility=112.0,cell_index=12,map_best=32. Reuse the exact two Y71 target-local candidates in their frozen order. For each candidate compute a training-only compatibility score = key_occurrence_count * (train_argmax_count/key_occurrence_count) * local_donor_consistency, valid only when target train argmax==source best, local donor best==source best, and local map_best==source map_best. Select the highest-scoring compatible trigger before evaluation; lexicographic key breaks exact score ties. Build an EPHEMERAL bridge row by copying every source retained payload field unchanged and substituting only the selected local trigger key; no source-state rewrite and no persistent bridge write. Activate at rank 7 using byte-identical 068 injection/scoring. Also evaluate the other compatible trigger as a preregistered falsification arm, but it cannot replace the selected trigger post hoc. If no compatible trigger exists, freeze REJECT and run original/passive controls only.",
  "exact_parent_sha": "2b1ed36c4858d837b395bb97bd2d0b770eaabb31",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-context-bridge-translation-r1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "predecessor": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-LOCAL-KEY-INDUCTION-FACTORIAL-071",
    "github_run_id": 37166648538,
    "classification": "negative",
    "validity_pass": true,
    "attribution": "NO_RESCUE",
    "exact_predecessor_sha": "2b1ed36c4858d837b395bb97bd2d0b770eaabb31",
    "observation": {
      "candidate_count": 2,
      "activation_position_count": 7,
      "variant_count": 14,
      "behavior_change_cell_count": 0,
      "any_rescue_count": 0,
      "rank1_key": [
        32,
        116,
        104,
        101
      ],
      "rank1_train_occurrence_count": 8,
      "rank1_train_argmax_count": 7,
      "rank2_key": [
        32,
        97,
        110,
        100
      ],
      "rank2_train_occurrence_count": 3,
      "rank2_train_argmax_count": 2
    },
    "eliminated_hypotheses": [
      "wrong local candidate rank",
      "wrong activation position",
      "direct local donor-row reuse is sufficient"
    ],
    "strengthened_hypothesis": "source retained payload may require target-context trigger translation rather than row replacement"
  },
  "cause_effect_trace": {
    "observed_failure": "transported old key is absent in target context; two direct local rows across all seven positions produced no behavior change",
    "internal_diagnostic": "training-only target key occurrence/successor agreement plus exact source retained-state identity",
    "attributed_cause": "trigger/context representation mismatch, not source-row integrity or activation rank",
    "candidate_corrective_mechanisms": [
      "local trigger -> immutable source payload bridge",
      "compatibility-based reject/fallback"
    ],
    "frozen_candidate_selection_rule": "highest training-only compatibility score among the two frozen Y71 candidates; no heldout labels",
    "exact_bounded_delta": "ephemeral key translation only; source payload immutable; 16/7/9 capacity unchanged",
    "qualification": "exact source/manifest identity, deterministic double replay, one-shot READY_RESEARCH, no persistent bridge write",
    "held_out_result": "same sealed third-manifest evaluation used only after trigger selection and bridge construction",
    "retain_revert": "bridge is ephemeral and discarded after run; unsupported bridge is not persisted; source retained state remains unchanged",
    "next_hypothesis": "if selected bridge works, verify bounded retain/revert and then repeat on a disjoint context; otherwise test bounded payload/context recombination rather than more key/position search"
  },
  "source_retained_state": {
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
    "source_experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INDEXED-COLLATERAL-RETAINED-STATE-MATERIALIZATION-067",
    "source_run_id": 37164473392
  },
  "frozen_target_candidates": [
    {
      "rank": 1,
      "key": [
        32,
        116,
        104,
        101
      ],
      "train_occurrence_count": 8,
      "train_argmax_count": 7,
      "local_best": 32,
      "local_map_best": 32,
      "local_consistency": 0.8739495798319328
    },
    {
      "rank": 2,
      "key": [
        32,
        97,
        110,
        100
      ],
      "train_occurrence_count": 3,
      "train_argmax_count": 2,
      "local_best": 32,
      "local_map_best": 32,
      "local_consistency": 0.9864864864864865
    }
  ],
  "compatibility": {
    "score": "train_argmax_count * local_consistency (equivalent to occurrence_count*(argmax_count/occurrence_count)*consistency)",
    "eligibility": "occurrence_count>=1 AND train_argmax_count>=1 AND target_train_argmax==source.best AND local_best==source.best AND local_map_best==source.map_best",
    "selection": "maximum score, lexicographic key tie-break",
    "reject_if_no_eligible": true,
    "heldout_compatibility_use_count": 0
  },
  "bridge_contract": {
    "persistence": "ephemeral only",
    "source_payload_fields_preserved": [
      "best",
      "total",
      "best_count",
      "consistency",
      "utility",
      "cell_index",
      "map_best"
    ],
    "translated_field": "key only",
    "bridge_row_synthesis_allowed": true,
    "arbitrary_payload_synthesis_forbidden": true,
    "persistent_state_write_count": 0,
    "capacity": "16 total / 7 active / 9 retained",
    "activation_position": 7,
    "schedules": [
      "A-C-B",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "future_packets": 12,
    "success_rule": "dependent incremental correct >0 AND technical-prose collateral incremental correct >0 AND partner collateral incremental correct >0"
  },
  "classification_rules": {
    "supported": "valid, selected training-only bridge improves positive prose collateral over ORIGINAL on at least one schedule, selected bridge has zero partner collateral failures, source payload identity is unchanged, and no persistence/capacity/authority violation occurs",
    "mixed": "valid and selected bridge fails rescue but the preregistered alternate bridge rescues, or selected bridge changes behavior without prose-collateral improvement; compatibility mechanism/ranking is informative but not yet successful",
    "negative": "valid and neither compatible bridge changes behavior/usefully improves prose collateral; key-only context translation is insufficient",
    "invalid": "any parent, authority, manifest/source identity, source-payload identity, candidate identity, compatibility calculation, heldout-selection boundary, bridge-field restriction, deterministic replay, capacity, provenance, or accounting requirement fails"
  },
  "no_post_result_tuning_rule": "Do not alter source retained state, candidate keys, compatibility formula/eligibility, selection rule, key-only bridge transform, activation rank, schedules, split, packet count, scoring, 16/7/9 capacity, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-BRIDGE-RETAIN-REVERT-073",
    "intent": "verify bridge retain/revert and source-state preservation, then replicate on a disjoint context before retention eligibility"
  },
  "successor_if_mixed": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-BRIDGE-COMPATIBILITY-ATTRIBUTION-073",
    "intent": "repair compatibility ranking without using heldout labels"
  },
  "successor_if_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-BRIDGE-PAYLOAD-RECOMBINATION-073",
    "intent": "test a preregistered bounded source-payload/local-context recombination while preserving source state and capacity"
  },
  "changed_paths": [
    "research/experiments/yggdrasil-rsi-corrective-tranche-2026-10-04.ice",
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-context-bridge-translation-072.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-bridge-translation-072.py",
    ".github/workflows/external-cumulative-dependent-pipeline-context-bridge-translation-072.yml"
  ]
}
