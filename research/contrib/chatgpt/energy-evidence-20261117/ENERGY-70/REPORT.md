# ENERGY-70 — exact representational-capacity bound and independent ENERGY-69 failure localization

**Date:** 2026-11-19 · **Scope:** read-only retrospective analytic diagnostic, independent of the original synthetic scorer; not a new scored trial, native Yggdrasil training, acceptance, or deployment.

## Provenance

Source: ENERGY-69 original binary `ENERGY-69-original-evidence.tar.xz`, 14,684 bytes, SHA-256 `2de9e13da3924b6ebc244a54f9907525685c897487e0718f9fbb060717058238`. The complete source and case-level archive are preserved as three base64 parts in the sibling `ENERGY-69` directory, with `archive_manifest.json`. This diagnostic verifies every part's SHA-256, concatenated archive size and SHA-256 before reading the frozen 72-case CSV and original result. No seeds, new data, model fit, model source, accepted reference or existing reports were changed.

Code: `analysis.py`, SHA-256 `3975d5d8487420f704ec7521d34afed8934e8f33e2733fcf76b0c323ab2493a5`. Output: `result.json`, SHA-256 `e6310e03ed70bbae32db1ff2fe25e4850e0bf983d2d37f595015552884689477`. Python 3.13.5 standard library only, exact rational proof.

## Exact mathematical capacity limit

Enumerate all 512 assignments of nine independent binary interventions. The fifth-order Walsh feature `χ_{0,1,2,3,4}` is exactly orthogonal, under the uniform distribution, to every Walsh character of degree 0 through 4 (**256/256 exact-zero inner products**). Consequently, for the restricted **linear span** of these features, an independent fifth-order signal of coefficient 0.45 has irreducible mean squared error `0.45² = 81/400 = 0.2025` before observation noise. With independent observation noise σ=0.30, the theoretical expected squared error floor is **117/400 = 0.2925**. When the correct fifth-order feature is included with an oracle coefficient, that floor falls to the noise variance **9/100 = 0.09**.

This is a statement about **linear combinations of bounded-order Walsh features under uniform interventions**. It is **not** a lower bound for general nonlinear networks, nonlinear energy minimizers, learned compositions, or distributions with dependent interventions. It does not establish that actual ENERGY-69 fitting attained either floor or that missing fifth-order features *caused* the observed 16.06% excess versus CV.

## Independent original case-receipt diagnostic

| Source family | Cases | Candidate−CV cold MSE | Candidate worse / better / tie | Candidate picked 4 |
|---|---:|---:|---:|---:|
| null | 18 | −0.0032404751 | 0 / 2 / 16 | 0 |
| two | 18 | +0.0086150262 | 15 / 3 / 0 | 18 |
| four | 18 | −0.0030093835 | 0 / 3 / 15 | 18 |
| four_plus_fifth | 18 | +0.1016989392 | 2 / 2 / 14 | 17 |

The original aggregate candidate−CV difference is **+0.0260160267 MSE**. The out-of-grammar family contributes **97.7272% of that net pooled excess**, using an exact 18/72 family weighting. This ratio is a net algebraic decomposition with offsetting gains/losses among other families, not the share of every individual error caused by that mechanism. The two-factor family independently shows 15/18 cases where fixed-four selection loses.

## Conclusion and candidate next stage

**ENERGY-69 remains DEVELOPMENT_NO_GO (2/5 frozen gates)**. The restricted fourth-order linear learner has a clear representational ceiling for an independent fifth-order Walsh effect, and the proposed block-selection rule sometimes overselects capacity on two-factor cases. More threshold sweeps on consumed seeds cannot qualify science. A new *prospectively frozen* mechanism should learn/combine previously unavailable interaction structure from action-consequence observations and compare against fully trained conventional fifth-order/ANF/structured Bayesian controls, plus no-mechanism negatives, unknown-family transfer, cold retention and matched fit+inference cost. Do not claim an energy-specific advantage from the exact lower-bound proof alone.

## Reproduction

```bash
python -B research/contrib/chatgpt/energy-evidence-20261117/ENERGY-70/analysis.py
```

All analytical assertions passed offline. No external execution/owner was involved. G29 Atlas Acceptance remains independently failing on the existing archive PR due to the unchanged indexed-file-source mismatch; full Linux/Windows CI and model scientific acceptance are **NOT PASSED**. Branch stays draft, no merge/promotion/deployment.
