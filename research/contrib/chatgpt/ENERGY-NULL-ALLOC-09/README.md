# ENERGY-NULL-ALLOC-09 — Exact null false-alarm risk with randomized arm sizes

**2026-11-20 · Independent analytical research · No original experimental seeds consumed · ENGINEERING PASS / SCIENCE NOT ESTABLISHED / DEPLOYMENT NONE**

## Scope and why it matters

The prior [ENERGY-DELAY-07](../ENERGY-DELAY-07/README.md) source-free causal-lag experiment produced 4 false causal declarations in 12 NULL worlds. [ENERGY-NULL-CERT-08](../ENERGY-NULL-CERT-08/README.md) showed that using a fixed Beta(.5) action-effect contrast threshold across three lag channels has high false-positive risk in a *simplified balanced* 12/12 sample.

This follow-up closes the important sample-allocation mismatch **analytically**, without replaying the 12 consumed primary seeds: the original protocol draws 24 randomized action assignments per NEW context, independently Bernoulli(.5). It does **not** force 12 of each action. Moreover, the three outcome lags share a hidden U, so their false alarms are correlated. A fabricated independent-three-lag point estimate would be invalid.

## Matching the original NEW-NULL intervention generator

For each of 24 randomized intervention episodes, A is an independent binary coin. U is an independent binary coin. At each lag, Y conditional on U is Bernoulli(.8) when U=1 and Bernoulli(.2) when U=0. The proxy Z is noisy and observed, but the previous candidate's *intervention contrast* deliberately **does not use Z**. Therefore, for **each lag considered separately**, Y is marginally Bernoulli(.5), independent of A, and iid across episodes. Within an episode, the different lag outcomes share U and are correlated.

For `N0 = n` observed action-0 episodes (`N1 = 24-n`) and `X0,X1` observed successes:

```
P(N0=n, X0=x0, X1=x1)
  = C(24,n) C(n,x0) C(24-n,x1) / 2^48.

D = (x1 + 1/2)/(N1+1) - (x0+1/2)/(N0+1).

The original action-effect heuristic declares a causal effect
if any of the three lags has |D| >= 0.30.
```

The [exact BigInt verifier](certificate.mjs) enumerates all **2,925** possible triples `(N0,X0,X1)` with integers, checks the total probability mass `2^48`, verifies label-swap symmetry and verifies that the N0=N1=12 slice agrees exactly with the previous balanced-null certificate. [Preregistration](prereg.json) commit `f40e3668e8771556d1d0a28ba3f1840a81b2fd15` preceded the [source commit](certificate.mjs) `b9158456d26e6e3a044ed71e00c3d0eb25b2daf9` (Git blob `72efdb6c54b24d3e6a7db2086eff1d2be2a3c020`), which was read back from GitHub **before** arithmetic execution.

## Exact certificate

| Outcome under this randomized NEW-NULL source model | Result |
| --- | ---: |
| Original `max(|D|)>=0.30`, **one** lag | **0.12920102208099138 = 12.9201%** |
| Original rule, **any of three correlated lags** | **12.9201% ≤ P(false alarm) ≤ 38.7603%** |
| Two-sided conventional Fisher + Bonferroni `alpha=0.05/3`, **one** lag | **0.00845106195554024 = 0.8451%** |
| Same calibrated control, **any three correlated lags** | **P(false alarm) ≤ 2.5353%** |

The exact numerators/denominators and conditional probability by each of 25 possible arm allocations are in [result.json](result.json), committed at `5e21295bf56a1968fd6bc2444ddc54bbf08e266c`.

The three-lag lower bound is its one-lag false-event probability; the upper bound is the union bound `min(1,3p)`. **Do not replace the bounds with `1-(1-p)^3`**: the lag outcomes share U, unlike the earlier simplified certificate. This sharper match gives a one-lag *exact* probability for the previous NULL generator, **not** an exact three-lag FWER value or a statistical reproduction of the 4 observed NULL false alarms.

The calibrated Fisher rule is a **standard** exact test, not a novel energy-based discovery or improvement. Conditional on a valid randomized sharp null, Fisher p values are superuniform; Bonferroni gives a general 5% FWER bound with arbitrary lag dependence. In this specific NULL source model the exact one-lag unconditional Fisher false-positive rate is smaller, so the union bound tightens to 2.5353%.

## Scientific and operational decision

The original 0.30 threshold remains **unacceptably susceptible to sampling noise** under the exact variable-arm marginal of the prior randomized NULL setup; adding three inspected delays compounds the risk. That makes the previous **4/12 false effect NO-GO** unsurprising, though it does not compute the probability of exactly four alarms across finite correlated worlds.

**Retire threshold-only causal-effect declaration.** Do not rerun ENERGY-DELAY-07 primary seeds to retune 0.30. Any future claimed causal advantage must improve **intervention utility under unknown out-of-family mechanisms** against fully fitted conventional causal controls, with preregistered null guards, independent functional retention and reproducible resource use. Passing Fisher/Bonferroni alone would be a conventional safeguard, not intelligence.

- **ENGINEERING:** Mathematical source identity, exact mass enumeration, count-symmetry and null-rate arithmetic PASS; separate dual-platform G29 Atlas acceptance remains failing for draft PR research additions.
- **SCIENTIFIC:** No new empirical gain or native model learning; original ENERGY-DELAY-07 MIXED_NO_GO stands.
- **DEPLOYMENT:** None. No accepted main, Amalgam PR #1278, private runner, scheduler, owner checkpoint, or production ref changed.
