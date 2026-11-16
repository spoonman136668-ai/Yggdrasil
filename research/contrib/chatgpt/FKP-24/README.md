# FKP-24 — Independent external causal MDP: source/action-interface preflight

**Research-only. No real upstream Causal-Gymnasium environment was instantiated or stepped in this gate. No native Yggdrasil model changes, scientific first-use, merge or deployment.**

## Motivation and distinction from previous source-safe experiments

The current FKP-23 [draft #1119](https://github.com/spoonman136668-ai/Yggdrasil/pull/1119) achieved **32/32** known-family shifted+return first-outcome predictions and preserved new contradiction-derived residual signatures `5` and `10`, but an independent fully informed exact Bayesian control also achieved **32/32**, leaving scientific superiority **NO-GO**. Those sources were authored in this research line and exposed a finite algebraic basis. WSP-120 [draft #1113](https://github.com/spoonman136668-ai/Yggdrasil/pull/1113) independently tests dynamic graph-programs, but its GRU control disagreed across operating systems, invalidating its comparison; do not replay its consumed cohort or borrow its authority.

**FKP-24 deliberately stops generating new easy synthetic Boolean worlds.** It prepares to test physically chosen binary actions and their sequential consequences in a **separate third-party causal environment**, without its hidden variables or counterfactuals flowing into the learner. This is not a completed learning experiment, and the external source is publicly inspectable; it will not become an independent blind owner evaluation merely by being external.

## Original frozen external-source provenance

The first and sole initial research commit `c269c14b8b35d5615838139f859e7020ba51aee1` contains only `prereg.json`. It freezes exact parent qualified research-only FKP-23 head `6a9d908c270bb209f13eb87db407bfd463f16446`, before any FKP-24 implementation or data.

External original source is **CausalAILab/Causal-Gymnasium**, Apache-2.0, exact commit `c94e9a4cd3641588b6b8507e71ccee5c27032bdf` ([upstream](https://github.com/CausalAILab/Causal-Gymnasium/tree/c94e9a4cd3641588b6b8507e71ccee5c27032bdf)). Frozen Git blob pins:

| Official upstream file | Git blob SHA-1 |
|---|---|
| `LICENSE` | `993e3a4922f003dced0fd061735697c850ea7205` |
| `causal_gym/envs/mdp.py` | `6264ec5450754c009e98c3e85f6d5927ece0a9ab` |
| `causal_gym/core/pch.py` | `ff37780c6b791877c70583b8d5f699be7fcd8817` |
| `causal_gym/core/task.py` | `668262f3f5c88fa2865b08ef10bbf96b09a3b73e` |
| `causal_gym/core/scm.py` | `f66f2638c797cfeaf0e96d4e13c06d4fabc2c8d5` |
| `causal_gym/envs/__init__.py` | `a36a43e2ccbca2c924db6b2852c70b5635bca181` |
| `causal_gym/__init__.py` | `6f8129d2caa303ee9fe87ff18fdbdfa153d8a53f` |
| `setup.py` | `31097c35f908e393bfd4763a298c1d5f4ab60600` |

No upstream files, pretrained weights, hidden response labels, images, credentials, or copied source code are committed in this research directory. `verify_upstream.py` inspects a previously allowed checkout **read-only** using `git rev-parse HEAD`, `git status --porcelain` and each frozen `HEAD:path` blob. Any changed SHA, dirty source or missing Git object fails closed. This action does not clone/execute external source. The source license is independently pinned; dependency resolution on a real runner remains unqualified.

## Public-only adapter contract

The native official API is `MDPPCH(max_step=30, task=Task(learning_regime=LearningRegime.do))`, invoked with `reset(seed)` and `do(policy)`. It is not the raw underlying SCM `step(x,u1,u2,u3)`. The source normally exposes exogenous/confounding variables and a counterfactual `ctf_do` path; **no learner may call either**, see the internal `env`, read causal graphs, or obtain private `info` or `natural_action`.

The adapter `native_public_mdp.py` is a strict action-before-outcome interface. A policy chooses a **binary action using only the last publicly observed binary state and the preceding immutable public transition tuples**. Only then does the trusted adapter invoke native `env.do` once, sealing that action and checking the native callback against the already-known state. It forwards exactly **before, chosen action, earned 0/1 reward, after, termination and truncation**, rejecting out-of-range values, future labels, repeated callback attempts, unsealed actions, nonphysical result shapes, unpermitted seeds and excess actions. It does not expose upstream `info` or native environment object to the policy. If source action execution fails after a call, the adapter **does not replay** an uncertain-effect intervention. Source closes on all paths.

The external source is imported **lazily only by `native_source_factory`**. The preflight/unit tests NEVER call this factory and only use strictly controlled fake source objects. Such mocks can prove *interface mechanics and denial of leaked data*, but **cannot** establish that an actual independent MDP run is operational. The adapter itself is an interface fence, **not a secure interpreter or separate operating-system process**. Genuine scientific blindness and independent owner acceptance require a real isolated source service/process with separate permissions.

## Source-admission and science gates

**Gate now (no first-use):** Original prereg, exact upstream commit/blob ownership, 11 mock physical-choice/negative tests + 5 independent custody tests, inherited FKP18–23 research tests, mandatory G29 and full-root 54/54 tests on **Ubuntu24.04 and Windows2022**. A one-shot GitHub-hosted source-safe workflow may verify the external Git checkout **without importing the package or stepping any real world**, then generate only the three `.ice/code-atlas.{html,ice,json}` artifacts. The actual source is read-only and remains unchanged.

**Next distinct mechanical source gate, not authorized here:** Install the exact upstream package/dependencies in an isolated qualified environment; first verify import/runtime interface. A native action test would be limited to four new public TRAIN seeds `996100..996103`, no more than **32 actual `do` actions each** (128 maximum), public transcript SHA receipts on Linux and Windows and no source-private data. Its first-use must be separately authorized by source owner and reproducible across qualified platforms. Protected DEV `996500..996531` and TRANSFER `996600..996663` remain closed.

**Next scientific gate, also NOT authorized or run:** Freeze the native source action/observation and seed split, a bounded tokenless persistent causal memory that adapts to actual confounded transitions, and **fully trained matched-information** GRU/MLP, Bayesian, retrieval and no-update controls. Judge cumulative reward, intervention value beyond source-blind policy, unfamiliar dynamics, cold retention/interference and **whole-process** time and resource use. All original first-use, held-source and native-promotion permissions are separate. Any strong-baseline tie is a no-unique-advantage result, not a novel general-intelligence proof.

**Caution:** Upstream CausalGym imports many optional environments eagerly and `setup.py` requests broad dependencies including Box2D. An installation/import failure is an **infrastructure/source admission failure**, not a scientific model failure. Do not silently vendor a modified simulator or fake native source to hide this limitation.

Research remains draft/unmerged, accepted `main=5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` unchanged, no new scheduler, owner, runner, paid API, migration to Work, cross-project integration or accepted model mutation.
