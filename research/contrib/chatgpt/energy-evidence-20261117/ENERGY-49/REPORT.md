# ENERGY-49 — Prospective diversity acquisition beats conventional policies on cold synthetic transfer

**Date:** November 18, 2026. **Classification: DEVELOPMENT_PROVISIONAL_GO** (5/5 critical + 4/4 supporting frozen checks). **NOT SCIENTIFIC_PASS.** No native Yggdrasil model training, first-use qualification, model weights, accepted checkpoint, merge, controller, or deployment.

## Why this study was independently preregistered

ENERGY-48 screened old-vs-new sparse-energy contradiction selection, which failed two excluded smoke seeds (99913,99919), so its fresh primary seeds remained unconsumed. The early screens suggested that simple **Hamming-space diversity** of do-interventions sometimes improves data collection with much less compute. This was a **developmentally selected** hypothesis, not a blind a priori discovery. Before consuming any primary seeds, the team committed the immutable ENERGY-48 experiment source to GitHub, committed the separate `analyze49.py` at **`1d9e23f7f90884f7cbf09c54490b55ded25ed0a8`**, froze nine gates in `prereg.json` at **`2a3dbf1d1c3548611bd70d10154f073f166119c5`**, and separately committed independent primary auditor `audit49.py` at **`8ff892f51008e7d083e61ff3abab1fa77f29464d`**. This source/prereg ordering was checked before primary scoring.

## Exact frozen design

Three previously untouched primary seeds **9109,9127,9137** × four source IDs × three causal families (parity2, parity3, mixed) = **36** different worlds, of which 27 change a factor and 9 have no factor change. These are generator-defined synthetic randomized `do` intervention cases in a **12-bit input system** with five hidden signed causal motifs and two nuisance cues whose correlations change. All learners receive **96 old + 48 new initial witnessed intervention outcomes**. The selector then chooses **24 new actions from a common 192-action unlabeled pool** and witnesses exactly those 24 consequences; each fully fitted downstream method has **168** observed training labels per world. **No selector sees held results, hidden causal weights or unselected candidate labels.** Three held sets of 128 actions (old, new and cold nuisance-shift) are disjoint.

Seven selection policies: unlabeled **Hamming-space diversity** (candidate), uninformed random, first-in-pool, bootstrap ElasticNet uncertainty committee, conventional dense old-new disagreement, sparse OMP4 old-new energy disagreement, and a shuffled-new-label sparse-disagreement negative. Every selector is evaluated using the **same context-gated fully trained ElasticNet** (728 authored features, alpha 0.025, L1 ratio 0.85), and separately **fully trained OMP7**. The authored factor grammar is supplied to all methods: **no general operator discovery** is demonstrated.

## Primary results — frozen downstream ElasticNet

| Acquisition policy | Cold MSE ↓ | Old MSE ↓ | Selection + fit/predict CPU seconds |
|---|---:|---:|---:|
| **Hamming diversity (candidate)** | **0.153288** | **0.133102** | 0.4135 |
| Dense conventional disagreement | 0.175688 | 0.133641 | 0.6258 |
| Fixed unlabeled pool order | 0.188591 | 0.133791 | 0.4078 |
| Sparse causal-energy contradiction | 0.199012 | 0.133683 | 0.4934 |
| **Random interventions** | **0.211290** | 0.133531 | 0.4252 |
| Shuffled-factor contradiction (negative) | 0.216037 | 0.133314 | 0.5071 |
| Four-model bootstrap uncertainty committee | 0.239903 | 0.133330 | 1.1128 |

Diversity achieved **27.45% less mean cold error than random** and **12.75% less than the strongest other method** (dense conventional disagreement). It also took approximately **2.8% less measured selection+fit/prediction CPU time than random** on this local run (0.4135 vs 0.4252 seconds). These times *exclude* the same common graph generation work charged to neither policy, host provisioning and audit; no true energy consumption was measured. These results do not mean every world improved: diversity was better than random in **23/36**, worse in **13/36**, and the result's variation across worlds matters.

### Three seed cohorts — separate confirmation, not a new tune

| Fresh seed | Diversity cold MSE | Random cold MSE | Direction |
|---|---:|---:|---|
| 9109 | 0.161278 | 0.262828 | Diversity better |
| 9127 | 0.142004 | 0.147958 | Diversity better by a small amount |
| 9137 | 0.156584 | 0.223085 | Diversity better |

The improvement is not uniformly large: seed 9127's mean margin was only about 4%. No causal general intelligence or universally stable mechanism is claimed from three correlated generator seeds.

## Frozen qualification: all nine pass

**Critical, required (5/5 PASS):** mean cold error ≥5% better than random; cold improvement in ≥2/3 seed cohorts; old-context MSE within 2% of the strongest other acquisition method; selection+fit/predict CPU ≤1.3x random; no-change world's cold error ≤1.10x random.

**Supporting (4/4 PASS):** mean cold error ≥3% better than strongest other selector; changed-world cold error ≥5% better than random; cold MSE ≥5% better than shuffled-label negative selector; OMP7 cold MSE no worse than OMP7 fed random acquisitions.

By the *prospectively recorded classification*, all critical and at least two supporting gates plus independent audit would qualify `DEVELOPMENT_PROVISIONAL_GO`; **9/9 achieved**. This is a *provisional external synthetic engineering/science development result*, not final independent science qualification, native Yggdrasil integration or a generalizable intelligence claim. Do not postscore retune these primary seeds.

## Source, audit, exact replay and custody

- **Fully original primary JSON** (all 36 worlds, complete 192-candidate policy selections, all 14 downstream model predictions' cryptographic digests, 3 per-arm MSE and measured timings), stored as `primary49.json.bz2`, original SHA-256 **`c145cc6d70916dd044c3fe222c8c4df689646adea786558c4eaaaec95d716aaf`**, compressed SHA-256 **`91845dcf90ea307de574d1e2794705113365ad4ea9c880c3dac92614a44f40ab`**. No result cases omitted.
- Independent, **source-free auditor `audit49.py`** reconstructed the world generator, all unlabeled intervention choices, factor models, model fitting, 128 predictions in every context per arm: **3,782 checks PASS**. It shares NumPy RNG and sklearn model implementations but imports **neither** the scorer nor its source. Audit response at `audit49_result.json`.
- Original-source replay **semantically identical** excluding Python wall timings, SHA-256 **`a53068d97916148f0d5db56d27e205d426e2b894ae97714955d4fbfb5b8c9b7a`**, and all frozen error metrics and gate verdicts identical. Proof in `replay49_receipt.json`.
- 36 convenient `case_receipts49.csv` rows and full original per-case objective/prediction digests support outside reaggregation. `provenance49.json`, `result49_archive.json` and `verify_archive49.py` record byte custody. All source/artifacts committed under the existing **draft PR #1210**, no native ref modification.

### Reproduction (external, read-only)

Extract the ENERGY-48 `source.tar.bz2` into a clean directory, obtain ENERGY-49 `analyze49.py` and `audit49.py` from this exact repository commit, then run with Python 3.13.5, NumPy 2.3.5 and scikit-learn 1.8.0, single threaded BLAS:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B experiment.py --mode primary --out primary_replay.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B analyze49.py primary_replay.json --out summary_replay.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B audit49.py primary_replay.json --out audit_replay.json
python -B verify_archive49.py
```

**ENGINEERING:** local independent source/refit and deterministic replay PASS. **SCIENTIFIC:** DEVELOPMENT_PROVISIONAL_GO on one synthetic generator family, independent native and real-world scientific qualification **NOT RUN**. **DEPLOYMENT:** NONE. PR remains draft; repo code-atlas CI must be reported separately, not confused with model/science evidence. No live runner, queue, scheduled task, native weights, merge or accepted branch changed.
