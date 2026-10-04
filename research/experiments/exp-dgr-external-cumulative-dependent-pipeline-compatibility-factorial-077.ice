{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COMPATIBILITY-FACTORIAL-077",
  "program": "Yggdrasil RSI tranche: retained-state compatibility key × payload factorial",
  "question": "On the disjoint fifth target context, is the Y075/Y076 failure caused by target-key selection, retained payload compatibility, or their interaction?",
  "hypothesis": "Y076 showed all six target-local candidate payloads fail clean rescue, so passive support/precision diagnostics cannot discriminate. Freeze two training-only keys before held-out evaluation: the Y075 source-conditioned key and the local-only key. Cross each key with two bounded shadow payload origins: the target-local donor payload for that key and the immutable source-retained payload projected onto that key using the already-established Y073 source-payload projection. The 2×2 factorial can distinguish key-selection, payload-origin, or interaction effects without mutating accepted retained state or operational policy.",
  "exact_parent_sha": "33d54e8ea9f96b73fb4c71d961e665be227e77f7",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-compatibility-factorial-r1",
  "predecessor": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COMPATIBILITY-DIAGNOSTIC-ATTRIBUTION-076",
    "github_run_id": 37192858813,
    "classification": "negative",
    "validity_pass": true,
    "observation": {
      "eligible_candidate_count": 6,
      "clean_rescue_count": 0,
      "non_rescue_count": 6,
      "low_target_support_non_rescue_rate_delta": 0,
      "low_target_precision_non_rescue_rate_delta": 0,
      "successor_mismatch_coverage": 0
    },
    "eliminated_hypothesis": "LOW_TARGET_SUPPORT, SUCCESSOR_MISMATCH, or LOW_TARGET_PRECISION alone discriminates clean rescue on the fifth context",
    "strengthened_hypothesis": "compatibility failure may depend on an interaction between which target key is used and which retained payload is attached to it"
  },
  "cause_effect_trace": {
    "observed_failure": "Y076 shadow-evaluated all six eligible target-local candidate rows; every candidate was a non-rescue, so training-only support and precision flags had no discriminatory outcome variance.",
    "prior_nonredundancy": "Y074 compared source-conditioned versus local key selection while retaining each target row's local payload; Y073 projected immutable source payload onto fixed bridge keys. Neither crossed key selector with payload origin on the Y075/Y076 fifth context.",
    "factorial_factors": {
      "key_selector": [
        "SOURCE_CONDITIONED",
        "LOCAL_ONLY"
      ],
      "payload_origin": [
        "TARGET_LOCAL",
        "SOURCE_RETAINED_PROJECTION"
      ]
    },
    "source_payload_projection": "keep the frozen selected target key but use the immutable source-retained payload fields best,total,best_count,consistency,utility,cell_index,map_best; this is shadow-only and follows the bounded Y073 projection pattern",
    "exact_bounded_delta": "four shadow variants only; no operational gate change, no accepted retained-state mutation, no persistent write, no capacity growth",
    "qualification": "exact fifth-manifest identity, exact Y075/Y076 selectors, exact source state, deterministic double replay, all four variants fixed before held-out/shadow evaluation",
    "retain_revert": "Y077 cannot change operational state. Supported attribution only authorizes a separately preregistered bounded correction.",
    "next_hypothesis": "payload main effect -> test reversible source-payload projection gate; key main effect -> test bounded selector correction; interaction -> test only the supported combination prospectively; no effect -> return to cumulative consolidation/representation mechanism"
  },
  "target_manifest": {
    "path": "research/experiments/external-future-data-fifth-context-manifest-076.json",
    "sha256": "7077d2b72d8954afc24f36b2971393acc11e3b345f7c3521102c20347b9c6171",
    "source_count": 3,
    "effective_total_bytes": 57272
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
  "frozen_reuse": {
    "donor_builder": "byte-identical Y075/Y076 fifth-context donor",
    "split": "60% training cue / 40% evaluation",
    "source_selector": "byte-identical Y075 source_rank",
    "local_selector": "byte-identical Y075 local_rank",
    "source_payload_projection": "Y073-style immutable source payload rebound to frozen target key",
    "schedules": [
      "A-C-B",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "future_packets": 12,
    "activation_position": 7,
    "capacity": "16 total / 7 active / 9 retained"
  },
  "factorial_cells": [
    "SOURCE_CONDITIONED_KEY × TARGET_LOCAL_PAYLOAD",
    "SOURCE_CONDITIONED_KEY × SOURCE_RETAINED_PROJECTION",
    "LOCAL_ONLY_KEY × TARGET_LOCAL_PAYLOAD",
    "LOCAL_ONLY_KEY × SOURCE_RETAINED_PROJECTION"
  ],
  "outcome_definition": {
    "clean_rescue": "active_positive_prose_collateral_schedule_count > original_positive_prose_collateral_schedule_count AND active_partner_collateral_failure_count == 0",
    "behavior_change": "any active-vs-original packet or summary difference",
    "effect_identification": {
      "key_main_effect": "1 iff both payload origins agree within each key and source-key outcome differs from local-key outcome; else 0",
      "payload_main_effect": "1 iff both key selectors agree within each payload origin and source-payload outcome differs from local-payload outcome; else 0",
      "interaction_effect": "1 iff 1-3 of the four cells are clean rescues and neither pure key nor pure payload main-effect pattern holds; else 0"
    }
  },
  "metrics": [
    "variant_count",
    "clean_rescue_count",
    "source_key_clean_rescue_count",
    "local_key_clean_rescue_count",
    "local_payload_clean_rescue_count",
    "source_payload_clean_rescue_count",
    "source_key_local_payload_clean_rescue",
    "source_key_source_payload_clean_rescue",
    "local_key_local_payload_clean_rescue",
    "local_key_source_payload_clean_rescue",
    "key_main_effect",
    "payload_main_effect",
    "interaction_effect",
    "source_state_mutation_count",
    "persistent_state_write_count",
    "heldout_factor_choice_count",
    "capacity_growth_event_count",
    "invalid_evaluation_rows"
  ],
  "classification_rules": {
    "supported": "valid AND clean_rescue_count>=1 AND exactly one of key_main_effect, payload_main_effect, interaction_effect equals 1",
    "mixed": "valid AND clean_rescue_count==4; rescue exists but the factorial does not discriminate key or payload compatibility",
    "negative": "valid AND clean_rescue_count==0",
    "invalid": "any parent, fifth-manifest identity, source-state identity, selector identity, factorial-cell identity, heldout ordering, deterministic replay, capacity, provenance, persistence or accounting requirement fails"
  },
  "rsi_success": false,
  "rsi_success_note": "Y077 is a shadow factorial attribution on an already studied target context; useful retained-state transfer still requires a separately preregistered prospective disjoint-context validation.",
  "no_post_result_tuning_rule": "Do not alter target data, source state, selectors, four factorial cells, source-payload projection, effect-identification logic, activation position, schedules, 16/7/9 capacity, outcome definition, classification, or authority after primary output.",
  "successors": {
    "supported": {
      "contract_id": "yggdrasil-078-factorial-supported-correction",
      "experiment_family": "bounded-correction-078"
    },
    "mixed": {
      "contract_id": "yggdrasil-078-factorial-disambiguation",
      "experiment_family": "factorial-disambiguation-078"
    },
    "negative": {
      "contract_id": "yggdrasil-078-consolidation-representation-attribution",
      "experiment_family": "consolidation-representation-attribution-078"
    }
  },
  "required_authority": {
    "disposition": "READY_RESEARCH",
    "manifest_sha256": "7077d2b72d8954afc24f36b2971393acc11e3b345f7c3521102c20347b9c6171",
    "hosted_compute": true,
    "research_only": true,
    "one_shot": true,
    "external_model_calls": false,
    "persistent_corpus": false,
    "production_authority": false
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-compatibility-factorial-077.ice"
  ]
}
