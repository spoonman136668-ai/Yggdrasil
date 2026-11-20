# ENERGY-NULL-CERT-08 — Exact fixed-group false-alarm certificate

**2026-11-20 · independent mathematical research · no primary scientific seeds or original model touched**

## Why this matters

ENERGY-DELAY-07 identified delayed direction correctly in 24/24 non-null synthetic worlds but falsely declared effects in 4/12 no-effect worlds. Its heuristic looked across three possible delays and declared causality if the largest absolute intervention-arm Beta(0.5)-smoothed difference was at least 0.30. Selecting the largest of multiple noisy contrasts without a multiple-comparison guard can inflate false alarms.

This certificate is an **exact mathematical analysis** of a deliberately simplified null, not a replay of ENERGY-DELAY-07 and not a native learning result.

## Frozen source and proof

- [Preregistration](prereg.json) first committed `f75f29a3829d7c07257b493c77bb7ca0421e00a4`.
- [Exact-integer verifier](certificate.mjs) committed `c643843a85fe7791813ef9a017e8ae71909c39dc`, Git blob `ec713e3c7fb3a1406686e08a858f7dfc5fff17cf`. GitHub readback matched the executed source before computing the result.
- [Exact result](result.json) committed `4b0254f0528eaf657a53b17c8d99a313924b098e`. Every probability is recorded as an exact integer numerator and denominator as well as a display decimal.

Assume **exactly 12 intervention outcomes per action at each of three independent lag channels**, all outcomes i.i.d. Bernoulli(1/2), with no action effect. For one channel the smoothed contrast is `D=(X1-X0)/13`; the frozen alarm condition `|D|>=0.30` becomes `|X1-X0|>=4`. Each arm count is Binomial(12, 1/2). Therefore the 1-lag false-alarm chance is

```
2 * sum_{k=0}^8 C(24,k) / 2^24 = 2543252 / 16777216
                                   = 0.1515896320343.
```

For three independent channels, the probability of at least one false alarm is `1-(1-p)^3 = 0.38931408777972654` (**38.93%**). The verifier enumerated all 169 possible (X0,X1) count pairs, checked probability-mass conservation, and verified the threshold with exact integer comparisons.

As a **conventional statistical control**, two-sided Fisher exact testing at `alpha = 0.05/3 = 1/60` per lag gives an exact one-lag false-rejection rate `0.006831049919128418` and under *this independent-lag null* the three-lag probability `0.020353478787334685` (**2.04%**). For valid randomized-assignment nulls, Bonferroni gives a broader `<=0.05` family-wise bound without independence between the three lags.

## Important boundaries

The earlier ENERGY-DELAY-07 generator did **not** force exactly 12/12 randomized intervention arms and its three outcomes shared a nuisance variable U. Therefore **38.93% is not the measured or exact predicted false-alarm probability in that original world**. The prior observed 4/12 remains a historical scientific NO-GO and must not be retroactively upgraded or rescored. A follow-up mathematical analysis of the original **randomized arm-count distribution** can close part of that modeling mismatch without rerunning consumed primary seeds.

Fisher + Bonferroni is a standard statistics safeguard, not a novel AI or native Yggdrasil mechanism. A learner that merely wraps this conventional guard cannot claim causal discovery, long-term cumulative memory, autonomy or an intelligence gain.

### Truthful classification

- **ENGINEERING:** exact-rational analytic verification PASS under the assumptions, committed source/results; repository-wide dual-OS G29 atlas validation remains failing on research-only new files.
- **SCIENTIFIC:** NO NEW EVIDENCE OF INTELLIGENCE; the analytic control exposes a false-alarm mechanism, not empirical model superiority.
- **DEPLOYMENT:** NONE. Draft contributor PR #1346 only. No accepted main, original owner learner, scheduled task or native checkpoint modification.
