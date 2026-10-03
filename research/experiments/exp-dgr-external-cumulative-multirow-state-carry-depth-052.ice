{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-STATE-CARRY-DEPTH-052",
  "program": "Yggdrasil fixed-capacity seven-row inter-cycle state-carry saturation boundary",
  "question": "At the fixed seven-active-slot limit, can all seven carried rows coexist with the unchanged orientation-complete guard without safety/recovery loss or a guard/carry compatibility conflict?",
  "hypothesis": "Replay the exact 36 frozen 051 cases with the identical six-cycle horizon, two steps per cycle, rows, cues, selectors, orientation-complete guard, and 0.95 safety floor. Beginning with cycle 1, attempt to carry exactly seven distinct keys from the immediately preceding cycle's final active partition, ranked by contribution to the final novel cue with utility then key tie-breaks. Because active capacity is exactly seven, no free slot remains. If a required guard key is outside the seven carried keys, record a guard/carry saturation conflict before selection and use the preregistered guard-priority fallback: retain the guard plus the top six carried keys in original carry ranking. This fallback is evidence of a saturation boundary and cannot support the full seven-row claim. All capacity remains fixed at 16 total / 7 active / 9 retained.",
  "exact_parent_sha": "2a87ca7de66667083d7ffa4a7d7bce4f6d2c437c",
  "qualification_branch": "research/external-hosted-yggdrasil-cumulative-multirow-state-carry-depth-r6",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "portfolio_context": {
    "branch": "research/portfolio-rsi-v1",
    "commit": "0643cb23ac8830c8f130c14cc8385b390d877cdc",
    "role": "advisory-only; after this frozen saturation test, successor selection prioritizes transfer-efficient learning on disjoint future dependent pipelines"
  },
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-STATE-CARRY-DEPTH-051",
    "github_run_id": "37140629601",
    "classification": "supported",
    "state_carry_application_count": 180,
    "state_carry_width_min": 6,
    "state_carry_width_max": 6,
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
    "sources": "byte-identical 051 external manifest",
    "base_case_count": 36,
    "reuse_cycles": 6,
    "novel_steps_per_cycle": 2,
    "episode_count": 432,
    "guard_rule": "byte-identical 051 orientation-complete guard",
    "capacity": "16 total / 7 active / 9 retained",
    "row_learning": false,
    "utility_updates": false,
    "protected_key_updates": false
  },
  "state_carry_protocol": {
    "carry_start_cycle": 1,
    "carry_attempt_count": 180,
    "carry_source": "immediately preceding cycle second-step active partition",
    "carry_key_rule": "top seven distinct active keys by contribution to preceding second-step novel cue; tie-break higher utility then key",
    "carried_state_width_intended": 7,
    "no_free_active_slot": true,
    "conflict_rule": "if guard applies and guard key is not among seven carried keys, record guard_carry_saturation_conflict_count and select guard plus first six carry keys; do not silently call that full seven-row carry",
    "second_step_rule": "byte-identical 051 selection",
    "learned_state": false
  },
  "classification_rules": {
    "supported": "Validity passes; all 180 seven-row carry attempts have zero guard/carry saturation conflicts, all 432 safety checks meet the 0.95 floor, and all 432 target and partner recoveries are positive.",
    "mixed": "Validity passes and target/partner recovery plus safety remain complete, but one or more guard/carry saturation conflicts require the preregistered guard-priority fallback, establishing a structural saturation boundary.",
    "negative": "Validity passes but any target/partner recovery becomes nonpositive or any non-target safety check fails.",
    "invalid": "Any parent, authority, source, carry accounting, conflict accounting, guard identity, frozen-state, capacity, determinism, or heldout-isolation criterion fails."
  },
  "no_post_result_tuning_rule": "Do not alter sources, horizon, intended seven-row carry width, carry ranking, guard rule, conflict/fallback rule, episode order, 0.95 floor, capacity, metrics, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-TRANSFER-053",
    "intent": "stop increasing carry width at the seven-active-slot ceiling and test whether saturated retained state reduces fixed-budget learning cost on a preregistered disjoint future A→A+B→derived+C pipeline"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-TRANSFER-053",
    "intent": "treat seven-slot saturation/conflict as the carry-depth boundary and test whether the best previously supported bounded carry state improves fixed-budget learning/reuse on a preregistered disjoint future dependent pipeline"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-multirow-state-carry-depth-052.ice",
    "research/applications/plane/exp-dgr-external-cumulative-multirow-state-carry-depth-052.py",
    ".github/workflows/external-cumulative-multirow-state-carry-depth-052.yml"
  ]
}
