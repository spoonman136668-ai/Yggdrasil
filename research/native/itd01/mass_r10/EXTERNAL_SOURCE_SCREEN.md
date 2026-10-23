# Mass Research R10-U — upstream external-source compatibility screen

**Evidence status:** READ-ONLY UPSTREAM SOURCE REVIEW / NO COHORTS / NO CKB ADMISSION.
**Local base:** independently scoped [Mass R10-I #424](https://github.com/spoonman136668-ai/Yggdrasil/pull/424), exact head `51a0a091aeb961c59e2d0d9407fa8492d8491d1b`. This candidate appends this review without altering the mathematical proof, its 8 focused tests, original source-free data or the frozen [native R10 #422](https://github.com/spoonman136668-ai/Yggdrasil/pull/422) protocol.

## R10-U question

Is a **genuinely third-party authored** causal environment already available that satisfies R10's frozen *native* interactive contract **as-is**, and can be independently witnessed and admitted before the first R10 adaptation episode?

R10's relevant frozen requirements are: four Boolean public sensory inputs, one binary latent; legal public `observe/probe_0/probe_1/commit_0/commit_1` actions, causal consequences/feedback delayed at least two steps and token-bound to originating actions; training and independently unfamiliar **non-isomorphic** structural families; identical maximum 32 public adaptation/probe episodes for every model; full learner and baseline cost/first-use/source custody. The source implementation and source-identity witness must be independent of the model-authoring lane.

**Method:** Inspect existing *public upstream Git commit contents* at immutable full SHAs (not scraped benchmark scores); read-only metadata/API examples with pinned Git file blobs. Do not clone into the private learner as training input, generate seeds/scenarios, test an actual episode, train a model, pull Docker images, import code, touch heldouts, or claim an independent first-use certificate. Published, openly inspectable upstream code is independent authorship, but NOT an authenticated untouched heldout by itself.

### 1. DeepMind Alchemy — viable future independent transfer track; R10 interface mismatch

- Upstream: `google-deepmind/dm_alchemy`, branch `master`, exact full commit `68a26254b5c0f15e84fa0c15d66bf0c626ede8e0`, publicly archived/read-only.
- README Git blob `22ce25cec896cf4892cadcba61cc264b27f3ced0`. Task/observation/action documentation `docs/index.md` blob `77f540812c7bc63b7d01b62d9cbd81e61587d70f`.
- Exact pinned sources: https://github.com/google-deepmind/dm_alchemy/blob/68a26254b5c0f15e84fa0c15d66bf0c626ede8e0/README.md and https://github.com/google-deepmind/dm_alchemy/blob/68a26254b5c0f15e84fa0c15d66bf0c626ede8e0/docs/index.md.
- The public task uses latent potion/stone relations, a symbolic `stone-to-potion-or-cauldron` integer action interface, discrete/binary stone-potion feature vectors, and optional full 3D action/visual mode. The documented 3D environment requires Docker/Linux and offers nine continuous-control channels rather than R10's five discrete actions.
- **Decision: NOT DIRECTLY ADMISSIBLE** into the fixed R10 four-binary-sensor, five-action, >=2-delayed-feedback interface. A symbol-level adapter would be a *new engineering design*, must preserve the original benchmark's causal laws and learner information while proving action/observation/latency semantics; do not call such an adapter externally witnessed just because the upstream is external. The original source can be considered for a distinct prospectively frozen R11-style transfer track without modifying R10 scores.

### 2. Causal-Gymnasium — actionable `do` interventions; no verified family-diversity or delayed-feedback match

- Upstream: `CausalAILab/Causal-Gymnasium`, branch `main`, exact full commit `c94e9a4cd3641588b6b8507e71ccee5c27032bdf`.
- PCH intervention wrapper `causal_gym/core/pch.py` blob `ff37780c6b791877c70583b8d5f699be7fcd8817`; inspected tabular confounded binary MDP `causal_gym/envs/mdp.py` blob `6264ec5450754c009e98c3e85f6d5927ece0a9ab`. License file blob `993e3a4922f003dced0fd061735697c850ea7205` appears to contain Apache 2.0 text; verify license integrity independently before incorporation.
- Pinned sources: https://github.com/CausalAILab/Causal-Gymnasium/blob/c94e9a4cd3641588b6b8507e71ccee5c27032bdf/causal_gym/core/pch.py and https://github.com/CausalAILab/Causal-Gymnasium/blob/c94e9a4cd3641588b6b8507e71ccee5c27032bdf/causal_gym/envs/mdp.py.
- The inspected `MDPSCM` has binary state/action/reward, **three exogenous disturbances**, and a two-action `do` policy; it supplies a reward in the same transition and defaults to 30 maximum steps. Its `PCH` wrapper supports causal `see`, `do`, `ctf_do`; this is genuine intervenable public code, not a frozen R10 native 4-sensor/one-latent/five-action, two-step-delayed-credit interface.
- No authentic non-isomorphic training/future holdout causal family witness or 32-action identifiability certificate was established by reading this single module.
- **Decision: NOT DIRECTLY ADMISSIBLE** under frozen R10, though potentially a useful independent future causal-MDP research suite after prospectively defining a compatible challenger source and checking privileged `info`/graph fields for leakage.

### 3. CausalGame (2026) — independent hidden SCM gameplay; deployment budget and action mismatch

- Upstream: `CausalGame/CausalGame`, branch `main`, exact full commit `34223510a0e7466ad399ff19714425f8708b7fbe`.
- API contract `docs/api-reference.md` blob `d57ee2e5fd7e0848f3659fa77d2a952f762234d5`, SCM-extensibility documentation `docs/adding-new-scm.md` blob `2bf27bcc02f53e471550d074b1fe3053bb8586e2`, source experiment configuration `experiments/antenna_trap/game.json` blob `0c8fdf2acdf9e6d2b7538da5633d9832b091e707`, MIT LICENSE blob `f94c5511bebe3de9c73e59dcc99ea0ed40443dde`.
- Exact pinned sources: https://github.com/CausalGame/CausalGame/blob/34223510a0e7466ad399ff19714425f8708b7fbe/docs/api-reference.md and https://github.com/CausalGame/CausalGame/blob/34223510a0e7466ad399ff19714425f8708b7fbe/experiments/antenna_trap/game.json.
- Documented agent API allocates up to **ten Stage-1 deployment calls**, a total of **200 drones**, then an irreversible final design for 1,000 drones. Experimental design varies protection of multiple drone components, uses censored deployment outcomes and more complex SCMs (14 scenario configurations found in `experiments/`).
- Changing the native 10-deployment budget to 32, suppressing existing dimensions into four Booleans, or exposing hidden environment effects would create an adapted derivative benchmark, **not direct use of the externally specified experiment**.
- **Decision: NOT DIRECTLY ADMISSIBLE** to native R10 as frozen. Potential value as a prospectively separate interactive scientific-discovery suite after preserved source-first-use and resource-appropriate model interfaces are defined.

## Strict gate conclusion

| Source | Independent publisher verified at pinned Git SHA | Native R10 interface and 32-probe semantics proven | Independent non-isomorphic unfamiliar families admitted | Outcome |
|---|---|---|---|---|
| DeepMind Alchemy | YES (public historical source) | NO | NO | NOT_DIRECTLY_ADMISSIBLE |
| Causal-Gymnasium selected MDP | YES (public historical source) | NO | NO | NOT_DIRECTLY_ADMISSIBLE |
| CausalGame | YES (public historical source) | NO | NO | NOT_DIRECTLY_ADMISSIBLE |

**R10_SOURCE_NOT_ADMISSIBLE_FROM_THREE_SCREENED_UPSTREAM_CANDIDATES / R10_EXTERNAL_FIRST_USE_NOT_PERFORMED / ACTUAL_R10_SOURCE_CERTIFICATE_NOT_ESTABLISHED / R10_IMPLEMENTATION_NOT_STARTED / CKB_ADMISSION_NOT_OBSERVED.**

This is a scoped negative **compatibility** finding, not a proof that no suitable benchmark exists anywhere. Do **not** fabricate a source, alter frozen native R10 protocol/32 budget after post-hoc inspection, substitute publication for independent first-use, or route a third-party benchmark through a hidden shape-transformer that leaks privileged labels. The proper next decision is either independently identify and certify a genuinely native-compatible source under a separate source-first-use witness or **close unexecuted R10 for source incompatibility** and preregister a new explicitly original-format external benchmark track after retaining the negative.

### Governance

CKB-plane is sole execution/admission/queue/first-use authority. This read-only source screen is *advisory evidence*, not a worker instruction, Code Atlas repair, qualified build, GH merger, protected branch change or scientific acceptance. Separate inherited Yggdrasil G29 source ancestry failure and R7Q [#601](https://github.com/spoonman136668-ai/ckb-plane/issues/601) remain unresolved, not bypassed.
