# MR32-A — residual-driven bounded predictive belief prototype

Date: 2026-10-31
Parent: MR31 draft head `0503b25fe74dca30035a65c1d81edabddd31926e`.
Classification: SOURCE-ONLY DEVELOPMENT CANDIDATE. No scientific admission or original-world execution.

## Hypothesis

A bounded state updated only after selected-action outcomes can preserve useful predictive information without storing exact public histories. When an observed consequence contradicts the prior forecast, the mechanism should revise a nearby belief or promote a useful retained belief. Persistent state is useful only if it improves prospective predictions and decisions at fixed total resource cost.

This source-only prototype explores one implementation of that hypothesis. It does not establish the hypothesis.

## Implemented contract

- Input: exactly 16 normalized public feature values, supplied by caller. These are an opaque task-scoped representation; the prototype has no interface for world ID, task name, object labels, hidden state, generator seed, evaluator labels or unselected counterfactuals.
- Output: exactly 8 normalized consequence values, predicted before feedback.
- State: exactly 16 slots partitioned as 7 active and 9 retained. No dynamic capacity growth.
- Read: nearest three prototype beliefs, with fixed active/retained retrieval weighting.
- Update: only after one pending selected-action prediction is supplied its actual observed outcome. A contradiction raises the update rate; sufficiently novel/high-residual observations form a new active state.
- Retention: least-useful active state is demoted into the retained partition. A contradictory retained state may be promoted by swapping it with the least-useful active state; both partition sizes remain invariant.
- Persistence: canonical JSON checkpoint with schema, exact partition, fixed slot count and SHA-256 integrity. Pending prediction cannot be checkpointed; tampered or malformed snapshots fail closed.
- Determinism: stable distance ordering and deterministic eviction/promotion tie breaks.

## Source-only test coverage

Nine focused unit tests cover:
1. fixed 16-slot capacity and 7/9 partition through 40 updates;
2. strict prediction-before-outcome and single-use feedback;
3. contradiction detection and belief revision;
4. prediction-equivalent cold restore;
5. refusal to checkpoint pending feedback;
6. checkpoint tamper detection;
7. malformed dimensions/nonfinite values;
8. exact checkpoint slot count/partition;
9. retained-belief contradiction and promotion without capacity growth.

Local execution: `python -m unittest -v` — **9/9 PASS**.
Local syntax check: `python -m py_compile residual_belief.py test_residual_belief.py` — PASS.
This is local source-only engineering evidence. Exact Git blob execution in CI, cross-platform CI, original-world execution, full regression and scientific qualification have NOT occurred.

## Mandatory next comparisons before any scientific claim

- memoryless predictive control with identical input/output contract;
- equal-total-state recurrent/state-space control with exactly equal total bytes, not merely 16 named slots;
- Bayesian/model-based predictor with equal public information and budget;
- same-weight active-state erasure and retained-state erasure;
- randomized/intervention-derived prospective evaluation with FIT/CHECK/TRANSFER cohorts frozen before model implementation and no CHECK/TRANSFER tuning;
- actual decision reward, prospective consequence loss, contradiction correction, cold-restart retention, interference resistance and unfamiliar-family transfer;
- CPU, wall time, peak RSS, checkpoint bytes, active/retained state bytes, feature transport and inference cost.

The current implementation is a compact prototype using nearest-prototype residual updates. It may simply reproduce conventional prototype memory or be inferior to a small recurrent/Bayesian control. The nine tests validate software contracts only; they are not efficacy benchmarks and do not show learned causal structure, persistent cognition advantage or transfer.

## Governance

- Keep PR #501 R7 source and accepted baseline unchanged.
- Keep Wingless source, representation, learning state and owner independent.
- MR29/MR30A negatives remain immutable; MR31 remains an acquisition-only development result.
- FSA-04 issue #83 is OPEN; independent durable first-use authority is NOT DEPLOYED.
- No original environment reset/step, protected cohort, new source-family intake, workflow dispatch, queue/controller, source integration, merge, accepted ref, runtime activation or promotion is authorized or performed by this branch.


## MR32-B conventional controls added (source-only)

Two explicit controls now share the candidate's public input/selected-outcome interface:
- `MemorylessMean`: global outcome mean, with no input-conditioned persistent representation.
- `ConventionalPrototypeControl`: nearest-prototype/online-EMA predictor with the same 16-slot and 7/9 partition counts, but no residual-driven promotion/demotion policy.

These provide a basic source-level comparator, not an adequately strong complete conventional baseline suite. The shared slot count is **not** a claim of exact byte, Python object, checkpoint or runtime resource parity. The control stores full feature/target vectors in all 16 slots but does not have MR32's same state semantics. Full serialized state and total process-resource measurements are still required.

Both control tests are included in the dedicated Windows/Linux source-only workflow. Any passing tests qualify only interface and deterministic software behavior. They do not establish efficacy or learning advantage. A capable trained recurrent/state-space and Bayesian/model-based comparator remains mandatory before scientific claims.
