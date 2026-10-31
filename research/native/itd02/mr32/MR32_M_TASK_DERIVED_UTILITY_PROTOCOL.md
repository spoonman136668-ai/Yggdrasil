# MR32-M — task-derived downstream utility: frozen development protocol

**Status:** protocol-only, development-only. No task experiment or scientific first-use is authorized by this document.

## Question

Can the MR32-H fixed-budget memory allocator learn which *actually used* memories improve later task performance from post-task outcomes, and use that learned utility to select memories better than random, fixed-recency, evidence-only, and a competent conventional learned utility controller?

This tests memory selection, not general intelligence, causal world identification, or the native Yggdrasil architecture.

## Frozen mechanism and budget

- Exactly 16 memory positions from empty initialization: 7 active and 9 retained.
- All methods receive the same public memory records, query stream, observed selected actions, and post-task outcome events.
- The learner receives only public metadata and post-task utility feedback for a memory that was actually retrieved/used. It receives no evaluator-private task state, target answer, future query, or unselected-item label.
- MR32-H's fixed metadata basis and linear utility scorer remain unchanged for this experiment. No threshold, learning-rate, capacity, or feature retuning after outcomes.
- A used-memory outcome is measured from the task's actual return, not a supplied binary usefulness label. The feedback scalar is the paired task-return difference between the same deterministic task episode with the selected memory available and a replay with that memory disabled. The evaluator computes this difference; only the scalar is delivered after the task. Both executions start from identical episode seed and public initial state.
- No feedback is generated for a memory that was not actually retrieved by the task.

## Task fixture and cohort separation

The implementation will provide a deterministic, source-only task simulator with two independently parameterized task regimes. Each episode contains a sequence of public queries and task actions; memories encode previously observed public action/consequence information. A memory is useful only to the extent that making it available changes the actual task return on a query that retrieves it.

- FIT: 48 task episodes over 8 frozen seed clusters, balanced across the two regimes. FIT is the only cohort allowed to update utility-model weights.
- TRANSFER: 64 task episodes over 16 disjoint frozen seed clusters, balanced across the two regimes. No TRANSFER feedback may update any method.
- The exact seed lists, task-regime definitions, query/action stream hashes, and task-return calculation must be committed with the implementation before execution. The implementation must assert FIT/TRANSFER disjointness and reject unlisted seeds.
- The two regimes are development fixtures, not Farama, Pycolab, MiniGrid, Crafter, Gridworlds, protected scientific first-use, or an external independent science authority. Results must be labelled **controlled task-fixture development evidence**.

## Required comparisons

1. **Random:** seeded selection among the same 16 records, with seed independent of task outcomes.
2. **Fixed recency:** the 7 most recently used/inserted records under the common event stream.
3. **Evidence-only:** deterministic ranking by observed evidence count, tie-broken by immutable memory key.
4. **MR32-H learned utility:** current 5-metadata-feature linear utility scorer, trained only from FIT task-derived paired return differences.
5. **Competent learned control:** a separately implemented interaction-capable Bayesian utility predictor using the same metadata and exact same FIT feedback events; no extra observations, task episodes, or tuning on TRANSFER.

Every method must use the same 16-record total capacity and 7-active/9-retained split, same record encodings and query stream. Report differences in serialized state bytes and process CPU/RSS; equal slot counts alone are not resource parity.

## Primary endpoint and falsifiers

Primary endpoint is mean TRANSFER task return per seed cluster, with paired per-episode and per-cluster differences. Also report no-memory return and the paired marginal return contribution of each selected memory. Active-set precision is diagnostic only.

A development signal requires all of the following:
- MR32-H exceeds each of random, recency, evidence-only and the competent learned control by at least **0.02 absolute task-return units** on aggregate TRANSFER.
- MR32-H wins against the strongest comparator in at least **12 of 16** independent TRANSFER seed clusters, with at least **6 of 8** wins within each regime.
- A deterministic paired cluster bootstrap (10,000 resamples; fixed seed recorded in code) has a 2.5th percentile greater than zero against the strongest comparator.
- The sign and magnitude reproduce on Windows and Ubuntu from identical task event hashes.
- All no-feedback, selected-use-only feedback, 16/7/9 capacity, checkpoint/cold-restore, task-seed custody, and resource-accounting invariants pass.

Any failure is retained as a negative or inconclusive result. Do not adjust the task generator, seeds, thresholds, utility labels, or model after inspecting TRANSFER. A pass is still only controlled task-fixture development evidence, not scientific admission.

## Required receipts

Record exact project commit and source blob identities; preregistration SHA; FIT and TRANSFER event hashes; per-episode selected memories and task returns; per-memory feedback provenance; model checkpoint hashes; per-method state bytes; full-process CPU time and peak RSS; wall time; cold-restart results; OS/Python/NumPy/runtime identity; and independent cross-OS reconciliation.

## Governance and stop conditions

- Source-only development branch and additive research files only.
- Do not run any original or protected native environment; do not consume or infer scientific first-use.
- Do not call a task-fixture run an independent source-family trial.
- Do not integrate with R7, FORGE, Wingless, production runtime, or accepted refs.
- FSA-04 [#83](https://github.com/spoonman136668-ai/FORGE/issues/83) remains the independent authority gate. The connected evidence currently records no independent FSA science issuer, no qualified durable off-provider custody/restore, and no permission for protected first-use.
- G29 remains fail-closed. No atlas waiver, accepted-ref mutation, merge, promotion, or controller/queue change.
- No paid API or external model call.

