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
