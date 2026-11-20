# Gate 10 — Blind-operator Boolean parent discovery

**Disposition: SCIENTIFIC_NEGATIVE_DEV. Research-only evidence. No promotion.**

This independently contributed study removes Gate 07's supplied `AND–XOR` operator names: the local learner sees a six-bit intervention, public context label A/B, and a noisy binary consequence, but **not** which two parent bits or which four-entry Boolean truth table produced it. The environment draws two genuine relevant parents and one of the 10 non-constant/non-unary 2-input truth tables. No hidden mediator is supplied.

**Important limit:** All outputs remain within two-input Boolean truth tables. Although the learner writes conditional tables from observations rather than receiving a named operator dictionary, it is **not** open-ended invention of arbitrary operators or general causal intelligence. Context labels and a two-parent search prior remain provided.

## Reproducible evidence

- [Committed preregistration](./prereg.json) — committed FIRST at `260483732ce6e063abd24f833d94b91718ff4984`
- [Executable source](./run.cjs) — first committed at `8c6595fea5610171ae1a412fa574b2473d5b4a82`, with a final-result envelope variable typo corrected at `9da42f61121b106e8b8b51511df13f18f14ca1a7` before any result was stored
- [Sealed results](./result.json) — result commit `b90d0847e2517d94171b435ec1268f10f898ebab`
- [Execution provenance](./provenance.json)
- Primary observed metrics came from executing exactly the GitHub-fetched source in a JavaScript V8 isolate; separate platform qualification must not be assumed until CI completes.

Reproduce without dependencies (Node.js 20 or later):

```sh
node research/contrib/chatgpt/self-assembling-topologies/gate10/run.cjs --verify research/contrib/chatgpt/self-assembling-topologies/gate10/result.json
```

It recomputes the frozen 64 development seeds (7000–7063) and both 32-seed negative controls (8000–8031), with identical observed interventions and rewards for every model.

## Outcomes

| Model | Returning-context held Brier ↓ |
|---|---:|
| Dynamic local pair selection, 260-byte packed state | 0.0593687227 |
| First-32-sample frozen pair, same 260-byte allocation | **0.0580313305** |
| Fit-end fixed selector, same 260-byte allocation | **0.0593687227** |
| Bayesian 15-pair × 16-truth-table control, 3,840 nominal float64 bytes | **0.0477636719** |
| Constant 0.5 | 0.25 |

The frozen success threshold required **≥0.02 Brier improvement over the same-state fitted fixed selector with a positive paired confidence interval**. The observed advantage is **0.0000000000** (95% interval `[0,0]`); there is **no unique performance advantage from structural revision** on final held predictions. The stronger, higher-memory Bayesian control also wins. Even the first-32 frozen comparator improves slightly over the dynamic on average.

Additional checks:
- Correct two-parent sets: **121/128 (94.53%)** across the 64 development seeds.
- Exact **cold prediction** restore: **64/64 seed runs PASS** after packing each pair selector and its last 64 observations in 260 bytes. This checks return predictions only; **not** continuation training equivalence after restore.
- Rewires/installations: 155 over all development seeds; comparison operations: local **430,080**, fit-end fixed **122,880** (local **3.5× more**), first-32 frozen **61,440**, Bayes **4,915,200**. These are algorithmic comparison counts, **not** elapsed compute/energy.
- Unrepresentable 3-way parity: abstained **29/64** world contexts; dynamic held Brier **0.2663439438**, chance reference 0.25.
- Random labels: abstained **33/64** world contexts; dynamic held Brier **0.2588848697**, chance reference 0.25.
- Frozen negative requirement was >=58/64 abstentions in EACH family. **FAILED.** The local pair model frequently invents unsupported confidence under misspecification/noise.

The Bayesian control's particularly poor out-of-family negative scores are a **known-model-misspecification diagnostic**: its hypothesis class assumes a two-parent truth table and lacks a noise/null alternative. Do not call its negative-family failures a general weakness of Bayesian inference.

## Engineering, science, integration

- **ENGINEERING development:** deterministic seeded synthetic run PASS; source/result/protocol commit ordering preserved; local cold prediction replay PASS. Full repository and platform CI need a separate exact-candidate receipt.
- **SCIENTIFIC:** **NO-GO** under preregistered matched control and negative thresholds. This also falsifies the simplistic assumption that choosing a better pair constitutes autonomous novel-operator learning.
- **INTEGRATION / DEPLOYMENT:** none. No native Yggdrasil first-use, accepted checkpoint, canonical learner, owner, or scheduler touched.

The next **separate** scientific question should first repair out-of-family confidence using preregistered null/misspecification controls and then evaluate intervention choice under an equal information/action/compute budget. Do not retune Gate 10 thresholds or reconsume its development seeds as independent confirmation.
