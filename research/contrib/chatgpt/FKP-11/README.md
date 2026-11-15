# FKP-11 — Memory Gym: can source-native reward feedback support learning?

**Research-only, source-headroom assay. No learner, native model integration, source-private access or protected first-use.** Follows [FKP-10 source admission #1100](https://github.com/spoonman136668-ai/Yggdrasil/pull/1100). The exact pinned upstream **MIT** Memory Gym is cloned at `a94f2b60d1769ea44df3226561488768e1dff9f4` into an isolated test directory and never copied or modified in this repository.

## Motivation

FKP-10 qualified real partially observable Memory Gym on Ubuntu and Windows with source receipts matching, but its eight short (32-action) random episodes delivered only **2 nonzero reward events out of 256 genuine source steps**. We cannot yet conclude a direct-weight-learning model is worth evaluating there; absent feedback, even a trained GRU cannot fairly be claimed inferior or superior.

**Frozen preimplementation protocol**: `prereg.json` committed first at `e400e8a830e30add038b8549045c4d4e437268dd`. FKP-11 uses fresh original public DEV seeds **971100..971103**, not FKP10's now-consumed 970100..970103.

## Method

Two original upstream tasks (`MortarMayhem-v0`, `MysteryPath-v0`), four new public seeds, two source-blind action policies (uniform independent random; fixed repeated 8-step macro actions) and two **explicitly separated reward configurations** (unmodified original defaults; original env's public `reward_command_failure=-0.05` / `reward_fall_off=-0.05`). Up to **256 actual env.step calls each ×32 episodes =8,192**. Only visible image observations, selected public actions and actual emitted rewards/terminations are accessed. No `info` content, hidden simulator attributes, private path/agent labels, human/debug renderer, model oracle or protected source key. More reward events via public reward adjustment are *not* learning or original benchmark scores.

For each exact paired task/seed/policy the action list and all observation/termination bytes MUST match despite the reward change; otherwise SOURCE_PAIR_DRIFT invalidates the feedback comparison. Seal source trace hashes and report positive/negative/nonzero events, distinct public frames, charged actions, and reward event counts from the first 32 actions against the full 256.

## Frozen decision

A **SOURCE_HEADROOM_PASS** (source-feasibility only) requires 16/16 paired trajectories identical, 16+ additional genuine nonzero reward events **per task**, 4/8 policy-seed episodes per task with at least 2 public reward events, and observable state variation. Partial source signal is SOURCE_MIXED; changed dynamics or no source signal is SOURCE_NO_GO. There is no independent learning or performance result; a subsequent learner would need matched fully trained recurrent/GRU, symbolic/control and native-tokenless models, real action consequences, cold retention and unfamiliar transfer, and whole-process costs.

The first original DEV execution must follow both OS fixture/G29/full-root-regression qualification on an exact SHA. Subsequent Windows replay is reproducibility, not untouched first-use. No work changes Yggdrasil accepted `main=5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`, runtime, loop, runner or protected cohorts.

## Reproduce (after first-use and pinned qualification only)

```console
python -B -m unittest discover -s research/contrib/chatgpt/FKP-11 -p test_fkp11.py -v
python -B research/contrib/chatgpt/FKP-11/probe.py --public-dev --upstream-root UPSTREAM_EXACT_CHECKOUT
python -B scripts/build_code_atlas.py --check-if-present
python -B -m unittest discover -s tests -p 'test_*.py' -v
```
