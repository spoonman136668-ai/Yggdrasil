{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-STATE-CARRY-DEPTH-050",
  "program": "Yggdrasil fixed-capacity five-row inter-cycle state carry",
  "question": "Does the supported six-cycle four-row carry regime remain safe when carried state width increases from four rows to five rows without changing total capacity?",
  "hypothesis": "Replay the exact 36 frozen 049 cases with identical six-cycle horizon, two steps per cycle, orientation-complete guard, rows, cues, selectors, and 0.95 safety floor. Beginning with cycle 1, carry exactly five distinct keys from the immediately preceding cycle's final active partition, ranked by contribution to that final novel cue with utility then key tie-breaks. Reserve all five on the next cycle's first step, fill the remaining two active slots with unchanged 049 ranking, and leave second-step selection byte-identical 049. Exactly 180 first-step episodes receive five-row carry. All 432 safety checks remain at or above 0.95 and all 432 target and 432 partner recoveries remain positive under fixed 16 total / 7 active / 9 retained capacity.",
  "exact_parent_sha": "906d1bd5809d573d7b1c5609aff800dd941bda61",
  "qualification_branch": "research/external-hosted-yggdrasil-cumulative-multirow-state-carry-depth-r4",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-STATE-CARRY-DEPTH-049",
    "github_run_id": "37137812815",
    "classification": "supported",
    "state_carry_application_count": 180,
    "state_carry_width_min": 4,
    "state_carry_width_max": 4,
    "non_target_safety_failure_count": 0,
    "minimum_applicable_non_target_preserved_to_unprotected_fraction": 0.9862600536193029,
    "positive_post_episode_target_recovery_check_count": 432,
    "positive_post_episode_partner_recovery_check_count": 432
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
  "frozen_reuse": {
    "sources": "byte-identical 049 external manifest",
    "base_case_count": 36,
    "reuse_cycles": 6,
    "novel_steps_per_cycle": 2,
    "episode_count": 432,
    "guard_rule": "byte-identical 049 orientation-complete guard",
    "capacity": "16 total / 7 active / 9 retained",
    "row_learning": false,
    "utility_updates": false,
    "protected_key_updates": false
  },
  "state_carry_protocol": {
    "carry_start_cycle": 1,
    "carry_application_count": 180,
    "carry_source": "immediately preceding cycle second-step active partition",
    "carry_key_rule": "top five distinct active keys by contribution to preceding second-step novel cue; tie-break higher utility then key",
    "next_first_step_rule": "reserve all five carried keys then fill remaining active slots using unchanged 049 ranking without duplicates",
    "second_step_rule": "byte-identical 049 selection",
    "carried_state_width": 5,
    "learned_state": false
  },
  "classification_rules": {
    "supported": "Validity passes; all 180 five-row carry applications are accounted, all 432 safety checks meet the 0.95 floor, and all 432 target and 432 partner recoveries are positive.",
    "mixed": "Validity passes and protected recovery remains complete, but one or more non-target safety checks fail.",
    "negative": "Validity passes but any target or partner recovery becomes nonpositive.",
    "invalid": "Any parent, authority, source, carry accounting, carry width/rule, guard identity, frozen-state, capacity, determinism, or heldout-isolation criterion fails."
  },
  "no_post_result_tuning_rule": "Do not alter sources, six-cycle horizon, five-row carry width, carry source/ranking/reservation rule, episode order, novel cue, guard rule/applicability, 0.95 floor, capacity, metrics, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-STATE-CARRY-DEPTH-051",
    "intent": "increase bounded carried state from five rows to six rows while keeping total capacity frozen"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-STATE-CARRY-ATTRIBUTION-051",
    "intent": "attribute the first five-row carry-induced safety or recovery failure before changing carry width or guard"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-multirow-state-carry-depth-050.ice",
    "research/applications/plane/exp-dgr-external-cumulative-multirow-state-carry-depth-050.py",
    ".github/workflows/external-cumulative-multirow-state-carry-depth-050.yml"
  ]
}
