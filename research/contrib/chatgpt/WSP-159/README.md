# WSP-159 — Strict public boundary for unfamiliar continuous causal dynamics

**Research-only source-free engineering. No original-source training, new model weights, protected first-use or scientific PASS.**

## Exact provenance

- Existing qualified parent: WSP-158 PR #1209 at SHA 256cf3c240524ba009016d09ba5c8543b537411f (science NO-GO).
- Preregistration sole-file first commit: 20a367d38e4a3525e914520ab348a3bbd02ced78.
- Independently authored upstream: CausalAILab/Causal-Gymnasium at c94e9a4cd3641588b6b8507e71ccee5c27032bdf.
- Original environment module: causal_gym/envs/cartpole_wind.py, Git blob d65a6a31941709dc9201259d80dd4ebbcf48b4fa.
- Original PCH API: causal_gym/core/pch.py at same upstream SHA; license Apache-2.0, LICENSE Git blob 993e3a4922f003dced0fd061735697c850ea7205.
- CKAD-18 remains independent. No existing native Yggdrasil or CKAD files are edited.

## Contract

Original CartPoleWind provides 4 public observation values, binary selected action, public next observation/reward, and terminated/truncated booleans. Its hidden wind and SCM state are not allowed learner data. Upstream CartPoleWindPCH.do executes a real source action and returns info; the untrusted info payload MUST NOT be sent to any learner. Neither may the graph, env, natural policy, ctf_do, private wind, unwrapped source object, source key or evaluation outcome.

public_boundary.py is pure Python and does not import NumPy, Gymnasium or the upstream simulator. The future approved runner must convert upstream NumPy state to an ordinary Python list via .tolist() and provide only the explicit public fields:

    PublicTransition.from_public(
        observation=(x, xdot, theta, thetadot),
        action=selected_action,
        next_observation=(x2, xdot2, theta2, thetadot2),
        reward=public_reward, terminated=done, truncated=timeout)

Immutable public-only record values are copied defensively and serialized as canonical ASCII JSON with SHA-256 digest; restored records are checked for byte-exact canonical content. Missing/extra/private fields, wrong actions/flags, non-finite floats, shape errors, duplicate JSON fields and altered bytes are rejected. A record hash is data INTEGRITY, NOT external action provenance or authorization. Authentic original action/source custody must come separately from a properly authorized independent owner-signed actor/journal.

## Reproduce the source-free engineering tests

    python -B -m unittest discover -s research/contrib/chatgpt/WSP-159 -p 'test_*.py' -v

Fixtures are fabricated only. No original source resets, steps, do/ctf_do interventions, protected labels, model weight training, or paid calls. The scoped one-shot GitHub CI branch workflow runs source-free focused Linux+Windows checks, creates three derived source-atlas files only once, and checks full root/NKR05 and G29 on exact final candidate source. Keep draft/unmerged.

## Scientific successor: separately qualified first-use required

Prior experiment WSP-158 found a narrow already-consumed stochastic DTR regime where optimized native calibration TIED an independently fitted calibrator; do not retune it. Future WSP-159 study must instead use genuinely unfamiliar external causal families with sufficient improvement headroom, same observations and policy action rights for each arm, fully converged strong conventional and independent model-based controls, exact matched budget, source-owner signed new cohorts, preserved held-outs and source-authenticity receipts. The conditional 13,312 original source-action CVH10 ceiling does NOT confer WSP159 authority.

A future native weight program must preserve previously learned causal structure while updating dynamics and measure actual intervention value, old-task retention, unfamiliar transfer, cold checkpoint validity, errors, and whole-process time/cost. Preserve Yggdrasil tokenless foundation. Do not duplicate CKAD's sparse solver, property-plane accumulation or stochastic cached histories.

**ENGINEERING:** pending exact dual-platform full regression and G29 for branch implementation.
**SCIENTIFIC:** UNVERIFIED / no primary performed; original source actions = zero.
**DEPLOYMENT/MERGE:** NONE, no accepted main/controller/runner/scheduler/ref promotion.
