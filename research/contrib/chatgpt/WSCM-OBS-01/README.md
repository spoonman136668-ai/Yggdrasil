# OBS-01 — Observable evidence limit for retained Yggdrasil causal functions

**Disposition: RETROSPECTIVE ANALYTIC OBSERVABILITY LIMIT.** This is an examination of an *already consumed, already reported* source-free Yggdrasil development scenario. The code derives exact Bayesian identification probabilities from frozen public conditional probabilities. No new world outcomes, native model training or protected first-use occurred. The 95% diagnostic target is exploratory, chosen for interpretability **after prior outcome information existed**; this is not a newly preregistered confirmatory experiment.

## Source and scope
- Research parent: Yggdrasil Amalgam [PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278) at `86264b41a08d49f558418c0fba367f3a2636befa`.
- Original retrospective input: `research/contrib/chatgpt/CAUSAL-AMALGAM/staged-retention-dev-01/identifiability.json` blob `40fdcca22297d90022a72aeb407467ecd9707b2e`; original protocol `staged_retention_protocol.json` blob `1bbc1672ccd80f248c86c5ec7482f6ade8a0d76a`. `source-excerpt.json` reproduces **only** the eight public old/new conditional probabilities and original analytic-only flags. Runtime refuses changed probabilities.
- Code: `observability_bound.py`. Exact rational arithmetic and memoized finite-horizon optimal Bayesian choice of public actions; complete 0–8 probe curves. `test_observability_bound.py` checks source mutation, no-information actions, Bayes total variation, two-probe limits, noise monotonicity and reproducibility.
- Result: `result-summary.json` includes exact rational 1/2/8-probe accuracies for four conditions; full curves deterministically regenerate. Full local result SHA256 `512000902a761a1840372635c95c5e8c23e8eda95469c0febeb1f618d868413f`.

## Observed mathematical limits
Under a balanced prior, **fixed publicly observed context** and **conditionally independent Bernoulli outcomes**, the Bayesian observer knows both conditional laws but **never receives the hidden regime label**. It chooses each action adaptively from the public history. This is an intentionally optimistic information upper bound, not a trained or deployable competing model.

| Public context | Outcome flip probability | MAP at 1 or 2 probes | First 95% within 8 |
|---|---|---:|---:|
| 0 | 0 | 84.375% | 5 |
| 0 | 10% | 77.5% | 7 |
| 1 | 0 | 78.125% | 7 |
| 1 | 10% | 72.5% | not reached by 8 |

At public context 1, action 0 yields the same `P(outcome=1)=7/32` under both laws, so this action provides zero regime information, irrespective of repeats under these assumptions. An alternative action distinguishes them, but needs sufficient charged observations. Even an **oracle-knowing-the-laws** Bayesian observer cannot guarantee instant, zero-evidence revival for a hidden regime switch.

This is a conditional information result, **not** a bound on Yggdrasil's full physical world if hidden-state correlations, additional sensors, changing contexts or different observation budgets exist. It does not prove any memory architecture incapable of long-term retention, and it does not justify replacing the native learner with an oracle Bayesian controller.

## Reproduction and gate
From this branch's checkout:
```sh
python -m unittest discover -s research/contrib/chatgpt/WSCM-OBS-01 -p test_observability_bound.py -v
python research/contrib/chatgpt/WSCM-OBS-01/observability_bound.py \
  research/contrib/chatgpt/WSCM-OBS-01/source-excerpt.json --output /tmp/obs01-full.json
```
Exact component tests: **8/8 local PASS** on CPython 3.13.5/Linux. Source-world actions: **zero**. Existing parent trained-model/Windows regression **not executed** for this exact candidate. This is an **UNPREREGISTERED retrospective diagnostic**; not a new scientific training result.

**ENGINEERING:** exact isolated analytic tests PASS; full integration/final dual-OS regression UNVERIFIED. **SCIENTIFIC:** conditional observability limit supported by exact math; native retention and transfer advantage UNVERIFIED. **DEPLOYMENT:** UNVERIFIED; draft PR, no accepted refs, interventions or controller changes.

**Decision:** The next real Yggdrasil experiment must *add usable observation information* (or prospectively charge enough discriminating interventions), preserve separate trained causal mechanisms, and beat a fully fitted exact Bayesian diagnosis baseline at equal information/actions/compute and cold retention. Do not build another fixed/soft router that only repackages the same evidence.
