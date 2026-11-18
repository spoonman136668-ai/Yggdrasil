# ENERGY-44 — Selective causal weight repair without forgetting

**2026-11-18 · Synthetic external research · DEVELOPMENT_NO_GO (4 PASS / 4 FAIL).** This is not native Yggdrasil training, native scientific first-use, unrestricted operator discovery, persistent agent cognition, an accepted Yggdrasil result, or production deployment.

## Question and mechanism

ENERGY-43 discovered most five-motif structures from observed actions, but its coefficient anchoring degraded old prediction error. ENERGY-44 freezes an old model trained on 96 intervention outcomes, then locally learns **two corrective factors** only for the changed new/cold contexts from another 96 labeled interventions. It does not edit the older model. The candidate minimizes observed new-stage residual squared error plus a fixed small coefficient penalty over all 120 pairs from the 16 highest-correlated candidate grammar features. Nothing is selected based on held-out answers. That is sparse corrective optimization, **not a demonstrated energy-specific cognitive benefit**.

The old and new contexts share three causal motifs; one old-only causal term disappears and one new-only term appears. Two nuisance cues change correlation across old, new and completely cold environments. Interventions randomly set 12 binary actions. The true hidden supports and real-valued weights are unavailable to every learner, but all methods know the **finite, authored 364-element grammar** of unary/parity-pair/parity-triple and pairwise AND functions. This does not measure spontaneous discovery of entirely new primitives or native Yggdrasil learning.

## Source identities and preregistration sequence

- Baseline evidence archive: `cd6fd81689489490bf6fd409c109f3810f0a6e64`.
- Fixed ENERGY-44 scorer and *separately authored* independent refit auditor **committed before primary**: `12c4a83b581c6a11e2b0db143e4756b2d6c9fd5f`.
- Original scorer SHA-256: `6882e7e4f202de660b90b9a0d08d20eb4ccfe67a8d143105a6c7390d5ea8ba30` (`experiment.py.bz2` SHA-256 `82159c625e2cb272587e5e51dab22a7025840b47978091054b0fe9efbe32e96f`). Original auditor SHA-256: `64743cf9ab2ec23475519ce12ec1cd566f09c4ee00fc5a9e1108871486f9ad90` (`audit.py.bz2` SHA-256 `7a2e16c6285ce53a0da16753d31b1872243c2e15c2f651f1dbd1381990803a00`). Exact source is linked to the unchanged ENERGY-43 original generator/auditor whose individual SHA-256s appear in `prereg.json`.
- Protocol, all 8 gates, seed identities, learner capacities, runtime budgets and classification rules **preregistered separately before scoring**: `bac0d6913ce6dbac81525acef8b1e2f9687339b3`.
- **Only pre-prereg smoke:** excluded seed `99829`, three synthetic worlds, independent generator/ten-model audit **11,583 checks PASS**. The auditor's own loop-variable bug was corrected *before the source was frozen*; no primary seed was inspected.
- **Primary (disjoint from ENERGY-43):** seeds `8713,8731,8741`, worlds `0..3`, three mechanism families: 36 worlds, 192 observed training consequences per world (96 old + 96 new) for every arm and 128 independently generated held interventions each old, new, and cold. Equal outcomes and sampling, 10 arms, and one prospectively frozen score pass.

## Ten fully trained arms

The target arm is **selective_repair**, which stores its four learned old-stage support coefficients unchanged, selects and fits at most two new-stage residual corrections, and gates those corrections off when asked old-stage questions. Exact-capacity conventional **omp_delta2** has identical stage-one model and 96 new-stage examples but uses standard OMP to select two residual correctors. The strong **omp_structural_memory** model is the ENERGY-43 best conventional approach: three first-stage structures retained, cumulative fitting of up to seven active factors on all 192 outcomes. Other controls: full-grammar OMP7, new-stage-only OMP4, regularized Ridge, dense ElasticNet, a 60-tree random forest, an unadapted old model and the identical two-factor corrective candidate with shuffled new-stage residual labels. Their training inputs, capacities and responsibilities are frozen and fully disclosed in the source.

## Frozen primary metrics

Mean squared error (MSE) on 4,608 held predictions per context; **lower is better**. Single-local-run sum of model fitting and inference Python wall times over 36 worlds; not physical energy consumption or entire-process cost.

| Arm | Old after new learning | New context | Cold context | Fit + prediction (s) |
|---|---:|---:|---:|---:|
| **ElasticNet full grammar (best cold)** | 0.147845 | 0.140751 | **0.202714** | 0.5684 |
| Conventional OMP structural memory (best old) | **0.128010** | **0.121612** | 0.224761 | 0.4701 |
| Conventional stagewise new OMP4 | 0.185176 | 0.154155 | 0.287924 | 0.2242 |
| Full grammar OMP7 | 0.148557 | 0.157956 | 0.308174 | 0.4567 |
| **Candidate: selective two-factor repair** | **0.185176** | 0.334189 | **0.411373** | 0.4356 |
| Exactly matched conventional OMP2 residual repair | 0.185176 | 0.336295 | 0.431157 | 0.2142 |
| No repair | 0.185176 | 2.392327 | 2.176577 | 0.1942 |
| Ridge full grammar | 1.991044 | 1.879180 | 2.145234 | 0.4881 |
| Shuffled-label corrective model | 0.185176 | 2.799168 | 2.578730 | 0.2822 |
| Forest on raw interventions | 2.571813 | 2.579534 | 2.637689 | 2.0457 |

Candidate cold MSE is **2.03× the strongest conventional control** (0.411373 / 0.202714), not at least 10% lower as required. Candidate beat the *exactly matched* two-factor OMP baseline by **4.59%** cold MSE, just shy of the prespecified 5% margin; this modest gain is not enough to overcome the stronger, more flexible controls. The candidate's old error before and after learning is **identical at 0.185176** because older coefficients are frozen. That is legitimate **zero overwrite**, but does not by itself show ideal retention: structural-memory OMP achieves **0.128010** old error with the same 192 outcomes. Candidate recovered **93.06% of true old-only/new-only support identities**, above the frozen 80% support-recall requirement.

### Eight frozen gates

| Gate | Result | Evidence |
|---|---|---|
| Candidate cold MSE at least 10% below best conventional | **FAIL** | 0.411373 versus best 0.202714 |
| Candidate old MSE inflation at most 1% | **PASS** | Exact preservation 0.185176 → 0.185176 |
| Candidate old MSE within 5% of best conventional | **FAIL** | 0.185176 versus 0.128010 |
| Candidate cold MSE ≥5% better than exactly matched OMP delta2 | **FAIL** | 4.59% improvement only |
| Candidate ≥20% cold MSE improvement over shuffled correction | **PASS** | 0.411373 versus 2.578730 |
| New-context corrective factor identity recall ≥80% | **PASS** | 93.06% |
| Candidate wins against strongest conventional per seed on at least 2 of 3 | **FAIL** | 0/3 |
| Candidate local fit+predict elapsed ≤3× OMP structural memory | **PASS** | 0.4356 versus 0.4701 seconds |

**4 PASS / 4 FAIL → DEVELOPMENT_NO_GO.** Independent consistency and source reconstruction are valid. Do not change the source, seeds, hyperparameters or gate thresholds to rescue the result.

### Postscore diagnosis — not additional acceptance gates

| Family (12 worlds each) | Candidate cold MSE | ElasticNet cold MSE | OMP structural cold MSE |
|---|---:|---:|---:|
| Parity pairs | 0.09381 | 0.17002 | 0.18237 |
| Parity triples | 0.28495 | 0.21219 | 0.23452 |
| Mixed parity and conjunctions | **0.85535** | **0.22593** | **0.25739** |

The parity-pair subgroup is favorable, but not a valid substitute for the frozen all-family objective. The strongest performance failure comes from mixed conjunction/parity worlds, where old-stage sparse discovery sometimes picks a misleading support; freezing that incorrect old model protects the error too. Across each of the three primary seeds, the strongest conventional fitted control outperformed the candidate. These are **postscore diagnostics**, not selection/tuning criteria.

## Independent audit, semantic replay, and archival custody

- A separately authored scorer-independent auditor imports only the **separately authored ENERGY-43 audit generator**, not ENERGY-44 experiment. It reconstructs all 36 worlds and 10 fully trained prediction paths, recomputes corrective pair choices using a different analytic two-parameter normal-equation expression, verifies exact factor indices, correction coefficients, stage-1 coefficients, ground-truth supports, 128 old+128 new+128 cold predictions per arm and all aggregate MSEs. **138,666 checked items, 0 errors, PASS**. As documented, both Python paths use shared third-party NumPy/sklearn implementations; this is not independent verification of their library internals.
- **One unchanged-source primary replay** matched the entire **69,813-byte non-timing semantic record byte-for-byte**, SHA-256 `4da36c38d7c4657b8e2b6dbf28f6b7dd55e115c33f1e50e8197cbe7a6de0482b`. All eight frozen gate decisions matched in the replay, including the cost gate; the numerical timer readings themselves naturally differ.
- The **original complete timing-bearing `scored.json`** is deposited byte-for-byte compressed as `scored.json.bz2`: raw **151,649 bytes**, SHA-256 `9661b101fb9289de14c0a41184cbdd19e7b81c8a1f1fe5c6f8fe75d29e935e74`, packed **24,429 bytes**, SHA-256 `722896e5ed4bcaffa7e5730c1fe9ae7d0b84f9f8e894d7816ee5a95faf7bb7de`. It contains every case, all 10 arms, exact model supports and coefficients where applicable, MSEs, timing measurements, decision and provenance. Archive integrity is checked by `verify_archive.py` without re-running the primary.
- The **36-world concise CSV** (`case_receipts.csv`), with source/factor identity and per-world selected competing held outcomes to 9 decimals, raw **6,013 bytes**, SHA-256 `8531518844d4874bf882636a7435582c7e24c426253390eb92521121b078314e`. The complete unrounded 10-arm data are in the archived original compressed JSON.
- Auditor receipt is `audit_result.json.bz2`, **206 bytes** originally (SHA-256 `b3d00c31d7eda929a54326b3f87b21bdf0432625fab8b2bfd866af669fb2018e`), 175 packed bytes (SHA-256 `e7b763118e265e40bdb9d75f46ebdfd4ed2158f287707ba7b8eded0d09773da7`).
- Local Linux CPU, Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.8.0, BLAS threads 1; no native runner, production credentials, paid API, GPU or accepted Yggdrasil model action.

## Reproduction

Checkout the archive commit, put `ENERGY-43` and `ENERGY-44` next to each other, and decompress the four immutable `.py.bz2` sources. Verify hashes from `prereg.json` before running. Then:

```bash
python -B verify_archive.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B experiment.py --primary --out reproduced.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B audit.py reproduced.json --out audited_reproduction.json
```

Expected deterministic case scores, selectivity, supports, decision bits and non-timing semantic SHA are frozen. Repeated timer values are not expected to match byte-for-byte. `verify_archive.py` verifies the original deposited primary/case receipts without consuming seeds again.

## Decision and next actionable research hypothesis

**Reject this particular 2-factor correction-only repair as a general improvement.** It maintains a frozen old predictive model but cannot repair a wrong old causal support on mixed mechanisms; correcting only the new-context output leaves the old error intact and cold generalization poor. The next distinct falsifiable mechanism is **contradiction-gated support replacement with hard negative-controls on unaffected predictions**, not further top-16 or ridge-threshold tuning on consumed seeds. Frozen old predictions should be protected on unaffected examples while implicated old structural supports can be reassessed using new evidence; matched conventional support-reselection/replay remains mandatory.

**ENGINEERING:** local scorer/auditor/replay PASS; native Linux+Windows full final regression UNVERIFIED. **SCIENCE:** DEVELOPMENT_NO_GO. **DEPLOYMENT:** NONE, draft archive PR only.
