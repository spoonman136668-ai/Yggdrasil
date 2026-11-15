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

## Original real-source outcome — 2026-11-15

**ENGINEERING PASS / DEVELOPMENT SOURCE GOAL HEADROOM NO-GO / SCIENTIFIC_PASS=false / DEPLOYMENT NONE.** The exact frozen source [one-shot GitHub Actions run #43764698791](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43764698791) **completed SUCCESS across all five jobs**, including G29/source custody, Ubuntu+Windows FKP17 focused 6/6 + G29 4/4 + mandatory 54/54 full inherited regression BEFORE new public H128 consequences, one original Linux source experiment, Windows replay with **identical FIT and AUDIT physical source trace SHA256**, and full post-source regressions on both OS. Linux original trial job `132967358547`, Windows source-only replay job `132967734163`. Windows is a deterministic replay of **previously consumed source IDs**, not independent model science.

**1,536 genuine physical plan trajectories, 238,655 original source-native actions** (119,178 FIT +119,477 AUDIT) under the preregistered 315,000 source budget. All four horizon results were calculated from the same H128 physical trajectories. Selected global best FIT-only plan: `PUBLIC_REWARD_FEEDBACK8_1` (plan22), with fit-selection seal `c385e4992ef32616b942bf89c78cde5014400cdacc481751941e99475d45d3a5`.

| Original AUDIT source metric | H16 | H32 | H64 | H128 |
|---|---:|---:|---:|---:|
| Goal-reachable contexts out of32 (privileged best of24) | 1 | **2** | 2 | **2** |
| Distinct worlds with an achieved goal out of8 | 1 | 1 | 1 | **1** |
| Privileged physically observed best-of24 mean return | +0.165625 | +0.1796875 | +0.1484375 | **+0.125** |
| Best-of-nine constant-only privileged source reference | +0.128125 | +0.1140625 | +0.096875 | +0.0875 |
| FIT-selected single global feedback plan mean return | −0.0359375 | −0.0375 | −0.0375 | **−0.0375** |
| Frozen source-blind plan18 mean return | −0.071875 | −0.1265625 | −0.2984375 | −0.64375 |
| Best-of24 minus FIT-selected plan mean return | +0.2015625 | +0.2171875 | +0.1859375 | **+0.1625** |
| Positive reward events across 24×32 branch prefixes | 249 | 291 | 328 | 383 |
| Negative reward events across 24×32 branch prefixes | 1,517 | 3,038 | 6,037 | 11,983 |

The H128 oracle advantage over the FIT-selected plan had **8-world clustered paired 10,000-bootstrap 95% CI [0.0671875,0.334375]**, which is positive and above the preregistered +0.15 mean threshold. However, **GOAL POSITIVE GATE FAILS**: prereg requires at least two distinct goal-reaching worlds and ≥4 goal-reachable contexts, whereas the same true source produced only **one** goal-reaching world and **two** anchor contexts. Crucially, **extending H32 to H128 did not add a single goal-reaching context or world**. It increased incidental positive rewards but introduced vastly more negative reward events. Even best-of24 hindsight mean return *decreased* from +0.1796875 at H32 to +0.125 at H128.

This is **not** evidence the agent learned to plan. No trained temporal learner, native Yggdrasil model, source-private oracle use in action selection, full-process compute-matched control, cold interference or unfamiliar-law transfer was executed. The 24-way best-of values are privileged counterfactual upper bounds computed **after physically observing all plan outcomes**; the sole fair FIT-selected global policy returned −0.0375 at H128. Every examined world was an already-consumed FKP16 TRAIN/VAL world, so these new H128 public source consequences count as DEVELOPMENT SOURCE ONLY, never independent held-out science. FKP16 DEV `976500..976531`, reserved transfer `976600..976663` and owner-protected cohorts were not touched by FKP17.

**Original exact source receipts**: FIT SHA-256 `e0e127f299fcf1ace4e76bb5d2afe3bcb4cf539bb4b49ff8335ba76d1bf69289`; AUDIT SHA-256 `30d2e27352fad3d8fa4b34f1996331ab894ab6993a369c8b90d178acdadfc9d3`, identical on Linux and Windows; method commit `3e776e8bc32a3b6bf6d63442fe5ffdcca0826e2f` and machine-generated-only G29 child `240b2c53ccdecc3a7ada477c335c603a053a4de9`. The full, per-plan public observation/action/reward/termination ledger is sealed in private CI artifact `fkp17-source-actual-128step-plan-ledger`, ID `14182315855`, 30-day retention expires 2026-12-15. Durable result/provenance/thresholds in `result.json`.

**Final decision:** `DEV_NO_GO_LONG_HORIZON_GOAL_SUFFICIENCY`. Freeze this 24-schedule H128 mechanism, **no after-the-fact tuning or expanded repetitions on the exposed cohorts**. A next distinct effort needs a goal-rich, source-identifiable consequential decision task (multiple independent goal worlds) and fully trained conventional matched controls before new native/tokenless causal learner science. Do not promote FKP17 to accepted main merely for passing source/CI. FKP17 is separate from the simultaneously opened [PR #1109](https://github.com/spoonman136668-ai/Yggdrasil/pull/1109), which preregisters structured causal-law priors. Avoid duplicate PRs and do not combine these different tasks as one replication.
