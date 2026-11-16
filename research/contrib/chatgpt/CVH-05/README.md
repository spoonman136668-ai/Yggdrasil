# CVH-05 — the original Causal-Gymnasium source, constructed **inside its own OS process**

**ENGINEERING: actual original-source constructor in separate OS worker PASS Windows/Linux, final full repository regression + G29 pending. SCIENTIFIC: NOT RUN. DEPLOYMENT: NONE.**

## What actually changed

The [CVH-04 draft PR #1163](https://github.com/spoonman136668-ai/Yggdrasil/pull/1163) proved an interprocess public `(action,consequence)` pipe for the existing tokenless CVH02 policy, but the OS subprocess contained only fabricated source logic. [CVH-03 draft PR #1160](https://github.com/spoonman136668-ai/Yggdrasil/pull/1160) previously verified the **original, unchanged** `CausalAILab/Causal-Gymnasium` source `c94e9a4cd3641588b6b8507e71ccee5c27032bdf`, 16 Git file blobs and five dependency pins, and constructed genuine MDPPCH MDPs, but in the qualification interpreter.

**CVH-05 connects those existing capabilities without creating an unauthorized source-action runner:** `source_child.py` imports the byte-identical CVH03 `verified_original_factory` **inside a newly launched short-lived Python source process**. It verifies the exact upstream Git checkout/16 blobs/pinned package versions, constructs one genuine original unchanged `causal_gym.envs.mdp.MDPPCH(max_step=30,Task(LearningRegime.do))`, and emits one minimal public source-custody handshake. The object is never serialized or sent to the parent and **is never reset or subjected to a source `do` action**. Its entire command grammar admits only an exact `close` frame. There is no `act`/step/reward/seed handler.

`constructor_ipc.py` runs in the **parent** (future learner-side) process, never imports the external `causal_gym` source, checks the strict public handshake keys `schema,kind,source_sha,source_blobs,original_objects,source_actions,source_resets`, and requires exactly one original child constructor, 16 matching source files, zero source resets/actions, a distinct OS PID and clean one-shot close/child reap. The parent cannot request any intervention, reward, private graph, confounder, counterfactual, training seed or extra source object. Bad frame size/type, extra/private fields, Git hash/source drift, timeout and non-zero process exit **fail closed** rather than silently promoting a source identifier or retrying an uncertain effect. As this gate executes no original source actions, the no-retry principle remains a guardrail, not proof of real-source effect custody.

`probe_original_child.py` runs exactly **two separately started and reaped original child processes**, checking the public custody acknowledgment is identical across both starts and across operating systems. A `--source-action` switch is explicitly refused. Original TRAIN `996100..996103`, DEV `996500..996531`, TRANSFER `996600..996663` remain unopened. Only preregistered **constructor-only** work is performed.

**Critical isolation limitation:** two processes under the same runner account are not a sandbox or independent trusted source owner; the PCH has not been wrapped for authenticated scientific first-use and the in-memory target import shims are an inherited qualified engineering accommodation, not a stock original full-package import. Genuine action/transfer science must be separately owner-admitted.

## Freeze, test failure and positive result

- Immutable preregistration FIRST commit `02a48f07511bcce3423897b6502bde26bb649314`.
- Before first focused test or source observation, source+20 tests committed at `182002ea4ba86e227056a2e370f8160d71633c5c`. Source blobs: child `194b96985307390b4c09b68fc0a9767ff294d2f5`, parent IPC `dc5fcce0acfa5cc8f64c5a9dc6caf8c5fe87d11f`, real-child probe `6c3ac735a10150c4d932594262c016ab93f64ae6`, original focused tests `54856b9c93f792870a11b248194a7d3a93fd38bd`.
- First [CI #43962087359](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43962087359) **ENGINEERING TEST FAIL before original source construction** (19/20 focused tests on each OS). The negative first-use CLI test erroneously invoked the **parent** probe under Python `-I` which suppresses sibling `constructor_ipc` import. It failed by module import error instead of expected action-denial error. This is a harness invocation failure, not original environment learning failure. **Source first-use ZERO.**
- Changed **only this test invocation** at commit `bf7aad5f6c2eb0b14bad7c5e32f8f95cb3cd825e` to supported `python -B`; the genuine **source child still launches with isolated Python `-I -B -u`**. Source worker/parent IPC/probe code, model, original upstream, prereg, seed roles and decision thresholds remain identical after first test.
- Corrected [authentic original-source child CI #43962310601](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43962310601) **COMPLETED SUCCESS** both Ubuntu 24.04 (job `133632658829`) and Windows 2022 (job `133632658403`). Each ran **20/20 source-free focused tests PASS**, exact inherited five dependency pins, original external Git clean checkout and all 16 Git blobs verified, then **two separate OS source-process constructors of the actual MDPPCH**. Public custody identical both OS, SHA256 `dae54eb9824155cc0e1fdac3b108459ed870b69111cd2aa22c1e844467dcb938`. Each source process exited cleanly; extra commands and first-use flags denied. Original resets **0**, original `do` **0**, public original rewards **0**.

The new code is additive under `research/contrib/chatgpt/CVH-05/`: `prereg.json`, `source_child.py`, `constructor_ipc.py`, `probe_original_child.py`, `test_constructor_ipc.py`, `result.json`, `provenance.json`, this README. Existing CVH01–04, FKP24–25, native Yggdrasil models and original source are unchanged.

## Qualification commands and scope

Source-free tests only (stdlib Python 3.12, no source checkout needed):

```sh
python -B -m unittest discover -s research/contrib/chatgpt/CVH-05 -p 'test_*.py' -v
python -I -B research/contrib/chatgpt/CVH-05/source_child.py --checkout /missing
# MUST refuse: no --constructor-only
python -B research/contrib/chatgpt/CVH-05/probe_original_child.py --checkout /missing --out /tmp/never.json --source-action
# MUST refuse BEFORE source checkout/import
```

For genuine **constructor-only** CI use the recorded one-shot workflow on a clean detached Git SHA checkout of upstream source with inherited exact direct dependencies. No `reset/do` code is in the protocol or command-line interface. A separate final source-derived G29 and **mandatory full exact-candidate inherited Python regression on Windows/Linux** is required for final engineering acceptance. No separately compiled native deployed Yggdrasil application is claimed.

## What this proves, and what it cannot prove

**ENGINEERING:** the genuine original independently authored CausalGym MDP can be held and constructed in a real, separate, short-lived source-side Python interpreter, while the parent sees only a bounded public source-custody record, with deterministic cross-platform receipt equality. This removes the earlier in-process original-object lifetime problem for **construction**. The original action/reward path has not been introduced or authorized.

**SCIENTIFIC:** **NOT RUN**, not an independent tokenless cognitive breakthrough. No original environment was reset/acted on; no source-world relation learned, no native policy trained on earned original rewards, no matched trained recurrent/tabular comparator on original data, no unfamiliar source transfer, no independent heldout success or whole-process speedup. CVH01's previously observed same-data conventional batch-return estimator ties the current tokenless earned-return learner on mock tapes. The original source's model is **not** user-accepted knowledge or production code.

**AUTHORITY/DEPLOYMENT:** all original experimental roles protected and unopened; main remains `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` until independently reverified. Draft source-only research only. No accepted weights, scheduler, alternate controller, local runner, paid APIs, new source owner service, merge or deployment. GitHub CI is not the authority for scientific first-use.

**Important protocol ordering:** [Yggdrasil external pilot issue #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426) specifically sets an **original two-stage DTR pilot first** and the original confounded MDP as a separate second-world option after source-qualified DTR feasibility. This MDP constructor interface is an engineering prerequisite, **not authorization to start MDP training ahead of DTR-first source-owner approval**. The next actual experiment should resolve this owner-specific ordering and freeze fully trained same-information controls before any protected source `reset/do` actions.

See `result.json` and `provenance.json` for immutable source custody, initial failure, corrective test-only change and passing cross-platform receipts.
