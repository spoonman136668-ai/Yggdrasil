schema: yggdrasil.research-preregistration.v1
experiment_id: EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-ORACLE-CANONICAL-INVARIANT-UTILIZATION-089-FIXA
parent_experiment: EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-ORACLE-CANONICAL-INVARIANT-UTILIZATION-089
parent_sha: 402033d22217e3d48f8eb200661a9fef0da21cce
preregistered_at_utc: 2026-10-05T09:57:03Z
independence: Yggdrasil-only. No Wingless evidence, manifests, thresholds, representations, outcomes, or successor decisions are consumed.
repair_scope: selector-collision FIXA only; scientific hypothesis, thresholds, canonical relation, capacity, disclosure rules, and outcome logic are unchanged from Y089.
selection_evidence:
  workflow_run_id: 37293321684
  screening_head_sha: 856e21f085be30ba4def1b21328f46af71367880
  candidate_universe_count: 448
  screened_count: 98
  eligible_screened_count: 15
  selection_rule: first two pairwise source-disjoint candidates in frozen order with SOURCE_CONDITIONED key different from LOCAL_ONLY key
  child_outcome_use_count: 0
  target_answer_disclosure_count: 0
  target_context_mapping_disclosure_count: 0
manifest_sha256: de2177f3998dc983bdfa1427a32eec5eebaa1c30b5a5884e382a64ce4c828aff
hypothesis: >
  The Y089 invalid result was caused solely by SOURCE_CONDITIONED and LOCAL_ONLY collapsing to the same selected row.
  On two fresh source-disjoint unseen contexts whose selectors are separated before any target outcome is evaluated,
  the unchanged oracle-canonical invariant relation can be validly re-tested under the same fixed capacity and disclosure rules.
capacity: 16 total / 7 active / 9 retained; unchanged
resources: fixed; no additional model calls, persistent slots, source bytes, packets, or evaluation budget
unseen_contexts:
  - name: sixth
    screening_name: fixa-candidate-a
    source_conditioned_key: [32, 116, 104, 101]
    local_only_key: [99, 116, 105, 111]
    code: {repo: apache/spark, commit: 2f4102c8117a087aba1324d52b268f7966670136, path: core/src/main/scala/org/apache/spark/SparkContext.scala, git_blob: f1cc057ef920e7349eb6b2ce9859fca1db854589, prefix_bytes: 41453, prefix_sha256: 25f004f46823b2232d5c168ec9ac7b16d3446edc9f492085bf89be7f6e4f4ed3}
    structured: {repo: hashicorp/terraform, commit: d8e7252bce0f6b363c3c5ef26eb6d343395b5f5f, path: go.sum, git_blob: be62f6851c7544d66cc825f2ebcbb3097f816d01, prefix_bytes: 14365, prefix_sha256: 9715c9e8a2c315695773e346e8287ce05faa9d590e2827cbb2ac95d704e4e0ee}
    technical_prose: {repo: curl/curl, commit: efcbd5607896d509c6fd77a740b8f8eb9f7586b6, path: docs/libcurl/curl_easy_setopt.md, git_blob: 23eda35203339b36d08956d1c17d8ea8924ae65d, prefix_bytes: 1454, prefix_sha256: 1c3fda81f31065246048856028c27a319edcc6b039d9776f765abfef52370c85}
  - name: seventh
    screening_name: fixb-cross-143
    source_conditioned_key: [44, 10, 32, 32]
    local_only_key: [32, 97, 110, 100]
    code: {repo: apache/cassandra, commit: b15526b4816518e415aa1046d7eb98232a0c1151, path: src/java/org/apache/cassandra/db/ColumnFamilyStore.java, git_blob: d69cf7354513d3444777b4c425d0147826c24953, prefix_bytes: 41453, prefix_sha256: d3046eb79b0cb75bd5552dfac4d43ea7a979e51c4a62a449af76dcb545389cd5}
    structured: {repo: npm/cli, commit: b317f16c80df02ea3628cfa77170d5ae9b59720c, path: package-lock.json, git_blob: ec6ec30dd06549a6df33600b41ec1e2babf459af, prefix_bytes: 14365, prefix_sha256: 667d1b6953fb1fc6b452a312bbb2fa7658dff68dab7bc41d60769771b1768252}
    technical_prose: {repo: qemu/qemu, commit: d7a65d1793d691d356a56833620f7d1e6f5d653b, path: docs/system/introduction.rst, git_blob: 8d9ef61d262b276250aa2bc102c6834adcd96be2, prefix_bytes: 1454, prefix_sha256: 5fe7c45b5bc52ac5bb55ed81cae9438f7ce157eb2325c5032f72d14ed89b18e2}
frozen_oracle_relation:
  source: exact Y089 canonical invariant relation; unchanged
  forbidden_disclosure:
    - target answer
    - correct historical context identity
    - target-to-context mapping
    - child outcome
    - clean-rescue label
  freeze_time: before either unseen-context child outcome is evaluated
target_selectors: SOURCE_CONDITIONED and LOCAL_ONLY unchanged
cells: 2 unseen contexts x 2 target selectors x 2 arms = 8 child evaluations
classification_rules:
  supported: >
    Valid; treatment changes at least one selected retained row in each unseen context; at least two oracle-only clean rescues
    spanning both unseen contexts; zero lost-control clean rescues; zero partner collateral failures.
  mixed: >
    Valid; support false; treatment changes selections in both unseen contexts and improves prose collateral or first-success timing
    in at least two target cases with zero partner harm and zero lost-control clean rescues.
  negative: valid and neither supported nor mixed.
  invalid: >
    Any frozen source/blob/prefix, preregistered selector-separation, canonical relation transform, forbidden-disclosure rule,
    candidate pool, target selector, 16/7/9 capacity, heldout ordering, deterministic replay, provenance, or accounting rule fails.
successors:
  supported: EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-SELF-LEARNED-CANONICAL-INVARIANT-090
  mixed: EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-INVARIANT-UTILIZATION-STAGE-LOCALIZATION-090
  negative: EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-RETAINED-COGNITION-DOWNSTREAM-INTEGRATION-090
infra_failure_policy: exact infrastructure repair and deterministic rerun only; scientific negative/mixed outcomes remain immutable
post_result_tuning: false
rsi_success: false
production_authority: false
accepted_ref_mutation: false
runtime_launch: false
capacity_change_authorized: false
