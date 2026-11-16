# CVH-04 — public-only OS process seam for a tokenless retained learner

**Status: source-free engineering process separation and 20/20 focused tests PASS Ubuntu+Windows, original CausalGym action first-use ZERO, scientific result NONE.** Final exact-source full repository G29 and dual-OS regression must be independently completed before treating the branch as engineering-qualified.

## Purpose: finish a real missing interface, don't create another controller or synthetic-learning claim

The independently authored original `CausalAILab/Causal-Gymnasium@c94e9a4cd3641588b6b8507e71ccee5c27032bdf` MDP has been qualified for **unchanged source construction**, not for actual source resets/do or source-owning process isolation, in [CVH-03 draft PR #1160](https://github.com/spoonman136668-ai/Yggdrasil/pull/1160) and its [genuine source constructor qualification run #43930592515](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43930592515). This parent already passes [full root regression and G29 on both OS #43931418817](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43931418817), and is source-pinned at `0975c5d83aa9b0357735139cae3457338ec67027`. The same developer research line's CVH-01/02 inherited policy stores public four-step earned-return consequences and cold checkpoint state. Its independently coded conventional batch estimator matches every same-tape return, so do not claim unique intelligence benefit.

**The gap**: the CVH-03 factory and existing FKP24 action adapter have no interprocess boundary; source-private objects and learner coexist within one Python interpreter. An environment/process that carries its own hidden variables should not be given as an in-process object to a learner during independent science. CVH-04 proves the fundamental **real operating-system subprocess protocol** with a deliberately synthetic mock source. It does **not** attach any real CausalGym environment yet.

The two strictly scoped Python modules:

- `public_ipc.py`: parent-side synchronous `ToySourceSession`. It invokes exactly one short-lived Python child process (no resident agent/runner/service), accepts **only** the observed binary state and six-field consequence tuple matching FKP24 `PublicConsequence`, and calls the **existing unmodified CVH-02 PublicEarnedPolicy** in ordinary choose-before-outcome order. The parent sends exactly one binary action, validates monotonically sequenced strict public consequence, and only then permits `policy.observe`. A private field, mismatched action/state, future/duplicate sequence, timeout, wrong type, oversized or corrupt message **terminates the child and forbids action replay**. Public result headers and the worker PID remain outside model inputs.
- `toy_source_child.py`: standard-library **mock process only**, no CausalGym or original FKP24 environment import, no network API, no original seeds or original `reset/do`. Whitelists toy seed identifiers `1..6` only, at most six chosen actions per episode. It holds a private mock salt and returns only six fields after a real IPC action request. Its negative-control fault modes deliberately inject forbidden private fields, wrong action, wrong sequence or silence; the parent rejects each.

This is **actual process separation from the fabricated source** (different PIDs and stdio protocol). It is **not** a sandbox against a malicious policy running with the same OS user's permissions, not independently authenticated original-source custody, and not source-first-use permission. The source child has no real scientific data or original CausalGym actions.

## Frozen protocol and qualification evidence

- Preregistration committed **first** at `ede2e4512606e4da134a5c747bff7ef06b0c1a67` before implementation, test scores, simulator feedback or code-as-a-learner claims.
- Exact immutable new code/test prefirst SHA `1692304819ff237a33fae5a617884f1861043556`, with Git blobs: mock child `cb56138556366f565192f2881ae3649f43280f4c`, public IPC `75f85dc2b6305a5089052a473fae113d6254ad9c`, 20 tests `a1bd4c8d9b1252d37a0fd6f16ca3a82fefb50f4f`. All prior accepted source, CVH02 policy, CVH01 learned memory and original external CausalGym remain byte-identical.
- [GitHub source-free first OS process CI #43957165138](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43957165138) **COMPLETED SUCCESS** both Ubuntu24.04 and Windows2022 Python3.12: **20/20 new focused tests each OS**, exact Git source/prereg checks, all protected-source seed entrypoint negative fences, unchanged source tree. Local focused Python test duration from GitHub: ~**0.846 seconds Ubuntu**, ~**1.298 seconds Windows**. These are individual suite test times, not entire end-to-end GitHub CI wall-clock or native source compute costs.
- Tests verify distinct OS subprocess PIDs, action requested prior to source consequence, strict public-only six-field records, 6-step episode closure, tokenless CVH02 policy cold restoration after completed mock episode, repeat seed same public trace despite different process IDs, inherited CVH01 independent batch-return numeric parity given precisely the same observed public data, and hostile response failures which **cannot** silently become learned outcomes or cause uncertain-effect replay.
- The derived `result.json` and `provenance.json` preserve engineering observations with zero original environment steps and separately enumerate what remains unverified.

### Reproduce (mock/source-free only)

```sh
python -B -m unittest discover -s research/contrib/chatgpt/CVH-04 -p 'test_*.py' -v
python -I -B research/contrib/chatgpt/CVH-04/toy_source_child.py --mock-only --toy-seed 996100
# Must refuse: real reserved seed ID not in toy 1..6 allowlist
```

No dependency beyond the existing repository's Python 3.12 standard library. This child has no function or CLI entrypoint that can invoke `CausalGym.reset`, `do`, `ctf_do`, the owner model or an external broker. It does not run any background tasks.

## Plain-English result and limits

**ENGINEERING:** We can place a **mock** causal source in its own short-lived OS process and safely carry only public binary actions and consequences to the current tokenless Yggdrasil research learner. Correct process separation, memory retention, and no uncertain-effect replay qualified in initial tests. The missing genuine-source process bridge remains pending a separately owned execution gate.

**SCIENTIFIC:** **NOT RUN**. No original independent causal-world action/reward was performed; no actual new causal relationship was discovered, and CVH01's observed return estimator still ties its strong independent equal-information batch estimator on mock records. No unfamiliar-source generalization, retention under original source interference, or whole-process efficiency advantage was measured.

**DEPLOYMENT:** None. Existing `main`, accepted weights, live research loop, controller, scheduled tasks, local Windows workstation, Wingless/Hybrid models, original CausalGym source, owners and project first-use cohorts remain unchanged. This is an isolated draft development branch. **Do not merge or automatically activate** based on these source-free tests.

Next source-scientific gate requires independently verified project-scoped **original source first-use authority** and separately qualified genuine source-side process custody before using reserved public mechanical `996100..996103` (max 32 `do` actions each), protected DEV `996500..996531`, or TRANSFER `996600..996663`. Only thereafter can a frozen truly equal-training/compute/action conventional benchmark and unfamiliar-world retention/transfer study produce a meaningful scientific verdict. Stop extending mock-data metrics as if they were scientific evidence.
