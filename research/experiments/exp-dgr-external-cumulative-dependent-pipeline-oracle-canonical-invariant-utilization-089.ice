schema: yggdrasil.research-preregistration.v1
experiment_id: EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-ORACLE-CANONICAL-INVARIANT-UTILIZATION-089
parent_experiment: EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-TRANSITION-STATE-FACTORIZATION-ATTRIBUTION-088
parent_sha: ada69803088e4edd15d5c8ba7376b49ce65c5bd2
preregistered_at_utc: 2026-10-04T23:29:00Z
independence: Yggdrasil-only. No Wingless evidence, manifests, thresholds, representations, outcomes, or successor decisions may be consumed.
hypothesis: >
  Retained cognition is present but fails to transfer because current retention stores context-local realizations.
  If the harness supplies only a frozen canonical invariant relation, without a target answer or target-context mapping,
  the existing fixed-capacity system can use retained cognition to produce clean rescues on genuinely unseen contexts.
competing_explanation: >
  Even when the invariant relation is supplied, retained cognition cannot be productively consumed; the failure is therefore
  downstream of memory-key/gate/factorization representation or reflects absent transferable cognition.
capacity: 16 total / 7 active / 9 retained; unchanged
resources: fixed; no additional model calls, persistent slots, source bytes, packets, or evaluation budget
unseen_contexts:
  - name: sixth
    code: {repo: pandas-dev/pandas, commit: 71e11934c88cebded4f633e845cd1a16d27bfbe6, path: pandas/core/frame.py, git_blob: 4db8d304aa294525595a9bcf13068713a0db9b31, prefix_bytes: 41453}
    structured: {repo: prettier/prettier, commit: 5927216227411bc2cdaf30d50559e0a475ab4832, path: yarn.lock, git_blob: c3f04b2437d5ea4bde2fc66576a162faf82d5fa9, prefix_bytes: 14365}
    technical_prose: {repo: numpy/numpy, commit: 2545ec71ff3394221c4186f8333064050c396afc, path: doc/source/user/quickstart.rst, git_blob: b611b5000eef62234bd22f66787a8bb32736b963, prefix_bytes: 1454}
  - name: seventh
    code: {repo: scikit-learn/scikit-learn, commit: a442e4bb39551feb7b0af4c00075e2cb91cf9b77, path: sklearn/ensemble/_forest.py, git_blob: f3f5d4554200c2425a959bb0b01dc43365e15c6e, prefix_bytes: 41453}
    structured: {repo: pnpm/pnpm, commit: fca2d32621419e34897a114a2f14199344bdb8fc, path: pnpm-lock.yaml, git_blob: 24088d8a8df904b3ac8b39b057708afc3205cc16, prefix_bytes: 14365}
    technical_prose: {repo: nodejs/node, commit: 93bb027b687e8bcf0b71bd62e0c8ff2630dc93cc, path: doc/api/fs.md, git_blob: d6eb4208ef0a7401a00a89ea3686eb0b9f7054fb, prefix_bytes: 1454}
frozen_oracle_relation:
  purpose: isolate utilization of invariant structure from the separate problem of learning that representation
  disclosure: the harness supplies only the canonical invariant relation signature
  forbidden_disclosure:
    - target answer
    - correct historical context identity
    - target-to-context mapping
    - child outcome
    - clean-rescue label
  transform: >
    Canonicalize the retained/target state into a context-label-free relational signature consisting only of
    anchor-relative key order/equality relations, within-key pairwise order/equality relations, best-versus-map_best relation,
    and ordinal ranks of best_count/consistency/utility/cell_index within the local eligible pool.
    No raw context identifier or raw byte identity is included.
  freeze_time: before either unseen-context child outcome is evaluated
control: current frozen retained-state retrieval/activation path from Y088 lineage
treatment: >
  The harness supplies the target canonical relation signature to the unchanged fixed-capacity consumer.
  Candidate retained states are matched by exact canonical relation first and the existing frozen deterministic tie-breakers second.
  The harness never identifies which historical context should be used.
target_selectors: SOURCE_CONDITIONED and LOCAL_ONLY unchanged
cells: 2 unseen contexts x 2 target selectors x 2 arms = 8 child evaluations
clean_rescue: active positive prose collateral schedules improve relative to original AND active partner collateral failure count remains zero
metrics:
  - control_clean_rescue_count
  - oracle_invariant_clean_rescue_count
  - oracle_only_clean_rescue_count
  - lost_control_clean_rescue_count
  - oracle_selected_row_change_count
  - oracle_behavior_change_count
  - active_positive_prose_collateral_schedule_count
  - active_mean_first_success_packet
  - active_partner_collateral_failure_count
  - per_context_clean_rescue_count
  - canonical_relation_identity_mismatch_count
  - target_source_identity_mismatch_count
  - heldout_outcome_use_before_oracle_relation_freeze
  - target_context_mapping_disclosure_count
  - target_answer_disclosure_count
  - post_result_relation_change_count
  - persistent_state_write_count
  - capacity_growth_event_count
  - invalid_evaluation_rows
classification_rules:
  supported: >
    Valid; treatment changes at least one selected retained row in each unseen context; at least two oracle-only clean rescues
    spanning both unseen contexts; zero lost-control clean rescues; zero partner collateral failures.
  mixed: >
    Valid; support false; treatment changes selections in both unseen contexts and improves prose collateral or first-success timing
    in at least two target cases with zero partner harm and zero lost-control clean rescues.
  negative: valid and neither supported nor mixed.
  invalid: >
    Any frozen source/blob/prefix, canonical relation transform, forbidden-disclosure rule, candidate pool, target selector,
    16/7/9 capacity, heldout ordering, deterministic replay, provenance, or accounting rule fails.
negative_interpretation: >
  Stop further memory-key/gate/factorization variants. Move downstream to integration/reasoning/developmental dynamics
  that consume retained cognition under the same fixed capacity.
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
