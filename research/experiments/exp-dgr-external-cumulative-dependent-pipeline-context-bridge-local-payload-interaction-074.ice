{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-BRIDGE-LOCAL-PAYLOAD-INTERACTION-074",
  "program": "Yggdrasil corrective RSI tranche: retained-state structural prior × local predictive payload",
  "corrective_tranche_path": "research/experiments/yggdrasil-rsi-corrective-tranche-2026-10-04.ice",
  "question": "Can the accepted retained state become useful when treated as a structural prior that selects a target-local predictive row, rather than by copying its literal key/value payload into the new context?",
  "hypothesis": "Keep the accepted source retained state immutable and derive only a coarse structural signature from its key/best using the preregistered byte classes WHITESPACE={9,10,13,32}, ALPHA={A-Z,a-z}, DIGIT={0-9}, OTHER=all remaining bytes. Rebuild the exact third-manifest canonical B+C target-local donor used in Y70/Y71. Candidate pool is all 16 donor rows whose exact 4-byte key occurs at least once in target technical-prose training and has at least one observed successor. SOURCE_CONDITIONED ranks candidates lexicographically by: (1) local best byte class matches source best byte class, descending; (2) number of key positions whose byte class matches the corresponding source-key byte class, descending; (3) target-prose key occurrence count descending; (4) target-prose argmax successor count descending; (5) donor utility descending; (6) lexicographic key ascending. LOCAL_ONLY ranks the identical eligible pool only by (3)-(6). Freeze both selected rows before evaluation. Each arm activates the exact selected local donor row at rank 7 using byte-identical 068 guard/injection/scoring; unlike Y72/Y73, the active row keeps its own local best/map_best and local payload. The retained source state is never rewritten or inserted. Compare ORIGINAL, SOURCE_CONDITIONED, and LOCAL_ONLY. If both selectors choose the same row, source-specific contribution is not demonstrated and cannot be classified supported.",
  "exact_parent_sha": "925d3245edb83db96a43365775d437dc9595a140",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-context-bridge-local-payload-interaction-r1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "predecessor": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-BRIDGE-PAYLOAD-RECOMBINATION-073",
    "github_run_id": 37168491107,
    "classification": "negative",
    "validity_pass": true,
    "exact_predecessor_sha": "925d3245edb83db96a43365775d437dc9595a140",
    "observation": {
      "coalition_trigger_count": 2,
      "coalition_behavior_change_count": 0,
      "coalition_positive_prose_collateral_schedule_count": 0,
      "coalition_mean_first_success_packet": 13,
      "single_behavior_change_count": 0,
      "source_payload_identity_mismatch_count": 0,
      "bridge_payload_mutation_count": 0,
      "persistent_state_write_count": 0
    },
    "eliminated_hypotheses": [
      "single-trigger sparsity",
      "two-trigger distributed exposure of the literal source payload is sufficient"
    ],
    "strengthened_hypothesis": "retained state may need to guide target-local predictive content rather than be copied literally"
  },
  "cause_effect_trace": {
    "observed_failure": "Y72 and Y73 changed trigger exposure while preserving literal source payload best=32; neither single nor coalition bridge changed behavior.",
    "internal_diagnostic": "source retained key/best structural byte classes plus target-local donor rows and target-prose training occurrences/successors",
    "attributed_cause": "literal source key/value payload is not behaviorally aligned with target prediction dynamics; source information may be useful only as a structural selection prior",
    "candidate_corrective_mechanisms": [
      "source-conditioned local-row selection",
      "local-only matched control"
    ],
    "frozen_candidate_selection_rule": "SOURCE_CONDITIONED and LOCAL_ONLY rankings above; no heldout labels, no post-result row choice",
    "exact_bounded_delta": "selection/recombination only; source state immutable; local donor row payload unchanged; one active row; 16/7/9 capacity unchanged",
    "qualification": "exact third-manifest identity, deterministic double replay, one-shot READY_RESEARCH, source/local selection frozen before evaluation",
    "held_out_result": "evaluation opened only after both selectors and active rows freeze",
    "retain_revert": "all local bridge activation is ephemeral; accepted source retained state remains unchanged regardless of result",
    "next_hypothesis": "if source-conditioned beats both original and local-only, verify retain/revert then replicate on a disjoint context; otherwise reject structural-prior mapping and test whether retained state should be explicitly marked incompatible"
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
    "immutable": true
  },
  "byte_classes": {
    "WHITESPACE": [
      9,
      10,
      13,
      32
    ],
    "ALPHA": "ASCII A-Z or a-z",
    "DIGIT": "ASCII 0-9",
    "OTHER": "all remaining byte values"
  },
  "target_candidate_contract": {
    "donor": "byte-identical Y70/Y71 canonical B+C donor",
    "pool_size_expected": 16,
    "eligibility": "exact 4-byte key occurs >=1 in target technical-prose training and has >=1 observed successor",
    "source_conditioned_ranking": [
      "local best class == source best class descending",
      "matching source/local key byte-class positions descending",
      "target key occurrence count descending",
      "target argmax successor count descending",
      "donor utility descending",
      "lexicographic key ascending"
    ],
    "local_only_ranking": [
      "target key occurrence count descending",
      "target argmax successor count descending",
      "donor utility descending",
      "lexicographic key ascending"
    ],
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
    "activation_position": 7,
    "guard_injection_scoring": "byte-identical 068",
    "capacity": "16 total / 7 active / 9 retained",
    "success_rule": "dependent incremental correct >0 AND technical-prose collateral incremental correct >0 AND partner collateral incremental correct >0"
  },
  "classification_rules": {
    "supported": "valid, selectors choose distinct rows, SOURCE_CONDITIONED improves positive prose collateral over both ORIGINAL and LOCAL_ONLY on at least one schedule, has zero partner collateral failures, and no source mutation/persistence/capacity/authority violation occurs",
    "mixed": "valid and SOURCE_CONDITIONED changes behavior or improves timing but does not beat both controls, or LOCAL_ONLY rescues while SOURCE_CONDITIONED does not",
    "negative": "valid and SOURCE_CONDITIONED is behaviorally equivalent/worse with no source-specific rescue, including the case where both selectors choose the same row",
    "invalid": "any parent, authority, manifest/source identity, source-state identity, byte-class definition, candidate-pool identity, selector ranking, heldout-selection boundary, local-row payload identity, deterministic replay, capacity, provenance or accounting requirement fails"
  },
  "no_post_result_tuning_rule": "Do not alter source state, byte classes, candidate eligibility, either ranking, activation rank, schedules, split, packet count, scoring, 16/7/9 capacity, classification or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-STRUCTURAL-PRIOR-RETAIN-REVERT-075",
    "intent": "verify source-conditioned local bridge retain/revert and then repeat unchanged on a disjoint context before retention eligibility"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-RETAINED-STATE-INCOMPATIBILITY-GATE-075",
    "intent": "test whether training-only compatibility diagnosis should reject this retained state before activation rather than force reuse"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-context-bridge-local-payload-interaction-074.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-bridge-local-payload-interaction-074.py",
    ".github/workflows/external-cumulative-dependent-pipeline-context-bridge-local-payload-interaction-074.yml"
  ]
}
