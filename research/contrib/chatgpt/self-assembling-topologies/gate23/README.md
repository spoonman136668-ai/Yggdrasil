# Gate 23 — Prequential source reliability and bounded causal mode-switching

**SCIENTIFIC NO-GO** against the frozen *joint* objective. Partial synthetic improvement in false-switch rejection and old-source reactivation does not establish independent native structural superiority.

## Identity and chronology

- Previous fully qualified Gate22 contributor head: `7f177f61508d8eeb37458c5c38f117cadf1e4271`.
- [Gate23 protocol](prereg.json) frozen at `61e43959294aa9122f64cfcb595f09dbf2e6225f`.
- [Executable](run.cjs) committed separately **before primary scoring** at `53f65d218c2692fabbd78ec7332eb2425a93ebb5`.
- [First sealed result](result.json) committed at `447bf9d7853a96d3d219614d55b99718e18fd46e`.
- [Receipt audit](audit.cjs) is independent numeric/custody auditing but NOT an independently coded second learner. [Provenance](provenance.json) records first-use and limits.

## Hypothesis and method

Can a source-model reliability check and a bounded, prequential log-evidence switch suppress unsupported topology changes while keeping the ability to adapt to a new causal world and reactivate its old source?

Six fresh finite-Boolean seed cohorts, 32 seeds each (192 synthetic worlds). Each world receives A64 labeled intervention vectors, then a hidden B48/A-return48 stream, with 16 strictly held additional actions per target phase. True parents, phase labels, truth function and future outcomes are not given to the learner. Four families remap parents at B; stationary3 and independent fair-noise are negative controls. The original A model is immutable.

Source predictor is a 1–3-parent graph fitted using A64 penalized leave-one-out Brier. If unpenalized source LOO Brier exceeds **0.20**, the detector abstains from changing modes and predicts .5. Otherwise, a 16-event rolling sum of **quantized prequential log-likelihood ratios** comparing a recent-32 graph to the immutable A model triggers switching at +3.0 or reactivation at -3.0, with one 8-event cooldown block. The recent-32 alternate is fitted by exhaustive subset comparison every eight observed outcomes, with no evaluation-label access.

Controls: independently written rolling-32 and all-history static MAP subset fit, Bayesian hazard source/rolling mixture, immutable A, and .5 null. All receive identical action/outcome data; these controls do **not** have exactly matched transient compute or inference work. The detector and rolling MAP share the same 41-subset hypothesis universe, so a detector result is not unique structural superiority. Packed source/stream/state use 384 bytes.

## Phase-end held-out Brier (lower better)

| Cohort | B detector | B rolling MAP | B hazard Bayes | Return detector | Return rolling MAP | Return Bayes |
|---|---:|---:|---:|---:|---:|---:|
| Pair XOR | 0.068952 | 0.068952 | 0.075130 | 0.056104 | 0.067927 | 0.057572 |
| MUX3 | 0.082661 | 0.082661 | 0.098559 | 0.059004 | 0.079538 | 0.061154 |
| Essential3 | 0.122638 | 0.122638 | 0.144291 | 0.068642 | 0.108189 | 0.068943 |
| Unary | 0.065197 | 0.065197 | 0.068243 | 0.042224 | 0.043423 | 0.042374 |
| Stationary3 | 0.071562 | 0.098515 | 0.072590 | 0.056283 | 0.093204 | 0.059728 |
| Independent noise | 0.251973 | 0.276082 | 0.263492 | 0.250410 | 0.305364 | 0.261578 |

## Frozen outcomes

- **False-change suppression:** Noise worlds switched 1/32, stationary nonlinear worlds 0/32. Previous Gate22 used different consumed seeds and had 26/32 noise switches; this is a historical contrast, **not a paired cross-gate causal improvement estimate**.
- **Stored source reactivation:** 127/128 related-world trials ended back in A mode after having entered B mode. The receipt does not establish exact re-entry times for each seed.
- **Phase-end B adaptation:** identical Brier to rolling MAP across 128 related trials (fixed mask and stream probabilities coincide at the phase endpoint), and **better** than the Bayesian hazard mixture by 0.011694 Brier; this does not demonstrate uniquely learned structure.
- **Return to A:** paired rolling-MAP minus detector Brier **+0.0182758559**, 95% normal CI **[+0.0127495291,+0.0238021827]**, meeting that frozen return threshold.
- **Bayes return control:** Bayes-minus-detector **+0.0010174221**, 95% CI **[-0.0000782148,+0.0021130591]**, below the frozen >= +0.005 and positive-CI thresholds; two independent scientific criteria FAIL.
- **Online adaptation penalty:** During the B stream *before phase endpoint*, detector-minus-rolling prequential Brier **+0.0503399094**, 95% CI **[+0.0464413159,+0.054238503]**, exceeding allowed +0.035; FAIL.
- **Reproducibility:** 192/192 phase-held action disjointness, immutable A forecasts and deterministic 384-byte in-process B48/R72 restoration checks PASS. Separate-process persistence remains unverified.

**Joint verdict:** 13/16 frozen thresholds pass; 3 FAIL. **SCIENTIFIC NO-GO** for a superior causal detector. A simple source reliability abstention + finite-window likelihood switching helps with noise and retained old-world predictions but still cannot beat the strong Bayesian alternative on return or maintain sufficiently low online B regret.

## Reproduce from the pinned source

```sh
node research/contrib/chatgpt/self-assembling-topologies/gate23/run.cjs --verify research/contrib/chatgpt/self-assembling-topologies/gate23/result.json
node research/contrib/chatgpt/self-assembling-topologies/gate23/audit.cjs
```

**ENGINEERING:** Source and first-use result sealed in Git. Full final current-head G29 source atlas plus Linux/Windows repository regression and exact-replay audit must run before engineering PASS.

**SCIENCE:** NO-GO for all joint frozen thresholds. The 192 worlds are consumed. Real action-intervention learning, independent cold-process restoration, compute-matched superiority, learning retention and general intelligence remain unproved.

**DEPLOYMENT:** NONE. PR #1340 remains draft, accepted main/canonical Amalgam unchanged. Neither contributor mode changes nor engineering PASS authorize model promotion, research-owner actions or native scientific first-use.
