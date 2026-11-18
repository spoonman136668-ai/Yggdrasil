# WSP-168 — Compositional action-effect learning with retained old/new relationship retrieval

**Source-free, research-only contribution. No original protected external-world actions, no accepted model/CKAD/controller/scheduler change, and no deployment or merge.**

## Exact predecessor and scientific motivation

Qualified predecessor WSP-167 [PR #1224](https://github.com/spoonman136668-ai/Yggdrasil/pull/1224) final SHA \`8ae7e116ac3de2510a447a53ef6324c20bfba4fd\`, tree \`3773105113de8d64b27e0dac25045edf7a70d4ea\`, full dual-OS #44279203845 PASS and independent G29 #44279209781 PASS. The source-free direct-weight feature tournament chose a preauthored \`s0*s1*s2\` feature in all three replicas and produced portable exact-rational component checkpoints. It also **FAILED** entirely unrepresented degree4 transfer and **FAILED** retrieval of old action1 relationships after adapting to new action1 data. Those frozen negatives are retained, not overwritten.

WSP-168 tests (a) *constructing* feature candidates using a compositional multiplication operator on the previously selected triple and (b) *retrieving* an intact old or new action-conditional relationship based on the previous witnessed PUBLIC action1 consequence rather than a hidden family label. **This is bounded symbolic composition and one-step observational change detection, not arbitrary free-form feature invention, real-world causal intervention or newly discovered general intelligence.**

- Prereg-only first SHA \`119573189016f2a3d79ce26b5ebb436b4bb0c01f\` directly on the qualified WSP167 parent. Source and test/evaluator SHA must be frozen BEFORE first CI scoring and referenced in the qualification workflow.
- All existing WSP-159–167, CKAD, Yggdrasil native main and original protected source artifacts remain unchanged. New code stays in \`research/contrib/chatgpt/WSP-168/\`.
- No original CausalAILab/Causal-Gymnasium original reset, step, do, ctf_do or protected first use (0 actions), no virgin first-use owner-signed cohort/actor lease. CVH10 historical conditional cap is not WSP authority.

## Compositional public relationship construction

Use the WSP166 256-state dyadic GRID, shuffled afresh by frozen seeds \`3427, 3539, 3659\`; each has first 48 public paired FIT states and next **48 disjoint** held states on the same finite state support. The synthetic generator provides public witnessed action0/action1 alternative outcome records at the exact same state; this is an artificial capability of the *fixture*, not evidence of externally permitted source counterfactuals.

Train one frozen WSP160 historical old-family parent on 96 old public FIT action outcomes. Old action0 and action1 behavior remains archived. New synthetic law has the same action0 public transition, but its action1 contrast includes prior bilinear polynomial contributions + the prior third-order interaction \`s0*s1*s2\` + a NEW quartic interaction \`4*s0*s1*s2*s3\` with fixed output coefficients. Generator coefficients exist **only in the tests**, not in learner input. Learner sees strictly WSP159 whitelisted public state, selected action, witnessed next state, reward, terminal flags and no private regime/coefficient/future value.

The new learner starts with the PREVIOUSLY selected 9-feature public grammar (eight old features plus \`s0*s1*s2\`) and applies exactly one composition operator:

    candidate_i(state) = previous_public_triple(state) × state[i]
    for i in {0,1,2,3}

There is **no hardcoded quartic term selection**. From 48 witnessed public paired new-law FIT states, use 36 only for an exact-rational 9-feature ridge null and four independent 10-feature candidates (ridge 1/64), then rank all on the separate 12 WITHIN-FIT selection pairs. Select the best if it improves RMSE by at least .01 over null; otherwise select NONE. Finally refit one 9/10-feature exact-rational directly written effect model on all 48 FIT pairs. Never use any of the 48 true held states to select or tune. The isolated trained effect (and covariance) serializes as SHA-256 integrity-bound canonical reduced numerator/denominator strings for strict Linux/Windows portability and separate-process cold restore.

All mathematical components are familiar (polynomial feature products, regularized RLS, selection by held inner-FIT error), so a fully FIT independent conventional batch ridge with the same selected feature and training records is a mandatory strong control. Independently implement the same four-candidate conventional batch inner tournament, plus fully FIT 13-feature all-composition conventional model and a 9-feature same-ridge direct control. Conventional ties do not establish native training superiority.

## One retained model: public-feedback law retrieval

The opt-in \`RetainedPublicLaws\` object contains two immutable relationship memories: the original frozen 4D old-family action-conditional public predictor and the newly trained composition effect. This is one model containing two stored relationships, not a second Yggdrasil autonomous learner, native controller or source-family oracle.

For action0 always use the archived action0 predictor. For action1 with **no prior witnessed action1 public outcome this episode**, use the old head. Once a previous public action1 transition has actually been witnessed, calculate its four-output squared prediction error under the old and new heads and choose the head with less error; ties choose old. A prior public action0 outcome conveys no evidence about action1-specific law and does not select new. This uses only the most recent within-episode public action1 record; never read current target before prediction. Reject previous terminal/truncated event as stale source contamination and reset each episode. There is no hidden source-mode id, future target, or privileged intervention.

Simulated held stream per seed: 16 episodes ×12 steps, on held public states, four old-only, four new-only, four old→new switching at step 6, four new→old switching at step 6. All *public action1* observations are delivered **after** each forecast. Score separately (i) first step with no evidence, (ii) first step immediately after a source rule switch (necessarily lagged), (iii) strictly after one already witnessed post-switch outcome, (iv) old-only and new-only persistent later steps. Simulated world identity is used to define source outcomes and evaluator score buckets ONLY; the model never receives it.

Independently trained fully FIT conventional new polynomial batch weights + identical public-last-outcome retriever is a strong same-information control; also show always-old, always-new, and an **oracle true-regime upper bound explicitly NOT AVAILABLE to the learner**. This directly measures old law retention, not just whether old weights still exist on disk.

## Frozen thresholds and explicit hard negative

Per seed, predeclared construction passes only if learned factor index=3 (previous triple × state3), held new action1 effect RMSE <=.020, improvement over same-ridge 9-feature >=.08 and independent conventional matched 10-feature forecast gap <=1e-8. Retention passes only if later-step old-only, new-only, old→new **after one new witness**, new→old **after one old witness** RMSE each <=.020. First-after-switch and first-of-episode errors must be reported unfiltered. All three seeds required.

A separate fifth-order unexposed new-source term \`4 × (4*s0*s1*s2*s3) × s3 × (1,-.75,.75,-.5)\` appears only in a held synthetic negative. It is **outside the single-step multiplication candidate set**. Held fifth-degree effect RMSE <=.08 across all seeds is a separate transfer-development signal; otherwise preserve NO-GO, do not tune after scoring.

Independent fully fitted conventional batch 10-feature and switching controls may tie or win; component byte determinism is distinct from inherited float parent byte portability and complete Yggdrasil reproducibility. Python CPU timings are not end-to-end wall-clock/cost superiority. Original-world \`SCIENTIFIC_PASS\` is always false because original actor/virgin source custody is missing and the paired source is authored synthetic.

## Reproduce source-free tests

    python -B -m unittest discover -s research/contrib/chatgpt/WSP-168 -p 'test_*.py' -v

Branch-only frozen workflow runs WSP159–168 focused, complete inherited 195/195 root regression and NKR05 6/6 on Linux and Windows, then independent G29 on exact final SHA/tree. The atlas generator is limited to exactly three derived \`.ice/code-atlas.*\` files. Never merge or claim all repository-global workflows green based on this scoped qualification.

**ENGINEERING:** pending source-free CI qualification.
**SCIENTIFIC:** source-free representation and memory retrieval development; native Yggdrasil/generalization and original-source first-use unverified; no conventional superiority.
**DEPLOYMENT:** NONE. Draft/unmerged.
