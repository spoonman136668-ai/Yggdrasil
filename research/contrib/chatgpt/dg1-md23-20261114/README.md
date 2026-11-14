# DG1-MD23 — genuine rewarded box-pickup transfer (prospective)

**Status:** protocol frozen at prereg-only commit `ea927ae080aee59d2dc0783f45eb703735dfb52f`; no MD23 code, toy preflight, registered first use, scientific result or deployment yet.

## Why this successor exists

MD22 (#1009) correctly ended **INVALID_TASK_COVERAGE**: all five agents obtained zero official UnlockPickup goals on 12 held-out episodes apiece, even though its learned conditional key-before-door effect was physically observed and ordinary DoorKey performance was reproducible. MD22's official result remains sealed, unmodified and unusable as a positive cross-family transfer result.

The UnlockPickup environment requires the agent to **pick up a box behind a locked door**, whereas DoorKey ends on reaching a goal square. An existing hardcoded task navigation scaffold should not be credited as learned planning. The exact reason all MD22 agents failed the box family remains **unverified**, so MD23 cannot simply label this as a proven model-architecture deficiency. The next test isolates actual reward-bearing task completion with a task-trained teacher and correctly states it is **heldout within-family generalization**, not zero-shot new-family transfer.

## Implementation boundary

- Extend only `research/contrib/chatgpt/dg1-md23-20261114/**` plus its isolated workflow and mechanical G29 atlas. Import frozen predecessor `mg20.py`, `mg21.py`, `md22.py` without modifying their original source, preregistrations, experiments or evidence.
- Build a teacher using only official 7×7×3 partial images, public heading, self-estimated pose, charged actions and observed rewards. Specifically verify rewarded box pickup, not merely a door opening or reaching a nonterminal room. Never read hidden environment positions, full grid, oracle planner or the mission string.
- Train all six frozen arms on one shared 24 DoorKey + 24 UnlockPickup teacher trajectory corpus. Include distinct 12-episode interference and four independent 12-seed evaluation blocks per arm.
- Learned arm: a bounded persistent conditional event graph whose observation-derived evidence changes key/door/box subgoal selection. Sham: same data/capacity/scaffold but permuted conditional edges. Also include a no-learning scripted policy, reactive policy, fully trained reward Q and fully trained recurrent imitation. No output from evaluation is permitted to update persistent learning.
- First prove teacher coverage and negative controls with **toy-only** seeds 11, 17, 19, 23, 29, 31. Coverage failures are independent of CI infrastructure failures. Ensure correctness of key pickup, locked-door toggle, box pickup, official terminal reward, cold restore, action counting and role/source isolation.
- Then qualify **one exact candidate SHA** with complete inherited regression and independent G29 source atlas on Ubuntu and Windows. Registered seeds `980001..985012` are reserved and must never be used by preflight.
- **Do not open the new scientific PR until code and preflight are ready.** The precedent uses the opening event to run the registered original study once per OS. Keep exact head/base/PR-action gates to prevent predecessor replay; later synchronize/push events must skip scientific first use. Store full evidence in GitHub Actions only.

## Disposition

Frozen success, mixed, negative and invalid definitions, exact cohorts, physical-action budget (348 episodes, maximum 89,088 actual `env.step` calls) and authority limits are in [prereg.json](./prereg.json).

Any future positive MD23 result would only be an **external development signal**, not a native Yggdrasil change, official controller upgrade, independent scientific acceptance or demonstration of AGI. Protected `main`, accepted state, scheduled tasks, the official research loop and Wingless/Hybrid/weight-programming tracks remain untouched.
