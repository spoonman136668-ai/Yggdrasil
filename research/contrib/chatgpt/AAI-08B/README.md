# AAI-08B — Sparse-return causal memory falsification

This independent **external contributor experiment is NOT scientifically authorized for first use yet**. The AAI-08A experiment completed with a reproducible scientific negative, and its complete results remain unchanged in [draft PR #1041](https://github.com/spoonman136668-ai/Yggdrasil/pull/1041).

## Causal diagnosis driving this design

Read-only retrospective audit of the *original 64 transfer worlds* reproduced all 192 candidate checkpoint decisions without running NS-Gym again. In 21 worlds the AAI-08A cache finished with a single regime slot. On A-return, it missed 16/64 decisions; 10 of those misses had one slot and 6 had two. Recent-window Beta missed only 4/64. The old experiment then gave every method 24 fresh A observations before testing recall, greatly weakening any claim of memory retrieval superiority.

This design explicitly tests the *value of stored older causal evidence* after 0/1/2/4/8 consequence probes, against two equally likely hidden forks: A returns or B remains. Zero-probe histories are identical and provide no causal information; B-stays is a necessary negative control against blindly guessing A. Matched learners observe the same official NS-Gym Bridge RIGHT actions, transition outcomes and rewards, never hidden A/B identity or shift notifications. Separate snapshots are used only to fork the counterfactual **continuation of the same already learned model** after B; no branch retrains from scratch.

## Frozen scope and stronger controls

The prespecified old **AAI-08A regime cache** is intentionally preserved *unchanged*, and compared with its one-slot ablation, four/eight/sixteen-observation recency Beta, fully trained all-history Beta and logistic, always-right reactive, plus a domain-informed A/B HMM upper bound marked **oracle** (not matched). The primary claim requires actual preserved-A memory retrieval and gain over the **best matched conventional** control, with paired CIs and a B-stays nondegradation test. Merely matching a fast conventional learner cannot pass.

The source is pure Python and contains no network, inference API, or native Yggdrasil code. The source-only tests use fabricated Boolean rows, not previously consumed science. The separate NS-Gym environment source is immutable at `scope-lab-vu/ns_gym@127df4b714fe4fcf680721d8e9278a96090acd7e`. Full protocol, budgets, threshold and exact never-reuse ranges are at `prereg.json` committed **BEFORE this source**.

**Authority fence:** creating this source and unit checks does **NOT** authorize running new 894xxx/895xxx/896xxx science cohorts. The prior explicit user grant was for AAI-08A first use, not AAI-08B. Keep independent of native Yggdrasil model, controller, owner loop, weights, accepted ref and deployment. No paid APIs, schedules or additional runners.
