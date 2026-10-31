# MR32-D source audit — distinction between learned belief and programmed heuristics

Date: 2026-10-31
Exact candidate source head reviewed: `14f653d7b3d4d7fe68ca83f5cd65e8d4eaa3e5e2`.
Later evidence-only receipt commits preserve the same code; source blobs:
- residual belief: `d3d3890afa8f8286beef7b20d59212cc2018e5e9`
- conventional prototype: `ed0a90ccca65a917ef10a440a9af23f023104c4d`
- resource inventory: `a0bb5c399ef94b5d81e4e34ed8367d2e519d1343`

## Audit finding

MR32 is correctly described as a bounded, action-conditioned, residual-updated prototype, but it is **not yet a learned memory-management policy or demonstrated native cognitive representation**.

The following decisions are currently hand-coded:
- Action vocabulary is fixed to indices 0, 1 and 2. Original owner action semantics have not been mapped/authorized.
- Input/output representations are caller-supplied fixed-width 16/8 normalized vectors; feature formation is not learned here.
- Nearest-three retrieval and active/retained weighting are fixed.
- Novelty threshold 0.25, residual threshold 0.35 and contradiction threshold 0.30 are constants.
- State-formation rule, 0.50/0.15 update rates and feature update rate 0.05 are fixed.
- Eviction utility, age decay, promotion rule and 7/9 partition are programmed.
- The target is an 8-value selected-action consequence vector, not an action policy or task reward.

Only the prototype vectors and counters update from selected observed outcomes. The criteria deciding which beliefs to form, retain, revise, demote and promote are not learned from downstream outcomes.

Therefore call MR32 a **programmed residual-prototype memory mechanism with online outcome updates**, not a fully learned belief-state mechanism. Software tests show interface behavior only.

## Resource result

Cross-platform run `41217380126` executed the exact-head resource inventory for 256 synthetic steps. On both hosted runners MR32 was larger/slower than the conventional prototype in the reported measurements. Exact JSON/checkpoint formats differed; Python deep-size and tracemalloc are not process RSS. The signal is unfavorable but not a fair resource-efficacy verdict.

## Scientific disposition

`ACTION_CONDITIONED_SOURCE_CONTRACT=PASS`
`WINDOWS_LINUX_FOCUSED_CI=PASS`
`PROGRAMMED_RETENTION_POLICY=CONFIRMED`
`LEARNED_RETENTION_POLICY=NOT_IMPLEMENTED`
`RESOURCE_ADVANTAGE=NOT_DEMONSTRATED`
`REWARD_OR_DECISION_GAIN=NOT_TESTED`
`UNFAMILIAR_TRANSFER=NOT_TESTED`
`ORIGINAL_WORLD_ADMISSION=BLOCKED_FSA04`

## Next engineering gate

Do not tune the three thresholds on historical or held-out traces. First decide whether to continue this prototype at all. A scientifically meaningful successor would need a fixed-resource, trainable state-formation/retention rule whose parameters are updated only from downstream task outcomes on a legitimate FIT cohort, with separate frozen CHECK/TRANSFER cohorts and learned-vs-programmed ablations. Without independent FSA first-use authority, only implementation, unit tests, synthetic software-contract checks and resource accounting can proceed.

Before further feature expansion:
1. Reduce Python object overhead and inference cost without changing semantics; prove exact equivalence on deterministic contract tests.
2. Unify serialization format for candidate and controls, then measure full checkpoint and active/retained state bytes.
3. Add a capable recurrent/state-space and Bayesian/model-based control; current mean/prototype controls are insufficient.
4. Preserve all source identities and negative resource evidence.

No original environments, cohorts, accepted refs, production architectures, owner baselines or controllers were modified.
