# CUE-01 — source-blind public-action retrieval for native causal memory

**Frozen outcome: `ENGINEERING_DEV_PASS_SCIENCE_UNVERIFIED`. Safety caveat: 2/4 unknown nonlinear worlds still induce incorrect provisional slot matches. This is not ready for autonomous selection of a native accepted memory or scientific first-use.**

## Actual gap

The prior [NKR-12 cumulative-memory bank PR #1148](https://github.com/spoonman136668-ai/Yggdrasil/pull/1148) preserves twelve immutable NKR-11 learned action-consequence relationships in a single cold-restorable 16-slot (seven active, nine retained) native memory, with 384/384 old and 192/192 repaired known-law recalled actions. It is **not** task recognition: its APIs require the caller to provide the memory slot.

The NKR-12 out-of-family falsifications already exist in [PR #1146](https://github.com/spoonman136668-ai/Yggdrasil/pull/1146) and [PR #1147](https://github.com/spoonman136668-ai/Yggdrasil/pull/1147), documenting the fixed ten-feature GF(2) learner's unsafe/conflicting behavior on some nonlinear laws. CUE-01 does not repeat or reinterpret those findings, edit either branch, or claim new outside-family learning.

**This code adds only `yggdrasil/native_action_cue_router.py`, an opt-in, read-only probe proposal and provisional retrieval interface.** It has no access to task identity, the source oracle, hidden world ID, or private evaluation target. A caller asks `propose(bank, public_cues)` for a public context/action intervention, executes that action outside the router, then passes the genuine observed consequence `(context,action,outcome)` to `select(bank, public_cues)`. The router compares these outcomes with previously stored numerical native relations. It proposes the most balanced deterministic partition of remaining candidate memories, with confirmation-oriented probes after a unique candidate emerges. Unknown or ambiguous observations abstain where they cannot be resolved. Every provisional match is labeled `PROVISIONAL_UNVERIFIED_SLOT_MATCH`, with `native_accepted=false`, `scientific_pass=false`, `write_to_accepted_model=false`, `learned_task_identity_verified=false`.

**Explicit limitation:** a unique match across eight observations is not proof that the environment is a previously stored law. A different unseen law can agree on those observations. There is no automatic acceptance, activation, memory write or externally authenticated source.

## Prospective freeze

The complete hypothesis, eight-action budget, source roster, four negative nonlinear worlds, tie rule, public-only information, acceptance limits and strong controls were frozen in `prereg.json` commit `d6f6be11f5483915e451011211275410de8c4cef` **before implementation or measured outcome**. All source and 17 focused tests were committed at `e34f8d30876b53bdbe7dd5fe5f9d37d95edf8a9c` **before source development screening**. Original NKR-12 bank, existing NKR-11 solver, accepted main and previously measured results are untouched.

Development source is **only the already-exposed 12 synthetic NKR-11 numerical action worlds**, loaded into the preexisting NKR-12 native bank. During retrieval, the oracle is in a separate source-only evaluator, which discloses only actual intervened public consequences, never the world index or causal masks. Re-identify each of those 12 worlds under a budget of at most eight public action observations, without fresh training; then test four nonresident nonlinear conjunction worlds as adversarial negatives. No original scientific data or protected first-use source is consumed.

Control 1 is a separately implemented **exhaustive symbolic retrieval** over the same twelve learned numerical slot predictions, using the same deterministic balanced partition and action budget; this is an **equal-capacity, equal-information benchmark expected to tie**. Control 2 is an eight-probe fixed-order policy; control 3 is a deterministic SHA256-sorted random probe policy. No privileged model or baseline gets a hidden world identity, different source actions or extra adaptation. Note that probe trajectories differ by policy, but source access, action cap and source mechanism are identical.

Frozen development gate: retrieve the true stored slot for at least 10/12 familiar worlds within eight probes with zero incorrect familiar-world matches, preserve original bank bytes, exactly tie the independent exhaustive symbolic selector on all known-world decisions, and keep all unknown-world outputs unverified and unaccepted. This is a **developmental mechanical interface**, not an independently admitted science result.

## Measured result

[Exact source-only development CI #43902972327](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43902972327): **COMPLETED SUCCESS on Ubuntu 24.04 and Windows 2022**, **17/17 focused/negative tests PASS** on both, source Git blobs and first-use fence PASS. Deterministic source/cold trace matches exactly across both platforms.

| Outcome | Native cue router | Independent exhaustive symbolic |
|---|---:|---:|
| Previously stored relationships correctly identified | **12/12** | **12/12 — TIE** |
| Wrong familiar-world matches | **0/12** | **0/12** |
| Actual public intervention budget | **8 per familiar world** | **8 per familiar world** |
| Retained preexisting bank checkpoint bytes | **24,773**, unchanged | Same |
| New original scientific source used | **0** | **0** |

**Hard negative:** Four synthetic, previously unrepresented nonlinear conjunction-action laws were queried. The router **abstained in two** and yielded **two FALSE PROVISIONAL SLOT MATCHES** among retained memories using a total of 26 public actions. There were **zero attempts to mark either as accepted or scientific**. The false-match rate is a practical obstacle to autonomous use: robust unknown-world rejection is **not solved** by this eight-probe policy. Do not present it as one.

Same deterministic source/public evidence SHA256: `caf7ae6b1b3af283ca9af2a1d852f95d25cdd8638281fb37b77d6b72b7990acc`. Same full experiment trace SHA256: `24f9eb825b52fdfa74e09560cf1fd55c4c8d6520a9691df0c4262f34b185cc40`. The native bank checkpoint SHA256 remains `a03b6e5fc63d3b69d088bd4b45aca3ed5df7d169e4c9820dcc8f9b3dd25b67bb`.

Other eight-action fixed-order and source-independent deterministic-random policy results are evaluated by the frozen `dev.py` but were not printed by the initial CI receipt. They are not claimed to be numerically inferior here. See `result.json` and `provenance.json` for exactly supported claims.

## Engineering, science, authority

From repository root (stdlib Python):

```sh
python -B -m unittest discover -s tests -p test_native_action_cue_router.py -v
python -B research/contrib/chatgpt/CUE-01/dev.py --source-dev
python -B research/contrib/chatgpt/CUE-01/dev.py --primary # must deny protected first-use
```

**ENGINEERING:** frozen read-only source-blind retrieval works and keeps existing native bank immutable on both platforms; complete inherited repository Python regression and code-atlas G29 qualification remain separate until explicitly completed on the exact source SHA.

**SCIENTIFIC:** no improvement over independent equal-informed symbolic selector, unknown-world safety failure at 2/4 false provisional matches, reused deterministic fixture data rather than authentic independent environmental sources; hence `SCIENTIFIC_PASS=false`, no unrestricted new causal operator invention, no automatic task identification certification and no native product promotion.

**DEPLOYMENT:** NONE. Isolated draft stacked on NKR-12, never merge/promote from these development scores alone. Keep independent Yggdrasil owner, actual native accepted model, protected science datasets, Forge/Wingless/Hybrid lanes, runners, scheduler and production state untouched.

A **genuinely different** next question is whether prospective unknown-law rejection with matched public action budgets can protect unobserved nonlinear source families *without* sacrificing identifiable known-world retrieval. It requires a separately frozen experiment, stronger out-of-family controls and independent source admission; simply labeling these false matches as confident would be invalid.
