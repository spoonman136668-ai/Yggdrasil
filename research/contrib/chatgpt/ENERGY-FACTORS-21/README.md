# ENERGY-FACTORS-21 — 20%-noise causal-change factorial and frozen alarm calibration ablation

**2026-11-20 · independent Yggdrasil Energy Research contributor · ENGINEERING source/protocol custody and independent postscore arithmetic PASS · SCIENTIFIC NO-GO · DEPLOYMENT NONE**

## Mission and discriminator

Gate 20 found that an OLD posterior top-8 structural-change detector closely matched full Bayesian inference at 15% observation noise, but fell sharply short at 20%. At the time, **three possible explanations were confounded**: OLD probability-mass truncation, a restricted NEW structural hypothesis neighborhood, and a high NULL-derived posterior alarm threshold.

This experiment manipulates those mechanisms factorially **on the same newly generated worlds** and evaluates two *predeclared* NULL-only calibration policies. No Gate 14–20 trial seeds reused and no threshold changed after observing held results. This is still a same-assistant synthetic research experiment—not independently qualified science on the native learner.

## Pinned repo evidence and execution

- [Yggdrasil draft contributor PR #1346](https://github.com/spoonman136668-ai/Yggdrasil/pull/1346), accepted base `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`; native Yggdrasil integration belongs solely to [Amalgam PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278).
- [prereg.json](prereg.json) **committed first** at `a83bf272c3ce9ea3869feb78d33e8afc348c5e57`.
- [experiment.js](experiment.js) **committed second** at `b4970df3854c76ea7ccbcbc4d08a343f15d7fc4e`; source file Git blob `5c2955056800123fd10c13bf5d1b7abc1e23a820` downloaded and verified against protocol and exact PR head **before** one smoke and one primary.
- Disjoint smoke on seed `200003`: OLD 24, NEW 16, first 12 unique context actions, OLD JSON posterior/readout parity PASS.
- Independently frozen **200 NULL calibration worlds**, seeds `210007 + 31*i` for `i=0..199`; all six detectors independently calibrate score thresholds at ascending rank **191/200 (95% policy)** and **197/200 (98% policy)**.
- Single held primary: **96 fresh seeds** `225011 + 37*i`, `i=0..95`, crossed with four causal families NULL, SINGLE_EDGE, DOUBLE_EDGE, NONLINEAR_AND. **384 worlds**, **9,216 OLD observations** and **6,144 NEW consequences** per arm. First 12 of 16 interventions target distinct binary inputs; remaining 4 are fixed. NEW and OLD observations identical for every model arm in a world; source truth withheld.
- Generative model: 62 XOR mask/bias candidates on 5 binary action input dimensions, 20% random label flip noise. All models use identical likelihood, OLD uniform prior, `P(change)=0.25` and exponentially distance-weighted, per-OLD-anchor normalized NEW-change transition prior. NONLINEAR_AND is held separately as out-of-model.
- [result.json](result.json) commits **all 200 raw calibration scores**, all **384 per-world OLD and NEW action/outcome traces**, all posterior values and budgets, both frozen rank cutoffs and world metrics. [audit.js](audit.js) / [audit-result.json](audit-result.json) independently reaggregate these saved scores and verify both calibration percentiles, paired source rows, action bounds, detector caps, metrics and frozen decision: **11/11 PASS**, no simulation replay. Original-source independent study and functional cold native retention remain UNVERIFIED.

## Design isolates OLD truncation × NEW search radius

- **Candidate OLD top8 / NEW local2:** retain old hypotheses until cumulative old posterior mass 95%, cap 8; NEW changed masks differ by <=2 bit flips, bias change allowed.
- **OLD top8 / NEW global:** same OLD posterior as candidate, but search all 61 possible changed new masks/biases.
- **OLD full / NEW local2:** keep all 62 OLD hypotheses, but same local NEW change radius.
- **Strong full Bayes:** all 62 OLD × 61 NEW hypotheses with exact posterior and transition marginalization.
- **Ablations:** OLD top4 / NEW local2 and OLD MAP1 / NEW local2.
- **Alarms:** two independently calibrated fixed thresholds for every model. At 95%, the candidate cutoff was `0.77569255`; at 98%, it was `0.97021073`. Full Bayes cutoff at 95% was `0.61917392` and at 98% was `0.80776657`. Different calibrated score distributions mean raw posterior cutoff numbers are not directly comparable.

## Frozen primary results

There were 96 held NULL worlds, 192 familiar changed XOR worlds (SINGLE+DOUBLE), and 96 nonlinear out-of-family shifts.

| Same-world structural model | 95% cutoff: familiar detection | 95% cutoff: NULL alerts | 98% cutoff: familiar detection | 98% cutoff: NULL alerts | Familiar event-Brier |
|---|---:|---:|---:|---:|---:|
| **OLD top8 + NEW local2 (candidate)** | **124/192 = 64.58%** | **4/96 = 4.17%** | 62/192 = 32.29% | 0/96 | **0.112667** |
| OLD top8 + NEW global | 119/192 = 61.98% | 4/96 = 4.17% | 65/192 = 33.85% | 0/96 | **0.110800** |
| OLD full + NEW local2 | 133/192 = 69.27% | 4/96 = 4.17% | 95/192 = 49.48% | 2/96 = 2.08% | 0.126511 |
| **Full Bayes OLD/new (strong conventional)** | **134/192 = 69.79%** | **4/96 = 4.17%** | 96/192 = 50.00% | 2/96 = 2.08% | 0.124897 |
| OLD top4 + NEW local2 | 109/192 = 56.77% | 4/96 = 4.17% | 47/192 = 24.48% | 1/96 = 1.04% | 0.116131 |
| OLD MAP1 + NEW local2 | 49/192 = 25.52% | 2/96 = 2.08% | 14/192 = 7.29% | 0/96 | 0.132261 |

**Within-study threshold causal contrast (same posterior, exact same held worlds):** 95% vs 98% candidate calibration increased familiar change detection from **62 to 124 out of 192** (32.29 percentage points), while held NULL false alerts increased from **0 to 4 out of 96**. Both policies and calibration ranks were frozen before any primary score. This shows that **alarm conservatism materially constrains sensitivity in this synthetic test**; it does not prove that simply lowering thresholds creates real causal cognition.

**Structural factorial contrasts at 95% policy**:
- Expand NEW search radius with OLD top8 fixed: familiar detection **124/192 -> 119/192**, **-2.60pp**; not a rescue, even though Brier improved slightly.
- Keep all OLD hypotheses with NEW radius2 fixed: familiar detection **124/192 -> 133/192**, **+4.69pp**; helpful but below the preregistered **+12pp** mechanism-identification requirement.
- Exact full Bayesian OLD+NEW: **134/192**, only **5.21pp** above bounded candidate at matched 95% calibration, with the same observed 4/96 false alert rate.

**Computational proxy** counted OLD likelihood/readout, per-model NEW hypothesis likelihood and transition weight evaluations: candidate **4,366.64** vs exact full **8,246** operations/world, ratio **1.889x**. OLD full + NEW local2 used **6,326** operations. This is neither measured wall-clock acceleration nor physical energy reduction. 95% calibrated candidate continuous familiar event-Brier **0.112667** was lower than full Bayes **0.124897** on this finite test cohort; this is not a statistically validated superiority claim over the correctly specified conventional model.

**Out-of-family nonlinear shift**: 95% candidate detection **16/96=16.67%**, full Bayes **25/96=26.04%**. Neither recognizes these nonlinear causal mechanisms reliably. No grounded transfer claims.

## Preregistered classification

The gate predeclared that a **single identifiable structural factor** must increase familiar recall by >=12 percentage points with controlled held false alarms and without >0.025 Brier degradation; the other factor must show a >=5pp smaller effect, and the improved policy must remain within 10pp of the exact full-Bayesian reference. It also mandated two fixed calibration reports, all matched source examples and independently reconstructed NULL thresholds.

**Result: SCIENTIFIC NO-GO.** Neither structural change met the >=12pp criterion:
- OLD full/local2 improved +4.69pp;
- NEW global with OLD top8 reduced recall -2.60pp.
- The 95% cutoff *did* recover 32.29pp within the same bounded detector, but the frozen rules did not license post-hoc promotion of threshold tuning to a distinctive intelligence mechanism.

**What this falsifies:** that *simply* expanding the historical hypothesis pool or widening the new-hypothesis search is the dominant high-noise recovery lever at matched 95% false-alarm calibration in this designed world. The evidence instead raises the importance of calibrated change decisions, intervention evidence/quantity, and model-family mismatch. Do not replay consumed seed cohorts or retune scores after seeing outcomes.

## Boundaries, risks and disposition

**ENGINEERING:** protocol/source readback and pre-result freeze PASS, one disjoint smoke, one calibration and primary, saved per-world sources, separate arithmetic/cohort audit 11/11 PASS. No native cold restore; JSON readout check is only same-process. Full cross-platform final regression and native acceptance are still unverified because prior [G29 atlas indexed-source-set check](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44817716133) failed on Windows/Linux for source-file set mismatch; check this exact final commit CI separately.

**SCIENTIFIC:** NO-GO for structural factor hypothesis. External real-world causal discovery, long-term native retention, cognitive capacity growth, energy savings, transfer, native learning improvement and independent scientific repetition remain unverified. A no-trial next step can preserve the frozen evidence and **hand off a candidate research question** to the Amalgam owner for independent, native tests; do not flood this branch with serial unqualified synthetic experiments or incorrectly merge it as science.

**DEPLOYMENT:** NONE; draft-only contributor. No accepted Yggdrasil main, Amalgam PR #1278, checkpoint, original-source first use, runner, scheduler, controller, model weights, paid API or production mutation.
