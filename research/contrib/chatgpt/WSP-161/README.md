# WSP-161 — Protected direct-weight repair of an existing continuous learner

**Source-free numerical development. No original-source reset/step/do, hidden family label, scientific first use, native main adoption, or autonomous controller change.**

## Exact provenance and question

Qualified parent WSP-160 [PR #1213](https://github.com/spoonman136668-ai/Yggdrasil/pull/1213), final head a76f9a566e6a015a130a6b7e3d0376cfa91b3853 (tree 4cf6db0d8f97211fce2795f21a65bd1d15a80f68). Existing WSP-160 implements conventional 10-feature / four-output recursive least squares direct numeric edits, and tied an independently trained batch ridge model. WSP-159 validates public transitions but has never run a live Causal-Gymnasium source; WSP-158 negative calibration is preserved. CKAD remains a separate cumulatively trained Yggdrasil track.

WSP-161 preregistration was committed **FIRST** as sole-file Git commit 9c916956fa743ea97ca2590784a733ac64f6e205, parented on qualified WSP-160. No changes to inherited model code/tests/CKAD; only isolated research contribution plus branch-only qualification and generated derived atlas.

**Hypothesis:** When newly witnessed public dynamics differ only along feature directions not constrained by older observations, can we program updates into the allowed coefficient subspace, preserving old forecasts while actually learning the new dynamics?

## Method: one base + one projected residual edit

- Fit an immutable WSP-160 model on 192 previously witnessed (but entirely fabricated) old public transitions. All old states have public fourth state component s3=0 and alternating observed actions. Freeze model and pick the first 16 already witnessed public state/action inputs. Their 10-dimensional feature span has rank eight.
- Two-pass modified Gram-Schmidt derives a fixed, nonlearned orthonormal rank-eight basis Q for the old source inputs. For every new public input phi, compute z=phi-Q^T(Q phi). No old source outcome, hidden family tag or simulator graph is passed during the new phase.
- Maintain a single additional four-output / 10-feature residual coefficient program plus 10x10 inverse ridge covariance. Each new observed public state transition directly adjusts only residual weights using standard rank-one recursive least squares on projected z, leaving all predictions on protected Q span invariant.
- On a contradictory new outcome that has **no distinguishable projected public direction**, return UNIDENTIFIABLE and refuse the weight edit. This protects old predictions but cannot solve contradictory worlds with identical public features; external memory, new observations or capacity would be required. The rejected event is retained in GitHub test output, not silently interpreted as successful learning.
- Save/load a versioned SHA-256 integrity-bound YPR1 checkpoint containing the original immutable WSP160 base, frozen basis, residual weights, retained covariance and count. This is a classical constrained estimator; an equally informed independent batch constrained ridge must numerically **tie**. Do not claim it is a newly invented algorithm, model-family discovery, or native general intelligence.

## Preregistered source-free comparison

Three fresh nonreserved seeds 607/809/911. Per seed, 192 old FIT, 64 old held VALID, 128 new FIT with publicly visible s3!=0, 64 new held VALID. Data are deterministic local authored **linear** dynamics, identical old law on s3=0, with novel additive s3 and action*s3 effects. The learner sees only public transition observations, never evaluator formulas or a family label. This is a **known engineered rank-two representational extension**, not externally unseen causal-world transfer.

Compare: projected direct edits, unchanged frozen base, conventional continued WSP160, and independently solved strong constrained batch ridge with same frozen base/anchor basis/FIT public observations. Frozen development thresholds: old held forecast drift relative to original base <=1e-9, new held RMSE <=0.03, new gain over frozen base >=0.05, predicted outputs match independent batch ridge <=1e-8. Every earlier-frozen old result is preserved. Report failures as development NO-GO without postscore tuning. Cold byte-exact restoration, resumed update, contradictory-alias refusal, malformed/privileged input, tamper/rehashed invalid basis and capacity negatives are required.

No model receives original external source observations. External CartPoleWind remains static source reference only at CausalAILab/Causal-Gymnasium@c94e9a4cd3641588b6b8507e71ccee5c27032bdf. The user-approved conditional CVH10 13,312-action ceiling is not a qualified source lease; source-owned virgin cohort and actor journal remain missing.

## Reproduction

    python -B -m unittest discover -s research/contrib/chatgpt/WSP-161 -p 'test_*.py' -v

Separate source-free workflow must pass WSP-159, WSP-160 and WSP-161 focused suites on Linux and Windows, mandatory inherited complete root regression + NKR05, and independent exact G29 at the final source SHA/tree. The original action count is **zero**. Source-free CPU times are not full training costs inclusive of externally acquired data, nor evidence of 2x efficiency.

**Engineering:** PENDING qualification.
**Science:** NOT AUTHENTIC FIRST USE; SCIENTIFIC_PASS=false.
**Deployment:** NONE; retain draft/unmerged, no accepted model/controller/scheduler changes.
