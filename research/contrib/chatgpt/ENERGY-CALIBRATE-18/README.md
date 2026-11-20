# ENERGY-CALIBRATE-18 — distinguishing noisy evidence from genuine causal change

**2026-11-20 | independent contributor-only source-free development | ENGINEERING bounded score audit PASS | SCIENTIFIC NO-GO | DEPLOYMENT NONE**

## Question

Can calibrating a bounded local change detector on *separate, frozen unchanged worlds* substantially reduce false repair decisions while retaining sensitivity to new causal relationships, relative to an exact full Bayesian marginal-old change detector with equal observations?

This gate deliberately **fixes intervention choice** instead of attempting another action-selection policy: all models receive exactly the same 24 OLD examples and 16 NEW consequences per world, with the first 12 NEW contexts distinct. This isolates the *decision/calibration* seam identified by ENERGY-TRANSFER-17. These are synthetic five-input binary causal systems; the experiment does not run or train Yggdrasil's native learner.

## Frozen custody, calibration, and controls

- Existing isolated [Yggdrasil draft PR #1346](https://github.com/spoonman136668-ai/Yggdrasil/pull/1346); accepted main at branch base `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`. Only [Amalgam PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278) owns cumulative native integration.
- [prereg.json](prereg.json) frozen **first** in commit `0cd7bdcf351f4cce3b70cc78e311abc37e902a80`.
- [experiment.js](experiment.js) frozen **second** in commit `3937a188c6ac13eeda5501b713722852c369fe75`, source Git blob `70a22806e981d740c73fdc1ce4166bd0873be9c4`, read back from the exact GitHub commit **before execution**. No postresult source adjustment.
- Disjoint smoke seed `90031`: 24 OLD, 16 NEW, first 12 unique contexts, OLD posterior/readout JSON roundtrip PASS.
- **120 calibration NULL worlds** from seed sequence `91001 + 11*i`, `i=0..119`; local, fully marginalized Bayesian, and MAP-old full Bayesian change posterior values used *only to set source-frozen NULL percentile thresholds*. Per-model criterion: sorted score rank `ceil(0.97*(120+1))=118` (one-based), declare change only when score strictly exceeds the rank-118 threshold. Two calibration alarms per method. No primary labels used in threshold selection.
- **240 new evaluation worlds** from `95003 + 13*i`, `i=0..59`, across NULL, SINGLE_EDGE, DOUBLE_EDGE and out-of-family NONLINEAR_AND. Primary has 60 NULL, 120 familiar changed and 60 nonlinear changed worlds. Total **5,760 OLD observations and 3,840 NEW outcome events per model**. All methods use the same fixed 12-distinct + four seeded input schedule and paired observable consequences.
- Fully marginal Bayesian control: all 62 OLD and NEW XOR hypotheses with uniform OLD prior, known 0.15 noise, prior `P(CHANGE)=0.25`, transition kernel `exp(-mask/bias Hamming distance)` conditional on change, normalized for each OLD hypothesis. This is a strong conventional *assumed-model* control, not a generative oracle; the fixed prior need not match held scenario proportions.
- Local candidate: anchor the OLD MAP hypothesis; search candidate NEW masks at radius <=2, compare change evidence to unchanged OLD, threshold learned on the separate calibration NULL worlds. Ablations: local fixed 0.80, full exact Bayesian calibrated, full fixed 0.95, global MAP-old calibrated, uncalibrated NEW-only MAP change, and never-change.
- [result.json](result.json) retains all 240 per-world continuous posterior scores, binary decisions, costs and digest of fixed action/outcome trace. [audit.js](audit.js) and [audit-result.json](audit-result.json) separately verify **11/11** saved-result cohort, decision, Brier and cost arithmetic predicates **without replaying any seed**.

## Frozen main result

Detection rates for familiar actual changes use SINGLE_EDGE+DOUBLE_EDGE (120 worlds); false changes use NULL (60 worlds).

| Detection rule | Held NULL false alarms | Familiar changed-world detection | Nonlinear change detection |
|---|---:|---:|---:|
| **Local calibrated (candidate)** | **3/60 = 5.00%** | **91/120 = 75.83%** | 13/60 = 21.67% |
| Local fixed posterior >=0.80 | 4/60 = 6.67% | 101/120 = 84.17% | 20/60 = 33.33% |
| **Full marginal Bayesian calibrated** | **2/60 = 3.33%** | **110/120 = 91.67%** | 31/60 = 51.67% |
| Full marginal Bayesian fixed posterior >=0.95 | 0/60 | 78/120 = 65.00% | 6/60 = 10.00% |
| MAP-old full Bayes calibrated | 3/60 = 5.00% | 81/120 = 67.50% | 9/60 = 15.00% |
| Uncalibrated NEW-only MAP structural difference | 16/60 = 26.67% | 120/120 = 100.00% | 52/60 = 86.67% |
| Always say unchanged | 0/60 | 0/120 | 0/60 |

The uncalibrated NEW-only MAP makes many false declarations despite detecting every familiar shift: **accuracy/sensitivity alone is misleading**. The fully Bayesian calibrated detector provides the stronger practical tradeoff in this model. Calibration thresholds are **not** remotely interchangeable: local `0.8944383`, full marginal `0.2718138`, MAP-old `0.9755247`, each calibrated to its own NULL score distribution. The full fixed `0.95` rule is unusually conservative and loses detection.

**Proper binary-event Brier, 180 familiar NULL + SINGLE_EDGE + DOUBLE_EDGE worlds (lower is better):** local **0.079711**, exact full marginal Bayes **0.062538**, MAP-old all-hypothesis Bayes **0.075903**. The local/full gap of +0.017173 stays within the preregistered +0.025 allowed error. On average per primary world the counted operation proxy was local **3,998** vs full **8,246**, a **2.063x** ratio; NOT a measured CPU/wall-clock/energy or real all-in runtime speedup. This proxy includes shared OLD fit and NEW hypothesis likelihood/transition calculations, but not infrastructure, memory allocation or hardware resource consumption.

## Frozen verdict and new failure

**NO-GO:** Five of six preregistered conditions passed, including <=5% held NULL alerts, >=65% absolute familiar sensitivity, Brier tolerance, calibration-vs-uncalibrated local-0.80 comparison, >=2.0x operation proxy and 100% same-process OLD JSON readout/equal action counts. **One decisive condition failed**: local familiar recall 75.83% is **15.83 percentage points below full calibrated Bayesian recall 91.67%**, outside the allowed 10-point gap.

This is a real falsification of the *compact MAP-anchored change-gate* at its frozen threshold on the defined synthetic test. It does not prove that Bayesian inference always dominates all local causal mechanisms, nor prove that calibrating the local detector is useless. It shows a **noise versus sensitivity tradeoff that the current local approximation cannot resolve at matched evidence**.

**Calibration evidence limitation:** Original 120 NULL calibration *scores* were not saved to the bounded `result.json`, only the fixed thresholds/ranks, counts and source procedure. Hence the separate auditor can verify threshold *application* to the 240 primary outcomes, but **cannot independently reconstruct percentile sorting from saved calibration scores**. Do not report independently authenticated calibration or original source rerun. Full 16-action original traces also are not saved individually, only per-world action/outcome digests, counters and source. This is a provenance gap to close in a *new* experiment without rerunning consumed seeds.

**Statistical limitation:** A 3/60 held NULL proportion equals 5% empirically, but does not establish a 5% long-run false alarm probability with high confidence. Neither the 60-world nonlinear performance nor this single paired synthetic generator constitutes independent scientific reproduction.

**ENGINEERING:** frozen source custody, single-source simulation, matched outcomes and 11/11 separate postscore arithmetic checks PASS. Exact full final Linux+Windows regression, regeneration of the committed G29 atlas source-set index, independent scientific replica, calibration-score trace custody, and native cold functional retention remain **UNVERIFIED**. The earlier [G29 CI source-set failure](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44793425779) is an engineering index problem and does not explain the negative scientific result.

**SCIENTIFIC:** **NO-GO**: compact MAP-anchored detector misses too many real changes relative to fully marginalized Bayesian change inference. No native persistent cognition, unfamiliar real-world transfer, scientific superiority or independently qualified computational gain.

**DEPLOYMENT:** **NONE**. No merge, accepted main change, Amalgam owner/checkpoint, protected first-use, native weights, runner, scheduler, controller, paid API or deployment.

## Next distinct falsifiable hypothesis

Try a **bounded top-k OLD posterior-mixture detector**, not a new active selector: retain a small, adaptively chosen mass-covering set of OLD hypotheses instead of only OLD MAP, and compare calibrated local-versus-exact Bayesian detection under the same actions, NULL false-alarm budget and independent cold functional check. Freeze top-k/mass rules and out-of-family safety stops before fresh seeds. Require an actual replicated gain over the strongest fitted controls before requesting native owner review; otherwise preserve failure and stop.
