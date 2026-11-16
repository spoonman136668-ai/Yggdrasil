# AAI-12X — lossless symmetry-pruned causal learner

**Result: `DEV_GO_SCIENCE_UNVERIFIED` — all frozen source-development criteria PASS; independent scientific first-use, native Yggdrasil acceptance, full platform regression, and deployment are NOT DONE.**

## Why this is not a rewrite of AAI-12W

AAI-12W PR/evidence [AAI-12W](https://github.com/spoonman136668-ai/Yggdrasil/tree/1ff913cd297f8f81a03322d66403f13bb03a3efd/research/contrib/chatgpt/AAI-12W) ended `DEV_NO_GO_NO_SCIENCE` because a causal input-role hypothesis enumerator took 14.63–15.56 times the fastest fully trained conventional control, exceeding its frozen 12× cap. That negative result and its thresholds remain unchanged. The present experiment is a **separately preregistered** algorithmic equivalence and efficiency test on newly derived mechanical source worlds. It does not promote the previous result.

For any fixed output role `k`, the unrestricted binary truth table over `(a,b,c)` has eight cells. Every permutation of `(a,b,c)` is only a permutation of those eight cell indices: there is an equivalent truth table with the *same* public predictions, empirical mismatch count, and number of visited cells. The original learner breaks ties by `(errors,-coverage,k,a,b,c,mask)`, so among six equivalent permutations the lexicographically sorted input triple wins. Accordingly the new implementation enumerates only `C(7,3)=35` triples per output role instead of `P(7,3)=210`: **280 hypotheses instead of 1,680**, without changing learner capacity. Residual bits are also cached using only actual public action events. This is a **lossless computational reduction**, not a new cognitive mechanism or new source information.

The original entire 7,273-byte `AAI-12W/learner.py` is copied **unchanged** into `reference_w.py` (Git blob `e8b0c9c2bb5349377993454179084840222f3e49`). All four conventional controls are trained by those exact original functions, not approximations or a different fitter.

## Pre-outcome freeze and exact sources

- Independent source parent: AAI-12P PR #1074, `abd374e7dc433981df991e103d8ebdff0b5eb093`.
- Preregistration first: commit **`2526b63668efaf2fc67f46d79d9227009b9059a9`**, before writing code or observing results.
- **All code and focused tests committed before the first measured result** at **`a43cb9b616c8ae04d3b79ec3811c9c358baeb6e2`**.
- Exact locally executed Git blobs were read back and matched: `world.py` `e6d2519106e175852434a0ce60dc87a44b24fed3`; `optimized.py` `4fe89d106f621f0599ff5fc6d81960aff54bae05`; `reference_w.py` `e8b0c9c2bb5349377993454179084840222f3e49`; `dev.py` `ee4fab853bc797abd9ff3699188fb28b356b12a0`; `test_dev.py` `c3b150f66abf6fcf26826ec480c5959308dfaa93`.
- **10/10** focused local protocol, isolation, action, equivalence, cold checkpoint and first-use denial tests PASS before screening. No source or test file changed after observing results.

## Prospective mechanical test

Completely new source namespace `AAI12X`, fixtures `gamma/delta/epsilon`, and **16 new three-essential-input hidden operator masks** chosen by a fixed SHA256 order with all AAI-12W masks excluded. Four familiar two-input worlds and four four-input negative worlds per fixture. Every world has unknown causal roles `(a,b,c,k)`, hidden one-bit temporal state, and actual one-input-do interventions. Learners see 48 public before/after action transitions, not hidden state/roles/rules. Every heldout trial receives the initial public state and three genuine bit-flip actions but **none of the intermediate outputs**, then predicts the final output. All evaluation predecessor states are disjoint from training predecessors.

**72 worlds** × **64 three-step episodes** = **4,608 heldout forecasts per arm**: 3,072 novel, 768 familiar, and 768 negative. **Seven arms**: optimized candidate, exact AAI-12W original, fully trained depth-7 ID3, 200-epoch quadratic logistic, kNN5, six-gate fixed-pair causal grammar, and a no-learning persistence negative. Every arm gets exactly the same public observations and cold-restores its trained model before predicting; 504 cold restores per run. Independent scientific first-use: **zero**.

## Exact scores

| Learner | Novel (3,072) | Familiar (768) | Negative (768) |
|---|---:|---:|---:|
| **Optimized causal** | **0.995443** | **1.000000** | **0.595052** |
| Original AAI-12W causal | **0.995443** | **1.000000** | **0.595052** |
| Strongest fitted conventional, six-gate pair | 0.751302 | **1.000000** | 0.578125 |
| Fitted ID3 depth 7 | 0.528646 | 0.578125 | 0.496094 |
| Full 200-epoch quadratic logistic | 0.513346 | 0.520833 | 0.516927 |
| kNN5 | 0.495443 | 0.506510 | 0.533854 |
| Persistence, no learning | 0.486003 | 0.502604 | 0.541667 |

**New causal learner vs strongest fully trained conventional**: **+0.244140625** novel absolute accuracy. All **16/16** novel worlds exceed 80% pooled across three fixtures. Familiar nonregression **PASS**. Four-input negative nonregression **PASS**. The optimized and reference candidate have **exactly identical learned programs in 72/72 worlds** and **exactly identical outputs in 4,608/4,608 heldout forecasts**.

### Frozen measured efficiency — three runs, no discarded measurements

| Run | Optimized model (s) | Original model (s) | Speedup | Ratio vs fastest fitted baseline |
|---|---:|---:|---:|---:|
| 1 | 0.171788 | 1.189930 | **6.927×** | **2.056×** |
| 2 | 0.166132 | 1.122059 | **6.754×** | **2.100×** |
| 3 | 0.176394 | 1.198040 | **6.792×** | **2.087×** |

All timing gate requirements PASSED in every run: at least 2× faster than exact reference and at most 12× the fastest **fully fitted nontrivial** conventional control (the depth-7 ID3, around 0.08 seconds for all 72 worlds). Timing includes model fitting, canonical JSON checkpoint/restore, and all forecasts. The common source fixture generator cost was **0.591707 s**, deliberately separated from the model efficiency comparison.

As a **secondary, nonqualifying diagnostic**, adding this same source-generation cost to each model gives a 2.261–2.334× reduction for source-generation-plus-one-model evaluation. Neither figure includes engineering tests, native build, CI, model training on real tasks, or autonomous-loop whole-process overhead. Do not describe them as production end-to-end gains.

**All eight prespecified development gates PASS in all three runs.** Exact action/score trace SHA256 `34ef09b44344e1d5a114a28ddb6bde7739edcbf369e09fa036b995429b32139c`; public source digest SHA256 `0b03397b16d0f321b39b2bce13fe1e6e30dba2bb0eeeb74c080e9c50784aeace`. Repeated scores, exact programs, trace and frozen gate decisions agree. See `result.json` and `provenance.json`.

## Reproduce / authority

From the directory, Python 3.13 standard library:

```sh
python -m unittest -q test_dev.py
python dev.py --source-dev
python dev.py --primary  # deliberately denied
```

This source-only development PASS demonstrates removal of redundant hypothesis searches and preservation of high *in-grammar* synthetic causal forecasts. It **does not** demonstrate unrestricted relationship invention, externally licensed/original-data transfer, persistent learning across worlds, general intelligence, or a qualified native Yggdrasil scientific improvement. The original W performance failure is preserved unchanged.

**Engineering:** local exact-source tests and repeatability PASS; official full Ubuntu/Windows native regression, exact-head generated code-atlas acceptance and native build not qualified.

**Scientific:** developmental hypothesis PASS, independent original scientific first-use **NOT RUN**; no model/science promotion.

**Deployment:** **NONE**. The new source remains isolated under `research/contrib/chatgpt/AAI-12X/`; main, accepted weights, owners, Forge/Wingless/Hybrid, runners and scheduler/controller authority unchanged. Any future qualification must use the owner's native isolated route, new independently witnessed data/source custody, full regressions and separate acceptance.
