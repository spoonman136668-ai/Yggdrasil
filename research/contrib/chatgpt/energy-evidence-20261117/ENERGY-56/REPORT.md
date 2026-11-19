# ENERGY-56 — Causal-factor composition under unfamiliar mechanism shifts

**Frozen decision: SCREEN_NO_GO (4 of 8 preregistered gates passed).** This is contributor-run, external synthetic research, NOT scientific acceptance or Yggdrasil-native learning.

## Custody

- Archive parent: `8c62d380d8953dea1675537f69f5e2e7a79bffa7`; source + independent refit-auditor frozen on GitHub at `f07c49ed1830221080919c36f9427c79970e1c96`; fresh-screen seeds, strong controls and all eight gates preregistered separately at `2ff3b2544e056e3eee23d9c95e028a5c06779896` **before** prospective outcomes.
- Source bundle Git blob `b4c0ce9608c4988dbec908913d144240b184cc65`, SHA-256 `38e67516fbac0608e94b1b406cf6da6124e24ec79c0d3f7fe8079d52798c1958`. Source exactly matches the original frozen scorer and auditor referenced in `source_manifest.json` and `provenance.json`.
- Excluded development-only seed `99903` (six worlds) was evaluated **before** GitHub source freeze. The first prefreeze prototype's cold 4.26546 versus no-composition 2.98985 triggered one bounded refinement: compose only disjoint triple factors and multiply compositions by 0.3. The final development variant remained worse, 4.18694 versus 2.98985. Development evidence cannot be claimed as independent confirmation.
- **Prospective screen seed 99917** evaluated once with the frozen source and no hyperparameter changes: **6 worlds = 2 world IDs × three preauthored families**. Primary seeds `9911,9923,9941` remain untouched, because the frozen stop criterion failed. No threshold, seed or model retuning after the prospective screen.

## Experiment and knowledge limits

Each world has a separate hidden grouping of ten causal action bits into three nonlinear modules plus an extra causal bit. The hidden operators differ across `parity_composed`, `mixed_composed` and `gated_composed`; true old/new consequence functions combine module outputs and interaction products. Two observed nuisance cues correlate with causal bits in OLD and NEW, then decorrelate at COLD. Exactly **512 distinct 10-bit causal intervention assignments** are partitioned into 128 witnessed old +96 witnessed new +96 held old +96 held new +96 held cold outcomes per world. All eight arms receive identical observed action-consequence data; no held labels, module grouping or true coefficients used for fitting.

The candidate learns eight old-context sparse features from an **authored 1–3-way parity dictionary**, then forms only products of disjoint selected degree-three factors. Learned old factors persist as an explicit basis, with separately fitted old/new Ridge heads; compositions scaled 0.3. A capacity-matched no-composition ablation uses the identical learned old factors and regularization. Strong fully fitted conventional controls include OMP12, ElasticNet and Ridge on the **full 1–6-way parity grammar**, RBF KernelRidge and 64-tree ExtraTrees. The shuffled-new-consequence ablation protects against apparent gain from irrelevant learning. Giving all methods a parity feature grammar is not evidence of autonomous operator invention.

## Prospective six-world cold-transfer results

| Method | Held OLD MSE ↓ | Held NEW MSE ↓ | Held COLD MSE ↓ |
|---|---:|---:|---:|
| no_composition | 3.533160 | 2.187808 | 3.525049 |
| hierarchical | 1.811859 | 1.328943 | 4.553741 |
| full_elasticnet | 0.875374 | 1.346644 | 4.607933 |
| full_omp | 1.322308 | 2.031353 | 5.303532 |
| full_ridge | 5.802626 | 4.802931 | 5.860407 |
| rbf_kernel | 5.429057 | 4.769009 | 5.220054 |
| extra_trees | 7.618388 | 7.414948 | 7.376730 |
| shuffled_composition | 1.811859 | 5.771280 | 5.910350 |

The proposed hierarchical model is **29.18% worse** on cold transfer than the identical lower-order learned factors **without** composition (4.553741 vs 3.525049). It is only **1.18% better** than the best conventional full-feature ElasticNet (4.607933), below the frozen 5% cold margin. Crucially, NEW MSE 1.328943 rose to cold MSE 4.553741, so stage-good prediction was not robust to nuisance shift. This is not improved retention or general transfer.

### Mechanism-family breakdown (diagnostic, not retrospective selection)

| Family | Hierarchical cold MSE | No-composition cold MSE |
|---|---:|---:|
| parity_composed | 5.543619 | 2.517665 |
| mixed_composed | 3.270390 | 3.033413 |
| gated_composed | 4.847214 | 5.024069 |

### Exactly frozen gate outcomes

| Preregistered gate | Decision |
|---|---|
| `cold_gain5_no_comp` | **FAIL** |
| `cold_gain5_strongest_conventional` | **FAIL** |
| `family_robust_10pct` | **FAIL** |
| `old_held_5pct` | **PASS** |
| `composition_nontrivial` | **PASS** |
| `shuffled_gain20` | **PASS** |
| `cold_gain5_vs_new` | **FAIL** |
| `audit_pass` | **PASS** |


Both required cold-accuracy gates FAILED. Final prospectively required outcome is **SCREEN_NO_GO** (4/8 gates PASS). Main native scientific first-use is not reached; primary is not run. Do not tune this used seed or relabel prefreeze results.

## Audit and repeatability

- A separately written `audit.py` refitted **all 8 learners** directly from the saved factual arrays, validated training/test assignment uniqueness and all per-world predictions, and independently recomputed every MSE, seed/family aggregate and selected support: **17,249 checks PASS** on fresh screen, 6 worlds. Excluded dev screen separately passed **17,239 checks**. The auditor shares the NumPy/scikit-learn numerical backends and observed arrays, and **does not independently regenerate hidden source truth**; this remains a limitation.
- Deterministic replay with unchanged source matched **431,651 bytes** of all non-timing semantic content; SHA-256 `995a5e978b7cf5869492399096bf874821713fbf48b4cf34748fdd268cf07bc5`. Per-case wall clock is excluded from the equality because natural runtime varies.
- `EVIDENCE.tar.bz2` retains the original complete raw scorer result, independent audit, original replay, prefreeze development receipts and exact replay receipt. `case_receipts.csv` is the six-world flat digest. No paid model, GPU, owner runner or protected data used. Local CPU timings do not establish physical energy efficiency.
- The standard repository code-atlas CI and native Yggdrasil acceptance are **separate infrastructure/engineering gates**, not substitutes for this negative synthetic scientific result.

## Decision

The observations show that learning reusable lower-order features did not guarantee useful **composition**: enriching the model with pairwise products of selected triples increased cold-context error, especially on parity-composed worlds. A more decisive successor must test actual structural composition discovery and stage-invariant coefficient estimation, with a **fresh, independently generated** world family and fully fitted conventional controls; it must not optimize this consumed cohort.

**ENGINEERING:** scorer, independent refit auditor, deterministic replay and integrity PASS locally; repository CI reported separately. **SCIENCE:** SCREEN_NO_GO. **DEPLOYMENT:** none. `main`, accepted refs and native Yggdrasil model remain unchanged.
