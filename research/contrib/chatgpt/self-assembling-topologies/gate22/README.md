# Gate 22 — Detect unannounced causal changes and reactivate retained knowledge

**Result: SCIENTIFIC NO-GO (mixed synthetic developmental evidence).** This contributor experiment is not a native Yggdrasil learner training result and cannot authorize Amalgam integration.

## Chronology and provenance

- Parent: Gate21 final Linux/Windows PASS commit `eb44df75612be0aaa6ee388a08f308eb8fc8dc39`.
- [Frozen experiment preregistration](prereg.json) committed first at `a4ad408eb9e4032407962ac06e4b14bd3a8e290a`.
- [Original frozen source](run.cjs) at `9f473e24cbe5c249ee0f608c23ca5f0fa0ca1351` aborted on an undeclared variable (`ReferenceError: best is not defined`) before producing any aggregate metric. This is preserved as a source execution failure, not a scientific negative.
- Source-only mechanical patch `7eec42d96c4011e57ad38b5fa7a34bb0140448a4` added the missing `let best` declaration. The hypotheses, thresholds, original evaluated seeds, model and data rules were not changed.
- First completed [sealed result](result.json) `ed488d5e9eccc79060c4175a6c198c2c48d690f7`, checked against frozen code blob `a23311393ddec84c579317deae4059d2efdc0448`.
- [Audit](audit.cjs) verifies receipt math, all failed thresholds, source call separation and custody; it is **not** a second independently implemented learner.

## Method

192 seeds: 32 each XOR-pair, MUX3, random essential 3-input Boolean, unary, stationary essential3 and independent random labels. Input is six binary controls, no tokenization or transformer. Each trial begins with source A: 64 labeled intervention consequences. Next, without exposing phase labels to learners, 48 new B training events follow (causal parents remapped), then 48 A-return training events. The stationary and independent-noise negative controls have no real change. Both B and A-return have **16 strictly held action outcomes** scored only at the end of that phase. Future outcomes never enter fitting or switch decisions.

The active self-assembling graph keeps A64 state immutable, evaluates local add/delete/swap neighbors every 8 experienced events using the prior 24 training outcomes, and checks proposed switches against the last 8 training-only witness outcomes. It needs >=0.025 witness Brier improvement, agreement on both 4-outcome halves, and >=0.005 null advantage for B entry. It may reactivate the original A graph if the source significantly outpredicts the current B graph. The model sees only past interventions and outcomes, not actual switch timestamps.

Controls: source-frozen A, all-history static exhaustive subset, rolling-32 static exhaustive subset, Bayesian hazard mixture of source and rolling posterior, ungated local graph, p=.5, and source/phase-aware oracle **only as an informationally advantaged illustration**. All receive the same A64 and streaming evidence; computations and transient scratch are not equalized. The algorithm packs 64 source pairs, up to 96 stream pairs and current state inside **384 bytes**.

## Main results: held-out Brier, lower better

| World | B gated | B rolling-32 | B hazard Bayes | A return gated | A return rolling-32 | A return hazard Bayes |
|---|---:|---:|---:|---:|---:|---:|
| XOR pair | 0.218717 | 0.073941 | 0.079092 | 0.058678 | 0.066503 | 0.058929 |
| MUX3 | 0.138158 | 0.083361 | 0.110731 | 0.062422 | 0.085293 | 0.065131 |
| Essential3 | 0.165557 | 0.093712 | 0.123462 | 0.078947 | 0.101464 | 0.078687 |
| Unary | 0.053729 | 0.056096 | 0.057089 | 0.065650 | 0.067079 | 0.064937 |
| Stationary | 0.057503 | 0.097035 | 0.058495 | 0.059961 | 0.090628 | 0.062749 |
| Independent noise | 0.281411 | 0.324354 | 0.268268 | 0.282642 | 0.302303 | 0.257939 |

**Positive bounded evidence:** For related A→B→A trials, source reactivation occurred by the return endpoint in **110/128**. The pooled A-return held Brier improvement versus rolling-32 is **+0.0136603812**, paired normal 95% CI **[+0.0096468373,+0.0176739251]**. All 192 synthetic same-process serialization/resume checks, immutable A forecasts and held-action disjointness checks passed.

**Decisive negatives:** In B, gated minus rolling-32 held Brier is **+0.0672626941** (CI [+0.0466192579,+0.0879061303]) and gated minus Bayesian hazard is **+0.0514467352** (CI [+0.0305376231,+0.0723558473]), both violating prereg non-regression limits. Returning A, the gated improvement over the already competitive Bayesian hazard is only **+0.0004965685**, CI **[-0.0008213484,+0.0018144854]**, below the prereg required +0.005 and not statistically resolved. The noise-only control made **26/32 false mode switches** (versus <=20% allowed) and held noise Brier exceeded the .5 null by more than allowed. Stationary false switches were **3/32**. Six of 16 joint thresholds failed. This is not evidence of unique local structural advantage.

**Interpretation:** A stored source model can support old-world reactivation, but this detector trades too much B adaptation for cautious switching, and its eight-witness search can still overfit random noise. Bayesian hazard offers essentially the same return performance without hard graph switches. More synthetic validation alone cannot establish native cumulative intelligence.

## Reproduce exactly from the final Git SHA

```sh
node research/contrib/chatgpt/self-assembling-topologies/gate22/run.cjs --verify research/contrib/chatgpt/self-assembling-topologies/gate22/result.json
node research/contrib/chatgpt/self-assembling-topologies/gate22/audit.cjs
```

**ENGINEERING:** Source/primary-result chronology is preserved. Existing full repo tests + Gate10–22 exact replay/audits on Windows and Linux required to close engineering. Do not call PASS until exact-head CI.

**SCIENCE:** NO-GO on frozen joint conditions; no accepted model-native or independent transfer gain. The true B and return phase markers are evaluator-only. Trial seed cohorts consumed; do not tune and relabel this test.

**DEPLOYMENT:** NONE. Keep PR #1340 draft, accepted main unchanged; no model/checkpoint promotion, controller/runner/scheduler, scientific first-use, or trading.
