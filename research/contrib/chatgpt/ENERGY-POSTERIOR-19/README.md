# ENERGY-POSTERIOR-19 — preserving historical causal uncertainty for calibrated change detection

**2026-11-20 · isolated Yggdrasil Energy Research contributor · engineering frozen-source/independent arithmetic audit PASS · SCIENTIFIC NO-GO (one frozen false-alarm criterion fails) · DEPLOYMENT NONE**

## Question

Does retaining a bounded, OLD-posterior-weighted set of plausible causal hypotheses, rather than committing to the single historical maximum-a-posteriori (MAP) explanation, recover the missing structural-change sensitivity under fixed matched interventions and 15% observation noise?

This is not a new architecture or an accepted native Yggdrasil model. It is a **source-free synthetic decision experiment** that tests a specific, falsifiable uncertainty-preservation mechanism. In the earlier [ENERGY-CALIBRATE-18](../ENERGY-CALIBRATE-18/README.md) experiment, the MAP-anchored local detector reached 75.83% familiar change sensitivity versus 91.67% for full Bayesian marginalization. The earlier trial's seeds were consumed and were **not replayed or threshold-tuned**.

## Exact GitHub custody, single-run procedure

- Existing draft contributor [PR #1346](https://github.com/spoonman136668-ai/Yggdrasil/pull/1346); accepted-main baseline `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`. Sole cumulative native integration owner remains [Amalgam PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278).
- Freeze [prereg.json](prereg.json) **before source** at commit `c2ff5f8c4b2eddf3e4b68b824e14fddb6b9c75a2`.
- Freeze [experiment.js](experiment.js) second at commit `3703d9f5f202aab92a8816964877e43c4f22c335`, exact GitHub blob `6e9afc5ad390c2e4135f01fb95ede59b59e99e31`, verified by GitHub readback **before** separate smoke or primary execution.
- One disjoint smoke seed `100901` on NULL: OLD 24 observations, NEW 16 with first 12 distinct interventions, all model inference probabilities finite. Only frozen source subsequently executed.
- **160 source-free NULL calibration worlds**: seeds `101003 + 17*i` for `i = 0..159`; score-only calibration, *no primary labels*. Each detector's sorted posterior threshold is the 157th smallest value: `ceil(0.97*(160+1))=157`; only `posterior > threshold` declares change.
- **320 source-free held evaluation worlds**: seeds `107011 + 19*i` for `i = 0..79`, crossed with NULL, SINGLE_EDGE, DOUBLE_EDGE and NONLINEAR_AND. Across primary worlds: **7,680 OLD observations**, **5,120 matched NEW consequence observations per model**, common exact fixed 12-distinct-plus-4 input schedule; source truth withheld from detectors.
- [result.json](result.json) preserves **all 160 original per-model calibration posterior scores** (closing Gate 18's calibration custody hole), all 320 evaluation world's posterior/decisions, 16 original action/outcome pairs per world, operation counts, and predeclared decision gates. It does **not** preserve original OLD outcome trace in full. [audit.js](audit.js), [audit-result.json](audit-result.json): **12/12 PASS** separate postscore arithmetic, exact percentile-threshold reconstruction, decision and world/action budget checks; not a separately operated simulation replica.

## Models and controls

Each model fits the identical 62-hypothesis OLD posterior from 24 OLD observations with uniform OLD prior, then uses a known 15% binary flip likelihood for each of 16 NEW consequences. All assume a change prior of 0.25 and an exponentially distance-weighted transition between XOR masks and bias bits. All alarms are independently calibrated on exactly the same 160 NULL worlds.

- **Candidate local posterior mixture:** retain the smallest ranked prefix with 95% OLD-posterior mass, capped at **8 OLD hypotheses**. For each retained OLD hypothesis, marginalize changed NEW hypotheses within mask Hamming radius <=2, with bias flips included; renormalize local changed alternatives and posterior OLD mass.
- **MAP1 local control:** same restricted NEW hypothesis radius <=2 but retain only one OLD hypothesis.
- **TOP4 local ablation:** identical candidate but cap OLD mixture at 4.
- **TOP8 FULL-radius ablation:** identical OLD-mass truncation, all 61 changed NEW alternatives considered per retained OLD.
- **Correctly modeled conventional exact full Bayes:** all 62 OLD and 61 possible NEW changed hypotheses per anchor, exact OLD-posterior and transition marginalization.
- **MAP1 global control:** old MAP only but all 61 possible NEW changed alternatives.
- **Never-change:** no false alarms, also no learned detections.

Full Bayes assumes a model family that is **misspecified** for NONLINEAR_AND worlds; its superiority on familiar XOR worlds cannot be generalized to arbitrary causal systems.

## Frozen outcomes

Calibration-derived posterior alarms on **160 familiar changed** (SINGLE_EDGE+DOUBLE_EDGE), **80 NULL** unchanged, and **80 NONLINEAR_AND** out-of-family worlds:

| Calibrated method | Familiar changed detection | NULL false change | Nonlinear AND detection | Familiar binary-event Brier |
|---|---:|---:|---:|---:|
| **Candidate top-posterior-mass <=8** | **150/160 = 93.75%** | **4/80 = 5.00%** | 44/80 = 55.00% | 0.051737 |
| Local MAP1 radius<=2 | 47/160 = 29.38% | **1/80 = 1.25%** | 0/80 | 0.074495 |
| Local TOP4 radius<=2 | 133/160 = 83.13% | 4/80 = 5.00% | 20/80 = 25.00% | 0.055767 |
| Local TOP8, full NEW alternative radius | 150/160 = 93.75% | 4/80 = 5.00% | 46/80 = 57.50% | 0.052730 |
| **Exact full Bayesian marginalization** | **151/160 = 94.38%** | **2/80 = 2.50%** | **46/80 = 57.50%** | **0.044819** |
| MAP1 global all NEW alternatives | 9/160 = 5.63% | 1/80 = 1.25% | 0/80 | 0.069516 |
| Never-change | 0/160 | 0/80 | 0/80 | N/A |

**Substantive scientific finding in this synthetic setup:** the bounded posterior mixture recovers **+64.38 percentage points of familiar change sensitivity** versus the top-1 local method on this new frozen held cohort. It nearly matches full Bayesian change sensitivity (93.75% versus 94.38%) while examining **1.7875 historical hypotheses on average** instead of 62. Its continuous event-Brier is 0.051737 vs full 0.044819, so it does **not** outperform the stronger conventional probability model.

On these specific synthetic sources, preserving OLD uncertainty appears more important than simply expanding the NEW-candidate neighborhood. These results **do not** demonstrate genuine long-term memory or learned new relationships in the native Yggdrasil substrate.

**Counted operations** per primary world: candidate **4,142.65**, exact full **8,246.00**, ratio **1.991×**. This is a deliberately narrow likelihood/transition operation proxy which includes OLD fitting and OLD readout. It is **not measured CPU/GPU wall time, actual physical energy savings, memory footprint or all-in research efficiency**. Never-change is trivial but useless, and a MAP1 detector is less costly yet misses many changes; do not claim absolute compute superiority.

### Preregistered acceptance truth

Six of seven frozen conditions PASS: <=5% held NULL false-alarm, >=75% familiar change recall and within 10 percentage points of exact full, proper binary-event Brier tolerance, >=1.5× operation proxy, action/same-process readout parity, and NONLINEAR detection noninferiority versus MAP1.

**One fails, so overall SCIENTIFIC NO-GO:** candidate false-change rate 5.00% is **3.75 percentage points above** MAP1's 1.25%, exceeding the frozen additional false-alarm tolerance of 2.50 points (by **1.25 points**). Importantly, MAP1's low false-alarm rate accompanies severely reduced sensitivity; that does not excuse changing the frozen requirement after scores are known. The candidate's observed 5% false-alarm proportion from 80 worlds does not prove its population false-alarm rate is <=5% with high confidence.

**The next experiment must not tune these consumed worlds.** A fresh calibration and held cohort is required to evaluate uncertainty-aware change *decision costs* and proper scoring against exact Bayes, perhaps with a predeclared false-change budget against exact full Bayesian rather than a weak low-sensitivity MAP baseline. Native integration remains prohibited until independently operated replication and qualified acceptance.

## Engineering, scientific and deployment boundaries

**ENGINEERING:** preregistration before source, GitHub blob readback before trial, disjoint smoke / 160 calibration / one 320-world primary, saved raw calibration scores and primary intervention traces, independent **12/12** postscore arithmetic auditor PASS. The auditor does **not** independently regenerate source outcomes, certify physical runtime, replay trained native checkpoints, or prove true model cold restoration. Only same-process JSON OLD posterior/readout parity was tested. Full exact-head Linux+Windows regression and the stale generated G29 atlas indexed source set remain separately unqualified; see the [previous exact-head CI failure](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44796965167).

**SCIENTIFIC:** **NO-GO by predeclared decision gate**, despite large calibrated synthetic sensitivity improvement. No independently sourced original-world data, trained conventional native model match, validated generalization, durable native memory, scientific learning gain, or autonomy demonstrated.

**DEPLOYMENT:** **NONE**. No accepted main mutation, native weights/training, Amalgam #1278, original scientific first-use, checkpoint, owner runner, scheduler, controller, merge or deployment.
