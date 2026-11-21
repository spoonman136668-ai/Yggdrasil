# CKAD25-RISKVAR — source-free risk-variance diagnostic

**Classification:** SOURCE-FREE EXACT ANALYTIC COUNTEREXAMPLE (not a preregistered experiment, not scientific improvement or accepted native training). This branch is an **isolated, read-only contributor** based on the existing CKAD25-AC frozen negative. It is not a competing Yggdrasil learner or a new canonical component.

## Verified inputs and nonduplication

- Qualified same-native intervention source [CKAD25-AB PR #1270](https://github.com/spoonman136668-ai/Yggdrasil/pull/1270), exact head `791c67f0afee62a3b9de695277c625783b099da5`.
- Already-tested unfamiliar action-role identity reassignment [CKAD25-AC PR #1274](https://github.com/spoonman136668-ai/Yggdrasil/pull/1274), exact head `0fdf138e02f2058366088025472ab339d3d36ec1`, original `DEVELOPMENT_NO_GO`. Its new action-role cohorts were already consumed; **do not repeat them**.
- **Source-level native policy:** `yggdrasil/native_cumulative_learner.py` Git blob `3f33f32c7919bba5297fbf79ff561ef9e85c7255`. `propose_source_change_witnesses` scores each candidate independently as `(1+faults[address])/(2+counts[address])`, then picks the two highest risks with address tie-break. We verified these lines directly at the pinned CKAD25-AC head; this contribution does **not** call that native method on an authentic checkpoint or modify it.
- No new native action, original-world first-use, source-held output or runner. Read-only source algebra only. CKAD25-AC's 24-bijection unobserved mapping result remains negative.

## Distinct gap: cross-world latent risk variance vanishes under independent Beta means

Frozen CKAD25-AB/AC *synthetic* hazard family has exactly four public action identities, an unknown hot address uniformly distributed among them, and independently drawn future changed worlds. Conditional on a fixed hidden hot address, each new world has a fault at the hot site with probability `3/4` or at each of the other three with probability `1/12`. Those probabilities sum to one; only one fault per future changed world. **The exact Bayes arm is supplied this model family**; the native empirical Beta estimator is not. This is a conventional extra-prior control, **not** a fair scientific proof that a new learned native algorithm is superior.

Source-free **hypothetical** public consequences on address `2` in two different earlier worlds:

```
address=2 -> no contradiction (0)
address=2 -> contradiction    (1)
```

Native empirical Beta risk for every address is now **1/2**: `(1+1)/(2+2)=1/2` at address 2, and `(1+0)/(2+0)=1/2` at all unobserved addresses. Deterministic tie-break selects **[0,1]**, discarding that contradictory variability as evidence of a shared latent hot-site cause.

Exact latent-variable Bayes conditional on the same hypothetical observed pair has posterior that hot site is address 2 with probability **9/20**, and any other specific site with probability **11/60**. The full two-witness history itself has probability **5/48** in the synthetic prior. Exact posterior *predictive risk* on address 2 is **23/60**, versus **37/180** at each other address, so the optimal two probes are **[2,0]**. Matched two-probe *conditional expected detection* under this assumed law is **53/90** (Bayes) versus **37/90** (native Beta): **delta 8/45 = 17.78 percentage points**. This is **a conditional mathematical expectation, not a measured detection gain**. The result follows from covariance between outcomes across worlds caused by the shared latent hot address, rather than a marginal mean.

**Complete finite exhaustive gate:** all `(4 addresses × 2 revealed outcomes)^2 = 64` ordered two-observation histories were enumerated with Python's exact `Fraction`; **4** have strictly better Bayes choice under its known synthetic prior, and **60** tie in *expected detection* (including some cases where the actual selected sets differ). A positive control with one positive witness and the empty-history negative control produce the same native/Bayes selected action set. The source-free math reports no new world stepping, no tested transfer or learned improvement.

## Reproduction and provenance

```bash
cd research/contrib/chatgpt/CKAD25-RISKVAR
PYTHONDONTWRITEBYTECODE=1 python -m unittest -v test_audit.py
PYTHONDONTWRITEBYTECODE=1 python audit.py > /tmp/riskvar-check.json
```

`result.json` is the exact deterministic original read-only result, containing all 4 strict-positive witness cases and exact fractions. Local Python 3.13.5 / Linux x86_64: **6/6 focused analytic tests PASS**. File Git blobs verify exact byte-for-byte tested source:

| File | Git blob |
|---|---|
| audit.py | `b2346b9ed6f850cc0e7e5c893e6052b0a862d394` |
| test_audit.py | `375f25b6ce03e2fd137d6230d2063049b61dc57b` |
| result.json | `c58e19ab015f0ccb0b4ce6b99b78e24535aa1e6b` |

**Engineering:** 6 source-free local tests PASS; full exact candidate Linux/Windows regression, authentic native method/checkpoint execution and resource ratio **NOT RUN/UNVERIFIED**. **Scientific:** no new original source evidence, no new scientific pass, no cold learned transfer. **Deployment:** none.

## Next legitimate falsifiable intervention

A future *native* candidate would need to retain source-witnessed cross-world latent-risk hypotheses and acquire their parameters from authorized observations, not have the evaluator supply hot-site labels/probabilities. Freeze a **disjoint** action/identity generalization task and test against **fully trained, equal-information and equal-action** Bayes latent-risk, conventional HMM/change-point and independent Beta controls, including no-mapping/no-evidence negatives, matched first-use source custody, predictive Brier, measured action value/cost, old-task cold retention and CPU <=2×. [Issue #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426) forbids protected new first-use without owner admission. This research-only proof does not authorize a runner, workflow, merge or owner action.

The central Amalgam [PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278) remains the sole research integration coordinator. Retention PR #1329 and accepted main are unchanged.
