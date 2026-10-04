schema: yggdrasil.research-preregistration.v1
experiment_id: EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INVARIANT-SPECIFIC-FACTORIZATION-ATTRIBUTION-087
parent_experiment: EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-EXPLICIT-CONTEXT-KEY-REPRESENTATION-ATTRIBUTION-086
parent_sha: 72acfd0eefc597e98562c5804e41a9f08672619c
preregistered_at_utc: 2026-10-04T20:52:00Z
hypothesis: >
  Y086's negative result may reflect equal weighting of heterogeneous key coordinates rather than
  absence of useful retained-state structure. Split the frozen 4-byte key into two historically
  most-stable coordinates (context-invariant) and two most-variable coordinates (context-specific),
  then retrieve lexicographically by invariant mismatch, specific mismatch, original total Hamming,
  context order, local rank, and lexical key.
frozen_design:
  historical_pool: byte-identical Y079/Y086 17-row full historical pool
  factorization_source: historical transfer/third/fourth pool only
  position_variability: number of distinct byte values at each of the four key coordinates
  invariant_positions: two coordinates with smallest distinct-count, ties by lower coordinate index
  specific_positions: remaining two coordinates
  control: byte-identical Y079 exact 4-byte Hamming retrieval and tie-breaks
  treatment: lexicographic invariant-distance, specific-distance, total 4-byte Hamming, context order, local_rank, lexical key
  target_keys: unchanged SOURCE_CONDITIONED and LOCAL_ONLY
  heldout_outcome_use_before_factorization_freeze: 0
  post_result_factorization_change_count: 0
  capacity: 16 total / 7 active / 9 retained
  persistent_state_write_count: 0
  external_model_calls: 0
candidate_set:
  - EXACT_KEY_ONLY
  - INVARIANT_SPECIFIC_FACTORIZED_KEY
classification_rules:
  supported: valid and factorized retrieval changes a selected row and cleanly rescues where exact control does not, with zero lost control rescue and zero partner collateral
  mixed: valid, support false, but a changed factorized selection improves prose collateral or first-success timing without partner harm
  negative: valid and neither supported nor mixed
  invalid: any frozen historical-pool identity, factorization rule, control retrieval, treatment ordering, target identity, heldout ordering, 16/7/9 capacity, provenance, or accounting rule fails
successors:
  supported: Y088 factorized-key prospective validation
  mixed: Y088 factorized-key disambiguation
  negative: Y088 transition-state factorization attribution
rsi_success: false
codex_usage: DISABLED
production_authority: false
accepted_ref_mutation: false
runtime_launch: false
capacity_change_authorized: false
authority_expansion: false
broker_access: false
ktrade_access: false
