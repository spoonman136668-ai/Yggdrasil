# ENERGY-68 — executable, exact-arithmetic structural counterexample

Date: 2026-11-19. Classification: **retrospective analytic feasibility, NOT a prospective trained-model trial**. Complements [ENERGY-68 PR comment](https://github.com/spoonman136668-ai/Yggdrasil/pull/1210#issuecomment-7016995930), which was a non-executable analytic account. This commit provides reproducible execution evidence and full source custody.

## Exact inputs and validation
- `proof.py` enumerates every one of the **512** equiprobable assignments of eight independent ±1 causal inputs and independent ±1 observation noise using Python standard-library `fractions.Fraction`. No RNG, seeds, model fit, external data, training, packages, native model or protected first-use.
- Four mutually orthogonal pairwise interaction terms `p_i=x_(2i-1)*x_(2i)`, target `y=e+sum(p_i)/10`.
- For 0,1,2,3,4 admitted terms, exact squared-loss population means: **26/25, 103/100, 51/50, 101/100, 1**. The proof checks the exact 5×5 orthogonality matrix; the coefficient-restricted prediction is the population optimum because these terms are orthogonal to all omitted terms and noise.
- First incremental gain: **1/104** (0.961538%); joint four-term gain: **1/26** (3.846154%). A rule requiring ≥3% incremental gain could stop at zero; conventional full-path selection can also attain exactly 1.
- No-signal control `y=e`: optimal error remains exactly 1 for every added capacity; forcing four spurious 0.1 coefficients worsens MSE to 26/25.

## Reproduce

```bash
python3 research/contrib/chatgpt/energy-evidence-20261117/ENERGY-68/proof.py > result.json
```

The exact `result.json` is committed beside the source. `proof.py` SHA-256 **b154db8c6a5936329645b1607d5f2a856887ec5470a489ce857807df631bdf8b** (2636 bytes); original output `result.json` SHA-256 **875e7cb79632dee00a1c9cd5d90f9e961cecaa504f1ba1152617814d8fefeb68** (933 bytes). Local execution and all arithmetic assertions PASS. Remote GitHub blob readback is an independent custody gate, not a second statistical trial.

## Limit and next experiment

This is a **constructed counterexample to per-step percentage gating**, not proof that joint-block learning, energy inference, native Yggdrasil, reasoning, transfer, retention, or computational efficiency beats a strong conventional model. ENERGY-67 `SCREEN_NO_GO` and all primary-seed reservations remain unchanged. The next eligible study must prospectively freeze a new block-structured causal candidate, disjoint source, trained full-path/ElasticNet/group regression/optimized nonlinear baselines, no-signal and label-shuffle controls, real intervention receipts, unfamiliar held structures, cold readout and matched fit+inference cost. Reject on missing seedwise improvement over strongest nonoracle, negative-control failure or retention regression. No merge/promotion/deployment.

## Independent G29 blocker

The draft archive branch adds hundreds of indexed evidence files. The original G29 checked-in source atlas is stale and CI fails on both Linux and Windows with `indexed file set changed`. This analytics-only commit cannot be considered G29 repair or full regression. Regeneration of the existing three atlas artifacts on an exact clean checkout and subsequent full Linux/Windows qualification remain separate gates.