# DWSA-RS04 — pairwise coverage is not causal identification

Date: 2026-11-21. Contributor **DEV-only source-free negative control**. Parent candidate: `9aae8adb08ef83542dbd1cae1e978dc305211e38` (RS03). The RS04 test is `transfer_identifiability.test.mjs`; run `node transfer_identifiability.test.mjs` in this directory, alongside `node feature_pairwise_gate.test.mjs`.

## Question and fixed construction

Can RS03's pairwise coverage plus a validation-approved donor establish a positive causal transfer on an unfamiliar three-feature combination?

The deterministic fixture uses the exact same FIT, VALID_OLD and VALID_NOVEL records in two possible causal worlds. Each pair in the unseen pre-action `[1,1,1]` is represented by an observed validation triple (`[0,1,1]`, `[1,0,1]`, `[1,1,0]`). All three VALID_NOVEL rows have `raw=0.5`, the same **constant** `donor=0.9`, and outcome 1. The held triple was not in FIT or VALID; its outcome can be either 0 or 1 without contradicting any observed record. No source, independent donor checkpoint or hidden held data are read.

## Observed source-free result

RS03 admits `gamma=1` and predicts 0.6 on `[1,1,1]` from a raw prediction of 0.5. The two causal worlds are indistinguishable to the gate:

| Unseen outcome | Raw Brier | RS03 Brier | RS03 - raw |
| --- | ---: | ---: | ---: |
| 0 | 0.25 | 0.36 | +0.11 (harm) |
| 1 | 0.25 | 0.16 | -0.09 (benefit) |

Equal-weight risk over the two possible worlds is 0.26 for RS03 against 0.25 for raw. This is a **deterministic identifiability counterexample**, not an empirical estimate of unfamiliar-world frequency or accuracy. A constant donor passes the development gate, so passage alone cannot demonstrate any actual donor-weight assimilation. An unseen key change leaves the result unchanged.

## Disposition and next admissible scientific action

- **ENGINEERING:** focused RS03/RS04 Node fixtures PASS on an isolated source copy. No RS03 behavior or native Yggdrasil code changed. Exact candidate full-platform final regression/G29/CI remains UNVERIFIED.
- **SCIENCE:** negative *guarantee* result: RS03 pair coverage does **not** identify an unseen three-way causal law or establish trained-donor provenance. Scientific gain, native retention and independent causal transfer are UNVERIFIED. This does **not** prove all potential donor methods fail.
- **DEPLOYMENT:** NONE. Protected source actions: **0**. Do not reuse previously consumed DWSA-64/BR01/RS01 cohorts or silently treat synthetic code as original-world data.
- **NEXT:** stop adding pairwise safety layers as a purported route to scientific transfer. A material advance would need genuinely discriminating pre-action mechanism information or authorized action-consequence interventions, a compatible independently trained donor, cold retention and equal-information fully trained controls, all prospectively frozen through existing source owner [issue #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426) (currently NO-GO). Preserve coordinator [PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278) and native tokenless architecture; do not dispatch an actor, merge or promote from this developer gate.
