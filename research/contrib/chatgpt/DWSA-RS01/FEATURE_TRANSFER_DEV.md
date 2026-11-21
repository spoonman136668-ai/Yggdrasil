# DWSA RS02 — source-free pre-action feature transfer (development only)

Date: 2026-11-21. **ENGINEERING: focused local PASS, full candidate qualification UNVERIFIED. SCIENCE: no original-world evaluation and no gain verified. DEPLOYMENT: none.**

## Ownership, source and purpose

- Research contributor branch: experiment/dwsa-br01-bounded-correction-dev-20261121, starting from exact SHA b9026c56a83ba74891e7caf072fb7c545986b00a.
- Accepted main remains 5e74f8db85b2f5839c42148c0dfba69a88b1a2c9; unified coordinator is [PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278). Protected new original-world first use is **NOT AUTHORIZED** by [issue #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426).
- Original RS01 gate, its pinned retrospective inputs, historical DWSA-64 and BR01 negatives and all native checkpoints are **unchanged**. No consumed source is replayed or relabeled as fresh.
- Question: Can a source-free developer gate generate a nonzero bounded donor adjustment on a previously unseen *context key* or unseen *combination* of public pre-action features without exact-key allowlisting? This is not a test of transfer between genuinely unfamiliar causal-law families.

## Fixed developer rule

- Inputs: frozen raw probability, independently frozen donor-derived probability, context key, unique witness ID, explicit feature schema ID and 2–8 binary, **pre-action public** feature values. Labels exist only on FIT/VALID rows; prediction accepts no label. The module checks schema consistency, but caller-provided provenance and labels do **not** authenticate source visibility or timing.
- Reuse existing RS01 FIT-only bounded correction cells (up to 16, each absolute shift <=0.1); unknown context keys receive zero correction. Validation labels never fit correction cells.
- Build only per-coordinate VALUE support from VALID_OLD and VALID_NOVEL, not held keys, held labels, or exact validation keys. With marginally supported features a never-seen key/combination can receive gamma times clamp(donor-minus-raw, -0.1, +0.1); otherwise no donor adjustment.
- Candidate gamma set is exactly [1, 0.5, 0.25]. VALID_OLD average and each old-key and old-feature-group Brier drift must be <= +0.02. VALID_NOVEL Brier must improve versus raw by >=0.005, and the donor addition must improve over raw-plus-identical-correction by >=0.002. Pick lowest passing novel Brier and smaller gamma on tie.
- If all candidates fail, gamma becomes zero and the active correction bank is emptied. Invalid dimensions, duplicate IDs, non-finite predictions, mismatched schema, malformed capsule values and prediction-time labels fail closed.
- This selection rule is a DEV implementation contract, **not** source-qualified prospective science. A marginal value occurring in validation does not imply that a new combination or new causal family obeys the same law.

## Reproducible focused local evidence

On Node v22.16.0, local isolated execution of feature_transfer_gate.test.mjs and syntax checks of both new MJS files passed before commit. No protected original-source actions, teacher runtime, training, native checkpoint, CI job, runner dispatch, paid API or deployment occurred.

The positive fixture has validation feature pairs [0,0] and [1,1]. A new context key NEVER_VALIDATED_KEY with unseen combination [1,0] changes forecast **0.50 to 0.60** with donor 0.90, capped at +0.10. This proves only an executable path for nonzero out-of-key contribution, **not** that the forecast is correct or that causal-structure transfer occurs.

Negative tests show unsupported feature-value fallback, validation rejection atomic rollback, absolute donor cap, malformed input rejection and old minority drift detection. **Important negative:** 99 common old rows and one rare row cause candidate gamma=1 and gamma=0.5 to fail the per-group drift veto, yet gamma=0.25 passes; the rare old prediction changes **1.0 to 0.875**, with old-row Brier penalty **+0.015625**. A deliberately anti-correlated donor under an unfamiliar interaction changes correct raw 0.95 to 0.85. Thus this developer mechanism still can hurt retention and cannot be promoted on these fixtures.

## Future owner-authorized scientific qualification — NOT EXECUTED

Source owner #426 must independently pin a source-native observation/action/target ABI, donor *already-trained* weights and provenance, original pre-action feature whitelist and timing, genuinely unfamiliar causal-structure families, unconsumed disjoint cohorts, one-shot source action lease, action/compute budget and execution authority. Different keys, seeds, graph labels and synthetic replicas of the same law are insufficient.

Freeze fully trained equal-data/compute raw, donor, raw+bounded correction, raw+donor, symbolic, tabular/Bayesian/recurrent and native cumulative learner controls, plus donor permutation, no-donor and feature-interaction ablations, cold old-world retention and interference tests. Stop unless unfamiliar-family held Brier beats the strongest fully trained control by >=0.005 absolute without old-world or per-context drift above +0.02 and reproducibility under independent owner qualification. Retain negative results and never tune on held outcomes.

**Unverified:** exact-final-code full Linux/Windows regressions and G29 atlas, independent source semantics, authentic pretrained donor compatibility, new real-world transfer, native model integration, cold retention, acceptance or deployment.
