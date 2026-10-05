{
  "schema": "yggdrasil.rsi-learned-mechanism-pilot.v1",
  "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-LEARNED-CONSUMER-ARCHITECTURE-092",
  "parent_experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-DEVELOPMENTAL-CONSUMER-ARCHITECTURE-091",
  "parent_sha": "d311a56ea6a838f6025c5b32c3ef01f641e17748",
  "hypothesis": "A bounded learned cognition consumer selected only by historical replay can beat the frozen Y091 alpha=0.5 retained/local developmental blend on sealed unseen contexts while preserving 16 total / 7 active / 9 retained and equal-or-lower effective inference cost.",
  "mutable_interface": "cognition_consumer(retained_state, local_state) -> decision_state",
  "candidate_search": {
    "candidate_count": 4,
    "families": [
      {
        "id": "shared-alpha",
        "learned_scalars": 1,
        "fields": "total,best_count,consistency,utility share alpha"
      },
      {
        "id": "count-score-alpha",
        "learned_scalars": 2,
        "fields": "count fields and score fields use separate alphas"
      },
      {
        "id": "distance-gated-alpha",
        "learned_scalars": 2,
        "fields": "shared alpha plus bounded relation-distance adjustment"
      },
      {
        "id": "fieldwise-alpha",
        "learned_scalars": 4,
        "fields": "one alpha for each continuous decision field"
      }
    ],
    "alpha_grid": [
      0,
      0.25,
      0.5,
      0.75,
      1
    ],
    "training_only_data": "exact Y091 historical transfer/third/fourth contexts; no fifteenth/sixteenth outcome access",
    "selection": "deterministic leave-one-historical-context-out replay score prioritizing clean rescue/no collateral, then first-success latency, minus fixed complexity penalty; lexicographic tie break",
    "failure_history": "all four candidate identities, learned alpha values, historical replay scores, complexity/resource eligibility, and unseen classifications retained",
    "dream_rsi_replay": "sealed prior lineage outcomes may be replayed exactly; no unexplored outcome is invented"
  },
  "decision_state": {
    "continuous_fields": [
      "total",
      "best_count",
      "consistency",
      "utility"
    ],
    "discrete_fields": "best and map_best remain target-local as in Y091; memory addressing is unchanged",
    "persistent_write": false
  },
  "resource_envelope": {
    "capacity": "16 total / 7 active / 9 retained",
    "baseline_effective_consumer_scalars": 1,
    "max_candidate_learned_scalars": 4,
    "support_requires_effective_consumer_scalars_lte_baseline": true,
    "candidate_count": 4,
    "external_model_calls": 0,
    "hidden_memory_growth": false,
    "persistent_state_growth": false,
    "gpu_required": false,
    "home_hardware_policy": "research/roadmap/home-hardware-feasibility.ice remains authoritative",
    "no_material_ram_vram_model_context_agent_compute_growth": true
  },
  "frozen_evaluation": {
    "unseen_contexts": [
      "fifteenth",
      "sixteenth"
    ],
    "candidate_frozen_before_unseen_outcomes": true,
    "supported": "valid; selected candidate is resource-eligible at equal/lower effective inference cost; learned treatment beats Y091 baseline on both unseen contexts with no lost clean rescue, no partner collateral failure, and behavior change on both",
    "mixed": "valid; support false; learned improves both contexts without collateral but is resource-ineligible, or improves exactly one context with no losses/collateral",
    "negative": "valid and neither supported nor mixed",
    "invalid": "identity/capacity/16-7-9/heldout/provenance/determinism/disclosure/persistence/resource-accounting failure"
  },
  "governance": {
    "no_post_result_tuning": true,
    "no_hidden_memory_or_capacity_growth": true,
    "sealed_negatives": true,
    "deterministic_replay": true,
    "no_oracle_or_label_leakage": true,
    "no_accepted_ref_mutation": true,
    "no_live_or_production_authority": true,
    "broad_continual_training": false
  },
  "successors": {
    "supported": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-LEARNED-CONSUMER-DISJOINT-REPLICATION-093",
    "mixed": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-LEARNED-CONSUMER-RESOURCE-ATTRIBUTION-093",
    "negative": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-LEARNED-CONSUMER-COMPONENT-ATTRIBUTION-093"
  }
}
