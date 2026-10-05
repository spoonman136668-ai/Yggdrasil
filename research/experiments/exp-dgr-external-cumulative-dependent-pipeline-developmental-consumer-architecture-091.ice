schema: yggdrasil.research-preregistration.v1
experiment_id: EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-DEVELOPMENTAL-CONSUMER-ARCHITECTURE-091
parent_experiment: EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-RETAINED-COGNITION-DOWNSTREAM-INTEGRATION-090
parent_sha: ede8318d8915ebfa0972a3b14cced943d5fed39a
preregistered_at_utc: 2026-10-05T19:00:00Z
independence: Yggdrasil-only. No Wingless evidence, manifests, thresholds, representations, outcomes, or successor decisions are consumed.
route: Y090 negative only; stop memory-addressing and one-field downstream integration variants and test one bounded developmental consumer architecture.
selection_evidence:
  workflow_run_id: 37359857463
  screening_head_sha: b21f3df51255b24f920324a662a3630b85210fa9
  screening_artifact_sha256: 4946a9493cfab1ecab720da250d61460337ba2a646919e4c9a33bc44fafd1042
  candidate_universe_count: 27
  screened_count: 14
  selection_rule: first two accounting-valid pairwise source-disjoint contexts in deterministic frozen order; LOCAL_ONLY selector only; no child outcome evaluation
  selected_contexts: [y091-fresh-00, y091-fresh-13]
  child_outcome_use_count: 0
  target_answer_disclosure_count: 0
  target_context_mapping_disclosure_count: 0
manifest_sha256: 61240cf6cf57f8e57aab40a4608fdd057acde6aea7f7ec16cb5bfd57f4011c52
hypothesis: >
  The Y090 negative means local decision grounding alone is insufficient. A fixed two-source developmental consumer that
  blends retained cumulative statistics with target-local cumulative statistics once, while grounding decision fields locally,
  will make retained cognition behaviorally useful under unchanged 16/7/9 capacity.
capacity: 16 total / 7 active / 9 retained; unchanged
resources: fixed; no additional model calls, persistent slots, packets, source bytes beyond the two frozen contexts, or evaluation budget
historical_memory:
  source: exact Y079/Y090 historical transfer, third, and fourth eligible retained pools
  retrieval: exact existing full-pool Hamming retrieval; unchanged
  post_result_memory_addressing_change_count: 0
unseen_contexts:
  - name: tenth
    screening_name: y091-fresh-00
    local_only_key: [99, 116, 105, 111]
    code: {repo: apache/flink, commit: 953f843d578572cc74343c1f1a1ddb64d5c5d3e5, path: flink-runtime/src/main/java/org/apache/flink/runtime/jobmaster/JobMaster.java, git_blob: 39a29191b9761bf70fdeec265605e404d47d3e6d, prefix_bytes: 41453, prefix_sha256: f689ce4c905a87dd3b30cc61f6aa923592cb20bb07c60091b40f9aae864e369e}
    structured: {repo: tauri-apps/tauri, commit: 79d3537620ddd136b81896b2048207e7c15e08b9, path: Cargo.lock, git_blob: a68f439de5de3c3c1ac0bb64892f275cfb4faf49, prefix_bytes: 14365, prefix_sha256: 6f88d8f078e1ce9122e2e16bb36c2dc6c426aad6d5af569c1d4fd887ac5f7b72}
    technical_prose: {repo: scikit-learn/scikit-learn, commit: c1f21786a8dc523c56ebb24f53b09dc14a57ea4d, path: README.rst, git_blob: cf30a4b3289a096a273ca490e1a846cf4c088795, prefix_bytes: 1454, prefix_sha256: f210b576a393107041b9ed51c76ab133c7cb51082ae1e3d119fe8abd09331561}
  - name: eleventh
    screening_name: y091-fresh-13
    local_only_key: [116, 114, 117, 99]
    code: {repo: godotengine/godot, commit: c016f22009aa773f0b2e6fce72baec168746491f, path: scene/main/node.cpp, git_blob: 0dfe2995e5c78480e528f0b841ffff88d82d40bc, prefix_bytes: 41453, prefix_sha256: 22dd9cb64887332ef50d73195745448e32cb0ece1bb62cc6918e196618f58991}
    structured: {repo: vitejs/vite, commit: 10033218d239c927cdc375970b5741cce408e81b, path: pnpm-lock.yaml, git_blob: 1429512d32326cad970a993ab6832080e5579292, prefix_bytes: 14365, prefix_sha256: 740787049be5cd656d5ef3a570eccaa3ab590daa5300a85ae0185a25f93deb03}
    technical_prose: {repo: tensorflow/tensorflow, commit: 1d968a6e886854cd650b7c378baee96effdef3dc, path: README.md, git_blob: 2ada91b134b2bc6daa60ca6265f1290f38a748c1, prefix_bytes: 1454, prefix_sha256: c47c609d3766e4eb0e95cec4aa3978271d00cbd9677aa44bdc0f165d1ab09c21}
target_selector: LOCAL_ONLY only; exact selector keys frozen by screen
control:
  name: EXACT_RETAINED_STATE
  rule: retrieve the exact existing full-pool retained row and project its full payload into the target key exactly as Y079/Y090 do
treatment:
  name: DEVELOPMENTAL_RESIDUAL_CONSUMER
  stages:
    - ground best and map_best to the target-local state
    - blend retained and target-local total and best_count by integer floor mean; blend consistency and utility by arithmetic mean
  retained_fields_preserved: [cell_index]
  blend_coefficient: 0.5 fixed before target outcomes; no sweep
  memory_retrieval_change: false
  persistent_state_change: false
  capacity_change: false
cells: 2 unseen contexts x 2 arms = 4 child evaluations
classification_rules:
  supported: >
    Valid; treatment-only clean rescue occurs in both unseen contexts; zero lost-control clean rescues;
    zero treatment partner collateral failures; and treatment changes behavior in both contexts.
  mixed: >
    Valid; support false; treatment improves prose collateral or first-success timing in both contexts,
    with zero lost-control clean rescues and zero treatment partner collateral failures.
  negative: valid and neither supported nor mixed.
  invalid: >
    Any exact source/blob/prefix, historical retained-pool identity, target-local selector key, retrieval rule, fixed 0.5 residual rule,
    16/7/9 capacity, heldout ordering, deterministic replay, provenance, disclosure, or accounting rule fails.
negative_interpretation: >
  The fixed developmental residual consumer also fails under fixed capacity; stop hand-designed retained/local blending
  and move to a learned or structurally different developmental consumer without returning to memory addressing variants.
infra_failure_policy: exact infrastructure repair and deterministic rerun only; scientific negative/mixed outcomes remain immutable
post_result_tuning: false
rsi_success: false
production_authority: false
accepted_ref_mutation: false
runtime_launch: false
capacity_change_authorized: false
