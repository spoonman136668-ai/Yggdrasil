schema: yggdrasil.research-preregistration.v1
experiment_id: EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-RETAINED-COGNITION-DOWNSTREAM-INTEGRATION-090
parent_experiment: EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-ORACLE-CANONICAL-INVARIANT-UTILIZATION-089-FIXA
parent_sha: 0f46d5b713ca7b1286c76b12434cc13f4e20e052
preregistered_at_utc: 2026-10-05T17:24:00Z
independence: Yggdrasil-only. No Wingless evidence, manifests, thresholds, representations, outcomes, or successor decisions are consumed.
route: Y089-FIXA negative only; stop memory key/gate/factorization variants and test one bounded downstream integration intervention.
selection_evidence:
  workflow_run_id: 37293321684
  screening_head_sha: 856e21f085be30ba4def1b21328f46af71367880
  screening_artifact_sha256: fd11676d85235bf7d4f07ad3ee5605a50af3cab7f44777d9a205698c889d95b3
  candidate_universe_count: 448
  screened_count: 98
  child_outcome_use_count: 0
  selection_rule: first two accounting-valid source-disjoint contexts not used by Y089-FIXA and mutually source-disjoint, in frozen screen order
  selected_contexts: [fixa-candidate-c, fixa-candidate-g]
  target_answer_disclosure_count: 0
  target_context_mapping_disclosure_count: 0
manifest_sha256: c2b4dbb284094d76a4343850cedac1d762328fe885620ec980672ca297bd2140
hypothesis: >
  The clean Y089-FIXA negative indicates that changing memory addressing or canonical retrieval is insufficient.
  A fixed downstream consumer intervention that grounds the retained cognition's decision fields in the target-local state,
  while preserving the retrieved retained cognition's cumulative statistics, will improve clean rescue under unchanged capacity.
capacity: 16 total / 7 active / 9 retained; unchanged
resources: fixed; no additional model calls, persistent slots, packets, source bytes beyond the two frozen contexts, or evaluation budget
historical_memory:
  source: exact Y079/Y089 historical transfer, third, and fourth eligible retained pools
  retrieval: exact existing full-pool Hamming retrieval; unchanged from pre-Y089 code
  post_result_memory_addressing_change_count: 0
unseen_contexts:
  - name: eighth
    screening_name: fixa-candidate-c
    code: {repo: apache/kafka, commit: a81595abe8d48b0edd2ca9d42b221eb9465e8bad, path: core/src/main/scala/kafka/server/KafkaApis.scala, git_blob: b688a933e7635855c1869828a08cddbc22c2a7b1, prefix_bytes: 41453, prefix_sha256: dd6e3c7fb622f1853c5e399cd96c6b44afeec3402d75fdc9a2ee959f6511b46e}
    structured: {repo: rustdesk/rustdesk, commit: e5bc204fe4dacc4db9c3cdb1f1338813986c89e7, path: Cargo.lock, git_blob: 727ef11d78aa3347d96218dc273dc83179bb1a7f, prefix_bytes: 14365, prefix_sha256: ca09e43477b21a998a835c6b24ab9007a9a085aee72bea74c7993c3537ad1800}
    technical_prose: {repo: denoland/deno, commit: b4f08f127652d8442b4d3dbabc277aca3840bc1d, path: README.md, git_blob: 8173eb951062916cc112a8fb7c0e120b1c945975, prefix_bytes: 1454, prefix_sha256: eabf6e4358ac7b181bdcf9c1695209c512b0f0dd6826ca4f84664471a5ccda05}
  - name: ninth
    screening_name: fixa-candidate-g
    code: {repo: postgres/postgres, commit: d6393fc40a59830a88a79bdf08e962122fa9c631, path: src/backend/executor/nodeAgg.c, git_blob: 29037cf3122e56ddb0a3a14ab9df70285539a4a7, prefix_bytes: 41453, prefix_sha256: 2da5169fddf0882b08375490fdbe5f3bfc252b495f5c08256de11503d192bb26}
    structured: {repo: apache/cassandra, commit: b15526b4816518e415aa1046d7eb98232a0c1151, path: build.xml, git_blob: f528fb4aebed40c698cad2499d3002524b70ca69, prefix_bytes: 14365, prefix_sha256: 868d62cbe280ce4258aa380a242e38986b10db297d4d232964a013848e520ce9}
    technical_prose: {repo: nodejs/node, commit: c56cb0947f9e67fe4bfd07f69bba82f6109d4416, path: doc/api/stream.md, git_blob: 1e8a2bd1ef930fc7277cdda5bade3e624e94edfd, prefix_bytes: 1454, prefix_sha256: 7f55e35323b059ef44b1234f9071a48fc231b012503fa6490d662f2b3f5b08a8}
target_selector: LOCAL_ONLY only; selected before any child outcome
control:
  name: EXACT_RETAINED_STATE
  rule: retrieve the exact existing full-pool retained row and project its full payload into the target key exactly as Y079 does
treatment:
  name: DOWNSTREAM_LOCAL_DECISION_GROUNDING
  rule: >
    Start from the exact control projection. Preserve retained total, best_count, consistency, utility, and cell_index.
    Replace only downstream decision-consumption fields best and map_best with the target-local state's preregistered values.
    Keep the target key and target-local training-count metadata unchanged. No field, gate, threshold, or coefficient is tuned.
  memory_retrieval_change: false
  persistent_state_change: false
  capacity_change: false
cells: 2 unseen contexts x 2 arms = 4 child evaluations
primary_metrics:
  - treatment_only_clean_rescue_count
  - lost_control_clean_rescue_count
  - treatment_behavior_change_count
  - treatment_partner_collateral_failure_count
  - treatment_improvement_case_count
  - all_child_source_identity_mismatch_count
  - all_child_transport_identity_mismatch_count
  - capacity_growth_event_count
classification_rules:
  supported: >
    Valid; treatment-only clean rescue occurs in both unseen contexts; zero lost-control clean rescues;
    zero treatment partner collateral failures; and treatment changes behavior in both contexts.
  mixed: >
    Valid; support false; treatment improves prose collateral or first-success timing in both contexts,
    with zero lost-control clean rescues and zero treatment partner collateral failures.
  negative: valid and neither supported nor mixed.
  invalid: >
    Any exact source/blob/prefix, historical retained-pool identity, target-local selector, retrieval rule, integration-field rule,
    16/7/9 capacity, heldout ordering, deterministic replay, provenance, disclosure, or accounting rule fails.
negative_interpretation: >
  Even bounded downstream integration of retained cognition fails under fixed capacity; shift to developmental dynamics or consumer architecture,
  and do not return to memory key/gate/factorization variants.
infra_failure_policy: exact infrastructure repair and deterministic rerun only; scientific negative/mixed outcomes remain immutable
post_result_tuning: false
rsi_success: false
production_authority: false
accepted_ref_mutation: false
runtime_launch: false
capacity_change_authorized: false
