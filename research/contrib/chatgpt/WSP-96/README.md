# WSP96 — Randomized interventions against a genuinely hidden common cause

**Only isolated, synthetic research. No accepted Yggdrasil/FORGE intelligence integration, merge, deployment or scheduled work.**

WSP95 (draft PR #1015) reached 595/700 unseen noisy-sensor goals in a qualified original 20-world development cohort, tying fully trained conventional, independent symbolic, and uniform-probing controls. Crucially, WSP95 **did not test confounding**: its nuisance channels drifted independently without influencing the choice of action.

## Plain-English hypothesis

Imagine a machine where an unseen condition both **makes operators choose one control more often** and **changes the reading produced by that control**. Looking at historical logs alone can make the control appear to have an effect it does not actually cause. To learn its real effect, we deliberately choose actions independently of that hidden condition.

WSP96 asks whether directly edited numerical evidence counts can use those **real randomized interventions** to learn which effects are causal and then solve new combinations. This does not imply direct-weight learning beats conventional statistics; a fully trained ordinary model and a symbolic count table receive **identical randomized source data** and are expected to tie.

## Prospective source and first-use custody

The complete protocol `prereg.json` was committed **first** at `6bf44edc2c45f62142f70ff15c5ba8bbcf95a485`, before the generator, learner, test files or original source use. Original public worlds use seeds 96011–96022; reserved original development worlds use 96101–96120. Public-only tests must NOT instantiate reserved worlds.

Each of 6 opaque actions (5 active plus 1 known zero-effect control) has a hidden five-output-bit effect. The **unobserved binary U** shifts two hidden output bits. In passively observed records, U also changes the probability of selecting one special action: 90% versus 4%. Therefore it is a *real unobserved common cause of logged action and outcome*. Neither U, favored action, hidden shift mask nor true action signatures is provided to any model.

The experiment generates exactly **144 randomized do(action) observations per world**: 24 for each of six actions, each with outcome-only five-bit readings, 4% independent measurement error and a hidden 25% U incidence. Randomization breaks the U→action-assignment link. A separate comparison gets **144 observational log records** created under the U-dependent action policy; these are **not equivalent intervention information**, even though the number of rows matches. Learners do not receive the hidden U or the probabilities.

## Bounded models and controls

- **Candidate:** direct integer action-by-output-bit count edits, no gradient, tokenization, transformer or LM; learn each effect bit by the fixed majority response rule under the preregistered U minority mixture. This assumes the latent disturbance is below 50% and is NOT universal hidden-confounder adjustment.
- **Independent symbolic:** genuinely separate action/outcome contingency histogram, independent exhaustive XOR planner, *same 144 randomized do observations*. An exact tie is required.
- **Ordinary fully trained baseline:** 200 full-batch gradient epochs of five-output logistic, source-matched one-hot action input and the same 144 randomized do observations. A tie is permitted and defeats any accuracy-superiority claim.
- **Observational-only naive control:** same numeric majority rule on **144 confounded historical A,Y records**, no randomized interventions. The counterfactual difference shows the value of intervening; NOT proof that direct editing outperforms a correctly randomized baseline.
- **Wrong action binding:** cycle the learned active-action effects under unchanged observation budget. **Deterministic random plan** and **evaluator-only exact causal oracle** complete the negative and ceiling controls.

The model receives twenty NEW counterfactual start/target planning questions/world (all ten active-action pairs and ten triples). It chooses up to three actions; execution of frozen plans against the hidden true effects determines success. Plans, original source record hashes and goal requests are **SHA256-frozen BEFORE inspecting hidden U, action effects or actual outcomes**. The effects used for goal scoring are *causal state changes*, not the U-corrupted single-episode outcome measurement. Model snapshots must cold-restore exactly, remain intact after unrelated worlds, reject corruption and unknown actions, and refuse replayed intervention source records.

Public development: **12 worlds, 240 originally unobserved goals**, 1728 randomized do records plus 1728 passive records, and preregistered original threshold >=200/240 correct, >=35 ahead of naive confounded observational logs, >=75 ahead of wrong action bindings, strong conventional >=190, observed U-based assignment bias in >=10 worlds, accurate causal effects and cold/source-cost checks. A genuine negative is preserved and prevents reserved first-use; no threshold changes after results.

Only after both Ubuntu and Windows public checks pass may a public qualification receipt be committed, followed by G29 source-only atlas regeneration (exactly three generated .ice files), mandatory complete WSP80–WSP96 focused tests and full Yggdrasil root regression on both platforms, and then ONE previously unused reserved DEV first-use (20 worlds, 400 novel planning goals), conditional on both platform passes at exact candidate SHA.

## Scientific limit and next step

This really has an unobserved common cause in the *observational action logs*. But the randomized do-arm uses a deliberately identifiable **known minority-disturbance XOR family** and a pre-programmed finite action-composition planner. It does not solve arbitrary nonidentifiable confounding or infer unknown high-level causal programs. The expected fully trained and independent symbolic ties should be reported without exaggeration. Independent science or general intelligence requires a stronger world, matched fully trained nonlinear learner, frozen independent source, memory interference and a task advantage that remains after equally informed controls.

All research artifacts and original negative/positive receipts remain GitHub-only. No new runner, paid API, ChatGPT Library output, controller, schedule, production action, main ref, accepted model or FORGE loop mutation.
