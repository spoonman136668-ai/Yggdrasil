# ENERGY-67 — Evidence-triggered causal representation growth

**2026-11-19: FROZEN `SCREEN_NO_GO`, 3/9 gates PASS.** This is external synthetic contributor research archived to existing Yggdrasil draft PR #1210; **not native Yggdrasil training, scientific acceptance, promotion or deployment**.

## Chronology and experimental custody

- Prior archive head: `68bc744a73dcb0ca28bd00312f982df96639455b`.
- Original scorer, separately authored auditor and source manifest frozen and committed **before prospective scoring** at `eb3d2a33783bbe4af0fc7c2e841d902488c7ccaf`.
- Prospective protocol frozen and read back **before screening** in separate commit `afa1b94d039619fd8ef60de9a7c037846c47e0b4`. Source tar SHA256 `1b0259ae8c9ab7a8bcb898ff2ebacf61ba804fd230a7b3ae76d649804c864ad0`.
- Excluded **pre-freeze engineering pilot** seed `109701`, three worlds, audited with 12,717 PASS checks; not confirmatory. This pilot showed a candidate tie against CV and a loss versus fixed five; no post-prospective tuning.
- Newly reserved and used **prospective screen** seeds `109711`, `109727`, four world IDs and three families each = **24 worlds**. **Reserved primary `109801`, `109819`, `109837` NOT consumed** due failed screen.

## Causal mechanism and matched controls

Every world has nine controllable binary action variables (no nuisance cues), 3 hidden OLD two-variable parity effects, and **two or four new fourth-order effects**; `four_quad_plus_fifth` additionally plants a fifth-order effect **out of the learner grammar**. There are **288 disjoint underlying action assignments** per world: OLD 80 witnessed, NEW 64 witnessed, OLD/NEW/COLD 48 withheld each; COLD uses the same NEW mechanism on previously unseen intervention IDs. Gaussian observation noise σ=0.18.

Learners do not access withheld outcomes or planted support IDs. The OLD model is a simple OMP3 approximation in a **preauthored 36-pair dictionary**, cloned identically for old readout. The NEW feature search uses a **preauthored 126 fourth-order parity dictionary**. Neither feature class nor factor algebra is invented by the learner. The proposed feature expansion accepts each proposed new factor only if it reduces the held-training validation MSE by at least 3%, stopping at first rejection. The **decisive conventional `cv_growth` control uses precisely the same ordered five-term path, all six training/validation fits, 48/16 NEW split, 64 final NEW labels and refit equations; it simply chooses the best validation-supported feature count**. This is matched data, feature path and compute for the critical mechanistic comparison. Fixed two/five are path-matched controls.

A standard train-only alpha-selected `matched_elasticnet` fits all 126 NEW fourth-order features plus the same OLD supports; `full_omp_five` learns from the full pair+quad bank. Frozen OLD, OLD support-only and shuffled NEW outcome controls are included. All arms have access to the same 80 OLD +64 NEW witness outcomes; external model capacity and compute differ outside the exactly matched growth-path comparisons. Physical energy consumption was not measured.

## Exact prospective screening MSE (lower better)

| Method | COLD held MSE |
|---|---:|
| **Conventional `cv_growth`** | **0.985495** |
| Fixed five new factors | 1.047039 |
| Conventional matched ElasticNet | 1.102861 |
| Candidate evidence-triggered `adaptive_growth` | **1.989497** |
| Fixed two new factors | 2.284159 |
| Full-bank OMP five | 2.044210 |
| OLD support-only | 4.213922 |
| Frozen OLD no-adaptation | 4.031120 |
| Shuffled NEW label negative | 10.335746 |

**Candidate has 101.88% MORE cold prediction error than exactly matched conventional validation selection**, and 80.39% MORE error than conventional matched ElasticNet. The proposed 3% stepwise stop threshold rejected profitable subsequent additions on many four-factor worlds; it did not respond reliably to increased mechanism complexity. It remains better than frozen OLD, but the strongest matched conventional control is substantially better still.

### Prospective independent seed cohorts

| Seed | Candidate | Same-path CV | Matched ElasticNet |
|---|---:|---:|---:|
| `109711` | 2.316502 | 0.660737 | 1.157040 |
| `109727` | 1.662492 | 1.310253 | 1.048682 |

### Mechanism-family cold scores and adaptive capacity

| Family | Candidate | Same-path CV | ElasticNet | Candidate mean added |
|---|---:|---:|---:|---:|
| `four_quad` | 1.534899 | 0.037124 | 0.065202 | 2.625 |
| `four_quad_plus_fifth` | 4.394792 | 2.880563 | 3.182093 | 1.625 |
| `two_quad` | 0.038799 | 0.038799 | 0.061288 | 2.375 |

## All frozen screening gates

| Gate | Decision |
|---|---|
| `adaptive_capacity_response` | **FAIL** |
| `both_seed_strongest` **(critical)** | **FAIL** |
| `family_non_degradation_10pct` **(critical)** | **FAIL** |
| `old_exact` | PASS |
| `shuffled_negative_20pct` | PASS |
| `vs_elasticnet_5pct` | **FAIL** |
| `vs_frozen_20pct` | PASS |
| `vs_matched_cv_3pct` **(critical)** | **FAIL** |
| `vs_strongest_5pct` **(critical)** | **FAIL** |

**3 PASS, 6 FAIL → `SCREEN_NO_GO`**. The four critical gates fail, so the 36-world reserved primary is NOT authorized by the frozen screening protocol. No source, seed, threshold, hyperparameter or interpretation was changed after the prospective scores; do not re-use consumed screen results to optimize a second confirmatory analysis.

## Audit, deterministic replay, source and limitations

- **PASS: 101,547 independent-source refit checks** across 24 worlds and nine modeled arms. The auditor independently reconstructs the randomized 512-intervention generator and every synthetic outcome, verifies disjoint OLD/NEW/OLD-held/NEW-held/COLD action identities, refits all methods including ElasticNet and two negative controls, verifies the actual exact matched candidate/CV feature paths, coefficients, every held-prediction vector, and original MSE aggregation. The auditor does **not import** scorer code but does share the disclosed simulated mechanism definition and common SciPy/NumPy/sklearn numerical backends; **not an independent scientific replication**.
- Unchanged frozen-source scorer replay of the same 24 worlds and subsequent independent audit: **PASS 101,547 checks**, all scientific scores and vector fields byte-identical after omitting `runtime_seconds` only. Semantic SHA256 `1e06f42167edec3d5855f4fdd0ae4943784f061502bf7e616e9fc34647b6e870`.
- The OLD held readout is copied/frozen by design, not evidence of mutable-model resistance to catastrophic forgetting. There is no unknown-grammar discovery, long-lived native learner, genuine transfer across new environments, power/Joule measurement or learned autonomy claim.
- Source archive `source.tar.bz2` (exact code, auditor, README, source manifest), original unmodified scored screen, independent screen audit, full replay plus audit, excluded development pilot and pilot audit, all retained in `EVIDENCE.tar.bz2` with SHA256 and per-file integrity in `archive_manifest.json` and `verify_archive.py`. `case_receipts.csv` indexes 24 world-level scores and chosen feature IDs.
- Exact reproduction: `export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1`, extract source archive, `python -B experiment.py --seeds 109711 109727 --out screen_scored.json`, `python -B audit.py screen_scored.json --out screen_audit.json`.

## Scientific decision

**REJECT** this 3% single-step stop rule; it was materially less reliable than conventional selection among the same fitted capacity choices. Further testing of automatic representation growth must use disjoint new seeds and a structurally different justified mechanism, not a relaxed cutoff on this failed cohort. No native Yggdrasil checkpoint, accepted ref, owner/runner/scheduler, external official research loop, merge or deployment was modified. GitHub CI is a separate status (the evidence-only archive does not qualify native regression).
