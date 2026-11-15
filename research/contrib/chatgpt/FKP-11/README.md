# FKP-11 — public action-consequence information in original Memory Gym environments

**Independent research-only source-sufficiency gate, not Yggdrasil native model training or integration.**

Reuses the independently qualified [FKP-10 Memory Gym source admission PR #1100](https://github.com/spoonman136668-ai/Yggdrasil/pull/1100) **without editing that branch**. FKP10 proved original source mechanics and Linux/Windows identical public traces at [run #43725716616](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43725716616). Only **2 nonzero public reward events in 256 true source actions** occurred under its fixed random policy, insufficient for a claim that a native temporal learner has adequate causal/reward information.

FKP11 tests whether a *public observation-conditioned associative action sampler* makes substantially more informative real action/consequence experience available than count-balanced or random sampling on two **original, external, MIT-licensed** Memory Gym POMDP tasks. No synthetic Boolean task and no private source labels.

## Frozen custody and primary disarm

- Accepted Yggdrasil parent main: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`. This repo's native memory remains untouched.
- Preregistration FIRST, before source and original DEV: `a84eda5246b9eedb3515ef0e6c7c1bda36fbdc08`.
- Frozen original source protocol SHA256 `c97dff4aa1b80b7fe8c0438a3960712224924d9475b85892f5718a1bd4c3c83e`, see `prereg.json`.
- Upstream original benchmark `MarcoMeter/endless-memory-gym`, exact Git SHA `a94f2b60d1769ea44df3226561488768e1dff9f4` with original MIT LICENSE and the same exact five pinned blobs already verified under FKP10. Clone unchanged into independent GitHub runner temp; **do not vendored-copy or edit upstream**.
- Original public DEV seeds `971000..971007` in each of `MortarMayhem-v0` and `MysteryPath-v0`, **8 original episodes/task/policy** with maximum **64 paid native actions** each, for at most 48 episodes /3,072 source-native env steps. FKP10 mechanical seeds `970100..970103` are consumed and excluded. Protected science cohorts `973000..973063` and negative `974000..974015` remain disarmed.
- Ubuntu 24.04 and Windows 2022, CPython 3.11; original `gymnasium==0.29.0`, `pygame==2.4.0`, `numpy==1.26.4`; SDL dummy; no GPU, model inference endpoints, paid APIs, new scheduler, controller or self-hosted/owner workstation runner.

## Genuine action-consequence mechanism and controls

All three policies receive the same task/seed reset and **the same initial 9-step source-public warmup action sequence**. Every later action is an actual original `MultiDiscrete([3,3])` source intervention; each observation, original reward and done flag comes from the original `env.step`. The estimator reads ONLY the source-returned public image arrays/actions/consequences; the `info` return is **ignored** and source-private world positions, target layouts or hidden dynamics are NEVER inspected. Public image feature is an 8×8 grid of 8-level quantized intensity values, with full observation SHA256 retained for custody, neither text nor tokens.

The small direct numerical `PublicAssociationMemory` counts actual observed transitions by `(public image fingerprint, action)` and tracks novel-vs-repeated action outcomes. **Curiosity** chooses a less-observed action for the currently seen image fingerprint; after tying per-state action visit count, global action counts and frozen action order break ties. **Balanced** cycles the same 9 actions; **random** selects among the same 9 actions with a frozen per-seed PRNG. The learner gets no hidden labels, replay of environment internals, outcome oracle, pretrained public source map or unfair extra source actions.

Important: this is a deliberately bounded **public transition-information mechanism**, *not* a trained reward-optimizing policy, arbitrary causal-law induction, autonomous agency or a full native Yggdrasil substrate. A later full scientific candidate needs trained recurrent GRU/Transformer-free recurrent and other fully fit matched controls, actual held reward/action success, persistent cold retention, interference, source cohorts and whole-process cost.

## Strict metrics and stop

Primary source evidence: paired-by-seed 10,000 fixed-seed-9090 bootstrap CI of **distinct quantized public observation rate**, separately for each task; compare curiosity vs both balanced and random at identical maximum steps. A positive public-information development signal requires curiosity ≥1.10× both passive novelty rates on **both** tasks, with positive CI lower bounds and no task-level reward degradation. Every task reports **actual public rewards and reward events**; image novelty may be irrelevant visual flicker, and cannot substitute for reward or real task completion.

Classify as `SOURCE_REWARD_SIGNAL_INSUFFICIENT` if *any task* receives zero actual reward events across all three policies; `DEV_NO_GO_CURIOSITY_POLICY` if the prereg positive effect fails; at best `DEV_PUBLIC_INFORMATION_SIGNAL_ONLY`. No scientific superiority or native model promotion from this diagnostic. Cross-OS original per-episode public image, action, real reward and terminal trace SHA256 must agree; divergence is `SOURCE_DETERMINISM_FAIL`, not a learning negative.

Do not rerun consumed public DEV to retune the feature grid, curiosity ranking, seed split, thresholds, training budget, reward definition, control policy or source. Protected scientific first-use is completely separate and requires an independently qualified strong learned model and owner-scoped admission.

## Exact source commands (public DEV only)

```console
python -B -m unittest discover -s research/contrib/chatgpt/FKP-11 -p test_fkp11.py -v
python -B research/contrib/chatgpt/FKP-11/study.py --public-dev --upstream-root /path/to/checked-out-exact-original-upstream
python -B scripts/build_code_atlas.py --check-if-present
python -B -m unittest discover -s tests -p 'test_*.py' -v
```

The original GH workflow executes frozen fixture checks + full inherited G29/root regression on **both OS BEFORE first original public DEV**; then runs once on Ubuntu and a determinism-only Windows replay. Any result on consumed world seeds afterwards is an engineering replay, not fresh science. Preserve both positive and negative outcomes, source SHA/tree and exact measured action charges in this branch.

**Yggdrasil accepted main and protected scientific evaluator remain untouched.**
