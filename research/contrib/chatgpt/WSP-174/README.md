# WSP-174 — Source-free chemistry public-evidence boundary

**Engineering only.** This is not a learner, a source-first-use job, a source lease, a training recipe, accepted Yggdrasil source, or scientific qualification. Original source resets/steps/interventions in this branch: **zero**.

## Original-source pin

- Independent upstream: `dido1998/CausalMBRL@2c595988b06b3d568fdde53213029e97841acb03`.
- `envs/chemistry_env_rl.py` blob: `58af54d7e7e30f8abe059df3d68565845a5b2c51`.
- MIT `LICENSE` blob: `cff393fe08ddf5fdd6fa4b8f509df9789bf54900`.
- Original source public `get_state()` produces a `(25,5,5)` one-hot object/color/position representation. Original `reset()` returns current and target (goal) public states; original `step()` returns public next state and reward `matches/5` plus `done=False`. The 25 actions select one of five objects and one of five colors; descendants are updated by source-owned MLPs and graph. This code does not fetch those private weights or graphs.

## Bounded bridge, not the simulator

`PublicEvidence.from_public(current_state=..., goal_state=..., action=..., next_state=..., reward=..., done=...)` accepts only pure Python lists/tuples from a future **independently approved** owner's public extraction step. The owner alone is responsible for converting NumPy arrays using `.tolist()` and for pinning exact dependencies/source and counting physical source actions. The bridge imports only Python's standard library and makes **no** source calls.

It checks 25x5x5 shape, exactly one color/position per object, unique positions, 0..24 discrete action, fixed object positions through the intervention, acted object's selected resulting color, literal source-`done=False`, reward increments and equality to the public returned goal/next state. All test tensors are fabricated negative-control fixtures, **not protected original results**.

`policy_input()` provides only current and publicly shown goal coordinates/colors; it does not disclose action consequences or reward before execution. `learning_record()` includes the public action and observed consequence **after** the step, with deterministic immutable ASCII JSON and SHA256 restore. No hidden source DAG, MLP weights, source random states, `actions_to_target`, evaluator labels, source seed or lease is accepted. A caller cannot reconstruct independently hidden graph truth just because it can inspect public reward.

## Important limitations and denial rules

- The original source's `step()` never sets `done=True`; an **owner-governed** externally imposed cap must be logged separately, without recoding a truncation as original termination. This gate never chooses such an execution cap.
- The target goal is an actual **public reset output** in this source; other environments must not assume goals are public.
- The bridge's scene extraction intentionally omits raw image features; all comparator arms must be granted the same registered public representation before any scientific test. This is an interface convention, not a trained encoder or representation-learning result.
- This guard checks *structural agreement of a purported public record*, not authenticity of a physical source action. Only a source-owner effects journal, signed first-use lease and independently qualified actor can attest original data origin.
- The upstream source's global `numpy`, Python `random` and PyTorch RNG usage remains unqualified. No original runtime, GPU, 10-step episodes, fully trained controls, new-world transfer or convergence is evidenced here.
- The 13,312 original action conditional maximum is **not** permission; CVH-10 first-use remains denied.

## Qualifier

Focused test: `python -B -m unittest discover -s research/contrib/chatgpt/WSP-174 -p 'test_*.py' -v`.

The branch-only CI follows existing WSP-169 architecture: isolated focused tests and inherited WSP-159–169 regression both OS; one bot-generated G29 atlas (only three derived files); then exact-final full root/NKR05 and independent G29 on Windows+Linux. A source-boundary engineering PASS cannot be promoted as a scientific PASS or approval to call an original source. Nothing in native `yggdrasil/`, CKAD, Forge, source owner, main or live runner is edited.

Source-owner work item: https://github.com/spoonman136668-ai/Yggdrasil/issues/426
Original WSP-169 parent: https://github.com/spoonman136668-ai/Yggdrasil/pull/1227

**Status at authoring:** local isolated source-free tests passed 8/8. CI, exact-final G29 and full dual-OS qualification pending; science first-use NO-GO / deployment NONE.
