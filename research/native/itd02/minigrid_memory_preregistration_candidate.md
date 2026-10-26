# ITD-02 MiniGrid Memory — Preregistration Candidate

**Status:** DRAFT — NOT ADMITTED FOR EXECUTION  
**Purpose:** Freeze the scientific decision rules before generating any original task episodes.  
**Source:** `Farama-Foundation/Minigrid@7f5853792ea7f04f75614661006d87fcf949f26d`  
**Environment candidate:** `MiniGrid-MemoryS7-v0`  
**Evidence boundary:** the existing static source-preflight and public-event contract only. No episode data, model fits, or protected first-use results are included here.

## 1. Question and falsifiable claims

Primary question: can the native Yggdrasil learner use past public observations to choose the matching object at the later fork, retain the useful information, and transfer the mechanism to held-out layouts/seeds?

A memory claim requires all of the following:
1. The final decision can be evaluated from public observations/history and reward without disclosing hidden environment fields to the learner or evaluator.
2. A preregistered witness set contains matching terminal public observations that occur after distinct public histories and require different optimal choices.
3. The native learner improves over a matched feed-forward/no-persistent-state control on witness-pair accuracy and held-out matching success.
4. The result persists after a cold restart when only the declared persistent learner artifact is restored.

A failed witness construction or an environment/API incompatibility is a stop, not permission to rewrite the task or invent a replacement simulator.

## 2. Source and information boundary

Pin the upstream commit and the existing Git-blob identities in the source-preflight test. The worker may load only the pinned environment and pass through its ordinary reset/step public return values.

Learner-available fields:
- Observation: `image`, `direction`, `mission`.
- Action: the source's seven discrete action IDs, unchanged.
- Reward and `terminated`/`truncated` flags.
- Episode/sequence identifiers added by the adapter, not derived from hidden state.

Never pass the environment object, full grid, cue/object type stored internally, `success_pos`, `failure_pos`, hidden goal, private RNG state, raw diagnostic `info`, or any answer/target bit to the learner or scoring code. The terminal score is computed from the environment's public reward only. Source inspection and adapter receipts do not attest a live worker's executable identity; execution needs its own receipt chain.

The projector must preserve the image values exactly. Do not compress the image to a hand-written cue label, answer bit, or three-action interface. A representation encoder, if later proposed, must be a separately specified, equally available component for every learning arm and must have its own tests.

## 3. Arms and parity

Freeze implementations and dependency/toolchain identities in the eventual admission package. All arms receive the same ordered public event stream and the same action IDs, rewards, episode resets, and step ceilings.

- **N — native candidate:** the declared Wingless/Yggdrasil-native mechanism under test; exact component and persistent-state contract must be pinned before admission.
- **R — recurrent control:** a trained conventional recurrent policy with hidden state reset at each episode and persistent learned weights.
- **F — feed-forward history control:** a conventional feed-forward policy over a fixed, preregistered window of public observations, actions and rewards; no privileged memory feature.
- **B — simple baseline:** a preregistered observation/history-independent policy, used as a sanity/control baseline, not as a competitive result.

Each trainable arm receives the same training interaction budget, optimizer/search budget, number of independent training seeds, and validation evaluation count. Equal interaction budget means counted environment steps, including failed episodes. Log wall time, CPU time, peak resident memory, artifact size and total steps. No arm-specific extra tuning after seeing validation or development results. If the native architecture cannot consume raw observations under this contract, stop and document the interface mismatch; do not silently give it an easier task.

## 4. Splits, tuning, and frozen evaluation

Use this deterministic seed allocation, with each seed used for exactly one split and never reused across splits:
- FIT: integers 10000–10999; one original-source episode per seed for the frozen FIT cohort (1,000 FIT episodes total). Any repeated parameter-training passes must reuse only those stored FIT events, must not recollect episodes, and count toward the same 1,000,000-step-per-arm ceiling. Record the exact per-seed episode count and total environment steps in the admission receipt before execution.
- VALID: integers 20000–20199 (200 episodes).
- DEV: integers 30000–30199 (200 episodes).

Before admission, verify that the pinned environment's reset seed fully controls the relevant randomized layout under the selected Gymnasium wrapper. If wrappers or version drift alter this guarantee, stop and specify new disjoint ranges before any episode is generated. These ranges are a preregistered plan, not evidence those episodes were run.

Use FIT for parameter updates only. VALID may select one configuration per arm under the same search-count ceiling. Freeze all weights, hyperparameters, preprocessing, checkpoints, score aggregation, and witness-generation code before opening DEV outcomes. DEV is evaluated once. No retraining or threshold adjustment based on DEV.

The witness-pair set must be constructed and validated before model training, using only source task rules and the public event protocol. Pair membership, labels, and an independent evaluator's derivation must be committed and hash-pinned before any held-out evaluation. The evaluator may use a separately isolated task-construction process, but may not reveal private state or labels to the learner. If a valid paired witness cannot be built and independently validated under this separation, the memory-required claim is inconclusive and the trial stops.

### Frozen MemoryS7 branch-decision geometry

For registered `MiniGrid-MemoryS7-v0` at the pinned source, the fixed layout has width 9, height 7, and `hallway_end=6`. The witness inclusion rule requires the reset public image to expose the unique Key/Ball cue at image cell `(2,6)`; this corresponds to the source cue at global `(1,2)` and implies the reset agent starts at `x=1`. Six `FORWARD` transitions reach the branch entrance `x=7`; the public decision observation is therefore event sequence `6`, before the branch-turn action is selected. At this view, the upper and lower end objects must be the only visible Key/Ball cells at image coordinates `(1,6)` and `(5,6)`, respectively. The candidate choices are `LEFT=0` when the cue matches the upper object and `RIGHT=1` otherwise. Freeze the recorded sequence as: decision observation at event `seq=6`; turn action in event `seq=7`, whose public direction must be north (`3`) after LEFT or south (`1`) after RIGHT; first FORWARD action in event `seq=8`, preserving that direction; second FORWARD action in event `seq=9`, reaching the selected end-object/success position with positive public reward and terminal success. Reject any trace whose public action or direction sequence disagrees.

This is a source-derived admission candidate, not episode evidence. Before original-source first-use, an independent reviewer must verify the geometry and action-to-success rule from the pinned public source, and the source-authorized receipt must confirm the public-pixel inclusion conditions. If the expected cells are absent, ambiguous, or inconsistent in actual observations, reject the pair; do not read hidden grid fields to salvage it.

## 5. Cold-restart retention

After final training and validation selection, terminate the learner process. Reconstruct it in a fresh process with no inherited RAM, caches, environment object, RNG state, hidden-state buffer or files except the preregistered persistent artifact and pinned configuration. Run DEV through the public interface from fresh episode resets. No model update during DEV. Record artifact hashes before and after; unexpected change fails the gate.

Report both uninterrupted inference and cold-restart results. If only weights are intended to persist, say so explicitly; if an external memory store is claimed as part of the mechanism, pin its schema, identity and contents in the artifact manifest before the run.

## 6. Outcomes and decision rules

Primary outcomes:
- DEV matching-task success rate (environment reward success).
- DEV witness-pair accuracy, with the exact definition and witness count frozen before admission.
- Difference between N and F in both outcomes, with a paired seed-level confidence interval and all failures retained.

Secondary outcomes:
- N versus R and B; calibration/uncertainty only if defined identically before execution.
- Cold-restart delta relative to uninterrupted inference.
- Wall time, CPU time, peak memory, interaction count, artifact size, crash/restart count and full run ledger.

Decision:
- **Support for the bounded native-memory claim:** the witness construction passes independently; N exceeds F on both primary outcomes by a preregistered minimum practical effect of 5 percentage points; the 95% paired seed-level interval for N−F excludes zero for witness-pair accuracy; cold-restart witness-pair accuracy degrades by no more than 5 percentage points; and there is no information, split, budget or receipt violation.
- **No-go:** a primary threshold fails, a conventional control matches/exceeds N on the primary outcomes, cold restart fails, or any hidden information leaks.
- **Inconclusive:** fewer than the preregistered minimum valid seeds remain, source identity drifts, witness labels cannot be independently validated, or a required receipt is absent. Do not recategorize an inconclusive/failed run as a positive.

A 5-point practical-effect threshold is a proposed criterion and must be accepted by the existing scientific admission authority before data collection; it must not be changed after seeing outcomes. Report raw counts and confidence intervals alongside rates. Preserve failed, invalid, crashed and zero-score trials in the results ledger.

## 7. Budgets and stop rules

Per arm: max 1,000,000 training environment steps total across the frozen training seed set, max 200 validation episodes per candidate configuration and max 200 DEV episodes per arm; max 20 VALID-selected configurations per trainable arm. Fixed wall-clock/resource ceilings and software versions must be added to the signed admission receipt before execution.

Stop immediately on source/identity drift, any protected-data exposure, seed overlap, unequal budgets, unplanned retry, worker ambiguity, lost durable receipt, or unauthorized process launch. No paid API. Do not access brokers or unrelated controller queues. Do not start a competing scheduler.

## 8. Required evidence before execution

The package is not executable until all are present:
1. Exact clean code/dependency/toolchain and task-source identities.
2. Passing G29 on the exact candidate commit on Linux and Windows, plus one required final system regression.
3. Independently verified same-final-observation/different-history witness and frozen witness-scoring implementation.
4. Exact learner/control versions, preprocessing, checkpoint/persistence contract, seed-list hashes, and resource limits.
5. Independently authenticated FSA authority, durable admission receipt, one-shot worker consumption/start/terminal receipts and ambiguity recovery under the existing FORGE authority.
6. The admission authority's explicit decision accepting this preregistration.

**No episodes or training are authorized by this document.** Creating this file, passing source tests, or merging its text cannot substitute for FSA admission. No accepted baselines, scientific thresholds, or promotion refs are mutated here.
