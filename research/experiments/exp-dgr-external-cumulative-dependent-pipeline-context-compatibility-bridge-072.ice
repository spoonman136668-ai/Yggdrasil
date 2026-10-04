{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-COMPATIBILITY-BRIDGE-072",
  "program": "Yggdrasil corrective RSI tranche: compatibility-gated retained-state bridge",
  "corrective_tranche_path": "research/experiments/yggdrasil-rsi-corrective-tranche-2026-10-04.json",
  "question": "Can Yggdrasil diagnose retained-state/target-context incompatibility before activation and use a bounded one-to-many bridge of exact local donor rows to make accepted retained state useful without rewriting that source state?",
  "hypothesis": "Use immutable source retained state R=[10,32,32,32] from 067 with best/map_best=32, total=best_count=112, consistency=1.0, utility=112.0, cell_index=12. Reuse the exact third-manifest target and Y70/Y71 canonical B+C donor. Before evaluation, DIRECT is compatible only if R occurs in target prose training, has an observed successor, and training successor argmax=32. If DIRECT fails, eligible bridge rows are exact canonical donor rows whose key occurs in target prose training, whose training successor argmax=32, and whose donor best/map_best=32. Score eligible rows as occurrence_count * consistency * (best_count/total), rank descending then lexicographic key, and if at least two exist freeze BRIDGE using the top two exact donor rows. Otherwise freeze REJECT. No evaluation bytes or schedule outcomes may influence the decision. During BRIDGE the source retained row stays unchanged and hibernating; the active seven-row guard removes bridge keys from the original guard, preserves the first five remaining original rows, then appends bridge rank1 and rank2. REJECT is byte-equivalent to ORIGINAL. DIRECT uses the byte-identical 068 direct transport construction. Capacity stays 16 total / 7 active / 9 retained.",
  "exact_parent_sha": "9aa8dd8af112890c0ef209b7c980141970483a6a",
  "scientific_predecessor": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-LOCAL-KEY-INDUCTION-FACTORIAL-071",
    "sha": "2b1ed36c4858d837b395bb97bd2d0b770eaabb31",
    "github_run_id": 37166648538,
    "classification": "negative",
    "attribution": "NO_RESCUE",
    "metrics": {
      "candidate_count": 2,
      "variant_count": 14,
      "any_rescue_count": 0,
      "behavior_change_cell_count": 0,
      "invalid_evaluation_rows": 0
    },
    "eliminated_or_weakened_hypothesis": "single local-row identity or activation position is sufficient",
    "strengthened_hypothesis": "transfer requires an explicit target-compatibility representation or bounded multi-key bridge"
  },
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-context-compatibility-bridge-r1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "source_retained_state": {
    "origin_experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INDEXED-COLLATERAL-RETAINED-STATE-MATERIALIZATION-067",
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
    "mutable": false
  },
  "external_manifest": {
    "path": "research/experiments/external-future-data-third-manifest-066.json",
    "sha256": "e46907e74ce92564bab657afc8d28b1a39b269bac88fb9b21092716c7ff53cb7",
    "source_count": 3,
    "effective_total_bytes": 57272
  },
  "external_authority": {
    "ckb_plane_main_sha": "42177636846fadadfa86d894f9a6f69073cae5b4",
    "manifest_sha256": "e46907e74ce92564bab657afc8d28b1a39b269bac88fb9b21092716c7ff53cb7",
    "research_decision_required": "READY_RESEARCH",
    "execution_host_policy": "GitHub-hosted compute only; host distinct from LINKDEADKB",
    "external_model_calls": false,
    "persistent_corpus": false,
    "production_authority": false
  },
  "frozen_compatibility": {
    "direct_rule": "source key occurrence_count>=1 AND successor_observation_count>=1 AND training successor argmax==32",
    "bridge_eligibility": "exact canonical B+C donor row AND local key occurrence_count>=1 AND local training successor argmax==32 AND donor best==32 AND donor map_best==32",
    "bridge_score": "occurrence_count * consistency * (best_count / total)",
    "bridge_rank": "score descending, then lexicographic key ascending",
    "bridge_width": 2,
    "decision_rule": "DIRECT if direct_rule passes; else BRIDGE if >=2 eligible rows; else REJECT",
    "heldout_compatibility_access_count": 0,
    "post_result_decision_change_count": 0
  },
  "frozen_bridge": {
    "source_state_rewrite_count": 0,
    "row_synthesis_count": 0,
    "bridge_rows": "top two exact eligible donor rows only",
    "source_state_behavior": "unchanged and hibernating during BRIDGE",
    "active_guard_rule": "remove bridge keys from original guard; preserve first five remaining original rows; append bridge rank1 then rank2; exactly seven unique rows",
    "reject_rule": "POLICY equals ORIGINAL exactly",
    "direct_rule": "POLICY uses exact 068 direct transport",
    "schedules": [
      "A-C-B",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "split": "60% training cue / 40% evaluation",
    "future_packets": 12,
    "capacity": "16 total / 7 active / 9 retained"
  },
  "cause_effect_trace": {
    "observed_failure": "068 direct transport, 070 local single-row induction, and 071 two-candidate x seven-position factorial all failed to restore prose collateral",
    "internal_diagnostic": "source-key target occurrence plus local donor occurrence/support/consistency and successor agreement",
    "attributed_cause": "retained state lacks a directly compatible target-key representation",
    "candidate_corrective_mechanisms": [
      "DIRECT",
      "one-to-many exact local BRIDGE",
      "REJECT"
    ],
    "frozen_candidate_selection_rule": "training-only compatibility and bridge scoring above",
    "exact_bounded_delta": "one ephemeral compatibility descriptor plus at most two exact local donor rows; source state unchanged; no capacity growth",
    "qualification": "exact source identities, deterministic double run, exact READY_RESEARCH receipt",
    "held_out_result": "evaluation opens only after DIRECT/BRIDGE/REJECT is frozen",
    "retain_revert": "failure or collateral regression rejects bridge and preserves original; support still requires later retain/revert and another disjoint-context replication",
    "next_hypothesis": "if bridge works, verify retain/revert; otherwise attribute bridge width/representation without silent capacity growth"
  },
  "metrics_and_thresholds": [
    [
      "compatibility_decision_count",
      "==",
      1
    ],
    [
      "heldout_compatibility_access_count",
      "==",
      0
    ],
    [
      "post_result_decision_change_count",
      "==",
      0
    ],
    [
      "source_state_rewrite_count",
      "==",
      0
    ],
    [
      "row_synthesis_count",
      "==",
      0
    ],
    [
      "capacity_growth_event_count",
      "==",
      0
    ],
    [
      "policy_partner_collateral_failure_count",
      "==",
      0
    ],
    [
      "policy_nonprose_regression_schedule_count",
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
    "supported": "valid, decision=DIRECT or BRIDGE, POLICY increases positive-prose collateral schedule count over ORIGINAL on >=1 schedule, partner failures=0, nonprose regression schedules=0, source state unchanged, all thresholds pass",
    "mixed": "valid and decision=REJECT (safe incompatibility rejection) or POLICY changes timing/dependent behavior without prose improvement while preserving collateral capability",
    "negative": "valid, DIRECT/BRIDGE activates but fails to improve prose collateral or causes nonprose/partner regression",
    "invalid": "any parent, authority, manifest identity, retained-state identity, compatibility rule, ranking, evaluation isolation, bridge construction, determinism, source-state immutability, capacity, provenance, or accounting requirement fails"
  },
  "rsi_success_for_this_experiment": false,
  "rsi_success_note": "One supported context bridge is not RSI transfer success; it must pass retain/revert and repeat on another disjoint context.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-BRIDGE-RETAIN-REVERT-073",
    "intent": "bounded retain/revert then another disjoint-context replication"
  },
  "successor_if_mixed": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-COMPATIBILITY-REJECTION-ATTRIBUTION-073",
    "intent": "attribute safe rejection/behavior-only change without weakening controls"
  },
  "successor_if_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-BRIDGE-WIDTH-ATTRIBUTION-073",
    "intent": "attribute bounded bridge representation/width failure; capacity remains fixed unless separately preregistered"
  },
  "no_post_result_tuning_rule": "Do not alter source state, target sources, compatibility rules, bridge score/rank/width, decision rule, guard construction, schedules, split, packet count, 16/7/9 capacity, thresholds, classification, or authority after primary output.",
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-context-compatibility-bridge-072.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-compatibility-bridge-072.py",
    ".github/workflows/external-cumulative-dependent-pipeline-context-compatibility-bridge-072.yml"
  ]
}
