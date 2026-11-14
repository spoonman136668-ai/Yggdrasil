# DG1-IV18 — paid two-probe novelty veto and two-step decisions

**Original science: VALID MIXED_DEV, PRIMARY NO-GO. Engineering: first-use exact-SHA Linux and Windows PASS. No promotion or deployment.**

This study asks whether two independent physical interventions, taken at contrasting states, can keep Yggdrasil's experimental retained causal memory useful without falsely reusing a past module when an unseen nonlinear relationship appears. It is **external synthetic research, not native model improvement**. The new environment requires two-step planned actions, not T17's one-step action selection.

## Precommitment and autonomy boundaries

The frozen [prereg.json](prereg.json) was committed separately at `20b0af804ffbd04d7e3d22cdf39b3c82a14d7093` **before** source, tests, original physical actions, or outcome. Protected main `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` was unchanged. The previous T17 PR #1000 remains a valid negative/mixed predecessor, not retuned.

Original study: new registered seeds 520001..520016, 16 worlds, six arms, 160 identical charged training actions per arm/world, then two held-out audits with 12 episodes each. Every audit episode charges **two diagnostic probes and two sequential goal actions**, with evaluator-only 36-plan counterfactual optimum never exposed to learners. **15,360 training + 9,216 evaluation = 24,576 charged physical actions.** No audit outcomes train any arm.

The candidate and two same-parameter ablations share identical model updates. Six arms: certified_gate, ungated_route, sham_route, no_archive, forgetting_rls, integer_recurrent (fully trainable fixed-point recurrent weights). All receive the same paid diagnostics. Novel C inserts a bilinear parent dependency not present in previous experiments or the trained linear causal modules.

## Frozen original result — lower two-step regret is better

| Learner | Cold return-A | Nonlinear unfamiliar-C |
| --- | ---: | ---: |
| certified_gate | 0.006705636159 | 0.055212400233 |
| ungated_route | **0.004528303631** | **0.052616772242** |
| forgetting_rls | 0.026292793453 | 0.063579716099 |
| integer_recurrent | 0.397539837596 | 0.351998268316 |
| no_archive | 0.038178225358 | 0.082184829439 |
| sham_route | 0.021237563031 | 0.062922718314 |

**Scientific primary NO-GO.** Return-A strong conventional, sham/no-archive, and per-world gates passed, but the new veto was worse than the ungated same-capacity causal learner on both regimes. Novel C also missed the strongest conventional margin, sham comparison, per-world wins and the false archived-memory-veto criterion. Genuine known-row reuse is not sufficient evidence of useful unfamiliar transfer. CPU cap gates passed, but scientific criterion did not.

The threshold was frozen at mean-squared diagnostic residual 0.0049 **before the study**. Do not tune it based on these results, repeat first-use on new code, or reclassify a genuine unfavorable outcome as infrastructure failure.

## Exact-source original evidence

Original PR head `d05ace991a6417532fd8603f273048d67ad2021d` (tree `89ac8cba5a7aa0d26c7470175d12a31e9c52d489`). [Original run 43541356818](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43541356818) completed with Linux and Windows 9/9 focused preflight tests, 54/54 full inherited regression each, and independent cross-OS strict non-timing *entire JSON and checkpoint hash* equality. [Independent G29 source atlas run 43541356821](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43541356821) PASS on both OS.

Full unabridged world-level original results remain solely in GitHub Actions: Ubuntu artifact `14092391266`; Windows artifact `14092022726`. Their ZIP SHA-256 digests are recorded in [provenance.json](provenance.json). This PR only commits compact scientific classification and reproducible provenance, not large data copies.

### Pre-first-use toy-only verification

```text
python -m py_compile research/contrib/chatgpt/dg1-iv18-20261113/iv18.py research/contrib/chatgpt/dg1-iv18-20261113/test_iv18.py
python -m unittest discover -s research/contrib/chatgpt/dg1-iv18-20261113 -p 'test_*.py' -v
```

Future scientific direction: independent non-synthetic or genuinely different environment family with long-horizon credit assignment, cold retention, and interventions, rather than iterating a synthetic novelty gate against these observed results. No native loop or deployed model changed.
