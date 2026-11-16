# FKP-25 — Original third-party causal MDP constructor without opening a world

**Research only, native original MDP constructor qualification. No `reset`, `do`, source-world first use, neural training, protected DEV or TRANSFER, native Yggdrasil admission, accepted-main ref change, scheduler, new runner or deployment.**

## Why this is not FKP-24 repeated

[FKP-24 draft #1120](https://github.com/spoonman136668-ai/Yggdrasil/pull/1120) qualified public action-boundary logic against mocks and verified the actual [CausalAILab/Causal-Gymnasium](https://github.com/CausalAILab/Causal-Gymnasium/tree/c94e9a4cd3641588b6b8507e71ccee5c27032bdf) Git source and eight file blobs on Windows and Ubuntu. It did **not import or construct** the real external `MDPSCM/MDPPCH`. That source-admission boundary was a genuine engineering PASS but external runtime was UNVERIFIED; previous home-authored finite Boolean family results remain control ties, not independent scientific transfer.

The actual upstream distribution's `causal_gym/__init__.py` imports `causal_gym.envs` eagerly; its environment namespace imports many unrelated Atari, MuJoCo, OGBench, MiniGrid and Torch-dependent environments. Its `setup.py` does not list all these eager imports as mandatory dependencies. Installing all those optional simulators just to instantiate the *binary causal MDP* would be wasteful and creates high packaging/ABI risk. Merely mocking missing libraries would be scientific misconduct.

FKP-25 makes a precise, **more limited** claim: load the original unchanged upstream `causal_gym/core` and `causal_gym/envs/mdp.py` modules from a detached SHA-pinned clean checkout with **two in-memory namespace containers that bypass only unrelated top-level package initializers**. It **does not replace or stub the original `SCM`, `PCH`, `MDPSCM`, `MDPPCH`, native transition/reward code, or any original core module**. The original class constructor must create its own object with `LearningRegime.do` and `max_step=30` using only pinned lightweight runtime dependencies.

This is an **original-MDP targeted import+constructor gate**, *not* a stock whole-package import, real environment step, or proof of whole upstream distribution installation.

## Frozen original evidence contract

The preregistration was the **FIRST and sole initial commit `0caef39ec83600d1da942036ab5862e7753906cb`**, on exact FKP-24 qualified parent `a9f7a64f34275c62f507987b3d52657ec9c78f21`. The original upstream source is `CausalAILab/Causal-Gymnasium@c94e9a4cd3641588b6b8507e71ccee5c27032bdf`, Apache-2.0. Source bytes, commit, branch, method, class, dependency versions, authority fences, two operating systems and zero permitted actions were frozen in `prereg.json` before any implementation.

`runtime_probe.py` first reuses FKP-24's **read-only Git pin + clean checkout + eight external blobs** and checks another nine Git blob pins, including original core `__init__`, graph, graph utilities, task types and the environment namespace initializer. **16 unique original Git files** are verified. Unexpected SHA or path, dirty checkout, missing exact package, wrong class inheritance or wrong native regime aborts **before a world can be opened**.

The prospective minimal dependency set, frozen at exact versions and checked at runtime, is `numpy==1.26.4`, `gymnasium==0.29.1`, `networkx==3.2.1`, `toposort==1.10` and `pydash==8.0.5`. These are supporting Python packages from their public distributions, **not modified or cloned causal-world sources**. Hosted Python3.11 and Python3.12 dependency resolution must be observed, not assumed. Runtime `pip` installation or version incompatibility must be classified as **infrastructure failure**, never as native model-learning failure. Pin exact installed direct dependencies in the receipt; transitive dependency versions must be preserved from the ephemeral runtime if a full dependency lock is later required.

The script constructs the exact original `MDPPCH(max_step=30, task=Task(learning_regime=LearningRegime.do))`, verifies the class is a subclass of the original PCH type and has a `do` method, then stops. It never calls `env.reset`, `do`, `see`, `step`, `ctf_do`, samples a source confounder, reads a source reward or gives a future label to a model. Original source code runs in a disposable Github-hosted process; the source checkout is temporary and unmodified.

## Qualification and interpretation

The source-safe unit tests use mock Git receipts and check clean/pinned source refusal, pinned dependency version refusal, source-import namespace isolation and AST denial of physical action calls. They **never import an original source module**. The *separate* native constructor stage only runs after exact-source FKP-25+inherited FKP-18–24 focused negative controls, regenerated three G29 atlas files and full mandatory root regression pass on both Ubuntu and Windows. Reuse the existing source-safe one-shot helper workflow. No new workflow file, deployment, controller, private runner, scheduler, paid API or science first-use is created.

**ENGINEERING TARGETED_CONSTRUCTOR_PASS**, if observed, means the **unchanged original third-party MDP implementation can be imported and constructed** through an explicitly non-standard targeted import path on both operating systems. It does **not** mean the full upstream distribution can import without its optional extras, `MDPPCH.do` works on real world resets, a learner acquired knowledge, a model beat fully trained controls or a genuine unknown operator was invented. The only possible source action receipt in this experiment is **zero**.

**After** this gate, a *separately authorized* public mechanical source experiment may attempt **four source-world seeds `996100..996103` with ≤32 actual actions each** behind the independently verified FKP-24 public-action adapter, preserving earned observations and exact source checksums. Further scientific experiments require new prospectively frozen, nonoverlapping TRAIN/VAL/DEV, independent owner-run true first-use, matched fully fitted recurrent/MLP/Bayesian/retrieval controls and whole-process compute/cold retention/transfer. Original protected `996500..996531` and TRANSFER `996600..996663` remain unopened.

**No native Yggdrasil merge or deployment is authorized.** Accepted `main=5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` remains unchanged; FKP-24 and WSP-120 are separate drafts. A dependency/runtime failure is preserved as a real negative, with no post-result source substitution or fake pass.
