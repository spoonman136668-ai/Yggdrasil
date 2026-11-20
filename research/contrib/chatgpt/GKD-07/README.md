# GKD-07 — GPT donor prior versus a real historical randomized intervention

## FINAL RESULT — SOURCE-ID NO-GO (not a scientific test)

**The unique-identity source check failed before any treatment-effect model was fitted or evaluated.** The one exact source attempt at [CI #44829776242](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44829776242), source commit `3c6c18dde8ecaf3bc2cad81488216c711fb4c885`, stopped with `GKD07_FAIL_CLOSED:DATA_ID_UNIQUE`. First row numeric fields were parsed before the second row exposed the collision; no FIT/VALID/DEV folds or pseudo-outcome scores were produced. This cohort is not clean untouched first-use.

A *subsequent source-metadata-only* audit of the pinned Rdatasets CSV (Git blob `1ea4da5f9f6106f984a5766376546fef662f7ae0`) found **445 records, one distinct `data_id` value, and 445 distinct `rownames` values**. The R package documentation labels `data_id` as an individual ID, but this particular export stores one dataset-wide value. No participant outcomes were analyzed by the metadata audit.

**Do not silently switch to `rownames` and rerun GKD-07**. The original public dataset has been touched, and the prospective unique-ID split assumption failed. Preserve the original code, split, prior and negative result. This is source/schema failure, **not donor inferiority or superiority**; scientific effect remains `UNVERIFIED`. The separate earlier GKD-06 Sachs donor negative remains valid.

Full machine-readable [source-only result](result.json) and [custody evidence](provenance.json) are archived. No accepted Yggdrasil model or weights were changed.

---



**Contributor research; prospective historical public DEV, not independent original-world first use.** Frozen preregistration FIRST: `872472cf6c068ac9b320491f83e2fd8fdf760564`, before any numeric NSW trial record was accessed. Accepted Yggdrasil native model `main@5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` untouched.

## Why this is a new question, not Sachs replay

GKD-06 [frozen real published negative](https://github.com/spoonman136668-ai/Yggdrasil/pull/1348#issuecomment-7052011482) established that a GPT-supplied candidate protein-parent mask **lost by 2.68% normalized RMSE** to a conventionally learned 2-feature alternative in *same-cell conditional prediction*. That is **not an intervention-effect estimate**. Replaying those 9 published Sachs groups would not be fresh evidence.

GKD-07 instead tests **actual historical randomized assignment** from the National Supported Work (NSW) job-training trial, reported in LaLonde (1986) and Dehejia–Wahba (1999), as provided in [causaldata::nsw_mixtape](https://www.rdocumentation.org/packages/causaldata/versions/0.1.3/topics/nsw_mixtape). Source is pinned to [Rdatasets Git commit `1dcc2bf5f955cc1224a3e1307256e1fe86b68dae`](https://github.com/vincentarelbundock/Rdatasets/tree/1dcc2bf5f955cc1224a3e1307256e1fe86b68dae), path `csv/causaldata/nsw_mixtape.csv`. The study involved **445 anonymized original experimental observations**, **185 assigned treatment and 260 control**. No nonexperimental PSID/CPS controls, paid APIs, private participant records, new human experiments or local/owner runners. Public source SHA-256 is recorded on first bounded download.

**Author-supplied prior, explicitly speculative:** `ATE(re74=0 AND re75=0) >= ATE(other pre-earnings)`. It assumes NSW job training benefits the previously zero-earning group at least as much as other participants. GPT output (not GPT weights) supplied this monotone constraint. There is **no claim that this is true** or that GPT had not seen NSW literature during pretraining.

## Causal evaluation and equal-information controls

The target is the average **causal effect of randomized program assignment on recorded 1978 earnings** conditional on pretraining earnings. Randomization permits unbiased pseudo-outcomes `Z = treat * re78 / (185/445) - (1-treat) * re78 / (260/445)`. This is an unbiased conditional-effect surrogate under randomized assignment and a common propensity, **not an observed individual potential outcome**. Unlike the Sachs task, no contemporaneously observed downstream outcomes are used as predictors.

The exact ID-based split is frozen: treatment arm 111 FIT/37 VALID/37 DEV and control arm 156 FIT/52 VALID/52 DEV, sorted by SHA256 of `GKD07-fold-v1|data_id`. The learner receives only FIT earnings/outcomes. Donor candidate pools subgroup FIT experimental contrasts whenever the frozen prior ordering is violated; it otherwise retains separate subgroup effects. Matched fully fitted controls are pooled randomized experimental difference, unconstrained FIT subgroup differences, and an eight-feature interacted ridge (using only treatment, pre-1974/75 earnings and the donor's zero-earner group). An ordinary identical shape-constrained implementation is an **equal-information tautological tie**, not an independent algorithm. A reverse-monotonic constrained prior is the sham.

VALID selects the strongest conventional model without seeing DEV. One reserved DEV cohort (89 trial participants) evaluates pre-specified pseudo-outcome RMSE; a fixed-seed paired 2,000-bootstrap interval and two predeclared heldout halves provide uncertainty and safety diagnostics. **PUBLIC_DEV_SIGNAL** requires donor >=5% RMSE improvement over both VALID-selected conventional and sham, lower bootstrap 95% percentile strictly >0, and nonregression in each DEV half. Do not retune, reorder, reread or re-split the data after the original score.

The standard baseline `unconstrained_group_diff` has **the same two groups** as donor; if the GPT prior supplies no genuinely predictive ordering information, it should not improve. No trained transformer, token sequence, native recurrent cognition, or general intelligence is evaluated here.

## Reproducibility / custody

- Offline test only: `python -B research/contrib/chatgpt/GKD-07/run.py --selftest`, source-free synthetic fixtures in existing Linux/Windows PR G29 regression.
- One-shot source/test: `python -B research/contrib/chatgpt/GKD-07/run.py --score-public`, **only from the unique exact commit subject** `research(GKD-07): SINGLE_PUBLIC_RCT_SCORE` in the existing GitHub-hosted Linux job, after source-free qualification.
- The source must have exactly 445 experimental rows, 185/260 treatment balance, unique data IDs, finite numerical outcome and pre-earnings, and exact documented headers. R's optional `rownames` CSV export column is ignored, never used as a feature; any other variation fails closed. Record complete source SHA-256, all validation scores, primary DEV loss and negative controls.
- The original outcome is a *historical published RCT*, not a live experiment or first-use external model trial. Assignment propensity is approximated by the 185/445 empirical treatment fraction; uncertainty from this, a small validation sample and potential prior source exposure limit interpretation.
- Even if a positive historical public DEV signal occurs, **SCIENTIFIC_PASS=false** until independently sourced trial reproduction, verified pretraining leakage controls and native Yggdrasil learning/retention. This contributor never promotes models, checkpoints, controllers, owner runners, merge, or deployment.

A fully scored negative is scientifically useful. **No scientific result or model change should be claimed until source is admitted and both outcomes and controls have been run under frozen code.**
