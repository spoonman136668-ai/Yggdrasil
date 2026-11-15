# FKP-17 — High-first 128-step original Memory Gym action-plan headroom

**SOURCE IDENTIFIABILITY RESEARCH ONLY. NOT native Yggdrasil integration or learned intelligence.** This study succeeds FKP-16 [PR #1107](https://github.com/spoonman136668-ai/Yggdrasil/pull/1107), whose **193,525 original source actions** produced no direct-memory improvement over conventional counts and zero goals for all learned policies at H16. There was still a physically measured privileged best-of-nine 16-step oracle return of +0.15625. The question is whether extending **actual consequential** action plans to H128, with nonconstant phases and public-reward feedback, creates an action-goal learning task with enough attainable reward signal to justify spending fresh held data on a true temporal learner.

## Source and custody

- Prereg-only first commit: `11133597b3e0e59dcb27e0c563e30d6b150287e1` BEFORE writing FKP-17 source or opening new 128-step branch outcomes; read `prereg.json`. No post-result design or threshold changes.
- Isolated research parent: FKP-16 finished source-qualified draft SHA `2de698ceedb28572ebb535a956c7b7e66e2cedad` (not native `main`). Accepted Yggdrasil baseline `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` remains unchanged.
- Original unmodified MIT external `MarcoMeter/endless-memory-gym@a94f2b60d1769ea44df3226561488768e1dff9f4`, exact five upstream blobs and clean Git worktree checked via retained FKP10 source admission. `MysteryPath-v0`, publicly configured `reward_fall_off=-0.05,max_steps=512`; NOT the default leaderboard benchmark.
- FIT worlds `975100..975107` and source AUDIT worlds `975200..975207` are **previously exposed FKP-16 training/validation source**. New H128 physical consequences on these same worlds are useful *source development*, **NOT independent original DEV or fresh protected scientific first-use**. FKP16 original DEV `976500..976531` already consumed and **disarmed**. Transfer `976600..976663` and owner-private cohorts **UNOPENED**. No source-operator or original accepted model modifications.
- Original source `reset` and `step` provides public RGB, chosen source-native `MultiDiscrete([3,3])` actions, numerical reward and done/trunc only. All `info`, private path/goal positions and hidden environment states ignored. Outcome "goal" requires **public** reward ≥1 **and** observed terminal flag, matching earlier FKP16.

## Frozen high-first protocol

**Start at 128 source-native steps per tested schedule**, and retroactively score horizons 16,32,64,128 from the *same physically executed trajectory*. Do not pay for separate 16/32/64 rollouts or invent reward after native termination. For each of 16 world seeds × 4 source-blind prefix anchors (0,16,32,64), physically replay identical public reset+prefix to each of **24 schedules**:

| Frozen schedule family | Count | Source action logic |
|---|---:|---|
| Constant 0–8 | 9 | Hold one legal macro for full horizon |
| Eight-step alternating | 9 | Switch between a legal macro and its +4 modulo9 partner every8 steps |
| Seed-blind periodic random | 3 | Seed/anchor/plan deterministic eight-step action blocks; no feedback |
| Reward-driven eight-step switch | 3 | Keep last action if its previous block had actual positive public reward; otherwise shift by a frozen +1/+2/+3, no private source knowledge |

That is **1,536 independent real source rollouts**, physically capped at **315,000** native actions including repeated prefix actions. H16/H32/H64/H128 labels come from these same physical rollouts. Zero goal evidence is a meaningful stopping result, not a reason to tune after the data.

The naive conventional fixed plan is selected by mean 128-step public outcome on the 8 FIT worlds **before** physically opening the 8 AUDIT worlds. Compare its earned return to a source-blind random plan (index18), privileged best constant9, and privileged hindsight best of all24. The 24-way oracle is **an unachievable upper bound with knowledge of the counterfactual results**; it cannot select a learner's real action.

**Frozen source-positive gate on already-consumed VAL worlds only**: at H128, at least 2 different worlds and ≥4/32 anchor contexts must have an actually executed goal-reaching schedule among 24, **plus** hindsight 24-way oracle mean advantage over FIT-selected fixed plan ≥0.15 source return and 10,000 world-cluster bootstrap (seed9090) CI lower>0. Passing is `DEV_SOURCE_HEADROOM_ONLY_NOT_SCIENCE`, not learned planning, scientific pass, native integration or OOD transfer. On failure classify `DEV_NO_GO_LONG_HORIZON_GOAL_SUFFICIENCY`, retain genuine null and stop this frozen mechanism.

No neural learner is trained by FKP-17; the best FIT-selected fixed schedule is a conventional historical selection baseline. Real goal access and decision-relevant causal information are prerequisites for a *subsequent* separately preregistered non-token temporal model vs fully trained GRU, model-based and replay controls. Source-only FKP-17 can't prove those advantages.

## Engineering qualification

Run one isolated GitHub Actions one-shot standard hosted Linux+Windows source-safe test first, with original SHA/tree/prereg/test blobs pinned. G29 code atlas regeneration may touch ONLY its 3 machine-generated `.ice/code-atlas` files; mandatory focused fixtures and inherited root full regression must pass **on both OS before any original 128-step public action data is exposed**. Then one original Linux public TRAIN/VAL study and deterministic Windows replay on the **same already-consumed world IDs** to establish reproducibility, with final source-safe/root regressions and original full source trace archived as private CI artifact. No new controller, cron, owner/sibling research runner, paid API, native Yggdrasil or accepted ref mutation.

The results belong in this draft source branch as `result.json` and README narrative only after the original execution, with model/source/method/prereg/threshold/test Git blobs unchanged. Preserve original physical source action counts and all per-branch public observation/action/reward/termination hashes. Avoid duplicate FKP-17 PRs or converting G29 acceptance success into `SCIENTIFIC_PASS`.
