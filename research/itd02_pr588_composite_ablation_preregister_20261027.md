# ITD-02 PR588: precommitted source-free composite ablation (development only)

**Read this before the runner and experiment implementation.** This statement fixes experiment constraints before evaluator/workflow code is added. No original Shuttle/FSA/held-out protected task data, native accepted refs, controllers or scientific permission. No tuning after outcomes. The candidate and all parents are exact frozen Git identities.

## Immutable model roots
- baseline: `e8c7dca8966a7d2721f49df2a9ac4c7419921097`
- exploration: `3723afc95cbe5d3355b54b479499036499c7183f`
- recency: `a39171a76d0d7817e3563682bb139a9d7ecf37c4`
- composite: `c92d0ff4f1cda4ba2714f1066d37b3cc48e46626`

On each variant the original `NativeTaskRingBridgeDev` chooses and updates its own action via source-public feedback and preserves local eight-cell memory, genuine LocalTaskRuntime, sealed checkpoint and no external suggestion of the selected action. Only the exploration and local-reward-recency switch differs in the already-existing frozen code trees:
- baseline = original bounded native greedy chooser + original local reward rule
- exploration = opt-in model-owned `choose_training(exploration_period=9, bootstrap_calls=18)` + original local reward rule
- recency = greedy `choose()` + recency reward rule
- composite = opt-in `choose_training(exploration_period=9, bootstrap_calls=18)` + recency reward rule

## Independent controls and matched information
Use independently acting count-mean and EMA(alpha=0.5) and rolling-six-mean public-observation/action policies, each taking the same number of real chosen feedback opportunities. Their own deterministic source-blind per-context first-three-action coverage and every-ninth-action coverage is permitted and must be disclosed (native arms may choose different actions). No shared fit state, reward predictions, hidden evaluator law, suggested action, cross-arm training or copied weights. The evaluation source alone maps actual current (observation, selected action, family, phase) to 10 / -3; only the resulting public reward is delivered.

Fix 6 enumerated synthetic task families (IDs 312..317), 2 independent seeds (931,937), 48 genuine selected feedback transitions per phase per arm: phase initial on LRV/MRV, phase unfamiliar on docked_LRV/docked_MRV, phase shifted on LRV/MRV with goal-action mapping rotated. Exactly 12 trials per arm, 144 accepted feedback events/trial, 1728/arm, 12096 across seven arms. Unfamiliar-context frozen readout happens BEFORE its online feedback, then after; reward-shift frozen readout before/after the corresponding feedback. Public observations only; no source-private data in the learner.

Require byte-identical native cold restore after each phase, preserved update count, zero pending actions, strict freeze during score probing, exact action/reward accounting, 7 acting variants and environment/clock isolation across arms. Record per-phase cumulative selected public reward, frozen choices and reward on both seen/unfamiliar tasks, feedback/update counts, checkpoint bytes, CPU time, process highwater RAM if available and Python allocation peak. Both Ubuntu and Windows hosted environments; these are not consumer-PC performance claims. If a platform cannot measure RSS, state it is unavailable.

## Decision
This is **synthetic source-free development** evidence, not independent scientific first-use, general transfer proof, full causal intelligence, or automatic promotion. Classify raw engineering completeness separately from learning:
- **Mechanistic supported** only if composite exceeds the strongest individual native variant and strongest conventional independent control on preregistered metrics across families, without an important cold-retention/resource regression. Do not post-select a favored family, seed, measure or test mode.
- Otherwise report NEGATIVE/MIXED/INSUFFICIENT. No minimum improvement threshold is loosened in response to data.
- Hold PR #588 draft regardless of result; no merge, acceptance, new scheduler, protected trial, native source modification or controller change.

This preregistration commits only planning text. Subsequent evaluator/CI changes do not alter these constants or model roots.
