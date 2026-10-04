{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-BRIDGE-PAYLOAD-RECOMBINATION-073",
  "program": "Yggdrasil corrective RSI tranche: distributed context bridge with immutable retained payload",
  "corrective_tranche_path": "research/experiments/yggdrasil-rsi-corrective-tranche-2026-10-04.ice",
  "question": "Did Y72 fail because a retained source payload must be expressed across a small compatible local trigger coalition rather than through one translated key?",
  "hypothesis": "Reuse the exact accepted source retained payload and the exact two Y72 compatible target-local triggers. Create two EPHEMERAL bridge rows, each copying source fields best,total,best_count,consistency,utility,cell_index,map_best unchanged and substituting only its preregistered local trigger key. Freeze COALITION={rank1,rank2}; there is no candidate selection after outcomes. For each schedule, start from the original seven-row prose guard. Keep any coalition trigger already present. For each missing coalition trigger, evict one lowest-priority original guard row from the tail, never evicting a coalition trigger, until room exists; insert missing coalition triggers at the vacated tail positions in compatibility-rank order. Preserve exactly seven unique active rows. Compare ORIGINAL, Y72_SINGLE_SELECTED (rank1 bridge using the byte-identical Y72 rule), and COALITION under the exact 068 scoring, 12 packets, schedules and 16/7/9 capacity. All bridge rows are discarded after execution; source retained state is never mutated or persisted.",
  "exact_parent_sha": "1d6f270f829240b2a361d5482b209587a65cc95d",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-context-bridge-payload-recombination-r1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "predecessor": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-BRIDGE-TRANSLATION-072",
    "github_run_id": 37167925315,
    "classification": "negative",
    "validity_pass": true,
    "decision": "BRIDGE",
    "exact_predecessor_sha": "1d6f270f829240b2a361d5482b209587a65cc95d",
    "observation": {
      "compatible_candidate_count": 2,
      "selected_trigger_rank": 1,
      "selected_compatibility_score": 6.117647058823529,
      "alternate_trigger_rank": 2,
      "alternate_compatibility_score": 1.972972972972973,
      "selected_bridge_behavior_change_count": 0,
      "alternate_bridge_behavior_change_count": 0,
      "selected_positive_prose_collateral_schedule_count": 0,
      "alternate_positive_prose_collateral_schedule_count": 0,
      "bridge_payload_mutation_count": 0,
      "persistent_state_write_count": 0
    },
    "eliminated_hypothesis": "one key-only local trigger is sufficient to make the accepted source payload useful",
    "strengthened_hypothesis": "context compatibility may require distributed local triggering/recombination while the retained source payload remains immutable"
  },
  "cause_effect_trace": {
    "observed_failure": "Both Y72 single-trigger bridges were compatible by training-only criteria yet produced zero behavior change and zero prose-collateral rescue.",
    "internal_diagnostic": "two target-local keys independently agree with source best=32 and source map_best=32 but cover distinct target-context motifs",
    "attributed_cause": "single-trigger bridge may be too sparse to expose retained payload in the target context",
    "candidate_corrective_mechanisms": [
      "fixed two-trigger compatible coalition carrying the same immutable source payload",
      "mandatory revert to original when coalition does not help"
    ],
    "frozen_candidate_selection_rule": "use both and only the two already-sealed Y72 compatible triggers; no outcome-based selection",
    "exact_bounded_delta": "one additional ephemeral bridge row relative to Y72 single-trigger arm; active capacity remains 7 and total state remains 16",
    "qualification": "deterministic double replay; exact Y72 trigger/source-state identity; one-shot research authority; no persistent state write",
    "held_out_result": "evaluation used only after coalition membership and guard construction are frozen",
    "retain_revert": "coalition is always discarded after the run; negative/mixed result leaves accepted source retained state unchanged",
    "next_hypothesis": "if coalition rescues, verify bridge retain/revert and then replicate on a disjoint context; otherwise move to bounded source/local payload interaction rather than more key-count expansion"
  },
  "source_retained_state": {
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
    "persistent_source_mutation_allowed": false
  },
  "frozen_triggers": [
    {
      "rank": 1,
      "key": [
        32,
        116,
        104,
        101
      ],
      "compatibility_score": 6.117647058823529
    },
    {
      "rank": 2,
      "key": [
        32,
        97,
        110,
        100
      ],
      "compatibility_score": 1.972972972972973
    }
  ],
  "coalition_contract": {
    "trigger_count": 2,
    "bridge_row_count": 2,
    "bridge_transform": "copy immutable source payload; key substitution only",
    "source_payload_mutation_count": 0,
    "arbitrary_payload_synthesis_count": 0,
    "persistent_state_write_count": 0,
    "active_guard_capacity": 7,
    "total_state_capacity": 16,
    "retained_state_capacity": 9,
    "eviction_rule": "remove lowest-priority original guard rows from tail, excluding coalition keys, only as needed to admit missing coalition keys",
    "insertion_order": "rank1 then rank2 into vacated tail positions",
    "heldout_selection_count": 0
  },
  "frozen_reuse": {
    "manifest_sha256": "e46907e74ce92564bab657afc8d28b1a39b269bac88fb9b21092716c7ff53cb7",
    "schedules": [
      "A-C-B",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "split": "60% training cue / 40% evaluation",
    "future_packets": 12,
    "baseline_and_scoring": "byte-identical 068/Y72",
    "single_control": "byte-identical selected rank1 Y72 bridge",
    "success_rule": "dependent incremental correct >0 AND technical-prose collateral incremental correct >0 AND partner collateral incremental correct >0"
  },
  "classification_rules": {
    "supported": "valid and COALITION improves positive prose collateral over both ORIGINAL and Y72_SINGLE_SELECTED on at least one schedule, has zero partner collateral failures, changes behavior, preserves source payload identity, and has zero persistence/capacity/authority violations",
    "mixed": "valid and COALITION changes behavior or first-success timing but does not improve positive prose collateral over both controls",
    "negative": "valid and COALITION is behaviorally equivalent to controls or worse with no prose-collateral rescue",
    "invalid": "any parent, authority, source/manifest identity, source-payload identity, trigger identity, coalition membership, guard construction, heldout-selection boundary, deterministic replay, capacity, provenance or accounting requirement fails"
  },
  "no_post_result_tuning_rule": "Do not alter source retained state, two trigger keys, compatibility ordering, coalition membership, guard eviction/insertion rule, schedules, split, packet count, scoring, 16/7/9 capacity, classification or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-BRIDGE-RETAIN-REVERT-074",
    "intent": "verify coalition bridge retain/revert and source-state preservation, then repeat on a disjoint context before retention eligibility"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-BRIDGE-LOCAL-PAYLOAD-INTERACTION-074",
    "intent": "test one preregistered bounded interaction between immutable source payload and local training statistics; do not expand trigger count further"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-context-bridge-payload-recombination-073.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-bridge-payload-recombination-073.py",
    ".github/workflows/external-cumulative-dependent-pipeline-context-bridge-payload-recombination-073.yml"
  ]
}
