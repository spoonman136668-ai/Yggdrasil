# MR32-P — exact counterfactual episodic credit for learned memory selection

**Status:** protocol-only; frozen before implementation and before any MR32-P task event.  
**Classification:** deterministic synthetic development only. No original-source execution, FSA-04 first-use, scientific admission, integration or promotion.

## 1. Question

Does exact counterfactual attribution of terminal task success to the memories actually used in a multi-step episode improve future memory selection beyond uniform terminal credit and leave-one-out credit?

The proposed candidate is **Shapley-Q16**: for the seven memories selected and actually used in an episode, replay every coalition of those memories under the identical task episode. Compute exact Shapley values from the resulting terminal task returns. Deliver only those post-episode, task-return-derived credits to the candidate learner.

This tests memory selection and delayed causal credit allocation. It does not establish general intelligence, source-neutral transfer, original-world performance, or superiority of Yggdrasil's overall architecture.

## 2. Historical boundary and baseline preservation

- Repository: \`spoonman136668-ai/Yggdrasil\`.
- Development parent: \`68f21c26e9cf42390cd1e09d2a2403011827d3cb\`, which preserves the closed MR32-O negative verdict.
- MR32-H and MR32-O are read-only historical results. Do not change their code, protocol, thresholds, cohorts, receipts or verdicts.
- MR32-O exact-head engineering qualification passed on Windows and Ubuntu (21/21 focused tests each; exact cross-platform event/checkpoint/score parity). Its frozen scientific result was NO-GO: DECA-Q16 mean terminal success trailed uniform episodic Monte Carlo by 0.04296875. Its TRANSFER seeds are consumed and prohibited from reuse.
- S4C1 remains a reproducible implementation reference only. Its multi-host numerical reproducibility passed, but the frozen Farama efficiency ceiling failed. It is not imported into MR32-P.
- FORGE FSA-04 issue #83 remains OPEN. Independent science authority, independent durable custody/restore and protected first-use are not established. MR32-P is restricted to a new synthetic source-only development cohort.

## 3. Causal estimand and evaluator interface

For one policy and one episode, let \(N\) be the set of the seven memory records actually retrieved in that episode. The policy sees the same public 16-item query permutation as every other method. Each record appears exactly once, so every selected active record has one real use receipt.

For every coalition \(S \subseteq N\), the evaluator reruns the deterministic 16-step episode from the same initial world state and public query permutation:
- if the current queried record is in \(S\), use the exact action recorded for that memory in the original policy rollout;
- otherwise, use the fixed no-memory fallback action \(0\);
- all task transitions execute normally, so removing a memory can change the downstream state trajectory and terminal outcome;
- all task randomness, target state and event order are held identical across every coalition.

Let \(v(S) \in \{0,1\}\) be the episode's terminal success from that replay. The empty coalition \(v(\varnothing)\) is the paired no-memory baseline; \(v(N)\) is the original policy's task return. There are exactly \(2^7=128\) coalition replays per policy/episode, including both endpoints.

The exact Shapley value for selected memory \(i\) is:

\[
\phi_i = \sum_{S \subseteq N \setminus \{i\}}
\frac{|S|!(7-|S|-1)!}{7!}\left(v(S\cup\{i\})-v(S)\right).
\]

This gives an additive, interaction-aware allocation of the actual terminal-return difference: \(\sum_{i \in N}\phi_i = v(N)-v(\varnothing)\). It handles redundancy, synergy, positive contributions and harmful contributions without treating the leave-one-out marginal as an additive decomposition.

**Only the following crosses the evaluator/policy boundary after event 16:** the signed per-memory Q16 Shapley credits, the corresponding public use-time feature receipts, and a receipt that the episode ended. The policy receives no target, hidden role weights, internal environment state, per-step reward, per-step correctness, coalition membership table, coalition outcomes, hidden target location, or evaluator diagnostics.

The evaluator must keep the complete coalition value table and all hidden task state in a separate evaluator object. The learner update API accepts only the serialized public use receipts plus the final signed Q16 credit vector. It must not accept an evaluator object, task spec, hidden target, coalition mask or terminal-state structure.

## 4. Deterministic multi-step task fixture

The task fixture is an 11-state modular route world with 16 unique public cue IDs per episode.

### Memory bank

For memory item \(i \in \{0,\ldots,15\}\):
- \`evidence_level = i % 8\`; public evidence count is \(2^{evidence\_level}\).
- \`error_level = (i // 2 + i // 8) % 4\).
- \`contradiction_level = (3*i + i // 4) % 4\).
- Proposed stored action is \`(7*i + 3) & 1\`.
- Initial use count is zero; initial last-used clock is -1.

These public metadata/action fields are identical across all methods. No record contains the target state or a hidden role label.

### Episode task

- The public query stream is a deterministic permutation of all 16 item IDs, sampled without replacement from a seed/regime/episode-derived integer seed.
- Initial world position is \`seed % 11\`.
- At each step, the policy receives only the public \`(step, item_id)\`. It does not receive current world position or target.
- If the queried memory is active, the actor uses the record's stored action; otherwise it uses fallback action 0.
- Evaluator-only world transition for action \(a\in\{0,1\}\), current state \(x\), item \(i\), and regime \(r\):
  \[
  x' = \left(x + (2a-1)(1+e_i) + (i \bmod 3) + 1 + r\right) \bmod 11,
  \]
  where \(e_i\) is the item's public evidence level.
- The evaluator derives the hidden terminal target from the complete public cue permutation using a frozen regime-specific role-weight mapping:
  - regime 0 weights by \`item_id % 4\`: \`(1, 3, 2, 5)\`;
  - regime 1 weights by \`item_id % 4\`: \`(4, 1, 5, 2)\`.
  \[
  target = \left(seed \bmod 11 +
  \sum_{i\ in\ query} \left((i+1)w_{i\bmod4} + 2e_i + 3q_i - c_i\right)\right) \bmod 11,
  \]
  where \(e_i,q_i,c_i\) are evidence, error and contradiction levels. The target and weights are evaluator-only, not public inputs to the policy.
- The episode terminal return is exactly 1 if the final world position equals the target and 0 otherwise. No intermediate reward or success signal is exposed.

The evaluator's deterministic transition/target implementation must be unit-tested independently against hand-calculated examples before it is used to generate any cohort. The policy-facing task runner must be a separate interface from the evaluator's hidden task-spec type.

## 5. Credit methods and selection controls

All learned selectors use the same six-coefficient Q16 linear utility model, same feature vector, learning rate, initialization, update ordering, training episode count, 16-record capacity and seven-active/nine-retained partition. The credit estimator is the sole intended treatment difference.

Required methods:
1. **Random selector:** seeded 7-of-16 active selection, no learning.
2. **Fixed recency:** choose seven by descending actual-use clock, then immutable item ID; no learning.
3. **Evidence-only:** choose seven by descending evidence count, then immutable item ID; no learning.
4. **Uniform episodic Monte Carlo:** divide \(v(N)-v(\varnothing)\) equally across the seven actually used memories.
5. **Leave-one-out learned control:** for each selected memory \(i\), use \(v(N)-v(N\setminus\{i\})\) as its feedback. These marginal values are deliberately not normalized; they can over/under-count interactions and are retained as a strong, transparent counterfactual baseline.
6. **Exact Shapley-Q16 candidate:** use the exact 7-player Shapley values from the complete coalition table. These credits sum to the terminal delta exactly after deterministic Q16 quantization/remainder allocation.

The three learned selectors have identical six public features:
\`[Q, evidence_q16, error_q16, contradiction_q16, recency_q16, use_count_q16]\`,
where \(Q=65536\), evidence is \`evidence_level*Q//7\`, error and contradiction are \`level*Q//3\`, recency is \`Q//(1+age)\`, and use count is \`min(uses,16)*Q//16\). Features are frozen at actual use time. No future query, world state or hidden label is included.

All learned weights initialize to zero and are bounded to \([-4Q,4Q]\). Prediction is \`clamp(sum(w_j*x_j)//Q,-Q,Q)\`. Learning rate is frozen at \`alpha_q16=5243\`. Model update is applied only after all 16 events and terminal outcome are complete. The learner processes its seven public use receipts in event-step order, updates from each method-specific signed credit, and cannot change weights while the episode is running.

### Exact Q16 Shapley quantization

For \(k=7\), each Shapley weight is an exact rational with denominator \(7!\). The implementation must compute coalition differences and the weighted numerator with integer arithmetic only. Convert the seven rational values to signed Q16 by floor division, then assign the remaining Q16 integer units in immutable item-ID ascending order until the allocated credits sum exactly to \((v(N)-v(\varnothing))Q\). Report the pre-quantized exact rational numerators and all final integer credits. The quantization correction is deterministic and must not depend on dict/set iteration order.

Uniform and leave-one-out controls use the same Q16 credit scale, same model update rule, and the same immutable use-time feature snapshots.

## 6. Exact evaluator work and fairness

Each policy uses exactly seven active memories and the query stream contains every item exactly once; therefore every policy has exactly seven actual memory-use receipts and exactly 128 coalitions per episode. The evaluator computes and stores the full 128-value coalition table for every policy. This fixes counterfactual evaluation work across random, recency, evidence-only, uniform, leave-one-out and Shapley methods.

Only the corresponding credit representation is passed to each learned selector. Non-learning controls do not consume or update from credit signals. Report per-method policy CPU, coalition evaluator CPU, total task transitions, checkpoint size, full-process CPU, wall time and peak RSS. Separate learner work from the common 128-coalition evaluator work. Candidate-versus-control resource comparison must include the incremental Shapley allocation and Q16 update cost, not just parameter count.

## 7. Cohorts and execution order

Only the frozen seeds below are valid. Reject any seed not listed. The seed lists are disjoint from MR32-M and MR32-O.

**FIT:** 16 independent seed clusters, eight per regime, eight episodes per cluster = 128 episodes. Regime 0 uses the first eight seeds; regime 1 the final eight:
\`2003, 2011, 2017, 2027, 2029, 2039, 2053, 2063, 2069, 2081, 2083, 2087, 2089, 2099, 2111, 2113\`.

**TRANSFER:** 32 independent seed clusters, 16 per regime, eight episodes per cluster = 256 episodes. Regime 0 uses the first 16 seeds; regime 1 the final 16:
\`3001, 3011, 3019, 3023, 3037, 3041, 3049, 3061, 3067, 3079, 3083, 3089, 3109, 3119, 3121, 3137, 3163, 3167, 3169, 3181, 3187, 3191, 3203, 3209, 3217, 3221, 3229, 3251, 3253, 3257, 3259, 3271\`.

Only FIT outcomes may update learned-selector weights. After FIT, checkpoint each learned selector and verify cold restore. Every TRANSFER cluster starts independently from the exact same method-specific FIT terminal checkpoint; do not carry public counters or recency/use state from one TRANSFER cluster into another. Learned weights remain frozen throughout TRANSFER. No TRANSFER terminal reward, coalition table, Shapley value or counterfactual diagnostic may update any policy.

## 8. Frozen endpoints and acceptance thresholds

**Primary endpoint:** mean terminal route success (0/1) per TRANSFER episode, paired within the same 32 seed clusters and public task episode streams.

A Shapley-Q16 development signal requires every condition:
- Shapley-Q16 exceeds each random, fixed-recency, evidence-only, uniform Monte Carlo and leave-one-out learned selector by at least **0.02 absolute terminal-success units**.
- Shapley-Q16 wins against the strongest comparator in at least **24 of 32** TRANSFER seed clusters.
- Shapley-Q16 wins in at least **12 of 16** clusters within each regime.
- A deterministic paired cluster bootstrap (10,000 resamples; fixed seed \`320116\`) has a 2.5th percentile strictly greater than zero against the strongest comparator.
- FIT and TRANSFER seeds are disjoint; all 128 coalition replays per policy/episode reconcile; Shapley efficiency holds; every use receipt is immutable; and TRANSFER feedback count is exactly zero.
- Windows and Ubuntu reproduce identical FIT/TRANSFER task-event hashes, all 128 coalition-value tables, fitted weights/checkpoint SHA256s, per-seed terminal returns, cluster differences and frozen verdict.
- Candidate checkpoint bytes and incremental policy/update CPU are each no more than **1.25x** the leave-one-out learned control. Also report all-in evaluator and process resources.

Comparator tie order is fixed: \`random\`, \`fixed_recency\`, \`evidence_only\`, \`uniform_mc\`, \`leave_one_out\`; exact aggregate ties are resolved in favor of the earliest method. The inclusive +0.02 Q16 threshold is \`ceil(0.02*65536)=1311\`. The bootstrap lower bound must be strictly positive. Cluster ties are not wins.

Any failed condition is retained as a negative or inconclusive result. No threshold, seed, task rule, feature, learning rate, cohort, evaluator method or stopping condition may be changed after TRANSFER is inspected. A pass is controlled synthetic development evidence only, not scientific admission.

## 9. Identifiability, leakage and mechanism-review gates

Implementation and execution are prohibited until the following source-only tests and review receipts exist:

1. **Shapley efficiency:** for every generated episode and every policy, the seven exact rational Shapley contributions sum to \(v(N)-v(\varnothing)\); the final Q16 credits sum exactly to its Q16-scaled value.
2. **Additive games:** a game \(v(S)=b+\sum_{i\in S}a_i\) must return exactly \(a_i\) for every player.
3. **Pure synergy:** for a two-player interaction where only the full coalition succeeds, exact Shapley must allocate one half to each; the seven-player fixture must give zero to null players.
4. **Redundancy:** for two interchangeable sufficient records, credit is split equally; removing either one individually must not be misrepresented as zero shared contribution.
5. **Harmful memory:** a record whose inclusion changes success to failure receives negative Shapley credit; a null record receives exactly zero.
6. **Order permutation:** permuting item IDs and replay order while preserving the coalition game must preserve credit attached to the corresponding semantic player.
7. **No evaluator leakage:** policy decision traces must be byte-identical when hidden task target/role weights are changed but the public stream and policy state are held fixed up to episode end. No hidden spec object, target value, intermediate state, coalition table or transfer outcome may appear in learner inputs.
8. **Counterfactual determinism:** all 128 coalition replays for a policy/episode must share exact public query order, initial state and environment stream; repeating an identical coalition must produce an identical terminal result.
9. **Causal interpretation boundary:** Shapley estimates contribution within this fixed task/policy coalition game. It does not prove globally necessary causes, effects under adaptive re-selection, independent source transfer or causal structure outside the synthetic simulator.
10. **Baseline isolation:** uniform and leave-one-out controls use the exact same policy feature/model/update budget; only their credit estimator differs. All selector policies get the same fixed 128-coalition evaluator budget per episode.

If any identifiability or leakage test fails, stop before FIT/TRANSFER and correct the implementation without inspecting held-out outcomes.

## 10. Evidence receipt contract

Record exact protocol blob SHA, source commit and source blob SHAs; task-generator version; every FIT and TRANSFER task event hash; all coalition returns; per-policy original and replay trajectories; actual selected-memory use receipts; exact rational Shapley numerators/denominators and quantized credits; leave-one-out and uniform credits; learner update inputs; checkpoint bytes and SHA256; cold-restore next-action parity; per-method and evaluator CPU; total state transitions; peak RSS; wall time; runtime/OS versions; per-seed-cluster and per-regime outcomes; bootstrap samples seed/bound; each frozen falsifier; and exact cross-OS reconciliation.

## 11. Governance and stop conditions

- Synthetic source-only task fixture. No Farama, Pycolab, MiniGrid, Crafter, Gridworlds or protected original-source execution.
- No protected first-use, independent source-family validation or independent scientific admission.
- FSA-04 FORGE issue #83 remains OPEN and unchanged.
- No edit to MR32-H/M/O historical code or receipts, S4C1 reference code, accepted refs, native research controllers, queues, schedulers, FORGE, Wingless or production runtime.
- No merge, promotion, deployment, release, atlas waiver, runner/controller mutation or paid API.
- This protocol freezes research design only. It does not grant execution, acceptance, source-admission or promotion authority.


## 12. Exact integer learning, update and receipt semantics

- \(Q=65536\). All model weights, features, predictions, credit signals and updates are signed integer Q16. No floating-point model arithmetic, BLAS, nondeterministic reductions or platform-specific math is permitted.
- At the start of each episode, capture the selected seven records' public feature vector at the actual-use event. The immutable feature receipt is \`[Q, evidence_level*Q//7, error_level*Q//3, contradiction_level*Q//3, Q//(1+age), min(uses,16)*Q//16]\`. Use-time feature values cannot be recomputed from the end-of-episode state.
- Prediction is \`clamp(sum(w[j]*x[j])//Q, -Q, Q)\`; each learner has six weights, initially zero and clamped to \`[-4*Q,4*Q]\`.
- For terminal delta \(d=v(N)-v(\varnothing)\), uniform control credits are \`floor(d*Q/7)\` for each used memory, then the residual integer units are assigned one per record in ascending immutable item ID until the seven credits sum exactly to \`d*Q\`.
- Leave-one-out control credit for item \(i\) is exactly \`(v(N)-v(N_without_i))*Q\`. It is not normalized; it can overcount synergy or redundancy. This is intentional and is measured as a control, not corrected after results.
- Shapley credit numerators are computed from the exact factorial-weighted sum in Section 3 with common denominator \(7!=5040\). For each item, calculate the signed Q16 credit by floor division of \`numerator*Q//5040\`. Since the exact Shapley values sum to the integer episode delta, the remaining Q16 units are nonnegative and fewer than seven; assign them one each in ascending immutable item ID. Assert \`sum(credits_q16)==d*Q\`.
- For each selected memory in ascending event-step order, compute \`error_q16=credit_q16-prediction_q16\`, then update \`w[j] = clamp(w[j] + (5243*error_q16*x[j])//(Q*Q), -4*Q, 4*Q)\`. The prediction for a receipt is computed against the model state immediately before that receipt's update. No update occurs before the terminal feedback boundary.
- All three learned selectors use exactly this same feature basis, coefficient count, initializer, clipping, learning rate and update order. Their only difference is the frozen credit estimator.
- FIT processes clusters in their listed order, episodes 0 through 7 per cluster. Each learned controller carries its own FIT-trained weights/use counts/recency across the complete FIT stream. TRANSFER starts each cluster from the exact immutable FIT terminal checkpoint; no TRANSFER state may flow from one seed cluster to another.
- A checkpoint is compact sorted-key JSON with schema/version and SHA256. Cold restore must preserve exact weights, counters, next active set and next action. Reject unknown fields, non-integer Q16 values, duplicate item IDs, invalid 7/9 partition or hash mismatch.
- Per-episode receipt ordering is fixed by \`(seed_cluster_index, episode_index, method_order, coalition_bitmask_ascending)\`; selected memory IDs and credit allocations are serialized in ascending item ID. No dependence on Python set/dict iteration is allowed.

## 13. Leakage-resistant policy/evaluator process boundary

The implementation must have two separately testable interfaces:

1. **Policy process interface:** receives only the frozen public query permutation, public memory records and public policy state; during each episode it returns the seven selected IDs and the 16 action decisions. It is not passed the environment target, transition state, regime role weights, terminal outcome, coalition masks, coalition-return table or evaluator callback.
2. **Evaluator interface:** receives the deterministic private task spec and the frozen policy action/use receipt. It performs the 128 counterfactual replays and returns a terminal coalition-value receipt to the experiment harness. The harness converts that table to the selected estimator's allowed per-use credit vector and only then calls the policy's post-episode learner update API.

The experiment harness must serialize and validate the policy input/output contract. The post-episode learner API must reject unrecognized fields and reject any attempt to update before the end-of-episode marker. The hidden target/state and complete coalition table remain outside the policy process. This is an information-boundary test, not a claim of cryptographic secrecy against an operator who can inspect evaluator source.

The public task permutation is the same across methods; the hidden target and transition state are identical across coalition replays. Counterfactual replays hold the original policy's seven selected IDs and proposed actions fixed: they intervene only on whether each selected memory's action is admitted, and let the environment evolve normally from the beginning. This defines the causal estimand as the selected memory's contribution within the realized policy's fixed episode coalition game, not as a global effect under re-running the memory selector.

## 14. Static feasibility review before implementation

Before the first MR32-P task execution, commit a review receipt establishing:
- 128 coalition bitmasks are exactly the complete powerset for seven players, with no duplicate or missing mask;
- replay engine is deterministic under fixed episode/coalition identity;
- the policy cannot access the evaluator's hidden target or coalition table through function arguments, shared mutable state, imports, filesystem, environment variables or receipt objects;
- exact Shapley test fixtures cover additive, null, pure synergy, interchangeable redundancy, harmful record, negative episode delta, item permutation and integer remainder cases;
- all methods receive the same 128 replay evaluator budget per episode and identical task/query streams;
- source task generator uses integer-only deterministic operations and identical event/target hashes across Windows and Ubuntu;
- the protocol seed lists are disjoint from both MR32-M and MR32-O historical cohorts;
- no executable cohort is run until the protocol, static feasibility review and focused identifiability tests are committed and frozen.

If exact Shapley or evaluator isolation is infeasible within the frozen budgets, record a protocol-level NO-GO and stop. Do not replace exact Shapley with a cheaper approximation after seeing cohort outcomes.
