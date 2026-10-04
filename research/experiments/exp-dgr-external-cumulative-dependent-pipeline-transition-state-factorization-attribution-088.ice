schema: yggdrasil.research-preregistration.v1
experiment_id: EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-TRANSITION-STATE-FACTORIZATION-ATTRIBUTION-088
parent_experiment: EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INVARIANT-SPECIFIC-FACTORIZATION-ATTRIBUTION-087
parent_sha: 5c22e4c1056bf548c574a4660fcdeca2d49d4169
preregistered_at_utc: 2026-10-04T21:49:00Z
hypothesis: >
  Y087's negative result may mean absolute key-coordinate factorization is insufficient while the
  pattern of state transition remains informative. For each historical row, freeze a four-bit
  transition mask indicating which key coordinates differ from that context's local representative.
  For each fifth-context target selector, freeze its transition mask relative to the other target
  selector before any child outcome is observed. Retrieve first by transition-mask Hamming distance,
  then exact four-byte key Hamming distance, context order, local rank, and lexical key.
frozen_design:
  historical_pool: byte-identical Y079/Y087 17-row full historical pool
  historical_anchor: context-local representative selected by frozen Y075 local_rank
  historical_transition_mask: four booleans key[i] != context_representative_key[i]
  target_transition_mask: four booleans target_selector_key[i] != other_target_selector_key[i]
  target_selectors: SOURCE_CONDITIONED and LOCAL_ONLY unchanged
  control: byte-identical Y079 exact 4-byte Hamming retrieval
  treatment: lexicographic transition-mask Hamming, exact-key Hamming, context order, local_rank, lexical key
  heldout_outcome_use_before_transition_factorization_freeze: 0
  post_result_transition_factorization_change_count: 0
  capacity: 16 total / 7 active / 9 retained
  persistent_state_write_count: 0
  external_model_calls: 0
candidate_set:
  - EXACT_KEY_ONLY
  - TRANSITION_MASK_FACTORIZED_KEY
classification_rules:
  supported: valid and transition-factorized retrieval changes a selected row and cleanly rescues where exact control does not, with zero lost control rescue and zero partner collateral
  mixed: valid, support false, but a changed transition-factorized selection improves prose collateral or first-success timing without partner harm
  negative: valid and neither supported nor mixed
  invalid: any frozen historical identity, representative anchor, transition-mask rule, control retrieval, treatment ordering, target selector identity, heldout ordering, 16/7/9 capacity, provenance, or accounting rule fails
successors:
  supported: Y089 transition-factorized prospective validation
  mixed: Y089 transition-factorized disambiguation
  negative: Y089 temporal-order state attribution
rsi_success: false
codex_usage: DISABLED
production_authority: false
accepted_ref_mutation: false
runtime_launch: false
capacity_change_authorized: false
authority_expansion: false
broker_access: false
ktrade_access: false
