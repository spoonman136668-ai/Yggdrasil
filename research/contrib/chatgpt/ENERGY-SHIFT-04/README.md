# ENERGY-SHIFT-04 — Sparse directed-causal repair after a mechanism change

**2026-11-20. Source-free synthetic independent Yggdrasil research. Scientific superiority: NO-GO; evidence category: MIXED. No native learner or checkpoint integration.**

## Objective and isolation

Can a persistent local edge-memory learner repair an unfamiliar causal transition while preserving unaffected relationships, without exceeding fully fitted conventional adaptive learning or the correctly specified Bayesian reference? This contribution is isolated inside [draft PR #1346](https://github.com/spoonman136668-ai/Yggdrasil/pull/1346); the sole cumulative learner and acceptance authority remain with [Amalgam PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278).

The experiment reuses no prior consumed ENERGY-FLUX-01 or ENERGY-TOPO-02 seeds. It keeps two old/new per-state/action count memories and triggers a bounded local reset only when an integrated change-evidence posterior reaches 0.75, while protecting action-0 knowledge. Underlying action-conditioned five-state transition relationships are hidden. Learners receive only the same observed consequence streams and the public epoch boundary. Each world belongs to one of: **LOCAL_SWAP** (two changed action-1 rows), **GLOBAL_REVERSE** (all five changed action-1 rows), or **NULL** (no causal change).

## Frozen source and genuine single-use execution

- Preregistration first committed `4aa0ea9352fe86f422e01945da5850b55506825a`, clarified **before executable freeze** in `5a14433b6edc4a5692969704b010ebc81d10914f`. The final [prereg.json](prereg.json) was read back from GitHub before scoring.
- Frozen [experiment.py](experiment.py) commit `60d67b2a8032eddaea5aaaf42dda7996e82b414c`; remote Git blob `e459c02183dc37bfae9dec46cdd9db10aafda392`, exact local executed Git blob identical; SHA-256 `492b44b123ac9fe77b0c0bfc354b63d27087e2c809c2f9ee3a531631bdfdf339`. Python source syntax was checked.
- Distinct smoke seed `92489` executed first. Then the **12 frozen primary seeds** were executed **once**, with a local exclusive-use lock, over 36 independent worlds, 2,520 fit/adaptation observations and **46,080 independent held transitions**.
- Original 173,386-byte local raw `primary.json` SHA-256: `ee15577d91135e1aaa34bf0988dbb6c45d89f069c938d462d112c62c16a5c548`; **raw file is not uploaded to the repository**. The repository stores [result.json](result.json) (aggregate transcription), [primary-metrics.csv](primary-metrics.csv) (36 per-world paired scores rounded to six decimals), and [provenance.json](provenance.json) (identity and custody). The local raw file's custody cannot be assumed to survive another ChatGPT runtime. **Do not rerun primary seeds to fill this evidence gap.**

## Frozen primary observations

Multiclass Brier (lower is better), on held action-1 predictions:

| Learner / control | Held action-1 Brier | Overall Brier | Model CPU including shared simulation/evaluation (s) |
|---|---:|---:|---:|
| Correctly specified exact structured Bayes oracle (source-family prior, no hidden labels) | **0.270540** | **0.271207** | 0.222944 |
| Fully fitted global change-point Bayes | **0.390584** | **0.358495** | 0.093813 |
| Proposed contradiction-gated local repair | 0.393465 | 0.359936 | 0.093684 |
| Fully fitted local row change-point Bayes | 0.400162 | 0.363284 | 0.094494 |
| Exponential-recency Dirichlet control | 0.424542 | 0.396017 | 0.094402 |
| Post-reset Dirichlet control | 0.411202 | 0.368804 | 0.093555 |
| Static fully fitted pooled Dirichlet | 0.509897 | 0.418152 | 0.093847 |

Against the **best fully fitted adaptive comparator**, local repair is **0.002882 Brier worse**, not >=0.01 better. Per-arm charged generation + model fit + JSON serialize/restore + held scoring CPU ratio is **0.998622**, nowhere near the required <=0.5. This is a short local source-free CPU measurement, not a native whole-process benchmark.

| Scenario | Local repair action-1 Brier | Strongest relevant fitted control | Interpretation |
|---|---:|---:|---|
| LOCAL_SWAP | 0.379883 | Row-change Bayes 0.388241 | Local repair better by only 0.008357, below 0.01 gain requirement |
| GLOBAL_REVERSE | 0.464561 | Post-reset Dirichlet 0.405213 | Local repair substantially worse under global rewiring |
| NULL | 0.335952 | Static pooled Dirichlet 0.335952 | Equal; no unnecessary resets |

**Negative controls and memory:** `0/12` NULL worlds triggered false local repair; candidate flagged changed rows in `12/12` LOCAL_SWAP and `12/12` GLOBAL_REVERSE worlds. In LOCAL_SWAP, post-score descriptive detection was 20 true changed rows, 0 false flags, 4 missed rows, 8/12 worlds exactly identifying both changed rows. This observation was **not a preregistered discovery/acceptance threshold**. All 36 JSON round-trips retained stored historical forecasts exactly, and protected action-0 Brier passed the frozen guard. **This does not prove independent-process cold restoration or cumulative lifelong retention**.

## Classification and interpretation

**MIXED_NO_GO, not SCIENTIFIC_PASS.** The candidate beats a static baseline under LOCAL_SWAP by 0.106095 held Brier and has some genuinely localized change detection, but a strong adaptive conventional model remains better over the whole frozen experiment. The correctly specified oracle is much better (0.270540), consistent with the [ENERGY-BOUND-03 Bayesian Brier boundary](../ENERGY-BOUND-03/ANALYSIS.md). The source includes uncertainty calculations but discretizes their output into a hard per-row reset; evidence suggests this loses probability calibration and performs badly under global changes. That mechanism diagnosis remains a hypothesis, not a demonstrated ablation.

**The next scientific discriminator, not executed here:** on a fresh preregistered disjoint cohort, compare (i) hard local repair, (ii) smoothly calibrated posterior local repair and (iii) independently trained global/local switch-mixture Bayesian controls at equal source/action budgets, testing both sparse and system-wide changes, historical functional retention across real process restarts and total compute. Do not tune threshold 0.75 or reuse the 12 consumed seeds based on this result. A new mechanism or seed cohort would need new prereg and separate first-use authority.

## ENGINEERING / SCIENTIFIC / DEPLOYMENT truth

- **ENGINEERING:** Exact source identity and local smoke/primary execution verified; local original primary SHA recorded. No independent dual-OS exact-source regression or native atlas acceptance. Existing source-pinned G29 Atlas CI rejects new indexed paths until regenerated at an exact final source commit. Do not bypass its guard.
- **SCIENTIFIC:** Mixed developmental result, strongest matched conventional comparison NO-GO, original owner first-use UNVERIFIED. Negative and null findings preserved.
- **DEPLOYMENT:** NONE. No accepted `main`, native checkpoint, program runner, model, controller, schedule or scientific integration changed. Keep independent contributor ownership.
