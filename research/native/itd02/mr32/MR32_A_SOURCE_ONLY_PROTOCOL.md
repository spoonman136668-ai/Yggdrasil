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


## MR32-C critical interface correction: selected-action conditioning

The original MR32-A/B prototype keyed predictive beliefs only by public features. That is insufficient for an action→consequence learner: two different selected actions in the same public context could be mixed into one successor prediction.

MR32-C corrects this before further qualification:
- `predict(public_features, selected_action)` requires an explicit selected action in the existing bounded action domain 0..2.
- Belief retrieval and update are conditioned on that action; outcomes from different actions cannot update the same slot.
- The pending feedback receipt binds public features, selected action, prediction and uncertainty; feedback remains single-use and strictly post-prediction.
- Each occupied checkpoint slot persists its selected-action key. The checkpoint schema is bumped to `yggdrasil.mr32.residual-belief.action-conditioned.v2`; legacy unconditioned snapshots are rejected as incompatible.
- Both conventional controls accept the same selected-action interface. The global-mean control deliberately ignores action in prediction, while the conventional prototype conditions on it.
- New tests verify that the residual candidate does not mix outcomes from different actions, that the prototype control separates action-conditioned outcomes, and that the memoryless baseline remains action-insensitive.

This fixes a necessary interface omission, not a scientific gain. The selected-action domain is a development interface assumption and still requires owner-authenticated mapping to the original Yggdrasil action semantics before any original-world use. No original environment or protected cohort was accessed.


## MR32-C control correction

The action-conditioned conventional prototype now allocates the first empty active slot when it encounters a previously unseen (public features, action) pair. The prior control implementation unconditionally wrote slot zero for every new pair, overwriting a different action's state; this was a comparator implementation defect, not an MR32 result. When all active slots are occupied, the baseline replaces the least-supported/oldest active prototype. Its fixed partition remains 7/9. This policy is intentionally conventional and still does not claim matched resource bytes.


## MR32-G — interaction-capable diagonal Bayesian control

Added a separate conventional baseline whose fixed basis includes bias, public features, selected-action indicators and every feature×action interaction. It has 68 coefficients per consequence output and a diagonal Gaussian posterior. This can represent action-specific feature effects that the additive diagonal Bayesian control cannot.

A held-out sign-reversal contract test now trains on a balanced action×feature development set and checks that the interaction model has lower error on the held-out combinations than the additive model. It is a deterministic synthetic expressivity check, not evidence about either native architecture. Model remains linear in its explicitly expanded basis and diagonal in posterior covariance; it is not a Bayesian causal graph learner/planner.


## MR32-H — trainable downstream-usefulness memory allocator

Added a separate candidate which maintains exactly 16 positions at all times: 7 active and 9 retained, including explicit empty slots before the store is populated. It learns a bounded linear utility predictor from post-task usefulness feedback for memory items explicitly marked as used. The learned score—not a fixed novelty or prediction-error threshold—determines the active/retained ranking and eviction order. Feedback cannot be assigned to an item that was not marked used. Pending feedback prevents checkpointing and eviction.

This pilot's metadata basis (evidence count, use count, recency, prediction-error summary and contradiction rate), linear predictor and update rule are fixed engineering choices. Its utility weights are learned from downstream labels. It is therefore a trainable retention scorer, not a fully learned representation or end-to-end memory policy. Synthetic test/inventory labels are only software-contract fixtures; no scientific efficacy is inferred.


## MR32-J — common checkpoint accounting

The deterministic resource inventory now wraps every model's model-specific payload in a shared `yggdrasil.mr32.common-checkpoint.v1` envelope with canonical JSON and a SHA-256 payload digest. It retains and reports native serialized byte count separately, alongside common-envelope byte count, deep Python object estimate, traced allocation peak and wall time. A cross-model test covers all seven model/control types and verifies common envelope identity and payload hash.

This standardizes serialization framing, not semantic state capacity: model payloads still differ in their number/type of variables, and deep object size/tracemalloc remain interpreter-specific/non-RSS. Equal total resource parity still requires matching representation capacity, CPU/inference budgets, calibrated RSS and repeated runs.


## MR32-K — held-out task-usefulness transfer falsification

The new `learned_retention_eval.py` trains the utility weights on eight FIT metadata profiles for 30 feedback epochs. It then transfers only the learned weights into a fresh allocator and inserts 16 disjoint-key TRANSFER records. Evaluation feedback is zero. The active 7-slot set is compared with fixed-recency and evidence-only top-seven controls on the same held-out records. A reproducible machine-readable result is emitted by the script and the workflow runs it on Windows and Linux.

The synthetic label is a fixed majority rule over evidence-count category, prediction-error category and contradiction-rate category. FIT and TRANSFER share this same generating rule. This only falsifies whether the linear scorer can learn this simple metadata rule and generalize it to new records; it does not model genuine future queries, causal worlds, real task reward, interference, or a novel task family. No scientific efficacy claim.


## MR32-L — leave-one-profile-out diagnostic

Added `learned_retention_cv.py`: eight folds each withhold one of the eight metadata profiles during FIT. Each fit receives seven of eight profile combinations for 30 rounds; only learned utility weights move into a fresh TRANSFER store. The omitted profile is represented in the transfer cohort, with zero transfer feedback. Per-fold learned active-set precision is reported against fixed recency and evidence-only controls. The dedicated Windows/Linux workflow runs the eight-fold diagnostic and its structural tests.

This is a profile-combination holdout under the same known synthetic majority-rule generator, not an unfamiliar task family or causal world. It is more discriminating than disjoint IDs with every profile observed during FIT, but remains synthetic and limited.


## MR32-M — content-conditioned learned allocator

A separate `ContentAwareMemoryAllocator` candidate now learns utility from the original five metadata signals plus the full 16-value stored representation. It retains the exact 16-slot, 7-active/9-retained contract and integrity-checked cold checkpoints; the metadata-only MR32-H candidate is unchanged. The dedicated Windows/Linux workflow now compiles, tests and resource-inventories both allocator variants.

The source-only discrimination fixture holds all metadata constant and trains on positive/negative content patterns, then tests new memory keys without evaluation feedback. This asks whether learned memory content can influence retention rather than relying exclusively on programmed metadata summaries. The representation dimension itself remains fixed and hand-authored, and the utility learner remains a linear online scorer. No original-world or authentic task outcome data are used.
