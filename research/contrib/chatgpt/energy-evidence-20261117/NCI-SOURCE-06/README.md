# NCI-SOURCE-06 — A first-coordinate guard must not be installed globally

**2026-11-19 | Independent Yggdrasil contributor | engineering analytic PASS | scientific result UNVERIFIED**

## Source-bound compatibility

Research Amalgam head: `86264b41a08d49f558418c0fba367f3a2636befa` (draft PR #1278). The following *actual GitHub source blobs* were read at that exact ref:

- `yggdrasil/native_causal_amalgam.py` blob `287e6fbb9d1f9612f88f9d5ed5dda88be4bb7952`: `NativeCausalAmalgam.activate()` requires projection 0 (`AMALGAM_PUBLIC_COORDINATES`). It is the exact **proposed**, not installed, NCI-SOURCE-03/04 first-statement guard's scope.
- `yggdrasil/native_episode_experience.py` blob `5a18b00a4c4131526e71f51d63dfd9eb9471c81e`: `_context()` uses a **learned** projection (0, 1 or None), comparing the *selected* coordinate in both views. The learner can select projection 1 from witnessed mismatch rates.
- `yggdrasil/native_cumulative_learner.py` blob `1bdeaa4277fc9b34bbf7c0f36c6d0a4cc00e1ca4`: generic `observe_experience` accepts this episode memory without always enforcing projection 0.
- `research/contrib/chatgpt/CKAD-26/campaign.py` blob `a756bf47b7c475946e2ef696cc3c3ee0d176eaac`: `retained_packet` explicitly reconstructs `row["s1"]` using `views[0][projection]`, from **the existing model's** episode-state projection.

The generic native source supports a valid agreement on coordinate 1 even when coordinate 0 differs. The earlier NCI-SOURCE-05 audit (2,456/2,456 historical *Amalgam* development rows consistent with projection 0) does **not** prove that a coordinate-0 guard is safe for the older generic learner or existing projection-1 checkpoints.

## Exhaustive finite negative control

`reproduce.py` evaluates two public-view contracts, not simulated source actions: for each projection, enumerate 2^7=128 cases (shared context bit, two other view bits, and `x1,s2,x2,y`). Construct `row["s1"]` from the correct projected context and compare to the Amalgam-only proposed predicate `row["s1"] == views[0][0] == views[1][0]`.

| Source-valid coordinate | Valid events | Accepted by coordinate-0-only guard | **Wrongly rejected** |
|---|---:|---:|---:|
| Projection 0 (fixed Amalgam) | 128 | 128 | 0 |
| Projection 1 (possible generic native) | 128 | 32 | **96** |

Example projection-1 source-valid evidence: `views=((0,0),(1,0))`, `row["s1"]=0`; the second coordinates agree, the first do not. Its source-visible context is identifiable *at projection 1*. No model was trained or consulted in constructing these mathematical cases. This does **not** show a real owner checkpoint currently selects projection 1; that is unverified.

**Disposition:** The *proposed* consistency guard may be qualified only at `NativeCausalAmalgam.observe_experience` with its verified projection-0 parent. **DO NOT** insert it indiscriminately in `NativeEpisodeExperience.observe`, `NativeCumulativeLearner.observe_experience` or all callers. A generic future source validator must use an authenticated existing model projection and real public field provenance, never a caller-forged projection. Never rewrite the ledger or old weights to force a match.

## Verification / authority

Reproduce: `python -B reproduce.py`. The exact stand-alone script was run locally twice with identical JSON results. A fuller, optional original-source blob/AST check and the same finite enumeration are bundled in the turn's `NCI-SOURCE-06-evidence.zip`; GitHub source identities were independently read from the GitHub connector, **not** through a local clean checkout. No full original source-imported native execution, real checkpoint cold restore, full Ubuntu/Windows regression or original-world scientific first-use has been performed.

**Engineering:** finite scope/counterexample PASS, original source blob readback PASS; native checkpoint/required full final regression UNVERIFIED. **Scientific:** no causal learning gain claimed; earlier ENERGY negatives intact. **Deployment:** NONE. No checkpoint owner, trainer, native model, scheduler, merge, accepted `main`, or original source lease changed. Owner-held checkpoint still unverified under LINEAGE01 #1322; protected new original-world first-use still blocked by source-owner issue #426.

**Central integration authority:** Sole Unified Causal Intelligence Amalgam Work chat; this is an independent contributor submission through existing research PR #1210, not an accepted model change.
