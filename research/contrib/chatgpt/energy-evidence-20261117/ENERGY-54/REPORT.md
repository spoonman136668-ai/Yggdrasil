# ENERGY-54 — Model-mismatch-aware expected information gain

**Frozen classification: SCREEN_NO_GO (2 of 9 preregistered gates PASS).**

- Source freeze commit: `66aec145d0ea97d2ed2d54ff1d48da14639f035f`
- Separate preregistration commit before prospective results: `ab267e84556a9bb7356d4818992fd88e5034bfbc`
- Screen: 24 fresh synthetic worlds; seeds **99851, 99863**, 4 worlds each × 3 families.
- Excluded prefreeze dev smoke: seed 99839, 3 worlds, 414 independent checks PASS (not confirmatory).
- Reserved primary seeds **9719, 9733, 9749 NOT consumed**.

## Cold transfer (fixed OMP3 downstream; lower MSE is better)

| Selection policy | Cold MSE | Selection CPU seconds (24 worlds) |
|---|---:|---:|
| d_optimal | 1.799278 | 0.05786 |
| hamming | 2.093611 | 0.02352 |
| robust_eig | 2.162700 | 1.12470 |
| tournament | 2.183895 | 0.02760 |
| eig | 2.353115 | 1.35185 |
| random | 2.359323 | 0.00357 |

**Proposed robust-EIG:** 2.162700 MSE, 20.20% worse than best other policy D-optimal (1.799278). Used D-optimal fallback on 49 of 288 decisions. Selection CPU time ratio to tournament **40.7×**.

## Frozen screening gates

| Gate | Result |
|---|---|
| `gain5_vs_best_omp` | **FAIL** |
| `gain5_vs_best_any` | **FAIL** |
| `gain10_vs_random_omp` | **FAIL** |
| `gain3_vs_tournament_omp` | **FAIL** |
| `per_seed_strict_both` | **FAIL** |
| `every_family_at_most10pct_worse` | **FAIL** |
| `old_predictions_exact` | **PASS** |
| `fallback_exercised` | **PASS** |
| `selection_compute_below8x_tournament` | **FAIL** |

## Replication by seed

| Seed | Proposed cold MSE | Best other OMP cold MSE |
|---|---:|---:|
| 99851 | 2.292455 | 1.844262 |
| 99863 | 2.032945 | 1.754294 |

## Replication by generator family

| Family | Proposed cold MSE | Best other OMP cold MSE |
|---|---:|---:|
| bank_parity4 | 0.704355 | 0.511145 |
| novel_parity5 | 4.409038 | 3.414001 |
| novel_conditional5 | 1.374708 | 1.256328 |

## Audit and research scope

- **Independent selection/refit audit: PASS 2,934 checks**, 24 worlds, six policies × three downstream learners, source assignments/labels and per-model prediction hashes verified.
- **Unchanged-source deterministic replay: PASS**, semantic SHA-256 `16513017c3496e2015c643709159b3205704b71fbf3a9a8540aeacab58e762c7`, excluding CPU timing fields only.
- Complete original scored primary-screen JSON SHA-256: `bb27add957d42caa60777f588a31549e152d65f1f24bcbb3814b4d667c8e2989`, preserved inside `EVIDENCE.tar.bz2`.
- Evidence archive SHA-256: `b22f6b81a5c9fbbb1fb6bed56f2da2f55f23135f712084ef40d70d05da841ef3`; source archive SHA-256 `e9bbeb9dd4fa1517b47a1f7dbf5b0b5605e02a22094cfc1a5c22163f2c86918e`.
- Audit independently implements action-selection and refits sklearn estimators, but **shares synthetic generator, NumPy and sklearn**; not independent Yggdrasil qualification.
- Exact source-free reproduction: `tar -xjf source.tar.bz2`, then `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B experiment.py --seeds 99851 99863 --out replay_screen.json` and `python -B audit.py replay_screen.json --out replay_audit.json`.
- First invoker of frozen screen could not write output (`PermissionError`), produced **no scored file**, and did not inspect outcomes. Reran unchanged scorer with normal directory write permissions, then audited. This is a local file permission issue, separate from the scientific negative.
- **ENGINEERING:** local source, independent audit, replay and file-integrity PASS. GitHub CI/native regression separate, not inferred.
- **SCIENCE:** SCREEN_NO_GO. The stronger conventional D-optimal design outperformed expected-information gain on both seeds and all family aggregates. No primary scientific pass.
- **DEPLOYMENT:** NONE. Yggdrasil main/accepted refs/model weights/Forge loop/owner/runners/queues unchanged.

## Interpretation

The causal-hypothesis posterior is a useful theoretical representation, but expensive expected-entropy integration and a residual-fit fallback did not improve action selection. In the supplied finite 24-hypothesis grammar, the out-of-bank mechanisms remain hard. Freeze these negatives and do not retune consumed seeds or claim autonomous causal learning.
