# ENERGY-REPLICATION-20 — bounded historical-posterior mixture, independent implementation and dual-noise falsification

**2026-11-20 | Yggdrasil Energy Research independent contributor | frozen development experiment performed | SCIENTIFIC NO-GO | DEPLOYMENT NONE**

## Exact scientific question

Does Gate 19's surprisingly successful bounded historical hypothesis mixture **reproduce** on fresh worlds implemented using an independently written source-free simulator, and does it keep its high causal-change detection when binary observation noise rises from 15% to 20%?

This tests a targeted hypothesis about **persistent uncertainty over learned causal explanations**; it is not a Yggdrasil native model update, genuinely independent scientific operator, source-sequestered external-world transfer, physical energy experiment, or a real learned memory system.

**Gate 19 predecessor (consumed; not rerun):** local top-8 posterior mixture recovered 150/160 changed XOR laws (93.75%) versus fully marginalized full Bayes 151/160 (94.38%) but violated a frozen false-alarm tolerance relative to low-recall MAP1.

## Source, fixed protocol and custody

- Existing isolated draft contributor [PR #1346](https://github.com/spoonman136668-ai/Yggdrasil/pull/1346), accepted-main base `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`. Sole native cumulative learner integration owner remains [Amalgam PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278).
- [prereg.json](prereg.json) frozen first: commit `3316d5fe6185d03ab02f85d0a18d7adaacd6b615`.
- Self-contained newly implemented [experiment.js](experiment.js), no previous experiment module import, frozen second at `16055ee60bb5618989b80c9b55b197be1df44cef`, GitHub blob `046eac5465fab6ed2a08534580c502151a4c641f` **read back at that exact commit before any smoke or primary**. Independently implemented by the *same research assistant*, therefore *not an independent human scientific replication*.
- One disjoint smoke (seed `119071`) confirms 24 OLD observations, 16 NEW, 12 distinct first input contexts and same-process OLD posterior/readout JSON parity.
- **15% noise regime:** 120 fresh calibration NULL worlds `120013 + 23*i`, `i=0..119`, then **60 independent primary seeds** `140021 + 29*i`, `i=0..59`, crossed with NULL, SINGLE_EDGE, DOUBLE_EDGE, NONLINEAR_AND = 240 primary worlds.
- **20% noise regime:** separate 120 calibration NULL worlds `160019 + 23*i`, then 60 primary seeds `180043 + 29*i` crossed with four families = 240 primary worlds.
- **240 distinct calibration worlds, 480 primary worlds, 11,520 OLD examples and 7,680 NEW consequences per model.** All models see the exact same OLD and NEW observations in each world. First 12 intervention inputs unique by fixed deterministic world schedule; remaining four input contexts prechosen rather than adaptively optimized. Source truth not supplied to learners. The learned family is 62 nonzero five-bit XOR masks and biases; the NONLINEAR_AND law includes a two-input AND and is *outside* this hypothesis family.
- All arms share uniform OLD hypothesis prior, `P(change)=.25`, exponential Hamming-distance conditional NEW transition prior, correct per-regime observation flip likelihood. Models include **top-8 bounded old posterior mixture (candidate), top-4 and MAP1 ablations, full exact OLD/NEW Bayesian change inference (strong conventional), and full OLD with local NEW neighborhood**.
- Each arm's alarm threshold separately calibrated at **119th of 120 sorted NULL change probabilities** (98% empirical cutoff, strict greater-than declaration) using only pre-test calibration scores. No held-source threshold tuning.
- [result.json](result.json) retains all raw calibration posterior scores, selected cutoff/rank, primary per-world posterior scores, NEW intervention/outcome action traces, OLD readout digest, and counted likelihood/transition operations (about 1.36 MB).
- [audit.js](audit.js) and [audit-result.json](audit-result.json) are **separate postscore arithmetic auditors, 10/10 PASS**: exact saved calibration percentile reconstruction, all fresh seed ranges and paired NEW traces, primary sampling budgets, model caps, summary reaggregation, frozen decisions. They **do not** rerun worlds under independent operators, verify native cold learned state, or measure hardware speed.

## Frozen results

At each observation-noise regime the primary has 60 NULL unchanged worlds, 120 familiar SINGLE/DOUBLE changed XOR worlds and 60 out-of-family NONLINEAR_AND worlds. **Higher detection is better; lower false-alarm rate and event-Brier are better.**

| Noise and calibrated method | Familiar changed detection | NULL false alarms | NONLINEAR_AND detection | Familiar event-Brier | Mean OLD hypotheses |
|---|---:|---:|---:|---:|---:|
| **15%: candidate top-8 mixture** | **111/120 = 92.50%** | 0/60 = 0% | 25/60 = 41.67% | **0.04143** | **1.66** |
| 15%: exact full Bayes | 112/120 = 93.33% | 0/60 = 0% | 30/60 = 50% | 0.04587 | 62 |
| 15%: MAP1 local | 34/120 = 28.33% | 0/60 = 0% | 2/60 = 3.33% | 0.04655 | 1 |
| **20%: candidate top-8 mixture** | **25/120 = 20.83%** | 1/60 = 1.67% | 0/60 = 0% | 0.12142 | 3.73 |
| 20%: exact full Bayes | **63/120 = 52.50%** | 0/60 = 0% | 13/60 = 21.67% | **0.12081** | 62 |
| 20%: MAP1 local | 20/120 = 16.67% | 2/60 = 3.33% | 2/60 = 3.33% | 0.15651 | 1 |

**15% regimen reproduced a limited, *synthetic* signal** on a second independently written simulator: top-8 remains within **0.83 percentage points** of fully fitted Bayesian changed-law detection with zero observed held NULL false alarms in both methods. It used 1.66 OLD hypotheses on average. This supports the conditional value of retaining multiple plausible past explanations at *this noise regime*, not proof of real generalized intelligence or memory.

**20% regime falsified robustness:** candidate recall fell to **20.83%**, a **31.67-point shortfall** from the full Bayesian 52.50%; both are materially worse at detecting change than at 15%. Candidate calibration threshold rose to **0.99484264** at 20%, versus full Bayes **0.77861916** on its differently scaled score. This evidence suggests the truncated OLD-posterior/local transition representation becomes poorly calibrated or loses sensitivity in higher noise, but **does not isolate the cause without an ablation separating posterior truncation, local NEW candidate radius, threshold estimation and limited input evidence**.

**Operation proxy** (mean per world, OLD fit + 32-input OLD readout + counted NEW likelihood and transition terms): 15% candidate **4,123.7** versus full **8,246** (**2.00× ratio**); 20% candidate **4,375.0** versus full **8,246** (**1.88× ratio**). This is **not real CPU/GPU wall-time, physical energy savings, or full-system cost improvement**.

**False-alarm uncertainty:** 0/60 or 1/60 measured NULL false alarms is not a calibrated population bound. Noise regime changes and cutoff differences were frozen beforehand; none of this justifies postscore threshold adjustment.

## Exact pass/fail under preregistered conditions

| Frozen requirement | 15% noise | 20% noise |
|---|---|---|
| Candidate NULL false alarms <=5% and no more than full Bayes +2.5pp | PASS | PASS |
| Candidate changed-law recall >=70% at 15%, >=55% at 20%, and no more than 10pp below full Bayes | PASS | **FAIL** |
| Candidate familiar event-Brier <= full Bayes+0.020 | PASS | PASS |
| Full/candidate counted operation ratio >=1.5 | PASS | PASS |
| 120 NULL-only calibration scores, primary event budgets, 12 initial unique inputs, old readout same-process serialization parity | PASS | PASS |

**Overall frozen classification: SCIENTIFIC NO-GO.** Reject native promotion or claims that the calibrated bounded detector survives increased noise.

**Critical scope:** This is the same assistant writing a new standalone synthetic simulator, **not independent scientific replication** or validation against unfamiliar external causal data. No complete native Yggdrasil model, actual learned-weight persistence, independent cold process restoration, interference/transfer testing, original-source custodied first-use, full candidate regression or independent scientific acceptance.

## Research disposition

**ENGINEERING:** frozen protocol/source readback, matched budgets, original calibration/NEW action custody and **10/10** postscore independent arithmetic audit PASS. The end-to-end cross-platform GitHub CI remains separately blocked by G29 source-index atlas check; inspect this exact candidate SHA's CI before claiming any candidate engineering acceptance.

**SCIENCE:** NO-GO on robustness. The next *distinct* causally discriminating test should isolate the three plausible drivers at **fixed 20% high noise**: OLD mass truncation, NEW local hypothesis neighborhood, and change-threshold conservatism; compare proper scoring and detection at a **matched false-positive budget** against full Bayes, with reserved new-seed source truth. Do not tune or reuse the consumed 20% worlds.

**DEPLOYMENT:** NONE; draft research PR only, no merges, native learner weights/checkpoints, training run, Amalgam #1278 integration, protected first-use, scheduled task, runner/controller, production or paid APIs.
