{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-TRANSFER-053",
  "program": "Yggdrasil fixed-capacity dependent-pipeline future-data learning efficiency",
  "question": "After forming and retaining A+B state, does bounded carry reduce the amount of disjoint future C data needed to solve a held-out A+B+C-dependent task versus a no-retained-state baseline under identical fixed capacity and C-data budgets?",
  "hypothesis": "For all six A-B-C source permutations, use only the first half of each source's frozen cue to form historical A+B state. The second half of C's cue is a disjoint future adaptation stream revealed in twelve fixed packets. Compare three frozen mechanisms at every packet: no retained state, six-row retained carry, and seven-row retained carry. All mechanisms see the identical C prefix and use 16 total / 7 active / 9 retained capacity; retained mechanisms may carry only rows selected from the historical A+B state and may not reread A or B cue bytes. The dependent held-out evaluation is a fixed interleave of A, B, and C held-out bytes and success requires positive dependent score plus positive collateral A and B recovery. Supported requires a preregistered retained mechanism to reduce mean packets-to-success by at least one packet versus no-retention and improve at least four of six schedules with zero capacity/authority growth. No candidate is retained by this experiment; a later disjoint transfer replication is required before retention.",
  "exact_parent_sha": "0b0aacf1489fed63dc17b1f371c69accc18bba3c",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-transfer-r1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "portfolio_context": {
    "branch": "research/portfolio-rsi-v1",
    "commit": "0643cb23ac8830c8f130c14cc8385b390d877cdc",
    "role": "advisory-only; primary objective is future-data learning efficiency under fixed budgets"
  },
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-STATE-CARRY-DEPTH-052",
    "github_run_id": "37141594816",
    "classification": "supported",
    "observation": {
      "state_carry_width_min": 7,
      "state_carry_width_max": 7,
      "state_carry_effective_width_min": 7,
      "state_carry_effective_width_max": 7,
      "guard_carry_saturation_conflict_count": 0,
      "non_target_safety_failure_count": 0,
      "positive_post_episode_target_recovery_check_count": 432,
      "positive_post_episode_partner_recovery_check_count": 432
    },
    "interpretation": "Carry depth reached the seven-active-slot ceiling without failure; further width growth is impossible under the fixed capacity, so the next question is whether retained state improves learning efficiency on future disjoint data."
  },
  "external_authority": {
    "ckb_plane_main_sha": "36d99a0257120ede57bb96638660d35014dd529e",
    "manifest_sha256": "75cdb3b97dbb7017299f573d506f07095ed89c06264b29724b78f29c909d4da4",
    "research_decision_required": "READY_RESEARCH",
    "execution_host_policy": "GitHub-hosted compute only; host distinct from LINKDEADKB",
    "external_model_calls": false,
    "persistent_corpus": false,
    "production_authority": false
  },
  "frozen_design": {
    "schedules": [
      "A-B-C",
      "A-C-B",
      "B-A-C",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "historical_split": "first half of frozen source cue for A and B only",
    "future_split": "second half of frozen source cue for C only; divided into twelve deterministic cumulative packets",
    "heldout_task": "fixed nested 32-byte interleave of the three frozen heldout evaluations; no heldout bytes influence state construction, carry selection, eviction, packet order, or stopping",
    "mechanisms": [
      "cold_no_retention",
      "carry6",
      "carry7"
    ],
    "carry_source": "historical A+B state ranked by contribution to fixed A+B derived cue",
    "carry6_rule": "reserve top six historical keys, inject missing keys by evicting lowest current dependent-cue contribution, then fill one active slot by current dependent-cue ranking",
    "carry7_rule": "reserve top seven historical keys, inject missing keys by the same eviction rule, and use all seven as active",
    "cold_rule": "build from C prefix only and select seven active rows by current dependent-cue contribution; no A/B cue reread",
    "success_rule": "dependent heldout incremental correct count > 0 AND A heldout incremental correct count > 0 AND B heldout incremental correct count > 0",
    "failure_packet_value": 13,
    "packet_budget": 12,
    "capacity": "16 total / 7 active / 9 retained for every mechanism"
  },
  "selection_rule": {
    "candidate_selection": "After all frozen schedules complete, choose the retained mechanism with lower mean first-success packet; tie selects carry6. This selection is evidence only and is not retained by 053.",
    "transfer_requirement": "A later preregistered disjoint replication is required before any mechanism can be retained as a learning-efficiency improvement."
  },
  "metrics_and_thresholds": [
    [
      "source_identity_mismatch_count",
      "==",
      0
    ],
    [
      "source_count",
      "==",
      3
    ],
    [
      "total_source_bytes",
      "==",
      57272
    ],
    [
      "base_training_identity_mismatch_count",
      "==",
      0
    ],
    [
      "schedule_count",
      "==",
      6
    ],
    [
      "mechanism_count",
      "==",
      3
    ],
    [
      "packet_budget_per_schedule",
      "==",
      12
    ],
    [
      "history_future_overlap_count",
      "==",
      0
    ],
    [
      "heldout_selection_use_count",
      "==",
      0
    ],
    [
      "selected_candidate_mean_packet_reduction",
      ">=",
      1
    ],
    [
      "selected_candidate_positive_reduction_schedule_count",
      ">=",
      4
    ],
    [
      "selected_candidate_collateral_failure_count",
      "==",
      0
    ],
    [
      "preserved_state_structure_count_min",
      "==",
      16
    ],
    [
      "preserved_state_structure_count_max",
      "==",
      16
    ],
    [
      "active_structure_count_min",
      "==",
      7
    ],
    [
      "active_structure_count_max",
      "==",
      7
    ],
    [
      "retained_structure_count_min",
      "==",
      9
    ],
    [
      "retained_structure_count_max",
      "==",
      9
    ],
    [
      "capacity_growth_event_count",
      "==",
      0
    ],
    [
      "row_mutation_event_count",
      "==",
      0
    ],
    [
      "tokenizer_use_count",
      "==",
      0
    ],
    [
      "external_model_call_count",
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
    "supported": "Validity passes and the preregistered selected retained mechanism reduces mean first-success packet by at least 1.0 versus no-retention, improves at least four of six schedules, and preserves A/B collateral at its successful packet.",
    "mixed": "Validity passes and a retained mechanism has positive mean packet reduction, but the 1.0 mean reduction or four-of-six transfer threshold is not met.",
    "negative": "Validity passes but neither retained mechanism improves mean future-data packets-to-success versus no-retention.",
    "invalid": "Any parent, authority, source, split isolation, packet accounting, heldout isolation, carry identity, capacity, determinism, or provenance criterion fails."
  },
  "no_post_result_tuning_rule": "Do not alter source identities, cue split, twelve-packet future schedule, heldout dependent task, carry6/carry7/cold rules, eviction ranking, success rule, packet failure value, capacity, candidate selection rule, metrics, thresholds, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-TRANSFER-REPLICATION-054",
    "intent": "replicate the selected carry mechanism on a second preregistered disjoint future split/task before retaining any mechanism as a learning-efficiency improvement"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-ATTRIBUTION-054",
    "intent": "attribute whether failure comes from carried-row identity, no free active slots, eviction interference, or lack of cross-domain transfer before changing the mechanism"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-transfer-053.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-transfer-053.py",
    ".github/workflows/external-cumulative-dependent-pipeline-transfer-053.yml"
  ]
}
