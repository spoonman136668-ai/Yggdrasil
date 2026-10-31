# MR32-O — multi-step task utility and delayed episodic credit assignment

**Protocol status:** frozen before executable implementation and before the first MR32-O task event.  
**Classification:** synthetic controlled development only. No original-source execution, FSA first-use, accepted-ref update, integration or promotion.

## 1. Question and falsifiable claim

Does a bounded eligibility-trace memory allocator learn which *retrieved memories* contribute to completion of a multi-step task when the only task feedback arrives after the entire episode, and does temporal credit assignment improve held-out terminal task success over uniform episodic credit, a stronger interaction-capable learned controller, and simple selection baselines?

This is a memory-selection / delayed-credit experiment. It does not test native architecture superiority, external source-family transfer, open-ended causal discovery or general intelligence.

The candidate is **DECA-Q16** (Delayed Episodic Credit Assignment), a fixed-point scorer that accumulates a frozen eligibility trace for each memory actually used during an episode and allocates the terminal paired task-return difference across those memories only when the episode ends.

## 2. Frozen identity and scope

- Repository: \`spoonman136668-ai/Yggdrasil\`.
- Development parent: MR32 branch head \`447ab6ac3cecf8a03379bf46c13d1845f410cfb2\`.
- Existing MR32-H, MR32-M and MR32-N sources and receipts are read-only historical context. This experiment does not edit, tune, replace or import the MR32-H allocator.
- S4C1 is retained as a reference only: MR34I12 PR #487 head \`7f58e0b4dd652306ae18b292966c71678f24fd73\`; terminal four-host evidence run #40051678635. Its all-four-host trained checkpoint reproducibility passed, but its frozen Farama CPU ceiling failed; its final disposition remains \`MR34I12_PORTABLE_RECURRENT_NUMERICS_NO_GO\`. No S4C1 code, weights or runtime are imported by MR32-O.
- FSA-04 FORGE issue #83 remains OPEN. Independent science authority, private-vault/off-provider custody and protected first-use are not established. MR32-O is therefore restricted to its own deterministic source-only task fixture.

## 3. Task environment and delayed outcome

Each episode contains exactly 12 public query events and three hidden goal events.

- The memory bank contains exactly 16 immutable records. Each record has a public item identifier, a frozen proposed binary action, and five public metadata fields: evidence level, prediction-error level, contradiction level, use count and recency.
- At each event the policy observes only the current public item identifier. It does not receive goal membership, goal order, target action, per-step correctness, progress, reward-to-go or evaluator-private state.
- If the queried record is active, the actor emits its stored proposed action and that retrieval is recorded as an actual memory use. Otherwise it emits the fixed no-memory fallback action \`0\`.
- The deterministic task fixture secretly chooses three distinct goal positions from the 12 events. The three goal events must all be answered correctly, in their event order, for terminal return \`1\`; otherwise terminal return is \`0\`. Distractor events do not advance the hidden goal chain. The fixture returns no intermediate reward or correctness signal.
- For every policy/episode the evaluator runs the identical deterministic episode twice: once using that policy's memory selections and once with all memory retrievals disabled (the fixed fallback action on every event). The evaluator computes \`delta_return = terminal_return_with_policy - terminal_return_no_memory\`, in \`{-1, 0, +1}\`.
- The policy receives this one scalar **only after event 12**. It receives no item-specific correctness labels, no counterfactual per-memory ablation labels and no feedback for memory records it did not actually retrieve. The evaluator may calculate per-memory leave-one-out effects as sealed diagnostics after decisions; those diagnostics are never fed to any learner.

The two deterministic task regimes use different frozen metadata-to-action reliability mappings. The mappings are task-generator code, not exposed labels. Task event and terminal-return generation uses integer thresholds and deterministic pseudorandom streams; no floating-point probability sampling or model calls are used.

## 4. Fixed budgets, arithmetic and mechanisms

All methods use the same 16 memory records and exactly 7 active / 9 retained positions. The public item encodings, proposed actions, metadata, query order, task budget and hidden task stream are identical across methods.

All learned selectors use integer Q16 fixed-point state and arithmetic. The candidate trace coefficient is frozen at \`lambda_q16 = 52429\` (nearest integer representation of 0.8). At terminal time, event-use eligibility is \`lambda_q16 ** (11 - event_step)\` in Q16 arithmetic, normalized across actual memory uses so the total credited episode delta is conserved. Each use stores its feature vector at selection time; later recency/use metadata cannot rewrite that receipt.

Required methods:

1. **Random:** deterministic seeded 7-of-16 active selection, independent of task outcomes.
2. **Fixed recency:** 7 most recently used records, with immutable key tie-break; no task-outcome learning.
3. **Evidence-only:** top 7 by frozen evidence count, then immutable key; no task-outcome learning.
4. **Uniform episodic Monte Carlo control:** same six-feature Q16 linear utility model and learning rate as DECA-Q16, but allocates the delayed episode \`delta_return\` uniformly across every memory actually used in that episode.
5. **Interaction learned control:** a separately implemented Q16 linear utility predictor with the same five public metadata fields plus all pairwise interactions; it receives the same single terminal \`delta_return\` for every memory actually used, with no per-step or per-memory oracle labels.
6. **DECA-Q16 candidate:** same base feature vector and learning-rate budget as uniform episodic Monte Carlo, but assigns delayed episode credit using the frozen normalized eligibility trace described above.

The prior MR32-H additive scorer is **not** reimplemented, retuned or included as a new candidate. Its frozen MR32-M terminal negative remains a prior result, not new evidence for MR32-O.

## 5. Cohorts and execution order

Seed clusters are frozen now; no unlisted seed is accepted.

**FIT — 16 clusters, 8 per regime, 8 episodes per cluster = 128 episodes.**  
Seeds:
\`101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179\`.

Regime 0 uses the first eight FIT seeds; regime 1 uses the final eight.

**TRANSFER — 32 disjoint clusters, 16 per regime, 8 episodes per cluster = 256 episodes.**  
Seeds:
\`1009, 1013, 1019, 1021, 1031, 1033, 1039, 1049, 1051, 1061, 1063, 1069, 1087, 1091, 1093, 1097, 1103, 1109, 1117, 1123, 1129, 1151, 1153, 1163, 1171, 1181, 1187, 1193, 1201, 1213, 1217, 1223\`.

Regime 0 uses the first 16 TRANSFER seeds; regime 1 uses the final 16.

Only FIT episodes may update learned selector parameters. TRANSFER parameters are frozen. All methods see identical task-event seeds, public query events and task outcomes. Policy-specific actual memory-use receipts can differ because selected active sets differ. No TRANSFER feedback may enter any selector.

## 6. Primary endpoint and frozen acceptance

**Primary endpoint:** mean terminal task-success return (0 or 1) per TRANSFER episode, paired by 32 seed clusters. Report per-regime results, no-memory terminal return, paired \`delta_return\`, actual memory-use counts and evaluator-only per-memory leave-one-out diagnostics.

A DECA-Q16 development signal requires every condition:

- DECA-Q16 exceeds **each** random, recency, evidence-only, uniform Monte Carlo and interaction learned controls by at least **0.02 absolute terminal-success units**.
- DECA-Q16 wins against the strongest comparator in at least **24 of 32** TRANSFER seed clusters.
- DECA-Q16 wins in at least **12 of 16** clusters within **each** regime.
- A deterministic paired cluster bootstrap (10,000 resamples; fixed seed \`320014\`) has a 2.5th percentile above zero against the strongest comparator.
- TRANSFER feedback is exactly zero for every learned selector; FIT/TRANSFER seed sets are disjoint; all pending-credit and use-time-feature receipts reconcile.
- Windows and Ubuntu reproduce identical FIT/TRANSFER event hashes, policy decisions, terminal-return arrays, per-cluster scores and fixed-point model/checkpoint bytes.
- DECA-Q16 serialized learned state is no more than **1.25x** the uniform Monte Carlo control, and its measured per-method CPU is no more than **1.25x** that control. Record complete-process peak RSS, wall time, all model checkpoint bytes and per-method CPU regardless of outcome.

Any failed condition is a frozen negative or inconclusive result. No threshold, seed, environment mapping, feedback rule, feature, lambda, controller or task endpoint may be adjusted after TRANSFER is inspected. A development pass does not confer scientific admission.

## 7. Receipt contract

The result must include:
- exact protocol file blob SHA and exact source commit / changed source blob SHAs;
- deterministic task-generator version and FIT/TRANSFER event hashes;
- each episode's public event stream, selected-memory identifiers, use steps, terminal return and no-memory return;
- a pending-credit receipt per selected memory with its immutable use-time feature vector and eligibility integer;
- terminal feedback delivery time (episode end), exact delta, normalized integer credit assigned to each used memory and fixed-point update receipt;
- per-method fitted checkpoint bytes and SHA256, cold-restore parity, selector state bytes and model parameter counts;
- per-method CPU, full-process peak RSS and wall time; OS, Python and runtime identity;
- per-seed-cluster paired results, per-regime summaries, bootstrap bounds and all frozen falsifier booleans.

## 8. Governance and stop conditions

- Source-only synthetic fixture. No Farama, Pycolab, MiniGrid, Crafter, Gridworlds or protected original source execution.
- No consumption, inference or claim of independent source-family first-use.
- No changes to S4C1, MR32-H/M/N historical code or receipts, native R7, accepted refs, original task engines, FORGE, Wingless, production runtime, controllers, queues or schedulers.
- FSA-04 #83 remains the independent science authority boundary. No protected source experiment can start until its prerequisites are independently established and authorized.
- No atlas waiver, merge, promotion, release, deployment, runner/controller mutation or paid API.


## 9. Exact task-generator and fixed-point specification

This section is frozen before executable task code.

### Memory bank

For public item IDs 0 through 15:

- \`evidence_level = item % 8\`; public evidence count is \`2 ** evidence_level\`.
- \`error_level = (item // 2 + item // 8) % 4\`.
- \`contradiction_level = (3 * item + item // 4) % 4\`.
- Public proposed action is \`(item * 7 + 3) & 1\`.
- Metadata and proposed action remain immutable throughout FIT and TRANSFER. They do not encode the hidden task goal or correct action.

For regime 0, the hidden probability (basis points) that the proposed action is correct is:
\`clamp(5600 + 400*evidence_level - 450*error_level - 300*contradiction_level, 2000, 9500)\`.

For regime 1 it is:
\`clamp(5200 + 160*evidence_level - 250*error_level - 150*contradiction_level + 200*evidence_level*(3-contradiction_level), 2000, 9500)\`.

The two reliability functions are evaluator-only task-generation rules. No probability or correctness label is delivered to a policy.

### Episode stream

- \`episode_seed = (cluster_seed * 1000003) XOR (regime * 97409) XOR (episode_index * 65537) XOR 0x4D52324F\`.
- Initialize \`random.Random(episode_seed)\`; choose the 12 public item IDs with \`sample(range(16), 12)\`; choose three distinct hidden goal positions with \`sorted(sample(range(12), 3))\`.
- For goal index \`g\` at hidden position \`p\`, let \`item = query_stream[p]\`; initialize a separate RNG with \`episode_seed XOR (item * 257) XOR (g * 65537) XOR 0x4F445543\`. Draw \`randrange(10000)\`. The hidden required action equals the stored proposal if the draw is below the regime/item reliability in basis points; otherwise it is the opposite bit.
- The policy receives only the 12 sequential public observations \`(step, item_id)\`. It does not receive the hidden goal positions, goal index, required action, correctness, stage/progress or any reward before episode termination.
- A task is complete only if all three hidden goal events are answered correctly in event order. The episode terminal return is exactly 1 for completion and 0 otherwise. No partial or intermediate reward is exposed.
- The evaluator-only no-memory paired replay uses action 0 on every event of the same episode. It is not a second sampled task and supplies no additional policy observation.
- Each item ID appears at most once per episode, so a selected record has at most one use receipt in that episode.

### Q16 arithmetic

- \`Q = 65536\`; all learned weights, feature values, predicted utilities, reward deltas, eligibility and credit allocations are signed/integer Q16. No floating-point model arithmetic, transcendental functions or platform BLAS are used.
- Base feature vector (six integers): bias \`Q\`; evidence \`evidence_level * Q // 7\`; error \`error_level * Q // 3\`; contradiction \`contradiction_level * Q // 3\`; recency \`Q // (1 + age)\`; and use count \`min(uses,16) * Q // 16\`. Age is the event-clock difference from the last actual use; initial \`last_used=-1\`, \`uses=0\`.
- Interaction-control feature vector adds all ten pairwise products of the five non-bias features, each computed as \`(x_i * x_j) // Q\`, for exactly 16 coefficients including bias.
- Prediction is \`clamp(sum(weight_i * feature_i) // Q, -Q, Q)\`. Weights start at zero and clamp to \`[-4*Q, 4*Q]\`. The frozen learning-rate integer is \`alpha_q16=5243\`.
- For each terminal paired outcome, \`delta_q16 = (terminal_return_with_policy - terminal_return_no_memory) * Q\`.
- Uniform episodic Monte Carlo divides \`delta_q16\` equally among the records actually used in that episode. DECA-Q16 uses \`lambda_q16=52429\`; its raw eligibility for a use at step \`t\` is repeated Q16 multiplication of lambda over \`11-t\` delays. Normalize those eligibilities so their integer credits sum exactly to \`delta_q16\`; assign any integer-division remainder to the most recently used record. This prevents the trace candidate from receiving a larger total episode signal than the uniform control.
- The interaction learned control uses the same uniform conserved episode-credit allocation and the fixed 16-feature interaction basis. The only candidate-vs-uniform difference is temporal eligibility weighting; the interaction control is the stronger richer-feature comparator.
- For each used record and its immutable use-time feature receipt, compute \`error_q16 = credit_q16 - prediction_q16\`; update each coefficient by \`floor(alpha_q16 * error_q16 * feature_q16 / Q^2)\`, then clamp. Update only after the terminal episode return is available. No unselected record receives feedback.

### State and transfer semantics

All six selectors start from the same 16-record bank and exactly seven active / nine retained entries. Learned policies update their active set by descending predicted utility, then immutable item ID. The random, recency and evidence-only controls are deterministic under their frozen seed/tie rules. FIT carries each policy's own learned weights, usage counters and checkpoint state across its 128 episodes. TRANSFER begins from each FIT terminal checkpoint; each transfer seed cluster gets a cold copy of that checkpoint, executes its eight episodes without task-outcome updates, and records any public use/recency state changes separately from learned-weight changes.

The canonical checkpoint is JSON with sorted keys and compact separators, protected by SHA256. Cold restore must preserve exact next active set, next action selection, fixed-point predictions, usage counters and learned weights.

## 10. Exact primary-result computation

For each of the 32 TRANSFER seed clusters, compute each policy's mean terminal success over its eight episodes. Aggregate mean return is the unweighted mean of the 32 cluster means; each cluster has equal weight. Paired cluster differences are candidate minus comparator. Bootstrap resampling samples 32 cluster indices with replacement, 10,000 times, using \`random.Random(320014)\`; sort the resulting means and report element 249 (zero-based) as the frozen 2.5th-percentile lower bound. Win counts compare paired cluster means strictly (\`candidate > comparator\`); ties are not wins.
