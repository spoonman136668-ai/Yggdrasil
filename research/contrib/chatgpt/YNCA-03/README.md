# YNCA-03 — Interventions against shared causal-expert failure

**Frozen heldout result: DEVELOPMENT_NO_GO. No model integration or scientific promotion.**

## Why run this

YNCA-01 (PR #1215) learned context-dependent expert weights but lost to global/shuffled controls. YNCA-02 (PR #1217) tried predicting when all three experts were wrong, but simple confidence calibration beat native contextual memory.

YNCA-03 tests a different approach: **gather interventional evidence rather than passively reweight expert confidence.** The mechanism chooses one binary action to probe after seeing the same passive causal evidence as all comparator policies. Four noisy consequences are observed. All methods then use an identical six-law exact Bayesian readout. The *only* intervention difference is action selection.

This isolated, tokenless action-value memory is an external synthetic contributor candidate, not the actual Yggdrasil owner model. The six laws are predefined (AND, OR, XOR, X1, X2, NOR); this is not evidence of discovering new causal structure.

## Locked design and custody

- Parent: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`
- Prereg before first-use: `901680bb4c818215e5c74375c07f711f164eca9b`
- Frozen executable source before first-use: `7a3ce4177de22e53482fe93205b92d2b81325087`; Linux SHA-256 `b80e0e7108a37f832671b7839e045029c7e1df7d3ec456cbff43762712ac895a`
- First hosted source-frozen run: [44270041015](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44270041015)
- Training: 1,024 independent worlds; shifted heldout: 512 worlds; never reused YNCA-01/02 seeds.
- Each world: 16 biased passive observations, 4 intervention outcomes per policy. Only the action differs. All policies use the same Bayes readout, candidate-law set and equal intervention budget.
- Policies: learned native action selection, shuffled-reward action selector, random, two fixed probes, exact Bayesian entropy-information probe, exact Bayesian expected-Brier-optimal probe, and zero-intervention baseline.
- First-use CI: 8/8 focused tests PASS on Linux and Windows. Same causal metrics across both OS. Windows source bytes had CRLF checkout conversion; original JSON hashes differ only by embedded source SHA.

## Heldout results (lower is better)

| Method | Four-action causal Brier ↓ |
| --- | ---: |
| Exact Bayes information-gain probe | **0.026506007** |
| Exact Bayes expected-Brier probe | 0.026896440 |
| Fixed intervention (1,0) | 0.032449478 |
| Native learned selector | 0.033085160 |
| Fixed intervention (0,1) | 0.033740377 |
| Random | 0.050075962 |
| Shuffled-reward learned selector | 0.057641351 |
| No probe | 0.062541548 |

Native gained **0.016990802 absolute Brier** against random (relative 33.9% reduction), paired-bootstrap 95% interval [0.013849212, 0.020354286]. But native's ratio to the strongest random/fixed control is **1.019589909**, i.e. slightly worse than the simple fixed (1,0) intervention. The preregistered requirement was <=0.95, so it **FAILS**. No retrospective retuning is permitted.

There were 108/512 worlds (21.1%) with a shared erroneous vote from all three passive heuristic experts on at least one action setting. Native Brier in this subgroup was 0.001826833 vs random 0.003764421, but Bayesian EIG reached 0.000163011; this is exploratory subgroup evidence, not a second successful endpoint.

## Plain-English interpretation

Intervening on a causal system can improve predictions dramatically over passive observation and random probing. This experiment shows the learned policy did better than random, but **it still did not learn to select experiments better than a fixed probe, and exact Bayesian planning remained stronger**. That identifies the next bottleneck: learning a robust action-selection policy under causal and observational shifts, not merely performing more probes.

## Reproduction

From repository root on Python 3.12+:

```bash
python -B -m unittest discover -s research/contrib/chatgpt/YNCA-03 -p 'test_*.py' -v
python -B research/contrib/chatgpt/YNCA-03/experiment.py --heldout > replay.json
```

The original raw Linux JSON SHA-256 from the workflow is `66df30404cd696a8abd27873a5f86a060b5762389f4656e45e6285d3c1d72334`. Source/raw result identities, job IDs and original artifact IDs are in `provenance.json`. This README and result records do not change any experimental source, parameters or consumed data.

## Qualification boundaries

**ENGINEERING:** Focused dual-platform PASS. Generated G29 atlas and full native regression are separately required before full engineering qualification.

**SCIENCE:** Synthetic development negative against strongest fixed control; no SCIENTIFIC_PASS, no evidence of new law invention, retention or real-world transfer. The exact Bayesian controls know all six law types from the start.

**DEPLOYMENT:** None. The accepted Yggdrasil model, checkpoints, owner runner, research loop and `main` remain untouched.

A new YNCA-04 proposal, if justified, should investigate the *cost of information*: which intervention to buy under a fixed budget, with true active-fault diagnosis rather than a coarse context action table. Keep its cohorts and first-use sources separate.
