# FKP-19 — learn actual delayed action credit (known-TRAIN research)

**Status: implementation authored; exact-source engineering qualification and first full 16-TRAIN-world diagnostic still UNVERIFIED. Protected DEV / TRANSFER first-use NOT AUTHORIZED or run. No native integration.**

## The change from FKP-18

FKP-18 [draft PR #1114](https://github.com/spoonman136668-ai/Yggdrasil/pull/1114) established that a tokenless sparse memory can distinguish conditional outcomes and the *order* of two observed events, but merely recording order does **not** establish which action caused a delayed outcome. FKP-17 [draft PR #1109](https://github.com/spoonman136668-ai/Yggdrasil/pull/1109) has a positive known-law training signal and a frozen NO-GO for unconditioned causal representations. Both remain untouched. WSP-120 [draft PR #1113](https://github.com/spoonman136668-ai/Yggdrasil/pull/1113) separately explores contradiction-driven graph-program growth; no grammar or evaluator is copied here.

FKP-19 adds a **physically acted-upon delayed-reward problem**, where the learner must infer from balanced interventions whether reward is attributable to the first or second action. There are no simulated alternative outcomes passed to a learner.

## Provenance and prospective freeze

- Parent: exact qualified FKP-18 commit `362b63ed081298284ac66470e06f9ff7653c4562`; **not main**, intentionally stacked for research-only reuse.
- First and sole preregistration commit: `42642b3834a804a7a866a3de8b79790dc669ef20`. The data family, cohort, action schedule, full controls, optimizer convergence criterion, budgets, negative classification and held-source bounds were frozen before any FKP-19 source, learner, test, scored result or evaluation.
- Source: `public_delayed_source.py` is independent original inspectable TRAIN-only code, not a hidden third-party evaluator. Public seed range **991100–991115**. Protected DEV **991500–991531** and reserved TRANSFER **991600–991663** fail closed, along with FKP17/FKP16 protected/consumed cohorts. No real hidden scientific first-use.
- Each independent environment starts with a publicly visible binary context, then an **actually selected first action** (0/1), with **zero immediate reward**. Only after a separately selected second distractor action does the source report actual reward **+1 or −1**, determined by the first action, context and the private-to-interface source-world polarity. The second action has no causal influence. Source implementation is inspectable, so no external-blindness claim is made.
- Every one of the seven arms experiences exactly **eight identical public exploration episodes per world**: all eight factorial (context × early action × later distractor) combinations, with 16 actual source-public actions; then **16 independent scored episodes**, with 32 physically selected actions/arm/world and no further training during scoring. All 16 TRAIN worlds are evaluated. No post-result tuning or rerun of protected first-use.

## Mechanism and comparisons

`lag_credit.py` reuses the frozen FKP-18 `SparseTemporalTrace` through a checked, research-only import for each two-action public episode, rather than copying or replacing that architecture. The new **ELIGIBILITY_CONTRAST** layer accumulates sparse public reward evidence from the earlier and current *intervened* actions, separately by observable context, and selects the lag with larger matched interventional reward contrast. It chooses a first action only **after** the eight actual observations. It learns a two-step temporal relationship via delayed feedback, not a textual label.

The independently authored **EXACT_BAYES_CONTEXT** comparator fits Beta(1,1) posterior source-observed success rates separately by context and earlier action. **FULLY_FITTED_INTERACTION_LOGISTIC** is a five-feature conventional interaction model (bias, context, first action, context×first action, distractor), trained from exactly the same eight public episodes with gradient descent and a **predeclared** training BCE ≤0.05 within 1,024 epochs, otherwise the comparator gate is INVALID. It is not an RNN; do not misrepresent it as one or claim the strongest possible conventional model has been ruled out. Neither conventional control is given the world polarity or future outcomes.

Four genuine equal-data negatives are included: credit assigned to CURRENT_ACTION_ONLY instead of earlier, CONTEXT_BLIND early credit, EARLY_ACTION_SHUFFLED initial intervention attribution, and NO_UPDATE. All arms take their own physically chosen actions on fresh sessions; report **earned feedback**, not imagined policy scores. Candidate and strong controls are expected to tie on this simple family; a tie is an **absence of unique scientific superiority**.

`test_delayed_credit.py` and `test_prereg.py` check source fairness, physical action-before-result sequence, disjoint protected cohorts, independent Bayesian/conventional agreement, lag contrast, incorrect-sham suppression, bounded cold snapshot, frozen scoring, tamper/history/false-label rejection and source independence. `run_known_train.py` records per-world 16-step actual returns, complete action/transcript SHA receipts, converged standard model receipts, candidate cold parity, source action budgets, per-arm initialization/scoring wall costs and whole-process time; the **10,000 resample, seed 1919** paired world-cluster bootstrap reselects the strongest informed conventional comparator on each replicate. It is descriptive TRAIN science development, **not a protected 95% science acceptance test**.

## Required classification

- **Engineering PASS** only with pinned prereg/source, G29-generated-only child and complete focused/G29/root regression on **Ubuntu+Windows**; preserve independent public-score receipts and unchanged main.
- **Known-family development mechanism signal** only if actual earned delayed rewards outperform all four sham negative controls, while assigning causality to the correct earlier intervention. Do not turn success into autonomous unseen-law discovery.
- **Science NOT RUN / NO PROMOTION:** A candidate tie with exact Bayes or fully fitted conventional logistic demonstrates that public delayed credit is learnable, **not uniquely native learning, efficiency superiority, or an invented operator**.
- **Unfamiliar transfer, persistent cross-world knowledge, cold interference, hidden source-law identification, actual independent acceptance and promotion are not tested**. Any future first-use on held-out worlds needs independent source qualification and owner authority. No other project's code, owner, runner, accepted main, scheduler, paid API or trading boundary may be changed.

**Original FKP-19 scores not yet available at this source-authorship checkpoint.**
